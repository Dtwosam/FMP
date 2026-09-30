from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp062-active-one-shot-historical-executor-dispatch-preflight-proof.yml"
)


class Exp062ActiveOneShotHistoricalExecutorDispatchPreflightProofTests(
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

    def test_workflow_pins_dec424_425_and_active_executor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_workflow_install_receipt.py": (
                "27e714620018413a09ceaf287fb7943bf884ee49"
            ),
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_dispatch_preflight.py": (
                "1978f71bb11097613d3820127f7a04ce2bf81adb"
            ),
            "scripts/phase8a_exp062_active_one_shot_historical_executor_dispatch_preflight.py": (
                "ef0f6df22d9208b6de8037585d706a1bb1e9eda4"
            ),
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml": (
                "51ce87584369be957482460d81649adb1cb9f05d"
            ),
        }
        for path, blob in expected.items():
            with self.subTest(path=path):
                self.assertIn(f"git hash-object {path}", text)
                self.assertIn(blob, text)

    def test_workflow_fetches_executor_and_discovery_inventories(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a-exp062-one-shot-historical-executor.yml/runs?"
            "branch=main&event=workflow_dispatch",
            text,
        )
        self.assertIn(
            "phase8a-exp062-discovery.yml/runs?"
            "branch=main&event=workflow_dispatch",
            text,
        )

    def test_workflow_invokes_plan_only_and_never_dispatches(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python scripts/phase8a_exp062_active_one_shot_historical_executor_dispatch_preflight.py plan",
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

    def test_workflow_proves_installed_state_and_runtime_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert plan["decision"] == "DEC-425"', text)
        self.assertIn('assert plan["install_receipt_decision"] == "DEC-424"', text)
        self.assertIn('assert plan["historical_executor_workflow_installed"] is True', text)
        self.assertIn('assert plan["historical_executor_available"] is True', text)
        self.assertIn('assert plan["executor_workflow_run_count"] == 0', text)
        self.assertIn('assert plan["historical_result_attempt_count"] == 0', text)
        self.assertIn('assert plan["historical_result_dispatch_authorized"]', text)
        self.assertIn('assert plan["historical_execute_mode_available"]', text)
        self.assertIn('assert plan["trading_authorized"]', text)

    def test_workflow_persists_only_preflight_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec426-active-one-shot-historical-executor-"
            "dispatch-preflight-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "active-one-shot-historical-executor-dispatch-preflight.json",
            text,
        )


if __name__ == "__main__":
    unittest.main()
