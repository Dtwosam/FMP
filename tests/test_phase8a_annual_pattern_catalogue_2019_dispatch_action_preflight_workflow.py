from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2019-dispatch-action-preflight.yml"
)


class AnnualPatternCatalogue2019DispatchActionPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-dispatch-action-preflight",
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

    def test_workflow_pins_exact_dec563_provenance(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37306565277",
            "c9b93843c2b853fc23d78cdbcebdbf51a3cc390e",
            "11344330424",
            "sha256:06b72e13349a47106e36ce631713da55e51407fdeeb6dd26518c8115191bf520",
            "fd554fbfd2ca556b0e4a6e65ddb00ec805809eda70d80a1e1a401edfeb71fcf8",
            "ba9c090cda76750e080d5da21aad8f41c88611da",
            "36565d2119da9326dfcbf9ed72178ecca7b2a9ae",
            "aa614fd67367a53be2889651a701b63f1ef2a7c9",
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_exact_six_run_inventory(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 6", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380}",
            text,
        )
        for run_id in (
            "37126711695",
            "37191637168",
            "37198002653",
            "37206992367",
            "37227536041",
            "37237817538",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            'assert not any(row["run_number"] >= 381 for row in rows)',
            text,
        )

    def test_workflow_freezes_only_run381_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert value["decision"] == "DEC-564"', text)
        self.assertIn('assert value["expected_run_number"] == 381', text)
        self.assertIn('assert value["expected_run_attempt"] == 1', text)
        self.assertIn('assert value["dispatch_ref"] == "main"', text)
        self.assertIn(
            'assert value["dispatch_input_annual_segment_label"] == "2019"',
            text,
        )
        self.assertIn('"37237817538"', text)
        self.assertIn('assert value["dispatch_command_present"] is False', text)
        self.assertIn('assert value["dispatch_action_executed"] is False', text)
        self.assertIn(
            'assert value["run_382_or_later_authorized"] is False',
            text,
        )
        self.assertIn('assert value["trading_authorized"] is False', text)

    def test_workflow_uploads_immutable_dec564_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2019-dec564-dispatch-action-preflight-",
            text,
        )
        self.assertIn(
            "dec564-2019-dispatch-action-preflight.json",
            text,
        )
        self.assertIn("if-no-files-found: error", text)


if __name__ == "__main__":
    unittest.main()
