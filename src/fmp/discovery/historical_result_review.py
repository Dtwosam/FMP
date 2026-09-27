from __future__ import annotations

from typing import Mapping

from .run_contract import (
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


EXP061_HISTORICAL_RESULT_REVIEW_DECISION = "DEC-290"
EXP061_HISTORICAL_RESULT_REVIEW_VERSION = (
    "fmp-exp061-historical-result-review-contract-v1"
)

EXPECTED_WORKFLOW_RUN_NUMBER = 2
EXPECTED_WORKFLOW_RUN_ATTEMPT = 1
UNEXPANDED_MATRIX_JOB_NAME = (
    "exp061-cell-${{ matrix.dataset.symbol }}-"
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


def _validate_digest(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"{field} must use sha256:<hex>")
    raw = value.removeprefix("sha256:")
    if len(raw) != 64:
        raise ValueError(f"{field} must contain a 64-character sha256")
    try:
        int(raw, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _require_run_identity(
    run: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> tuple[int, str]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    run_id = run.get("id")
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        raise ValueError("DEC-290 historical run id must be a positive integer")

    expected = {
        "name": WORKFLOW_NAME,
        "path": WORKFLOW_PATH,
        "event": WORKFLOW_EVENT,
        "head_branch": WORKFLOW_BRANCH,
        "head_sha": expected_head_sha,
        "run_number": EXPECTED_WORKFLOW_RUN_NUMBER,
        "run_attempt": EXPECTED_WORKFLOW_RUN_ATTEMPT,
        "status": "completed",
    }
    for field, expected_value in expected.items():
        if run.get(field) != expected_value:
            raise ValueError(f"DEC-290 historical run {field} mismatch")

    conclusion = run.get("conclusion")
    if not isinstance(conclusion, str) or not conclusion:
        raise ValueError("DEC-290 historical run conclusion must be terminal")
    return run_id, conclusion


def _validate_jobs(
    jobs_payload: Mapping[str, object],
    *,
    run_id: int,
    success: bool,
) -> tuple[list[Mapping[str, object]], list[str]]:
    raw = jobs_payload.get("jobs")
    if not isinstance(raw, list) or not raw:
        raise ValueError("DEC-290 requires at least one materialized job")

    expected = set(expected_job_names())
    allowed = expected | {UNEXPANDED_MATRIX_JOB_NAME}
    rows: list[Mapping[str, object]] = []
    names: list[str] = []
    seen_ids: set[int] = set()

    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-290 job row is malformed")
        job_id = item.get("id")
        if (
            not isinstance(job_id, int)
            or isinstance(job_id, bool)
            or job_id <= 0
            or job_id in seen_ids
        ):
            raise ValueError("DEC-290 job id is invalid or duplicated")
        seen_ids.add(job_id)
        if item.get("run_id") not in (None, run_id):
            raise ValueError("DEC-290 job run id mismatch")

        name = item.get("name")
        if not isinstance(name, str) or name not in allowed:
            raise ValueError(f"DEC-290 unexpected materialized job: {name!r}")
        if name in names:
            raise ValueError(f"DEC-290 duplicate materialized job name: {name}")
        names.append(name)

        if item.get("status") != "completed":
            raise ValueError("DEC-290 review requires terminal jobs")
        conclusion = item.get("conclusion")
        if not isinstance(conclusion, str) or not conclusion:
            raise ValueError("DEC-290 job conclusion must be terminal")
        if name == UNEXPANDED_MATRIX_JOB_NAME and conclusion != "skipped":
            raise ValueError(
                "DEC-290 unexpanded matrix placeholder must be skipped"
            )
        rows.append(item)

    if names.count(PREFLIGHT_JOB_NAME) != 1:
        raise ValueError("DEC-290 requires exactly one preflight job")

    if success:
        if len(rows) != EXPECTED_JOB_COUNT:
            raise ValueError("DEC-290 success requires exactly 20 jobs")
        if set(names) != expected:
            raise ValueError("DEC-290 success job inventory mismatch")
        if any(item.get("conclusion") != "success" for item in rows):
            raise ValueError("DEC-290 success requires every job to succeed")
    return rows, names


def _validate_artifacts(
    artifacts_payload: Mapping[str, object],
    *,
    code_commit: str,
    success: bool,
) -> tuple[list[Mapping[str, object]], list[str]]:
    raw = artifacts_payload.get("artifacts")
    if not isinstance(raw, list):
        raise ValueError("DEC-290 artifacts payload must contain artifacts list")

    expected = set(expected_artifact_names(code_commit=code_commit))
    rows: list[Mapping[str, object]] = []
    names: list[str] = []
    seen_ids: set[int] = set()
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-290 artifact row is malformed")
        artifact_id = item.get("id")
        if (
            not isinstance(artifact_id, int)
            or isinstance(artifact_id, bool)
            or artifact_id <= 0
            or artifact_id in seen_ids
        ):
            raise ValueError("DEC-290 artifact id is invalid or duplicated")
        seen_ids.add(artifact_id)

        name = item.get("name")
        if not isinstance(name, str) or name not in expected:
            raise ValueError(f"DEC-290 unexpected artifact: {name!r}")
        if name in names:
            raise ValueError(f"DEC-290 duplicate artifact name: {name}")
        names.append(name)
        if item.get("expired") is not False:
            raise ValueError("DEC-290 review requires non-expired artifacts")
        _validate_digest(
            item.get("digest"),
            field=f"DEC-290 artifact {name} digest",
        )
        rows.append(item)

    if success:
        if len(rows) != EXPECTED_ARTIFACT_COUNT:
            raise ValueError("DEC-290 success requires exactly 20 artifacts")
        if set(names) != expected:
            raise ValueError("DEC-290 success artifact inventory mismatch")
    return rows, names


def review_historical_result_terminal_shape(
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
    run_id, conclusion = _require_run_identity(
        run,
        expected_head_sha=expected_head_sha,
    )
    success = conclusion == "success"
    jobs, job_names = _validate_jobs(
        jobs_payload,
        run_id=run_id,
        success=success,
    )
    artifacts, artifact_names = _validate_artifacts(
        artifacts_payload,
        code_commit=expected_head_sha,
        success=success,
    )

    aggregate_artifact = f"phase8a-exp061-aggregate-{expected_head_sha}"
    aggregate_present = aggregate_artifact in artifact_names
    aggregate_job_rows = [
        item for item in jobs if item.get("name") == AGGREGATE_JOB_NAME
    ]
    aggregate_job_success = (
        len(aggregate_job_rows) == 1
        and aggregate_job_rows[0].get("conclusion") == "success"
    )

    if success and (not aggregate_present or not aggregate_job_success):
        raise ValueError(
            "DEC-290 success requires successful aggregate job and artifact"
        )

    return {
        "decision": EXP061_HISTORICAL_RESULT_REVIEW_DECISION,
        "version": EXP061_HISTORICAL_RESULT_REVIEW_VERSION,
        "run_id": run_id,
        "code_commit": expected_head_sha,
        "workflow_run_number": EXPECTED_WORKFLOW_RUN_NUMBER,
        "workflow_run_attempt": EXPECTED_WORKFLOW_RUN_ATTEMPT,
        "run_conclusion": conclusion,
        "terminal_classification": (
            "SUCCESS_SHAPE_PENDING_CONTENT_REVIEW"
            if success
            else "NON_SUCCESS_SLOT_CONSUMED_NO_RETRY"
        ),
        "historical_result_slot_consumed": True,
        "materialized_job_count": len(jobs),
        "materialized_job_names": job_names,
        "artifact_count": len(artifacts),
        "artifact_names": artifact_names,
        "aggregate_job_success": aggregate_job_success,
        "aggregate_artifact_present": aggregate_present,
        "cell_and_aggregate_content_review_required": success,
        "partial_evidence_review_required": not success,
        "historical_result_accepted": False,
        "pattern_hypotheses_accepted": False,
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
    "EXP061_HISTORICAL_RESULT_REVIEW_DECISION",
    "EXP061_HISTORICAL_RESULT_REVIEW_VERSION",
    "UNEXPANDED_MATRIX_JOB_NAME",
    "review_historical_result_terminal_shape",
]
