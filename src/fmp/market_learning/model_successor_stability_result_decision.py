from __future__ import annotations

from typing import Mapping

from .model_successor_stability_result_review import (
    validate_stability_model_terminal_review,
)


STABILITY_MODEL_RESULT_DECISION = "DEC-111"

REVIEWED_MODEL_RUN_ID = 35978474425
REVIEWED_MODEL_HEAD_SHA = (
    "dabafcc290d2b383531532d873c7d6c697198d5a"
)
REVIEWED_MODEL_RUN_ATTEMPT = 1
REVIEWED_MODEL_RUN_CONCLUSION = "success"

REVIEWED_AGGREGATE_ARTIFACT_ID = 10800835426
REVIEWED_AGGREGATE_ARTIFACT_NAME = (
    "exp046-stability-model-result-evidence-"
    "dabafcc290d2b383531532d873c7d6c697198d5a-"
    "from-feature-35867307338-outcome-35876715434"
)
REVIEWED_AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:"
    "f52ffa5d98eb196a33b97c6c09172a97"
    "c2c4ad712a41603ec7aef535825cb5d2"
)
REVIEWED_EVIDENCE_FINGERPRINT = (
    "499c91e4508f07bf8a637657969175fb"
    "ba8e93d07236b94ded06ae884b386214"
)

REVIEWED_VERIFIED_CELL_COUNT = 18
REVIEWED_SELECTED_CELL_COUNT = 0
REVIEWED_NO_STABLE_MODEL_CHALLENGER_COUNT = 18
REVIEWED_NO_MODEL_FAMILY_AVAILABLE_COUNT = 0
REVIEWED_VALIDATION_PASS_COUNT = 0
REVIEWED_RETROSPECTIVE_HOLDOUT_PASS_COUNT = 0
REVIEWED_LOGISTIC_NONCONVERGENCE_CELL_COUNT = 5
REVIEWED_AGGREGATE_SELECTION_PASS_VARIANT_COUNT = 2
REVIEWED_STABLE_SELECTION_PASS_VARIANT_COUNT = 0
REVIEWED_STABILITY_REJECT_VARIANT_COUNT = 2
REVIEWED_ACCEPTED_MODEL_CANDIDATE_COUNT = 0

PREDECESSOR_RESULT_DECISION = "DEC-102"
PREDECESSOR_EVIDENCE_FINGERPRINT = (
    "3e0ebac02dbba690b4c03dd10c3fdd30"
    "c5eb0d6356b881e38f9a3527f0135c55"
)

CROSS_RUN_HGB_COMMON_FITTED_CELL_COUNT = 18
CROSS_RUN_HGB_PREPROCESSOR_EXACT_COUNT = 18
CROSS_RUN_HGB_MODEL_FINGERPRINT_EXACT_COUNT = 18

CROSS_RUN_LOGISTIC_COMMON_FITTED_CELL_COUNT = 10
CROSS_RUN_LOGISTIC_PREPROCESSOR_EXACT_COUNT = 10
CROSS_RUN_LOGISTIC_MODEL_FINGERPRINT_EXACT_COUNT = 4
CROSS_RUN_LOGISTIC_MODEL_FINGERPRINT_MISMATCH_COUNT = 6
CROSS_RUN_LOGISTIC_FIT_STATUS_CHANGE_COUNT = 5
CROSS_RUN_LOGISTIC_FIT_STATUS_CHANGES = (
    ("EURUSD", "5m", 60, "FAILED_NON_CONVERGENCE", "FITTED"),
    ("EURUSD", "5m", 240, "FAILED_NON_CONVERGENCE", "FITTED"),
    ("EURUSD", "15m", 240, "FAILED_NON_CONVERGENCE", "FITTED"),
    ("GBPUSD", "5m", 240, "FITTED", "FAILED_NON_CONVERGENCE"),
    ("USDJPY", "15m", 240, "FITTED", "FAILED_NON_CONVERGENCE"),
)

LOGISTIC_CROSS_RUN_REPRODUCIBILITY_ACCEPTED = False
LOGISTIC_REPRODUCIBILITY_DIAGNOSTIC_REQUIRED = True

