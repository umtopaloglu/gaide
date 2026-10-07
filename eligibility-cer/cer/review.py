"""Review sidecar: dual sign-off (clinical + informatics) per executable criterion.

review/NCT*.json = {"decisions": [{"criterion": "Inc-b2", "role": "clinical|informatics",
                    "decision": "approve|reject|needs_change", "reviewer": "...", "date": "YYYY-MM-DD", "comment": "..."}],
                    "release": {"authorized_by": "...", "date": "..."}}   # optional
Nothing here is auto-approved.  A criterion is `validated` only with an approve from BOTH roles and no
later reject/needs_change; the CER is `validated` only when every criterion that is not pure narrative
is validated; it is `released` only with an explicit release block on a validated CER.
"""
ROLES = ("clinical", "informatics")


def text_hash(text):
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()


def apply_review(cer, sidecar):
    """Decisions pinned to a criterion text (criterion_text_sha256) only count while that text is unchanged:
    after an amendment they become STALE and the criterion needs review again.  Unpinned decisions still count
    but are reported; decisions for criteria that no longer exist are reported as orphaned."""
    texts = {r.get("display_number"): text_hash(r["text"]) for r in cer["criteria"]}
    latest, stale, orphaned, unpinned = {}, [], [], []
    for d in sidecar.get("decisions", []):
        if d["criterion"] not in texts:
            orphaned.append(d); continue
        pin = d.get("criterion_text_sha256")
        if pin and pin != texts[d["criterion"]]:
            stale.append(d); continue
        if not pin:
            unpinned.append(d["criterion"])
        latest[(d["criterion"], d["role"])] = d          # later entries supersede earlier ones
    pending, validated = [], 0
    for r in cer["criteria"]:
        num = r.get("display_number")
        st = {role: latest.get((num, role), {}).get("decision") for role in ROLES}
        if any(v in ("reject", "needs_change") for v in st.values()):
            r["review_status"] = "changes_requested"
        elif all(v == "approve" for v in st.values()):
            r["review_status"] = "validated"; validated += 1
        elif any(st.values()):
            r["review_status"] = "partially_reviewed"
        r["review"] = {role: latest.get((num, role)) for role in ROLES if latest.get((num, role))}
        if r["review_status"] != "validated":
            pending.append(num)
    res = {x["conflict"]: x for x in sidecar.get("conflict_resolutions", [])}
    open_conf = []
    for c in cer.get("conflicts", []):
        r = res.get(c["id"])
        if r and r.get("outcome") and r.get("adjudicator"):
            c["status"] = "resolved"; c["adjudication"].update(outcome=r["outcome"], clinical_owner=r["adjudicator"])
        elif c["blocks_release"]:
            open_conf.append(c["id"])
    cer["review_summary"] = {"open_conflicts": open_conf, "stale_decisions": stale, "orphaned_decisions": orphaned,
                             "unpinned_decisions": sorted(set(unpinned)), "criteria": len(cer["criteria"]), "validated": validated, "pending": pending}
    status = "draft"
    if validated == len(cer["criteria"]) and open_conf:
        status = "in_review"                                      # material open registry conflict blocks release
    elif validated == len(cer["criteria"]):
        status = "validated"
        if sidecar.get("release", {}).get("authorized_by"):
            status = "released"; cer["lifecycle"]["release"] = sidecar["release"]
    elif validated or any(r["review_status"] != "needs_review" for r in cer["criteria"]):
        status = "in_review"
    cer["lifecycle"]["status"] = status
    cer["lifecycle"]["note"] = {"released": "Released by an explicit authorization record.",
        "validated": "All criteria dual-approved; awaiting release authorization (not yet executable for screening).",
        "in_review": "Review in progress" + (" (blocked by open registry conflict)." if open_conf else "."), "draft": "Draft only: not reviewed; not executable for screening."}[status]
    return cer


def worklist(cer):
    """Review queue, riskiest first: flagged, authored/typed content, then the rest."""
    rows = []
    def count(n, key):
        c = 1 if key(n) else 0
        return c + sum(count(k, key) for k in n.get("children", []))
    for r in cer["criteria"]:
        flags = count(r, lambda n: bool(n["flags"]))
        origin = r["origin"]
        kinds = {"x": 0}
        def walk(n):
            if n["type"] == "predicate": kinds["x"] += 1
            for k in n.get("children", []): walk(k)
        walk(r)
        rows.append({"criterion": r.get("display_number"), "polarity": r["polarity"], "origin": origin,
                     "typed_predicates": kinds["x"], "flagged_nodes": flags, "status": r["review_status"],
                     "text": r["text"][:100]})
    rows.sort(key=lambda x: (x["status"] == "validated", -(x["typed_predicates"] > 0), -x["flagged_nodes"]))
    return rows
