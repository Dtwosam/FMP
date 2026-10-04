from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2018-runtime-authorization-plan.yml"
)


class AnnualPatternCatalogue2018RuntimeAuthorizationPlanWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-runtime-authorization-plan",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2018-runtime-authorization-plan.yml",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_concrete_dec546_evidence_and_templates(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37229862532",
            "8440244e1c77ecaf5773427d6d4efcd1a7d4dc16",
            "11313482812",
            "79e9bd2485160dd59fbb88a2d50f32a52b6cfd573f80555a8716fde4ea18c71e",
            "34fe76b3bd30d054853b43f660f996757e8bdb30793c03ad6937cc3078b427a0",
            "543752e5ecad05fed0b368170663a9329b0405aa",
            "411cc7022cd6a8acf9ccd13c83abf09cd76173f2",
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_run380_is_absent(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("set(by_number) == {1, 376, 377, 378, 379}", text)
        self.assertIn('row["run_number"] >= 380', text)
        self.assertIn('value["expected_run_number"] == 380', text)
        self.assertIn(
            'value["expected_previous_annual_freeze_run_id"] == 37227536041',
            text,
        )

    def test_workflow_cannot_dispatch_or_mutate(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)
        self.assertIn('value["plan_source_only"] is True', text)
        self.assertIn('"trading_authorized",', text)


if __name__ == "__main__":
    unittest.main()
