from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_active_one_shot_executor_workflow_installation_preflight_proof_runtime_freeze import (
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION,
)


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_CONTRACT_DECISION = (
    "DEC-372"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_CONTRACT_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-workflow-install-authorization-contract-v1"
)

DEC371_RUNTIME_FREEZE_BLOB_SHA = "fb9f968fcfc953217234f7484b14d98293087f02"
DEC371_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "a498bf1cae3c6e92803fc750331c3090c35bb3af13bf01a62866831d29bb95f8"
)

DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "phase8a-exp062-one-shot-historical-executor.yml.disabled"
)
DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA = (
    "51ce87584369be957482460d81649adb1cb9f05d"
)
EXPECTED_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
)

ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_SOURCE_AUTHORIZED = (
    True
)
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
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def validate_active_one_shot_historical_executor_workflow_install_authorization_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec371_runtime_freeze": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_active_one_shot_executor_workflow_installation_preflight_proof_runtime_freeze.py",
            DEC371_RUNTIME_FREEZE_BLOB_SHA,
        ),
        "dormant_executor_workflow_template": (
            root / DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH,
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-372 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-372 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    exact = {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_"
            "PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "active_installation_preflight_proof_head_sha": (
            "035c0ee8190a7eb1e2c8ac80771e6eeb19d1e8e1"
        ),
        "active_installation_preflight_proof_run_id": 36484309283,
        "active_installation_preflight_proof_job_id": 109137344254,
        "active_installation_preflight_proof_artifact_id": 10997847720,
        "active_installation_preflight_proof_artifact_digest": (
            "sha256:d122e474752f1ec8127eb610b55321dbf94cc7dcb339eca43eafb7e429ef4a07"
        ),
        "active_installation_preflight_raw_sha256": (
            "5bf7760c7ad36e642eeeaf9e29b5fb0e5108a4059207ff2d7d75bd4c9f6bcf3b"
        ),
        "active_installation_preflight_canonical_sha256": (
            "30de670f8483139b23fbd51bd05444677278fd7d1ba1f1eb8f0cc33409cf3a74"
        ),
        "dec370_freeze_fingerprint_sha256": (
            "51e47a3d6d2876b52e2090714e6f89b4c2ce0ae2d869d79e5b2cd4586c774af6"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "dormant_executor_workflow_template_blob_sha": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
        ),
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "active_one_shot_historical_executor_workflow_installation_source_authorized": True,
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
            "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_AUTHORIZATION_CONTRACT"
        ),
    }
    for field, expected_value in exact.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-372 runtime freeze {field} mismatch")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC371_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC371_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-372 DEC-371 runtime freeze fingerprint mismatch")

    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-372 runtime freeze {field} must remain false")


def build_active_one_shot_historical_executor_workflow_install_authorization_contract(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
) -> dict[str, object]:
    root = Path(repository_root)
    source_blobs = (
        validate_active_one_shot_historical_executor_workflow_install_authorization_contract_sources(
            repository_root=root,
        )
    )
    _validate_runtime_freeze(runtime_freeze)

    active_path = root / EXPECTED_EXECUTOR_WORKFLOW_PATH
    if active_path.exists():
        raise ValueError(
            "DEC-372 requires active executor workflow path to remain absent"
        )

    return {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_CONTRACT_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_CONTRACT_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "AUTHORIZATION_SOURCE_AUTHORIZED_INSTALL_LOCKED"
        ),
        **source_blobs,
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC371_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "terminal_review_decision": "DEC-334",
        "dormant_executor_workflow_template_path": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH
        ),
        "dormant_executor_workflow_template_blob_sha": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
        ),
        "dormant_executor_workflow_template_present": True,
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": (
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_SOURCE_AUTHORIZED
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
            "READ_ONLY_CURRENT_MAIN_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_AUTHORIZATION_PREFLIGHT"
        ),
    }


__all__ = [
    "ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_SOURCE_AUTHORIZED",
    "DEC371_RUNTIME_FREEZE_FINGERPRINT_SHA256",
    "DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA",
    "DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH",
    "EXPECTED_EXECUTOR_WORKFLOW_PATH",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_CONTRACT_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_CONTRACT_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "build_active_one_shot_historical_executor_workflow_install_authorization_contract",
    "validate_active_one_shot_historical_executor_workflow_install_authorization_contract_sources",
]
