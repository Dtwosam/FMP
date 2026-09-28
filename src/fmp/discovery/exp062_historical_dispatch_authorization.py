from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_execution_runtime_freeze import (
    EXP062_HISTORICAL_EXECUTION_RUNTIME_FREEZE_DECISION,
    EXP062_HISTORICAL_EXECUTION_RUNTIME_FREEZE_VERSION,
)


EXP062_HISTORICAL_DISPATCH_AUTHORIZATION_DECISION = "DEC-318"
EXP062_HISTORICAL_DISPATCH_AUTHORIZATION_VERSION = (
    "fmp-exp062-historical-dispatch-authorization-v1"
)

DEC317_RUNTIME_FREEZE_BLOB_SHA = (
    "9626f6cd1c66a67d91dd3acf743e120ea8d2e9c0"
)
DEC317_RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "eeac1b77b7bd77b14880aeb192ea1df664c15b91e440e3938b8cba0a67b95619"
)

ONE_SHOT_DISPATCH_SOURCE_AUTHORIZED = True
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
HISTORICAL_EXECUTOR_AVAILABLE = False
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


def validate_historical_dispatch_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = root / "src/fmp/discovery/exp062_historical_execution_runtime_freeze.py"
    if not path.is_file():
        raise ValueError(f"missing DEC-318 source dependency: {path}")
    actual = _git_blob_sha(path)
    if actual != DEC317_RUNTIME_FREEZE_BLOB_SHA:
        raise ValueError(
            "DEC-318 DEC-317 runtime-freeze Git blob mismatch: "
            f"{actual} != {DEC317_RUNTIME_FREEZE_BLOB_SHA}"
        )
    return {"dec317_runtime_freeze_blob_sha": actual}


def _validate_runtime_freeze(value: Mapping[str, object]) -> None:
    exact = {
        "decision": EXP062_HISTORICAL_EXECUTION_RUNTIME_FREEZE_DECISION,
        "version": EXP062_HISTORICAL_EXECUTION_RUNTIME_FREEZE_VERSION,
        "stage": (
            "EXP062_HISTORICAL_EXECUTION_PLAN_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "plan_proof_head_sha": (
            "ea69e82c9f653facba8ed6589fe4243848187ad3"
        ),
        "plan_proof_run_id": 36414282818,
        "plan_proof_job_id": 108901556593,
        "plan_proof_artifact_id": 10966632240,
        "plan_proof_artifact_digest": (
            "sha256:9299ebfd344c0bd2a66ccd6e29339e035840c8b4204cbfc16bb6d3e938a53254"
        ),
        "plan_raw_sha256": (
            "594b5bd129a93ad7b07f69e00826251dd693f1bb388e6b4dff64eda0b34a7c72"
        ),
        "plan_canonical_sha256": (
            "152bbb90efe3941f1338c73cf24f91f10a877cda3ee5c46f08c4f556d653a12f"
        ),
        "dec316_freeze_fingerprint_sha256": (
            "7c7d99f4c89aac4e11d27536b9f8d2d39322672a9a0332f141d1d86f93b19be3"
        ),
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "historical_execution_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_DISPATCH_AUTHORIZATION_CONTRACT"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-318 runtime freeze {field} mismatch")

    unsigned = dict(value)
    fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC317_RUNTIME_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC317_RUNTIME_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-318 DEC-317 runtime freeze fingerprint mismatch")


def build_historical_dispatch_authorization_contract(
    *,
    repository_root: Path,
    runtime_freeze: Mapping[str, object],
) -> dict[str, object]:
    source = validate_historical_dispatch_authorization_sources(
        repository_root=repository_root,
    )
    _validate_runtime_freeze(runtime_freeze)

    return {
        "decision": EXP062_HISTORICAL_DISPATCH_AUTHORIZATION_DECISION,
        "version": EXP062_HISTORICAL_DISPATCH_AUTHORIZATION_VERSION,
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_DISPATCH_SOURCE_AUTHORIZED_RUNTIME_LOCKED"
        ),
        **source,
        "runtime_freeze_decision": runtime_freeze["decision"],
        "runtime_freeze_version": runtime_freeze["version"],
        "runtime_freeze_fingerprint_sha256": (
            DEC317_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_dispatch_source_authorized": (
            ONE_SHOT_DISPATCH_SOURCE_AUTHORIZED
        ),
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_executor_available": HISTORICAL_EXECUTOR_AVAILABLE,
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
            "READ_ONLY_CURRENT_MAIN_ONE_SHOT_DISPATCH_OPERATOR"
        ),
    }


__all__ = [
    "EXP062_HISTORICAL_DISPATCH_AUTHORIZATION_DECISION",
    "EXP062_HISTORICAL_DISPATCH_AUTHORIZATION_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "ONE_SHOT_DISPATCH_SOURCE_AUTHORIZED",
    "build_historical_dispatch_authorization_contract",
    "validate_historical_dispatch_authorization_sources",
]
