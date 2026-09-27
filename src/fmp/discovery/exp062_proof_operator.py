from __future__ import annotations

import shlex
from typing import Mapping, Sequence

from .exp062_proof_contract import (
    EXP062_GATE_PROOF_CONTRACT_VERSION,
    PROOF_DISPATCH_AUTHORIZED,
)
from .exp062_run_contract import (
    WORKFLOW_BRANCH,
    WORKFLOW_EVENT,
    WORKFLOW_NAME,
    WORKFLOW_PATH,
)


EXP062_PROOF_OPERATOR_DECISION = "DEC-302"
EXP062_PROOF_OPERATOR_VERSION = "fmp-exp062-proof-operator-v1"

PROOF_EXECUTE_MODE_AVAILABLE = False
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


def proof_dispatch_command() -> tuple[str, ...]:
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


def _matching_manual_main_runs(
    runs_payload: Mapping[str, object],
) -> tuple[Mapping[str, object], ...]:
    raw = runs_payload.get("workflow_runs")
    if not isinstance(raw, list):
        raise ValueError("DEC-302 requires workflow_runs list")

    matches: list[Mapping[str, object]] = []
    seen_ids: set[int] = set()
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-302 workflow-run row is malformed")
        run_id = item.get("id")
        if (
            not isinstance(run_id, int)
            or isinstance(run_id, bool)
            or run_id <= 0
        ):
            raise ValueError("DEC-302 workflow-run id is invalid")
        if run_id in seen_ids:
            raise ValueError("DEC-302 duplicate workflow-run id")
        seen_ids.add(run_id)

        if (
            item.get("name") == WORKFLOW_NAME
            and item.get("path") == WORKFLOW_PATH
            and item.get("event") == WORKFLOW_EVENT
            and item.get("head_branch") == WORKFLOW_BRANCH
        ):
            matches.append(item)

    matches.sort(key=lambda item: int(item["id"]))
    return tuple(matches)


def build_proof_plan(
    *,
    main_branch: Mapping[str, object],
    workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-302 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-302 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-302 main head mismatch")

    matches = _matching_manual_main_runs(workflow_runs)
    if len(matches) > 1:
        raise ValueError("DEC-302 refuses multiple EXP-062 proof/history runs")

    if matches:
        run = matches[0]
        if run.get("run_number") != 1:
            raise ValueError("DEC-302 first EXP-062 run must be workflow run #1")
        if run.get("run_attempt") != 1:
            raise ValueError("DEC-302 first EXP-062 run attempt must be 1")
        stage = "EXP062_PROOF_RUN_PRESENT_REVIEW_REQUIRED"
        planned = None
        run_present = True
        run_id = run["id"]
        run_head_sha = run.get("head_sha")
        run_status = run.get("status")
        run_conclusion = run.get("conclusion")
    else:
        stage = "EXP062_PROOF_DISPATCH_AUTHORIZATION_REQUIRED"
        planned = shell_join(proof_dispatch_command())
        run_present = False
        run_id = None
        run_head_sha = None
        run_status = None
        run_conclusion = None

    return {
        "decision": EXP062_PROOF_OPERATOR_DECISION,
        "operator_version": EXP062_PROOF_OPERATOR_VERSION,
        "proof_contract_version": EXP062_GATE_PROOF_CONTRACT_VERSION,
        "expected_head_sha": expected_head_sha,
        "stage": stage,
        "run_present": run_present,
        "run_id": run_id,
        "run_head_sha": run_head_sha,
        "run_status": run_status,
        "run_conclusion": run_conclusion,
        "matching_manual_main_run_count": len(matches),
        "planned_dispatch_command": planned,
        "proof_dispatch_authorized": PROOF_DISPATCH_AUTHORIZED,
        "proof_execute_mode_available": PROOF_EXECUTE_MODE_AVAILABLE,
        "historical_result_dispatch_authorized": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
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


def validate_proof_plan(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    if value.get("decision") != EXP062_PROOF_OPERATOR_DECISION:
        raise ValueError("DEC-302 operator decision mismatch")
    if value.get("operator_version") != EXP062_PROOF_OPERATOR_VERSION:
        raise ValueError("DEC-302 operator version mismatch")
    if value.get("proof_contract_version") != (
        EXP062_GATE_PROOF_CONTRACT_VERSION
    ):
        raise ValueError("DEC-302 proof contract mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")

    for field in (
        "proof_dispatch_authorized",
        "proof_execute_mode_available",
        "historical_result_dispatch_authorized",
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
            raise ValueError(f"DEC-302 {field} must remain false")

    stage = value.get("stage")
    count = value.get("matching_manual_main_run_count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ValueError("DEC-302 run count is invalid")

    if stage == "EXP062_PROOF_DISPATCH_AUTHORIZATION_REQUIRED":
        if value.get("run_present") is not False or count != 0:
            raise ValueError("DEC-302 missing-run shape mismatch")
        if value.get("run_id") is not None:
            raise ValueError("DEC-302 missing-run id must be null")
        if value.get("planned_dispatch_command") != shell_join(
            proof_dispatch_command()
        ):
            raise ValueError("DEC-302 planned proof command mismatch")
    elif stage == "EXP062_PROOF_RUN_PRESENT_REVIEW_REQUIRED":
        if value.get("run_present") is not True or count != 1:
            raise ValueError("DEC-302 present-run shape mismatch")
        run_id = value.get("run_id")
        if (
            not isinstance(run_id, int)
            or isinstance(run_id, bool)
            or run_id <= 0
        ):
            raise ValueError("DEC-302 present-run id is invalid")
        if value.get("planned_dispatch_command") is not None:
            raise ValueError("DEC-302 cannot plan a second proof run")
    else:
        raise ValueError("DEC-302 stage mismatch")

    return value


__all__ = [
    "EXP062_PROOF_OPERATOR_DECISION",
    "EXP062_PROOF_OPERATOR_VERSION",
    "PROOF_EXECUTE_MODE_AVAILABLE",
    "build_proof_plan",
    "proof_dispatch_command",
    "shell_join",
    "validate_proof_plan",
]
