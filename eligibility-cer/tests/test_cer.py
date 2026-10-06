import glob, json, os, sys, unittest
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from cer import evaluate as E
from cer import extract as X
from cer.build import build_cer

def load(n):
    return json.load(open(os.path.join(HERE, "data", "raw", f"{n}.json"), encoding="utf-8"))

def rec(text):
    return {"protocolSection": {"identificationModule": {"nctId": "NCT00000000", "briefTitle": "t"},
                                "eligibilityModule": {"eligibilityCriteria": text}}}

def flat(n):
    yield n
    for c in n.get("children", []):
        yield from flat(c)

class TruthTables(unittest.TestCase):
    T, F, U = True, False, None
    def test_all_any(self):
        self.assertIs(E.and3([self.T, self.U]), None); self.assertIs(E.and3([self.F, self.U]), False)
        self.assertIs(E.or3([self.F, self.U]), None); self.assertIs(E.or3([self.T, self.U]), True)
        self.assertIs(E.not3(None), None)
    def test_atleast(self):
        self.assertIs(E.atleast3([True, True, None], 2), True)
        self.assertIs(E.atleast3([True, None, False], 2), None)
        self.assertIs(E.atleast3([True, False, False], 2), False)
    def test_polarity_applied_once(self):
        self.assertEqual(E.requirement_outcome(True, "inclusion"), "satisfied")
        self.assertEqual(E.requirement_outcome(True, "exclusion"), "violated")
        self.assertEqual(E.requirement_outcome(False, "exclusion"), "satisfied")
        self.assertEqual(E.requirement_outcome(None, "exclusion"), "unresolved")

class Extraction(unittest.TestCase):
    def test_ecog_forms(self):
        for t, want in [("ECOG score < 2", [0, 1]), ("ECOG performance status of 0 or 1", [0, 1]),
                        ("Eastern Cooperative Oncology Group (ECOG) performance status (PS) 0-1", [0, 1])]:
            p = X.extract_predicates(t)[0][0]
            self.assertEqual(p["allowed_values"], want, t)
    def test_no_substring_lab_match(self):
        self.assertEqual(X.extract_predicates("liver metastases <= 3 and clearance")[0], [])
    def test_shared_qualifier_ast_alt(self):
        ps = X.extract_predicates("AST and ALT <= 2.0 x ULN")[0]
        self.assertEqual({p["analyte"] for p in ps}, {"AST", "ALT"})
        self.assertTrue(all(p["uln_multiple"] and p["value"] == 2.0 for p in ps))
    def test_time_window_anchor(self):
        tw = X.time_window("Other malignancies within 5 years before screening (except x)")
        self.assertEqual((tw["value"], tw["unit"], tw["anchor"], tw["status"]), (5.0, "year", "screening", "parsed"))
        self.assertEqual(X.time_window("within 3 years")["status"], "anchor_missing_or_unrecognised")

class BuildAndFixtures(unittest.TestCase):
    def test_fixtures_account_for_every_line_and_ids_unique(self):
        for p in glob.glob(os.path.join(HERE, "data", "raw", "NCT*.json")):
            cer = build_cer(json.load(open(p, encoding="utf-8")))
            self.assertTrue(cer["validation"]["structure_ok"], (p, cer["validation"]["problems"]))
            self.assertEqual(cer["lifecycle"]["status"], "draft")
    def test_section_polarity_and_or_group(self):
        cer = build_cer(rec("Inclusion Criteria:\n\n* Age ≥ 18 years\n\nExclusion Criteria:\n\n* Patients with any of the following:\n   1. HIV infection\n   2. active tuberculosis"))
        inc, exc = cer["criteria"]
        self.assertEqual((inc["polarity"], exc["polarity"]), ("inclusion", "exclusion"))
        self.assertEqual(exc["op"], "ANY")
    def test_heading_flips_polarity_inside_inclusion(self):
        cer = build_cer(rec("Inclusion Criteria:\n\n1. Phase A:\n\n   Main exclusion criteria:\n   * Prior SERD\n"))
        self.assertEqual(cer["criteria"][0]["polarity"], "exclusion")
        self.assertEqual(cer["criteria"][0]["scope"], ["Phase A"])

class SafetyBehaviour(unittest.TestCase):
    def setUp(self):
        self.cer = build_cer(load("NCT06357533"))
    def test_untested_biomarker_is_unresolved_not_failure(self):
        r = E.evaluate(self.cer, {"age": 60, "ecog": 1, "biomarkers": {"PD-L1": {"state": "present", "score": 70}}})
        row = next(x for x in r["criteria"] if x["number"] == "Inc-b3")
        self.assertEqual(row["outcome"], "unresolved")
        self.assertEqual(r["counts"]["violated"], 0)
    def test_positive_driver_mutation_violates(self):
        r = E.evaluate(self.cer, {"biomarkers": {"EGFR": {"state": "present"}}})
        self.assertEqual(next(x for x in r["criteria"] if x["number"] == "Inc-b3")["outcome"], "violated")
    def test_negative_without_adequacy_is_unknown(self):
        r = E.evaluate(self.cer, {"biomarkers": {"EGFR": {"state": "absent"}, "ALK": {"state": "absent"}, "ROS1": {"state": "absent"}}})
        self.assertEqual(next(x for x in r["criteria"] if x["number"] == "Inc-b3")["outcome"], "unresolved")
    def test_stale_ecog_unknown_and_draft_is_labelled(self):
        r = E.evaluate(self.cer, {"as_of": "2026-10-06", "ecog": {"value": 3, "date": "2025-01-01"}})
        self.assertEqual(next(x for x in r["criteria"] if x["number"] == "Inc-b7")["outcome"], "unresolved")
        self.assertTrue(r["disposition"].startswith("DRAFT-PROVISIONAL"))
    def test_flat_list_violation_is_downgraded(self):
        cer = build_cer(load("NCT05512364"))
        r = E.evaluate(cer, {"labs": {"Tumour size": {"value": 2.5}}}, scope="ctDNA screening phase")
        row = next(x for x in r["criteria"] if x["number"] == "Inc-1.b1.b7")
        self.assertEqual(row["outcome"], "unresolved")
    def test_multi_scope_requires_scope(self):
        with self.assertRaises(ValueError):
            E.evaluate(build_cer(load("NCT05512364")), {})

