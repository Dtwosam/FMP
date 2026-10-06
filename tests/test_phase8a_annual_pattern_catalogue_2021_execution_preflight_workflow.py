from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2021-execution-preflight.yml"
)


class AnnualCatalogue2021ExecutionPreflightWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_one_shot_preflight(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2021-execution-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("gh api --method POST", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_workflow_pins_exact_recovered_dec579_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37447286936",
            "2fdbcb85f4509ca5e4342cc06a284e1bcd109cc4",
            "11404455773",
            "sha256:bfd0286ed48e1ee8690921275ec34485025d95f92579519d8e68398867d45d5c",
            "ebde4b5ee78421cc2afb4c12c4ff2603b6d01f1990fbfe683aed11d00653a76c",
            "53cd4475b2e9f70252bc4962666ce421daf7795d3e78defbb38ec948448e1c3c",
            "981309374459ed6b99030f66d08ac5fc0e707dcc",
            "c0f721cafeba138d1df2cfba035c3daa96ba6bea",
            "7c721121197b83e687fd2c76773773f8ab4c07ae",
            "9ab3245ae4a073d469b6714e6f3585c79609294f",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_exact_eight_run_history(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 8", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382}",
            text,
        )
        for run_id in (
            "37126711695",
            "37191637168",
            "37198002653",
            "37206992367",
            "37227536041",
            "37237817538",
            "37310525635",
            "37443770076",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            'assert not any(row["run_number"] >= 383 for row in rows)',
            text,
        )

    def test_workflow_freezes_2021_at_run383_without_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'assert value["annual_segment_label"] == "2021"',
            text,
        )
        self.assertIn(
            'assert value["prior_segment_label"] == "2020"',
            text,
        )
        self.assertIn(
            'assert value["previous_annual_freeze_run_id"] == 37443770076',
            text,
        )
        self.assertIn(
            'assert value["successful_2020_run_number"] == 382',
            text,
        )
        self.assertIn(
            'assert value["expected_next_run_number"] == 383',
            text,
        )
        self.assertIn(
            'assert value["expected_next_run_attempt"] == 1',
            text,
        )
        self.assertIn('assert value["preflight_read_only"] is True', text)
        self.assertIn("assert value[field] is False, field", text)
        self.assertIn(
            "annual-catalogue-2021-dec580-execution-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
