from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_execution_authorization import (
    EXP062_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION,
    EXP062_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION,
)
from .exp062_historical_execution_operator import (
    EXP062_HISTORICAL_EXECUTION_OPERATOR_DECISION,
    EXP062_HISTORICAL_EXECUTION_OPERATOR_VERSION,
    historical_execution_dispatch_command,
    shell_join,
    validate_historical_execution_plan,
)
from .exp062_runtime_proof_freeze import (
    PROOF_RUN_ID as HISTORICAL_GATE_PROOF_RUN_ID,
)


EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_DECISION = "DEC-315"
EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_VERSION = (
    "fmp-exp062-historical-execution-plan-proof-review-v1"
)

PLAN_PROOF_WORKFLOW_NAME = "phase8a-exp062-historical-execution-plan"
PLAN_PROOF_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-historical-execution-plan.yml"
)
PLAN_PROOF_JOB_NAME = "read-only-historical-execution-plan"

DEC314_PLAN_PROOF_WORKFLOW_BLOB_SHA = (
    "d2b2e4fcc2a39e614dda98c890ec13b6387725e8"
)
DEC313_HISTORICAL_EXECUTION_OPERATOR_BLOB_SHA = (
    "7f21ccf59de9605c7fab45b4506f947ffae69cab"
)
DEC313_HISTORICAL_EXECUTION_OPERATOR_CLI_BLOB_SHA = (
    "9ecb3f47d7e68461e4a7d893ad5862d7e78a1fc8"
)
DEC312_HISTORICAL_EXECUTION_AUTHORIZATION_BLOB_SHA = (
    "aa8cfb25e3d78c0c72da4b22898c1263a42548ba"
)
ACTIVATED_CLI_BLOB_SHA = "773784d0770d54b1d3e41fba2057b9314a090034"
ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA = (
    "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
)
DEC311_HISTORICAL_PLAN_FREEZE_BLOB_SHA = (
    "e3274118b37066efe2869d554e78e6b68e64b32a"
)

