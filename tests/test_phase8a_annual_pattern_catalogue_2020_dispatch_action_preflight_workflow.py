from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2020-dispatch-action-preflight.yml"
)


class AnnualPatternCatalogue2020DispatchActionPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-dispatch-action-preflight",
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
            "37378217595",
            "4dae528384904779a9a8d110c347fb92d23ac75f",
            "11372815746",
            "sha256:52e9424d5448bb6c2ec51edabc832350c34dbe6f53dcb5a9cae883b987c4d53d",
            "bf1960379603190bf990d808b102c67d156d8ba194e023ef90859c8a8da3d79e",
            "b0ae947f98ed3f4ecb89f6a73e593a77078dae40",
            "c15f361dfdf0a3f4909644c5ce0325b7225ac6f8",
            "e6962667406a92982d60ed66b3a1cc48cf2c0bdc",
            "695a50b418da752e1bd37d6302f209033ab611f5",
            "4e124365430672fa63825b272001937c60151644",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_exact_seven_run_inventory(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 7", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381}",
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
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            'assert not any(row["run_number"] >= 382 for row in rows)',
            text,
        )

    def test_workflow_freezes_only_run382_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert value["decision"] == "DEC-575"', text)
        self.assertIn('assert value["expected_run_number"] == 382', text)
        self.assertIn('assert value["expected_run_attempt"] == 1', text)
        self.assertIn('assert value["dispatch_ref"] == "main"', text)
        self.assertIn(
            'assert value["dispatch_input_annual_segment_label"] == "2020"',
            text,
        )
        self.assertIn('"37310525635"', text)
        self.assertIn('assert value["dispatch_command_present"] is False', text)
        self.assertIn('assert value["dispatch_action_executed"] is False', text)
        self.assertIn(
            'assert value["run_383_or_later_authorized"] is False',
            text,
        )
        self.assertIn('assert value["trading_authorized"] is False', text)
        self.assertIn(
            "EXACT_2020_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN",
            text,
        )

    def test_workflow_uploads_immutable_dec575_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2020-dec575-dispatch-action-preflight-",
            text,
        )
        self.assertIn(
            "dec575-2020-dispatch-action-preflight.json",
            text,
        )
        self.assertIn("if-no-files-found: error", text)


if __name__ == "__main__":
    unittest.main()
