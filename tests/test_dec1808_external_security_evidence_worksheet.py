"""DEC-1808: static evidence-request worksheet never becomes approval."""
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "dec1752_phase8a_readiness_report.py"
WORKSHEET = ROOT / "docs" / "dec1808-independent-owner-evidence-worksheet.md"


class Phase8AExternalEvidenceWorksheetTests(unittest.TestCase):
    def test_contains_all_eight_exact_independent_proof_ids_and_roles(self):
        audit = runpy.run_path(str(SCRIPT))
        data = WORKSHEET.read_text()
        self.assertEqual(data.count("### Proof "), 8)
        for i, (proof, role) in enumerate(zip(audit["PROOFS"], audit["OWNERS"]), 1):
            with self.subTest(proof=proof):
                self.assertIn(f"### Proof {i}: `{proof}`", data)
                self.assertIn(f"**Required reviewer role:** {role}", data)

    def test_all_acceptance_requirements_are_unmodified_source_text(self):
        audit = runpy.run_path(str(SCRIPT))
        data = WORKSHEET.read_text()
        self.assertEqual(len(audit["PROOF_ACCEPTANCE_CRITERIA"]), 8)
        for criterion in audit["PROOF_ACCEPTANCE_CRITERIA"].values():
            self.assertIn("**Acceptance requirement (source-defined):** " + criterion,
                          data)

    def test_every_proof_is_explicitly_missing_and_unattested(self):
        data = WORKSHEET.read_text()
        self.assertEqual(data.count("**Status: MISSING — not authorization.**"), 8)
        self.assertEqual(data.count("**Evidence collection fields (unfilled and NOT attested):**"), 8)
        self.assertIn("not a security attestation", data)
        self.assertIn("no dispatch, retry", data)

    def test_external_evidence_review_stays_separate_from_protected_action(self):
        data = WORKSHEET.read_text()
        self.assertIn("distinct scoped human decision", data)
        self.assertIn("2023/run385/attempt1", data)
        self.assertIn("#779/#820/#821", data)
        self.assertIn("DRAFT / NEVER MERGE / NEVER PROMOTE", data)


if __name__ == "__main__":
    unittest.main()
