from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp062-active-one-shot-historical-executor-workflow-install-activation-preflight-proof.yml"
)


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallActivationPreflightProofTests(
    unittest.TestCase
):
    def test_workflow_is_push_main_read_only_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp062-active-one-shot-historical-executor-"
            "workflow-install-activation-preflight-proof",
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

    def test_workflow_pins_dec396_397_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_workflow_install_activation_contract.py": "e212b776a04aef6978a4ffad378d2b9c4aac2ec5",
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_workflow_install_activation_preflight.py": "bffa1c2cf26bdbd8c0428beb682439b1312b1115",
            "scripts/phase8a_exp062_active_one_shot_historical_executor_workflow_install_activation_preflight.py": "271f0fde0162b40c96f63bbc7eddaf100f0575ce",
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
            "python scripts/phase8a_exp062_active_one_shot_historical_executor_workflow_install_activation_preflight.py plan",
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

    def test_workflow_proves_activation_gate_and_runtime_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert plan["decision"] == "DEC-397"', text)
        self.assertIn(
            'assert plan["install_activation_contract_decision"] == "DEC-396"',
            text,
        )
        self.assertIn("install_activation_source_authorized", text)
        self.assertIn("historical_executor_workflow_install_authorized", text)
        self.assertIn("historical_result_dispatch_authorized", text)
        self.assertIn("historical_execute_mode_available", text)
        self.assertIn("trading_authorized", text)

    def test_workflow_persists_only_activation_preflight_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec398-active-one-shot-historical-executor-"
            "workflow-install-activation-preflight-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "active-one-shot-historical-executor-workflow-install-activation-preflight.json",
            text,
        )


if __name__ == "__main__":
    unittest.main()
