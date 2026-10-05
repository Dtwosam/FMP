from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2020-runtime-install-action.yml"
)


class AnnualPatternCatalogue2020RuntimeInstallActionWorkflowTests(
    unittest.TestCase
):
    def test_builder_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-runtime-install-action",
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

    def test_builder_pins_exact_dec570_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37321690650",
            "6b8f0015a0d38276356b3370d73d4d6a26c9e644",
            "11350136423",
            "97eee3d49aec78ebbc1f3aa7190159d4dfba62c861f221163bd03c2699fdad7c",
            "07c6cb7108e04a3f01707466f6a7912d01cfcc2a",
            "098b0fecfae04eb46762e6bb240719e4a10b9473",
            "cb7df2aa6601c0ca81678ce700aad315a336ceaa",
            "cd420419cb149c23056edfcaf650d4d7e2d3775a",
            "367ec514057b011711ab9734a839f8cf03d1334125db336c947e979d923cab36",
        ):
            self.assertIn(value, text)

    def test_builder_rechecks_runtime_and_run382_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        current_check = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e"'
        )
        self.assertEqual(text.count(current_check), 2)
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2020_runtime_authorization.py",
            text,
        )
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381}",
            text,
        )
        self.assertIn('row["run_number"] >= 382', text)

    def test_builder_freezes_exact_two_file_action_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["action_count"] == 2', text)
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_2020_runtime_authorization.py"',
            text,
        )
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_runtime.py"',
            text,
        )
        self.assertIn(
            '"695a50b418da752e1bd37d6302f209033ab611f5"',
            text,
        )
        self.assertIn(
            '"4e124365430672fa63825b272001937c60151644"',
            text,
        )
        self.assertIn('value["repository_mutation_authorized"] is True', text)
        self.assertIn('"annual_workflow_dispatch_authorized",', text)
        self.assertIn('"trading_authorized",', text)


if __name__ == "__main__":
    unittest.main()
