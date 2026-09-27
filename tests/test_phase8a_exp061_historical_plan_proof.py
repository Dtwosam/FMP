from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase8a-exp061-historical-plan.yml"


class Exp061HistoricalPlanProofTests(unittest.TestCase):
    def test_workflow_is_push_main_read_only_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-exp061-historical-plan", text)
        self.assertIn("push:", text)
        self.assertIn("branches:", text)
        self.assertIn("- main", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("actions: write", text)

    def test_workflow_pins_dec280_281_282_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/proof_result_decision.py": (
                "fbed3788ab0c1c1e00dccfe0f84a293ff04f6ccd"
            ),
            "src/fmp/discovery/historical_run_authorization.py": (
                "1eab1cee2fc81441cf1c3168cc73275cd29addf5"
            ),
            "src/fmp/discovery/historical_operator.py": (
                "1ffef37d94b04a8206f665c375dc0b2642c4caa9"
            ),
            "scripts/phase8a_exp061_historical_operator.py": (
                "4d667d05ef2a5bd672cb9d98a81f13dd2ba9370c"
            ),
            ".github/workflows/phase8a-exp061-discovery.yml": (
                "d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9"
            ),
            "requirements/exp061-discovery-run.txt": (
                "1ff32214dee10d877a067e750cd69ffad96d5fe5"
            ),
        }
        for path, blob in expected.items():
            with self.subTest(path=path):
                self.assertIn(f"git hash-object {path}", text)
                self.assertIn(blob, text)

    def test_workflow_invokes_plan_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python scripts/phase8a_exp061_historical_operator.py plan",
            text,
        )
        self.assertNotIn(
            "phase8a_exp061_historical_operator.py execute",
            text,
        )
        self.assertNotIn(
            "phase8a_exp061_historical_operator.py advance",
            text,
        )
        shell_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip().startswith("gh workflow run ")
        ]
        self.assertEqual(shell_lines, [])

    def test_workflow_requires_exact_current_main_and_clean_checkout(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("ref: main", text)
        self.assertIn("fetch-depth: 0", text)
        self.assertIn('test "$GITHUB_EVENT_NAME" = "push"', text)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', text)
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

    def test_workflow_proves_empty_slot_and_downstream_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert plan["decision"] == "DEC-282"', text)
        self.assertIn('assert plan["authorization_decision"] == "DEC-281"', text)
        self.assertIn(
            'assert plan["stage"] == "EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE"',
            text,
        )
        self.assertIn('assert plan["proof_run_id"] == 36319888985', text)
        self.assertIn('assert plan["proof_run_count"] == 1', text)
        self.assertIn('assert plan["historical_result_attempt_count"] == 0', text)
        self.assertIn(
            'assert plan["historical_result_slot_consumed"] is False',
            text,
        )
        self.assertIn(
            "gh workflow run phase8a-exp061-discovery.yml --ref main",
            text,
        )
        for field in (
            "historical_result_dispatch_authorized",
            "historical_execute_mode_available",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIn(field, text)

    def test_workflow_persists_only_plan_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp061-dec283-historical-plan-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/historical-plan.json",
            text,
        )
        self.assertNotIn("phase8a-exp061-cell-", text)
        self.assertNotIn("phase8a-exp061-aggregate-", text)


if __name__ == "__main__":
    unittest.main()
