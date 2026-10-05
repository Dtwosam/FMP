from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2020-run382-runtime-evidence-recovery.yml"
)


class AnnualPatternCatalogue2020Run382RuntimeEvidenceRecoveryWorkflowTests(
    unittest.TestCase
):
    def test_recovery_reviewer_is_read_only_with_recovery_path(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-run382-runtime-evidence-recovery",
            text,
        )
        self.assertIn("  workflow_run:", text)
        self.assertIn("      - phase8a-annual-pattern-catalogue", text)
        self.assertIn("  workflow_dispatch:", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  actions: write", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("gh api --method POST", text)

    def test_reviewer_requires_exact_successful_run382(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "github.event.workflow_run.run_number == 382",
            text,
        )
        self.assertIn(
            "github.event.workflow_run.conclusion == 'success'",
            text,
        )
        self.assertIn('test "$TARGET_RUN_NUMBER" = "382"', text)
        self.assertIn('"run_number": 382', text)
        self.assertNotIn('test "$TARGET_RUN_NUMBER" = "381"', text)
        self.assertNotIn('"run_number": 381', text)

    def test_reviewer_pins_exact_recovery_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "7c721121197b83e687fd2c76773773f8ab4c07ae",
            "260d38c31182eafaeb64741f447df297b2640ef4",
            "2185ee4597a0255ec607db3ac7ed3acb9cee0aba",
            "cd170c2386034930f53645498f7d24ec13442b71",
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
            "26b2148f0d1f49eb8b817f2b2504a11dcb99199a",
            "695a50b418da752e1bd37d6302f209033ab611f5",
            "4e124365430672fa63825b272001937c60151644",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_reviewer_resolves_successful_dec578_same_head(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a-annual-catalogue-2020-run382-dispatch-recovery.yml/"
            "runs?event=push&branch=main&per_page=100",
            text,
        )
        self.assertIn(
            '== "phase8a-annual-catalogue-2020-run382-dispatch-recovery"',
            text,
        )
        self.assertIn(
            '== ".github/workflows/'
            'phase8a-annual-catalogue-2020-run382-dispatch-recovery.yml"',
            text,
        )
        self.assertIn(
            'row.get("head_sha") == os.environ["TARGET_HEAD_SHA"]',
            text,
        )
        self.assertIn('row.get("run_number") == 1', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row.get("conclusion") == "success"', text)

    def test_reviewer_binds_dec578_receipt_and_dec579_output(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2020-dec578-run382-recovery-dispatch-",
            text,
        )
        self.assertIn(
            "dec578-run382-recovery-dispatch-receipt.json",
            text,
        )
        self.assertIn('receipt["decision"] == "DEC-578"', text)
        self.assertIn(
            'receipt["failed_dispatcher_run_id"] == 37390547252',
            text,
        )
        self.assertIn(
            'receipt["failed_dispatcher_job_id"] == 112034309419',
            text,
        )
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2020_run382_recovery_evidence_review.py",
            text,
        )
        self.assertIn('binding["decision"] == "DEC-579"', text)
        self.assertIn(
            'binding["source_dispatch_receipt_decision"] == "DEC-578"',
            text,
        )
        self.assertIn(
            'binding["recovery_dispatch_receipt_bound"] is True',
            text,
        )
        self.assertIn('binding["run_number"] == 382', text)
        self.assertIn('binding["annual_cell_count"] == 18', text)
        self.assertIn(
            'binding["directional_record_count"] == 89460',
            text,
        )
        self.assertIn(
            'binding["next_segment_execution_authorized"] is False',
            text,
        )
        self.assertIn('binding["trading_authorized"] is False', text)
        self.assertIn(
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2021_EXECUTION_PREFLIGHT",
            text,
        )
        self.assertIn(
            "annual-catalogue-2020-dec579-runtime-binding-recovery-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
