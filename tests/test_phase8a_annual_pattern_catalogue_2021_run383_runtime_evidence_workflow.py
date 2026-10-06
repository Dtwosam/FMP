from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2021-run383-runtime-evidence.yml"
)


class AnnualPatternCatalogue2021Run383RuntimeEvidenceWorkflowTests(
    unittest.TestCase
):
    def test_reviewer_supports_normal_and_recovery_paths(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2021-run383-runtime-evidence",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("    branches:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "phase8a-annual-catalogue-2021-run383-runtime-evidence.yml",
            text,
        )
        self.assertIn("  workflow_run:", text)
        self.assertIn("      - phase8a-annual-pattern-catalogue", text)
        self.assertIn("  workflow_dispatch:", text)
        self.assertIn("      target_run_id:", text)
        self.assertIn("      target_head_sha:", text)
        self.assertIn("      target_run_number:", text)
        self.assertIn("github.event.workflow_run.run_number == 383", text)
        self.assertIn(
            "github.event.workflow_run.conclusion == 'success'",
            text,
        )
        self.assertIn("github.event_name == 'push'", text)
        self.assertIn('RECOVERY_TARGET_RUN_ID: "37531960014"', text)
        self.assertIn(
            'RECOVERY_TARGET_HEAD_SHA: '
            '"a1e194907c273a2fcdddfb4c24d64a96cfd8d263"',
            text,
        )
        self.assertIn('RECOVERY_TARGET_RUN_NUMBER: "383"', text)

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
            "542ace21e77c2bbdf5fec5312556c58d9e641da7",
            "1e80c0a61be899e62ac98540d1c7e0449f105008",
            "17eaaa7bd6f7f25e4c6b553d49b3c2a0bf6412e2",
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
            "0730061851beb76a426f2b3fd470cf1e35eb68d4",
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "37531906353",
            "11445116144",
            "sha256:fc03d22a19fe0cf8cd1348e6f5aad2ee755c4807f0e10cfffe0c0349420ca3b4",
            "11444044655",
            "sha256:bdc4d7ecd42b65f9e461fd1803076aa51f74e57b5d9b4945cfb54f793bb4c839",
        ):
            self.assertIn(value, text)

    def test_recovery_push_is_one_shot_and_exact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn(
            'test "$source_run_id" = "$RECOVERY_DEC589_RUN_ID"',
            text,
        )
        self.assertIn(
            'test "$artifact_id" = "$RECOVERY_DEC589_ARTIFACT_ID"',
            text,
        )
        self.assertIn(
            'test "$artifact_id" = "$RECOVERY_FREEZE_ARTIFACT_ID"',
            text,
        )
        self.assertNotIn("run_384_or_later_authorized = True", text)

    def test_reviewer_requires_successful_dec589_same_head(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a-annual-catalogue-2021-run383-dispatch.yml/runs",
            text,
        )
        self.assertIn('row.get("head_sha") == os.environ["TARGET_HEAD_SHA"]', text)
        self.assertIn('row.get("run_number") == 1', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row.get("conclusion") == "success"', text)
        self.assertIn('"decision"] == "DEC-589"', text)
        self.assertIn('"run_number"] == 383', text)

    def test_reviewer_binds_run383_without_later_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2021_run383_evidence_review.py",
            text,
        )
        self.assertIn('assert binding["decision"] == "DEC-590"', text)
        self.assertIn('assert binding["run_number"] == 383', text)
        self.assertIn(
            'assert binding["previous_annual_freeze_run_id"] == 37443770076',
            text,
        )
        self.assertIn('assert binding["annual_cell_count"] == 18', text)
        self.assertIn(
            'assert binding["directional_record_count"] == 89460',
            text,
        )
        self.assertIn(
            'assert binding["final_required_annual_segment_bound"] is True',
            text,
        )
        self.assertIn(
            'assert binding["cross_year_comparison_authorized"] is False',
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
            "annual-catalogue-2021-dec590-runtime-binding-",
            text,
        )
        self.assertIn(
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_CROSS_YEAR_COMPARISON_PREFLIGHT",
            text,
        )


if __name__ == "__main__":
    unittest.main()
