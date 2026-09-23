from __future__ import annotations

import unittest
from unittest.mock import patch

from fmp.market_learning.model_successor_result_record import (
    AGGREGATE_EVIDENCE_FINGERPRINT,
    AGGREGATE_MODEL_EVIDENCE_JOB_ID,
    AUTHORIZATION_PREFLIGHT_JOB_ID,
    EXPECTED_ARTIFACTS,
    LOGISTIC_NONCONVERGENCE_CELLS,
    MATRIX_JOB_IDS,
    REVIEWED_SUCCESSOR_MODEL_HEAD_SHA,
    REVIEWED_SUCCESSOR_MODEL_RUN_ID,
    SELECTED_CELL,
    SELECTED_CELL_RESULT_FINGERPRINT,
    SELECTED_CONFIDENCE_THRESHOLD,
    SELECTED_MODEL_FAMILY,
    SUCCESSOR_MODEL_RESULT_RECORD_DECISION,
    validate_reviewed_successor_model_result,
    validate_selected_successor_challenger,
)


def _run() -> dict[str, object]:
    return {
        "id": REVIEWED_SUCCESSOR_MODEL_RUN_ID,
        "name": "phase8a-exp045-model-training",
        "path": ".github/workflows/phase8a-exp045-model-training.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": REVIEWED_SUCCESSOR_MODEL_HEAD_SHA,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    ids = [
        AUTHORIZATION_PREFLIGHT_JOB_ID,
        *sorted(MATRIX_JOB_IDS),
        AGGREGATE_MODEL_EVIDENCE_JOB_ID,
    ]
    return {
        "jobs": [
            {
                "id": job_id,
                "status": "completed",
                "conclusion": "success",
                "name": (
                    "authorization-preflight"
                    if job_id == AUTHORIZATION_PREFLIGHT_JOB_ID
                    else (
                        "aggregate-model-evidence"
                        if job_id == AGGREGATE_MODEL_EVIDENCE_JOB_ID
                        else f"model-cells (synthetic-{job_id})"
                    )
                ),
            }
            for job_id in ids
        ]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": artifact_id,
                "name": name,
                "digest": digest,
                "expired": False,
            }
            for name, (artifact_id, digest) in EXPECTED_ARTIFACTS.items()
        ]
    }


def _aggregate() -> dict[str, object]:
    cells: list[dict[str, object]] = []
    all_cells = [
        (symbol, timeframe, horizon)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY")
        for timeframe in ("5m", "15m", "1h")
        for horizon in (60, 240)
    ]
    for identity in all_cells:
        selected = identity == SELECTED_CELL
        cells.append(
            {
                "symbol": identity[0],
                "timeframe": identity[1],
                "horizon_minutes": identity[2],
                "result_fingerprint": (
                    SELECTED_CELL_RESULT_FINGERPRINT
                    if selected
                    else "a" * 64
                ),
                "selection_status": (
                    "SELECTED"
                    if selected
                    else "NO_MODEL_CHALLENGER"
                ),
                "validation_status": (
                    "REJECT"
                    if selected
                    else "LOCKED_NO_SELECTION"
                ),
                "retrospective_holdout_status": (
                    "LOCKED_VALIDATION_REJECT"
                    if selected
                    else "LOCKED_NO_SELECTION"
                ),
                "logistic_fit_status": (
                    "FAILED_NON_CONVERGENCE"
                    if identity in LOGISTIC_NONCONVERGENCE_CELLS
                    else "FITTED"
                ),
                "hgb_fit_status": "FITTED",
            }
        )
    return {
        "evidence_fingerprint": AGGREGATE_EVIDENCE_FINGERPRINT,
        "cells": cells,
    }


def _selected_detail() -> dict[str, object]:
    return {
        "result_fingerprint": SELECTED_CELL_RESULT_FINGERPRINT,
        "cell": {
            "symbol": SELECTED_CELL[0],
            "timeframe": SELECTED_CELL[1],
            "horizon_minutes": SELECTED_CELL[2],
        },
        "selection": {
            "status": "SELECTED",
            "selected_variant": {
                "model_family": SELECTED_MODEL_FAMILY,
                "confidence_threshold": SELECTED_CONFIDENCE_THRESHOLD,
            },
            "variants": [
                {
                    "model_family": SELECTED_MODEL_FAMILY,
                    "confidence_threshold": SELECTED_CONFIDENCE_THRESHOLD,
                    "scenarios": {
                        "0.5": {
                            "gate": {"passed": True},
                            "metrics": {
                                "directional_candidate_count": 460,
                                "total_net_pips": 2353.6999999999875,
                            },
                        }
                    },
                }
            ],
        },
        "validation": {
            "status": "REJECT",
            "scenarios": {
                "0.5": {
                    "gate": {"passed": False},
                    "metrics": {
                        "directional_candidate_count": 83,
                        "total_net_pips": -1397.5000000000007,
                    },
                }
            },
        },
        "retrospective_holdout": {
            "status": "LOCKED_VALIDATION_REJECT"
        },
    }


