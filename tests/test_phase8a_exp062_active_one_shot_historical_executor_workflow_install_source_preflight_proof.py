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
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_workflow_install_source_contract.py": "a09eca21a8b5e7b88182040ada5d9298eb922282",
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_workflow_install_source_preflight.py": "cb8ca1ca5b65e9703844d3df9b0a622e2e3ed1bc",
            "scripts/phase8a_exp062_active_one_shot_historical_executor_workflow_install_source_preflight.py": "1c9615b7ee55ff1387cd95464abf2202f8dd9d3f",
            "docs/superpowers/templates/phase8a-exp062-one-shot-historical-executor.yml.disabled": "51ce87584369be957482460d81649adb1cb9f05d",
            ".github/workflows/phase8a-exp062-discovery.yml": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
            "requirements/exp061-discovery-run.txt": "1ff32214dee10d877a067e750cd69ffad96d5fe5",
        }
        for path, blob in expected.items():
            with self.subTest(path=path):
                self.assertIn(f"git hash-object {path}", text)
                self.assertIn(blob, text)

    def test_workflow_is_exact_run_two_recovery(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "2"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('test "$(git rev-parse origin/main)" = "$GITHUB_SHA"', text)
        self.assertIn("36613664506", text)
        self.assertIn("109561121322", text)
        self.assertIn("0db04ae49b3533778b08afa31e9ef9a26576b80c", text)
        self.assertIn('assert run["conclusion"] == "failure"', text)
        self.assertIn(
            '"Run exact DEC-403 read-only install-source preflight"',
            text,
        )
        self.assertIn(
            '"Verify install-source-ready active path absent preflight and all locks"',
            text,
        )

    def test_recovery_verifier_uses_real_dec403_fields(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("install_source_slot_verified_available", text)
        self.assertIn(
            'assert plan["historical_result_slot_verified_available"] is True',
            text,
        )
        self.assertIn('assert plan["proof_run_count"] == 1', text)
        self.assertIn('assert plan["historical_result_attempt_count"] == 0', text)
        self.assertIn('assert plan["expected_target_run_number"] == 2', text)
        self.assertIn('assert plan["expected_target_run_attempt"] == 1', text)

    def test_workflow_invokes_plan_only_and_never_installs_or_dispatches(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python scripts/phase8a_exp062_active_one_shot_historical_executor_workflow_install_source_preflight.py plan",
            text,
        )
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("actions: write", text)

    def test_workflow_proves_source_gates_and_runtime_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert plan["decision"] == "DEC-403"', text)
        self.assertIn(
            'assert plan["install_source_contract_decision"] == "DEC-402"',
            text,
        )
        for field in (
            "install_authorization_source_authorized",
            "install_decision_source_authorized",
            "install_execution_authorization_source_authorized",
            "install_execution_contract_source_authorized",
            "install_activation_source_authorized",
            "install_source_authorized",
            "historical_executor_workflow_install_authorized",
            "historical_result_dispatch_authorized",
            "historical_execute_mode_available",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIn(field, text)

    def test_workflow_persists_only_recovery_preflight_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec407-active-one-shot-historical-executor-"
            "workflow-install-source-preflight-recovery-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "active-one-shot-historical-executor-workflow-install-source-preflight.json",
            text,
        )


if __name__ == "__main__":
    unittest.main()
