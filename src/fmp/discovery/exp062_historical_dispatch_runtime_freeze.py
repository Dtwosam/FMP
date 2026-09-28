from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_dispatch_plan_freeze import (
    EXP062_REVIEWED_HISTORICAL_DISPATCH_PLAN_FREEZE_DECISION,
    EXP062_REVIEWED_HISTORICAL_DISPATCH_PLAN_FREEZE_VERSION,
    freeze_reviewed_historical_dispatch_plan,
)
from .exp062_historical_dispatch_plan_review import (
    EXP062_HISTORICAL_DISPATCH_PLAN_REVIEW_DECISION,
    EXP062_HISTORICAL_DISPATCH_PLAN_REVIEW_VERSION,
    review_historical_dispatch_plan_proof,
)


EXP062_HISTORICAL_DISPATCH_RUNTIME_FREEZE_DECISION = "DEC-323"
EXP062_HISTORICAL_DISPATCH_RUNTIME_FREEZE_VERSION = (
    "fmp-exp062-historical-dispatch-runtime-freeze-v1"
)

DISPATCH_PLAN_PROOF_HEAD_SHA = "fee1a78168254e7e8fecc104859d1a231b727243"
DISPATCH_PLAN_PROOF_RUN_ID = 36418793172
DISPATCH_PLAN_PROOF_JOB_ID = 108916232597
DISPATCH_PLAN_PROOF_ARTIFACT_ID = 10967344018
DISPATCH_PLAN_PROOF_ARTIFACT_NAME = (
    "exp062-dec320-historical-dispatch-plan-"
    "fee1a78168254e7e8fecc104859d1a231b727243"
)
DISPATCH_PLAN_PROOF_ARTIFACT_DIGEST = (
    "sha256:ca0f1156fab234327bbcdd9c3150cb7904ed6def230f035019b2139c4c523adf"
)
DISPATCH_PLAN_PROOF_ARTIFACT_ZIP_SHA256 = (
    "ca0f1156fab234327bbcdd9c3150cb7904ed6def230f035019b2139c4c523adf"
)
DISPATCH_PLAN_RAW_SHA256 = (
    "a6fa5f3a7f3f45df5d64efe1661a5b17887f88fded31e1cbb1620df5b18a95d1"
)
DISPATCH_PLAN_CANONICAL_SHA256 = (
    "41ca6c710d8750851350c2108b42970501a5efa14481cff61e2a66877ee90f6d"
)

DEC321_REVIEWER_BLOB_SHA = "8dee8008204ed816df211861ff4a7fb9e952d781"
DEC322_FREEZE_BUILDER_BLOB_SHA = (
    "6b7ab36c939fca7a9d53569e4617ebe6584e5b7c"
)
DEC322_FREEZE_FINGERPRINT_SHA256 = (
    "b7d3e5461511c8e14dd4402028ad24daefcf431cece3b59575588ba915db510e"
)

_FALSE_AUTHORITY_FIELDS = (
    "historical_result_dispatch_authorized",
    "historical_executor_available",
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


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def validate_historical_dispatch_runtime_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec321_reviewer": (
            root / "src/fmp/discovery/exp062_historical_dispatch_plan_review.py",
            DEC321_REVIEWER_BLOB_SHA,
        ),
        "dec322_freeze_builder": (
            root / "src/fmp/discovery/exp062_historical_dispatch_plan_freeze.py",
            DEC322_FREEZE_BUILDER_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-323 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-323 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _validate_reviewed_result(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": EXP062_HISTORICAL_DISPATCH_PLAN_REVIEW_DECISION,
            "version": EXP062_HISTORICAL_DISPATCH_PLAN_REVIEW_VERSION,
            "stage": (
                "EXP062_HISTORICAL_DISPATCH_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE"
            ),
            "proof_run_id": DISPATCH_PLAN_PROOF_RUN_ID,
            "proof_head_sha": DISPATCH_PLAN_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": DISPATCH_PLAN_PROOF_JOB_ID,
            "proof_artifact_id": DISPATCH_PLAN_PROOF_ARTIFACT_ID,
            "proof_artifact_name": DISPATCH_PLAN_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": DISPATCH_PLAN_PROOF_ARTIFACT_DIGEST,
            "plan_raw_sha256": DISPATCH_PLAN_RAW_SHA256,
            "plan_canonical_sha256": DISPATCH_PLAN_CANONICAL_SHA256,
            "plan_decision": "DEC-319",
            "plan_operator_version": (
                "fmp-exp062-historical-dispatch-operator-v1"
            ),
            "historical_gate_proof_run_id": 36358289723,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "one_shot_dispatch_source_authorized": True,
            "historical_result_dispatch_authorized": False,
            "historical_executor_available": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "next_gate": (
                "IMMUTABLE_HISTORICAL_DISPATCH_PLAN_PROOF_FREEZE_BEFORE_ONE_SHOT_EXECUTOR"
            ),
        },
        prefix="DEC-323 reviewed result",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-323 reviewed result {field} must remain false"
            )


