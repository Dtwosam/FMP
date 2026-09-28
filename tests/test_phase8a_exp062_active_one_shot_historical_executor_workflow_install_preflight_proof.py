from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp062-active-one-shot-historical-executor-workflow-install-preflight-proof.yml"
)


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallPreflightProofTests(
    unittest.TestCase
):
    def test_workflow_is_push_main_read_only_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp062-active-one-shot-historical-executor-workflow-install-preflight-proof",
            text,
        )
        self.assertIn("push:", text)
        self.assertIn("- main", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("actions: write", text)

    def test_workflow_pins_dec360_dec361_and_template_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_workflow_install_contract.py": (
                "63d645115dec87a4ec2bbec8448a26ea7cdded34"
            ),
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_workflow_install_preflight.py": (
                "e7a40563e173709e04a63f4d08ac73aa7224a15d"
            ),
            "scripts/phase8a_exp062_active_one_shot_historical_executor_workflow_install_preflight.py": (
                "f8c5f2d892fe9b3ac8492d6e142fbf698cd2bcdf"
            ),
            "docs/superpowers/templates/phase8a-exp062-one-shot-historical-executor.yml.disabled": (
                "51ce87584369be957482460d81649adb1cb9f05d"
            ),
            ".github/workflows/phase8a-exp062-discovery.yml": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
            "requirements/exp061-discovery-run.txt": (
                "1ff32214dee10d877a067e750cd69ffad96d5fe5"
            ),
        }
        for path, blob in expected.items():
            with self.subTest(path=path):
                self.assertIn(f"git hash-object {path}", text)
                self.assertIn(blob, text)

    def test_workflow_requires_active_executor_path_absent(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "test ! -e .github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
            text,
        )

    def test_workflow_invokes_plan_only_and_never_installs_or_dispatches(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python scripts/phase8a_exp062_active_one_shot_historical_executor_workflow_install_preflight.py plan",
            text,
        )
        self.assertNotIn(
            "phase8a_exp062_active_one_shot_historical_executor_workflow_install_preflight.py install",
            text,
        )
        self.assertNotIn(
            "phase8a_exp062_active_one_shot_historical_executor_workflow_install_preflight.py execute",
            text,
        )
        shell_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip().startswith("gh workflow run ")
        ]
        self.assertEqual(shell_lines, [])

    def test_workflow_requires_first_exact_main(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', text)
        self.assertIn('test "$(git rev-parse HEAD)" = "$GITHUB_SHA"', text)
        self.assertIn(
            'test "$(git rev-parse origin/main)" = "$GITHUB_SHA"',
            text,
        )
        self.assertIn('test -z "$(git status --porcelain)"', text)

    def test_workflow_proves_active_path_absent_and_all_runtime_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert plan["decision"] == "DEC-361"', text)
        self.assertIn(
            'assert plan["install_contract_decision"] == "DEC-360"',
            text,
        )
        self.assertIn(
            'assert plan["executor_workflow_path_exists"] is False',
            text,
        )
        self.assertIn(
            'assert plan["historical_result_attempt_count"] == 0',
            text,
        )
        self.assertIn(
            'assert plan["expected_target_run_number"] == 2',
            text,
        )
        for field in (
            "historical_executor_workflow_install_authorized",
            "historical_executor_workflow_installed",
            "historical_executor_available",
            "historical_result_dispatch_authorized",
            "historical_execute_mode_available",
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
            with self.subTest(field=field):
                self.assertIn(field, text)

    def test_workflow_persists_only_active_install_preflight_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec362-active-one-shot-historical-executor-workflow-install-preflight-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/active-one-shot-historical-executor-workflow-install-preflight.json",
            text,
        )
        self.assertNotIn("phase8a-exp062-cell-", text)
        self.assertNotIn("phase8a-exp062-aggregate-", text)


if __name__ == "__main__":
    unittest.main()
