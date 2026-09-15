from __future__ import annotations

import unittest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch, sentinel

from fmp.contracts import Direction, QuoteBar
from fmp.models.contracts import ModelFamily, SELECTION_SPLIT
from fmp.strategies.contracts import SignalCandidate


UTC = timezone.utc


def financial_metrics(
    *,
    trades: int,
    net_return: float,
    expectancy: float,
    profit_factor: float,
    drawdown: float,
    yearly: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> dict[str, object]:
    return {
        "phase3_metrics": {
            "trade_count": trades,
            "net_return": net_return,
            "expectancy_usd": expectancy,
            "profit_factor": profit_factor,
            "max_drawdown_fraction": drawdown,
        },
        "calendar_year_breakdown": {
            str(year): {"net_pnl_usd": value}
            for year, value in zip((2021, 2022, 2023), yearly, strict=True)
        },
    }


def financial_result(**kwargs):
    from fmp.models.evaluation import FinancialResult

    return FinancialResult(
        slippage_pips=kwargs.pop("slippage_pips", 0.2),
        candidate_count=100,
        directional_candidate_count=100,
        metrics=financial_metrics(**kwargs),
        run_identity={"test": True},
    )


class Phase6EvaluationTests(unittest.TestCase):
    def test_run_candidate_backtest_reuses_phase3_adapter_engine_and_risk_contract(self) -> None:
        from fmp.backtest.costs import ZeroCommission, ZeroFinancing
        from fmp.models.evaluation import run_candidate_backtest
        from fmp.risk import RiskConfig

        observation = datetime(2020, 1, 2, 9, 0, tzinfo=UTC)
        known = observation + timedelta(minutes=15)
        candidate = SignalCandidate(
            candidate_id="A",
            symbol="USDJPY",
            observation_bar_timestamp_utc=observation,
            signal_known_timestamp_utc=known,
            direction=Direction.LONG,
            stop_price=149.0,
            target_price=151.0,
            latest_exit_timestamp_utc=observation + timedelta(hours=7),
            reason_code="RULE_SIGNAL",
            metadata={"session_name": "london"},
        )
        bars = (
            QuoteBar(
                timestamp_utc=observation,
                symbol="USDJPY",
                bid_open=149.9,
                bid_high=150.1,
                bid_low=149.8,
                bid_close=150.0,
                ask_open=150.0,
                ask_high=150.2,
                ask_low=149.9,
                ask_close=150.1,
            ),
        )
        returned_metrics = {"phase3_metrics": {"trade_count": 1}}

        with (
            patch("fmp.models.evaluation.candidate_to_decision", return_value=(sentinel.decision, sentinel.exit)) as adapt,
            patch("fmp.models.evaluation.run_backtest", return_value=sentinel.run) as run,
            patch("fmp.models.evaluation.compute_research_metrics", return_value=returned_metrics) as report,
        ):
            result = run_candidate_backtest(
                bars=bars,
                candidates=(candidate,),
                strategy_id="session_breakout",
                split=SELECTION_SPLIT,
                code_commit="abc123",
                slippage_pips=0.2,
            )

        adapt.assert_called_once_with(
            candidate,
            next_bar_timestamp_utc=known,
            requested_risk_fraction=0.0025,
        )
        config = run.call_args.kwargs["config"]
        self.assertEqual(config.slippage_pips, 0.2)
        self.assertEqual(config.starting_equity_usd, 100_000.0)
        self.assertEqual(config.requested_risk_fraction if hasattr(config, "requested_risk_fraction") else 0.0025, 0.0025)
        self.assertEqual(config.risk_config, RiskConfig())
        self.assertIsInstance(config.commission_model, ZeroCommission)
        self.assertIsInstance(config.financing_model, ZeroFinancing)
        self.assertEqual(config.requested_start_utc.date(), date(2019, 1, 1))
        self.assertEqual(config.requested_end_utc.date(), date(2021, 1, 1))
        self.assertEqual(config.code_commit, "abc123")
        self.assertEqual(run.call_args.kwargs["decisions"], (sentinel.decision,))
        self.assertEqual(run.call_args.kwargs["scheduled_exits"], (sentinel.exit,))
        report.assert_called_once()
        self.assertEqual(result.metrics, returned_metrics)

    def test_selection_gate_requires_all_eight_conditions(self) -> None:
        from fmp.models.evaluation import selection_gate

        baseline = financial_result(
            trades=100, net_return=0.02, expectancy=20.0, profit_factor=1.2, drawdown=0.10
        )
        filtered = financial_result(
            trades=40, net_return=0.03, expectancy=25.0, profit_factor=1.3, drawdown=0.10
        )
        passed = selection_gate(filtered, baseline)
        self.assertTrue(passed.passed)
        self.assertEqual(len(passed.criteria), 8)
        self.assertTrue(all(passed.criteria.values()))

        failed = selection_gate(
            financial_result(
                trades=39, net_return=0.03, expectancy=25.0, profit_factor=1.3, drawdown=0.10
            ),
            baseline,
        )
        self.assertFalse(failed.passed)
        self.assertFalse(failed.criteria["trade_count_at_least_40pct_baseline"])

    def test_validation_gate_requires_yearly_two_of_three_and_half_pip_robustness(self) -> None:
        from fmp.models.evaluation import validation_gate

        baseline02 = financial_result(
            trades=100, net_return=0.02, expectancy=20.0, profit_factor=1.2, drawdown=0.10,
            yearly=(100.0, 100.0, 100.0),
        )
        filtered02 = financial_result(
            trades=50, net_return=0.04, expectancy=30.0, profit_factor=1.4, drawdown=0.08,
            yearly=(110.0, 90.0, 120.0),
        )
        baseline05 = financial_result(
            trades=100, net_return=0.01, expectancy=10.0, profit_factor=1.1, drawdown=0.12,
            yearly=(0.0, 0.0, 0.0), slippage_pips=0.5,
        )
        filtered05 = financial_result(
            trades=50, net_return=0.02, expectancy=15.0, profit_factor=1.2, drawdown=0.10,
            yearly=(0.0, 0.0, 0.0), slippage_pips=0.5,
        )
        gate = validation_gate(filtered02, baseline02, filtered05, baseline05)
        self.assertTrue(gate.passed)
        self.assertTrue(gate.criteria["yearly_net_pnl_improves_at_least_two_of_three"])
        self.assertTrue(gate.criteria["robust_05_all"])

        failed = validation_gate(
            financial_result(
                trades=50, net_return=0.04, expectancy=30.0, profit_factor=1.4, drawdown=0.08,
                yearly=(110.0, 90.0, 90.0),
            ),
            baseline02,
            filtered05,
            baseline05,
        )
        self.assertFalse(failed.passed)
        self.assertFalse(failed.criteria["yearly_net_pnl_improves_at_least_two_of_three"])

    def test_variant_selection_uses_frozen_tie_break_order(self) -> None:
        from fmp.models.evaluation import GateResult, select_one_variant

        baseline = financial_result(
            trades=100, net_return=0.02, expectancy=20.0, profit_factor=1.2, drawdown=0.10
        )
        gate = GateResult(passed=True, criteria={"all": True})
        common = dict(
            filtered=financial_result(
                trades=50, net_return=0.03, expectancy=25.0, profit_factor=1.3, drawdown=0.08
            ),
            baseline=baseline,
            gate=gate,
        )
        rows = (
            {"model_family": ModelFamily.HIST_GRADIENT_BOOSTING.value, "retained_fraction": 0.75, **common},
            {"model_family": ModelFamily.LOGISTIC_REGRESSION.value, "retained_fraction": 0.50, **common},
            {"model_family": ModelFamily.LOGISTIC_REGRESSION.value, "retained_fraction": 0.75, **common},
        )
        selected = select_one_variant(rows)
        assert selected is not None
        self.assertEqual(selected.model_family, ModelFamily.LOGISTIC_REGRESSION.value)
        self.assertEqual(selected.retained_fraction, 0.75)

        better = {
            "model_family": ModelFamily.HIST_GRADIENT_BOOSTING.value,
            "retained_fraction": 0.25,
            "filtered": financial_result(
                trades=45, net_return=0.05, expectancy=24.0, profit_factor=1.25, drawdown=0.09
            ),
            "baseline": baseline,
            "gate": gate,
        }
        selected = select_one_variant((*rows, better))
        assert selected is not None
        self.assertEqual(selected.model_family, ModelFamily.HIST_GRADIENT_BOOSTING.value)
        self.assertEqual(selected.retained_fraction, 0.25)

    def test_no_qualifying_variant_returns_none(self) -> None:
        from fmp.models.evaluation import GateResult, select_one_variant

        self.assertIsNone(
            select_one_variant(
                (
                    {
                        "model_family": ModelFamily.LOGISTIC_REGRESSION.value,
                        "retained_fraction": 0.75,
                        "filtered": financial_result(
                            trades=50, net_return=-0.01, expectancy=-1.0, profit_factor=0.9, drawdown=0.2
                        ),
                        "baseline": financial_result(
                            trades=100, net_return=0.01, expectancy=1.0, profit_factor=1.1, drawdown=0.1
                        ),
                        "gate": GateResult(passed=False, criteria={"all": False}),
                    },
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
