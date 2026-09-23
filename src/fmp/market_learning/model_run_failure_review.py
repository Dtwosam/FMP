from __future__ import annotations

from typing import Mapping


MODEL_RUN_FAILURE_REVIEW_DECISION = "DEC-094"

REVIEWED_FAILED_MODEL_RUN_ID = 35891605645
REVIEWED_FAILED_MODEL_HEAD_SHA = "e97fa03d0e94fd505d0f926eb730e01a41947880"
REVIEWED_FAILED_MODEL_RUN_ATTEMPT = 1

AUTHORIZATION_PREFLIGHT_JOB_ID = 107285171765
AGGREGATE_MODEL_EVIDENCE_JOB_ID = 107292746560

UPLOAD_FAILURE_JOBS: Mapping[int, tuple[str, str]] = {
    107285328769: ("EURUSD", "5m"),
    107285328904: ("EURUSD", "1h"),
    107285328635: ("GBPUSD", "15m"),
    107285328632: ("GBPUSD", "1h"),
    107285329110: ("USDJPY", "1h"),
}

LOGISTIC_NONCONVERGENCE_JOBS: Mapping[int, tuple[str, str]] = {
    107285328653: ("EURUSD", "15m"),
    107285328704: ("GBPUSD", "5m"),
    107285328835: ("USDJPY", "5m"),
    107285328648: ("USDJPY", "15m"),
}

EXPECTED_MATRIX_JOB_IDS = frozenset(
    {
        *UPLOAD_FAILURE_JOBS,
        *LOGISTIC_NONCONVERGENCE_JOBS,
    }
)


def validate_reviewed_failed_model_run(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
) -> dict[str, object]:
    if run.get("id") != REVIEWED_FAILED_MODEL_RUN_ID:
        raise ValueError("reviewed EXP-044 model run id mismatch")
    if run.get("name") != "phase8a-exp044-model-training":
        raise ValueError("reviewed EXP-044 model run name mismatch")
    if run.get("path") != ".github/workflows/phase8a-exp044-model-training.yml":
        raise ValueError("reviewed EXP-044 model run path mismatch")
    if run.get("event") != "workflow_dispatch":
        raise ValueError("reviewed EXP-044 model run event mismatch")
    if run.get("head_branch") != "main":
        raise ValueError("reviewed EXP-044 model run branch mismatch")
    if run.get("head_sha") != REVIEWED_FAILED_MODEL_HEAD_SHA:
        raise ValueError("reviewed EXP-044 model run head SHA mismatch")
    if run.get("run_attempt") != REVIEWED_FAILED_MODEL_RUN_ATTEMPT:
        raise ValueError("reviewed EXP-044 model run attempt mismatch")
    if run.get("status") != "completed":
        raise ValueError("reviewed EXP-044 model run is not completed")
    if run.get("conclusion") != "failure":
        raise ValueError("reviewed EXP-044 model run must remain failed")

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError("reviewed EXP-044 model jobs payload is malformed")
    indexed: dict[int, Mapping[str, object]] = {}
    for raw in jobs:
        if not isinstance(raw, Mapping):
            raise ValueError("reviewed EXP-044 model job row is malformed")
        job_id = raw.get("id")
        if not isinstance(job_id, int) or isinstance(job_id, bool):
            raise ValueError("reviewed EXP-044 model job id is malformed")
        if job_id in indexed:
            raise ValueError("duplicate reviewed EXP-044 model job id")
        indexed[job_id] = raw

    expected_ids = {
        AUTHORIZATION_PREFLIGHT_JOB_ID,
        AGGREGATE_MODEL_EVIDENCE_JOB_ID,
        *EXPECTED_MATRIX_JOB_IDS,
    }
    if set(indexed) != expected_ids:
        raise ValueError("reviewed EXP-044 model job inventory mismatch")

    preflight = indexed[AUTHORIZATION_PREFLIGHT_JOB_ID]
    if (
        preflight.get("status") != "completed"
        or preflight.get("conclusion") != "success"
    ):
        raise ValueError("reviewed EXP-044 authorization preflight mismatch")

    aggregate = indexed[AGGREGATE_MODEL_EVIDENCE_JOB_ID]
    if (
        aggregate.get("status") != "completed"
        or aggregate.get("conclusion") != "skipped"
    ):
        raise ValueError("reviewed EXP-044 aggregate job mismatch")

    def failed_step(job: Mapping[str, object]) -> str:
        steps = job.get("steps")
        if not isinstance(steps, list):
            raise ValueError("reviewed EXP-044 model job steps are malformed")
        failed = [
            step
            for step in steps
            if isinstance(step, Mapping)
            and step.get("conclusion") == "failure"
        ]
        if len(failed) != 1:
            raise ValueError(
                "reviewed EXP-044 model job must have exactly one failed step"
            )
        name = failed[0].get("name")
        if not isinstance(name, str):
            raise ValueError("reviewed EXP-044 failed-step name is malformed")
        return name

    for job_id in UPLOAD_FAILURE_JOBS:
        job = indexed[job_id]
        if (
            job.get("status") != "completed"
            or job.get("conclusion") != "failure"
        ):
            raise ValueError("reviewed EXP-044 upload-failure job mismatch")
        if failed_step(job) != "Upload pair/timeframe model-cell evidence":
            raise ValueError(
                "reviewed EXP-044 upload-failure step identity mismatch"
            )

    for job_id in LOGISTIC_NONCONVERGENCE_JOBS:
        job = indexed[job_id]
        if (
            job.get("status") != "completed"
            or job.get("conclusion") != "failure"
        ):
            raise ValueError(
                "reviewed EXP-044 convergence-failure job mismatch"
            )
        if failed_step(job) != "Run exact 60m and 240m model cells":
            raise ValueError(
                "reviewed EXP-044 convergence-failure step identity mismatch"
            )

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("reviewed EXP-044 artifact listing is malformed")
    if artifacts:
        raise ValueError("reviewed EXP-044 failed run must have zero artifacts")
    total_count = artifacts_payload.get("total_count")
    if total_count not in (None, 0):
        raise ValueError("reviewed EXP-044 failed run artifact count mismatch")

    return {
        "model_run_failure_reviewed": True,
        "reviewed_failed_model_run_id": REVIEWED_FAILED_MODEL_RUN_ID,
        "reviewed_failed_model_head_sha": REVIEWED_FAILED_MODEL_HEAD_SHA,
        "reviewed_failed_model_run_attempt": REVIEWED_FAILED_MODEL_RUN_ATTEMPT,
        "successful_computation_upload_failure_count": len(
            UPLOAD_FAILURE_JOBS
        ),
        "logistic_nonconvergence_job_count": len(
            LOGISTIC_NONCONVERGENCE_JOBS
        ),
        "aggregate_model_evidence_skipped": True,
        "persisted_model_artifact_count": 0,
        "replacement_model_run_authorized": False,
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


__all__ = [
    "AGGREGATE_MODEL_EVIDENCE_JOB_ID",
    "AUTHORIZATION_PREFLIGHT_JOB_ID",
    "EXPECTED_MATRIX_JOB_IDS",
    "LOGISTIC_NONCONVERGENCE_JOBS",
    "MODEL_RUN_FAILURE_REVIEW_DECISION",
    "REVIEWED_FAILED_MODEL_HEAD_SHA",
    "REVIEWED_FAILED_MODEL_RUN_ATTEMPT",
    "REVIEWED_FAILED_MODEL_RUN_ID",
    "UPLOAD_FAILURE_JOBS",
    "validate_reviewed_failed_model_run",
]
