from __future__ import annotations

import unittest

from fmp.discovery.historical_result_review_contract import (
    MATRIX_TEMPLATE_JOB_NAME,
    classify_historical_terminal_result,
)
from fmp.discovery.run_contract import (
    AGGREGATE_JOB_NAME,
    PREFLIGHT_JOB_NAME,
    expected_artifact_names,
    expected_job_names,
)


HEAD = "a" * 40


def _run(
    *,
    conclusion: str = "success",
    status: str = "completed",
    run_number: int = 2,
    run_attempt: int = 1,
    head_sha: str = HEAD,
) -> dict[str, object]:
    return {
        "id": 40000000000,
        "name": "phase8a-exp061-discovery",
        "path": ".github/workflows/phase8a-exp061-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "run_number": run_number,
        "run_attempt": run_attempt,
        "status": status,
        "conclusion": conclusion,
    }


def _job(name: str, conclusion: str) -> dict[str, object]:
    return {
        "id": abs(hash((name, conclusion))) + 1,
        "name": name,
        "status": "completed",
        "conclusion": conclusion,
    }


def _artifact(index: int, name: str) -> dict[str, object]:
    return {
        "id": 50000000000 + index,
        "name": name,
        "expired": False,
    }


def _success_jobs() -> dict[str, object]:
    return {
        "jobs": [
            _job(name, "success")
            for name in expected_job_names()
        ]
    }


def _success_artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            _artifact(index, name)
            for index, name in enumerate(
                expected_artifact_names(code_commit=HEAD),
                start=1,
            )
        ]
    }


class Exp061HistoricalTerminalReviewContractTests(unittest.TestCase):
    def test_complete_success_requires_exact_twenty_jobs_and_artifacts(self) -> None:
        report = classify_historical_terminal_result(
            run=_run(),
            jobs_payload=_success_jobs(),
            artifacts_payload=_success_artifacts(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            report["stage"],
            "EXP061_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED",
        )
        self.assertTrue(report["historical_result_success_complete"])
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertEqual(report["materialized_job_count"], 20)
        self.assertEqual(report["artifact_count"], 20)
        self.assertFalse(
            report["github_unexpanded_matrix_placeholder_present"]
        )
        self.assertTrue(report["aggregate_result_content_review_required"])
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["rerun_authorized"])
        self.assertFalse(report["retry_authorized"])
        self.assertFalse(report["replacement_run_authorized"])

    def test_success_missing_job_or_artifact_fails_closed(self) -> None:
        jobs = _success_jobs()
        jobs["jobs"] = jobs["jobs"][:-1]
        with self.assertRaisesRegex(
            ValueError,
            "exact 20-job inventory",
        ):
            classify_historical_terminal_result(
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_success_artifacts(),
                expected_head_sha=HEAD,
            )

        artifacts = _success_artifacts()
        artifacts["artifacts"] = artifacts["artifacts"][:-1]
        with self.assertRaisesRegex(
            ValueError,
            "exact 20-artifact inventory",
        ):
            classify_historical_terminal_result(
                run=_run(),
                jobs_payload=_success_jobs(),
                artifacts_payload=artifacts,
                expected_head_sha=HEAD,
            )

    def test_early_terminal_failure_accepts_exact_skipped_matrix_template(self) -> None:
        jobs = {
            "jobs": [
                _job(PREFLIGHT_JOB_NAME, "failure"),
                _job(MATRIX_TEMPLATE_JOB_NAME, "skipped"),
                _job(AGGREGATE_JOB_NAME, "skipped"),
            ]
        }
        artifacts = {
            "artifacts": [
                _artifact(
                    1,
                    expected_artifact_names(code_commit=HEAD)[0],
                )
            ]
        }
        report = classify_historical_terminal_result(
            run=_run(conclusion="failure"),
            jobs_payload=jobs,
            artifacts_payload=artifacts,
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            report["stage"],
            "EXP061_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED",
        )
        self.assertFalse(report["historical_result_success_complete"])
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertTrue(
            report["github_unexpanded_matrix_placeholder_present"]
        )
        self.assertTrue(report["partial_evidence_may_be_preserved"])
        self.assertFalse(report["rerun_authorized"])
        self.assertFalse(report["retry_authorized"])
        self.assertFalse(report["replacement_run_authorized"])

    def test_partial_expanded_cell_failure_closes_slot(self) -> None:
        expected = list(expected_job_names())
        jobs = {
            "jobs": [
                _job(PREFLIGHT_JOB_NAME, "success"),
                _job(expected[1], "success"),
                _job(expected[2], "failure"),
                _job(AGGREGATE_JOB_NAME, "skipped"),
            ]
        }
        artifacts = {
            "artifacts": [
                _artifact(
                    1,
                    expected_artifact_names(code_commit=HEAD)[0],
                ),
                _artifact(
                    2,
                    expected_artifact_names(code_commit=HEAD)[1],
                ),
            ]
        }
        report = classify_historical_terminal_result(
            run=_run(conclusion="failure"),
            jobs_payload=jobs,
            artifacts_payload=artifacts,
            expected_head_sha=HEAD,
        )
        self.assertEqual(report["materialized_job_count"], 4)
        self.assertEqual(report["artifact_count"], 2)
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertFalse(report["aggregate_result_content_review_required"])

    def test_placeholder_cannot_mix_with_expanded_cells(self) -> None:
        jobs = {
            "jobs": [
                _job(PREFLIGHT_JOB_NAME, "failure"),
                _job(MATRIX_TEMPLATE_JOB_NAME, "skipped"),
                _job(expected_job_names()[1], "skipped"),
                _job(AGGREGATE_JOB_NAME, "skipped"),
            ]
        }
        with self.assertRaisesRegex(
            ValueError,
            "cannot mix matrix template placeholder",
        ):
            classify_historical_terminal_result(
                run=_run(conclusion="failure"),
                jobs_payload=jobs,
                artifacts_payload={"artifacts": []},
                expected_head_sha=HEAD,
            )

    def test_wrong_run_identity_or_nonterminal_run_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "run_number mismatch"):
            classify_historical_terminal_result(
                run=_run(run_number=3),
                jobs_payload=_success_jobs(),
                artifacts_payload=_success_artifacts(),
                expected_head_sha=HEAD,
            )

        with self.assertRaisesRegex(ValueError, "status mismatch"):
            classify_historical_terminal_result(
                run=_run(status="in_progress", conclusion=""),
                jobs_payload=_success_jobs(),
                artifacts_payload=_success_artifacts(),
                expected_head_sha=HEAD,
            )

        with self.assertRaisesRegex(ValueError, "head_sha mismatch"):
            classify_historical_terminal_result(
                run=_run(head_sha="b" * 40),
                jobs_payload=_success_jobs(),
                artifacts_payload=_success_artifacts(),
                expected_head_sha=HEAD,
            )

    def test_unexpected_job_or_artifact_is_rejected(self) -> None:
        jobs = _success_jobs()
        jobs["jobs"] = [
            *jobs["jobs"],
            _job("unexpected-job", "success"),
        ]
        with self.assertRaisesRegex(ValueError, "unexpected job names"):
            classify_historical_terminal_result(
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_success_artifacts(),
                expected_head_sha=HEAD,
            )

        artifacts = _success_artifacts()
        artifacts["artifacts"] = [
            *artifacts["artifacts"],
            _artifact(99, "unexpected-artifact"),
        ]
        with self.assertRaisesRegex(ValueError, "unexpected artifact name"):
            classify_historical_terminal_result(
                run=_run(),
                jobs_payload=_success_jobs(),
                artifacts_payload=artifacts,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
