from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2017-runtime-authorization-plan.yml"
)


class AnnualPatternCatalogue2017RuntimeAuthorizationPlanWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2017-runtime-authorization-plan",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2017-runtime-authorization-plan.yml",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_concrete_dec535_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37213629059",
            "3283a51a41e4c3f71079be9ab9758fa739ab87b2",
            "11307204031",
            "db62ce19a4f0805fa8255cdc25a1b3e8e35883e2aead2f98569077221273bb8c",
            "441b411cdae5b541226d3c0ef88b6cf687ce70da",
            "8dbf24b1b81fa6173fe74c43bc648ede2a7f3a01",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_run379_is_absent(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("set(by_number) == {1, 376, 377, 378}", text)
        self.assertIn('row["run_number"] >= 379', text)
        self.assertIn('value["expected_run_number"] == 379', text)
        self.assertIn(
            'value["expected_previous_annual_freeze_run_id"] == 37206992367',
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
