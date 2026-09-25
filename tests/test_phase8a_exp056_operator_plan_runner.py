from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp056-operator-plan.yml"
)


class Exp056OperatorPlanRunnerTests(unittest.TestCase):
    def test_runner_is_read_only_and_main_push_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-exp056-operator-plan", text)
        self.assertIn("push:", text)
        self.assertIn("branches:", text)
        self.assertIn("- main", text)
        self.assertIn(
            "- .github/workflows/phase8a-exp056-operator-plan.yml",
            text,
        )
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)

    def test_runner_executes_only_dec215_next_plan(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python scripts/phase8a_exp056_operator.py next",
            text,
        )
        self.assertNotIn(
            "phase8a_exp056_operator.py advance",
            text,
        )
        self.assertNotIn("advance --execute", text)
        self.assertNotIn(
            "gh workflow run "
            "phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml",
            text,
        )
        self.assertIn(
            'assert plan["operator_decision"] == "DEC-215"',
            text,
        )
        self.assertIn(
            '"FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_"',
            text,
        )
        self.assertIn('"RUN_DISPATCH_REQUIRED"', text)
        self.assertIn('assert plan["read_only"] is True', text)
        self.assertIn('assert plan["run_state"] == "MISSING"', text)

    def test_runner_preserves_clean_worktree(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'PYTHONPATH: ${{ github.workspace }}/src',
            text,
        )
        self.assertIn(
            "python -m pip install -r "
            "requirements/exp056-model-run.txt",
            text,
        )
        self.assertNotIn(
            "requirements/exp056-model-run.txt -e .",
            text,
        )
        self.assertIn(
            'test -z "$(git status --porcelain)"',
            text,
        )
        self.assertIn(
            '"$RUNNER_TEMP/operator-plan.json"',
            text,
        )
        self.assertNotIn(
            "> operator-plan.json",
            text,
        )

    def test_runner_requires_current_main_checkout(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("ref: main", text)
        self.assertIn("fetch-depth: 0", text)
        self.assertIn(
            'test "$GITHUB_EVENT_NAME" = "push"',
            text,
        )
        self.assertIn(
            'test "$GITHUB_REF" = "refs/heads/main"',
            text,
        )
        self.assertIn(
            'test "$(git branch --show-current)" = "main"',
            text,
        )
        self.assertIn(
            'test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"',
            text,
        )

    def test_runner_persists_plan_and_downstream_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('python-version: "3.12.14"', text)
        self.assertIn(
            "exp056-dec215-read-only-operator-plan-",
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/operator-plan.json",
            text,
        )
        for field in (
            "replacement_model_run_authorized",
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIn(field, text)


if __name__ == "__main__":
    unittest.main()
