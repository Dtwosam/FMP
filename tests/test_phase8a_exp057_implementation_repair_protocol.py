from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_failure_diagnostics import (
    EXPECTED_STATIC_MISSING_PREDECESSOR_EXPORTS,
)
from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_protocol import (
    fit_temporal_residual_lower_tail_utility_protocol_payload,
)
from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_repair_protocol import (
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_VERSION,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED,
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED,
    TRADING_AUTHORIZED,
    fit_temporal_residual_lower_tail_utility_repair_protocol_fingerprint,
    fit_temporal_residual_lower_tail_utility_repair_protocol_payload,
    validate_fit_temporal_residual_lower_tail_utility_repair_predecessor_identity,
)


class Exp057ImplementationRepairProtocolTests(unittest.TestCase):
    def test_identity_and_fingerprint_are_frozen(self) -> None:
        validate_fit_temporal_residual_lower_tail_utility_repair_predecessor_identity()
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_EXPERIMENT_ID,
            "EXP-20260925-057",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_DECISION,
            "DEC-220",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_VERSION,
            (
                "fmp-exp057-fit-temporal-residual-lower-tail-utility-"
                "implementation-repair-protocol-v1"
            ),
        )
        first = (
            fit_temporal_residual_lower_tail_utility_repair_protocol_fingerprint()
        )
        second = (
            fit_temporal_residual_lower_tail_utility_repair_protocol_fingerprint()
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)

    def test_exp056_model_semantics_are_preserved(self) -> None:
        predecessor = (
            fit_temporal_residual_lower_tail_utility_protocol_payload()
        )
        payload = (
            fit_temporal_residual_lower_tail_utility_repair_protocol_payload()
        )

        for field in (
            "chronology",
            "model_family",
            "temporal_jackknife",
            "out_of_fit_utility_calibration",
            "fit_temporal_support_calibration",
            "fit_temporal_feature_support",
            "fit_temporal_residual_bound",
            "fit_temporal_residual_breadth",
            "selection",
            "validation",
            "retrospective_holdout",
        ):
            with self.subTest(field=field):
                self.assertEqual(payload[field], predecessor[field])

        predecessor_consensus = dict(predecessor["utility_consensus"])
        repaired_consensus = dict(payload["utility_consensus"])
        self.assertTrue(
            predecessor_consensus.pop(
                "fit_temporal_residual_lower_tail_added"
            )
        )
        self.assertFalse(
            repaired_consensus.pop(
                "fit_temporal_residual_lower_tail_added"
            )
        )
        self.assertTrue(
            repaired_consensus.pop(
                "fit_temporal_residual_lower_tail_retained"
            )
        )
        self.assertEqual(repaired_consensus, predecessor_consensus)

        predecessor_tail = dict(
            predecessor["fit_temporal_residual_lower_tail"]
        )
        repaired_tail = dict(payload["fit_temporal_residual_lower_tail"])
        self.assertTrue(
            predecessor_tail.pop("authorized_protocol_change")
        )
        self.assertFalse(
            repaired_tail.pop("authorized_protocol_change")
        )
        self.assertTrue(repaired_tail.pop("retained_from_exp056"))
        self.assertEqual(repaired_tail, predecessor_tail)

    def test_exact_seven_name_implementation_repair_only(self) -> None:
        payload = (
            fit_temporal_residual_lower_tail_utility_repair_protocol_payload()
        )
        repair = payload["implementation_repair"]
        self.assertTrue(repair["authorized"])
        self.assertFalse(
            repair["protocol_semantics_change_authorized"]
        )
        self.assertEqual(
            repair["from_attribute_root"],
            "_predecessor",
        )
        self.assertEqual(repair["to_attribute_root"], "_base")
        self.assertEqual(repair["exact_attribute_count"], 7)
        self.assertEqual(
            repair["exact_attribute_names"],
            list(sorted(EXPECTED_STATIC_MISSING_PREDECESSOR_EXPORTS)),
        )
        self.assertIn(
            "_predecessor.<name> with _base.<name>",
            repair["repair_rule"],
        )

    def test_all_model_and_gate_changes_remain_closed(self) -> None:
        payload = (
            fit_temporal_residual_lower_tail_utility_repair_protocol_payload()
        )
        auth = payload["authorization"]
        self.assertTrue(
            auth["implementation_dependency_repair_authorized"]
        )
        self.assertFalse(auth["protocol_semantics_change_authorized"])

        for field in (
            "model_protocol_result_authorized",
            "model_fit_authorized",
            "historical_result_execution_authorized",
            "feature_change_authorized",
            "financial_target_change_authorized",
            "outer_chronology_change_authorized",
            "hgb_structural_config_change_authorized",
            "jackknife_view_change_authorized",
            "unanimous_utility_consensus_change_authorized",
            "positive_utility_requirement_change_authorized",
            "pooled_out_of_fit_calibration_change_authorized",
            "fit_temporal_utility_support_change_authorized",
            "fit_temporal_feature_support_change_authorized",
            "fit_temporal_residual_bound_change_authorized",
            "fit_temporal_residual_breadth_change_authorized",
            "fit_temporal_residual_lower_tail_change_authorized",
            "selection_window_calibration_authorized",
            "selection_window_quota_authorized",
            "validation_calibration_authorized",
            "holdout_calibration_authorized",
            "realized_selection_outcome_ranking_authorized",
            "density_anchor_change_authorized",
            "minimum_directional_candidate_count_change_authorized",
            "stability_screen_change_authorized",
            "per_window_financial_gate_change_authorized",
            "per_window_cutoff_tuning_authorized",
            "logistic_reintroduction_authorized",
            "classifier_fallback_authorized",
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(auth[field], False)

        self.assertTrue(IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED)
        self.assertFalse(PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED)
        self.assertFalse(MODEL_PROTOCOL_RESULT_AUTHORIZED)
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_EXECUTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_predecessor_failure_and_diagnostic_are_explicit(self) -> None:
        payload = (
            fit_temporal_residual_lower_tail_utility_repair_protocol_payload()
        )
        self.assertEqual(
            payload["semantic_predecessor_experiment_id"],
            "EXP-20260925-056",
        )
        self.assertEqual(
            payload["semantic_predecessor_protocol_decision"],
            "DEC-209",
        )
        self.assertEqual(
            payload["failed_predecessor_result_decision"],
            "DEC-218",
        )
        self.assertEqual(
            payload["failure_diagnostic_decision"],
            "DEC-219",
        )
        self.assertEqual(
            payload["failure_diagnostic_classification"],
            (
                "EXP056_IMPLEMENTATION_FAILED_BEFORE_EVIDENCE_DUE_"
                "INTERMEDIATE_PREDECESSOR_EXPORT_DRIFT"
            ),
        )


if __name__ == "__main__":
    unittest.main()
