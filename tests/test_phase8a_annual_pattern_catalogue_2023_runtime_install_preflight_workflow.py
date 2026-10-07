from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/phase8a-annual-catalogue-2023-runtime-install-preflight.yml"
)


class AnnualPatternCatalogue2023RuntimeInstallPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2023-runtime-install-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2023-runtime-install-preflight.yml",
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

    def test_workflow_pins_exact_dec604_plan_and_targets(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37688619041",
            "affbb533a320f639c8e4d1a955c2b1fd907b0d63",
            "11512058473",
            "a43cd3c767082ae3c20587690e202f98da32c9824b0cda2f33d211ac19e21de8",
            "9c5841d3842bc1c342c0e4032460c30ec66c33d0d144c47c4cf1a3523a7d1440",
            "614784849bca811cbd822cd2243eec19f26163d1",
            "2335f0c106c628ff817e904f40a29b0f589fafca",
            "fe5c18f8ffa5e3d698f91060ec8c28e0d0692318",
            "2c4292abadbffb9dd87edaab67d9e32783facae7",
            "f2734c7ea32355b1024d1097812578b23fc4409d",
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        ):
            self.assertIn(value, text)
        self.assertIn('"run_number": 1', text)
        self.assertIn(
            "annual-catalogue-2023-dec604-runtime-authorization-plan-",
            text,
        )
        self.assertIn("dec603-2023-execution-authorization.json", text)
        self.assertIn("dec604-2023-runtime-authorization-plan.json", text)
        self.assertIn("dec605-2023-runtime-install-preflight.json", text)

    def test_workflow_rechecks_run385_is_absent(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383, 384}",
            text,
        )
        self.assertIn('382: (37443770076, "success")', text)
        self.assertIn('383: (37531960014, "success")', text)
        self.assertIn('384: (37663157285, "success")', text)
        self.assertIn('row["run_number"] >= 385', text)
        self.assertIn('value["expected_run_number"] == 385', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37663157285',
            text,
        )
        self.assertIn(
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC605",
            text,
        )

    def test_workflow_preserves_dormant_install_boundary(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2023_runtime_authorization.py",
            text,
        )
        self.assertIn('value["preflight_read_only"] is True', text)
        self.assertIn(
            'value["source_authorization_protected_history_access_authorized"] is True',
            text,
        )
        self.assertIn('value["protected_catalogue_segment"] is True', text)
        for field in (
            "repository_mutation_authorized",
            "runtime_authorization_installed",
            "runtime_gate_active",
            "annual_workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "run_386_or_later_authorized",
            "next_segment_execution_authorized",
            "protected_history_access_authorized",
            "cross_year_comparison_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertIn(f'"{field}",', text)
        self.assertNotIn("annual_pattern_catalogue_2021", text)


if __name__ == "__main__":
    unittest.main()
