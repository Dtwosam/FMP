from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

from fmp.contracts import QuoteBar
from fmp.shadow import NormalizedQuote
from fmp.shadow.bars import LiveBarBuilder


UTC = timezone.utc
BASE = datetime(2026, 9, 15, 12, 0, tzinfo=UTC)


def quote(
    minute: int,
    second: int,
    *,
    bid: float,
    ask: float,
    tradeable: bool = True,
) -> NormalizedQuote:
    source = BASE + timedelta(minutes=minute, seconds=second)
    return NormalizedQuote(
        source_time_utc=source,
        received_at_utc=source + timedelta(milliseconds=10),
        receive_monotonic_ns=int((minute * 60 + second) * 1_000_000_000),
        symbol="USDJPY",
        bid=bid,
        ask=ask,
        tradeable=tradeable,
    )


class Phase8LiveBarTests(unittest.TestCase):
    def test_complete_15m_bar_is_left_labelled_and_keeps_bid_ask_ohlc_separate(self) -> None:
        builder = LiveBarBuilder()
        for minute in range(15):
            self.assertEqual(
                builder.on_quote(
                    quote(
                        minute,
                        5,
                        bid=140.00 + minute * 0.01,
                        ask=140.02 + minute * 0.01,
                    )
                ),
                (),
            )
            builder.on_quote(
                quote(
                    minute,
                    50,
                    bid=140.005 + minute * 0.01,
                    ask=140.025 + minute * 0.01,
                )
            )

        completed = builder.on_time_advance(BASE + timedelta(minutes=15))
        self.assertEqual(len(completed), 1)
        bar = completed[0]
        self.assertIsInstance(bar, QuoteBar)
        self.assertEqual(bar.timestamp_utc, BASE)
        self.assertEqual(bar.symbol, "USDJPY")
        self.assertAlmostEqual(bar.bid_open, 140.00)
        self.assertAlmostEqual(bar.bid_high, 140.145)
        self.assertAlmostEqual(bar.bid_low, 140.00)
        self.assertAlmostEqual(bar.bid_close, 140.145)
        self.assertAlmostEqual(bar.ask_open, 140.02)
        self.assertAlmostEqual(bar.ask_high, 140.165)
        self.assertAlmostEqual(bar.ask_low, 140.02)
        self.assertAlmostEqual(bar.ask_close, 140.165)

    def test_nontradeable_price_never_forms_required_minute(self) -> None:
        builder = LiveBarBuilder()
        for minute in range(15):
            builder.on_quote(
                quote(
                    minute,
                    10,
                    bid=140.0,
                    ask=140.02,
                    tradeable=minute != 7,
                )
            )
        self.assertEqual(builder.on_time_advance(BASE + timedelta(minutes=15)), ())

    def test_time_advance_can_close_buckets_but_never_creates_missing_price(self) -> None:
        builder = LiveBarBuilder()
        builder.on_quote(quote(0, 10, bid=140.0, ask=140.02))
        self.assertEqual(builder.on_time_advance(BASE + timedelta(minutes=1)), ())
        builder.on_time_advance(BASE + timedelta(minutes=2))
        for minute in range(2, 15):
            builder.on_quote(quote(minute, 10, bid=140.0, ask=140.02))
        self.assertEqual(builder.on_time_advance(BASE + timedelta(minutes=15)), ())

    def test_no_forward_fill_when_many_minutes_have_no_tradeable_quote(self) -> None:
        builder = LiveBarBuilder()
        builder.on_quote(quote(0, 1, bid=140.0, ask=140.02))
        builder.on_quote(quote(14, 59, bid=141.0, ask=141.02))
        self.assertEqual(builder.on_time_advance(BASE + timedelta(minutes=15)), ())

    def test_stale_interval_invalidates_every_intersected_minute_and_15m_bar(self) -> None:
        builder = LiveBarBuilder()
        for minute in range(15):
            builder.on_quote(quote(minute, 10, bid=140.0, ask=140.02))
        builder.mark_stale_interval(
            BASE + timedelta(minutes=6, seconds=30),
            BASE + timedelta(minutes=8, seconds=30),
        )
        self.assertEqual(builder.on_time_advance(BASE + timedelta(minutes=15)), ())

    def test_15m_bar_is_not_exposed_before_exact_interval_end(self) -> None:
        builder = LiveBarBuilder()
        for minute in range(15):
            builder.on_quote(quote(minute, 1, bid=140.0, ask=140.02))
        self.assertEqual(
            builder.on_time_advance(BASE + timedelta(minutes=14, seconds=59, milliseconds=999)),
            (),
        )
        completed = builder.on_time_advance(BASE + timedelta(minutes=15))
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].timestamp_utc, BASE)

    def test_quote_at_exact_boundary_closes_previous_15m_before_joining_next(self) -> None:
        builder = LiveBarBuilder()
        for minute in range(15):
            builder.on_quote(quote(minute, 1, bid=140.0, ask=140.02))
        completed = builder.on_quote(quote(15, 0, bid=141.0, ask=141.02))
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].timestamp_utc, BASE)

    def test_non_utc_or_regressing_time_operations_fail_closed(self) -> None:
        builder = LiveBarBuilder()
        builder.on_quote(quote(1, 0, bid=140.0, ask=140.02))
        with self.assertRaises(ValueError):
            builder.on_time_advance((BASE + timedelta(minutes=2)).replace(tzinfo=None))
        with self.assertRaises(ValueError):
            builder.on_time_advance(BASE)
        with self.assertRaises(ValueError):
            builder.mark_stale_interval(BASE + timedelta(minutes=2), BASE + timedelta(minutes=1))

    def test_live_bar_module_has_no_historical_backfill_or_candle_loader_hook(self) -> None:
        source = Path("src/fmp/shadow/bars.py").read_text(encoding="utf-8").lower()
        for forbidden in ("backfill", "historical candle", "load_candle", "load_history"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
