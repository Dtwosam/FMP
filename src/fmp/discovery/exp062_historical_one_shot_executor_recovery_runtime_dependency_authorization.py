from __future__ import annotations

import hashlib
from pathlib import Path


EXP062_RECOVERY_RUNTIME_DEPENDENCY_RECOVERY_AUTHORIZATION_DECISION = "DEC-439"
EXP062_RECOVERY_RUNTIME_DEPENDENCY_RECOVERY_AUTHORIZATION_VERSION = (
    "fmp-exp062-recovery-runtime-dependency-recovery-authorization-v1"
)

DEC436_RECOVERY_AUTHORIZATION_BLOB_SHA = (
    "481fbfbb43557b1b42c0d9bc84ded0775816714e"
)
DEC436_RECOVERY_WORKFLOW_BLOB_SHA = (
    "a2520a108373d25d67dd470794eeb4f0fc9e3187"
)
ORIGINAL_EXECUTOR_WORKFLOW_BLOB_SHA = (
    "51ce87584369be957482460d81649adb1cb9f05d"
)
DISCOVERY_WORKFLOW_BLOB_SHA = (
    "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
)
PINNED_PLANNING_RUNTIME_BLOB_SHA = (
    "1ff32214dee10d877a067e750cd69ffad96d5fe5"
)

FAILED_ORIGINAL_EXECUTOR_RUN_ID = 36702494195
FAILED_ORIGINAL_EXECUTOR_JOB_ID = 109844958600
FAILED_ORIGINAL_EXECUTOR_HEAD_SHA = (
    "59b55d519449e20cf396d70ed9a5722b989d933a"
)
FAILED_ORIGINAL_EXECUTOR_RUN_NUMBER = 2
FAILED_ORIGINAL_EXECUTOR_RUN_ATTEMPT = 1

FAILED_DEC436_RECOVERY_RUN_ID = 36707978889
FAILED_DEC436_RECOVERY_JOB_ID = 109862691026
FAILED_DEC436_RECOVERY_HEAD_SHA = (
    "ed757a631dfe9ec7065cf95db04b446034da45e4"
)
FAILED_DEC436_RECOVERY_RUN_NUMBER = 1
FAILED_DEC436_RECOVERY_RUN_ATTEMPT = 1

