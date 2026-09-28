from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_dormant_one_shot_executor_source_proof_runtime_freeze import (
    EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_DECISION,
    EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_VERSION,
)


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_DECISION = (
    "DEC-360"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-workflow-install-contract-v1"
)

DEC359_RUNTIME_FREEZE_BLOB_SHA = "3d4b7912396fbf7d51b6de4b30138bcd75566387"
DEC359_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "f7e1a6d1946dd42a5f72fbd9c154d1efa448db5d4e38b7469cbf0d0485fde84f"
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

ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED = True
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


def validate_active_one_shot_historical_executor_workflow_install_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec359_runtime_freeze": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_dormant_one_shot_executor_source_proof_runtime_freeze.py",
            DEC359_RUNTIME_FREEZE_BLOB_SHA,
        ),
        "dormant_executor_workflow_template": (
            root / DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH,
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-360 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-360 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    exact = {
        "decision": (
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "dormant_source_proof_head_sha": (
            "67337de4b21efab0cbafb3c9237397f0a98d524e"
        ),
        "dormant_source_proof_run_id": 36473192632,
        "dormant_source_proof_job_id": 109100293950,
        "dormant_source_proof_artifact_id": 10991479562,
        "dormant_source_proof_artifact_digest": (
            "sha256:092e1daebf889560d27ebe57242772c3806322627dab03e64a2ff400d9b4b1d1"
        ),
        "dormant_source_raw_sha256": (
            "1dfae5078e400fc2dbf0b10ef6d4297dc4d3c0660386ebb8c46b63c6dbe69060"
        ),
        "dormant_source_canonical_sha256": (
            "4d6cf8999ecb5346a10ecb31cdc1b669736d4d466e6b31c503b3fbf1a5e633a7"
        ),
        "dec358_freeze_fingerprint_sha256": (
            "8ba4411b8c7468a1f0eecc0352490e00577452ce96a81710fca6457e779e9897"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "dormant_executor_workflow_template_blob_sha": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
        ),
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "dormant_executor_workflow_template_present": True,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
            "WORKFLOW_INSTALL_CONTRACT"
        ),
    }
    for field, expected_value in exact.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-360 runtime freeze {field} mismatch")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC359_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC359_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-360 DEC-359 runtime freeze fingerprint mismatch")


def build_active_one_shot_historical_executor_workflow_install_contract(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
) -> dict[str, object]:
    root = Path(repository_root)
    source_blobs = (
        validate_active_one_shot_historical_executor_workflow_install_contract_sources(
            repository_root=root,
        )
    )
    _validate_runtime_freeze(runtime_freeze)

    active_path = root / EXPECTED_EXECUTOR_WORKFLOW_PATH
    if active_path.exists():
        raise ValueError(
            "DEC-360 requires active executor workflow path to remain absent"
        )

    return {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "SOURCE_AUTHORIZED_ACTIVE_WORKFLOW_ABSENT"
        ),
        **source_blobs,
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC359_RUNTIME_FREEZE_FINGERPRINT_SHA256
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
        "active_one_shot_historical_executor_workflow_install_source_authorized": (
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED
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
            "WORKFLOW_INSTALL_PREFLIGHT"
        ),
    }


__all__ = [
    "ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED",
    "DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA",
    "DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH",
    "EXPECTED_EXECUTOR_WORKFLOW_PATH",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "build_active_one_shot_historical_executor_workflow_install_contract",
    "validate_active_one_shot_historical_executor_workflow_install_contract_sources",
]