if __name__ == "__main__":
    unittest.main()


class AuthoredReviewCql(unittest.TestCase):
    @staticmethod
    def full(n, authored=True):
        import run as R
        return R.load_cer(n)
    def test_authored_or_group_and_identity(self):
        raw = build_cer(load("NCT06520683"))
        old = {r["display_number"]: r for r in raw["criteria"]}
        cer = self.full("NCT06520683")
        r = next(x for x in cer["criteria"] if x["display_number"] == "Inc-b2")
        self.assertEqual(r["origin"], "authored_proposal")
        self.assertEqual(r["id"], old["Inc-b2"]["id"])               # identity preserved
        self.assertEqual(r["polarity"], "inclusion")
        anyg = next(c for c in r["children"] if c.get("op") == "ANY")
        self.assertEqual(len(anyg["children"]), 5)
        self.assertEqual(cer["authored_applied"].count("Inc-b2"), 1)
    def test_exception_keeps_positive_unresolved(self):
        cer = self.full("NCT06520683")
        r = E.evaluate(cer, {"facts": {"condition:other_malignancy": True}})
        row = next(x for x in r["criteria"] if x["number"] == "Exc-b5")
        self.assertEqual(row["outcome"], "unresolved")
    def test_review_requires_both_roles(self):
        from cer.review import apply_review
        cer = build_cer(load("NCT06357533"))
        num = cer["criteria"][0]["display_number"]
        apply_review(cer, {"decisions": [{"criterion": num, "role": "clinical", "decision": "approve"}]})
        self.assertEqual(cer["criteria"][0]["review_status"], "partially_reviewed")
        apply_review(cer, {"decisions": [{"criterion": num, "role": "clinical", "decision": "approve"},
                                         {"criterion": num, "role": "informatics", "decision": "approve"}]})
        self.assertEqual(cer["criteria"][0]["review_status"], "validated")
        self.assertEqual(cer["lifecycle"]["status"], "in_review")      # others still pending
        apply_review(cer, {"decisions": [{"criterion": num, "role": "clinical", "decision": "approve"},
                                         {"criterion": num, "role": "informatics", "decision": "needs_change"}]})
        self.assertEqual(cer["criteria"][0]["review_status"], "changes_requested")
    def test_release_only_when_everything_validated_and_authorised(self):
        from cer.review import apply_review
        cer = build_cer(load("NCT06357533"))
        dec = [{"criterion": r["display_number"], "role": ro, "decision": "approve"} for r in cer["criteria"] for ro in ("clinical", "informatics")]
        apply_review(cer, {"decisions": dec})
        self.assertEqual(cer["lifecycle"]["status"], "validated")
        apply_review(cer, {"decisions": dec, "release": {"authorized_by": "X", "date": "2026-10-06"}})
        self.assertEqual(cer["lifecycle"]["status"], "released")
        self.assertFalse(E.evaluate(cer, {})["disposition"].startswith("DRAFT"))
    def test_cql_gated_by_default_and_never_silently_drops(self):
        from cer.cql import compile_cql
        cer = self.full("NCT06128837")
        text, man = compile_cql(cer)
        self.assertEqual(man["executable_typed_leaves"], 0)
        self.assertIn("NOT VALIDATED", text)
        self.assertTrue(all(f"\"Req {r['display_number']}\"" in text for r in cer["criteria"]))
        text, man = compile_cql(cer, allow_draft=True)
        self.assertGreater(man["executable_typed_leaves"], 5)
        self.assertIn("AgeInYears() >= 18", text)
        self.assertIn("not (", text)                                   # exclusion polarity applied once, at the root
        import re as _re
        code = _re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=_re.S)    # parens inside comments don't count
        self.assertEqual(code.count("("), code.count(")"))
        self.assertNotRegex(text, r"//[^\n]*\)\s*\n\s*and")             # no line comment swallowing a ')'
        narr = []
        for r in cer["criteria"]:
            narr += [n for n in flat(r) if n["type"] == "narrative"]
        reasons = " ".join(u["reason"] for u in man["unsupported"])
        self.assertIn("human_judgment", reasons); self.assertIn("text_dependent", reasons)
        self.assertGreaterEqual(len(man["unsupported"]), len(narr))
        self.assertFalse(man["translator_validated"])
    def test_cql_missing_anchor_is_parameter_without_default(self):
        from cer.cql import compile_cql
        text, _ = compile_cql(self.full("NCT06128837"), allow_draft=True)
        self.assertRegex(text, r'parameter "ScreeningDate" DateTime\s+//')
        self.assertNotIn("Now()", text)
