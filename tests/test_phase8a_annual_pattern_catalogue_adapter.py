from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
import unittest

import polars as pl

from fmp.discovery.annual_pattern_catalogue_adapter import (
    adapt_verified_annual_catalogue_segment,
    adapter_contract_payload,
)
from fmp.discovery.annual_pattern_catalogue_loader import (
    VerifiedAnnualCatalogueSegmentFrames,
)
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES
from fmp.market_learning.contracts import (
    EVIDENCE_LABEL,
    MARKET_FEATURE_SET_VERSION,
)
from fmp.market_learning.outcomes import MARKET_OUTCOME_SET_VERSION


_PROCESSED = "a" * 64
_FEATURE_MANIFEST = "b" * 64
_OUTCOME_MANIFEST = "c" * 64
_FEATURE_EVIDENCE = "d" * 64
_OUTCOME_EVIDENCE = "e" * 64
_SESSION_FLAGS = (
    "is_london_new_york_overlap",
    "is_london_session",
    "is_new_york_session",
    "is_asia_session",
)


def _feature_row(
    available: datetime,
    *,
    processed: str = _PROCESSED,
    nonfinite_feature: str | None = None,
) -> dict[str, object]:
    row: dict[str, object] = {
        "symbol": "EURUSD",
        "timeframe": "5m",
        "bar_start_utc": available - timedelta(minutes=5),
        "available_at_utc": available,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "processed_manifest_sha256": processed,
    }
    row.update({name: 0.0 for name in CONTINUOUS_FEATURES})
    if nonfinite_feature is not None:
        row[nonfinite_feature] = math.nan
    row.update({name: False for name in _SESSION_FLAGS})
    return row


def _outcome_row(
    available: datetime,
    *,
    horizon: int = 60,
    processed: str = _PROCESSED,
) -> dict[str, object]:
    return {
        "symbol": "EURUSD",
        "timeframe": "5m",
        "bar_start_utc": available - timedelta(minutes=5),
        "available_at_utc": available,
        "exit_timestamp_utc": available + timedelta(minutes=horizon),
        "horizon_minutes": horizon,
        "long_net_pips_0p5": 1.0,
        "short_net_pips_0p5": -1.0,
        "long_net_pips_1p0": 0.5,
        "short_net_pips_1p0": -1.5,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "processed_manifest_sha256": processed,
    }


def _bundle(
    *,
    segment: str = "2023",
    feature_rows: list[dict[str, object]] | None = None,
    outcome_rows: list[dict[str, object]] | None = None,
) -> VerifiedAnnualCatalogueSegmentFrames:
    available = datetime(2023, 1, 1, 0, 5, tzinfo=timezone.utc)
    return VerifiedAnnualCatalogueSegmentFrames(
        annual_segment_label=segment,
        symbol="EURUSD",
        timeframe="5m",
        feature_frame=pl.DataFrame(
            feature_rows if feature_rows is not None else [_feature_row(available)]
        ),
        outcome_frame=pl.DataFrame(
            outcome_rows if outcome_rows is not None else [_outcome_row(available)]
        ),
        processed_manifest_sha256=_PROCESSED,
        feature_manifest_sha256=_FEATURE_MANIFEST,
        outcome_manifest_sha256=_OUTCOME_MANIFEST,
        feature_evidence_fingerprint=_FEATURE_EVIDENCE,
        outcome_evidence_fingerprint=_OUTCOME_EVIDENCE,
        selected_feature_artifacts=("data/features/2023/01.parquet",),
        selected_outcome_artifacts=("data/outcomes/2023/01.parquet",),
    )


