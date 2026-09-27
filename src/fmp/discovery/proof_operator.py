from __future__ import annotations

import shlex
from typing import Mapping, Sequence

from .proof_contract import (
    EXP061_GATE_PROOF_CONTRACT_VERSION,
    PROOF_DISPATCH_AUTHORIZED,
)
from .run_contract import (
    WORKFLOW_BRANCH,
    WORKFLOW_EVENT,
    WORKFLOW_NAME,
    WORKFLOW_PATH,
)


EXP061_PROOF_OPERATOR_DECISION = "DEC-278"
EXP061_PROOF_OPERATOR_VERSION = "fmp-exp061-proof-operator-v1"

PROOF_EXECUTE_MODE_AVAILABLE = False
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def proof_dispatch_command() -> tuple[str, ...]:
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


def _matching_manual_main_runs(
    runs_payload: Mapping[str, object],
) -> tuple[Mapping[str, object], ...]:
    raw = runs_payload.get("workflow_runs")
    if not isinstance(raw, list):
        raise ValueError("EXP-061 proof operator requires workflow_runs list")
    matches: list[Mapping[str, object]] = []
    seen_ids: set[int] = set()
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("EXP-061 proof operator run row is malformed")
        run_id = item.get("id")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise ValueError("EXP-061 proof operator run id is invalid")
        if run_id in seen_ids:
            raise ValueError("EXP-061 proof operator duplicate run id")
        seen_ids.add(run_id)
        if (
            item.get("name") == WORKFLOW_NAME
            and item.get("path") == WORKFLOW_PATH
            and item.get("event") == WORKFLOW_EVENT
            and item.get("head_branch") == WORKFLOW_BRANCH
        ):
            matches.append(item)
    return tuple(sorted(matches, key=lambda item: int(item["id"])))


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
        raise ValueError("EXP-061 proof operator requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("EXP-061 proof operator main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("EXP-061 proof operator main head mismatch")

    matches = _matching_manual_main_runs(workflow_runs)
    if matches:
        latest = matches[-1]
        stage = "EXP061_PROOF_RUN_PRESENT_REVIEW_REQUIRED"
        planned = None
        run_present = True
        run_id = latest["id"]
        run_status = latest.get("status")
        run_conclusion = latest.get("conclusion")
    else:
        stage = "EXP061_PROOF_DISPATCH_AUTHORIZATION_REQUIRED"
        planned = shell_join(proof_dispatch_command())
        run_present = False
        run_id = None
        run_status = None
        run_conclusion = None

    return {
        "decision": EXP061_PROOF_OPERATOR_DECISION,
        "operator_version": EXP061_PROOF_OPERATOR_VERSION,
        "proof_contract_version": EXP061_GATE_PROOF_CONTRACT_VERSION,
        "expected_head_sha": expected_head_sha,
        "stage": stage,
        "run_present": run_present,
        "run_id": run_id,
        "run_status": run_status,
        "run_conclusion": run_conclusion,
        "matching_manual_main_run_count": len(matches),
        "planned_dispatch_command": planned,
        "proof_dispatch_authorized": PROOF_DISPATCH_AUTHORIZED,
        "proof_execute_mode_available": PROOF_EXECUTE_MODE_AVAILABLE,
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


def validate_proof_plan(value: Mapping[str, object]) -> Mapping[str, object]:
    if value.get("decision") != EXP061_PROOF_OPERATOR_DECISION:
        raise ValueError("EXP-061 proof operator decision mismatch")
    if value.get("operator_version") != EXP061_PROOF_OPERATOR_VERSION:
        raise ValueError("EXP-061 proof operator version mismatch")
    if value.get("proof_contract_version") != EXP061_GATE_PROOF_CONTRACT_VERSION:
        raise ValueError("EXP-061 proof operator contract mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")

    for field in (
        "proof_dispatch_authorized",
        "proof_execute_mode_available",
        "historical_result_dispatch_authorized",
        "historical_discovery_execution_authorized",
        "discovery_result_authorized",
        "trading_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"EXP-061 proof operator {field} must remain false")

    stage = value.get("stage")
    count = value.get("matching_manual_main_run_count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ValueError("EXP-061 proof operator run count is invalid")

    if stage == "EXP061_PROOF_DISPATCH_AUTHORIZATION_REQUIRED":
        if value.get("run_present") is not False or count != 0:
            raise ValueError("EXP-061 proof operator missing-run shape mismatch")
        if value.get("run_id") is not None:
            raise ValueError("EXP-061 proof operator missing-run id must be null")
        if value.get("planned_dispatch_command") != shell_join(
            proof_dispatch_command()
        ):
            raise ValueError("EXP-061 proof operator dispatch command mismatch")
    elif stage == "EXP061_PROOF_RUN_PRESENT_REVIEW_REQUIRED":
        if value.get("run_present") is not True or count < 1:
            raise ValueError("EXP-061 proof operator present-run shape mismatch")
        run_id = value.get("run_id")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise ValueError("EXP-061 proof operator present-run id is invalid")
        if value.get("planned_dispatch_command") is not None:
            raise ValueError("EXP-061 proof operator cannot plan a second proof run")
    else:
        raise ValueError("EXP-061 proof operator stage mismatch")
    return value


__all__ = [
    "EXP061_PROOF_OPERATOR_DECISION",
    "EXP061_PROOF_OPERATOR_VERSION",
    "PROOF_EXECUTE_MODE_AVAILABLE",
    "build_proof_plan",
    "proof_dispatch_command",
    "shell_join",
    "validate_proof_plan",
]