class Exp045ReviewedResultRecordTests(unittest.TestCase):
    def test_selected_challenger_detail_is_exact(self) -> None:
        report = validate_selected_successor_challenger(
            _selected_detail()
        )
        self.assertTrue(report["selected_cell_verified"])
        self.assertEqual(
            report["selected_model_family"],
            SELECTED_MODEL_FAMILY,
        )
        self.assertEqual(
            report["selected_confidence_threshold"],
            SELECTED_CONFIDENCE_THRESHOLD,
        )
        self.assertEqual(
            report["validation_status"],
            "REJECT",
        )
        self.assertEqual(
            report["retrospective_holdout_status"],
            "LOCKED_VALIDATION_REJECT",
        )

    def test_reviewed_result_closes_without_candidate(self) -> None:
        frozen_review = {
            "stage": "SUCCESSOR_MODEL_RESULT_REVIEW_REQUIRED",
            "successor_model_result_evidence_fingerprint": (
                AGGREGATE_EVIDENCE_FINGERPRINT
            ),
            "verified_cell_count": 18,
            "selected_cell_count": 1,
            "no_model_challenger_count": 17,
            "no_model_family_available_count": 0,
            "validation_pass_count": 0,
            "retrospective_holdout_pass_count": 0,
            "logistic_nonconvergence_cell_count": 6,
            "prior_result_informed": True,
            "untouched_oos": False,
            "promotion_authorized": False,
            "shadow_authorized": False,
            "demo_order_authorized": False,
            "broker_mutation_authorized": False,
            "live_order_authorized": False,
            "real_money_authorized": False,
            "trading_authorized": False,
        }
        with patch(
            "fmp.market_learning.model_successor_result_record."
            "validate_successor_model_terminal_review",
            return_value=frozen_review,
        ):
            report = validate_reviewed_successor_model_result(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                aggregate_evidence=_aggregate(),
                selected_cell_evidence=_selected_detail(),
            )

        self.assertEqual(
            report["successor_model_result_record_decision"],
            SUCCESSOR_MODEL_RESULT_RECORD_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "SUCCESSOR_MODEL_RESULT_REVIEWED_NO_CANDIDATE",
        )
        self.assertEqual(report["selected_cell_count"], 1)
        self.assertEqual(report["validation_pass_count"], 0)
        self.assertEqual(
            report["retrospective_holdout_pass_count"],
            0,
        )
        self.assertFalse(
            report["replacement_model_run_authorized"]
        )
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_artifact_digest_drift_fails_closed(self) -> None:
        payload = _artifacts()
        payload["artifacts"][0]["digest"] = "sha256:" + "0" * 64
        with patch(
            "fmp.market_learning.model_successor_result_record."
            "validate_successor_model_terminal_review",
            return_value={},
        ):
            with self.assertRaisesRegex(
                ValueError,
                "artifact digest mismatch",
            ):
                validate_reviewed_successor_model_result(
                    run=_run(),
                    jobs_payload=_jobs(),
                    artifacts_payload=payload,
                    aggregate_evidence=_aggregate(),
                    selected_cell_evidence=_selected_detail(),
                )

    def test_nonconvergence_inventory_drift_fails_closed(self) -> None:
        aggregate = _aggregate()
        aggregate["cells"][0]["logistic_fit_status"] = "FITTED"
        frozen_review = {
            "stage": "SUCCESSOR_MODEL_RESULT_REVIEW_REQUIRED",
            "successor_model_result_evidence_fingerprint": (
                AGGREGATE_EVIDENCE_FINGERPRINT
            ),
            "verified_cell_count": 18,
            "selected_cell_count": 1,
            "no_model_challenger_count": 17,
            "no_model_family_available_count": 0,
            "validation_pass_count": 0,
            "retrospective_holdout_pass_count": 0,
            "logistic_nonconvergence_cell_count": 6,
        }
        with patch(
            "fmp.market_learning.model_successor_result_record."
            "validate_successor_model_terminal_review",
            return_value=frozen_review,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "non-convergence inventory mismatch",
            ):
                validate_reviewed_successor_model_result(
                    run=_run(),
                    jobs_payload=_jobs(),
                    artifacts_payload=_artifacts(),
                    aggregate_evidence=aggregate,
                    selected_cell_evidence=_selected_detail(),
                )


if __name__ == "__main__":
    unittest.main()
