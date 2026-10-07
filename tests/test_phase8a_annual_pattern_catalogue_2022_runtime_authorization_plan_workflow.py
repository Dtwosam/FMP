from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2022-runtime-authorization-plan.yml"
)


class AnnualCatalogue2022RuntimeAuthorizationPlanWorkflowTests(unittest.TestCase):
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
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_workflow_pins_exact_dec592_and_templates(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37608559036",
            "0d9b8deec0b6cd26f447596fc59a682f7c536e0b",
            "11475911390",
            "sha256:a70abd5972c0aa78459c6540ffc863f0a463183e880baa8b96752b0336fd5d85",
            "5365ca95855d97df7ad28ff7d4e6f5c2ec51183899da7f88048d78b5d381bf54",
            "b335202460f6cd61d30f54717c97de5451fdc251e08fab45beffccdd2bd5df3d",
            "d7710ab16dde2eea6b0d93dc6387c6cc489b30d7",
            "fc1c5fe9d6dbbb7ecb6441fb4292fef00fab6f2f",
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        ):
            self.assertIn(value, text)

    def test_workflow_rejects_run384_or_later_before_plan(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 9", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        self.assertIn(
            'assert not any(row["run_number"] >= 384 for row in rows)',
            text,
        )

    def test_workflow_emits_only_dormant_plan(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Build concrete DEC-593 runtime authorization plan", text)
        self.assertIn('assert value["plan_source_only"] is True', text)
        self.assertIn('"repository_mutation_authorized"', text)
        self.assertIn('"annual_workflow_dispatch_authorized"', text)
        self.assertIn('"run_385_or_later_authorized"', text)
        self.assertIn('"protected_history_access_authorized"', text)
        self.assertIn('"cross_year_comparison_authorized"', text)
        self.assertIn("assert value[field] is False, field", text)
        self.assertIn(
            "annual-catalogue-2022-dec593-runtime-authorization-plan-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
