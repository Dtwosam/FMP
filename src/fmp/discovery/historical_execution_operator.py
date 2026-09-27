from __future__ import annotations

import shlex
from pathlib import Path
from typing import Mapping, Sequence

from .historical_execution_authorization import (
    EXPECTED_WORKFLOW_RUN_ATTEMPT,
    EXPECTED_WORKFLOW_RUN_NUMBER,
    EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION,
    EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
    HISTORICAL_EXECUTION_SOURCE_AUTHORIZED,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    validate_historical_execution_authorization_sources,
)
from .historical_run_authorization import (
    EXP061_GATE_PROOF_RUN_ID,
    classify_historical_run_inventory,
)


EXP061_HISTORICAL_EXECUTION_OPERATOR_DECISION = "DEC-286"
EXP061_HISTORICAL_EXECUTION_OPERATOR_VERSION = (
    "fmp-exp061-historical-execution-operator-v1"
)

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


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def historical_execution_dispatch_command() -> tuple[str, ...]:
    return (
        "gh",
        "workflow",
        "run",
        "phase8a-exp061-discovery.yml",
        "--ref",
        "main",
    )


def shell_join(parts: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def _matching_runs(
    workflow_runs: Mapping[str, object],
) -> list[Mapping[str, object]]:
    raw = workflow_runs.get("workflow_runs")
    if not isinstance(raw, list):
        raise ValueError("DEC-286 requires workflow_runs list")

    matches: list[Mapping[str, object]] = []
    seen_ids: set[int] = set()
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-286 workflow-run row is malformed")
        run_id = item.get("id")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise ValueError("DEC-286 workflow-run id is invalid")
        if run_id in seen_ids:
            raise ValueError("DEC-286 duplicate workflow-run id")
        seen_ids.add(run_id)
        if (
            item.get("name") == "phase8a-exp061-discovery"
            and item.get("path") == ".github/workflows/phase8a-exp061-discovery.yml"
            and item.get("event") == "workflow_dispatch"
            and item.get("head_branch") == "main"
        ):
            matches.append(item)
    return sorted(matches, key=lambda row: int(row["id"]))


def build_historical_execution_plan(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_historical_execution_authorization_sources(
        repository_root=repository_root,
    )
    if not HISTORICAL_EXECUTION_SOURCE_AUTHORIZED:
        raise ValueError("DEC-286 requires DEC-285 execution source authorization")
    if not HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED:
        raise ValueError("DEC-286 requires DEC-285 runtime execution authorization")
    if HISTORICAL_RESULT_DISPATCH_AUTHORIZED:
        raise ValueError("DEC-286 predecessor dispatch must still be locked")

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-286 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-286 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-286 main head mismatch")

    inventory = classify_historical_run_inventory(workflow_runs)
    matches = _matching_runs(workflow_runs)

    proof = [
        item for item in matches if item.get("id") == EXP061_GATE_PROOF_RUN_ID
    ]
    if len(proof) != 1:
        raise ValueError("DEC-286 requires exactly one frozen proof run")
    if proof[0].get("run_number") != 1:
        raise ValueError("DEC-286 frozen proof must remain workflow run number 1")
    if proof[0].get("run_attempt") != 1:
        raise ValueError("DEC-286 frozen proof must remain attempt 1")

    historical = [
        item for item in matches if item.get("id") != EXP061_GATE_PROOF_RUN_ID
    ]
    if len(historical) > 1:
        raise ValueError("DEC-286 historical slot has multiple attempts")

    stage = inventory["stage"]
    if stage == "EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE":
        if historical:
            raise ValueError("DEC-286 inventory/historical-run mismatch")
        planned = shell_join(historical_execution_dispatch_command())
    elif stage == "EXP061_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED":
        if len(historical) != 1:
            raise ValueError("DEC-286 present-run inventory mismatch")
        run = historical[0]
        if run.get("run_number") != EXPECTED_WORKFLOW_RUN_NUMBER:
            raise ValueError("DEC-286 historical run must be workflow run number 2")
        if run.get("run_attempt") != EXPECTED_WORKFLOW_RUN_ATTEMPT:
            raise ValueError("DEC-286 historical run attempt must remain 1")
        planned = None
    else:
        raise ValueError("DEC-286 inventory stage mismatch")

    return {
        **source,
        "decision": EXP061_HISTORICAL_EXECUTION_OPERATOR_DECISION,
        "operator_version": EXP061_HISTORICAL_EXECUTION_OPERATOR_VERSION,
        "authorization_decision": (
            EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION
        ),
        "authorization_version": (
            EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION
        ),
        "expected_head_sha": expected_head_sha,
        "stage": stage,
        "proof_run_id": inventory["proof_run_id"],
        "proof_run_count": inventory["proof_run_count"],
        "proof_run_number": 1,
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
        "expected_target_run_number": EXPECTED_WORKFLOW_RUN_NUMBER,
        "expected_target_run_attempt": EXPECTED_WORKFLOW_RUN_ATTEMPT,
        "planned_dispatch_command": planned,
        "historical_result_dispatch_authorized": False,
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
    }


def validate_historical_execution_plan(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    if value.get("decision") != EXP061_HISTORICAL_EXECUTION_OPERATOR_DECISION:
        raise ValueError("DEC-286 operator decision mismatch")
    if value.get("operator_version") != EXP061_HISTORICAL_EXECUTION_OPERATOR_VERSION:
        raise ValueError("DEC-286 operator version mismatch")
    if value.get("authorization_decision") != (
        EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION
    ):
        raise ValueError("DEC-286 authorization decision mismatch")
    if value.get("authorization_version") != (
        EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION
    ):
        raise ValueError("DEC-286 authorization version mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")

    if value.get("historical_execution_source_authorized") is not True:
        raise ValueError("DEC-286 requires execution source authorization")
    if value.get("historical_discovery_execution_authorized") is not True:
        raise ValueError("DEC-286 requires runtime execution authorization")
    if value.get("discovery_result_authorized") is not True:
        raise ValueError("DEC-286 requires discovery-result authorization")

    for field in (
        "historical_result_dispatch_authorized",
        "historical_execute_mode_available",
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
            raise ValueError(f"DEC-286 {field} must remain false")

    if value.get("proof_run_count") != 1 or value.get("proof_run_number") != 1:
        raise ValueError("DEC-286 requires the exact workflow run #1 proof")
    if value.get("expected_target_run_number") != 2:
        raise ValueError("DEC-286 target run number must remain 2")
    if value.get("expected_target_run_attempt") != 1:
        raise ValueError("DEC-286 target run attempt must remain 1")

    stage = value.get("stage")
    count = value.get("historical_result_attempt_count")
    if stage == "EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE":
        if count != 0:
            raise ValueError("DEC-286 empty slot count mismatch")
        if value.get("historical_result_slot_consumed") is not False:
            raise ValueError("DEC-286 empty slot marked consumed")
        if value.get("historical_result_run_id") is not None:
            raise ValueError("DEC-286 empty slot run id must be null")
        if value.get("planned_dispatch_command") != shell_join(
            historical_execution_dispatch_command()
        ):
            raise ValueError("DEC-286 planned dispatch command mismatch")
    elif stage == "EXP061_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED":
        if count != 1:
            raise ValueError("DEC-286 present-run count mismatch")
        if value.get("historical_result_slot_consumed") is not True:
            raise ValueError("DEC-286 present run must consume slot")
        run_id = value.get("historical_result_run_id")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise ValueError("DEC-286 present-run id is invalid")
        if value.get("planned_dispatch_command") is not None:
            raise ValueError("DEC-286 cannot plan a second historical run")
    else:
        raise ValueError("DEC-286 stage mismatch")
    return value


__all__ = [
    "EXP061_HISTORICAL_EXECUTION_OPERATOR_DECISION",
    "EXP061_HISTORICAL_EXECUTION_OPERATOR_VERSION",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "build_historical_execution_plan",
    "historical_execution_dispatch_command",
    "validate_historical_execution_plan",
]