class AnnualPatternCatalogueSegmentAdapterTests(unittest.TestCase):
    def test_2023_verified_segment_adapts_without_exp061_range_limit(self) -> None:
        adapted = adapt_verified_annual_catalogue_segment(_bundle())

        self.assertEqual(adapted.annual_segment_label, "2023")
        self.assertEqual(adapted.symbol, "EURUSD")
        self.assertEqual(adapted.timeframe, "5m")
        self.assertEqual(len(adapted.feature_observations), 1)
        self.assertEqual(len(adapted.outcome_observations), 1)
        self.assertEqual(
            adapted.feature_observations[0].observation_id,
            adapted.outcome_observations[0].observation_id,
        )
        self.assertEqual(adapted.processed_manifest_sha256, _PROCESSED)
        self.assertEqual(adapted.feature_manifest_sha256, _FEATURE_MANIFEST)
        self.assertEqual(adapted.outcome_manifest_sha256, _OUTCOME_MANIFEST)
        self.assertEqual(adapted.feature_evidence_fingerprint, _FEATURE_EVIDENCE)
        self.assertEqual(adapted.outcome_evidence_fingerprint, _OUTCOME_EVIDENCE)

    def test_nonfinite_continuous_feature_is_normalized_to_null(self) -> None:
        available = datetime(2023, 1, 1, 0, 5, tzinfo=timezone.utc)
        feature_name = CONTINUOUS_FEATURES[0]
        bundle = _bundle(
            feature_rows=[
                _feature_row(
                    available,
                    nonfinite_feature=feature_name,
                )
            ]
        )

        adapted = adapt_verified_annual_catalogue_segment(bundle)

        self.assertIsNone(adapted.feature_observations[0].values[feature_name])

    def test_outcome_crossing_annual_boundary_fails_closed(self) -> None:
        available = datetime(2023, 12, 31, 23, 5, tzinfo=timezone.utc)
        bundle = _bundle(
            feature_rows=[_feature_row(available)],
            outcome_rows=[_outcome_row(available, horizon=60)],
        )

        with self.assertRaisesRegex(
            ValueError,
            "outcome exit crossed annual segment boundary",
        ):
            adapt_verified_annual_catalogue_segment(bundle)

    def test_feature_outside_annual_segment_fails_closed(self) -> None:
        available = datetime(2024, 1, 1, 0, 5, tzinfo=timezone.utc)
        bundle = _bundle(
            segment="2023",
            feature_rows=[_feature_row(available)],
            outcome_rows=[_outcome_row(available)],
        )

        with self.assertRaisesRegex(ValueError, "feature row escaped annual segment"):
            adapt_verified_annual_catalogue_segment(bundle)

    def test_processed_manifest_drift_fails_closed(self) -> None:
        available = datetime(2023, 1, 1, 0, 5, tzinfo=timezone.utc)
        bundle = _bundle(
            feature_rows=[_feature_row(available, processed="f" * 64)],
        )

        with self.assertRaisesRegex(
            ValueError,
            "processed-manifest identity mismatch",
        ):
            adapt_verified_annual_catalogue_segment(bundle)

    def test_duplicate_feature_identity_fails_closed(self) -> None:
        available = datetime(2023, 1, 1, 0, 5, tzinfo=timezone.utc)
        row = _feature_row(available)
        bundle = _bundle(feature_rows=[row, dict(row)])

        with self.assertRaisesRegex(
            ValueError,
            "duplicate DEC-474 feature-frame identity",
        ):
            adapt_verified_annual_catalogue_segment(bundle)

    def test_outcome_without_matching_feature_fails_closed(self) -> None:
        feature_available = datetime(2023, 1, 1, 0, 5, tzinfo=timezone.utc)
        outcome_available = datetime(2023, 1, 1, 0, 10, tzinfo=timezone.utc)
        bundle = _bundle(
            feature_rows=[_feature_row(feature_available)],
            outcome_rows=[_outcome_row(outcome_available)],
        )

        with self.assertRaisesRegex(
            ValueError,
            "adapted outcome has no matching feature observation",
        ):
            adapt_verified_annual_catalogue_segment(bundle)

    def test_2026_partial_segment_accepts_rows_only_through_august_20(self) -> None:
        available = datetime(2026, 8, 20, 22, 5, tzinfo=timezone.utc)
        bundle = _bundle(
            segment="2026_YTD_TO_2026_08_20",
            feature_rows=[_feature_row(available)],
            outcome_rows=[_outcome_row(available)],
        )

        adapted = adapt_verified_annual_catalogue_segment(bundle)

        self.assertEqual(
            adapted.annual_segment_label,
            "2026_YTD_TO_2026_08_20",
        )
        self.assertEqual(len(adapted.outcome_observations), 1)

    def test_contract_is_source_only_and_keeps_all_downstream_authority_false(self) -> None:
        payload = adapter_contract_payload()

        self.assertEqual(payload["decision"], "DEC-474")
        self.assertEqual(payload["source_loader_decision"], "DEC-473")
        self.assertEqual(
            payload["source_loader_merge_sha"],
            "f3fd12018ff9602dbc233b0b5c99bf6764489ea8",
        )
        self.assertTrue(payload["accepts_verified_loader_bundle_only"])
        self.assertTrue(payload["preserves_manifest_and_evidence_identities"])
        self.assertTrue(payload["normalizes_nonfinite_continuous_features_to_null"])
        self.assertTrue(payload["enforces_annual_segment_boundaries"])
        self.assertEqual(
            payload["next_gate"],
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_RUNTIME_WIRING",
        )
        for field in (
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
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
