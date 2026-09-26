from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_regime_balance_utility_failure_diagnostics import (
    EXPECTED_INVALID_BREADTH_ACCESS_NAMES,
)
from fmp.market_learning.model_successor_fit_temporal_residual_regime_balance_utility_protocol import (
    fit_temporal_residual_regime_balance_utility_protocol_payload,
)
from fmp.market_learning.model_successor_fit_temporal_residual_regime_balance_utility_repair_protocol import (
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_VERSION,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED,
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED,
    TRADING_AUTHORIZED,
    fit_temporal_residual_regime_balance_utility_repair_protocol_fingerprint,
    fit_temporal_residual_regime_balance_utility_repair_protocol_payload,
    validate_fit_temporal_residual_regime_balance_utility_repair_predecessor_identity,
)


class Exp060ImplementationRepairProtocolTests(unittest.TestCase):
    def test_identity_and_fingerprint_are_frozen(self) -> None:
        validate_fit_temporal_residual_regime_balance_utility_repair_predecessor_identity()
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_EXPERIMENT_ID,
            "EXP-20260926-060",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_DECISION,
            "DEC-253",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_VERSION,
            (
                "fmp-exp060-fit-temporal-residual-regime-balance-utility-"
                "implementation-repair-protocol-v1"
            ),
        )
        first = (
            fit_temporal_residual_regime_balance_utility_repair_protocol_fingerprint()
        )
        second = (
            fit_temporal_residual_regime_balance_utility_repair_protocol_fingerprint()
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)

    def test_exp059_model_semantics_are_preserved(self) -> None:
        predecessor = (
            fit_temporal_residual_regime_balance_utility_protocol_payload()
        )
        payload = (
            fit_temporal_residual_regime_balance_utility_repair_protocol_payload()
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
            "fit_temporal_residual_lower_tail",
            "fit_temporal_residual_regime_floor",
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
                "fit_temporal_residual_regime_balance_added"
            )
        )
        self.assertFalse(
            repaired_consensus.pop(
                "fit_temporal_residual_regime_balance_added"
            )
        )
        self.assertTrue(
            repaired_consensus.pop(
                "fit_temporal_residual_regime_balance_retained"
            )
        )
        self.assertEqual(repaired_consensus, predecessor_consensus)

        predecessor_balance = dict(
            predecessor["fit_temporal_residual_regime_balance"]
        )
        repaired_balance = dict(
            payload["fit_temporal_residual_regime_balance"]
        )
        self.assertTrue(
            predecessor_balance.pop("authorized_protocol_change")
        )
        self.assertFalse(
            repaired_balance.pop("authorized_protocol_change")
        )
        self.assertTrue(repaired_balance.pop("retained_from_exp059"))
        self.assertEqual(repaired_balance, predecessor_balance)

    def test_exact_four_name_depth_repair_only(self) -> None:
        payload = (
            fit_temporal_residual_regime_balance_utility_repair_protocol_payload()
        )
        repair = payload["implementation_repair"]
        self.assertTrue(repair["authorized"])
        self.assertFalse(
            repair["protocol_semantics_change_authorized"]
        )
        self.assertEqual(
            repair["from_attribute_root"],
            "_predecessor._predecessor",
        )
        self.assertEqual(
            repair["to_attribute_root"],
            "_predecessor._predecessor._predecessor",
        )
        self.assertEqual(repair["exact_attribute_count"], 4)
        self.assertEqual(
            repair["exact_attribute_names"],
            list(sorted(EXPECTED_INVALID_BREADTH_ACCESS_NAMES)),
        )
        self.assertIn(
            "_predecessor._predecessor.<name> with "
            "_predecessor._predecessor._predecessor.<name>",
            repair["repair_rule"],
        )

    def test_all_model_and_gate_changes_remain_closed(self) -> None:
        payload = (
            fit_temporal_residual_regime_balance_utility_repair_protocol_payload()
        )
        auth = payload["authorization"]
        self.assertTrue(
            auth["implementation_dependency_repair_authorized"]
        )
        self.assertFalse(auth["protocol_semantics_change_authorized"])

        for field, value in auth.items():
            if field == "implementation_dependency_repair_authorized":
                continue
            with self.subTest(field=field):
                self.assertIs(value, False)

        self.assertTrue(IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED)
        self.assertFalse(PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED)
        self.assertFalse(MODEL_PROTOCOL_RESULT_AUTHORIZED)
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_EXECUTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_predecessor_failure_and_diagnostic_are_explicit(self) -> None:
        payload = (
            fit_temporal_residual_regime_balance_utility_repair_protocol_payload()
        )
        self.assertEqual(
            payload["semantic_predecessor_experiment_id"],
            "EXP-20260926-059",
        )
        self.assertEqual(
            payload["semantic_predecessor_protocol_decision"],
            "DEC-242",
        )
        self.assertEqual(
            payload["failed_predecessor_result_decision"],
            "DEC-251",
        )
        self.assertEqual(
            payload["failure_diagnostic_decision"],
            "DEC-252",
        )
        self.assertEqual(
            payload["failure_diagnostic_classification"],
            (
                "EXP059_IMPLEMENTATION_FAILED_BEFORE_EVIDENCE_DUE_"
                "PREDECESSOR_DEPTH_DRIFT"
            ),
        )


if __name__ == "__main__":
    unittest.main()
