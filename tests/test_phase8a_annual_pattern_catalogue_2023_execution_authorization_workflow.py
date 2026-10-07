from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2023-execution-authorization.yml"
)


class AnnualCatalogue2023ExecutionAuthorizationWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_source_only_first_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2023-execution-authorization",
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
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2023_runtime_authorization.py",
            text,
        )

    def test_workflow_pins_concrete_dec602_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37678209687",
            "c9d61bdd982eac727ece651be754310d7871cfa7",
            "11507656390",
            "sha256:519c9e963df4def2011fab65c49ca909b3f7a24aacb5b09a1b8582d51cc6a8a5",
            "dc63a0265b9e2b00625431b3d48c9625ed077047bc505caac04c692890198db4",
            "4ed1e69320a4e66dd11454f35f39abbca43f14c74f8d6b52de672257a1ba658e",
            "2c4292abadbffb9dd87edaab67d9e32783facae7",
            "d7e0823bc0d7513b6d7ee27a02fb5b519bc4818b",
            "f2734c7ea32355b1024d1097812578b23fc4409d",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_exact_history_before_run385(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 10", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383, 384}",
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
            "37663157285",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            'assert not any(row["run_number"] >= 385 for row in rows)',
            text,
        )

    def test_workflow_builds_only_protected_source_authorization(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Build concrete DEC-603 authorization", text)
        self.assertIn("Install pinned authorization dependencies", text)
        self.assertIn("requirements/exp061-discovery-run.txt", text)
        self.assertIn("scikit-learn==1.9.1", text)
        self.assertIn('assert value["decision"] == "DEC-603"', text)
        self.assertIn('assert value["annual_segment_label"] == "2023"', text)
        self.assertIn('assert value["prior_segment_label"] == "2022"', text)
        self.assertIn(
            'assert value["previous_annual_freeze_run_id"] == 37663157285',
            text,
        )
        self.assertIn('assert value["expected_run_number"] == 385', text)
        self.assertIn(
            'assert value["annual_workflow_dispatch_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert value["historical_artifact_read_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert value["historical_catalogue_execution_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert value["historical_result_production_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert value["protected_history_access_authorized"] is True',
            text,
        )
        self.assertIn('assert value["source_only_authorization"] is True', text)
        self.assertIn('assert value["protected_catalogue_segment"] is True', text)
        self.assertIn(
            'assert value["protocol_full_collection_catalogue_use_authorized"] is True',
            text,
        )
        self.assertIn(
            'assert value["protocol_2023_2026_catalogue_use_authorized"] is True',
            text,
        )
        self.assertIn('"run_386_or_later_authorized"', text)
        self.assertIn('"cross_year_comparison_authorized"', text)
        self.assertIn("assert value[field] is False, field", text)
        self.assertIn(
            "annual-catalogue-2023-dec603-execution-authorization-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
