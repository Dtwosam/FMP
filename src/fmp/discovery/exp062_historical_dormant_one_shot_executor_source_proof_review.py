from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping


EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION = (
    "DEC-357"
)
EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION = (
    "fmp-exp062-dormant-one-shot-historical-executor-source-proof-review-v1"
)

PROOF_WORKFLOW_NAME = (
    "phase8a-exp062-dormant-one-shot-historical-executor-workflow-source-proof"
)
PROOF_WORKFLOW_PATH = (
    ".github/workflows/"
    "phase8a-exp062-dormant-one-shot-historical-executor-workflow-source-proof.yml"
)
PROOF_JOB_NAME = (
    "read-only-dormant-one-shot-historical-executor-workflow-source-proof"
)

_EXPECTED_SOURCE_BLOBS = {
    "dec356_workflow": "0522e443eda017759c78ccbc718f453cdb0bf8f9",
    "dec355_source": "003e44126d9d6a807efd51b5a589128f6d4b5aac",
    "dec354_installation_source_contract": (
        "e4fc6a7d1faaca50bc6936597f0e8b66fe096985"
    ),
    "dormant_executor_workflow_template": (
        "51ce87584369be957482460d81649adb1cb9f05d"
    ),
    "active_discovery_workflow": (
        "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
    ),
}

_FALSE_AUTHORITY_FIELDS = (
    "historical_executor_workflow_install_authorized",
    "historical_executor_workflow_installed",
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


def validate_dormant_one_shot_historical_executor_source_proof_review_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    paths = {
        "dec356_workflow": root / PROOF_WORKFLOW_PATH,
        "dec355_source": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_dormant_workflow_source.py"
        ),
        "dec354_installation_source_contract": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_workflow_installation_source_contract.py"
        ),
        "dormant_executor_workflow_template": (
            root
            / "docs/superpowers/templates/"
            "phase8a-exp062-one-shot-historical-executor.yml.disabled"
        ),
        "active_discovery_workflow": (
            root / ".github/workflows/phase8a-exp062-discovery.yml"
        ),
    }
    actual: dict[str, str] = {}
    for label, path in paths.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-357 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != _EXPECTED_SOURCE_BLOBS[label]:
            raise ValueError(f"DEC-357 {label} Git blob mismatch")
        actual[label] = actual_sha
    return actual


def _parse_source_report(
    raw: bytes,
) -> tuple[dict[str, object], str, str]:
    if not isinstance(raw, bytes) or not raw:
        raise ValueError("DEC-357 source bytes must be non-empty")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("DEC-357 source artifact is invalid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("DEC-357 source JSON root must be an object")

    exact = {
        "decision": "DEC-355",
        "version": (
            "fmp-exp062-one-shot-historical-executor-dormant-workflow-source-v1"
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_DORMANT_TEMPLATE_SOURCE_"
            "FROZEN_ACTIVE_WORKFLOW_UNINSTALLED"
        ),
        "source_blobs": {
            "dec354_installation_source_contract": (
                "e4fc6a7d1faaca50bc6936597f0e8b66fe096985"
            ),
            "dormant_executor_workflow_template": (
                "51ce87584369be957482460d81649adb1cb9f05d"
            ),
            "active_discovery_workflow": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
        },
        "installation_source_contract_decision": "DEC-354",
        "dormant_executor_workflow_template_path": (
            "docs/superpowers/templates/"
            "phase8a-exp062-one-shot-historical-executor.yml.disabled"
        ),
        "dormant_executor_workflow_template_blob_sha": (
            "51ce87584369be957482460d81649adb1cb9f05d"
        ),
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "active_discovery_workflow_path": (
            ".github/workflows/phase8a-exp062-discovery.yml"
        ),
        "active_discovery_workflow_blob_sha": (
            "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
        ),
        "dormant_executor_workflow_template_present": True,
        "dormant_template_dispatch_capable_if_installed": True,
        "dormant_template_actions_write_required_if_installed": True,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "historical_executor_workflow_install_authorized": False,
        "historical_executor_workflow_installed": False,
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
            "REPOSITORY_HOSTED_READ_ONLY_DORMANT_ONE_SHOT_HISTORICAL_"
            "EXECUTOR_WORKFLOW_SOURCE_PROOF"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-357 source report {field} mismatch")
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-357 source report {field} must remain false"
            )

    return (
        value,
        hashlib.sha256(raw).hexdigest(),
        hashlib.sha256(_canonical_json(value)).hexdigest(),
    )


def review_dormant_one_shot_historical_executor_source_proof(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    source_bytes: bytes,
    expected_head_sha: str,
    repository_root: Path = Path("."),
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    source_blobs = (
        validate_dormant_one_shot_historical_executor_source_proof_review_sources(
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
            raise ValueError(f"DEC-357 proof run {field} mismatch")
    run_id = _positive_int(run.get("id"), field="DEC-357 proof run id")

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 1:
        raise ValueError("DEC-357 proof requires exactly one job")
    job = jobs[0]
    if not isinstance(job, Mapping):
        raise ValueError("DEC-357 proof job row is malformed")
    if job.get("name") != PROOF_JOB_NAME:
        raise ValueError("DEC-357 proof job name mismatch")
    if job.get("status") != "completed":
        raise ValueError("DEC-357 proof job status mismatch")
    if job.get("conclusion") != "success":
        raise ValueError("DEC-357 proof job conclusion mismatch")
    job_id = _positive_int(job.get("id"), field="DEC-357 proof job id")

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-357 proof requires exactly one artifact")
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-357 proof artifact row is malformed")
    artifact_id = _positive_int(
        artifact.get("id"),
        field="DEC-357 proof artifact id",
    )
    artifact_name = (
        "exp062-dec356-dormant-one-shot-historical-executor-source-"
        f"{expected_head_sha}"
    )
    if artifact.get("name") != artifact_name:
        raise ValueError("DEC-357 proof artifact name mismatch")
    if artifact.get("expired") is not False:
        raise ValueError("DEC-357 proof artifact must be non-expired")
    artifact_digest = _sha256_digest(
        artifact.get("digest"),
        field="DEC-357 proof artifact digest",
    )

    source_report, raw_sha256, canonical_sha256 = _parse_source_report(
        source_bytes
    )

    return {
        "decision": (
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION
        ),
        "version": (
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION
        ),
        "stage": (
            "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "REVIEWED_ACTIVE_WORKFLOW_UNINSTALLED"
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
        "source_raw_sha256": raw_sha256,
        "source_canonical_sha256": canonical_sha256,
        "dormant_source_decision": source_report["decision"],
        "dormant_source_version": source_report["version"],
        "dormant_executor_workflow_template_blob_sha": source_report[
            "dormant_executor_workflow_template_blob_sha"
        ],
        "expected_executor_workflow_path": source_report[
            "expected_executor_workflow_path"
        ],
        "dormant_executor_workflow_template_present": True,
        "dormant_template_dispatch_capable_if_installed": True,
        "dormant_template_actions_write_required_if_installed": True,
        "historical_gate_proof_run_id": source_report[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "historical_executor_workflow_install_authorized": False,
        "historical_executor_workflow_installed": False,
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
            "IMMUTABLE_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "SOURCE_PROOF_FREEZE_BEFORE_INSTALL"
        ),
    }


__all__ = [
    "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION",
    "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION",
    "review_dormant_one_shot_historical_executor_source_proof",
    "validate_dormant_one_shot_historical_executor_source_proof_review_sources",
]
