from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2019-run381-runtime-evidence-recovery.yml"
)


class AnnualCatalogue2019Run381RuntimeEvidenceRecoveryWorkflowTests(
    unittest.TestCase
):
    def test_recovery_is_one_shot_read_only_push_workflow(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-run381-runtime-evidence-recovery",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_recovery_pins_exact_run_dispatcher_and_artifacts(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37310525635",
            "8bcee3a7a834743f08bd9ad73109bfc09609a2fe",
            "37310506796",
            "11345118826",
            "sha256:ab1f031f0b986521b64c2667029b48a8052c5f936bb0633aff536770fb64646f",
            "11345931866",
            "sha256:cc3f5100c276e30df87d721a15843ff56b533354a5adaba6699d716a2daa8178",
        ):
            self.assertIn(value, text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381}",
            text,
        )
        self.assertIn('assert not any(row["run_number"] >= 382', text)

    def test_recovery_reuses_frozen_dec566_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for blob in (
            "9eec5e2ea74fc15b5d2686aa426bcaaddae5c14b",
            "e0afe81ed2deed038c2eaea005da9eac97217de0",
            "10011419d45ae929b6f26c4818d638c80d4018e7",
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
            "ba9c090cda76750e080d5da21aad8f41c88611da",
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(blob, text)

    def test_recovery_has_no_dispatch_or_rerun_surface(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("rerun-failed-jobs", text)
        self.assertIn('binding["decision"] == "DEC-566"', text)
        self.assertIn('binding["run_id"] == 37310525635', text)
        self.assertIn('binding["run_number"] == 381', text)
        self.assertIn(
            'binding["previous_annual_freeze_run_id"] == 37237817538',
            text,
        )
        self.assertIn(
            'binding["next_segment_execution_authorized"] is False',
            text,
        )
        self.assertIn('binding["trading_authorized"] is False', text)
        self.assertIn(
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_EXECUTION_PREFLIGHT",
            text,
        )
        self.assertIn(
            "annual-catalogue-2019-dec566-runtime-binding-recovery-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
