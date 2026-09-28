from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp062-historical-execution-plan.yml"
)


class Exp062HistoricalExecutionPlanProofTests(unittest.TestCase):
    def test_workflow_is_push_main_read_only_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp062-historical-execution-plan",
            text,
        )
        self.assertIn("push:", text)
        self.assertIn("branches:", text)
        self.assertIn("- main", text)
        self.assertIn(
            "- .github/workflows/phase8a-exp062-discovery.yml",
            text,
        )
        self.assertIn(
            "- src/fmp/discovery/exp062_historical_plan_result_freeze.py",
            text,
        )
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("actions: write", text)

    def test_workflow_pins_dec311_312_313_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/exp062_historical_plan_result_freeze.py": (
                "e3274118b37066efe2869d554e78e6b68e64b32a"
            ),
            "src/fmp/discovery/exp062_historical_execution_authorization.py": (
                "aa8cfb25e3d78c0c72da4b22898c1263a42548ba"
            ),
            "scripts/phase8a_exp062.py": (
                "773784d0770d54b1d3e41fba2057b9314a090034"
            ),
            "src/fmp/discovery/exp062_historical_execution_operator.py": (
                "7f21ccf59de9605c7fab45b4506f947ffae69cab"
            ),
            "scripts/phase8a_exp062_historical_execution_operator.py": (
                "9ecb3f47d7e68461e4a7d893ad5862d7e78a1fc8"
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
            "python scripts/phase8a_exp062_historical_execution_operator.py plan",
            text,
        )
        self.assertNotIn(
            "phase8a_exp062_historical_execution_operator.py execute",
            text,
        )
        self.assertNotIn(
            "phase8a_exp062_historical_execution_operator.py advance",
            text,
        )
        shell_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip().startswith("gh workflow run ")
        ]
        self.assertEqual(shell_lines, [])

    def test_workflow_requires_exact_first_main_and_clean_checkout(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("ref: main", text)
        self.assertIn("fetch-depth: 0", text)
        self.assertIn('test "$GITHUB_EVENT_NAME" = "push"', text)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('test "$(git rev-parse HEAD)" = "$GITHUB_SHA"', text)
        self.assertIn(
            'test "$(git rev-parse origin/main)" = "$GITHUB_SHA"',
            text,
        )
        self.assertIn(
            "python -m pip install -r requirements/exp061-discovery-run.txt",
            text,
        )
        self.assertNotIn(
            "requirements/exp061-discovery-run.txt -e .",
            text,
        )
        self.assertIn('test -z "$(git status --porcelain)"', text)

    def test_workflow_proves_run_two_plan_and_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert plan["decision"] == "DEC-313"', text)
        self.assertIn('assert plan["authorization_decision"] == "DEC-312"', text)
        self.assertIn(
            'assert plan["stage"] == "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE"',
            text,
        )
        self.assertIn('assert plan["proof_run_id"] == 36358289723', text)
        self.assertIn('assert plan["proof_run_number"] == 1', text)
        self.assertIn(
            'assert plan["historical_result_attempt_count"] == 0',
            text,
        )
        self.assertIn(
            'assert plan["expected_target_run_number"] == 2',
            text,
        )
        self.assertIn(
            'assert plan["expected_target_run_attempt"] == 1',
            text,
        )
        self.assertIn(
            "gh workflow run phase8a-exp062-discovery.yml --ref main",
            text,
        )
        self.assertIn(
            'assert plan["historical_execution_source_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert plan["historical_discovery_execution_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert plan["discovery_result_authorized"] is True',
            text,
        )
        for field in (
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

    def test_workflow_persists_only_execution_plan_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec314-historical-execution-plan-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/historical-execution-plan.json",
            text,
        )
        self.assertNotIn("phase8a-exp062-cell-", text)
        self.assertNotIn("phase8a-exp062-aggregate-", text)


if __name__ == "__main__":
    unittest.main()
