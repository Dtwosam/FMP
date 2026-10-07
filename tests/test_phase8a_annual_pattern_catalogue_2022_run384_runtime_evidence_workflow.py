from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2022-run384-runtime-evidence.yml"
)


class AnnualPatternCatalogue2022Run384RuntimeEvidenceWorkflowTests(
    unittest.TestCase
):
    def test_reviewer_supports_normal_and_recovery_paths(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-run384-runtime-evidence",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("    branches:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "phase8a-annual-catalogue-2022-run384-runtime-evidence.yml",
            text,
        )
        self.assertIn("  workflow_run:", text)
        self.assertIn("      - phase8a-annual-pattern-catalogue", text)
        self.assertIn("  workflow_dispatch:", text)
        self.assertIn("      target_run_id:", text)
        self.assertIn("      target_head_sha:", text)
        self.assertIn("      target_run_number:", text)
        self.assertIn("github.event.workflow_run.run_number == 384", text)
        self.assertIn(
            "github.event.workflow_run.conclusion == 'success'",
            text,
        )
        self.assertIn("github.event_name == 'push'", text)
        self.assertIn('RECOVERY_TARGET_RUN_ID: "37663157285"', text)
        self.assertIn(
            'RECOVERY_TARGET_HEAD_SHA: '
            '"dd79687adc4ec179c56f91939cb600e6746fab5d"',
            text,
        )
        self.assertIn('RECOVERY_TARGET_RUN_NUMBER: "384"', text)

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
            "7048781474ce74b8bbed0fd380f8edf4ec51491d",
            "2d6a436c61b13fbd502b3807dc98087bcfa7ccea",
            "818cf0bb73cc7cd479e8718e3f868c05a17fcccf",
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
            "34a805b3ab9038e847097f51a3fcc1d5c1806a53",
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
            "f2734c7ea32355b1024d1097812578b23fc4409d",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "37663125699",
            "11501542840",
            "sha256:98ed52875dd04ab9880641d5f6b81af750a9f70e872d6d50f835cd16b2fbf600",
            "11502162657",
            "sha256:9756c9d4bf9a3579b4495b03867adce774f78735203f66c3efef6792cc600ae9",
        ):
            self.assertIn(value, text)

    def test_recovery_push_is_one_shot_and_exact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn(
            'test "$source_run_id" = "$RECOVERY_DEC600_RUN_ID"',
            text,
        )
        self.assertIn(
            'test "$artifact_id" = "$RECOVERY_DEC600_ARTIFACT_ID"',
            text,
        )
        self.assertIn(
            'test "$artifact_id" = "$RECOVERY_FREEZE_ARTIFACT_ID"',
            text,
        )
        self.assertIn('assert receipt["run_number"] == 384', text)
        self.assertNotIn('assert receipt["run_number"] == 383', text)
        self.assertNotIn("run_385_or_later_authorized = True", text)

    def test_reviewer_requires_successful_dec600_same_head(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a-annual-catalogue-2022-run384-dispatch.yml/runs",
            text,
        )
        self.assertIn('row.get("head_sha") == os.environ["TARGET_HEAD_SHA"]', text)
        self.assertIn('row.get("run_number") == 1', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row.get("conclusion") == "success"', text)
        self.assertIn('"decision"] == "DEC-600"', text)
        self.assertIn('"run_number"] == 384', text)

    def test_reviewer_binds_run384_without_later_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2022_run384_evidence_review.py",
            text,
        )
        self.assertIn('assert binding["decision"] == "DEC-601"', text)
        self.assertIn('assert binding["run_number"] == 384', text)
        self.assertIn(
            'assert binding["previous_annual_freeze_run_id"] == 37531960014',
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
            'assert binding["rerun_authorized"] is False',
            text,
        )
        self.assertIn(
            'assert binding["retry_authorized"] is False',
            text,
        )
        self.assertIn(
            'assert binding["replacement_run_authorized"] is False',
            text,
        )
        self.assertIn(
            'assert binding["run_385_or_later_authorized"] is False',
            text,
        )
        self.assertIn(
            'assert binding["protected_history_access_authorized"] is False',
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
            "annual-catalogue-2022-dec601-runtime-binding-",
            text,
        )
        self.assertIn(
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_CROSS_YEAR_COMPARISON_PREFLIGHT",
            text,
        )


if __name__ == "__main__":
    unittest.main()
