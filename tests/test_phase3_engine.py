from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.backtest.engine import (
    DECLARED_EARLIEST_BAR,
    NEXT_SUPPLIED_BAR,
    BacktestConfig,
    run_backtest,
)
from fmp.contracts import Decision, Direction, ExitReason, QuoteBar, RejectionCode, ScheduledExit
from fmp.risk import RiskConfig


DAY = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)


def eurusd_bar(
    minute: int,
    *,
    bid_open: float = 1.1000,
    bid_high: float = 1.1008,
    bid_low: float = 1.0995,
    bid_close: float = 1.1003,
    ask_open: float = 1.1002,
    ask_high: float = 1.1010,
    ask_low: float = 1.0997,
    ask_close: float = 1.1005,
    day: datetime = DAY,
) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=day + timedelta(minutes=minute),
        symbol="EURUSD",
        bid_open=bid_open,
        bid_high=bid_high,
        bid_low=bid_low,
        bid_close=bid_close,
        ask_open=ask_open,
        ask_high=ask_high,
        ask_low=ask_low,
        ask_close=ask_close,
    )


def gbpusd_bar(minute: int, *, target_hit: bool = False) -> QuoteBar:
    high = 1.3025 if target_hit else 1.3010
    return QuoteBar(
        timestamp_utc=DAY + timedelta(minutes=minute),
        symbol="GBPUSD",
        bid_open=1.3000,
        bid_high=high,
        bid_low=1.2995,
        bid_close=1.3004,
        ask_open=1.3002,
        ask_high=high + 0.0002,
        ask_low=1.2997,
        ask_close=1.3006,
    )


def usdjpy_bar(minute: int) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=DAY + timedelta(minutes=minute),
        symbol="USDJPY",
        bid_open=150.00,
        bid_high=150.08,
        bid_low=149.95,
        bid_close=150.03,
        ask_open=150.02,
        ask_high=150.10,
        ask_low=149.97,
        ask_close=150.05,
    )


def long_decision(
    decision_id: str,
    *,
    symbol: str = "EURUSD",
    decision_minute: int,
    executable_minute: int,
    requested_risk_fraction: float | None = None,
    stop_price: float | None = None,
    target_price: float | None = None,
    day: datetime = DAY,
) -> Decision:
    defaults = {
        "EURUSD": (1.0992, None),
        "GBPUSD": (1.2992, None),
        "USDJPY": (149.90, None),
    }
    default_stop, default_target = defaults[symbol]
    return Decision(
        decision_id=decision_id,
        symbol=symbol,
        decision_timestamp_utc=day + timedelta(minutes=decision_minute),
        direction=Direction.LONG,
        earliest_executable_timestamp_utc=day + timedelta(minutes=executable_minute),
        requested_risk_fraction=requested_risk_fraction,
        stop_price=default_stop if stop_price is None else stop_price,
        target_price=default_target if target_price is None else target_price,
    )


def config(
    *,
    risk_config: RiskConfig | None = None,
    execution_timing_mode: str = NEXT_SUPPLIED_BAR,
) -> BacktestConfig:
    return BacktestConfig(
        starting_equity_usd=10_000.0,
        slippage_pips=0.0,
        risk_config=risk_config or RiskConfig(),
        commission_model=ZeroCommission(),
        financing_model=ZeroFinancing(),
        processed_data_manifest_id="phase2-manifest-sha",
        schema_version="fmp-canonical-1m-v1",
        timeframe="1m",
        requested_start_utc=DAY,
        requested_end_utc=DAY + timedelta(days=1),
        code_commit="engine-test-commit",
        decision_config={"fixture": "phase3-engine-tests"},
        execution_timing_mode=execution_timing_mode,
    )


