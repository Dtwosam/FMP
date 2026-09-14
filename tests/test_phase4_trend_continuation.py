from __future__ import annotations

import unittest
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.trend_continuation import (
    TrendContinuationConfig,
    _trend_context,
    duration_to_bars,
    generate_trend_continuation_candidates,
)


BASE = datetime(2020, 1, 2, 0, 0, tzinfo=timezone.utc)
LONDON = ZoneInfo("Europe/London")


def local_label(session_date: date, hour: int) -> datetime:
    return datetime.combine(session_date, time(hour, 0), tzinfo=LONDON).astimezone(timezone.utc)


def quote(
    timestamp_utc: datetime,
    mid_close: float,
    *,
    mid_high: float | None = None,
    mid_low: float | None = None,
) -> QuoteBar:
    spread_half = 0.0001
    high = mid_close + 0.0005 if mid_high is None else max(mid_high, mid_close)
    low = mid_close - 0.0005 if mid_low is None else min(mid_low, mid_close)
    return QuoteBar(
        timestamp_utc=timestamp_utc,
        symbol="EURUSD",
        bid_open=mid_close - spread_half,
        bid_high=high - spread_half,
        bid_low=low - spread_half,
        bid_close=mid_close - spread_half,
        ask_open=mid_close + spread_half,
        ask_high=high + spread_half,
        ask_low=low + spread_half,
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


def trend_session(
    session_date: date,
    *,
    direction: str = "long",
    target_r_multiple: float = 1.0,
    include_exit: bool = True,
    omit_hour: int | None = None,
    flatten_from_eight: bool = False,
    touch_only: bool = False,
) -> tuple[QuoteBar, ...]:
    if direction == "long":
        closes = {
            0: 1.1000,
            1: 1.1005,
            2: 1.1010,
            3: 1.1015,
            4: 1.1020,
            5: 1.1025,
            6: 1.1030,
            7: 1.1020,
            8: 1.1040,
        }
        default_after = 1.1040
    else:
        closes = {
            0: 1.1040,
            1: 1.1035,
            2: 1.1030,
            3: 1.1025,
            4: 1.1020,
            5: 1.1015,
            6: 1.1010,
            7: 1.1020,
            8: 1.1000,
        }
        default_after = 1.1000

    bars: list[QuoteBar] = []
    for hour in range(17):
        if hour == omit_hour or (hour == 16 and not include_exit):
            continue
        close = closes.get(hour, default_after)
        high = None
        low = None
        if direction == "long":
            if hour == 6:
                low = 1.1025
            elif hour == 7:
                low = 1.1010
            elif hour == 8:
                low = 1.1030
        else:
            if hour == 6:
                high = 1.1015
            elif hour == 7:
                high = 1.1030
            elif hour == 8:
                high = 1.1005

        if flatten_from_eight and hour >= 8:
            close = 1.1020
        if touch_only and hour == 8:
            close = 1.1020
            high = 1.1040

        bars.append(quote(local_label(session_date, hour), close, mid_high=high, mid_low=low))
    return tuple(sorted(bars, key=lambda item: item.timestamp_utc))


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
        context = _trend_context(bars, end_index=4, fast_count=2, slow_count=4, width=timedelta(hours=1))
        self.assertEqual(context, Direction.LONG)

    def test_short_context_is_exact_inverse(self) -> None:
        bars = hourly_bars([1.0030, 1.0030, 1.0030, 1.0010, 1.0000])
        context = _trend_context(bars, end_index=4, fast_count=2, slow_count=4, width=timedelta(hours=1))
        self.assertEqual(context, Direction.SHORT)

    def test_equal_averages_are_neutral(self) -> None:
        bars = hourly_bars([1.0000] * 5)
        self.assertIsNone(_trend_context(bars, end_index=4, fast_count=2, slow_count=4, width=timedelta(hours=1)))

    def test_missing_cadence_inside_required_context_is_ineligible(self) -> None:
        bars = hourly_bars([1.0000, 1.0000, 1.0000, 1.0020, 1.0030], skip_index=3)
        self.assertIsNone(_trend_context(bars, end_index=4, fast_count=2, slow_count=4, width=timedelta(hours=1)))


class Phase4TrendContinuationSignalTests(unittest.TestCase):
    def config(self, target: float = 1.0) -> TrendContinuationConfig:
        return TrendContinuationConfig(trend_window_id="A", target_r_multiple=target, timeframe="1h")

    def test_long_resumption_freezes_three_bar_stop_target_and_exit(self) -> None:
        session_date = date(2020, 1, 2)
        candidate = generate_trend_continuation_candidates(trend_session(session_date), config=self.config())[0]
        self.assertEqual(candidate.direction, Direction.LONG)
        self.assertEqual(candidate.reason_code, "CONTINUATION_LONG")
        self.assertEqual(candidate.observation_bar_timestamp_utc, local_label(session_date, 8))
        self.assertEqual(candidate.signal_known_timestamp_utc, local_label(session_date, 9))
        self.assertEqual(candidate.latest_exit_timestamp_utc, local_label(session_date, 16))
        self.assertAlmostEqual(candidate.stop_price or 0.0, 1.1010)
        self.assertAlmostEqual(candidate.target_price or 0.0, 1.1070)

    def test_short_resumption_is_symmetric(self) -> None:
        candidate = generate_trend_continuation_candidates(
            trend_session(date(2020, 1, 2), direction="short"),
            config=self.config(),
        )[0]
        self.assertEqual(candidate.direction, Direction.SHORT)
        self.assertEqual(candidate.reason_code, "CONTINUATION_SHORT")
        self.assertAlmostEqual(candidate.stop_price or 0.0, 1.1030)
        self.assertAlmostEqual(candidate.target_price or 0.0, 1.0970)

    def test_one_and_one_half_r_target_is_anchored_to_signal_midpoint(self) -> None:
        candidate = generate_trend_continuation_candidates(
            trend_session(date(2020, 1, 2)),
            config=self.config(1.5),
        )[0]
        self.assertAlmostEqual(candidate.target_price or 0.0, 1.1085)

    def test_intrabar_touch_without_close_cross_does_not_trigger(self) -> None:
        candidate = generate_trend_continuation_candidates(
            trend_session(date(2020, 1, 2), flatten_from_eight=True, touch_only=True),
            config=self.config(),
        )[0]
        self.assertEqual(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "NO_CONTINUATION")

    def test_only_first_qualifying_signal_is_emitted_per_session(self) -> None:
        candidates = generate_trend_continuation_candidates(trend_session(date(2020, 1, 2)), config=self.config())
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].observation_bar_timestamp_utc, local_label(date(2020, 1, 2), 8))

    def test_complete_session_without_pullback_resumption_records_no_trade(self) -> None:
        session_date = date(2020, 1, 2)
        bars = tuple(
            quote(local_label(session_date, hour), 1.1000 + hour * 0.0005)
            for hour in range(17)
        )
        candidate = generate_trend_continuation_candidates(bars, config=self.config())[0]
        self.assertEqual(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "NO_CONTINUATION")
        self.assertEqual(candidate.observation_bar_timestamp_utc, local_label(session_date, 14))
        self.assertEqual(candidate.signal_known_timestamp_utc, local_label(session_date, 15))

    def test_missing_three_bar_or_sma_context_never_shortens_history(self) -> None:
        candidate = generate_trend_continuation_candidates(
            trend_session(date(2020, 1, 2), omit_hour=7),
            config=self.config(),
        )[0]
        self.assertEqual(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "NO_CONTINUATION")

    def test_missing_exact_1600_exit_fails_closed(self) -> None:
        candidate = generate_trend_continuation_candidates(
            trend_session(date(2020, 1, 2), include_exit=False),
            config=self.config(),
        )[0]
        self.assertEqual(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "INCOMPLETE_SESSION")

    def test_summer_london_dst_maps_signal_known_and_exit_to_utc(self) -> None:
        session_date = date(2020, 7, 2)
        candidate = generate_trend_continuation_candidates(trend_session(session_date), config=self.config())[0]
        self.assertEqual(candidate.observation_bar_timestamp_utc, datetime(2020, 7, 2, 7, tzinfo=timezone.utc))
        self.assertEqual(candidate.signal_known_timestamp_utc, datetime(2020, 7, 2, 8, tzinfo=timezone.utc))
        self.assertEqual(candidate.latest_exit_timestamp_utc, datetime(2020, 7, 2, 15, tzinfo=timezone.utc))

    def test_candidate_generation_is_byte_deterministic(self) -> None:
        bars = trend_session(date(2020, 1, 2))
        first = generate_trend_continuation_candidates(bars, config=self.config())
        second = generate_trend_continuation_candidates(bars, config=self.config())
        self.assertEqual(first, second)
        self.assertEqual(first[0].stable_json_bytes(), second[0].stable_json_bytes())


if __name__ == "__main__":
    unittest.main()
