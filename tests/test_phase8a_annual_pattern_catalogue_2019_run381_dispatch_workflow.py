from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2019-run381-dispatch.yml"
)


class AnnualPatternCatalogue2019Run381DispatchWorkflowTests(unittest.TestCase):
    def test_dispatcher_is_exact_one_shot_push_executor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-run381-dispatch",
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

    def test_dispatcher_pins_exact_dec564_evidence_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37309216521",
            "79bffed4149cdeee1f74b8c02efdec42cb05c800",
            "11344423884",
            "sha256:2d828fa08459a23172057722e8befc69d89891734e95980a4241be5121ac0db4",
            "33ea75e1f34b2d643617be37e254644193506dea7fd959772c9eb00115088709",
            "ba9c090cda76750e080d5da21aad8f41c88611da",
            "36565d2119da9326dfcbf9ed72178ecca7b2a9ae",
            "9eec5e2ea74fc15b5d2686aa426bcaaddae5c14b",
            "e0afe81ed2deed038c2eaea005da9eac97217de0",
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_dispatcher_whitelists_only_atomic_landing_files(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = (
            ".github/workflows/phase8a-annual-catalogue-2019-run381-dispatch.yml",
            ".github/workflows/phase8a-annual-catalogue-2019-run381-runtime-evidence.yml",
            ".github/workflows/tests.yml",
            "docs/decision-log.md",
            "docs/project-state.md",
            "docs/source-of-truth-changelog.md",
            "docs/superpowers/specs/2026-10-05-phase8a-annual-catalogue-2019-run381-dispatch-and-evidence.md",
            "scripts/phase8a_annual_pattern_catalogue_2019_run381_evidence_review.py",
            "src/fmp/discovery/annual_pattern_catalogue_2019_run381_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2019_run381_dispatch_workflow.py",
            "tests/test_phase8a_annual_pattern_catalogue_2019_run381_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2019_run381_runtime_evidence_workflow.py",
        )
        for path in expected:
            self.assertIn(f'"{path}"', text)

    def test_dispatcher_submits_only_exact_run381_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(text.count(command), 1)
        self.assertIn("--ref main", text)
        self.assertIn("-f annual_segment_label=2019", text)
        self.assertIn("-f previous_annual_freeze_run_id=37237817538", text)
        self.assertIn('row.get("run_number") == 381', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row["run_number"] >= 381', text)
        self.assertIn('row.get("run_number") >= 382', text)
        self.assertNotIn("-f annual_segment_label=2019", text)

    def test_dispatch_receipt_claims_submission_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-565"', text)
        self.assertIn(
            '"stage": "ANNUAL_CATALOGUE_2019_RUN_381_DISPATCH_SUBMITTED"',
            text,
        )
        self.assertIn('"dispatch_submitted": True', text)
        self.assertIn('"result_claimed": False', text)
        self.assertIn('"run_382_or_later_authorized": False', text)
        self.assertIn('"next_segment_execution_authorized": False', text)
        self.assertIn('"strategy_v1_synthesis_authorized": False', text)
        self.assertIn('"broker_mutation_authorized": False', text)
        self.assertIn('"live_order_authorized": False', text)
        self.assertIn('"real_money_authorized": False', text)
        self.assertIn('"trading_authorized": False', text)
        self.assertIn(
            '"next_gate": "REVIEW_2019_RUN_381_BEFORE_ANY_2020_EXECUTION"',
            text,
        )


if __name__ == "__main__":
    unittest.main()
