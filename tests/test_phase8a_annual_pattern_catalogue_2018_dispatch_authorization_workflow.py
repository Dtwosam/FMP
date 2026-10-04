from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2018-dispatch-authorization.yml"
)


class AnnualPatternCatalogue2018DispatchAuthorizationWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-dispatch-authorization",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2018-dispatch-authorization.yml",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_exact_dec551_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37233894381",
            "35263ec4c59bae4733507c53b080f3ea07ff1325",
            "11314757055",
            "7a7ba8c4c008e6e1d6ce144eb8c2df17f506a18894d1487f044fef9533fcd9d7",
            "f756088f404f77220b366eaffdfd36cfe805f9fcd91a274ef7c5a364994893c8",
            "8d4f59be7db640749aa3f5da7ba43f9e5466dd2f",
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_unconsumed_run380_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379}",
            text,
        )
        self.assertIn('row.get("run_number") >= 380', text)
        self.assertIn('value["expected_run_number"] == 380', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37227536041',
            text,
        )

    def test_workflow_emits_source_only_authorization(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-552"', text)
        self.assertIn('value["source_only_authorization"] is True', text)
        self.assertIn(
            'value["annual_workflow_dispatch_authorized"] is True',
            text,
        )
        self.assertIn('assert value[field] is False, field', text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("rerun-failed-jobs", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)


if __name__ == "__main__":
    unittest.main()
