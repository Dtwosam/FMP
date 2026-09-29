from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_MUTATION_AUTHORIZATION_DECISION = (
    "DEC-423"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_MUTATION_AUTHORIZATION_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-workflow-install-mutation-authorization-v1"
)

DEC422_RUNTIME_FREEZE_BLOB_SHA = "65108857f15b6ab084bbb5f8a0358b7bbd4aaa59"
DEC422_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "cce3b8900f630ddf0e651af10ceba39311f1e00485f6bca99af28252195aae0f"
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

EXPLICIT_REPOSITORY_MUTATION_AUTHORIZED = True
HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED = True
HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED = False
HISTORICAL_EXECUTOR_AVAILABLE = False
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
HISTORICAL_EXECUTE_MODE_AVAILABLE = False

_FALSE_AUTHORITY_FIELDS = (
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

_SOURCE_GATES = (
    "active_one_shot_historical_executor_workflow_install_authorization_source_authorized",
    "active_one_shot_historical_executor_workflow_install_decision_source_authorized",
    "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized",
    "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized",
    "active_one_shot_historical_executor_workflow_install_activation_source_authorized",
    "active_one_shot_historical_executor_workflow_install_source_authorized",
    "active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized",
    "active_one_shot_historical_executor_workflow_install_action_contract_source_authorized",
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


def validate_active_one_shot_historical_executor_workflow_install_mutation_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    runtime_path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_active_one_shot_executor_workflow_install_action_preflight_proof_runtime_freeze.py"
    )
    template_path = root / DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH

    if not runtime_path.is_file():
        raise ValueError(f"missing DEC-423 source dependency: {runtime_path}")
    runtime_sha = _git_blob_sha(runtime_path)
    if runtime_sha != DEC422_RUNTIME_FREEZE_BLOB_SHA:
        raise ValueError("DEC-423 DEC-422 runtime-freeze Git blob mismatch")

    if not template_path.is_file():
        raise ValueError("DEC-423 requires dormant executor template present")
    template_sha = _git_blob_sha(template_path)
    if template_sha != DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-423 dormant executor template Git blob mismatch")

    return {
        "dec422_runtime_freeze": runtime_sha,
        "dormant_executor_workflow_template": template_sha,
    }


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    if value.get("decision") != "DEC-422":
        raise ValueError("DEC-423 runtime freeze decision mismatch")
    if value.get("version") != (
        "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
        "action-preflight-proof-runtime-freeze-v1"
    ):
        raise ValueError("DEC-423 runtime freeze version mismatch")
    if value.get("runtime_freeze_fingerprint_sha256") != (
        DEC422_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-423 runtime freeze fingerprint mismatch")
    if value.get("expected_executor_workflow_path") != EXPECTED_EXECUTOR_WORKFLOW_PATH:
        raise ValueError("DEC-423 expected executor workflow path mismatch")
    if value.get("executor_workflow_path_exists") is not False:
        raise ValueError("DEC-423 runtime freeze requires active workflow absent")
    if value.get("historical_result_attempt_count") != 0:
        raise ValueError("DEC-423 historical-result attempt count mismatch")
    if value.get("historical_result_slot_consumed") is not False:
        raise ValueError("DEC-423 historical-result slot must remain unused")
    if value.get("historical_result_slot_verified_available") is not True:
        raise ValueError("DEC-423 historical-result slot must be available")
    if value.get("expected_target_run_number") != 2:
        raise ValueError("DEC-423 expected target run number mismatch")
    if value.get("expected_target_run_attempt") != 1:
        raise ValueError("DEC-423 expected target run attempt mismatch")
    for field in _SOURCE_GATES:
        if value.get(field) is not True:
            raise ValueError(f"DEC-423 runtime freeze {field} mismatch")
    if value.get("historical_executor_workflow_install_authorized") is not False:
        raise ValueError("DEC-423 predecessor install authority must remain false")
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-423 runtime freeze {field} must remain false")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC422_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC422_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-423 runtime freeze fingerprint mismatch")


def build_active_one_shot_historical_executor_workflow_install_mutation_authorization(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
) -> dict[str, object]:
    root = Path(repository_root)
    source_blobs = (
        validate_active_one_shot_historical_executor_workflow_install_mutation_authorization_sources(
            repository_root=root,
        )
    )
    _validate_runtime_freeze(runtime_freeze)

    active_path = root / EXPECTED_EXECUTOR_WORKFLOW_PATH
    if active_path.exists():
        raise ValueError(
            "DEC-423 authorization must be created before active workflow installation"
        )

    return {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_MUTATION_AUTHORIZATION_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_MUTATION_AUTHORIZATION_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "REPOSITORY_MUTATION_AUTHORIZED_ACTIVE_WORKFLOW_ABSENT"
        ),
        **source_blobs,
        "authorization_basis": "explicit_operator_authorization",
        "explicit_repository_mutation_authorized": (
            EXPLICIT_REPOSITORY_MUTATION_AUTHORIZED
        ),
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC422_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "dormant_executor_workflow_template_path": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH
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
        **{field: True for field in _SOURCE_GATES},
        "historical_executor_workflow_install_authorized": (
            HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED
        ),
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
        "next_gate": "ACTIVE_WORKFLOW_INSTALL_REPOSITORY_MUTATION",
    }


__all__ = [
    "DEC422_RUNTIME_FREEZE_FINGERPRINT_SHA256",
    "EXPLICIT_REPOSITORY_MUTATION_AUTHORIZED",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_MUTATION_AUTHORIZATION_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_MUTATION_AUTHORIZATION_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "build_active_one_shot_historical_executor_workflow_install_mutation_authorization",
    "validate_active_one_shot_historical_executor_workflow_install_mutation_authorization_sources",
]
