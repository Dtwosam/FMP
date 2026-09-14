from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import unittest
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.volatility_breakout import (
    VolatilityBreakoutConfig,
    generate_volatility_breakout_candidates,
)


LONDON = ZoneInfo("Europe/London")


def _local_utc(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute), tzinfo=LONDON).astimezone(timezone.utc)


def _bar(
    ts: datetime,
    *,
    close: float,
    high: float,
    low: float,
    symbol: str = "EURUSD",
) -> QuoteBar:
    spread = 0.02 if symbol == "USDJPY" else 0.0002
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


def _session_bars(
    day: date,
    *,
    timeframe_minutes: int = 60,
    signal_direction: Direction | None = None,
    signal_range: float = 0.0020,
    symbol: str = "EURUSD",
) -> list[QuoteBar]:
    step = timedelta(minutes=timeframe_minutes)
    reference_high = 150.10 if symbol == "USDJPY" else 1.1000
    reference_low = 150.00 if symbol == "USDJPY" else 1.0990
    reference_close = (reference_high + reference_low) / 2
    base_range = reference_high - reference_low

    start = _local_utc(day, 0)
    end = _local_utc(day, 16)
    bars: list[QuoteBar] = []
    current = start
    while current <= end:
        local = current.astimezone(LONDON)
        if local.hour == 8 and local.minute == 0 and signal_direction is Direction.LONG:
            low = reference_high
            high = low + signal_range
            close = low + signal_range / 2
            bars.append(_bar(current, close=close, high=high, low=low, symbol=symbol))
        elif local.hour == 8 and local.minute == 0 and signal_direction is Direction.SHORT:
            high = reference_low
            low = high - signal_range
            close = high - signal_range / 2
            bars.append(_bar(current, close=close, high=high, low=low, symbol=symbol))
        else:
            bars.append(
                _bar(
                    current,
                    close=reference_close,
                    high=reference_high,
                    low=reference_low,
                    symbol=symbol,
                )
            )
        current += step
    return bars


def _candidate_for_day(candidates, day: date):
    matched = [item for item in candidates if item.metadata.get("session_date") == day.isoformat()]
    if len(matched) != 1:
        raise AssertionError(f"expected exactly one candidate for {day}, got {len(matched)}")
    return matched[0]


