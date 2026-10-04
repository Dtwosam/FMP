from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2018-execution-authorization.yml"
)


class AnnualPatternCatalogue2018ExecutionAuthorizationWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-execution-authorization",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  contents: write", text)
        self.assertNotIn("  actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_workflow_pins_exact_dec545_provenance(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37229319220",
            "24fa329cbcf88192cdc19e63173edd55b3aa7eb5",
            "11313083318",
            "sha256:36f76bba9cd3cef5fd1b3236f3bc80ad62029edf9c493ce10d946b7bcadf18a4",
            "55b9378a78f54a99a9055da1ac0294e73c5e02434fc4ad17d38acea7ac5c6315",
            "c50f1480ae6b39764f75974182830f149fc820fc",
            "ed71113733ae0034d81914d4c0ab37efb5c4ce6e",
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_unconsumed_run380_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379}",
            text,
        )
        self.assertIn('row.get("run_number") >= 380', text)
        self.assertIn('value["expected_run_number"] == 380', text)
        self.assertIn('value["expected_run_attempt"] == 1', text)

    def test_workflow_cannot_dispatch_or_mutate_repository(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)
        self.assertNotIn("git add", text)
        self.assertIn('"dispatch_command_present",', text)
        self.assertIn('"dispatch_action_executed",', text)
        self.assertIn('"trading_authorized",', text)
        self.assertIn("assert value[field] is False, field", text)

    def test_workflow_uploads_only_dec546_evidence_bundle(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2018-dec546-execution-authorization-",
            text,
        )
        self.assertIn(
            "dec546-2018-execution-authorization.json",
            text,
        )
        self.assertIn("if-no-files-found: error", text)


if __name__ == "__main__":
    unittest.main()
