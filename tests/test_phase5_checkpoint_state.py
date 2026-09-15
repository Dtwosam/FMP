from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase5CheckpointStateTests(unittest.TestCase):
    def test_phase5_checkpoint_remains_recorded_after_phase6_activation(self) -> None:
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        evidence = (ROOT / "docs/phase5-acceptance-evidence.md").read_text(encoding="utf-8")

        self.assertIn("`fmp-v1-phase5-features`", state)
        self.assertIn("`e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`", state)
        self.assertIn(
            "`fmp-v1-phase5-features` — CREATED at `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`",
            evidence,
        )
        self.assertIn("**Decision:** DEC-030 — APPROVED", evidence)
        self.assertIn("tests run `34912677109`", evidence)
        self.assertIn("Phase 3 acceptance run `34912677100`", evidence)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — ACTIVE", state)
        self.assertNotIn("## Phase 6 — UNSTARTED", state)
        self.assertIn("Phase 7 remains UNSTARTED", state)
        self.assertIn("final-test data remains locked", state.lower())
        self.assertIn("real-money trading remain locked", state.lower())


if __name__ == "__main__":
    unittest.main()
