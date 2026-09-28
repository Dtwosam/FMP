from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp062-historical-dispatch-plan.yml"
)


class Exp062HistoricalDispatchPlanProofTests(unittest.TestCase):
    def test_workflow_is_push_main_read_only_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp062-historical-dispatch-plan",
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

    def test_workflow_pins_dec317_318_319_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/exp062_historical_execution_runtime_freeze.py": (
                "9626f6cd1c66a67d91dd3acf743e120ea8d2e9c0"
            ),
            "src/fmp/discovery/exp062_historical_dispatch_authorization.py": (
                "b5360751459212cfabb37a3dd7758fe0cc28c4a6"
            ),
            "src/fmp/discovery/exp062_historical_dispatch_operator.py": (
                "72c1cd881c004c91c2cf7c3797e00d68e3a27056"
            ),
            "scripts/phase8a_exp062_historical_dispatch_operator.py": (
                "9f41465f287daccc5f7685453129bc20916bec17"
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
            "python scripts/phase8a_exp062_historical_dispatch_operator.py plan",
            text,
        )
        self.assertNotIn(
            "phase8a_exp062_historical_dispatch_operator.py execute",
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
        self.assertIn('assert plan["decision"] == "DEC-319"', text)
        self.assertIn('assert plan["authorization_decision"] == "DEC-318"', text)
        self.assertIn(
            'assert plan["stage"] == "EXP062_ONE_SHOT_DISPATCH_SLOT_AVAILABLE"',
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
            'assert plan["one_shot_dispatch_source_authorized"] is True',
            text,
        )
        for field in (
            "historical_result_dispatch_authorized",
            "historical_executor_available",
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

    def test_workflow_persists_only_dispatch_plan_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec320-historical-dispatch-plan-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/historical-dispatch-plan.json",
            text,
        )
        self.assertNotIn("phase8a-exp062-cell-", text)
        self.assertNotIn("phase8a-exp062-aggregate-", text)


if __name__ == "__main__":
    unittest.main()
