from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2020-runtime-authorization-plan.yml"
)


class AnnualPatternCatalogue2020RuntimeAuthorizationPlanWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-runtime-authorization-plan",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2020-runtime-authorization-plan.yml",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_concrete_dec568_evidence_and_templates(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37315889656",
            "d4031faa3dc1f2a01882b222fc82292c7305822f",
            "11346849851",
            "a03cd0d85672e8ae760b8490982fe93f541738c68b733860f10bb16caf968308",
            "cfd43db91d2703e743132e61540ed95acec11fc9d4f6f89d8a8c011345a95f55",
            "143f04dd282c0527586c9f4165bc26b17a1c4a3a",
            "3e55a5f600df9cfe28e8de0e3971304f5ba55ab7",
            "270fea87dd298888f224f605a88e66215ae06911",
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
            "f59b06f9ac0fd51742f3771b6875f22872ffefcd",
            "4e124365430672fa63825b272001937c60151644",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_run382_is_absent(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381}",
            text,
        )
        self.assertIn('by_number[381]["conclusion"] == "success"', text)
        self.assertIn('row["run_number"] >= 382', text)
        self.assertIn('value["expected_run_number"] == 382', text)
        self.assertIn(
            'value["expected_previous_annual_freeze_run_id"] == 37310525635',
            text,
        )
        self.assertIn('"run_number": 1', text)

    def test_workflow_uses_dec568_and_dec569_names_consistently(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2020-dec568-execution-authorization-",
            text,
        )
        self.assertIn(
            "annual-catalogue-2020-dec569-runtime-authorization-plan-",
            text,
        )
        self.assertIn("dec568-2020-execution-authorization.json", text)
        self.assertIn("dec569-2020-runtime-authorization-plan.json", text)
        self.assertNotIn("dec557", text)
        self.assertNotIn("dec558", text)

    def test_workflow_cannot_dispatch_or_mutate(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)
        self.assertIn('value["plan_source_only"] is True', text)
        self.assertIn('"trading_authorized",', text)


if __name__ == "__main__":
    unittest.main()
