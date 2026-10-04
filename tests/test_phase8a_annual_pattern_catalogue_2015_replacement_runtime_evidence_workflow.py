from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(
    ".github/workflows/"
    "phase8a-annual-catalogue-2015-replacement-runtime-evidence.yml"
)


class AnnualCatalogue2015ReplacementRuntimeEvidenceWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_workflow_run_reviewer(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2015-replacement-runtime-evidence",
            text,
        )
        self.assertIn("  workflow_run:", text)
        self.assertIn("      - phase8a-annual-pattern-catalogue", text)
        self.assertIn("      - completed", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  actions: write", text)
        self.assertNotIn("  push:", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_reviewer_is_limited_to_replacement_run_two(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "github.event.workflow_run.run_number == 377",
            text,
        )
        self.assertIn('"run_number": 377', text)
        self.assertIn('"run_attempt": 1', text)
        self.assertIn('"conclusion": "success"', text)
        self.assertIn(
            "phase8a-annual-catalogue-2015-replacement-executor-recovery.yml",
            text,
        )
        self.assertIn('row.get("run_number") == 3', text)
        self.assertIn('row.get("run_number") == 1', text)
        self.assertIn("37190929052", text)
        self.assertIn('row.get("run_attempt") == 1', text)

    def test_reviewer_pins_exact_review_freeze_binding_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for blob in (
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "74e9499d9485c8e2a402fb675c995cc1961ff16a",
            "350806f8d37e4deae6ff8a16551e7b07fd1d5958",
            "d6935a7b31b028b955f182cf81bc2c123a321852",
            "97cfd73d5693046f05104342cb74867d5dc471cc",
            "400e9715a6e3b2dab413ce2ecff0fbce8c46f6b0",
            "0e472b79d12c8a5f14963fac3ed718f5e2c28d02",
            "f8a9a872195f01ca85627a6a6cac4a0c0672f82d",
            "584871d8f55f1da0e5bd885f91542141dc523972",
            "1ff32214dee10d877a067e750cd69ffad96d5fe5",
        ):
            self.assertIn(blob, text)

    def test_reviewer_runs_dec500_dec501_dec502_in_order(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        review = text.index(
            "phase8a_annual_pattern_catalogue_2015_replacement_run_review.py"
        )
        freeze = text.index(
            "phase8a_annual_pattern_catalogue_2015_replacement_run_freeze.py"
        )
        binding = text.index(
            "phase8a_annual_pattern_catalogue_2015_runtime_evidence_binding.py"
        )
        self.assertLess(review, freeze)
        self.assertLess(freeze, binding)
        self.assertIn('"decision"] == "DEC-502"', text)
        self.assertIn('"runtime_evidence_bound"] is True', text)

    def test_reviewer_cannot_dispatch_or_escalate_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("rerun-failed-jobs", text)
        self.assertIn("assert binding[field] is False, field", text)
        for field in (
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


if __name__ == "__main__":
    unittest.main()
