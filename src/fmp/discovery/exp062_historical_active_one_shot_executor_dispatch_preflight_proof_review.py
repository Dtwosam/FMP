from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_REVIEW_DECISION = (
    "DEC-427"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_REVIEW_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-dispatch-preflight-proof-review-v1"
)

PROOF_WORKFLOW_NAME = (
    "phase8a-exp062-active-one-shot-historical-executor-"
    "dispatch-preflight-proof"
)
PROOF_WORKFLOW_PATH = (
    ".github/workflows/"
    "phase8a-exp062-active-one-shot-historical-executor-"
    "dispatch-preflight-proof.yml"
)
PROOF_JOB_NAME = (
    "read-only-active-one-shot-historical-executor-dispatch-preflight"
)

_EXPECTED_SOURCE_BLOBS = {
    "dec426_workflow": "0bb9cd78639ebad68eb7db0fb9d083ce86b75319",
    "dec425_preflight": "1978f71bb11097613d3820127f7a04ce2bf81adb",
    "dec425_preflight_cli": "ef0f6df22d9208b6de8037585d706a1bb1e9eda4",
    "dec424_install_receipt": "27e714620018413a09ceaf287fb7943bf884ee49",
    "active_executor_workflow": "51ce87584369be957482460d81649adb1cb9f05d",
    "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
}

