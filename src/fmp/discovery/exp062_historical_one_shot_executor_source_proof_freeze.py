from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .exp062_historical_one_shot_executor_source_proof_review import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION,
)


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION = "DEC-340"
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_VERSION = (
    "fmp-exp062-one-shot-historical-executor-source-proof-freeze-v1"
)

_EXPECTED_REVIEW_SOURCE_BLOBS = {
    "dec338_workflow": "3104d6521e1c11f0c8be92eab0eef21c5e9eb80c",
    "dec337_source": "26ee48241550d6e52501fc901ab88aaa3f42e755",
    "dec336_runtime_freeze": "9673e115eeb373c4881d36a8b5d91a2801cd8ad1",
    "dec334_terminal_review": "fda2a45f74b101303467cf7b8527bec1bfc5e168",
    "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
}

_FALSE_AUTHORITY_FIELDS = (
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


def _validate_source_blobs(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-340 review_source_blobs must be a mapping")
    actual = dict(value)
    if actual != _EXPECTED_REVIEW_SOURCE_BLOBS:
        raise ValueError("DEC-340 review_source_blobs mismatch")
    return {str(k): str(v) for k, v in actual.items()}


def _validate_reviewed_result(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> None:
    exact = {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "REVIEWED_SLOT_AVAILABLE"
        ),
        "proof_workflow_name": (
            "phase8a-exp062-one-shot-historical-executor-source-proof"
        ),
        "proof_workflow_path": (
            ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor-source-proof.yml"
        ),
        "proof_head_sha": expected_head_sha,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "source_contract_decision": "DEC-337",
        "source_contract_version": (
            "fmp-exp062-one-shot-historical-executor-source-v1"
        ),
        "runtime_freeze_decision": "DEC-336",
        "runtime_freeze_fingerprint_sha256": (
            "147ab77116979afa8d0d07c3c748fb80e02865a382317824320f6af534bfc374"
        ),
        "terminal_review_decision": "DEC-334",
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "one_shot_historical_executor_source_authorized": True,
        "historical_executor_available": False,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "next_gate": (
            "IMMUTABLE_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "FREEZE_BEFORE_EXECUTOR_WORKFLOW"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-340 reviewed result {field} mismatch")

    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-340 reviewed result {field} must remain false"
            )

    _validate_positive_int(value.get("proof_run_id"), field="DEC-340 proof_run_id")
    _validate_positive_int(value.get("proof_job_id"), field="DEC-340 proof_job_id")
    _validate_positive_int(
        value.get("proof_artifact_id"),
        field="DEC-340 proof_artifact_id",
    )
    artifact_name = value.get("proof_artifact_name")
    if artifact_name != (
        "exp062-dec338-one-shot-historical-executor-source-"
        f"{expected_head_sha}"
    ):
        raise ValueError("DEC-340 proof_artifact_name mismatch")
    _validate_sha256_digest(
        value.get("proof_artifact_digest"),
        field="DEC-340 proof_artifact_digest",
    )
    _validate_sha256(
        value.get("contract_raw_sha256"),
        field="DEC-340 contract_raw_sha256",
    )
    _validate_sha256(
        value.get("contract_canonical_sha256"),
        field="DEC-340 contract_canonical_sha256",
    )
    _validate_source_blobs(value.get("review_source_blobs"))


def freeze_reviewed_one_shot_historical_executor_source_proof(
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
    source_blobs = _validate_source_blobs(
        reviewed_result.get("review_source_blobs")
    )

    frozen: dict[str, object] = {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
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
        "contract_raw_sha256": reviewed_result["contract_raw_sha256"],
        "contract_canonical_sha256": reviewed_result[
            "contract_canonical_sha256"
        ],
        "review_source_blobs": source_blobs,
        "source_contract_decision": reviewed_result[
            "source_contract_decision"
        ],
        "source_contract_version": reviewed_result[
            "source_contract_version"
        ],
        "runtime_freeze_decision": reviewed_result[
            "runtime_freeze_decision"
        ],
        "runtime_freeze_fingerprint_sha256": reviewed_result[
            "runtime_freeze_fingerprint_sha256"
        ],
        "terminal_review_decision": reviewed_result[
            "terminal_review_decision"
        ],
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
        "one_shot_historical_executor_source_authorized": True,
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
            "CONCRETE_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "RUNTIME_EVIDENCE_BINDING_BEFORE_EXECUTOR_WORKFLOW"
        ),
    }
    frozen["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_VERSION",
    "freeze_reviewed_one_shot_historical_executor_source_proof",
]
