from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp060-operator-plan.yml"
)


class Exp060OperatorPlanRunnerTests(unittest.TestCase):
    def test_runner_is_read_only_and_main_push_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-exp060-operator-plan", text)
        self.assertIn("push:", text)
        self.assertIn("branches:", text)
        self.assertIn("- main", text)
        self.assertIn(
            "- .github/workflows/phase8a-exp060-operator-plan.yml",
            text,
        )
        self.assertIn(
            "- scripts/phase8a_exp060_operator.py",
            text,
        )
        self.assertIn(
            "- src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_balance_utility_repair_operator.py",
            text,
        )
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("actions: write", text)

    def test_runner_executes_only_dec259_next_plan(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python scripts/phase8a_exp060_operator.py next",
            text,
        )
        self.assertNotIn(
            "phase8a_exp060_operator.py advance",
            text,
        )
        self.assertNotIn("advance --execute", text)
        self.assertNotIn(
            "gh workflow run "
            "phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml",
            text,
        )
        self.assertIn(
            'assert plan["operator_decision"] == "DEC-259"',
            text,
        )
        self.assertIn(
            '"FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_"',
            text,
        )
        self.assertIn('"RUN_DISPATCH_REQUIRED"', text)
        self.assertIn('assert plan["read_only"] is True', text)
        self.assertIn('assert plan["run_state"] == "MISSING"', text)
        self.assertIn(
            "fit_temporal_residual_regime_balance_utility_repair_model_run_dispatch_authorized",
            text,
        )
        self.assertIn(
            "authoritative_fit_temporal_residual_regime_balance_utility_repair_model_result_execution_authorized",
            text,
        )

    def test_runner_preserves_clean_worktree(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'PYTHONPATH: ${{ github.workspace }}/src',
            text,
        )
        self.assertIn(
            "python -m pip install -r "
            "requirements/exp060-model-run.txt",
            text,
        )
        self.assertNotIn(
            "requirements/exp060-model-run.txt -e .",
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
            "exp060-dec259-read-only-operator-plan-",
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
