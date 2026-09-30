from __future__ import annotations

import hashlib
import shlex
from pathlib import Path
from typing import Mapping, Sequence

from .exp062_historical_active_one_shot_executor_dispatch_authorization import (
    ACTIVE_EXECUTOR_WORKFLOW_BLOB_SHA,
    ACTIVE_EXECUTOR_WORKFLOW_PATH,
    EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZED,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_DECISION,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_VERSION,
    HISTORICAL_EXECUTOR_AVAILABLE as AUTH_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED as AUTH_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE as AUTH_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED as AUTH_DISPATCH_AUTHORIZED,
)
from .exp062_historical_run_authorization import classify_historical_run_inventory


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_DECISION = (
    "DEC-431"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-dispatch-action-preflight-v1"
)
DEC430_DISPATCH_AUTHORIZATION_BLOB_SHA = (
    "87aada4c5224c633e8eb419f971c8f7f0699b18f"
)


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


def executor_dispatch_command() -> tuple[str, ...]:
    return (
        "gh",
        "workflow",
        "run",
        "phase8a-exp062-one-shot-historical-executor.yml",
        "--ref",
        "main",
    )


def shell_join(parts: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def validate_active_one_shot_historical_executor_dispatch_action_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    auth_path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_active_one_shot_executor_dispatch_authorization.py"
    )
    active_path = root / ACTIVE_EXECUTOR_WORKFLOW_PATH

    if not auth_path.is_file():
        raise ValueError(f"missing DEC-431 source dependency: {auth_path}")
    auth_sha = _git_blob_sha(auth_path)
    if auth_sha != DEC430_DISPATCH_AUTHORIZATION_BLOB_SHA:
        raise ValueError("DEC-431 DEC-430 authorization Git blob mismatch")

    if not active_path.is_file():
        raise ValueError("DEC-431 requires installed executor workflow")
    active_sha = _git_blob_sha(active_path)
    if active_sha != ACTIVE_EXECUTOR_WORKFLOW_BLOB_SHA:
        raise ValueError("DEC-431 active executor workflow Git blob mismatch")

    if EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZED is not True:
        raise ValueError("DEC-431 requires explicit one-shot authorization")
    if AUTH_WORKFLOW_INSTALLED is not True:
        raise ValueError("DEC-431 requires installed workflow")
    if AUTH_EXECUTOR_AVAILABLE is not True:
        raise ValueError("DEC-431 requires executor availability")
    if AUTH_DISPATCH_AUTHORIZED is not True:
        raise ValueError("DEC-431 requires dispatch authorization")
    if AUTH_EXECUTE_MODE_AVAILABLE is not False:
        raise ValueError("DEC-431 requires general execute mode locked")

    return {
        "dec430_dispatch_authorization_blob_sha": auth_sha,
        "active_executor_workflow_blob_sha": active_sha,
    }


def _validate_executor_inventory(value: Mapping[str, object]) -> None:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("DEC-431 executor workflow_runs must be a list")
    if runs:
        raise ValueError("DEC-431 requires zero executor workflow runs")


def build_active_one_shot_historical_executor_dispatch_action_preflight(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    executor_workflow_runs: Mapping[str, object],
    discovery_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = (
        validate_active_one_shot_historical_executor_dispatch_action_preflight_sources(
            repository_root=repository_root,
        )
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )

    if main_branch.get("name") != "main":
        raise ValueError("DEC-431 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-431 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-431 main head mismatch")

    _validate_executor_inventory(executor_workflow_runs)

    inventory = classify_historical_run_inventory(discovery_workflow_runs)
    if inventory["stage"] != "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE":
        raise ValueError("DEC-431 requires unused historical-result slot")
    if inventory["historical_result_attempt_count"] != 0:
        raise ValueError("DEC-431 historical-result attempt count mismatch")
    if inventory["historical_result_slot_consumed"] is not False:
        raise ValueError("DEC-431 historical-result slot must remain unused")

    return {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_VERSION
        ),
        "authorization_decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_DECISION
        ),
        "authorization_version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_VERSION
        ),
        **source,
        "expected_head_sha": expected_head_sha,
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_ACTION_PREFLIGHT_AUTHORIZED_SLOT_AVAILABLE"
        ),
        "active_executor_workflow_path": ACTIVE_EXECUTOR_WORKFLOW_PATH,
        "active_executor_workflow_present": True,
        "executor_workflow_run_count": 0,
        "expected_executor_run_number": 1,
        "expected_executor_run_attempt": 1,
        "historical_gate_proof_run_id": inventory["proof_run_id"],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_executor_dispatch_command": shell_join(
            executor_dispatch_command()
        ),
        "explicit_one_shot_executor_dispatch_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "historical_result_dispatch_authorized": True,
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
            "REPOSITORY_HOSTED_READ_ONLY_ONE_SHOT_EXECUTOR_"
            "DISPATCH_ACTION_PREFLIGHT_PROOF"
        ),
    }


def validate_active_one_shot_historical_executor_dispatch_action_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    expected = {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_VERSION
        ),
        "authorization_decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_DECISION
        ),
        "authorization_version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_AUTHORIZATION_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_ACTION_PREFLIGHT_AUTHORIZED_SLOT_AVAILABLE"
        ),
        "active_executor_workflow_path": ACTIVE_EXECUTOR_WORKFLOW_PATH,
        "active_executor_workflow_present": True,
        "executor_workflow_run_count": 0,
        "expected_executor_run_number": 1,
        "expected_executor_run_attempt": 1,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_executor_dispatch_command": shell_join(
            executor_dispatch_command()
        ),
        "explicit_one_shot_executor_dispatch_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "historical_result_dispatch_authorized": True,
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
            "REPOSITORY_HOSTED_READ_ONLY_ONE_SHOT_EXECUTOR_"
            "DISPATCH_ACTION_PREFLIGHT_PROOF"
        ),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-431 {field} mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    return value


__all__ = [
    "DEC430_DISPATCH_AUTHORIZATION_BLOB_SHA",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_VERSION",
    "build_active_one_shot_historical_executor_dispatch_action_preflight",
    "executor_dispatch_command",
    "shell_join",
    "validate_active_one_shot_historical_executor_dispatch_action_preflight",
    "validate_active_one_shot_historical_executor_dispatch_action_preflight_sources",
]
