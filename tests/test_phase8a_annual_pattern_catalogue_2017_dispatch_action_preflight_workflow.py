from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2017-dispatch-action-preflight.yml"
)


class AnnualPatternCatalogue2017DispatchActionPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2017-dispatch-action-preflight",
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

    def test_workflow_pins_exact_dec541_provenance(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37223700484",
            "070b5ab9a9e6635ca26fa43f67ab71fdd49b3c1d",
            "11310658984",
            "sha256:97ee57fdb892b7041276bcd6c56da7ab06422e719c8b74aa322e35be80d243a3",
            "16d42cb2552df761b80e0b32a23de5378f143c004946cfe2c816f280b17d8e8e",
            "bae38bbf6ab23627f791d498117eb6e5f3e4e8d2",
            "c845a254c1205fee7ff56a43a56dc410d79f8291",
            "ba4a59867bba225bcdc683dde451151922074cdb",
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_exact_annual_inventory(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 4", text)
        self.assertIn("assert set(by_number) == {1, 376, 377, 378}", text)
        self.assertIn("37126711695", text)
        self.assertIn("37191637168", text)
        self.assertIn("37198002653", text)
        self.assertIn("37206992367", text)
        self.assertIn(
            'assert not any(row["run_number"] >= 379 for row in rows)',
            text,
        )

    def test_workflow_freezes_only_run379_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert value["expected_run_number"] == 379', text)
        self.assertIn('assert value["expected_run_attempt"] == 1', text)
        self.assertIn('assert value["dispatch_ref"] == "main"', text)
        self.assertIn(
            'assert value["dispatch_input_annual_segment_label"] == "2017"',
            text,
        )
        self.assertIn(
            'value["dispatch_input_previous_annual_freeze_run_id"]',
            text,
        )
        self.assertIn('"37206992367"', text)
        self.assertIn('assert value["dispatch_command_present"] is False', text)
        self.assertIn('assert value["dispatch_action_executed"] is False', text)
        self.assertIn('assert value["run_380_or_later_authorized"] is False', text)
        self.assertIn('assert value["trading_authorized"] is False', text)

    def test_workflow_uploads_immutable_dec542_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2017-dec542-dispatch-action-preflight-",
            text,
        )
        self.assertIn(
            "dec542-2017-dispatch-action-preflight.json",
            text,
        )
        self.assertIn("if-no-files-found: error", text)


if __name__ == "__main__":
    unittest.main()
