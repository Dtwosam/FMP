from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2022-dispatch-action-preflight.yml"
)


class AnnualPatternCatalogue2022DispatchActionPreflightWorkflowTests(
    unittest.TestCase
):
    def test_builder_is_first_push_read_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-dispatch-action-preflight",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_builder_pins_recovered_dec598_authorization(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37651828690",
            "a6bd637f55e356a948378f6a85e99443ee287a4f",
            "11495689874",
            "ccefdfe0cdc1998e53e4e26533e236466f50b21b80a1b3583e449b24cedd2d8b",
            "4b6dbbb1c02b0806828c19748f50bc2e06aa75b6a9baee88d6716a7e35900270",
            "ea4dde85fcb62f6b8ce44a16a7eae29334acbdf21aeeecaa06ebddb6bb749628",
            "34a805b3ab9038e847097f51a3fcc1d5c1806a53",
            "a2c752251d6a090539ddef9192e66b79e05ac789",
            "2f234ac4a420eaacdf7a61007e442d15a61ed374",
        ):
            self.assertIn(value, text)
        self.assertIn(
            "phase8a-annual-catalogue-2022-dispatch-authorization-recovery.yml",
            text,
        )
        self.assertIn(
            '"name": "phase8a-annual-catalogue-2022-dispatch-authorization-recovery"',
            text,
        )
        self.assertIn(
            "annual-catalogue-2022-dec598-dispatch-authorization-",
            text,
        )
        self.assertIn("dec598-2022-dispatch-authorization.json", text)

    def test_builder_rechecks_exact_nine_run_inventory(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 9", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        self.assertIn("37531960014", text)
        self.assertIn("a1e194907c273a2fcdddfb4c24d64a96cfd8d263", text)
        self.assertIn(
            'assert not any(row["run_number"] >= 384 for row in rows)',
            text,
        )

    def test_builder_freezes_only_run384_dispatch_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-599"', text)
        self.assertIn('value["expected_run_number"] == 384', text)
        self.assertIn('value["expected_run_attempt"] == 1', text)
        self.assertIn('value["dispatch_ref"] == "main"', text)
        self.assertIn(
            'value["dispatch_input_annual_segment_label"] == "2022"',
            text,
        )
        self.assertIn(
            'value["dispatch_input_previous_annual_freeze_run_id"]',
            text,
        )
        self.assertIn('"37531960014"', text)
        self.assertIn('value["dispatch_parameters_frozen"] is True', text)
        self.assertIn(
            'value["annual_workflow_dispatch_authorized"] is True',
            text,
        )
        self.assertIn('value["dispatch_command_present"] is False', text)
        self.assertIn('value["dispatch_action_executed"] is False', text)
        self.assertIn('value["preflight_read_only"] is True', text)
        for field in (
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "run_385_or_later_authorized",
            "next_segment_execution_authorized",
            "protected_history_access_authorized",
            "cross_year_comparison_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertIn(f'value["{field}"] is False', text)
        self.assertIn(
            "EXACT_2022_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN",
            text,
        )

    def test_builder_uploads_immutable_dec599_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2022-dec599-dispatch-action-preflight-",
            text,
        )
        self.assertIn("dec599-2022-dispatch-action-preflight.json", text)
        self.assertIn("if-no-files-found: error", text)


if __name__ == "__main__":
    unittest.main()
