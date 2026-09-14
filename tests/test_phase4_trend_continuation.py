from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.trend_continuation import (
    TrendContinuationConfig,
    _trend_context,
    duration_to_bars,
)


BASE = datetime(2020, 1, 2, 0, 0, tzinfo=timezone.utc)


def quote(timestamp_utc: datetime, mid_close: float) -> QuoteBar:
    spread_half = 0.0001
    return QuoteBar(
        timestamp_utc=timestamp_utc,
        symbol="EURUSD",
        bid_open=mid_close - spread_half,
        bid_high=mid_close + 0.0004,
        bid_low=mid_close - 0.0006,
        bid_close=mid_close - spread_half,
        ask_open=mid_close + spread_half,
        ask_high=mid_close + 0.0006,
        ask_low=mid_close - 0.0004,
        ask_close=mid_close + spread_half,
    )


def hourly_bars(closes: list[float], *, skip_index: int | None = None) -> tuple[QuoteBar, ...]:
    out: list[QuoteBar] = []
    for index, close in enumerate(closes):
        offset = index
        if skip_index is not None and index >= skip_index:
            offset += 1
        out.append(quote(BASE + timedelta(hours=offset), close))
    return tuple(out)


class Phase4TrendContinuationContextTests(unittest.TestCase):
    def test_duration_to_bar_count_is_exact_for_all_signal_timeframes(self) -> None:
        self.assertEqual(duration_to_bars("5m", 2), 24)
        self.assertEqual(duration_to_bars("5m", 32), 384)
        self.assertEqual(duration_to_bars("15m", 8), 32)
        self.assertEqual(duration_to_bars("15m", 16), 64)
        self.assertEqual(duration_to_bars("1h", 2), 2)
        self.assertEqual(duration_to_bars("1h", 32), 32)

    def test_config_accepts_only_predeclared_grid(self) -> None:
        TrendContinuationConfig(trend_window_id="A", target_r_multiple=1.0, timeframe="5m")
        TrendContinuationConfig(trend_window_id="B", target_r_multiple=1.5, timeframe="15m")
        TrendContinuationConfig(trend_window_id="C", target_r_multiple=1.0, timeframe="1h")
        with self.assertRaises(ValueError):
            TrendContinuationConfig(trend_window_id="D", target_r_multiple=1.0, timeframe="15m")
        with self.assertRaises(ValueError):
            TrendContinuationConfig(trend_window_id="A", target_r_multiple=2.0, timeframe="15m")
        with self.assertRaises(ValueError):
            TrendContinuationConfig(trend_window_id="A", target_r_multiple=1.0, timeframe="1m")

    def test_long_context_requires_fast_above_slow_and_rising_slow(self) -> None:
        bars = hourly_bars([1.0000, 1.0000, 1.0000, 1.0020, 1.0030])
        context = _trend_context(
            bars,
            end_index=4,
            fast_count=2,
            slow_count=4,
            width=timedelta(hours=1),
        )
        self.assertEqual(context, Direction.LONG)

    def test_short_context_is_exact_inverse(self) -> None:
        bars = hourly_bars([1.0030, 1.0030, 1.0030, 1.0010, 1.0000])
        context = _trend_context(
            bars,
            end_index=4,
            fast_count=2,
            slow_count=4,
            width=timedelta(hours=1),
        )
        self.assertEqual(context, Direction.SHORT)

    def test_equal_averages_are_neutral(self) -> None:
        bars = hourly_bars([1.0000] * 5)
        context = _trend_context(
            bars,
            end_index=4,
            fast_count=2,
            slow_count=4,
            width=timedelta(hours=1),
        )
        self.assertIsNone(context)

    def test_missing_cadence_inside_required_context_is_ineligible(self) -> None:
        bars = hourly_bars([1.0000, 1.0000, 1.0000, 1.0020, 1.0030], skip_index=3)
        context = _trend_context(
            bars,
            end_index=4,
            fast_count=2,
            slow_count=4,
            width=timedelta(hours=1),
        )
        self.assertIsNone(context)


if __name__ == "__main__":
    unittest.main()
