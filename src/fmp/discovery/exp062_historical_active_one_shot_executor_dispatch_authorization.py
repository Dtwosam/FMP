from __future__ import annotations

import hashlib
from pathlib import Path

from .exp062_historical_active_one_shot_executor_dispatch_preflight_proof_runtime_freeze import (
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION,
)


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_DECISION = (
    "DEC-430"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-dispatch-authorization-v1"
)

DEC429_RUNTIME_FREEZE_BLOB_SHA = "98fbb04a78efeef0a9a1fc919b5e5d61093c09de"
DEC429_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "a561a4a66111c5c2edc3183e68a978b01ead42f9b8f8c8c061244b50fc751dac"
)
ACTIVE_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
)
ACTIVE_EXECUTOR_WORKFLOW_BLOB_SHA = (
    "51ce87584369be957482460d81649adb1cb9f05d"
)

EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZED = True
HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED = True
HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED = True
HISTORICAL_EXECUTOR_AVAILABLE = True
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = True
HISTORICAL_EXECUTE_MODE_AVAILABLE = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def validate_active_one_shot_historical_executor_dispatch_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    runtime_path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_active_one_shot_executor_dispatch_preflight_proof_runtime_freeze.py"
    )
    active_path = root / ACTIVE_EXECUTOR_WORKFLOW_PATH

    if not runtime_path.is_file():
        raise ValueError(f"missing DEC-430 source dependency: {runtime_path}")
    runtime_sha = _git_blob_sha(runtime_path)
    if runtime_sha != DEC429_RUNTIME_FREEZE_BLOB_SHA:
        raise ValueError("DEC-430 DEC-429 runtime-freeze Git blob mismatch")

    if not active_path.is_file():
        raise ValueError("DEC-430 requires installed executor workflow present")
    active_sha = _git_blob_sha(active_path)
    if active_sha != ACTIVE_EXECUTOR_WORKFLOW_BLOB_SHA:
        raise ValueError("DEC-430 active executor workflow Git blob mismatch")

    return {
        "dec429_runtime_freeze": runtime_sha,
        "active_executor_workflow": active_sha,
    }


def build_active_one_shot_historical_executor_dispatch_authorization(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source_blobs = (
        validate_active_one_shot_historical_executor_dispatch_authorization_sources(
            repository_root=repository_root,
        )
    )

    return {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_AUTHORIZED_RUN_NOT_STARTED"
        ),
        **source_blobs,
        "authorization_basis": "explicit_operator_authorization",
        "explicit_one_shot_executor_dispatch_authorized": (
            EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZED
        ),
        "runtime_freeze_decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "runtime_freeze_version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "runtime_freeze_fingerprint_sha256": (
            DEC429_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "active_executor_workflow_path": ACTIVE_EXECUTOR_WORKFLOW_PATH,
        "active_executor_workflow_blob_sha": ACTIVE_EXECUTOR_WORKFLOW_BLOB_SHA,
        "executor_workflow_run_count": 0,
        "expected_executor_run_number": 1,
        "expected_executor_run_attempt": 1,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "historical_executor_workflow_install_authorized": (
            HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED
        ),
        "historical_executor_workflow_installed": (
            HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED
        ),
        "historical_executor_available": HISTORICAL_EXECUTOR_AVAILABLE,
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_execute_mode_available": (
            HISTORICAL_EXECUTE_MODE_AVAILABLE
        ),
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": (
            CANDIDATE_COMPILATION_AUTHORIZED
        ),
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": (
            "READ_ONLY_CURRENT_MAIN_ONE_SHOT_EXECUTOR_"
            "DISPATCH_ACTION_PREFLIGHT_BEFORE_RUN"
        ),
    }


__all__ = [
    "ACTIVE_EXECUTOR_WORKFLOW_BLOB_SHA",
    "ACTIVE_EXECUTOR_WORKFLOW_PATH",
    "DEC429_RUNTIME_FREEZE_BLOB_SHA",
    "DEC429_RUNTIME_FREEZE_FINGERPRINT_SHA256",
    "EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZED",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "build_active_one_shot_historical_executor_dispatch_authorization",
    "validate_active_one_shot_historical_executor_dispatch_authorization_sources",
]
