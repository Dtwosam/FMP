from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase4SessionBreakoutEvidenceStateTests(unittest.TestCase):
    def test_evidence_record_binds_full_successful_matrix_and_candidate(self):
        evidence = (ROOT / "docs" / "phase4-session-breakout-evidence.md").read_text(encoding="utf-8")
        self.assertIn("34848137086", evidence)
        self.assertIn("cc01929b80cbd1d5619de8476caa8f3d3410262e", evidence)
        self.assertIn("18/18", evidence)
        self.assertIn("486/486", evidence)
        self.assertIn("USDJPY", evidence)
        self.assertIn("15m", evidence)
        self.assertIn("5 pips", evidence)
        self.assertIn("1.5", evidence)
        self.assertIn("1.0-pip", evidence)
        self.assertIn("2022", evidence)
        self.assertIn("Final-test touched: NO", evidence)

    def test_experiment_registry_records_pass_and_serious_candidate_promotion(self):
        log = (ROOT / "docs" / "experiment-log.md").read_text(encoding="utf-8")
        self.assertIn("### EXP-20260914-001 — Session breakout baseline", log)
        self.assertIn("- Status: PASS", log)
        self.assertIn("- Code commit: `cc01929b80cbd1d5619de8476caa8f3d3410262e`", log)
        self.assertIn("- Final-test touched?: NO", log)
        self.assertIn("- Conclusion: PROMOTE", log)
        self.assertIn("USDJPY 15m", log)
        self.assertIn("5-pip", log)
        self.assertIn("1.5", log)
        self.assertIn("trend continuation", log.lower())

    def test_project_state_preserves_phase4_candidate_and_later_gates(self):
        state = (ROOT / "docs" / "project-state.md").read_text(encoding="utf-8")
        self.assertIn("**Current phase:** Phase 7 — Walk-forward Evaluation", state)
        self.assertIn("**Phase status:** PASS", state)
        self.assertIn("## Phase 4 — PASS", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — PASS", state)
        self.assertIn("## Phase 7 — PASS", state)
        self.assertIn("EXP-20260914-001", state)
        self.assertIn("USDJPY 15m", state)
        self.assertIn("Final-test touched: YES — Stage 1 2024 and Stage 2 2025-2026", state)
        self.assertIn("trend continuation", state.lower())
        self.assertIn("Real-money trading: locked", state)
        self.assertNotIn("## Phase 8 — ACTIVE", state)


if __name__ == "__main__":
    unittest.main()
