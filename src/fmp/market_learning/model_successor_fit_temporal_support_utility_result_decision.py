from __future__ import annotations

from typing import Mapping

from .model_successor_fit_temporal_support_utility_result_review import (
    validate_fit_temporal_support_utility_model_terminal_review,
)


FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_DECISION = "DEC-172"

REVIEWED_MODEL_RUN_ID = 36114617377
REVIEWED_MODEL_HEAD_SHA = "d477555cf116f07fa195de1b4a4c0d2f3b2838c5"
REVIEWED_MODEL_RUN_ATTEMPT = 1
REVIEWED_MODEL_RUN_CONCLUSION = "success"

REVIEWED_AGGREGATE_ARTIFACT_ID = 10855585092
REVIEWED_AGGREGATE_ARTIFACT_NAME = (
    "exp052-fit-temporal-support-utility-model-result-evidence-"
    "d477555cf116f07fa195de1b4a4c0d2f3b2838c5-"
    "from-feature-35867307338-outcome-35876715434"
)
REVIEWED_AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:"
    "c7a593b2ded1f44aee447dd352d20101b54febb65be0c5f3e8a5791a1db4d263"
)
REVIEWED_EVIDENCE_FINGERPRINT = (
    "34e397e027a069db9344d56546b654f00"
    "bd34aff73240e5bca1d55e7b3dab7eb"
)

REVIEWED_VERIFIED_CELL_COUNT = 18
REVIEWED_VERIFIED_REGRESSOR_COUNT = 108
REVIEWED_VERIFIED_POOLED_REFERENCE_COUNT = 108
REVIEWED_VERIFIED_SUPPORT_REFERENCE_COUNT = 432
REVIEWED_SELECTED_CELL_COUNT = 0
REVIEWED_NO_STABLE_MODEL_CHALLENGER_COUNT = 18
REVIEWED_VALIDATION_PASS_CELL_COUNT = 0
REVIEWED_HOLDOUT_PASS_CELL_COUNT = 0
REVIEWED_AGGREGATE_SELECTION_PASS_VARIANT_COUNT = 1
REVIEWED_STABLE_SELECTION_PASS_VARIANT_COUNT = 0
REVIEWED_UNAVAILABLE_BUDGET_VARIANT_COUNT = 26
REVIEWED_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT = 26392
REVIEWED_ACCEPTED_MODEL_CANDIDATE_COUNT = 0

REVIEWED_AGGREGATE_PASS_CELL = ("USDJPY", "5m", 60)
REVIEWED_AGGREGATE_PASS_BUDGET = 250
REVIEWED_AGGREGATE_PASS_SELECTION_CANDIDATE_COUNT = 250
REVIEWED_AGGREGATE_PASS_TOTAL_NET_PIPS = 1247.500000000025
REVIEWED_AGGREGATE_PASS_SUPPORT_CUTOFF = 0.9924051599114572
REVIEWED_AGGREGATE_PASS_POOLED_CUTOFF = 0.9967413248462105
REVIEWED_AGGREGATE_PASS_RAW_CUTOFF = 6.412340537481511

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
        raise ValueError("DEC-172 artifact listing is malformed")
    matches: list[Mapping[str, object]] = []
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-172 artifact row is malformed")
        if raw.get("name") == REVIEWED_AGGREGATE_ARTIFACT_NAME:
            matches.append(raw)
    if len(matches) != 1:
        raise ValueError(
            "DEC-172 requires exactly one reviewed aggregate artifact"
        )
    artifact = matches[0]
    if artifact.get("id") != REVIEWED_AGGREGATE_ARTIFACT_ID:
        raise ValueError("DEC-172 aggregate artifact id mismatch")
    if artifact.get("expired") is not False:
        raise ValueError("DEC-172 aggregate artifact must remain non-expired")
    digest = artifact.get("digest")
    if digest is not None and digest != REVIEWED_AGGREGATE_ARTIFACT_DIGEST:
        raise ValueError("DEC-172 aggregate artifact digest mismatch")


