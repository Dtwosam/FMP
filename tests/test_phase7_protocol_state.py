from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase7ProtocolStateTests(unittest.TestCase):
    def test_dec033_activates_phase7_protocol_state(self) -> None:
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        experiments = (ROOT / "docs/experiment-log.md").read_text(encoding="utf-8")
        spec = (
            ROOT
            / "docs/superpowers/specs/2026-09-15-phase7-walk-forward-design.md"
        ).read_text(encoding="utf-8")

        self.assertIn("DEC-033 — Phase 7 walk-forward evaluation protocol — APPROVED", decision)
        self.assertIn("**Status:** APPROVED", spec)
        self.assertIn("### EXP-20260915-008 — Phase 7 walk-forward evaluation", experiments)
        self.assertIn("- Status: PLANNED", experiments)
        self.assertIn("**Current phase:** Phase 7", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("## Phase 7 — ACTIVE", state)
        self.assertIn("EXP-20260915-008", state)
        self.assertNotIn("## Phase 8 — ACTIVE", state)


if __name__ == "__main__":
    unittest.main()
