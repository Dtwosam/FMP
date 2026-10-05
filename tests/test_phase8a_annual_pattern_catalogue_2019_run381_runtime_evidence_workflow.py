from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2019-run381-runtime-evidence.yml"
)


class AnnualPatternCatalogue2019Run381RuntimeEvidenceWorkflowTests(
    unittest.TestCase
):
    def test_reviewer_supports_normal_and_manual_recovery_paths(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-run381-runtime-evidence",
            text,
        )
        self.assertIn("  workflow_run:", text)
        self.assertIn("      - phase8a-annual-pattern-catalogue", text)
        self.assertIn("  workflow_dispatch:", text)
        self.assertIn("      target_run_id:", text)
        self.assertIn("      target_head_sha:", text)
        self.assertIn("      target_run_number:", text)
        self.assertIn("github.event.workflow_run.run_number == 381", text)
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
            "9eec5e2ea74fc15b5d2686aa426bcaaddae5c14b",
            "e0afe81ed2deed038c2eaea005da9eac97217de0",
            "10011419d45ae929b6f26c4818d638c80d4018e7",
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
            "ba9c090cda76750e080d5da21aad8f41c88611da",
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_reviewer_requires_successful_dec554_same_head(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a-annual-catalogue-2019-run381-dispatch.yml/runs",
            text,
        )
        self.assertIn('row.get("head_sha") == os.environ["TARGET_HEAD_SHA"]', text)
        self.assertIn('row.get("run_number") == 1', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row.get("conclusion") == "success"', text)
        self.assertIn('"decision"] == "DEC-565"', text)
        self.assertIn('"run_number"] == 381', text)

    def test_reviewer_binds_run381_without_later_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2019_run381_evidence_review.py",
            text,
        )
        self.assertIn('assert binding["decision"] == "DEC-566"', text)
        self.assertIn('assert binding["run_number"] == 381', text)
        self.assertIn(
            'assert binding["previous_annual_freeze_run_id"] == 37237817538',
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
            "annual-catalogue-2019-dec555-runtime-binding-",
            text,
        )
        self.assertIn(
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_EXECUTION_PREFLIGHT",
            text,
        )


if __name__ == "__main__":
    unittest.main()
