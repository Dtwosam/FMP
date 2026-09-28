from __future__ import annotations

from typing import Mapping

from .exp062_proof_executor import (
    proof_execution_evidence,
    validate_fresh_proof_execution_plan,
)


EXP062_CONNECTOR_PROOF_BOOTSTRAP_DECISION = "DEC-306"
EXP062_CONNECTOR_PROOF_BOOTSTRAP_VERSION = (
    "fmp-exp062-connector-proof-bootstrap-v1"
)
REQUIRED_EVENT_NAME = "pull_request"
REQUIRED_BASE_REF = "main"
REQUIRED_HEAD_REF = "phase8a-dec307-exp062-proof-bootstrap-activation"


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def build_connector_proof_bootstrap_evidence(
    first_plan: Mapping[str, object],
    second_plan: Mapping[str, object],
    *,
    main_head_sha: str,
    event_name: str,
    base_ref: str,
    head_ref: str,
    run_attempt: int,
) -> dict[str, object]:
    main_head_sha = _validate_commit(main_head_sha, field="main_head_sha")
    if event_name != REQUIRED_EVENT_NAME:
        raise ValueError("DEC-306 requires pull_request event")
    if base_ref != REQUIRED_BASE_REF:
        raise ValueError("DEC-306 requires base ref main")
    if head_ref != REQUIRED_HEAD_REF:
        raise ValueError("DEC-306 activation branch mismatch")
    if isinstance(run_attempt, bool) or run_attempt != 1:
        raise ValueError("DEC-306 refuses workflow reruns")
    if dict(first_plan) != dict(second_plan):
        raise ValueError("DEC-306 proof plans changed before dispatch")

    first_command = validate_fresh_proof_execution_plan(
        first_plan,
        expected_head_sha=main_head_sha,
    )
    second_command = validate_fresh_proof_execution_plan(
        second_plan,
        expected_head_sha=main_head_sha,
    )
    if first_command != second_command:
        raise ValueError("DEC-306 proof command changed before dispatch")

    evidence = proof_execution_evidence(
        plan=second_plan,
        executor_head_sha=main_head_sha,
    )
    return {
        **evidence,
        "bootstrap_decision": EXP062_CONNECTOR_PROOF_BOOTSTRAP_DECISION,
        "bootstrap_version": EXP062_CONNECTOR_PROOF_BOOTSTRAP_VERSION,
        "bootstrap_main_head_sha": main_head_sha,
        "bootstrap_event_name": event_name,
        "bootstrap_base_ref": base_ref,
        "bootstrap_head_ref": head_ref,
        "bootstrap_run_attempt": run_attempt,
        "connector_recovery_path": True,
    }


__all__ = [
    "EXP062_CONNECTOR_PROOF_BOOTSTRAP_DECISION",
    "EXP062_CONNECTOR_PROOF_BOOTSTRAP_VERSION",
    "REQUIRED_BASE_REF",
    "REQUIRED_EVENT_NAME",
    "REQUIRED_HEAD_REF",
    "build_connector_proof_bootstrap_evidence",
]
