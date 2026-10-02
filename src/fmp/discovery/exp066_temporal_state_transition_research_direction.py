from __future__ import annotations

from .pattern_protocol import (
    CONTINUOUS_FEATURES,
    HORIZONS_MINUTES,
    SESSION_DIMENSION,
    SESSION_STATES,
    SYMBOLS,
    TIMEFRAMES,
)


POST_EXP065_RESEARCH_DIRECTION_DECISION = "DEC-469"
POST_EXP065_RESEARCH_DIRECTION_VERSION = (
    "fmp-exp066-temporal-state-transition-research-direction-v1"
)

GOVERNING_RESEARCH_METHOD = "DISCOVERY_FIRST_MARKET_PATTERN_RESEARCH"
SOURCE_RESULT_DECISION = "DEC-468"
SOURCE_RESULT_MERGE_SHA = "632afde7655bc650f04cec2d7bffb8da6893627e"
SOURCE_RESULT_BLOB_SHA = "12580fe033a29d4d25b61140a4cf53a7126547ea"
SOURCE_EXPERIMENT_ID = "EXP-20261001-065"
SUCCESSOR_EXPERIMENT_ID = "EXP-20261002-066"

SOURCE_HISTORICAL_RUN_ID = 36905224184
SOURCE_AGGREGATE_EVIDENCE_FINGERPRINT = (
    "be0822560c0c4ec5a7dfc90e85c65d963621e04a4bd238ea078a4ac4d7a99682"
)

RETROSPECTIVE_DESIGN_START = "2015-01-01"
RETROSPECTIVE_DESIGN_END = "2022-12-31"
RESERVED_ROBUSTNESS_START = "2023-01-01"
RESERVED_ROBUSTNESS_END = "2026-08-20"

SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = True
SUCCESSOR_EXECUTION_AUTHORIZED = False
SUCCESSOR_HISTORICAL_RESULT_AUTHORIZED = False

RERUN_EXP065_AUTHORIZED = False
RETRY_EXP065_AUTHORIZED = False
REPLACEMENT_EXP065_AUTHORIZED = False
EXP065_THRESHOLD_RELAXATION_AUTHORIZED = False
EXP065_PROTOCOL_REDEFINITION_AUTHORIZED = False
EXP065_HYPOTHESIS_RESCUE_AUTHORIZED = False

STATIC_DISCRETE_ATOMIC_STATE_FAMILY_CLOSED = True
SINGLE_FEATURE_CONTINUOUS_RANK_FAMILY_CLOSED = True
PAIRWISE_CONTINUOUS_INTERACTION_FAMILY_CLOSED = True

EXP066_TEMPORAL_STATE_TRANSITION_SOURCE_DESIGN_AUTHORIZED = True
EXP066_ONE_STATE_DIMENSION_PER_HYPOTHESIS = True
EXP066_TWO_TIMEPOINT_STATE_PATH_ONLY = True
EXP066_LONGER_SEQUENCE_AUTHORIZED = False
EXP066_MULTI_DIMENSION_TRANSITION_CONJUNCTION_AUTHORIZED = False
EXP066_NEW_RAW_FEATURE_AUTHORIZED = False
EXP066_NEW_SYMBOL_AUTHORIZED = False
EXP066_NEW_TIMEFRAME_AUTHORIZED = False
EXP066_NEW_HORIZON_AUTHORIZED = False

RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _validate_git_sha1(value: str, *, field: str) -> str:
    if len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git SHA-1")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _guardrail_mapping() -> dict[str, object]:
    return {
        "intended_market_behavior": (
            "REPEATED_FUTURE_RETURN_BEHAVIOUR_CONDITIONAL_ON_HOW_ONE_EXISTING_"
            "LEAKAGE_SAFE_MARKET_STATE_MOVED_FROM_A_FROZEN_PRIOR_OBSERVATION_"
            "TO_THE_CURRENT_OBSERVATION_INCLUDING_STATE_PERSISTENCE"
        ),
        "measurement_vocabulary_covered": [
            "direction_trend_state",
            "sideways_range_state",
            "volatility_and_volatility_change",
            "momentum_and_return_structure",
            "candle_range_structure",
            "session_time_context",
            "location_relative_to_previous_or_session_structure",
            "spread_quote_quality_context",
            "fixed_future_return_outcomes",
        ],
        "deliberately_not_covered": [
            "new_raw_features_or_alternative_data",
            "arbitrary_long_state_sequences",
            "continuous_change_magnitude_or_speed_within_a_state",
            "multi_dimension_transition_conjunctions",
            "three_plus_feature_interactions",
            "result_driven_lag_selection",
            "strategy_entry_stop_target_compilation",
            "reserved_2023_2026_robustness_access",
        ],
        "why_useful_after_prior_evidence": (
            "EXP061_EXP063_EXP064_AND_EXP065_PRIMARILY_TESTED_POINT_IN_TIME_"
            "STATE_LEVEL_CONTINUOUS_OR_STATIC_PAIRWISE_REPRESENTATIONS;_"
            "EXP066_ASKS_WHETHER_THE_PATH_INTO_OR_PERSISTENCE_OF_A_STATE_"
            "CARRIES_REPEATABLE_INFORMATION"
        ),
        "justified_negative_result_conclusion": (
            "THE_EXACT_FROZEN_EXP066_TWO_TIMEPOINT_SINGLE_DIMENSION_TRANSITION_"
            "REPRESENTATION_FAILED_ITS_PREDECLARED_GATE"
        ),
        "negative_result_does_not_justify": [
            "DISCOVERY_FIRST_MARKET_PATTERN_RESEARCH_FAILED",
            "NO_MARKET_EDGE_EXISTS",
            "ALL_TEMPORAL_MARKET_BEHAVIOUR_IS_EXHAUSTED",
            "OTHER_BOUNDED_REPRESENTATIONS_ARE_INVALID",
        ],
        "survivor_rejoins_main_workflow": (
            "FREEZE_EXACT_TRANSITION_PATTERN_THEN_REQUIRE_LATER_CHRONOLOGICAL_"
            "EVIDENCE_BEFORE_STRATEGY_COMPILATION_ROBUSTNESS_AND_PROSPECTIVE_"
            "SHADOW_OR_DEMO_GATES"
        ),
    }


