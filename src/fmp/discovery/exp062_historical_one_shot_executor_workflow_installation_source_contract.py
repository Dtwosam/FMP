from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_one_shot_executor_workflow_install_preflight_proof_runtime_freeze import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION,
)


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_CONTRACT_DECISION = (
    "DEC-354"
)
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_CONTRACT_VERSION = (
    "fmp-exp062-one-shot-historical-executor-workflow-installation-source-contract-v1"
)

DEC353_RUNTIME_FREEZE_BLOB_SHA = "2183798aa137e234849f92a0aee13e14a76876e2"
DEC353_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "aa2eafcf48f19f694ac9acac08b91174b2ca1282c2a2b6ea2a33cb16aa2d4385"
)

DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "phase8a-exp062-one-shot-historical-executor.yml.disabled"
)
EXPECTED_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
)

ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_AUTHORIZED = True
DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PRESENT = False
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


def validate_one_shot_historical_executor_workflow_installation_source_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_one_shot_executor_workflow_install_preflight_proof_runtime_freeze.py"
    )
    if not path.is_file():
        raise ValueError(f"missing DEC-354 source dependency: {path}")
    actual = _git_blob_sha(path)
    if actual != DEC353_RUNTIME_FREEZE_BLOB_SHA:
        raise ValueError(
            "DEC-354 DEC-353 runtime-freeze Git blob mismatch: "
            f"{actual} != {DEC353_RUNTIME_FREEZE_BLOB_SHA}"
        )
    return {"dec353_runtime_freeze_blob_sha": actual}


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    exact = {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "workflow_install_preflight_proof_head_sha": (
            "bef60cd8656f0db48293570c13f91e2e09fe5be8"
        ),
        "workflow_install_preflight_proof_run_id": 36461898040,
        "workflow_install_preflight_proof_job_id": 109062250103,
        "workflow_install_preflight_proof_artifact_id": 10987972547,
        "workflow_install_preflight_proof_artifact_digest": (
            "sha256:60a723a55502ee9b8145258c5482ce71b82b2331c572378536b14d78f6ef2f91"
        ),
        "workflow_install_preflight_raw_sha256": (
            "ee754581b87576c3c23228a2371b88b3b8a38fdcd9c20ebd2c222c18f7c65e0d"
        ),
        "workflow_install_preflight_canonical_sha256": (
            "5c1893ea24a627ea421f05564d6d0cc490215201c01162fbe0b6ab519a323c8b"
        ),
        "dec352_freeze_fingerprint_sha256": (
            "75fad6795f4046d83f5ae29f08475c969e29d3fe3af0e3448dde46292a959f4a"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "workflow_install_slot_verified_available": True,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_"
            "INSTALLATION_SOURCE_CONTRACT"
        ),
    }
    for field, expected_value in exact.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-354 runtime freeze {field} mismatch")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC353_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC353_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-354 DEC-353 runtime freeze fingerprint mismatch")


def build_one_shot_historical_executor_workflow_installation_source_contract(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
) -> dict[str, object]:
    source = (
        validate_one_shot_historical_executor_workflow_installation_source_contract_sources(
            repository_root=repository_root,
        )
    )
    _validate_runtime_freeze(runtime_freeze)

    return {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_CONTRACT_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_CONTRACT_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_"
            "SOURCE_AUTHORIZED_TEMPLATE_ABSENT_RUNTIME_LOCKED"
        ),
        **source,
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC353_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "terminal_review_decision": "DEC-334",
        "dormant_executor_workflow_template_path": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH
        ),
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "dormant_executor_workflow_template_present": False,
        "executor_workflow_path_exists": False,
        "workflow_install_slot_verified_available": True,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "one_shot_historical_executor_workflow_installation_source_authorized": (
            ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_AUTHORIZED
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
            "DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_TEMPLATE_SOURCE"
        ),
    }


__all__ = [
    "DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH",
    "EXPECTED_EXECUTOR_WORKFLOW_PATH",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_CONTRACT_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_CONTRACT_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_AUTHORIZED",
    "build_one_shot_historical_executor_workflow_installation_source_contract",
    "validate_one_shot_historical_executor_workflow_installation_source_contract_sources",
]
