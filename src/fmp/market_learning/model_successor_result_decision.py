from __future__ import annotations

from typing import Mapping

from .model_successor_result_review import (
    validate_successor_model_terminal_review,
)


SUCCESSOR_MODEL_RESULT_DECISION = "DEC-102"

REVIEWED_MODEL_RUN_ID = 35911916239
REVIEWED_MODEL_HEAD_SHA = (
    "6d42a5053c5f2f696071715640dab24973a40517"
)
REVIEWED_MODEL_RUN_ATTEMPT = 1
REVIEWED_MODEL_RUN_CONCLUSION = "success"

REVIEWED_AGGREGATE_ARTIFACT_ID = 10774927034
REVIEWED_AGGREGATE_ARTIFACT_NAME = (
    "exp045-model-result-evidence-"
    "6d42a5053c5f2f696071715640dab24973a40517-"
    "from-feature-35867307338-outcome-35876715434"
)
REVIEWED_AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:"
    "8602d0b5e9bb6ad746f5cd5c96e878e631d6ed090dcd7a236c0ee00c6fadd5a5"
)
REVIEWED_EVIDENCE_FINGERPRINT = (
    "3e0ebac02dbba690b4c03dd10c3fdd30"
    "c5eb0d6356b881e38f9a3527f0135c55"
)

REVIEWED_VERIFIED_CELL_COUNT = 18
REVIEWED_SELECTED_CELL_COUNT = 1
REVIEWED_NO_MODEL_CHALLENGER_COUNT = 17
REVIEWED_NO_MODEL_FAMILY_AVAILABLE_COUNT = 0
REVIEWED_VALIDATION_PASS_COUNT = 0
REVIEWED_RETROSPECTIVE_HOLDOUT_PASS_COUNT = 0
REVIEWED_LOGISTIC_NONCONVERGENCE_CELL_COUNT = 6

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
            "DEC-102 artifact listing is malformed"
        )

    matches: list[Mapping[str, object]] = []
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "DEC-102 artifact row is malformed"
            )
        if raw.get("name") == REVIEWED_AGGREGATE_ARTIFACT_NAME:
            matches.append(raw)

    if len(matches) != 1:
        raise ValueError(
            "DEC-102 requires exactly one reviewed aggregate artifact"
        )

    artifact = matches[0]
    if artifact.get("id") != REVIEWED_AGGREGATE_ARTIFACT_ID:
        raise ValueError(
            "DEC-102 aggregate artifact id mismatch"
        )
    if artifact.get("expired") is not False:
        raise ValueError(
            "DEC-102 aggregate artifact must remain non-expired"
        )
    digest = artifact.get("digest")
    if (
        digest is not None
        and digest != REVIEWED_AGGREGATE_ARTIFACT_DIGEST
    ):
        raise ValueError(
            "DEC-102 aggregate artifact digest mismatch"
        )


def validate_reviewed_successor_model_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    aggregate_evidence: Mapping[str, object],
) -> dict[str, object]:
    if run.get("id") != REVIEWED_MODEL_RUN_ID:
        raise ValueError(
            "DEC-102 reviewed model run id mismatch"
        )
    if run.get("head_sha") != REVIEWED_MODEL_HEAD_SHA:
        raise ValueError(
            "DEC-102 reviewed model head SHA mismatch"
        )
    if run.get("run_attempt") != REVIEWED_MODEL_RUN_ATTEMPT:
        raise ValueError(
            "DEC-102 reviewed model run attempt mismatch"
        )
    if run.get("conclusion") != REVIEWED_MODEL_RUN_CONCLUSION:
        raise ValueError(
            "DEC-102 reviewed model run conclusion mismatch"
        )

    _validate_aggregate_artifact_identity(
        artifacts_payload
    )

    review = validate_successor_model_terminal_review(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        aggregate_evidence=aggregate_evidence,
    )

    exact = {
        "stage": "SUCCESSOR_MODEL_RESULT_REVIEW_REQUIRED",
        "successor_model_terminal_reviewed": True,
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": REVIEWED_MODEL_RUN_ATTEMPT,
        "reviewed_model_run_conclusion": REVIEWED_MODEL_RUN_CONCLUSION,
        "persisted_cell_artifact_count": 9,
        "aggregate_artifact_present": True,
        "successor_model_result_evidence_verified": True,
        "successor_model_result_evidence_fingerprint": (
            REVIEWED_EVIDENCE_FINGERPRINT
        ),
        "successor_model_result_code_commit": (
            REVIEWED_MODEL_HEAD_SHA
        ),
        "verified_cell_count": REVIEWED_VERIFIED_CELL_COUNT,
        "selected_cell_count": REVIEWED_SELECTED_CELL_COUNT,
        "no_model_challenger_count": (
            REVIEWED_NO_MODEL_CHALLENGER_COUNT
        ),
        "no_model_family_available_count": (
            REVIEWED_NO_MODEL_FAMILY_AVAILABLE_COUNT
        ),
        "validation_pass_count": (
            REVIEWED_VALIDATION_PASS_COUNT
        ),
        "retrospective_holdout_pass_count": (
            REVIEWED_RETROSPECTIVE_HOLDOUT_PASS_COUNT
        ),
        "logistic_nonconvergence_cell_count": (
            REVIEWED_LOGISTIC_NONCONVERGENCE_CELL_COUNT
        ),
        "prior_result_informed": True,
        "untouched_oos": False,
        "replacement_model_run_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }
    for field, expected in exact.items():
        if review.get(field) != expected:
            raise ValueError(
                f"DEC-102 terminal review {field} mismatch"
            )

    return {
        **review,
        "successor_model_result_decision": (
            SUCCESSOR_MODEL_RESULT_DECISION
        ),
        "stage": (
            "SUCCESSOR_MODEL_RESULT_REVIEWED_"
            "NO_ACCEPTED_CHALLENGER"
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
    "REVIEWED_EVIDENCE_FINGERPRINT",
    "REVIEWED_LOGISTIC_NONCONVERGENCE_CELL_COUNT",
    "REVIEWED_MODEL_HEAD_SHA",
    "REVIEWED_MODEL_RUN_ATTEMPT",
    "REVIEWED_MODEL_RUN_CONCLUSION",
    "REVIEWED_MODEL_RUN_ID",
    "REVIEWED_NO_MODEL_CHALLENGER_COUNT",
    "REVIEWED_NO_MODEL_FAMILY_AVAILABLE_COUNT",
    "REVIEWED_RETROSPECTIVE_HOLDOUT_PASS_COUNT",
    "REVIEWED_SELECTED_CELL_COUNT",
    "REVIEWED_VALIDATION_PASS_COUNT",
    "REVIEWED_VERIFIED_CELL_COUNT",
    "SHADOW_AUTHORIZED",
    "SUCCESSOR_MODEL_RESULT_DECISION",
    "TRADING_AUTHORIZED",
    "validate_reviewed_successor_model_result",
]
