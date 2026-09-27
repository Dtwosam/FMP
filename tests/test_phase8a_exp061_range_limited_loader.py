from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from fmp.discovery.range_limited_loader import (
    EXP061_SELECTED_MONTH_COUNT,
    EXP061_SELECTED_MONTHS,
    _artifact_map,
    _canonical_json,
    _expected_paths,
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


class Exp061RangeLimitedLoaderTests(unittest.TestCase):
    def test_selected_months_are_exactly_2015_through_2022(self) -> None:
        self.assertEqual(EXP061_SELECTED_MONTH_COUNT, 96)
        self.assertEqual(len(EXP061_SELECTED_MONTHS), 96)
        self.assertEqual(EXP061_SELECTED_MONTHS[0], "2015-01")
        self.assertEqual(EXP061_SELECTED_MONTHS[-1], "2022-12")
        self.assertFalse(any(month.startswith("2023-") for month in EXP061_SELECTED_MONTHS))

        paths = _expected_paths(prefix="root/")
        self.assertEqual(len(paths), 96)
        self.assertEqual(paths[0], "root/2015/01.parquet")
        self.assertEqual(paths[-1], "root/2022/12.parquet")
        self.assertFalse(any("/2023/" in path for path in paths))

    def test_artifact_manifest_selection_is_exact_and_deterministic(self) -> None:
        prefix = (
            "data/features/fmp-market-feature-v1/"
            "EURUSD/15m/"
        )
        paths = _expected_paths(prefix=prefix)
        manifest = {"artifacts": [_artifact(path) for path in paths]}
        mapped = _artifact_map(
            manifest,
            expected_prefix=prefix,
            label="test feature",
        )
        self.assertEqual(tuple(mapped), paths)

        duplicate = {"artifacts": [_artifact(paths[0]), _artifact(paths[0])]}
        with self.assertRaisesRegex(ValueError, "duplicated"):
            _artifact_map(
                duplicate,
                expected_prefix=prefix,
                label="test feature",
            )

    def test_upstream_evidence_fingerprint_is_recomputed(self) -> None:
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
            relative = "data/features/fmp-market-feature-v1/EURUSD/15m/2015/01.parquet"
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
                    label="EXP-061 feature",
                )

    def test_loader_contract_keeps_execution_and_trading_locked(self) -> None:
        payload = loader_contract_payload()
        self.assertEqual(payload["selected_month_count"], 96)
        self.assertFalse(payload["reads_2023_or_later_partitions"])
        self.assertTrue(payload["filters_targets_reaching_2023_before_adapter"])
        for field in (
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
