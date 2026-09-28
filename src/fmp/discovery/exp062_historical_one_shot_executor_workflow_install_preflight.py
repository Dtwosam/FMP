from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .exp062_historical_one_shot_executor_workflow_install_contract import (
    EXPECTED_EXECUTOR_WORKFLOW_PATH,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_DECISION,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_VERSION,
    HISTORICAL_EXECUTOR_AVAILABLE as CONTRACT_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED as CONTRACT_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE as CONTRACT_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED as CONTRACT_DISPATCH_AUTHORIZED,
    ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED,
)
from .exp062_historical_run_authorization import (
    classify_historical_run_inventory,
)


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_DECISION = "DEC-349"
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_VERSION = (
    "fmp-exp062-one-shot-historical-executor-workflow-install-preflight-v1"
)

DEC348_INSTALL_CONTRACT_BLOB_SHA = "111a56fdbb8844c119307465e7b7cf6a4d43d95a"

HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED = False
HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED = False
HISTORICAL_EXECUTOR_AVAILABLE = False
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
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


def validate_one_shot_historical_executor_workflow_install_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    contract_path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_one_shot_executor_workflow_install_contract.py"
    )
    if not contract_path.is_file():
        raise ValueError(f"missing DEC-349 source dependency: {contract_path}")
    actual = _git_blob_sha(contract_path)
    if actual != DEC348_INSTALL_CONTRACT_BLOB_SHA:
        raise ValueError(
            "DEC-349 DEC-348 install-contract Git blob mismatch: "
            f"{actual} != {DEC348_INSTALL_CONTRACT_BLOB_SHA}"
        )

    if ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED is not True:
        raise ValueError("DEC-349 requires install-source authorization")
    if CONTRACT_WORKFLOW_INSTALLED is not False:
        raise ValueError("DEC-349 requires workflow installed=false")
    if CONTRACT_EXECUTOR_AVAILABLE is not False:
        raise ValueError("DEC-349 requires executor availability false")
    if CONTRACT_DISPATCH_AUTHORIZED is not False:
        raise ValueError("DEC-349 requires dispatch authorization false")
    if CONTRACT_EXECUTE_MODE_AVAILABLE is not False:
        raise ValueError("DEC-349 requires execute mode false")

    return {"dec348_install_contract_blob_sha": actual}


def build_one_shot_historical_executor_workflow_install_preflight(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    root = Path(repository_root)
    source = validate_one_shot_historical_executor_workflow_install_preflight_sources(
        repository_root=root,
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )

    if main_branch.get("name") != "main":
        raise ValueError("DEC-349 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-349 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-349 main head mismatch")

    executor_workflow_path = root / EXPECTED_EXECUTOR_WORKFLOW_PATH
    if executor_workflow_path.exists():
        raise ValueError(
            "DEC-349 requires future executor workflow to remain absent"
        )

    inventory = classify_historical_run_inventory(workflow_runs)
    if inventory["stage"] != "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE":
        raise ValueError(
            "DEC-349 workflow-install preflight requires an unused historical slot"
        )
    if inventory["historical_result_attempt_count"] != 0:
        raise ValueError("DEC-349 empty slot attempt count mismatch")
    if inventory["historical_result_slot_consumed"] is not False:
        raise ValueError("DEC-349 empty slot marked consumed")

    return {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_VERSION
        ),
        "install_contract_decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_DECISION
        ),
        "install_contract_version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_VERSION
        ),
        **source,
        "expected_head_sha": expected_head_sha,
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "PREFLIGHT_SOURCE_ABSENT_SLOT_AVAILABLE"
        ),
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "workflow_install_slot_verified_available": True,
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
        "one_shot_historical_executor_source_authorized": True,
        "one_shot_historical_executor_workflow_source_authorized": True,
        "one_shot_historical_executor_workflow_install_source_authorized": True,
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
            "REPOSITORY_HOSTED_READ_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_PREFLIGHT_PROOF"
        ),
    }


def validate_one_shot_historical_executor_workflow_install_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    expected = {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_VERSION
        ),
        "install_contract_decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_DECISION
        ),
        "install_contract_version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "PREFLIGHT_SOURCE_ABSENT_SLOT_AVAILABLE"
        ),
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "workflow_install_slot_verified_available": True,
        "proof_run_count": 1,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "one_shot_historical_executor_source_authorized": True,
        "one_shot_historical_executor_workflow_source_authorized": True,
        "one_shot_historical_executor_workflow_install_source_authorized": True,
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
            "REPOSITORY_HOSTED_READ_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_PREFLIGHT_PROOF"
        ),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-349 {field} mismatch")

    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    return value


__all__ = [
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_VERSION",
    "build_one_shot_historical_executor_workflow_install_preflight",
    "validate_one_shot_historical_executor_workflow_install_preflight",
    "validate_one_shot_historical_executor_workflow_install_preflight_sources",
]
