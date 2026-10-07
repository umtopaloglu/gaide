"""Amendment handling: versioned source snapshots, criterion-level diff, impact report.

Each distinct eligibility text is kept in data/history/<NCT>/<sha12>.json (immutable).  `diff_cers(old, new)`
classifies criteria as unchanged / modified / added / removed / renumbered.  Impact: reviews pinned to changed
text become stale (see review.apply_review), LLM proposals for changed text are skipped, CQL/graph are rebuilt and
the release hash changes.  Display numbers can shift in an amendment, so matching uses text first, number second.
"""
import glob
import hashlib
import json
import os
from difflib import SequenceMatcher

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(HERE, "data", "history")


def content_hash(record):
    return hashlib.sha256((record["protocolSection"]["eligibilityModule"].get("eligibilityCriteria") or "").encode()).hexdigest()


def snapshot(record):
    """Store the record under its content hash.  Returns (path, created)."""
    nct = record["protocolSection"]["identificationModule"]["nctId"]
    h = content_hash(record)
    d = os.path.join(HIST, nct)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{h[:12]}.json")
    if os.path.exists(path):
        return path, False
    json.dump(record, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return path, True


def versions(nct):
    """Snapshots ordered by their retrieval time (oldest first)."""
    out = []
    for p in glob.glob(os.path.join(HIST, nct, "*.json")):
        r = json.load(open(p, encoding="utf-8"))
        out.append((r.get("_provenance", {}).get("retrieved_at") or "", p, r))
    return [(p, r) for _, p, r in sorted(out)]


def _h(t):
    return hashlib.sha256(t.encode()).hexdigest()


def diff_cers(old, new):
    o = {r["display_number"]: r for r in old["criteria"]}
    n = {r["display_number"]: r for r in new["criteria"]}
    o_by_text = {_h(r["text"]): k for k, r in o.items()}
    rows, used_old, pending = [], set(), []
    for k, r in n.items():                       # pass 1: identical text (same or new number)
        th = _h(r["text"])
        if k in o and _h(o[k]["text"]) == th:
            rows.append({"change": "unchanged", "new": k, "old": k}); used_old.add(k)
        else:
            pending.append(k)
    rest = []
    for k in pending:
        th = _h(n[k]["text"])
        if th in o_by_text and o_by_text[th] not in used_old:
            rows.append({"change": "renumbered", "new": k, "old": o_by_text[th]}); used_old.add(o_by_text[th])
        else:
            rest.append(k)
    for k in rest:                               # pass 2: same number, different text -> modified; else added
        r = n[k]
        if k in o and k not in used_old:
            sim = SequenceMatcher(None, o[k]["text"], r["text"]).ratio()
            rows.append({"change": "modified", "new": k, "old": k, "similarity": round(sim, 2),
                         "old_text": o[k]["text"], "new_text": r["text"],
                         "polarity_changed": o[k]["polarity"] != r["polarity"]})
            used_old.add(k)
        else:
            rows.append({"change": "added", "new": k, "new_text": r["text"]})
    for k, r in o.items():
        if k not in used_old:
            rows.append({"change": "removed", "old": k, "old_text": r["text"]})
    counts = {}
    for x in rows:
        counts[x["change"]] = counts.get(x["change"], 0) + 1
    return {"nct_id": new["source"]["nct_id"], "from_sha256": old["source"]["content_sha256"],
            "to_sha256": new["source"]["content_sha256"], "counts": counts, "criteria": rows}


def impact(diff, sidecar=None):
    """What must happen because of this amendment."""
    changed = [x for x in diff["criteria"] if x["change"] in ("modified", "added", "removed")]
    renum = [x for x in diff["criteria"] if x["change"] == "renumbered"]
    stale = []
    for d in (sidecar or {}).get("decisions", []):
        hit = next((x for x in changed if d["criterion"] in (x.get("old"), x.get("new"))), None)
        if hit:
            stale.append({"criterion": d["criterion"], "role": d["role"], "decision": d["decision"], "because": hit["change"]})
    actions = []
    if changed:
        actions += ["re-review changed/added criteria (clinical + informatics)", "rebuild CQL/graph; new release hash",
                    "re-evaluate queued candidates against the new release", "keep prior results with their original versions"]
    if renum:
        actions.append("renumbered criteria: identity kept by text match -- move review decisions to the new numbers")
    if any(x.get("polarity_changed") for x in changed):
        actions.insert(0, "POLARITY CHANGED for at least one criterion -- critical review")
    return {"changed": len(changed), "renumbered": len(renum), "stale_review_decisions": stale, "actions": actions,
            "release_blocked_until_re_review": bool(changed)}
