from __future__ import annotations

import copy
from unittest.mock import patch
import unittest

from fmp.discovery.exp062_adapter_proof_result_decision import (
    AGGREGATE_ARTIFACT_DIGEST,
    AGGREGATE_ARTIFACT_ID,
    AGGREGATE_ARTIFACT_NAME,
    AGGREGATE_JSON_SHA256,
    CELL_ARTIFACT_BINDINGS,
    EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION,
    PROOF_HEAD_SHA,
    PROOF_RUN_ID,
    RAW_NONFINITE_BY_FEATURE,
    TOTAL_FEATURE_ROW_COUNT,
    TOTAL_OUTCOME_ROW_COUNT,
    TOTAL_RAW_NONFINITE_VALUE_COUNT,
    freeze_exp062_adapter_proof_result,
)


def _run() -> dict[str, object]:
    return {
        "id": PROOF_RUN_ID,
        "name": "phase8a-exp062-adapter-proof",
        "path": ".github/workflows/phase8a-exp062-adapter-proof.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _artifacts() -> dict[str, object]:
    rows = [
        {
            "id": artifact_id,
            "name": name,
            "digest": digest,
            "expired": False,
        }
        for _, _, artifact_id, name, digest, _ in CELL_ARTIFACT_BINDINGS
    ]
    rows.append(
        {
            "id": AGGREGATE_ARTIFACT_ID,
            "name": AGGREGATE_ARTIFACT_NAME,
            "digest": AGGREGATE_ARTIFACT_DIGEST,
            "expired": False,
        }
    )
    return {"artifacts": rows}


def _zip_hashes() -> dict[int, str]:
    value = {
        artifact_id: digest.removeprefix("sha256:")
        for _, _, artifact_id, _, digest, _ in CELL_ARTIFACT_BINDINGS
    }
    value[AGGREGATE_ARTIFACT_ID] = AGGREGATE_ARTIFACT_DIGEST.removeprefix(
        "sha256:"
    )
    return value


def _json_hashes() -> dict[int, str]:
    value = {
        artifact_id: raw_sha
        for _, _, artifact_id, _, _, raw_sha in CELL_ARTIFACT_BINDINGS
    }
    value[AGGREGATE_ARTIFACT_ID] = AGGREGATE_JSON_SHA256
    return value


def _terminal() -> dict[str, object]:
    return {
        "decision": "DEC-295",
        "version": "fmp-exp062-adapter-proof-review-contract-v1",
        "stage": "EXP062_ADAPTER_PROOF_SUCCESS_COMPLETE_REVIEW_REQUIRED",
        "proof_run_id": PROOF_RUN_ID,
        "proof_run_head_sha": PROOF_HEAD_SHA,
        "proof_run_conclusion": "success",
        "proof_run_attempt": 1,
        "proof_success_complete": True,
        "materialized_job_count": 10,
        "artifact_count": 10,
        "expected_success_job_count": 10,
        "expected_success_artifact_count": 10,
        "aggregate_content_review_required": True,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def _content() -> dict[str, object]:
    zeros = {
        "body_to_range": 0,
        "close_location": 0,
        "momentum_accel_4h": 0,
        "prev_asia_high_dist_pips": 0,
        "prev_asia_low_dist_pips": 0,
        "prev_fx_day_high_dist_pips": 0,
        "prev_fx_day_low_dist_pips": 0,
        "range_vs_prior_median_8h": 0,
        "realized_vol_1h": RAW_NONFINITE_BY_FEATURE["realized_vol_1h"],
        "realized_vol_24h": RAW_NONFINITE_BY_FEATURE["realized_vol_24h"],
        "realized_vol_8h": RAW_NONFINITE_BY_FEATURE["realized_vol_8h"],
        "return_1h": 0,
        "return_24h": 0,
        "roc_4h": 0,
        "roc_8h": 0,
        "sma_distance_2h_pips": 0,
        "sma_distance_8h_pips": 0,
        "sma_slope_2h_pips": 0,
        "sma_slope_8h_pips": 0,
        "spread_percentile_prior_24h": 0,
    }
    return {
        "decision": "DEC-296",
        "version": "fmp-exp062-adapter-proof-content-review-v1",
        "stage": "EXP062_ADAPTER_REPAIR_REAL_DATA_PROOF_VERIFIED",
        "proof_run_id": PROOF_RUN_ID,
        "proof_run_head_sha": PROOF_HEAD_SHA,
        "verified_cell_probe_count": 9,
        "aggregate_proof_verified": True,
        "all_nine_real_data_adapter_probes_successful": True,
        "total_feature_row_count": TOTAL_FEATURE_ROW_COUNT,
        "total_outcome_row_count": TOTAL_OUTCOME_ROW_COUNT,
        "total_raw_nonfinite_value_count": TOTAL_RAW_NONFINITE_VALUE_COUNT,
        "cells_with_raw_nonfinite_values": 9,
        "raw_nonfinite_by_feature": zeros,
        "cells": [],
        "repair_meaning": "NONFINITE_MISSING_VALUES_NORMALIZED_WITHOUT_MINING",
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


class Exp062AdapterProofResultFreezeTests(unittest.TestCase):
    def _freeze(
        self,
        *,
        artifacts: dict[str, object] | None = None,
        zip_hashes: dict[int, str] | None = None,
        json_hashes: dict[int, str] | None = None,
        content: dict[str, object] | None = None,
    ) -> dict[str, object]:
        with (
            patch(
                "fmp.discovery.exp062_adapter_proof_result_decision.classify_exp062_adapter_proof_terminal",
                return_value=_terminal(),
            ),
            patch(
                "fmp.discovery.exp062_adapter_proof_result_decision.review_exp062_adapter_proof_content",
                return_value=_content() if content is None else content,
            ),
        ):
            return freeze_exp062_adapter_proof_result(
                run=_run(),
                jobs_payload={"jobs": []},
                artifacts_payload=_artifacts() if artifacts is None else artifacts,
                cell_probes=[{} for _ in range(9)],
                aggregate_proof={},
                artifact_zip_sha256_by_id=(
                    _zip_hashes() if zip_hashes is None else zip_hashes
                ),
                artifact_json_sha256_by_id=(
                    _json_hashes() if json_hashes is None else json_hashes
                ),
            )

    def test_exact_proof_freezes_verified_repair(self) -> None:
        report = self._freeze()
        self.assertEqual(
            report["decision"],
            EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "EXP062_ADAPTER_REPAIR_PROOF_FROZEN_AND_VERIFIED",
        )
        self.assertEqual(report["proof_run_id"], PROOF_RUN_ID)
        self.assertEqual(report["proof_job_count"], 10)
        self.assertEqual(report["proof_artifact_count"], 10)
        self.assertEqual(report["verified_cell_probe_count"], 9)
        self.assertEqual(
            report["total_raw_nonfinite_value_count"],
            TOTAL_RAW_NONFINITE_VALUE_COUNT,
        )
        self.assertEqual(
            report["raw_nonfinite_by_feature"],
            RAW_NONFINITE_BY_FEATURE,
        )
        self.assertTrue(report["repair_verified_on_real_accepted_data"])
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
            self.assertFalse(report[field], field)

    def test_artifact_identity_drift_is_rejected(self) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows[0]["id"] = 999
        with self.assertRaisesRegex(ValueError, "unexpected artifact id"):
            self._freeze(artifacts=artifacts)

    def test_zip_hash_drift_is_rejected(self) -> None:
        hashes = _zip_hashes()
        artifact_id = CELL_ARTIFACT_BINDINGS[0][2]
        hashes[artifact_id] = "0" * 64
        with self.assertRaisesRegex(ValueError, "ZIP sha256 mismatch"):
            self._freeze(zip_hashes=hashes)

    def test_json_hash_drift_is_rejected(self) -> None:
        hashes = _json_hashes()
        hashes[AGGREGATE_ARTIFACT_ID] = "0" * 64
        with self.assertRaisesRegex(ValueError, "JSON sha256 mismatch"):
            self._freeze(json_hashes=hashes)

    def test_content_count_drift_is_rejected(self) -> None:
        content = _content()
        content["total_raw_nonfinite_value_count"] = (
            TOTAL_RAW_NONFINITE_VALUE_COUNT + 1
        )
        with self.assertRaisesRegex(
            ValueError,
            "total_raw_nonfinite_value_count mismatch",
        ):
            self._freeze(content=content)

    def test_nonfinite_feature_totals_must_match_exact_real_proof(self) -> None:
        content = _content()
        counts = copy.deepcopy(content["raw_nonfinite_by_feature"])
        assert isinstance(counts, dict)
        counts["realized_vol_8h"] += 1
        content["raw_nonfinite_by_feature"] = counts
        with self.assertRaisesRegex(
            ValueError,
            "non-finite feature totals mismatch",
        ):
            self._freeze(content=content)


if __name__ == "__main__":
    unittest.main()
