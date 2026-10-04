from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2018-dispatch-preflight.yml"
)


class AnnualPatternCatalogue2018DispatchPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-dispatch-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)

    def test_workflow_pins_exact_dec550_install_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37233054691",
            "11048bd278bbf8f3697571aaff40c27656449a6c",
            "11314488545",
            "8b9732b24a5ef6163d8ab54f34d058eecd9e1c4ce1a68c79a88306178933df2d",
            "1fc73dfc1e102996cecd5b9ffcb75d3ab4fa3ade",
            "171056b861bf3e795271cd04631b4f8fdba7a827",
            "a941a09da38674ca08a33204d743ea2580bb8357",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_exact_installed_state_and_run380_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
            text,
        )
        self.assertIn(
            "410180c34a9e3500bbbb42310a5253b993ac7785",
            text,
        )
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379}",
            text,
        )
        self.assertIn('row["run_number"] >= 380', text)
        self.assertIn(
            'git merge-base --is-ancestor "$DEC550_INSTALL_COMMIT_SHA" "$GITHUB_SHA"',
            text,
        )

    def test_workflow_emits_read_only_dec551_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-551"', text)
        self.assertIn('value["expected_run_number"] == 380', text)
        self.assertIn('value["expected_run_attempt"] == 1', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37227536041',
            text,
        )
        self.assertIn('value["annual_workflow_run_count"] == 5', text)
        self.assertIn('value["dispatch_command_present"] is False', text)
        self.assertIn('value["preflight_read_only"] is True', text)
        self.assertIn('"annual_workflow_dispatch_authorized",', text)
        self.assertIn('"trading_authorized",', text)
        self.assertIn(
            "annual-catalogue-2018-dec551-dispatch-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
