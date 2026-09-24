from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_regime_consensus_operator import (
    REPOSITORY,
    REGIME_CONSENSUS_MODEL_WORKFLOW_FILE,
    REGIME_CONSENSUS_MODEL_WORKFLOW_NAME,
    REGIME_CONSENSUS_MODEL_WORKFLOW_PATH,
    build_regime_consensus_operator_report,
    classify_regime_consensus_model_run,
    regime_consensus_operator_gate_metadata,
    dispatch_command_for_regime_consensus_report,
    select_regime_consensus_aggregate_artifact,
    select_regime_consensus_manual_main_run,
    shell_join,
    regime_consensus_artifact_download_endpoint,
    regime_consensus_model_dispatch_command,
    regime_consensus_model_run_artifacts_endpoint,
    regime_consensus_model_run_endpoint,
    regime_consensus_model_run_jobs_endpoint,
    regime_consensus_model_runs_endpoint,
    validate_regime_consensus_operator_checkout,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/phase8a_exp048_operator.py"
SHA = "a" * 40


def _run(
    *,
    status: str = "completed",
    conclusion: str | None = "success",
) -> dict[str, object]:
    return {
        "id": 123,
        "name": REGIME_CONSENSUS_MODEL_WORKFLOW_NAME,
        "path": REGIME_CONSENSUS_MODEL_WORKFLOW_PATH,
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


class Exp047RegimeConsensusOperatorTests(unittest.TestCase):
    def test_checkout_requires_clean_exact_main(self) -> None:
        report = validate_regime_consensus_operator_checkout(
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
            validate_regime_consensus_operator_checkout(
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
            validate_regime_consensus_operator_checkout(
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
            validate_regime_consensus_operator_checkout(
                branch="main",
                head_sha=SHA,
                origin_main_sha=SHA,
                porcelain_status=" M changed.py",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )

    def test_exact_workflow_endpoints_and_dispatch(self) -> None:
        self.assertEqual(
            regime_consensus_model_dispatch_command(),
            (
                "gh",
                "workflow",
                "run",
                REGIME_CONSENSUS_MODEL_WORKFLOW_FILE,
                "--ref",
                "main",
                "-R",
                REPOSITORY,
            ),
        )
        self.assertEqual(
            shell_join(regime_consensus_model_dispatch_command()),
            "gh workflow run phase8a-exp048-regime-consensus-model-training.yml "
            "--ref main -R Dtwosam/FMP",
        )
        self.assertIn(
            "phase8a-exp048-regime-consensus-model-training.yml/runs",
            regime_consensus_model_runs_endpoint(),
        )
        self.assertIn(
            "branch=main",
            regime_consensus_model_runs_endpoint(),
        )
        self.assertIn(
            "event=workflow_dispatch",
            regime_consensus_model_runs_endpoint(),
        )
        self.assertEqual(
            regime_consensus_model_run_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123",
        )
        self.assertEqual(
            regime_consensus_model_run_jobs_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123/jobs?per_page=100",
        )
        self.assertEqual(
            regime_consensus_model_run_artifacts_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123/"
            "artifacts?per_page=100",
        )
        self.assertEqual(
            regime_consensus_artifact_download_endpoint(456),
            "repos/Dtwosam/FMP/actions/artifacts/456/zip",
        )

    def test_run_selection_forbids_second_manual_main_run(self) -> None:
        self.assertIsNone(
            select_regime_consensus_manual_main_run(
                {"workflow_runs": []}
            )
        )
        selected = select_regime_consensus_manual_main_run(
            {"workflow_runs": [_run()]}
        )
        self.assertEqual(selected["id"], 123)

        with self.assertRaisesRegex(
            ValueError,
            "multiple manual main runs",
        ):
            select_regime_consensus_manual_main_run(
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
            select_regime_consensus_manual_main_run(
                {
                    "workflow_runs": [
                        {**_run(), "name": "wrong"}
                    ]
                }
            )

    def test_run_classification_is_one_way(self) -> None:
        self.assertEqual(
            classify_regime_consensus_model_run(None)["run_state"],
            "MISSING",
        )
        self.assertEqual(
            classify_regime_consensus_model_run(
                _run(
                    status="in_progress",
                    conclusion=None,
                )
            )["run_state"],
            "IN_PROGRESS",
        )
        self.assertEqual(
            classify_regime_consensus_model_run(
                _run(
                    status="completed",
                    conclusion="failure",
                )
            )["run_state"],
            "TERMINAL",
        )

    def test_missing_run_is_only_dispatchable_state(self) -> None:
        report = build_regime_consensus_operator_report(
            checkout=_checkout(),
            run=None,
        )
        self.assertEqual(
            report["stage"],
            "REGIME_CONSENSUS_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            report["regime_consensus_model_run_dispatch_authorized"]
        )
        self.assertTrue(
            report[
                "authoritative_regime_consensus_model_result_execution_authorized"
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
            dispatch_command_for_regime_consensus_report(report),
            regime_consensus_model_dispatch_command(),
        )

        active = build_regime_consensus_operator_report(
            checkout=_checkout(),
            run=_run(
                status="in_progress",
                conclusion=None,
            ),
        )
        self.assertEqual(
            active["stage"],
            "REGIME_CONSENSUS_MODEL_RUN_IN_PROGRESS",
        )
        self.assertIsNone(
            dispatch_command_for_regime_consensus_report(active)
        )

        terminal = build_regime_consensus_operator_report(
            checkout=_checkout(),
            run=_run(conclusion="failure"),
        )
        self.assertEqual(
            terminal["stage"],
            "REGIME_CONSENSUS_MODEL_TERMINAL_REVIEW_REQUIRED",
        )
        self.assertIsNone(
            dispatch_command_for_regime_consensus_report(terminal)
        )

    def test_gate_metadata_matches_dec118_source_shape(self) -> None:
        gate = {
            "regime_consensus_model_execution_gate_decision": "DEC-116",
            "regime_consensus_model_execution_authorization_decision": "DEC-128",
            "dec123_merged_commit": "1" * 40,
            "dec124_merged_commit": "2" * 40,
            "dec125_merged_commit": "3" * 40,
            "dec126_merged_commit": "4" * 40,
            "dec127_merged_commit": "5" * 40,
            "dec126_workflow_blob_sha": "6" * 40,
            "dec126_cli_blob_sha": "7" * 40,
            "dec126_gate_blob_sha": "8" * 40,
            "dec127_review_blob_sha": "9" * 40,
            "regime_consensus_workflow_blob_sha": "a" * 40,
            "regime_consensus_cli_blob_sha": "b" * 40,
        }
        metadata = regime_consensus_operator_gate_metadata(gate)
        self.assertEqual(
            metadata["dec127_merged_commit"],
            "5" * 40,
        )
        self.assertEqual(
            metadata["regime_consensus_workflow_blob_sha"],
            "a" * 40,
        )
        self.assertNotIn("dec107_merged_commit", metadata)

        drifted = dict(gate)
        drifted.pop("dec127_merged_commit")
        with self.assertRaisesRegex(
            ValueError,
            "dec127_merged_commit",
        ):
            regime_consensus_operator_gate_metadata(drifted)

    def test_public_cli_has_no_stale_dec107_gate_key(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("dec107_merged_commit", text)
        self.assertIn(
            "regime_consensus_operator_gate_metadata(gate)",
            text,
        )

    def test_dispatch_report_tamper_fails_closed(self) -> None:
        report = build_regime_consensus_operator_report(
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
            dispatch_command_for_regime_consensus_report(tampered)

        unlocked = dict(report)
        unlocked["promotion_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "promotion_authorized must remain false",
        ):
            dispatch_command_for_regime_consensus_report(unlocked)

    def test_aggregate_artifact_selection_is_exact(self) -> None:
        expected = (
            f"exp048-regime-consensus-model-result-evidence-{SHA}-"
            "from-feature-35867307338-outcome-35876715434"
        )
        selected = select_regime_consensus_aggregate_artifact(
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
            select_regime_consensus_aggregate_artifact(
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
            "dispatch_command_for_regime_consensus_report(confirmed)",
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
