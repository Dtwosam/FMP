from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/phase8a-annual-catalogue-2022-runtime-install-action.yml"
)


class AnnualPatternCatalogue2022RuntimeInstallActionWorkflowTests(
    unittest.TestCase
):
    def test_builder_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-runtime-install-action",
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

    def test_builder_pins_exact_dec594_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37616348059",
            "ae0949d54a55d2a71a7cd78f153c391be0c6ff23",
            "11480120937",
            "17334ae595a45bfb8174b7bcb41cab169b4185064ca33c05a79dcaa548fdafd1",
            "56c3ff244ed7ad47a07ab64efbea68e41acb61cfdba24303f2d265a2e690b08c",
            "6927206445b32ea2cd8a1e78b0511f70e9815a9204d771712c5976a5d79af4e4",
            "90fbc26b51d50d019e39c467d461bd7ba6b4f22b",
            "e4fc3e1d1d0336136cdaa72a931c2b490e80463b",
            "8d1fce9c947fd7a579a6ab581d605293a02329a3",
            "d7710ab16dde2eea6b0d93dc6387c6cc489b30d7",
        ):
            self.assertIn(value, text)

    def test_builder_rechecks_runtime_and_run384_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        current_check = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"'
        )
        self.assertEqual(text.count(current_check), 2)
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2022_runtime_authorization.py",
            text,
        )
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        self.assertIn('382: (37443770076, "success")', text)
        self.assertIn('383: (37531960014, "success")', text)
        self.assertIn('row["run_number"] >= 384', text)

    def test_builder_freezes_exact_two_file_action_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["action_count"] == 2', text)
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_2022_runtime_authorization.py"',
            text,
        )
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_runtime.py"',
            text,
        )
        self.assertIn(
            '"ecb21dc7106e7bd43447f4135c3a696251a75e05"',
            text,
        )
        self.assertIn(
            '"d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"',
            text,
        )
        self.assertIn(
            '"f2734c7ea32355b1024d1097812578b23fc4409d"',
            text,
        )
        self.assertIn('value["repository_mutation_authorized"] is True', text)
        for field in (
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

    def test_builder_has_no_stale_prior_year_names(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("annual_pattern_catalogue_2021", text)
        for stale in ("DEC-584", "DEC-583", "dec584", "dec583"):
            self.assertNotIn(stale, text)


if __name__ == "__main__":
    unittest.main()
