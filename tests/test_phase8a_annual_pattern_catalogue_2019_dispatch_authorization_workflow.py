from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2019-dispatch-authorization.yml"
)


class AnnualPatternCatalogue2019DispatchAuthorizationWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-dispatch-authorization",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_exact_dec562_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37305622078",
            "236fc332c3d0fb0ad52a25038e764cd0f4e5d49f",
            "11344155034",
            "b7245744efdd4cd646b8eac6f094e9198e0f4d0cd2d36883c70685fa0feffbb7",
            "b02c7c68f682f9706e3f9e4a6e4ade7826e1abb47d01330f543279221063fe45",
            "aa614fd67367a53be2889651a701b63f1ef2a7c9",
            "f35a9de76f8db031109657eacce69a494e29beaa",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_unconsumed_run381_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380}",
            text,
        )
        self.assertIn('row.get("run_number") >= 381', text)
        self.assertIn('value["expected_run_number"] == 381', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37237817538',
            text,
        )

    def test_workflow_emits_source_only_authorization(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-563"', text)
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
