from __future__ import annotations

from typing import Mapping

from .exp062_historical_terminal_review_contract import (
    EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION,
    EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION,
    classify_historical_terminal_result,
)
from .exp062_run_contract import (
    EXP062_EXPERIMENT_ID,
    expected_aggregate_artifact_name,
    validate_aggregate_evidence,
)


EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION = "DEC-440"
EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_VERSION = (
    "fmp-exp062-historical-result-content-review-v1"
)

EXP062_HISTORICAL_RUN_ID = 36714210992
EXP062_HISTORICAL_RUN_HEAD_SHA = "013395092804de6b0ef51537081ab8443b8b91be"
EXP062_HISTORICAL_RUN_NUMBER = 2
EXP062_HISTORICAL_RUN_ATTEMPT = 1

EXP062_AGGREGATE_ARTIFACT_ID = 11096592737
EXP062_AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:077535bc6e9d9a1d6e8693f873b7552cf8028d793ef79eab175dbbd9970430bc"
)
EXP062_AGGREGATE_JSON_SHA256 = (
    "bfdf9787e9ee32c30ff29aa70594d7404bc7fc2cb573a60068802d2aacbaa6f3"
)
EXP062_AGGREGATE_EVIDENCE_FINGERPRINT = (
    "b8019226fb7fce14c6711834fe16cdbb52795d9ca8996b1ed98ede7ecfba9506"
)

EXPECTED_DISCOVERY_SHORTLIST_COUNT = 67
EXPECTED_CONFIRMATION_FROZEN_COUNT = 11
EXPECTED_VALIDATION_ACCEPTED_COUNT = 0
EXPECTED_EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"

RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character SHA-256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_aggregate_artifact(
    artifacts_payload: Mapping[str, object],
) -> Mapping[str, object]:
    raw = artifacts_payload.get("artifacts")
    if not isinstance(raw, list):
        raise ValueError("DEC-440 artifacts payload must contain artifacts")

    expected_name = expected_aggregate_artifact_name(
        code_commit=EXP062_HISTORICAL_RUN_HEAD_SHA,
    )
    matches = [
        item
        for item in raw
        if isinstance(item, Mapping) and item.get("name") == expected_name
    ]
    if len(matches) != 1:
        raise ValueError("DEC-440 requires exactly one aggregate artifact")

    artifact = matches[0]
    _require_exact(
        artifact,
        {
            "id": EXP062_AGGREGATE_ARTIFACT_ID,
            "name": expected_name,
            "digest": EXP062_AGGREGATE_ARTIFACT_DIGEST,
            "expired": False,
        },
        prefix="DEC-440 aggregate artifact",
    )
    return artifact


