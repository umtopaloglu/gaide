"""Assemble a draft Canonical Eligibility Representation (CER) from a ct.gov record."""
import hashlib
import re
import uuid

from . import extract as X
from .segment import HEAD_NAMED_RE, build_tree, normalize, parse_items, split_inline_letters

SCHEMA_VERSION = "cer-draft-0.1"
NS = uuid.UUID("6f1c1a52-7e3c-4a0b-9d54-2c0c1f3b9e11")
SCOPE_WORDS = re.compile(r"\b(phase|arm|cohort|part|trial|stratum|screening|randomi[sz]ed|period|step)\b", re.I)
GROUP_OPS = [
    (re.compile(r"\b(any|one) of the following|\beither\b", re.I), "ANY", "explicit"),
    (re.compile(r"\ball (of )?the following|\ball the following", re.I), "ALL", "explicit"),
]


class _Ctx:
    def __init__(self, nct):
        self.nct, self.n_nodes, self.flags = nct, 0, []

    def nid(self, path):
        self.n_nodes += 1
        return str(uuid.uuid5(NS, f"{self.nct}|{path}"))


def _node(ctx, path, ntype, text, span, **kw):
    n = {"id": ctx.nid(path), "path": path, "type": ntype, "text": text, "source_span": span,
         "flags": [], "review_status": "needs_review", "origin": "interpreted_rule_based"}
    n.update(kw)
    return n


def _group_op(text, polarity):
    for rx, op, basis in GROUP_OPS:
        if rx.search(text):
            return op, basis
    if re.search(r"\bfollowing\b", text, re.I):
        return ("ANY" if polarity == "exclusion" else "ALL"), "assumed"
    return "ALL", "assumed"


def _predicate_node(ctx, path, p, parent_text, span, extra=None):
    n = _node(ctx, path, "predicate", parent_text[p["span"][0]:p["span"][1]], span,
              predicate={k: v for k, v in p.items() if k != "span"}, computability="structured_computable",
              sub_span=p["span"])
    if "applicability" in p:
        n["applicability"] = n["predicate"].pop("applicability")
        n["flags"].append("conditional_applicability: threshold applies only if condition is true; "
                          "may override a stricter sibling threshold -> needs clinical review")
    if p["kind"] in ("lab", "measurement") and p.get("terminology", {}).get("status") != "proposed_unreviewed":
        n["flags"].append("terminology unmapped")
    if p["kind"] == "biomarker" and p.get("qualifier_gaps"):
        n["flags"].append("biomarker qualifiers not stated in text: " + ", ".join(p["qualifier_gaps"]))
    if extra:
        n.update(extra)
    return n


def _leaf(ctx, path, text, span, ctxinfo):
    """One criterion statement -> predicate / group / narrative node."""
    tw, exc = X.time_window(text), X.exceptions(text)
    preds, connector, covered = X.extract_predicates(text)
    common = {}
    if re.search(r"\w\*|\*\w|\*\s*$", text):
        common["flags"] = ["footnote marker (*): a qualifying note elsewhere in the text may modify this criterion -> review together"]
    if tw:
        common["time_window"] = tw
        if tw["status"] != "parsed":
            common.setdefault("flags", []).append("temporal anchor missing or unrecognised -> evaluate as unknown until resolved")
    if exc:
        common["exceptions"] = exc
    if not preds:
        sc = X.simple_condition(text)
        if sc and not exc and not tw:
            n = _predicate_node(ctx, path, sc, text, span)
            n["flags"].append("condition predicate has no terminology binding yet -> not executable until bound")
        else:
            comp, sub = X.classify(text, False)
            n = _node(ctx, path, "narrative", text, span, computability=comp, subtype=sub)
            hits = sorted({m.group(0).lower() for m in X.COND_RE.finditer(text)})
            if hits:
                n["concept_hits"] = hits
        for k, v in common.items():
            if k == "flags":
                n["flags"] += v
            else:
                n[k] = v
        return n
    kids = [_predicate_node(ctx, f"{path}.p{i}", p, text, span) for i, p in enumerate(preds)]
    if len(kids) == 1:
        n = kids[0]
        n["text"] = text
    else:
        op = "ALL" if connector == "MIXED" else connector
        n = _node(ctx, path, "group", text, span, op=op, children=kids,
                  logic_basis="inferred_from_connector" if connector != "ALL" else "assumed_conjunction")
        if connector == "MIXED":
            n["flags"].append("mixed and/or between extracted predicates: ALL assumed, precedence unverified")
        elif connector == "ALL":
            n["flags"].append("conjunction assumed between extracted predicates (list/commas)")
    rest = X.uncovered_words(text, covered)
    coverage = 1 - len(rest) / max(1, len(re.findall(r"[A-Za-z]{3,}", text)))
    n["extraction_coverage"] = round(coverage, 2)
    if len(rest) >= 8:
        resid = _node(ctx, path + ".r", "narrative", text, span, computability=X.classify(text, False)[0],
                      subtype="residual text not covered by typed predicates")
        top = _node(ctx, path + ".g", "group", text, span, op="ALL", children=[n, resid],
                    logic_basis="residual_added")
        top["flags"].append(f"~{int(coverage*100)}% of the statement's content words are typed; residual kept as narrative requirement")
        n = top
    for k, v in common.items():
        if k == "flags":
            n["flags"] += v
        else:
            n[k] = v
    return n


