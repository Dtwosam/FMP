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
    validate_historical_plan,
)
from .exp062_historical_run_authorization import (
    EXP062_HISTORICAL_RUN_AUTHORIZATION_DECISION,
    EXP062_HISTORICAL_RUN_AUTHORIZATION_VERSION,
)
from .exp062_runtime_proof_freeze import (
    PROOF_HEAD_SHA,
    PROOF_RUN_ID,
)


EXP062_HISTORICAL_PLAN_REVIEW_DECISION = "DEC-310"
EXP062_HISTORICAL_PLAN_REVIEW_VERSION = (
    "fmp-exp062-historical-plan-proof-review-v1"
)

PLAN_PROOF_WORKFLOW_NAME = "phase8a-exp062-historical-plan"
PLAN_PROOF_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-historical-plan.yml"
)
PLAN_PROOF_JOB_NAME = "read-only-historical-plan"

DEC309_PLAN_PROOF_WORKFLOW_BLOB_SHA = (
    "5de2d32d6e12997d76ed8d76457f790870924376"
)
DEC308_HISTORICAL_OPERATOR_BLOB_SHA = (
    "990ec40bbe3ee4f776a521e1d823cb0b7ed68913"
)
DEC308_HISTORICAL_OPERATOR_CLI_BLOB_SHA = (
    "444200402e12812d9f1b16e32fa0b5bcbf0aa762"
)
DEC307_HISTORICAL_AUTHORIZATION_BLOB_SHA = (
    "5715257543e9387d9749cfe3bb626fa03a144ed4"
)
DEC306_RUNTIME_PROOF_FREEZE_BLOB_SHA = (
    "8e9baec1ae7b24055064535fbf7e262055dffeca"
)

_FALSE_PLAN_AUTHORITY_FIELDS = (
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


def validate_historical_plan_review_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "plan_proof_workflow": (
            root / PLAN_PROOF_WORKFLOW_PATH,
            DEC309_PLAN_PROOF_WORKFLOW_BLOB_SHA,
        ),
        "historical_operator": (
            root / "src/fmp/discovery/exp062_historical_operator.py",
            DEC308_HISTORICAL_OPERATOR_BLOB_SHA,
        ),
        "historical_operator_cli": (
            root / "scripts/phase8a_exp062_historical_operator.py",
            DEC308_HISTORICAL_OPERATOR_CLI_BLOB_SHA,
        ),
        "historical_authorization": (
            root / "src/fmp/discovery/exp062_historical_run_authorization.py",
            DEC307_HISTORICAL_AUTHORIZATION_BLOB_SHA,
        ),
        "runtime_proof_freeze": (
            root / "src/fmp/discovery/exp062_runtime_proof_freeze.py",
            DEC306_RUNTIME_PROOF_FREEZE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-310 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-310 {label} Git blob mismatch: "
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
        raise ValueError("DEC-310 historical plan bytes must be non-empty")
    try:
        value = json.loads(plan_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("DEC-310 historical plan artifact is invalid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("DEC-310 historical plan JSON root must be an object")

    validate_historical_plan(value)

    exact = {
        "decision": EXP062_HISTORICAL_OPERATOR_DECISION,
        "operator_version": EXP062_HISTORICAL_OPERATOR_VERSION,
        "authorization_decision": EXP062_HISTORICAL_RUN_AUTHORIZATION_DECISION,
        "authorization_version": EXP062_HISTORICAL_RUN_AUTHORIZATION_VERSION,
        "expected_head_sha": expected_head_sha,
        "stage": "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE",
        "proof_run_id": PROOF_RUN_ID,
        "proof_head_sha": PROOF_HEAD_SHA,
        "proof_run_count": 1,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_head_sha": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "planned_dispatch_command": shell_join(historical_dispatch_command()),
        "historical_result_slot_source_authorized": True,
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-310 historical plan {field} mismatch")

    for field in _FALSE_PLAN_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-310 historical plan {field} must remain false")

    return (
        value,
        hashlib.sha256(plan_bytes).hexdigest(),
        hashlib.sha256(_canonical_json(value)).hexdigest(),
    )


def review_historical_plan_proof(
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
    source_blobs = validate_historical_plan_review_sources(
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
            raise ValueError(f"DEC-310 plan-proof run {field} mismatch")
    run_id = _validate_positive_int(
        run.get("id"),
        field="DEC-310 plan-proof run id",
    )

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 1:
        raise ValueError("DEC-310 plan proof requires exactly one job")
    job = jobs[0]
    if not isinstance(job, Mapping):
        raise ValueError("DEC-310 plan-proof job row is malformed")
    if job.get("name") != PLAN_PROOF_JOB_NAME:
        raise ValueError("DEC-310 plan-proof job name mismatch")
    if job.get("status") != "completed":
        raise ValueError("DEC-310 plan-proof job status mismatch")
    if job.get("conclusion") != "success":
        raise ValueError("DEC-310 plan-proof job conclusion mismatch")
    job_id = _validate_positive_int(
        job.get("id"),
        field="DEC-310 plan-proof job id",
    )

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-310 plan proof requires exactly one artifact")
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-310 plan-proof artifact row is malformed")
    artifact_id = _validate_positive_int(
        artifact.get("id"),
        field="DEC-310 plan-proof artifact id",
    )
    expected_artifact_name = (
        f"exp062-dec309-historical-plan-{expected_head_sha}"
    )
    if artifact.get("name") != expected_artifact_name:
        raise ValueError("DEC-310 plan-proof artifact name mismatch")
    if artifact.get("expired") is not False:
        raise ValueError("DEC-310 plan-proof artifact must be non-expired")
    artifact_digest = _validate_sha256_digest(
        artifact.get("digest"),
        field="DEC-310 plan-proof artifact digest",
    )

    plan, raw_sha256, canonical_sha256 = _parse_and_validate_plan(
        plan_bytes,
        expected_head_sha=expected_head_sha,
    )

    return {
        "decision": EXP062_HISTORICAL_PLAN_REVIEW_DECISION,
        "version": EXP062_HISTORICAL_PLAN_REVIEW_VERSION,
        "stage": "EXP062_HISTORICAL_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE",
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
        "historical_gate_proof_head_sha": plan["proof_head_sha"],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_source_authorized": True,
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
        "review_source_blobs": source_blobs,
        "next_gate": (
            "IMMUTABLE_HISTORICAL_PLAN_PROOF_FREEZE_BEFORE_EXECUTION_AUTHORIZATION"
        ),
    }


__all__ = [
    "EXP062_HISTORICAL_PLAN_REVIEW_DECISION",
    "EXP062_HISTORICAL_PLAN_REVIEW_VERSION",
    "PLAN_PROOF_JOB_NAME",
    "PLAN_PROOF_WORKFLOW_NAME",
    "PLAN_PROOF_WORKFLOW_PATH",
    "review_historical_plan_proof",
    "validate_historical_plan_review_sources",
]