SECOND_RECOVERY_WORKFLOW_PATH = (
    ".github/workflows/"
    "phase8a-exp062-one-shot-historical-executor-recovery-runtime-dependency.yml"
)
EXPECTED_SECOND_RECOVERY_RUN_NUMBER = 1
EXPECTED_SECOND_RECOVERY_RUN_ATTEMPT = 1
EXPECTED_TARGET_RUN_NUMBER = 2
EXPECTED_TARGET_RUN_ATTEMPT = 1


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def validate_recovery_runtime_dependency_recovery_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec436_recovery_authorization": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_recovery_authorization.py",
            DEC436_RECOVERY_AUTHORIZATION_BLOB_SHA,
        ),
        "dec436_recovery_workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor-recovery.yml",
            DEC436_RECOVERY_WORKFLOW_BLOB_SHA,
        ),
        "original_executor_workflow": (
            root
            / ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor.yml",
            ORIGINAL_EXECUTOR_WORKFLOW_BLOB_SHA,
        ),
        "active_discovery_workflow": (
            root / ".github/workflows/phase8a-exp062-discovery.yml",
            DISCOVERY_WORKFLOW_BLOB_SHA,
        ),
        "pinned_planning_runtime": (
            root / "requirements/exp061-discovery-run.txt",
            PINNED_PLANNING_RUNTIME_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-439 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-439 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def build_recovery_runtime_dependency_recovery_authorization(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source_blobs = (
        validate_recovery_runtime_dependency_recovery_authorization_sources(
            repository_root=repository_root,
        )
    )
    return {
        "decision": (
            EXP062_RECOVERY_RUNTIME_DEPENDENCY_RECOVERY_AUTHORIZATION_DECISION
        ),
        "version": (
            EXP062_RECOVERY_RUNTIME_DEPENDENCY_RECOVERY_AUTHORIZATION_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_RUNTIME_DEPENDENCY_"
            "RECOVERY_AUTHORIZED_HISTORICAL_RESULT_NOT_STARTED"
        ),
        **source_blobs,
        "authorization_basis": (
            "explicit_recovery_after_dec436_missing_pinned_runtime_dependency"
        ),
        "failed_original_executor_run_id": FAILED_ORIGINAL_EXECUTOR_RUN_ID,
        "failed_original_executor_job_id": FAILED_ORIGINAL_EXECUTOR_JOB_ID,
        "failed_original_executor_head_sha": FAILED_ORIGINAL_EXECUTOR_HEAD_SHA,
        "failed_original_executor_run_number": (
            FAILED_ORIGINAL_EXECUTOR_RUN_NUMBER
        ),
        "failed_original_executor_run_attempt": (
            FAILED_ORIGINAL_EXECUTOR_RUN_ATTEMPT
        ),
        "failed_original_executor_conclusion": "failure",
        "failed_original_executor_dispatched_historical_result": False,
        "failed_dec436_recovery_run_id": FAILED_DEC436_RECOVERY_RUN_ID,
        "failed_dec436_recovery_job_id": FAILED_DEC436_RECOVERY_JOB_ID,
        "failed_dec436_recovery_head_sha": FAILED_DEC436_RECOVERY_HEAD_SHA,
        "failed_dec436_recovery_run_number": (
            FAILED_DEC436_RECOVERY_RUN_NUMBER
        ),
        "failed_dec436_recovery_run_attempt": (
            FAILED_DEC436_RECOVERY_RUN_ATTEMPT
        ),
        "failed_dec436_recovery_conclusion": "failure",
        "failed_dec436_recovery_failed_step": (
            "Require exact DEC-436 recovery authorization"
        ),
        "failed_dec436_recovery_error_type": "ModuleNotFoundError",
        "failed_dec436_recovery_missing_dependency": "polars",
        "failed_dec436_recovery_dispatched_historical_result": False,
        "failed_dec436_recovery_receipt_uploaded": False,
        "expected_second_recovery_run_number": (
            EXPECTED_SECOND_RECOVERY_RUN_NUMBER
        ),
        "expected_second_recovery_run_attempt": (
            EXPECTED_SECOND_RECOVERY_RUN_ATTEMPT
        ),
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": EXPECTED_TARGET_RUN_NUMBER,
        "expected_target_run_attempt": EXPECTED_TARGET_RUN_ATTEMPT,
        "explicit_one_shot_runtime_dependency_recovery_dispatch_authorized": True,
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
        "next_gate": (
            "MANUAL_DEC439_RUNTIME_DEPENDENCY_RECOVERY_WORKFLOW_"
            "RUN_1_ATTEMPT_1"
        ),
    }


__all__ = [
    "DEC436_RECOVERY_AUTHORIZATION_BLOB_SHA",
    "DEC436_RECOVERY_WORKFLOW_BLOB_SHA",
    "DISCOVERY_WORKFLOW_BLOB_SHA",
    "EXPECTED_SECOND_RECOVERY_RUN_ATTEMPT",
    "EXPECTED_SECOND_RECOVERY_RUN_NUMBER",
    "EXPECTED_TARGET_RUN_ATTEMPT",
    "EXPECTED_TARGET_RUN_NUMBER",
    "EXP062_RECOVERY_RUNTIME_DEPENDENCY_RECOVERY_AUTHORIZATION_DECISION",
    "EXP062_RECOVERY_RUNTIME_DEPENDENCY_RECOVERY_AUTHORIZATION_VERSION",
    "FAILED_DEC436_RECOVERY_HEAD_SHA",
    "FAILED_DEC436_RECOVERY_JOB_ID",
    "FAILED_DEC436_RECOVERY_RUN_ATTEMPT",
    "FAILED_DEC436_RECOVERY_RUN_ID",
    "FAILED_DEC436_RECOVERY_RUN_NUMBER",
    "FAILED_ORIGINAL_EXECUTOR_HEAD_SHA",
    "FAILED_ORIGINAL_EXECUTOR_JOB_ID",
    "FAILED_ORIGINAL_EXECUTOR_RUN_ATTEMPT",
    "FAILED_ORIGINAL_EXECUTOR_RUN_ID",
    "FAILED_ORIGINAL_EXECUTOR_RUN_NUMBER",
    "ORIGINAL_EXECUTOR_WORKFLOW_BLOB_SHA",
    "PINNED_PLANNING_RUNTIME_BLOB_SHA",
    "SECOND_RECOVERY_WORKFLOW_PATH",
    "build_recovery_runtime_dependency_recovery_authorization",
    "validate_recovery_runtime_dependency_recovery_authorization_sources",
]
