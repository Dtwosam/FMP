from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2017-run379-runtime-evidence-recovery.yml"
)


class AnnualCatalogue2017Run379RuntimeEvidenceRecoveryWorkflowTests(
    unittest.TestCase
):
    def test_recovery_is_one_shot_read_only_push_workflow(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2017-run379-runtime-evidence-recovery",
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
            "37227536041",
            "7b4c1ef8573e280c067443b72f1534d9091d5b7f",
            "37227526295",
            "11313110298",
            "sha256:5a22e2c287e406add84c7709116e413d68e8b17e243abd33ca2b1ab7a2ceb6af",
            "11312736203",
            "sha256:f276bd11a394688dd894f1f73b93d3c22223b6b0942615e6c3f8f41a314c06f5",
        ):
            self.assertIn(value, text)
        self.assertIn("assert set(by_number) == {1, 376, 377, 378, 379}", text)
        self.assertIn('assert not any(row["run_number"] >= 380', text)

    def test_recovery_reuses_frozen_dec544_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for blob in (
            "67e45260a79be451d7484dfcef1fc36c4df12bf0",
            "7ac3b36a2556123a86a93d3216cd3ed16d14ce2a",
            "f491b70ccc54588ba39be0a7629f4093e3453b91",
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
            "bae38bbf6ab23627f791d498117eb6e5f3e4e8d2",
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(blob, text)

    def test_recovery_has_no_annual_dispatch_or_rerun_surface(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("rerun-failed-jobs", text)
        self.assertIn('binding["decision"] == "DEC-544"', text)
        self.assertIn('binding["next_segment_execution_authorized"] is False', text)
        self.assertIn('binding["trading_authorized"] is False', text)
        self.assertIn(
            "annual-catalogue-2017-dec544-runtime-binding-recovery-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
