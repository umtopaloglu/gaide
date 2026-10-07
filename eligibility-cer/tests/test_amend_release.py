import copy, json, os, shutil, sys, tempfile, unittest
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import run as R
from cer.amendments import diff_cers, impact
from cer.build import build_cer
from cer.review import apply_review, text_hash


def amended(rec):
    r = copy.deepcopy(rec)
    em = r["protocolSection"]["eligibilityModule"]
    t = em["eligibilityCriteria"]
    t = t.replace("* ECOG performance status of 0 or 1", "* ECOG performance status of 0 to 2")      # modified
    t = t.replace("* History of leptomeningeal carcinomatosis\n", "")                                   # removed
    t = t.replace("* History of active primary immunodeficiency", "* History of active primary immunodeficiency\n* Prior organ transplant")  # added
    em["eligibilityCriteria"] = t
    return r


class Amendments(unittest.TestCase):
    def setUp(self):
        self.rec = R.load("NCT06357533")
        self.old, self.new = build_cer(self.rec), build_cer(amended(self.rec))
    def test_diff_classifies_changes(self):
        d = diff_cers(self.old, self.new)
        ch = {x["change"] for x in d["criteria"]}
        self.assertTrue({"modified", "added", "removed", "unchanged"} <= ch | {"renumbered"})
        mod = [x for x in d["criteria"] if x["change"] == "modified"]
        self.assertTrue(any("0 to 2" in x["new_text"] for x in mod))
        self.assertNotEqual(d["from_sha256"], d["to_sha256"])
    def test_pinned_approvals_go_stale_and_unpinned_are_reported(self):
        ecog = next(r for r in self.old["criteria"] if "ECOG" in r["text"])
        other = next(r for r in self.old["criteria"] if r["display_number"] == "Inc-b1")
        dec = [{"criterion": ecog["display_number"], "role": ro, "decision": "approve", "criterion_text_sha256": text_hash(ecog["text"])}
               for ro in ("clinical", "informatics")]
        dec += [{"criterion": other["display_number"], "role": "clinical", "decision": "approve"}]
        apply_review(self.old, {"decisions": dec})
        self.assertEqual(next(r for r in self.old["criteria"] if r is ecog)["review_status"], "validated")
        apply_review(self.new, {"decisions": dec})
        new_ecog = next(r for r in self.new["criteria"] if "ECOG" in r["text"])
        self.assertEqual(new_ecog["review_status"], "needs_review")
        self.assertEqual(len(self.new["review_summary"]["stale_decisions"]), 2)
        self.assertIn("Inc-b1", self.new["review_summary"]["unpinned_decisions"])
    def test_removed_criterion_decisions_are_orphaned_not_crashing(self):
        gone = next(r for r in self.old["criteria"] if "leptomeningeal" in r["text"])
        new = build_cer(amended(self.rec))
        num = gone["display_number"]
        if num in {r["display_number"] for r in new["criteria"]}:
            num = "Exc-b99"
        apply_review(new, {"decisions": [{"criterion": num, "role": "clinical", "decision": "approve"}]})
        self.assertEqual(len(new["review_summary"]["orphaned_decisions"]), 1)
    def test_impact_lists_actions_and_blocks_release(self):
        d = diff_cers(self.old, self.new)
        imp = impact(d, {"decisions": [{"criterion": x.get("new") or x.get("old"), "role": "clinical", "decision": "approve"}
                                       for x in d["criteria"] if x["change"] == "modified"]})
        self.assertTrue(imp["release_blocked_until_re_review"])
        self.assertTrue(imp["stale_review_decisions"])


if __name__ == "__main__":
    unittest.main()


class Release(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(dir=os.path.join(HERE, "out"))
    def tearDown(self):
        shutil.rmtree(self.tmp)
    def test_candidate_is_idempotent_verifiable_and_tamper_evident(self):
        from cer.release import build_release, verify_release
        cer = R.load_cer("NCT06520683")
        d, m, created = build_release(cer, out_root=self.tmp)
        self.assertTrue(created)
        self.assertEqual(m["status"], "candidate")
        self.assertFalse(m["usable_for_screening"])
        self.assertTrue(any("not dual-approved" in x for x in m["blocking_reasons"]))
        self.assertTrue(verify_release(d)[0])
        d2, m2, created2 = build_release(R.load_cer("NCT06520683"), out_root=self.tmp)
        self.assertEqual((d2, created2), (d, False))                       # same content -> same id, no duplicate
        cql = next(p for p in m["files"] if p.endswith(".cql"))
        with open(os.path.join(d, cql), "a") as f:
            f.write("\\n// edited")
        ok, problems = verify_release(d)
        self.assertFalse(ok); self.assertIn(f"modified {cql}", problems)
        with self.assertRaises(RuntimeError):
            build_release(R.load_cer("NCT06520683"), out_root=self.tmp)
    def test_new_content_gets_new_id_and_rollback_pointer(self):
        from cer.release import build_release
        cer = R.load_cer("NCT06357533")
        d1, m1, _ = build_release(cer, out_root=self.tmp)
        cer2 = build_cer(amended(R.load("NCT06357533")))
        d2, m2, _ = build_release(cer2, out_root=self.tmp)
        self.assertNotEqual(m1["release_id"], m2["release_id"])
        self.assertEqual(m2["rollback_target"], m1["release_id"])
    def test_package_has_no_patient_evidence(self):
        from cer.release import build_release
        d, m, _ = build_release(R.load_cer("NCT06128837"), out_root=self.tmp)
        self.assertFalse(any("evidence" in p for p in m["files"]))


class Determinism(unittest.TestCase):
    def test_graph_bytes_identical_across_processes_and_hash_seeds(self):
        import subprocess
        code = ("import sys,hashlib; sys.path.insert(0,%r); import run as R; from cer import graph as G; "
                "print(hashlib.sha256(G.to_jsonld(R.load_cer('NCT06520683'))[0].encode()).hexdigest())") % HERE
        outs = {subprocess.run([sys.executable, "-c", code], env={**os.environ, "PYTHONHASHSEED": s}, capture_output=True,
                               text=True, check=True).stdout.strip() for s in ("1", "2", "3")}
        self.assertEqual(len(outs), 1)
