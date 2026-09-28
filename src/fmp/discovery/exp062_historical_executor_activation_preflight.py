from __future__ import annotations

import hashlib
import shlex
from pathlib import Path
from typing import Mapping, Sequence

from .exp062_historical_executor_activation_contract import (
    EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_DECISION,
    EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_VERSION,
    HISTORICAL_EXECUTOR_AVAILABLE as CONTRACT_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTE_MODE_AVAILABLE as CONTRACT_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED as CONTRACT_DISPATCH_AUTHORIZED,
    ONE_SHOT_EXECUTOR_ACTIVATION_SOURCE_AUTHORIZED,
)
from .exp062_historical_run_authorization import (
    classify_historical_run_inventory,
)


EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_DECISION = "DEC-331"
EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_VERSION = (
    "fmp-exp062-historical-executor-activation-preflight-v1"
)

DEC330_ACTIVATION_CONTRACT_BLOB_SHA = (
    "35edfdfed85e52ebd723f2637060f4f102e7920b"
)

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


def historical_executor_activation_dispatch_command() -> tuple[str, ...]:
    return (
        "gh",
        "workflow",
        "run",
        "phase8a-exp062-discovery.yml",
        "--ref",
        "main",
    )


def shell_join(parts: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def validate_historical_executor_activation_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = (
        root
        / "src/fmp/discovery/exp062_historical_executor_activation_contract.py"
    )
    if not path.is_file():
        raise ValueError(f"missing DEC-331 source dependency: {path}")
    actual = _git_blob_sha(path)
    if actual != DEC330_ACTIVATION_CONTRACT_BLOB_SHA:
        raise ValueError(
            "DEC-331 DEC-330 activation-contract Git blob mismatch: "
            f"{actual} != {DEC330_ACTIVATION_CONTRACT_BLOB_SHA}"
        )
    if ONE_SHOT_EXECUTOR_ACTIVATION_SOURCE_AUTHORIZED is not True:
        raise ValueError("DEC-331 requires activation source authorization")
    if CONTRACT_EXECUTOR_AVAILABLE is not False:
        raise ValueError("DEC-331 requires executor availability false")
    if CONTRACT_DISPATCH_AUTHORIZED is not False:
        raise ValueError("DEC-331 requires dispatch authorization false")
    if CONTRACT_EXECUTE_MODE_AVAILABLE is not False:
        raise ValueError("DEC-331 requires execute mode false")
    return {"dec330_activation_contract_blob_sha": actual}


def build_historical_executor_activation_preflight(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_historical_executor_activation_preflight_sources(
        repository_root=repository_root,
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-331 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-331 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-331 main head mismatch")

    inventory = classify_historical_run_inventory(workflow_runs)
    stage = inventory["stage"]

    if stage == "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE":
        if inventory["historical_result_attempt_count"] != 0:
            raise ValueError("DEC-331 empty slot attempt count mismatch")
        if inventory["historical_result_slot_consumed"] is not False:
            raise ValueError("DEC-331 empty slot marked consumed")
        planned = shell_join(historical_executor_activation_dispatch_command())
        preflight_stage = (
            "EXP062_ONE_SHOT_EXECUTOR_ACTIVATION_PREFLIGHT_SLOT_AVAILABLE"
        )
    elif stage == "EXP062_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED":
        if inventory["historical_result_attempt_count"] != 1:
            raise ValueError("DEC-331 consumed slot attempt count mismatch")
        if inventory["historical_result_slot_consumed"] is not True:
            raise ValueError("DEC-331 present run must consume slot")
        planned = None
        preflight_stage = (
            "EXP062_ONE_SHOT_EXECUTOR_ACTIVATION_PREFLIGHT_SLOT_CONSUMED_REVIEW_REQUIRED"
        )
    else:
        raise ValueError("DEC-331 inventory stage mismatch")

    return {
        "decision": EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_DECISION,
        "version": EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_VERSION,
        "activation_contract_decision": (
            EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_DECISION
        ),
        "activation_contract_version": (
            EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_VERSION
        ),
        **source,
        "expected_head_sha": expected_head_sha,
        "stage": preflight_stage,
        "proof_run_id": inventory["proof_run_id"],
        "proof_run_count": inventory["proof_run_count"],
        "historical_result_attempt_count": inventory[
            "historical_result_attempt_count"
        ],
        "historical_result_run_id": inventory["historical_result_run_id"],
        "historical_result_run_status": inventory[
            "historical_result_run_status"
        ],
        "historical_result_run_conclusion": inventory[
            "historical_result_run_conclusion"
        ],
        "historical_result_slot_consumed": inventory[
            "historical_result_slot_consumed"
        ],
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command": planned,
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
            "REPOSITORY_HOSTED_READ_ONLY_EXECUTOR_ACTIVATION_PREFLIGHT_PROOF"
        ),
    }


def validate_historical_executor_activation_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    expected = {
        "decision": EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_DECISION,
        "version": EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_VERSION,
        "activation_contract_decision": (
            EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_DECISION
        ),
        "activation_contract_version": (
            EXP062_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT_VERSION
        ),
        "proof_run_count": 1,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
            "REPOSITORY_HOSTED_READ_ONLY_EXECUTOR_ACTIVATION_PREFLIGHT_PROOF"
        ),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-331 {field} mismatch")

    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    stage = value.get("stage")
    if stage == "EXP062_ONE_SHOT_EXECUTOR_ACTIVATION_PREFLIGHT_SLOT_AVAILABLE":
        if value.get("historical_result_attempt_count") != 0:
            raise ValueError("DEC-331 available-slot attempt count mismatch")
        if value.get("historical_result_slot_consumed") is not False:
            raise ValueError("DEC-331 available slot marked consumed")
        if value.get("historical_result_run_id") is not None:
            raise ValueError("DEC-331 available slot run id must be null")
        if value.get("planned_dispatch_command") != shell_join(
            historical_executor_activation_dispatch_command()
        ):
            raise ValueError("DEC-331 planned dispatch command mismatch")
    elif stage == (
        "EXP062_ONE_SHOT_EXECUTOR_ACTIVATION_PREFLIGHT_SLOT_CONSUMED_REVIEW_REQUIRED"
    ):
        if value.get("historical_result_attempt_count") != 1:
            raise ValueError("DEC-331 consumed-slot attempt count mismatch")
        if value.get("historical_result_slot_consumed") is not True:
            raise ValueError("DEC-331 consumed slot must be true")
        run_id = value.get("historical_result_run_id")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise ValueError("DEC-331 consumed-slot run id invalid")
        if value.get("planned_dispatch_command") is not None:
            raise ValueError("DEC-331 cannot plan a second dispatch")
    else:
        raise ValueError("DEC-331 stage mismatch")
    return value


__all__ = [
    "EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_DECISION",
    "EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_VERSION",
    "build_historical_executor_activation_preflight",
    "historical_executor_activation_dispatch_command",
    "validate_historical_executor_activation_preflight",
    "validate_historical_executor_activation_preflight_sources",
]
