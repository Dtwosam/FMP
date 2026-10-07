from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2022-execution-authorization.yml"
)


class AnnualCatalogue2022ExecutionAuthorizationWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_source_only_first_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-execution-authorization",
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
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("gh api --method POST", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2022_runtime_authorization.py",
            text,
        )

    def test_workflow_pins_concrete_dec591_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37603215074",
            "ed7589b1e63591c6508271ff75dcfc7a63893421",
            "11474170578",
            "sha256:cc129455cda4fe6ec8835f436abc3ef39f009d073a4dc2efac859313f753cd50",
            "4dcd96a91c673559f0aecbb0e8cf61c437fb49e0f1831ebb9fc40d4428a1bdda",
            "c8a481c2040ad6d61e74c1624c6b040b968854da25304e0c4ee6877451480b60",
            "e68e9f1ee41ca89f0ae3d7758d59b4ce8c5823bb",
            "a52661d8abd910856bc5260898a7f21cc4958f94",
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_exact_history_before_run384(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 9", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        for run_id in (
            "37126711695",
            "37191637168",
            "37198002653",
            "37206992367",
            "37227536041",
            "37237817538",
            "37310525635",
            "37443770076",
            "37531960014",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            'assert not any(row["run_number"] >= 384 for row in rows)',
            text,
        )

    def test_workflow_builds_only_source_authorization(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Build concrete DEC-592 authorization", text)
        self.assertIn("Install pinned authorization dependencies", text)
        self.assertIn("requirements/exp061-discovery-run.txt", text)
        self.assertIn("scikit-learn==1.9.1", text)
        self.assertIn('assert value["decision"] == "DEC-592"', text)
        self.assertIn('assert value["annual_segment_label"] == "2022"', text)
        self.assertIn('assert value["prior_segment_label"] == "2021"', text)
        self.assertIn(
            'assert value["previous_annual_freeze_run_id"] == 37531960014',
            text,
        )
        self.assertIn('assert value["expected_run_number"] == 384', text)
        self.assertIn(
            'assert value["annual_workflow_dispatch_authorized"] is True',
            text,
        )
        self.assertIn('assert value["source_only_authorization"] is True', text)
        self.assertIn('"run_385_or_later_authorized"', text)
        self.assertIn('"protected_history_access_authorized"', text)
        self.assertIn('"cross_year_comparison_authorized"', text)
        self.assertIn("assert value[field] is False, field", text)
        self.assertIn(
            "annual-catalogue-2022-dec592-execution-authorization-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