class Phase3EngineTests(unittest.TestCase):
    def test_signal_cannot_fill_on_decision_bar_and_fills_next_bar(self) -> None:
        bars = [eurusd_bar(0), eurusd_bar(1), eurusd_bar(2)]
        decision = long_decision("D-1", decision_minute=0, executable_minute=1)
        run = run_backtest(bars=bars, decisions=[decision], config=config())
        self.assertEqual(len(run.trades), 1)
        self.assertEqual(run.trades[0].entry_timestamp_utc, DAY + timedelta(minutes=1))
        self.assertNotEqual(run.trades[0].entry_timestamp_utc, decision.decision_timestamp_utc)

    def test_declared_execution_later_than_first_next_bar_is_timing_rejection(self) -> None:
        bars = [eurusd_bar(0), eurusd_bar(1), eurusd_bar(2)]
        decision = long_decision("D-LATE", decision_minute=0, executable_minute=2)
        run = run_backtest(bars=bars, decisions=[decision], config=config())
        self.assertEqual(run.trades, ())
        self.assertEqual(len(run.rejections), 1)
        self.assertEqual(run.rejections[0].code, RejectionCode.TIMING_CONTRACT)


    def test_declared_earliest_mode_can_execute_after_intervening_1m_bars(self) -> None:
        bars = [eurusd_bar(0), eurusd_bar(1), eurusd_bar(2), eurusd_bar(3)]
        decision = long_decision("D-DECLARED", decision_minute=0, executable_minute=3)
        run = run_backtest(
            bars=bars,
            decisions=[decision],
            config=config(execution_timing_mode=DECLARED_EARLIEST_BAR),
        )
        self.assertEqual(len(run.trades), 1)
        self.assertEqual(
            run.trades[0].entry_timestamp_utc,
            DAY + timedelta(minutes=3),
        )
        self.assertEqual(
            run.run_identity["execution_timing_mode"],
            DECLARED_EARLIEST_BAR,
        )

    def test_declared_earliest_mode_rejects_missing_exact_execution_bar(self) -> None:
        bars = [eurusd_bar(0), eurusd_bar(1), eurusd_bar(3)]
        decision = long_decision("D-MISSING", decision_minute=0, executable_minute=2)
        run = run_backtest(
            bars=bars,
            decisions=[decision],
            config=config(execution_timing_mode=DECLARED_EARLIEST_BAR),
        )
        self.assertEqual(run.trades, ())
        self.assertEqual(len(run.rejections), 1)
        self.assertEqual(run.rejections[0].code, RejectionCode.TIMING_CONTRACT)

    def test_backtest_config_rejects_unknown_execution_timing_mode(self) -> None:
        with self.assertRaises(ValueError):
            config(execution_timing_mode="LOOKAHEAD")

    def test_no_trade_is_preserved_as_reasoned_record(self) -> None:
        decision = Decision(
            decision_id="NT-1",
            symbol="EURUSD",
            decision_timestamp_utc=DAY,
            direction=Direction.NO_TRADE,
            earliest_executable_timestamp_utc=None,
            requested_risk_fraction=None,
            stop_price=None,
            target_price=None,
            reason_code="FILTERED",
            reason_text="fixture says no trade",
        )
        run = run_backtest(bars=[eurusd_bar(0)], decisions=[decision], config=config())
        self.assertEqual(run.trades, ())
        self.assertEqual(run.rejections[0].code, RejectionCode.NO_TRADE)
        self.assertIn("fixture says no trade", run.rejections[0].explanation)

    def test_same_bar_after_entry_both_thresholds_resolve_to_stop(self) -> None:
        entry_bar = eurusd_bar(
            1,
            bid_high=1.1025,
            bid_low=1.0988,
            ask_high=1.1027,
            ask_low=1.0990,
        )
        decision = long_decision(
            "D-AMB",
            decision_minute=0,
            executable_minute=1,
            stop_price=1.0992,
            target_price=1.1020,
        )
        run = run_backtest(
            bars=[eurusd_bar(0), entry_bar],
            decisions=[decision],
            config=config(),
        )
        self.assertEqual(len(run.trades), 1)
        closed = run.trades[0]
        self.assertEqual(closed.entry_timestamp_utc, entry_bar.timestamp_utc)
        self.assertEqual(closed.exit_timestamp_utc, entry_bar.timestamp_utc)
        self.assertEqual(closed.exit_reason, ExitReason.STOP)
        self.assertTrue(closed.intrabar_ambiguous)

    def test_stable_decision_order_rejects_second_when_only_one_slot_remains(self) -> None:
        bars = [
            eurusd_bar(0),
            eurusd_bar(1),
            gbpusd_bar(1),
            usdjpy_bar(1),
            eurusd_bar(2),
            gbpusd_bar(2),
            usdjpy_bar(2),
        ]
        existing = long_decision(
            "EXISTING",
            decision_minute=0,
            executable_minute=1,
            requested_risk_fraction=0.005,
            target_price=1.1100,
        )
        decision_a = long_decision(
            "A",
            symbol="GBPUSD",
            decision_minute=1,
            executable_minute=2,
            requested_risk_fraction=0.005,
            stop_price=1.2992,
            target_price=1.3100,
        )
        decision_b = long_decision(
            "B",
            symbol="USDJPY",
            decision_minute=1,
            executable_minute=2,
            requested_risk_fraction=0.005,
            stop_price=149.90,
            target_price=151.0,
        )
        run = run_backtest(
            bars=bars,
            decisions=[decision_b, existing, decision_a],
            config=config(),
        )
        rejected = {item.decision_id: item.code for item in run.rejections}
        self.assertNotIn("A", rejected)
        self.assertEqual(rejected["B"], RejectionCode.SIMULTANEOUS_RISK)
        self.assertTrue(any(trade.decision_id == "A" for trade in run.trades))

    def test_exit_before_entry_releases_reserved_risk_at_same_timestamp(self) -> None:
        bars = [
            eurusd_bar(0),
            eurusd_bar(1),
            gbpusd_bar(1),
            eurusd_bar(2),
            gbpusd_bar(2, target_hit=True),
            usdjpy_bar(2),
        ]
        first = long_decision(
            "EUR-OPEN",
            decision_minute=0,
            executable_minute=1,
            requested_risk_fraction=0.005,
            target_price=1.1100,
        )
        second = long_decision(
            "GBP-CLOSE",
            symbol="GBPUSD",
            decision_minute=0,
            executable_minute=1,
            requested_risk_fraction=0.005,
            stop_price=1.2992,
            target_price=1.3020,
        )
        replacement = long_decision(
            "JPY-NEW",
            symbol="USDJPY",
            decision_minute=1,
            executable_minute=2,
            requested_risk_fraction=0.005,
            stop_price=149.90,
            target_price=151.0,
        )
        run = run_backtest(
            bars=bars,
            decisions=[first, second, replacement],
            config=config(),
        )
        rejected = {item.decision_id: item.code for item in run.rejections}
        self.assertNotIn("JPY-NEW", rejected)
        self.assertTrue(any(trade.decision_id == "JPY-NEW" for trade in run.trades))

    def test_daily_halt_blocks_later_same_day_entry_and_resets_next_utc_day(self) -> None:
        bars: list[QuoteBar] = [eurusd_bar(0)]
        decisions: list[Decision] = []
        for minute in range(1, 6):
            bars.append(
                eurusd_bar(
                    minute,
                    bid_open=1.1000,
                    bid_high=1.1005,
                    bid_low=1.0990,
                    bid_close=1.0995,
                    ask_open=1.1002,
                    ask_high=1.1007,
                    ask_low=1.0992,
                    ask_close=1.0997,
                )
            )
            decisions.append(
                long_decision(
                    f"LOSS-{minute}",
                    decision_minute=minute - 1,
                    executable_minute=minute,
                    requested_risk_fraction=0.005,
                    stop_price=1.0992,
                    target_price=1.1100,
                )
            )

        next_day = DAY + timedelta(days=1)
        bars.append(
            QuoteBar(
                timestamp_utc=next_day,
                symbol="EURUSD",
                bid_open=1.1000,
                bid_high=1.1005,
                bid_low=1.0995,
                bid_close=1.1002,
                ask_open=1.1002,
                ask_high=1.1007,
                ask_low=1.0997,
                ask_close=1.1004,
            )
        )
        decisions.append(
            Decision(
                decision_id="NEXT-DAY",
                symbol="EURUSD",
                decision_timestamp_utc=next_day - timedelta(minutes=1),
                direction=Direction.LONG,
                earliest_executable_timestamp_utc=next_day,
                requested_risk_fraction=0.0025,
                stop_price=1.0992,
                target_price=None,
            )
        )

        run = run_backtest(bars=bars, decisions=decisions, config=config())
        rejected = {item.decision_id: item.code for item in run.rejections}
        self.assertEqual(rejected["LOSS-5"], RejectionCode.DAILY_HALT)
        self.assertNotIn("NEXT-DAY", rejected)
        self.assertTrue(any(trade.decision_id == "NEXT-DAY" for trade in run.trades))

    def test_open_position_closes_at_end_of_data_on_bid_close(self) -> None:
        bars = [eurusd_bar(0), eurusd_bar(1), eurusd_bar(2, bid_close=1.1006, ask_close=1.1008)]
        decision = long_decision(
            "D-EOD",
            decision_minute=0,
            executable_minute=1,
            stop_price=1.0900,
            target_price=None,
        )
        run = run_backtest(bars=bars, decisions=[decision], config=config())
        self.assertEqual(len(run.trades), 1)
        closed = run.trades[0]
        self.assertEqual(closed.exit_reason, ExitReason.END_OF_DATA)
        self.assertEqual(closed.exit_timestamp_utc, DAY + timedelta(minutes=2))
        self.assertEqual(closed.exit_reference_price, 1.1006)

    def test_invalid_stop_geometry_is_preserved_as_rejection(self) -> None:
        decision = long_decision(
            "BAD-STOP",
            decision_minute=0,
            executable_minute=1,
            stop_price=1.1010,
        )
        run = run_backtest(
            bars=[eurusd_bar(0), eurusd_bar(1)],
            decisions=[decision],
            config=config(),
        )
        self.assertEqual(run.trades, ())
        self.assertEqual(run.rejections[0].code, RejectionCode.INVALID_STOP_TARGET)

    def test_scheduled_exit_precedes_same_bar_stop_target_evaluation(self) -> None:
        bars = [
            eurusd_bar(0),
            eurusd_bar(1, bid_low=1.0995, bid_high=1.1008),
            eurusd_bar(
                2,
                bid_open=1.1004,
                bid_high=1.1030,
                bid_low=1.0980,
                ask_open=1.1006,
                ask_high=1.1032,
                ask_low=1.0982,
            ),
        ]
        decision = long_decision(
            "TIME-FIRST",
            decision_minute=0,
            executable_minute=1,
            stop_price=1.0990,
            target_price=1.1020,
        )
        run = run_backtest(
            bars=bars,
            decisions=[decision],
            scheduled_exits=[ScheduledExit("TIME-FIRST", "EURUSD", DAY + timedelta(minutes=2))],
            config=config(),
        )
        self.assertEqual(len(run.trades), 1)
        self.assertEqual(run.trades[0].exit_reason, ExitReason.TIME_EXIT)
        self.assertEqual(run.trades[0].exit_reference_price, 1.1004)
        self.assertFalse(run.trades[0].intrabar_ambiguous)

    def test_scheduled_exit_releases_risk_before_same_timestamp_entry(self) -> None:
        bars = [
            eurusd_bar(0),
            eurusd_bar(1),
            gbpusd_bar(1),
            usdjpy_bar(1),
            # Make the timed EURUSD exit PnL-neutral at reference prices so this
            # fixture isolates reservation-release ordering rather than changing
            # the simultaneous-risk denominator via realized PnL.
            eurusd_bar(2, bid_open=1.1002, ask_open=1.1004),
            gbpusd_bar(2),
            usdjpy_bar(2),
        ]
        scheduled = long_decision(
            "EUR-TIME",
            decision_minute=0,
            executable_minute=1,
            requested_risk_fraction=0.005,
            stop_price=1.0900,
            target_price=1.1100,
        )
        persistent = long_decision(
            "GBP-HOLD",
            symbol="GBPUSD",
            decision_minute=0,
            executable_minute=1,
            requested_risk_fraction=0.005,
            stop_price=1.2900,
            target_price=1.3200,
        )
        replacement = long_decision(
            "JPY-NEW-TIME",
            symbol="USDJPY",
            decision_minute=1,
            executable_minute=2,
            requested_risk_fraction=0.005,
            stop_price=149.90,
            target_price=151.0,
        )
        run = run_backtest(
            bars=bars,
            decisions=[scheduled, persistent, replacement],
            scheduled_exits=[ScheduledExit("EUR-TIME", "EURUSD", DAY + timedelta(minutes=2))],
            config=config(),
        )
        rejected = {item.decision_id: item.code for item in run.rejections}
        self.assertNotIn("JPY-NEW-TIME", rejected)
        self.assertTrue(any(trade.decision_id == "JPY-NEW-TIME" for trade in run.trades))
        timed = next(trade for trade in run.trades if trade.decision_id == "EUR-TIME")
        self.assertEqual(timed.exit_reason, ExitReason.TIME_EXIT)
        self.assertAlmostEqual(timed.net_pnl_usd, 0.0)

    def test_scheduled_exit_is_noop_after_prior_target(self) -> None:
        bars = [
            eurusd_bar(0),
            eurusd_bar(1),
            eurusd_bar(2, bid_high=1.1030, ask_high=1.1032),
            eurusd_bar(3),
        ]
        decision = long_decision(
            "TARGET-FIRST",
            decision_minute=0,
            executable_minute=1,
            stop_price=1.0900,
            target_price=1.1020,
        )
        run = run_backtest(
            bars=bars,
            decisions=[decision],
            scheduled_exits=[ScheduledExit("TARGET-FIRST", "EURUSD", DAY + timedelta(minutes=3))],
            config=config(),
        )
        self.assertEqual(len(run.trades), 1)
        self.assertEqual(run.trades[0].exit_reason, ExitReason.TARGET)
        self.assertEqual(run.trades[0].exit_timestamp_utc, DAY + timedelta(minutes=2))


if __name__ == "__main__":
    unittest.main()