class VolatilityBreakoutTests(unittest.TestCase):
    def test_config_accepts_only_frozen_multipliers_and_timeframes(self) -> None:
        for multiplier in (1.0, 1.5, 2.0):
            for timeframe in ("5m", "15m", "1h"):
                config = VolatilityBreakoutConfig(
                    range_multiplier=multiplier,
                    timeframe=timeframe,
                )
                self.assertEqual((config.range_multiplier, config.timeframe), (multiplier, timeframe))
        with self.assertRaises(ValueError):
            VolatilityBreakoutConfig(range_multiplier=1.25, timeframe="1h")
        with self.assertRaises(ValueError):
            VolatilityBreakoutConfig(range_multiplier=1.0, timeframe="1m")

    def test_long_breakout_uses_exact_preceding_8h_reference_and_fixed_1r_target(self) -> None:
        day = date(2021, 4, 6)
        config = VolatilityBreakoutConfig(range_multiplier=1.5, timeframe="1h")
        candidate = _candidate_for_day(
            generate_volatility_breakout_candidates(
                _session_bars(day, signal_direction=Direction.LONG),
                config=config,
            ),
            day,
        )
        self.assertIs(candidate.direction, Direction.LONG)
        self.assertEqual(candidate.reason_code, "VOLATILITY_BREAKOUT_LONG")
        self.assertEqual(candidate.observation_bar_timestamp_utc, _local_utc(day, 8))
        self.assertEqual(candidate.signal_known_timestamp_utc, _local_utc(day, 9))
        self.assertEqual(candidate.latest_exit_timestamp_utc, _local_utc(day, 16))
        self.assertAlmostEqual(candidate.metadata["reference_high"], 1.1000)
        self.assertAlmostEqual(candidate.metadata["reference_low"], 1.0990)
        self.assertAlmostEqual(candidate.metadata["reference_median_range"], 0.0010)
        self.assertEqual(candidate.metadata["reference_start_utc"], _local_utc(day, 0))
        self.assertEqual(candidate.metadata["reference_end_utc"], _local_utc(day, 8))
        self.assertAlmostEqual(candidate.stop_price, 1.1000)
        self.assertAlmostEqual(candidate.target_price, 1.1020)

    def test_short_breakout_is_symmetric(self) -> None:
        day = date(2021, 4, 7)
        config = VolatilityBreakoutConfig(range_multiplier=1.5, timeframe="1h")
        candidate = _candidate_for_day(
            generate_volatility_breakout_candidates(
                _session_bars(day, signal_direction=Direction.SHORT),
                config=config,
            ),
            day,
        )
        self.assertIs(candidate.direction, Direction.SHORT)
        self.assertEqual(candidate.reason_code, "VOLATILITY_BREAKOUT_SHORT")
        self.assertAlmostEqual(candidate.stop_price, 1.0990)
        self.assertAlmostEqual(candidate.target_price, 1.0970)

    def test_range_threshold_is_inclusive_but_close_break_must_be_strict(self) -> None:
        day = date(2021, 4, 8)
        qualifying = VolatilityBreakoutConfig(range_multiplier=2.0, timeframe="1h")
        candidate = _candidate_for_day(
            generate_volatility_breakout_candidates(
                _session_bars(day, signal_direction=Direction.LONG, signal_range=0.0020),
                config=qualifying,
            ),
            day,
        )
        self.assertIs(candidate.direction, Direction.LONG)

        bars = _session_bars(day, signal_direction=None)
        bars[8] = _bar(
            _local_utc(day, 8),
            close=1.1000,
            high=1.1010,
            low=1.0990,
        )
        no_break = _candidate_for_day(
            generate_volatility_breakout_candidates(bars, config=qualifying),
            day,
        )
        self.assertIs(no_break.direction, Direction.NO_TRADE)
        self.assertEqual(no_break.reason_code, "NO_VOLATILITY_BREAKOUT")

    def test_range_below_multiplier_does_not_qualify_even_with_channel_break(self) -> None:
        day = date(2021, 4, 9)
        config = VolatilityBreakoutConfig(range_multiplier=2.0, timeframe="1h")
        candidate = _candidate_for_day(
            generate_volatility_breakout_candidates(
                _session_bars(day, signal_direction=Direction.LONG, signal_range=0.0018),
                config=config,
            ),
            day,
        )
        self.assertIs(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "NO_VOLATILITY_BREAKOUT")

    def test_missing_reference_or_exit_bar_fails_closed(self) -> None:
        day = date(2021, 4, 12)
        config = VolatilityBreakoutConfig(range_multiplier=1.0, timeframe="1h")
        for missing in (_local_utc(day, 3), _local_utc(day, 16)):
            bars = [bar for bar in _session_bars(day) if bar.timestamp_utc != missing]
            candidate = _candidate_for_day(
                generate_volatility_breakout_candidates(bars, config=config),
                day,
            )
            self.assertIs(candidate.direction, Direction.NO_TRADE)
            self.assertEqual(candidate.reason_code, "INCOMPLETE_VOLATILITY_SESSION")
            self.assertEqual(candidate.metadata["missing_timestamp_utc"], missing)

    def test_london_dst_and_15m_signal_known_time_are_explicit(self) -> None:
        day = date(2021, 3, 29)
        config = VolatilityBreakoutConfig(range_multiplier=1.5, timeframe="15m")
        candidate = _candidate_for_day(
            generate_volatility_breakout_candidates(
                _session_bars(
                    day,
                    timeframe_minutes=15,
                    signal_direction=Direction.LONG,
                    signal_range=0.0020,
                ),
                config=config,
            ),
            day,
        )
        self.assertEqual(candidate.observation_bar_timestamp_utc, datetime(2021, 3, 29, 7, 0, tzinfo=timezone.utc))
        self.assertEqual(candidate.signal_known_timestamp_utc, datetime(2021, 3, 29, 7, 15, tzinfo=timezone.utc))
        self.assertEqual(candidate.latest_exit_timestamp_utc, datetime(2021, 3, 29, 15, 0, tzinfo=timezone.utc))

    def test_first_breakout_only_and_candidate_bytes_are_deterministic(self) -> None:
        day = date(2021, 4, 13)
        config = VolatilityBreakoutConfig(range_multiplier=1.0, timeframe="1h")
        bars = _session_bars(day, signal_direction=Direction.LONG)
        bars[9] = _bar(_local_utc(day, 9), close=1.0975, high=1.0990, low=1.0970)
        first = generate_volatility_breakout_candidates(tuple(bars), config=config)
        second = generate_volatility_breakout_candidates(tuple(reversed(bars)), config=config)
        candidate = _candidate_for_day(first, day)
        self.assertIs(candidate.direction, Direction.LONG)
        self.assertEqual(
            tuple(item.stable_json_bytes() for item in first),
            tuple(item.stable_json_bytes() for item in second),
        )

    def test_rejects_duplicate_or_multi_symbol_input(self) -> None:
        day = date(2021, 4, 14)
        config = VolatilityBreakoutConfig(range_multiplier=1.0, timeframe="1h")
        bars = _session_bars(day)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            generate_volatility_breakout_candidates(bars + [bars[0]], config=config)
        mixed = bars + [_bar(_local_utc(day, 17), close=150.0, high=150.1, low=149.9, symbol="USDJPY")]
        with self.assertRaisesRegex(ValueError, "exactly one symbol"):
            generate_volatility_breakout_candidates(mixed, config=config)


if __name__ == "__main__":
    unittest.main()
