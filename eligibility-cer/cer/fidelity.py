"""Protocol -> CER fidelity metrics against an adjudicated reference set (plan sections 1, 6).

Reports criterion accounting, predicate precision/recall/F1 with Wilson 95% CIs and denominators, and counts of
CRITICAL discrepancies (polarity inversion, changed ALL/ANY scope, wrong numeric boundary, omission, spurious logic).
NOTE: numbers are only meaningful against an INDEPENDENTLY adjudicated reference.  The bundled example reference is
authored by the same assistant that wrote the proposals and is flagged `independent: false`; it exercises the plumbing only.

reference/NCT*.json: {"independent": bool, "adjudicators": [...],
  "criteria": [{"criterion": "Inc-b5", "polarity": "inclusion", "op": "ALL|ANY|NOT|null", "leaves": [ {kind, analyte?, concept?, comparator?, value?, allowed_values?, required_state?} ]}]}
"""
import math


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0, c - h), 3), round(min(1, c + h), 3))


def _name(p):
    return p.get("analyte") or p.get("concept") or (p.get("scale") if p["kind"] == "performance_status" else "") or ""


def _key(p):
    return (p["kind"], _name(p), p.get("comparator") or "",
            float(p["value"]) if p.get("value") is not None else None, tuple(p.get("allowed_values") or ()),
            p.get("required_state") or "")


def _leaves(n):
    if n["type"] == "predicate":
        return [n["predicate"]]
    return [x for c in n.get("children", []) for x in _leaves(c)]


def _top_op(n):
    return n.get("op") if n["type"] == "group" else None


def evaluate_fidelity(cer, ref):
    by = {r["display_number"]: r for r in cer["criteria"]}
    tp = fp = fn = 0
    crit = []
    found = 0
    for rc in ref["criteria"]:
        r = by.get(rc["criterion"])
        if r is None:
            crit.append({"code": "OMISSION", "criterion": rc["criterion"]}); fn += len(rc["leaves"]); continue
        found += 1
        if r["polarity"] != rc["polarity"]:
            crit.append({"code": "POLARITY_INVERSION", "criterion": rc["criterion"]})
        if rc.get("op") and _top_op(r) not in (rc["op"], None) or (rc.get("op") and _top_op(r) is None and len(rc["leaves"]) > 1):
            crit.append({"code": "AND_OR_SCOPE_CHANGED", "criterion": rc["criterion"], "expected": rc["op"], "got": _top_op(r)})
        got = {_key(p) for p in _leaves(r)}
        exp = {_key(p) for p in rc["leaves"]}
        tp += len(got & exp); fp += len(got - exp); fn += len(exp - got)
        for g in got - exp:
            same = [e for e in exp - got if e[:2] == g[:2]]
            if same:
                crit.append({"code": "WRONG_BOUNDARY_OR_VALUE", "criterion": rc["criterion"], "got": str(g), "expected": str(same[0])})
            else:
                crit.append({"code": "SPURIOUS_PREDICATE", "criterion": rc["criterion"], "got": str(g)})
    P = tp / (tp + fp) if tp + fp else None
    R = tp / (tp + fn) if tp + fn else None
    F = 2 * P * R / (P + R) if P and R else None
    return {"nct_id": cer["source"]["nct_id"], "reference_independent": bool(ref.get("independent")),
            "warning": None if ref.get("independent") else "reference is NOT independently adjudicated: plumbing check only",
            "criterion_accounting": {"found": found, "reference": len(ref["criteria"]),
                                     "recall": found / len(ref["criteria"]) if ref["criteria"] else None, "release_requires": 1.0},
            "predicates": {"tp": tp, "fp": fp, "fn": fn, "precision": P, "precision_ci95": wilson(tp, tp + fp),
                           "recall": R, "recall_ci95": wilson(tp, tp + fn), "f1": F},
            "critical_discrepancies": crit, "release_blocking": bool(crit) or found != len(ref["criteria"])}
