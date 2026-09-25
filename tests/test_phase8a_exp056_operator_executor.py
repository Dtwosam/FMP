from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp056-operator-execute.yml"
)


class Exp056OperatorExecutorTests(unittest.TestCase):
    def test_executor_is_single_main_push_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp056-operator-execute",
            text,
        )
        self.assertIn("push:", text)
        self.assertIn("branches:", text)
        self.assertIn("- main", text)
        self.assertIn(
            "- .github/workflows/phase8a-exp056-operator-execute.yml",
            text,
        )
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: write", text)

    def test_executor_uses_only_existing_dec215_execute_path(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python scripts/phase8a_exp056_operator.py advance --execute",
            text,
        )
        self.assertNotIn(
            "gh workflow run "
            "phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml",
            text,
        )
        self.assertNotIn(
            "actions/workflows/"
            "phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml/"
            "dispatches",
            text,
        )
        self.assertNotIn('"rerun"', text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("replacement dispatch", text.lower())

    def test_executor_binds_successful_dec216_plan(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("36175134738", text)
        self.assertIn("10882710327", text)
        self.assertIn(
            "8345129a80822f91f42681846f5f3a0eb63c8218",
            text,
        )
        self.assertIn(
            "sha256:dfbf6ffc5c2201e2f4a6f7e6118048d416ca6cc9f56e78cde36fae7361ccc9d3",
            text,
        )
        self.assertIn(
            "exp056-dec215-read-only-operator-plan-",
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
        self.assertIn(
            'assert plan["operator_decision"] == "DEC-215"',
            text,
        )
        self.assertIn(
            'assert plan["run_state"] == "MISSING"',
            text,
        )

    def test_executor_verifies_plan_zip_digest_and_content(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("sha256sum", text)
        self.assertIn("dec216-plan.zip", text)
        self.assertIn('rglob("operator-plan.json")', text)
        self.assertIn(
            "fit_temporal_residual_lower_tail_utility_model_run_dispatch_authorized",
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

    def test_executor_keeps_checkout_immutable(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("ref: main", text)
        self.assertIn("fetch-depth: 0", text)
        self.assertIn('python-version: "3.12.14"', text)
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
            "PYTHONPATH: ${{ github.workspace }}/src",
            text,
        )
        self.assertIn(
            'test -z "$(git status --porcelain)"',
            text,
        )

    def test_executor_independently_confirms_single_submitted_run(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml/runs?"
            "branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn("assert len(runs) == 1", text)
        self.assertIn(
            'assert run["head_sha"] == os.environ["GITHUB_SHA"]',
            text,
        )
        self.assertIn(
            'assert run["run_attempt"] == 1',
            text,
        )
        self.assertIn(
            'assert isinstance(run["id"], int) and run["id"] > 0',
            text,
        )

    def test_executor_evidence_stays_outside_checkout(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            '"$RUNNER_TEMP/exp056-executor-evidence"',
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/exp056-executor-evidence",
            text,
        )
        self.assertNotIn(
            "path: exp056-executor-evidence",
            text,
        )


if __name__ == "__main__":
    unittest.main()
