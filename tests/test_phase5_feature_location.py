from __future__ import annotations

import unittest
from datetime import datetime, timezone

import polars as pl

from tests.phase5_helpers import make_bars


class Phase5LocationFeatureTests(unittest.TestCase):
    def _features(self, frame):
        from fmp.features.base import prepare_base_frame
        from fmp.features.location import add_location_features

        base = prepare_base_frame(
            frame, symbol="EURUSD", timeframe="1h", processed_manifest_sha256="a" * 64
        )
        return add_location_features(base)

    def test_completed_same_day_asia_and_london_levels_become_available_after_close(self) -> None:
        frame = make_bars(timeframe="1h", start=datetime(2023, 1, 9, 0, tzinfo=timezone.utc), count=48)
        out = self._features(frame)
        # At 12:00 UTC, Tokyo 09:00-17:00 session (00:00-08:00 UTC) is complete.
        asia = out.filter(pl.col("bar_start_utc") == datetime(2023, 1, 9, 12, tzinfo=timezone.utc)).row(0, named=True)
        self.assertIsNotNone(asia["prev_asia_high_dist_pips"])
        self.assertIsNotNone(asia["prev_asia_low_dist_pips"])
        # At 17:00 UTC, London 08:00-16:00 session is complete.
        london = out.filter(pl.col("bar_start_utc") == datetime(2023, 1, 9, 17, tzinfo=timezone.utc)).row(0, named=True)
        self.assertIsNotNone(london["prev_london_high_dist_pips"])
        self.assertIsNotNone(london["prev_london_low_dist_pips"])

    def test_previous_fx_day_uses_new_york_close_boundary(self) -> None:
        frame = make_bars(timeframe="1h", start=datetime(2023, 1, 9, 22, tzinfo=timezone.utc), count=30)
        out = self._features(frame)
        row = out.filter(pl.col("bar_start_utc") == datetime(2023, 1, 10, 23, tzinfo=timezone.utc)).row(0, named=True)
        self.assertIsNotNone(row["prev_fx_day_high_dist_pips"])
        self.assertIsNotNone(row["prev_fx_day_low_dist_pips"])
        self.assertIsNotNone(row["prev_fx_day_close_dist_pips"])

    def test_incomplete_reference_session_is_not_used_and_last_complete_reference_persists(self) -> None:
        frame = make_bars(timeframe="1h", start=datetime(2023, 1, 9, 0, tzinfo=timezone.utc), count=60)
        bad_ts = datetime(2023, 1, 10, 3, tzinfo=timezone.utc)  # inside second Asia session
        frame = frame.with_columns(
            pl.when(pl.col("timestamp_utc") == bad_ts)
            .then(False)
            .otherwise(pl.col("is_complete"))
            .alias("is_complete")
        )
        out = self._features(frame)
        before_bad = out.filter(pl.col("bar_start_utc") == datetime(2023, 1, 9, 12, tzinfo=timezone.utc)).row(0, named=True)
        after_bad = out.filter(pl.col("bar_start_utc") == datetime(2023, 1, 10, 12, tzinfo=timezone.utc)).row(0, named=True)
        # Second Asia session is incomplete, so the explicit reference remains the first complete one.
        self.assertAlmostEqual(
            after_bad["prev_asia_high_dist_pips"] - before_bad["prev_asia_high_dist_pips"],
            (after_bad["mid_close"] - before_bad["mid_close"]) / after_bad["pip_size"],
            places=8,
        )

    def test_no_complete_reference_means_null_not_partial_level(self) -> None:
        frame = make_bars(timeframe="1h", start=datetime(2023, 1, 9, 2, tzinfo=timezone.utc), count=8)
        out = self._features(frame)
        row = out.row(-1, named=True)
        self.assertIsNone(row["prev_asia_high_dist_pips"])
        self.assertIsNone(row["prev_london_high_dist_pips"])
        self.assertIsNone(row["prev_fx_day_high_dist_pips"])


if __name__ == "__main__":
    unittest.main()
