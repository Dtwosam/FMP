from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from tests.phase5_helpers import make_bars


class Phase5FeatureBaseTests(unittest.TestCase):
    def test_base_frame_midpoints_pips_and_availability(self) -> None:
        from fmp.features.base import prepare_base_frame

        frame = make_bars(symbol="EURUSD", timeframe="15m", count=2)
        out = prepare_base_frame(
            frame,
            symbol="EURUSD",
            timeframe="15m",
            processed_manifest_sha256="a" * 64,
        )
        row = out.row(0, named=True)
        self.assertAlmostEqual(row["mid_open"], (row["bid_open"] + row["ask_open"]) / 2)
        self.assertAlmostEqual(row["mid_high"], (row["bid_high"] + row["ask_high"]) / 2)
        self.assertEqual(row["bar_end_utc"], row["bar_start_utc"] + timedelta(minutes=15))
        self.assertEqual(row["available_at_utc"], row["bar_end_utc"])
        self.assertEqual(row["feature_set_version"], "fmp-feature-v1")
        self.assertEqual(row["processed_manifest_sha256"], "a" * 64)
        self.assertEqual(row["pip_size"], 0.0001)

    def test_jpy_pip_size_is_one_hundredth(self) -> None:
        from fmp.features.base import prepare_base_frame

        out = prepare_base_frame(
            make_bars(symbol="USDJPY", timeframe="1h", count=1),
            symbol="USDJPY",
            timeframe="1h",
            processed_manifest_sha256="b" * 64,
        )
        self.assertEqual(out["pip_size"][0], 0.01)

    def test_base_rejects_duplicates_wrong_symbol_and_wrong_timeframe(self) -> None:
        import polars as pl
        from fmp.features.base import prepare_base_frame

        frame = make_bars(count=2)
        dup = pl.concat([frame, frame.slice(0, 1)])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            prepare_base_frame(dup, symbol="EURUSD", timeframe="1h", processed_manifest_sha256="c" * 64)
        with self.assertRaises(ValueError):
            prepare_base_frame(frame, symbol="GBPUSD", timeframe="1h", processed_manifest_sha256="c" * 64)
        with self.assertRaises(ValueError):
            prepare_base_frame(frame, symbol="EURUSD", timeframe="5m", processed_manifest_sha256="c" * 64)

    def test_incomplete_current_bar_is_retained_for_null_feature_semantics(self) -> None:
        from fmp.features.base import prepare_base_frame

        frame = make_bars(count=2).with_columns(
            __import__("polars").when(__import__("polars").col("timestamp_utc") == make_bars(count=2)["timestamp_utc"][1])
            .then(False)
            .otherwise(__import__("polars").col("is_complete"))
            .alias("is_complete")
        )
        out = prepare_base_frame(frame, symbol="EURUSD", timeframe="1h", processed_manifest_sha256="d" * 64)
        self.assertEqual(out.height, 2)
        self.assertFalse(out["is_complete"][1])


if __name__ == "__main__":
    unittest.main()
