from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_one_shot_executor_workflow_preflight_proof_runtime_freeze import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION,
)


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_DECISION = "DEC-348"
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_VERSION = (
    "fmp-exp062-one-shot-historical-executor-workflow-install-contract-v1"
)

DEC347_RUNTIME_FREEZE_BLOB_SHA = "4781dae661a78d7b50e2070e87b8d7e34ea49f3c"
DEC347_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "b714ceec4a30fde0693db5c21eab2ce62d7a63c1c724c55321bc8cb13b423e03"
)

EXPECTED_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
)

ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED = True
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
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def validate_one_shot_historical_executor_workflow_install_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_one_shot_executor_workflow_preflight_proof_runtime_freeze.py"
    )
    if not path.is_file():
        raise ValueError(f"missing DEC-348 source dependency: {path}")
    actual = _git_blob_sha(path)
    if actual != DEC347_RUNTIME_FREEZE_BLOB_SHA:
        raise ValueError(
            "DEC-348 DEC-347 runtime-freeze Git blob mismatch: "
            f"{actual} != {DEC347_RUNTIME_FREEZE_BLOB_SHA}"
        )
    return {"dec347_runtime_freeze_blob_sha": actual}


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    exact = {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "workflow_preflight_proof_head_sha": (
            "c43a1701cadd57c25903d3b637f2af70b28d1065"
        ),
        "workflow_preflight_proof_run_id": 36455684780,
        "workflow_preflight_proof_job_id": 109041310360,
        "workflow_preflight_proof_artifact_id": 10984953455,
        "workflow_preflight_proof_artifact_digest": (
            "sha256:eec64c9bb1f6688dca010825e83e191c6a423d21bf6522396d7f650ec2db675f"
        ),
        "workflow_preflight_raw_sha256": (
            "56981ba62638129f39693239d22b76c65cb3a8e0b236741b3a80984137c2c0d7"
        ),
        "workflow_preflight_canonical_sha256": (
            "d6bf96a73b1377ad65887c6ba001c2c2d39812d58205e59e304c1c88e3ef22dc"
        ),
        "dec346_freeze_fingerprint_sha256": (
            "3ba4b6aba0cafab3989c1f20536ad36603786efdcef49964a31bc99b73a79988"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_historical_executor_source_authorized": True,
        "one_shot_historical_executor_workflow_source_authorized": True,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT"
        ),
    }
    for field, expected_value in exact.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-348 runtime freeze {field} mismatch")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC347_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC347_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-348 DEC-347 runtime freeze fingerprint mismatch")


def build_one_shot_historical_executor_workflow_install_contract(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
) -> dict[str, object]:
    source = validate_one_shot_historical_executor_workflow_install_contract_sources(
        repository_root=repository_root,
    )
    _validate_runtime_freeze(runtime_freeze)

    return {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "SOURCE_AUTHORIZED_RUNTIME_LOCKED"
        ),
        **source,
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC347_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "terminal_review_decision": "DEC-334",
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_historical_executor_source_authorized": True,
        "one_shot_historical_executor_workflow_source_authorized": True,
        "one_shot_historical_executor_workflow_install_source_authorized": (
            ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED
        ),
        "historical_executor_workflow_installed": (
            HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED
        ),
        "historical_executor_available": HISTORICAL_EXECUTOR_AVAILABLE,
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_execute_mode_available": HISTORICAL_EXECUTE_MODE_AVAILABLE,
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
            "READ_ONLY_CURRENT_MAIN_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_PREFLIGHT"
        ),
    }


__all__ = [
    "EXPECTED_EXECUTOR_WORKFLOW_PATH",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED",
    "build_one_shot_historical_executor_workflow_install_contract",
    "validate_one_shot_historical_executor_workflow_install_contract_sources",
]
