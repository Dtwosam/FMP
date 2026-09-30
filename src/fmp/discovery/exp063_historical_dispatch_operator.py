from __future__ import annotations

import hashlib
import shlex
from pathlib import Path
from typing import Mapping, Sequence

from .exp063_historical_execution_authorization import (
    HISTORICAL_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_AUTHORIZED,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
)
from .exp063_historical_run_authorization import (
    classify_historical_run_inventory,
)


EXP063_HISTORICAL_DISPATCH_OPERATOR_DECISION = "DEC-449"
EXP063_HISTORICAL_DISPATCH_OPERATOR_VERSION = (
    "fmp-exp063-read-only-dispatch-operator-v1"
)

DEC449_EXECUTION_AUTHORIZATION_BLOB_SHA = (
    "fd87ab32eafa43e2cffb305680a1747314f4f3e5"
)
DEC448_RUN_AUTHORIZATION_BLOB_SHA = (
    "f6070b1ecc8951338767b24dac1f0ff9ec7a24ae"
)

ONE_SHOT_DISPATCH_SOURCE_AUTHORIZED = True
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
    payload = Path(path).read_bytes()
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


def historical_dispatch_command() -> tuple[str, ...]:
    return (
        "gh",
        "workflow",
        "run",
        "phase8a-exp063-persistence.yml",
        "--ref",
        "main",
    )


def shell_join(parts: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def validate_historical_dispatch_operator_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec449_execution_authorization": (
            root
            / "src/fmp/discovery/exp063_historical_execution_authorization.py",
            DEC449_EXECUTION_AUTHORIZATION_BLOB_SHA,
        ),
        "dec448_run_authorization": (
            root / "src/fmp/discovery/exp063_historical_run_authorization.py",
            DEC448_RUN_AUTHORIZATION_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-449 dispatch dependency: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(
                f"DEC-449 {label} Git blob mismatch: {sha} != {expected_sha}"
            )
        actual[label] = sha

    if HISTORICAL_RESULT_DISPATCH_AUTHORIZED is not True:
        raise ValueError("DEC-449 requires one-shot dispatch authorization")
    if HISTORICAL_EXECUTION_AUTHORIZED is not True:
        raise ValueError("DEC-449 requires runtime execution authorization")
    if HISTORICAL_RESULT_AUTHORIZED is not True:
        raise ValueError("DEC-449 requires historical result authorization")

    return actual


def build_historical_dispatch_plan(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    sources = validate_historical_dispatch_operator_sources(
        repository_root=repository_root,
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-449 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-449 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-449 main head mismatch")

    inventory = classify_historical_run_inventory(workflow_runs)
    if inventory["stage"] == "EXP063_HISTORICAL_RESULT_SLOT_AVAILABLE":
        if inventory["historical_result_attempt_count"] != 0:
            raise ValueError("DEC-449 available slot attempt count mismatch")
        if inventory["historical_result_slot_consumed"] is not False:
            raise ValueError("DEC-449 available slot marked consumed")
        planned = shell_join(historical_dispatch_command())
        stage = "EXP063_ONE_SHOT_DISPATCH_READY"
    elif (
        inventory["stage"]
        == "EXP063_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED"
    ):
        if inventory["historical_result_attempt_count"] != 1:
            raise ValueError("DEC-449 consumed slot attempt count mismatch")
        if inventory["historical_result_slot_consumed"] is not True:
            raise ValueError("DEC-449 present run must consume slot")
        planned = None
        stage = "EXP063_ONE_SHOT_SLOT_CONSUMED_REVIEW_REQUIRED"
    else:
        raise ValueError("DEC-449 inventory stage mismatch")

    return {
        "decision": EXP063_HISTORICAL_DISPATCH_OPERATOR_DECISION,
        "operator_version": EXP063_HISTORICAL_DISPATCH_OPERATOR_VERSION,
        **sources,
        "expected_head_sha": expected_head_sha,
        "stage": stage,
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
        "expected_target_run_number": 1,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command": planned,
        "one_shot_dispatch_source_authorized": True,
        "historical_result_dispatch_authorized": True,
        "historical_execution_authorized": True,
        "historical_result_authorized": True,
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
    }


def validate_historical_dispatch_plan(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    expected = {
        "decision": EXP063_HISTORICAL_DISPATCH_OPERATOR_DECISION,
        "operator_version": EXP063_HISTORICAL_DISPATCH_OPERATOR_VERSION,
        "expected_target_run_number": 1,
        "expected_target_run_attempt": 1,
        "one_shot_dispatch_source_authorized": True,
        "historical_result_dispatch_authorized": True,
        "historical_execution_authorized": True,
        "historical_result_authorized": True,
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
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-449 dispatch plan {field} mismatch")

    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    stage = value.get("stage")
    if stage == "EXP063_ONE_SHOT_DISPATCH_READY":
        if value.get("historical_result_attempt_count") != 0:
            raise ValueError("DEC-449 ready attempt count mismatch")
        if value.get("historical_result_slot_consumed") is not False:
            raise ValueError("DEC-449 ready slot marked consumed")
        if value.get("historical_result_run_id") is not None:
            raise ValueError("DEC-449 ready run id must be null")
        if value.get("planned_dispatch_command") != shell_join(
            historical_dispatch_command()
        ):
            raise ValueError("DEC-449 planned dispatch command mismatch")
    elif stage == "EXP063_ONE_SHOT_SLOT_CONSUMED_REVIEW_REQUIRED":
        if value.get("historical_result_attempt_count") != 1:
            raise ValueError("DEC-449 consumed attempt count mismatch")
        if value.get("historical_result_slot_consumed") is not True:
            raise ValueError("DEC-449 consumed slot must be true")
        run_id = value.get("historical_result_run_id")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise ValueError("DEC-449 consumed run id invalid")
        if value.get("planned_dispatch_command") is not None:
            raise ValueError("DEC-449 cannot plan a second dispatch")
    else:
        raise ValueError("DEC-449 dispatch plan stage mismatch")
    return value


__all__ = [
    "EXP063_HISTORICAL_DISPATCH_OPERATOR_DECISION",
    "EXP063_HISTORICAL_DISPATCH_OPERATOR_VERSION",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "build_historical_dispatch_plan",
    "historical_dispatch_command",
    "shell_join",
    "validate_historical_dispatch_operator_sources",
    "validate_historical_dispatch_plan",
]
