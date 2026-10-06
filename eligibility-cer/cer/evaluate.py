"""Three-valued evaluation of a CER against synthetic patient evidence.

Rules implemented from the reference architecture:
- predicate truth is True / False / None(unknown); technical status kept separately
- missing, stale, inadequate evidence -> unknown, never a clinical negative
- polarity is applied once, at the criterion root: requirement outcome from condition truth
- ALL / ANY / NOT / ATLEAST follow the documented truth tables
- the result is never "eligible": it is a screening disposition for human adjudication
"""
from datetime import date

NA = "NA"


def and3(vals):
    vals = [v for v in vals if v != NA]
    if not vals:
        return NA
    if any(v is False for v in vals):
        return False
    return True if all(v is True for v in vals) else None


def or3(vals):
    vals = [v for v in vals if v != NA]
    if not vals:
        return NA
    if any(v is True for v in vals):
        return True
    return False if all(v is False for v in vals) else None


def not3(v):
    return v if v in (None, NA) else (not v)


def atleast3(vals, n):
    vals = [v for v in vals if v != NA]
    t, u = sum(v is True for v in vals), sum(v is None for v in vals)
    if t >= n:
        return True
    return False if t + u < n else None


def _cmp(a, op, b):
    return {">=": a >= b, "<=": a <= b, ">": a > b, "<": a < b, "=": a == b}[op]


def _fresh(entry, ev, max_age):
    d = entry.get("date")
    if not d:
        return True, None
    age = (date.fromisoformat(ev.get("as_of", date.today().isoformat())) - date.fromisoformat(d)).days
    return (age <= max_age), f"evidence {age}d old (limit {max_age}d)"


def eval_predicate(p, ev, max_age=90):
    """-> (truth, reason)"""
    key, k = p["key"], p["kind"]
    if k == "age":
        a = ev.get("age")
        return (None, "age not supplied") if a is None else (_cmp(a, p["comparator"], p["value"]), f"age={a}")
    if k == "ecog":
        e = ev.get("ecog")
        if e is None:
            return None, "ECOG not documented"
        ok, why = _fresh(e, ev, max_age) if isinstance(e, dict) else (True, None)
        v = e["value"] if isinstance(e, dict) else e
        return (None, f"ECOG stale: {why}") if not ok else (v in p["allowed_values"], f"ECOG={v}")
    if k in ("lab", "measurement"):
        e = ev.get("labs", {}).get(p["analyte"])
        if not e:
            return None, f"no {p['analyte']} result"
        if e.get("status", "final") != "final":
            return None, f"{p['analyte']} result status '{e.get('status')}'"
        ok, why = _fresh(e, ev, max_age)
        if not ok:
            return None, f"{p['analyte']} stale: {why}"
        thr = p["value"]
        if p.get("uln_multiple"):
            if "uln" not in e:
                return None, f"{p['analyte']} has no result-specific ULN"
            thr = p["value"] * e["uln"]
        return _cmp(e["value"], p["comparator"], thr), f"{p['analyte']}={e['value']} vs {p['comparator']}{thr:g}"
    if k == "biomarker":
        e = ev.get("biomarkers", {}).get(p["analyte"])
        if not e or e.get("state") in (None, "not_tested", "unknown"):
            return None, f"{p['analyte']}: not tested / no report (not a negative)"
        if p["required_state"] == "score":
            if e.get("score") is None:
                return None, f"{p['analyte']}: no score"
            return _cmp(e["score"], p["comparator"], p["value"]), f"{p['analyte']} score={e['score']}"
        if e["state"] == "absent" and not e.get("adequate", False):
            return None, f"{p['analyte']}: negative result lacks adequacy (assay/specimen) -> unresolved"
        return (e["state"] == p["required_state"]), f"{p['analyte']} {e['state']}"
    if k == "condition":
        f = ev.get("facts", {}).get(key)
        return (None, f"no coded evidence for '{p['concept']}'") if f is None else (bool(f), f"{key}={f}")
    return None, "unsupported predicate kind"


