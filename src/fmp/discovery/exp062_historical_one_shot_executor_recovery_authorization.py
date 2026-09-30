from __future__ import annotations

import hashlib
from pathlib import Path

from .exp062_historical_one_shot_executor_dispatch_action_preflight_proof_runtime_freeze import (
    EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION,
    EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION,
)


EXP062_ONE_SHOT_EXECUTOR_RECOVERY_AUTHORIZATION_DECISION = "DEC-436"
EXP062_ONE_SHOT_EXECUTOR_RECOVERY_AUTHORIZATION_VERSION = (
    "fmp-exp062-one-shot-executor-recovery-authorization-v1"
)

DEC435_RUNTIME_FREEZE_BLOB_SHA = "d70fb2ef8f55462be278dd22e42a733b5e03fc67"
ORIGINAL_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
)
ORIGINAL_EXECUTOR_WORKFLOW_BLOB_SHA = "51ce87584369be957482460d81649adb1cb9f05d"
DISCOVERY_WORKFLOW_PATH = ".github/workflows/phase8a-exp062-discovery.yml"
DISCOVERY_WORKFLOW_BLOB_SHA = "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"

FAILED_EXECUTOR_RUN_ID = 36702494195
FAILED_EXECUTOR_JOB_ID = 109844958600
FAILED_EXECUTOR_HEAD_SHA = "59b55d519449e20cf396d70ed9a5722b989d933a"
FAILED_EXECUTOR_RUN_NUMBER = 2
FAILED_EXECUTOR_RUN_ATTEMPT = 1
FAILED_EXECUTOR_RUN_CONCLUSION = "failure"
FAILED_EXECUTOR_GUARD_STEP = "Require exact one-shot executor run"

RECOVERY_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor-recovery.yml"
)
EXPECTED_RECOVERY_RUN_NUMBER = 1
EXPECTED_RECOVERY_RUN_ATTEMPT = 1
EXPECTED_TARGET_RUN_NUMBER = 2
EXPECTED_TARGET_RUN_ATTEMPT = 1


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def validate_one_shot_executor_recovery_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec435_runtime_freeze": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_dispatch_action_preflight_proof_runtime_freeze.py",
            DEC435_RUNTIME_FREEZE_BLOB_SHA,
        ),
        "original_executor_workflow": (
            root / ORIGINAL_EXECUTOR_WORKFLOW_PATH,
            ORIGINAL_EXECUTOR_WORKFLOW_BLOB_SHA,
        ),
        "discovery_workflow": (
            root / DISCOVERY_WORKFLOW_PATH,
            DISCOVERY_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-436 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-436 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    if (
        EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION
        != "DEC-435"
    ):
        raise ValueError("DEC-436 predecessor decision drift")
    if (
        EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION
        != "fmp-exp062-one-shot-executor-dispatch-action-preflight-proof-runtime-freeze-v1"
    ):
        raise ValueError("DEC-436 predecessor version drift")

    return actual


def build_one_shot_executor_recovery_authorization(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source_blobs = validate_one_shot_executor_recovery_authorization_sources(
        repository_root=repository_root,
    )
    return {
        "decision": EXP062_ONE_SHOT_EXECUTOR_RECOVERY_AUTHORIZATION_DECISION,
        "version": EXP062_ONE_SHOT_EXECUTOR_RECOVERY_AUTHORIZATION_VERSION,
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_RECOVERY_AUTHORIZED_"
            "HISTORICAL_RESULT_NOT_STARTED"
        ),
        **source_blobs,
        "authorization_basis": (
            "explicit_recovery_after_fail_closed_executor_run_number_drift"
        ),
        "failed_executor_run_id": FAILED_EXECUTOR_RUN_ID,
        "failed_executor_job_id": FAILED_EXECUTOR_JOB_ID,
        "failed_executor_head_sha": FAILED_EXECUTOR_HEAD_SHA,
        "failed_executor_run_number": FAILED_EXECUTOR_RUN_NUMBER,
        "failed_executor_run_attempt": FAILED_EXECUTOR_RUN_ATTEMPT,
        "failed_executor_run_conclusion": FAILED_EXECUTOR_RUN_CONCLUSION,
        "failed_executor_guard_step": FAILED_EXECUTOR_GUARD_STEP,
        "failed_executor_dispatched_historical_result": False,
        "failed_executor_receipt_uploaded": False,
        "original_executor_workflow_path": ORIGINAL_EXECUTOR_WORKFLOW_PATH,
        "recovery_workflow_path": RECOVERY_WORKFLOW_PATH,
        "expected_recovery_run_number": EXPECTED_RECOVERY_RUN_NUMBER,
        "expected_recovery_run_attempt": EXPECTED_RECOVERY_RUN_ATTEMPT,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": EXPECTED_TARGET_RUN_NUMBER,
        "expected_target_run_attempt": EXPECTED_TARGET_RUN_ATTEMPT,
        "explicit_one_shot_executor_recovery_dispatch_authorized": True,
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
            "MANUAL_DEC436_RECOVERY_EXECUTOR_WORKFLOW_RUN_1_ATTEMPT_1"
        ),
    }


__all__ = [
    "DEC435_RUNTIME_FREEZE_BLOB_SHA",
    "DISCOVERY_WORKFLOW_BLOB_SHA",
    "DISCOVERY_WORKFLOW_PATH",
    "EXPECTED_RECOVERY_RUN_ATTEMPT",
    "EXPECTED_RECOVERY_RUN_NUMBER",
    "EXPECTED_TARGET_RUN_ATTEMPT",
    "EXPECTED_TARGET_RUN_NUMBER",
    "EXP062_ONE_SHOT_EXECUTOR_RECOVERY_AUTHORIZATION_DECISION",
    "EXP062_ONE_SHOT_EXECUTOR_RECOVERY_AUTHORIZATION_VERSION",
    "FAILED_EXECUTOR_HEAD_SHA",
    "FAILED_EXECUTOR_JOB_ID",
    "FAILED_EXECUTOR_RUN_ATTEMPT",
    "FAILED_EXECUTOR_RUN_CONCLUSION",
    "FAILED_EXECUTOR_RUN_ID",
    "FAILED_EXECUTOR_RUN_NUMBER",
    "ORIGINAL_EXECUTOR_WORKFLOW_BLOB_SHA",
    "ORIGINAL_EXECUTOR_WORKFLOW_PATH",
    "RECOVERY_WORKFLOW_PATH",
    "build_one_shot_executor_recovery_authorization",
    "validate_one_shot_executor_recovery_authorization_sources",
]
