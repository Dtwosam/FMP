from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping


EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_REVIEW_DECISION = "DEC-437"
EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_REVIEW_VERSION = (
    "fmp-exp062-one-shot-executor-recovery-receipt-review-v1"
)

RECOVERY_WORKFLOW_NAME = (
    "phase8a-exp062-one-shot-historical-executor-recovery"
)
RECOVERY_WORKFLOW_PATH = (
    ".github/workflows/"
    "phase8a-exp062-one-shot-historical-executor-recovery.yml"
)
RECOVERY_JOB_NAME = "one-shot-historical-executor-recovery"

_EXPECTED_SOURCE_BLOBS = {
    "dec436_recovery_workflow": "a2520a108373d25d67dd470794eeb4f0fc9e3187",
    "dec436_recovery_authorization": "481fbfbb43557b1b42c0d9bc84ded0775816714e",
    "original_executor_workflow": "51ce87584369be957482460d81649adb1cb9f05d",
    "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
}

_FALSE_AUTHORITY_FIELDS = (
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
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


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


def _sha256_digest(value: object, *, field: str) -> str:
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


def validate_one_shot_executor_recovery_receipt_review_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    paths = {
        "dec436_recovery_workflow": root / RECOVERY_WORKFLOW_PATH,
        "dec436_recovery_authorization": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_recovery_authorization.py"
        ),
        "original_executor_workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "active_discovery_workflow": (
            root / ".github/workflows/phase8a-exp062-discovery.yml"
        ),
    }
    actual: dict[str, str] = {}
    for label, path in paths.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-437 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != _EXPECTED_SOURCE_BLOBS[label]:
            raise ValueError(f"DEC-437 {label} Git blob mismatch")
        actual[label] = actual_sha
    return actual


def _parse_receipt(
    raw: bytes,
    *,
    expected_head_sha: str,
    expected_recovery_run_id: int,
) -> tuple[dict[str, object], str, str]:
    if not isinstance(raw, bytes) or not raw:
        raise ValueError("DEC-437 receipt bytes must be non-empty")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("DEC-437 receipt artifact is invalid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("DEC-437 receipt JSON root must be an object")

    exact = {
        "decision": "DEC-436",
        "recovery_workflow": RECOVERY_WORKFLOW_NAME,
        "recovery_run_id": expected_recovery_run_id,
        "recovery_run_number": 1,
        "recovery_run_attempt": 1,
        "recovery_head_sha": expected_head_sha,
        "failed_original_executor_run_id": 36702494195,
        "failed_original_executor_job_id": 109844958600,
        "failed_original_executor_run_number": 2,
        "failed_original_executor_run_attempt": 1,
        "failed_original_executor_conclusion": "failure",
        "failed_original_executor_dispatched_historical_result": False,
        "historical_result_run_number": 2,
        "historical_result_run_attempt": 1,
        "historical_result_head_sha": expected_head_sha,
        "dispatch_command": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-437 receipt {field} mismatch")
    historical_result_run_id = _positive_int(
        value.get("historical_result_run_id"),
        field="DEC-437 historical result run id",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-437 receipt {field} must remain false")

    return (
        value,
        hashlib.sha256(raw).hexdigest(),
        hashlib.sha256(_canonical_json(value)).hexdigest(),
    )


def review_one_shot_executor_recovery_receipt(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    receipt_bytes: bytes,
    expected_head_sha: str,
    repository_root: Path = Path("."),
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    source_blobs = validate_one_shot_executor_recovery_receipt_review_sources(
        repository_root=repository_root,
    )

    expected_run = {
        "name": RECOVERY_WORKFLOW_NAME,
        "path": RECOVERY_WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": expected_head_sha,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in expected_run.items():
        if run.get(field) != expected:
            raise ValueError(f"DEC-437 recovery run {field} mismatch")
    run_id = _positive_int(run.get("id"), field="DEC-437 recovery run id")

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 1:
        raise ValueError("DEC-437 recovery requires exactly one job")
    job = jobs[0]
    if not isinstance(job, Mapping):
        raise ValueError("DEC-437 recovery job row is malformed")
    if job.get("name") != RECOVERY_JOB_NAME:
        raise ValueError("DEC-437 recovery job name mismatch")
    if job.get("status") != "completed":
        raise ValueError("DEC-437 recovery job status mismatch")
    if job.get("conclusion") != "success":
        raise ValueError("DEC-437 recovery job conclusion mismatch")
    job_id = _positive_int(job.get("id"), field="DEC-437 recovery job id")

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-437 recovery requires exactly one artifact")
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-437 recovery artifact row is malformed")
    artifact_id = _positive_int(
        artifact.get("id"),
        field="DEC-437 recovery artifact id",
    )
    artifact_name = (
        "exp062-dec436-one-shot-historical-executor-recovery-receipt-"
        f"{expected_head_sha}"
    )
    if artifact.get("name") != artifact_name:
        raise ValueError("DEC-437 recovery artifact name mismatch")
    if artifact.get("expired") is not False:
        raise ValueError("DEC-437 recovery artifact must be non-expired")
    artifact_digest = _sha256_digest(
        artifact.get("digest"),
        field="DEC-437 recovery artifact digest",
    )

    receipt, raw_sha256, canonical_sha256 = _parse_receipt(
        receipt_bytes,
        expected_head_sha=expected_head_sha,
        expected_recovery_run_id=run_id,
    )

    return {
        "decision": EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_REVIEW_DECISION,
        "version": EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_REVIEW_VERSION,
        "stage": (
            "EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_REVIEWED_"
            "HISTORICAL_RESULT_DISPATCHED"
        ),
        "recovery_workflow_name": RECOVERY_WORKFLOW_NAME,
        "recovery_workflow_path": RECOVERY_WORKFLOW_PATH,
        "recovery_run_id": run_id,
        "recovery_head_sha": expected_head_sha,
        "recovery_run_number": 1,
        "recovery_run_attempt": 1,
        "recovery_run_conclusion": "success",
        "recovery_job_id": job_id,
        "recovery_artifact_id": artifact_id,
        "recovery_artifact_name": artifact_name,
        "recovery_artifact_digest": artifact_digest,
        "receipt_raw_sha256": raw_sha256,
        "receipt_canonical_sha256": canonical_sha256,
        "recovery_authorization_decision": "DEC-436",
        "recovery_authorization_version": (
            "fmp-exp062-one-shot-executor-recovery-authorization-v1"
        ),
        "failed_original_executor_run_id": 36702494195,
        "failed_original_executor_job_id": 109844958600,
        "failed_original_executor_run_number": 2,
        "failed_original_executor_run_attempt": 1,
        "failed_original_executor_conclusion": "failure",
        "failed_original_executor_dispatched_historical_result": False,
        "historical_result_run_id": receipt["historical_result_run_id"],
        "historical_result_run_number": 2,
        "historical_result_run_attempt": 1,
        "historical_result_head_sha": expected_head_sha,
        "historical_result_dispatched": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
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
            "IMMUTABLE_DEC436_RECOVERY_RECEIPT_FREEZE_"
            "WHILE_HISTORICAL_RESULT_RUN_2_COMPLETES"
        ),
    }


__all__ = [
    "EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_REVIEW_DECISION",
    "EXP062_ONE_SHOT_EXECUTOR_RECOVERY_RECEIPT_REVIEW_VERSION",
    "review_one_shot_executor_recovery_receipt",
    "validate_one_shot_executor_recovery_receipt_review_sources",
]
