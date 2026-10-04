from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2018-dispatch-action-preflight.yml"
)


class AnnualPatternCatalogue2018DispatchActionPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-dispatch-action-preflight",
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

    def test_workflow_pins_exact_dec552_provenance(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37234867097",
            "8a02d66cfd0aee43e105e9057a813c0dffcc6dde",
            "11314579371",
            "sha256:b30f3995ca0207b65f772b15b84b23d61d9f1826ba77aabadb2a0e84064d8709",
            "eb0089103203b334c12800643f74cc838e8e9e140b4b7868f48ba74793d1d043",
            "67e2f0de14fe9ffcc8dce5473f816ed5c1ca9cb7",
            "bc1d76fc99a18b1e4b3f31682822b2d84efa3764",
            "8d4f59be7db640749aa3f5da7ba43f9e5466dd2f",
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_exact_five_run_inventory(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 5", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379}",
            text,
        )
        for run_id in (
            "37126711695",
            "37191637168",
            "37198002653",
            "37206992367",
            "37227536041",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            'assert not any(row["run_number"] >= 380 for row in rows)',
            text,
        )

    def test_workflow_freezes_only_run380_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert value["decision"] == "DEC-553"', text)
        self.assertIn('assert value["expected_run_number"] == 380', text)
        self.assertIn('assert value["expected_run_attempt"] == 1', text)
        self.assertIn('assert value["dispatch_ref"] == "main"', text)
        self.assertIn(
            'assert value["dispatch_input_annual_segment_label"] == "2018"',
            text,
        )
        self.assertIn('"37227536041"', text)
        self.assertIn('assert value["dispatch_command_present"] is False', text)
        self.assertIn('assert value["dispatch_action_executed"] is False', text)
        self.assertIn(
            'assert value["run_381_or_later_authorized"] is False',
            text,
        )
        self.assertIn('assert value["trading_authorized"] is False', text)

    def test_workflow_uploads_immutable_dec553_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2018-dec553-dispatch-action-preflight-",
            text,
        )
        self.assertIn(
            "dec553-2018-dispatch-action-preflight.json",
            text,
        )
        self.assertIn("if-no-files-found: error", text)


if __name__ == "__main__":
    unittest.main()
