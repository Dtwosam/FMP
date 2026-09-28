from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp062-one-shot-historical-executor-workflow-preflight-proof.yml"
)


class Exp062OneShotHistoricalExecutorWorkflowPreflightProofTests(
    unittest.TestCase
):
    def test_workflow_is_push_main_read_only_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp062-one-shot-historical-executor-workflow-preflight-proof",
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

    def test_workflow_pins_dec342_343_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/exp062_historical_one_shot_executor_workflow_contract.py": (
                "d87bf8f4fc3ad8fc081760c1250dc0f8dc9ffadc"
            ),
            "src/fmp/discovery/exp062_historical_one_shot_executor_workflow_preflight.py": (
                "1339dd02256b9d3fc51b2a312a2272fd5d949796"
            ),
            "scripts/phase8a_exp062_one_shot_historical_executor_workflow_preflight.py": (
                "8b2e190e75f378a52fa66ad61b0e1bbadacb343b"
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

    def test_workflow_invokes_plan_only_and_never_dispatches(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python scripts/phase8a_exp062_one_shot_historical_executor_workflow_preflight.py plan",
            text,
        )
        self.assertNotIn(
            "phase8a_exp062_one_shot_historical_executor_workflow_preflight.py execute",
            text,
        )
        self.assertNotIn(
            "phase8a_exp062_one_shot_historical_executor_workflow_preflight.py advance",
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

    def test_workflow_proves_slot_available_and_all_runtime_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert plan["decision"] == "DEC-343"', text)
        self.assertIn(
            'assert plan["workflow_contract_decision"] == "DEC-342"',
            text,
        )
        self.assertIn(
            '"EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_"',
            text,
        )
        self.assertIn('assert plan["proof_run_id"] == 36358289723', text)
        self.assertIn(
            'assert plan["historical_result_attempt_count"] == 0',
            text,
        )
        self.assertIn(
            'assert plan["expected_target_run_number"] == 2',
            text,
        )
        self.assertIn(
            "gh workflow run phase8a-exp062-discovery.yml --ref main",
            text,
        )
        self.assertIn(
            '"one_shot_historical_executor_workflow_source_authorized"',
            text,
        )
        for field in (
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

    def test_workflow_persists_only_preflight_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec344-one-shot-historical-executor-workflow-preflight-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/one-shot-historical-executor-workflow-preflight.json",
            text,
        )
        self.assertNotIn("phase8a-exp062-cell-", text)
        self.assertNotIn("phase8a-exp062-aggregate-", text)


if __name__ == "__main__":
    unittest.main()
