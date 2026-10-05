from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2020-run382-dispatch.yml"
)


class AnnualPatternCatalogue2020Run382DispatchWorkflowTests(unittest.TestCase):
    def test_dispatcher_is_exact_one_shot_push_executor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-run382-dispatch",
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

    def test_dispatcher_pins_exact_dec575_evidence_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37388217346",
            "557b68e3361acfb1cd4dfdaf70c7b9fe63f68412",
            "11380193702",
            "sha256:b061e88aa70a9897ddb129477ba62925c6ddd738b1cd49270bf46a1d4f3f7343",
            "f0aad3d285539bbe2f0124db0a0869cc9a6813892c5be75252c46ade933a0a92",
            "26b2148f0d1f49eb8b817f2b2504a11dcb99199a",
            "c15f361dfdf0a3f4909644c5ce0325b7225ac6f8",
            "10fe71352013d0711e1c032446fc5eba0ec94dff",
            "87445bdcef0731682c121c7f7d32f921c0e1219c",
            "695a50b418da752e1bd37d6302f209033ab611f5",
            "4e124365430672fa63825b272001937c60151644",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_dispatcher_whitelists_only_atomic_landing_files(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = (
            ".github/workflows/phase8a-annual-catalogue-2020-run382-dispatch.yml",
            ".github/workflows/phase8a-annual-catalogue-2020-run382-runtime-evidence.yml",
            ".github/workflows/tests.yml",
            "scripts/phase8a_annual_pattern_catalogue_2020_run382_evidence_review.py",
            "src/fmp/discovery/annual_pattern_catalogue_2020_run382_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2020_run382_dispatch_workflow.py",
            "tests/test_phase8a_annual_pattern_catalogue_2020_run382_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2020_run382_runtime_evidence_workflow.py",
        )
        for path in expected:
            self.assertIn(f'"{path}"', text)

    def test_dispatcher_submits_only_exact_run382_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(text.count(command), 1)
        self.assertIn("--ref main", text)
        self.assertIn("-f annual_segment_label=2020", text)
        self.assertIn("-f previous_annual_freeze_run_id=37310525635", text)
        self.assertIn('row.get("run_number") == 382', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row["run_number"] >= 382', text)
        self.assertIn('row.get("run_number") >= 383', text)
        self.assertNotIn("-f annual_segment_label=2021", text)

    def test_dispatch_receipt_claims_submission_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-576"', text)
        self.assertIn(
            '"stage": "ANNUAL_CATALOGUE_2020_RUN_382_DISPATCH_SUBMITTED"',
            text,
        )
        self.assertIn('"dispatch_submitted": True', text)
        self.assertIn('"result_claimed": False', text)
        self.assertIn('"run_383_or_later_authorized": False', text)
        self.assertIn('"next_segment_execution_authorized": False', text)
        self.assertIn('"strategy_v1_synthesis_authorized": False', text)
        self.assertIn('"broker_mutation_authorized": False', text)
        self.assertIn('"live_order_authorized": False', text)
        self.assertIn('"real_money_authorized": False', text)
        self.assertIn('"trading_authorized": False', text)
        self.assertIn(
            '"next_gate": "REVIEW_2020_RUN_382_BEFORE_ANY_2021_EXECUTION"',
            text,
        )


if __name__ == "__main__":
    unittest.main()
