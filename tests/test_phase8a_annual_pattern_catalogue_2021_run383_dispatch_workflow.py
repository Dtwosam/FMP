from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2021-run383-dispatch.yml"
)


class AnnualPatternCatalogue2021Run383DispatchWorkflowTests(unittest.TestCase):
    def test_dispatcher_is_exact_one_shot_push_executor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2021-run383-dispatch",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: write", text)
        self.assertNotIn("  workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_dispatcher_pins_exact_dec588_evidence_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37524076259",
            "d7f28de97b36d5511ace296d621281dc5536fdb9",
            "11440679577",
            "sha256:337a225d590433bef40d07633e6dcdddd828b8e76319fc4c73def80a68293186",
            "55b7da3109c69f0fb3df4d126653ace160cc10b854d4356c8e9564b45b95145d",
            "c4c3261a522f381630740c016b7975bf2f469c447455996be86762113e8f22f3",
            "0730061851beb76a426f2b3fd470cf1e35eb68d4",
            "a954b18cfdd04d7d39556420cd6580a4387576af",
            "542ace21e77c2bbdf5fec5312556c58d9e641da7",
            "1e80c0a61be899e62ac98540d1c7e0449f105008",
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_dispatcher_whitelists_only_atomic_landing_files(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = (
            ".github/workflows/phase8a-annual-catalogue-2021-run383-dispatch.yml",
            ".github/workflows/phase8a-annual-catalogue-2021-run383-runtime-evidence.yml",
            ".github/workflows/tests.yml",
            "scripts/phase8a_annual_pattern_catalogue_2021_run383_evidence_review.py",
            "src/fmp/discovery/annual_pattern_catalogue_2021_run383_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2021_run383_dispatch_workflow.py",
            "tests/test_phase8a_annual_pattern_catalogue_2021_run383_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2021_run383_runtime_evidence_workflow.py",
        )
        for path in expected:
            self.assertIn(f'"{path}"', text)

    def test_dispatcher_submits_only_exact_run383_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(text.count(command), 1)
        self.assertIn("--ref main", text)
        self.assertIn("-f annual_segment_label=2021", text)
        self.assertIn("-f previous_annual_freeze_run_id=37443770076", text)
        self.assertIn('row.get("run_number") == 383', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382}",
            text,
        )
        self.assertIn("681e81e021d4970a67b18370142d55b17ec68864", text)
        self.assertIn('row["run_number"] >= 383', text)
        self.assertIn('row.get("run_number") >= 384', text)
        self.assertNotIn("-f annual_segment_label=2022", text)

    def test_dispatch_receipt_claims_submission_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-589"', text)
        self.assertIn(
            '"stage": "ANNUAL_CATALOGUE_2021_RUN_383_DISPATCH_SUBMITTED"',
            text,
        )
        self.assertIn('"dispatch_submitted": True', text)
        self.assertIn('"result_claimed": False', text)
        self.assertIn("dec589-run383-dispatch-receipt.json", text)
        self.assertIn('"run_384_or_later_authorized": False', text)
        self.assertIn('"next_segment_execution_authorized": False', text)
        self.assertIn('"strategy_v1_synthesis_authorized": False', text)
        self.assertIn('"broker_mutation_authorized": False', text)
        self.assertIn('"live_order_authorized": False', text)
        self.assertIn('"real_money_authorized": False', text)
        self.assertIn('"trading_authorized": False', text)
        self.assertIn(
            '"next_gate": "REVIEW_2021_RUN_382_BEFORE_ANY_2021_EXECUTION"',
            text,
        )


if __name__ == "__main__":
    unittest.main()
