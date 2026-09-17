from pathlib import Path
import unittest


EXPECTED_PHASE7_TAG = "fmp-v1-phase7-walk-forward"
EXPECTED_PHASE7_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"
EXPECTED_EXPERIMENT = "EXP-20260917-010"
EXPECTED_DECISION = "DEC-037"
OLD_EXPERIMENT = "EXP-20260915-009"
PROVIDER = "FP_MARKETS_MT5_DEMO"
ALLOWED_SERVERS = ("FPMarketsSC-Demo", "FPMarketsSC-Demo2")


class Phase8ProtocolStateTests(unittest.TestCase):
    """Guard the amended Phase 8 state while all execution gates remain locked."""

    def test_phase8_mt5_source_of_truth_is_active_and_execution_remains_locked(self) -> None:
        decision_log = Path("docs/decision-log.md").read_text(encoding="utf-8")
        experiment_log = Path("docs/experiment-log.md").read_text(encoding="utf-8")
        state = Path("docs/project-state.md").read_text(encoding="utf-8")
        sources = Path("docs/source-register.md").read_text(encoding="utf-8")
        amendment = Path(
            "docs/superpowers/specs/2026-09-17-phase8-mt5-bridge-amendment.md"
        ).read_text(encoding="utf-8")

        self.assertIn(f"- {EXPECTED_DECISION} — Phase 8", decision_log)
        self.assertIn(f"## {EXPECTED_DECISION} — Phase 8", decision_log)
        self.assertIn(f"### {EXPECTED_EXPERIMENT} — Phase 8", experiment_log)
        self.assertIn("- Status: RUNNING", experiment_log)
        self.assertIn(OLD_EXPERIMENT, experiment_log)
        self.assertIn("STOPPED BEFORE QUALIFICATION", experiment_log)
        self.assertIn("**Current phase:** Phase 8 — Live shadow mode", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn(EXPECTED_EXPERIMENT, state)
        self.assertIn(EXPECTED_PHASE7_TAG, state)
        self.assertIn(EXPECTED_PHASE7_SHA, state)
        self.assertIn(PROVIDER, sources)
        for server in ALLOWED_SERVERS:
            self.assertIn(server, sources)
        self.assertIn("2026-09-17", sources)
        self.assertIn("**Status:** APPROVED / ACTIVATED", amendment)
        self.assertIn("DEC-008", decision_log)
        self.assertIn("Phase 9/demo order placement: LOCKED", state)
        self.assertIn("production/live order placement and broker mutation: LOCKED", state)
        self.assertIn("Real-money trading: locked", state)
        self.assertIn("no demo order placement", amendment.lower())


if __name__ == "__main__":
    unittest.main()
