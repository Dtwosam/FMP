from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION = "DEC-339"
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION = (
    "fmp-exp062-one-shot-historical-executor-source-proof-review-v1"
)

PROOF_WORKFLOW_NAME = "phase8a-exp062-one-shot-historical-executor-source-proof"
PROOF_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor-source-proof.yml"
)
PROOF_JOB_NAME = "read-only-one-shot-historical-executor-source-proof"

DEC338_WORKFLOW_BLOB_SHA = "3104d6521e1c11f0c8be92eab0eef21c5e9eb80c"
DEC337_SOURCE_BLOB_SHA = "26ee48241550d6e52501fc901ab88aaa3f42e755"
DEC336_RUNTIME_FREEZE_BLOB_SHA = "9673e115eeb373c4881d36a8b5d91a2801cd8ad1"
DEC334_TERMINAL_REVIEW_BLOB_SHA = "fda2a45f74b101303467cf7b8527bec1bfc5e168"
ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA = "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"

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


def validate_one_shot_historical_executor_source_proof_review_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec338_workflow": (
            root / PROOF_WORKFLOW_PATH,
            DEC338_WORKFLOW_BLOB_SHA,
        ),
        "dec337_source": (
            root
            / "src/fmp/discovery/exp062_historical_one_shot_executor_source.py",
            DEC337_SOURCE_BLOB_SHA,
        ),
        "dec336_runtime_freeze": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_executor_activation_preflight_runtime_freeze.py",
            DEC336_RUNTIME_FREEZE_BLOB_SHA,
        ),
        "dec334_terminal_review": (
            root
            / "src/fmp/discovery/exp062_historical_terminal_review_contract.py",
            DEC334_TERMINAL_REVIEW_BLOB_SHA,
        ),
        "active_discovery_workflow": (
            root / ".github/workflows/phase8a-exp062-discovery.yml",
            ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-339 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-339 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _parse_and_validate_contract(
    contract_bytes: bytes,
    *,
    expected_head_sha: str,
) -> tuple[dict[str, object], str, str]:
    if not isinstance(contract_bytes, bytes) or not contract_bytes:
        raise ValueError("DEC-339 contract bytes must be non-empty")
    try:
        contract = json.loads(contract_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("DEC-339 source-contract artifact is invalid JSON") from exc
    if not isinstance(contract, dict):
        raise ValueError("DEC-339 source-contract JSON root must be an object")

    exact = {
        "decision": "DEC-337",
        "version": "fmp-exp062-one-shot-historical-executor-source-v1",
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_AUTHORIZED_"
            "RUNTIME_DISPATCH_LOCKED"
        ),
        "dec336_runtime_freeze_blob_sha": DEC336_RUNTIME_FREEZE_BLOB_SHA,
        "runtime_freeze_decision": "DEC-336",
        "runtime_freeze_version": (
            "fmp-exp062-historical-executor-activation-preflight-"
            "runtime-freeze-v1"
        ),
        "runtime_freeze_fingerprint_sha256": (
            "147ab77116979afa8d0d07c3c748fb80e02865a382317824320f6af534bfc374"
        ),
        "terminal_review_decision": "DEC-334",
        "terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "expected_head_sha": expected_head_sha,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_historical_executor_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "next_gate": (
            "REPOSITORY_HOSTED_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_SOURCE_PROOF"
        ),
    }
    for field, expected in exact.items():
        if contract.get(field) != expected:
            raise ValueError(f"DEC-339 source contract {field} mismatch")

    for field in _FALSE_AUTHORITY_FIELDS:
        if contract.get(field) is not False:
            raise ValueError(
                f"DEC-339 source contract {field} must remain false"
            )

    return (
        contract,
        hashlib.sha256(contract_bytes).hexdigest(),
        hashlib.sha256(_canonical_json(contract)).hexdigest(),
    )


def review_one_shot_historical_executor_source_proof(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    contract_bytes: bytes,
    expected_head_sha: str,
    repository_root: Path = Path("."),
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    source_blobs = validate_one_shot_historical_executor_source_proof_review_sources(
        repository_root=repository_root,
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
            raise ValueError(f"DEC-339 proof run {field} mismatch")
    run_id = _validate_positive_int(
        run.get("id"),
        field="DEC-339 proof run id",
    )

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 1:
        raise ValueError("DEC-339 proof requires exactly one job")
    job = jobs[0]
    if not isinstance(job, Mapping):
        raise ValueError("DEC-339 proof job row is malformed")
    if job.get("name") != PROOF_JOB_NAME:
        raise ValueError("DEC-339 proof job name mismatch")
    if job.get("status") != "completed":
        raise ValueError("DEC-339 proof job status mismatch")
    if job.get("conclusion") != "success":
        raise ValueError("DEC-339 proof job conclusion mismatch")
    job_id = _validate_positive_int(
        job.get("id"),
        field="DEC-339 proof job id",
    )

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-339 proof requires exactly one artifact")
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-339 proof artifact row is malformed")
    artifact_id = _validate_positive_int(
        artifact.get("id"),
        field="DEC-339 proof artifact id",
    )
    artifact_name = (
        f"exp062-dec338-one-shot-historical-executor-source-{expected_head_sha}"
    )
    if artifact.get("name") != artifact_name:
        raise ValueError("DEC-339 proof artifact name mismatch")
    if artifact.get("expired") is not False:
        raise ValueError("DEC-339 proof artifact must be non-expired")
    artifact_digest = _validate_sha256_digest(
        artifact.get("digest"),
        field="DEC-339 proof artifact digest",
    )

    contract, raw_sha256, canonical_sha256 = _parse_and_validate_contract(
        contract_bytes,
        expected_head_sha=expected_head_sha,
    )

    return {
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
        "contract_raw_sha256": raw_sha256,
        "contract_canonical_sha256": canonical_sha256,
        "source_contract_decision": contract["decision"],
        "source_contract_version": contract["version"],
        "runtime_freeze_decision": contract["runtime_freeze_decision"],
        "runtime_freeze_fingerprint_sha256": contract[
            "runtime_freeze_fingerprint_sha256"
        ],
        "terminal_review_decision": contract["terminal_review_decision"],
        "historical_gate_proof_run_id": contract[
            "historical_gate_proof_run_id"
        ],
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
            "IMMUTABLE_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "FREEZE_BEFORE_EXECUTOR_WORKFLOW"
        ),
    }


__all__ = [
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION",
    "review_one_shot_historical_executor_source_proof",
    "validate_one_shot_historical_executor_source_proof_review_sources",
]
