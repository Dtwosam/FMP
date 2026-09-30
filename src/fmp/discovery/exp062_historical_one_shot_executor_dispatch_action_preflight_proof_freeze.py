from __future__ import annotations

import hashlib
import json
from typing import Mapping


EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_FREEZE_DECISION = (
    "DEC-434"
)
EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_FREEZE_VERSION = (
    "fmp-exp062-one-shot-executor-dispatch-action-preflight-proof-freeze-v1"
)

_EXPECTED_SOURCE_BLOBS = {
    "dec432_workflow": "29dc3eb49c5c682cb74cd80ed104d3c584859314",
    "dec431_preflight": "93ab88965e74df0b067ba09dbbb8d0622c53e578",
    "dec431_preflight_cli": "df486dd739952ab10b9ff31d6c35a01eab38618e",
    "dec430_authorization": "87aada4c5224c633e8eb419f971c8f7f0699b18f",
    "active_executor_workflow": "51ce87584369be957482460d81649adb1cb9f05d",
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
        raise ValueError("DEC-434 review_source_blobs must be an object")
    actual = dict(value)
    if actual != _EXPECTED_SOURCE_BLOBS:
        raise ValueError("DEC-434 review_source_blobs mismatch")
    return {str(key): str(val) for key, val in actual.items()}


def _validate_review(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> dict[str, str]:
    exact = {
        "decision": "DEC-433",
        "version": (
            "fmp-exp062-one-shot-executor-dispatch-action-preflight-"
            "proof-review-v1"
        ),
        "stage": (
            "EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_"
            "PROOF_REVIEWED_AUTHORIZED_RUN_NOT_STARTED"
        ),
        "proof_workflow_name": (
            "phase8a-exp062-one-shot-executor-dispatch-action-preflight-proof"
        ),
        "proof_workflow_path": (
            ".github/workflows/"
            "phase8a-exp062-one-shot-executor-dispatch-action-preflight-proof.yml"
        ),
        "proof_head_sha": expected_head_sha,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "action_preflight_decision": "DEC-431",
        "action_preflight_version": (
            "fmp-exp062-active-one-shot-historical-executor-"
            "dispatch-action-preflight-v1"
        ),
        "authorization_decision": "DEC-430",
        "authorization_version": (
            "fmp-exp062-active-one-shot-historical-executor-"
            "dispatch-authorization-v1"
        ),
        "dec430_dispatch_authorization_blob_sha": (
            "87aada4c5224c633e8eb419f971c8f7f0699b18f"
        ),
        "active_executor_workflow_blob_sha": (
            "51ce87584369be957482460d81649adb1cb9f05d"
        ),
        "active_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "active_executor_workflow_present": True,
        "executor_workflow_run_count": 0,
        "expected_executor_run_number": 1,
        "expected_executor_run_attempt": 1,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_executor_dispatch_command": (
            "gh workflow run "
            "phase8a-exp062-one-shot-historical-executor.yml --ref main"
        ),
        "explicit_one_shot_executor_dispatch_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "historical_result_dispatch_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "next_gate": (
            "IMMUTABLE_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_"
            "PROOF_FREEZE_BEFORE_RUN"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-434 review {field} mismatch")
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-434 review {field} must remain false")

    _positive_int(value.get("proof_run_id"), field="DEC-434 proof run id")
    _positive_int(value.get("proof_job_id"), field="DEC-434 proof job id")
    _positive_int(value.get("proof_artifact_id"), field="DEC-434 proof artifact id")
    _sha256_digest(
        value.get("proof_artifact_digest"),
        field="DEC-434 proof artifact digest",
    )
    _sha256(
        value.get("preflight_raw_sha256"),
        field="DEC-434 preflight raw SHA-256",
    )
    _sha256(
        value.get("preflight_canonical_sha256"),
        field="DEC-434 preflight canonical SHA-256",
    )
    return _source_blobs(value.get("review_source_blobs"))


def freeze_reviewed_one_shot_executor_dispatch_action_preflight_proof(
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
            EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_FREEZE_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_"
            "PROOF_REVIEWED_AND_FROZEN_AUTHORIZED_RUN_NOT_STARTED"
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
        "action_preflight_decision": reviewed_result[
            "action_preflight_decision"
        ],
        "action_preflight_version": reviewed_result[
            "action_preflight_version"
        ],
        "authorization_decision": reviewed_result["authorization_decision"],
        "authorization_version": reviewed_result["authorization_version"],
        "dec430_dispatch_authorization_blob_sha": reviewed_result[
            "dec430_dispatch_authorization_blob_sha"
        ],
        "active_executor_workflow_blob_sha": reviewed_result[
            "active_executor_workflow_blob_sha"
        ],
        "active_executor_workflow_path": reviewed_result[
            "active_executor_workflow_path"
        ],
        "active_executor_workflow_present": True,
        "executor_workflow_run_count": 0,
        "expected_executor_run_number": 1,
        "expected_executor_run_attempt": 1,
        "historical_gate_proof_run_id": reviewed_result[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_executor_dispatch_command": reviewed_result[
            "planned_executor_dispatch_command"
        ],
        "explicit_one_shot_executor_dispatch_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "historical_result_dispatch_authorized": True,
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
            "CONCRETE_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_"
            "PROOF_RUNTIME_EVIDENCE_BINDING_BEFORE_RUN"
        ),
    }
    frozen["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_FREEZE_DECISION",
    "EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_FREEZE_VERSION",
    "freeze_reviewed_one_shot_executor_dispatch_action_preflight_proof",
]
