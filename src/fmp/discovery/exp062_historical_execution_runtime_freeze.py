from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_execution_plan_freeze import (
    EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_DECISION,
    EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_VERSION,
    freeze_reviewed_historical_execution_plan,
)
from .exp062_historical_execution_plan_review import (
    EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_DECISION,
    EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_VERSION,
    review_historical_execution_plan_proof,
)


EXP062_HISTORICAL_EXECUTION_RUNTIME_FREEZE_DECISION = "DEC-317"
EXP062_HISTORICAL_EXECUTION_RUNTIME_FREEZE_VERSION = (
    "fmp-exp062-historical-execution-runtime-freeze-v1"
)

PLAN_PROOF_HEAD_SHA = "ea69e82c9f653facba8ed6589fe4243848187ad3"
PLAN_PROOF_RUN_ID = 36414282818
PLAN_PROOF_JOB_ID = 108901556593
PLAN_PROOF_ARTIFACT_ID = 10966632240
PLAN_PROOF_ARTIFACT_NAME = (
    "exp062-dec314-historical-execution-plan-"
    "ea69e82c9f653facba8ed6589fe4243848187ad3"
)
PLAN_PROOF_ARTIFACT_DIGEST = (
    "sha256:9299ebfd344c0bd2a66ccd6e29339e035840c8b4204cbfc16bb6d3e938a53254"
)
PLAN_PROOF_ARTIFACT_ZIP_SHA256 = (
    "9299ebfd344c0bd2a66ccd6e29339e035840c8b4204cbfc16bb6d3e938a53254"
)
PLAN_RAW_SHA256 = (
    "594b5bd129a93ad7b07f69e00826251dd693f1bb388e6b4dff64eda0b34a7c72"
)
PLAN_CANONICAL_SHA256 = (
    "152bbb90efe3941f1338c73cf24f91f10a877cda3ee5c46f08c4f556d653a12f"
)

DEC315_REVIEWER_BLOB_SHA = "284789801505b9391be19ebb1a19c4fae28e2444"
DEC316_FREEZE_BUILDER_BLOB_SHA = (
    "2867bc05986bf93dc531d152760bbbac604854fe"
)
DEC316_FREEZE_FINGERPRINT_SHA256 = (
    "7c7d99f4c89aac4e11d27536b9f8d2d39322672a9a0332f141d1d86f93b19be3"
)

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


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must contain 64 hex characters")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_historical_execution_runtime_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec315_reviewer": (
            root / "src/fmp/discovery/exp062_historical_execution_plan_review.py",
            DEC315_REVIEWER_BLOB_SHA,
        ),
        "dec316_freeze_builder": (
            root / "src/fmp/discovery/exp062_historical_execution_plan_freeze.py",
            DEC316_FREEZE_BUILDER_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-317 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-317 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def _validate_reviewed_result(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_DECISION,
            "version": EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_VERSION,
            "stage": (
                "EXP062_HISTORICAL_EXECUTION_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE"
            ),
            "proof_run_id": PLAN_PROOF_RUN_ID,
            "proof_head_sha": PLAN_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": PLAN_PROOF_JOB_ID,
            "proof_artifact_id": PLAN_PROOF_ARTIFACT_ID,
            "proof_artifact_name": PLAN_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": PLAN_PROOF_ARTIFACT_DIGEST,
            "plan_raw_sha256": PLAN_RAW_SHA256,
            "plan_canonical_sha256": PLAN_CANONICAL_SHA256,
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
        },
        prefix="DEC-317 reviewed result",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-317 reviewed result {field} must remain false"
            )


def _validate_dec316_freeze(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_DECISION
            ),
            "version": (
                EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_VERSION
            ),
            "stage": (
                "EXP062_HISTORICAL_EXECUTION_PLAN_REVIEWED_AND_FROZEN"
            ),
            "proof_run_id": PLAN_PROOF_RUN_ID,
            "proof_head_sha": PLAN_PROOF_HEAD_SHA,
            "proof_job_id": PLAN_PROOF_JOB_ID,
            "proof_artifact_id": PLAN_PROOF_ARTIFACT_ID,
            "proof_artifact_name": PLAN_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": PLAN_PROOF_ARTIFACT_DIGEST,
            "plan_raw_sha256": PLAN_RAW_SHA256,
            "plan_canonical_sha256": PLAN_CANONICAL_SHA256,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "historical_execution_source_authorized": True,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "freeze_fingerprint_sha256": (
                DEC316_FREEZE_FINGERPRINT_SHA256
            ),
            "next_gate": (
                "CONCRETE_RUNTIME_EVIDENCE_BINDING_BEFORE_ONE_SHOT_DISPATCH"
            ),
        },
        prefix="DEC-317 DEC-316 freeze",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-317 DEC-316 freeze {field} must remain false"
            )

    unsigned = dict(value)
    fingerprint = unsigned.pop("freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC316_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC316_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-317 DEC-316 freeze fingerprint mismatch")


