from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = "fmp-v1-phase6-models"
CLOSURE_SHA = "5d387b7ca93d04c498eb04c376e0dd92f1fe1953"
TESTS_RUN = "34972534430"
PHASE3_RUN = "34972534435"


class Phase6CheckpointStateTests(unittest.TestCase):
    def test_phase6_checkpoint_is_created_at_verified_closure_commit(self) -> None:
        evidence = (ROOT / "docs/phase6-ml-filter-evidence.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")

        created_marker = f"`{CHECKPOINT}` — CREATED at `{CLOSURE_SHA}`"
        self.assertIn(created_marker, evidence)
        self.assertIn(created_marker, state)

        self.assertIn(f"tests run `{TESTS_RUN}`", evidence)
        self.assertIn("573/573 tests PASS", evidence)
        self.assertIn("workflow YAML PASS", evidence)
        self.assertIn("compile PASS", evidence)
        self.assertIn(f"Phase 3 acceptance run `{PHASE3_RUN}`", evidence)

        self.assertIn("## Phase 6 — PASS", state)
        self.assertIn("**Phase status:** PASS", state)
        self.assertIn("Phase 7 remains UNSTARTED", state)
        self.assertIn("Final-test touched: NO", state)
        self.assertIn("final-test", state.lower())
        self.assertIn("locked", state.lower())
        self.assertIn("broker/live/demo", state.lower())
        self.assertIn("real-money trading", state.lower())


if __name__ == "__main__":
    unittest.main()
