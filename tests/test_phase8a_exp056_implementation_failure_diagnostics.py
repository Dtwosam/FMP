from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_failure_diagnostics import (
    DEC218_MERGED_COMMIT,
    EXPECTED_STATIC_MISSING_PREDECESSOR_EXPORTS,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION,
    IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION,
    OBSERVED_RUNTIME_MISSING_EXPORTS,
    SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    SUCCESSOR_MODEL_FIT_AUTHORIZED,
    SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED,
    analyze_exp056_dependency_export_drift,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp056ImplementationFailureDiagnosticTests(unittest.TestCase):
    def test_static_audit_matches_exact_seven_export_drift(self) -> None:
        report = analyze_exp056_dependency_export_drift(
            repository_root=ROOT,
        )
        self.assertEqual(
            report["diagnostic_decision"],
            "DEC-219",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION,
            "DEC-219",
        )
        self.assertEqual(
            report["diagnostic_classification"],
            IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION,
        )
        self.assertEqual(
            tuple(report["static_missing_predecessor_exports"]),
            tuple(sorted(EXPECTED_STATIC_MISSING_PREDECESSOR_EXPORTS)),
        )
        self.assertEqual(
            report["static_missing_predecessor_export_count"],
            7,
        )
        self.assertEqual(
            report["latent_missing_export_count"],
            5,
        )
        self.assertTrue(
            report["all_missing_exports_available_on_base"]
        )

    def test_observed_runtime_failures_are_subset_of_static_drift(self) -> None:
        report = analyze_exp056_dependency_export_drift(
            repository_root=ROOT,
        )
        self.assertEqual(
            tuple(report["observed_runtime_missing_exports"]),
            OBSERVED_RUNTIME_MISSING_EXPORTS,
        )
        self.assertTrue(
            set(OBSERVED_RUNTIME_MISSING_EXPORTS).issubset(
                set(report["static_missing_predecessor_exports"])
            )
        )
        self.assertIn(
            "MIN_STABILITY_WINDOW_CANDIDATE_SHARE",
            report["static_missing_predecessor_exports"],
        )
        self.assertIn(
            "FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL",
            report["static_missing_predecessor_exports"],
        )

    def test_repair_boundary_is_implementation_only(self) -> None:
        report = analyze_exp056_dependency_export_drift(
            repository_root=ROOT,
        )
        self.assertIn(
            "_predecessor.<name> with _base.<name>",
            report["implementation_repair_rule"],
        )
        self.assertFalse(
            report["protocol_semantics_change_authorized"]
        )
        self.assertFalse(report["exp056_rerun_authorized"])
        self.assertFalse(report["exp056_replacement_run_authorized"])
        self.assertTrue(
            report["successor_protocol_source_open_authorized"]
        )
        self.assertFalse(
            report["successor_model_fit_authorized"]
        )
        self.assertFalse(
            report["successor_historical_result_execution_authorized"]
        )

    def test_failure_slot_identity_is_frozen(self) -> None:
        report = analyze_exp056_dependency_export_drift(
            repository_root=ROOT,
        )
        self.assertEqual(
            DEC218_MERGED_COMMIT,
            "2f2171f0166f22c19482a905d6906d1cfd672275",
        )
        self.assertEqual(
            report["reviewed_failed_model_run_id"],
            36175841645,
        )
        self.assertEqual(
            report["predecessor_result_decision"],
            "DEC-218",
        )
        self.assertEqual(
            report["predecessor_failure_classification"],
            (
                "IMPLEMENTATION_DEPENDENCY_EXPORT_DRIFT_"
                "PREVENTED_ALL_EXP056_CELL_RESULTS"
            ),
        )

    def test_all_execution_and_trading_paths_remain_closed(self) -> None:
        report = analyze_exp056_dependency_export_drift(
            repository_root=ROOT,
        )
        self.assertTrue(SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED)
        self.assertFalse(SUCCESSOR_MODEL_FIT_AUTHORIZED)
        self.assertFalse(
            SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED
        )
        for field in (
            "exp056_rerun_authorized",
            "exp056_replacement_run_authorized",
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
            "model_successor_fit_temporal_residual_lower_tail_utility_failure_diagnostics.py"
        )
        source = path.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
