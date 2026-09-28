from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_executor_preflight_runtime_freeze import (
    EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_FREEZE_DECISION,
    EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_FREEZE_VERSION,
)


EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_DECISION = "DEC-330"
EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_VERSION = (
    "fmp-exp062-historical-executor-activation-contract-v1"
)

DEC329_RUNTIME_FREEZE_BLOB_SHA = (
    "f9f727ae23b88fe52ca9c41739f04ab26bec0b4e"
)
DEC329_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "5c4e081fca4848cf18f8ed03c68e5d7854723e92368eded03fb5e9b54756ab61"
)

ONE_SHOT_EXECUTOR_ACTIVATION_SOURCE_AUTHORIZED = True
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


def validate_historical_executor_activation_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = (
        root
        / "src/fmp/discovery/exp062_historical_executor_preflight_runtime_freeze.py"
    )
    if not path.is_file():
        raise ValueError(f"missing DEC-330 source dependency: {path}")
    actual = _git_blob_sha(path)
    if actual != DEC329_RUNTIME_FREEZE_BLOB_SHA:
        raise ValueError(
            "DEC-330 DEC-329 runtime-freeze Git blob mismatch: "
            f"{actual} != {DEC329_RUNTIME_FREEZE_BLOB_SHA}"
        )
    return {"dec329_runtime_freeze_blob_sha": actual}


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    exact = {
        "decision": (
            EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "preflight_proof_head_sha": (
            "a811aacaae82e15b18267b6e4ba659054abb0341"
        ),
        "preflight_proof_run_id": 36422936991,
        "preflight_proof_job_id": 108929843306,
        "preflight_proof_artifact_id": 10970303347,
        "preflight_proof_artifact_digest": (
            "sha256:fe116a7fff7ffdec27e787d3cd7981ac67772276efb12a5b434b04ee3855c74c"
        ),
        "preflight_raw_sha256": (
            "5dfa7800a8dcbe4537910690a0ba70b3c93467c685d7c5c99898d0b6d111f9d8"
        ),
        "preflight_canonical_sha256": (
            "9970dcbf44241a3b9ffc6aab01d8a3bab6749813f88d0771dee101ea640aec3d"
        ),
        "dec328_freeze_fingerprint_sha256": (
            "2e295d03066fcfa4dcea300c3f263bcf6a67cb96d6b356410821af493b2d5675"
        ),
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_executor_source_authorized": True,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-330 runtime freeze {field} mismatch")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC329_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC329_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-330 DEC-329 runtime freeze fingerprint mismatch")


def build_historical_executor_activation_contract(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
) -> dict[str, object]:
    source = validate_historical_executor_activation_contract_sources(
        repository_root=repository_root,
    )
    _validate_runtime_freeze(runtime_freeze)

    return {
        "decision": EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_DECISION,
        "version": EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_VERSION,
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_ACTIVATION_SOURCE_AUTHORIZED_RUNTIME_LOCKED"
        ),
        **source,
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC329_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_executor_activation_source_authorized": (
            ONE_SHOT_EXECUTOR_ACTIVATION_SOURCE_AUTHORIZED
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
        "next_gate": "READ_ONLY_CURRENT_MAIN_EXECUTOR_ACTIVATION_PREFLIGHT",
    }


__all__ = [
    "EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_DECISION",
    "EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "ONE_SHOT_EXECUTOR_ACTIVATION_SOURCE_AUTHORIZED",
    "build_historical_executor_activation_contract",
    "validate_historical_executor_activation_contract_sources",
]
