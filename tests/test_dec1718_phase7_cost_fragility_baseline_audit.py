"""DEC-1718: recheck published Phase 7 cost fragility without new research.

This reads only the frozen public historical evidence document. The numbers
are not new profits, predictive live returns, or Phase 8A Strategy V1 evidence.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import unittest


EVIDENCE = (
    Path(__file__).resolve().parents[1]
    / "docs/phase7-walk-forward-evidence.md"
)
EXPECTED = {
    Decimal("0.2"): (Decimal("0.757266"), Decimal("757.27"),
                     Decimal("3.8054"), Decimal("1.062731"), 199, 5),
    Decimal("0.5"): (Decimal("0.262176"), Decimal("262.18"),
                     Decimal("1.3175"), Decimal("1.021310"), 199, 4),
    Decimal("1.0"): (Decimal("-0.562118"), Decimal("-562.12"),
                     Decimal("-2.8247"), Decimal("0.955760"), 199, 4),
}


def _cost_table() -> dict[Decimal, tuple[Decimal, Decimal, Decimal,
                                       Decimal, int, int]]:
    source = EVIDENCE.read_text(encoding="utf-8")
    section = source.split("## Aggregate cost results\n", 1)[1].split(
        "\n## Gate recomputation", 1
    )[0]
    parsed = {}
    for line in section.splitlines():
        if not line.startswith("| ") or " pips |" not in line:
            continue
        fields = [item.strip() for item in line.strip("|").split("|")]
        if len(fields) != 9:
            raise ValueError("Unexpected historical cost table shape")
        slippage = Decimal(fields[0].removesuffix(" pips"))
        if slippage in parsed:
            raise ValueError("Duplicate historical cost row")
        values = (
            Decimal(fields[1].removesuffix("%")),
            Decimal(fields[2].replace("$", "")),
            Decimal(fields[4].replace("$", "")),
            Decimal(fields[5]),
            int(fields[3]),
            int(fields[7].split(" of ")[0]),
        )
        parsed[slippage] = values
    return parsed


class Phase7HistoricalCostSensitivityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = EVIDENCE.read_text(encoding="utf-8")
        cls.rows = _cost_table()

    def test_exact_frozen_three_scenario_cost_inventory(self):
        self.assertEqual(set(self.rows), {Decimal("0.2"), Decimal("0.5"),
                                          Decimal("1.0")})

    def test_all_published_economic_metrics_match_frozen_evidence(self):
        self.assertEqual(self.rows, EXPECTED)

    def test_trade_sample_fixed_across_cost_scenarios(self):
        self.assertEqual([v[4] for _, v in sorted(self.rows.items())],
                         [199, 199, 199])

    def test_cost_increase_reduces_net_historical_return(self):
        returns = [v[0] for _, v in sorted(self.rows.items())]
        self.assertGreater(returns[0], returns[1])
        self.assertGreater(returns[1], returns[2])

    def test_one_pip_scenario_loses_money(self):
        high = self.rows[Decimal("1.0")]
        self.assertLess(high[0], Decimal("0"))
        self.assertLess(high[1], Decimal("0"))
        self.assertLess(high[2], Decimal("0"))
        self.assertLess(high[3], Decimal("1"))

    def test_half_pip_baseline_margin_is_small(self):
        baseline = self.rows[Decimal("0.5")]
        self.assertGreater(baseline[0], Decimal("0"))
        self.assertLess(baseline[0], Decimal("0.3"))
        self.assertLess(baseline[3], Decimal("1.03"))

    def test_cost_stress_reduces_positive_window_count(self):
        counts = [v[5] for _, v in sorted(self.rows.items())]
        self.assertEqual(counts, [5, 4, 4])

    def test_linear_crossing_is_only_an_interpolation_not_an_edge(self):
        positive = self.rows[Decimal("0.5")][0]
        negative = self.rows[Decimal("1.0")][0]
        # Pure arithmetic between reported historical observations. This is
        # NOT a forward break-even execution forecast or promotion threshold.
        interpolated = Decimal("0.5") + Decimal("0.5") * positive / (
            positive - negative
        )
        self.assertGreater(interpolated, Decimal("0.65"))
        self.assertLess(interpolated, Decimal("0.67"))

    def test_one_pip_case_is_diagnostic_not_a_retroactive_promotion_gate(self):
        self.assertIn(
            "The 1.0-pip diagnostic is negative",
            self.source,
        )
        self.assertIn(
            "it is not a promotion gate",
            self.source,
        )

    def test_phase7_outcome_authorizes_shadow_design_only(self):
        self.assertIn(
            "The authoritative Stage 2 status is therefore "
            "PHASE7_PROMOTE_TO_SHADOW_DESIGN.",
            self.source,
        )
        self.assertIn(
            "eligible for Phase 8 shadow design only",
            self.source,
        )
        self.assertIn(
            "does not authorize broker integration, demo trading, "
            "live trading, order placement, or real-money trading",
            self.source,
        )
