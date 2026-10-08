"""Terminology normalization layer: source phrase -> reviewed canonical binding (Table 4 of the plan).

* Preserves the source phrase/span; adds canonical binding, cross-links, execution binding, mapping semantics,
  value-set record (frozen expansion + hash), provenance and lifecycle.
* Unmapped is explicit (relationship 'no-map'), never silently dropped and never a clinical negative.
* A bundle that cannot be loaded is a TECHNICAL failure (technical_status), not evidence a criterion is false.
* OMOP concept ids are NOT invented: the execution binding says a site vocabulary snapshot is required.
"""
import hashlib
import json
import os
import re

RELATIONSHIPS = ("equivalent", "broader", "narrower", "inexact", "related", "context-dependent", "no-map")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_BUNDLE = os.path.join(HERE, "terminology", "seed-bundle.json")


class TerminologyUnavailable(Exception):
    pass


def _hash(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_bundle(path=DEFAULT_BUNDLE):
    try:
        b = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise TerminologyUnavailable(str(e))
    for vs in b["value_sets"]:                                   # freeze expansions
        members = sorted(f"{c['system']}|{code}" for c in vs["compose"] for code in c["codes"])
        vs["frozen_expansion"] = {"members": members, "sha256": hashlib.sha256("\n".join(members).encode()).hexdigest(),
                                  "date": b["built"]}
    b["sha256"] = _hash({k: v for k, v in b.items() if k != "sha256"})
    b["_rx"] = [(c, re.compile(r"(?<![A-Za-z0-9])(?:" + "|".join(re.escape(p) for p in c["patterns"]) + r")(?![A-Za-z0-9])",
                                0 if c["role"] == "biomarker" else re.I)) for c in b["concepts"]]
    b["_by_id"] = {c["id"]: c for c in b["concepts"]}
    return b


def _find(bundle, role, text):
    hits = [c for c, rx in bundle["_rx"] if c["role"] == role and rx.search(text)]
    return hits                      # bundle order decides ties; the reviewer sees the relationship + rationale


def _role_and_text(n):
    p = n["predicate"]
    k = p["kind"]
    if k in ("lab", "measurement"):
        return "observation", p["analyte"]
    if k in ("ecog",):
        return "observation", "ECOG"
    if k == "condition":
        return "condition", p["concept"]
    if k == "biomarker":
        return "biomarker", p["analyte"]
    return None, None


def _binding(n, concept, bundle, source_text, now):
    p = n["predicate"]
    src = {"phrase": source_text, "document_span": n["source_span"], "criterion_node": n["id"],
           "source_code": None, "inherited_context": n.get("scope") or []}
    if concept is None:
        return {"source_evidence": src, "canonical_binding": None, "cross_terminology_links": {},
                "execution_binding": {"fhir": None, "omop": None},
                "mapping_semantics": {"relationship": "no-map", "direction": "source_to_target", "context": "no seeded concept"},
                "value_set": None,
                "provenance": {"tool": f"eligibility-cer/terminology {bundle['bundle_version']}", "mapper": "pattern match", "confidence": None,
                               "rationale": "no seed concept matched; requires terminology-lead mapping", "reviewer": None, "status": "unmapped"},
                "lifecycle": {"valid_from": now, "deprecated": None, "impacted_releases": [], "requires_re_review": True}}
    prim = concept["primary"]
    sysu = bundle["code_systems"][prim["system"]]["uri"]
    vs = next((v for v in bundle["value_sets"] if v["concept"] == concept["id"]), None)
    unit = p.get("unit")
    return {"source_evidence": src,
            "canonical_binding": {"concept_id": concept["id"], "semantic_role": concept["role"], "label": concept["label"],
                                  "primary": prim, "code_system_uri": sysu},
            "cross_terminology_links": concept["cross_links"],
            "execution_binding": {"fhir": {"system": sysu, "code": prim["code"], "display": prim["display"],
                                           **({"valueSet": vs["id"]} if vs else {}), **({"ucum_unit": unit} if unit and p["kind"] in ("lab", "measurement") else {})},
                                  "omop": {"status": "requires site vocabulary snapshot",
                                           "note": "map to Standard Concept at the site; concept id 0 / unmapped = unresolved, not negative"}},
            "mapping_semantics": {"relationship": concept["relationship"], "direction": concept["direction"],
                                  "context": concept["rationale"]},
            "value_set": ({"id": vs["id"], "version": vs["version"], "compose": vs["compose"], "hierarchy_policy": vs["hierarchy_policy"],
                           "frozen_expansion": vs["frozen_expansion"], "excluded": vs["excluded"]} if vs else None),
            "provenance": {"tool": f"eligibility-cer/terminology {bundle['bundle_version']}", "mapper": "pattern match (seed bundle)",
                           "confidence": concept["confidence"], "rationale": concept["rationale"], "reviewer": None,
                           "status": "proposed_unreviewed"},
            "lifecycle": {"valid_from": now, "deprecated": None, "impacted_releases": [], "requires_re_review": True}}


def _walk(n, f):
    f(n)
    for c in n.get("children", []):
        _walk(c, f)


def bind_cer(cer, bundle=None, path=DEFAULT_BUNDLE):
    """Attach a binding record to every predicate node.  Returns cer (mutated)."""
    try:
        bundle = bundle or load_bundle(path)
    except TerminologyUnavailable as e:
        cer["terminology"] = {"technical_status": "terminology_unavailable", "detail": str(e),
                              "note": "technical failure: no criterion is evaluated false because of it"}
        return cer
    used, stats = {}, {"bound": 0, "unmapped": 0, "by_relationship": {}}

    def f(n):
        if n["type"] != "predicate":
            return
        role, text = _role_and_text(n)
        if role is None:
            n["binding"] = None
            return
        hits = _find(bundle, role, text)
        b = _binding(n, hits[0] if hits else None, bundle, text, bundle["built"])
        n["binding"] = b
        rel = b["mapping_semantics"]["relationship"]
        stats["by_relationship"][rel] = stats["by_relationship"].get(rel, 0) + 1
        stats["bound" if hits else "unmapped"] += 1
        if b["value_set"]:
            used[b["value_set"]["id"]] = b["value_set"]
        n["predicate"]["terminology"] = {"status": b["provenance"]["status"], "relationship": rel,
                                         **({"system": b["canonical_binding"]["primary"]["system"],
                                             "code": b["canonical_binding"]["primary"]["code"]} if hits else {})}
        if not hits:
            n["flags"] = [x for x in n["flags"] if "terminology" not in x] + ["terminology unmapped (no-map) -> not executable until bound"]
        elif rel in ("inexact", "related", "broader", "narrower", "context-dependent"):
            n["flags"].append(f"mapping relationship '{rel}': {b['mapping_semantics']['context'][:120]}")
    for r in cer["criteria"]:
        _walk(r, f)
    cer["terminology"] = {"bundle_id": bundle["bundle_id"], "bundle_version": bundle["bundle_version"], "sha256": bundle["sha256"],
                          "status": bundle["status"], "warning": bundle["warning"], "stats": stats, "value_sets": used,
                          "licenses": {k: v["license"] for k, v in bundle["code_systems"].items()}}
    return cer
