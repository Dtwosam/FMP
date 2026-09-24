from __future__ import annotations

from typing import Mapping

from .model_successor_temporal_calibrated_utility_result_review import (
    validate_temporal_calibrated_utility_model_terminal_review,
)


TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_DECISION = "DEC-161"

REVIEWED_MODEL_RUN_ID = 36066217609
REVIEWED_MODEL_HEAD_SHA = (
    "3443b95ae3c524c74df4b2daebe9c526eb01ec9c"
)
REVIEWED_MODEL_RUN_ATTEMPT = 1
REVIEWED_MODEL_RUN_CONCLUSION = "success"

REVIEWED_AGGREGATE_ARTIFACT_ID = 10837836415
REVIEWED_AGGREGATE_ARTIFACT_NAME = (
    "exp051-temporal-calibrated-utility-model-result-evidence-"
    "3443b95ae3c524c74df4b2daebe9c526eb01ec9c-"
    "from-feature-35867307338-outcome-35876715434"
)
REVIEWED_AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:"
    "ffbd18124dfe94c6eb25ae92fa4fda9650a26bd152173b000549b9a6e9fcace0"
)
REVIEWED_EVIDENCE_FINGERPRINT = (
    "7dd836ed1c76c8eefd09b2b75e1eef9e"
    "875f5c6261c6fbb2cac8e3209781aaea"
)

REVIEWED_VERIFIED_CELL_COUNT = 18
REVIEWED_VERIFIED_REGRESSOR_COUNT = 108
REVIEWED_VERIFIED_CALIBRATION_REFERENCE_COUNT = 108
REVIEWED_SELECTED_CELL_COUNT = 0
REVIEWED_NO_STABLE_MODEL_CHALLENGER_COUNT = 18
REVIEWED_VALIDATION_PASS_CELL_COUNT = 0
REVIEWED_HOLDOUT_PASS_CELL_COUNT = 0
REVIEWED_AGGREGATE_SELECTION_PASS_VARIANT_COUNT = 1
REVIEWED_STABLE_SELECTION_PASS_VARIANT_COUNT = 0
REVIEWED_UNAVAILABLE_BUDGET_VARIANT_COUNT = 26
REVIEWED_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT = 26392
REVIEWED_ACCEPTED_MODEL_CANDIDATE_COUNT = 0

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


def _validate_aggregate_artifact_identity(
    artifacts_payload: Mapping[str, object],
) -> None:
    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError(
            "DEC-161 artifact listing is malformed"
        )

    matches: list[Mapping[str, object]] = []
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "DEC-161 artifact row is malformed"
            )
        if raw.get("name") == REVIEWED_AGGREGATE_ARTIFACT_NAME:
            matches.append(raw)

    if len(matches) != 1:
        raise ValueError(
            "DEC-161 requires exactly one reviewed aggregate artifact"
        )

    artifact = matches[0]
    if artifact.get("id") != REVIEWED_AGGREGATE_ARTIFACT_ID:
        raise ValueError(
            "DEC-161 aggregate artifact id mismatch"
        )
    if artifact.get("expired") is not False:
        raise ValueError(
            "DEC-161 aggregate artifact must remain non-expired"
        )
    digest = artifact.get("digest")
    if (
        digest is not None
        and digest != REVIEWED_AGGREGATE_ARTIFACT_DIGEST
    ):
        raise ValueError(
            "DEC-161 aggregate artifact digest mismatch"
        )


