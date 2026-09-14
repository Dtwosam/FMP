from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import unittest
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.session_sweep_rejection import (
    SessionSweepRejectionConfig,
    generate_session_sweep_rejection_candidates,
)


LONDON = ZoneInfo("Europe/London")


def _local_utc(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute), tzinfo=LONDON).astimezone(timezone.utc)


def _bar(
    ts: datetime,
    *,
    close: float,
    high: float | None = None,
    low: float | None = None,
    symbol: str = "EURUSD",
) -> QuoteBar:
    spread = 0.02 if symbol == "USDJPY" else 0.0002
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


def _bars_for_day(
    day: date,
    *,
    timeframe_minutes: int = 60,
    symbol: str = "EURUSD",
    signal_direction: Direction | None = None,
    buffer_pips: int = 0,
    signal_hour: int = 8,
) -> list[QuoteBar]:
    center = 150.00 if symbol == "USDJPY" else 1.1000
    high_level = 150.10 if symbol == "USDJPY" else 1.1100
    low_level = 149.90 if symbol == "USDJPY" else 1.0900
    inside = 0.01 if symbol == "USDJPY" else 0.0010
    pip = 0.01 if symbol == "USDJPY" else 0.0001
    width = timedelta(minutes=timeframe_minutes)

    bars: list[QuoteBar] = []
    current = _local_utc(day, 0)
    reference_end = _local_utc(day, 8)
    index = 0
    while current < reference_end:
        bars.append(
            _bar(
                current,
                close=center,
                high=high_level if index == 2 else center,
                low=low_level if index == 5 else center,
                symbol=symbol,
            )
        )
        current += width
        index += 1

    current = _local_utc(day, 8)
    exit_label = _local_utc(day, 16)
    while current <= exit_label:
        local_hour = current.astimezone(LONDON).hour
        if local_hour == signal_hour and signal_direction is Direction.SHORT:
            bars.append(
                _bar(
                    current,
                    close=high_level - inside,
                    high=high_level + buffer_pips * pip,
                    low=high_level - 2 * inside,
                    symbol=symbol,
                )
            )
        elif local_hour == signal_hour and signal_direction is Direction.LONG:
            bars.append(
                _bar(
                    current,
                    close=low_level + inside,
                    high=low_level + 2 * inside,
                    low=low_level - buffer_pips * pip,
                    symbol=symbol,
                )
            )
        else:
            bars.append(_bar(current, close=center, symbol=symbol))
        current += width
    return bars


def _candidate_for_day(candidates, day: date):
    matched = [
        candidate
        for candidate in candidates
        if candidate.metadata.get("session_date") == day.isoformat()
    ]
    if len(matched) != 1:
        raise AssertionError(f"expected one candidate for {day}, got {len(matched)}")
    return matched[0]