def review_exp062_historical_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    aggregate_evidence: Mapping[str, object],
    aggregate_json_sha256: str,
) -> dict[str, object]:
    terminal = classify_historical_terminal_result(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        expected_head_sha=EXP062_HISTORICAL_RUN_HEAD_SHA,
    )
    _require_exact(
        terminal,
        {
            "decision": EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION,
            "version": EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION,
            "stage": "EXP062_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED",
            "historical_run_id": EXP062_HISTORICAL_RUN_ID,
            "historical_run_head_sha": EXP062_HISTORICAL_RUN_HEAD_SHA,
            "historical_run_number": EXP062_HISTORICAL_RUN_NUMBER,
            "historical_run_attempt": EXP062_HISTORICAL_RUN_ATTEMPT,
            "historical_run_conclusion": "success",
            "historical_result_slot_consumed": True,
            "historical_result_success_complete": True,
            "materialized_job_count": 20,
            "artifact_count": 20,
            "aggregate_result_content_review_required": True,
            "rerun_authorized": False,
            "retry_authorized": False,
            "replacement_run_authorized": False,
            "candidate_compilation_authorized": False,
            "promotion_authorized": False,
            "phase8b_authorized": False,
            "trading_authorized": False,
        },
        prefix="DEC-440 terminal review",
    )
    if terminal.get("job_conclusion_counts") != {"success": 20}:
        raise ValueError("DEC-440 terminal job conclusion counts mismatch")
    if terminal.get("github_unexpanded_matrix_placeholder_present") is not False:
        raise ValueError("DEC-440 successful result cannot contain matrix placeholder")

    artifact = _validate_aggregate_artifact(artifacts_payload)

    aggregate_json_sha256 = _validate_sha256(
        aggregate_json_sha256,
        field="DEC-440 aggregate JSON SHA-256",
    )
    if aggregate_json_sha256 != EXP062_AGGREGATE_JSON_SHA256:
        raise ValueError("DEC-440 aggregate JSON SHA-256 mismatch")

    aggregate = validate_aggregate_evidence(aggregate_evidence)
    _require_exact(
        aggregate,
        {
            "experiment_id": EXP062_EXPERIMENT_ID,
            "code_commit": EXP062_HISTORICAL_RUN_HEAD_SHA,
            "evidence_fingerprint": EXP062_AGGREGATE_EVIDENCE_FINGERPRINT,
            "evidence_label": EXPECTED_EVIDENCE_LABEL,
            "expected_cell_count": 18,
            "verified_cell_count": 18,
            "discovery_shortlist_count": EXPECTED_DISCOVERY_SHORTLIST_COUNT,
            "confirmation_frozen_count": EXPECTED_CONFIRMATION_FROZEN_COUNT,
            "validation_accepted_count": EXPECTED_VALIDATION_ACCEPTED_COUNT,
            "untouched_oos": False,
            "reserved_robustness_opened": False,
            "candidate_compilation_authorized": False,
            "promotion_authorized": False,
            "phase8b_authorized": False,
            "demo_order_authorized": False,
            "broker_mutation_authorized": False,
            "live_order_authorized": False,
            "real_money_authorized": False,
            "trading_authorized": False,
        },
        prefix="DEC-440 aggregate evidence",
    )

    return {
        "decision": EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION,
        "version": EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_VERSION,
        "stage": "EXP062_HISTORICAL_RESULT_CONTENT_REVIEWED_NO_VALIDATION_ACCEPTED",
        "experiment_id": EXP062_EXPERIMENT_ID,
        "terminal_review_decision": terminal["decision"],
        "terminal_review_version": terminal["version"],
        "historical_run_id": EXP062_HISTORICAL_RUN_ID,
        "historical_run_head_sha": EXP062_HISTORICAL_RUN_HEAD_SHA,
        "historical_run_number": EXP062_HISTORICAL_RUN_NUMBER,
        "historical_run_attempt": EXP062_HISTORICAL_RUN_ATTEMPT,
        "historical_run_conclusion": "success",
        "historical_result_slot_consumed": True,
        "aggregate_artifact_id": artifact["id"],
        "aggregate_artifact_name": artifact["name"],
        "aggregate_artifact_digest": artifact["digest"],
        "aggregate_json_sha256": aggregate_json_sha256,
        "aggregate_evidence_fingerprint": aggregate["evidence_fingerprint"],
        "evidence_label": aggregate["evidence_label"],
        "untouched_oos": False,
        "verified_cell_count": aggregate["verified_cell_count"],
        "discovery_shortlist_count": aggregate["discovery_shortlist_count"],
        "confirmation_frozen_count": aggregate["confirmation_frozen_count"],
        "validation_accepted_count": aggregate["validation_accepted_count"],
        "aggregate_result_content_review_required": False,
        "historical_result_review_complete": True,
        "validation_accepted_candidates_present": False,
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": "IMMUTABLE_HISTORICAL_RESULT_REVIEW_FREEZE",
    }


__all__ = [
    "EXP062_AGGREGATE_ARTIFACT_DIGEST",
    "EXP062_AGGREGATE_ARTIFACT_ID",
    "EXP062_AGGREGATE_EVIDENCE_FINGERPRINT",
    "EXP062_AGGREGATE_JSON_SHA256",
    "EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION",
    "EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_VERSION",
    "EXP062_HISTORICAL_RUN_HEAD_SHA",
    "EXP062_HISTORICAL_RUN_ID",
    "review_exp062_historical_result",
]
