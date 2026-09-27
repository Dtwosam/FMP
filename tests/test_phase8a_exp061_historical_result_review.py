from __future__ import annotations

import copy
import unittest

from fmp.discovery.historical_result_review import (
    UNEXPANDED_MATRIX_JOB_NAME,
    review_historical_result_terminal_shape,
)
from fmp.discovery.run_contract import (
    AGGREGATE_JOB_NAME,
    PREFLIGHT_JOB_NAME,
    expected_artifact_names,
    expected_job_names,
)


HEAD = "a" * 40
RUN_ID = 40000000000


def _run(*, conclusion: str = "success", run_number: int = 2) -> dict[str, object]:
    return {
        "id": RUN_ID,
        "name": "phase8a-exp061-discovery",
        "path": ".github/workflows/phase8a-exp061-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": run_number,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": conclusion,
    }


def _success_jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": 50000000000 + index,
                "run_id": RUN_ID,
                "name": name,
                "status": "completed",
                "conclusion": "success",
            }
            for index, name in enumerate(expected_job_names())
        ]
    }


def _success_artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": 60000000000 + index,
                "name": name,
                "expired": False,
                "digest": "sha256:" + (f"{index + 1:064x}"[-64:]),
            }
            for index, name in enumerate(
                expected_artifact_names(code_commit=HEAD)
            )
        ]
    }


class Exp061HistoricalResultReviewTests(unittest.TestCase):
    def test_success_shape_requires_later_content_review(self) -> None:
        report = review_historical_result_terminal_shape(
            run=_run(),
            jobs_payload=_success_jobs(),
            artifacts_payload=_success_artifacts(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            report["terminal_classification"],
            "SUCCESS_SHAPE_PENDING_CONTENT_REVIEW",
        )
        self.assertEqual(report["materialized_job_count"], 20)
        self.assertEqual(report["artifact_count"], 20)
        self.assertTrue(report["aggregate_job_success"])
        self.assertTrue(report["aggregate_artifact_present"])
        self.assertTrue(report["cell_and_aggregate_content_review_required"])
        self.assertFalse(report["historical_result_accepted"])
        self.assertFalse(report["pattern_hypotheses_accepted"])
        self.assertTrue(report["historical_result_slot_consumed"])

    def test_non_success_shape_consumes_slot_without_retry(self) -> None:
        jobs = {
            "jobs": [
                {
                    "id": 1,
                    "run_id": RUN_ID,
                    "name": PREFLIGHT_JOB_NAME,
                    "status": "completed",
                    "conclusion": "failure",
                },
                {
                    "id": 2,
                    "run_id": RUN_ID,
                    "name": UNEXPANDED_MATRIX_JOB_NAME,
                    "status": "completed",
                    "conclusion": "skipped",
                },
                {
                    "id": 3,
                    "run_id": RUN_ID,
                    "name": AGGREGATE_JOB_NAME,
                    "status": "completed",
                    "conclusion": "skipped",
                },
            ]
        }
        artifacts = {
            "artifacts": [
                {
                    "id": 4,
                    "name": f"phase8a-exp061-preflight-{HEAD}",
                    "expired": False,
                    "digest": "sha256:" + "1" * 64,
                }
            ]
        }
        report = review_historical_result_terminal_shape(
            run=_run(conclusion="failure"),
            jobs_payload=jobs,
            artifacts_payload=artifacts,
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            report["terminal_classification"],
            "NON_SUCCESS_SLOT_CONSUMED_NO_RETRY",
        )
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertTrue(report["partial_evidence_review_required"])
        self.assertFalse(report["cell_and_aggregate_content_review_required"])
        self.assertFalse(report["rerun_authorized"])
        self.assertFalse(report["retry_authorized"])
        self.assertFalse(report["replacement_run_authorized"])

    def test_run_number_or_attempt_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "run_number mismatch"):
            review_historical_result_terminal_shape(
                run=_run(run_number=3),
                jobs_payload=_success_jobs(),
                artifacts_payload=_success_artifacts(),
                expected_head_sha=HEAD,
            )

        run = _run()
        run["run_attempt"] = 2
        with self.assertRaisesRegex(ValueError, "run_attempt mismatch"):
            review_historical_result_terminal_shape(
                run=run,
                jobs_payload=_success_jobs(),
                artifacts_payload=_success_artifacts(),
                expected_head_sha=HEAD,
            )

    def test_success_missing_job_or_artifact_fails_closed(self) -> None:
        jobs = _success_jobs()
        jobs["jobs"] = jobs["jobs"][:-1]
        with self.assertRaisesRegex(ValueError, "exactly 20 jobs"):
            review_historical_result_terminal_shape(
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_success_artifacts(),
                expected_head_sha=HEAD,
            )

        artifacts = _success_artifacts()
        artifacts["artifacts"] = artifacts["artifacts"][:-1]
        with self.assertRaisesRegex(ValueError, "exactly 20 artifacts"):
            review_historical_result_terminal_shape(
                run=_run(),
                jobs_payload=_success_jobs(),
                artifacts_payload=artifacts,
                expected_head_sha=HEAD,
            )

    def test_unexpected_artifact_is_rejected_even_on_failure(self) -> None:
        artifacts = {
            "artifacts": [
                {
                    "id": 10,
                    "name": "unexpected-artifact",
                    "expired": False,
                    "digest": "sha256:" + "2" * 64,
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "unexpected artifact"):
            review_historical_result_terminal_shape(
                run=_run(conclusion="failure"),
                jobs_payload={
                    "jobs": [
                        {
                            "id": 11,
                            "run_id": RUN_ID,
                            "name": PREFLIGHT_JOB_NAME,
                            "status": "completed",
                            "conclusion": "failure",
                        }
                    ]
                },
                artifacts_payload=artifacts,
                expected_head_sha=HEAD,
            )

    def test_unexpanded_matrix_placeholder_must_be_skipped(self) -> None:
        jobs = {
            "jobs": [
                {
                    "id": 20,
                    "run_id": RUN_ID,
                    "name": PREFLIGHT_JOB_NAME,
                    "status": "completed",
                    "conclusion": "failure",
                },
                {
                    "id": 21,
                    "run_id": RUN_ID,
                    "name": UNEXPANDED_MATRIX_JOB_NAME,
                    "status": "completed",
                    "conclusion": "failure",
                },
            ]
        }
        with self.assertRaisesRegex(
            ValueError,
            "unexpanded matrix placeholder must be skipped",
        ):
            review_historical_result_terminal_shape(
                run=_run(conclusion="failure"),
                jobs_payload=jobs,
                artifacts_payload={"artifacts": []},
                expected_head_sha=HEAD,
            )

    def test_all_downstream_authorities_remain_false(self) -> None:
        report = review_historical_result_terminal_shape(
            run=_run(),
            jobs_payload=_success_jobs(),
            artifacts_payload=_success_artifacts(),
            expected_head_sha=HEAD,
        )
        for field in (
            "historical_result_accepted",
            "pattern_hypotheses_accepted",
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
            self.assertFalse(report[field], field)


if __name__ == "__main__":
    unittest.main()
