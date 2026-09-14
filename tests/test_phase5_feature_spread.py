from __future__ import annotations

import unittest

import polars as pl

from tests.phase5_helpers import make_bars


class Phase5SpreadFeatureTests(unittest.TestCase):
    def _features(self, frame=None):
        from fmp.features.base import prepare_base_frame
        from fmp.features.spread import add_spread_features

        frame = frame if frame is not None else make_bars(timeframe="1h", count=30)
        base = prepare_base_frame(frame, symbol="EURUSD", timeframe="1h", processed_manifest_sha256="a" * 64)
        return add_spread_features(base)

    def test_close_spread_and_complete_windows(self) -> None:
        out = self._features()
        row = out.row(24, named=True)
        self.assertAlmostEqual(
            row["spread_close_pips"],
            (row["ask_close"] - row["bid_close"]) / row["pip_size"],
        )
        self.assertIsNotNone(row["spread_mean_1h_pips"])
        self.assertIsNotNone(row["spread_median_prior_8h_pips"])
        self.assertIsNotNone(row["spread_vs_prior_median_8h"])
        self.assertIsNotNone(row["spread_percentile_prior_24h"])
        self.assertGreaterEqual(row["spread_percentile_prior_24h"], 0.0)
        self.assertLessEqual(row["spread_percentile_prior_24h"], 1.0)

    def test_prior_windows_exclude_current_spread(self) -> None:
        frame = make_bars(timeframe="1h", count=12)
        ts = frame["timestamp_utc"][-1]
        frame = frame.with_columns(
            pl.when(pl.col("timestamp_utc") == ts)
            .then(pl.col("bid_close") + 0.01)
            .otherwise(pl.col("ask_close"))
            .alias("ask_close")
        )
        out = self._features(frame)
        row = out.row(-1, named=True)
        self.assertGreater(row["spread_vs_prior_median_8h"], 100)

    def test_gap_nulls_prior_duration_windows(self) -> None:
        frame = make_bars(timeframe="1h", count=12).filter(pl.int_range(pl.len()) != 7)
        row = self._features(frame).row(-1, named=True)
        self.assertIsNone(row["spread_median_prior_8h_pips"])
        self.assertIsNone(row["spread_vs_prior_median_8h"])

    def test_nonpositive_prior_median_makes_ratio_null(self) -> None:
        frame = make_bars(timeframe="1h", count=12).with_columns(
            pl.col("bid_close").alias("ask_close")
        )
        row = self._features(frame).row(-1, named=True)
        self.assertIsNone(row["spread_vs_prior_median_8h"])


if __name__ == "__main__":
    unittest.main()
