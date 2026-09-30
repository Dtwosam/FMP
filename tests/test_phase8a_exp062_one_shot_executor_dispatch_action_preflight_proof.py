from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp062-one-shot-executor-dispatch-action-preflight-proof.yml"
)


class Exp062OneShotExecutorDispatchActionPreflightProofTests(unittest.TestCase):
    def test_workflow_is_push_main_read_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("push:", text)
        self.assertIn("- main", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("actions: write", text)

    def test_workflow_pins_dec430_431_and_executor_source(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_dispatch_authorization.py": (
                "87aada4c5224c633e8eb419f971c8f7f0699b18f"
            ),
            "src/fmp/discovery/exp062_historical_active_one_shot_executor_dispatch_action_preflight.py": (
                "93ab88965e74df0b067ba09dbbb8d0622c53e578"
            ),
            "scripts/phase8a_exp062_active_one_shot_historical_executor_dispatch_action_preflight.py": (
                "df486dd739952ab10b9ff31d6c35a01eab38618e"
            ),
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml": (
                "51ce87584369be957482460d81649adb1cb9f05d"
            ),
        }
        for path, blob in expected.items():
            with self.subTest(path=path):
                self.assertIn(f"git hash-object {path}", text)
                self.assertIn(blob, text)

    def test_workflow_fetches_both_one_shot_inventories(self) -> None:
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
            "python scripts/phase8a_exp062_active_one_shot_historical_executor_dispatch_action_preflight.py plan",
            text,
        )
        shell_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip().startswith("gh workflow run ")
        ]
        self.assertEqual(shell_lines, [])

    def test_workflow_proves_authorization_and_zero_runs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert plan["decision"] == "DEC-431"', text)
        self.assertIn('assert plan["authorization_decision"] == "DEC-430"', text)
        self.assertIn('assert plan["executor_workflow_run_count"] == 0', text)
        self.assertIn('assert plan["historical_result_attempt_count"] == 0', text)
        self.assertIn(
            'assert plan["explicit_one_shot_executor_dispatch_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert plan["historical_result_dispatch_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert plan["historical_execute_mode_available"] is False',
            text,
        )

    def test_workflow_persists_only_preflight_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec432-one-shot-executor-dispatch-action-preflight-"
            "${{ github.sha }}",
            text,
        )
        self.assertIn(
            "one-shot-executor-dispatch-action-preflight.json",
            text,
        )


if __name__ == "__main__":
    unittest.main()