def _convert(ctx, items, c, path_prefix, out):
    """Walk the item tree; append requirement nodes to `out`."""
    for i, it in enumerate(items):
        marker = it.marker.rstrip(".)") if it.marker and it.marker not in "*•-–" else ""
        path = f"{path_prefix}/{marker or ('b' + str(i + 1))}"
        if not path_prefix:
            path = f"/{c['tag'].lower()}{path}"
        if it.kind == "hint":
            c["hint"] = it.text
            continue
        if it.kind == "heading":
            sub = dict(c)
            low = it.text.lower()
            if "exclusion" in low:
                sub["polarity"], sub["polarity_source"] = "exclusion", f"heading '{it.text}'"
            elif "inclusion" in low:
                sub["polarity"], sub["polarity_source"] = "inclusion", f"heading '{it.text}'"
            if not HEAD_NAMED_RE.match(it.text):
                letters = re.sub(r"[^A-Za-z]", "", it.text)
                if letters.isupper() and not re.search(r"\b(phase|arm|cohort|part|step|stage)\b", it.text, re.I):
                    sub["category"] = it.text.rstrip(":")         # e.g. legacy NCI "PATIENT CHARACTERISTICS": grouping only
                else:
                    sub["scope"] = c["scope"] + [it.text.rstrip(":")]
            sub.pop("hint", None)
            ctx_scopes.append({"label": it.text, "span": [it.start, it.end]})
            _convert(ctx, it.children, sub, path, out)
            continue
        head, inline_parts = split_inline_letters(it)
        is_scope = (it.colon and it.children and SCOPE_WORDS.search(it.text) and "following" not in it.text.lower()
                    and not inline_parts and len(it.text.split()) <= 8
                    and not re.search(r"\b(must|should|shall|have|has|had|received|require[sd]?|no|not)\b", it.text, re.I))
        if is_scope:
            sub = dict(c)
            sub["scope"] = c["scope"] + [it.text.rstrip(":")]
            ctx_scopes.append({"label": it.text, "span": [it.start, it.end]})
            _convert(ctx, it.children, sub, path, out)
            continue
        span = [it.start, it.end]
        node = _requirement(ctx, it, head, inline_parts, c, path, span)
        node["display_number"] = f"{c['tag']}-{path.lstrip('/').split('/', 1)[1].replace('/', '.')}"
        node["polarity"] = c["polarity"]
        node["polarity_source"] = c.get("polarity_source", f"section '{c['section']}'")
        node["scope"] = list(c["scope"])
        if c.get("category"):
            node["category"] = c["category"]
        if c.get("hint"):
            node["branch_hint"] = c["hint"]
            node["flags"].append(f"follows branch heading '{c['hint']}' in a flat list; branch membership unresolved")
        if it.structure_basis == "heuristic":
            node["flags"].append("nesting inferred from a flat list (heuristic) -> verify parent/child grouping")
        out.append(node)


