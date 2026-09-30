from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .exp062_historical_active_one_shot_executor_workflow_install_receipt import (
    ACTIVE_EXECUTOR_WORKFLOW_PATH,
    EXECUTOR_WORKFLOW_BLOB_SHA,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_DECISION,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_VERSION,
    HISTORICAL_EXECUTOR_AVAILABLE as RECEIPT_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED as RECEIPT_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE as RECEIPT_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED as RECEIPT_DISPATCH_AUTHORIZED,
)
from .exp062_historical_run_authorization import classify_historical_run_inventory


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_DECISION = (
    "DEC-425"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-dispatch-preflight-v1"
)

DEC424_INSTALL_RECEIPT_BLOB_SHA = "27e714620018413a09ceaf287fb7943bf884ee49"


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


def validate_active_one_shot_historical_executor_dispatch_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    receipt_path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_active_one_shot_executor_workflow_install_receipt.py"
    )
    active_path = root / ACTIVE_EXECUTOR_WORKFLOW_PATH

    if not receipt_path.is_file():
        raise ValueError(f"missing DEC-425 source dependency: {receipt_path}")
    receipt_sha = _git_blob_sha(receipt_path)
    if receipt_sha != DEC424_INSTALL_RECEIPT_BLOB_SHA:
        raise ValueError("DEC-425 DEC-424 install-receipt Git blob mismatch")

    if not active_path.is_file():
        raise ValueError("DEC-425 requires installed executor workflow present")
    active_sha = _git_blob_sha(active_path)
    if active_sha != EXECUTOR_WORKFLOW_BLOB_SHA:
        raise ValueError("DEC-425 active executor workflow Git blob mismatch")

    if RECEIPT_WORKFLOW_INSTALLED is not True:
        raise ValueError("DEC-425 requires installed workflow state")
    if RECEIPT_EXECUTOR_AVAILABLE is not True:
        raise ValueError("DEC-425 requires executor availability")
    if RECEIPT_DISPATCH_AUTHORIZED is not False:
        raise ValueError("DEC-425 requires dispatch authorization false")
    if RECEIPT_EXECUTE_MODE_AVAILABLE is not False:
        raise ValueError("DEC-425 requires execute mode false")

    return {
        "dec424_install_receipt_blob_sha": receipt_sha,
        "active_executor_workflow_blob_sha": active_sha,
    }


def _validate_executor_run_inventory(
    value: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("DEC-425 executor workflow_runs must be a list")

    if runs:
        raise ValueError(
            "DEC-425 requires zero executor workflow runs before dispatch authorization"
        )

    return {
        "executor_workflow_run_count": 0,
        "executor_workflow_run_id": None,
        "executor_workflow_run_status": None,
        "executor_workflow_run_conclusion": None,
    }


def build_active_one_shot_historical_executor_dispatch_preflight(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    executor_workflow_runs: Mapping[str, object],
    discovery_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    root = Path(repository_root)
    source = validate_active_one_shot_historical_executor_dispatch_preflight_sources(
        repository_root=root,
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )

    if main_branch.get("name") != "main":
        raise ValueError("DEC-425 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-425 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-425 main head mismatch")

    executor_inventory = _validate_executor_run_inventory(
        executor_workflow_runs,
    )
    historical_inventory = classify_historical_run_inventory(
        discovery_workflow_runs
    )
    if historical_inventory["stage"] != "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE":
        raise ValueError(
            "DEC-425 requires unused historical-result slot before dispatch"
        )
    if historical_inventory["historical_result_attempt_count"] != 0:
        raise ValueError("DEC-425 historical-result attempt count mismatch")
    if historical_inventory["historical_result_slot_consumed"] is not False:
        raise ValueError("DEC-425 historical-result slot must remain unused")

    return {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_VERSION
        ),
        "install_receipt_decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_DECISION
        ),
        "install_receipt_version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_VERSION
        ),
        **source,
        "expected_head_sha": expected_head_sha,
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_PREFLIGHT_INSTALLED_EXECUTOR_READY_RUNTIME_LOCKED"
        ),
        "active_executor_workflow_path": ACTIVE_EXECUTOR_WORKFLOW_PATH,
        "active_executor_workflow_present": True,
        "historical_executor_workflow_install_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        **executor_inventory,
        "historical_gate_proof_run_id": historical_inventory["proof_run_id"],
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
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
        "next_gate": (
            "EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
    }


def validate_active_one_shot_historical_executor_dispatch_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    expected = {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_VERSION
        ),
        "install_receipt_decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_DECISION
        ),
        "install_receipt_version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_PREFLIGHT_INSTALLED_EXECUTOR_READY_RUNTIME_LOCKED"
        ),
        "active_executor_workflow_path": ACTIVE_EXECUTOR_WORKFLOW_PATH,
        "active_executor_workflow_present": True,
        "historical_executor_workflow_install_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "executor_workflow_run_count": 0,
        "executor_workflow_run_id": None,
        "executor_workflow_run_status": None,
        "executor_workflow_run_conclusion": None,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
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
        "next_gate": (
            "EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-425 {field} mismatch")

    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    return value


__all__ = [
    "DEC424_INSTALL_RECEIPT_BLOB_SHA",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_VERSION",
    "build_active_one_shot_historical_executor_dispatch_preflight",
    "validate_active_one_shot_historical_executor_dispatch_preflight",
    "validate_active_one_shot_historical_executor_dispatch_preflight_sources",
]
