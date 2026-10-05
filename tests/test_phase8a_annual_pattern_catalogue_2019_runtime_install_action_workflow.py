from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2019-runtime-install-action.yml"
)


class AnnualPatternCatalogue2019RuntimeInstallActionWorkflowTests(
    unittest.TestCase
):
    def test_builder_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-runtime-install-action",
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

    def test_builder_pins_exact_dec559_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37295798286",
            "bb1c7901d1b5859bec97a381716166e9024a6022",
            "11338796649",
            "3d8b6933a1949c77a4e6b29df5bd86896a140d0011ba6859187d412df24cc8f9",
            "15cc0c8e3b93453ecaf6ba1dfd635133279acb6c",
            "d406fd01bf308afd9003f29c06d20ff3da4ec3fc",
            "a3b087419f9b9dd8980139f5dc47db4de3f657fd",
            "41e7adba8b5061028d8adc7ef93d1fc02424039e",
            "1c585ad2a2a0bdf3a0fc811376d1fa5701b293b2fd888abca30ea5c13fcf3861",
        ):
            self.assertIn(value, text)

    def test_builder_rechecks_runtime_and_run381_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        current_check = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "410180c34a9e3500bbbb42310a5253b993ac7785"'
        )
        self.assertEqual(text.count(current_check), 1)
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2019_runtime_authorization.py",
            text,
        )
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380}",
            text,
        )
        self.assertIn('row["run_number"] >= 381', text)

    def test_builder_freezes_exact_two_file_action_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["action_count"] == 2', text)
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_2019_runtime_authorization.py"',
            text,
        )
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_runtime.py"',
            text,
        )
        self.assertIn(
            '"d87fe85a5b426fa92caf7d6cc165445590f4097c"',
            text,
        )
        self.assertIn(
            '"07ddfe7a968de10cd1d4f8592760cc9eb9e6300e"',
            text,
        )
        self.assertIn('value["repository_mutation_authorized"] is True', text)
        self.assertIn('"annual_workflow_dispatch_authorized",', text)
        self.assertIn('"trading_authorized",', text)


if __name__ == "__main__":
    unittest.main()
