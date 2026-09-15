from pathlib import Path
import unittest


EXPECTED_PHASE7_TAG = "fmp-v1-phase7-walk-forward"
EXPECTED_PHASE7_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"
EXPECTED_EXPERIMENT = "EXP-20260915-009"
EXPECTED_DECISION = "DEC-036"
PRACTICE_STREAM_HOST = "stream-fxpractice.oanda.com"


class Phase8ProtocolStateTests(unittest.TestCase):
    def test_phase8_source_of_truth_is_active_and_execution_remains_locked(self) -> None:
        decision_log = Path("docs/decision-log.md").read_text(encoding="utf-8")
        experiment_log = Path("docs/experiment-log.md").read_text(encoding="utf-8")
        state = Path("docs/project-state.md").read_text(encoding="utf-8")
        sources = Path("docs/source-register.md").read_text(encoding="utf-8")
        design = Path(
            "docs/superpowers/specs/2026-09-15-phase8-shadow-design.md"
        ).read_text(encoding="utf-8")

        self.assertIn(f"- {EXPECTED_DECISION} — Phase 8", decision_log)
        self.assertIn(f"## {EXPECTED_DECISION} — Phase 8", decision_log)
        self.assertIn(f"### {EXPECTED_EXPERIMENT} — Phase 8", experiment_log)
        self.assertIn("- Status: RUNNING", experiment_log)
        self.assertIn("**Current phase:** Phase 8 — Live shadow mode", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn(EXPECTED_PHASE7_TAG, state)
        self.assertIn(EXPECTED_PHASE7_SHA, state)
        self.assertIn(PRACTICE_STREAM_HOST, sources)
        self.assertIn("2026-09-15", sources)
        self.assertIn("**Status:** APPROVED / ACTIVATED", design)
        self.assertIn("DEC-008", decision_log)
        self.assertIn("Real-money trading: locked", state)
        self.assertIn("demo", state.lower())
        self.assertIn("locked", state.lower())


if __name__ == "__main__":
    unittest.main()
