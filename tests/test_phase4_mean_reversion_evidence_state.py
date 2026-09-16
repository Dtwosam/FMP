from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase4MeanReversionEvidenceStateTests(unittest.TestCase):
    def test_evidence_record_binds_full_successful_matrix_and_rejection(self):
        evidence = (ROOT / "docs" / "phase4-mean-reversion-evidence.md").read_text(encoding="utf-8")
        self.assertIn("34875463677", evidence)
        self.assertIn("87003a3982ca61eb6fd030c5291616d98dbb0c1a", evidence)
        self.assertIn("18/18", evidence)
        self.assertIn("324/324", evidence)
        self.assertIn("REJECT", evidence)
        self.assertIn("zero", evidence.lower())
        self.assertIn("0.2-pip", evidence)
        self.assertIn("Final-test touched: NO", evidence)

    def test_exp003_record_preserves_protocol_and_records_fail(self):
        record = (ROOT / "docs" / "phase4-mean-reversion-predeclaration.md").read_text(encoding="utf-8")
        self.assertIn("EXP-20260914-003", record)
        self.assertIn("**Status:** FAIL", record)
        self.assertIn("DEC-020", record)
        self.assertIn("4h, 8h, 16h", record)
        self.assertIn("1.5σ and 2.0σ", record)
        self.assertIn("0.2, 0.5, 1.0", record)
        self.assertIn("18 pair/timeframe/split cells and 324 configuration rows", record)
        self.assertIn("87003a3982ca61eb6fd030c5291616d98dbb0c1a", record)
        self.assertIn("34875463677", record)
        self.assertIn("Final-test touched?: NO", record)
        self.assertIn("Conclusion: REJECT", record)

    def test_project_state_preserves_phase4_rejection_and_frozen_candidate(self):
        state = (ROOT / "docs" / "project-state.md").read_text(encoding="utf-8")
        self.assertIn("**Current phase:** Phase 8 — Live shadow mode", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("## Phase 4 — PASS", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — PASS", state)
        self.assertIn("## Phase 7 — PASS", state)
        self.assertIn("EXP-20260914-003", state)
        self.assertIn("experiment status: FAIL", state)
        self.assertIn("conclusion: REJECT", state)
        self.assertIn("USDJPY 15m", state)
        self.assertIn("previous-day high/low rejection", state.lower())
        self.assertIn("Final-test touched: YES — Stage 1 2024 and Stage 2 2025-2026", state)
        self.assertIn("Real-money trading: locked", state)
        self.assertIn("## Phase 8 — ACTIVE", state)


if __name__ == "__main__":
    unittest.main()
