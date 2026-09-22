from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PHASE7_TAG = "fmp-v1-phase7-walk-forward"
PHASE7_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"


class Phase4AcceptanceStateTests(unittest.TestCase):
    def test_phase4_is_pass_after_phase8_activation(self) -> None:
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        evidence = (ROOT / "docs/phase4-acceptance-evidence.md").read_text(encoding="utf-8")

        self.assertIn("## Phase 4 — PASS", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — PASS", state)
        self.assertIn("## Phase 7 — PASS", state)
        self.assertIn(PHASE7_TAG, state)
        self.assertIn(PHASE7_SHA, state)
        self.assertIn("DEC-028", state)
        self.assertEqual(decision.count("## DEC-028 — Phase 4 baseline strategy research acceptance review"), 1)
        self.assertIn("- DEC-028 — Phase 4 baseline strategy research acceptance review — APPROVED", decision)
        self.assertIn("**Result:** PASS", evidence)
        self.assertIn("Final-test touched?: NO", evidence)
        self.assertIn("Final-test touched: YES — Stage 1 2024 and Stage 2 2025-2026", state)
        self.assertIn("**Current phase:** Phase 8A — Multi-pair, multi-strategy portfolio research", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("## Phase 8 — ACTIVE AS AMENDED PHASE 8A / 8B", state)
        self.assertIn("Phase 9/demo order placement: LOCKED", state)
        self.assertIn("Real-money trading: locked", state)


if __name__ == "__main__":
    unittest.main()
