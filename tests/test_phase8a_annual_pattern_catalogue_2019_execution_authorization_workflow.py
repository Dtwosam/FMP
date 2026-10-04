from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2019-execution-authorization.yml"
)


class AnnualPatternCatalogue2019ExecutionAuthorizationWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-execution-authorization",
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

    def test_workflow_pins_exact_dec556_provenance(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37240728378",
            "9fa3446b389cbbe1c8429968032ae573198e78b2",
            "11317461212",
            "sha256:09be3f1d11e77ab6da407a67346a6ff4d4ce631f4acb6265575da6db64eeb202",
            "3d311b8d8d387aca00f079bdab6b0531cf17aefc36913165cfb5eb265ad50421",
            "084fa62c7fd4855fc561038d991e1215df2ff73b",
            "a813a8db59927eaf9108e010a5db84f6c6dafa27",
            "410180c34a9e3500bbbb42310a5253b993ac7785",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_unconsumed_run381_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 6", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380}",
            text,
        )
        self.assertIn('379: (37227536041, "success")', text)
        self.assertIn('380: (37237817538, "success")', text)
        self.assertIn('row.get("run_number") >= 381', text)
        self.assertIn('value["expected_run_number"] == 381', text)
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
        self.assertIn('"run_382_or_later_authorized",', text)
        self.assertIn('"trading_authorized",', text)
        self.assertIn("assert value[field] is False, field", text)

    def test_workflow_uploads_only_dec557_evidence_bundle(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("dec545", text)
        self.assertNotIn("dec546", text)
        self.assertIn(
            "annual-catalogue-2019-dec557-execution-authorization-",
            text,
        )
        self.assertIn(
            "dec557-2019-execution-authorization.json",
            text,
        )
        self.assertIn("if-no-files-found: error", text)


if __name__ == "__main__":
    unittest.main()
