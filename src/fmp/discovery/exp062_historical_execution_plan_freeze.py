from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .exp062_historical_execution_plan_review import (
    EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_DECISION,
    EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_VERSION,
)


EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_DECISION = "DEC-316"
EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_VERSION = (
    "fmp-exp062-reviewed-historical-execution-plan-freeze-v1"
)

_EXPECTED_REVIEW_SOURCE_BLOBS = {
    "plan_proof_workflow": "d2b2e4fcc2a39e614dda98c890ec13b6387725e8",
    "execution_operator": "7f21ccf59de9605c7fab45b4506f947ffae69cab",
    "execution_operator_cli": "9ecb3f47d7e68461e4a7d893ad5862d7e78a1fc8",
    "execution_authorization": "aa8cfb25e3d78c0c72da4b22898c1263a42548ba",
    "activated_cli": "773784d0770d54b1d3e41fba2057b9314a090034",
    "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
    "historical_plan_freeze": "e3274118b37066efe2869d554e78e6b68e64b32a",
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


def _validate_positive_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must contain 64 hex characters")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_sha256_digest(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"{field} must use sha256:<hex>")
    _validate_sha256(value.removeprefix("sha256:"), field=field)
    return value.lower()


def _validate_review_source_blobs(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-316 review_source_blobs must be a mapping")
    actual = dict(value)
    if actual != _EXPECTED_REVIEW_SOURCE_BLOBS:
        raise ValueError("DEC-316 review_source_blobs mismatch")
    return {str(key): str(blob) for key, blob in actual.items()}


def _validate_reviewed_result(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> None:
    exact = {
        "decision": EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_DECISION,
        "version": EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_VERSION,
        "stage": (
            "EXP062_HISTORICAL_EXECUTION_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE"
        ),
        "proof_workflow_name": "phase8a-exp062-historical-execution-plan",
        "proof_workflow_path": (
            ".github/workflows/phase8a-exp062-historical-execution-plan.yml"
        ),
        "proof_head_sha": expected_head_sha,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "plan_decision": "DEC-313",
        "plan_operator_version": (
            "fmp-exp062-historical-execution-operator-v1"
        ),
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "historical_execution_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "next_gate": (
            "IMMUTABLE_HISTORICAL_EXECUTION_PLAN_PROOF_FREEZE_BEFORE_DISPATCH_AUTHORIZATION"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-316 reviewed result {field} mismatch")

    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-316 reviewed result {field} must remain false"
            )

    _validate_positive_int(
        value.get("proof_run_id"),
        field="DEC-316 proof_run_id",
    )
    _validate_positive_int(
        value.get("proof_job_id"),
        field="DEC-316 proof_job_id",
    )
    _validate_positive_int(
        value.get("proof_artifact_id"),
        field="DEC-316 proof_artifact_id",
    )
    artifact_name = value.get("proof_artifact_name")
    if artifact_name != (
        f"exp062-dec314-historical-execution-plan-{expected_head_sha}"
    ):
        raise ValueError("DEC-316 proof_artifact_name mismatch")
    _validate_sha256_digest(
        value.get("proof_artifact_digest"),
        field="DEC-316 proof_artifact_digest",
    )
    _validate_sha256(
        value.get("plan_raw_sha256"),
        field="DEC-316 plan_raw_sha256",
    )
    _validate_sha256(
        value.get("plan_canonical_sha256"),
        field="DEC-316 plan_canonical_sha256",
    )
    _validate_review_source_blobs(value.get("review_source_blobs"))


def freeze_reviewed_historical_execution_plan(
    reviewed_result: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    _validate_reviewed_result(
        reviewed_result,
        expected_head_sha=expected_head_sha,
    )
    source_blobs = _validate_review_source_blobs(
        reviewed_result.get("review_source_blobs")
    )

    frozen: dict[str, object] = {
        "decision": (
            EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_DECISION
        ),
        "version": (
            EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_HISTORICAL_EXECUTION_PLAN_REVIEWED_AND_FROZEN"
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
        "plan_raw_sha256": reviewed_result["plan_raw_sha256"],
        "plan_canonical_sha256": reviewed_result[
            "plan_canonical_sha256"
        ],
        "review_source_blobs": source_blobs,
        "plan_decision": reviewed_result["plan_decision"],
        "plan_operator_version": reviewed_result["plan_operator_version"],
        "historical_gate_proof_run_id": reviewed_result[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "historical_execution_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "historical_result_dispatch_authorized": False,
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
            "CONCRETE_RUNTIME_EVIDENCE_BINDING_BEFORE_ONE_SHOT_DISPATCH"
        ),
    }
    frozen["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_DECISION",
    "EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_VERSION",
    "freeze_reviewed_historical_execution_plan",
]
