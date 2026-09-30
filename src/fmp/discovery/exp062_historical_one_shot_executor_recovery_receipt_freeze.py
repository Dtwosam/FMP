from __future__ import annotations

import hashlib
import json
from typing import Mapping


EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_FREEZE_DECISION = "DEC-438"
EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_FREEZE_VERSION = (
    "fmp-exp062-one-shot-executor-recovery-receipt-freeze-v1"
)

_EXPECTED_SOURCE_BLOBS = {
    "dec436_recovery_workflow": "a2520a108373d25d67dd470794eeb4f0fc9e3187",
    "dec436_recovery_authorization": "481fbfbb43557b1b42c0d9bc84ded0775816714e",
    "original_executor_workflow": "51ce87584369be957482460d81649adb1cb9f05d",
    "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
}

_FALSE_AUTHORITY_FIELDS = (
    "historical_execute_mode_available",
    "rerun_authorized",
    "retry_authorized",
    "replacement_run_authorized",
    "reserved_robustness_access_authorized",
    "candidate_compilation_authorized",
    "promotion_authorized",
    "phase8b_authorized",
    "demo_order_authorized",
    "broker_mutation_authorized",
    "live_order_authorized",
    "real_money_authorized",
    "trading_authorized",
)


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character SHA-256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _sha256_digest(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"{field} must use sha256:<hex>")
    _sha256(value.removeprefix("sha256:"), field=field)
    return value.lower()


def _source_blobs(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-438 review_source_blobs must be an object")
    actual = dict(value)
    if actual != _EXPECTED_SOURCE_BLOBS:
        raise ValueError("DEC-438 review_source_blobs mismatch")
    return {str(key): str(val) for key, val in actual.items()}


def _validate_review(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> dict[str, str]:
    exact = {
        "decision": "DEC-437",
        "version": (
            "fmp-exp062-one-shot-executor-recovery-receipt-review-v1"
        ),
        "stage": (
            "EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_REVIEWED_"
            "HISTORICAL_RESULT_DISPATCHED"
        ),
        "recovery_workflow_name": (
            "phase8a-exp062-one-shot-historical-executor-recovery"
        ),
        "recovery_workflow_path": (
            ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor-recovery.yml"
        ),
        "recovery_head_sha": expected_head_sha,
        "recovery_run_number": 1,
        "recovery_run_attempt": 1,
        "recovery_run_conclusion": "success",
        "recovery_authorization_decision": "DEC-436",
        "recovery_authorization_version": (
            "fmp-exp062-one-shot-executor-recovery-authorization-v1"
        ),
        "failed_original_executor_run_id": 36702494195,
        "failed_original_executor_job_id": 109844958600,
        "failed_original_executor_run_number": 2,
        "failed_original_executor_run_attempt": 1,
        "failed_original_executor_conclusion": "failure",
        "failed_original_executor_dispatched_historical_result": False,
        "historical_result_run_number": 2,
        "historical_result_run_attempt": 1,
        "historical_result_head_sha": expected_head_sha,
        "historical_result_dispatched": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "next_gate": (
            "IMMUTABLE_DEC436_RECOVERY_RECEIPT_FREEZE_"
            "WHILE_HISTORICAL_RESULT_RUN_2_COMPLETES"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-438 review {field} mismatch")
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-438 review {field} must remain false")

    _positive_int(value.get("recovery_run_id"), field="DEC-438 recovery run id")
    _positive_int(value.get("recovery_job_id"), field="DEC-438 recovery job id")
    _positive_int(
        value.get("recovery_artifact_id"),
        field="DEC-438 recovery artifact id",
    )
    _positive_int(
        value.get("historical_result_run_id"),
        field="DEC-438 historical result run id",
    )
    _sha256_digest(
        value.get("recovery_artifact_digest"),
        field="DEC-438 recovery artifact digest",
    )
    _sha256(
        value.get("receipt_raw_sha256"),
        field="DEC-438 receipt raw SHA-256",
    )
    _sha256(
        value.get("receipt_canonical_sha256"),
        field="DEC-438 receipt canonical SHA-256",
    )
    return _source_blobs(value.get("review_source_blobs"))


def freeze_reviewed_one_shot_executor_recovery_receipt(
    reviewed_result: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    source_blobs = _validate_review(
        reviewed_result,
        expected_head_sha=expected_head_sha,
    )

    frozen: dict[str, object] = {
        "decision": EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_FREEZE_DECISION,
        "version": EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_FREEZE_VERSION,
        "stage": (
            "EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_REVIEWED_AND_FROZEN_"
            "HISTORICAL_RESULT_DISPATCHED"
        ),
        "source_review_decision": reviewed_result["decision"],
        "source_review_version": reviewed_result["version"],
        "recovery_workflow_name": reviewed_result["recovery_workflow_name"],
        "recovery_workflow_path": reviewed_result["recovery_workflow_path"],
        "recovery_run_id": reviewed_result["recovery_run_id"],
        "recovery_head_sha": expected_head_sha,
        "recovery_run_number": 1,
        "recovery_run_attempt": 1,
        "recovery_run_conclusion": "success",
        "recovery_job_id": reviewed_result["recovery_job_id"],
        "recovery_artifact_id": reviewed_result["recovery_artifact_id"],
        "recovery_artifact_name": reviewed_result["recovery_artifact_name"],
        "recovery_artifact_digest": reviewed_result[
            "recovery_artifact_digest"
        ],
        "receipt_raw_sha256": reviewed_result["receipt_raw_sha256"],
        "receipt_canonical_sha256": reviewed_result[
            "receipt_canonical_sha256"
        ],
        "review_source_blobs": source_blobs,
        "recovery_authorization_decision": "DEC-436",
        "recovery_authorization_version": (
            "fmp-exp062-one-shot-executor-recovery-authorization-v1"
        ),
        "failed_original_executor_run_id": 36702494195,
        "failed_original_executor_job_id": 109844958600,
        "failed_original_executor_run_number": 2,
        "failed_original_executor_run_attempt": 1,
        "failed_original_executor_conclusion": "failure",
        "failed_original_executor_dispatched_historical_result": False,
        "historical_result_run_id": reviewed_result[
            "historical_result_run_id"
        ],
        "historical_result_run_number": 2,
        "historical_result_run_attempt": 1,
        "historical_result_head_sha": expected_head_sha,
        "historical_result_dispatched": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "historical_execute_mode_available": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": (
            "CONCRETE_DEC436_RECOVERY_RECEIPT_RUNTIME_EVIDENCE_BINDING_"
            "WHILE_HISTORICAL_RESULT_RUN_2_COMPLETES"
        ),
    }
    frozen["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_FREEZE_DECISION",
    "EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_FREEZE_VERSION",
    "freeze_reviewed_one_shot_executor_recovery_receipt",
]
