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


if __name__ == "__main__":
    unittest.main()
