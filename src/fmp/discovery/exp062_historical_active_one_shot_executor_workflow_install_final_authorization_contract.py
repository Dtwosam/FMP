from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_active_one_shot_executor_workflow_install_source_preflight_proof_recovery_runtime_freeze import (
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_RUNTIME_FREEZE_DECISION,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_RUNTIME_FREEZE_VERSION,
)


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_DECISION = (
    "DEC-411"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-workflow-install-final-authorization-contract-v1"
)

DEC410_RUNTIME_FREEZE_BLOB_SHA = "705c08d50a8dfcae5391a0b240d78fea5716a8de"
DEC410_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "77fa5c98293226176d71a759af44f23e434987a57c66d343c13f7f727202e853"
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

ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_SOURCE_AUTHORIZED = True
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


def validate_active_one_shot_historical_executor_workflow_install_final_authorization_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    runtime_path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_active_one_shot_executor_workflow_install_source_preflight_proof_recovery_runtime_freeze.py"
    )
    template_path = root / DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH

    if not runtime_path.is_file():
        raise ValueError(f"missing DEC-411 source dependency: {runtime_path}")
    runtime_sha = _git_blob_sha(runtime_path)
    if runtime_sha != DEC410_RUNTIME_FREEZE_BLOB_SHA:
        raise ValueError(
            "DEC-411 DEC-410 runtime-freeze Git blob mismatch: "
            f"{runtime_sha} != {DEC410_RUNTIME_FREEZE_BLOB_SHA}"
        )

    if not template_path.is_file():
        raise ValueError("DEC-411 requires dormant executor template present")
    template_sha = _git_blob_sha(template_path)
    if template_sha != DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-411 dormant executor template Git blob mismatch")

    return {
        "dec410_runtime_freeze": runtime_sha,
        "dormant_executor_workflow_template": template_sha,
    }


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    exact = {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "SOURCE_PREFLIGHT_RECOVERY_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "failed_proof_run_id": 36613664506,
        "failed_proof_head_sha": (
            "0db04ae49b3533778b08afa31e9ef9a26576b80c"
        ),
        "failed_proof_job_id": 109561121322,
        "failed_proof_run_number": 1,
        "failed_proof_run_attempt": 1,
        "failed_proof_run_conclusion": "failure",
        "recovery_proof_head_sha": (
            "3ea7d3f7bfe8f1dfb3bbac612f74255da4fee432"
        ),
        "recovery_proof_run_id": 36616131587,
        "recovery_proof_run_number": 2,
        "recovery_proof_run_attempt": 1,
        "recovery_proof_run_conclusion": "success",
        "recovery_proof_job_id": 109569478100,
        "recovery_proof_artifact_id": 11054938805,
        "recovery_proof_artifact_digest": (
            "sha256:e71ad4c19602bec2c3fa71ad6f76e41eadea53edd5ef310ea2110d251002da25"
        ),
        "recovery_proof_artifact_zip_sha256": (
            "e71ad4c19602bec2c3fa71ad6f76e41eadea53edd5ef310ea2110d251002da25"
        ),
        "recovery_preflight_raw_sha256": (
            "aea9a6f510ee7f5147adb7aea4cba2e9662093dfc2a8465adc9b7aec61556639"
        ),
        "recovery_preflight_canonical_sha256": (
            "4f96d9df7e7e4fba224a376b500539e4581bc34d852178f00796ee7be66f6c6b"
        ),
        "dec408_review_decision": "DEC-408",
        "dec409_freeze_decision": "DEC-409",
        "dec409_freeze_fingerprint_sha256": (
            "c0c04735c57638fde0a57122c240ea6c9aacd86fc7e43cdc532aaf8ba54cd9d3"
        ),
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
        "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_decision_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_activation_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "next_gate": (
            "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "FINAL_AUTHORIZATION_CONTRACT_BEFORE_INSTALL"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-411 runtime freeze {field} mismatch")

    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-411 runtime freeze {field} must remain false")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC410_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC410_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-411 DEC-410 runtime freeze fingerprint mismatch")


def build_active_one_shot_historical_executor_workflow_install_final_authorization_contract(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
) -> dict[str, object]:
    root = Path(repository_root)
    source_blobs = (
        validate_active_one_shot_historical_executor_workflow_install_final_authorization_contract_sources(
            repository_root=root,
        )
    )
    _validate_runtime_freeze(runtime_freeze)

    if (root / EXPECTED_EXECUTOR_WORKFLOW_PATH).exists():
        raise ValueError(
            "DEC-411 requires active executor workflow path to remain absent"
        )

    return {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "FINAL_AUTHORIZATION_CONTRACT_SOURCE_AUTHORIZED_INSTALL_LOCKED"
        ),
        **source_blobs,
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC410_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "dormant_executor_workflow_template_path": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH
        ),
        "dormant_executor_workflow_template_blob_sha": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
        ),
        "dormant_executor_workflow_template_present": True,
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "failed_proof_run_id": 36613664506,
        "recovery_proof_run_id": 36616131587,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_decision_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_activation_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized": (
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_SOURCE_AUTHORIZED
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
            "WORKFLOW_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT"
        ),
    }


__all__ = [
    "ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_SOURCE_AUTHORIZED",
    "DEC410_RUNTIME_FREEZE_FINGERPRINT_SHA256",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "build_active_one_shot_historical_executor_workflow_install_final_authorization_contract",
    "validate_active_one_shot_historical_executor_workflow_install_final_authorization_contract_sources",
]
