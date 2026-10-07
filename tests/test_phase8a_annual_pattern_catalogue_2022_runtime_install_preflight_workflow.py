from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/phase8a-annual-catalogue-2022-runtime-install-preflight.yml"
)


class AnnualPatternCatalogue2022RuntimeInstallPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-runtime-install-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2022-runtime-install-preflight.yml",
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

    def test_workflow_pins_exact_dec593_plan_and_targets(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37611869958",
            "9d53e2f11746ccff7e525a1df1d10427fdfdd2be",
            "11477773270",
            "ff974250ff9a09069e77f8c61e96649c9318e83dfcccab74e8dfd3dd07fed420",
            "2ed8681de71e27f9767f75a9e47861044c81c3886639195e412495613acd09fd",
            "8d1fce9c947fd7a579a6ab581d605293a02329a3",
            "7328c94907198d80e8a201772ce6d23561983aa5",
            "d7710ab16dde2eea6b0d93dc6387c6cc489b30d7",
            "e68e9f1ee41ca89f0ae3d7758d59b4ce8c5823bb",
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        ):
            self.assertIn(value, text)
        self.assertIn('"run_number": 1', text)
        self.assertIn(
            "annual-catalogue-2022-dec593-runtime-authorization-plan-",
            text,
        )
        self.assertIn("dec592-2022-execution-authorization.json", text)
        self.assertIn("dec593-2022-runtime-authorization-plan.json", text)
        self.assertIn("dec594-2022-runtime-install-preflight.json", text)

    def test_workflow_rechecks_run384_is_absent(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        self.assertIn('382: (37443770076, "success")', text)
        self.assertIn('383: (37531960014, "success")', text)
        self.assertIn('row["run_number"] >= 384', text)
        self.assertIn('value["expected_run_number"] == 384', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37531960014',
            text,
        )
        self.assertIn(
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC594",
            text,
        )

    def test_workflow_preserves_dormant_install_boundary(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2022_runtime_authorization.py",
            text,
        )
        self.assertIn('value["preflight_read_only"] is True', text)
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
            "run_385_or_later_authorized",
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
