"""Reviewer workbench: one self-contained HTML page with every study's CER embedded.

Published as a claude.ai Artifact it uses the `db` + `user` capabilities: each signed-in reviewer writes only
their own decisions (reviews/<their id>/studies/<NCT>), everyone reads all decisions live.  Decisions are pinned
to the criterion text hash, so an amendment makes them stale.  Opened as a plain file it still renders and can
copy decisions as JSON.  `run.py import-review` turns the stored decisions into review/<NCT>.json sidecars.
"""
import glob
import hashlib
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sum(p):
    k = p["kind"]
    if k in ("lab", "measurement"):
        return f"{p['analyte']} {p.get('comparator','')} {p.get('value', 0):g} {p.get('unit') or ''}".strip()
    if k == "age":
        return f"age {p['comparator']} {p['value']:g} years"
    if k in ("ecog", "performance_status"):
        return f"{p.get('scale', 'ECOG')} ∈ {{{', '.join(str(v) for v in p['allowed_values'])}}}"
    if k == "biomarker":
        if p.get("required_state") == "score":
            return f"{p['analyte']} {p.get('score_method','')} {p['comparator']} {p['value']:g}{p.get('unit') or ''}"
        return f"{p['analyte']} {p.get('alteration','')}: {p['required_state']}"
    if k == "condition":
        return p["concept"]
    return k


def _node(n):
    o = {"t": n["type"]}
    if n["type"] == "group":
        o["op"] = n["op"]
        o["ch"] = [_node(c) for c in n["children"]]
    elif n["type"] == "predicate":
        o["k"] = n["predicate"]["kind"]
        o["s"] = _sum(n["predicate"])
        b = n.get("binding")
        if b and b.get("canonical_binding"):
            cb = b["canonical_binding"]
            o["b"] = {"sys": cb["primary"]["system"], "code": cb["primary"]["code"], "disp": cb["primary"]["display"],
                      "rel": b["mapping_semantics"]["relationship"]}
        elif b:
            o["b"] = {"rel": "no-map"}
    else:
        o["c"] = n["computability"]
        o["sub"] = n.get("subtype") or ""
        o["q"] = n["text"]
    tw = n.get("time_window")
    if tw:
        o["tw"] = f"{tw.get('value', 0):g} {tw.get('unit','')} before {tw.get('anchor','?')}"
    if n.get("exceptions"):
        o["ex"] = [e["text"] for e in n["exceptions"]]
    if n.get("applicability"):
        o["if"] = n["applicability"]["condition"]
    if n.get("flags"):
        o["f"] = n["flags"]
    return o


def study_payload(cer, release_manifest=None):
    crit = []
    for r in cer["criteria"]:
        prov = r.get("proposal_provenance")
        crit.append({"num": r["display_number"], "pol": r["polarity"], "scope": r.get("scope") or [], "cat": r.get("category"),
                     "text": r["text"], "sha": hashlib.sha256(r["text"].encode()).hexdigest(), "origin": r["origin"],
                     "tree": _node(r),
                     "llm": ({"model": prov.get("model_served"), "confidence": prov.get("confidence"),
                              "uncertainties": prov.get("uncertainties") or []} if prov else None)})
    s = cer["source"]
    return {"nct": s["nct_id"], "title": s.get("title"), "status": s.get("overall_status"), "sha": s["content_sha256"],
            "lifecycle": cer["lifecycle"]["status"], "disclosure": cer["completeness_disclosure"],
            "conflicts": [{"field": c["assertions"][0]["field"], "registry": c["assertions"][0]["value"],
                           "text": c["assertions"][1]["value"], "criterion": c["assertions"][1].get("criterion"),
                           "status": c["status"]} for c in cer.get("conflicts", [])],
            "release": ({"id": release_manifest["release_id"][:12], "status": release_manifest["status"],
                         "blocking": release_manifest["blocking_reasons"]} if release_manifest else None),
            "criteria": crit}


def build_payload(cers):
    studies = []
    for cer in cers:
        nct = cer["source"]["nct_id"]
        idx = os.path.join(HERE, "out", "releases", nct, "index.json")
        man = None
        if os.path.exists(idx):
            last = json.load(open(idx))["releases"][-1]["release_id"][:12]
            mp = os.path.join(HERE, "out", "releases", nct, last, "manifest.json")
            man = json.load(open(mp)) if os.path.exists(mp) else None
        studies.append(study_payload(cer, man))
    return {"schema": "workbench-1", "studies": studies}


def render(payload):
    tpl = open(os.path.join(HERE, "cer", "workbench_template.html"), encoding="utf-8").read()
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return tpl.replace("/*__DATA__*/null", data)


VALID_DECISIONS = {"approve", "needs_change", "reject"}
VALID_ROLES = {"clinical", "informatics"}


def import_reviews(dump, known):
    """dump: {"reviews": {reviewer_id: {NCT: {"decisions": {criterion: {...}}}}}} (rows written by viewers -> untrusted).
    known: {NCT: {criterion: text_sha}}.  Returns ({NCT: sidecar}, rejected rows)."""
    out, bad = {}, []
    for uid, studies in (dump.get("reviews") or {}).items():
        if not isinstance(studies, dict) or not isinstance(uid, str) or len(uid) > 200:
            bad.append({"reviewer": str(uid)[:40], "why": "malformed reviewer entry"}); continue
        for nct, doc in studies.items():
            if nct not in known or not isinstance(doc, dict):
                bad.append({"reviewer": uid, "study": str(nct)[:20], "why": "unknown study"}); continue
            for num, d in (doc.get("decisions") or {}).items():
                ok = (isinstance(d, dict) and num in known[nct] and d.get("role") in VALID_ROLES
                      and d.get("decision") in VALID_DECISIONS and isinstance(d.get("sha"), str) and len(d["sha"]) == 64
                      and isinstance(d.get("comment", ""), str) and len(d.get("comment", "")) <= 4000)
                if not ok:
                    bad.append({"reviewer": uid, "study": nct, "criterion": str(num)[:40], "why": "invalid decision row"}); continue
                out.setdefault(nct, {"decisions": []})["decisions"].append({
                    "criterion": num, "role": d["role"], "decision": d["decision"], "reviewer": uid,
                    "date": str(d.get("ts", ""))[:32], "comment": d.get("comment", ""), "criterion_text_sha256": d["sha"]})
    for sc in out.values():
        sc["decisions"].sort(key=lambda x: x["date"])          # later decisions supersede earlier ones
    return out, bad
