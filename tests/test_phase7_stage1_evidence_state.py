from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase7Stage1EvidenceStateTests(unittest.TestCase):
    def test_stage1_outcome_remains_recorded_after_phase8_activation(self) -> None:
        evidence = (ROOT / "docs/phase7-stage1-evidence.md").read_text(encoding="utf-8")
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        experiments = (ROOT / "docs/experiment-log.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")

        # Immutable Stage 1 evidence and authorization remain exact.
        self.assertIn("35013047267", evidence)
        self.assertIn("e33270de1f89757d1bf2a0d12ef40b2dc36bc110", evidence)
        self.assertIn("10414407590", evidence)
        self.assertIn("d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb", evidence)
        self.assertIn("session_breakout — STAGE1_PASS", evidence)
        self.assertIn("volatility_breakout — STAGE1_REJECT", evidence)

        self.assertIn("DEC-034 — Phase 7 Stage 1 final-gate outcome", decision)
        self.assertIn("Stage 2 is authorized only for `session_breakout`", decision)

        # Phase 7 remains closed while the current project state advances to Phase 8.
        self.assertIn("### EXP-20260915-008 — Phase 7 walk-forward evaluation", experiments)
        self.assertIn("- Status: PASS", experiments)

        self.assertIn("## Phase 7 — PASS", state)
        self.assertIn("**Current phase:** Phase 8 — Live shadow mode", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("Final-test touched: YES — Stage 1 2024 and Stage 2 2025-2026", state)
        self.assertIn("Stage 2 survivor: `session_breakout`", state)
        self.assertIn("Stage 2 rejected candidate: `volatility_breakout`", state)
        self.assertIn("10414407590", state)
        self.assertIn("PHASE7_PROMOTE_TO_SHADOW_DESIGN", state)
        self.assertIn("## Phase 8 — ACTIVE", state)
        self.assertIn("Real-money trading: locked", state)


if __name__ == "__main__":
    unittest.main()
