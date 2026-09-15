from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Phase4CheckpointStateTests(unittest.TestCase):
    def test_phase4_checkpoint_is_recorded_without_starting_phase5(self) -> None:
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
        self.assertIn("final-test data remains locked", state.lower())
        self.assertIn("Real-money trading: locked", state)
        self.assertIn("## Phase 5 — PASS", state)


if __name__ == "__main__":
    unittest.main()
