from __future__ import annotations

import unittest
from pathlib import Path


class Phase1RepairWorkflowTests(unittest.TestCase):
    def test_workflow_exposes_targeted_month_repair_inputs_and_job(self) -> None:
        workflow = Path(".github/workflows/phase1-full-acquisition.yml").read_text(encoding="utf-8")

        self.assertIn("repair_year:", workflow)
        self.assertIn("repair_month:", workflow)
        self.assertIn("targeted-repair:", workflow)
        self.assertIn("--continue-on-error", workflow)
        self.assertIn("Verify targeted repair provenance", workflow)

    def test_full_matrix_manual_dispatch_is_not_implicit_when_repair_inputs_are_set(self) -> None:
        workflow = Path(".github/workflows/phase1-full-acquisition.yml").read_text(encoding="utf-8")

        self.assertIn("inputs.repair_year == ''", workflow)
        self.assertIn("inputs.repair_month == ''", workflow)

    def test_workflow_supports_serial_push_triggered_repair_batch(self) -> None:
        workflow = Path(".github/workflows/phase1-full-acquisition.yml").read_text(encoding="utf-8")

        self.assertIn("docs/phase1-repair-queue.json", workflow)
        self.assertIn("[phase1-repair-batch]", workflow)
        self.assertIn("repair-batch-plan:", workflow)
        self.assertIn("repair-batch:", workflow)
        self.assertIn("fromJSON(needs.repair-batch-plan.outputs.matrix)", workflow)
        self.assertIn("max-parallel: 1", workflow)
        self.assertIn("Verify repair batch month provenance", workflow)

    def test_repair_batch_push_does_not_run_cloud_smoke(self) -> None:
        workflow = Path(".github/workflows/phase1-full-acquisition.yml").read_text(encoding="utf-8")

        self.assertIn(
            "!contains(github.event.head_commit.message, '[phase1-repair-batch]')",
            workflow,
        )

    def test_workflow_supports_exact_gap_batch_without_month_matrix(self) -> None:
        workflow = Path(".github/workflows/phase1-full-acquisition.yml").read_text(encoding="utf-8")

        self.assertIn("docs/phase1-exact-gap-queue.json", workflow)
        self.assertIn("[phase1-exact-gap-batch]", workflow)
        self.assertIn("exact-gap-repair:", workflow)
        self.assertIn("fetch-plan", workflow)
        self.assertIn("verify-plan", workflow)
        self.assertIn("Acquire exact missing chunks only", workflow)
        self.assertIn("Verify exact-gap repair provenance", workflow)

    def test_exact_gap_batch_push_does_not_run_cloud_smoke(self) -> None:
        workflow = Path(".github/workflows/phase1-full-acquisition.yml").read_text(encoding="utf-8")

        self.assertIn(
            "!contains(github.event.head_commit.message, '[phase1-exact-gap-batch]')",
            workflow,
        )

    def test_exact_gap_plan_is_validated_before_source_access(self) -> None:
        workflow = Path(".github/workflows/phase1-full-acquisition.yml").read_text(encoding="utf-8")

        validate_index = workflow.index("Validate exact-gap plan before source access")
        acquire_index = workflow.index("Acquire exact missing chunks only")
        self.assertLess(validate_index, acquire_index)
        self.assertIn("exact_gap_plan_sha256=", workflow)
        self.assertIn("exact_gap_chunks=", workflow)

    def test_exact_gap_batch_rejects_github_reruns(self) -> None:
        workflow = Path(".github/workflows/phase1-full-acquisition.yml").read_text(encoding="utf-8")

        self.assertIn("GITHUB_RUN_ATTEMPT", workflow)
        self.assertIn("regenerate a fresh exact-gap plan", workflow)

    def test_no_source_tag_suppresses_all_push_acquisition_jobs(self) -> None:
        workflow = Path(".github/workflows/phase1-full-acquisition.yml").read_text(encoding="utf-8")

        self.assertIn("[phase1-no-source]", workflow)
        self.assertIn(
            "!contains(github.event.head_commit.message, '[phase1-no-source]')",
            workflow,
        )

    def test_acquisition_trigger_tags_are_mutually_exclusive(self) -> None:
        workflow = Path(".github/workflows/phase1-full-acquisition.yml").read_text(encoding="utf-8")

        self.assertIn(
            "contains(github.event.head_commit.message, '[phase1-full]') && "
            "!contains(github.event.head_commit.message, '[phase1-repair-batch]') && "
            "!contains(github.event.head_commit.message, '[phase1-exact-gap-batch]')",
            workflow,
        )
        self.assertIn(
            "contains(github.event.head_commit.message, '[phase1-repair-batch]') && "
            "!contains(github.event.head_commit.message, '[phase1-full]') && "
            "!contains(github.event.head_commit.message, '[phase1-exact-gap-batch]')",
            workflow,
        )
        self.assertIn(
            "contains(github.event.head_commit.message, '[phase1-exact-gap-batch]') && "
            "!contains(github.event.head_commit.message, '[phase1-full]') && "
            "!contains(github.event.head_commit.message, '[phase1-repair-batch]')",
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
