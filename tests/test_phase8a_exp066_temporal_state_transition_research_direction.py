from __future__ import annotations

import unittest

from fmp.discovery.exp066_temporal_state_transition_research_direction import (
    GOVERNING_RESEARCH_METHOD,
    SOURCE_RESULT_BLOB_SHA,
    SOURCE_RESULT_MERGE_SHA,
    SUCCESSOR_EXPERIMENT_ID,
    build_exp066_temporal_state_transition_research_direction,
)


class Exp066TemporalStateTransitionResearchDirectionTests(unittest.TestCase):
    def test_direction_binds_exact_frozen_dec468_source_identities(self) -> None:
        self.assertEqual(len(SOURCE_RESULT_MERGE_SHA), 40)
        self.assertEqual(len(SOURCE_RESULT_BLOB_SHA), 40)
        int(SOURCE_RESULT_MERGE_SHA, 16)
        int(SOURCE_RESULT_BLOB_SHA, 16)
        value = build_exp066_temporal_state_transition_research_direction()
        self.assertEqual(value["source_result_merge_sha"], SOURCE_RESULT_MERGE_SHA)
        self.assertEqual(value["source_result_blob_sha"], SOURCE_RESULT_BLOB_SHA)

    def test_direction_maps_explicitly_back_to_discovery_first_guardrail(self) -> None:
        value = build_exp066_temporal_state_transition_research_direction()
        self.assertEqual(
            value["governing_research_method"],
            GOVERNING_RESEARCH_METHOD,
        )
        self.assertEqual(value["successor_experiment_id"], SUCCESSOR_EXPERIMENT_ID)
        guardrail = value["discovery_first_guardrail"]
        for field in (
            "intended_market_behavior",
            "measurement_vocabulary_covered",
            "deliberately_not_covered",
            "why_useful_after_prior_evidence",
            "justified_negative_result_conclusion",
            "negative_result_does_not_justify",
            "survivor_rejoins_main_workflow",
        ):
            self.assertTrue(guardrail[field], field)
        self.assertIn(
            "DISCOVERY_FIRST_MARKET_PATTERN_RESEARCH_FAILED",
            guardrail["negative_result_does_not_justify"],
        )

    def test_direction_is_temporal_not_another_static_pairwise_rescue(self) -> None:
        value = build_exp066_temporal_state_transition_research_direction()
        direction = value["research_direction"]
        self.assertTrue(direction["temporal_state_transition_source_design_permitted"])
        self.assertTrue(direction["one_state_dimension_per_hypothesis"])
        self.assertTrue(direction["two_timepoint_state_path_only"])
        self.assertFalse(direction["longer_state_sequences_permitted"])
        self.assertFalse(direction["multi_dimension_transition_conjunctions_permitted"])
        self.assertFalse(direction["new_raw_feature_permitted"])
        self.assertFalse(direction["result_driven_lag_or_transition_expansion_permitted"])
        self.assertFalse(value["rerun_exp065_authorized"])
        self.assertFalse(value["retry_exp065_authorized"])
        self.assertFalse(value["replacement_exp065_authorized"])
        self.assertFalse(value["exp065_threshold_relaxation_authorized"])
        self.assertFalse(value["exp065_protocol_redefinition_authorized"])
        self.assertFalse(value["exp065_hypothesis_rescue_authorized"])

    def test_existing_market_universe_and_closed_reserve_are_preserved(self) -> None:
        value = build_exp066_temporal_state_transition_research_direction()
        universe = value["bounded_universe"]
        self.assertEqual(universe["symbols"], ["EURUSD", "GBPUSD", "USDJPY"])
        self.assertEqual(universe["timeframes"], ["5m", "15m", "1h"])
        self.assertEqual(universe["horizons_minutes"], [60, 240])
        self.assertEqual(len(universe["continuous_features"]), 20)
        self.assertEqual(universe["session_dimension"], "session_state")
        chronology = value["chronology"]
        self.assertEqual(chronology["retrospective_design_label"], "ALREADY_SEEN_DESIGN_EVIDENCE")
        self.assertTrue(chronology["2015_2022_may_not_be_called_fresh_validation"])
        self.assertFalse(chronology["reserved_robustness_opened"])
        self.assertTrue(chronology["genuinely_fresh_evidence_requires_later_prospective_observation"])

    def test_only_source_protocol_design_is_opened(self) -> None:
        value = build_exp066_temporal_state_transition_research_direction()
        self.assertTrue(value["successor_protocol_source_open_authorized"])
        for field in (
            "successor_execution_authorized",
            "successor_historical_result_authorized",
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
        self.assertEqual(
            value["next_gate"],
            "SOURCE_ONLY_EXP066_TEMPORAL_STATE_TRANSITION_PROTOCOL",
        )


if __name__ == "__main__":
    unittest.main()
