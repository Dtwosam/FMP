from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from fmp.backtest.costs import FixedCommissionPerMillion, ZeroCommission, ZeroFinancing
from fmp.backtest.execution import (
    close_end_of_data,
    entry_reference_price,
    evaluate_exit,
    fill_entry,
)
from fmp.contracts import Direction, ExitReason, OrderIntent, QuoteBar


BASE_TS = datetime(2026, 9, 14, 0, 1, tzinfo=timezone.utc)


def bar(
    *,
    timestamp: datetime = BASE_TS,
    symbol: str = "EURUSD",
    bid_open: float = 1.1000,
    bid_high: float = 1.1010,
    bid_low: float = 1.0995,
    bid_close: float = 1.1005,
    ask_open: float = 1.1002,
    ask_high: float = 1.1012,
    ask_low: float = 1.0997,
    ask_close: float = 1.1007,
) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=timestamp,
        symbol=symbol,
        bid_open=bid_open,
        bid_high=bid_high,
        bid_low=bid_low,
        bid_close=bid_close,
        ask_open=ask_open,
        ask_high=ask_high,
        ask_low=ask_low,
        ask_close=ask_close,
    )


def intent(
    *,
    decision_id: str = "D-001",
    direction: Direction = Direction.LONG,
    units: int = 100_000,
    stop_price: float = 1.0990,
    target_price: float | None = 1.1020,
) -> OrderIntent:
    return OrderIntent(
        decision_id=decision_id,
        symbol="EURUSD",
        direction=direction,
        units=units,
        reserved_risk_usd=100.0,
        stop_price=stop_price,
        target_price=target_price,
        decision_timestamp_utc=BASE_TS - timedelta(minutes=1),
        earliest_executable_timestamp_utc=BASE_TS,
    )


