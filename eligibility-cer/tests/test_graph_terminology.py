import copy, glob, json, os, sys, unittest
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import run as R
from cer import graph as G
from cer.conflicts import detect
from cer.fidelity import evaluate_fidelity, wilson
from cer.review import apply_review
from cer.terminology import RELATIONSHIPS, TerminologyUnavailable, bind_cer, load_bundle
from cer.cql import compile_cql
from cer.build import build_cer

NCTS = [os.path.basename(p)[:-5] for p in sorted(glob.glob(os.path.join(HERE, "data", "raw", "NCT*.json")))]


class Terminology(unittest.TestCase):
    def test_bundle_hash_and_frozen_expansion_are_deterministic(self):
        a, b = load_bundle(), load_bundle()
        self.assertEqual(a["sha256"], b["sha256"])
        vs = next(v for v in a["value_sets"] if v["id"] == "vs:cond-hiv")
        self.assertEqual(vs["frozen_expansion"]["members"], ["SNOMED CT|86406008"])
        self.assertEqual(len(vs["frozen_expansion"]["sha256"]), 64)
    def test_every_predicate_gets_a_binding_with_explicit_relationship(self):
        for n in NCTS:
            cer = R.load_cer(n)
            def walk(x):
                if x["type"] == "predicate" and x["predicate"]["kind"] not in ("age", "performance_status"):
                    b = x["binding"]
                    self.assertIn(b["mapping_semantics"]["relationship"], RELATIONSHIPS, n)
                    self.assertEqual(b["source_evidence"]["criterion_node"], x["id"])
                    self.assertIn("status", b["provenance"])
                for c in x.get("children", []):
                    walk(c)
            for r in cer["criteria"]:
                walk(r)
    def test_inexact_mapping_is_flagged_and_unmapped_is_not_dropped(self):
        cer = R.load_cer("NCT06838273")
        flat = []
        def walk(x):
            flat.append(x)
            for c in x.get("children", []):
                walk(c)
        for r in cer["criteria"]:
            walk(r)
        hiv = next(x for x in flat if x["type"] == "predicate" and x["predicate"].get("concept") == "HIV antibody positive")
        self.assertEqual(hiv["binding"]["mapping_semantics"]["relationship"], "inexact")
        self.assertTrue(any("inexact" in f for f in hiv["flags"]))
        self.assertIsNone(hiv["binding"]["execution_binding"]["omop"].get("concept_id"))   # never invented
        unm = [x for x in flat if x["type"] == "predicate" and x.get("binding") and x["binding"]["mapping_semantics"]["relationship"] == "no-map"]
        self.assertTrue(unm and all(x["binding"]["canonical_binding"] is None for x in unm))
    def test_missing_bundle_is_technical_failure_not_false(self):
        cer = build_cer(json.load(open(os.path.join(HERE, "data", "raw", "NCT06357533.json"), encoding="utf-8")))
        bind_cer(cer, path="/nonexistent/bundle.json")
        self.assertEqual(cer["terminology"]["technical_status"], "terminology_unavailable")
        text, man = compile_cql(cer, allow_draft=True)           # no bindings -> leaves unsupported, never false
        self.assertEqual(man["capability"]["trial_backend_label"] in ("unavailable", "partial"), True)


class GraphProfile(unittest.TestCase):
    def test_lossless_round_trip_shacl_and_hash_stability_for_every_study(self):
        for n in NCTS:
            cer = R.load_cer(n)
            txt, h, gid = G.to_jsonld(cer)
            self.assertEqual(json.dumps(G.from_jsonld(txt), sort_keys=True), json.dumps(cer, sort_keys=True), n)
            ok, rep = G.validate_shacl(txt)
            self.assertTrue(ok, rep[:400])
            self.assertEqual(G.to_jsonld(cer)[1], h)
    def test_operand_order_and_grouping_survive(self):
        cer = R.load_cer("NCT06520683")
        back = G.from_jsonld(G.to_jsonld(cer)[0])
        r = next(x for x in back["criteria"] if x["display_number"] == "Inc-b2")
        o = next(x for x in cer["criteria"] if x["display_number"] == "Inc-b2")
        self.assertEqual([c["id"] for c in r["children"][1]["children"]], [c["id"] for c in o["children"][1]["children"]])
        self.assertEqual(r["children"][1]["op"], "ANY")
    def test_hash_changes_when_polarity_changes(self):
        cer = R.load_cer("NCT06357533"); h = G.to_jsonld(cer)[1]
        cer2 = copy.deepcopy(cer); cer2["criteria"][1]["polarity"] = "exclusion"
        self.assertNotEqual(G.to_jsonld(cer2)[1], h)
    def test_shacl_rejects_bad_graphs(self):
        cer = R.load_cer("NCT06520683")
        bad = copy.deepcopy(cer); bad["criteria"][2]["polarity"] = "maybe"
        self.assertFalse(G.validate_shacl(G.to_jsonld(bad)[0])[0])
        bad = copy.deepcopy(cer)
        g = next(r for r in bad["criteria"] if r["type"] == "group"); g["op"] = "XOR"
        self.assertFalse(G.validate_shacl(G.to_jsonld(bad)[0])[0])
        bad = copy.deepcopy(cer); bad["criteria"][2]["source_span"] = None
        with self.assertRaises(Exception):
            G.validate_shacl(G.to_jsonld(bad)[0])
    def test_no_patient_content_in_graph(self):
        txt = G.to_jsonld(R.load_cer("NCT06128837"))[0].lower()
        self.assertNotIn("patient_id", txt); self.assertNotIn("mrn", txt)
    def test_competency_queries(self):
        ds, gid = G.to_dataset(R.load_cer("NCT06838273"))
        pol = {str(r[0]): int(r[1]) for r in G.competency(ds, gid, "criteria_by_polarity")}
        self.assertEqual(set(pol), {"inclusion", "exclusion"})
        self.assertTrue(len(G.competency(ds, gid, "criteria_using_value_set")) >= 3)
        self.assertTrue(len(G.competency(ds, gid, "provenance_of_node")) > 0)
        self.assertTrue(len(G.competency(ds, gid, "unmapped_predicates")) >= 1)


