from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PHASE7_TAG = "fmp-v1-phase7-walk-forward"
PHASE7_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"


class Phase4CheckpointStateTests(unittest.TestCase):
    def test_phase4_checkpoint_remains_recorded_after_phase8_activation(self) -> None:
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        evidence = (ROOT / "docs/phase4-acceptance-evidence.md").read_text(encoding="utf-8")

        self.assertIn("`fmp-v1-phase4-baselines`", state)
        self.assertIn("`115bb8080e951db16ca1a1174227ffa181a03d1b`", state)
        self.assertIn("`fmp-v1-phase4-baselines` — CREATED at `115bb8080e951db16ca1a1174227ffa181a03d1b`", evidence)
        self.assertIn("**Decision:** DEC-028 — APPROVED", evidence)
        self.assertIn("tests run `34903338560`", evidence)
        self.assertIn("Phase 3 acceptance run `34903338538`", evidence)
        self.assertIn("## Phase 4 — PASS", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — PASS", state)
        self.assertIn("## Phase 7 — PASS", state)
        self.assertIn(PHASE7_TAG, state)
        self.assertIn(PHASE7_SHA, state)
        self.assertIn("**Current phase:** Phase 8 — Live shadow mode", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("## Phase 8 — ACTIVE", state)
        self.assertIn("Phase 9/demo order placement: LOCKED", state)
        self.assertIn("Real-money trading: locked", state)


if __name__ == "__main__":
    unittest.main()
