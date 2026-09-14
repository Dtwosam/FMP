from __future__ import annotations

import unittest
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.session_breakout import (
    SessionBreakoutConfig,
    generate_session_breakout_candidates,
)


LONDON = ZoneInfo("Europe/London")


def local_label(session_date: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(session_date, time(hour, minute), tzinfo=LONDON).astimezone(timezone.utc)


def quote(
    timestamp_utc: datetime,
    *,
    symbol: str = "EURUSD",
    mid_open: float = 1.1000,
    mid_high: float | None = None,
    mid_low: float | None = None,
    mid_close: float | None = None,
) -> QuoteBar:
    spread_half = 0.0001 if symbol != "USDJPY" else 0.01
    default_range_half = 0.0005 if symbol != "USDJPY" else 0.05
    if mid_high is None:
        mid_high = mid_open + default_range_half
    if mid_low is None:
        mid_low = mid_open - default_range_half
    if mid_close is None:
        mid_close = mid_open
    return QuoteBar(
        timestamp_utc=timestamp_utc,
        symbol=symbol,
        bid_open=mid_open - spread_half,
        bid_high=mid_high - spread_half,
        bid_low=mid_low - spread_half,
        bid_close=mid_close - spread_half,
        ask_open=mid_open + spread_half,
        ask_high=mid_high + spread_half,
        ask_low=mid_low + spread_half,
        ask_close=mid_close + spread_half,
    )


def one_hour_session(
    session_date: date,
    *,
    symbol: str = "EURUSD",
    breakout_hour: int | None = 8,
    breakout_close: float | None = 1.1013,
    omit_local_hour: int | None = None,
    include_exit: bool = True,
) -> list[QuoteBar]:
    if symbol == "USDJPY":
        base = 150.00
        range_high = 150.10
        range_low = 149.90
        neutral_high = 150.05
        neutral_low = 149.95
    else:
        base = 1.1000
        range_high = 1.1010
        range_low = 1.0990
        neutral_high = 1.1005
        neutral_low = 1.0995

    bars: list[QuoteBar] = []
    for hour in range(0, 8):
        if omit_local_hour == hour:
            continue
        bars.append(
            quote(
                local_label(session_date, hour),
                symbol=symbol,
                mid_open=base,
                mid_high=range_high if hour == 2 else neutral_high,
                mid_low=range_low if hour == 3 else neutral_low,
                mid_close=base,
            )
        )
    for hour in range(8, 12):
        if omit_local_hour == hour:
            continue
        close = base
        if breakout_hour == hour and breakout_close is not None:
            close = breakout_close
        bars.append(
            quote(
                local_label(session_date, hour),
                symbol=symbol,
                mid_open=base,
                mid_high=max(neutral_high, close),
                mid_low=min(neutral_low, close),
                mid_close=close,
            )
        )
    if include_exit:
        bars.append(quote(local_label(session_date, 16), symbol=symbol, mid_open=base, mid_close=base))
    return sorted(bars, key=lambda bar: bar.timestamp_utc)


class Phase4SessionBreakoutTests(unittest.TestCase):
    def test_config_accepts_only_predeclared_grid(self) -> None:
        SessionBreakoutConfig(buffer_pips=2, target_range_multiple=1.0, timeframe="15m")
        with self.assertRaises(ValueError):
            SessionBreakoutConfig(buffer_pips=3, target_range_multiple=1.0, timeframe="15m")
        with self.assertRaises(ValueError):
            SessionBreakoutConfig(buffer_pips=2, target_range_multiple=2.0, timeframe="15m")
        with self.assertRaises(ValueError):
            SessionBreakoutConfig(buffer_pips=2, target_range_multiple=1.0, timeframe="1m")

    def test_winter_long_breakout_uses_midpoint_range_and_exact_local_exit(self) -> None:
        session_date = date(2020, 1, 2)
        candidates = generate_session_breakout_candidates(
            one_hour_session(session_date),
            config=SessionBreakoutConfig(buffer_pips=2, target_range_multiple=1.0, timeframe="1h"),
        )
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.direction, Direction.LONG)
        self.assertEqual(candidate.observation_bar_timestamp_utc, local_label(session_date, 8))
        self.assertEqual(candidate.signal_known_timestamp_utc, local_label(session_date, 9))
        self.assertEqual(candidate.latest_exit_timestamp_utc, local_label(session_date, 16))
        self.assertAlmostEqual(candidate.stop_price or 0.0, 1.0990)
        self.assertAlmostEqual(candidate.target_price or 0.0, 1.1033)
        self.assertAlmostEqual(float(candidate.metadata["range_width"]), 0.0020)

    def test_summer_london_dst_maps_windows_to_shifted_utc_labels(self) -> None:
        session_date = date(2020, 7, 2)
        candidate = generate_session_breakout_candidates(
            one_hour_session(session_date),
            config=SessionBreakoutConfig(buffer_pips=2, target_range_multiple=1.0, timeframe="1h"),
        )[0]
        self.assertEqual(local_label(session_date, 0), datetime(2020, 7, 1, 23, tzinfo=timezone.utc))
        self.assertEqual(candidate.observation_bar_timestamp_utc, datetime(2020, 7, 2, 7, tzinfo=timezone.utc))
        self.assertEqual(candidate.signal_known_timestamp_utc, datetime(2020, 7, 2, 8, tzinfo=timezone.utc))
        self.assertEqual(candidate.latest_exit_timestamp_utc, datetime(2020, 7, 2, 15, tzinfo=timezone.utc))

    def test_first_breakout_only_even_when_later_bar_crosses_other_direction(self) -> None:
        session_date = date(2020, 1, 2)
        bars = one_hour_session(session_date, breakout_hour=8, breakout_close=1.1013)
        reversal_timestamp = local_label(session_date, 9)
        reversal_close = 1.0985
        bars = [
            quote(
                bar.timestamp_utc,
                mid_open=(bar.bid_open + bar.ask_open) / 2,
                mid_high=max(
                    (bar.bid_high + bar.ask_high) / 2,
                    reversal_close if bar.timestamp_utc == reversal_timestamp else (bar.bid_close + bar.ask_close) / 2,
                ),
                mid_low=min(
                    (bar.bid_low + bar.ask_low) / 2,
                    reversal_close if bar.timestamp_utc == reversal_timestamp else (bar.bid_close + bar.ask_close) / 2,
                ),
                mid_close=reversal_close if bar.timestamp_utc == reversal_timestamp else (bar.bid_close + bar.ask_close) / 2,
            )
            for bar in bars
        ]
        candidate = generate_session_breakout_candidates(
            bars,
            config=SessionBreakoutConfig(buffer_pips=2, target_range_multiple=1.0, timeframe="1h"),
        )[0]
        self.assertEqual(candidate.direction, Direction.LONG)
        self.assertEqual(candidate.observation_bar_timestamp_utc, local_label(session_date, 8))

    def test_non_jpy_buffer_is_exact_and_larger_buffer_can_remove_signal(self) -> None:
        session_date = date(2020, 1, 2)
        bars = one_hour_session(session_date, breakout_close=1.1013)
        two_pip = generate_session_breakout_candidates(
            bars,
            config=SessionBreakoutConfig(buffer_pips=2, target_range_multiple=1.0, timeframe="1h"),
        )[0]
        five_pip = generate_session_breakout_candidates(
            bars,
            config=SessionBreakoutConfig(buffer_pips=5, target_range_multiple=1.0, timeframe="1h"),
        )[0]
        self.assertEqual(two_pip.direction, Direction.LONG)
        self.assertEqual(five_pip.direction, Direction.NO_TRADE)
        self.assertEqual(five_pip.reason_code, "NO_BREAKOUT")

    def test_jpy_pip_buffer_and_target_math_use_jpy_convention(self) -> None:
        session_date = date(2020, 1, 2)
        bars = one_hour_session(session_date, symbol="USDJPY", breakout_close=150.13)
        candidate = generate_session_breakout_candidates(
            bars,
            config=SessionBreakoutConfig(buffer_pips=2, target_range_multiple=1.0, timeframe="1h"),
        )[0]
        self.assertEqual(candidate.direction, Direction.LONG)
        self.assertAlmostEqual(candidate.stop_price or 0.0, 149.90)
        self.assertAlmostEqual(candidate.target_price or 0.0, 150.33)

    def test_target_multiple_is_anchored_to_closed_signal_midpoint(self) -> None:
        session_date = date(2020, 1, 2)
        bars = one_hour_session(session_date, breakout_close=1.1013)
        half = generate_session_breakout_candidates(
            bars,
            config=SessionBreakoutConfig(buffer_pips=2, target_range_multiple=0.5, timeframe="1h"),
        )[0]
        one_half = generate_session_breakout_candidates(
            bars,
            config=SessionBreakoutConfig(buffer_pips=2, target_range_multiple=1.5, timeframe="1h"),
        )[0]
        self.assertAlmostEqual(half.target_price or 0.0, 1.1023)
        self.assertAlmostEqual(one_half.target_price or 0.0, 1.1043)

    def test_missing_range_bar_fails_closed_as_incomplete_session(self) -> None:
        candidate = generate_session_breakout_candidates(
            one_hour_session(date(2020, 1, 2), omit_local_hour=3),
            config=SessionBreakoutConfig(buffer_pips=0, target_range_multiple=1.0, timeframe="1h"),
        )[0]
        self.assertEqual(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "INCOMPLETE_SESSION")

    def test_missing_pre_signal_breakout_bar_fails_closed(self) -> None:
        session_date = date(2020, 1, 2)
        bars = one_hour_session(session_date, breakout_hour=9, breakout_close=1.1013, omit_local_hour=8)
        candidate = generate_session_breakout_candidates(
            bars,
            config=SessionBreakoutConfig(buffer_pips=0, target_range_multiple=1.0, timeframe="1h"),
        )[0]
        self.assertEqual(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "INCOMPLETE_SESSION")

    def test_missing_exact_1600_exit_bar_fails_closed(self) -> None:
        candidate = generate_session_breakout_candidates(
            one_hour_session(date(2020, 1, 2), include_exit=False),
            config=SessionBreakoutConfig(buffer_pips=0, target_range_multiple=1.0, timeframe="1h"),
        )[0]
        self.assertEqual(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "INCOMPLETE_SESSION")

    def test_complete_session_without_breakout_records_no_trade(self) -> None:
        session_date = date(2020, 1, 2)
        candidate = generate_session_breakout_candidates(
            one_hour_session(session_date, breakout_hour=None, breakout_close=None),
            config=SessionBreakoutConfig(buffer_pips=0, target_range_multiple=1.0, timeframe="1h"),
        )[0]
        self.assertEqual(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "NO_BREAKOUT")
        self.assertEqual(candidate.observation_bar_timestamp_utc, local_label(session_date, 11))
        self.assertEqual(candidate.signal_known_timestamp_utc, local_label(session_date, 12))

    def test_candidate_generation_is_deterministic(self) -> None:
        bars = one_hour_session(date(2020, 1, 2))
        config = SessionBreakoutConfig(buffer_pips=2, target_range_multiple=1.0, timeframe="1h")
        first = generate_session_breakout_candidates(bars, config=config)
        second = generate_session_breakout_candidates(bars, config=config)
        self.assertEqual(first, second)
        self.assertEqual(first[0].stable_json_bytes(), second[0].stable_json_bytes())


if __name__ == "__main__":
    unittest.main()
