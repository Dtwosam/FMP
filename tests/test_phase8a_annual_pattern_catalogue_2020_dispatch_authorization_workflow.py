from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2020-dispatch-authorization.yml"
)


class AnnualPatternCatalogue2020DispatchAuthorizationWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-dispatch-authorization",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_exact_dec573_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37367592757",
            "46aa484cc4729ff662122fb629576a6a40c1530f",
            "11368966845",
            "bba88547a36138109e6178936fd632e9bc61e81f8725e12124d739477916c5fa",
            "54ad1c4e693545ace92aed406140005ef8b609971247d1cf5b4240931dc7987e",
            "e6962667406a92982d60ed66b3a1cc48cf2c0bdc",
            "2ab0ecb028853bcc1cbbbed44d421d87b9c2a1d1",
            "0e796623ddc8b95e62db9d841d658d2b1898eac0",
            "695a50b418da752e1bd37d6302f209033ab611f5",
            "4e124365430672fa63825b272001937c60151644",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_unconsumed_run382_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381}",
            text,
        )
        self.assertIn('row.get("run_number") >= 382', text)
        self.assertIn('value["expected_run_number"] == 382', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37310525635',
            text,
        )

    def test_workflow_emits_source_only_authorization(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-574"', text)
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
