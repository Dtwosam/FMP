from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2018-run380-runtime-evidence.yml"
)


class AnnualPatternCatalogue2018Run380RuntimeEvidenceWorkflowTests(
    unittest.TestCase
):
    def test_reviewer_supports_normal_and_manual_recovery_paths(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-run380-runtime-evidence",
            text,
        )
        self.assertIn("  workflow_run:", text)
        self.assertIn("      - phase8a-annual-pattern-catalogue", text)
        self.assertIn("  workflow_dispatch:", text)
        self.assertIn("      target_run_id:", text)
        self.assertIn("      target_head_sha:", text)
        self.assertIn("      target_run_number:", text)
        self.assertIn("github.event.workflow_run.run_number == 380", text)
        self.assertIn(
            "github.event.workflow_run.conclusion == 'success'",
            text,
        )

    def test_reviewer_is_read_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  actions: write", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh api --method POST", text)

    def test_reviewer_pins_exact_dispatcher_and_review_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "c44123cb04a8f476cf3efdb635bd1efb1d072df1",
            "ff47d2f2ef43039dfcb88c1b9c65ce3d34428044",
            "aaf2b566804182e064f84dc7956c20e4f99661fe",
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
            "67e2f0de14fe9ffcc8dce5473f816ed5c1ca9cb7",
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
            "410180c34a9e3500bbbb42310a5253b993ac7785",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_reviewer_requires_successful_dec554_same_head(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a-annual-catalogue-2018-run380-dispatch.yml/runs",
            text,
        )
        self.assertIn('row.get("head_sha") == os.environ["TARGET_HEAD_SHA"]', text)
        self.assertIn('row.get("run_number") == 1', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row.get("conclusion") == "success"', text)
        self.assertIn('"decision"] == "DEC-554"', text)
        self.assertIn('"run_number"] == 380', text)

    def test_reviewer_binds_run380_without_later_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2018_run380_evidence_review.py",
            text,
        )
        self.assertIn('assert binding["decision"] == "DEC-555"', text)
        self.assertIn('assert binding["run_number"] == 380', text)
        self.assertIn(
            'assert binding["previous_annual_freeze_run_id"] == 37227536041',
            text,
        )
        self.assertIn('assert binding["annual_cell_count"] == 18', text)
        self.assertIn(
            'assert binding["directional_record_count"] == 89460',
            text,
        )
        self.assertIn(
            'assert binding["next_segment_execution_authorized"] is False',
            text,
        )
        self.assertIn(
            'assert binding["strategy_v1_synthesis_authorized"] is False',
            text,
        )
        self.assertIn('assert binding["trading_authorized"] is False', text)
        self.assertIn(
            "annual-catalogue-2018-dec555-runtime-binding-",
            text,
        )
        self.assertIn(
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2019_EXECUTION_PREFLIGHT",
            text,
        )


if __name__ == "__main__":
    unittest.main()
