from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp062-active-one-shot-historical-executor-workflow-install-source-preflight-proof.yml"
)


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallSourcePreflightProofTests(
    unittest.TestCase
):
    def test_workflow_is_push_main_read_only_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp062-active-one-shot-historical-executor-"
            "workflow-install-source-preflight-proof",
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

    def test_workflow_pins_dec402_403_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_workflow_install_source_contract.py": "736d77cf08169d5d111a411d1a2d9ae6a5e4cbf5",
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_workflow_install_source_preflight.py": "c3081cbe6b62738638321124463e4ac70dab0a5d",
            "scripts/phase8a_exp062_active_one_shot_historical_executor_workflow_install_source_preflight.py": "1c9615b7ee55ff1387cd95464abf2202f8dd9d3f",
            "docs/superpowers/templates/phase8a-exp062-one-shot-historical-executor.yml.disabled": "51ce87584369be957482460d81649adb1cb9f05d",
            ".github/workflows/phase8a-exp062-discovery.yml": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
            "requirements/exp061-discovery-run.txt": "1ff32214dee10d877a067e750cd69ffad96d5fe5",
        }
        for path, blob in expected.items():
            with self.subTest(path=path):
                self.assertIn(f"git hash-object {path}", text)
                self.assertIn(blob, text)

    def test_workflow_invokes_plan_only_and_never_installs_or_dispatches(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python scripts/phase8a_exp062_active_one_shot_historical_executor_workflow_install_source_preflight.py plan",
            text,
        )
        self.assertNotIn(" install", text.split("preflight.py plan")[0][-30:])
        self.assertNotIn("gh workflow run ", text)

    def test_workflow_requires_first_exact_main_and_absent_active_path(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('test "$(git rev-parse origin/main)" = "$GITHUB_SHA"', text)
        self.assertIn(
            "test ! -e .github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
            text,
        )

    def test_workflow_proves_source_gate_and_runtime_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert plan["decision"] == "DEC-403"', text)
        self.assertIn(
            'assert plan["install_source_contract_decision"] == "DEC-402"',
            text,
        )
        self.assertIn("install_source_authorized", text)
        self.assertIn("historical_executor_workflow_install_authorized", text)
        self.assertIn("historical_result_dispatch_authorized", text)
        self.assertIn("historical_execute_mode_available", text)
        self.assertIn("trading_authorized", text)

    def test_workflow_persists_only_source_preflight_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec404-active-one-shot-historical-executor-"
            "workflow-install-source-preflight-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "active-one-shot-historical-executor-workflow-install-source-preflight.json",
            text,
        )


if __name__ == "__main__":
    unittest.main()
