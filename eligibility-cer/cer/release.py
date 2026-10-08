"""Immutable release packages (plan: "an approved API or controlled export distributes immutable, integrity-checked releases").

out/releases/<NCT>/<release_id12>/  contains every artifact + manifest.json with a SHA-256 per file.
release_id = SHA-256 over the sorted (path, file hash) list, so identical content -> identical id (idempotent).
A package is `released` only when the CER lifecycle is `released`; otherwise it is a `candidate` and the manifest
lists every reason it may not be used for screening.  `verify_release(dir)` detects any later modification.
"""
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone

from . import graph as G
from .cql import compile_cql

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def blocking_reasons(cer):
    r = []
    lc = cer["lifecycle"]["status"]
    if lc != "released":
        r.append(f"lifecycle is '{lc}', not 'released'")
    rs = cer.get("review_summary", {})
    if rs.get("pending"):
        r.append(f"{len(rs['pending'])} criteria not dual-approved")
    if rs.get("open_conflicts"):
        r.append(f"{len(rs['open_conflicts'])} open registry conflict(s)")
    if rs.get("stale_decisions"):
        r.append(f"{len(rs['stale_decisions'])} review decision(s) stale after a text change")
    if not cer["validation"]["structure_ok"]:
        r.append("structure validation failed")
    t = cer.get("terminology", {})
    if t.get("technical_status"):
        r.append(f"terminology: {t['technical_status']}")
    elif t.get("status") == "UNREVIEWED_SEED":
        r.append("terminology bundle is an unreviewed seed")
    return r


def _artifacts(cer, extra_files):
    files = {}
    files["cer.json"] = json.dumps(cer, sort_keys=True, ensure_ascii=False, indent=1).encode()
    txt, ghash, _ = G.to_jsonld(cer)
    files["graph.release.jsonld"] = txt.encode()
    scopes = [None] + sorted({s[0] for s in cer["scopes"] if s})
    caps = {}
    for sc in scopes:
        cql, man = compile_cql(cer, sc)                       # gated: only validated criteria compile
        stem = man["library"]
        files[f"cql/{stem}.cql"] = cql.encode()
        files[f"cql/{stem}.manifest.json"] = json.dumps(man, sort_keys=True, indent=1).encode()
        caps[stem] = man["capability"]["trial_backend_label"]
    for name, path in extra_files.items():
        if path and os.path.exists(path):
            files[name] = open(path, "rb").read()
    return files, ghash, caps


def build_release(cer, out_root=None, extra_files=None):
    nct = cer["source"]["nct_id"]
    out_root = out_root or os.path.join(HERE, "out", "releases")
    files, ghash, caps = _artifacts(cer, extra_files or {})
    hashes = {p: _sha(b) for p, b in sorted(files.items())}
    rid = _sha(json.dumps(sorted(hashes.items())).encode())
    base = os.path.join(out_root, nct)
    idx_path = os.path.join(base, "index.json")
    index = json.load(open(idx_path)) if os.path.exists(idx_path) else {"nct_id": nct, "releases": []}
    d = os.path.join(base, rid[:12])
    if os.path.exists(d):
        ok, problems = verify_release(d)
        if not ok:
            raise RuntimeError(f"existing package {d} was modified: {problems}")
        return d, json.load(open(os.path.join(d, "manifest.json"))), False
    reasons = blocking_reasons(cer)
    prev = index["releases"][-1]["release_id"] if index["releases"] else None
    manifest = {"release_id": rid, "nct_id": nct, "status": "released" if not reasons else "candidate",
                "usable_for_screening": not reasons, "blocking_reasons": reasons,
                "cer_content_sha256": cer["source"]["content_sha256"], "lifecycle": cer["lifecycle"]["status"],
                "graph_canonical_sha256": ghash, "backend_capability": caps,
                "terminology": {k: (cer.get("terminology") or {}).get(k) for k in ("bundle_id", "bundle_version", "sha256", "status", "licenses")},
                "previous_release_id": prev, "rollback_target": prev,
                "effective_interval": {"from": None, "to": None},
                "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "files": hashes,
                "note": "Files are immutable; any change produces a new release id. Patient data is never included."}
    os.makedirs(d)
    for p, b in files.items():
        fp = os.path.join(d, p)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "wb").write(b)
    json.dump(manifest, open(os.path.join(d, "manifest.json"), "w"), indent=1, ensure_ascii=False)
    index["releases"].append({"release_id": rid, "status": manifest["status"], "created": manifest["created"],
                              "cer_content_sha256": manifest["cer_content_sha256"]})
    json.dump(index, open(idx_path, "w"), indent=1)
    return d, manifest, True


def verify_release(d):
    m = json.load(open(os.path.join(d, "manifest.json")))
    problems = []
    for p, h in m["files"].items():
        fp = os.path.join(d, p)
        if not os.path.exists(fp):
            problems.append(f"missing {p}")
        elif _sha(open(fp, "rb").read()) != h:
            problems.append(f"modified {p}")
    present = {os.path.relpath(os.path.join(r, f), d) for r, _, fs in os.walk(d) for f in fs} - {"manifest.json"}
    problems += [f"unexpected {p}" for p in sorted(present - set(m["files"]))]
    if _sha(json.dumps(sorted(m["files"].items())).encode()) != m["release_id"]:
        problems.append("release_id does not match file hashes")
    return not problems, problems
