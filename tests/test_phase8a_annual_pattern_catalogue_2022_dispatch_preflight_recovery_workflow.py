from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2022-dispatch-preflight-recovery.yml"
)


class AnnualPatternCatalogue2022DispatchPreflightRecoveryWorkflowTests(
    unittest.TestCase
):
    def test_recovery_is_first_push_read_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-dispatch-preflight-recovery",
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
            "37639335647",
            "112853803675",
            "15fdcc3f183ea6aa1ad95bd7749c704f09a8fc69",
            "f217e70367d6fd3b241adc25fdc3b005840b0ecb",
        ):
            self.assertIn(value, text)
        self.assertIn(
            'assert steps["Recheck installed main and unconsumed run-384 slot"] '
            '== "failure"',
            text,
        )
        self.assertIn(
            'assert steps["Build concrete DEC-597 dispatch preflight"] '
            '== "skipped"',
            text,
        )
        self.assertIn(
            'assert steps["Upload immutable DEC-597 dispatch preflight"] '
            '== "skipped"',
            text,
        )
        self.assertIn("assert artifacts == []", text)

    def test_recovery_fixes_exact_history_dictionary(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            '382: (37443770076, "681e81e021d4970a67b18370142d55b17ec68864", '
            '"success"),\n              383: (37531960014, '
            '"a1e194907c273a2fcdddfb4c24d64a96cfd8d263", "success"),',
            text,
        )
        self.assertNotIn(
            '"success"),\\n              383: (37531960014',
            text,
        )
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        self.assertIn('row["run_number"] >= 384', text)

    def test_recovery_keeps_dec597_read_only_boundary(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37635483891",
            "68bdb581a89247b0a2e5046fe9a30f086260e498",
            "11489650716",
            "704fa463bbd6d23fea6a829be3db9d84b8789fb09df1dd924e526040e4d53112",
            "df6da8cb52578c82e36c6206714a0452496614d9",
            "99e99b92f74776694bdfcaab2499587b36129f6c371ef87c1696e3ba4ad3ecfd",
            "79ebf56af148c5976734976e5332b3a16b314c8a42916223c771a3fd32b78de4",
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        ):
            self.assertIn(value, text)
        self.assertIn('value["decision"] == "DEC-597"', text)
        self.assertIn('value["preflight_read_only"] is True', text)
        self.assertIn('value["dispatch_command_present"] is False', text)
        for field in (
            "annual_workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
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
