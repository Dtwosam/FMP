from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2023-execution-authorization-recovery.yml"
)


class AnnualCatalogue2023ExecutionAuthorizationRecoveryWorkflowTests(
    unittest.TestCase
):
    def test_recovery_is_first_push_read_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2023-execution-authorization-recovery",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('test "$(git rev-parse origin/main)" = "$GITHUB_SHA"', text)

    def test_recovery_pins_failed_original_and_proves_no_output(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37683412011",
            "113004966636",
            "9899b8b301a928a9fff63e2da9b5002253f3b66d",
            "2ee1d7832bf0fc4d516e283bcfb698e04ebfb975",
        ):
            self.assertIn(value, text)
        self.assertIn(
            'assert steps["Fetch and verify exact DEC-602 preflight artifact"] '
            '== "failure"',
            text,
        )
        self.assertIn(
            'assert steps["Fetch exact current main and annual history"] '
            '== "skipped"',
            text,
        )
        self.assertIn(
            'assert steps["Build concrete DEC-603 authorization"] == "skipped"',
            text,
        )
        self.assertIn(
            'assert steps["Upload immutable DEC-603 authorization"] == "skipped"',
            text,
        )
        self.assertIn("assert artifacts == []", text)

    def test_recovery_corrects_only_dec602_run_number_assertion(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["expected_next_run_number"] == 385', text)
        self.assertNotIn('value["expected_next_run_number"] == 384', text)
        self.assertIn("assert len(rows) == 10", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383, 384}",
            text,
        )
        self.assertIn('row["run_number"] >= 385', text)

    def test_recovery_preserves_protected_source_only_authorization(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37678209687",
            "11507656390",
            "sha256:519c9e963df4def2011fab65c49ca909b3f7a24aacb5b09a1b8582d51cc6a8a5",
            "dc63a0265b9e2b00625431b3d48c9625ed077047bc505caac04c692890198db4",
            "4ed1e69320a4e66dd11454f35f39abbca43f14c74f8d6b52de672257a1ba658e",
            "2c4292abadbffb9dd87edaab67d9e32783facae7",
            "d7e0823bc0d7513b6d7ee27a02fb5b519bc4818b",
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        ):
            self.assertIn(value, text)
        self.assertIn('value["decision"] == "DEC-603"', text)
        self.assertIn('value["expected_run_number"] == 385', text)
        self.assertIn(
            'value["protected_history_access_authorized"] is True',
            text,
        )
        self.assertIn('value["source_only_authorization"] is True', text)
        for field in (
            "runtime_authorization_installed",
            "runtime_gate_active",
            "dispatch_command_present",
            "dispatch_action_executed",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "run_386_or_later_authorized",
            "next_segment_execution_authorized",
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
