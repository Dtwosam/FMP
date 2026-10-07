from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2022-dispatch-authorization.yml"
)


class AnnualPatternCatalogue2022DispatchAuthorizationWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-dispatch-authorization",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_exact_dec597_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37643850671",
            "1fafdacab1df0bc2df24b6fa8cd822b031e5cda8",
            "11492114816",
            "440254694717b13d2fe346a0aae4b247beb02dd9cb18feab7ad6a947968d13d2",
            "090b8c7e9a1e835387bb7e1579d6db902d359e537c67caa1357a1d96ff938c92",
            "015a894dca744889a6fdb56b64190e48c43a13e62c149363e248778660c53481",
            "2f234ac4a420eaacdf7a61007e442d15a61ed374",
            "1d3279f0d2a554d7e57eeb69c2d25be367ffb696",
            "6680b571765622653bf53a006a1cb7126cf7ea80",
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_unconsumed_run383_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        self.assertIn('row.get("run_number") >= 384', text)
        self.assertIn('value["expected_run_number"] == 384', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37531960014',
            text,
        )

    def test_workflow_emits_source_only_authorization(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-598"', text)
        self.assertIn('value["source_only_authorization"] is True', text)
        self.assertIn(
            'value["annual_workflow_dispatch_authorized"] is True',
            text,
        )
        self.assertIn('assert value[field] is False, field', text)
        self.assertIn('"run_385_or_later_authorized",', text)
        self.assertIn('"protected_history_access_authorized",', text)
        self.assertIn('"cross_year_comparison_authorized",', text)
        self.assertIn(
            "phase8a-annual-catalogue-2022-dispatch-preflight-recovery.yml",
            text,
        )
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("rerun-failed-jobs", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)

    def test_workflow_has_no_stale_prior_year_names(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for stale in ("DEC-587", "DEC-586", "dec587", "dec586", "annual_pattern_catalogue_2021"):
            self.assertNotIn(stale, text)


if __name__ == "__main__":
    unittest.main()
