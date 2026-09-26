from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp015-stage-a-operator-plan.yml"
)
REQUIREMENTS = ROOT / "requirements/exp015-stage-a-operator.txt"


class Exp015StageAOperatorPlanRunnerTests(unittest.TestCase):
    def test_runner_is_read_only_and_main_push_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-exp015-stage-a-operator-plan", text)
        self.assertIn("push:", text)
        self.assertIn("branches:", text)
        self.assertIn("- main", text)
        for path in (
            ".github/workflows/phase8a-exp015-stage-a-operator-plan.yml",
            "requirements/exp015-stage-a-operator.txt",
            "scripts/phase8a_exp015_stage_a_operator.py",
            "src/fmp/portfolio/exp015_stage_a_operator.py",
            "src/fmp/portfolio/exp015_stage_a_terminal_review.py",
            ".github/workflows/phase8a-exp015-stage-a.yml",
        ):
            with self.subTest(path=path):
                self.assertIn(f"- {path}", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("actions: write", text)

    def test_runner_binds_frozen_dec264_and_dec265_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for sha in (
            "ae8bdfbdb1bcfd62204a1bd0ec32dddfd9938930",
            "751c886f2d00e46d3c0a20fabbe0db4231db0d5d",
            "3f2bca609ab6c1cd324f95c47be99584b11d9d90",
            "11010d32842b0f0ab829e0cc20d4654a7d5dcf2e",
        ):
            with self.subTest(sha=sha):
                self.assertIn(sha, text)
        self.assertIn("git hash-object", text)

    def test_runner_executes_only_dec265_next_plan(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python scripts/phase8a_exp015_stage_a_operator.py next",
            text,
        )
        self.assertNotIn("phase8a_exp015_stage_a_operator.py advance", text)
        self.assertNotIn("advance --execute", text)
        self.assertNotIn("/dispatches", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("\n          gh workflow run ", text)
        self.assertIn(
            'assert plan["operator_decision"] == "DEC-265"',
            text,
        )
        self.assertIn(
            'assert plan["stage"] == "EXP015_STAGE_A_READ_ONLY_PROOF_REQUIRED"',
            text,
        )
        self.assertIn('assert plan["run_state"] == "MISSING"', text)
        self.assertIn('assert plan["operator_read_only"] is True', text)
        self.assertIn(
            'assert plan["head_sha"] == os.environ["GITHUB_SHA"]',
            text,
        )

    def test_runner_preserves_clean_worktree_with_minimal_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'PYTHONPATH: ${{ github.workspace }}/src',
            text,
        )
        self.assertIn(
            "python -m pip install -r requirements/exp015-stage-a-operator.txt",
            text,
        )
        self.assertNotIn("pip install -e .", text)
        self.assertIn(
            'test -z "$(git status --porcelain)"',
            text,
        )
        requirements = REQUIREMENTS.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            requirements,
            [
                "polars==1.44.2",
                "polars-runtime-32==1.44.2",
            ],
        )

    def test_runner_requires_current_main_checkout(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("ref: main", text)
        self.assertIn("fetch-depth: 0", text)
        self.assertIn('test "$GITHUB_EVENT_NAME" = "push"', text)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', text)
        self.assertIn(
            'test "$(git branch --show-current)" = "main"',
            text,
        )
        self.assertIn(
            'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"',
            text,
        )
        self.assertIn(
            'test "$(git rev-parse origin/main)" = "$GITHUB_SHA"',
            text,
        )
        self.assertIn(
            'git merge-base --is-ancestor "ed4373a7a0da36850a5f08971e9e12bd63cf1554" "$GITHUB_SHA"',
            text,
        )

    def test_runner_persists_exact_missing_slot_plan_and_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('python-version: "3.12.14"', text)
        self.assertIn(
            "exp015-dec265-stage-a-read-only-plan-",
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/operator-plan.json",
            text,
        )
        self.assertIn('assert plan["authoritative_slot_available"] is True', text)
        self.assertIn('assert plan["read_only_proof_required"] is True', text)
        self.assertIn('"phase8a-exp015-stage-a.yml "', text)
        for field in (
            "stage_a_dispatch_authorized",
            "stage_a_executor_authorized",
            "stage_a_retry_authorized",
            "stage_a_replacement_authorized",
            "stage_b_execution_authorized",
            "stage_c_execution_authorized",
            "portfolio_selection_authorized",
            "phase8a_acceptance_authorized",
            "phase8b_authorized",
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
