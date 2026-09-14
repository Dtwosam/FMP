from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase4TrendContinuationEvidenceStateTests(unittest.TestCase):
    def test_evidence_record_binds_full_successful_matrix_and_rejection(self):
        evidence = (ROOT / "docs" / "phase4-trend-continuation-evidence.md").read_text(encoding="utf-8")
        self.assertIn("34863705913", evidence)
        self.assertIn("d1c821cb8b4bfaaddbc334fee0f2f3b1dfe054a2", evidence)
        self.assertIn("18/18", evidence)
        self.assertIn("324/324", evidence)
        self.assertIn("REJECT", evidence)
        self.assertIn("zero", evidence.lower())
        self.assertIn("0.2-pip", evidence)
        self.assertIn("0.5-pip", evidence)
        self.assertIn("1.0-pip", evidence)
        self.assertIn("Final-test touched: NO", evidence)

    def test_experiment_registry_records_fail_and_reject(self):
        log = (ROOT / "docs" / "experiment-log.md").read_text(encoding="utf-8")
        self.assertIn("### EXP-20260914-002 — Trend continuation baseline", log)
        self.assertIn("- Status: FAIL", log)
        self.assertIn("- Code commit: `d1c821cb8b4bfaaddbc334fee0f2f3b1dfe054a2`", log)
        self.assertIn("- Final-test touched?: NO", log)
        self.assertIn("- Conclusion: REJECT", log)
        self.assertIn("mean reversion", log.lower())

    def test_project_state_keeps_phase4_active_and_session_candidate_frozen(self):
        state = (ROOT / "docs" / "project-state.md").read_text(encoding="utf-8")
        self.assertIn("**Current phase:** Phase 4 — Baseline Strategy Research", state)
        self.assertIn("**Phase status:** PASS", state)
        self.assertIn("EXP-20260914-002", state)
        self.assertIn("experiment status: FAIL", state)
        self.assertIn("conclusion: REJECT", state)
        self.assertIn("USDJPY 15m", state)
        self.assertIn("mean reversion", state.lower())
        self.assertIn("Final-test touched: NO", state)
        self.assertIn("## Phase 5 — UNSTARTED", state)
        self.assertIn("Real-money trading remains locked", state)


if __name__ == "__main__":
    unittest.main()
