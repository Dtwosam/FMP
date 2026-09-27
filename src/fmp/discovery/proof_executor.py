from __future__ import annotations

from typing import Mapping

from .proof_operator import (
    EXP061_PROOF_OPERATOR_DECISION,
    EXP061_PROOF_OPERATOR_VERSION,
    proof_dispatch_command,
    shell_join,
    validate_proof_plan,
)


EXP061_PROOF_EXECUTOR_DECISION = "DEC-279"
EXP061_PROOF_EXECUTOR_VERSION = "fmp-exp061-proof-one-shot-executor-v1"
REQUIRED_PLAN_STAGE = "EXP061_PROOF_DISPATCH_AUTHORIZATION_REQUIRED"

PROOF_DISPATCH_AUTHORIZED = True
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
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


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def validate_fresh_proof_execution_plan(
    plan: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> tuple[str, ...]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    validated = validate_proof_plan(plan)

    if validated.get("decision") != EXP061_PROOF_OPERATOR_DECISION:
        raise ValueError("EXP-061 proof executor requires DEC-278 operator")
    if validated.get("operator_version") != EXP061_PROOF_OPERATOR_VERSION:
        raise ValueError("EXP-061 proof executor operator version mismatch")
    if validated.get("expected_head_sha") != expected_head_sha:
        raise ValueError("EXP-061 proof executor plan head mismatch")
    if validated.get("stage") != REQUIRED_PLAN_STAGE:
        raise ValueError("EXP-061 proof executor requires a fresh missing-run plan")
    if validated.get("run_present") is not False:
        raise ValueError("EXP-061 proof executor requires no existing proof run")
    if validated.get("run_id") is not None:
        raise ValueError("EXP-061 proof executor fresh plan cannot bind a run")
    if validated.get("matching_manual_main_run_count") != 0:
        raise ValueError("EXP-061 proof executor requires an unused proof slot")
    if validated.get("proof_dispatch_authorized") is not False:
        raise ValueError("DEC-278 plan must remain read-only")
    if validated.get("proof_execute_mode_available") is not False:
        raise ValueError("DEC-278 operator must have no execute mode")

    for field in (
        "historical_result_dispatch_authorized",
        "historical_discovery_execution_authorized",
        "discovery_result_authorized",
        "trading_authorized",
    ):
        if validated.get(field) is not False:
            raise ValueError(
                f"EXP-061 proof executor requires {field}=false in fresh plan"
            )

    command = proof_dispatch_command()
    if validated.get("planned_dispatch_command") != shell_join(command):
        raise ValueError("EXP-061 proof executor planned command mismatch")
    return command


def proof_execution_evidence(
    *,
    plan: Mapping[str, object],
    executor_head_sha: str,
) -> dict[str, object]:
    command = validate_fresh_proof_execution_plan(
        plan,
        expected_head_sha=executor_head_sha,
    )
    return {
        **dict(plan),
        "executor_decision": EXP061_PROOF_EXECUTOR_DECISION,
        "executor_version": EXP061_PROOF_EXECUTOR_VERSION,
        "executor_head_sha": executor_head_sha,
        "fresh_plan_rechecked_twice": True,
        "dispatch_command": shell_join(command),
        "proof_dispatch_authorized_by_dec279": PROOF_DISPATCH_AUTHORIZED,
        "proof_dispatch_submitted": True,
        "historical_result_slot_consumed": False,
        "historical_result_claimed": False,
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
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


__all__ = [
    "EXP061_PROOF_EXECUTOR_DECISION",
    "EXP061_PROOF_EXECUTOR_VERSION",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "PROOF_DISPATCH_AUTHORIZED",
    "REPLACEMENT_RUN_AUTHORIZED",
    "RERUN_AUTHORIZED",
    "RETRY_AUTHORIZED",
    "proof_execution_evidence",
    "validate_fresh_proof_execution_plan",
]
