from __future__ import annotations

from typing import Mapping

from .model_successor_fit_temporal_residual_regime_balance_utility_result_review import (
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_REVIEW_DECISION,
    validate_fit_temporal_residual_regime_balance_utility_model_terminal_review,
)


FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_DECISION = "DEC-251"

DEC250_MERGED_COMMIT = "8b47a025598feea1b9a382c4f0c35ac644512acc"
DEC246_REVIEW_BLOB_SHA = "5adc6ad72b2dfab1de1cca09a9bb2bc09663bfc5"

REVIEWED_MODEL_RUN_ID = 36239443323
REVIEWED_MODEL_HEAD_SHA = "8b47a025598feea1b9a382c4f0c35ac644512acc"
REVIEWED_MODEL_RUN_ATTEMPT = 1
REVIEWED_MODEL_RUN_CONCLUSION = "failure"

REVIEWED_AUTHORIZATION_PREFLIGHT_JOB_ID = 108397079850
REVIEWED_AGGREGATE_JOB_ID = 108399322051
REVIEWED_MATRIX_JOB_IDS = (
    108397160370,
    108397160381,
    108397160382,
    108397160383,
    108397160396,
    108397160412,
    108397160414,
    108397160415,
    108397160448,
)

INTERMEDIATE_PREDECESSOR_MODULE = (
    "fmp.market_learning."
    "model_successor_fit_temporal_residual_lower_tail_utility_repair_training"
)
MISSING_BREADTH_RULE_EXPORT = "FIT_TEMPORAL_RESIDUAL_BREADTH_RULE"
SUGGESTED_LOWER_TAIL_EXPORT = "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_RULE"

EXPECTED_MATRIX_FAILURE_SIGNATURE = (
    "AttributeError: module "
    f"'{INTERMEDIATE_PREDECESSOR_MODULE}' "
    f"has no attribute '{MISSING_BREADTH_RULE_EXPORT}'. "
    f"Did you mean: '{SUGGESTED_LOWER_TAIL_EXPORT}'?"
)

FAILURE_CLASSIFICATION = (
    "IMPLEMENTATION_DEPENDENCY_EXPORT_DEPTH_DRIFT_PREVENTED_ALL_EXP059_CELL_RESULTS"
)

MODEL_RUN_DISPATCH_AUTHORIZED = False
REPLACEMENT_MODEL_RUN_AUTHORIZED = False
AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED = False
MODEL_PROTOCOL_RESULT_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _validate_failure_signatures(
    failure_signatures: Mapping[int, str],
) -> int:
    if set(failure_signatures) != set(REVIEWED_MATRIX_JOB_IDS):
        raise ValueError("DEC-251 matrix failure job inventory mismatch")
    for job_id in REVIEWED_MATRIX_JOB_IDS:
        value = failure_signatures.get(job_id)
        if value != EXPECTED_MATRIX_FAILURE_SIGNATURE:
            raise ValueError(
                f"DEC-251 failure signature mismatch for job {job_id}"
            )
    return len(REVIEWED_MATRIX_JOB_IDS)


def validate_reviewed_fit_temporal_residual_regime_balance_utility_failed_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    failure_signatures: Mapping[int, str],
) -> dict[str, object]:
    if run.get("id") != REVIEWED_MODEL_RUN_ID:
        raise ValueError("DEC-251 reviewed model run id mismatch")
    if run.get("head_sha") != REVIEWED_MODEL_HEAD_SHA:
        raise ValueError("DEC-251 reviewed model head SHA mismatch")
    if run.get("run_attempt") != REVIEWED_MODEL_RUN_ATTEMPT:
        raise ValueError("DEC-251 reviewed model run attempt mismatch")
    if run.get("conclusion") != REVIEWED_MODEL_RUN_CONCLUSION:
        raise ValueError("DEC-251 reviewed model run conclusion mismatch")

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or artifacts:
        raise ValueError("DEC-251 requires zero persisted model artifacts")
    total_count = artifacts_payload.get("total_count")
    if total_count is not None and total_count != 0:
        raise ValueError("DEC-251 artifact total_count must be zero")

    review = (
        validate_fit_temporal_residual_regime_balance_utility_model_terminal_review(
            run=run,
            jobs_payload=jobs_payload,
            artifacts_payload=artifacts_payload,
            aggregate_evidence=None,
        )
    )

    expected_review = {
        "fit_temporal_residual_regime_balance_utility_model_terminal_reviewed": True,
        "fit_temporal_residual_regime_balance_utility_model_result_review_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_REVIEW_DECISION
        ),
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": REVIEWED_MODEL_RUN_ATTEMPT,
        "reviewed_model_run_conclusion": REVIEWED_MODEL_RUN_CONCLUSION,
        "persisted_cell_artifact_count": 0,
        "aggregate_artifact_present": False,
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_"
            "RUN_FAILURE_REVIEW_REQUIRED"
        ),
        "authorization_preflight_conclusion": "success",
        "successful_matrix_job_count": 0,
        "failed_matrix_job_count": 9,
        "cancelled_matrix_job_count": 0,
        "skipped_matrix_job_count": 0,
        "replacement_model_run_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    for field, expected in expected_review.items():
        if review.get(field) != expected:
            raise ValueError(f"DEC-251 terminal review {field} mismatch")

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError("DEC-251 jobs payload is malformed")
    by_id = {
        job.get("id"): job
        for job in jobs
        if isinstance(job, Mapping)
    }
    preflight = by_id.get(REVIEWED_AUTHORIZATION_PREFLIGHT_JOB_ID)
    aggregate = by_id.get(REVIEWED_AGGREGATE_JOB_ID)
    if not isinstance(preflight, Mapping) or preflight.get("conclusion") != "success":
        raise ValueError("DEC-251 authorization preflight identity mismatch")
    if not isinstance(aggregate, Mapping) or aggregate.get("conclusion") != "skipped":
        raise ValueError("DEC-251 aggregate job identity mismatch")

    failed_job_count = _validate_failure_signatures(failure_signatures)

    return {
        **review,
        "fit_temporal_residual_regime_balance_utility_model_result_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_DECISION
        ),
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_"
            "REVIEWED_FAILED_NO_RESULT"
        ),
        "failure_classification": FAILURE_CLASSIFICATION,
        "failed_matrix_job_signature_count": failed_job_count,
        "model_result_produced": False,
        "accepted_model_candidate_count": 0,
        "model_run_dispatch_authorized": MODEL_RUN_DISPATCH_AUTHORIZED,
        "replacement_model_run_authorized": REPLACEMENT_MODEL_RUN_AUTHORIZED,
        "authoritative_model_result_execution_authorized": (
            AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED
        ),
        "model_protocol_result_authorized": MODEL_PROTOCOL_RESULT_AUTHORIZED,
        "model_fit_authorized": MODEL_FIT_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "shadow_authorized": SHADOW_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


__all__ = [
    "AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC246_REVIEW_BLOB_SHA",
    "DEC250_MERGED_COMMIT",
    "DEMO_ORDER_AUTHORIZED",
    "EXPECTED_MATRIX_FAILURE_SIGNATURE",
    "FAILURE_CLASSIFICATION",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_DECISION",
    "INTERMEDIATE_PREDECESSOR_MODULE",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "MODEL_RUN_DISPATCH_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REPLACEMENT_MODEL_RUN_AUTHORIZED",
    "REVIEWED_MATRIX_JOB_IDS",
    "REVIEWED_MODEL_HEAD_SHA",
    "REVIEWED_MODEL_RUN_ID",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "validate_reviewed_fit_temporal_residual_regime_balance_utility_failed_result",
]
