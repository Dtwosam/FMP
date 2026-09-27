from __future__ import annotations

from typing import Mapping

from .exp062_proof_operator import (
    EXP062_PROOF_OPERATOR_DECISION,
    EXP062_PROOF_OPERATOR_VERSION,
    proof_dispatch_command,
    shell_join,
    validate_proof_plan,
)


EXP062_PROOF_EXECUTOR_DECISION = "DEC-303"
EXP062_PROOF_EXECUTOR_VERSION = (
    "fmp-exp062-proof-one-shot-executor-v1"
)
REQUIRED_PLAN_STAGE = "EXP062_PROOF_DISPATCH_AUTHORIZATION_REQUIRED"

PROOF_DISPATCH_AUTHORIZED = True
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

    if validated.get("decision") != EXP062_PROOF_OPERATOR_DECISION:
        raise ValueError("DEC-303 requires DEC-302 proof operator")
    if validated.get("operator_version") != EXP062_PROOF_OPERATOR_VERSION:
        raise ValueError("DEC-303 proof operator version mismatch")
    if validated.get("expected_head_sha") != expected_head_sha:
        raise ValueError("DEC-303 plan head mismatch")
    if validated.get("stage") != REQUIRED_PLAN_STAGE:
        raise ValueError("DEC-303 requires a fresh zero-run proof plan")
    if validated.get("run_present") is not False:
        raise ValueError("DEC-303 requires no existing EXP-062 run")
    if validated.get("run_id") is not None:
        raise ValueError("DEC-303 fresh plan cannot bind a run")
    if validated.get("matching_manual_main_run_count") != 0:
        raise ValueError("DEC-303 requires zero EXP-062 manual-main runs")
    if validated.get("proof_dispatch_authorized") is not False:
        raise ValueError("DEC-302 plan must remain dispatch-read-only")
    if validated.get("proof_execute_mode_available") is not False:
        raise ValueError("DEC-302 operator must have no execute mode")

    for field in (
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
        if validated.get(field) is not False:
            raise ValueError(f"DEC-303 requires {field}=false")

    command = proof_dispatch_command()
    if validated.get("planned_dispatch_command") != shell_join(command):
        raise ValueError("DEC-303 planned proof command mismatch")
    return command


def proof_execution_evidence(
    *,
    plan: Mapping[str, object],
    executor_head_sha: str,
) -> dict[str, object]:
    executor_head_sha = _validate_commit(
        executor_head_sha,
        field="executor_head_sha",
    )
    command = validate_fresh_proof_execution_plan(
        plan,
        expected_head_sha=executor_head_sha,
    )
    return {
        **dict(plan),
        "executor_decision": EXP062_PROOF_EXECUTOR_DECISION,
        "executor_version": EXP062_PROOF_EXECUTOR_VERSION,
        "executor_head_sha": executor_head_sha,
        "fresh_plan_rechecked_twice": True,
        "dispatch_command": shell_join(command),
        "proof_dispatch_authorized_by_dec303": True,
        "proof_dispatch_submitted": True,
        "historical_result_slot_consumed": False,
        "historical_result_claimed": False,
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


__all__ = [
    "EXP062_PROOF_EXECUTOR_DECISION",
    "EXP062_PROOF_EXECUTOR_VERSION",
    "PROOF_DISPATCH_AUTHORIZED",
    "proof_execution_evidence",
    "validate_fresh_proof_execution_plan",
]
