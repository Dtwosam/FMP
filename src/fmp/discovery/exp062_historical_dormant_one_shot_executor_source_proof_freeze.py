from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .exp062_historical_dormant_one_shot_executor_source_proof_review import (
    EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION,
    EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION,
)


EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION = "DEC-358"
EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_VERSION = (
    "fmp-exp062-dormant-one-shot-historical-executor-source-proof-freeze-v1"
)

_EXPECTED_REVIEW_SOURCE_BLOBS = {
    "dec356_workflow": "1cf665417e32c6810bf8ff62e5bc4a3b7a1ac598",
    "dec355_source": "0672310946ab6bb3b77d2de5c4ea5d68e41f810a",
    "dec354_installation_source_contract": (
        "e4fc6a7d1faaca50bc6936597f0e8b66fe096985"
    ),
    "dormant_executor_workflow_template": (
        "51ce87584369be957482460d81649adb1cb9f05d"
    ),
    "active_discovery_workflow": (
        "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
    ),
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
        raise ValueError("DEC-358 review_source_blobs must be a mapping")
    actual = dict(value)
    if actual != _EXPECTED_REVIEW_SOURCE_BLOBS:
        raise ValueError("DEC-358 review_source_blobs mismatch")
    return {str(k): str(v) for k, v in actual.items()}


def _validate_review(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> None:
    exact = {
        "decision": (
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION
        ),
        "version": (
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION
        ),
        "stage": (
            "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "REVIEWED_ACTIVE_WORKFLOW_UNINSTALLED"
        ),
        "proof_workflow_name": (
            "phase8a-exp062-dormant-one-shot-historical-executor-"
            "workflow-source-proof"
        ),
        "proof_workflow_path": (
            ".github/workflows/"
            "phase8a-exp062-dormant-one-shot-historical-executor-"
            "workflow-source-proof.yml"
        ),
        "proof_head_sha": expected_head_sha,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "dormant_source_decision": "DEC-355",
        "dormant_source_version": (
            "fmp-exp062-one-shot-historical-executor-dormant-workflow-source-v1"
        ),
        "dormant_executor_workflow_template_blob_sha": (
            "51ce87584369be957482460d81649adb1cb9f05d"
        ),
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "dormant_executor_workflow_template_present": True,
        "dormant_template_dispatch_capable_if_installed": True,
        "dormant_template_actions_write_required_if_installed": True,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "historical_executor_workflow_install_authorized": False,
        "historical_executor_workflow_installed": False,
        "historical_executor_available": False,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "next_gate": (
            "IMMUTABLE_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "SOURCE_PROOF_FREEZE_BEFORE_INSTALL"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-358 reviewed result {field} mismatch")
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-358 reviewed result {field} must remain false")

    _positive_int(value.get("proof_run_id"), field="DEC-358 proof_run_id")
    _positive_int(value.get("proof_job_id"), field="DEC-358 proof_job_id")
    _positive_int(
        value.get("proof_artifact_id"),
        field="DEC-358 proof_artifact_id",
    )
    if value.get("proof_artifact_name") != (
        "exp062-dec356-dormant-one-shot-historical-executor-source-"
        f"{expected_head_sha}"
    ):
        raise ValueError("DEC-358 proof_artifact_name mismatch")
    _sha256_digest(
        value.get("proof_artifact_digest"),
        field="DEC-358 proof_artifact_digest",
    )
    _sha256(value.get("source_raw_sha256"), field="DEC-358 source_raw_sha256")
    _sha256(
        value.get("source_canonical_sha256"),
        field="DEC-358 source_canonical_sha256",
    )
    _source_blobs(value.get("review_source_blobs"))


def freeze_reviewed_dormant_one_shot_historical_executor_source_proof(
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
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION
        ),
        "version": (
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "REVIEWED_AND_FROZEN"
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
        "source_raw_sha256": reviewed_result["source_raw_sha256"],
        "source_canonical_sha256": reviewed_result["source_canonical_sha256"],
        "review_source_blobs": source_blobs,
        "dormant_source_decision": reviewed_result["dormant_source_decision"],
        "dormant_source_version": reviewed_result["dormant_source_version"],
        "dormant_executor_workflow_template_blob_sha": reviewed_result[
            "dormant_executor_workflow_template_blob_sha"
        ],
        "expected_executor_workflow_path": reviewed_result[
            "expected_executor_workflow_path"
        ],
        "dormant_executor_workflow_template_present": True,
        "dormant_template_dispatch_capable_if_installed": True,
        "dormant_template_actions_write_required_if_installed": True,
        "historical_gate_proof_run_id": reviewed_result[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
            "CONCRETE_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "RUNTIME_EVIDENCE_BINDING_BEFORE_INSTALL"
        ),
    }
    frozen["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION",
    "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_VERSION",
    "freeze_reviewed_dormant_one_shot_historical_executor_source_proof",
]
