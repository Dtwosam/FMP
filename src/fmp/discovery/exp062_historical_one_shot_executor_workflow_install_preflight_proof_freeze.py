from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .exp062_historical_one_shot_executor_workflow_install_preflight_proof_review import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_REVIEW_DECISION,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_REVIEW_VERSION,
)


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_DECISION = (
    "DEC-352"
)
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_VERSION = (
    "fmp-exp062-one-shot-historical-executor-workflow-install-preflight-proof-freeze-v1"
)

_EXPECTED_REVIEW_SOURCE_BLOBS = {
    "dec350_workflow": "e35c61e91475078f2c40d971c683b899e298c6c3",
    "dec349_preflight": "e91b032a4e5e43e5fae5e4f6cc677501cabc8381",
    "dec349_preflight_cli": "431cc88658dddfb29c698f026851e78d4574f8a2",
    "dec348_install_contract": "111a56fdbb8844c119307465e7b7cf6a4d43d95a",
    "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
}

_FALSE_AUTHORITY_FIELDS = (
    "historical_executor_workflow_install_authorized",
    "historical_executor_workflow_installed",
    "historical_executor_available",
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
        raise ValueError(f"{field} must contain 64 hex characters")
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
        raise ValueError("DEC-352 review_source_blobs must be a mapping")
    actual = dict(value)
    if actual != _EXPECTED_REVIEW_SOURCE_BLOBS:
        raise ValueError("DEC-352 review_source_blobs mismatch")
    return {str(k): str(v) for k, v in actual.items()}


def _validate_review(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> None:
    exact = {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_REVIEW_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_REVIEW_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_"
            "PROOF_REVIEWED_SOURCE_ABSENT_SLOT_AVAILABLE"
        ),
        "proof_workflow_name": (
            "phase8a-exp062-one-shot-historical-executor-"
            "workflow-install-preflight-proof"
        ),
        "proof_workflow_path": (
            ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor-"
            "workflow-install-preflight-proof.yml"
        ),
        "proof_head_sha": expected_head_sha,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "workflow_install_preflight_decision": "DEC-349",
        "workflow_install_preflight_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-install-preflight-v1"
        ),
        "install_contract_decision": "DEC-348",
        "install_contract_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-install-contract-v1"
        ),
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "executor_workflow_path_exists": False,
        "workflow_install_slot_verified_available": True,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "one_shot_historical_executor_workflow_install_source_authorized": True,
        "historical_executor_workflow_install_authorized": False,
        "historical_executor_workflow_installed": False,
        "historical_executor_available": False,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "next_gate": (
            "IMMUTABLE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "PREFLIGHT_PROOF_FREEZE_BEFORE_WORKFLOW_INSTALL"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-352 reviewed result {field} mismatch")
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-352 reviewed result {field} must remain false")

    _positive_int(value.get("proof_run_id"), field="DEC-352 proof_run_id")
    _positive_int(value.get("proof_job_id"), field="DEC-352 proof_job_id")
    _positive_int(
        value.get("proof_artifact_id"),
        field="DEC-352 proof_artifact_id",
    )
    if value.get("proof_artifact_name") != (
        "exp062-dec350-one-shot-historical-executor-workflow-install-preflight-"
        f"{expected_head_sha}"
    ):
        raise ValueError("DEC-352 proof_artifact_name mismatch")
    _sha256_digest(
        value.get("proof_artifact_digest"),
        field="DEC-352 proof_artifact_digest",
    )
    _sha256(
        value.get("preflight_raw_sha256"),
        field="DEC-352 preflight_raw_sha256",
    )
    _sha256(
        value.get("preflight_canonical_sha256"),
        field="DEC-352 preflight_canonical_sha256",
    )
    _source_blobs(value.get("review_source_blobs"))


def freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof(
    reviewed_result: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    _validate_review(reviewed_result, expected_head_sha=expected_head_sha)
    source_blobs = _source_blobs(reviewed_result.get("review_source_blobs"))

    frozen: dict[str, object] = {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_"
            "PROOF_REVIEWED_AND_FROZEN"
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
        "workflow_install_preflight_decision": reviewed_result[
            "workflow_install_preflight_decision"
        ],
        "workflow_install_preflight_version": reviewed_result[
            "workflow_install_preflight_version"
        ],
        "install_contract_decision": reviewed_result[
            "install_contract_decision"
        ],
        "install_contract_version": reviewed_result[
            "install_contract_version"
        ],
        "expected_executor_workflow_path": reviewed_result[
            "expected_executor_workflow_path"
        ],
        "executor_workflow_path_exists": False,
        "workflow_install_slot_verified_available": True,
        "historical_gate_proof_run_id": reviewed_result[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "one_shot_historical_executor_workflow_install_source_authorized": True,
        "historical_executor_workflow_install_authorized": False,
        "historical_executor_workflow_installed": False,
        "historical_executor_available": False,
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
            "CONCRETE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BINDING_BEFORE_WORKFLOW_INSTALL"
        ),
    }
    frozen["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_VERSION",
    "freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof",
]
