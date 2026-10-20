"""DEC-1844: owner handoff is an unfilled, source-bound human request."""
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "dec1843-independent-external-security-proof-acceptance-handoff.md"
DOCUMENTARY = ROOT / "scripts" / "dec1752_phase8a_readiness_report.py"
SEVEN_SOURCE = ROOT / "scripts" / "dec1816_offline_security_review_bundle.py"


class Phase8AIndependentHumanEvidenceHandoffTests(unittest.TestCase):
    def test_all_eight_exact_proof_ids_and_owners_are_present_once(self):
        audit = runpy.run_path(str(DOCUMENTARY))
        data = HANDOFF.read_text(encoding="utf-8")
        self.assertEqual(len(audit["PROOFS"]), 8)
        self.assertEqual(len(audit["OWNERS"]), 8)
        for proof, owner in zip(audit["PROOFS"], audit["OWNERS"]):
            with self.subTest(proof=proof):
                self.assertEqual(data.count("| `" + proof + "` |"), 1)
                self.assertIn("| `" + proof + "` | " + owner + " |", data)

    def test_each_proof_is_unfilled_with_no_selected_remediation(self):
        data = HANDOFF.read_text(encoding="utf-8")
        self.assertEqual(data.count("| **MISSING** |"), 8)
        self.assertIn("**UNSELECTED / NOT APPROVED**", data)
        self.assertIn("Every external signoff: **MISSING**", data)
        self.assertIn("Approved ref-lock remedy: **NONE**", data)
        self.assertIn("One-shot run385/attempt1 human permission: **NONE**", data)

    def test_issue_navigation_matches_source_only_review_index(self):
        data = HANDOFF.read_text(encoding="utf-8")
        mapping = runpy.run_path(str(SEVEN_SOURCE))["REVIEW_ISSUE_REFERENCES"]
        audit = runpy.run_path(str(DOCUMENTARY))
        self.assertEqual(set(mapping), set(audit["PROOFS"]))
        for key, refs in mapping.items():
            with self.subTest(proof=key):
                row = next(
                    line for line in data.splitlines()
                    if line.startswith("| `" + key + "` |")
                )
                for ref in refs:
                    number = ref.rstrip("/").split("/")[-1]
                    self.assertIn("#" + number, row)
        self.assertIn(
            "[#779](https://github.com/Dtwosam/FMP/issues/779)", data)
        self.assertIn(
            "[#820](https://github.com/Dtwosam/FMP/pull/820)", data)
        self.assertIn(
            "[#821](https://github.com/Dtwosam/FMP/pull/821)", data)

    def test_no_source_only_matrix_grants_the_irreversible_run(self):
        data = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("2023/run385/attempt1", data)
        self.assertIn("2022/run384", data)
        plain = data.replace("**", "").lower()
        self.assertIn("not an independent signature", plain)
        self.assertIn("no dispatch or retry", plain)
        self.assertIn("Strategy V1", data)
        self.assertIn("broker", data)
        self.assertIn("DRAFT / NEVER MERGE / NEVER PROMOTE", data)


if __name__ == "__main__":
    unittest.main()
