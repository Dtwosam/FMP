from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.operator import (
    MODEL_WORKFLOW_NAME,
    dispatch_command_for_next_report,
    model_dispatch_command,
    model_run_artifacts_endpoint,
    model_run_jobs_endpoint,
    model_run_endpoint,
    model_runs_endpoint,
    select_model_result_artifact,
    shell_join,
    validate_model_run_for_result,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/phase8a_exp044_operator.py"
SHA = "a" * 40


class Exp044ModelOperatorTests(unittest.TestCase):
    def test_model_endpoints_and_dispatch_are_exact(self) -> None:
        self.assertIn(
            "phase8a-exp044-model-training.yml/runs",
            model_runs_endpoint(),
        )
        self.assertIn("branch=main", model_runs_endpoint())
        self.assertIn("event=workflow_dispatch", model_runs_endpoint())
        self.assertEqual(
            model_run_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123",
        )
        self.assertEqual(
            model_run_artifacts_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123/artifacts?per_page=100",
        )
        self.assertEqual(
            model_run_jobs_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123/jobs?per_page=100",
        )
        command = model_dispatch_command()
        self.assertEqual(
            shell_join(command),
            "gh workflow run phase8a-exp044-model-training.yml "
            "--ref main -R Dtwosam/FMP",
        )

    def test_model_run_validation_requires_exact_successful_manual_main_run(self) -> None:
        run = {
            "id": 123,
            "name": MODEL_WORKFLOW_NAME,
            "path": ".github/workflows/phase8a-exp044-model-training.yml",
            "event": "workflow_dispatch",
            "head_branch": "main",
            "status": "completed",
            "conclusion": "success",
            "head_sha": SHA,
        }
        result = validate_model_run_for_result(
            run,
            expected_run_id=123,
        )
        self.assertTrue(result["model_run_verified"])
        self.assertEqual(result["model_head_sha"], SHA)

        invalid = dict(run)
        invalid["conclusion"] = "failure"
        with self.assertRaisesRegex(ValueError, "did not succeed"):
            validate_model_run_for_result(
                invalid,
                expected_run_id=123,
            )

    def test_model_result_artifact_must_be_exact_and_nonexpired(self) -> None:
        expected = (
            f"exp044-model-result-evidence-{SHA}-"
            "from-feature-35867307338-outcome-35876715434"
        )
        selected = select_model_result_artifact(
            {
                "artifacts": [
                    {"id": 55, "name": expected, "expired": False},
                ]
            },
            model_head_sha=SHA,
        )
        self.assertEqual(selected["model_result_artifact_id"], 55)
        self.assertEqual(selected["model_result_artifact_name"], expected)

        with self.assertRaisesRegex(
            ValueError,
            "exactly one non-expired",
        ):
            select_model_result_artifact(
                {
                    "artifacts": [
                        {"id": 55, "name": expected, "expired": True},
                    ]
                },
                model_head_sha=SHA,
            )

    def test_model_dispatch_stage_is_the_only_model_dispatchable_state(self) -> None:
        command = model_dispatch_command()
        report = {
            "read_only": True,
            "stage": "MODEL_RUN_DISPATCH_REQUIRED",
            "dispatch_command": shell_join(command),
            "model_protocol_result_authorized": True,
            "model_fit_authorized": True,
            "model_run_dispatch_authorized": True,
            "authoritative_model_result_execution_authorized": True,
            "promotion_authorized": False,
            "trading_authorized": False,
        }
        self.assertEqual(
            dispatch_command_for_next_report(report),
            command,
        )

        for stage in (
            "MODEL_RUN_IN_PROGRESS",
            "MODEL_RUN_REVIEW_REQUIRED",
            "MODEL_RESULT_REVIEW_REQUIRED",
        ):
            with self.subTest(stage=stage):
                self.assertIsNone(
                    dispatch_command_for_next_report(
                        {
                            "read_only": True,
                            "stage": stage,
                            "model_protocol_result_authorized": False,
                            "model_fit_authorized": False,
                            "promotion_authorized": False,
                            "trading_authorized": False,
                        }
                    )
                )

    def test_operator_source_closes_v1_after_reviewed_failure(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("MODEL_RUN_EXECUTION_CLOSED", text)
        self.assertIn("MODEL_RUN_AUTHORIZATION_CLOSED", text)
        self.assertIn("MODEL_RUN_FAILURE_REVIEWED", text)
        self.assertIn("REVIEWED_FAILED_MODEL_RUN_ID", text)
        self.assertIn("model_run_jobs_endpoint", text)
        self.assertIn("validate_reviewed_failed_model_run", text)
        self.assertIn(
            "Do not rerun or replace run ",
            text,
        )
        self.assertIn(
            "35891605645. Any continued model research requires a ",
            text,
        )
        self.assertNotIn(
            'stage="MODEL_RUN_DISPATCH_REQUIRED"',
            text,
        )


if __name__ == "__main__":
    unittest.main()
