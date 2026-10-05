from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2019-runtime-install-preflight.yml"
)


class AnnualPatternCatalogue2019RuntimeInstallPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-runtime-install-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2019-runtime-install-preflight.yml",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_concrete_dec558_plan_and_targets(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37294642532",
            "2e8d66e515b9f87023f78ae06c644bf804440501",
            "11337484835",
            "7ee0dbfd168a8a63664419cce85e41a65fde46f9e492dbee65868386d74975a8",
            "a3b087419f9b9dd8980139f5dc47db4de3f657fd",
            "80423970c62f71ac9a426e4c4d0190419a99c3c2",
            "41e7adba8b5061028d8adc7ef93d1fc02424039e",
            "084fa62c7fd4855fc561038d991e1215df2ff73b",
            "410180c34a9e3500bbbb42310a5253b993ac7785",
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_run381_is_absent(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380}",
            text,
        )
        self.assertIn('by_number[380]["conclusion"] == "success"', text)
        self.assertIn('row["run_number"] >= 381', text)
        self.assertIn('value["expected_run_number"] == 381', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37237817538',
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
