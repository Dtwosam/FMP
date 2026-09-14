from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import unittest
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.previous_day_rejection import (
    PreviousDayRejectionConfig,
    generate_previous_day_rejection_candidates,
    previous_completed_ny_session_bounds,
)


LONDON = ZoneInfo("Europe/London")
NEW_YORK = ZoneInfo("America/New_York")


def _local_utc(day: date, hour: int, *, zone: ZoneInfo, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute), tzinfo=zone).astimezone(timezone.utc)


def _bar(
    ts: datetime,
    *,
    close: float,
    high: float | None = None,
    low: float | None = None,
    symbol: str = "EURUSD",
) -> QuoteBar:
    spread = 0.0002 if symbol != "USDJPY" else 0.02
    high = close if high is None else high
    low = close if low is None else low
    return QuoteBar(
        timestamp_utc=ts,
        symbol=symbol,
        bid_open=close - spread / 2,
        bid_high=high - spread / 2,
        bid_low=low - spread / 2,
        bid_close=close - spread / 2,
        ask_open=close + spread / 2,
        ask_high=high + spread / 2,
        ask_low=low + spread / 2,
        ask_close=close + spread / 2,
    )


def _reference_bars(
    london_day: date,
    *,
    timeframe_minutes: int = 60,
    symbol: str = "EURUSD",
    high: float = 1.1100,
    low: float = 1.0900,
) -> list[QuoteBar]:
    start, end = previous_completed_ny_session_bounds(london_day)
    bars: list[QuoteBar] = []
    current = start
    index = 0
    while current < end:
        close = 1.1000
        bar_high = high if index == 3 else close
        bar_low = low if index == 7 else close
        bars.append(_bar(current, close=close, high=bar_high, low=bar_low, symbol=symbol))
        current += timedelta(minutes=timeframe_minutes)
        index += 1
    return bars


def _signal_session_bars(
    london_day: date,
    *,
    signal_direction: Direction | None,
    buffer_pips: int = 0,
    symbol: str = "EURUSD",
) -> list[QuoteBar]:
    pip = 0.0001 if symbol != "USDJPY" else 0.01
    bars: list[QuoteBar] = []
    previous_label = _local_utc(london_day, 7, zone=LONDON)
    bars.append(_bar(previous_label, close=1.1000, symbol=symbol))
    for hour in range(8, 17):
        ts = _local_utc(london_day, hour, zone=LONDON)
        if hour == 8 and signal_direction is Direction.SHORT:
            bars.append(
                _bar(
                    ts,
                    close=1.1090,
                    high=1.1100 + buffer_pips * pip,
                    low=1.1080,
                    symbol=symbol,
                )
            )
        elif hour == 8 and signal_direction is Direction.LONG:
            bars.append(
                _bar(
                    ts,
                    close=1.0910,
                    high=1.0920,
                    low=1.0900 - buffer_pips * pip,
                    symbol=symbol,
                )
            )
        else:
            bars.append(_bar(ts, close=1.1000, symbol=symbol))
    return bars


