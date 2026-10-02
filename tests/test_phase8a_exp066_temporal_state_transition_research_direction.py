from __future__ import annotations

import unittest

from fmp.discovery.exp066_temporal_state_transition_research_direction import (
    CURRENT_SUB_EXPERIMENT,
    GOVERNING_RESEARCH_METHOD,
    POST_EXP065_RESEARCH_DIRECTION_DECISION,
    POST_EXP065_RESEARCH_DIRECTION_VERSION,
    SOURCE_RESULT_BLOB_SHA,
    SOURCE_RESULT_MERGE_SHA,
    SUCCESSOR_EXPERIMENT_ID,
    build_exp066_temporal_state_transition_research_direction,
)


class Exp066TemporalStateTransitionResearchDirectionTests(unittest.TestCase):
    def test_direction_binds_dec468_and_new_experiment_identity(self) -> None:
        value = build_exp066_temporal_state_transition_research_direction()

        self.assertEqual(POST_EXP065_RESEARCH_DIRECTION_DECISION, "DEC-469")
        self.assertEqual(
            POST_EXP065_RESEARCH_DIRECTION_VERSION,
            "fmp-exp066-temporal-state-transition-research-direction-v1",
        )
        self.assertEqual(
            SOURCE_RESULT_MERGE_SHA,
            "632afde7655bc650f04cec2d7bffb8da6893627e",
        )
        self.assertEqual(
            SOURCE_RESULT_BLOB_SHA,
            "12580fe033a29d4d25b61140a4cf53a7126547ea",
        )
        self.assertEqual(SUCCESSOR_EXPERIMENT_ID, "EXP-20261002-066")
        self.assertEqual(value["source_result_decision"], "DEC-468")
        self.assertEqual(value["source_experiment_id"], "EXP-20261001-065")
        self.assertEqual(value["successor_experiment_id"], "EXP-20261002-066")
        self.assertEqual(value["source_historical_run_id"], 36905224184)
        self.assertEqual(
            value["source_aggregate_evidence_fingerprint"],
            "be0822560c0c4ec5a7dfc90e85c65d963621e04a4bd238ea078a4ac4d7a99682",
        )

    def test_direction_keeps_method_separate_from_sub_experiment(self) -> None:
        value = build_exp066_temporal_state_transition_research_direction()

        self.assertEqual(
            GOVERNING_RESEARCH_METHOD,
            "DEC-268_DISCOVERY_FIRST_MARKET_PATTERN_RESEARCH",
        )
        self.assertEqual(
            CURRENT_SUB_EXPERIMENT,
            "EXP066_TEMPORAL_STATE_TRANSITION_DISCOVERY",
        )
        self.assertEqual(value["governing_research_method"], GOVERNING_RESEARCH_METHOD)
        self.assertEqual(value["current_sub_experiment"], CURRENT_SUB_EXPERIMENT)

    def test_direction_uses_exact_exp065_negative_result(self) -> None:
        result = build_exp066_temporal_state_transition_research_direction()[
            "source_result"
        ]

        self.assertEqual(result["hypotheses"], 13680)
        self.assertEqual(result["evaluable_hypotheses"], 13680)
        self.assertEqual(result["qualifying_hypotheses"], 0)
        self.assertEqual(result["deduplicated_hypotheses"], 0)
        self.assertEqual(result["shortlist_count"], 0)
        self.assertEqual(result["frozen_count"], 0)
        self.assertEqual(
            result["classification"],
            "NO_PAIRWISE_INTERACTION_HYPOTHESIS_PASSED_FROZEN_GATE",
        )

    def test_guardrail_mapping_answers_all_seven_required_questions(self) -> None:
        mapping = build_exp066_temporal_state_transition_research_direction()[
            "guardrail_mapping"
        ]

        self.assertEqual(
            set(mapping),
            {
                "1_market_behaviour_intended_to_discover",
                "2_dec268_measurement_vocabulary_covered",
                "3_deliberately_omitted",
                "4_why_useful_after_prior_evidence",
                "5_negative_result_justifies",
                "6_negative_result_does_not_justify",
                "7_survivor_rejoins_main_workflow",
            },
        )
        self.assertIn(
            "prior state -> current state",
            mapping["1_market_behaviour_intended_to_discover"],
        )
        self.assertIn(
            "EXP-065",
            mapping["4_why_useful_after_prior_evidence"],
        )
        self.assertIn(
            "does not reject DEC-268",
            mapping["6_negative_result_does_not_justify"],
        )
        self.assertIn(
            "chronological confirmation and validation",
            mapping["7_survivor_rejoins_main_workflow"],
        )

    def test_direction_opens_only_bounded_temporal_transition_design(self) -> None:
        direction = build_exp066_temporal_state_transition_research_direction()[
            "research_direction"
        ]

        self.assertTrue(direction["pairwise_continuous_interaction_family_closed"])
        self.assertFalse(direction["exp065_threshold_relaxation_permitted"])
        self.assertFalse(direction["exp065_protocol_redefinition_permitted"])
        self.assertFalse(direction["exp065_hypothesis_rescue_permitted"])
        self.assertTrue(direction["temporal_transition_source_design_permitted"])
        self.assertTrue(direction["same_dimension_transitions_only"])
        self.assertFalse(direction["cross_dimension_transitions_permitted"])
        self.assertFalse(direction["state_sequences_longer_than_two_permitted"])
        self.assertFalse(direction["new_raw_feature_permitted"])
        self.assertFalse(direction["alternative_data_permitted"])
        self.assertFalse(direction["model_family_search_permitted"])

    def test_measurement_coverage_and_omissions_are_explicit(self) -> None:
        mapping = build_exp066_temporal_state_transition_research_direction()[
            "guardrail_mapping"
        ]
        covered = mapping["2_dec268_measurement_vocabulary_covered"]
        omitted = mapping["3_deliberately_omitted"]

        self.assertIn("volatility_and_volatility_change", covered)
        self.assertIn("session_and_time_context", covered)
        self.assertIn("spread_and_quote_quality_context", covered)
        self.assertIn("fixed_future_return_or_price_path_outcomes", covered)
        self.assertIn("cross_dimension_transition_interactions", omitted)
        self.assertIn("state_sequences_longer_than_prior_to_current", omitted)
        self.assertIn("reserved_2023_2026_data", omitted)

    def test_market_feature_and_state_universe_remains_bounded(self) -> None:
        bounded = build_exp066_temporal_state_transition_research_direction()[
            "bounded_universe"
        ]

        self.assertEqual(bounded["symbols"], ["EURUSD", "GBPUSD", "USDJPY"])
        self.assertEqual(bounded["timeframes"], ["5m", "15m", "1h"])
        self.assertEqual(bounded["horizons_minutes"], [60, 240])
        self.assertEqual(len(bounded["continuous_features"]), 20)
        self.assertEqual(bounded["session_dimension"], "session_state")
        self.assertEqual(len(bounded["session_states"]), 5)
        self.assertEqual(bounded["maximum_states_per_transition_hypothesis"], 2)
        self.assertFalse(bounded["new_raw_features_authorized_by_dec469"])
        self.assertFalse(bounded["new_symbols_authorized_by_dec469"])
        self.assertFalse(bounded["new_timeframes_authorized_by_dec469"])
        self.assertFalse(bounded["new_horizons_authorized_by_dec469"])
        self.assertFalse(bounded["alternative_data_authorized_by_dec469"])
        self.assertFalse(bounded["cross_dimension_transitions_authorized_by_dec469"])

    def test_all_execution_and_downstream_paths_remain_locked(self) -> None:
        value = build_exp066_temporal_state_transition_research_direction()

        self.assertTrue(value["successor_protocol_source_open_authorized"])
        for field in (
            "successor_execution_authorized",
            "successor_historical_result_authorized",
            "rerun_exp065_authorized",
            "retry_exp065_authorized",
            "replacement_exp065_authorized",
            "exp065_threshold_relaxation_authorized",
            "exp065_protocol_redefinition_authorized",
            "exp065_hypothesis_rescue_authorized",
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
        chronology = build_exp066_temporal_state_transition_research_direction()[
            "chronology"
        ]

        self.assertEqual(chronology["retrospective_design_start"], "2015-01-01")
        self.assertEqual(chronology["retrospective_design_end"], "2022-12-31")
        self.assertEqual(
            chronology["retrospective_design_label"],
            "ALREADY_SEEN_DESIGN_EVIDENCE",
        )
        self.assertTrue(chronology["2015_2022_may_not_be_called_fresh_validation"])
        self.assertTrue(
            chronology[
                "protocol_must_freeze_chronological_discovery_confirmation_validation"
            ]
        )
        self.assertEqual(chronology["reserved_robustness_start"], "2023-01-01")
        self.assertEqual(chronology["reserved_robustness_end"], "2026-08-20")
        self.assertFalse(chronology["reserved_robustness_opened"])

    def test_next_gate_is_source_only_protocol(self) -> None:
        value = build_exp066_temporal_state_transition_research_direction()

        self.assertEqual(
            value["next_gate"],
            "SOURCE_ONLY_EXP066_TEMPORAL_STATE_TRANSITION_PROTOCOL",
        )


if __name__ == "__main__":
    unittest.main()
