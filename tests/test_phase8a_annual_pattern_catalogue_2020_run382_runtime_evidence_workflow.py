from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2020-run382-runtime-evidence.yml"
)


class AnnualPatternCatalogue2020Run382RuntimeEvidenceWorkflowTests(
    unittest.TestCase
):
    def test_reviewer_supports_normal_and_recovery_paths(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-run382-runtime-evidence",
            text,
        )
        self.assertIn("  workflow_run:", text)
        self.assertIn("      - phase8a-annual-pattern-catalogue", text)
        self.assertIn("  workflow_dispatch:", text)
        self.assertIn("      target_run_id:", text)
        self.assertIn("      target_head_sha:", text)
        self.assertIn("      target_run_number:", text)
        self.assertIn("github.event.workflow_run.run_number == 382", text)
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
            "10fe71352013d0711e1c032446fc5eba0ec94dff",
            "87445bdcef0731682c121c7f7d32f921c0e1219c",
            "8da7e442ee91e68dc0f4d22947d46c7709f10022",
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
            "26b2148f0d1f49eb8b817f2b2504a11dcb99199a",
            "695a50b418da752e1bd37d6302f209033ab611f5",
            "4e124365430672fa63825b272001937c60151644",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_reviewer_requires_successful_dec576_same_head(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a-annual-catalogue-2020-run382-dispatch.yml/runs",
            text,
        )
        self.assertIn('row.get("head_sha") == os.environ["TARGET_HEAD_SHA"]', text)
        self.assertIn('row.get("run_number") == 1', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row.get("conclusion") == "success"', text)
        self.assertIn('"decision"] == "DEC-576"', text)
        self.assertIn('"run_number"] == 382', text)

    def test_reviewer_binds_run382_without_later_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2020_run382_evidence_review.py",
            text,
        )
        self.assertIn('assert binding["decision"] == "DEC-577"', text)
        self.assertIn('assert binding["run_number"] == 382', text)
        self.assertIn(
            'assert binding["previous_annual_freeze_run_id"] == 37310525635',
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
            "annual-catalogue-2020-dec577-runtime-binding-",
            text,
        )
        self.assertIn(
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2021_EXECUTION_PREFLIGHT",
            text,
        )


if __name__ == "__main__":
    unittest.main()
