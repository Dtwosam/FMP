from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_operator import (
    EXP062_HISTORICAL_OPERATOR_DECISION,
    EXP062_HISTORICAL_OPERATOR_VERSION,
    historical_dispatch_command,
    shell_join,
)
from .exp062_historical_plan_review import (
    EXP062_HISTORICAL_PLAN_REVIEW_DECISION,
    EXP062_HISTORICAL_PLAN_REVIEW_VERSION,
    review_historical_plan_proof,
)
from .exp062_runtime_proof_freeze import (
    PROOF_HEAD_SHA as HISTORICAL_GATE_PROOF_HEAD_SHA,
    PROOF_RUN_ID as HISTORICAL_GATE_PROOF_RUN_ID,
)


EXP062_HISTORICAL_PLAN_PROOF_FREEZE_DECISION = "DEC-311"
EXP062_HISTORICAL_PLAN_PROOF_FREEZE_VERSION = (
    "fmp-exp062-historical-plan-proof-freeze-v1"
)

DEC310_MERGED_COMMIT = "243833543b9c76d4e51ca6b554cbdda4f5aa1a53"
DEC310_REVIEW_SOURCE_BLOB_SHA = "5c8870c10e86122342bb181cb5a15ebc709924ce"

DEC309_MERGED_COMMIT = "95c193343a905acd40daf0eea5d27d55fd2537e1"
DEC309_PLAN_PROOF_RUN_ID = 36403342301
DEC309_PLAN_PROOF_JOB_ID = 108866149073
DEC309_PLAN_PROOF_ARTIFACT_ID = 10960559187
DEC309_PLAN_PROOF_ARTIFACT_NAME = (
    "exp062-dec309-historical-plan-"
    "95c193343a905acd40daf0eea5d27d55fd2537e1"
)
DEC309_PLAN_PROOF_ARTIFACT_DIGEST = (
    "sha256:07679d85ea3ee0a9373bbd78363ab98eb973377ace6d68828528f91188ff3cf8"
)
DEC309_ARTIFACT_ZIP_SHA256 = (
    "07679d85ea3ee0a9373bbd78363ab98eb973377ace6d68828528f91188ff3cf8"
)
DEC309_PLAN_RAW_SHA256 = (
    "ac34769d589dbcc18a056d1ebaf960b6881f943f221d771e80216df32d313672"
)
DEC309_PLAN_CANONICAL_SHA256 = (
    "d6cd04c0c29a2e82da12e687ce56ae80387f7ad3c9727b23018ee548684e62a6"
)

_FALSE_AUTHORITY_FIELDS = (
    "historical_result_dispatch_authorized",
    "historical_execute_mode_available",
    "historical_discovery_execution_authorized",
    "discovery_result_authorized",
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


def validate_historical_plan_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = root / "src/fmp/discovery/exp062_historical_plan_review.py"
    if not path.is_file():
        raise ValueError(f"missing DEC-311 source dependency: {path}")
    actual = _git_blob_sha(path)
    if actual != DEC310_REVIEW_SOURCE_BLOB_SHA:
        raise ValueError(
            "DEC-311 DEC-310 review Git blob mismatch: "
            f"{actual} != {DEC310_REVIEW_SOURCE_BLOB_SHA}"
        )
    return {
        "dec310_review_source_blob_sha": actual,
    }


def _validate_reviewed_result(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": EXP062_HISTORICAL_PLAN_REVIEW_DECISION,
            "version": EXP062_HISTORICAL_PLAN_REVIEW_VERSION,
            "stage": "EXP062_HISTORICAL_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE",
            "proof_workflow_name": "phase8a-exp062-historical-plan",
            "proof_workflow_path": (
                ".github/workflows/phase8a-exp062-historical-plan.yml"
            ),
            "proof_run_id": DEC309_PLAN_PROOF_RUN_ID,
            "proof_head_sha": DEC309_MERGED_COMMIT,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": DEC309_PLAN_PROOF_JOB_ID,
            "proof_artifact_id": DEC309_PLAN_PROOF_ARTIFACT_ID,
            "proof_artifact_name": DEC309_PLAN_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": DEC309_PLAN_PROOF_ARTIFACT_DIGEST,
            "plan_raw_sha256": DEC309_PLAN_RAW_SHA256,
            "plan_canonical_sha256": DEC309_PLAN_CANONICAL_SHA256,
            "plan_decision": EXP062_HISTORICAL_OPERATOR_DECISION,
            "plan_operator_version": EXP062_HISTORICAL_OPERATOR_VERSION,
            "historical_gate_proof_run_id": HISTORICAL_GATE_PROOF_RUN_ID,
            "historical_gate_proof_head_sha": HISTORICAL_GATE_PROOF_HEAD_SHA,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_source_authorized": True,
            "next_gate": (
                "IMMUTABLE_HISTORICAL_PLAN_PROOF_FREEZE_BEFORE_EXECUTION_AUTHORIZATION"
            ),
        },
        prefix="DEC-311 reviewed plan proof",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-311 reviewed plan proof {field} must remain false"
            )


