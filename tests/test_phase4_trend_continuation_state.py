from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class Phase4TrendContinuationStateTests(unittest.TestCase):
    def test_dec019_freezes_family_specific_protocol(self) -> None:
        text = read("docs/decision-log.md")
        self.assertIn("DEC-019 — Phase 4 trend-continuation baseline protocol — APPROVED", text)
        self.assertIn("## DEC-019 — Phase 4 trend-continuation baseline protocol", text)
        section = text.split("## DEC-019 — Phase 4 trend-continuation baseline protocol", 1)[1]
        for value in (
            "2h/8h",
            "4h/16h",
            "8h/32h",
            "1.0R",
            "1.5R",
            "08:00",
            "14:00",
            "Europe/London",
            "16:00",
            "three-bar structural stop",
            "6 strategy configurations",
            "324 benchmark configuration rows",
            "0.2, 0.5, and 1.0 pips per fill",
            "zero commission and zero financing",
            "requested risk/trade: 0.25%",
            "hard max risk/trade: 0.50%",
            "maximum simultaneous open risk: 1.00%",
            "daily realized-loss halt: 1.50%",
            "no post-result parameter expansion",
            "Final untouched test: 2024-01-01 through 2026-08-20 inclusive",
        ):
            self.assertIn(value, section)
        self.assertIn("DEC-018 remains authoritative", section)
        self.assertIn("DEC-008 remains unchanged", section)

    def test_exp002_preserves_predeclared_protocol_after_rejection(self) -> None:
        text = read("docs/experiment-log.md")
        marker = "### EXP-20260914-002 — Trend continuation baseline"
        self.assertIn(marker, text)
        section = text.split(marker, 1)[1]
        self.assertIn("- Status: FAIL", section)
        self.assertIn("pullback", section.lower())
        self.assertIn("- Pair(s): EURUSD, GBPUSD, USDJPY", section)
        self.assertIn("- Timeframe(s): 5m, 15m, 1h", section)
        self.assertIn("- Train period: 2015-01-01 through 2020-12-31 inclusive", section)
        self.assertIn("- Validation period: 2021-01-01 through 2023-12-31 inclusive", section)
        self.assertIn("- Final-test touched?: NO", section)
        self.assertIn("2h/8h", section)
        self.assertIn("4h/16h", section)
        self.assertIn("8h/32h", section)
        self.assertIn("1.0R", section)
        self.assertIn("1.5R", section)
        self.assertIn("0.2, 0.5, 1.0 pips per fill", section)
        self.assertIn("zero commission; zero financing", section)
        self.assertIn("0.25% requested", section)
        self.assertIn("0.50% hard per-trade max", section)
        self.assertIn("1.00% simultaneous max", section)
        self.assertIn("1.50% UTC day-start realized-loss halt", section)
        self.assertIn("- Result summary:", section)
        self.assertIn("- Conclusion: REJECT", section)
        self.assertIn("no post-result parameter expansion", section.lower())

    def test_project_state_preserves_phase4_pass_and_frozen_candidate(self) -> None:
        text = read("docs/project-state.md")
        self.assertIn("**Current phase:** Phase 6 — Statistical / ML Filters", text)
        self.assertIn("**Phase status:** ACTIVE", text)
        self.assertIn("## Phase 4 — PASS", text)
        self.assertIn("## Phase 5 — PASS", text)
        self.assertIn("## Phase 6 — ACTIVE", text)
        self.assertIn("EXP-20260914-001 — Session breakout baseline", text)
        self.assertIn("USDJPY 15m, 5-pip breakout buffer, 1.5x target-range multiple", text)
        self.assertIn("EXP-20260914-002 — Trend continuation baseline", text)
        self.assertIn("experiment status: FAIL", text)
        self.assertIn("conclusion: REJECT", text)
        self.assertIn("mean reversion", text.lower())
        self.assertIn("Final-test touched: NO", text)
        self.assertIn("Real-money trading: locked", text)
        self.assertIn("DEC-008 remains unchanged", text)


if __name__ == "__main__":
    unittest.main()
