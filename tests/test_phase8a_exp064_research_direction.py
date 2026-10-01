from __future__ import annotations

import unittest

from fmp.discovery.exp064_research_direction import (
    POST_EXP063_RESEARCH_DIRECTION_DECISION,
    POST_EXP063_RESEARCH_DIRECTION_VERSION,
    SOURCE_RESULT_BLOB_SHA,
    SOURCE_RESULT_MERGE_SHA,
    SUCCESSOR_EXPERIMENT_ID,
    build_exp064_continuous_stability_research_direction,
)


class Exp064ResearchDirectionTests(unittest.TestCase):
    def test_direction_binds_dec450_and_new_experiment_identity(self) -> None:
        value = build_exp064_continuous_stability_research_direction()

        self.assertEqual(POST_EXP063_RESEARCH_DIRECTION_DECISION, "DEC-451")
        self.assertEqual(
            POST_EXP063_RESEARCH_DIRECTION_VERSION,
            "fmp-exp064-continuous-stability-research-direction-v1",
        )
        self.assertEqual(
            SOURCE_RESULT_MERGE_SHA,
            "839af1e85b526c3c2a11b228e4aa8d3865589f06",
        )
        self.assertEqual(
            SOURCE_RESULT_BLOB_SHA,
            "b572dbf4801c211b72285049654ebf4d96744cf1",
        )
        self.assertEqual(SUCCESSOR_EXPERIMENT_ID, "EXP-20261001-064")
        self.assertEqual(value["source_result_decision"], "DEC-450")
        self.assertEqual(value["source_experiment_id"], "EXP-20260930-063")
        self.assertEqual(value["successor_experiment_id"], "EXP-20261001-064")
        self.assertEqual(value["source_historical_run_id"], 36773288493)

    def test_direction_uses_exact_exp063_negative_result(self) -> None:
        value = build_exp064_continuous_stability_research_direction()
        result = value["source_result"]

        self.assertEqual(result["enumerated_patterns"], 37350)
        self.assertEqual(result["directional_hypotheses"], 74700)
        self.assertEqual(result["qualifying_directional_hypotheses"], 0)
        self.assertEqual(result["persistence_shortlist_count"], 0)
        self.assertEqual(result["persistence_frozen_count"], 0)
        self.assertEqual(
            result["classification"],
            "NO_DIRECTIONAL_HYPOTHESIS_PASSED_FROZEN_PERSISTENCE_GATE",
        )

    def test_direction_closes_discrete_atomic_state_family(self) -> None:
        value = build_exp064_continuous_stability_research_direction()
        direction = value["research_direction"]

        self.assertTrue(direction["discrete_tertile_atomic_state_family_closed"])
        self.assertTrue(direction["exp061_exp063_one_two_predicate_family_closed"])
        self.assertFalse(direction["threshold_relaxation_permitted"])
        self.assertFalse(direction["exp063_pattern_rescue_permitted"])
        self.assertTrue(direction["continuous_or_rank_effect_source_design_permitted"])
        self.assertTrue(direction["deterministic_existing_feature_transforms_permitted"])
        self.assertFalse(direction["new_raw_feature_permitted"])

    def test_market_and_feature_universe_remains_bounded(self) -> None:
        value = build_exp064_continuous_stability_research_direction()
        bounded = value["bounded_universe"]

        self.assertEqual(
            bounded["symbols"],
            ["EURUSD", "GBPUSD", "USDJPY"],
        )
        self.assertEqual(bounded["timeframes"], ["5m", "15m", "1h"])
        self.assertEqual(bounded["horizons_minutes"], [60, 240])
        self.assertEqual(len(bounded["continuous_features"]), 20)
        self.assertFalse(bounded["new_raw_features_authorized_by_dec451"])
        self.assertFalse(bounded["new_symbols_authorized_by_dec451"])
        self.assertFalse(bounded["new_timeframes_authorized_by_dec451"])
        self.assertFalse(bounded["new_horizons_authorized_by_dec451"])

    def test_all_historical_execution_and_downstream_paths_remain_locked(self) -> None:
        value = build_exp064_continuous_stability_research_direction()

        self.assertTrue(value["successor_protocol_source_open_authorized"])
        for field in (
            "successor_execution_authorized",
            "successor_historical_result_authorized",
            "rerun_exp063_authorized",
            "retry_exp063_authorized",
            "replacement_exp063_authorized",
            "exp063_threshold_relaxation_authorized",
            "exp063_pattern_redefinition_authorized",
            "exp063_pattern_rescue_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(value[field], field)

    def test_chronology_keeps_reserved_block_closed(self) -> None:
        value = build_exp064_continuous_stability_research_direction()
        chronology = value["chronology"]

        self.assertEqual(chronology["retrospective_design_start"], "2015-01-01")
        self.assertEqual(chronology["retrospective_design_end"], "2022-12-31")
        self.assertEqual(
            chronology["retrospective_design_label"],
            "ALREADY_SEEN_DESIGN_EVIDENCE",
        )
        self.assertTrue(chronology["2015_2022_may_not_be_called_fresh_validation"])
        self.assertEqual(chronology["reserved_robustness_start"], "2023-01-01")
        self.assertEqual(chronology["reserved_robustness_end"], "2026-08-20")
        self.assertFalse(chronology["reserved_robustness_opened"])

    def test_next_gate_is_source_only_protocol(self) -> None:
        value = build_exp064_continuous_stability_research_direction()

        self.assertEqual(
            value["next_gate"],
            "SOURCE_ONLY_EXP064_CONTINUOUS_STABILITY_PROTOCOL",
        )


if __name__ == "__main__":
    unittest.main()
