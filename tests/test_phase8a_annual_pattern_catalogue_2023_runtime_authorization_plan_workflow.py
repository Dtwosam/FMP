from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2023-runtime-authorization-plan.yml"
)


class AnnualCatalogue2023RuntimeAuthorizationPlanWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_source_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
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

    def test_workflow_pins_recovered_dec603_and_templates(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37685394468",
            "a4235aa2bc8501da8a7273d80a133e712cd04721",
            "11511180606",
            "sha256:ee25e982971a0c3ce65f4a6b25a2229e35e7a2f3285b30f2bfcdff87734c311a",
            "dc1f6dc96e4bdbf527ffba49be9df175310389737bd7c70ca945bd260baf3946",
            "aa9b4e8c4bceee20f5d03d8579e1b0407bc21b6597528707f003f5f0bc5aef7d",
            "phase8a-annual-catalogue-2023-execution-authorization-recovery",
            "fe5c18f8ffa5e3d698f91060ec8c28e0d0692318",
            "9176e4e1e8d55751af3b444bd804ef3f5fc08f3d",
            "2c4292abadbffb9dd87edaab67d9e32783facae7",
            "d7e0823bc0d7513b6d7ee27a02fb5b519bc4818b",
            "f2734c7ea32355b1024d1097812578b23fc4409d",
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        ):
            self.assertIn(value, text)

    def test_workflow_rejects_run385_or_later_before_plan(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 10", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383, 384}",
            text,
        )
        self.assertIn(
            '384: (37663157285, "success", '
            '"dd79687adc4ec179c56f91939cb600e6746fab5d")',
            text,
        )
        self.assertIn(
            'assert not any(row["run_number"] >= 385 for row in rows)',
            text,
        )

    def test_workflow_emits_only_dormant_protected_plan(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Build concrete DEC-604 runtime authorization plan", text)
        self.assertIn('assert value["plan_source_only"] is True', text)
        self.assertIn(
            'assert value["source_authorization_protected_history_access_authorized"] '
            'is True',
            text,
        )
        self.assertIn('assert value["protected_catalogue_segment"] is True', text)
        self.assertIn(
            'assert value["protocol_full_collection_catalogue_use_authorized"] '
            'is True',
            text,
        )
        self.assertIn(
            'assert value["protocol_2023_2026_catalogue_use_authorized"] is True',
            text,
        )
        self.assertIn('"repository_mutation_authorized"', text)
        self.assertIn('"annual_workflow_dispatch_authorized"', text)
        self.assertIn('"run_386_or_later_authorized"', text)
        self.assertIn('"protected_history_access_authorized"', text)
        self.assertIn('"cross_year_comparison_authorized"', text)
        self.assertIn("assert value[field] is False, field", text)
        self.assertIn(
            "annual-catalogue-2023-dec604-runtime-authorization-plan-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