MODEL_RUN_DISPATCH_AUTHORIZED = False
REPLACEMENT_MODEL_RUN_AUTHORIZED = False
AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED = False
MODEL_PROTOCOL_RESULT_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = False
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
            "DEC-111 artifact listing is malformed"
        )

    matches: list[Mapping[str, object]] = []
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "DEC-111 artifact row is malformed"
            )
        if raw.get("name") == REVIEWED_AGGREGATE_ARTIFACT_NAME:
            matches.append(raw)

    if len(matches) != 1:
        raise ValueError(
            "DEC-111 requires exactly one reviewed aggregate artifact"
        )

    artifact = matches[0]
    if artifact.get("id") != REVIEWED_AGGREGATE_ARTIFACT_ID:
        raise ValueError(
            "DEC-111 aggregate artifact id mismatch"
        )
    if artifact.get("expired") is not False:
        raise ValueError(
            "DEC-111 aggregate artifact must remain non-expired"
        )
    digest = artifact.get("digest")
    if (
        digest is not None
        and digest != REVIEWED_AGGREGATE_ARTIFACT_DIGEST
    ):
        raise ValueError(
            "DEC-111 aggregate artifact digest mismatch"
        )


def validate_reviewed_stability_model_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    aggregate_evidence: Mapping[str, object],
) -> dict[str, object]:
    if run.get("id") != REVIEWED_MODEL_RUN_ID:
        raise ValueError(
            "DEC-111 reviewed model run id mismatch"
        )
    if run.get("head_sha") != REVIEWED_MODEL_HEAD_SHA:
        raise ValueError(
            "DEC-111 reviewed model head SHA mismatch"
        )
    if run.get("run_attempt") != REVIEWED_MODEL_RUN_ATTEMPT:
        raise ValueError(
            "DEC-111 reviewed model run attempt mismatch"
        )
    if run.get("conclusion") != REVIEWED_MODEL_RUN_CONCLUSION:
        raise ValueError(
            "DEC-111 reviewed model run conclusion mismatch"
        )

    _validate_aggregate_artifact_identity(
        artifacts_payload
    )

    review = validate_stability_model_terminal_review(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        aggregate_evidence=aggregate_evidence,
    )

    exact = {
        "stage": "STABILITY_MODEL_RESULT_REVIEW_REQUIRED",
        "stability_model_terminal_reviewed": True,
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": REVIEWED_MODEL_RUN_ATTEMPT,
        "reviewed_model_run_conclusion": REVIEWED_MODEL_RUN_CONCLUSION,
        "persisted_cell_artifact_count": 9,
        "aggregate_artifact_present": True,
        "stability_model_result_evidence_verified": True,
        "stability_model_result_evidence_fingerprint": (
            REVIEWED_EVIDENCE_FINGERPRINT
        ),
        "stability_model_result_code_commit": (
            REVIEWED_MODEL_HEAD_SHA
        ),
        "verified_cell_count": REVIEWED_VERIFIED_CELL_COUNT,
        "selected_cell_count": REVIEWED_SELECTED_CELL_COUNT,
        "no_stable_model_challenger_count": (
            REVIEWED_NO_STABLE_MODEL_CHALLENGER_COUNT
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
        "aggregate_selection_pass_variant_count": (
            REVIEWED_AGGREGATE_SELECTION_PASS_VARIANT_COUNT
        ),
        "stable_selection_pass_variant_count": (
            REVIEWED_STABLE_SELECTION_PASS_VARIANT_COUNT
        ),
        "stability_reject_variant_count": (
            REVIEWED_STABILITY_REJECT_VARIANT_COUNT
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
                f"DEC-111 terminal review {field} mismatch"
            )

    return {
        **review,
        "stability_model_result_decision": (
            STABILITY_MODEL_RESULT_DECISION
        ),
        "stage": (
            "STABILITY_MODEL_RESULT_REVIEWED_"
            "NO_STABLE_CHALLENGER"
        ),
        "accepted_model_candidate_count": (
            REVIEWED_ACCEPTED_MODEL_CANDIDATE_COUNT
        ),
        "predecessor_result_decision": (
            PREDECESSOR_RESULT_DECISION
        ),
        "predecessor_evidence_fingerprint": (
            PREDECESSOR_EVIDENCE_FINGERPRINT
        ),
        "cross_run_hgb_common_fitted_cell_count": (
            CROSS_RUN_HGB_COMMON_FITTED_CELL_COUNT
        ),
        "cross_run_hgb_preprocessor_exact_count": (
            CROSS_RUN_HGB_PREPROCESSOR_EXACT_COUNT
        ),
        "cross_run_hgb_model_fingerprint_exact_count": (
            CROSS_RUN_HGB_MODEL_FINGERPRINT_EXACT_COUNT
        ),
        "cross_run_logistic_common_fitted_cell_count": (
            CROSS_RUN_LOGISTIC_COMMON_FITTED_CELL_COUNT
        ),
        "cross_run_logistic_preprocessor_exact_count": (
            CROSS_RUN_LOGISTIC_PREPROCESSOR_EXACT_COUNT
        ),
        "cross_run_logistic_model_fingerprint_exact_count": (
            CROSS_RUN_LOGISTIC_MODEL_FINGERPRINT_EXACT_COUNT
        ),
        "cross_run_logistic_model_fingerprint_mismatch_count": (
            CROSS_RUN_LOGISTIC_MODEL_FINGERPRINT_MISMATCH_COUNT
        ),
        "cross_run_logistic_fit_status_change_count": (
            CROSS_RUN_LOGISTIC_FIT_STATUS_CHANGE_COUNT
        ),
        "cross_run_logistic_fit_status_changes": [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "horizon_minutes": horizon,
                "exp045_status": predecessor,
                "exp046_status": successor,
            }
            for (
                symbol,
                timeframe,
                horizon,
                predecessor,
                successor,
            ) in CROSS_RUN_LOGISTIC_FIT_STATUS_CHANGES
        ],
        "logistic_cross_run_reproducibility_accepted": (
            LOGISTIC_CROSS_RUN_REPRODUCIBILITY_ACCEPTED
        ),
        "logistic_reproducibility_diagnostic_required": (
            LOGISTIC_REPRODUCIBILITY_DIAGNOSTIC_REQUIRED
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
        "successor_protocol_source_open_authorized": (
            SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED
        ),
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
    "CROSS_RUN_HGB_COMMON_FITTED_CELL_COUNT",
    "CROSS_RUN_HGB_MODEL_FINGERPRINT_EXACT_COUNT",
    "CROSS_RUN_HGB_PREPROCESSOR_EXACT_COUNT",
    "CROSS_RUN_LOGISTIC_COMMON_FITTED_CELL_COUNT",
    "CROSS_RUN_LOGISTIC_FIT_STATUS_CHANGE_COUNT",
    "CROSS_RUN_LOGISTIC_FIT_STATUS_CHANGES",
    "CROSS_RUN_LOGISTIC_MODEL_FINGERPRINT_EXACT_COUNT",
    "CROSS_RUN_LOGISTIC_MODEL_FINGERPRINT_MISMATCH_COUNT",
    "CROSS_RUN_LOGISTIC_PREPROCESSOR_EXACT_COUNT",
    "DEMO_ORDER_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_CROSS_RUN_REPRODUCIBILITY_ACCEPTED",
    "LOGISTIC_REPRODUCIBILITY_DIAGNOSTIC_REQUIRED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "MODEL_RUN_DISPATCH_AUTHORIZED",
    "PREDECESSOR_EVIDENCE_FINGERPRINT",
    "PREDECESSOR_RESULT_DECISION",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REPLACEMENT_MODEL_RUN_AUTHORIZED",
    "REVIEWED_ACCEPTED_MODEL_CANDIDATE_COUNT",
    "REVIEWED_AGGREGATE_ARTIFACT_DIGEST",
    "REVIEWED_AGGREGATE_ARTIFACT_ID",
    "REVIEWED_AGGREGATE_ARTIFACT_NAME",
    "REVIEWED_AGGREGATE_SELECTION_PASS_VARIANT_COUNT",
    "REVIEWED_EVIDENCE_FINGERPRINT",
    "REVIEWED_LOGISTIC_NONCONVERGENCE_CELL_COUNT",
    "REVIEWED_MODEL_HEAD_SHA",
    "REVIEWED_MODEL_RUN_ATTEMPT",
    "REVIEWED_MODEL_RUN_CONCLUSION",
    "REVIEWED_MODEL_RUN_ID",
    "REVIEWED_NO_MODEL_FAMILY_AVAILABLE_COUNT",
    "REVIEWED_NO_STABLE_MODEL_CHALLENGER_COUNT",
    "REVIEWED_RETROSPECTIVE_HOLDOUT_PASS_COUNT",
    "REVIEWED_SELECTED_CELL_COUNT",
    "REVIEWED_STABILITY_REJECT_VARIANT_COUNT",
    "REVIEWED_STABLE_SELECTION_PASS_VARIANT_COUNT",
    "REVIEWED_VALIDATION_PASS_COUNT",
    "REVIEWED_VERIFIED_CELL_COUNT",
    "SHADOW_AUTHORIZED",
    "STABILITY_MODEL_RESULT_DECISION",
    "SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "validate_reviewed_stability_model_result",
]
