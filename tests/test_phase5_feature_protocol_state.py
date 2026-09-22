import unittest
from pathlib import Path


PHASE7_TAG = "fmp-v1-phase7-walk-forward"
PHASE7_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


class Phase5FeatureProtocolStateTests(unittest.TestCase):
    def test_dec029_and_approved_spec_freeze_phase5_protocol(self) -> None:
        decision = read("docs/decision-log.md")
        spec = read("docs/superpowers/specs/2026-09-14-phase5-leakage-safe-feature-engine-design.md")
        self.assertIn("DEC-029 — Phase 5 leakage-safe feature-engine protocol — APPROVED", decision)
        self.assertIn("## DEC-029 — Phase 5 leakage-safe feature-engine protocol", decision)
        self.assertIn("**Status:** APPROVED", spec)
        self.assertIn("fmp-feature-v1", spec)
        self.assertIn("2024-01-01 or later", spec)
        self.assertIn("before that partition is opened", spec)

    def test_project_state_preserves_phase5_checkpoint_under_phase8_activation(self) -> None:
        state = read("docs/project-state.md")
        self.assertIn("## Phase 4 — PASS", state)
        self.assertIn("fmp-v1-phase4-baselines", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("fmp-v1-phase5-features", state)
        self.assertIn("## Phase 6 — PASS", state)
        self.assertIn("2024-01-01 or later", state)
        self.assertIn("## Phase 7 — PASS", state)
        self.assertIn(PHASE7_TAG, state)
        self.assertIn(PHASE7_SHA, state)
        self.assertIn("**Current phase:** Phase 8A — Multi-pair, multi-strategy portfolio research", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("## Phase 8 — ACTIVE AS AMENDED PHASE 8A / 8B", state)
        self.assertIn("real-money trading", state.lower())
        self.assertIn("DEC-008 remains unchanged", state)
        self.assertIn("Phase 9/demo order placement: LOCKED", state)


if __name__ == "__main__":
    unittest.main()
