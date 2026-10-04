from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2017-execution-authorization.yml"
)


class AnnualPatternCatalogue2017ExecutionAuthorizationWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2017-execution-authorization",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "phase8a-annual-catalogue-2017-execution-authorization.yml",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  contents: write", text)
        self.assertNotIn("  actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_exact_dec534_provenance(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37210041270",
            "23231c82360da824e3b9eedbd4e2a5edcffd0d45",
            "11306121033",
            "sha256:531c468e36ac80f6c0c24620c14b78d2b2faad869d53be098efe7a2b31425e04",
            "ef70a0aec215943a2d992a484fd95feb390c6e07",
            "7e6e6a54d4111a44a68218e551c379fa342d3e27",
            "b564f5a26fdef146fc6080962e7c4762b0b5949a",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_unconsumed_run379_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert set(by_number) == {1, 376, 377, 378}", text)
        self.assertIn("row.get(\"run_number\") >= 379", text)
        self.assertIn('value["expected_run_number"] == 379', text)
        self.assertIn('value["expected_run_attempt"] == 1', text)

    def test_workflow_cannot_dispatch_or_mutate_repository(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)
        self.assertNotIn("git add", text)
        self.assertIn('value["dispatch_command_present"]', text)
        self.assertIn('value["dispatch_action_executed"]', text)
        self.assertIn('value["trading_authorized"]', text)

    def test_workflow_uploads_only_dec535_evidence_bundle(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2017-dec535-execution-authorization-",
            text,
        )
        self.assertIn(
            "dec535-2017-execution-authorization.json",
            text,
        )
        self.assertIn("if-no-files-found: error", text)


if __name__ == "__main__":
    unittest.main()
