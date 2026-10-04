from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2018-runtime-install-action.yml"
)


class AnnualPatternCatalogue2018RuntimeInstallActionWorkflowTests(
    unittest.TestCase
):
    def test_builder_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-runtime-install-action",
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

    def test_builder_pins_exact_dec548_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37231591329",
            "4f21ed0efa53beccc722a7180661e11603e6f14a",
            "11314511176",
            "993afb2809aa675ee2df789a402cc736a5f4992f906394a2f9161ba66675887c",
            "23abea26faf35d775d4f11a41ccf280d10eb78fd",
            "b91f76ca53381a732ff721ceeb6832eff22b028a",
            "49e4549672a27bb8d985b0746d8914122072906d",
            "543752e5ecad05fed0b368170663a9329b0405aa",
        ):
            self.assertIn(value, text)

    def test_builder_rechecks_runtime_and_run380_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        current_check = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"'
        )
        self.assertEqual(text.count(current_check), 2)
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2018_runtime_authorization.py",
            text,
        )
        self.assertIn("set(by_number) == {1, 376, 377, 378, 379}", text)
        self.assertIn('row["run_number"] >= 380', text)

    def test_builder_freezes_exact_two_file_action_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["action_count"] == 2', text)
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_2018_runtime_authorization.py"',
            text,
        )
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_runtime.py"',
            text,
        )
        self.assertIn(
            '"cd50f50156cf74c34cd97d69d24291dc373b390f"',
            text,
        )
        self.assertIn(
            '"410180c34a9e3500bbbb42310a5253b993ac7785"',
            text,
        )
        self.assertIn('value["repository_mutation_authorized"] is True', text)
        self.assertIn('"annual_workflow_dispatch_authorized",', text)
        self.assertIn('"trading_authorized",', text)


if __name__ == "__main__":
    unittest.main()
