from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
import unittest

from fmp.contracts import QuoteBar
from fmp.strategies.mean_reversion import (
    MeanReversionConfig,
    duration_to_bars,
    rolling_reference,
    z_score_against_reference,
)


def _bar(ts: datetime, close: float) -> QuoteBar:
    spread = 0.0002
    bid = close - spread / 2
    ask = close + spread / 2
    return QuoteBar(
        symbol="EURUSD",
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


if __name__ == "__main__":
    unittest.main()