def validate_reviewed_fit_temporal_support_utility_model_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    aggregate_evidence: Mapping[str, object],
) -> dict[str, object]:
    if run.get("id") != REVIEWED_MODEL_RUN_ID:
        raise ValueError("DEC-172 reviewed model run id mismatch")
    if run.get("head_sha") != REVIEWED_MODEL_HEAD_SHA:
        raise ValueError("DEC-172 reviewed model head SHA mismatch")
    if run.get("run_attempt") != REVIEWED_MODEL_RUN_ATTEMPT:
        raise ValueError("DEC-172 reviewed model run attempt mismatch")
    if run.get("conclusion") != REVIEWED_MODEL_RUN_CONCLUSION:
        raise ValueError("DEC-172 reviewed model run conclusion mismatch")

    _validate_aggregate_artifact_identity(artifacts_payload)

    review = validate_fit_temporal_support_utility_model_terminal_review(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        aggregate_evidence=aggregate_evidence,
    )

    exact = {
        "stage": "FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_REVIEW_REQUIRED",
        "fit_temporal_support_utility_model_terminal_reviewed": True,
        "fit_temporal_support_utility_model_result_review_decision": "DEC-167",
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": REVIEWED_MODEL_RUN_ATTEMPT,
        "reviewed_model_run_conclusion": REVIEWED_MODEL_RUN_CONCLUSION,
        "persisted_cell_artifact_count": 9,
        "aggregate_artifact_present": True,
        "fit_temporal_support_utility_model_result_evidence_verified": True,
        "verified_cell_count": REVIEWED_VERIFIED_CELL_COUNT,
        "verified_regressor_count": REVIEWED_VERIFIED_REGRESSOR_COUNT,
        "verified_pooled_calibration_reference_count": (
            REVIEWED_VERIFIED_POOLED_REFERENCE_COUNT
        ),
        "verified_fit_temporal_support_reference_count": (
            REVIEWED_VERIFIED_SUPPORT_REFERENCE_COUNT
        ),
        "selected_cell_count": REVIEWED_SELECTED_CELL_COUNT,
        "no_fit_temporal_support_utility_stable_model_challenger_count": (
            REVIEWED_NO_STABLE_MODEL_CHALLENGER_COUNT
        ),
        "validation_pass_cell_count": REVIEWED_VALIDATION_PASS_CELL_COUNT,
        "holdout_pass_cell_count": REVIEWED_HOLDOUT_PASS_CELL_COUNT,
        "aggregate_selection_pass_variant_count": (
            REVIEWED_AGGREGATE_SELECTION_PASS_VARIANT_COUNT
        ),
        "stable_selection_pass_variant_count": (
            REVIEWED_STABLE_SELECTION_PASS_VARIANT_COUNT
        ),
        "unavailable_budget_variant_count": REVIEWED_UNAVAILABLE_BUDGET_VARIANT_COUNT,
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
            raise ValueError(f"DEC-172 terminal review {field} mismatch")

    return {
        **review,
        "fit_temporal_support_utility_model_result_decision": (
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_DECISION
        ),
        "stage": (
            "FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_"
            "REVIEWED_NO_STABLE_CHALLENGER"
        ),
        "accepted_model_candidate_count": REVIEWED_ACCEPTED_MODEL_CANDIDATE_COUNT,
        "reviewed_aggregate_pass_cell": list(REVIEWED_AGGREGATE_PASS_CELL),
        "reviewed_aggregate_pass_budget": REVIEWED_AGGREGATE_PASS_BUDGET,
        "reviewed_aggregate_pass_selection_candidate_count": (
            REVIEWED_AGGREGATE_PASS_SELECTION_CANDIDATE_COUNT
        ),
        "reviewed_aggregate_pass_total_net_pips": (
            REVIEWED_AGGREGATE_PASS_TOTAL_NET_PIPS
        ),
        "reviewed_aggregate_pass_support_cutoff": (
            REVIEWED_AGGREGATE_PASS_SUPPORT_CUTOFF
        ),
        "reviewed_aggregate_pass_pooled_cutoff": (
            REVIEWED_AGGREGATE_PASS_POOLED_CUTOFF
        ),
        "reviewed_aggregate_pass_raw_cutoff": REVIEWED_AGGREGATE_PASS_RAW_CUTOFF,
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
    "DEMO_ORDER_AUTHORIZED",
    "FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_DECISION",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "MODEL_RUN_DISPATCH_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REPLACEMENT_MODEL_RUN_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "validate_reviewed_fit_temporal_support_utility_model_result",
]
