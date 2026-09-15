from __future__ import annotations

import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.contracts import SignalCandidate
from fmp.walkforward.data import LoadedPhase7Bars


def bar(timestamp: datetime) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=timestamp,
        symbol="USDJPY",
        bid_open=150.00,
        bid_high=150.10,
        bid_low=149.90,
        bid_close=150.04,
        ask_open=150.02,
        ask_high=150.12,
        ask_low=149.92,
        ask_close=150.06,
    )


def loaded_15m() -> LoadedPhase7Bars:
    warmup = bar(datetime(2023, 12, 31, 23, 45, tzinfo=timezone.utc))
    scored = (
        bar(datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)),
        bar(datetime(2024, 1, 1, 0, 15, tzinfo=timezone.utc)),
        bar(datetime(2024, 1, 1, 0, 30, tzinfo=timezone.utc)),
    )
    return LoadedPhase7Bars(
        bars=(warmup, *scored),
        scored_bars=scored,
        eligible_scored_dates=(date(2024, 1, 1),),
        opened_partition_keys=("15m:2023-12", "15m:2024-01"),
        warmup_range=(
            datetime(2023, 12, 25, tzinfo=timezone.utc),
            datetime(2024, 1, 1, tzinfo=timezone.utc),
        ),
    )


def loaded_1h() -> LoadedPhase7Bars:
    warmup = bar(datetime(2023, 12, 31, 23, 0, tzinfo=timezone.utc))
    scored = (
        bar(datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)),
        bar(datetime(2024, 1, 1, 1, 0, tzinfo=timezone.utc)),
    )
    return LoadedPhase7Bars(
        bars=(warmup, *scored),
        scored_bars=scored,
        eligible_scored_dates=(date(2024, 1, 1),),
        opened_partition_keys=("1h:2023-12", "1h:2024-01"),
        warmup_range=(
            datetime(2023, 12, 25, tzinfo=timezone.utc),
            datetime(2024, 1, 1, tzinfo=timezone.utc),
        ),
    )


def no_trade(candidate_id: str, observation: datetime, known: datetime) -> SignalCandidate:
    return SignalCandidate(
        candidate_id=candidate_id,
        symbol="USDJPY",
        observation_bar_timestamp_utc=observation,
        signal_known_timestamp_utc=known,
        direction=Direction.NO_TRADE,
        stop_price=None,
        target_price=None,
        latest_exit_timestamp_utc=None,
        reason_code="TEST_NO_TRADE",
        metadata={"session_name": "london"},
    )


