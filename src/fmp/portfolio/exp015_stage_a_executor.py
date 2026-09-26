from __future__ import annotations

from typing import Mapping

from .exp015_stage_a_operator import (
    exp015_stage_a_planned_dispatch_command,
    shell_join,
    validate_exp015_stage_a_operator_report,
)


EXECUTOR_DECISION = "DEC-267"
OPERATOR_DECISION = "DEC-265"
EXECUTION_STAGE = "EXP015_STAGE_A_READ_ONLY_PROOF_REQUIRED"


def validate_exp015_stage_a_fresh_execution_plan(
    plan: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> tuple[str, ...]:
    validated = validate_exp015_stage_a_operator_report(plan)

    if validated.get("operator_decision") != OPERATOR_DECISION:
        raise ValueError("EXP-015 Stage A executor requires the DEC-265 operator")
    if validated.get("head_sha") != expected_head_sha:
        raise ValueError("EXP-015 Stage A executor plan head must equal executor HEAD")
    if validated.get("run_present") is not False:
        raise ValueError("EXP-015 Stage A executor requires an unused authoritative slot")
    if validated.get("run_state") != "MISSING":
        raise ValueError("EXP-015 Stage A executor requires MISSING run state")
    if validated.get("run_id") is not None:
        raise ValueError("EXP-015 Stage A executor missing-state plan cannot bind a run")
    if validated.get("stage") != EXECUTION_STAGE:
        raise ValueError("EXP-015 Stage A executor plan stage mismatch")
    if validated.get("authoritative_slot_available") is not True:
        raise ValueError("EXP-015 Stage A executor requires the sole slot to be available")
    if validated.get("read_only_proof_required") is not True:
        raise ValueError("EXP-015 Stage A executor requires the proven missing-state shape")

    command = exp015_stage_a_planned_dispatch_command()
    if validated.get("planned_dispatch_command") != shell_join(command):
        raise ValueError("EXP-015 Stage A executor planned command mismatch")
    return command


__all__ = [
    "EXECUTION_STAGE",
    "EXECUTOR_DECISION",
    "OPERATOR_DECISION",
    "validate_exp015_stage_a_fresh_execution_plan",
]
