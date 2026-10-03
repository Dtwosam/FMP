from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(
    ".github/workflows/"
    "phase8a-annual-catalogue-2015-replacement-executor-recovery.yml"
)


class AnnualCatalogue2015ReplacementExecutorRecoveryTests(unittest.TestCase):
    def test_recovery_is_one_shot_push_executor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2015-replacement-executor-recovery",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  actions: write", text)
        self.assertIn("  contents: read", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_recovery_proves_original_executor_failed_before_dispatch(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("37149151549", text)
        self.assertIn("ae6684d35003d1f63e7a53685d9c83fc906ec820", text)
        self.assertIn('"conclusion": "failure"', text)
        self.assertIn("37126711695", text)
        self.assertIn("assert len(rows) == 1", text)
        self.assertIn('assert first["run_number"] == 1', text)

    def test_recovery_installs_pinned_runtime_before_dec499(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        install = text.index(
            "python -m pip install -r requirements/exp061-discovery-run.txt -e ."
        )
        preflight = text.index(
            "python scripts/phase8a_annual_pattern_catalogue_2015_replacement_dispatch_action_preflight.py"
        )
        self.assertLess(install, preflight)
        self.assertIn(
            "1ff32214dee10d877a067e750cd69ffad96d5fe5",
            text,
        )
        self.assertIn('test -z "$(git status --porcelain)"', text)

    def test_recovery_dispatches_exactly_2015_run_two(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(text.count(command), 1)
        self.assertIn("--ref main", text)
        self.assertIn("-f annual_segment_label=2015", text)
        self.assertIn('row.get("run_number") == 2', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row.get("run_number") >= 3', text)
        self.assertNotIn("-f annual_segment_label=2016", text)

    def test_recovery_receipt_keeps_later_authority_locked(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-517"', text)
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


if __name__ == "__main__":
    unittest.main()
