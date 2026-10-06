from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2021-execution-authorization.yml"
)


class AnnualCatalogue2021ExecutionAuthorizationWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_one_shot_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2021-execution-authorization",
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
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "2"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn("37457496751", text)
        self.assertIn("112248575079", text)
        self.assertIn(
            'steps["Require exact first authorization push"] == "failure"',
            text,
        )
        self.assertIn(
            'steps["Fetch and verify exact DEC-580 preflight artifact"] == "skipped"',
            text,
        )
        self.assertIn("assert artifacts == []", text)

    def test_workflow_pins_exact_dec580_preflight(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37452889764",
            "5b775915dc14c9f14aac34ac8dc98643a24841d8",
            "11407570779",
            "sha256:f408d6cdd389bb9f25e84d6aec110a502a0ac9d8a1098d92c8709aab879f6f62",
            "42582ae521d339a1a1df7b46fae7675fd5bce6cc98669bdbaa211d3bd864129e",
            "3e086e82201ed0bea85226c115ae7a09e7d95983",
            "981309374459ed6b99030f66d08ac5fc0e707dcc",
            "src/fmp/discovery/annual_pattern_catalogue_2021_execution_preflight.py",
            "4e124365430672fa63825b272001937c60151644",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_run383_slot_unconsumed(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 8", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382}",
            text,
        )
        self.assertIn(
            'and row.get("run_number") >= 383',
            text,
        )
        self.assertIn(
            'assert value["expected_run_number"] == 383',
            text,
        )
        self.assertIn(
            'assert value["expected_run_attempt"] == 1',
            text,
        )

    def test_authorization_stays_source_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert value["decision"] == "DEC-581"', text)
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
            "run_384_or_later_authorized",
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
            "annual-catalogue-2021-dec581-execution-authorization-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