def validate_reviewed_temporal_calibrated_utility_model_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    aggregate_evidence: Mapping[str, object],
) -> dict[str, object]:
    if run.get("id") != REVIEWED_MODEL_RUN_ID:
        raise ValueError(
            "DEC-161 reviewed model run id mismatch"
        )
    if run.get("head_sha") != REVIEWED_MODEL_HEAD_SHA:
        raise ValueError(
            "DEC-161 reviewed model head SHA mismatch"
        )
    if run.get("run_attempt") != REVIEWED_MODEL_RUN_ATTEMPT:
        raise ValueError(
            "DEC-161 reviewed model run attempt mismatch"
        )
    if run.get("conclusion") != REVIEWED_MODEL_RUN_CONCLUSION:
        raise ValueError(
            "DEC-161 reviewed model run conclusion mismatch"
        )

    _validate_aggregate_artifact_identity(
        artifacts_payload
    )

    review = (
        validate_temporal_calibrated_utility_model_terminal_review(
            run=run,
            jobs_payload=jobs_payload,
            artifacts_payload=artifacts_payload,
            aggregate_evidence=aggregate_evidence,
        )
    )

    exact = {
        "stage": (
            "TEMPORAL_CALIBRATED_UTILITY_MODEL_"
            "RESULT_REVIEW_REQUIRED"
        ),
        "temporal_calibrated_utility_model_terminal_reviewed": True,
        "temporal_calibrated_utility_model_result_review_decision": (
            "DEC-154"
        ),
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": REVIEWED_MODEL_RUN_ATTEMPT,
        "reviewed_model_run_conclusion": REVIEWED_MODEL_RUN_CONCLUSION,
        "persisted_cell_artifact_count": 9,
        "aggregate_artifact_present": True,
        "temporal_calibrated_utility_model_result_evidence_verified": (
            True
        ),
        "verified_cell_count": REVIEWED_VERIFIED_CELL_COUNT,
        "verified_regressor_count": REVIEWED_VERIFIED_REGRESSOR_COUNT,
        "verified_calibration_reference_count": (
            REVIEWED_VERIFIED_CALIBRATION_REFERENCE_COUNT
        ),
        "selected_cell_count": REVIEWED_SELECTED_CELL_COUNT,
        "no_temporal_calibrated_utility_stable_model_challenger_count": (
            REVIEWED_NO_STABLE_MODEL_CHALLENGER_COUNT
        ),
        "validation_pass_cell_count": (
            REVIEWED_VALIDATION_PASS_CELL_COUNT
        ),
        "holdout_pass_cell_count": (
            REVIEWED_HOLDOUT_PASS_CELL_COUNT
        ),
        "aggregate_selection_pass_variant_count": (
            REVIEWED_AGGREGATE_SELECTION_PASS_VARIANT_COUNT
        ),
        "stable_selection_pass_variant_count": (
            REVIEWED_STABLE_SELECTION_PASS_VARIANT_COUNT
        ),
        "unavailable_budget_variant_count": (
            REVIEWED_UNAVAILABLE_BUDGET_VARIANT_COUNT
        ),
        "utility_eligible_selection_row_count": (
            REVIEWED_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
        ),
        "evidence_fingerprint": REVIEWED_EVIDENCE_FINGERPRINT,
        "prior_result_informed": True,
        "untouched_oos": False,
        "replacement_model_run_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    for field, expected in exact.items():
        if review.get(field) != expected:
            raise ValueError(
                f"DEC-161 terminal review {field} mismatch"
            )

    return {
        **review,
        "temporal_calibrated_utility_model_result_decision": (
            TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_DECISION
        ),
        "stage": (
            "TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_"
            "REVIEWED_NO_STABLE_CHALLENGER"
        ),
        "accepted_model_candidate_count": (
            REVIEWED_ACCEPTED_MODEL_CANDIDATE_COUNT
        ),
        "model_run_dispatch_authorized": (
            MODEL_RUN_DISPATCH_AUTHORIZED
        ),
        "replacement_model_run_authorized": (
            REPLACEMENT_MODEL_RUN_AUTHORIZED
        ),
        "authoritative_model_result_execution_authorized": (
            AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED
        ),
        "model_protocol_result_authorized": (
            MODEL_PROTOCOL_RESULT_AUTHORIZED
        ),
        "model_fit_authorized": MODEL_FIT_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "shadow_authorized": SHADOW_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": (
            BROKER_MUTATION_AUTHORIZED
        ),
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


__all__ = [
    "AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEMO_ORDER_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "MODEL_RUN_DISPATCH_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REPLACEMENT_MODEL_RUN_AUTHORIZED",
    "REVIEWED_ACCEPTED_MODEL_CANDIDATE_COUNT",
    "REVIEWED_AGGREGATE_ARTIFACT_DIGEST",
    "REVIEWED_AGGREGATE_ARTIFACT_ID",
    "REVIEWED_AGGREGATE_ARTIFACT_NAME",
    "REVIEWED_AGGREGATE_SELECTION_PASS_VARIANT_COUNT",
    "REVIEWED_EVIDENCE_FINGERPRINT",
    "REVIEWED_HOLDOUT_PASS_CELL_COUNT",
    "REVIEWED_MODEL_HEAD_SHA",
    "REVIEWED_MODEL_RUN_ATTEMPT",
    "REVIEWED_MODEL_RUN_CONCLUSION",
    "REVIEWED_MODEL_RUN_ID",
    "REVIEWED_NO_STABLE_MODEL_CHALLENGER_COUNT",
    "REVIEWED_SELECTED_CELL_COUNT",
    "REVIEWED_STABLE_SELECTION_PASS_VARIANT_COUNT",
    "REVIEWED_UNAVAILABLE_BUDGET_VARIANT_COUNT",
    "REVIEWED_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT",
    "REVIEWED_VALIDATION_PASS_CELL_COUNT",
    "REVIEWED_VERIFIED_CALIBRATION_REFERENCE_COUNT",
    "REVIEWED_VERIFIED_CELL_COUNT",
    "REVIEWED_VERIFIED_REGRESSOR_COUNT",
    "SHADOW_AUTHORIZED",
    "TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_DECISION",
    "TRADING_AUTHORIZED",
    "validate_reviewed_temporal_calibrated_utility_model_result",
]