_FALSE_PLAN_AUTHORITY_FIELDS = (
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


def _validate_sha256_digest(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"{field} must use sha256:<hex>")
    raw = value.removeprefix("sha256:")
    if len(raw) != 64:
        raise ValueError(f"{field} must contain 64 hex characters")
    try:
        int(raw, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_historical_execution_plan_review_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "plan_proof_workflow": (
            root / PLAN_PROOF_WORKFLOW_PATH,
            DEC314_PLAN_PROOF_WORKFLOW_BLOB_SHA,
        ),
        "execution_operator": (
            root / "src/fmp/discovery/exp062_historical_execution_operator.py",
            DEC313_HISTORICAL_EXECUTION_OPERATOR_BLOB_SHA,
        ),
        "execution_operator_cli": (
            root / "scripts/phase8a_exp062_historical_execution_operator.py",
            DEC313_HISTORICAL_EXECUTION_OPERATOR_CLI_BLOB_SHA,
        ),
        "execution_authorization": (
            root / "src/fmp/discovery/exp062_historical_execution_authorization.py",
            DEC312_HISTORICAL_EXECUTION_AUTHORIZATION_BLOB_SHA,
        ),
        "activated_cli": (
            root / "scripts/phase8a_exp062.py",
            ACTIVATED_CLI_BLOB_SHA,
        ),
        "active_discovery_workflow": (
            root / ".github/workflows/phase8a-exp062-discovery.yml",
            ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA,
        ),
        "historical_plan_freeze": (
            root / "src/fmp/discovery/exp062_historical_plan_result_freeze.py",
            DEC311_HISTORICAL_PLAN_FREEZE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-315 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-315 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _parse_and_validate_plan(
    plan_bytes: bytes,
    *,
    expected_head_sha: str,
) -> tuple[dict[str, object], str, str]:
    if not isinstance(plan_bytes, bytes) or not plan_bytes:
        raise ValueError("DEC-315 execution plan bytes must be non-empty")
    try:
        value = json.loads(plan_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("DEC-315 execution plan artifact is invalid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("DEC-315 execution plan JSON root must be an object")

    validate_historical_execution_plan(value)

    exact = {
        "decision": EXP062_HISTORICAL_EXECUTION_OPERATOR_DECISION,
        "operator_version": EXP062_HISTORICAL_EXECUTION_OPERATOR_VERSION,
        "authorization_decision": (
            EXP062_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "authorization_version": (
            EXP062_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION
        ),
        "expected_head_sha": expected_head_sha,
        "stage": "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE",
        "proof_run_id": HISTORICAL_GATE_PROOF_RUN_ID,
        "proof_run_count": 1,
        "proof_run_number": 1,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command": shell_join(
            historical_execution_dispatch_command()
        ),
        "historical_execution_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-315 execution plan {field} mismatch")

    for field in _FALSE_PLAN_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-315 execution plan {field} must remain false")

    return (
        value,
        hashlib.sha256(plan_bytes).hexdigest(),
        hashlib.sha256(_canonical_json(value)).hexdigest(),
    )


def review_historical_execution_plan_proof(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    plan_bytes: bytes,
    expected_head_sha: str,
    repository_root: Path = Path("."),
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    source_blobs = validate_historical_execution_plan_review_sources(
        repository_root=repository_root,
    )

    expected_run = {
        "name": PLAN_PROOF_WORKFLOW_NAME,
        "path": PLAN_PROOF_WORKFLOW_PATH,
        "event": "push",
        "head_branch": "main",
        "head_sha": expected_head_sha,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in expected_run.items():
        if run.get(field) != expected:
            raise ValueError(f"DEC-315 plan-proof run {field} mismatch")
    run_id = _validate_positive_int(
        run.get("id"),
        field="DEC-315 plan-proof run id",
    )

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 1:
        raise ValueError("DEC-315 plan proof requires exactly one job")
    job = jobs[0]
    if not isinstance(job, Mapping):
        raise ValueError("DEC-315 plan-proof job row is malformed")
    if job.get("name") != PLAN_PROOF_JOB_NAME:
        raise ValueError("DEC-315 plan-proof job name mismatch")
    if job.get("status") != "completed":
        raise ValueError("DEC-315 plan-proof job status mismatch")
    if job.get("conclusion") != "success":
        raise ValueError("DEC-315 plan-proof job conclusion mismatch")
    job_id = _validate_positive_int(
        job.get("id"),
        field="DEC-315 plan-proof job id",
    )

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-315 plan proof requires exactly one artifact")
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-315 plan-proof artifact row is malformed")
    artifact_id = _validate_positive_int(
        artifact.get("id"),
        field="DEC-315 plan-proof artifact id",
    )
    expected_artifact_name = (
        f"exp062-dec314-historical-execution-plan-{expected_head_sha}"
    )
    if artifact.get("name") != expected_artifact_name:
        raise ValueError("DEC-315 plan-proof artifact name mismatch")
    if artifact.get("expired") is not False:
        raise ValueError("DEC-315 plan-proof artifact must be non-expired")
    artifact_digest = _validate_sha256_digest(
        artifact.get("digest"),
        field="DEC-315 plan-proof artifact digest",
    )

    plan, raw_sha256, canonical_sha256 = _parse_and_validate_plan(
        plan_bytes,
        expected_head_sha=expected_head_sha,
    )

    return {
        "decision": EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_DECISION,
        "version": EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_VERSION,
        "stage": "EXP062_HISTORICAL_EXECUTION_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE",
        "proof_workflow_name": PLAN_PROOF_WORKFLOW_NAME,
        "proof_workflow_path": PLAN_PROOF_WORKFLOW_PATH,
        "proof_run_id": run_id,
        "proof_head_sha": expected_head_sha,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": job_id,
        "proof_artifact_id": artifact_id,
        "proof_artifact_name": expected_artifact_name,
        "proof_artifact_digest": artifact_digest,
        "plan_raw_sha256": raw_sha256,
        "plan_canonical_sha256": canonical_sha256,
        "plan_decision": plan["decision"],
        "plan_operator_version": plan["operator_version"],
        "historical_gate_proof_run_id": plan["proof_run_id"],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
        "review_source_blobs": source_blobs,
        "next_gate": (
            "IMMUTABLE_HISTORICAL_EXECUTION_PLAN_PROOF_FREEZE_BEFORE_DISPATCH_AUTHORIZATION"
        ),
    }


__all__ = [
    "EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_DECISION",
    "EXP062_HISTORICAL_EXECUTION_PLAN_REVIEW_VERSION",
    "PLAN_PROOF_JOB_NAME",
    "PLAN_PROOF_WORKFLOW_NAME",
    "PLAN_PROOF_WORKFLOW_PATH",
    "review_historical_execution_plan_proof",
    "validate_historical_execution_plan_review_sources",
]
