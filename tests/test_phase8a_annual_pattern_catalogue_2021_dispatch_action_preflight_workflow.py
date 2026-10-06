from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2021-dispatch-action-preflight.yml"
)


class AnnualPatternCatalogue2021DispatchActionPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2021-dispatch-action-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("gh workflow run ", text)

    def test_workflow_pins_exact_dec574_provenance(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37508621309",
            "80ea2e3a75397e098168fefa04851019d18c80f2",
            "11432463273",
            "sha256:4af08ca12556d2aae88a26510e4ec182dc7214ed0e8a1d851c60ec0e5ab09c4d",
            "d171f0c272166c277e3eae6dd37b7c8e6ff1166c0503a4bf5e0ff793226049b2",
            "133ff766a5bdb47e41ae6f52515407ebd7f34824025139b47978be0380fc006a",
            "36c24f50f93bf48e0110510a38b54e2a92551c18",
            "a954b18cfdd04d7d39556420cd6580a4387576af",
            "17a7b4de05f3d27bc96ecbc182347ac1fc7926af",
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_exact_eight_run_inventory(self) -> None:
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
            "37443770076",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            'assert not any(row["run_number"] >= 383 for row in rows)',
            text,
        )

    def test_workflow_freezes_only_run383_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert value["decision"] == "DEC-588"', text)
        self.assertIn('assert value["expected_run_number"] == 383', text)
        self.assertIn('assert value["expected_run_attempt"] == 1', text)
        self.assertIn('assert value["dispatch_ref"] == "main"', text)
        self.assertIn(
            'assert value["dispatch_input_annual_segment_label"] == "2021"',
            text,
        )
        self.assertIn('"37443770076"', text)
        self.assertIn('assert value["dispatch_command_present"] is False', text)
        self.assertIn('assert value["dispatch_action_executed"] is False', text)
        self.assertIn(
            'assert value["run_384_or_later_authorized"] is False',
            text,
        )
        self.assertIn('assert value["trading_authorized"] is False', text)
        self.assertIn(
            "EXACT_2021_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN",
            text,
        )

    def test_workflow_uploads_immutable_dec575_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2021-dec588-dispatch-action-preflight-",
            text,
        )
        self.assertIn(
            "dec588-2021-dispatch-action-preflight.json",
            text,
        )
        self.assertIn("if-no-files-found: error", text)


if __name__ == "__main__":
    unittest.main()
