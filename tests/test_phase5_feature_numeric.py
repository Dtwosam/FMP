from __future__ import annotations

import math
import unittest

import polars as pl

from tests.phase5_helpers import make_bars


class Phase5NumericFeatureTests(unittest.TestCase):
    def _features(self, frame=None):
        from fmp.features.base import prepare_base_frame
        from fmp.features.numeric import add_numeric_features

        frame = frame if frame is not None else make_bars(timeframe="1h", count=30)
        base = prepare_base_frame(frame, symbol="EURUSD", timeframe="1h", processed_manifest_sha256="a" * 64)
        return add_numeric_features(base)

    def test_returns_range_true_range_and_candle_formulas(self) -> None:
        out = self._features()
        r1 = out.row(1, named=True)
        r0 = out.row(0, named=True)
        self.assertAlmostEqual(r1["return_1bar"], r1["mid_close"] / r0["mid_close"] - 1.0)
        self.assertAlmostEqual(r1["log_return_1bar"], math.log(r1["mid_close"] / r0["mid_close"]))
        self.assertAlmostEqual(r1["range_pips"], (r1["mid_high"] - r1["mid_low"]) / r1["pip_size"])
        expected_tr = max(
            r1["mid_high"] - r1["mid_low"],
            abs(r1["mid_high"] - r0["mid_close"]),
            abs(r1["mid_low"] - r0["mid_close"]),
        ) / r1["pip_size"]
        self.assertAlmostEqual(r1["true_range_pips"], expected_tr)
        self.assertAlmostEqual(r1["body_pips"], abs(r1["mid_close"] - r1["mid_open"]) / r1["pip_size"])
        self.assertIn(r1["candle_direction"], (-1, 0, 1))

    def test_duration_returns_momentum_sma_and_volatility_are_available_after_warmup(self) -> None:
        out = self._features()
        row = out.row(24, named=True)
        anchor_1h = out.row(23, named=True)
        anchor_24h = out.row(0, named=True)
        self.assertAlmostEqual(row["return_1h"], row["mid_close"] / anchor_1h["mid_close"] - 1.0)
        self.assertAlmostEqual(row["return_24h"], row["mid_close"] / anchor_24h["mid_close"] - 1.0)
        self.assertIsNotNone(row["realized_vol_1h"])
        self.assertIsNotNone(row["realized_vol_8h"])
        self.assertIsNotNone(row["realized_vol_24h"])
        self.assertIsNotNone(row["sma_distance_2h_pips"])
        self.assertIsNotNone(row["sma_distance_8h_pips"])
        self.assertIsNotNone(row["roc_4h"])
        self.assertIsNotNone(row["roc_8h"])
        self.assertIsNotNone(row["momentum_accel_4h"])
        self.assertIn(row["breakout_above_prior_8h"], (0, 1))
        self.assertIn(row["breakout_below_prior_8h"], (0, 1))

    def test_prior_8h_reference_excludes_current_bar(self) -> None:
        frame = make_bars(timeframe="1h", count=12)
        last_ts = frame["timestamp_utc"][-1]
        frame = frame.with_columns(
            pl.when(pl.col("timestamp_utc") == last_ts)
            .then(pl.lit(9.0))
            .otherwise(pl.col("bid_high"))
            .alias("bid_high"),
            pl.when(pl.col("timestamp_utc") == last_ts)
            .then(pl.lit(9.00002))
            .otherwise(pl.col("ask_high"))
            .alias("ask_high"),
        )
        out = self._features(frame)
        self.assertEqual(out["breakout_above_prior_8h"][-1], 1)

    def test_gap_or_incomplete_bar_nulls_duration_window(self) -> None:
        frame = make_bars(timeframe="1h", count=14).slice(0, 14)
        # Remove one bar inside the trailing 8h path.
        frame = frame.filter(pl.int_range(pl.len()) != 8)
        out = self._features(frame)
        row = out.row(-1, named=True)
        self.assertIsNone(row["realized_vol_8h"])
        self.assertIsNone(row["sma_distance_8h_pips"])
        self.assertIsNone(row["roc_8h"])

    def test_directional_streak_caps_at_twenty_and_zero_range_ratios_are_null(self) -> None:
        out = self._features(make_bars(timeframe="1h", count=25, step=0.001))
        self.assertEqual(out["directional_streak"][-1], 20)
        frame = make_bars(timeframe="1h", count=2)
        ts = frame["timestamp_utc"][1]
        frame = frame.with_columns(
            *[
                pl.when(pl.col("timestamp_utc") == ts).then(pl.lit(1.2)).otherwise(pl.col(col)).alias(col)
                for col in ("bid_open", "bid_high", "bid_low", "bid_close")
            ],
            *[
                pl.when(pl.col("timestamp_utc") == ts).then(pl.lit(1.20002)).otherwise(pl.col(col)).alias(col)
                for col in ("ask_open", "ask_high", "ask_low", "ask_close")
            ],
        )
        row = self._features(frame).row(-1, named=True)
        self.assertIsNone(row["body_to_range"])
        self.assertIsNone(row["close_location"])


if __name__ == "__main__":
    unittest.main()
