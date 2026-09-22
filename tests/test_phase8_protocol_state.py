from pathlib import Path
import unittest


EXPECTED_PHASE7_TAG = "fmp-v1-phase7-walk-forward"
EXPECTED_PHASE7_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"
STOPPED_EXPERIMENT = "EXP-20260922-011"
ACTIVE_EXPERIMENT = "EXP-20260922-012"
LIVENESS_DECISION = "DEC-038"
PORTFOLIO_DECISION = "DEC-039"
OLD_EXPERIMENT = "EXP-20260915-009"
DIAGNOSTIC_EXPERIMENT = "EXP-20260917-010"
PROVIDER = "FP_MARKETS_MT5_DEMO"
ALLOWED_SERVERS = ("FPMarketsSC-Demo", "FPMarketsSC-Demo2")


class Phase8ProtocolStateTests(unittest.TestCase):
    """Guard the DEC-039 Phase 8A state while all execution gates remain locked."""

    def test_phase8a_portfolio_source_of_truth_is_active_and_execution_remains_locked(self) -> None:
        decision_log = Path("docs/decision-log.md").read_text(encoding="utf-8")
        experiment_log = Path("docs/experiment-log.md").read_text(encoding="utf-8")
        state = Path("docs/project-state.md").read_text(encoding="utf-8")
        sources = Path("docs/source-register.md").read_text(encoding="utf-8")
        liveness = Path(
            "docs/superpowers/specs/2026-09-22-phase8-liveness-amendment.md"
        ).read_text(encoding="utf-8")
        redesign = Path(
            "docs/superpowers/specs/2026-09-22-phase8a-portfolio-research-redesign.md"
        ).read_text(encoding="utf-8")

        self.assertIn(f"## {LIVENESS_DECISION} — Phase 8", decision_log)
        self.assertIn(f"## {PORTFOLIO_DECISION} — Phase 8 portfolio-research pivot", decision_log)
        self.assertIn(f"### {STOPPED_EXPERIMENT} — Phase 8", experiment_log)
        self.assertIn("STOPPED BEFORE REGISTRATION / SUPERSEDED BY PHASE 8A", experiment_log)
        self.assertIn(f"### {ACTIVE_EXPERIMENT} — Phase 8A", experiment_log)
        self.assertIn("- Status: ACTIVE — IMPLEMENTATION", experiment_log)
        self.assertIn(OLD_EXPERIMENT, experiment_log)
        self.assertIn("STOPPED BEFORE QUALIFICATION", experiment_log)
        self.assertIn(DIAGNOSTIC_EXPERIMENT, experiment_log)
        self.assertIn("STOPPED FOR LIVENESS AMENDMENT", experiment_log)

        self.assertIn(
            "**Current phase:** Phase 8A — Multi-pair, multi-strategy portfolio research",
            state,
        )
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("## Phase 8 — ACTIVE AS AMENDED PHASE 8A / 8B", state)
        self.assertIn(ACTIVE_EXPERIMENT, state)
        self.assertIn(STOPPED_EXPERIMENT, state)
        self.assertIn("no EXP-011 campaign registration occurred", state)
        self.assertIn(EXPECTED_PHASE7_TAG, state)
        self.assertIn(EXPECTED_PHASE7_SHA, state)
        self.assertIn("EURUSD, GBPUSD, and USDJPY", state)
        self.assertIn("champion", state.lower())
        self.assertIn("challenger", state.lower())

        self.assertIn(PROVIDER, sources)
        for server in ALLOWED_SERVERS:
            self.assertIn(server, sources)
        self.assertIn("2026-09-17", sources)

        self.assertIn("**Status:** APPROVED / ACTIVATED", liveness)
        self.assertIn("market_quiet", liveness)
        self.assertIn("OUTCOME_UNKNOWN_AFTER_GAP", liveness)
        self.assertIn("5-second quote deadline", liveness)

        self.assertIn("**Status:** APPROVED", redesign)
        self.assertIn("EURUSD", redesign)
        self.assertIn("GBPUSD", redesign)
        self.assertIn("USDJPY", redesign)
        self.assertIn("RETIRE", redesign.upper())
        self.assertIn("continuous learning", redesign.lower())
        self.assertIn("must not describe them as an untouched final test", redesign)

        self.assertIn("DEC-008", decision_log)
        self.assertIn("Phase 9/demo order placement: LOCKED", state)
        self.assertIn("production/live order placement and broker mutation: LOCKED", state)
        self.assertIn("Real-money trading: locked", state)
        self.assertIn("no practice/demo order placement", liveness.lower())


if __name__ == "__main__":
    unittest.main()
