from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2020-run382-runtime-evidence-recovery-push.yml"
)


class AnnualPatternCatalogue2020Run382RuntimeEvidenceRecoveryPushTests(
    unittest.TestCase
):
    def test_recovery_is_first_push_read_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-run382-runtime-evidence-recovery-push",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_recovery_pins_exact_run382_and_dec578_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37443770076",
            "681e81e021d4970a67b18370142d55b17ec68864",
            "37443726793",
            "11402975356",
            "sha256:2f0c084420cff57989cc72f79b68dc63d730a5df29c6cbf03d30e2e70f75f25a",
            "11402652816",
            "sha256:c42e50f8eba75f9626e179d6567ce78e9849393975ff59c8a1bc2e8a8a73e183",
            "135e2d329ea1c3bf4b3e8e4fa3bfc8a0712471a8e347f905172767cba8ca058a",
            "53cd4475b2e9f70252bc4962666ce421daf7795d3e78defbb38ec948448e1c3c",
        ):
            self.assertIn(value, text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382}",
            text,
        )
        self.assertIn('assert not any(row["run_number"] >= 383', text)

    def test_recovery_requires_absent_original_dec579_run(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a-annual-catalogue-2020-run382-runtime-evidence-recovery.yml/runs?per_page=100",
            text,
        )
        self.assertIn("assert prior == []", text)

    def test_recovery_reuses_frozen_dec579_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for blob in (
            "7c721121197b83e687fd2c76773773f8ab4c07ae",
            "260d38c31182eafaeb64741f447df297b2640ef4",
            "cd170c2386034930f53645498f7d24ec13442b71",
            "74074bf13937f93e0f8014066e04151fce90893f",
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
            "26b2148f0d1f49eb8b817f2b2504a11dcb99199a",
            "695a50b418da752e1bd37d6302f209033ab611f5",
            "4e124365430672fa63825b272001937c60151644",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(blob, text)

    def test_recovery_has_no_execution_mutation_surface(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("rerun-failed-jobs", text)
        self.assertNotIn("gh api --method POST", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)

    def test_recovery_binds_dec579_and_keeps_all_authority_false(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('binding["decision"] == "DEC-579"', text)
        self.assertIn('binding["run_id"] == 37443770076', text)
        self.assertIn('binding["run_number"] == 382', text)
        self.assertIn('binding["run_attempt"] == 1', text)
        self.assertIn(
            'binding["source_dispatch_receipt_decision"] == "DEC-578"',
            text,
        )
        self.assertIn(
            'binding["recovery_dispatch_receipt_bound"] is True',
            text,
        )
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
            "annual-catalogue-2020-dec579-runtime-binding-recovery-push-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
