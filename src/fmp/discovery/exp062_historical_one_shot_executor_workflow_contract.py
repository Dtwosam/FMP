from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_one_shot_executor_source_proof_runtime_freeze import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_DECISION,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_VERSION,
)


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_CONTRACT_DECISION = "DEC-342"
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_CONTRACT_VERSION = (
    "fmp-exp062-one-shot-historical-executor-workflow-contract-v1"
)

DEC341_RUNTIME_FREEZE_BLOB_SHA = "b99a2f453423734a92d79d8f8d1c2fa1fa20d45f"
DEC341_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "7375b8fa30a425d660e6a0c392eb6c0084d9f0bb65c7b141d5ef11a6459650da"
)

ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_SOURCE_AUTHORIZED = True
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


def validate_one_shot_historical_executor_workflow_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_one_shot_executor_source_proof_runtime_freeze.py"
    )
    if not path.is_file():
        raise ValueError(f"missing DEC-342 source dependency: {path}")
    actual = _git_blob_sha(path)
    if actual != DEC341_RUNTIME_FREEZE_BLOB_SHA:
        raise ValueError(
            "DEC-342 DEC-341 runtime-freeze Git blob mismatch: "
            f"{actual} != {DEC341_RUNTIME_FREEZE_BLOB_SHA}"
        )
    return {"dec341_runtime_freeze_blob_sha": actual}


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    exact = {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "source_proof_head_sha": (
            "e9dfbf034614b54598d31653da3868ed66aa90ba"
        ),
        "source_proof_run_id": 36442399041,
        "source_proof_job_id": 108995955292,
        "source_proof_artifact_id": 10979242048,
        "source_proof_artifact_digest": (
            "sha256:7dff775fc559cf9dbd754f45c24fbc814035b1602b59ca5eb9f82678af4e8b88"
        ),
        "source_contract_raw_sha256": (
            "484ad49fa3b3e925ae4a3576af840a8736c9b25ef439b619e8b60e8011f94d63"
        ),
        "source_contract_canonical_sha256": (
            "cb650b81c2549bfb5bfa62f6609bec9b39e4ed118f3e54c302a48a3a27a11616"
        ),
        "dec340_freeze_fingerprint_sha256": (
            "e340394fb987c68d9203a57c9cd363f255729b3424a9600ec03533ff421960a8"
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_CONTRACT"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-342 runtime freeze {field} mismatch")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC341_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC341_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-342 DEC-341 runtime freeze fingerprint mismatch")


def build_one_shot_historical_executor_workflow_contract(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
) -> dict[str, object]:
    source = validate_one_shot_historical_executor_workflow_contract_sources(
        repository_root=repository_root,
    )
    _validate_runtime_freeze(runtime_freeze)

    return {
        "decision": EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_CONTRACT_DECISION,
        "version": EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_CONTRACT_VERSION,
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_SOURCE_AUTHORIZED_"
            "RUNTIME_LOCKED"
        ),
        **source,
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC341_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "terminal_review_decision": "DEC-334",
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
        "one_shot_historical_executor_workflow_source_authorized": (
            ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_SOURCE_AUTHORIZED
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
            "READ_ONLY_CURRENT_MAIN_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT"
        ),
    }


__all__ = [
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_CONTRACT_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_CONTRACT_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_SOURCE_AUTHORIZED",
    "build_one_shot_historical_executor_workflow_contract",
    "validate_one_shot_historical_executor_workflow_contract_sources",
]
