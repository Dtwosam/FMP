from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import math
import unittest
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.mean_reversion import (
    MeanReversionConfig,
    duration_to_bars,
    generate_mean_reversion_candidates,
    rolling_reference,
    z_score_against_reference,
)


LONDON = ZoneInfo("Europe/London")


def _bar(ts: datetime, close: float, *, symbol: str = "EURUSD") -> QuoteBar:
    spread = 0.0002 if symbol != "USDJPY" else 0.02
    bid = close - spread / 2
    ask = close + spread / 2
    return QuoteBar(
        symbol=symbol,
        timestamp_utc=ts,
        bid_open=bid,
        bid_high=bid,
        bid_low=bid,
        bid_close=bid,
        ask_open=ask,
        ask_high=ask,
        ask_low=ask,
        ask_close=ask,
    )


def _local_utc(day: date, hour: int) -> datetime:
    return datetime.combine(day, time(hour, 0), tzinfo=LONDON).astimezone(timezone.utc)


def _one_hour_session(day: date, signal_close: float, *, include_exit: bool = True) -> tuple[QuoteBar, ...]:
    closes = (1.0000, 1.0100, 0.9900, 1.0000, 1.0000, signal_close)
    bars = [
        _bar(_local_utc(day, local_hour), close)
        for local_hour, close in zip(range(3, 9), closes)
    ]
    if include_exit:
        bars.append(_bar(_local_utc(day, 16), 1.0000))
    return tuple(bars)


class MeanReversionPrimitiveTests(unittest.TestCase):
    def test_config_accepts_only_frozen_grid(self) -> None:
        for lookback in (4, 8, 16):
            for threshold in (1.5, 2.0):
                for timeframe in ("5m", "15m", "1h"):
                    cfg = MeanReversionConfig(lookback, threshold, timeframe)
                    self.assertEqual((cfg.lookback_hours, cfg.threshold_sigma, cfg.timeframe), (lookback, threshold, timeframe))

        with self.assertRaises(ValueError):
            MeanReversionConfig(2, 1.5, "5m")
        with self.assertRaises(ValueError):
            MeanReversionConfig(4, 1.0, "5m")
        with self.assertRaises(ValueError):
            MeanReversionConfig(4, 1.5, "1m")

    def test_duration_to_bars_matches_wall_clock_lookbacks(self) -> None:
        expected = {
            (4, "5m"): 48,
            (4, "15m"): 16,
            (4, "1h"): 4,
            (8, "5m"): 96,
            (8, "15m"): 32,
            (8, "1h"): 8,
            (16, "5m"): 192,
            (16, "15m"): 64,
            (16, "1h"): 16,
        }
        for (hours, timeframe), count in expected.items():
            self.assertEqual(duration_to_bars(timeframe, hours), count)

    def test_reference_excludes_observation_and_uses_population_stddev(self) -> None:
        start = datetime(2020, 1, 1, tzinfo=timezone.utc)
        bars = tuple(_bar(start + timedelta(hours=i), close) for i, close in enumerate((1.0, 2.0, 3.0, 4.0, 100.0)))
        reference = rolling_reference(
            bars,
            observation_index=4,
            lookback_count=4,
            width=timedelta(hours=1),
        )
        self.assertIsNotNone(reference)
        mean, std = reference
        self.assertAlmostEqual(mean, 2.5)
        self.assertAlmostEqual(std, math.sqrt(1.25))
        self.assertAlmostEqual(z_score_against_reference(4.5, mean, std), 2.0 / math.sqrt(1.25))

    def test_reference_fails_closed_on_missing_cadence(self) -> None:
        start = datetime(2020, 1, 1, tzinfo=timezone.utc)
        bars = (
            _bar(start, 1.0),
            _bar(start + timedelta(hours=1), 2.0),
            _bar(start + timedelta(hours=3), 3.0),
            _bar(start + timedelta(hours=4), 4.0),
            _bar(start + timedelta(hours=5), 5.0),
        )
        self.assertIsNone(
            rolling_reference(
                bars,
                observation_index=4,
                lookback_count=4,
                width=timedelta(hours=1),
            )
        )

    def test_reference_fails_closed_on_zero_variance(self) -> None:
        start = datetime(2020, 1, 1, tzinfo=timezone.utc)
        bars = tuple(_bar(start + timedelta(hours=i), 1.0) for i in range(5))
        self.assertIsNone(
            rolling_reference(
                bars,
                observation_index=4,
                lookback_count=4,
                width=timedelta(hours=1),
            )
        )


class MeanReversionCandidateTests(unittest.TestCase):
    def test_long_fresh_excursion_uses_pre_session_previous_state_and_frozen_geometry(self) -> None:
        day = date(2020, 1, 15)
        config = MeanReversionConfig(4, 1.5, "1h")
        candidates = generate_mean_reversion_candidates(_one_hour_session(day, 0.9850), config=config)
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertIs(candidate.direction, Direction.LONG)
        self.assertEqual(candidate.observation_bar_timestamp_utc, _local_utc(day, 8))
        self.assertEqual(candidate.signal_known_timestamp_utc, _local_utc(day, 9))
        self.assertEqual(candidate.latest_exit_timestamp_utc, _local_utc(day, 16))
        self.assertAlmostEqual(candidate.metadata["previous_z"], 0.0)
        self.assertLessEqual(candidate.metadata["current_z"], -1.5)
        self.assertAlmostEqual(candidate.target_price, 1.0)
        self.assertAlmostEqual(candidate.stop_price, 0.9850 - math.sqrt(0.00005))

    def test_short_fresh_excursion_is_symmetric(self) -> None:
        day = date(2020, 1, 16)
        config = MeanReversionConfig(4, 1.5, "1h")
        candidate = generate_mean_reversion_candidates(_one_hour_session(day, 1.0150), config=config)[0]
        self.assertIs(candidate.direction, Direction.SHORT)
        self.assertGreaterEqual(candidate.metadata["current_z"], 1.5)
        self.assertAlmostEqual(candidate.target_price, 1.0)
        self.assertAlmostEqual(candidate.stop_price, 1.0150 + math.sqrt(0.00005))

    def test_missing_exact_exit_fails_closed(self) -> None:
        day = date(2020, 1, 17)
        config = MeanReversionConfig(4, 1.5, "1h")
        candidate = generate_mean_reversion_candidates(
            _one_hour_session(day, 0.9850, include_exit=False),
            config=config,
        )[0]
        self.assertIs(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "INCOMPLETE_SESSION")

    def test_summer_dst_maps_0800_and_1600_london_to_shifted_utc(self) -> None:
        day = date(2020, 7, 1)
        config = MeanReversionConfig(4, 1.5, "1h")
        candidate = generate_mean_reversion_candidates(_one_hour_session(day, 0.9850), config=config)[0]
        self.assertEqual(candidate.observation_bar_timestamp_utc.hour, 7)
        self.assertEqual(candidate.latest_exit_timestamp_utc.hour, 15)

    def test_candidate_generation_is_byte_deterministic(self) -> None:
        day = date(2020, 1, 20)
        config = MeanReversionConfig(4, 2.0, "1h")
        bars = _one_hour_session(day, 0.9850)
        first = generate_mean_reversion_candidates(bars, config=config)
        second = generate_mean_reversion_candidates(tuple(reversed(bars)), config=config)
        self.assertEqual(
            tuple(candidate.stable_json_bytes() for candidate in first),
            tuple(candidate.stable_json_bytes() for candidate in second),
        )


if __name__ == "__main__":
    unittest.main()
