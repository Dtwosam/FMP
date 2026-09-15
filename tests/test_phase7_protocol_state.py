from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PHASE7_TAG = "fmp-v1-phase7-walk-forward"
PHASE7_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"


class Phase7ProtocolStateTests(unittest.TestCase):
    def test_dec033_protocol_remains_recorded_after_phase8_activation(self) -> None:
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        experiments = (ROOT / "docs/experiment-log.md").read_text(encoding="utf-8")
        spec = (
            ROOT
            / "docs/superpowers/specs/2026-09-15-phase7-walk-forward-design.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "## DEC-033 — Phase 7 walk-forward evaluation protocol\n\n"
            "**Date:** 2026-09-15\n"
            "**Status:** APPROVED",
            decision,
        )
        self.assertIn("Phase 7 is ACTIVE only for test-first implementation", decision)
        self.assertIn("PLANNED with `Final-test touched: NO`", decision)
        self.assertIn("**Status:** APPROVED", spec)
        self.assertIn("### EXP-20260915-008 — Phase 7 walk-forward evaluation", experiments)
        self.assertIn("- Status: PASS", experiments)
        self.assertIn("## Phase 7 — PASS", state)
        self.assertIn("EXP-20260915-008", state)
        self.assertIn(PHASE7_TAG, state)
        self.assertIn(PHASE7_SHA, state)
        self.assertIn("**Current phase:** Phase 8 — Live shadow mode", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("## Phase 8 — ACTIVE", state)
        self.assertIn("DEC-036", state)


if __name__ == "__main__":
    unittest.main()
