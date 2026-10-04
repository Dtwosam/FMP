from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(
    ".github/workflows/"
    "phase8a-annual-catalogue-2015-replacement-executor-recovery.yml"
)


class AnnualCatalogue2015ReplacementExecutorRecoveryTests(unittest.TestCase):
    def test_recovery_is_exact_third_push_executor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2015-replacement-executor-recovery",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  actions: write", text)
        self.assertIn("  contents: read", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "3"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_recovery_binds_failed_run376_before_new_dispatch(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("37126711695", text)
        self.assertIn("37191637168", text)
        self.assertIn("4c14fa7db6eb812b89ecb79201f7e298fa9c04f3", text)
        self.assertIn("build_2015_run376_failure_receipt", text)
        self.assertIn("build_2015_run377_execution_authorization", text)
        self.assertIn('assert set(by_number) == {1, 376}', text)
        self.assertIn('assert failed["conclusion"] == "failure"', text)

    def test_recovery_uses_clean_dependency_install(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("python -m pip install", text)
        self.assertIn("scikit-learn==1.9.1", text)
        self.assertNotIn("-e .", text)
        self.assertIn(
            "1ff32214dee10d877a067e750cd69ffad96d5fe5",
            text,
        )
        self.assertIn('test -z "$(git status --porcelain)"', text)

    def test_recovery_dispatches_exactly_fresh_2015_run377(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(text.count(command), 1)
        self.assertIn("--ref main", text)
        self.assertIn("-f annual_segment_label=2015", text)
        self.assertIn('row.get("run_number") == 377', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row["run_number"] >= 378', text)
        self.assertNotIn("-f annual_segment_label=2016", text)

    def test_dec528_receipt_keeps_run378_and_later_locked(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-528"', text)
        self.assertIn('"source_failure_decision": "DEC-526"', text)
        self.assertIn('"source_authorization_decision": "DEC-527"', text)
        self.assertIn('"run_number": 377', text)
        self.assertIn('"dispatch_submitted": True', text)
        self.assertIn('"result_claimed": False', text)
        for field in (
            "rerun_authorized",
            "retry_authorized",
            "run_378_or_later_authorized",
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


if __name__ == "__main__":
    unittest.main()
