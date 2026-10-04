from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2017-run379-dispatch.yml"
)


class AnnualPatternCatalogue2017Run379DispatchWorkflowTests(unittest.TestCase):
    def test_dispatcher_is_exact_one_shot_push_executor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2017-run379-dispatch",
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

    def test_dispatcher_pins_exact_dec542_evidence_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37226222971",
            "edbbfd0ba3d33ecb61aa3ba6604bd954e98a83f1",
            "11311294443",
            "sha256:d26a3d27a026546568dccab7305f44facdbfcbc749d2aac5f9233f43f86b61ea",
            "ef31f7ea8c5e50dacee9cd2462b701d17e422f1507b2eb048db781c764d4b2db",
            "bae38bbf6ab23627f791d498117eb6e5f3e4e8d2",
            "c845a254c1205fee7ff56a43a56dc410d79f8291",
            "67e45260a79be451d7484dfcef1fc36c4df12bf0",
            "7ac3b36a2556123a86a93d3216cd3ed16d14ce2a",
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_dispatcher_whitelists_only_atomic_landing_files(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = (
            ".github/workflows/phase8a-annual-catalogue-2017-run379-dispatch.yml",
            ".github/workflows/phase8a-annual-catalogue-2017-run379-runtime-evidence.yml",
            ".github/workflows/tests.yml",
            "docs/decision-log.md",
            "docs/project-state.md",
            "docs/source-of-truth-changelog.md",
            "docs/superpowers/specs/2026-10-04-phase8a-annual-catalogue-2017-run379-dispatch-and-evidence.md",
            "scripts/phase8a_annual_pattern_catalogue_2017_run379_evidence_review.py",
            "src/fmp/discovery/annual_pattern_catalogue_2017_run379_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2017_run379_dispatch_workflow.py",
            "tests/test_phase8a_annual_pattern_catalogue_2017_run379_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2017_run379_runtime_evidence_workflow.py",
        )
        for path in expected:
            self.assertIn(f'"{path}"', text)

    def test_dispatcher_submits_only_exact_run379_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(text.count(command), 1)
        self.assertIn("--ref main", text)
        self.assertIn("-f annual_segment_label=2017", text)
        self.assertIn("-f previous_annual_freeze_run_id=37206992367", text)
        self.assertIn('row.get("run_number") == 379', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row.get("run_number") >= 380', text)
        self.assertNotIn("-f annual_segment_label=2018", text)

    def test_dispatch_receipt_claims_submission_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-543"', text)
        self.assertIn(
            '"stage": "ANNUAL_CATALOGUE_2017_RUN_379_DISPATCH_SUBMITTED"',
            text,
        )
        self.assertIn('"dispatch_submitted": True', text)
        self.assertIn('"result_claimed": False', text)
        self.assertIn('"run_380_or_later_authorized": False', text)
        self.assertIn('"next_segment_execution_authorized": False', text)
        self.assertIn('"strategy_v1_synthesis_authorized": False', text)
        self.assertIn('"broker_mutation_authorized": False', text)
        self.assertIn('"live_order_authorized": False', text)
        self.assertIn('"real_money_authorized": False', text)
        self.assertIn('"trading_authorized": False', text)
        self.assertIn(
            '"next_gate": "REVIEW_2017_RUN_379_BEFORE_ANY_2018_EXECUTION"',
            text,
        )


if __name__ == "__main__":
    unittest.main()
