from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_active_one_shot_executor_workflow_install_final_authorization_preflight_proof_runtime_freeze import (
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION,
)


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_DECISION = (
    "DEC-417"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-workflow-install-action-contract-v1"
)

DEC416_RUNTIME_FREEZE_BLOB_SHA = "1a4accb526aa5e0657ea9ad953fe2cefd564d8be"
DEC416_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "3f90062e42cc36c61286b31fcd625a7e511140819c19f268e283be1807e2f0c7"
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

ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_SOURCE_AUTHORIZED = True
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

_REVIEW_SOURCE_BLOBS = {
    "dec413_workflow": "dace2b0752937b2d15349f5564b88ed9aea82bf1",
    "dec412_preflight": "89c6a606703ce72916451e0168e1b58bb765baaa",
    "dec412_preflight_cli": "6ab0b9bbecec471cfabc67b50906b2213626296b",
    "dec411_final_authorization_contract": (
        "30493981eb2e5663e1fe620026c2c0af0cc03dd9"
    ),
    "dormant_executor_workflow_template": (
        DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
    ),
    "active_discovery_workflow": (
        "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
    ),
}


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


def validate_active_one_shot_historical_executor_workflow_install_action_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    runtime_path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_active_one_shot_executor_workflow_install_final_authorization_preflight_proof_runtime_freeze.py"
    )
    template_path = root / DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH

    if not runtime_path.is_file():
        raise ValueError(f"missing DEC-417 source dependency: {runtime_path}")
    runtime_sha = _git_blob_sha(runtime_path)
    if runtime_sha != DEC416_RUNTIME_FREEZE_BLOB_SHA:
        raise ValueError(
            "DEC-417 DEC-416 runtime-freeze Git blob mismatch: "
            f"{runtime_sha} != {DEC416_RUNTIME_FREEZE_BLOB_SHA}"
        )

    if not template_path.is_file():
        raise ValueError("DEC-417 requires dormant executor template present")
    template_sha = _git_blob_sha(template_path)
    if template_sha != DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-417 dormant executor template Git blob mismatch")

    return {
        "dec416_runtime_freeze": runtime_sha,
        "dormant_executor_workflow_template": template_sha,
    }


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    exact = {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "FINAL_AUTHORIZATION_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "active_install_final_authorization_preflight_proof_head_sha": (
            "8c7598348ade4ed8ea23458eef958add378c3e6d"
        ),
        "active_install_final_authorization_preflight_proof_run_id": 36622849087,
        "active_install_final_authorization_preflight_proof_run_number": 1,
        "active_install_final_authorization_preflight_proof_run_attempt": 1,
        "active_install_final_authorization_preflight_proof_run_conclusion": "success",
        "active_install_final_authorization_preflight_proof_job_id": 109592333745,
        "active_install_final_authorization_preflight_proof_artifact_id": 11058592607,
        "active_install_final_authorization_preflight_proof_artifact_name": (
            "exp062-dec413-active-one-shot-historical-executor-workflow-"
            "install-final-authorization-preflight-"
            "8c7598348ade4ed8ea23458eef958add378c3e6d"
        ),
        "active_install_final_authorization_preflight_proof_artifact_digest": (
            "sha256:8303140ebc7a5e37922080051ab634bc7a6c9f13940d52f3802b1017fd658c7a"
        ),
        "active_install_final_authorization_preflight_proof_artifact_zip_sha256": (
            "8303140ebc7a5e37922080051ab634bc7a6c9f13940d52f3802b1017fd658c7a"
        ),
        "active_install_final_authorization_preflight_raw_sha256": (
            "c265d3b6f1d9cc60946438d8fd7bd6d96ad4c976133293558ce0df548a09f730"
        ),
        "active_install_final_authorization_preflight_canonical_sha256": (
            "cca954fa188bf34ed308668563de0fa58226e50e242e65b0b33fac581dc5290c"
        ),
        "dec414_review_decision": "DEC-414",
        "dec414_review_version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
            "final-authorization-preflight-proof-review-v1"
        ),
        "dec415_freeze_decision": "DEC-415",
        "dec415_freeze_version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
            "final-authorization-preflight-proof-freeze-v1"
        ),
        "dec415_freeze_fingerprint_sha256": (
            "4a71a6b29ccea4d5415ce64ca84fc0c43988a2daf98cbe912f4654868b907ffa"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "dec334_terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "dec414_reviewer_blob_sha": (
            "331ebd4e6871bbf3dc81df3c76b40b5831048736"
        ),
        "dec415_freeze_builder_blob_sha": (
            "1c5e61ae1602e249c3888e8fa58532cb81fef1aa"
        ),
        "dec334_terminal_review_contract_blob_sha": (
            "fda2a45f74b101303467cf7b8527bec1bfc5e168"
        ),
        "review_source_blobs": _REVIEW_SOURCE_BLOBS,
        "dormant_executor_workflow_template_blob_sha": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
        ),
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "historical_gate_proof_run_id": 36358289723,
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
        "active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "next_gate": (
            "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_ACTION_CONTRACT_BEFORE_INSTALL"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-417 runtime freeze {field} mismatch")

    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-417 runtime freeze {field} must remain false")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC416_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC416_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-417 DEC-416 runtime freeze fingerprint mismatch")


def build_active_one_shot_historical_executor_workflow_install_action_contract(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
) -> dict[str, object]:
    root = Path(repository_root)
    source_blobs = (
        validate_active_one_shot_historical_executor_workflow_install_action_contract_sources(
            repository_root=root,
        )
    )
    _validate_runtime_freeze(runtime_freeze)

    if (root / EXPECTED_EXECUTOR_WORKFLOW_PATH).exists():
        raise ValueError(
            "DEC-417 requires active executor workflow path to remain absent"
        )

    return {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "ACTION_CONTRACT_SOURCE_AUTHORIZED_INSTALL_LOCKED"
        ),
        **source_blobs,
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC416_RUNTIME_FREEZE_FINGERPRINT_SHA256
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
        "active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_action_contract_source_authorized": (
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_SOURCE_AUTHORIZED
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
            "WORKFLOW_INSTALL_ACTION_PREFLIGHT"
        ),
    }


__all__ = [
    "ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_SOURCE_AUTHORIZED",
    "DEC416_RUNTIME_FREEZE_FINGERPRINT_SHA256",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "build_active_one_shot_historical_executor_workflow_install_action_contract",
    "validate_active_one_shot_historical_executor_workflow_install_action_contract_sources",
]
