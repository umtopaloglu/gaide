"""Overlay *authored proposals* onto a rule-based draft CER.

An authored proposal is what the architecture calls the constrained-LLM step: someone (here, Claude
working inside the session) proposes a typed expression tree for a criterion, keyed by display number.
It replaces the rule-based node but keeps source text/span/polarity/scope, is labelled
origin="authored_proposal", and stays review_status="needs_review" -- it is NOT approved content.

Spec grammar (JSON):
  {"op": "ALL|ANY|NOT", "of": [spec, ...]}
  {"p": {predicate fields}, "tw": {...time window...}, "exc": ["..."]}      # typed predicate
  {"narrative": "text_dependent|human_judgment", "subtype": "...", "text": "..."}
"""
import re

from .extract import slug

NA_TERM = {"status": "unmapped"}


def _pred(p):
    p = dict(p)
    k = p["kind"]
    if k == "condition":
        p["key"] = "condition:" + slug(p["concept"])
    elif k in ("lab", "measurement"):
        p["key"] = f"{k}:{slug(p['analyte'])}"
        p.setdefault("uln_multiple", False)
    elif k == "biomarker":
        p["key"] = "biomarker:" + slug(p["analyte"])
        p.setdefault("alteration", "alteration")
        p.setdefault("qualifier_gaps", [])
    elif k == "ecog":
        p["key"] = "ecog"; p.setdefault("scale", "ECOG")
    elif k == "age":
        p["key"] = "age"; p.setdefault("unit", "a")
    p.setdefault("terminology", dict(NA_TERM) if k not in ("age", "ecog") else {"status": "n/a"})
    return p


def _mk(spec, root, path, counter, origin="authored_proposal"):
    counter[0] += 1
    base = {"id": f"{root['id']}#a{counter[0]}", "path": path, "text": root["text"], "source_span": root["source_span"],
            "flags": [], "review_status": "needs_review", "origin": origin}
    if "op" in spec:
        n = dict(base, type="group", op=spec["op"], logic_basis="authored",
                 children=[_mk(c, root, f"{path}.{i}", counter, origin) for i, c in enumerate(spec["of"])])
        if spec["op"] == "NOT" and len(n["children"]) != 1:
            raise ValueError("NOT takes exactly one child")
        return n
    if "p" in spec:
        p = _pred(spec["p"])
        n = dict(base, type="predicate", predicate=p, computability="structured_computable")
        if p["kind"] in ("condition",) or p.get("terminology", {}).get("status") == "unmapped":
            n["flags"].append("terminology unmapped -> not executable until bound")
        if p["kind"] == "biomarker" and p["qualifier_gaps"]:
            n["flags"].append("biomarker qualifiers not stated: " + ", ".join(p["qualifier_gaps"]))
    else:
        n = dict(base, type="narrative", computability=spec["narrative"], subtype=spec.get("subtype", ""))
    if spec.get("text"):
        n["text"] = spec["text"]
    if spec.get("tw"):
        tw = dict(spec["tw"]); tw.setdefault("direction", "lookback"); tw.setdefault("value", None)
        tw["status"] = "parsed" if tw.get("anchor") not in (None, "unspecified") else "anchor_missing_or_unrecognised"
        n["time_window"] = tw
        if tw["status"] != "parsed":
            n["flags"].append("temporal anchor missing -> evaluate as unknown until resolved")
    if spec.get("exc"):
        n["exceptions"] = [{"keyword": "except", "text": t, "status": "unparsed"} for t in spec["exc"]]
    if spec.get("note"):
        n["flags"].append(spec["note"])
    return n


def _walk(n, f):
    f(n)
    for c in n.get("children", []):
        _walk(c, f)


def apply_authored(cer, proposals, origin="authored_proposal", skip=(), provenance=None):
    """proposals: {display_number: spec}.  Returns list of display numbers applied.
    origin: authored_proposal (hand-written) or llm_proposal; skip: criteria not to touch; provenance: per-criterion dict."""
    by = {r.get("display_number"): i for i, r in enumerate(cer["criteria"])}
    done = []
    for num, spec in proposals.items():
        if num.startswith("_") or num in skip:
            continue
        if num not in by:
            raise KeyError(f"authored proposal for unknown criterion {num}")
        old = cer["criteria"][by[num]]
        new = _mk(spec, old, old["path"], [0], origin)
        for k in ("display_number", "polarity", "polarity_source", "scope", "branch_hint"):
            if k in old:
                new[k] = old[k]
        new["id"] = old["id"]                          # identity survives re-interpretation
        new["supersedes_origin"] = old["origin"]
        new["flags"].append(f"{origin.replace('_', ' ')} replaces rule-based parse -> requires clinical + informatics review")
        if provenance and num in provenance:
            new["proposal_provenance"] = provenance[num]
        cer["criteria"][by[num]] = new
        done.append(num)
    return done
