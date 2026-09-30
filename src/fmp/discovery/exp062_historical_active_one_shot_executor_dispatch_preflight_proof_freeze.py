from __future__ import annotations

import hashlib
import json
from typing import Mapping


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_FREEZE_DECISION = (
    "DEC-428"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_FREEZE_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-dispatch-preflight-proof-freeze-v1"
)

_EXPECTED_SOURCE_BLOBS = {
    "dec426_workflow": "0bb9cd78639ebad68eb7db0fb9d083ce86b75319",
    "dec425_preflight": "1978f71bb11097613d3820127f7a04ce2bf81adb",
    "dec425_preflight_cli": "ef0f6df22d9208b6de8037585d706a1bb1e9eda4",
    "dec424_install_receipt": "27e714620018413a09ceaf287fb7943bf884ee49",
    "active_executor_workflow": "51ce87584369be957482460d81649adb1cb9f05d",
    "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
}

_FALSE_AUTHORITY_FIELDS = (
    "historical_result_dispatch_authorized",
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
        raise ValueError("DEC-428 review_source_blobs must be an object")
    actual = dict(value)
    if actual != _EXPECTED_SOURCE_BLOBS:
        raise ValueError("DEC-428 review_source_blobs mismatch")
    return {str(key): str(val) for key, val in actual.items()}


def _validate_review(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> dict[str, str]:
    exact = {
        "decision": "DEC-427",
        "version": (
            "fmp-exp062-active-one-shot-historical-executor-"
            "dispatch-preflight-proof-review-v1"
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_PREFLIGHT_PROOF_REVIEWED_RUNTIME_LOCKED"
        ),
        "proof_workflow_name": (
            "phase8a-exp062-active-one-shot-historical-executor-"
            "dispatch-preflight-proof"
        ),
        "proof_workflow_path": (
            ".github/workflows/"
            "phase8a-exp062-active-one-shot-historical-executor-"
            "dispatch-preflight-proof.yml"
        ),
        "proof_head_sha": expected_head_sha,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "dispatch_preflight_decision": "DEC-425",
        "dispatch_preflight_version": (
            "fmp-exp062-active-one-shot-historical-executor-"
            "dispatch-preflight-v1"
        ),
        "install_receipt_decision": "DEC-424",
        "install_receipt_version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-"
            "install-receipt-v1"
        ),
        "dec424_install_receipt_blob_sha": (
            "27e714620018413a09ceaf287fb7943bf884ee49"
        ),
        "active_executor_workflow_blob_sha": (
            "51ce87584369be957482460d81649adb1cb9f05d"
        ),
        "active_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "active_executor_workflow_present": True,
        "historical_executor_workflow_install_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "executor_workflow_run_count": 0,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "next_gate": (
            "IMMUTABLE_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_PREFLIGHT_PROOF_FREEZE_BEFORE_AUTHORIZATION"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-428 review {field} mismatch")
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-428 review {field} must remain false")

    _positive_int(value.get("proof_run_id"), field="DEC-428 proof run id")
    _positive_int(value.get("proof_job_id"), field="DEC-428 proof job id")
    _positive_int(value.get("proof_artifact_id"), field="DEC-428 proof artifact id")
    _sha256_digest(
        value.get("proof_artifact_digest"),
        field="DEC-428 proof artifact digest",
    )
    _sha256(
        value.get("preflight_raw_sha256"),
        field="DEC-428 preflight raw SHA-256",
    )
    _sha256(
        value.get("preflight_canonical_sha256"),
        field="DEC-428 preflight canonical SHA-256",
    )
    return _source_blobs(value.get("review_source_blobs"))


def freeze_reviewed_active_one_shot_historical_executor_dispatch_preflight_proof(
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
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_FREEZE_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_PREFLIGHT_PROOF_REVIEWED_AND_FROZEN"
        ),
        "source_review_decision": reviewed_result["decision"],
        "source_review_version": reviewed_result["version"],
        "proof_workflow_name": reviewed_result["proof_workflow_name"],
        "proof_workflow_path": reviewed_result["proof_workflow_path"],
        "proof_run_id": reviewed_result["proof_run_id"],
        "proof_head_sha": expected_head_sha,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": reviewed_result["proof_job_id"],
        "proof_artifact_id": reviewed_result["proof_artifact_id"],
        "proof_artifact_name": reviewed_result["proof_artifact_name"],
        "proof_artifact_digest": reviewed_result["proof_artifact_digest"],
        "preflight_raw_sha256": reviewed_result["preflight_raw_sha256"],
        "preflight_canonical_sha256": reviewed_result[
            "preflight_canonical_sha256"
        ],
        "review_source_blobs": source_blobs,
        "dispatch_preflight_decision": reviewed_result[
            "dispatch_preflight_decision"
        ],
        "dispatch_preflight_version": reviewed_result[
            "dispatch_preflight_version"
        ],
        "install_receipt_decision": reviewed_result["install_receipt_decision"],
        "install_receipt_version": reviewed_result["install_receipt_version"],
        "dec424_install_receipt_blob_sha": reviewed_result[
            "dec424_install_receipt_blob_sha"
        ],
        "active_executor_workflow_blob_sha": reviewed_result[
            "active_executor_workflow_blob_sha"
        ],
        "active_executor_workflow_path": reviewed_result[
            "active_executor_workflow_path"
        ],
        "active_executor_workflow_present": True,
        "historical_executor_workflow_install_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "executor_workflow_run_count": 0,
        "historical_gate_proof_run_id": reviewed_result[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
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
            "CONCRETE_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BINDING_"
            "BEFORE_AUTHORIZATION"
        ),
    }
    frozen["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_FREEZE_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_FREEZE_VERSION",
    "freeze_reviewed_active_one_shot_historical_executor_dispatch_preflight_proof",
]
