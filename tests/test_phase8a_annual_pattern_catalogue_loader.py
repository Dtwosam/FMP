from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from fmp.discovery.annual_pattern_catalogue_loader import (
    FULL_HISTORY_SELECTED_MONTH_COUNT,
    FULL_HISTORY_SELECTED_MONTHS,
    _artifact_map,
    _canonical_json,
    _expected_paths,
    _segment_bounds,
    _segment_months,
    _validate_evidence_mapping,
    _verify_selected_artifact,
    loader_contract_payload,
)
from fmp.market_learning.contracts import (
    EVIDENCE_LABEL,
    EXPERIMENT_ID,
    MARKET_FEATURE_SET_VERSION,
)


def _evidence(*, complete_field: str) -> dict[str, object]:
    value: dict[str, object] = {
        "experiment_id": EXPERIMENT_ID,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        complete_field: True,
        "model_fit_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "cells": [],
    }
    value["evidence_fingerprint"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


def _artifact(relative: str) -> dict[str, object]:
    return {
        "path": relative,
        "sha256": "a" * 64,
        "size_bytes": 1,
        "row_count": 1,
    }


class AnnualPatternCatalogueFullHistoryLoaderTests(unittest.TestCase):
    def test_full_history_months_are_exactly_2015_01_through_2026_08(self) -> None:
        self.assertEqual(FULL_HISTORY_SELECTED_MONTH_COUNT, 140)
        self.assertEqual(len(FULL_HISTORY_SELECTED_MONTHS), 140)
        self.assertEqual(FULL_HISTORY_SELECTED_MONTHS[0], "2015-01")
        self.assertEqual(FULL_HISTORY_SELECTED_MONTHS[-1], "2026-08")
        self.assertIn("2023-01", FULL_HISTORY_SELECTED_MONTHS)
        self.assertNotIn("2026-09", FULL_HISTORY_SELECTED_MONTHS)

    def test_segment_months_and_bounds_are_exact_and_isolated(self) -> None:
        self.assertEqual(
            _segment_months("2015"),
            tuple(f"2015-{month:02d}" for month in range(1, 13)),
        )
        self.assertEqual(
            _segment_months("2026_YTD_TO_2026_08_20"),
            tuple(f"2026-{month:02d}" for month in range(1, 9)),
        )
        start, end = _segment_bounds("2026_YTD_TO_2026_08_20")
        self.assertEqual(start.isoformat(), "2026-01-01T00:00:00+00:00")
        self.assertEqual(end.isoformat(), "2026-08-21T00:00:00+00:00")
        with self.assertRaisesRegex(ValueError, "segment label drift"):
            _segment_months("2027")

    def test_expected_paths_follow_only_requested_annual_segment(self) -> None:
        prefix = "data/features/fmp-market-feature-v1/EURUSD/15m/"
        paths_2015 = _expected_paths(prefix=prefix, months=_segment_months("2015"))
        paths_2026 = _expected_paths(
            prefix=prefix,
            months=_segment_months("2026_YTD_TO_2026_08_20"),
        )
        self.assertEqual(len(paths_2015), 12)
        self.assertEqual(paths_2015[0], prefix + "2015/01.parquet")
        self.assertEqual(paths_2015[-1], prefix + "2015/12.parquet")
        self.assertEqual(len(paths_2026), 8)
        self.assertEqual(paths_2026[-1], prefix + "2026/08.parquet")

    def test_artifact_manifest_selection_is_exact_and_duplicate_safe(self) -> None:
        prefix = "data/features/fmp-market-feature-v1/EURUSD/15m/"
        paths = _expected_paths(prefix=prefix, months=_segment_months("2015"))
        manifest = {"artifacts": [_artifact(path) for path in paths]}
        mapped = _artifact_map(
            manifest,
            expected_prefix=prefix,
            label="DEC-473 feature manifest",
        )
        self.assertEqual(tuple(mapped), paths)

        duplicate = {"artifacts": [_artifact(paths[0]), _artifact(paths[0])]}
        with self.assertRaisesRegex(ValueError, "duplicated"):
            _artifact_map(
                duplicate,
                expected_prefix=prefix,
                label="DEC-473 feature manifest",
            )

    def test_upstream_exp044_evidence_fingerprint_is_recomputed(self) -> None:
        evidence = _evidence(complete_field="feature_evidence_complete")
        fingerprint = evidence["evidence_fingerprint"]
        self.assertEqual(
            _validate_evidence_mapping(
                evidence,
                label="EXP-044 feature",
                complete_field="feature_evidence_complete",
            ),
            fingerprint,
        )

        tampered = dict(evidence)
        tampered["shadow_authorized"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            _validate_evidence_mapping(
                tampered,
                label="EXP-044 feature",
                complete_field="feature_evidence_complete",
            )

    def test_selected_artifact_checksum_is_verified_before_schema_read(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            relative = (
                "data/features/fmp-market-feature-v1/"
                "EURUSD/15m/2015/01.parquet"
            )
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"x")
            raw = {
                "path": relative,
                "sha256": hashlib.sha256(b"y").hexdigest(),
                "size_bytes": 1,
                "row_count": 1,
            }
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                _verify_selected_artifact(
                    root=root,
                    relative=relative,
                    raw=raw,
                    expected_schema=("irrelevant",),
                    label="DEC-473 feature",
                )

    def test_loader_contract_binds_full_collection_but_keeps_authority_locked(self) -> None:
        payload = loader_contract_payload()
        self.assertEqual(payload["decision"], "DEC-473")
        self.assertEqual(payload["source_evidence_decision"], "DEC-472")
        self.assertEqual(payload["selected_month_count"], 140)
        self.assertEqual(payload["annual_segment_count"], 12)
        self.assertEqual(payload["annual_segments"][0], "2015")
        self.assertEqual(
            payload["annual_segments"][-1],
            "2026_YTD_TO_2026_08_20",
        )
        self.assertTrue(payload["loads_one_annual_segment_at_a_time"])
        self.assertTrue(payload["filters_outcomes_crossing_annual_boundary"])
        self.assertTrue(payload["reuses_exp044_materialized_features"])
        self.assertTrue(payload["reuses_exp044_materialized_outcomes"])
        self.assertEqual(
            payload["next_gate"],
            "ANNUAL_PATTERN_CATALOGUE_FULL_HISTORY_LOADER_EXECUTION_AUTHORIZATION",
        )
        for field in (
            "new_data_acquisition_authorized",
            "new_feature_materialization_authorized",
            "new_outcome_materialization_authorized",
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
