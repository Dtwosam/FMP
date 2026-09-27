from __future__ import annotations

from typing import Mapping

from .run_contract import (
    EXP061_RUN_CONTRACT_VERSION,
    WORKFLOW_BRANCH,
    WORKFLOW_EVENT,
    WORKFLOW_NAME,
    WORKFLOW_PATH,
    WORKFLOW_RUN_ATTEMPT,
)


EXP061_EXECUTION_GATE_DECISION = "DEC-275"
EXP061_EXECUTION_GATE_VERSION = "fmp-exp061-execution-gate-v1"

WORKFLOW_SOURCE_FROZEN = True
WORKFLOW_ACTIVATION_AUTHORIZED = False
WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _validate_commit(value: str) -> str:
    if len(value) != 40:
        raise ValueError("EXP-061 code commit must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("EXP-061 code commit must be hexadecimal") from exc
    return value


def execution_gate_report(*, code_commit: str) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    return {
        "decision": EXP061_EXECUTION_GATE_DECISION,
        "gate_version": EXP061_EXECUTION_GATE_VERSION,
        "run_contract_version": EXP061_RUN_CONTRACT_VERSION,
        "code_commit": code_commit,
        "stage": "EXP061_WORKFLOW_SOURCE_FROZEN_EXECUTION_LOCKED",
        "workflow": {
            "name": WORKFLOW_NAME,
            "path": WORKFLOW_PATH,
            "event": WORKFLOW_EVENT,
            "branch": WORKFLOW_BRANCH,
            "run_attempt": WORKFLOW_RUN_ATTEMPT,
        },
        "workflow_source_frozen": WORKFLOW_SOURCE_FROZEN,
        "workflow_activation_authorized": WORKFLOW_ACTIVATION_AUTHORIZED,
        "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
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
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


def validate_execution_gate_report(value: Mapping[str, object]) -> Mapping[str, object]:
    if value.get("decision") != EXP061_EXECUTION_GATE_DECISION:
        raise ValueError("EXP-061 execution-gate decision mismatch")
    if value.get("gate_version") != EXP061_EXECUTION_GATE_VERSION:
        raise ValueError("EXP-061 execution-gate version mismatch")
    if value.get("run_contract_version") != EXP061_RUN_CONTRACT_VERSION:
        raise ValueError("EXP-061 execution-gate run-contract mismatch")
    _validate_commit(str(value.get("code_commit")))
    if value.get("stage") != "EXP061_WORKFLOW_SOURCE_FROZEN_EXECUTION_LOCKED":
        raise ValueError("EXP-061 execution-gate stage mismatch")
    if value.get("workflow_source_frozen") is not True:
        raise ValueError("EXP-061 workflow source must be frozen")
    for field in (
        "workflow_activation_authorized",
        "workflow_dispatch_authorized",
        "historical_discovery_execution_authorized",
        "discovery_result_authorized",
        "rerun_authorized",
        "retry_authorized",
        "replacement_run_authorized",
        "reserved_robustness_access_authorized",
        "candidate_compilation_authorized",
        "phase8b_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"EXP-061 execution-gate {field} must remain false")
    workflow = value.get("workflow")
    if not isinstance(workflow, Mapping):
        raise ValueError("EXP-061 execution-gate workflow identity is malformed")
    expected = {
        "name": WORKFLOW_NAME,
        "path": WORKFLOW_PATH,
        "event": WORKFLOW_EVENT,
        "branch": WORKFLOW_BRANCH,
        "run_attempt": WORKFLOW_RUN_ATTEMPT,
    }
    if dict(workflow) != expected:
        raise ValueError("EXP-061 execution-gate workflow identity mismatch")
    return value


def require_historical_execution_authorized(*, code_commit: str) -> None:
    report = execution_gate_report(code_commit=code_commit)
    validate_execution_gate_report(report)
    raise PermissionError(
        "DEC-275 freezes EXP-061 workflow/CLI source only; historical discovery "
        "execution and result production remain locked"
    )


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_COMPILATION_AUTHORIZED",
    "DEMO_ORDER_AUTHORIZED",
    "DISCOVERY_RESULT_AUTHORIZED",
    "EXP061_EXECUTION_GATE_DECISION",
    "EXP061_EXECUTION_GATE_VERSION",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "PHASE8B_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "RERUN_AUTHORIZED",
    "REPLACEMENT_RUN_AUTHORIZED",
    "RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED",
    "RETRY_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "WORKFLOW_ACTIVATION_AUTHORIZED",
    "WORKFLOW_DISPATCH_AUTHORIZED",
    "WORKFLOW_SOURCE_FROZEN",
    "execution_gate_report",
    "require_historical_execution_authorized",
    "validate_execution_gate_report",
]
