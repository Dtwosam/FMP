from __future__ import annotations

from typing import Mapping

from .historical_execution_operator import (
    EXP061_HISTORICAL_EXECUTION_OPERATOR_DECISION,
    EXP061_HISTORICAL_EXECUTION_OPERATOR_VERSION,
    historical_execution_dispatch_command,
    shell_join,
    validate_historical_execution_plan,
)
from .historical_execution_plan_result_decision import (
    DEC287_PROOF_ARTIFACT_DIGEST,
    DEC287_PROOF_ARTIFACT_ID,
    DEC287_PROOF_RUN_ID,
    EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_DECISION,
    EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_VERSION,
)


EXP061_HISTORICAL_EXECUTOR_DECISION = "DEC-289"
EXP061_HISTORICAL_EXECUTOR_VERSION = (
    "fmp-exp061-historical-one-shot-executor-v1"
)
REQUIRED_PLAN_STAGE = "EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE"
REQUIRED_REVIEW_STAGE = (
    "EXP061_HISTORICAL_EXECUTION_PLAN_PROOF_REVIEWED_AND_FROZEN"
)

HISTORICAL_RESULT_DISPATCH_AUTHORIZED = True
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = True
DISCOVERY_RESULT_AUTHORIZED = True
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


def validate_reviewed_execution_plan(
    reviewed: Mapping[str, object],
) -> Mapping[str, object]:
    expected = {
        "decision": EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_DECISION,
        "version": EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_VERSION,
        "stage": REQUIRED_REVIEW_STAGE,
        "proof_run_id": DEC287_PROOF_RUN_ID,
        "proof_artifact_id": DEC287_PROOF_ARTIFACT_ID,
        "proof_artifact_digest": DEC287_PROOF_ARTIFACT_DIGEST,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
    }
    for field, expected_value in expected.items():
        if reviewed.get(field) != expected_value:
            raise ValueError(
                f"DEC-289 reviewed predecessor {field} mismatch"
            )
    return reviewed


def validate_fresh_historical_execution_plan(
    plan: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> tuple[str, ...]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    validated = validate_historical_execution_plan(plan)

    if validated.get("decision") != EXP061_HISTORICAL_EXECUTION_OPERATOR_DECISION:
        raise ValueError("DEC-289 requires DEC-286 execution operator")
    if validated.get("operator_version") != (
        EXP061_HISTORICAL_EXECUTION_OPERATOR_VERSION
    ):
        raise ValueError("DEC-289 execution operator version mismatch")
    if validated.get("expected_head_sha") != expected_head_sha:
        raise ValueError("DEC-289 plan head mismatch")
    if validated.get("stage") != REQUIRED_PLAN_STAGE:
        raise ValueError("DEC-289 requires a fresh unused historical slot")
    if validated.get("proof_run_id") != 36319888985:
        raise ValueError("DEC-289 proof run id mismatch")
    if validated.get("proof_run_count") != 1:
        raise ValueError("DEC-289 requires exactly one proof run")
    if validated.get("proof_run_number") != 1:
        raise ValueError("DEC-289 proof must remain workflow run number 1")
    if validated.get("historical_result_attempt_count") != 0:
        raise ValueError("DEC-289 requires zero historical-result attempts")
    if validated.get("historical_result_slot_consumed") is not False:
        raise ValueError("DEC-289 requires an unconsumed historical slot")
    if validated.get("historical_result_run_id") is not None:
        raise ValueError("DEC-289 fresh plan cannot bind a historical run")
    if validated.get("expected_target_run_number") != 2:
        raise ValueError("DEC-289 target workflow run number must be 2")
    if validated.get("expected_target_run_attempt") != 1:
        raise ValueError("DEC-289 target run attempt must be 1")
    if validated.get("historical_execution_source_authorized") is not True:
        raise ValueError("DEC-289 requires execution source authorization")
    if validated.get("historical_discovery_execution_authorized") is not True:
        raise ValueError("DEC-289 requires target runtime execution authorization")
    if validated.get("discovery_result_authorized") is not True:
        raise ValueError("DEC-289 requires target result authorization")
    if validated.get("historical_result_dispatch_authorized") is not False:
        raise ValueError("DEC-286 plan must remain dispatch-read-only")
    if validated.get("historical_execute_mode_available") is not False:
        raise ValueError("DEC-286 operator must have no execute mode")

    for field in (
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
            raise ValueError(f"DEC-289 requires {field}=false")

    command = historical_execution_dispatch_command()
    if validated.get("planned_dispatch_command") != shell_join(command):
        raise ValueError("DEC-289 planned dispatch command mismatch")
    return command


def historical_execution_evidence(
    *,
    plan: Mapping[str, object],
    reviewed_predecessor: Mapping[str, object],
    executor_head_sha: str,
) -> dict[str, object]:
    executor_head_sha = _validate_commit(
        executor_head_sha,
        field="executor_head_sha",
    )
    command = validate_fresh_historical_execution_plan(
        plan,
        expected_head_sha=executor_head_sha,
    )
    reviewed = validate_reviewed_execution_plan(reviewed_predecessor)

    if reviewed.get("planned_dispatch_command_frozen") != shell_join(command):
        raise ValueError("DEC-289 reviewed predecessor command mismatch")

    return {
        **dict(plan),
        "executor_decision": EXP061_HISTORICAL_EXECUTOR_DECISION,
        "executor_version": EXP061_HISTORICAL_EXECUTOR_VERSION,
        "executor_head_sha": executor_head_sha,
        "reviewed_predecessor_decision": reviewed["decision"],
        "reviewed_predecessor_version": reviewed["version"],
        "reviewed_proof_run_id": reviewed["proof_run_id"],
        "reviewed_proof_artifact_id": reviewed["proof_artifact_id"],
        "reviewed_proof_artifact_digest": reviewed["proof_artifact_digest"],
        "reviewed_plan_raw_sha256": reviewed["plan_raw_sha256"],
        "reviewed_plan_canonical_sha256": reviewed["plan_canonical_sha256"],
        "fresh_plan_rechecked_twice": True,
        "dispatch_command": shell_join(command),
        "historical_result_dispatch_authorized_by_dec289": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_result_dispatch_submitted": True,
        "historical_result_slot_consumed_on_submission": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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


__all__ = [
    "DISCOVERY_RESULT_AUTHORIZED",
    "EXP061_HISTORICAL_EXECUTOR_DECISION",
    "EXP061_HISTORICAL_EXECUTOR_VERSION",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "REPLACEMENT_RUN_AUTHORIZED",
    "RERUN_AUTHORIZED",
    "RETRY_AUTHORIZED",
    "historical_execution_evidence",
    "validate_fresh_historical_execution_plan",
    "validate_reviewed_execution_plan",
]