def freeze_historical_execution_runtime_evidence(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    plan_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = validate_historical_execution_runtime_freeze_sources(
        repository_root=repository_root,
    )

    reviewed = review_historical_execution_plan_proof(
        run=proof_run,
        jobs_payload=proof_jobs_payload,
        artifacts_payload=proof_artifacts_payload,
        plan_bytes=plan_bytes,
        expected_head_sha=PLAN_PROOF_HEAD_SHA,
        repository_root=repository_root,
    )
    _validate_reviewed_result(reviewed)

    frozen_review = freeze_reviewed_historical_execution_plan(
        reviewed,
        expected_head_sha=PLAN_PROOF_HEAD_SHA,
    )
    _validate_dec316_freeze(frozen_review)

    artifact_zip_sha256 = _validate_sha256(
        artifact_zip_sha256,
        field="DEC-317 artifact ZIP sha256",
    )
    if artifact_zip_sha256 != PLAN_PROOF_ARTIFACT_ZIP_SHA256:
        raise ValueError("DEC-317 artifact ZIP sha256 mismatch")
    if artifact_zip_sha256 != PLAN_PROOF_ARTIFACT_DIGEST.removeprefix(
        "sha256:"
    ):
        raise ValueError(
            "DEC-317 artifact ZIP hash does not match GitHub digest"
        )

    frozen: dict[str, object] = {
        "decision": EXP062_HISTORICAL_EXECUTION_RUNTIME_FREEZE_DECISION,
        "version": EXP062_HISTORICAL_EXECUTION_RUNTIME_FREEZE_VERSION,
        "stage": (
            "EXP062_HISTORICAL_EXECUTION_PLAN_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "plan_proof_head_sha": PLAN_PROOF_HEAD_SHA,
        "plan_proof_run_id": PLAN_PROOF_RUN_ID,
        "plan_proof_run_number": 1,
        "plan_proof_run_attempt": 1,
        "plan_proof_run_conclusion": "success",
        "plan_proof_job_id": PLAN_PROOF_JOB_ID,
        "plan_proof_artifact_id": PLAN_PROOF_ARTIFACT_ID,
        "plan_proof_artifact_name": PLAN_PROOF_ARTIFACT_NAME,
        "plan_proof_artifact_digest": PLAN_PROOF_ARTIFACT_DIGEST,
        "plan_proof_artifact_zip_sha256": PLAN_PROOF_ARTIFACT_ZIP_SHA256,
        "plan_raw_sha256": PLAN_RAW_SHA256,
        "plan_canonical_sha256": PLAN_CANONICAL_SHA256,
        "dec315_review_decision": reviewed["decision"],
        "dec315_review_version": reviewed["version"],
        "dec316_freeze_decision": frozen_review["decision"],
        "dec316_freeze_version": frozen_review["version"],
        "dec316_freeze_fingerprint_sha256": (
            DEC316_FREEZE_FINGERPRINT_SHA256
        ),
        "dec315_reviewer_blob_sha": source_blobs["dec315_reviewer"],
        "dec316_freeze_builder_blob_sha": source_blobs[
            "dec316_freeze_builder"
        ],
        "historical_gate_proof_run_id": reviewed[
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_DISPATCH_AUTHORIZATION_CONTRACT"
        ),
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "DEC316_FREEZE_FINGERPRINT_SHA256",
    "EXP062_HISTORICAL_EXECUTION_RUNTIME_FREEZE_DECISION",
    "EXP062_HISTORICAL_EXECUTION_RUNTIME_FREEZE_VERSION",
    "PLAN_CANONICAL_SHA256",
    "PLAN_PROOF_ARTIFACT_DIGEST",
    "PLAN_PROOF_ARTIFACT_ID",
    "PLAN_PROOF_HEAD_SHA",
    "PLAN_PROOF_JOB_ID",
    "PLAN_PROOF_RUN_ID",
    "PLAN_RAW_SHA256",
    "freeze_historical_execution_runtime_evidence",
    "validate_historical_execution_runtime_freeze_sources",
]
