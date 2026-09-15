from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class Phase4ResearchStateTests(unittest.TestCase):
    def test_dec018_freezes_split_timing_grid_costs_and_risk(self) -> None:
        text = read("docs/decision-log.md")
        self.assertIn("DEC-018 — Phase 4 baseline research protocol — APPROVED", text)
        self.assertIn("## DEC-018 — Phase 4 baseline research protocol", text)
        self.assertIn("Development: 2015-01-01 through 2020-12-31 inclusive", text)
        self.assertIn("Validation: 2021-01-01 through 2023-12-31 inclusive", text)
        self.assertIn("Final untouched test: 2024-01-01 through 2026-08-20 inclusive", text)
        self.assertIn("final-test data is unavailable from the normal development/validation runner", text)
        self.assertIn("observation label `T`", text)
        self.assertIn("true signal-known time is `T + W`", text)
        self.assertIn("earliest executable timestamp is `T + W`", text)
        self.assertIn("(0, 0.5), (0, 1.0), (0, 1.5)", text)
        self.assertIn("(2, 0.5), (2, 1.0), (2, 1.5)", text)
        self.assertIn("(5, 0.5), (5, 1.0), (5, 1.5)", text)
        self.assertIn("0.2, 0.5, and 1.0 pips per fill", text)
        self.assertIn("zero commission and zero financing", text)
        self.assertIn("requested risk/trade: 0.25%", text)
        self.assertIn("hard max risk/trade: 0.50%", text)
        self.assertIn("maximum simultaneous open risk: 1.00%", text)
        self.assertIn("daily realized-loss halt: 1.50%", text)
        self.assertIn("DEC-008 remains unchanged", text)

    def test_first_serious_experiment_preserves_predeclared_protocol_after_result(self) -> None:
        text = read("docs/experiment-log.md")
        marker = "### EXP-20260914-001 — Session breakout baseline"
        self.assertIn(marker, text)
        section = text.split(marker, 1)[1]
        self.assertIn("- Status: PASS", section)
        self.assertIn("After a completed pre-London range", section)
        self.assertIn(
            "- Code commit: `cc01929b80cbd1d5619de8476caa8f3d3410262e`",
            section,
        )
        self.assertIn("- Pair(s): EURUSD, GBPUSD, USDJPY", section)
        self.assertIn("- Timeframe(s): 5m, 15m, 1h", section)
        self.assertIn("- Train period: 2015-01-01 through 2020-12-31 inclusive", section)
        self.assertIn("- Validation period: 2021-01-01 through 2023-12-31 inclusive", section)
        self.assertIn("- Final-test touched?: NO", section)
        self.assertIn("buffer_pips = {0, 2, 5}", section)
        self.assertIn("target_range_multiple = {0.5, 1.0, 1.5}", section)
        self.assertIn("historical BID/ASK spread", section)
        self.assertIn("0.2, 0.5, 1.0 pips per fill", section)
        self.assertIn("zero commission; zero financing", section)
        self.assertIn("0.25% requested", section)
        self.assertIn("0.50% hard per-trade max", section)
        self.assertIn("1.00% simultaneous max", section)
        self.assertIn("1.50% UTC day-start realized-loss halt", section)
        self.assertIn("- Conclusion: PROMOTE", section)
        self.assertIn("USDJPY 15m", section)
        self.assertIn("trend continuation", section.lower())

    def test_project_state_preserves_phase4_pass_and_locks_later_phases(self) -> None:
        text = read("docs/project-state.md")
        self.assertIn("**Current phase:** Phase 6 — Statistical / ML Filters", text)
        self.assertIn("**Phase status:** PASS", text)
        self.assertIn("## Phase 3 — PASS", text)
        self.assertIn("## Phase 4 — PASS", text)
        self.assertIn("## Phase 5 — PASS", text)
        self.assertIn("## Phase 6 — PASS", text)
        self.assertIn("Final-test touched: NO", text)
        self.assertIn("Real-money trading: locked", text)
        self.assertIn("DEC-008 remains unchanged", text)


if __name__ == "__main__":
    unittest.main()
