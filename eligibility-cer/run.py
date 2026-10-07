#!/usr/bin/env python3
"""Source B pilot CLI.

  python run.py fetch NCT06128837 NCT06357533      # needs ct.gov network access
  python run.py search "lung cancer" --n 5          # list candidate NCT ids
  python run.py build [NCT...]                      # data/raw/*.json -> out/*.cer.json + out/*.html
  python run.py propose NCT04547166 [--provider anthropic|replay] [--criteria Exc-4,Exc-5] [--dry-run]
  python run.py graph NCT06520683                   # out/graph/*.jsonld (+ round-trip + SHACL check)
  python run.py review NCT06520683                  # review worklist (+ review/NCT*.json sidecar applied)
  python run.py cql NCT06128837 [--scope S] [--allow-draft]   # -> out/*.cql + manifest
  python run.py evaluate NCT05512364 evidence/x.json --scope "Randomised trial"
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cer.build import build_cer          # noqa: E402
from cer.evaluate import evaluate        # noqa: E402
from cer.render import render            # noqa: E402
from cer.authored import apply_authored  # noqa: E402
from cer.review import apply_review, worklist  # noqa: E402
from cer.cql import compile_cql          # noqa: E402
from cer.terminology import bind_cer     # noqa: E402
from cer.conflicts import detect         # noqa: E402
from cer import graph as G               # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RAW, OUT = os.path.join(HERE, "data", "raw"), os.path.join(HERE, "out")


def load(nct):
    with open(os.path.join(RAW, f"{nct}.json"), encoding="utf-8") as f:
        return json.load(f)


def apply_llm_proposals(cer, d):
    """Overlay LLM proposals.  Hand-authored proposals win; proposals whose criterion text changed are stale -> skipped."""
    import hashlib
    texts = {r["display_number"]: r["text"] for r in cer["criteria"]}
    stale = {k for k, v in d["results"].items()
             if v.get("criterion_text_sha256") != hashlib.sha256(texts.get(k, "").encode()).hexdigest()}
    prov = {k: {"run": d["run"], **{f: v.get(f) for f in ("model_served", "request_id", "confidence", "uncertainties")}}
            for k, v in d["results"].items()}
    return apply_authored(cer, d["proposals"], origin="llm_proposal",
                          skip=set(cer.get("authored_applied", [])) | stale, provenance=prov)


def load_cer(nct):
    """rule-based draft + authored proposals + review sidecar (all optional)"""
    cer = build_cer(load(nct))
    ap = os.path.join(HERE, "authored", f"{nct}.json")
    cer["authored_applied"] = apply_authored(cer, json.load(open(ap, encoding="utf-8"))) if os.path.exists(ap) else []
    lp = os.path.join(HERE, "proposals", "llm", f"{nct}.json")
    cer["llm_applied"] = apply_llm_proposals(cer, json.load(open(lp, encoding="utf-8"))) if os.path.exists(lp) else []
    bind_cer(cer)
    cer["conflicts"] = detect(cer)
    rp = os.path.join(HERE, "review", f"{nct}.json")
    return apply_review(cer, json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else {})


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("ncts", nargs="+")
    s = sub.add_parser("search"); s.add_argument("condition"); s.add_argument("--n", type=int, default=10); s.add_argument("--phase")
    b = sub.add_parser("build"); b.add_argument("ncts", nargs="*")
    gp = sub.add_parser("graph"); gp.add_argument("nct")
    pp = sub.add_parser("propose"); pp.add_argument("nct"); pp.add_argument("--provider"); pp.add_argument("--model")
    pp.add_argument("--criteria", help="comma-separated display numbers (default: narrative/flagged criteria)")
    pp.add_argument("--dry-run", action="store_true", help="print the prompt and schema for the first target; no API call")
    w = sub.add_parser("review"); w.add_argument("nct")
    c = sub.add_parser("cql"); c.add_argument("nct"); c.add_argument("--scope"); c.add_argument("--allow-draft", action="store_true")
    v = sub.add_parser("evaluate"); v.add_argument("nct"); v.add_argument("evidence"); v.add_argument("--scope")
    a = ap.parse_args(argv)
    os.makedirs(RAW, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    if a.cmd == "fetch":
        from cer.fetch import fetch_study
        for n in a.ncts:
            d = fetch_study(n)
            json.dump(d, open(os.path.join(RAW, f"{n}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("saved", n)
    elif a.cmd == "search":
        from cer.fetch import search
        for n, t in search(a.condition, phase=a.phase, n=a.n):
            print(n, t[:100])
    elif a.cmd == "build":
        ncts = a.ncts or sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(RAW, "NCT*.json")))
        for n in ncts:
            cer = load_cer(n)
            evs = []
            for p in sorted(glob.glob(os.path.join(HERE, "evidence", f"{n}_*.json"))):
                ev = json.load(open(p)); scope = ev.pop("_scope", None)
                r = evaluate(cer, ev, scope); r["patient"] = ev.get("_patient") or os.path.basename(p); evs.append(r)
            json.dump(cer, open(os.path.join(OUT, f"{n}.cer.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            open(os.path.join(OUT, f"{n}.html"), "w", encoding="utf-8").write(render(cer, evs))
            i = cer["inventory"]
            print(f"{n}: {i['criteria_total']} criteria ({i['inclusion']} inc / {i['exclusion']} exc), "
                  f"{i['typed_predicates']} typed predicates, leaves={i['leaves_by_computability']}, "
                  f"flagged={i['flagged_nodes']}, structure_ok={cer['validation']['structure_ok']}")
    elif a.cmd == "propose":
        from cer.llm import get_provider
        from cer.llm.proposer import SYSTEM, default_targets, proposal_schema, propose, user_prompt
        cer = build_cer(load(a.nct))
        ap = os.path.join(HERE, "authored", f"{a.nct}.json")
        if os.path.exists(ap):
            apply_authored(cer, json.load(open(ap, encoding="utf-8")))
        targets = a.criteria.split(",") if a.criteria else default_targets(cer)
        if a.dry_run:
            by = {r["display_number"]: r for r in cer["criteria"]}
            print("SYSTEM:\n" + SYSTEM + "\n\nUSER:\n" + user_prompt(by[targets[0]]))
            print(f"\nSCHEMA bytes: {len(json.dumps(proposal_schema()))}; targets ({len(targets)}): {', '.join(targets)}")
            return
        prov = get_provider(a.provider, model=a.model)
        out = propose(cer, prov, targets)
        path = os.path.join(HERE, "proposals", "llm", f"{a.nct}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(out, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        st = {}
        for v in out["results"].values():
            st[v["status"]] = st.get(v["status"], 0) + 1
        print(f"wrote {path}: {st}")
    elif a.cmd == "graph":
        cer = load_cer(a.nct)
        txt, h, gid = G.to_jsonld(cer)
        os.makedirs(os.path.join(OUT, "graph"), exist_ok=True)
        path = os.path.join(OUT, "graph", f"{a.nct}.release.jsonld")
        open(path, "w", encoding="utf-8").write(txt)
        back = G.from_jsonld(txt)
        rt = json.dumps(back, sort_keys=True) == json.dumps(cer, sort_keys=True)
        ok, rep = G.validate_shacl(txt)
        print(f"{a.nct}: wrote {path}  canonical_hash={h[:16]}  round_trip_lossless={rt}  shacl_conforms={ok}")
        if not ok:
            print(rep)
    elif a.cmd == "review":
        cer = load_cer(a.nct)
        for c in cer.get("conflicts", []):
            print(f"CONFLICT [{c['status']}] {c['assertions'][0]['field']} {c['assertions'][0]['value']} vs narrative {c['assertions'][1]['value']}")
        print(f"{a.nct}  lifecycle={cer['lifecycle']['status']}  validated={cer['review_summary']['validated']}/{cer['review_summary']['criteria']}")
        for r in worklist(cer):
            print(f"{r['criterion']:<14}{r['polarity'][:3]} {r['origin']:<20}{r['status']:<18}preds={r['typed_predicates']} flags={r['flagged_nodes']}  {r['text']}")
    elif a.cmd == "cql":
        cer = load_cer(a.nct)
        text, man = compile_cql(cer, a.scope, a.allow_draft)
        base = os.path.join(OUT, f"{man['library']}")
        open(base + ".cql", "w", encoding="utf-8").write(text)
        json.dump(man, open(base + ".manifest.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"wrote {base}.cql  gated={man['gated']} executable_leaves={man['executable_typed_leaves']} unsupported={len(man['unsupported'])}")
    elif a.cmd == "evaluate":
        cer = load_cer(a.nct); ev = json.load(open(a.evidence))
        print(json.dumps(evaluate(cer, ev, a.scope), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