class Phase7EvaluationTests(unittest.TestCase):
    def test_frozen_strategy_configs_are_exact_with_no_grid_surface(self) -> None:
        from fmp.strategies.session_breakout import SessionBreakoutConfig
        from fmp.strategies.volatility_breakout import VolatilityBreakoutConfig
        from fmp.walkforward.evaluation import evaluate_window

        with patch("fmp.walkforward.evaluation.generate_session_breakout_candidates", return_value=()) as generator:
            evaluate_window(
                loaded_15m(),
                candidate_id="session_breakout",
                window_name="stage1-2024",
                slippage_pips=0.2,
                code_commit="abc123",
            )
        self.assertEqual(
            generator.call_args.kwargs["config"],
            SessionBreakoutConfig(buffer_pips=5, target_range_multiple=1.5, timeframe="15m"),
        )
        self.assertEqual(generator.call_args.args[0], loaded_15m().bars)

        with patch("fmp.walkforward.evaluation.generate_volatility_breakout_candidates", return_value=()) as generator:
            evaluate_window(
                loaded_1h(),
                candidate_id="volatility_breakout",
                window_name="stage1-2024",
                slippage_pips=0.5,
                code_commit="abc123",
            )
        self.assertEqual(
            generator.call_args.kwargs["config"],
            VolatilityBreakoutConfig(range_multiplier=2.0, timeframe="1h"),
        )

    def test_warmup_candidates_are_never_adapted_or_scored(self) -> None:
        from fmp.research.adapter import candidate_to_decision as real_adapter
        from fmp.walkforward.evaluation import evaluate_window

        loaded = loaded_15m()
        warmup_candidate = no_trade(
            "warmup",
            datetime(2023, 12, 31, 23, 45, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
        )
        scored_candidate = no_trade(
            "scored",
            datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 0, 15, tzinfo=timezone.utc),
        )
        with patch(
            "fmp.walkforward.evaluation.generate_session_breakout_candidates",
            return_value=(warmup_candidate, scored_candidate),
        ), patch(
            "fmp.walkforward.evaluation.candidate_to_decision",
            wraps=real_adapter,
        ) as adapter:
            result = evaluate_window(
                loaded,
                candidate_id="session_breakout",
                window_name="stage1-2024",
                slippage_pips=0.2,
                code_commit="abc123",
            )

        self.assertEqual(result.candidate_count, 2)
        self.assertEqual(result.scored_candidate_count, 1)
        self.assertEqual(result.directional_candidate_count, 0)
        self.assertEqual(adapter.call_count, 1)
        self.assertIs(adapter.call_args.args[0], scored_candidate)
        self.assertEqual(result.trade_count, 0)
        self.assertEqual(result.gross_profit_usd, 0.0)
        self.assertEqual(result.gross_loss_usd, 0.0)
        self.assertEqual(result.warmup_range, loaded.warmup_range)
        self.assertEqual(result.opened_partition_keys, loaded.opened_partition_keys)
        self.assertEqual(result.refit_status, "NOT_APPLICABLE_FIXED_RULE")

    def test_evaluation_reuses_phase3_engine_costs_risk_and_scored_bars_only(self) -> None:
        from fmp.backtest.engine import run_backtest as real_run_backtest
        from fmp.research.reporting import compute_research_metrics as real_metrics
        from fmp.walkforward.evaluation import evaluate_window

        loaded = loaded_15m()
        scored_candidate = no_trade(
            "scored",
            datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 0, 15, tzinfo=timezone.utc),
        )
        with patch(
            "fmp.walkforward.evaluation.generate_session_breakout_candidates",
            return_value=(scored_candidate,),
        ), patch(
            "fmp.walkforward.evaluation.run_backtest",
            wraps=real_run_backtest,
        ) as engine, patch(
            "fmp.walkforward.evaluation.compute_research_metrics",
            wraps=real_metrics,
        ) as metrics:
            result = evaluate_window(
                loaded,
                candidate_id="session_breakout",
                window_name="stage1-2024",
                slippage_pips=1.0,
                code_commit="abc123",
            )

        self.assertEqual(engine.call_args.kwargs["bars"], loaded.scored_bars)
        self.assertEqual(metrics.call_args.kwargs["eligible_utc_dates"], loaded.eligible_scored_dates)
        identity = result.run_identity
        self.assertEqual(identity["starting_equity_usd"], 100_000.0)
        self.assertEqual(identity["slippage_pips"], 1.0)
        self.assertEqual(identity["commission_model"], {"model": "zero_commission"})
        self.assertEqual(identity["financing_model"], {"model": "zero_financing"})
        self.assertEqual(identity["requested_start_utc"], datetime(2024, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(identity["requested_end_utc"], datetime(2025, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(identity["decision_config"]["experiment_id"], "EXP-20260915-008")
        self.assertEqual(identity["decision_config"]["refit_status"], "NOT_APPLICABLE_FIXED_RULE")

    def test_unapproved_cost_and_mismatched_loaded_contract_fail_closed(self) -> None:
        from fmp.walkforward.evaluation import evaluate_window

        with self.assertRaisesRegex(ValueError, "slippage"):
            evaluate_window(
                loaded_15m(),
                candidate_id="session_breakout",
                window_name="stage1-2024",
                slippage_pips=0.3,
                code_commit="abc123",
            )
        with self.assertRaisesRegex(ValueError, "code_commit"):
            evaluate_window(
                loaded_15m(),
                candidate_id="session_breakout",
                window_name="stage1-2024",
                slippage_pips=0.2,
                code_commit="",
            )
        bad = loaded_15m()
        bad = LoadedPhase7Bars(
            bars=bad.bars,
            scored_bars=bad.scored_bars,
            eligible_scored_dates=bad.eligible_scored_dates,
            opened_partition_keys=("1h:2023-12", "1h:2024-01"),
            warmup_range=bad.warmup_range,
        )
        with self.assertRaisesRegex(ValueError, "partition"):
            evaluate_window(
                bad,
                candidate_id="session_breakout",
                window_name="stage1-2024",
                slippage_pips=0.2,
                code_commit="abc123",
            )


if __name__ == "__main__":
    unittest.main()