class SessionSweepRejectionTests(unittest.TestCase):
    def test_config_accepts_only_frozen_buffers_and_timeframes(self) -> None:
        for buffer_pips in (0, 2, 5):
            for timeframe in ("5m", "15m", "1h"):
                config = SessionSweepRejectionConfig(buffer_pips=buffer_pips, timeframe=timeframe)
                self.assertEqual((config.buffer_pips, config.timeframe), (buffer_pips, timeframe))
        with self.assertRaises(ValueError):
            SessionSweepRejectionConfig(buffer_pips=1, timeframe="1h")
        with self.assertRaises(ValueError):
            SessionSweepRejectionConfig(buffer_pips=0, timeframe="1m")

    def test_short_sweep_uses_frozen_session_levels_and_signal_extreme(self) -> None:
        day = date(2021, 1, 12)
        config = SessionSweepRejectionConfig(buffer_pips=2, timeframe="1h")
        candidate = _candidate_for_day(
            generate_session_sweep_rejection_candidates(
                _bars_for_day(day, signal_direction=Direction.SHORT, buffer_pips=2),
                config=config,
            ),
            day,
        )
        self.assertIs(candidate.direction, Direction.SHORT)
        self.assertEqual(candidate.reason_code, "SESSION_SWEEP_REJECTION_SHORT")
        self.assertEqual(candidate.observation_bar_timestamp_utc, _local_utc(day, 8))
        self.assertEqual(candidate.signal_known_timestamp_utc, _local_utc(day, 9))
        self.assertEqual(candidate.latest_exit_timestamp_utc, _local_utc(day, 16))
        self.assertAlmostEqual(candidate.stop_price, 1.1102)
        self.assertAlmostEqual(candidate.target_price, 1.1000)
        self.assertAlmostEqual(candidate.metadata["reference_high"], 1.1100)
        self.assertAlmostEqual(candidate.metadata["reference_low"], 1.0900)
        self.assertAlmostEqual(candidate.metadata["reference_midpoint"], 1.1000)

    def test_long_sweep_is_symmetric(self) -> None:
        day = date(2021, 1, 13)
        config = SessionSweepRejectionConfig(buffer_pips=5, timeframe="1h")
        candidate = _candidate_for_day(
            generate_session_sweep_rejection_candidates(
                _bars_for_day(day, signal_direction=Direction.LONG, buffer_pips=5),
                config=config,
            ),
            day,
        )
        self.assertIs(candidate.direction, Direction.LONG)
        self.assertAlmostEqual(candidate.stop_price, 1.0895)
        self.assertAlmostEqual(candidate.target_price, 1.1000)

    def test_usdjpy_uses_jpy_pip_size(self) -> None:
        day = date(2021, 1, 14)
        config = SessionSweepRejectionConfig(buffer_pips=2, timeframe="1h")
        candidate = _candidate_for_day(
            generate_session_sweep_rejection_candidates(
                _bars_for_day(
                    day,
                    symbol="USDJPY",
                    signal_direction=Direction.SHORT,
                    buffer_pips=2,
                ),
                config=config,
            ),
            day,
        )
        self.assertIs(candidate.direction, Direction.SHORT)
        self.assertAlmostEqual(candidate.stop_price, 150.12)
        self.assertAlmostEqual(candidate.target_price, 150.00)

    def test_zero_buffer_touch_qualifies_but_close_on_boundary_does_not(self) -> None:
        day = date(2021, 1, 15)
        config = SessionSweepRejectionConfig(buffer_pips=0, timeframe="1h")
        bars = _bars_for_day(day)
        bars[8] = _bar(_local_utc(day, 8), close=1.1100, high=1.1100, low=1.1090)
        candidate = _candidate_for_day(
            generate_session_sweep_rejection_candidates(bars, config=config), day
        )
        self.assertIs(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "NO_SESSION_SWEEP_REJECTION")

        bars[8] = _bar(_local_utc(day, 8), close=1.1090, high=1.1100, low=1.1080)
        candidate = _candidate_for_day(
            generate_session_sweep_rejection_candidates(bars, config=config), day
        )
        self.assertIs(candidate.direction, Direction.SHORT)

    def test_summer_dst_maps_london_session_and_exit(self) -> None:
        day = date(2021, 7, 15)
        config = SessionSweepRejectionConfig(buffer_pips=0, timeframe="1h")
        candidate = _candidate_for_day(
            generate_session_sweep_rejection_candidates(
                _bars_for_day(day, signal_direction=Direction.SHORT),
                config=config,
            ),
            day,
        )
        self.assertEqual(candidate.observation_bar_timestamp_utc, datetime(2021, 7, 15, 7, tzinfo=timezone.utc))
        self.assertEqual(candidate.latest_exit_timestamp_utc, datetime(2021, 7, 15, 15, tzinfo=timezone.utc))

    def test_missing_reference_bar_fails_closed(self) -> None:
        day = date(2021, 1, 18)
        config = SessionSweepRejectionConfig(buffer_pips=0, timeframe="1h")
        bars = _bars_for_day(day)
        missing = bars.pop(3).timestamp_utc
        candidate = _candidate_for_day(
            generate_session_sweep_rejection_candidates(bars, config=config), day
        )
        self.assertIs(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "INCOMPLETE_REFERENCE_SESSION")
        self.assertEqual(candidate.metadata["missing_timestamp_utc"], missing)

    def test_missing_signal_bar_or_exact_exit_fails_closed(self) -> None:
        day = date(2021, 1, 19)
        config = SessionSweepRejectionConfig(buffer_pips=0, timeframe="1h")
        bars = _bars_for_day(day)
        bars = [bar for bar in bars if bar.timestamp_utc != _local_utc(day, 12)]
        candidate = _candidate_for_day(
            generate_session_sweep_rejection_candidates(bars, config=config), day
        )
        self.assertEqual(candidate.reason_code, "INCOMPLETE_SIGNAL_SESSION")

        bars = [
            bar
            for bar in _bars_for_day(day)
            if bar.timestamp_utc != _local_utc(day, 16)
        ]
        candidate = _candidate_for_day(
            generate_session_sweep_rejection_candidates(bars, config=config), day
        )
        self.assertEqual(candidate.reason_code, "INCOMPLETE_SIGNAL_SESSION")

    def test_ambiguous_dual_sweep_fails_closed(self) -> None:
        day = date(2021, 1, 20)
        config = SessionSweepRejectionConfig(buffer_pips=0, timeframe="1h")
        bars = _bars_for_day(day)
        bars[8] = _bar(_local_utc(day, 8), close=1.1000, high=1.1110, low=1.0890)
        candidate = _candidate_for_day(
            generate_session_sweep_rejection_candidates(bars, config=config), day
        )
        self.assertIs(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "AMBIGUOUS_DUAL_SESSION_SWEEP")

    def test_invalid_first_geometry_consumes_date_and_does_not_retry(self) -> None:
        day = date(2021, 1, 21)
        config = SessionSweepRejectionConfig(buffer_pips=0, timeframe="1h")
        bars = _bars_for_day(day)
        # First bar sweeps the high but closes below the midpoint, so the frozen
        # midpoint target is not below the SHORT signal close.
        bars[8] = _bar(_local_utc(day, 8), close=1.0990, high=1.1110, low=1.0980)
        # A later valid high rejection must not rescue the date/configuration.
        bars[9] = _bar(_local_utc(day, 9), close=1.1090, high=1.1110, low=1.1080)
        candidate = _candidate_for_day(
            generate_session_sweep_rejection_candidates(bars, config=config), day
        )
        self.assertIs(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "INVALID_SESSION_SWEEP_GEOMETRY")
        self.assertEqual(candidate.observation_bar_timestamp_utc, _local_utc(day, 8))

    def test_complete_no_setup_and_candidate_bytes_are_deterministic(self) -> None:
        day = date(2021, 1, 22)
        config = SessionSweepRejectionConfig(buffer_pips=0, timeframe="1h")
        bars = tuple(_bars_for_day(day))
        first = generate_session_sweep_rejection_candidates(bars, config=config)
        second = generate_session_sweep_rejection_candidates(tuple(reversed(bars)), config=config)
        candidate = _candidate_for_day(first, day)
        self.assertEqual(candidate.reason_code, "NO_SESSION_SWEEP_REJECTION")
        self.assertEqual(
            tuple(item.stable_json_bytes() for item in first),
            tuple(item.stable_json_bytes() for item in second),
        )

    def test_rejects_duplicate_or_multi_symbol_input(self) -> None:
        day = date(2021, 1, 25)
        config = SessionSweepRejectionConfig(buffer_pips=0, timeframe="1h")
        bars = _bars_for_day(day)
        with self.assertRaises(ValueError):
            generate_session_sweep_rejection_candidates(bars + [bars[0]], config=config)
        mixed = bars + [_bar(_local_utc(day, 17), close=150.0, symbol="USDJPY")]
        with self.assertRaises(ValueError):
            generate_session_sweep_rejection_candidates(mixed, config=config)


if __name__ == "__main__":
    unittest.main()
