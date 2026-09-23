from __future__ import annotations

import unittest

from fmp.market_learning.operator import (
    FEATURE_WORKFLOW_NAME,
    OUTCOME_WORKFLOW_NAME,
    artifact_download_endpoint,
    feature_dispatch_command,
    feature_run_artifacts_endpoint,
    feature_run_endpoint,
    feature_runs_endpoint,
    outcome_dispatch_command,
    outcome_run_artifacts_endpoint,
    outcome_run_endpoint,
    outcome_runs_endpoint,
    select_feature_evidence_artifact,
    select_outcome_evidence_artifacts,
    shell_join,
    validate_feature_evidence_for_outcomes,
    validate_feature_run_for_outcomes,
    validate_no_existing_manual_runs,
    validate_operator_checkout,
    validate_outcome_run_for_readiness,
)


SHA = "a" * 40


class Exp044OperatorTests(unittest.TestCase):
    def test_clean_exact_main_checkout_is_required(self) -> None:
        report = validate_operator_checkout(
            branch="main",
            head_sha=SHA,
            origin_main_sha=SHA,
            porcelain_status="",
            origin_url="https://github.com/Dtwosam/FMP.git",
        )
        self.assertEqual(report["head_sha"], SHA)
        self.assertTrue(report["clean_worktree"])
        self.assertTrue(report["origin_verified"])

        with self.assertRaisesRegex(ValueError, "main branch"):
            validate_operator_checkout(
                branch="feature",
                head_sha=SHA,
                origin_main_sha=SHA,
                porcelain_status="",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )
        with self.assertRaisesRegex(ValueError, "exactly match"):
            validate_operator_checkout(
                branch="main",
                head_sha=SHA,
                origin_main_sha="b" * 40,
                porcelain_status="",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )
        with self.assertRaisesRegex(ValueError, "clean working tree"):
            validate_operator_checkout(
                branch="main",
                head_sha=SHA,
                origin_main_sha=SHA,
                porcelain_status=" M file.txt",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )
        with self.assertRaisesRegex(ValueError, "origin remote"):
            validate_operator_checkout(
                branch="main",
                head_sha=SHA,
                origin_main_sha=SHA,
                porcelain_status="",
                origin_url="https://github.com/example/other.git",
            )

    def test_no_existing_manual_main_run_is_required(self) -> None:
        validate_no_existing_manual_runs(
            {"workflow_runs": []},
            workflow_name=FEATURE_WORKFLOW_NAME,
        )
        validate_no_existing_manual_runs(
            {
                "workflow_runs": [
                    {
                        "id": 1,
                        "event": "push",
                        "head_branch": "main",
                    },
                    {
                        "id": 2,
                        "event": "workflow_dispatch",
                        "head_branch": "other",
                    },
                ]
            },
            workflow_name=FEATURE_WORKFLOW_NAME,
        )
        with self.assertRaisesRegex(ValueError, "already has manual main run"):
            validate_no_existing_manual_runs(
                {
                    "workflow_runs": [
                        {
                            "id": 123,
                            "event": "workflow_dispatch",
                            "head_branch": "main",
                        }
                    ]
                },
                workflow_name=FEATURE_WORKFLOW_NAME,
            )

    def test_outcome_feature_run_must_match_exact_successful_manual_main_run(self) -> None:
        run = {
            "id": 123,
            "name": FEATURE_WORKFLOW_NAME,
            "path": ".github/workflows/phase8a-exp044-market-features.yml",
            "event": "workflow_dispatch",
            "head_branch": "main",
            "status": "completed",
            "conclusion": "success",
            "head_sha": SHA,
        }
        report = validate_feature_run_for_outcomes(run, expected_run_id=123)
        self.assertTrue(report["feature_run_verified"])
        self.assertEqual(report["feature_run_id"], 123)
        self.assertEqual(report["feature_head_sha"], SHA)

        cases = (
            ("name", "wrong", "name mismatch"),
            ("path", ".github/workflows/wrong.yml", "path mismatch"),
            ("event", "push", "workflow_dispatch"),
            ("head_branch", "other", "originate from main"),
            ("status", "in_progress", "not completed"),
            ("conclusion", "failure", "did not succeed"),
        )
        for field, value, pattern in cases:
            invalid = dict(run)
            invalid[field] = value
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, pattern):
                    validate_feature_run_for_outcomes(
                        invalid,
                        expected_run_id=123,
                    )

    def test_dispatch_commands_are_exact_manual_main_workflows(self) -> None:
        feature = feature_dispatch_command()
        self.assertEqual(
            feature,
            (
                "gh",
                "workflow",
                "run",
                "phase8a-exp044-market-features.yml",
                "--ref",
                "main",
                "-R",
                "Dtwosam/FMP",
            ),
        )
        outcome = outcome_dispatch_command(123)
        self.assertEqual(
            outcome,
            (
                "gh",
                "workflow",
                "run",
                "phase8a-exp044-market-outcomes.yml",
                "--ref",
                "main",
                "-R",
                "Dtwosam/FMP",
                "-f",
                "feature_run_id=123",
            ),
        )
        self.assertIn("phase8a-exp044-market-features.yml", shell_join(feature))
        self.assertIn("feature_run_id=123", shell_join(outcome))

    def test_outcome_run_must_be_exact_successful_manual_main_run(self) -> None:
        run = {
            "id": 456,
            "name": OUTCOME_WORKFLOW_NAME,
            "path": ".github/workflows/phase8a-exp044-market-outcomes.yml",
            "event": "workflow_dispatch",
            "head_branch": "main",
            "status": "completed",
            "conclusion": "success",
            "head_sha": "b" * 40,
        }
        report = validate_outcome_run_for_readiness(
            run,
            expected_run_id=456,
        )
        self.assertTrue(report["outcome_run_verified"])
        self.assertEqual(report["outcome_run_id"], 456)
        self.assertEqual(report["outcome_head_sha"], "b" * 40)

        cases = (
            ("name", "wrong", "name mismatch"),
            ("path", ".github/workflows/wrong.yml", "path mismatch"),
            ("event", "push", "workflow_dispatch"),
            ("head_branch", "other", "originate from main"),
            ("status", "in_progress", "not completed"),
            ("conclusion", "failure", "did not succeed"),
        )
        for field, value, pattern in cases:
            invalid = dict(run)
            invalid[field] = value
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, pattern):
                    validate_outcome_run_for_readiness(
                        invalid,
                        expected_run_id=456,
                    )

    def test_outcome_evidence_artifacts_require_exact_bound_pair(self) -> None:
        feature_sha = "a" * 40
        outcome_sha = "b" * 40
        outcome_name = (
            f"exp044-market-outcome-evidence-{outcome_sha}-from-{feature_sha}"
        )
        readiness_name = (
            f"exp044-market-learning-readiness-{outcome_sha}-from-{feature_sha}"
        )
        selected = select_outcome_evidence_artifacts(
            {
                "artifacts": [
                    {"id": 70, "name": outcome_name, "expired": False},
                    {"id": 71, "name": readiness_name, "expired": False},
                    {"id": 72, "name": "unrelated", "expired": False},
                ]
            },
            outcome_head_sha=outcome_sha,
            feature_head_sha=feature_sha,
        )
        self.assertEqual(selected["outcome_evidence_artifact_id"], 70)
        self.assertEqual(selected["readiness_artifact_id"], 71)
        self.assertEqual(selected["outcome_evidence_artifact_name"], outcome_name)
        self.assertEqual(selected["readiness_artifact_name"], readiness_name)

        with self.assertRaisesRegex(ValueError, "non-expired outcome_evidence"):
            select_outcome_evidence_artifacts(
                {
                    "artifacts": [
                        {"id": 70, "name": outcome_name, "expired": True},
                        {"id": 71, "name": readiness_name, "expired": False},
                    ]
                },
                outcome_head_sha=outcome_sha,
                feature_head_sha=feature_sha,
            )
        with self.assertRaisesRegex(ValueError, "non-expired readiness"):
            select_outcome_evidence_artifacts(
                {
                    "artifacts": [
                        {"id": 70, "name": outcome_name, "expired": False},
                        {"id": 71, "name": readiness_name, "expired": False},
                        {"id": 73, "name": readiness_name, "expired": False},
                    ]
                },
                outcome_head_sha=outcome_sha,
                feature_head_sha=feature_sha,
            )

    def test_feature_evidence_artifact_selection_requires_exact_nonexpired_match(self) -> None:
        expected_name = f"exp044-market-feature-evidence-{SHA}"
        selected = select_feature_evidence_artifact(
            {
                "artifacts": [
                    {"id": 44, "name": "unrelated", "expired": False},
                    {"id": 45, "name": expected_name, "expired": False},
                ]
            },
            feature_head_sha=SHA,
        )
        self.assertEqual(selected["artifact_id"], 45)
        self.assertEqual(selected["artifact_name"], expected_name)
        self.assertEqual(selected["feature_head_sha"], SHA)

        with self.assertRaisesRegex(ValueError, "exactly one non-expired"):
            select_feature_evidence_artifact(
                {
                    "artifacts": [
                        {"id": 45, "name": expected_name, "expired": True},
                    ]
                },
                feature_head_sha=SHA,
            )
        with self.assertRaisesRegex(ValueError, "exactly one non-expired"):
            select_feature_evidence_artifact(
                {
                    "artifacts": [
                        {"id": 45, "name": expected_name, "expired": False},
                        {"id": 46, "name": expected_name, "expired": False},
                    ]
                },
                feature_head_sha=SHA,
            )

    def test_feature_evidence_must_cross_bind_run_and_keep_locks_false(self) -> None:
        evidence = {
            "code_commit": SHA,
            "feature_evidence_complete": True,
            "verified_cell_count": 9,
            "evidence_fingerprint": "d" * 64,
            "model_fit_authorized": False,
            "shadow_authorized": False,
            "demo_order_authorized": False,
            "broker_mutation_authorized": False,
            "live_order_authorized": False,
            "real_money_authorized": False,
        }
        report = validate_feature_evidence_for_outcomes(
            evidence,
            expected_code_commit=SHA,
        )
        self.assertTrue(report["feature_evidence_verified"])
        self.assertEqual(report["feature_evidence_fingerprint"], "d" * 64)
        self.assertEqual(report["feature_evidence_code_commit"], SHA)

        wrong_commit = dict(evidence)
        wrong_commit["code_commit"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "code commit mismatch"):
            validate_feature_evidence_for_outcomes(
                wrong_commit,
                expected_code_commit=SHA,
            )

        unlocked = dict(evidence)
        unlocked["model_fit_authorized"] = True
        with self.assertRaisesRegex(ValueError, "must remain false"):
            validate_feature_evidence_for_outcomes(
                unlocked,
                expected_code_commit=SHA,
            )

    def test_api_endpoints_are_repository_and_workflow_scoped(self) -> None:
        self.assertEqual(
            feature_run_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123",
        )
        self.assertIn(
            "phase8a-exp044-market-features.yml/runs",
            feature_runs_endpoint(),
        )
        self.assertIn("branch=main", feature_runs_endpoint())
        self.assertIn("event=workflow_dispatch", feature_runs_endpoint())
        self.assertIn(
            "phase8a-exp044-market-outcomes.yml/runs",
            outcome_runs_endpoint(),
        )
        self.assertIn("branch=main", outcome_runs_endpoint())
        self.assertIn("event=workflow_dispatch", outcome_runs_endpoint())
        self.assertEqual(
            feature_run_artifacts_endpoint(123),
            "repos/Dtwosam/FMP/actions/runs/123/artifacts?per_page=100",
        )
        self.assertEqual(
            artifact_download_endpoint(456),
            "repos/Dtwosam/FMP/actions/artifacts/456/zip",
        )
        self.assertEqual(
            outcome_run_endpoint(456),
            "repos/Dtwosam/FMP/actions/runs/456",
        )
        self.assertEqual(
            outcome_run_artifacts_endpoint(456),
            "repos/Dtwosam/FMP/actions/runs/456/artifacts?per_page=100",
        )

    def test_invalid_run_ids_fail_closed(self) -> None:
        for value in (0, -1, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    outcome_dispatch_command(value)  # type: ignore[arg-type]
                with self.assertRaises(ValueError):
                    feature_run_endpoint(value)  # type: ignore[arg-type]
                with self.assertRaises(ValueError):
                    feature_run_artifacts_endpoint(value)  # type: ignore[arg-type]
                with self.assertRaises(ValueError):
                    artifact_download_endpoint(value)  # type: ignore[arg-type]
                with self.assertRaises(ValueError):
                    outcome_run_endpoint(value)  # type: ignore[arg-type]
                with self.assertRaises(ValueError):
                    outcome_run_artifacts_endpoint(value)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
