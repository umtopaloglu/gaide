"""Typed registry-conflict records (plan section 1).  A conflict NEVER overwrites the CER.

Detected here: ct.gov *structured* age fields vs age limits stated in the eligibility *narrative* of the same record.
Each record holds both assertions, source locations, timestamps and affected artifacts; a material open conflict
blocks release (see review.apply_review).  Owners: sponsor/coordinating-centre clinical owner adjudicates intent;
terminology lead adjudicates mapping semantics; registry steward corrects the record or documents the exception.
"""
import uuid


def _walk(n, f):
    f(n)
    for c in n.get("children", []):
        _walk(c, f)


def detect(cer):
    demo = {r["display_number"]: r["predicate"] for r in cer["criteria"] if r.get("origin") == "imported_structured" and r["type"] == "predicate"}
    out = []
    ts = cer["source"].get("retrieved_at")
    for r in cer["criteria"]:
        if r.get("origin") == "imported_structured":
            continue
        def f(n):
            if n["type"] != "predicate" or n["predicate"]["kind"] != "age":
                return
            p = n["predicate"]
            field = "Demo-min-age" if p["comparator"] in (">=", ">") else "Demo-max-age" if p["comparator"] in ("<=", "<") else None
            d = demo.get(field)
            if d and (d["value"] != p["value"] or d["comparator"] != p["comparator"]):
                out.append({
                    "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"conflict|{cer['source']['nct_id']}|{n['id']}|{field}")),
                    "type": "registry_structured_vs_narrative", "severity": "material", "status": "open", "blocks_release": True,
                    "assertions": [
                        {"source": "ClinicalTrials.gov structured field", "field": "minimumAge" if field == "Demo-min-age" else "maximumAge",
                         "value": f"{d['comparator']} {d['value']:g} years", "location": field},
                        {"source": "eligibility narrative", "value": f"{p['comparator']} {p['value']:g} years", "node": n["id"],
                         "criterion": r.get("display_number"), "source_span": n["source_span"], "text": n["text"][:160]}],
                    "detected_at": ts, "affected_artifacts": [n["id"], cer["source"]["nct_id"]],
                    "adjudication": {"clinical_owner": None, "terminology_lead": None, "registry_steward": None, "outcome": None},
                    "policy": "approved protocol controls; do not silently prefer the structured or the narrative value"})
        _walk(r, f)
    return out
