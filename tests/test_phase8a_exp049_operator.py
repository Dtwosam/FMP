from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_regime_utility_operator import (
    DEC137_MERGED_COMMIT,
    REPOSITORY,
    REGIME_UTILITY_MODEL_WORKFLOW_FILE,
    REGIME_UTILITY_MODEL_WORKFLOW_NAME,
    REGIME_UTILITY_MODEL_WORKFLOW_PATH,
    build_regime_utility_operator_report,
    classify_regime_utility_model_run,
    regime_utility_operator_gate_metadata,
    dispatch_command_for_regime_utility_report,
    select_regime_utility_aggregate_artifact,
    select_regime_utility_manual_main_run,
    shell_join,
    regime_utility_artifact_download_endpoint,
    regime_utility_model_dispatch_command,
    regime_utility_model_run_artifacts_endpoint,
    regime_utility_model_run_endpoint,
    regime_utility_model_run_jobs_endpoint,
    regime_utility_model_runs_endpoint,
    validate_regime_utility_operator_checkout,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/phase8a_exp049_operator.py"
SHA = "a" * 40


def _run(
    *,
    status: str = "completed",
    conclusion: str | None = "success",
) -> dict[str, object]:
    return {
        "id": 123,
        "name": REGIME_UTILITY_MODEL_WORKFLOW_NAME,
        "path": REGIME_UTILITY_MODEL_WORKFLOW_PATH,
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


class Exp049RegimeUtilityOperatorTests(unittest.TestCase):
    def test_authorization_merge_identity_is_frozen(self) -> None:
        self.assertEqual(
            DEC137_MERGED_COMMIT,
            "33227b25cd1a888c3e0c7db3a50bd0cb61f5aad6",
        )

    def test_checkout_requires_clean_exact_main(self) -> None:
        report = validate_regime_utility_operator_checkout(
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
            validate_regime_utility_operator_checkout(
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
            validate_regime_utility_operator_checkout(
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
            validate_regime_utility_operator_checkout(
                branch="main",
                head_sha=SHA,
                origin_main_sha=SHA,
                porcelain_status=" M changed.py",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )

    def test_exact_workflow_endpoints_and_dispatch(self) -> None:
        self.assertEqual(
            regime_utility_model_dispatch_command(),
            (
                "gh",
                "workflow",
                "run",
                REGIME_UTILITY_MODEL_WORKFLOW_FILE,
                "--ref",
                "main",
                "-R",
                REPOSITORY,
            ),
        )
        self.assertEqual(
            shell_join(regime_utility_model_dispatch_command()),
            "gh workflow run phase8a-exp049-regime-utility-model-training.yml "
            "--ref main -R Dtwosam/FMP",
        )
        self.assertIn(
            "phase8a-exp049-regime-utility-model-training.yml/runs",
            regime_utility_model_runs_endpoint(),
        )
        self.assertIn(
            "branch=main",
            regime_utility_model_runs_endpoint(),
        )
        self.assertIn(
            "event=workflow_dispatch",
            regime_utility_model_runs_endpoint(),
        )
        self.assertEqual(
            regime_utility_model_run_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123",
        )
        self.assertEqual(
            regime_utility_model_run_jobs_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123/jobs?per_page=100",
        )
        self.assertEqual(
            regime_utility_model_run_artifacts_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123/"
            "artifacts?per_page=100",
        )
        self.assertEqual(
            regime_utility_artifact_download_endpoint(456),
            "repos/Dtwosam/FMP/actions/artifacts/456/zip",
        )

    def test_run_selection_forbids_second_manual_main_run(self) -> None:
        self.assertIsNone(
            select_regime_utility_manual_main_run(
                {"workflow_runs": []}
            )
        )
        selected = select_regime_utility_manual_main_run(
            {"workflow_runs": [_run()]}
        )
        self.assertEqual(selected["id"], 123)

        with self.assertRaisesRegex(
            ValueError,
            "multiple manual main runs",
        ):
            select_regime_utility_manual_main_run(
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
            select_regime_utility_manual_main_run(
                {
                    "workflow_runs": [
                        {**_run(), "name": "wrong"}
                    ]
                }
            )

    def test_run_classification_is_one_way(self) -> None:
        self.assertEqual(
            classify_regime_utility_model_run(None)["run_state"],
            "MISSING",
        )
        self.assertEqual(
            classify_regime_utility_model_run(
                _run(
                    status="in_progress",
                    conclusion=None,
                )
            )["run_state"],
            "IN_PROGRESS",
        )
        self.assertEqual(
            classify_regime_utility_model_run(
                _run(
                    status="completed",
                    conclusion="failure",
                )
            )["run_state"],
            "TERMINAL",
        )

    def test_missing_run_is_only_dispatchable_state(self) -> None:
        report = build_regime_utility_operator_report(
            checkout=_checkout(),
            run=None,
        )
        self.assertEqual(
            report["stage"],
            "REGIME_UTILITY_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            report["regime_utility_model_run_dispatch_authorized"]
        )
        self.assertTrue(
            report[
                "authoritative_regime_utility_model_result_execution_authorized"
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
            dispatch_command_for_regime_utility_report(report),
            regime_utility_model_dispatch_command(),
        )

        active = build_regime_utility_operator_report(
            checkout=_checkout(),
            run=_run(
                status="in_progress",
                conclusion=None,
            ),
        )
        self.assertEqual(
            active["stage"],
            "REGIME_UTILITY_MODEL_RUN_IN_PROGRESS",
        )
        self.assertIsNone(
            dispatch_command_for_regime_utility_report(active)
        )

        terminal = build_regime_utility_operator_report(
            checkout=_checkout(),
            run=_run(conclusion="failure"),
        )
        self.assertEqual(
            terminal["stage"],
            "REGIME_UTILITY_MODEL_TERMINAL_REVIEW_REQUIRED",
        )
        self.assertIsNone(
            dispatch_command_for_regime_utility_report(terminal)
        )

    def test_gate_metadata_matches_dec137_source_shape(self) -> None:
        gate = {
            "regime_utility_model_execution_gate_decision": "DEC-135",
            "regime_utility_model_execution_authorization_decision": "DEC-137",
            "dec132_merged_commit": "1" * 40,
            "dec133_merged_commit": "2" * 40,
            "dec134_merged_commit": "3" * 40,
            "dec135_merged_commit": "4" * 40,
            "dec136_merged_commit": "5" * 40,
            "dec135_workflow_blob_sha": "6" * 40,
            "dec135_cli_blob_sha": "7" * 40,
            "dec135_gate_blob_sha": "8" * 40,
            "dec136_review_blob_sha": "9" * 40,
            "regime_utility_workflow_blob_sha": "a" * 40,
            "regime_utility_cli_blob_sha": "b" * 40,
        }
        metadata = regime_utility_operator_gate_metadata(gate)
        self.assertEqual(
            metadata["dec136_merged_commit"],
            "5" * 40,
        )
        self.assertEqual(
            metadata["regime_utility_workflow_blob_sha"],
            "a" * 40,
        )
        self.assertNotIn("dec127_merged_commit", metadata)

        drifted = dict(gate)
        drifted.pop("dec136_merged_commit")
        with self.assertRaisesRegex(
            ValueError,
            "dec136_merged_commit",
        ):
            regime_utility_operator_gate_metadata(drifted)

    def test_public_cli_binds_utility_gate_metadata(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("regime_consensus", text)
        self.assertNotIn("EXP-048", text)
        self.assertIn(
            "regime_utility_operator_gate_metadata(gate)",
            text,
        )

    def test_dispatch_report_tamper_fails_closed(self) -> None:
        report = build_regime_utility_operator_report(
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
            dispatch_command_for_regime_utility_report(tampered)

        unlocked = dict(report)
        unlocked["promotion_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "promotion_authorized must remain false",
        ):
            dispatch_command_for_regime_utility_report(unlocked)

    def test_aggregate_artifact_selection_is_exact(self) -> None:
        expected = (
            f"exp049-regime-utility-model-result-evidence-{SHA}-"
            "from-feature-35867307338-outcome-35876715434"
        )
        selected = select_regime_utility_aggregate_artifact(
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
            select_regime_utility_aggregate_artifact(
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
            "dispatch_command_for_regime_utility_report(confirmed)",
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
