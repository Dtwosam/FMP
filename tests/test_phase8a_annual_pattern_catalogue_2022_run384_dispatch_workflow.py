from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2022-run384-dispatch.yml"
)


class AnnualPatternCatalogue2022Run384DispatchWorkflowTests(unittest.TestCase):
    def test_dispatcher_is_exact_one_shot_push_executor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-run384-dispatch",
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

    def test_dispatcher_pins_exact_dec599_evidence_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37657193417",
            "246a452bc146da3463d81aed2395294b3a53f58c",
            "11500265123",
            "sha256:05b22b33b49c10e5650a3fe7862846ee8ca7f7be8d042f39952161254043135a",
            "c046f502b6e231cb506e5b8c6430e259983ac2eb93d1d632840185aae40897bf",
            "59016a2a5a41e29eb046fe78fc4a35417da249a6cfada9388e16a0eaee7d7b61",
            "34a805b3ab9038e847097f51a3fcc1d5c1806a53",
            "a2c752251d6a090539ddef9192e66b79e05ac789",
            "ab661758202a8ba679687321148192856be00554",
            "2d6a436c61b13fbd502b3807dc98087bcfa7ccea",
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
            "f2734c7ea32355b1024d1097812578b23fc4409d",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_dispatcher_whitelists_only_atomic_landing_files(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = (
            ".github/workflows/phase8a-annual-catalogue-2022-run384-dispatch.yml",
            ".github/workflows/phase8a-annual-catalogue-2022-run384-runtime-evidence.yml",
            ".github/workflows/tests.yml",
            "scripts/phase8a_annual_pattern_catalogue_2022_run384_evidence_review.py",
            "src/fmp/discovery/annual_pattern_catalogue_2022_run384_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2022_run384_dispatch_workflow.py",
            "tests/test_phase8a_annual_pattern_catalogue_2022_run384_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2022_run384_runtime_evidence_workflow.py",
        )
        for path in expected:
            self.assertIn(f'"{path}"', text)

    def test_dispatcher_submits_only_exact_run384_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(text.count(command), 1)
        self.assertIn("--ref main", text)
        self.assertIn("-f annual_segment_label=2022", text)
        self.assertIn("-f previous_annual_freeze_run_id=37531960014", text)
        self.assertIn('row.get("run_number") == 384', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        self.assertIn("681e81e021d4970a67b18370142d55b17ec68864", text)
        self.assertIn("a1e194907c273a2fcdddfb4c24d64a96cfd8d263", text)
        self.assertIn('row["run_number"] >= 384', text)
        self.assertIn('row.get("run_number") >= 385', text)
        self.assertNotIn("-f annual_segment_label=2023", text)

    def test_dispatch_receipt_claims_submission_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-600"', text)
        self.assertIn(
            '"stage": "ANNUAL_CATALOGUE_2022_RUN_384_DISPATCH_SUBMITTED"',
            text,
        )
        self.assertIn('"dispatch_submitted": True', text)
        self.assertIn('"result_claimed": False', text)
        self.assertIn("dec600-run384-dispatch-receipt.json", text)
        self.assertIn('"run_385_or_later_authorized": False', text)
        self.assertIn('"next_segment_execution_authorized": False', text)
        self.assertIn('"protected_history_access_authorized": False', text)
        self.assertIn('"cross_year_comparison_authorized": False', text)
        self.assertIn('"strategy_v1_synthesis_authorized": False', text)
        self.assertIn('"broker_mutation_authorized": False', text)
        self.assertIn('"live_order_authorized": False', text)
        self.assertIn('"real_money_authorized": False', text)
        self.assertIn('"trading_authorized": False', text)
        self.assertIn(
            '"next_gate": "REVIEW_2022_RUN_384_BEFORE_CROSS_YEAR_COMPARISON"',
            text,
        )


if __name__ == "__main__":
    unittest.main()
