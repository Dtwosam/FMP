from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2017-runtime-install-preflight.yml"
)


class AnnualPatternCatalogue2017RuntimeInstallPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2017-runtime-install-preflight",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)

    def test_workflow_pins_concrete_dec536_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37215086807",
            "585feb304ab11ac2fead24eac05233960ba80e0e",
            "11307494750",
            "80395e51c57ca26788ef4291d7cdf1e6e3e79ef6cf92893e9d37d14dd8bc2adc",
            "446fb95265ee222aa40ffa3f11ef869a1ede8090",
            "70c12fb07f1ae950bbcbfd99739fb4ba9dff35d8",
        ):
            self.assertIn(value, text)

    def test_workflow_keeps_run379_unconsumed(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("set(by_number) == {1, 376, 377, 378}", text)
        self.assertIn('row["run_number"] >= 379', text)
        self.assertIn('value["expected_run_number"] == 379', text)
        self.assertIn('"repository_mutation_authorized",', text)
        self.assertIn('"trading_authorized",', text)


if __name__ == "__main__":
    unittest.main()
