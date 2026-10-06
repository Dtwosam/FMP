from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/phase8a-annual-catalogue-2021-runtime-install-preflight.yml"
)


class AnnualPatternCatalogue2021RuntimeInstallPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2021-runtime-install-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2021-runtime-install-preflight.yml",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)

    def test_workflow_pins_exact_dec582_plan_and_targets(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37473293705",
            "2403d2770eca576e418f216196a0111fa7f07136",
            "11416884894",
            "cfc8580df9318eeebfdae9e446fa92603e5f2e408ec0066a05945845654743b0",
            "ea0244c3ef60cfa21dc90567faeff680bca856afc68acc96e9e74c19fafd54f1",
            "b8ba899634fe1b45ee7a50dc13da97440c3d45d0",
            "8211f2a35e7d69efdd195e426350831e936f3fc5",
            "de1643991d85cd63e5505401b871e3c02315e0e9",
            "3e086e82201ed0bea85226c115ae7a09e7d95983",
            "4e124365430672fa63825b272001937c60151644",
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        ):
            self.assertIn(value, text)
        self.assertIn('"run_number": 1', text)
        self.assertIn(
            "annual-catalogue-2021-dec582-runtime-authorization-plan-",
            text,
        )
        self.assertIn("dec581-2021-execution-authorization.json", text)
        self.assertIn("dec582-2021-runtime-authorization-plan.json", text)
        self.assertIn("dec583-2021-runtime-install-preflight.json", text)

    def test_workflow_rechecks_run383_is_absent(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382}",
            text,
        )
        self.assertIn('382: (37443770076, "success")', text)
        self.assertIn('row["run_number"] >= 383', text)
        self.assertIn('value["expected_run_number"] == 383', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37443770076',
            text,
        )
        self.assertIn(
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC583",
            text,
        )

    def test_workflow_preserves_dormant_install_boundary(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2021_runtime_authorization.py",
            text,
        )
        self.assertIn('value["preflight_read_only"] is True', text)
        self.assertIn('"repository_mutation_authorized",', text)
        self.assertIn('"runtime_authorization_installed",', text)
        self.assertIn('"runtime_gate_active",', text)
        self.assertIn('"annual_workflow_dispatch_authorized",', text)
        self.assertIn('"trading_authorized",', text)

    def test_workflow_has_no_stale_prior_decision_names(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("dec568", text)
        self.assertNotIn("dec569", text)
        self.assertNotIn("dec570", text)
        self.assertNotIn("DEC568", text)
        self.assertNotIn("DEC569", text)
        self.assertNotIn("DEC570", text)


if __name__ == "__main__":
    unittest.main()
