from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
import unittest

import polars as pl

from fmp.discovery.exp062_nonfinite_feature_adapter import (
    EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION,
    EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION,
    adapt_feature_frame,
)
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES
from fmp.market_learning.contracts import MARKET_FEATURE_SET_VERSION


PROCESSED_SHA = "a" * 64


def _row() -> dict[str, object]:
    available = datetime(2020, 6, 1, 12, 15, tzinfo=timezone.utc)
    row: dict[str, object] = {
        "symbol": "EURUSD",
        "timeframe": "15m",
        "bar_start_utc": available - timedelta(minutes=15),
        "available_at_utc": available,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "processed_manifest_sha256": PROCESSED_SHA,
        "is_london_new_york_overlap": False,
        "is_london_session": True,
        "is_new_york_session": False,
        "is_asia_session": False,
    }
    for name in CONTINUOUS_FEATURES:
        row[name] = 1.0
    return row


class Exp062NonfiniteFeatureNormalizationTests(unittest.TestCase):
    def test_repair_identity_is_separate_from_exp061_result(self) -> None:
        self.assertEqual(
            EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION,
            "DEC-293",
        )
        self.assertEqual(
            EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION,
            "fmp-exp062-nonfinite-feature-normalization-v1",
        )

    def test_nan_and_infinities_become_null_missing_features(self) -> None:
        row = _row()
        row["realized_vol_1h"] = float("nan")
        row["realized_vol_8h"] = float("inf")
        row["realized_vol_24h"] = float("-inf")

        observations, processed = adapt_feature_frame(
            pl.DataFrame([row]),
            symbol="EURUSD",
            timeframe="15m",
        )

        self.assertEqual(processed, PROCESSED_SHA)
        self.assertEqual(len(observations), 1)
        values = observations[0].values
        self.assertIsNone(values["realized_vol_1h"])
        self.assertIsNone(values["realized_vol_8h"])
        self.assertIsNone(values["realized_vol_24h"])

    def test_existing_null_and_finite_values_are_preserved(self) -> None:
        row = _row()
        row["realized_vol_1h"] = None
        row["return_1h"] = -0.0125
        row["sma_distance_2h_pips"] = 0.0

        observations, _ = adapt_feature_frame(
            pl.DataFrame([row]),
            symbol="EURUSD",
            timeframe="15m",
        )
        values = observations[0].values

        self.assertIsNone(values["realized_vol_1h"])
        self.assertEqual(values["return_1h"], -0.0125)
        self.assertEqual(values["sma_distance_2h_pips"], 0.0)
        self.assertTrue(math.isfinite(float(values["return_1h"])))

    def test_session_flags_are_not_coerced_or_normalized(self) -> None:
        row = _row()
        row["is_london_session"] = 1

        with self.assertRaisesRegex(
            ValueError,
            "session flag is_london_session must be boolean",
        ):
            adapt_feature_frame(
                pl.DataFrame([row]),
                symbol="EURUSD",
                timeframe="15m",
            )

    def test_invalid_non_numeric_continuous_value_still_fails_closed(self) -> None:
        row = _row()
        row["realized_vol_8h"] = "not-a-number"

        with self.assertRaisesRegex(
            ValueError,
            "continuous feature realized_vol_8h must be finite or null",
        ):
            adapt_feature_frame(
                pl.DataFrame([row]),
                symbol="EURUSD",
                timeframe="15m",
            )

    def test_repair_changes_only_nonfinite_continuous_values(self) -> None:
        row = _row()
        row["realized_vol_8h"] = float("nan")
        row["is_london_session"] = True

        observations, _ = adapt_feature_frame(
            pl.DataFrame([row]),
            symbol="EURUSD",
            timeframe="15m",
        )
        values = observations[0].values

        self.assertIsNone(values["realized_vol_8h"])
        self.assertIs(values["is_london_session"], True)
        for name in CONTINUOUS_FEATURES:
            if name != "realized_vol_8h":
                self.assertEqual(values[name], 1.0)


if __name__ == "__main__":
    unittest.main()
