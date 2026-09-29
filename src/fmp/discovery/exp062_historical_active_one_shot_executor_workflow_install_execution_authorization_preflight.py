from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .exp062_historical_active_one_shot_executor_workflow_install_execution_authorization_contract import (
    ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_SOURCE_AUTHORIZED,
    DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA,
    DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH,
    EXPECTED_EXECUTOR_WORKFLOW_PATH,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT_DECISION,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT_VERSION,
    HISTORICAL_EXECUTOR_AVAILABLE as CONTRACT_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED as CONTRACT_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED as CONTRACT_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE as CONTRACT_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED as CONTRACT_DISPATCH_AUTHORIZED,
)
from .exp062_historical_run_authorization import classify_historical_run_inventory


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT_DECISION = (
    "DEC-385"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-workflow-install-execution-authorization-preflight-v1"
)

DEC384_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT_BLOB_SHA = (
    "40a3164fe713baf4289099e829527abc3da94c6e"
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


def validate_active_one_shot_historical_executor_workflow_install_execution_authorization_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    contract_path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_active_one_shot_executor_workflow_install_execution_authorization_contract.py"
    )
    template_path = root / DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH

    if not contract_path.is_file():
        raise ValueError(f"missing DEC-385 source dependency: {contract_path}")
    contract_sha = _git_blob_sha(contract_path)
    if contract_sha != DEC384_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT_BLOB_SHA:
        raise ValueError(
            "DEC-385 DEC-384 install-execution-authorization-contract Git blob mismatch: "
            f"{contract_sha} != {DEC384_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT_BLOB_SHA}"
        )

    if not template_path.is_file():
        raise ValueError("DEC-385 requires dormant executor template present")
    template_sha = _git_blob_sha(template_path)
    if template_sha != DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-385 dormant executor template Git blob mismatch")

    if (
        ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_SOURCE_AUTHORIZED
        is not True
    ):
        raise ValueError("DEC-385 requires install-execution authorization source")
    if CONTRACT_INSTALL_AUTHORIZED is not False:
        raise ValueError("DEC-385 requires install authorization false")
    if CONTRACT_WORKFLOW_INSTALLED is not False:
        raise ValueError("DEC-385 requires installed state false")
    if CONTRACT_EXECUTOR_AVAILABLE is not False:
        raise ValueError("DEC-385 requires executor availability false")
    if CONTRACT_DISPATCH_AUTHORIZED is not False:
        raise ValueError("DEC-385 requires dispatch authorization false")
    if CONTRACT_EXECUTE_MODE_AVAILABLE is not False:
        raise ValueError("DEC-385 requires execute mode false")

    return {
        "dec384_install_execution_authorization_contract_blob_sha": contract_sha,
        "dormant_executor_workflow_template_blob_sha": template_sha,
    }


def build_active_one_shot_historical_executor_workflow_install_execution_authorization_preflight(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    root = Path(repository_root)
    source = (
        validate_active_one_shot_historical_executor_workflow_install_execution_authorization_preflight_sources(
            repository_root=root,
        )
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )

    if main_branch.get("name") != "main":
        raise ValueError("DEC-385 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-385 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-385 main head mismatch")

    if (root / EXPECTED_EXECUTOR_WORKFLOW_PATH).exists():
        raise ValueError(
            "DEC-385 requires active executor workflow path to remain absent"
        )

    inventory = classify_historical_run_inventory(workflow_runs)
    if inventory["stage"] != "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE":
        raise ValueError(
            "DEC-385 install-execution authorization preflight requires unused historical slot"
        )
    if inventory["historical_result_attempt_count"] != 0:
        raise ValueError("DEC-385 empty slot attempt count mismatch")
    if inventory["historical_result_slot_consumed"] is not False:
        raise ValueError("DEC-385 empty slot marked consumed")

    return {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT_VERSION
        ),
        "install_execution_authorization_contract_decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT_DECISION
        ),
        "install_execution_authorization_contract_version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT_VERSION
        ),
        **source,
        "expected_head_sha": expected_head_sha,
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "EXECUTION_AUTHORIZATION_PREFLIGHT_SOURCE_READY_ACTIVE_WORKFLOW_ABSENT_SLOT_AVAILABLE"
        ),
        "dormant_executor_workflow_template_path": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH
        ),
        "dormant_executor_workflow_template_present": True,
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "install_execution_authorization_slot_verified_available": True,
        "proof_run_id": inventory["proof_run_id"],
        "proof_run_count": inventory["proof_run_count"],
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_decision_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": True,
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
            "REPOSITORY_HOSTED_READ_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT_PROOF"
        ),
    }


def validate_active_one_shot_historical_executor_workflow_install_execution_authorization_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    expected = {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT_VERSION
        ),
        "install_execution_authorization_contract_decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT_DECISION
        ),
        "install_execution_authorization_contract_version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "EXECUTION_AUTHORIZATION_PREFLIGHT_SOURCE_READY_ACTIVE_WORKFLOW_ABSENT_SLOT_AVAILABLE"
        ),
        "dormant_executor_workflow_template_path": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH
        ),
        "dormant_executor_workflow_template_present": True,
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "install_execution_authorization_slot_verified_available": True,
        "proof_run_count": 1,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_decision_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": True,
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
            "REPOSITORY_HOSTED_READ_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT_PROOF"
        ),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-385 {field} mismatch")

    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    return value


__all__ = [
    "DEC384_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT_BLOB_SHA",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT_VERSION",
    "build_active_one_shot_historical_executor_workflow_install_execution_authorization_preflight",
    "validate_active_one_shot_historical_executor_workflow_install_execution_authorization_preflight",
    "validate_active_one_shot_historical_executor_workflow_install_execution_authorization_preflight_sources",
]