def eval_node(n, ev):
    """-> (truth for the node's *condition*, reason).  An exception or temporal anchor that is not
    executable keeps a positive result unresolved (it could be an excepted / out-of-window case)."""
    v, why = _eval_core(n, ev)
    if v is True and (n.get("exceptions") or n.get("time_window", {}).get("status") not in (None, "parsed")):
        return None, "exception / unresolved temporal anchor not executable -> unresolved. " + why
    return v, why


def _eval_core(n, ev):
    if n.get("applicability"):
        f = ev.get("facts", {}).get(n["applicability"]["key"])
        if f is None:
            return None, f"applicability unresolved: '{n['applicability']['condition']}'"
        if not f:
            return NA, f"not applicable ({n['applicability']['condition']}=false)"
    t = n["type"]
    if t == "predicate":
        return eval_predicate(n["predicate"], ev)
    if t == "narrative":
        why = {"human_judgment": "human judgement required", "text_dependent": "needs narrative evidence review"}[n["computability"]]
        return None, why
    kids = [eval_node(c, ev) for c in n["children"]]
    vals = [k[0] for k in kids]
    op = n["op"]
    v = and3(vals) if op == "ALL" else or3(vals) if op == "ANY" else not3(vals[0]) if op == "NOT" else atleast3(vals, n.get("n", 1))
    return v, "; ".join(r for _, r in kids if r)[:300]


def requirement_outcome(truth, polarity):
    if truth == NA:
        return "not_applicable"
    if truth is None:
        return "unresolved"
    if polarity == "inclusion":
        return "satisfied" if truth else "violated"
    return "violated" if truth else "satisfied"


def evaluate(cer, ev, scope=None):
    scopes = cer["scopes"]
    roots = cer["criteria"]
    multi = [s for s in scopes if s]
    if multi and scope is None:
        raise ValueError(f"this CER has scopes {['/'.join(s) for s in multi]}; pass scope=...")
    sel = [r for r in roots if not r["scope"] or (scope and any(scope.lower() in s.lower() for s in r["scope"]))]
    rows = []
    for r in sel:
        # nested requirement children (inside an item) are conditions; evaluate the root expression
        truth, why = eval_node(r, ev)
        # carry the exact polarity-applied outcome per root
        out = requirement_outcome(truth, r["polarity"])
        unverified = [f for f in r["flags"] if "flat list" in f or "branch heading" in f]
        if out == "violated" and unverified:
            out, why = "unresolved", "violation downgraded: item grouping/branch scope unverified (" + unverified[0][:60] + "…). " + why
        rows.append({"id": r["id"], "number": r.get("display_number"), "polarity": r["polarity"],
                     "text": r["text"][:140], "condition_truth": {True: "true", False: "false", None: "unknown", NA: "n/a"}[truth],
                     "outcome": out, "reason": why,
                     "computability": r.get("computability") or "composite"})
    violated = [x for x in rows if x["outcome"] == "violated"]
    unresolved = [x for x in rows if x["outcome"] == "unresolved"]
    if violated:
        disp = "screen_out_supported_by_adequate_evidence"
    elif unresolved:
        disp = "candidate_with_unresolved_requirements"
    else:
        disp = "all_requirements_satisfied_pending_adjudication"
    if cer["lifecycle"]["status"] != "released":
        disp = "DRAFT-PROVISIONAL: " + disp
    return {"nct_id": cer["source"]["nct_id"], "scope": scope, "disposition": disp,
            "determining_criteria": [x["number"] for x in violated],
            "counts": {"satisfied": sum(x["outcome"] == "satisfied" for x in rows), "violated": len(violated),
                       "unresolved": len(unresolved), "not_applicable": sum(x["outcome"] == "not_applicable" for x in rows)},
            "note": "Screening disposition only. Not an eligibility or enrollment decision.", "criteria": rows}
