from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2017-runtime-install-action.yml"
)


class AnnualPatternCatalogue2017RuntimeInstallActionWorkflowTests(
    unittest.TestCase
):
    def test_builder_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2017-runtime-install-action",
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

    def test_builder_pins_exact_dec537_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37215789401",
            "f8a8de09adc4b64b84b2129eacbc38d0eb00e645",
            "11308490990",
            "892512ac79d2b372372871a143d887f01e5c96d9ed60ea8243f1cbfb4b7cc6ea",
            "b6fd22c5eca66ca373d0479e63af51cd39068ed9",
            "247b78dd727689494f0c070b3d95d8b296528f96",
        ):
            self.assertIn(value, text)

    def test_builder_rechecks_runtime_and_run379_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py',
            text,
        )
        self.assertIn(
            "b564f5a26fdef146fc6080962e7c4762b0b5949a",
            text,
        )
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2017_runtime_authorization.py",
            text,
        )
        self.assertIn("set(by_number) == {1, 376, 377, 378}", text)
        self.assertIn('row["run_number"] >= 379', text)

    def test_builder_freezes_exact_two_file_action_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["action_count"] == 2', text)
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_2017_runtime_authorization.py"',
            text,
        )
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_runtime.py"',
            text,
        )
        self.assertIn('value["repository_mutation_authorized"] is True', text)
        self.assertIn('"annual_workflow_dispatch_authorized",', text)
        self.assertIn('"trading_authorized",', text)


if __name__ == "__main__":
    unittest.main()
