from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2018-run380-runtime-evidence-recovery.yml"
)


class AnnualCatalogue2018Run380RuntimeEvidenceRecoveryWorkflowTests(
    unittest.TestCase
):
    def test_recovery_is_one_shot_read_only_push_workflow(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-run380-runtime-evidence-recovery",
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
            "37237817538",
            "30971a996f514670a6f836d8e45cf80137197a4f",
            "37237807553",
            "11316382138",
            "sha256:684b436c37ad31d4933b8253495acb4dfbdd912adfca3a354e90cde49e355ed9",
            "11315584379",
            "sha256:ce2cdb7b4aa5fa9a0c7130e444b067463f333c0324942d57166d60b0af42e2c1",
        ):
            self.assertIn(value, text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380}",
            text,
        )
        self.assertIn('assert not any(row["run_number"] >= 381', text)

    def test_recovery_reuses_frozen_dec555_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for blob in (
            "c44123cb04a8f476cf3efdb635bd1efb1d072df1",
            "ff47d2f2ef43039dfcb88c1b9c65ce3d34428044",
            "aaf2b566804182e064f84dc7956c20e4f99661fe",
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
            "67e2f0de14fe9ffcc8dce5473f816ed5c1ca9cb7",
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
            "410180c34a9e3500bbbb42310a5253b993ac7785",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(blob, text)

    def test_recovery_has_no_dispatch_or_rerun_surface(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("rerun-failed-jobs", text)
        self.assertIn('binding["decision"] == "DEC-555"', text)
        self.assertIn('binding["run_id"] == 37237817538', text)
        self.assertIn('binding["run_number"] == 380', text)
        self.assertIn(
            'binding["previous_annual_freeze_run_id"] == 37227536041',
            text,
        )
        self.assertIn('binding["next_segment_execution_authorized"] is False', text)
        self.assertIn('binding["trading_authorized"] is False', text)
        self.assertIn(
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2019_EXECUTION_PREFLIGHT",
            text,
        )
        self.assertIn(
            "annual-catalogue-2018-dec555-runtime-binding-recovery-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
