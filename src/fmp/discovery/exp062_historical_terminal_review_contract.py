from __future__ import annotations

from typing import Mapping

from .exp062_run_contract import (
    AGGREGATE_JOB_NAME,
    EXPECTED_ARTIFACT_COUNT,
    EXPECTED_JOB_COUNT,
    PREFLIGHT_JOB_NAME,
    WORKFLOW_BRANCH,
    WORKFLOW_EVENT,
    WORKFLOW_NAME,
    WORKFLOW_PATH,
    expected_artifact_names,
    expected_job_names,
)
from .exp062_runtime_proof_freeze import PROOF_RUN_ID


EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION = "DEC-334"
EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION = (
    "fmp-exp062-historical-terminal-review-contract-v1"
)

EXPECTED_HISTORICAL_RUN_NUMBER = 2
EXPECTED_HISTORICAL_RUN_ATTEMPT = 1
MATRIX_TEMPLATE_JOB_NAME = (
    "exp062-cell-${{ matrix.dataset.symbol }}-"
    "${{ matrix.dataset.timeframe }}-"
    "${{ matrix.dataset.horizon }}m"
)

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


def _validate_positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _validate_terminal_run(
    run: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> tuple[int, str]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    run_id = _validate_positive_int(
        run.get("id"),
        field="historical run id",
    )
    if run_id == PROOF_RUN_ID:
        raise ValueError("DEC-334 historical run cannot reuse the proof run id")

    expected = {
        "name": WORKFLOW_NAME,
        "path": WORKFLOW_PATH,
        "event": WORKFLOW_EVENT,
        "head_branch": WORKFLOW_BRANCH,
        "head_sha": expected_head_sha,
        "run_number": EXPECTED_HISTORICAL_RUN_NUMBER,
        "run_attempt": EXPECTED_HISTORICAL_RUN_ATTEMPT,
        "status": "completed",
    }
    for field, expected_value in expected.items():
        if run.get(field) != expected_value:
            raise ValueError(f"DEC-334 historical run {field} mismatch")

    conclusion = run.get("conclusion")
    if not isinstance(conclusion, str) or not conclusion:
        raise ValueError("DEC-334 terminal historical run requires a conclusion")
    return run_id, conclusion


def _validate_jobs(
    jobs_payload: Mapping[str, object],
    *,
    run_success: bool,
) -> tuple[list[Mapping[str, object]], bool]:
    raw = jobs_payload.get("jobs")
    if not isinstance(raw, list):
        raise ValueError("DEC-334 jobs payload must contain jobs")

    jobs: list[Mapping[str, object]] = []
    names: list[str] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-334 job row is malformed")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("DEC-334 job name is malformed")
        if item.get("status") != "completed":
            raise ValueError("DEC-334 terminal run has non-terminal job")
        conclusion = item.get("conclusion")
        if not isinstance(conclusion, str) or not conclusion:
            raise ValueError("DEC-334 terminal job requires a conclusion")
        jobs.append(item)
        names.append(name)

    if len(names) != len(set(names)):
        raise ValueError("DEC-334 job inventory contains duplicate names")

    expected = set(expected_job_names())
    allowed = expected | {MATRIX_TEMPLATE_JOB_NAME}
    unexpected = set(names) - allowed
    if unexpected:
        raise ValueError(
            f"DEC-334 unexpected job names: {sorted(unexpected)!r}"
        )

    placeholder = MATRIX_TEMPLATE_JOB_NAME in names
    if placeholder:
        row = next(
            item for item in jobs
            if item.get("name") == MATRIX_TEMPLATE_JOB_NAME
        )
        if row.get("conclusion") != "skipped":
            raise ValueError("DEC-334 matrix template placeholder must be skipped")
        expanded_cells = {
            name
            for name in names
            if name.startswith("exp062-cell-")
            and name != MATRIX_TEMPLATE_JOB_NAME
        }
        if expanded_cells:
            raise ValueError(
                "DEC-334 cannot mix matrix template placeholder with expanded cells"
            )

    if run_success:
        if placeholder:
            raise ValueError(
                "DEC-334 successful run cannot contain matrix template placeholder"
            )
        if set(names) != expected or len(names) != EXPECTED_JOB_COUNT:
            raise ValueError(
                "DEC-334 successful run requires exact 20-job inventory"
            )
        if any(item.get("conclusion") != "success" for item in jobs):
            raise ValueError(
                "DEC-334 successful run requires every job to succeed"
            )
    else:
        if PREFLIGHT_JOB_NAME not in names:
            raise ValueError(
                "DEC-334 non-success run must materialize preflight"
            )
        if AGGREGATE_JOB_NAME in names:
            aggregate = next(
                item for item in jobs
                if item.get("name") == AGGREGATE_JOB_NAME
            )
            if aggregate.get("conclusion") == "success":
                expanded = {
                    name
                    for name in names
                    if name.startswith("exp062-cell-")
                    and name != MATRIX_TEMPLATE_JOB_NAME
                }
                expected_cells = {
                    name
                    for name in expected
                    if name.startswith("exp062-cell-")
                }
                if expanded != expected_cells:
                    raise ValueError(
                        "DEC-334 successful aggregate requires all cell jobs"
                    )

    return jobs, placeholder


def _validate_artifacts(
    artifacts_payload: Mapping[str, object],
    *,
    expected_head_sha: str,
    run_success: bool,
) -> list[Mapping[str, object]]:
    raw = artifacts_payload.get("artifacts")
    if not isinstance(raw, list):
        raise ValueError("DEC-334 artifacts payload must contain artifacts")

    expected = set(expected_artifact_names(code_commit=expected_head_sha))
    artifacts: list[Mapping[str, object]] = []
    names: list[str] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-334 artifact row is malformed")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("DEC-334 artifact name is malformed")
        if name not in expected:
            raise ValueError(f"DEC-334 unexpected artifact name: {name}")
        if item.get("expired") is not False:
            raise ValueError("DEC-334 review requires non-expired artifacts")
        _validate_positive_int(
            item.get("id"),
            field="DEC-334 artifact id",
        )
        artifacts.append(item)
        names.append(name)

    if len(names) != len(set(names)):
        raise ValueError("DEC-334 artifact inventory contains duplicates")

    if run_success:
        if set(names) != expected or len(names) != EXPECTED_ARTIFACT_COUNT:
            raise ValueError(
                "DEC-334 successful run requires exact 20-artifact inventory"
            )
    return artifacts


def classify_historical_terminal_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    run_id, conclusion = _validate_terminal_run(
        run,
        expected_head_sha=expected_head_sha,
    )
    run_success = conclusion == "success"
    jobs, placeholder = _validate_jobs(
        jobs_payload,
        run_success=run_success,
    )
    artifacts = _validate_artifacts(
        artifacts_payload,
        expected_head_sha=expected_head_sha,
        run_success=run_success,
    )

    conclusions: dict[str, int] = {}
    for job in jobs:
        value = str(job["conclusion"])
        conclusions[value] = conclusions.get(value, 0) + 1

    stage = (
        "EXP062_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED"
        if run_success
        else "EXP062_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED"
    )

    return {
        "decision": EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION,
        "version": EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION,
        "stage": stage,
        "historical_run_id": run_id,
        "historical_run_head_sha": expected_head_sha,
        "historical_run_number": EXPECTED_HISTORICAL_RUN_NUMBER,
        "historical_run_attempt": EXPECTED_HISTORICAL_RUN_ATTEMPT,
        "historical_run_conclusion": conclusion,
        "historical_result_slot_consumed": True,
        "historical_result_success_complete": run_success,
        "materialized_job_count": len(jobs),
        "job_conclusion_counts": conclusions,
        "github_unexpanded_matrix_placeholder_present": placeholder,
        "artifact_count": len(artifacts),
        "expected_success_job_count": EXPECTED_JOB_COUNT,
        "expected_success_artifact_count": EXPECTED_ARTIFACT_COUNT,
        "aggregate_result_content_review_required": run_success,
        "partial_evidence_may_be_preserved": not run_success,
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
    "EXPECTED_HISTORICAL_RUN_ATTEMPT",
    "EXPECTED_HISTORICAL_RUN_NUMBER",
    "EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION",
    "EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION",
    "MATRIX_TEMPLATE_JOB_NAME",
    "classify_historical_terminal_result",
]
