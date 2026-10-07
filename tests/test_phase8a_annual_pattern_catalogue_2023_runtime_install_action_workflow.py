from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/phase8a-annual-catalogue-2023-runtime-install-action.yml"
)


class AnnualPatternCatalogue2023RuntimeInstallActionWorkflowTests(
    unittest.TestCase
):
    def test_builder_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2023-runtime-install-action",
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

    def test_builder_pins_exact_dec605_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37691460323",
            "81ffd195079d853d7bcd7a49ac34720d563f1a49",
            "11513856300",
            "0cc56948730d68dc76f21fdc5d99dad97218640f3ddabd62b77062d1acb0e00b",
            "08d7d79adb7f1fabbe156851923adb4f1f907f2dacd54ddbd82e33063116de76",
            "85c8ac47a4e98d296b4423be1dd551286f82187dc5ec1f0c4c9eadf2fd316599",
            "42477932452d07a445d7c85650a01b3692fa755c",
            "2f56a4251545bfe327adeb84c5f23009f43f67a3",
            "614784849bca811cbd822cd2243eec19f26163d1",
            "fe5c18f8ffa5e3d698f91060ec8c28e0d0692318",
        ):
            self.assertIn(value, text)

    def test_builder_rechecks_runtime_and_run385_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        current_check = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "f2734c7ea32355b1024d1097812578b23fc4409d"'
        )
        self.assertEqual(text.count(current_check), 2)
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2023_runtime_authorization.py",
            text,
        )
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383, 384}",
            text,
        )
        self.assertIn('382: (37443770076, "success")', text)
        self.assertIn('383: (37531960014, "success")', text)
        self.assertIn('384: (37663157285, "success")', text)
        self.assertIn('row["run_number"] >= 385', text)

    def test_builder_freezes_exact_two_file_action_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["action_count"] == 2', text)
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py"',
            text,
        )
        self.assertIn(
            '"src/fmp/discovery/annual_pattern_catalogue_runtime.py"',
            text,
        )
        self.assertIn(
            '"cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191"',
            text,
        )
        self.assertIn(
            '"f2734c7ea32355b1024d1097812578b23fc4409d"',
            text,
        )
        self.assertIn(
            '"0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3"',
            text,
        )
        self.assertIn(
            'value["source_authorization_protected_history_access_authorized"] is True',
            text,
        )
        self.assertIn('value["protected_catalogue_segment"] is True', text)
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

    def test_builder_has_no_stale_prior_year_names(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("annual_pattern_catalogue_2021", text)
        for stale in ("DEC-584", "DEC-583", "dec584", "dec583"):
            self.assertNotIn(stale, text)


if __name__ == "__main__":
    unittest.main()
