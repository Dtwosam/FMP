from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(
    ".github/workflows/"
    "phase8a-annual-catalogue-2015-replacement-one-shot-executor.yml"
)


class AnnualCatalogue2015ReplacementOneShotExecutorTests(unittest.TestCase):
    def test_executor_is_push_once_and_actions_write_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-annual-catalogue-2015-replacement-one-shot-executor", text)
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  actions: write", text)
        self.assertIn("  contents: read", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)

    def test_executor_pins_exact_authorized_replacement_surface(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for blob in (
            "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
            "ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b",
            "c63fc9f72ad34fa6fd903f2dde8e85570521c9b9",
            "6701d3607d1576a81848810ec699ffd5b7a858a1",
            "89ad05565fa1aff8ce97ac0eb6a8d5579781ee62",
        ):
            self.assertIn(blob, text)
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2015_replacement_dispatch_action_preflight.py",
            text,
        )
        self.assertIn('assert preflight["decision"] == "DEC-499"', text)
        self.assertIn('assert preflight["failed_first_run_id"] == 37126711695', text)
        self.assertIn('assert preflight["expected_replacement_run_number"] == 2', text)
        self.assertIn('assert preflight["expected_replacement_run_attempt"] == 1', text)

    def test_executor_has_exactly_one_target_dispatch_command(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(text.count(command), 2)
        self.assertIn("--ref main", text)
        self.assertIn("-f annual_segment_label=2015", text)
        self.assertNotIn("-f annual_segment_label=2016", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("rerun-failed-jobs", text)
        self.assertNotIn("gh workflow enable", text)

    def test_executor_rejects_run3_and_writes_non_result_receipt(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('row.get("run_number") >= 3', text)
        self.assertIn('"decision": "DEC-512"', text)
        self.assertIn('"replacement_run_number": target["run_number"]', text)
        self.assertIn('"dispatch_submitted": True', text)
        self.assertIn('"result_claimed": False', text)
        for field in (
            "rerun_authorized",
            "retry_authorized",
            "third_or_later_run_authorized",
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
            self.assertIn(f'"{field}": False', text)

    def test_executor_contains_no_broker_or_order_execution_command(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for forbidden in (
            "order_send(",
            "MetaTrader5",
            "mt5.",
            "broker_order",
            "live_order(",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
