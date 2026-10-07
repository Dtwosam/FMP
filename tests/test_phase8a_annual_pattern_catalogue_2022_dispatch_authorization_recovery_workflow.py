from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2022-dispatch-authorization-recovery.yml"
)


class AnnualPatternCatalogue2022DispatchAuthorizationRecoveryWorkflowTests(
    unittest.TestCase
):
    def test_recovery_is_first_push_read_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-dispatch-authorization-recovery",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        for forbidden in ("gh workflow run ", "git push", "git commit"):
            self.assertNotIn(forbidden, text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_recovery_pins_failed_original_and_proves_no_output(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37648009956",
            "112883713950",
            "7631013958e0254e71794018c2e242f8f3b05a6f",
            "9116b5b23122bf769d744f56691f1942d7f948da",
        ):
            self.assertIn(value, text)
        self.assertIn(
            'assert steps["Fetch and verify exact DEC-597 preflight evidence"] '
            '== "failure"',
            text,
        )
        self.assertIn(
            'assert steps["Build concrete DEC-598 authorization"] == "skipped"',
            text,
        )
        self.assertIn(
            'assert steps["Upload immutable DEC-598 authorization"] == "skipped"',
            text,
        )
        self.assertIn("assert artifacts == []", text)

    def test_recovery_corrects_exact_dec597_workflow_name(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            '"name": "phase8a-annual-catalogue-2022-dispatch-preflight-recovery"',
            text,
        )
        self.assertIn(
            '"path": ".github/workflows/'
            'phase8a-annual-catalogue-2022-dispatch-preflight-recovery.yml"',
            text,
        )
        self.assertNotIn(
            '"name": "phase8a-annual-catalogue-2022-dispatch-preflight",',
            text,
        )

    def test_recovery_preserves_run384_authorization_boundary(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        self.assertIn('row.get("run_number") >= 384', text)
        self.assertIn('value["decision"] == "DEC-598"', text)
        self.assertIn('value["expected_run_number"] == 384', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37531960014',
            text,
        )
        self.assertIn('value["annual_workflow_dispatch_authorized"] is True', text)
        self.assertIn('value["source_only_authorization"] is True', text)
        for field in (
            "dispatch_command_present",
            "dispatch_action_executed",
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
            self.assertIn(f'"{field}",', text)


if __name__ == "__main__":
    unittest.main()
