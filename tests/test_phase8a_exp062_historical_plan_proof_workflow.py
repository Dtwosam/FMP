from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(
    ".github/workflows/phase8a-exp062-historical-plan.yml"
)


class Exp062HistoricalPlanProofWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_and_first_run_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("name: phase8a-exp062-historical-plan", text)
        self.assertIn("branches:\n      - main", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("contents: write", text)

    def test_workflow_pins_dec306_307_308_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        expected = {
            "src/fmp/discovery/exp062_runtime_proof_freeze.py": (
                "8e9baec1ae7b24055064535fbf7e262055dffeca"
            ),
            "src/fmp/discovery/exp062_historical_run_authorization.py": (
                "5715257543e9387d9749cfe3bb626fa03a144ed4"
            ),
            "src/fmp/discovery/exp062_historical_operator.py": (
                "990ec40bbe3ee4f776a521e1d823cb0b7ed68913"
            ),
            "scripts/phase8a_exp062_historical_operator.py": (
                "444200402e12812d9f1b16e32fa0b5bcbf0aa762"
            ),
            ".github/workflows/phase8a-exp062-discovery.yml": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
        }
        for path, sha in expected.items():
            with self.subTest(path=path):
                self.assertIn(f"git hash-object {path}", text)
                self.assertIn(sha, text)

    def test_workflow_only_runs_read_only_plan(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn(
            "python scripts/phase8a_exp062_historical_operator.py plan",
            text,
        )
        self.assertEqual(
            text.count(
                "gh workflow run phase8a-exp062-discovery.yml --ref main"
            ),
            1,
        )
        self.assertIn(
            '"historical_result_dispatch_authorized"',
            text,
        )
        self.assertIn(
            '"historical_execute_mode_available"',
            text,
        )
        self.assertIn(
            '"historical_discovery_execution_authorized"',
            text,
        )
        self.assertIn(
            '"reserved_robustness_access_authorized"',
            text,
        )
        self.assertIn(
            '"trading_authorized"',
            text,
        )

    def test_workflow_uploads_only_plan_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: exp062-dec309-historical-plan-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/historical-plan.json",
            text,
        )
        self.assertNotIn("cell-evidence", text)
        self.assertNotIn("aggregate-evidence", text)


if __name__ == "__main__":
    unittest.main()
