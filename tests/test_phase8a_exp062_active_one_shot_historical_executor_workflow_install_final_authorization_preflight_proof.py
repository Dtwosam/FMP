from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp062-active-one-shot-historical-executor-workflow-install-final-authorization-preflight-proof.yml"
)


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallFinalAuthorizationPreflightProofTests(
    unittest.TestCase
):
    def test_workflow_is_push_main_read_only_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("push:", text)
        self.assertIn("- main", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("actions: write", text)

    def test_workflow_pins_dec411_412_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_workflow_install_final_authorization_contract.py": (
                "30493981eb2e5663e1fe620026c2c0af0cc03dd9"
            ),
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_workflow_install_final_authorization_preflight.py": (
                "89c6a606703ce72916451e0168e1b58bb765baaa"
            ),
            "scripts/phase8a_exp062_active_one_shot_historical_executor_workflow_install_final_authorization_preflight.py": (
                "6ab0b9bbecec471cfabc67b50906b2213626296b"
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
            "python scripts/phase8a_exp062_active_one_shot_historical_executor_workflow_install_final_authorization_preflight.py plan",
            text,
        )
        self.assertNotIn("workflow_install_final_authorization_preflight.py install", text)
        self.assertNotIn("workflow_install_final_authorization_preflight.py execute", text)
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

    def test_workflow_proves_seven_source_gates_and_all_runtime_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert plan["decision"] == "DEC-412"', text)
        self.assertIn(
            'assert plan["final_authorization_contract_decision"] == "DEC-411"',
            text,
        )
        self.assertIn(
            'assert plan["final_authorization_slot_verified_available"] is True',
            text,
        )
        self.assertIn('assert plan["historical_result_attempt_count"] == 0', text)
        for field in (
            "install_authorization_source_authorized",
            "install_decision_source_authorized",
            "install_execution_authorization_source_authorized",
            "install_execution_contract_source_authorized",
            "install_activation_source_authorized",
            "install_source_authorized",
            "install_final_authorization_contract_source_authorized",
            "historical_executor_workflow_install_authorized",
            "historical_result_dispatch_authorized",
            "historical_execute_mode_available",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIn(field, text)

    def test_workflow_persists_only_preflight_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec413-active-one-shot-historical-executor-workflow-"
            "install-final-authorization-preflight-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "active-one-shot-historical-executor-workflow-install-final-authorization-preflight.json",
            text,
        )


if __name__ == "__main__":
    unittest.main()
