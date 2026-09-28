from __future__ import annotations

import shlex
from typing import Mapping, Sequence

from .exp062_historical_run_authorization import (
    EXP062_HISTORICAL_RUN_AUTHORIZATION_DECISION,
    EXP062_HISTORICAL_RUN_AUTHORIZATION_VERSION,
    HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED,
    classify_historical_run_inventory,
)


EXP062_HISTORICAL_OPERATOR_DECISION = "DEC-308"
EXP062_HISTORICAL_OPERATOR_VERSION = "fmp-exp062-historical-operator-v1"

HISTORICAL_EXECUTE_MODE_AVAILABLE = False
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
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
        "phase8a-exp062-discovery.yml",
        "--ref",
        "main",
    )


def shell_join(parts: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def build_historical_plan(
    *,
    main_branch: Mapping[str, object],
    workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    if EXP062_HISTORICAL_RUN_AUTHORIZATION_DECISION != "DEC-307":
        raise ValueError("EXP-062 historical authorization decision drift")
    if not HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED:
        raise ValueError("EXP-062 historical-result source slot is not authorized")

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("EXP-062 historical operator requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("EXP-062 historical operator main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("EXP-062 historical operator main head mismatch")

    inventory = classify_historical_run_inventory(workflow_runs)
    stage = inventory["stage"]
    if stage == "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE":
        planned = shell_join(historical_dispatch_command())
    elif stage == "EXP062_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED":
        planned = None
    else:
        raise ValueError("EXP-062 historical operator inventory stage mismatch")

    return {
        "decision": EXP062_HISTORICAL_OPERATOR_DECISION,
        "operator_version": EXP062_HISTORICAL_OPERATOR_VERSION,
        "authorization_decision": EXP062_HISTORICAL_RUN_AUTHORIZATION_DECISION,
        "authorization_version": EXP062_HISTORICAL_RUN_AUTHORIZATION_VERSION,
        "expected_head_sha": expected_head_sha,
        "stage": stage,
        "proof_run_id": inventory["proof_run_id"],
        "proof_head_sha": inventory["proof_head_sha"],
        "proof_run_count": inventory["proof_run_count"],
        "historical_result_attempt_count": inventory[
            "historical_result_attempt_count"
        ],
        "historical_result_run_id": inventory["historical_result_run_id"],
        "historical_result_head_sha": inventory["historical_result_head_sha"],
        "historical_result_run_status": inventory[
            "historical_result_run_status"
        ],
        "historical_result_run_conclusion": inventory[
            "historical_result_run_conclusion"
        ],
        "historical_result_slot_consumed": inventory[
            "historical_result_slot_consumed"
        ],
        "planned_dispatch_command": planned,
        "historical_result_slot_source_authorized": (
            HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED
        ),
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_execute_mode_available": HISTORICAL_EXECUTE_MODE_AVAILABLE,
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


def validate_historical_plan(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    if value.get("decision") != EXP062_HISTORICAL_OPERATOR_DECISION:
        raise ValueError("EXP-062 historical operator decision mismatch")
    if value.get("operator_version") != EXP062_HISTORICAL_OPERATOR_VERSION:
        raise ValueError("EXP-062 historical operator version mismatch")
    if value.get("authorization_decision") != (
        EXP062_HISTORICAL_RUN_AUTHORIZATION_DECISION
    ):
        raise ValueError("EXP-062 historical operator authorization mismatch")
    if value.get("authorization_version") != (
        EXP062_HISTORICAL_RUN_AUTHORIZATION_VERSION
    ):
        raise ValueError(
            "EXP-062 historical operator authorization version mismatch"
        )
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")

    if value.get("historical_result_slot_source_authorized") is not True:
        raise ValueError(
            "EXP-062 historical operator source slot must remain authorized"
        )
    for field in (
        "historical_result_dispatch_authorized",
        "historical_execute_mode_available",
        "historical_discovery_execution_authorized",
        "discovery_result_authorized",
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
        if value.get(field) is not False:
            raise ValueError(
                f"EXP-062 historical operator {field} must remain false"
            )

    if value.get("proof_run_count") != 1:
        raise ValueError("EXP-062 historical operator requires one frozen proof run")

    attempt_count = value.get("historical_result_attempt_count")
    if (
        not isinstance(attempt_count, int)
        or isinstance(attempt_count, bool)
        or attempt_count not in {0, 1}
    ):
        raise ValueError("EXP-062 historical operator attempt count is invalid")

    stage = value.get("stage")
    if stage == "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE":
        if attempt_count != 0:
            raise ValueError("EXP-062 historical operator empty-slot count mismatch")
        if value.get("historical_result_slot_consumed") is not False:
            raise ValueError(
                "EXP-062 historical operator empty slot marked consumed"
            )
        if value.get("historical_result_run_id") is not None:
            raise ValueError(
                "EXP-062 historical operator empty slot run id must be null"
            )
        if value.get("planned_dispatch_command") != shell_join(
            historical_dispatch_command()
        ):
            raise ValueError(
                "EXP-062 historical operator dispatch command mismatch"
            )
    elif stage == "EXP062_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED":
        if attempt_count != 1:
            raise ValueError(
                "EXP-062 historical operator present-run count mismatch"
            )
        if value.get("historical_result_slot_consumed") is not True:
            raise ValueError(
                "EXP-062 historical operator present run must consume slot"
            )
        run_id = value.get("historical_result_run_id")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise ValueError(
                "EXP-062 historical operator present-run id is invalid"
            )
        if value.get("planned_dispatch_command") is not None:
            raise ValueError(
                "EXP-062 historical operator cannot plan a second historical run"
            )
    else:
        raise ValueError("EXP-062 historical operator stage mismatch")
    return value


__all__ = [
    "EXP062_HISTORICAL_OPERATOR_DECISION",
    "EXP062_HISTORICAL_OPERATOR_VERSION",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "build_historical_plan",
    "historical_dispatch_command",
    "shell_join",
    "validate_historical_plan",
]
