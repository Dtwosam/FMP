from __future__ import annotations

import unittest

from fmp.market_learning.model_run_failure_review import (
    AGGREGATE_MODEL_EVIDENCE_JOB_ID,
    AUTHORIZATION_PREFLIGHT_JOB_ID,
    LOGISTIC_NONCONVERGENCE_JOBS,
    MODEL_RUN_FAILURE_REVIEW_DECISION,
    REVIEWED_FAILED_MODEL_HEAD_SHA,
    REVIEWED_FAILED_MODEL_RUN_ATTEMPT,
    REVIEWED_FAILED_MODEL_RUN_ID,
    UPLOAD_FAILURE_JOBS,
    validate_reviewed_failed_model_run,
)


def _run() -> dict[str, object]:
    return {
        "id": REVIEWED_FAILED_MODEL_RUN_ID,
        "name": "phase8a-exp044-model-training",
        "path": ".github/workflows/phase8a-exp044-model-training.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": REVIEWED_FAILED_MODEL_HEAD_SHA,
        "run_attempt": REVIEWED_FAILED_MODEL_RUN_ATTEMPT,
        "status": "completed",
        "conclusion": "failure",
    }


def _job(
    job_id: int,
    *,
    conclusion: str,
    failed_step: str | None = None,
) -> dict[str, object]:
    steps: list[dict[str, object]] = [
        {
            "name": "Set up job",
            "status": "completed",
            "conclusion": "success",
        }
    ]
    if failed_step is not None:
        steps.append(
            {
                "name": failed_step,
                "status": "completed",
                "conclusion": "failure",
            }
        )
    return {
        "id": job_id,
        "status": "completed",
        "conclusion": conclusion,
        "steps": steps,
    }


def _jobs() -> dict[str, object]:
    rows: list[dict[str, object]] = [
        _job(
            AUTHORIZATION_PREFLIGHT_JOB_ID,
            conclusion="success",
        ),
        _job(
            AGGREGATE_MODEL_EVIDENCE_JOB_ID,
            conclusion="skipped",
        ),
    ]
    rows.extend(
        _job(
            job_id,
            conclusion="failure",
            failed_step=(
                "Upload pair/timeframe model-cell evidence"
            ),
        )
        for job_id in UPLOAD_FAILURE_JOBS
    )
    rows.extend(
        _job(
            job_id,
            conclusion="failure",
            failed_step="Run exact 60m and 240m model cells",
        )
        for job_id in LOGISTIC_NONCONVERGENCE_JOBS
    )
    return {"jobs": rows}


class Exp044ModelRunFailureReviewTests(unittest.TestCase):
    def test_exact_failed_run_is_reviewed_and_all_authorizations_close(self) -> None:
        result = validate_reviewed_failed_model_run(
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload={
                "total_count": 0,
                "artifacts": [],
            },
        )
        self.assertEqual(
            MODEL_RUN_FAILURE_REVIEW_DECISION,
            "DEC-094",
        )
        self.assertIs(result["model_run_failure_reviewed"], True)
        self.assertEqual(
            result["reviewed_failed_model_run_id"],
            REVIEWED_FAILED_MODEL_RUN_ID,
        )
        self.assertEqual(
            result[
                "successful_computation_upload_failure_count"
            ],
            5,
        )
        self.assertEqual(
            result["logistic_nonconvergence_job_count"],
            4,
        )
        self.assertEqual(
            result["persisted_model_artifact_count"],
            0,
        )
        self.assertIs(
            result["replacement_model_run_authorized"],
            False,
        )
        for field in (
            "model_protocol_result_authorized",
            "model_fit_authorized",
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertIs(result[field], False)

    def test_reviewed_run_identity_drift_fails_closed(self) -> None:
        run = _run()
        run["id"] = REVIEWED_FAILED_MODEL_RUN_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "run id mismatch",
        ):
            validate_reviewed_failed_model_run(
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload={
                    "total_count": 0,
                    "artifacts": [],
                },
            )

    def test_failure_class_drift_fails_closed(self) -> None:
        payload = _jobs()
        jobs = payload["jobs"]
        assert isinstance(jobs, list)
        target_id = next(iter(LOGISTIC_NONCONVERGENCE_JOBS))
        target = next(
            row
            for row in jobs
            if isinstance(row, dict)
            and row.get("id") == target_id
        )
        steps = target["steps"]
        assert isinstance(steps, list)
        failed = next(
            step
            for step in steps
            if isinstance(step, dict)
            and step.get("conclusion") == "failure"
        )
        failed["name"] = "Upload pair/timeframe model-cell evidence"

        with self.assertRaisesRegex(
            ValueError,
            "convergence-failure step identity mismatch",
        ):
            validate_reviewed_failed_model_run(
                run=_run(),
                jobs_payload=payload,
                artifacts_payload={
                    "total_count": 0,
                    "artifacts": [],
                },
            )

    def test_any_persisted_artifact_fails_review_identity(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "must have zero artifacts",
        ):
            validate_reviewed_failed_model_run(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload={
                    "total_count": 1,
                    "artifacts": [
                        {
                            "id": 1,
                            "name": "unexpected",
                            "expired": False,
                        }
                    ],
                },
            )


if __name__ == "__main__":
    unittest.main()
