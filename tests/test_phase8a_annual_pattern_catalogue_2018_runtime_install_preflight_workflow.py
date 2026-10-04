from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2018-runtime-install-preflight.yml"
)


class AnnualPatternCatalogue2018RuntimeInstallPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-runtime-install-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2018-runtime-install-preflight.yml",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_concrete_dec547_plan_and_targets(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37231060551",
            "1c61ad18d07d6fbc034c20610d7a130e09630a66",
            "11314500352",
            "633476f0bab6a5e1f3165cab44be176c05c01f955569ff0018cae957006ab56c",
            "49e4549672a27bb8d985b0746d8914122072906d",
            "938e805cd36de2582f68b660c0891cee5e865bc1",
            "543752e5ecad05fed0b368170663a9329b0405aa",
            "c50f1480ae6b39764f75974182830f149fc820fc",
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_run380_is_absent(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379}",
            text,
        )
        self.assertIn('row["run_number"] >= 380', text)
        self.assertIn('value["expected_run_number"] == 380', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37227536041',
            text,
        )

    def test_workflow_cannot_dispatch_or_mutate(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)
        self.assertIn('value["preflight_read_only"] is True', text)
        self.assertIn('"repository_mutation_authorized",', text)
        self.assertIn('"trading_authorized",', text)


if __name__ == "__main__":
    unittest.main()
