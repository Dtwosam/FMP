from datetime import date, datetime, timedelta, timezone
import unittest
from zoneinfo import ZoneInfo

from fmp.contracts import QuoteBar
from fmp.portfolio import StrategyVersion
from fmp.portfolio.research_data import (
    LoadedRetrospectiveBars,
    PHASE8A_RETROSPECTIVE_LABEL,
    RetrospectiveRange,
)
from fmp.portfolio.research_runner import (
    Phase8ARetrospectivePlan,
    build_strategy_config,
    run_phase8a_retrospective_strategy,
    summarize_daily_returns,
)
from fmp.strategies.mean_reversion import MeanReversionConfig
from fmp.strategies.session_breakout import SessionBreakoutConfig
from fmp.strategies.trend_continuation import TrendContinuationConfig
from fmp.strategies.volatility_breakout import VolatilityBreakoutConfig


LONDON = ZoneInfo("Europe/London")
STRATEGY_COMMIT = "c" * 40
RUNNER_COMMIT = "d" * 40


def _version(
    family: str,
    *,
    symbol: str = "EURUSD",
    timeframe: str = "1h",
    parameters: dict[str, object],
) -> StrategyVersion:
    return StrategyVersion.create(
        family=family,
        version="phase8a-test-v1",
        symbol=symbol,
        timeframe=timeframe,
        parameters=parameters,
        signal_contract_version="phase8a-test-signal-v1",
        code_commit=STRATEGY_COMMIT,
    )


def _bar(ts: datetime, *, close: float = 1.1000) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=ts,
        symbol="EURUSD",
        bid_open=close - 0.0001,
        bid_high=close + 0.0004,
        bid_low=close - 0.0004,
        bid_close=close - 0.0001,
        ask_open=close + 0.0001,
        ask_high=close + 0.0006,
        ask_low=close - 0.0002,
        ask_close=close + 0.0001,
    )


def _neutral_london_day(day: date) -> tuple[QuoteBar, ...]:
    start = datetime(day.year, day.month, day.day, tzinfo=LONDON).astimezone(timezone.utc)
    return tuple(_bar(start + timedelta(hours=hour)) for hour in range(17))


class Phase8ARetrospectiveRunnerTests(unittest.TestCase):
    def test_plan_freezes_retrospective_label_cost_and_identity(self) -> None:
        strategy = _version(
            "session_breakout",
            parameters={"buffer_pips": 5, "target_range_multiple": 1.5},
        )
        plan = Phase8ARetrospectivePlan(
            experiment_id="EXP-20260922-012-TEST",
            strategy=strategy,
            research_range=RetrospectiveRange(
                start=date(2020, 1, 1),
                end_exclusive=date(2020, 2, 1),
            ),
            slippage_pips=0.5,
            runner_code_commit=RUNNER_COMMIT,
        )
        self.assertEqual(plan.evidence_label, PHASE8A_RETROSPECTIVE_LABEL)
        self.assertFalse(plan.untouched_oos)
        self.assertEqual(plan.requested_risk_fraction, 0.0025)
        self.assertEqual(plan.starting_equity_usd, 100_000.0)

        with self.assertRaises(ValueError):
            Phase8ARetrospectivePlan(
                experiment_id="EXP-20260922-012-TEST",
                strategy=strategy,
                research_range=plan.research_range,
                slippage_pips=0.3,
                runner_code_commit=RUNNER_COMMIT,
            )
        with self.assertRaises(ValueError):
            Phase8ARetrospectivePlan(
                experiment_id="EXP-20260922-012-TEST",
                strategy=strategy,
                research_range=plan.research_range,
                slippage_pips=0.2,
                runner_code_commit="bad",
            )

    def test_family_config_dispatch_is_exact_and_rejects_unknown_shapes(self) -> None:
        session = build_strategy_config(
            _version(
                "session_breakout",
                parameters={"buffer_pips": 2, "target_range_multiple": 1.0},
            )
        )
        self.assertIsInstance(session, SessionBreakoutConfig)

        trend = build_strategy_config(
            _version(
                "trend_continuation",
                parameters={"trend_window_id": "B", "target_r_multiple": 1.5},
            )
        )
        self.assertIsInstance(trend, TrendContinuationConfig)

        mean = build_strategy_config(
            _version(
                "mean_reversion",
                parameters={"lookback_hours": 8, "threshold_sigma": 2.0},
            )
        )
        self.assertIsInstance(mean, MeanReversionConfig)

        vol = build_strategy_config(
            _version(
                "volatility_breakout",
                parameters={"range_multiplier": 1.5},
            )
        )
        self.assertIsInstance(vol, VolatilityBreakoutConfig)

        with self.assertRaises(ValueError):
            build_strategy_config(
                _version(
                    "session_breakout",
                    parameters={
                        "buffer_pips": 2,
                        "target_range_multiple": 1.0,
                        "post_result_rescue": True,
                    },
                )
            )
        with self.assertRaises(ValueError):
            build_strategy_config(
                _version("unknown_family", parameters={"x": 1})
            )

    def test_daily_return_summary_reports_high_return_day_frequency_without_claiming_target(self) -> None:
        summary = summarize_daily_returns(
            [
                {"date": "2026-01-01", "return": 0.12},
                {"date": "2026-01-02", "return": -0.03},
                {"date": "2026-01-03", "return": 0.10},
                {"date": "2026-01-04", "return": 0.01},
            ]
        )
        self.assertEqual(summary["observed_days"], 4)
        self.assertEqual(summary["days_ge_10pct"], 2)
        self.assertEqual(summary["days_ge_10pct_fraction"], 0.5)
        self.assertEqual(summary["best_day_return"], 0.12)
        self.assertEqual(summary["worst_day_return"], -0.03)

    def test_runner_emits_explicit_retrospective_identity_on_previously_seen_history(self) -> None:
        strategy = _version(
            "session_breakout",
            parameters={"buffer_pips": 5, "target_range_multiple": 1.5},
        )
        plan = Phase8ARetrospectivePlan(
            experiment_id="EXP-20260922-012-TEST",
            strategy=strategy,
            research_range=RetrospectiveRange(
                start=date(2020, 1, 2),
                end_exclusive=date(2020, 1, 3),
            ),
            slippage_pips=0.2,
            runner_code_commit=RUNNER_COMMIT,
        )
        bars = _neutral_london_day(date(2020, 1, 2))
        loaded = LoadedRetrospectiveBars(
            bars=bars,
            excluded_incomplete_count=0,
            eligible_utc_dates=(date(2020, 1, 2),),
            evidence_label=PHASE8A_RETROSPECTIVE_LABEL,
            start=date(2020, 1, 2),
            end_exclusive=date(2020, 1, 3),
            processed_manifest_sha256="e" * 64,
            opened_artifact_months=("2020-01",),
        )

        result = run_phase8a_retrospective_strategy(
            plan=plan,
            dataset_root=None,
            manifest_path=None,
            bars_loader=lambda **_: loaded,
        )

        self.assertEqual(result["protocol"], "fmp-phase8a-retrospective-strategy-v1")
        self.assertEqual(result["evidence_label"], PHASE8A_RETROSPECTIVE_LABEL)
        self.assertFalse(result["untouched_oos"])
        self.assertEqual(result["strategy_fingerprint"], strategy.fingerprint)
        self.assertEqual(result["runner_code_commit"], RUNNER_COMMIT)
        self.assertEqual(result["processed_manifest_sha256"], "e" * 64)
        self.assertEqual(result["opened_artifact_months"], ["2020-01"])
        self.assertIn("daily_return_summary", result["metrics"])


if __name__ == "__main__":
    unittest.main()