def _requirement(ctx, it, head, inline_parts, c, path, span):
    kids = []
    if inline_parts:
        for letter, seg in inline_parts:
            kids.append(_leaf(ctx, f"{path}/{letter.rstrip('.')}", seg, span, c))
    if it.children:
        sub_out = []
        sub = dict(c)
        sub.pop("hint", None)
        _convert(ctx, it.children, sub, path, sub_out)
        for k in sub_out:                         # children inside a requirement are conditions, not roots
            for f in ("polarity", "polarity_source", "scope", "display_number"):
                k.pop(f, None)
        kids += sub_out
    if kids:
        op, basis = _group_op(head, c["polarity"])
        n = _node(ctx, path, "group", it.text, span, op=op, children=kids, logic_basis=basis, lead_in=head)
        if basis == "assumed":
            n["flags"].append(f"group operator {op} assumed from wording/polarity -> verify")
        if head and not inline_parts:
            tw, exc = X.time_window(head), X.exceptions(head)
            if tw: n["time_window"] = tw
            if exc: n["exceptions"] = exc
        return n
    return _leaf(ctx, path, it.text, span, c)


ctx_scopes: list = []


def _walk(n, f):
    f(n)
    for k in n.get("children", []):
        _walk(k, f)


def build_cer(record: dict, source_meta: dict | None = None) -> dict:
    ps = record["protocolSection"]
    nct = ps["identificationModule"]["nctId"]
    em = ps["eligibilityModule"]
    raw = em.get("eligibilityCriteria") or ""
    text = normalize(raw)
    ctx = _Ctx(nct)
    ctx_scopes.clear()
    items = parse_items(text)
    tree = build_tree(items)
    roots: list = []
    base = {"polarity": "inclusion", "scope": [], "section": "preamble", "polarity_source": "no section header (assumed inclusion)"}
    # iterate section by section
    sec_items, cur = [], None
    for t in tree:
        if t.kind == "section":
            q = re.sub(r"^(?:key\s+)?(?:inclusion|exclusion)\s+criteria", "", t.text, flags=re.I).strip(" :[]")
            cur = {"section": t.section, "items": [], "qualifier": q or None}
            sec_items.append(cur)
        else:
            if cur is None:
                cur = {"section": "preamble", "items": []}
                sec_items.append(cur)
            cur["items"].append(t)
    seen = {}
    for s in sec_items:
        seen[s["section"]] = seen.get(s["section"], 0) + 1
        s["ord"] = seen[s["section"]]
    for s in sec_items:
        c = dict(base)
        c["section"] = s["section"]
        c["tag"] = s["section"][:3].title() + (str(s["ord"]) if seen[s["section"]] > 1 else "")
        c["scope"] = [s["qualifier"]] if s.get("qualifier") else []
        c["polarity"] = s["section"] if s["section"] in ("inclusion", "exclusion") else "inclusion"
        c["polarity_source"] = f"section '{s['section']}'" if s["section"] != "preamble" else base["polarity_source"]
        _convert(ctx, s["items"], c, "", roots)
    roots = _demographics(ctx, em) + roots
    all_nodes = []
    for r in roots:
        _walk(r, all_nodes.append)
    scopes = sorted({tuple(r["scope"]) for r in roots})
    h = hashlib.sha256(raw.encode()).hexdigest()
    prov = record.get("_provenance", {})
    cer = {
        "schema_version": SCHEMA_VERSION,
        "lifecycle": {"status": "draft", "note": "Draft only: not clinically or informatically reviewed; not executable for screening."},
        "source": {
            "source_type": "B", "source_role": "Source B: ClinicalTrials.gov eligibility text (designated as the Source B document by the program owner)",
            "registry": "ClinicalTrials.gov", "nct_id": nct,
            "title": ps["identificationModule"].get("briefTitle"),
            "overall_status": ps.get("statusModule", {}).get("overallStatus"),
            "retrieved_at": prov.get("retrieved_at") or (source_meta or {}).get("retrieved_at"),
            "retrieved_via": prov.get("retrieved_via") or (source_meta or {}).get("retrieved_via", "ct.gov API v2"),
            "content_sha256": h,
            "protocol_baseline": "registry_excerpt",
            "demographics": {"minimum_age": em.get("minimumAge"), "maximum_age": em.get("maximumAge"),
                             "sex": em.get("sex"), "healthy_volunteers": em.get("healthyVolunteers")},
            "text_normalized": text,
        },
        "completeness_disclosure": (
            "Source B input is the ClinicalTrials.gov eligibility section. It can omit protocol definitions, appendices, "
            "lab tables and amendment detail, so criteria referring to content outside this text stay unresolved."),
        "ctrp_biomarker_contract": {"status": "not_supplied",
                                    "note": "No CTRP structured biomarker object ingested -> registry biomarker coverage is UNKNOWN, "
                                            "not 'no biomarker restriction'. Biomarker predicates below are interpreted from free text."},
        "scopes": [list(s) for s in scopes],
        "criteria": roots,
    }
    cer["scope_items"] = list(ctx_scopes)
    cer["inventory"] = inventory(cer, items)
    cer["validation"] = validate(cer, text, items)
    return cer


