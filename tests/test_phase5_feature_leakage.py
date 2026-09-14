from __future__ import annotations

import unittest

import polars as pl
from polars.testing import assert_frame_equal

from tests.phase5_helpers import make_bars


class Phase5LeakageTests(unittest.TestCase):
    def _build(self, frame):
        from fmp.features.engine import build_feature_frame

        return build_feature_frame(
            frame, symbol="EURUSD", timeframe="1h", processed_manifest_sha256="a" * 64
        )

    def test_prefix_equivalence(self) -> None:
        source = make_bars(timeframe="1h", count=40)
        full = self._build(source)
        prefix = self._build(source.head(25))
        assert_frame_equal(full.head(25), prefix, check_row_order=True, check_column_order=True)

    def test_future_perturbation_does_not_change_earlier_rows(self) -> None:
        source = make_bars(timeframe="1h", count=40)
        cutoff = source["timestamp_utc"][24]
        perturbed = source.with_columns(
            pl.when(pl.col("timestamp_utc") > cutoff)
            .then(pl.col("bid_close") + 5.0)
            .otherwise(pl.col("bid_close"))
            .alias("bid_close"),
            pl.when(pl.col("timestamp_utc") > cutoff)
            .then(pl.col("ask_close") + 5.0)
            .otherwise(pl.col("ask_close"))
            .alias("ask_close"),
        )
        baseline = self._build(source)
        changed = self._build(perturbed)
        assert_frame_equal(baseline.head(25), changed.head(25), check_row_order=True, check_column_order=True)

    def test_current_closed_bar_is_allowed_to_change_current_feature_row(self) -> None:
        source = make_bars(timeframe="1h", count=30)
        ts = source["timestamp_utc"][20]
        changed_source = source.with_columns(
            pl.when(pl.col("timestamp_utc") == ts)
            .then(pl.col("bid_close") + 0.01)
            .otherwise(pl.col("bid_close"))
            .alias("bid_close"),
            pl.when(pl.col("timestamp_utc") == ts)
            .then(pl.col("ask_close") + 0.01)
            .otherwise(pl.col("ask_close"))
            .alias("ask_close"),
        )
        baseline = self._build(source).row(20, named=True)
        changed = self._build(changed_source).row(20, named=True)
        self.assertNotEqual(baseline["return_1bar"], changed["return_1bar"])
        self.assertEqual(baseline["available_at_utc"], changed["available_at_utc"])

    def test_gap_forces_post_gap_warmup_for_long_windows(self) -> None:
        source = make_bars(timeframe="1h", count=35).filter(pl.int_range(pl.len()) != 10)
        out = self._build(source)
        # Immediately after a missing bar, 24h duration features cannot be complete.
        row = out.row(12, named=True)
        self.assertIsNone(row["return_24h"])
        self.assertIsNone(row["realized_vol_24h"])
        self.assertIsNone(row["spread_percentile_prior_24h"])

    def test_deterministic_regeneration_values(self) -> None:
        source = make_bars(timeframe="1h", count=35)
        first = self._build(source)
        second = self._build(source)
        assert_frame_equal(first, second, check_row_order=True, check_column_order=True)


if __name__ == "__main__":
    unittest.main()
