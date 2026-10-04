from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2017-execution-preflight.yml"
)


class AnnualCatalogue2017ExecutionPreflightWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_one_shot_preflight(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2017-execution-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "2"', text)
        self.assertIn("PYTHONPATH: ${{ github.workspace }}/src", text)
        self.assertIn("37209674158", text)
        self.assertIn("0d6640f4833f2ddf377e4004cce9df7ea845f7da", text)

    def test_workflow_pins_exact_dec522_artifact_and_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37208993431",
            "11305284883",
            "sha256:6282a6765f659a5a5801e2b1c8804d0dd23b96c4f235a770cd8e0e6053caab8c",
            "c95d28505fab6a8c55c9889ba5da6565be3b63cb98321eea58d26196b60a2b40",
            "01e15f5081523136af12af7ccc443b79c44d102732a31cb9075a29ea67e80b99",
            "7e6e6a54d4111a44a68218e551c379fa342d3e27",
            "0d22cd83b38c9a976ac98534d9fa9e4b626808b7",
            "ad182ce30d32aff985558f3b2fd9370ca1141cc2",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_exact_four_run_history(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 4", text)
        self.assertIn("assert set(by_number) == {1, 376, 377, 378}", text)
        self.assertIn("37126711695", text)
        self.assertIn("37191637168", text)
        self.assertIn("37198002653", text)
        self.assertIn("37206992367", text)

    def test_workflow_freezes_2017_at_run379_without_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert value["expected_next_run_number"] == 379', text)
        self.assertIn('assert value["expected_next_run_attempt"] == 1', text)
        self.assertIn('assert value["preflight_read_only"] is True', text)
        self.assertIn("assert value[field] is False, field", text)
        self.assertIn(
            "annual-catalogue-2017-dec534-execution-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
