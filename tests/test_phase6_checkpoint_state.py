from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = "fmp-v1-phase6-models"
CLOSURE_SHA = "5d387b7ca93d04c498eb04c376e0dd92f1fe1953"
TESTS_RUN = "34972534430"
PHASE3_RUN = "34972534435"
PHASE7_TAG = "fmp-v1-phase7-walk-forward"
PHASE7_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"


# Durable guard for the immutable Phase 6 checkpoint across later approved phases.
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
        self.assertIn("## Phase 7 — PASS", state)
        self.assertIn("Final-test touched: YES — Stage 1 2024 and Stage 2 2025-2026", state)
        self.assertIn(PHASE7_TAG, state)
        self.assertIn(PHASE7_SHA, state)
        self.assertIn("**Current phase:** Phase 8 — Live shadow mode", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("## Phase 8 — ACTIVE", state)
        self.assertIn("Phase 9/demo order placement: LOCKED", state)
        self.assertIn("production/live order placement and broker mutation: LOCKED", state)
        self.assertIn("Real-money trading: locked", state)


if __name__ == "__main__":
    unittest.main()
