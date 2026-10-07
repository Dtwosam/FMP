from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT / ".github/workflows/phase8a-annual-catalogue-2022-dispatch-preflight.yml"
)


class AnnualPatternCatalogue2022DispatchPreflightWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-annual-catalogue-2022-dispatch-preflight", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)

    def test_workflow_pins_exact_dec596_recovery_install_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37635483891",
            "68bdb581a89247b0a2e5046fe9a30f086260e498",
            "11489650716",
            "704fa463bbd6d23fea6a829be3db9d84b8789fb09df1dd924e526040e4d53112",
            "df6da8cb52578c82e36c6206714a0452496614d9",
            "99e99b92f74776694bdfcaab2499587b36129f6c371ef87c1696e3ba4ad3ecfd",
            "79ebf56af148c5976734976e5332b3a16b314c8a42916223c771a3fd32b78de4",
            "6680b571765622653bf53a006a1cb7126cf7ea80",
            "4899b8be7cba3a1708aa0560aaa3d762dfd32e47",
            "8f7891820c91bcac1fec5627c7b93ee967ab3754",
        ):
            self.assertIn(value, text)
        self.assertIn(
            '"name": "phase8a-annual-catalogue-2022-runtime-install-executor-recovery"',
            text,
        )
        self.assertIn(
            '"path": ".github/workflows/'
            'phase8a-annual-catalogue-2022-runtime-install-executor-recovery.yml"',
            text,
        )

    def test_workflow_rechecks_installed_state_and_run384_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("ecb21dc7106e7bd43447f4135c3a696251a75e05", text)
        self.assertIn("f2734c7ea32355b1024d1097812578b23fc4409d", text)
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        self.assertIn(
            '383: (37531960014, "a1e194907c273a2fcdddfb4c24d64a96cfd8d263", "success")',
            text,
        )
        self.assertIn('row["run_number"] >= 384', text)
        self.assertIn(
            'git merge-base --is-ancestor "$DEC596_INSTALL_COMMIT_SHA" "$GITHUB_SHA"',
            text,
        )

    def test_workflow_emits_read_only_dec597_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-597"', text)
        self.assertIn('value["expected_run_number"] == 384', text)
        self.assertIn('value["expected_run_attempt"] == 1', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37531960014',
            text,
        )
        self.assertIn('value["annual_workflow_run_count"] == 9', text)
        self.assertIn('value["successful_2021_run_id"] == 37531960014', text)
        self.assertIn('value["dispatch_command_present"] is False', text)
        self.assertIn('value["preflight_read_only"] is True', text)
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
        self.assertIn(
            "annual-catalogue-2022-dec597-dispatch-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
