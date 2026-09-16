from __future__ import annotations

import inspect
from dataclasses import replace
from pathlib import Path
import unittest

import fmp.shadow.gates as gates_module
from fmp.shadow.cli import build_parser, main
from fmp.shadow.gates import (
    FinancialScenarioMetrics,
    Phase8ReviewEvidence,
    Phase8ReviewOutcome,
    SpreadSummary,
    evaluate_phase8_review,
)


EPS = 1e-9


def _financial(
    *,
    trade_count: int = 45,
    net_return: float = 0.01,
    expectancy_usd: float = 10.0,
    profit_factor: float = 1.2,
    max_drawdown_fraction: float = 0.04,
) -> FinancialScenarioMetrics:
    return FinancialScenarioMetrics(
        trade_count=trade_count,
        net_return=net_return,
        expectancy_usd=expectancy_usd,
        profit_factor=profit_factor,
        max_drawdown_fraction=max_drawdown_fraction,
    )


def _evidence() -> Phase8ReviewEvidence:
    return Phase8ReviewEvidence(
        structural_safety_ok=True,
        durable_artifacts_secret_free=True,
        qualification_pass=True,
        denominator_date_count=40,
        valid_date_count=36,
        fully_observed_london_dates=30,
        malformed_silently_accepted_count=0,
        stale_gap_financial_outcomes_count=0,
        operational_events_complete=True,
        processing_latency_p99_ms=250.0,
        max_entry_quote_delay_seconds=5.0,
        max_time_exit_quote_delay_seconds=5.0,
        historical_entry_spread=SpreadSummary(median_pips=1.0, p95_pips=1.5),
        historical_exit_spread=SpreadSummary(median_pips=1.1, p95_pips=1.6),
        live_entry_spread=SpreadSummary(median_pips=1.5, p95_pips=2.0),
        live_exit_spread=SpreadSummary(median_pips=1.6, p95_pips=2.1),
        scenario_metrics={
            0.2: _financial(),
            0.5: _financial(net_return=0.005, expectancy_usd=5.0, profit_factor=1.1),
            1.0: _financial(net_return=-0.50, expectancy_usd=-500.0, profit_factor=0.1, max_drawdown_fraction=0.50),
        },
        campaign_minimums_met=True,
        replay_identical=True,
    )


