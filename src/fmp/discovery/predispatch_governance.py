from __future__ import annotations

from typing import Mapping, Sequence

from .market_learning_adapter import validate_cell_evidence
from .run_contract import (
    AGGREGATE_JOB_NAME,
    EXPECTED_CELL_COUNT,
    EXPECTED_JOB_COUNT,
    PREFLIGHT_JOB_NAME,
    WORKFLOW_BRANCH,
    WORKFLOW_EVENT,
    WORKFLOW_NAME,
    WORKFLOW_PATH,
    WORKFLOW_RUN_ATTEMPT,
    compile_aggregate_evidence,
    expected_aggregate_artifact_name,
    expected_artifact_names,
    expected_job_names,
    validate_aggregate_evidence,
)


EXP061_PREDISPATCH_GOVERNANCE_DECISION = "DEC-277"
EXP061_PREDISPATCH_GOVERNANCE_VERSION = "fmp-exp061-predispatch-governance-v1"

TERMINAL_NON_SUCCESS_CONCLUSIONS = {"failure", "cancelled", "timed_out"}

WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_RESULT_RUN_AUTHORIZED = False
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


def _validate_sha(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git SHA")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _positive_run_id(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError("EXP-061 run id must be a positive integer")
    return value


def _relevant_manual_main_runs(
    payload: Mapping[str, object],
) -> tuple[Mapping[str, object], ...]:
    raw_runs = payload.get("workflow_runs")
    if not isinstance(raw_runs, list):
        raise ValueError("EXP-061 workflow-run listing is malformed")

    relevant: list[Mapping[str, object]] = []
    seen_ids: set[int] = set()
    for raw in raw_runs:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-061 workflow-run listing contains a malformed row")
        if raw.get("event") != WORKFLOW_EVENT or raw.get("head_branch") != WORKFLOW_BRANCH:
            continue
        run_id = _positive_run_id(raw.get("id"))
        if run_id in seen_ids:
            raise ValueError("EXP-061 workflow-run listing contains duplicate run ids")
        seen_ids.add(run_id)
        if raw.get("name") != WORKFLOW_NAME:
            raise ValueError("EXP-061 manual-main run workflow name mismatch")
        if raw.get("path") != WORKFLOW_PATH:
            raise ValueError("EXP-061 manual-main run workflow path mismatch")
        if raw.get("run_attempt") != WORKFLOW_RUN_ATTEMPT:
            raise ValueError("EXP-061 manual-main run must remain attempt 1")
        _validate_sha(raw.get("head_sha"), field="EXP-061 run head SHA")
        status = raw.get("status")
        if not isinstance(status, str) or not status:
            raise ValueError("EXP-061 manual-main run status is invalid")
        conclusion = raw.get("conclusion")
        if conclusion is not None and not isinstance(conclusion, str):
            raise ValueError("EXP-061 manual-main run conclusion is invalid")
        relevant.append(raw)

    relevant.sort(key=lambda row: _positive_run_id(row.get("id")))
    return tuple(relevant)


def validate_no_prior_manual_main_runs(
    payload: Mapping[str, object],
) -> dict[str, object]:
    relevant = _relevant_manual_main_runs(payload)
    if relevant:
        ids = [int(row["id"]) for row in relevant]
        raise ValueError(
            f"EXP-061 authoritative slot is not empty; manual-main runs exist: {ids}"
        )
    return {
        "decision": EXP061_PREDISPATCH_GOVERNANCE_DECISION,
        "stage": "EXP061_ZERO_PRIOR_MANUAL_MAIN_RUNS_VERIFIED",
        "prior_manual_main_run_count": 0,
        "authoritative_slot_observed_empty": True,
        "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_result_run_authorized": HISTORICAL_RESULT_RUN_AUTHORIZED,
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
    }


def validate_first_run_guard(
    payload: Mapping[str, object],
    *,
    current_run_id: int,
    current_head_sha: str,
) -> dict[str, object]:
    current_run_id = _positive_run_id(current_run_id)
    current_head_sha = _validate_sha(
        current_head_sha,
        field="current EXP-061 run head SHA",
    )
    relevant = _relevant_manual_main_runs(payload)
    if len(relevant) != 1:
        ids = [int(row["id"]) for row in relevant]
        raise ValueError(
            "EXP-061 first-run guard requires the current run to be the only "
            f"manual-main run; observed {ids}"
        )
    run = relevant[0]
    if run.get("id") != current_run_id:
        raise ValueError("EXP-061 first-run guard current run id mismatch")
    if run.get("head_sha") != current_head_sha:
        raise ValueError("EXP-061 first-run guard current head SHA mismatch")
    if run.get("run_attempt") != 1:
        raise ValueError("EXP-061 first-run guard forbids rerun attempts")

    return {
        "decision": EXP061_PREDISPATCH_GOVERNANCE_DECISION,
        "stage": "EXP061_FIRST_RUN_GUARD_PASSED",
        "current_run_id": current_run_id,
        "current_head_sha": current_head_sha,
        "manual_main_run_count": 1,
        "prior_manual_main_run_count": 0,
        "first_run_guard_passed": True,
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
    }


def build_read_only_operator_plan(
    payload: Mapping[str, object],
) -> dict[str, object]:
    relevant = _relevant_manual_main_runs(payload)
    base: dict[str, object] = {
        "decision": EXP061_PREDISPATCH_GOVERNANCE_DECISION,
        "operator_read_only": True,
        "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_result_run_authorized": HISTORICAL_RESULT_RUN_AUTHORIZED,
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

    if not relevant:
        return {
            **base,
            "stage": "EXP061_READ_ONLY_AUTHORIZATION_GATE_REQUIRED",
            "run_present": False,
            "run_id": None,
            "authoritative_slot_observed_empty": True,
            "next_action": (
                "Freeze and merge a separate one-shot historical-run authorization "
                "before any dispatch can be considered."
            ),
        }

    if len(relevant) > 1:
        ids = [int(row["id"]) for row in relevant]
        raise ValueError(
            f"EXP-061 has multiple manual-main runs and must fail closed: {ids}"
        )

    run = relevant[0]
    run_id = _positive_run_id(run.get("id"))
    if run.get("status") == "completed":
        return {
            **base,
            "stage": "EXP061_TERMINAL_REVIEW_REQUIRED",
            "run_present": True,
            "run_id": run_id,
            "authoritative_slot_observed_empty": False,
            "run_head_sha": _validate_sha(
                run.get("head_sha"),
                field="EXP-061 run head SHA",
            ),
            "run_conclusion": run.get("conclusion"),
            "next_action": (
                "Review the single terminal run through the frozen DEC-277 terminal "
                "review contract; do not retry, rerun, or replace it."
            ),
        }

    return {
        **base,
        "stage": "EXP061_RUN_IN_PROGRESS",
        "run_present": True,
        "run_id": run_id,
        "authoritative_slot_observed_empty": False,
        "run_head_sha": _validate_sha(
            run.get("head_sha"),
            field="EXP-061 run head SHA",
        ),
        "run_status": run.get("status"),
        "next_action": (
            "Observe the existing run only; do not dispatch, retry, rerun, or replace it."
        ),
    }


def validate_read_only_operator_plan(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    if value.get("operator_read_only") is not True:
        raise ValueError("EXP-061 operator plan must remain read-only")
    for field in (
        "workflow_dispatch_authorized",
        "historical_result_run_authorized",
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
            raise ValueError(f"EXP-061 operator plan {field} must remain false")
    if "planned_dispatch_command" in value or "dispatch_command" in value:
        raise ValueError("EXP-061 read-only operator plan cannot expose a dispatch command")

    stage = value.get("stage")
    if stage == "EXP061_READ_ONLY_AUTHORIZATION_GATE_REQUIRED":
        if value.get("run_present") is not False:
            raise ValueError("EXP-061 empty-slot plan cannot bind a run")
        if value.get("authoritative_slot_observed_empty") is not True:
            raise ValueError("EXP-061 empty-slot plan must record the empty slot")
    elif stage in {"EXP061_RUN_IN_PROGRESS", "EXP061_TERMINAL_REVIEW_REQUIRED"}:
        if value.get("run_present") is not True:
            raise ValueError("EXP-061 occupied-slot plan must bind a run")
        if value.get("authoritative_slot_observed_empty") is not False:
            raise ValueError("EXP-061 occupied slot cannot remain empty")
        _positive_run_id(value.get("run_id"))
    else:
        raise ValueError("EXP-061 operator plan stage mismatch")
    return value


def _validate_terminal_run(run: Mapping[str, object]) -> tuple[int, str, str]:
    run_id = _positive_run_id(run.get("id"))
    if run.get("name") != WORKFLOW_NAME:
        raise ValueError("EXP-061 terminal review workflow name mismatch")
    if run.get("path") != WORKFLOW_PATH:
        raise ValueError("EXP-061 terminal review workflow path mismatch")
    if run.get("event") != WORKFLOW_EVENT:
        raise ValueError("EXP-061 terminal review event mismatch")
    if run.get("head_branch") != WORKFLOW_BRANCH:
        raise ValueError("EXP-061 terminal review branch mismatch")
    if run.get("run_attempt") != 1:
        raise ValueError("EXP-061 terminal review forbids rerun attempts")
    if run.get("status") != "completed":
        raise ValueError("EXP-061 terminal review requires a completed run")
    head_sha = _validate_sha(run.get("head_sha"), field="EXP-061 terminal head SHA")
    conclusion = run.get("conclusion")
    if conclusion not in {"success", *TERMINAL_NON_SUCCESS_CONCLUSIONS}:
        raise ValueError(f"unexpected EXP-061 terminal conclusion: {conclusion!r}")
    return run_id, head_sha, str(conclusion)


def _validate_jobs(
    jobs_payload: Mapping[str, object],
    *,
    require_success: bool,
) -> tuple[dict[str, Mapping[str, object]], int]:
    raw_jobs = jobs_payload.get("jobs")
    if not isinstance(raw_jobs, list):
        raise ValueError("EXP-061 terminal job listing is malformed")
    expected = set(expected_job_names())
    by_name: dict[str, Mapping[str, object]] = {}
    seen_ids: set[int] = set()
    for raw in raw_jobs:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-061 terminal job row is malformed")
        job_id = raw.get("id")
        if not isinstance(job_id, int) or isinstance(job_id, bool) or job_id in seen_ids:
            raise ValueError("EXP-061 terminal job id is malformed or duplicated")
        seen_ids.add(job_id)
        name = raw.get("name")
        if not isinstance(name, str) or name not in expected or name in by_name:
            raise ValueError(f"unexpected or duplicate EXP-061 terminal job name: {name!r}")
        if raw.get("status") != "completed":
            raise ValueError("EXP-061 terminal review requires terminal jobs")
        by_name[name] = raw

    if require_success:
        if set(by_name) != expected or len(by_name) != EXPECTED_JOB_COUNT:
            raise ValueError("successful EXP-061 run requires exact 20-job inventory")
        if any(job.get("conclusion") != "success" for job in by_name.values()):
            raise ValueError("successful EXP-061 run requires every job to succeed")
    elif not by_name:
        raise ValueError("non-success EXP-061 run must expose at least one terminal job")
    return by_name, len(by_name)


def _validate_artifacts(
    artifacts_payload: Mapping[str, object],
    *,
    head_sha: str,
    require_success: bool,
) -> tuple[set[str], int]:
    raw = artifacts_payload.get("artifacts")
    if not isinstance(raw, list):
        raise ValueError("EXP-061 terminal artifact listing is malformed")
    expected = set(expected_artifact_names(code_commit=head_sha))
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("EXP-061 terminal artifact row is malformed")
        name = item.get("name")
        if not isinstance(name, str) or name in seen or name not in expected:
            raise ValueError(f"unexpected or duplicate EXP-061 terminal artifact: {name!r}")
        if item.get("expired") is not False:
            raise ValueError("EXP-061 terminal review requires non-expired artifacts")
        seen.add(name)

    total_count = artifacts_payload.get("total_count")
    if total_count is not None and total_count != len(raw):
        raise ValueError("EXP-061 terminal artifact count mismatch")
    if require_success and seen != expected:
        raise ValueError("successful EXP-061 run requires exact 20-artifact inventory")
    return seen, len(seen)


def validate_terminal_review(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    cell_evidence: Sequence[Mapping[str, object]] | None = None,
    aggregate_evidence: Mapping[str, object] | None = None,
) -> dict[str, object]:
    run_id, head_sha, conclusion = _validate_terminal_run(run)
    success = conclusion == "success"
    jobs, job_count = _validate_jobs(jobs_payload, require_success=success)
    artifacts, artifact_count = _validate_artifacts(
        artifacts_payload,
        head_sha=head_sha,
        require_success=success,
    )

    base = {
        "decision": EXP061_PREDISPATCH_GOVERNANCE_DECISION,
        "terminal_reviewed": True,
        "reviewed_run_id": run_id,
        "reviewed_head_sha": head_sha,
        "reviewed_run_attempt": 1,
        "reviewed_conclusion": conclusion,
        "terminal_job_count": job_count,
        "persisted_artifact_count": artifact_count,
        "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_result_run_authorized": HISTORICAL_RESULT_RUN_AUTHORIZED,
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

    aggregate_name = expected_aggregate_artifact_name(code_commit=head_sha)

    if success:
        if cell_evidence is None or len(cell_evidence) != EXPECTED_CELL_COUNT:
            raise ValueError("successful EXP-061 terminal review requires 18 cell evidence objects")
        validated_cells = [validate_cell_evidence(item) for item in cell_evidence]
        if aggregate_evidence is None:
            raise ValueError("successful EXP-061 terminal review requires aggregate evidence")
        validated_aggregate = validate_aggregate_evidence(aggregate_evidence)
        rebuilt = compile_aggregate_evidence(
            validated_cells,
            code_commit=head_sha,
        )
        if dict(validated_aggregate) != rebuilt:
            raise ValueError("EXP-061 aggregate evidence does not reproduce from cell evidence")
        return {
            **base,
            "stage": "EXP061_HISTORICAL_RESULT_REVIEW_REQUIRED",
            "verified_cell_evidence_count": EXPECTED_CELL_COUNT,
            "aggregate_artifact_present": aggregate_name in artifacts,
            "aggregate_evidence_verified": True,
            "validated_pattern_count": rebuilt["validation_accepted_count"],
        }

    if aggregate_evidence is not None:
        raise ValueError("non-success EXP-061 terminal review cannot claim aggregate evidence")
    if aggregate_name in artifacts:
        raise ValueError("non-success EXP-061 terminal review cannot claim aggregate artifact")
    if cell_evidence is not None:
        for item in cell_evidence:
            validate_cell_evidence(item)

    return {
        **base,
        "stage": "EXP061_RUN_FAILURE_REVIEW_REQUIRED",
        "successful_job_count": sum(
            job.get("conclusion") == "success" for job in jobs.values()
        ),
        "failed_job_count": sum(
            job.get("conclusion") == "failure" for job in jobs.values()
        ),
        "cancelled_job_count": sum(
            job.get("conclusion") == "cancelled" for job in jobs.values()
        ),
        "skipped_job_count": sum(
            job.get("conclusion") == "skipped" for job in jobs.values()
        ),
        "persisted_expected_artifacts": sorted(artifacts),
        "aggregate_artifact_present": False,
        "aggregate_evidence_verified": False,
    }


__all__ = [
    "CANDIDATE_COMPILATION_AUTHORIZED",
    "DISCOVERY_RESULT_AUTHORIZED",
    "EXP061_PREDISPATCH_GOVERNANCE_DECISION",
    "EXP061_PREDISPATCH_GOVERNANCE_VERSION",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "HISTORICAL_RESULT_RUN_AUTHORIZED",
    "RERUN_AUTHORIZED",
    "REPLACEMENT_RUN_AUTHORIZED",
    "RETRY_AUTHORIZED",
    "TERMINAL_NON_SUCCESS_CONCLUSIONS",
    "WORKFLOW_DISPATCH_AUTHORIZED",
    "build_read_only_operator_plan",
    "validate_first_run_guard",
    "validate_no_prior_manual_main_runs",
    "validate_read_only_operator_plan",
    "validate_terminal_review",
]