def _validate_dec322_freeze(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_REVIEWED_HISTORICAL_DISPATCH_PLAN_FREEZE_DECISION
            ),
            "version": (
                EXP062_REVIEWED_HISTORICAL_DISPATCH_PLAN_FREEZE_VERSION
            ),
            "stage": "EXP062_HISTORICAL_DISPATCH_PLAN_REVIEWED_AND_FROZEN",
            "proof_run_id": DISPATCH_PLAN_PROOF_RUN_ID,
            "proof_head_sha": DISPATCH_PLAN_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": DISPATCH_PLAN_PROOF_JOB_ID,
            "proof_artifact_id": DISPATCH_PLAN_PROOF_ARTIFACT_ID,
            "proof_artifact_name": DISPATCH_PLAN_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": DISPATCH_PLAN_PROOF_ARTIFACT_DIGEST,
            "plan_raw_sha256": DISPATCH_PLAN_RAW_SHA256,
            "plan_canonical_sha256": DISPATCH_PLAN_CANONICAL_SHA256,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "planned_dispatch_command_frozen": (
                "gh workflow run phase8a-exp062-discovery.yml --ref main"
            ),
            "one_shot_dispatch_source_authorized": True,
            "historical_result_dispatch_authorized": False,
            "historical_executor_available": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "freeze_fingerprint_sha256": (
                DEC322_FREEZE_FINGERPRINT_SHA256
            ),
            "next_gate": (
                "CONCRETE_DISPATCH_PLAN_RUNTIME_EVIDENCE_BINDING_BEFORE_ONE_SHOT_EXECUTOR"
            ),
        },
        prefix="DEC-323 DEC-322 freeze",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-323 DEC-322 freeze {field} must remain false"
            )

    unsigned = dict(value)
    fingerprint = unsigned.pop("freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC322_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC322_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-323 DEC-322 freeze fingerprint mismatch")


def freeze_historical_dispatch_runtime_evidence(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    plan_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = validate_historical_dispatch_runtime_freeze_sources(
        repository_root=repository_root,
    )

    reviewed = review_historical_dispatch_plan_proof(
        run=proof_run,
        jobs_payload=proof_jobs_payload,
        artifacts_payload=proof_artifacts_payload,
        plan_bytes=plan_bytes,
        expected_head_sha=DISPATCH_PLAN_PROOF_HEAD_SHA,
        repository_root=repository_root,
    )
    _validate_reviewed_result(reviewed)

    frozen_review = freeze_reviewed_historical_dispatch_plan(
        reviewed,
        expected_head_sha=DISPATCH_PLAN_PROOF_HEAD_SHA,
    )
    _validate_dec322_freeze(frozen_review)

    artifact_zip_sha256 = _validate_sha256(
        artifact_zip_sha256,
        field="DEC-323 artifact ZIP sha256",
    )
    if artifact_zip_sha256 != DISPATCH_PLAN_PROOF_ARTIFACT_ZIP_SHA256:
        raise ValueError("DEC-323 artifact ZIP sha256 mismatch")
    if artifact_zip_sha256 != DISPATCH_PLAN_PROOF_ARTIFACT_DIGEST.removeprefix(
        "sha256:"
    ):
        raise ValueError(
            "DEC-323 artifact ZIP hash does not match GitHub digest"
        )

    frozen: dict[str, object] = {
        "decision": EXP062_HISTORICAL_DISPATCH_RUNTIME_FREEZE_DECISION,
        "version": EXP062_HISTORICAL_DISPATCH_RUNTIME_FREEZE_VERSION,
        "stage": (
            "EXP062_HISTORICAL_DISPATCH_PLAN_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "dispatch_plan_proof_head_sha": DISPATCH_PLAN_PROOF_HEAD_SHA,
        "dispatch_plan_proof_run_id": DISPATCH_PLAN_PROOF_RUN_ID,
        "dispatch_plan_proof_run_number": 1,
        "dispatch_plan_proof_run_attempt": 1,
        "dispatch_plan_proof_run_conclusion": "success",
        "dispatch_plan_proof_job_id": DISPATCH_PLAN_PROOF_JOB_ID,
        "dispatch_plan_proof_artifact_id": DISPATCH_PLAN_PROOF_ARTIFACT_ID,
        "dispatch_plan_proof_artifact_name": DISPATCH_PLAN_PROOF_ARTIFACT_NAME,
        "dispatch_plan_proof_artifact_digest": (
            DISPATCH_PLAN_PROOF_ARTIFACT_DIGEST
        ),
        "dispatch_plan_proof_artifact_zip_sha256": (
            DISPATCH_PLAN_PROOF_ARTIFACT_ZIP_SHA256
        ),
        "dispatch_plan_raw_sha256": DISPATCH_PLAN_RAW_SHA256,
        "dispatch_plan_canonical_sha256": DISPATCH_PLAN_CANONICAL_SHA256,
        "dec321_review_decision": reviewed["decision"],
        "dec321_review_version": reviewed["version"],
        "dec322_freeze_decision": frozen_review["decision"],
        "dec322_freeze_version": frozen_review["version"],
        "dec322_freeze_fingerprint_sha256": (
            DEC322_FREEZE_FINGERPRINT_SHA256
        ),
        "dec321_reviewer_blob_sha": source_blobs["dec321_reviewer"],
        "dec322_freeze_builder_blob_sha": source_blobs[
            "dec322_freeze_builder"
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
        "one_shot_dispatch_source_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_executor_available": False,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_CONTRACT"
        ),
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "DEC322_FREEZE_FINGERPRINT_SHA256",
    "DISPATCH_PLAN_CANONICAL_SHA256",
    "DISPATCH_PLAN_PROOF_ARTIFACT_DIGEST",
    "DISPATCH_PLAN_PROOF_ARTIFACT_ID",
    "DISPATCH_PLAN_PROOF_HEAD_SHA",
    "DISPATCH_PLAN_PROOF_JOB_ID",
    "DISPATCH_PLAN_PROOF_RUN_ID",
    "DISPATCH_PLAN_RAW_SHA256",
    "EXP062_HISTORICAL_DISPATCH_RUNTIME_FREEZE_DECISION",
    "EXP062_HISTORICAL_DISPATCH_RUNTIME_FREEZE_VERSION",
    "freeze_historical_dispatch_runtime_evidence",
    "validate_historical_dispatch_runtime_freeze_sources",
]