_TRUE_STATE_FIELDS = (
    "active_executor_workflow_present",
    "historical_executor_workflow_install_authorized",
    "historical_executor_workflow_installed",
    "historical_executor_available",
    "historical_result_slot_verified_available",
    "historical_discovery_execution_authorized",
    "discovery_result_authorized",
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


def validate_active_one_shot_historical_executor_dispatch_preflight_proof_review_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    paths = {
        "dec426_workflow": root / PROOF_WORKFLOW_PATH,
        "dec425_preflight": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_active_one_shot_executor_dispatch_preflight.py"
        ),
        "dec425_preflight_cli": (
            root
            / "scripts/"
            "phase8a_exp062_active_one_shot_historical_executor_dispatch_preflight.py"
        ),
        "dec424_install_receipt": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_active_one_shot_executor_workflow_install_receipt.py"
        ),
        "active_executor_workflow": (
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
            raise ValueError(f"missing DEC-427 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != _EXPECTED_SOURCE_BLOBS[label]:
            raise ValueError(f"DEC-427 {label} Git blob mismatch")
        actual[label] = actual_sha
    return actual


def _parse_preflight(
    raw: bytes,
    *,
    expected_head_sha: str,
) -> tuple[dict[str, object], str, str]:
    if not isinstance(raw, bytes) or not raw:
        raise ValueError("DEC-427 preflight bytes must be non-empty")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("DEC-427 preflight artifact is invalid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("DEC-427 preflight JSON root must be an object")

    exact = {
        "decision": "DEC-425",
        "version": (
            "fmp-exp062-active-one-shot-historical-executor-"
            "dispatch-preflight-v1"
        ),
        "install_receipt_decision": "DEC-424",
        "install_receipt_version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-"
            "install-receipt-v1"
        ),
        "dec424_install_receipt_blob_sha": (
            "27e714620018413a09ceaf287fb7943bf884ee49"
        ),
        "active_executor_workflow_blob_sha": (
            "51ce87584369be957482460d81649adb1cb9f05d"
        ),
        "active_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "expected_head_sha": expected_head_sha,
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_PREFLIGHT_INSTALLED_EXECUTOR_READY_RUNTIME_LOCKED"
        ),
        "executor_workflow_run_count": 0,
        "executor_workflow_run_id": None,
        "executor_workflow_run_status": None,
        "executor_workflow_run_conclusion": None,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "next_gate": (
            "EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-427 preflight {field} mismatch")
    for field in _TRUE_STATE_FIELDS:
        if value.get(field) is not True:
            raise ValueError(f"DEC-427 preflight {field} must remain true")
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-427 preflight {field} must remain false")

    return (
        value,
        hashlib.sha256(raw).hexdigest(),
        hashlib.sha256(_canonical_json(value)).hexdigest(),
    )


def review_active_one_shot_historical_executor_dispatch_preflight_proof(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    preflight_bytes: bytes,
    expected_head_sha: str,
    repository_root: Path = Path("."),
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    source_blobs = (
        validate_active_one_shot_historical_executor_dispatch_preflight_proof_review_sources(
            repository_root=repository_root,
        )
    )

    expected_run = {
        "name": PROOF_WORKFLOW_NAME,
        "path": PROOF_WORKFLOW_PATH,
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
            raise ValueError(f"DEC-427 proof run {field} mismatch")
    run_id = _positive_int(run.get("id"), field="DEC-427 proof run id")

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 1:
        raise ValueError("DEC-427 proof requires exactly one job")
    job = jobs[0]
    if not isinstance(job, Mapping):
        raise ValueError("DEC-427 proof job row is malformed")
    if job.get("name") != PROOF_JOB_NAME:
        raise ValueError("DEC-427 proof job name mismatch")
    if job.get("status") != "completed":
        raise ValueError("DEC-427 proof job status mismatch")
    if job.get("conclusion") != "success":
        raise ValueError("DEC-427 proof job conclusion mismatch")
    job_id = _positive_int(job.get("id"), field="DEC-427 proof job id")

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-427 proof requires exactly one artifact")
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-427 proof artifact row is malformed")
    artifact_id = _positive_int(
        artifact.get("id"),
        field="DEC-427 proof artifact id",
    )
    artifact_name = (
        "exp062-dec426-active-one-shot-historical-executor-"
        "dispatch-preflight-"
        f"{expected_head_sha}"
    )
    if artifact.get("name") != artifact_name:
        raise ValueError("DEC-427 proof artifact name mismatch")
    if artifact.get("expired") is not False:
        raise ValueError("DEC-427 proof artifact must be non-expired")
    artifact_digest = _sha256_digest(
        artifact.get("digest"),
        field="DEC-427 proof artifact digest",
    )

    preflight, raw_sha256, canonical_sha256 = _parse_preflight(
        preflight_bytes,
        expected_head_sha=expected_head_sha,
    )

    return {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_REVIEW_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_REVIEW_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_PREFLIGHT_PROOF_REVIEWED_RUNTIME_LOCKED"
        ),
        "proof_workflow_name": PROOF_WORKFLOW_NAME,
        "proof_workflow_path": PROOF_WORKFLOW_PATH,
        "proof_run_id": run_id,
        "proof_head_sha": expected_head_sha,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": job_id,
        "proof_artifact_id": artifact_id,
        "proof_artifact_name": artifact_name,
        "proof_artifact_digest": artifact_digest,
        "preflight_raw_sha256": raw_sha256,
        "preflight_canonical_sha256": canonical_sha256,
        "dispatch_preflight_decision": preflight["decision"],
        "dispatch_preflight_version": preflight["version"],
        "install_receipt_decision": preflight["install_receipt_decision"],
        "install_receipt_version": preflight["install_receipt_version"],
        "dec424_install_receipt_blob_sha": preflight[
            "dec424_install_receipt_blob_sha"
        ],
        "active_executor_workflow_blob_sha": preflight[
            "active_executor_workflow_blob_sha"
        ],
        "active_executor_workflow_path": preflight[
            "active_executor_workflow_path"
        ],
        "active_executor_workflow_present": True,
        "historical_executor_workflow_install_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "executor_workflow_run_count": 0,
        "historical_gate_proof_run_id": preflight[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
        "review_source_blobs": source_blobs,
        "next_gate": (
            "IMMUTABLE_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_PREFLIGHT_PROOF_FREEZE_BEFORE_AUTHORIZATION"
        ),
    }


__all__ = [
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_REVIEW_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_REVIEW_VERSION",
    "review_active_one_shot_historical_executor_dispatch_preflight_proof",
    "validate_active_one_shot_historical_executor_dispatch_preflight_proof_review_sources",
]
