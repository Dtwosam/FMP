from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_dispatch_runtime_freeze import (
    EXP062_HISTORICAL_DISPATCH_RUNTIME_FREEZE_DECISION,
    EXP062_HISTORICAL_DISPATCH_RUNTIME_FREEZE_VERSION,
)


EXP062_HISTORICAL_EXECUTOR_CONTRACT_DECISION = "DEC-324"
EXP062_HISTORICAL_EXECUTOR_CONTRACT_VERSION = (
    "fmp-exp062-historical-executor-contract-v1"
)

DEC323_RUNTIME_FREEZE_BLOB_SHA = (
    "44815c9ff23fcd022346558e8c043673154ca0b3"
)
DEC323_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "d412cc0fe115f7c10da6b0cfee092de718539ade041c8476659f6c30f8adc8c3"
)

ONE_SHOT_EXECUTOR_SOURCE_AUTHORIZED = True
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


def validate_historical_executor_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = root / "src/fmp/discovery/exp062_historical_dispatch_runtime_freeze.py"
    if not path.is_file():
        raise ValueError(f"missing DEC-324 source dependency: {path}")
    actual = _git_blob_sha(path)
    if actual != DEC323_RUNTIME_FREEZE_BLOB_SHA:
        raise ValueError(
            "DEC-324 DEC-323 runtime-freeze Git blob mismatch: "
            f"{actual} != {DEC323_RUNTIME_FREEZE_BLOB_SHA}"
        )
    return {"dec323_runtime_freeze_blob_sha": actual}


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    exact = {
        "decision": EXP062_HISTORICAL_DISPATCH_RUNTIME_FREEZE_DECISION,
        "version": EXP062_HISTORICAL_DISPATCH_RUNTIME_FREEZE_VERSION,
        "stage": (
            "EXP062_HISTORICAL_DISPATCH_PLAN_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "dispatch_plan_proof_head_sha": (
            "fee1a78168254e7e8fecc104859d1a231b727243"
        ),
        "dispatch_plan_proof_run_id": 36418793172,
        "dispatch_plan_proof_job_id": 108916232597,
        "dispatch_plan_proof_artifact_id": 10967344018,
        "dispatch_plan_proof_artifact_digest": (
            "sha256:ca0f1156fab234327bbcdd9c3150cb7904ed6def230f035019b2139c4c523adf"
        ),
        "dispatch_plan_raw_sha256": (
            "a6fa5f3a7f3f45df5d64efe1661a5b17887f88fded31e1cbb1620df5b18a95d1"
        ),
        "dispatch_plan_canonical_sha256": (
            "41ca6c710d8750851350c2108b42970501a5efa14481cff61e2a66877ee90f6d"
        ),
        "dec322_freeze_fingerprint_sha256": (
            "b7d3e5461511c8e14dd4402028ad24daefcf431cece3b59575588ba915db510e"
        ),
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_dispatch_source_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_executor_available": False,
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
        "next_gate": "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_CONTRACT",
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-324 runtime freeze {field} mismatch")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC323_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC323_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-324 DEC-323 runtime freeze fingerprint mismatch")


def build_historical_executor_contract(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
) -> dict[str, object]:
    source = validate_historical_executor_contract_sources(
        repository_root=repository_root,
    )
    _validate_runtime_freeze(runtime_freeze)

    return {
        "decision": EXP062_HISTORICAL_EXECUTOR_CONTRACT_DECISION,
        "version": EXP062_HISTORICAL_EXECUTOR_CONTRACT_VERSION,
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_AUTHORIZED_RUNTIME_LOCKED"
        ),
        **source,
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC323_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_executor_source_authorized": (
            ONE_SHOT_EXECUTOR_SOURCE_AUTHORIZED
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
        "next_gate": "READ_ONLY_CURRENT_MAIN_EXECUTOR_PREFLIGHT",
    }


__all__ = [
    "EXP062_HISTORICAL_EXECUTOR_CONTRACT_DECISION",
    "EXP062_HISTORICAL_EXECUTOR_CONTRACT_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "ONE_SHOT_EXECUTOR_SOURCE_AUTHORIZED",
    "build_historical_executor_contract",
    "validate_historical_executor_contract_sources",
]
