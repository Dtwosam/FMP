from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp051-operator-execute.yml"
)


class Exp051OperatorExecutorTests(unittest.TestCase):
    def test_executor_is_single_main_push_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn(
            "name: phase8a-exp051-operator-execute",
            text,
        )
        self.assertIn("push:", text)
        self.assertIn("branches:", text)
        self.assertIn("- main", text)
        self.assertIn(
            "- .github/workflows/phase8a-exp051-operator-execute.yml",
            text,
        )
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: write", text)

    def test_executor_uses_only_existing_dec156_execute_path(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn(
            "python scripts/phase8a_exp051_operator.py advance --execute",
            text,
        )
        self.assertNotIn(
            "gh workflow run "
            "phase8a-exp051-temporal-calibrated-utility-model-training.yml",
            text,
        )
        self.assertNotIn(
            "actions/workflows/"
            "phase8a-exp051-temporal-calibrated-utility-model-training.yml/dispatches",
            text,
        )
        self.assertNotIn(
            '"rerun"',
            text,
        )

    def test_executor_binds_successful_read_only_plan(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn(
            "36065565456",
            text,
        )
        self.assertIn(
            "10835714803",
            text,
        )
        self.assertIn(
            "a997808602ab3a9f4ca53982895c05cb0a358e67",
            text,
        )
        self.assertIn(
            "exp051-dec156-read-only-operator-plan-",
            text,
        )
        self.assertIn(
            'assert run["conclusion"] == "success"',
            text,
        )
        self.assertIn(
            'assert run["run_attempt"] == 1',
            text,
        )

    def test_executor_keeps_checkout_immutable(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("ref: main", text)
        self.assertIn("fetch-depth: 0", text)
        self.assertIn(
            'python-version: "3.12.14"',
            text,
        )
        self.assertIn(
            "python -m pip install -r "
            "requirements/exp051-model-run.txt",
            text,
        )
        self.assertNotIn(
            "requirements/exp051-model-run.txt -e .",
            text,
        )
        self.assertIn(
            "PYTHONPATH: ${{ github.workspace }}/src",
            text,
        )
        self.assertIn(
            'test -z "$(git status --porcelain)"',
            text,
        )
        self.assertIn(
            'Path(os.environ["RUNNER_TEMP"])',
            text,
        )

    def test_executor_receipt_claims_dispatch_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn(
            'assert receipt["operator_decision"] == "DEC-156"',
            text,
        )
        self.assertIn(
            'assert receipt["advance_execute_requested"] is True',
            text,
        )
        self.assertIn(
            'assert receipt["advance_dispatchable"] is True',
            text,
        )
        self.assertIn(
            'assert receipt["dispatch_submitted"] is True',
            text,
        )
        self.assertIn(
            'assert receipt["result_claimed"] is False',
            text,
        )
        self.assertIn(
            'assert receipt["run_state"] == "MISSING"',
            text,
        )

    def test_executor_keeps_downstream_locks_false(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

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

    def test_execution_receipt_stays_outside_checkout(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn(
            '>"$RUNNER_TEMP/operator-execution.json"',
            text.replace(" ", ""),
        )
        self.assertIn(
            "path: ${{ runner.temp }}/operator-execution.json",
            text,
        )
        self.assertNotIn(
            "path: operator-execution.json",
            text,
        )


if __name__ == "__main__":
    unittest.main()