class Phase8AcceptanceGateTests(unittest.TestCase):
    def test_review_outcome_values_are_exact(self) -> None:
        self.assertEqual(Phase8ReviewOutcome.PASS.value, "PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN")
        self.assertEqual(Phase8ReviewOutcome.NEED_MORE_DATA.value, "PHASE8_NEED_MORE_DATA")
        self.assertEqual(Phase8ReviewOutcome.REJECT_OPERATIONAL.value, "PHASE8_REJECT_OPERATIONAL_MISMATCH")
        self.assertEqual(Phase8ReviewOutcome.REJECT_MARKET.value, "PHASE8_REJECT_MARKET_MISMATCH")
        self.assertEqual(Phase8ReviewOutcome.REJECT_FINANCIAL.value, "PHASE8_REJECT_FINANCIAL_MISMATCH")
        self.assertEqual(Phase8ReviewOutcome.REJECT_SAFETY.value, "PHASE8_REJECT_SAFETY_FAILURE")

    def test_all_exact_inclusive_boundaries_pass_and_one_pip_scenario_is_diagnostic_only(self) -> None:
        evidence = _evidence()
        self.assertEqual(evaluate_phase8_review(evidence), Phase8ReviewOutcome.PASS)
        diagnostic = dict(evidence.scenario_metrics)
        diagnostic[1.0] = _financial(
            trade_count=1,
            net_return=-0.99,
            expectancy_usd=-10_000.0,
            profit_factor=0.0,
            max_drawdown_fraction=0.99,
        )
        self.assertEqual(
            evaluate_phase8_review(replace(evidence, scenario_metrics=diagnostic)),
            Phase8ReviewOutcome.PASS,
        )

    def test_safety_and_replay_failures_use_dedicated_safety_outcome(self) -> None:
        base = _evidence()
        for changed in (
            replace(base, structural_safety_ok=False),
            replace(base, durable_artifacts_secret_free=False),
            replace(base, replay_identical=False),
        ):
            self.assertEqual(evaluate_phase8_review(changed), Phase8ReviewOutcome.REJECT_SAFETY)

    def test_operational_integrity_and_timing_boundaries_are_exact(self) -> None:
        base = _evidence()
        self.assertEqual(evaluate_phase8_review(base), Phase8ReviewOutcome.PASS)
        failures = (
            replace(base, qualification_pass=False),
            replace(base, valid_date_count=35),  # 35/40 < 90%
            replace(base, malformed_silently_accepted_count=1),
            replace(base, stale_gap_financial_outcomes_count=1),
            replace(base, operational_events_complete=False),
            replace(base, processing_latency_p99_ms=250.0 + EPS),
            replace(base, max_entry_quote_delay_seconds=5.0 + EPS),
            replace(base, max_time_exit_quote_delay_seconds=5.0 + EPS),
        )
        for changed in failures:
            self.assertEqual(
                evaluate_phase8_review(changed),
                Phase8ReviewOutcome.REJECT_OPERATIONAL,
            )
        self.assertEqual(
            evaluate_phase8_review(replace(base, valid_date_count=36, denominator_date_count=40)),
            Phase8ReviewOutcome.PASS,
        )

    def test_short_but_sound_campaign_returns_need_more_data(self) -> None:
        base = _evidence()
        self.assertEqual(
            evaluate_phase8_review(replace(base, campaign_minimums_met=False)),
            Phase8ReviewOutcome.NEED_MORE_DATA,
        )
        scenarios = dict(base.scenario_metrics)
        scenarios[0.2] = replace(scenarios[0.2], trade_count=39)
        self.assertEqual(
            evaluate_phase8_review(replace(base, scenario_metrics=scenarios)),
            Phase8ReviewOutcome.NEED_MORE_DATA,
        )
        self.assertEqual(
            evaluate_phase8_review(
                replace(base, fully_observed_london_dates=29, campaign_minimums_met=False)
            ),
            Phase8ReviewOutcome.NEED_MORE_DATA,
        )

    def test_spread_parity_is_inclusive_at_historical_plus_half_pip(self) -> None:
        base = _evidence()
        self.assertEqual(evaluate_phase8_review(base), Phase8ReviewOutcome.PASS)
        for field, spread in (
            ("live_entry_spread", SpreadSummary(1.5 + EPS, 2.0)),
            ("live_entry_spread", SpreadSummary(1.5, 2.0 + EPS)),
            ("live_exit_spread", SpreadSummary(1.6 + EPS, 2.1)),
            ("live_exit_spread", SpreadSummary(1.6, 2.1 + EPS)),
        ):
            self.assertEqual(
                evaluate_phase8_review(replace(base, **{field: spread})),
                Phase8ReviewOutcome.REJECT_MARKET,
            )

    def test_financial_gates_are_strict_except_drawdown_inclusive_boundary(self) -> None:
        base = _evidence()
        for scenario in (0.2, 0.5):
            for override in (
                {"net_return": 0.0},
                {"expectancy_usd": 0.0},
                {"profit_factor": 1.0},
                {"max_drawdown_fraction": 0.05 + EPS},
            ):
                scenarios = dict(base.scenario_metrics)
                scenarios[scenario] = replace(scenarios[scenario], **override)
                self.assertEqual(
                    evaluate_phase8_review(replace(base, scenario_metrics=scenarios)),
                    Phase8ReviewOutcome.REJECT_FINANCIAL,
                )

        scenarios = dict(base.scenario_metrics)
        scenarios[0.2] = replace(
            scenarios[0.2],
            net_return=EPS,
            expectancy_usd=EPS,
            profit_factor=1.0 + EPS,
            max_drawdown_fraction=0.05,
        )
        scenarios[0.5] = replace(
            scenarios[0.5],
            net_return=EPS,
            expectancy_usd=EPS,
            profit_factor=1.0 + EPS,
            max_drawdown_fraction=0.05,
        )
        self.assertEqual(
            evaluate_phase8_review(replace(base, scenario_metrics=scenarios)),
            Phase8ReviewOutcome.PASS,
        )

    def test_gate_module_is_pure_and_review_cli_is_offline_without_threshold_overrides(self) -> None:
        source = inspect.getsource(gates_module)
        for forbidden in ("OandaPracticePricingStream", "urllib", "http.client", "requests"):
            self.assertNotIn(forbidden, source)

        parser = build_parser()
        args = parser.parse_args(["review", "--campaign-dir", "campaign"])
        self.assertEqual(args.command, "review")
        for forbidden in (
            "minimum_trades",
            "coverage",
            "latency",
            "spread_tolerance",
            "slippage",
            "host",
            "instrument",
        ):
            self.assertFalse(hasattr(args, forbidden))

        calls: list[Path] = []
        rc = main(
            ["review", "--campaign-dir", "campaign"],
            environ={},
            review_command=lambda path: calls.append(path) or Phase8ReviewOutcome.PASS,
        )
        self.assertEqual(rc, 0)
        self.assertEqual(calls, [Path("campaign")])


if __name__ == "__main__":
    unittest.main()
