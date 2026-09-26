from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp015-stage-a-operator-execute.yml"
)


class Exp015StageAOperatorExecutorWorkflowTests(unittest.TestCase):
    def test_executor_is_first_main_push_only_with_actions_write(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-exp015-stage-a-operator-execute", text)
        self.assertIn("push:", text)
        self.assertIn("branches:", text)
        self.assertIn("- main", text)
        for path in (
            ".github/workflows/phase8a-exp015-stage-a-operator-execute.yml",
            "scripts/phase8a_exp015_stage_a_executor.py",
            "src/fmp/portfolio/exp015_stage_a_executor.py",
        ):
            with self.subTest(path=path):
                self.assertIn(f"- {path}", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: write", text)

    def test_executor_binds_exact_trigger_sha_and_refuses_prior_executor_runs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('test "$(git rev-parse HEAD)" = "$GITHUB_SHA"', text)
        self.assertIn('test "$(git rev-parse origin/main)" = "$GITHUB_SHA"', text)
        self.assertIn(
            'git merge-base --is-ancestor "82a90af8edbf156e89df3a63f2003da71d4473d3" "$GITHUB_SHA"',
            text,
        )
        for sha in (
            "ae8bdfbdb1bcfd62204a1bd0ec32dddfd9938930",
            "751c886f2d00e46d3c0a20fabbe0db4231db0d5d",
            "3f2bca609ab6c1cd324f95c47be99584b11d9d90",
            "11010d32842b0f0ab829e0cc20d4654a7d5dcf2e",
            "1ff32214dee10d877a067e750cd69ffad96d5fe5",
        ):
            with self.subTest(frozen_sha=sha):
                self.assertIn(sha, text)
        self.assertIn("git hash-object", text)
        self.assertIn("executor-current-run.json", text)
        self.assertIn("executor-runs.json", text)
        self.assertIn('assert current["head_sha"] == os.environ["GITHUB_SHA"]', text)
        self.assertIn('assert current["run_attempt"] == 1', text)
        self.assertIn('assert not [item for item in relevant if item.get("id") != current_id]', text)

    def test_executor_binds_successful_dec266_proof_and_zip_digest(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for token in (
            "36277672941",
            "10917841059",
            "82a90af8edbf156e89df3a63f2003da71d4473d3",
            "sha256:b5cc74574518bc0db4a9229e1b55117fa99ec2b17264f7ee42a538df0adc3cf3",
            "b5cc74574518bc0db4a9229e1b55117fa99ec2b17264f7ee42a538df0adc3cf3",
            "exp015-dec265-stage-a-read-only-plan-",
            "sha256sum",
            'rglob("operator-plan.json")',
            'assert plan["operator_decision"] == "DEC-265"',
            'assert plan["run_state"] == "MISSING"',
            'assert plan["operator_read_only"] is True',
        ):
            with self.subTest(token=token):
                self.assertIn(token, text)

    def test_executor_requires_slot_empty_then_uses_only_dec267_script(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        endpoint = (
            "phase8a-exp015-stage-a.yml/runs?"
            "branch=main&event=workflow_dispatch&per_page=100"
        )
        self.assertGreaterEqual(text.count(endpoint), 2)
        self.assertIn("assert runs == []", text)
        self.assertIn(
            "python scripts/phase8a_exp015_stage_a_executor.py",
            text,
        )
        self.assertNotIn(
            "gh workflow run phase8a-exp015-stage-a.yml",
            text,
        )
        self.assertNotIn("/dispatches", text)
        self.assertNotIn("gh run rerun", text)

    def test_executor_independently_confirms_exactly_one_stage_a_run(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(runs) == 1", text)
        self.assertIn('assert run["name"] == "phase8a-exp015-stage-a"', text)
        self.assertIn(
            'assert run["path"] == ".github/workflows/phase8a-exp015-stage-a.yml"',
            text,
        )
        self.assertIn(
            'assert run["head_sha"] == os.environ["GITHUB_SHA"]',
            text,
        )
        self.assertIn('assert run["run_attempt"] == 1', text)
        self.assertIn('assert isinstance(run["id"], int) and run["id"] > 0', text)

    def test_executor_evidence_stays_outside_checkout(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            '"$RUNNER_TEMP/exp015-stage-a-executor-evidence"',
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/exp015-stage-a-executor-evidence",
            text,
        )
        self.assertNotIn("path: exp015-stage-a-executor-evidence", text)
        self.assertIn('test -z "$(git status --porcelain)"', text)


if __name__ == "__main__":
    unittest.main()