def _demographics(ctx, em):
    """ct.gov structured age fields are imported deterministically (not parsed from prose)."""
    out = []
    for field, cmp_, tag in (("minimumAge", ">=", "min-age"), ("maximumAge", "<=", "max-age")):
        raw = em.get(field)
        if not raw:
            continue
        m = re.match(r"(\d+)\s*(Years?)\b", raw, re.I)
        pred = {"kind": "age", "comparator": cmp_, "value": float(m.group(1)), "unit": "a", "key": "age",
                "terminology": {"status": "n/a"}} if m else None
        n = _node(ctx, f"/demo/{tag}", "predicate" if pred else "narrative", f"{field}: {raw}", [0, 0],
                  origin="imported_structured", display_number=f"Demo-{tag}", polarity="inclusion",
                  polarity_source="ct.gov structured field", scope=[])
        if pred:
            n.update(predicate=pred, computability="structured_computable")
        else:
            n.update(computability="text_dependent", subtype="age unit not in years")
        out.append(n)
    return out


def inventory(cer, items):
    leaves = []
    for r in cer["criteria"]:
        _walk(r, lambda n: leaves.append(n) if n["type"] != "group" else None)
    by = {}
    for n in leaves:
        k = n.get("computability", "?")
        by[k] = by.get(k, 0) + 1
    return {"criteria_total": len(cer["criteria"]),
            "inclusion": sum(1 for r in cer["criteria"] if r["polarity"] == "inclusion"),
            "exclusion": sum(1 for r in cer["criteria"] if r["polarity"] == "exclusion"),
            "leaf_nodes": len(leaves), "leaves_by_computability": by,
            "typed_predicates": sum(1 for n in leaves if n["type"] == "predicate"),
            "flagged_nodes": sum(1 for r in cer["criteria"] for _ in _flagged(r))}


def _flagged(r):
    stack = [r]
    while stack:
        n = stack.pop()
        if n["flags"]:
            yield n
        stack.extend(n.get("children", []))


def validate(cer, text, items):
    """Structural checks.  Passing means *accounted for*, not *clinically correct*."""
    problems = []
    spans = []
    for r in cer["criteria"]:
        _walk(r, lambda n: spans.append(tuple(n["source_span"])))
    spans = [sp for sp in spans if sp != (0, 0)]
    for sc in cer.get("scope_items", []):
        spans.append(tuple(sc["span"]))
    covered_lines = []
    pos = 0
    for line in text.split("\n"):
        s, e = pos, pos + len(line)
        pos = e + 1
        if not line.strip():
            continue
        if SECTION_LINE(line):
            continue
        inside = any(a <= s and e <= b + 1 for a, b in spans) or any(a <= s < b for a, b in spans)
        if not inside:
            covered_lines.append(line.strip())
    heading_texts = {i.text for i in items if i.kind in ("heading", "hint")}
    orphan = [l for l in covered_lines if not any(h and (h in l or l in h) for h in heading_texts)]
    if orphan:
        problems.append({"code": "UNACCOUNTED_SOURCE_LINES", "detail": orphan})

    def check(n):
        if n["type"] == "group" and not n.get("children"):
            problems.append({"code": "EMPTY_GROUP", "node": n["id"]})
        if n["type"] == "group" and n.get("op") not in ("ALL", "ANY", "NOT", "ATLEAST"):
            problems.append({"code": "BAD_OP", "node": n["id"]})
        if n["type"] == "predicate" and "predicate" not in n:
            problems.append({"code": "PREDICATE_WITHOUT_BODY", "node": n["id"]})
    for r in cer["criteria"]:
        _walk(r, check)
        if r.get("polarity") not in ("inclusion", "exclusion"):
            problems.append({"code": "NO_POLARITY", "node": r["id"]})
    ids = []
    for r in cer["criteria"]:
        _walk(r, lambda n: ids.append(n["id"]))
    if len(ids) != len(set(ids)):
        problems.append({"code": "DUPLICATE_IDS"})
    return {"structure_ok": not problems, "problems": problems,
            "meaning": "NOT validated: clinical + informatics review still required for every executable criterion."}


def SECTION_LINE(line):
    from .segment import SECTION_RE
    return bool(SECTION_RE.match(line.strip()))
