from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_regime_balance_utility_failure_diagnostics import (
    DEC251_MERGED_COMMIT,
    EXPECTED_INVALID_BREADTH_ACCESS_NAMES,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION,
    IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION,
    OBSERVED_RUNTIME_MISSING_EXPORT,
    SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    SUCCESSOR_MODEL_FIT_AUTHORIZED,
    SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED,
    analyze_exp059_predecessor_depth_drift,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp059ImplementationFailureDiagnosticTests(unittest.TestCase):
    def test_static_audit_matches_exact_four_depth_errors(self) -> None:
        report = analyze_exp059_predecessor_depth_drift(
            repository_root=ROOT,
        )
        self.assertEqual(
            report["diagnostic_decision"],
            "DEC-252",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION,
            "DEC-252",
        )
        self.assertEqual(
            report["diagnostic_classification"],
            IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION,
        )
        self.assertEqual(report["invalid_breadth_access_count"], 4)
        self.assertEqual(
            tuple(report["invalid_breadth_access_names"]),
            tuple(sorted(EXPECTED_INVALID_BREADTH_ACCESS_NAMES)),
        )
        self.assertEqual(report["invalid_chain_depth"], 2)
        self.assertEqual(report["repaired_chain_depth"], 3)

    def test_runtime_failure_is_explained_by_static_audit(self) -> None:
        report = analyze_exp059_predecessor_depth_drift(
            repository_root=ROOT,
        )
        self.assertEqual(
            report["observed_runtime_missing_export"],
            OBSERVED_RUNTIME_MISSING_EXPORT,
        )
        self.assertIn(
            OBSERVED_RUNTIME_MISSING_EXPORT,
            report["invalid_breadth_access_names"],
        )

    def test_exact_repaired_accesses_are_one_level_deeper(self) -> None:
        report = analyze_exp059_predecessor_depth_drift(
            repository_root=ROOT,
        )
        expected = tuple(
            sorted(
                "_predecessor._predecessor._predecessor." + name
                for name in EXPECTED_INVALID_BREADTH_ACCESS_NAMES
            )
        )
        self.assertEqual(
            tuple(report["repaired_breadth_accesses"]),
            expected,
        )
        self.assertIn(
            "_predecessor._predecessor.<name> with "
            "_predecessor._predecessor._predecessor.<name>",
            report["implementation_repair_rule"],
        )

    def test_failure_slot_identity_is_frozen(self) -> None:
        report = analyze_exp059_predecessor_depth_drift(
            repository_root=ROOT,
        )
        self.assertEqual(
            DEC251_MERGED_COMMIT,
            "639fa26f841d0d3bb4c8577372a8539a0c0fd38f",
        )
        self.assertEqual(
            report["reviewed_failed_model_run_id"],
            36239443323,
        )
        self.assertEqual(
            report["predecessor_result_decision"],
            "DEC-251",
        )
        self.assertEqual(
            report["predecessor_failure_classification"],
            (
                "IMPLEMENTATION_DEPENDENCY_EXPORT_DEPTH_DRIFT_"
                "PREVENTED_ALL_EXP059_CELL_RESULTS"
            ),
        )

    def test_repair_boundary_is_source_only(self) -> None:
        report = analyze_exp059_predecessor_depth_drift(
            repository_root=ROOT,
        )
        self.assertFalse(
            report["protocol_semantics_change_authorized"]
        )
        self.assertFalse(report["exp059_rerun_authorized"])
        self.assertFalse(report["exp059_replacement_run_authorized"])
        self.assertTrue(
            report["successor_protocol_source_open_authorized"]
        )
        self.assertFalse(report["successor_model_fit_authorized"])
        self.assertFalse(
            report["successor_historical_result_execution_authorized"]
        )
        self.assertTrue(SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED)
        self.assertFalse(SUCCESSOR_MODEL_FIT_AUTHORIZED)
        self.assertFalse(
            SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED
        )

    def test_all_execution_and_trading_paths_remain_closed(self) -> None:
        report = analyze_exp059_predecessor_depth_drift(
            repository_root=ROOT,
        )
        for field in (
            "exp059_rerun_authorized",
            "exp059_replacement_run_authorized",
            "successor_model_fit_authorized",
            "successor_historical_result_execution_authorized",
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(report[field], False)

    def test_source_contains_no_dispatch_or_broker_path(self) -> None:
        path = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_balance_utility_failure_diagnostics.py"
        )
        source = path.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