class PreviousDayRejectionTests(unittest.TestCase):
    def test_config_accepts_only_frozen_buffers_and_timeframes(self) -> None:
        for buffer_pips in (0, 2, 5):
            for timeframe in ("5m", "15m", "1h"):
                config = PreviousDayRejectionConfig(buffer_pips=buffer_pips, timeframe=timeframe)
                self.assertEqual((config.buffer_pips, config.timeframe), (buffer_pips, timeframe))
        with self.assertRaises(ValueError):
            PreviousDayRejectionConfig(buffer_pips=1, timeframe="1h")
        with self.assertRaises(ValueError):
            PreviousDayRejectionConfig(buffer_pips=0, timeframe="1m")

    def test_monday_london_references_completed_friday_new_york_session(self) -> None:
        london_day = date(2021, 3, 15)
        start, end = previous_completed_ny_session_bounds(london_day)
        self.assertEqual(end.astimezone(NEW_YORK).date(), date(2021, 3, 12))
        self.assertEqual(end.astimezone(NEW_YORK).hour, 17)
        self.assertEqual(start.astimezone(NEW_YORK).date(), date(2021, 3, 11))
        self.assertEqual(start.astimezone(NEW_YORK).hour, 17)

    def test_short_rejection_uses_previous_day_high_signal_wick_and_close_back_inside(self) -> None:
        day = date(2021, 3, 16)
        config = PreviousDayRejectionConfig(buffer_pips=2, timeframe="1h")
        bars = _reference_bars(day) + _signal_session_bars(
            day, signal_direction=Direction.SHORT, buffer_pips=2
        )
        candidate = generate_previous_day_rejection_candidates(bars, config=config)[0]
        self.assertIs(candidate.direction, Direction.SHORT)
        self.assertEqual(candidate.reason_code, "PREVIOUS_DAY_REJECTION_SHORT")
        self.assertEqual(candidate.observation_bar_timestamp_utc, _local_utc(day, 8, zone=LONDON))
        self.assertEqual(candidate.signal_known_timestamp_utc, _local_utc(day, 9, zone=LONDON))
        self.assertEqual(candidate.latest_exit_timestamp_utc, _local_utc(day, 16, zone=LONDON))
        self.assertAlmostEqual(candidate.stop_price, 1.1102)
        self.assertAlmostEqual(candidate.target_price, 1.1000)
        self.assertAlmostEqual(candidate.metadata["previous_day_high"], 1.1100)
        self.assertAlmostEqual(candidate.metadata["previous_day_low"], 1.0900)
        self.assertAlmostEqual(candidate.metadata["previous_day_midpoint"], 1.1000)

    def test_long_rejection_is_symmetric(self) -> None:
        day = date(2021, 3, 17)
        config = PreviousDayRejectionConfig(buffer_pips=5, timeframe="1h")
        bars = _reference_bars(day) + _signal_session_bars(
            day, signal_direction=Direction.LONG, buffer_pips=5
        )
        candidate = generate_previous_day_rejection_candidates(bars, config=config)[0]
        self.assertIs(candidate.direction, Direction.LONG)
        self.assertAlmostEqual(candidate.stop_price, 1.0895)
        self.assertAlmostEqual(candidate.target_price, 1.1000)

    def test_missing_reference_bar_fails_closed_with_reasoned_no_trade(self) -> None:
        day = date(2021, 3, 18)
        config = PreviousDayRejectionConfig(buffer_pips=0, timeframe="1h")
        reference = _reference_bars(day)
        missing = reference.pop(4).timestamp_utc
        candidate = generate_previous_day_rejection_candidates(
            reference + _signal_session_bars(day, signal_direction=None), config=config
        )[0]
        self.assertIs(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "INCOMPLETE_REFERENCE_SESSION")
        self.assertEqual(candidate.metadata["missing_timestamp_utc"], missing)

    def test_complete_session_without_rejection_emits_no_rejection(self) -> None:
        day = date(2021, 3, 19)
        config = PreviousDayRejectionConfig(buffer_pips=0, timeframe="1h")
        candidate = generate_previous_day_rejection_candidates(
            _reference_bars(day) + _signal_session_bars(day, signal_direction=None), config=config
        )[0]
        self.assertIs(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "NO_REJECTION")

    def test_ambiguous_dual_rejection_fails_closed(self) -> None:
        day = date(2021, 3, 22)
        config = PreviousDayRejectionConfig(buffer_pips=0, timeframe="1h")
        signal = _signal_session_bars(day, signal_direction=None)
        signal[1] = _bar(
            _local_utc(day, 8, zone=LONDON),
            close=1.1000,
            high=1.1110,
            low=1.0890,
        )
        candidate = generate_previous_day_rejection_candidates(
            _reference_bars(day) + signal, config=config
        )[0]
        self.assertIs(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "AMBIGUOUS_DUAL_REJECTION")

    def test_first_rejection_only_and_candidate_bytes_are_deterministic(self) -> None:
        day = date(2021, 3, 23)
        config = PreviousDayRejectionConfig(buffer_pips=0, timeframe="1h")
        signal = _signal_session_bars(day, signal_direction=Direction.SHORT)
        signal[2] = _bar(
            _local_utc(day, 9, zone=LONDON),
            close=1.0910,
            high=1.0920,
            low=1.0890,
        )
        bars = tuple(_reference_bars(day) + signal)
        first = generate_previous_day_rejection_candidates(bars, config=config)
        second = generate_previous_day_rejection_candidates(tuple(reversed(bars)), config=config)
        self.assertEqual(len(first), 1)
        self.assertIs(first[0].direction, Direction.SHORT)
        self.assertEqual(
            tuple(item.stable_json_bytes() for item in first),
            tuple(item.stable_json_bytes() for item in second),
        )


if __name__ == "__main__":
    unittest.main()
