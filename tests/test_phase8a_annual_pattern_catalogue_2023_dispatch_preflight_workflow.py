from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT / ".github/workflows/phase8a-annual-catalogue-2023-dispatch-preflight.yml"
)


class AnnualPatternCatalogue2023DispatchPreflightWorkflowTests(unittest.TestCase):
    def test_builder_is_path_scoped_read_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-annual-catalogue-2023-dispatch-preflight", text)
        self.assertIn("  push:", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        for forbidden in (
            "contents: write",
            "actions: write",
            "workflow_dispatch:",
            "gh workflow run ",
            "gh run rerun",
            "git push",
            "git commit",
        ):
            self.assertNotIn(forbidden, text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_pins_concrete_recovered_dec607(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37763604645",
            "f0243b9782b6f8a7fe18b02308410352a3f7f1d8",
            "11542709585",
            "e055c0e1d6727451c52c4cc3d3f7530fa6afc65faf87cf0d6e95e013f1b2eef8",
            "3eb688a0e69afba4a04d2b91a61fa7189135eeab",
            "1a13067292e6e52eff69d606e968b15e362ef19e8a14278d80cd594a64f5fc9c",
            "dde50dd5d4a7ad7d0fb92cc69eda83090f08958c391706b283cef9796dbfcaef",
            "fb4f8fa390e94a75a8d52c99cbc041e9bf1e8164",
            "1cb36a2ba837c38eae7b9419dfd6ef25e9333490",
            "a8cc32730ab16e9d876725363ddc6d53fa09890a",
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
            "phase8a-annual-catalogue-2023-runtime-install-executor-recovery",
        ):
            self.assertIn(value, text)

    def test_requires_exact_history_and_absent_run385(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383, 384}",
            text,
        )
        self.assertIn(
            '383: (37531960014, "a1e194907c273a2fcdddfb4c24d64a96cfd8d263", "success")',
            text,
        )
        self.assertIn(
            '384: (37663157285, "dd79687adc4ec179c56f91939cb600e6746fab5d", "success")',
            text,
        )
        self.assertIn('row["run_number"] >= 385', text)

    def test_emits_only_read_only_dec608(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-608"', text)
        self.assertIn('value["expected_run_number"] == 385', text)
        self.assertIn('value["previous_annual_freeze_run_id"] == 37663157285', text)
        self.assertIn('value["annual_workflow_run_count"] == 10', text)
        self.assertIn('value["successful_2022_run_id"] == 37663157285', text)
        self.assertIn('value["source_authorization_protected_history_access_authorized"] is True', text)
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
            "run_386_or_later_authorized",
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
        self.assertIn("annual-catalogue-2023-dec608-dispatch-preflight-", text)


if __name__ == "__main__":
    unittest.main()
