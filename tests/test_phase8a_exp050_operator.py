from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_temporal_jackknife_utility_operator import (
    DEC146_MERGED_COMMIT,
    REPOSITORY,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_FILE,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_NAME,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_PATH,
    build_temporal_jackknife_utility_operator_report,
    classify_temporal_jackknife_utility_model_run,
    temporal_jackknife_utility_operator_gate_metadata,
    dispatch_command_for_temporal_jackknife_utility_report,
    select_temporal_jackknife_utility_aggregate_artifact,
    select_temporal_jackknife_utility_manual_main_run,
    shell_join,
    temporal_jackknife_utility_artifact_download_endpoint,
    temporal_jackknife_utility_model_dispatch_command,
    temporal_jackknife_utility_model_run_artifacts_endpoint,
    temporal_jackknife_utility_model_run_endpoint,
    temporal_jackknife_utility_model_run_jobs_endpoint,
    temporal_jackknife_utility_model_runs_endpoint,
    validate_temporal_jackknife_utility_operator_checkout,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/phase8a_exp050_operator.py"
SHA = "a" * 40


def _run(
    *,
    status: str = "completed",
    conclusion: str | None = "success",
) -> dict[str, object]:
    return {
        "id": 123,
        "name": TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_NAME,
        "path": TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_PATH,
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


class Exp050TemporalJackknifeUtilityOperatorTests(unittest.TestCase):
    def test_authorization_merge_identity_is_frozen(self) -> None:
        self.assertEqual(
            DEC146_MERGED_COMMIT,
            "dd40df2522cf3ae9cfa5802d3d2a95a995570981",
        )

    def test_checkout_requires_clean_exact_main(self) -> None:
        report = validate_temporal_jackknife_utility_operator_checkout(
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
            validate_temporal_jackknife_utility_operator_checkout(
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
            validate_temporal_jackknife_utility_operator_checkout(
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
            validate_temporal_jackknife_utility_operator_checkout(
                branch="main",
                head_sha=SHA,
                origin_main_sha=SHA,
                porcelain_status=" M changed.py",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )

    def test_exact_workflow_endpoints_and_dispatch(self) -> None:
        self.assertEqual(
            temporal_jackknife_utility_model_dispatch_command(),
            (
                "gh",
                "workflow",
                "run",
                TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_FILE,
                "--ref",
                "main",
                "-R",
                REPOSITORY,
            ),
        )
        self.assertEqual(
            shell_join(temporal_jackknife_utility_model_dispatch_command()),
            "gh workflow run phase8a-exp050-temporal-jackknife-utility-model-training.yml "
            "--ref main -R Dtwosam/FMP",
        )
        self.assertIn(
            "phase8a-exp050-temporal-jackknife-utility-model-training.yml/runs",
            temporal_jackknife_utility_model_runs_endpoint(),
        )
        self.assertIn(
            "branch=main",
            temporal_jackknife_utility_model_runs_endpoint(),
        )
        self.assertIn(
            "event=workflow_dispatch",
            temporal_jackknife_utility_model_runs_endpoint(),
        )
        self.assertEqual(
            temporal_jackknife_utility_model_run_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123",
        )
        self.assertEqual(
            temporal_jackknife_utility_model_run_jobs_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123/jobs?per_page=100",
        )
        self.assertEqual(
            temporal_jackknife_utility_model_run_artifacts_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123/"
            "artifacts?per_page=100",
        )
        self.assertEqual(
            temporal_jackknife_utility_artifact_download_endpoint(456),
            "repos/Dtwosam/FMP/actions/artifacts/456/zip",
        )

    def test_run_selection_forbids_second_manual_main_run(self) -> None:
        self.assertIsNone(
            select_temporal_jackknife_utility_manual_main_run(
                {"workflow_runs": []}
            )
        )
        selected = select_temporal_jackknife_utility_manual_main_run(
            {"workflow_runs": [_run()]}
        )
        self.assertEqual(selected["id"], 123)

        with self.assertRaisesRegex(
            ValueError,
            "multiple manual main runs",
        ):
            select_temporal_jackknife_utility_manual_main_run(
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
            select_temporal_jackknife_utility_manual_main_run(
                {
                    "workflow_runs": [
                        {**_run(), "name": "wrong"}
                    ]
                }
            )

    def test_run_classification_is_one_way(self) -> None:
        self.assertEqual(
            classify_temporal_jackknife_utility_model_run(None)["run_state"],
            "MISSING",
        )
        self.assertEqual(
            classify_temporal_jackknife_utility_model_run(
                _run(
                    status="in_progress",
                    conclusion=None,
                )
            )["run_state"],
            "IN_PROGRESS",
        )
        self.assertEqual(
            classify_temporal_jackknife_utility_model_run(
                _run(
                    status="completed",
                    conclusion="failure",
                )
            )["run_state"],
            "TERMINAL",
        )

    def test_missing_run_is_only_dispatchable_state(self) -> None:
        report = build_temporal_jackknife_utility_operator_report(
            checkout=_checkout(),
            run=None,
        )
        self.assertEqual(
            report["stage"],
            "TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            report["temporal_jackknife_utility_model_run_dispatch_authorized"]
        )
        self.assertTrue(
            report[
                "authoritative_temporal_jackknife_utility_model_result_execution_authorized"
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
            dispatch_command_for_temporal_jackknife_utility_report(report),
            temporal_jackknife_utility_model_dispatch_command(),
        )

        active = build_temporal_jackknife_utility_operator_report(
            checkout=_checkout(),
            run=_run(
                status="in_progress",
                conclusion=None,
            ),
        )
        self.assertEqual(
            active["stage"],
            "TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_IN_PROGRESS",
        )
        self.assertIsNone(
            dispatch_command_for_temporal_jackknife_utility_report(active)
        )

        terminal = build_temporal_jackknife_utility_operator_report(
            checkout=_checkout(),
            run=_run(conclusion="failure"),
        )
        self.assertEqual(
            terminal["stage"],
            "TEMPORAL_JACKKNIFE_UTILITY_MODEL_TERMINAL_REVIEW_REQUIRED",
        )
        self.assertIsNone(
            dispatch_command_for_temporal_jackknife_utility_report(terminal)
        )

    def test_gate_metadata_matches_dec137_source_shape(self) -> None:
        gate = {
            "temporal_jackknife_utility_model_execution_gate_decision": "DEC-144",
            "temporal_jackknife_utility_model_execution_authorization_decision": "DEC-146",
            "dec141_merged_commit": "1" * 40,
            "dec142_merged_commit": "2" * 40,
            "dec143_merged_commit": "3" * 40,
            "dec144_merged_commit": "4" * 40,
            "dec145_merged_commit": "5" * 40,
            "dec144_workflow_blob_sha": "6" * 40,
            "dec144_cli_blob_sha": "7" * 40,
            "dec144_gate_blob_sha": "8" * 40,
            "dec145_review_blob_sha": "9" * 40,
            "temporal_jackknife_utility_workflow_blob_sha": "a" * 40,
            "temporal_jackknife_utility_cli_blob_sha": "b" * 40,
        }
        metadata = temporal_jackknife_utility_operator_gate_metadata(gate)
        self.assertEqual(
            metadata["dec145_merged_commit"],
            "5" * 40,
        )
        self.assertEqual(
            metadata["temporal_jackknife_utility_workflow_blob_sha"],
            "a" * 40,
        )
        self.assertNotIn("dec127_merged_commit", metadata)

        drifted = dict(gate)
        drifted.pop("dec145_merged_commit")
        with self.assertRaisesRegex(
            ValueError,
            "dec145_merged_commit",
        ):
            temporal_jackknife_utility_operator_gate_metadata(drifted)

    def test_public_cli_binds_utility_gate_metadata(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("regime_consensus", text)
        self.assertNotIn("EXP-048", text)
        self.assertIn(
            "temporal_jackknife_utility_operator_gate_metadata(gate)",
            text,
        )

    def test_dispatch_report_tamper_fails_closed(self) -> None:
        report = build_temporal_jackknife_utility_operator_report(
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
            dispatch_command_for_temporal_jackknife_utility_report(tampered)

        unlocked = dict(report)
        unlocked["promotion_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "promotion_authorized must remain false",
        ):
            dispatch_command_for_temporal_jackknife_utility_report(unlocked)

    def test_aggregate_artifact_selection_is_exact(self) -> None:
        expected = (
            f"exp050-temporal-jackknife-utility-model-result-evidence-{SHA}-"
            "from-feature-35867307338-outcome-35876715434"
        )
        selected = select_temporal_jackknife_utility_aggregate_artifact(
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
            select_temporal_jackknife_utility_aggregate_artifact(
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
            "dispatch_command_for_temporal_jackknife_utility_report(confirmed)",
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
