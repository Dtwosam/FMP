from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2017-dispatch-authorization.yml"
)


class AnnualPatternCatalogue2017DispatchAuthorizationWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2017-dispatch-authorization",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2017-dispatch-authorization.yml",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_exact_dec540_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37223000759",
            "f7983f960ae141f15c83b3cc05f6d6030140c802",
            "11311031268",
            "a54675bd49ef6bb17d32f44b1d21a4adb10b541e3a248f583b05293505ef498d",
            "7329cf4238c1aa8b608d7b4e41eaaaf643f78c3fb99f7ae399f6db303a75ffad",
            "0e048756a1a9ca5f8d45896c6ff212d386996ed0",
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_unconsumed_run379_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert set(by_number) == {1, 376, 377, 378}", text)
        self.assertIn('row.get("run_number") >= 379', text)
        self.assertIn('value["expected_run_number"] == 379', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37206992367',
            text,
        )

    def test_workflow_emits_source_only_authorization(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-541"', text)
        self.assertIn('value["source_only_authorization"] is True', text)
        self.assertIn(
            'value["annual_workflow_dispatch_authorized"] is True',
            text,
        )
        self.assertIn('assert value[field] is False, field', text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("rerun-failed-jobs", text)


if __name__ == "__main__":
    unittest.main()
