from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from fmp.data.phase2.artifacts import PHASE1_FROZEN_PLAN_SHA256, PHASE1_SOURCE_CHECKPOINT
from fmp.features.contracts import PROCESSED_SCHEMA_VERSION
from fmp.market_learning.evidence import EXPECTED_CELLS, EXPECTED_SOURCE_MANIFEST_SHA256
from fmp.market_learning.outcomes import MARKET_OUTCOME_SET_VERSION
from fmp.market_learning.readiness import (
    READINESS_VERSION,
    build_training_readiness,
    compile_training_readiness,
)


FEATURE_COMMIT = "a" * 40
OUTCOME_COMMIT = "b" * 40


def _canonical_fingerprint(value: dict[str, object]) -> str:
    payload = (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _feature_evidence() -> dict[str, object]:
    cells: list[dict[str, object]] = []
    for index, (symbol, timeframe) in enumerate(EXPECTED_CELLS, start=1):
        cells.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "manifest_sha256": f"{index:064x}",
                "processed_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256[symbol],
                "row_count": 100 + index,
                "artifact_count": 140,
                "output_start_utc": "2015-01-01T00:05:00Z",
                "output_end_utc": "2026-08-20T23:55:00Z",
            }
        )
    evidence: dict[str, object] = {
        "evidence_version": 1,
        "experiment_id": "EXP-20260923-044",
        "feature_set_version": "fmp-market-feature-v1",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "code_commit": FEATURE_COMMIT,
        "historical_source": {
            "provider": "Dukascopy",
            "reuse_existing_accepted_history": True,
            "new_acquisition_performed": False,
            "phase1_checkpoint": PHASE1_SOURCE_CHECKPOINT,
            "phase1_frozen_plan_sha256": PHASE1_FROZEN_PLAN_SHA256,
            "phase2_schema_version": PROCESSED_SCHEMA_VERSION,
            "processed_manifest_sha256_by_symbol": dict(
                sorted(EXPECTED_SOURCE_MANIFEST_SHA256.items())
            ),
        },
        "expected_cell_count": 9,
        "verified_cell_count": 9,
        "feature_evidence_complete": True,
        "model_fit_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "cells": cells,
    }
    evidence["evidence_fingerprint"] = _canonical_fingerprint(evidence)
    return evidence


def _outcome_evidence(feature: dict[str, object]) -> dict[str, object]:
    feature_cells = {
        (cell["symbol"], cell["timeframe"]): cell
        for cell in feature["cells"]
    }
    cells: list[dict[str, object]] = []
    for index, identity in enumerate(EXPECTED_CELLS, start=1):
        symbol, timeframe = identity
        source = feature_cells[identity]
        cells.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "manifest_sha256": f"{100 + index:064x}",
                "feature_manifest_sha256": source["manifest_sha256"],
                "processed_manifest_sha256": source["processed_manifest_sha256"],
                "source_feature_rows": source["row_count"],
                "labeled_rows": 2 * int(source["row_count"]) - 1,
                "artifact_count": 140,
                "output_start_utc": "2015-01-01T00:05:00Z",
                "output_end_utc": "2026-08-20T23:59:00Z",
            }
        )
    evidence: dict[str, object] = {
        "evidence_version": 1,
        "experiment_id": "EXP-20260923-044",
        "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
        "feature_set_version": "fmp-market-feature-v1",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "code_commit": OUTCOME_COMMIT,
        "feature_evidence_fingerprint": feature["evidence_fingerprint"],
        "expected_cell_count": 9,
        "verified_cell_count": 9,
        "outcome_evidence_complete": True,
        "model_fit_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "cells": cells,
    }
    evidence["evidence_fingerprint"] = _canonical_fingerprint(evidence)
    return evidence


class MarketLearningReadinessTests(unittest.TestCase):
    def test_matching_evidence_opens_protocol_source_only(self) -> None:
        feature = _feature_evidence()
        outcome = _outcome_evidence(feature)
        first = build_training_readiness(
            feature_evidence=feature,
            outcome_evidence=outcome,
        )
        second = build_training_readiness(
            feature_evidence=feature,
            outcome_evidence=outcome,
        )

        self.assertEqual(first, second)
        self.assertEqual(first["readiness_version"], READINESS_VERSION)
        self.assertTrue(first["data_preparation_complete"])
        self.assertTrue(first["model_protocol_source_open_authorized"])
        self.assertFalse(first["model_protocol_result_authorized"])
        self.assertFalse(first["model_fit_authorized"])
        self.assertFalse(first["promotion_authorized"])
        self.assertFalse(first["shadow_authorized"])
        self.assertFalse(first["demo_order_authorized"])
        self.assertFalse(first["broker_mutation_authorized"])
        self.assertFalse(first["live_order_authorized"])
        self.assertFalse(first["real_money_authorized"])
        self.assertEqual(first["verified_cell_count"], 9)
        self.assertEqual(len(first["readiness_fingerprint"]), 64)

    def test_mismatched_feature_fingerprint_fails_closed(self) -> None:
        feature = _feature_evidence()
        outcome = _outcome_evidence(feature)
        outcome["feature_evidence_fingerprint"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "does not bind"):
            build_training_readiness(
                feature_evidence=feature,
                outcome_evidence=outcome,
            )

    def test_mismatched_feature_manifest_fails_closed(self) -> None:
        feature = _feature_evidence()
        outcome = _outcome_evidence(feature)
        outcome["cells"][0]["feature_manifest_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "does not bind feature manifest"):
            build_training_readiness(
                feature_evidence=feature,
                outcome_evidence=outcome,
            )

    def test_any_model_fit_authorization_fails_closed(self) -> None:
        feature = _feature_evidence()
        outcome = _outcome_evidence(feature)
        outcome["model_fit_authorized"] = True
        with self.assertRaisesRegex(ValueError, "model_fit_authorized"):
            build_training_readiness(
                feature_evidence=feature,
                outcome_evidence=outcome,
            )

    def test_persisted_evidence_is_revalidated_before_readiness(self) -> None:
        feature = _feature_evidence()
        outcome = _outcome_evidence(feature)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_path = root / "feature-evidence.json"
            outcome_path = root / "outcome-evidence.json"
            feature_path.write_text(
                json.dumps(feature, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            outcome_path.write_text(
                json.dumps(outcome, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            readiness = compile_training_readiness(
                feature_evidence_path=feature_path,
                outcome_evidence_path=outcome_path,
            )
            self.assertTrue(readiness["data_preparation_complete"])

            tampered = json.loads(outcome_path.read_text(encoding="utf-8"))
            tampered["verified_cell_count"] = 8
            outcome_path.write_text(
                json.dumps(tampered, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                compile_training_readiness(
                    feature_evidence_path=feature_path,
                    outcome_evidence_path=outcome_path,
                )


if __name__ == "__main__":
    unittest.main()