class Phase3ExecutionTests(unittest.TestCase):
    def test_long_entry_reference_is_ask_open_and_buy_slippage_is_adverse(self) -> None:
        quote = bar()
        self.assertEqual(entry_reference_price(quote, Direction.LONG), 1.1002)
        position = fill_entry(
            intent(),
            quote,
            slippage_pips=1.0,
            commission_model=ZeroCommission(),
        )
        self.assertEqual(position.entry_reference_price, 1.1002)
        self.assertAlmostEqual(position.entry_price, 1.1003)
        self.assertEqual(position.entry_commission_usd, 0.0)
        self.assertEqual(position.position_id, "D-001")

    def test_short_entry_reference_is_bid_open_and_sell_slippage_is_adverse(self) -> None:
        quote = bar()
        short = intent(direction=Direction.SHORT, stop_price=1.1015, target_price=1.0985)
        self.assertEqual(entry_reference_price(quote, Direction.SHORT), 1.1000)
        position = fill_entry(
            short,
            quote,
            slippage_pips=1.0,
            commission_model=ZeroCommission(),
        )
        self.assertAlmostEqual(position.entry_price, 1.0999)

    def test_entry_commission_is_recorded_per_execution_side(self) -> None:
        position = fill_entry(
            intent(),
            bar(),
            slippage_pips=0.0,
            commission_model=FixedCommissionPerMillion(30.0),
        )
        self.assertAlmostEqual(position.entry_commission_usd, 3.0)

    def test_long_stop_uses_bid_and_sell_slippage(self) -> None:
        position = fill_entry(intent(), bar(), slippage_pips=0.0, commission_model=ZeroCommission())
        exit_fill = evaluate_exit(
            position,
            bar(
                timestamp=BASE_TS + timedelta(minutes=1),
                bid_open=1.1000,
                bid_high=1.1005,
                bid_low=1.0988,
                bid_close=1.0994,
                ask_open=1.1002,
                ask_high=1.1007,
                ask_low=1.0990,
                ask_close=1.0996,
            ),
            slippage_pips=1.0,
            commission_model=ZeroCommission(),
            financing_model=ZeroFinancing(),
        )
        self.assertIsNotNone(exit_fill)
        assert exit_fill is not None
        self.assertEqual(exit_fill.reason, ExitReason.STOP)
        self.assertEqual(exit_fill.reference_price, 1.0990)
        self.assertAlmostEqual(exit_fill.execution_price, 1.0989)
        self.assertFalse(exit_fill.intrabar_ambiguous)

    def test_short_stop_uses_ask_and_buy_slippage(self) -> None:
        position = fill_entry(
            intent(direction=Direction.SHORT, stop_price=1.1010, target_price=1.0980),
            bar(),
            slippage_pips=0.0,
            commission_model=ZeroCommission(),
        )
        exit_fill = evaluate_exit(
            position,
            bar(
                timestamp=BASE_TS + timedelta(minutes=1),
                bid_open=1.1000,
                bid_high=1.1009,
                bid_low=1.0995,
                bid_close=1.1004,
                ask_open=1.1002,
                ask_high=1.1011,
                ask_low=1.0997,
                ask_close=1.1006,
            ),
            slippage_pips=1.0,
            commission_model=ZeroCommission(),
            financing_model=ZeroFinancing(),
        )
        self.assertIsNotNone(exit_fill)
        assert exit_fill is not None
        self.assertEqual(exit_fill.reason, ExitReason.STOP)
        self.assertEqual(exit_fill.reference_price, 1.1010)
        self.assertAlmostEqual(exit_fill.execution_price, 1.1011)

    def test_long_target_uses_bid_and_declared_target(self) -> None:
        position = fill_entry(intent(), bar(), slippage_pips=0.0, commission_model=ZeroCommission())
        exit_fill = evaluate_exit(
            position,
            bar(
                timestamp=BASE_TS + timedelta(minutes=1),
                bid_open=1.1005,
                bid_high=1.1024,
                bid_low=1.1000,
                bid_close=1.1021,
                ask_open=1.1007,
                ask_high=1.1026,
                ask_low=1.1002,
                ask_close=1.1023,
            ),
            slippage_pips=1.0,
            commission_model=ZeroCommission(),
            financing_model=ZeroFinancing(),
        )
        assert exit_fill is not None
        self.assertEqual(exit_fill.reason, ExitReason.TARGET)
        self.assertEqual(exit_fill.reference_price, 1.1020)
        self.assertAlmostEqual(exit_fill.execution_price, 1.1019)

    def test_short_target_uses_ask_and_declared_target(self) -> None:
        position = fill_entry(
            intent(direction=Direction.SHORT, stop_price=1.1020, target_price=1.0980),
            bar(),
            slippage_pips=0.0,
            commission_model=ZeroCommission(),
        )
        exit_fill = evaluate_exit(
            position,
            bar(
                timestamp=BASE_TS + timedelta(minutes=1),
                bid_open=1.0990,
                bid_high=1.0995,
                bid_low=1.0975,
                bid_close=1.0982,
                ask_open=1.0992,
                ask_high=1.0997,
                ask_low=1.0977,
                ask_close=1.0984,
            ),
            slippage_pips=1.0,
            commission_model=ZeroCommission(),
            financing_model=ZeroFinancing(),
        )
        assert exit_fill is not None
        self.assertEqual(exit_fill.reason, ExitReason.TARGET)
        self.assertEqual(exit_fill.reference_price, 1.0980)
        self.assertAlmostEqual(exit_fill.execution_price, 1.0981)

    def test_both_stop_and_target_reachable_resolves_to_stop(self) -> None:
        position = fill_entry(intent(), bar(), slippage_pips=0.0, commission_model=ZeroCommission())
        exit_fill = evaluate_exit(
            position,
            bar(
                timestamp=BASE_TS + timedelta(minutes=1),
                bid_open=1.1005,
                bid_high=1.1025,
                bid_low=1.0985,
                bid_close=1.1000,
                ask_open=1.1007,
                ask_high=1.1027,
                ask_low=1.0987,
                ask_close=1.1002,
            ),
            slippage_pips=0.0,
            commission_model=ZeroCommission(),
            financing_model=ZeroFinancing(),
        )
        assert exit_fill is not None
        self.assertEqual(exit_fill.reason, ExitReason.STOP)
        self.assertEqual(exit_fill.reference_price, 1.0990)
        self.assertTrue(exit_fill.intrabar_ambiguous)

    def test_long_gap_through_stop_uses_worse_bid_open(self) -> None:
        position = fill_entry(intent(), bar(), slippage_pips=0.0, commission_model=ZeroCommission())
        exit_fill = evaluate_exit(
            position,
            bar(
                timestamp=BASE_TS + timedelta(minutes=1),
                bid_open=1.0985,
                bid_high=1.0995,
                bid_low=1.0980,
                bid_close=1.0990,
                ask_open=1.0987,
                ask_high=1.0997,
                ask_low=1.0982,
                ask_close=1.0992,
            ),
            slippage_pips=0.0,
            commission_model=ZeroCommission(),
            financing_model=ZeroFinancing(),
        )
        assert exit_fill is not None
        self.assertEqual(exit_fill.reason, ExitReason.STOP)
        self.assertEqual(exit_fill.reference_price, 1.0985)

    def test_short_gap_through_stop_uses_worse_ask_open(self) -> None:
        position = fill_entry(
            intent(direction=Direction.SHORT, stop_price=1.1010, target_price=1.0980),
            bar(),
            slippage_pips=0.0,
            commission_model=ZeroCommission(),
        )
        exit_fill = evaluate_exit(
            position,
            bar(
                timestamp=BASE_TS + timedelta(minutes=1),
                bid_open=1.1013,
                bid_high=1.1018,
                bid_low=1.1008,
                bid_close=1.1010,
                ask_open=1.1015,
                ask_high=1.1020,
                ask_low=1.1010,
                ask_close=1.1012,
            ),
            slippage_pips=0.0,
            commission_model=ZeroCommission(),
            financing_model=ZeroFinancing(),
        )
        assert exit_fill is not None
        self.assertEqual(exit_fill.reason, ExitReason.STOP)
        self.assertEqual(exit_fill.reference_price, 1.1015)

    def test_favorable_target_gap_does_not_receive_price_improvement(self) -> None:
        position = fill_entry(intent(), bar(), slippage_pips=0.0, commission_model=ZeroCommission())
        exit_fill = evaluate_exit(
            position,
            bar(
                timestamp=BASE_TS + timedelta(minutes=1),
                bid_open=1.1030,
                bid_high=1.1035,
                bid_low=1.1025,
                bid_close=1.1032,
                ask_open=1.1032,
                ask_high=1.1037,
                ask_low=1.1027,
                ask_close=1.1034,
            ),
            slippage_pips=0.0,
            commission_model=ZeroCommission(),
            financing_model=ZeroFinancing(),
        )
        assert exit_fill is not None
        self.assertEqual(exit_fill.reason, ExitReason.TARGET)
        self.assertEqual(exit_fill.reference_price, 1.1020)
        self.assertEqual(exit_fill.execution_price, 1.1020)

    def test_no_threshold_reached_returns_none(self) -> None:
        position = fill_entry(intent(), bar(), slippage_pips=0.0, commission_model=ZeroCommission())
        exit_fill = evaluate_exit(
            position,
            bar(timestamp=BASE_TS + timedelta(minutes=1)),
            slippage_pips=0.0,
            commission_model=ZeroCommission(),
            financing_model=ZeroFinancing(),
        )
        self.assertIsNone(exit_fill)

    def test_end_of_data_long_uses_bid_close(self) -> None:
        position = fill_entry(intent(), bar(), slippage_pips=0.0, commission_model=ZeroCommission())
        exit_fill = close_end_of_data(
            position,
            bar(timestamp=BASE_TS + timedelta(minutes=5)),
            slippage_pips=1.0,
            commission_model=FixedCommissionPerMillion(30.0),
            financing_model=ZeroFinancing(),
        )
        self.assertEqual(exit_fill.reason, ExitReason.END_OF_DATA)
        self.assertEqual(exit_fill.reference_price, 1.1005)
        self.assertAlmostEqual(exit_fill.execution_price, 1.1004)
        self.assertAlmostEqual(exit_fill.exit_commission_usd, 3.0)
        self.assertEqual(exit_fill.financing_cost_usd, 0.0)

    def test_end_of_data_short_uses_ask_close(self) -> None:
        position = fill_entry(
            intent(direction=Direction.SHORT, stop_price=1.1020, target_price=1.0980),
            bar(),
            slippage_pips=0.0,
            commission_model=ZeroCommission(),
        )
        exit_fill = close_end_of_data(
            position,
            bar(timestamp=BASE_TS + timedelta(minutes=5)),
            slippage_pips=1.0,
            commission_model=ZeroCommission(),
            financing_model=ZeroFinancing(),
        )
        self.assertEqual(exit_fill.reference_price, 1.1007)
        self.assertAlmostEqual(exit_fill.execution_price, 1.1008)


if __name__ == "__main__":
    unittest.main()
