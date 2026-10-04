from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2018-run380-dispatch.yml"
)


class AnnualPatternCatalogue2018Run380DispatchWorkflowTests(unittest.TestCase):
    def test_dispatcher_is_exact_one_shot_push_executor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-run380-dispatch",
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

    def test_dispatcher_pins_exact_dec553_evidence_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37235949110",
            "67b8baa1f6a5770c2add27189f86f65f46a263d6",
            "11315522989",
            "sha256:e4d9b6c8661442c1a1debebac843f2dabf07bca6e36054dc7d2ed43a74f1375e",
            "ba609f06481c1b08e10d16dc772290cd0f3988de9ba32eaa56c13b5561ab86c2",
            "67e2f0de14fe9ffcc8dce5473f816ed5c1ca9cb7",
            "bc1d76fc99a18b1e4b3f31682822b2d84efa3764",
            "c44123cb04a8f476cf3efdb635bd1efb1d072df1",
            "ff47d2f2ef43039dfcb88c1b9c65ce3d34428044",
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
            "410180c34a9e3500bbbb42310a5253b993ac7785",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_dispatcher_whitelists_only_atomic_landing_files(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = (
            ".github/workflows/phase8a-annual-catalogue-2018-run380-dispatch.yml",
            ".github/workflows/phase8a-annual-catalogue-2018-run380-runtime-evidence.yml",
            ".github/workflows/tests.yml",
            "docs/decision-log.md",
            "docs/project-state.md",
            "docs/source-of-truth-changelog.md",
            "docs/superpowers/specs/2026-10-04-phase8a-annual-catalogue-2018-run380-dispatch-and-evidence.md",
            "scripts/phase8a_annual_pattern_catalogue_2018_run380_evidence_review.py",
            "src/fmp/discovery/annual_pattern_catalogue_2018_run380_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2018_run380_dispatch_workflow.py",
            "tests/test_phase8a_annual_pattern_catalogue_2018_run380_evidence_review.py",
            "tests/test_phase8a_annual_pattern_catalogue_2018_run380_runtime_evidence_workflow.py",
        )
        for path in expected:
            self.assertIn(f'"{path}"', text)

    def test_dispatcher_submits_only_exact_run380_parameters(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(text.count(command), 1)
        self.assertIn("--ref main", text)
        self.assertIn("-f annual_segment_label=2018", text)
        self.assertIn("-f previous_annual_freeze_run_id=37227536041", text)
        self.assertIn('row.get("run_number") == 380', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row["run_number"] >= 380', text)
        self.assertIn('row.get("run_number") >= 381', text)
        self.assertNotIn("-f annual_segment_label=2019", text)

    def test_dispatch_receipt_claims_submission_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-554"', text)
        self.assertIn(
            '"stage": "ANNUAL_CATALOGUE_2018_RUN_380_DISPATCH_SUBMITTED"',
            text,
        )
        self.assertIn('"dispatch_submitted": True', text)
        self.assertIn('"result_claimed": False', text)
        self.assertIn('"run_381_or_later_authorized": False', text)
        self.assertIn('"next_segment_execution_authorized": False', text)
        self.assertIn('"strategy_v1_synthesis_authorized": False', text)
        self.assertIn('"broker_mutation_authorized": False', text)
        self.assertIn('"live_order_authorized": False', text)
        self.assertIn('"real_money_authorized": False', text)
        self.assertIn('"trading_authorized": False', text)
        self.assertIn(
            '"next_gate": "REVIEW_2018_RUN_380_BEFORE_ANY_2019_EXECUTION"',
            text,
        )


if __name__ == "__main__":
    unittest.main()
