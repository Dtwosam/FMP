from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2020-dispatch-preflight.yml"
)


class AnnualPatternCatalogue2020DispatchPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-dispatch-preflight",
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

    def test_workflow_pins_exact_dec572_install_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37361230835",
            "2d57ea571111845cd58a34a0c25a89eabe233bcb",
            "11367191085",
            "5f0f9862b411a9da4f0c383259ef78dc9df842be4a58ee06c43374a0b774d716",
            "3ee648808bc2982c02dd1cb10fd45911f6379dcb",
            "1f77559f7aadfb83e338e467148d86b2a99850d69909e689f04604fa19c3e7b4",
            "0e796623ddc8b95e62db9d841d658d2b1898eac0",
            "83b914063bb376fecac4d1023c278dbe8b19006b",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_exact_installed_state_and_run382_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "695a50b418da752e1bd37d6302f209033ab611f5",
            text,
        )
        self.assertIn(
            "4e124365430672fa63825b272001937c60151644",
            text,
        )
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381}",
            text,
        )
        self.assertIn('row["run_number"] >= 382', text)
        self.assertIn(
            'git merge-base --is-ancestor "$DEC572_INSTALL_COMMIT_SHA" "$GITHUB_SHA"',
            text,
        )

    def test_workflow_emits_read_only_dec573_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-573"', text)
        self.assertIn('value["expected_run_number"] == 382', text)
        self.assertIn('value["expected_run_attempt"] == 1', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37310525635',
            text,
        )
        self.assertIn('value["annual_workflow_run_count"] == 7', text)
        self.assertIn('value["dispatch_command_present"] is False', text)
        self.assertIn('value["preflight_read_only"] is True', text)
        self.assertIn('"annual_workflow_dispatch_authorized",', text)
        self.assertIn('"trading_authorized",', text)
        self.assertIn(
            "annual-catalogue-2020-dec573-dispatch-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
