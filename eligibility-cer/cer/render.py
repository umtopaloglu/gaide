"""Render a CER (optionally with evaluation results) as a single self-contained HTML page."""
import html
import json

CSS = """
:root{--bg:#fff;--fg:#1c2330;--mut:#667085;--line:#e4e7ec;--card:#f8fafc;--inc:#067647;--exc:#b42318;--warn:#b54708;--acc:#175cd3}
@media (prefers-color-scheme:dark){:root{--bg:#0f1420;--fg:#e6e9f0;--mut:#98a2b3;--line:#2a3142;--card:#161c2b;--inc:#47cd89;--exc:#f97066;--warn:#fdb022;--acc:#84adff}}
body{background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif;margin:0;padding:16px;max-width:1100px;margin-inline:auto}
h1{font-size:20px;margin:0 0 4px}h2{font-size:16px;margin:24px 0 8px}.mut{color:var(--mut)}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:8px 0}
.node{border-left:3px solid var(--line);margin:6px 0 6px 6px;padding:2px 0 2px 10px}
.root.inclusion{border-left-color:var(--inc)}.root.exclusion{border-left-color:var(--exc)}
.b{display:inline-block;font-size:11px;border:1px solid var(--line);border-radius:10px;padding:0 7px;margin-right:4px;white-space:nowrap}
.b.inc{color:var(--inc)}.b.exc{color:var(--exc)}.b.op{color:var(--acc);font-weight:600}.b.warn{color:var(--warn)}
.flag{color:var(--warn);font-size:12px}code{font-size:12px;background:var(--card);padding:1px 4px;border-radius:4px}
.src{color:var(--mut);font-size:12px}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top;font-size:13px}
.ok{color:var(--inc)}.bad{color:var(--exc)}.unk{color:var(--warn)}
"""


def e(x):
    return html.escape(str(x))


def pred_str(p):
    k = p["kind"]
    if k in ("lab", "measurement"):
        u = p.get("unit") or ""
        return f"{p['analyte']} {p['comparator']} {p['value']:g} {u}"
    if k == "age":
        return f"age {p['comparator']} {p['value']:g} y"
    if k == "ecog":
        return f"ECOG ∈ {p['allowed_values']}"
    if k == "biomarker":
        if p["required_state"] == "score":
            return f"{p['analyte']} {p.get('score_method','')} {p['comparator']} {p['value']:g}{p['unit']}"
        return f"{p['analyte']} {p['alteration']} : {p['required_state']}"
    if k == "condition":
        return f"condition: {p['concept']}"
    return k


def node_html(n, root=False):
    bits = []
    if root:
        bits.append(f"<span class='b {'inc' if n['polarity']=='inclusion' else 'exc'}'>{e(n['polarity'])}</span>")
        bits.append(f"<b>{e(n.get('display_number',''))}</b> ")
    if n["type"] == "group":
        bits.append(f"<span class='b op'>{e(n['op'])}</span><span class='b'>{e(n.get('logic_basis',''))}</span>")
    elif n["type"] == "predicate":
        bits.append(f"<span class='b op'>{e(n['predicate']['kind'])}</span><code>{e(pred_str(n['predicate']))}</code>")
    else:
        bits.append(f"<span class='b warn'>{e(n['computability'])}</span><span class='b'>{e(n.get('subtype',''))}</span>")
    if n.get("computability") and n["type"] == "predicate":
        bits.append(f"<span class='b'>{e(n['computability'])}</span>")
    tw = n.get("time_window")
    if tw:
        bits.append(f"<span class='b'>⏱ {tw['value']:g} {e(tw['unit'])} before {e(tw['anchor'])}</span>")
    if n.get("applicability"):
        bits.append(f"<span class='b warn'>if: {e(n['applicability']['condition'])}</span>")
    for x in n.get("exceptions", []):
        bits.append(f"<span class='b warn'>except: {e(x['text'][:60])}</span>")
    for sc in n.get("scope", []):
        bits.append(f"<span class='b'>scope: {e(sc)}</span>")
    out = [f"<div class='node{' root ' + n['polarity'] if root else ''}'>", " ".join(bits)]
    if root or n["type"] != "predicate":
        out.append(f"<div class='src'>“{e(n['text'])}”</div>")
    for f in n["flags"]:
        out.append(f"<div class='flag'>⚑ {e(f)}</div>")
    for c in n.get("children", []):
        out.append(node_html(c))
    out.append("</div>")
    return "".join(out)


def render(cer, evaluations=None):
    s, inv, val = cer["source"], cer["inventory"], cer["validation"]
    h = [f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>CER {e(s['nct_id'])}</title><style>{CSS}</style>"]
    h.append(f"<h1>{e(s['nct_id'])} <span class=mut>· Source B · lifecycle: {e(cer['lifecycle']['status'])}</span></h1><div>{e(s['title'])}</div>")
    h.append(f"<div class='card'><b>Provenance</b> — {e(s['registry'])}, retrieved {e(s['retrieved_at'])} via {e(s['retrieved_via'])}, sha256 <code>{e(s['content_sha256'][:16])}…</code>, baseline: {e(s['protocol_baseline'])}<br>"
             f"<span class=flag>⚑ {e(cer['completeness_disclosure'])}</span><br><span class=flag>⚑ CTRP biomarkers: {e(cer['ctrp_biomarker_contract']['status'])} — {e(cer['ctrp_biomarker_contract']['note'])}</span></div>")
    h.append("<div class='card'><b>Inventory</b> — " + ", ".join(f"{k}: {e(v)}" for k, v in inv.items() if k != 'leaves_by_computability')
             + " | leaves: " + ", ".join(f"{e(k)}={v}" for k, v in inv["leaves_by_computability"].items())
             + f"<br><b>Structure check:</b> <span class='{'ok' if val['structure_ok'] else 'bad'}'>{'passed' if val['structure_ok'] else 'FAILED'}</span> "
             f"<span class=mut>— {e(val['meaning'])}</span>"
             + ("" if val["structure_ok"] else f"<pre>{e(json.dumps(val['problems'], indent=1, ensure_ascii=False))}</pre>") + "</div>")
    if evaluations:
        for ev in evaluations:
            h.append(f"<h2>Patient: {e(ev['patient'])} <span class=mut>(scope: {e(ev.get('scope'))})</span></h2><div class=card><b>{e(ev['disposition'])}</b> {e(ev['counts'])}"
                     f" — determining: {e(ev['determining_criteria'])}<table><tr><th>Criterion</th><th>Outcome</th><th>Condition truth</th><th>Why</th></tr>")
            for r in ev["criteria"]:
                cls = {"satisfied": "ok", "violated": "bad"}.get(r["outcome"], "unk")
                h.append(f"<tr><td>{e(r['number'])}<br><span class=src>{e(r['text'][:90])}</span></td><td class={cls}>{e(r['outcome'])}</td><td>{e(r['condition_truth'])}</td><td>{e(r['reason'][:200])}</td></tr>")
            h.append("</table></div>")
    h.append("<h2>Inclusion criteria</h2>")
    h += [node_html(r, True) for r in cer["criteria"] if r["polarity"] == "inclusion"]
    h.append("<h2>Exclusion criteria</h2>")
    h += [node_html(r, True) for r in cer["criteria"] if r["polarity"] == "exclusion"]
    return "".join(h)
