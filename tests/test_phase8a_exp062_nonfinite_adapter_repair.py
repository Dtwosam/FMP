from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
import unittest

import polars as pl

from fmp.discovery.exp062_adapter_repair import (
    EXP062_EXPERIMENT_ID,
    adapt_market_learning_cell_exp062,
    exp062_adapter_repair_payload,
    normalize_nonfinite_continuous_features,
)
from fmp.discovery.market_learning_adapter import adapt_market_learning_cell
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES
from fmp.market_learning.contracts import (
    EVIDENCE_LABEL,
    MARKET_FEATURE_SET_VERSION,
)
from fmp.market_learning.outcomes import MARKET_OUTCOME_SET_VERSION


PROCESSED_SHA = "a" * 64


def _feature_row(
    *,
    available: datetime,
) -> dict[str, object]:
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


def _outcome_row(
    *,
    available: datetime,
    horizon: int = 60,
) -> dict[str, object]:
    return {
        "symbol": "EURUSD",
        "timeframe": "15m",
        "bar_start_utc": available - timedelta(minutes=15),
        "available_at_utc": available,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "processed_manifest_sha256": PROCESSED_SHA,
        "exit_timestamp_utc": available + timedelta(minutes=horizon),
        "horizon_minutes": horizon,
        "long_net_pips_0p5": 1.0,
        "short_net_pips_0p5": -1.0,
        "long_net_pips_1p0": 0.4,
        "short_net_pips_1p0": -1.6,
        "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
        "evidence_label": EVIDENCE_LABEL,
    }


class Exp062NonfiniteAdapterRepairTests(unittest.TestCase):
    def test_exact_exp061_nan_failure_is_normalized_to_none(self) -> None:
        available = datetime(2020, 6, 1, 12, 15, tzinfo=timezone.utc)
        row = _feature_row(available=available)
        row["realized_vol_1h"] = float("nan")
        row["realized_vol_8h"] = float("inf")
        row["realized_vol_24h"] = float("-inf")
        feature_frame = pl.DataFrame([row])
        outcome_frame = pl.DataFrame([_outcome_row(available=available)])

        with self.assertRaisesRegex(
            ValueError,
            "continuous feature realized_vol_1h must be finite or null",
        ):
            adapt_market_learning_cell(
                feature_frame=feature_frame,
                outcome_frame=outcome_frame,
                symbol="EURUSD",
                timeframe="15m",
            )

        repaired = adapt_market_learning_cell_exp062(
            feature_frame=feature_frame,
            outcome_frame=outcome_frame,
            symbol="EURUSD",
            timeframe="15m",
        )
        values = repaired.adapted.feature_observations[0].values
        self.assertIsNone(values["realized_vol_1h"])
        self.assertIsNone(values["realized_vol_8h"])
        self.assertIsNone(values["realized_vol_24h"])
        self.assertEqual(values["return_1h"], 1.0)

        counts = dict(repaired.normalized_nonfinite_counts)
        self.assertEqual(counts["realized_vol_1h"], 1)
        self.assertEqual(counts["realized_vol_8h"], 1)
        self.assertEqual(counts["realized_vol_24h"], 1)
        self.assertEqual(repaired.normalized_nonfinite_total, 3)

    def test_only_nonfinite_values_change(self) -> None:
        available = datetime(2020, 6, 1, 12, 15, tzinfo=timezone.utc)
        first = _feature_row(available=available)
        second = _feature_row(available=available + timedelta(minutes=15))
        first["realized_vol_1h"] = float("nan")
        second["realized_vol_1h"] = 2.5
        first["roc_4h"] = None
        frame = pl.DataFrame([first, second])

        normalized, counts = normalize_nonfinite_continuous_features(frame)
        values = normalized["realized_vol_1h"].to_list()
        self.assertIsNone(values[0])
        self.assertEqual(values[1], 2.5)
        self.assertIsNone(normalized["roc_4h"].to_list()[0])
        self.assertEqual(dict(counts)["realized_vol_1h"], 1)
        self.assertEqual(dict(counts)["roc_4h"], 0)

        for name in CONTINUOUS_FEATURES:
            for value in normalized[name].to_list():
                if value is not None:
                    self.assertTrue(math.isfinite(float(value)), name)

    def test_reserved_2023_boundary_remains_closed(self) -> None:
        available = datetime(2023, 1, 1, 0, 15, tzinfo=timezone.utc)
        row = _feature_row(available=available)
        row["realized_vol_1h"] = float("nan")
        with self.assertRaisesRegex(
            ValueError,
            "outside 2015-2022 input range",
        ):
            adapt_market_learning_cell_exp062(
                feature_frame=pl.DataFrame([row]),
                outcome_frame=pl.DataFrame([_outcome_row(available=available)]),
                symbol="EURUSD",
                timeframe="15m",
            )

    def test_source_identity_mismatch_remains_closed(self) -> None:
        available = datetime(2020, 6, 1, 12, 15, tzinfo=timezone.utc)
        feature = _feature_row(available=available)
        feature["realized_vol_8h"] = float("nan")
        outcome = _outcome_row(available=available)
        outcome["processed_manifest_sha256"] = "b" * 64

        with self.assertRaisesRegex(
            ValueError,
            "processed-manifest identity mismatch",
        ):
            adapt_market_learning_cell_exp062(
                feature_frame=pl.DataFrame([feature]),
                outcome_frame=pl.DataFrame([outcome]),
                symbol="EURUSD",
                timeframe="15m",
            )

    def test_missing_continuous_column_fails_closed(self) -> None:
        available = datetime(2020, 6, 1, 12, 15, tzinfo=timezone.utc)
        row = _feature_row(available=available)
        row.pop("realized_vol_8h")
        with self.assertRaisesRegex(
            ValueError,
            "missing continuous columns",
        ):
            normalize_nonfinite_continuous_features(pl.DataFrame([row]))

    def test_repair_payload_opens_no_execution_or_trading_path(self) -> None:
        payload = exp062_adapter_repair_payload()
        self.assertEqual(payload["experiment_id"], EXP062_EXPERIMENT_ID)
        self.assertTrue(payload["preserves_exp061_feature_calculations"])
        self.assertTrue(payload["preserves_exp061_windows"])
        self.assertTrue(payload["preserves_exp061_thresholds"])
        self.assertTrue(payload["preserves_exp061_cost_assumptions"])
        for field in (
            "historical_source_access_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(payload[field], field)


if __name__ == "__main__":
    unittest.main()
