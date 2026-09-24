from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_density_operator import (
    REPOSITORY,
    DENSITY_MODEL_WORKFLOW_FILE,
    DENSITY_MODEL_WORKFLOW_NAME,
    DENSITY_MODEL_WORKFLOW_PATH,
    build_density_operator_report,
    classify_density_model_run,
    dispatch_command_for_density_report,
    select_density_aggregate_artifact,
    select_density_manual_main_run,
    shell_join,
    density_artifact_download_endpoint,
    density_model_dispatch_command,
    density_model_run_artifacts_endpoint,
    density_model_run_endpoint,
    density_model_run_jobs_endpoint,
    density_model_runs_endpoint,
    validate_density_operator_checkout,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/phase8a_exp047_operator.py"
SHA = "a" * 40


def _run(
    *,
    status: str = "completed",
    conclusion: str | None = "success",
) -> dict[str, object]:
    return {
        "id": 123,
        "name": DENSITY_MODEL_WORKFLOW_NAME,
        "path": DENSITY_MODEL_WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": SHA,
        "status": status,
        "conclusion": conclusion,
    }


def _checkout() -> dict[str, object]:
    return {
        "repository": REPOSITORY,
        "branch": "main",
        "head_sha": SHA,
        "clean_worktree": True,
        "origin_verified": True,
    }


class Exp047DensityOperatorTests(unittest.TestCase):
    def test_checkout_requires_clean_exact_main(self) -> None:
        report = validate_density_operator_checkout(
            branch="main",
            head_sha=SHA,
            origin_main_sha=SHA,
            porcelain_status="",
            origin_url="https://github.com/Dtwosam/FMP.git",
        )
        self.assertEqual(report["head_sha"], SHA)
        self.assertTrue(report["clean_worktree"])

        with self.assertRaisesRegex(
            ValueError,
            "local main branch",
        ):
            validate_density_operator_checkout(
                branch="feature",
                head_sha=SHA,
                origin_main_sha=SHA,
                porcelain_status="",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )

        with self.assertRaisesRegex(
            ValueError,
            "exactly match fetched origin/main",
        ):
            validate_density_operator_checkout(
                branch="main",
                head_sha=SHA,
                origin_main_sha="b" * 40,
                porcelain_status="",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )

        with self.assertRaisesRegex(
            ValueError,
            "clean working tree",
        ):
            validate_density_operator_checkout(
                branch="main",
                head_sha=SHA,
                origin_main_sha=SHA,
                porcelain_status=" M changed.py",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )

    def test_exact_workflow_endpoints_and_dispatch(self) -> None:
        self.assertEqual(
            density_model_dispatch_command(),
            (
                "gh",
                "workflow",
                "run",
                DENSITY_MODEL_WORKFLOW_FILE,
                "--ref",
                "main",
                "-R",
                REPOSITORY,
            ),
        )
        self.assertEqual(
            shell_join(density_model_dispatch_command()),
            "gh workflow run phase8a-exp047-density-model-training.yml "
            "--ref main -R Dtwosam/FMP",
        )
        self.assertIn(
            "phase8a-exp047-density-model-training.yml/runs",
            density_model_runs_endpoint(),
        )
        self.assertIn(
            "branch=main",
            density_model_runs_endpoint(),
        )
        self.assertIn(
            "event=workflow_dispatch",
            density_model_runs_endpoint(),
        )
        self.assertEqual(
            density_model_run_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123",
        )
        self.assertEqual(
            density_model_run_jobs_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123/jobs?per_page=100",
        )
        self.assertEqual(
            density_model_run_artifacts_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123/"
            "artifacts?per_page=100",
        )
        self.assertEqual(
            density_artifact_download_endpoint(456),
            "repos/Dtwosam/FMP/actions/artifacts/456/zip",
        )

    def test_run_selection_forbids_second_manual_main_run(self) -> None:
        self.assertIsNone(
            select_density_manual_main_run(
                {"workflow_runs": []}
            )
        )
        selected = select_density_manual_main_run(
            {"workflow_runs": [_run()]}
        )
        self.assertEqual(selected["id"], 123)

        with self.assertRaisesRegex(
            ValueError,
            "multiple manual main runs",
        ):
            select_density_manual_main_run(
                {
                    "workflow_runs": [
                        _run(),
                        {**_run(), "id": 124},
                    ]
                }
            )

        with self.assertRaisesRegex(
            ValueError,
            "name mismatch",
        ):
            select_density_manual_main_run(
                {
                    "workflow_runs": [
                        {**_run(), "name": "wrong"}
                    ]
                }
            )

    def test_run_classification_is_one_way(self) -> None:
        self.assertEqual(
            classify_density_model_run(None)["run_state"],
            "MISSING",
        )
        self.assertEqual(
            classify_density_model_run(
                _run(
                    status="in_progress",
                    conclusion=None,
                )
            )["run_state"],
            "IN_PROGRESS",
        )
        self.assertEqual(
            classify_density_model_run(
                _run(
                    status="completed",
                    conclusion="failure",
                )
            )["run_state"],
            "TERMINAL",
        )

    def test_missing_run_is_only_dispatchable_state(self) -> None:
        report = build_density_operator_report(
            checkout=_checkout(),
            run=None,
        )
        self.assertEqual(
            report["stage"],
            "DENSITY_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            report["density_model_run_dispatch_authorized"]
        )
        self.assertTrue(
            report[
                "authoritative_density_model_result_execution_authorized"
            ]
        )
        self.assertTrue(
            report["model_protocol_result_authorized"]
        )
        self.assertTrue(report["model_fit_authorized"])
        self.assertFalse(
            report["replacement_model_run_authorized"]
        )
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["trading_authorized"])
        self.assertEqual(
            dispatch_command_for_density_report(report),
            density_model_dispatch_command(),
        )

        active = build_density_operator_report(
            checkout=_checkout(),
            run=_run(
                status="in_progress",
                conclusion=None,
            ),
        )
        self.assertEqual(
            active["stage"],
            "DENSITY_MODEL_RUN_IN_PROGRESS",
        )
        self.assertIsNone(
            dispatch_command_for_density_report(active)
        )

        terminal = build_density_operator_report(
            checkout=_checkout(),
            run=_run(conclusion="failure"),
        )
        self.assertEqual(
            terminal["stage"],
            "DENSITY_MODEL_TERMINAL_REVIEW_REQUIRED",
        )
        self.assertIsNone(
            dispatch_command_for_density_report(terminal)
        )

    def test_dispatch_report_tamper_fails_closed(self) -> None:
        report = build_density_operator_report(
            checkout=_checkout(),
            run=None,
        )
        tampered = dict(report)
        tampered["dispatch_command"] = (
            "gh workflow run wrong.yml"
        )
        with self.assertRaisesRegex(
            ValueError,
            "does not match frozen workflow",
        ):
            dispatch_command_for_density_report(tampered)

        unlocked = dict(report)
        unlocked["promotion_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "promotion_authorized must remain false",
        ):
            dispatch_command_for_density_report(unlocked)

    def test_aggregate_artifact_selection_is_exact(self) -> None:
        expected = (
            f"exp047-density-model-result-evidence-{SHA}-"
            "from-feature-35867307338-outcome-35876715434"
        )
        selected = select_density_aggregate_artifact(
            {
                "artifacts": [
                    {
                        "id": 55,
                        "name": expected,
                        "expired": False,
                    }
                ]
            },
            head_sha=SHA,
        )
        self.assertEqual(selected["artifact_id"], 55)
        self.assertEqual(
            selected["artifact_name"],
            expected,
        )

        with self.assertRaisesRegex(
            ValueError,
            "exactly one non-expired",
        ):
            select_density_aggregate_artifact(
                {
                    "artifacts": [
                        {
                            "id": 55,
                            "name": expected,
                            "expired": True,
                        }
                    ]
                },
                head_sha=SHA,
            )

    def test_operator_cli_double_checks_before_execute(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            "confirmed = _read_next_via_public_cli()",
            text,
        )
        self.assertIn(
            "if confirmed != plan:",
            text,
        )
        self.assertIn(
            "dispatch_command_for_density_report(confirmed)",
            text,
        )
        self.assertIn(
            "_run(command, capture=False)",
            text,
        )
        self.assertNotIn(
            "workflow_dispatch:",
            text,
        )
        self.assertNotIn(
            'add_parser("rerun"',
            text,
        )


if __name__ == "__main__":
    unittest.main()
