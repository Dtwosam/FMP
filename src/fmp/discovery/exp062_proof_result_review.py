from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .exp062_proof_contract import (
    EXP062_GATE_PROOF_CONTRACT_DECISION,
    EXP062_GATE_PROOF_CONTRACT_VERSION,
    validate_gate_proof_terminal,
)
from .exp062_proof_executor import (
    EXP062_PROOF_EXECUTOR_DECISION,
    EXP062_PROOF_EXECUTOR_VERSION,
)
from .exp062_proof_operator import (
    EXP062_PROOF_OPERATOR_DECISION,
    EXP062_PROOF_OPERATOR_VERSION,
    proof_dispatch_command,
    shell_join,
)


EXP062_PROOF_RESULT_REVIEW_DECISION = "DEC-304"
EXP062_PROOF_RESULT_REVIEW_VERSION = (
    "fmp-exp062-proof-result-review-v1"
)

HISTORICAL_RESULT_SLOT_OPEN_AUTHORIZED = False
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


def _validate_executor_evidence(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> Mapping[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    expected = {
        "decision": EXP062_PROOF_OPERATOR_DECISION,
        "operator_version": EXP062_PROOF_OPERATOR_VERSION,
        "proof_contract_version": EXP062_GATE_PROOF_CONTRACT_VERSION,
        "expected_head_sha": expected_head_sha,
        "stage": "EXP062_PROOF_DISPATCH_AUTHORIZATION_REQUIRED",
        "run_present": False,
        "run_id": None,
        "run_head_sha": None,
        "run_status": None,
        "run_conclusion": None,
        "matching_manual_main_run_count": 0,
        "planned_dispatch_command": shell_join(proof_dispatch_command()),
        "proof_dispatch_authorized": False,
        "proof_execute_mode_available": False,
        "executor_decision": EXP062_PROOF_EXECUTOR_DECISION,
        "executor_version": EXP062_PROOF_EXECUTOR_VERSION,
        "executor_head_sha": expected_head_sha,
        "fresh_plan_rechecked_twice": True,
        "dispatch_command": shell_join(proof_dispatch_command()),
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
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(
                f"DEC-304 executor evidence {field} mismatch"
            )
    return value


def review_gate_proof_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    preflight_evidence: Mapping[str, object],
    executor_evidence: Mapping[str, object],
    expected_head_sha: str,
    repository_root: Path = Path("."),
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    terminal = validate_gate_proof_terminal(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        preflight_evidence=preflight_evidence,
        expected_head_sha=expected_head_sha,
        repository_root=repository_root,
    )
    executor = _validate_executor_evidence(
        executor_evidence,
        expected_head_sha=expected_head_sha,
    )

    if terminal.get("decision") != EXP062_GATE_PROOF_CONTRACT_DECISION:
        raise ValueError("DEC-304 terminal proof decision mismatch")
    if terminal.get("contract_version") != (
        EXP062_GATE_PROOF_CONTRACT_VERSION
    ):
        raise ValueError("DEC-304 terminal proof contract mismatch")
    if terminal.get("stage") != "EXP062_GATE_PROOF_REVIEWED_FAIL_CLOSED":
        raise ValueError("DEC-304 terminal proof stage mismatch")
    if terminal.get("proof_head_sha") != expected_head_sha:
        raise ValueError("DEC-304 proof head mismatch")

    for field in (
        "historical_result_slot_consumed",
        "historical_discovery_execution_occurred",
        "proof_dispatch_authorized",
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
        if terminal.get(field) is not False:
            raise ValueError(f"DEC-304 terminal {field} must remain false")

    return {
        "decision": EXP062_PROOF_RESULT_REVIEW_DECISION,
        "version": EXP062_PROOF_RESULT_REVIEW_VERSION,
        "stage": "EXP062_GATE_PROOF_RESULT_REVIEWED_FAIL_CLOSED",
        "proof_contract_decision": terminal["decision"],
        "proof_contract_version": terminal["contract_version"],
        "proof_executor_decision": executor["executor_decision"],
        "proof_executor_version": executor["executor_version"],
        "proof_run_id": terminal["proof_run_id"],
        "proof_head_sha": expected_head_sha,
        "proof_run_number": terminal["proof_run_number"],
        "proof_run_attempt": terminal["proof_run_attempt"],
        "proof_run_conclusion": terminal["proof_run_conclusion"],
        "preflight_artifact_id": terminal["preflight_artifact_id"],
        "preflight_artifact_digest": terminal["preflight_artifact_digest"],
        "materialized_job_count": terminal["materialized_job_count"],
        "materialized_downstream_job_count": terminal[
            "materialized_downstream_job_count"
        ],
        "materialized_downstream_job_names": terminal[
            "materialized_downstream_job_names"
        ],
        "github_unexpanded_matrix_placeholder_present": terminal[
            "github_unexpanded_matrix_placeholder_present"
        ],
        "historical_result_slot_consumed": False,
        "historical_result_slot_open_authorized": False,
        "historical_discovery_execution_occurred": False,
        "cell_result_artifact_count": 0,
        "aggregate_result_artifact_count": 0,
        "proof_dispatch_submitted": True,
        "proof_dispatch_authorized": False,
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
        "next_gate": (
            "IMMUTABLE_PROOF_RESULT_FREEZE_BEFORE_HISTORICAL_SLOT"
        ),
    }


__all__ = [
    "EXP062_PROOF_RESULT_REVIEW_DECISION",
    "EXP062_PROOF_RESULT_REVIEW_VERSION",
    "review_gate_proof_result",
]
