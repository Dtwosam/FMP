from __future__ import annotations

import unittest

from fmp.discovery.exp065_pairwise_interaction_research_direction import (
    POST_EXP064_RESEARCH_DIRECTION_DECISION,
    POST_EXP064_RESEARCH_DIRECTION_VERSION,
    SOURCE_RESULT_BLOB_SHA,
    SOURCE_RESULT_MERGE_SHA,
    SUCCESSOR_EXPERIMENT_ID,
    build_exp065_pairwise_interaction_research_direction,
)


class Exp065PairwiseInteractionResearchDirectionTests(unittest.TestCase):
    def test_direction_binds_dec458_and_new_experiment_identity(self) -> None:
        value = build_exp065_pairwise_interaction_research_direction()

        self.assertEqual(POST_EXP064_RESEARCH_DIRECTION_DECISION, "DEC-459")
        self.assertEqual(
            POST_EXP064_RESEARCH_DIRECTION_VERSION,
            "fmp-exp065-pairwise-interaction-research-direction-v1",
        )
        self.assertEqual(
            SOURCE_RESULT_MERGE_SHA,
            "e3c2a7a1dbb6592a8438f3949ffa83177e31f4e6",
        )
        self.assertEqual(
            SOURCE_RESULT_BLOB_SHA,
            "c5878685950e14a632b4eb8d2616d9540afb12d2",
        )
        self.assertEqual(SUCCESSOR_EXPERIMENT_ID, "EXP-20261001-065")
        self.assertEqual(value["source_result_decision"], "DEC-458")
        self.assertEqual(value["source_experiment_id"], "EXP-20261001-064")
        self.assertEqual(value["successor_experiment_id"], "EXP-20261001-065")
        self.assertEqual(value["source_historical_run_id"], 36853290904)
        self.assertEqual(
            value["source_aggregate_evidence_fingerprint"],
            "832e8c814ac578b614764d37cba15e64569e2f841dfa6f72f2c9cd9a8fdbcbb1",
        )

    def test_direction_uses_exact_exp064_negative_result(self) -> None:
        value = build_exp065_pairwise_interaction_research_direction()
        result = value["source_result"]

        self.assertEqual(result["hypotheses"], 1440)
        self.assertEqual(result["evaluable_hypotheses"], 1440)
        self.assertEqual(result["qualifying_hypotheses"], 0)
        self.assertEqual(result["deduplicated_hypotheses"], 0)
        self.assertEqual(result["continuous_stability_shortlist_count"], 0)
        self.assertEqual(result["continuous_stability_frozen_count"], 0)
        self.assertEqual(
            result["classification"],
            "NO_CONTINUOUS_STABILITY_HYPOTHESIS_PASSED_FROZEN_GATE",
        )

    def test_direction_closes_prior_families_without_rescue(self) -> None:
        value = build_exp065_pairwise_interaction_research_direction()
        direction = value["research_direction"]

        self.assertTrue(direction["discrete_tertile_atomic_state_family_closed"])
        self.assertTrue(direction["single_feature_continuous_rank_family_closed"])
        self.assertFalse(direction["exp064_threshold_relaxation_permitted"])
        self.assertFalse(direction["exp064_protocol_redefinition_permitted"])
        self.assertFalse(direction["exp064_hypothesis_rescue_permitted"])

    def test_direction_opens_only_bounded_pairwise_source_design(self) -> None:
        value = build_exp065_pairwise_interaction_research_direction()
        direction = value["research_direction"]

        self.assertTrue(direction["pairwise_interaction_source_design_permitted"])
        self.assertTrue(direction["exactly_two_features_per_hypothesis"])
        self.assertFalse(direction["three_plus_feature_interactions_permitted"])
        self.assertFalse(direction["new_raw_feature_permitted"])
        self.assertTrue(direction["exact_pair_construction_deferred_to_protocol"])
        self.assertTrue(direction["exact_interaction_transform_deferred_to_protocol"])
        self.assertTrue(direction["exact_interaction_estimator_deferred_to_protocol"])
        self.assertTrue(
            direction["interaction_incrementality_requirement_must_be_defined_before_execution"]
        )

    def test_market_and_feature_universe_remains_bounded(self) -> None:
        value = build_exp065_pairwise_interaction_research_direction()
        bounded = value["bounded_universe"]

        self.assertEqual(
            bounded["symbols"],
            ["EURUSD", "GBPUSD", "USDJPY"],
        )
        self.assertEqual(bounded["timeframes"], ["5m", "15m", "1h"])
        self.assertEqual(bounded["horizons_minutes"], [60, 240])
        self.assertEqual(len(bounded["continuous_features"]), 20)
        self.assertEqual(bounded["maximum_features_per_successor_hypothesis"], 2)
        self.assertFalse(bounded["new_raw_features_authorized_by_dec459"])
        self.assertFalse(bounded["new_symbols_authorized_by_dec459"])
        self.assertFalse(bounded["new_timeframes_authorized_by_dec459"])
        self.assertFalse(bounded["new_horizons_authorized_by_dec459"])

    def test_all_execution_and_downstream_paths_remain_locked(self) -> None:
        value = build_exp065_pairwise_interaction_research_direction()

        self.assertTrue(value["successor_protocol_source_open_authorized"])
        for field in (
            "successor_execution_authorized",
            "successor_historical_result_authorized",
            "rerun_exp064_authorized",
            "retry_exp064_authorized",
            "replacement_exp064_authorized",
            "exp064_threshold_relaxation_authorized",
            "exp064_protocol_redefinition_authorized",
            "exp064_hypothesis_rescue_authorized",
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
        value = build_exp065_pairwise_interaction_research_direction()
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
        value = build_exp065_pairwise_interaction_research_direction()

        self.assertEqual(
            value["next_gate"],
            "SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_PROTOCOL",
        )


if __name__ == "__main__":
    unittest.main()
