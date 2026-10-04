from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2017-dispatch-preflight.yml"
)


class AnnualPatternCatalogue2017DispatchPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2017-dispatch-preflight",
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

    def test_workflow_pins_exact_dec539_install_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37219929487",
            "9c3e2e6042b5a00109ee1f07ad6fd24c9ac33308",
            "11309927463",
            "6672b0642a763424541d971d84b273f8c2fde5089fcd736e6152fe8dc9a7e32e",
            "dcdf7210b0039077efa3a23c65c2ed8fa41e2427",
            "613d04ca8c543c67a6f210abc6e333a5c87c519e",
            "0650e9ef326cc5517fcc3b19d1811062a51dd857",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_exact_installed_state_and_run379_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
            text,
        )
        self.assertIn(
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
            text,
        )
        self.assertIn("set(by_number) == {1, 376, 377, 378}", text)
        self.assertIn('row["run_number"] >= 379', text)
        self.assertIn(
            'git merge-base --is-ancestor "$DEC539_INSTALL_COMMIT_SHA" "$GITHUB_SHA"',
            text,
        )

    def test_workflow_emits_read_only_dec540_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-540"', text)
        self.assertIn('value["expected_run_number"] == 379', text)
        self.assertIn('value["expected_run_attempt"] == 1', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37206992367',
            text,
        )
        self.assertIn('value["dispatch_command_present"] is False', text)
        self.assertIn('value["preflight_read_only"] is True', text)
        self.assertIn(
            '"annual_workflow_dispatch_authorized",',
            text,
        )
        self.assertIn('"trading_authorized",', text)
        self.assertIn(
            "annual-catalogue-2017-dec540-dispatch-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
