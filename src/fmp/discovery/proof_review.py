from __future__ import annotations

from typing import Mapping

from .proof_contract import validate_gate_proof_terminal
from .proof_executor import (
    EXP061_PROOF_EXECUTOR_DECISION,
    EXP061_PROOF_EXECUTOR_VERSION,
    validate_fresh_proof_execution_plan,
)


PROOF_REVIEW_PREP_VERSION = "fmp-exp061-proof-review-prep-v1"


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def validate_proof_executor_evidence(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> Mapping[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    validate_fresh_proof_execution_plan(
        value,
        expected_head_sha=expected_head_sha,
    )
    if value.get("executor_decision") != EXP061_PROOF_EXECUTOR_DECISION:
        raise ValueError("EXP-061 proof review executor decision mismatch")
    if value.get("executor_version") != EXP061_PROOF_EXECUTOR_VERSION:
        raise ValueError("EXP-061 proof review executor version mismatch")
    if value.get("executor_head_sha") != expected_head_sha:
        raise ValueError("EXP-061 proof review executor head mismatch")
    if value.get("fresh_plan_rechecked_twice") is not True:
        raise ValueError("EXP-061 proof review requires two fresh plans")
    if value.get("proof_dispatch_authorized_by_dec279") is not True:
        raise ValueError("EXP-061 proof review DEC-279 authorization mismatch")
    if value.get("proof_dispatch_submitted") is not True:
        raise ValueError("EXP-061 proof review dispatch was not submitted")
    if value.get("historical_result_slot_consumed") is not False:
        raise ValueError("EXP-061 proof review cannot consume historical slot")
    if value.get("historical_result_claimed") is not False:
        raise ValueError("EXP-061 proof review executor cannot claim result")

    for field in (
        "historical_result_dispatch_authorized",
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
            raise ValueError(
                f"EXP-061 proof review executor {field} must remain false"
            )
    return value


def review_proof_terminal(
    *,
    executor_evidence: Mapping[str, object],
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    preflight_evidence: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    validate_proof_executor_evidence(
        executor_evidence,
        expected_head_sha=expected_head_sha,
    )
    terminal = validate_gate_proof_terminal(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        preflight_evidence=preflight_evidence,
        expected_head_sha=expected_head_sha,
    )
    return {
        "review_prep_version": PROOF_REVIEW_PREP_VERSION,
        "executor_evidence_validated": True,
        "executor_head_sha": expected_head_sha,
        **terminal,
    }


__all__ = [
    "PROOF_REVIEW_PREP_VERSION",
    "review_proof_terminal",
    "validate_proof_executor_evidence",
]
