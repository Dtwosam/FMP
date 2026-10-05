from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2020-execution-authorization.yml"
)


class AnnualCatalogue2020ExecutionAuthorizationWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_one_shot_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-execution-authorization",
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
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_workflow_pins_exact_dec567_preflight(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37313687059",
            "35115a69cae452d0afd922549fe41b4b8e404fd7",
            "11346985812",
            "sha256:182be0b68d721e3267a84bab37c5a3bcb5c25b84b546ba9565c20b6c2ee1f1b0",
            "bfccf190a7abad8464bafbf96a039305a8034f754fdc7cd05f5825c65398204f",
            "270fea87dd298888f224f605a88e66215ae06911",
            "e045b3e82d2f16e870c77b5b107d8d46fcf96f85",
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_run382_slot_unconsumed(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 7", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381}",
            text,
        )
        self.assertIn(
            'and row.get("run_number") >= 382',
            text,
        )
        self.assertIn(
            'assert value["expected_run_number"] == 382',
            text,
        )
        self.assertIn(
            'assert value["expected_run_attempt"] == 1',
            text,
        )

    def test_authorization_stays_source_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert value["decision"] == "DEC-568"', text)
        self.assertIn(
            'assert value["annual_workflow_dispatch_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert value["historical_catalogue_execution_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert value["source_only_authorization"] is True',
            text,
        )
        for field in (
            "runtime_authorization_installed",
            "runtime_gate_active",
            "dispatch_command_present",
            "dispatch_action_executed",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "run_383_or_later_authorized",
            "next_segment_execution_authorized",
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
            self.assertIn(f'"{field}",', text)
        self.assertIn(
            "annual-catalogue-2020-dec568-execution-authorization-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
