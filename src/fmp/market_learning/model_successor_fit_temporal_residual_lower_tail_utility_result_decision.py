from __future__ import annotations

from typing import Mapping

from .model_successor_fit_temporal_residual_lower_tail_utility_result_review import (
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_REVIEW_DECISION,
    validate_fit_temporal_residual_lower_tail_utility_model_terminal_review,
)


FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_DECISION = "DEC-218"

DEC217_MERGED_COMMIT = "3ce20d7445f6837cae067c0c561002215b05b2f9"
DEC213_REVIEW_BLOB_SHA = "0bfc50d39d04d82e95c731b7284c7be143191efd"

REVIEWED_MODEL_RUN_ID = 36175841645
REVIEWED_MODEL_HEAD_SHA = "3ce20d7445f6837cae067c0c561002215b05b2f9"
REVIEWED_MODEL_RUN_ATTEMPT = 1
REVIEWED_MODEL_RUN_CONCLUSION = "failure"

REVIEWED_AUTHORIZATION_PREFLIGHT_JOB_ID = 108206116932
REVIEWED_AGGREGATE_JOB_ID = 108210729511

PREDECESSOR_TRAINING_MODULE = (
    "fmp.market_learning."
    "model_successor_fit_temporal_residual_breadth_utility_training"
)
MISSING_STABILITY_SHARE_EXPORT = "MIN_STABILITY_WINDOW_CANDIDATE_SHARE"
MISSING_SUPPORT_COUNT_EXPORT = (
    "FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL"
)

EXPECTED_MATRIX_FAILURE_EXPORTS = {
    108206298902: MISSING_STABILITY_SHARE_EXPORT,
    108206298929: MISSING_STABILITY_SHARE_EXPORT,
    108206298937: MISSING_STABILITY_SHARE_EXPORT,
    108206298943: MISSING_STABILITY_SHARE_EXPORT,
    108206298952: MISSING_SUPPORT_COUNT_EXPORT,
    108206298986: MISSING_STABILITY_SHARE_EXPORT,
    108206298987: MISSING_STABILITY_SHARE_EXPORT,
    108206299029: MISSING_STABILITY_SHARE_EXPORT,
    108206299131: MISSING_STABILITY_SHARE_EXPORT,
}

FAILURE_CLASSIFICATION = (
    "IMPLEMENTATION_DEPENDENCY_EXPORT_DRIFT_PREVENTED_ALL_EXP056_CELL_RESULTS"
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
) -> dict[str, int]:
    if set(failure_signatures) != set(EXPECTED_MATRIX_FAILURE_EXPORTS):
        raise ValueError("DEC-218 matrix failure job inventory mismatch")

    stability_count = 0
    support_count = 0
    for job_id, expected_export in EXPECTED_MATRIX_FAILURE_EXPORTS.items():
        value = failure_signatures.get(job_id)
        if not isinstance(value, str):
            raise ValueError("DEC-218 failure signature is malformed")
        expected = (
            f"AttributeError: module '{PREDECESSOR_TRAINING_MODULE}' "
            f"has no attribute '{expected_export}'"
        )
        if value != expected:
            raise ValueError(
                f"DEC-218 failure signature mismatch for job {job_id}"
            )
        if expected_export == MISSING_STABILITY_SHARE_EXPORT:
            stability_count += 1
        elif expected_export == MISSING_SUPPORT_COUNT_EXPORT:
            support_count += 1
        else:
            raise ValueError("DEC-218 unexpected failure export")

    if stability_count != 8 or support_count != 1:
        raise ValueError("DEC-218 failure signature counts drift")

    return {
        "missing_stability_share_export_job_count": stability_count,
        "missing_support_count_export_job_count": support_count,
    }


def validate_reviewed_fit_temporal_residual_lower_tail_utility_failed_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    failure_signatures: Mapping[int, str],
) -> dict[str, object]:
    if run.get("id") != REVIEWED_MODEL_RUN_ID:
        raise ValueError("DEC-218 reviewed model run id mismatch")
    if run.get("head_sha") != REVIEWED_MODEL_HEAD_SHA:
        raise ValueError("DEC-218 reviewed model head SHA mismatch")
    if run.get("run_attempt") != REVIEWED_MODEL_RUN_ATTEMPT:
        raise ValueError("DEC-218 reviewed model run attempt mismatch")
    if run.get("conclusion") != REVIEWED_MODEL_RUN_CONCLUSION:
        raise ValueError("DEC-218 reviewed model run conclusion mismatch")

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or artifacts:
        raise ValueError("DEC-218 requires zero persisted model artifacts")
    total_count = artifacts_payload.get("total_count")
    if total_count is not None and total_count != 0:
        raise ValueError("DEC-218 artifact total_count must be zero")

    review = (
        validate_fit_temporal_residual_lower_tail_utility_model_terminal_review(
            run=run,
            jobs_payload=jobs_payload,
            artifacts_payload=artifacts_payload,
            aggregate_evidence=None,
        )
    )

    expected_review = {
        "fit_temporal_residual_lower_tail_utility_model_terminal_reviewed": True,
        "fit_temporal_residual_lower_tail_utility_model_result_review_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_REVIEW_DECISION
        ),
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": REVIEWED_MODEL_RUN_ATTEMPT,
        "reviewed_model_run_conclusion": REVIEWED_MODEL_RUN_CONCLUSION,
        "persisted_cell_artifact_count": 0,
        "aggregate_artifact_present": False,
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_"
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
            raise ValueError(f"DEC-218 terminal review {field} mismatch")

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError("DEC-218 jobs payload is malformed")
    by_id = {
        job.get("id"): job
        for job in jobs
        if isinstance(job, Mapping)
    }
    preflight = by_id.get(REVIEWED_AUTHORIZATION_PREFLIGHT_JOB_ID)
    aggregate = by_id.get(REVIEWED_AGGREGATE_JOB_ID)
    if not isinstance(preflight, Mapping) or preflight.get("conclusion") != "success":
        raise ValueError("DEC-218 authorization preflight identity mismatch")
    if not isinstance(aggregate, Mapping) or aggregate.get("conclusion") != "skipped":
        raise ValueError("DEC-218 aggregate job identity mismatch")

    signature_summary = _validate_failure_signatures(failure_signatures)

    return {
        **review,
        **signature_summary,
        "fit_temporal_residual_lower_tail_utility_model_result_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_DECISION
        ),
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_"
            "REVIEWED_FAILED_NO_RESULT"
        ),
        "failure_classification": FAILURE_CLASSIFICATION,
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
    "DEC213_REVIEW_BLOB_SHA",
    "DEC217_MERGED_COMMIT",
    "DEMO_ORDER_AUTHORIZED",
    "EXPECTED_MATRIX_FAILURE_EXPORTS",
    "FAILURE_CLASSIFICATION",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_DECISION",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "MODEL_RUN_DISPATCH_AUTHORIZED",
    "PREDECESSOR_TRAINING_MODULE",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REPLACEMENT_MODEL_RUN_AUTHORIZED",
    "REVIEWED_MODEL_HEAD_SHA",
    "REVIEWED_MODEL_RUN_ID",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "validate_reviewed_fit_temporal_residual_lower_tail_utility_failed_result",
]
