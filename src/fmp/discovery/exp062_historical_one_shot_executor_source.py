from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_executor_activation_preflight import (
    EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_DECISION,
    EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_VERSION,
    historical_executor_activation_dispatch_command,
    shell_join,
    validate_historical_executor_activation_preflight,
)
from .exp062_historical_executor_activation_preflight_runtime_freeze import (
    EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_RUNTIME_FREEZE_DECISION,
    EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_RUNTIME_FREEZE_VERSION,
)
from .exp062_historical_terminal_review_contract import (
    EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION,
    EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION,
)


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_DECISION = "DEC-337"
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_VERSION = (
    "fmp-exp062-one-shot-historical-executor-source-v1"
)

DEC336_RUNTIME_FREEZE_BLOB_SHA = (
    "9673e115eeb373c4881d36a8b5d91a2801cd8ad1"
)
DEC336_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "147ab77116979afa8d0d07c3c748fb80e02865a382317824320f6af534bfc374"
)

ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_AUTHORIZED = True
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


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_one_shot_historical_executor_source_dependencies(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_executor_activation_preflight_runtime_freeze.py"
    )
    if not path.is_file():
        raise ValueError(f"missing DEC-337 source dependency: {path}")
    actual = _git_blob_sha(path)
    if actual != DEC336_RUNTIME_FREEZE_BLOB_SHA:
        raise ValueError(
            "DEC-337 DEC-336 runtime-freeze Git blob mismatch: "
            f"{actual} != {DEC336_RUNTIME_FREEZE_BLOB_SHA}"
        )
    return {"dec336_runtime_freeze_blob_sha": actual}


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    exact = {
        "decision": (
            EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "activation_preflight_proof_head_sha": (
            "12d11320ae302902df0a0deb7343408922deee83"
        ),
        "activation_preflight_proof_run_id": 36431469794,
        "activation_preflight_proof_job_id": 108958446980,
        "activation_preflight_proof_artifact_id": 10973597441,
        "activation_preflight_proof_artifact_digest": (
            "sha256:ee6e7ac2e8c18e1f8d276bba14ca942e20615143316ac185f4b814333804c2d5"
        ),
        "activation_preflight_raw_sha256": (
            "775010a0c3d4afe11191adb53d8ad54e7cf0d5de85b1a0b5adcb28c470e9a4a5"
        ),
        "activation_preflight_canonical_sha256": (
            "98b9180ae3b438b3c372ba34cbab9473d7f38ba5c1eb1add2dee988df4e09ad8"
        ),
        "dec334_terminal_review_decision": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION
        ),
        "dec334_terminal_review_version": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION
        ),
        "dec335_freeze_fingerprint_sha256": (
            "567320a598f245a8e7521281ddde3a1acaa0e3f294aebe12554688d2258f020b"
        ),
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_executor_activation_source_authorized": True,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_BEFORE_DISPATCH"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-337 runtime freeze {field} mismatch")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC336_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC336_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-337 DEC-336 runtime freeze fingerprint mismatch")


def _validate_fresh_activation_preflight(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> None:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    validated = validate_historical_executor_activation_preflight(value)
    exact = {
        "decision": EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_DECISION,
        "version": EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_VERSION,
        "expected_head_sha": expected_head_sha,
        "stage": (
            "EXP062_ONE_SHOT_EXECUTOR_ACTIVATION_PREFLIGHT_SLOT_AVAILABLE"
        ),
        "proof_run_count": 1,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command": shell_join(
            historical_executor_activation_dispatch_command()
        ),
        "one_shot_executor_activation_source_authorized": True,
        "historical_executor_available": False,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
    }
    for field, expected in exact.items():
        if validated.get(field) != expected:
            raise ValueError(f"DEC-337 fresh preflight {field} mismatch")

    for field in (
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
    ):
        if validated.get(field) is not False:
            raise ValueError(f"DEC-337 fresh preflight {field} must remain false")


def build_one_shot_historical_executor_source_contract(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
    fresh_activation_preflight: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_one_shot_historical_executor_source_dependencies(
        repository_root=repository_root,
    )
    _validate_runtime_freeze(runtime_freeze)
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    _validate_fresh_activation_preflight(
        fresh_activation_preflight,
        expected_head_sha=expected_head_sha,
    )

    return {
        "decision": EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_DECISION,
        "version": EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_VERSION,
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_AUTHORIZED_"
            "RUNTIME_DISPATCH_LOCKED"
        ),
        **source,
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC336_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "terminal_review_decision": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION
        ),
        "terminal_review_version": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION
        ),
        "expected_head_sha": expected_head_sha,
        "historical_gate_proof_run_id": fresh_activation_preflight[
            "proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": shell_join(
            historical_executor_activation_dispatch_command()
        ),
        "one_shot_historical_executor_source_authorized": (
            ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_AUTHORIZED
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
            "REPOSITORY_HOSTED_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_SOURCE_PROOF"
        ),
    }


__all__ = [
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_VERSION",
    "ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_AUTHORIZED",
    "build_one_shot_historical_executor_source_contract",
    "validate_one_shot_historical_executor_source_dependencies",
]