def freeze_historical_plan_proof(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    plan_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = validate_historical_plan_freeze_sources(
        repository_root=repository_root,
    )
    reviewed = review_historical_plan_proof(
        run=proof_run,
        jobs_payload=proof_jobs_payload,
        artifacts_payload=proof_artifacts_payload,
        plan_bytes=plan_bytes,
        expected_head_sha=DEC309_MERGED_COMMIT,
        repository_root=repository_root,
    )
    _validate_reviewed_result(reviewed)

    artifact_zip_sha256 = _validate_sha256(
        artifact_zip_sha256,
        field="DEC-311 artifact ZIP sha256",
    )
    if artifact_zip_sha256 != DEC309_ARTIFACT_ZIP_SHA256:
        raise ValueError("DEC-311 artifact ZIP sha256 mismatch")
    if (
        artifact_zip_sha256
        != DEC309_PLAN_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
    ):
        raise ValueError(
            "DEC-311 artifact ZIP hash does not match GitHub artifact digest"
        )

    frozen: dict[str, object] = {
        "decision": EXP062_HISTORICAL_PLAN_PROOF_FREEZE_DECISION,
        "version": EXP062_HISTORICAL_PLAN_PROOF_FREEZE_VERSION,
        "stage": "EXP062_HISTORICAL_PLAN_PROOF_REVIEWED_AND_FROZEN",
        "source_review_decision": reviewed["decision"],
        "source_review_version": reviewed["version"],
        "dec310_merged_commit": DEC310_MERGED_COMMIT,
        **source_blobs,
        "proof_run_id": DEC309_PLAN_PROOF_RUN_ID,
        "proof_head_sha": DEC309_MERGED_COMMIT,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": DEC309_PLAN_PROOF_JOB_ID,
        "proof_artifact_id": DEC309_PLAN_PROOF_ARTIFACT_ID,
        "proof_artifact_name": DEC309_PLAN_PROOF_ARTIFACT_NAME,
        "proof_artifact_digest": DEC309_PLAN_PROOF_ARTIFACT_DIGEST,
        "artifact_zip_sha256": DEC309_ARTIFACT_ZIP_SHA256,
        "plan_raw_sha256": DEC309_PLAN_RAW_SHA256,
        "plan_canonical_sha256": DEC309_PLAN_CANONICAL_SHA256,
        "plan_decision": EXP062_HISTORICAL_OPERATOR_DECISION,
        "plan_operator_version": EXP062_HISTORICAL_OPERATOR_VERSION,
        "historical_gate_proof_run_id": HISTORICAL_GATE_PROOF_RUN_ID,
        "historical_gate_proof_head_sha": HISTORICAL_GATE_PROOF_HEAD_SHA,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_source_authorized": True,
        "historical_result_slot_verified_available": True,
        "planned_dispatch_command_frozen": shell_join(
            historical_dispatch_command()
        ),
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
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
            "SOURCE_ONLY_HISTORICAL_EXECUTION_AUTHORIZATION_CONTRACT"
        ),
    }
    frozen["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "DEC309_ARTIFACT_ZIP_SHA256",
    "DEC309_MERGED_COMMIT",
    "DEC309_PLAN_CANONICAL_SHA256",
    "DEC309_PLAN_PROOF_ARTIFACT_DIGEST",
    "DEC309_PLAN_PROOF_ARTIFACT_ID",
    "DEC309_PLAN_PROOF_JOB_ID",
    "DEC309_PLAN_PROOF_RUN_ID",
    "DEC309_PLAN_RAW_SHA256",
    "EXP062_HISTORICAL_PLAN_PROOF_FREEZE_DECISION",
    "EXP062_HISTORICAL_PLAN_PROOF_FREEZE_VERSION",
    "freeze_historical_plan_proof",
    "validate_historical_plan_freeze_sources",
]