class ConflictsCapabilityFidelity(unittest.TestCase):
    def _rec(self, text, minage="18 Years", maxage=None):
        return {"protocolSection": {"identificationModule": {"nctId": "NCT00000001", "briefTitle": "t"},
                "eligibilityModule": {"eligibilityCriteria": text, "minimumAge": minage, "maximumAge": maxage}}}
    def test_age_conflict_is_recorded_blocks_release_and_never_overwrites(self):
        cer = build_cer(self._rec("Inclusion Criteria:\n\n* Age >= 21 years"))
        cer["conflicts"] = detect(cer)
        self.assertEqual(len(cer["conflicts"]), 1)
        c = cer["conflicts"][0]
        self.assertEqual((c["status"], c["blocks_release"]), ("open", True))
        self.assertEqual(len(c["assertions"]), 2)
        before = json.dumps([r["predicate"] for r in cer["criteria"] if r["type"] == "predicate"], sort_keys=True)
        dec = [{"criterion": r["display_number"], "role": ro, "decision": "approve"} for r in cer["criteria"] for ro in ("clinical", "informatics")]
        apply_review(cer, {"decisions": dec})
        self.assertEqual(cer["lifecycle"]["status"], "in_review")            # blocked by the open conflict
        apply_review(cer, {"decisions": dec, "conflict_resolutions": [{"conflict": c["id"], "outcome": "text controls", "adjudicator": "owner"}]})
        self.assertEqual(cer["lifecycle"]["status"], "validated")
        self.assertEqual(before, json.dumps([r["predicate"] for r in cer["criteria"] if r["type"] == "predicate"], sort_keys=True))
    def test_consistent_age_has_no_conflict(self):
        cer = build_cer(self._rec("Inclusion Criteria:\n\n* Age >= 18 years")); self.assertEqual(detect(cer), [])
    def test_capability_manifest_accounts_for_every_node(self):
        cer = R.load_cer("NCT06838273")
        text, man = compile_cql(cer, allow_draft=True)
        ids = []
        def walk(x):
            ids.append(x["id"])
            for c in x.get("children", []):
                walk(c)
        for r in cer["criteria"]:
            walk(r)
        per = man["capability"]["per_node"]
        self.assertEqual(set(ids), set(per))
        self.assertTrue(all(v["status"] in ("supported", "conditionally_supported", "unsupported") for v in per.values()))
        self.assertEqual(man["capability"]["trial_backend_label"], "partial")
        self.assertFalse(man["capability"]["overall_assertion_allowed"])
        gated, gman = compile_cql(cer)
        self.assertEqual(gman["capability"]["trial_backend_label"], "unavailable")
    def test_condition_cql_never_turns_missing_into_false(self):
        text, _ = compile_cql(R.load_cer("NCT06838273"), allow_draft=True)
        self.assertIn('parameter "ConditionCoverageComplete" Boolean default false', text)
        self.assertIn('then true else (if "ConditionCoverageComplete" then false else null as Boolean)', text)
    def test_fidelity_metrics_and_flagging(self):
        ref = json.load(open(os.path.join(HERE, "reference", "NCT06520683.example.json")))
        r = evaluate_fidelity(R.load_cer("NCT06520683"), ref)
        self.assertEqual(r["criterion_accounting"]["recall"], 1.0)
        self.assertFalse(r["reference_independent"]); self.assertIsNotNone(r["warning"])
        bad = copy.deepcopy(ref); bad["criteria"][1]["leaves"][1]["value"] = 75      # reference says <=75 -> boundary mismatch
        self.assertIn("WRONG_BOUNDARY_OR_VALUE", {d["code"] for d in evaluate_fidelity(R.load_cer("NCT06520683"), bad)["critical_discrepancies"]})
        flip = copy.deepcopy(ref); flip["criteria"][3]["polarity"] = "inclusion"
        self.assertIn("POLARITY_INVERSION", {d["code"] for d in evaluate_fidelity(R.load_cer("NCT06520683"), flip)["critical_discrepancies"]})
        self.assertEqual(wilson(0, 0), (None, None))
    def test_new_nci_studies_parse_scopes_and_zubrod_is_not_ecog(self):
        cer = R.load_cer("NCT02635009")
        self.assertTrue(any("Step 1" in s for sc in cer["scopes"] for s in sc))
        ps = [x for r in cer["criteria"] for x in [r] if x["type"] == "predicate" and x["predicate"]["kind"] == "performance_status"]
        self.assertTrue(ps and ps[0]["predicate"]["scale"] == "Zubrod")
        from cer import evaluate as E
        res = E.evaluate(cer, {"as_of": "2026-10-06", "ecog": {"value": 1, "date": "2026-10-01"}}, scope="Step 1")
        row = next(x for x in res["criteria"] if "Zubrod" in x["text"])
        self.assertEqual(row["outcome"], "unresolved")                       # ECOG value is not accepted for a Zubrod rule


if __name__ == "__main__":
    unittest.main()
