from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_REVIEW_DECISION = (
    "DEC-345"
)
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_REVIEW_VERSION = (
    "fmp-exp062-one-shot-historical-executor-workflow-preflight-proof-review-v1"
)

PROOF_WORKFLOW_NAME = (
    "phase8a-exp062-one-shot-historical-executor-workflow-preflight-proof"
)
PROOF_WORKFLOW_PATH = (
    ".github/workflows/"
    "phase8a-exp062-one-shot-historical-executor-workflow-preflight-proof.yml"
)
PROOF_JOB_NAME = (
    "read-only-one-shot-historical-executor-workflow-preflight"
)

DEC344_WORKFLOW_BLOB_SHA = "b070aa25d11ef481602686fb85da9a8bd5c8c1cc"
DEC343_PREFLIGHT_BLOB_SHA = "1339dd02256b9d3fc51b2a312a2272fd5d949796"
DEC343_PREFLIGHT_CLI_BLOB_SHA = "8b2e190e75f378a52fa66ad61b0e1bbadacb343b"
DEC342_WORKFLOW_CONTRACT_BLOB_SHA = (
    "d87bf8f4fc3ad8fc081760c1250dc0f8dc9ffadc"
)
ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA = (
    "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
)

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


def validate_one_shot_historical_executor_workflow_preflight_proof_review_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec344_workflow": (
            root / PROOF_WORKFLOW_PATH,
            DEC344_WORKFLOW_BLOB_SHA,
        ),
        "dec343_preflight": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_workflow_preflight.py",
            DEC343_PREFLIGHT_BLOB_SHA,
        ),
        "dec343_preflight_cli": (
            root
            / "scripts/"
            "phase8a_exp062_one_shot_historical_executor_workflow_preflight.py",
            DEC343_PREFLIGHT_CLI_BLOB_SHA,
        ),
        "dec342_workflow_contract": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_workflow_contract.py",
            DEC342_WORKFLOW_CONTRACT_BLOB_SHA,
        ),
        "active_discovery_workflow": (
            root / ".github/workflows/phase8a-exp062-discovery.yml",
            ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-345 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-345 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _parse_and_validate_preflight(
    preflight_bytes: bytes,
    *,
    expected_head_sha: str,
) -> tuple[dict[str, object], str, str]:
    if not isinstance(preflight_bytes, bytes) or not preflight_bytes:
        raise ValueError("DEC-345 preflight bytes must be non-empty")
    try:
        preflight = json.loads(preflight_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("DEC-345 preflight artifact is invalid JSON") from exc
    if not isinstance(preflight, dict):
        raise ValueError("DEC-345 preflight JSON root must be an object")

    exact = {
        "decision": "DEC-343",
        "version": (
            "fmp-exp062-one-shot-historical-executor-workflow-preflight-v1"
        ),
        "workflow_contract_decision": "DEC-342",
        "workflow_contract_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-contract-v1"
        ),
        "dec342_workflow_contract_blob_sha": (
            DEC342_WORKFLOW_CONTRACT_BLOB_SHA
        ),
        "expected_head_sha": expected_head_sha,
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_"
            "PREFLIGHT_SLOT_AVAILABLE"
        ),
        "proof_run_id": 36358289723,
        "proof_run_count": 1,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_historical_executor_source_authorized": True,
        "one_shot_historical_executor_workflow_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "next_gate": (
            "REPOSITORY_HOSTED_READ_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_PREFLIGHT_PROOF"
        ),
    }
    for field, expected_value in exact.items():
        if preflight.get(field) != expected_value:
            raise ValueError(f"DEC-345 preflight {field} mismatch")

    for field in _FALSE_AUTHORITY_FIELDS:
        if preflight.get(field) is not False:
            raise ValueError(
                f"DEC-345 preflight {field} must remain false"
            )

    return (
        preflight,
        hashlib.sha256(preflight_bytes).hexdigest(),
        hashlib.sha256(_canonical_json(preflight)).hexdigest(),
    )


def review_one_shot_historical_executor_workflow_preflight_proof(
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
        validate_one_shot_historical_executor_workflow_preflight_proof_review_sources(
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
    for field, expected_value in expected_run.items():
        if run.get(field) != expected_value:
            raise ValueError(f"DEC-345 proof run {field} mismatch")
    run_id = _validate_positive_int(
        run.get("id"),
        field="DEC-345 proof run id",
    )

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 1:
        raise ValueError("DEC-345 proof requires exactly one job")
    job = jobs[0]
    if not isinstance(job, Mapping):
        raise ValueError("DEC-345 proof job row is malformed")
    if job.get("name") != PROOF_JOB_NAME:
        raise ValueError("DEC-345 proof job name mismatch")
    if job.get("status") != "completed":
        raise ValueError("DEC-345 proof job status mismatch")
    if job.get("conclusion") != "success":
        raise ValueError("DEC-345 proof job conclusion mismatch")
    job_id = _validate_positive_int(
        job.get("id"),
        field="DEC-345 proof job id",
    )

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-345 proof requires exactly one artifact")
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-345 proof artifact row is malformed")
    artifact_id = _validate_positive_int(
        artifact.get("id"),
        field="DEC-345 proof artifact id",
    )
    artifact_name = (
        "exp062-dec344-one-shot-historical-executor-workflow-preflight-"
        f"{expected_head_sha}"
    )
    if artifact.get("name") != artifact_name:
        raise ValueError("DEC-345 proof artifact name mismatch")
    if artifact.get("expired") is not False:
        raise ValueError("DEC-345 proof artifact must be non-expired")
    artifact_digest = _validate_sha256_digest(
        artifact.get("digest"),
        field="DEC-345 proof artifact digest",
    )

    preflight, raw_sha256, canonical_sha256 = (
        _parse_and_validate_preflight(
            preflight_bytes,
            expected_head_sha=expected_head_sha,
        )
    )

    return {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_REVIEW_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_REVIEW_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_"
            "REVIEWED_SLOT_AVAILABLE"
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
        "workflow_preflight_decision": preflight["decision"],
        "workflow_preflight_version": preflight["version"],
        "workflow_contract_decision": preflight[
            "workflow_contract_decision"
        ],
        "workflow_contract_version": preflight[
            "workflow_contract_version"
        ],
        "historical_gate_proof_run_id": preflight["proof_run_id"],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "one_shot_historical_executor_source_authorized": True,
        "one_shot_historical_executor_workflow_source_authorized": True,
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
        "review_source_blobs": source_blobs,
        "next_gate": (
            "IMMUTABLE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_"
            "PROOF_FREEZE_BEFORE_EXECUTOR_WORKFLOW"
        ),
    }


__all__ = [
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_REVIEW_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_REVIEW_VERSION",
    "review_one_shot_historical_executor_workflow_preflight_proof",
    "validate_one_shot_historical_executor_workflow_preflight_proof_review_sources",
]
