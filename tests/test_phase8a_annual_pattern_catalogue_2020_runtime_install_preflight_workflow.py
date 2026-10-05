from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2020-runtime-install-preflight.yml"
)


class AnnualPatternCatalogue2020RuntimeInstallPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-runtime-install-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2020-runtime-install-preflight.yml",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_corrected_dec569_plan_and_targets(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37318488687",
            "9f95010b402ce8413833dcdd5d051b2b45e795e7",
            "11349042014",
            "855375a850fe4e90475f5f9dd4d4721fba5bbac6ce8162d3c9d6d3854bbc7f",
            "cb7df2aa6601c0ca81678ce700aad315a336ceaa",
            "4a577f814733051b560591e8cf3c054b43fdbff1",
            "cd420419cb149c23056edfcaf650d4d7e2d3775a",
            "270fea87dd298888f224f605a88e66215ae06911",
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
            "695a50b418da752e1bd37d6302f209033ab611f5",
            "4e124365430672fa63825b272001937c60151644",
        ):
            self.assertIn(value, text)
        self.assertIn('"run_number": 2', text)
        self.assertIn(
            "annual-catalogue-2020-dec569-runtime-authorization-plan-",
            text,
        )
        self.assertIn("dec568-2020-execution-authorization.json", text)
        self.assertIn("dec569-2020-runtime-authorization-plan.json", text)
        self.assertIn("dec570-2020-runtime-install-preflight.json", text)

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
            'value["previous_annual_freeze_run_id"] == 37310525635',
            text,
        )
        self.assertIn(
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC570",
            text,
        )

    def test_workflow_cannot_dispatch_or_mutate(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)
        self.assertIn('value["preflight_read_only"] is True', text)
        self.assertIn('"repository_mutation_authorized",', text)
        self.assertIn('"trading_authorized",', text)

    def test_workflow_has_no_stale_prior_decision_names(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("dec557", text)
        self.assertNotIn("dec558", text)
        self.assertNotIn("dec559", text)
        self.assertNotIn("DEC559", text)


if __name__ == "__main__":
    unittest.main()
