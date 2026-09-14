from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from fmp.contracts import (
    Decision,
    Direction,
    ExitReason,
    OrderSide,
    QuoteBar,
    RejectionCode,
    validate_decisions,
    validate_quote_bars,
)


def quote_bar(
    *,
    timestamp: datetime | None = None,
    symbol: str = "EURUSD",
    bid_open: float = 1.1000,
    bid_high: float = 1.1010,
    bid_low: float = 1.0990,
    bid_close: float = 1.1005,
    ask_open: float = 1.1002,
    ask_high: float = 1.1012,
    ask_low: float = 1.0992,
    ask_close: float = 1.1007,
) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=timestamp or datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc),
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


class Phase3ContractTests(unittest.TestCase):
    def test_enum_values_are_stable(self) -> None:
        self.assertEqual(Direction.LONG.value, "LONG")
        self.assertEqual(Direction.SHORT.value, "SHORT")
        self.assertEqual(Direction.NO_TRADE.value, "NO_TRADE")
        self.assertEqual(OrderSide.BUY.value, "BUY")
        self.assertEqual(OrderSide.SELL.value, "SELL")
        self.assertEqual(ExitReason.STOP.value, "STOP")
        self.assertEqual(ExitReason.TARGET.value, "TARGET")
        self.assertEqual(ExitReason.END_OF_DATA.value, "END_OF_DATA")
        self.assertEqual(RejectionCode.TIMING_CONTRACT.value, "TIMING_CONTRACT")
        self.assertEqual(RejectionCode.NO_TRADE.value, "NO_TRADE")

    def test_quote_bar_accepts_supported_utc_quotes(self) -> None:
        row = quote_bar()
        self.assertEqual(row.symbol, "EURUSD")
        self.assertEqual(row.timestamp_utc.tzinfo, timezone.utc)

    def test_quote_bar_rejects_non_utc_timestamp(self) -> None:
        with self.assertRaisesRegex(ValueError, "UTC"):
            quote_bar(timestamp=datetime(2026, 9, 14, 0, 0))

    def test_quote_bar_rejects_non_zero_utc_offset(self) -> None:
        plus_one = timezone(timedelta(hours=1))
        with self.assertRaisesRegex(ValueError, "UTC"):
            quote_bar(timestamp=datetime(2026, 9, 14, 1, 0, tzinfo=plus_one))

    def test_quote_bar_rejects_unsupported_symbol(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported symbol"):
            quote_bar(symbol="AUDUSD")

    def test_quote_bar_rejects_non_positive_price(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            quote_bar(bid_low=0.0)

    def test_quote_bar_rejects_internal_ohlc_inconsistency(self) -> None:
        with self.assertRaisesRegex(ValueError, "OHLC"):
            quote_bar(bid_open=1.1020)

    def test_quote_bar_rejects_ask_below_bid(self) -> None:
        with self.assertRaisesRegex(ValueError, "ask.*bid"):
            quote_bar(ask_close=1.1000)

    def test_validate_quote_bars_requires_global_timestamp_symbol_order(self) -> None:
        first = quote_bar(
            timestamp=datetime(2026, 9, 14, 0, 1, tzinfo=timezone.utc),
            symbol="EURUSD",
        )
        second = quote_bar(
            timestamp=datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc),
            symbol="GBPUSD",
        )
        with self.assertRaisesRegex(ValueError, "sorted"):
            validate_quote_bars([first, second])

    def test_validate_quote_bars_rejects_duplicate_identity(self) -> None:
        row = quote_bar()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_quote_bars([row, row])

    def test_validate_quote_bars_allows_same_timestamp_for_different_symbols(self) -> None:
        ts = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
        rows = [
            quote_bar(timestamp=ts, symbol="EURUSD"),
            quote_bar(timestamp=ts, symbol="GBPUSD"),
            quote_bar(
                timestamp=ts,
                symbol="USDJPY",
                bid_open=150.00,
                bid_high=150.10,
                bid_low=149.90,
                bid_close=150.05,
                ask_open=150.02,
                ask_high=150.12,
                ask_low=149.92,
                ask_close=150.07,
            ),
        ]
        validate_quote_bars(rows)

    def test_directional_decision_requires_next_timestamp_after_decision(self) -> None:
        decision_ts = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError, "earliest executable"):
            Decision(
                decision_id="D-001",
                symbol="EURUSD",
                decision_timestamp_utc=decision_ts,
                direction=Direction.LONG,
                earliest_executable_timestamp_utc=decision_ts,
                requested_risk_fraction=0.0025,
                stop_price=1.0990,
                target_price=1.1020,
            )

    def test_directional_decision_requires_stop(self) -> None:
        decision_ts = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError, "stop"):
            Decision(
                decision_id="D-001",
                symbol="EURUSD",
                decision_timestamp_utc=decision_ts,
                direction=Direction.LONG,
                earliest_executable_timestamp_utc=decision_ts + timedelta(minutes=1),
                requested_risk_fraction=0.0025,
                stop_price=None,
                target_price=1.1020,
            )

    def test_no_trade_decision_allows_no_execution_fields(self) -> None:
        decision = Decision(
            decision_id="NT-001",
            symbol="EURUSD",
            decision_timestamp_utc=datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc),
            direction=Direction.NO_TRADE,
            earliest_executable_timestamp_utc=None,
            requested_risk_fraction=None,
            stop_price=None,
            target_price=None,
            reason_code="FILTERED",
            reason_text="fixture says no trade",
        )
        self.assertEqual(decision.direction, Direction.NO_TRADE)

    def test_decision_id_must_be_non_empty(self) -> None:
        with self.assertRaisesRegex(ValueError, "decision_id"):
            Decision(
                decision_id="",
                symbol="EURUSD",
                decision_timestamp_utc=datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc),
                direction=Direction.NO_TRADE,
                earliest_executable_timestamp_utc=None,
                requested_risk_fraction=None,
                stop_price=None,
                target_price=None,
            )

    def test_validate_decisions_rejects_duplicate_ids(self) -> None:
        decision = Decision(
            decision_id="NT-001",
            symbol="EURUSD",
            decision_timestamp_utc=datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc),
            direction=Direction.NO_TRADE,
            earliest_executable_timestamp_utc=None,
            requested_risk_fraction=None,
            stop_price=None,
            target_price=None,
        )
        with self.assertRaisesRegex(ValueError, "duplicate decision_id"):
            validate_decisions([decision, decision])


if __name__ == "__main__":
    unittest.main()