def build_exp066_temporal_state_transition_research_direction() -> dict[str, object]:
    _validate_git_sha1(SOURCE_RESULT_MERGE_SHA, field="DEC-469 source result merge SHA")
    _validate_git_sha1(SOURCE_RESULT_BLOB_SHA, field="DEC-469 source result blob SHA")
    if SOURCE_RESULT_DECISION != "DEC-468":
        raise ValueError("DEC-469 source result decision drift")
    if SOURCE_EXPERIMENT_ID == SUCCESSOR_EXPERIMENT_ID:
        raise ValueError("DEC-469 successor experiment identity must be new")
    if tuple(SYMBOLS) != ("EURUSD", "GBPUSD", "USDJPY"):
        raise ValueError("DEC-469 symbol universe drift")
    if tuple(TIMEFRAMES) != ("5m", "15m", "1h"):
        raise ValueError("DEC-469 timeframe universe drift")
    if tuple(HORIZONS_MINUTES) != (60, 240):
        raise ValueError("DEC-469 horizon universe drift")
    if len(CONTINUOUS_FEATURES) != 20:
        raise ValueError("DEC-469 requires the same 20 continuous features")
    if SESSION_DIMENSION != "session_state" or len(SESSION_STATES) != 5:
        raise ValueError("DEC-469 session-state vocabulary drift")
    if RETROSPECTIVE_DESIGN_END >= RESERVED_ROBUSTNESS_START:
        raise ValueError("DEC-469 retrospective/reserved chronology overlap")
    if not all(
        (
            STATIC_DISCRETE_ATOMIC_STATE_FAMILY_CLOSED,
            SINGLE_FEATURE_CONTINUOUS_RANK_FAMILY_CLOSED,
            PAIRWISE_CONTINUOUS_INTERACTION_FAMILY_CLOSED,
        )
    ):
        raise ValueError("DEC-469 must keep predecessor representation families closed")
    if not EXP066_ONE_STATE_DIMENSION_PER_HYPOTHESIS:
        raise ValueError("DEC-469 transition hypothesis must use one state dimension")
    if not EXP066_TWO_TIMEPOINT_STATE_PATH_ONLY:
        raise ValueError("DEC-469 transition path must remain two-timepoint")
    if EXP066_LONGER_SEQUENCE_AUTHORIZED:
        raise ValueError("DEC-469 cannot authorize longer state sequences")
    if EXP066_MULTI_DIMENSION_TRANSITION_CONJUNCTION_AUTHORIZED:
        raise ValueError("DEC-469 cannot authorize multi-dimension transition conjunctions")

    guardrail = _guardrail_mapping()
    for field in (
        "intended_market_behavior",
        "measurement_vocabulary_covered",
        "deliberately_not_covered",
        "why_useful_after_prior_evidence",
        "justified_negative_result_conclusion",
        "negative_result_does_not_justify",
        "survivor_rejoins_main_workflow",
    ):
        if not guardrail.get(field):
            raise ValueError(f"DEC-469 discovery-first guardrail field missing: {field}")

    return {
        "decision": POST_EXP065_RESEARCH_DIRECTION_DECISION,
        "version": POST_EXP065_RESEARCH_DIRECTION_VERSION,
        "stage": "EXP066_TEMPORAL_STATE_TRANSITION_PROTOCOL_SOURCE_DESIGN_OPEN",
        "governing_research_method": GOVERNING_RESEARCH_METHOD,
        "source_result_decision": SOURCE_RESULT_DECISION,
        "source_result_merge_sha": SOURCE_RESULT_MERGE_SHA,
        "source_result_blob_sha": SOURCE_RESULT_BLOB_SHA,
        "source_experiment_id": SOURCE_EXPERIMENT_ID,
        "successor_experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "source_historical_run_id": SOURCE_HISTORICAL_RUN_ID,
        "source_aggregate_evidence_fingerprint": (
            SOURCE_AGGREGATE_EVIDENCE_FINGERPRINT
        ),
        "source_result": {
            "hypotheses": 13680,
            "evaluable_hypotheses": 13680,
            "qualifying_hypotheses": 0,
            "deduplicated_hypotheses": 0,
            "pairwise_interaction_shortlist_count": 0,
            "pairwise_interaction_frozen_count": 0,
            "classification": (
                "NO_PAIRWISE_INTERACTION_HYPOTHESIS_PASSED_FROZEN_GATE"
            ),
            "negative_result_scope": (
                "EXACT_FROZEN_EXP065_PAIRWISE_INTERACTION_PROTOCOL_ONLY"
            ),
            "discovery_first_method_rejected": False,
        },
        "research_direction": {
            "primary_question": (
                "CAN_BOUNDED_RECENT_SINGLE_DIMENSION_STATE_TRANSITIONS_OR_"
                "PERSISTENCE_FROM_EXISTING_LEAKAGE_SAFE_MEASUREMENTS_SHOW_"
                "REPEATABLE_FUTURE_RETURN_BEHAVIOUR_AFTER_STATIC_SNAPSHOT_"
                "REPRESENTATIONS_PRODUCED_NO_FROZEN_SURVIVORS"
            ),
            "temporal_state_transition_source_design_permitted": True,
            "one_state_dimension_per_hypothesis": True,
            "two_timepoint_state_path_only": True,
            "longer_state_sequences_permitted": False,
            "multi_dimension_transition_conjunctions_permitted": False,
            "new_raw_feature_permitted": False,
            "exact_prior_observation_lag_deferred_to_protocol": True,
            "exact_state_calibration_deferred_to_protocol": True,
            "exact_transition_inventory_deferred_to_protocol": True,
            "exact_search_volume_deferred_to_protocol": True,
            "support_stability_and_cost_gates_must_be_defined_before_execution": True,
            "result_driven_lag_or_transition_expansion_permitted": False,
        },
        "discovery_first_guardrail": guardrail,
        "bounded_universe": {
            "symbols": list(SYMBOLS),
            "timeframes": list(TIMEFRAMES),
            "horizons_minutes": list(HORIZONS_MINUTES),
            "continuous_features": list(CONTINUOUS_FEATURES),
            "session_dimension": SESSION_DIMENSION,
            "session_states": list(SESSION_STATES),
            "new_raw_features_authorized_by_dec469": False,
            "new_symbols_authorized_by_dec469": False,
            "new_timeframes_authorized_by_dec469": False,
            "new_horizons_authorized_by_dec469": False,
        },
        "chronology": {
            "retrospective_design_start": RETROSPECTIVE_DESIGN_START,
            "retrospective_design_end": RETROSPECTIVE_DESIGN_END,
            "retrospective_design_label": "ALREADY_SEEN_DESIGN_EVIDENCE",
            "2015_2022_may_not_be_called_fresh_validation": True,
            "reserved_robustness_start": RESERVED_ROBUSTNESS_START,
            "reserved_robustness_end": RESERVED_ROBUSTNESS_END,
            "reserved_robustness_opened": False,
            "genuinely_fresh_evidence_requires_later_prospective_observation": True,
        },
        "successor_protocol_source_open_authorized": (
            SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED
        ),
        "successor_execution_authorized": SUCCESSOR_EXECUTION_AUTHORIZED,
        "successor_historical_result_authorized": (
            SUCCESSOR_HISTORICAL_RESULT_AUTHORIZED
        ),
        "rerun_exp065_authorized": RERUN_EXP065_AUTHORIZED,
        "retry_exp065_authorized": RETRY_EXP065_AUTHORIZED,
        "replacement_exp065_authorized": REPLACEMENT_EXP065_AUTHORIZED,
        "exp065_threshold_relaxation_authorized": (
            EXP065_THRESHOLD_RELAXATION_AUTHORIZED
        ),
        "exp065_protocol_redefinition_authorized": (
            EXP065_PROTOCOL_REDEFINITION_AUTHORIZED
        ),
        "exp065_hypothesis_rescue_authorized": EXP065_HYPOTHESIS_RESCUE_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": "SOURCE_ONLY_EXP066_TEMPORAL_STATE_TRANSITION_PROTOCOL",
    }


__all__ = [
    "GOVERNING_RESEARCH_METHOD",
    "POST_EXP065_RESEARCH_DIRECTION_DECISION",
    "POST_EXP065_RESEARCH_DIRECTION_VERSION",
    "SOURCE_RESULT_BLOB_SHA",
    "SOURCE_RESULT_MERGE_SHA",
    "SUCCESSOR_EXPERIMENT_ID",
    "build_exp066_temporal_state_transition_research_direction",
]
