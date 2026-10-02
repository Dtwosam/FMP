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

GOVERNING_RESEARCH_METHOD = "DEC-268_DISCOVERY_FIRST_MARKET_PATTERN_RESEARCH"
CURRENT_SUB_EXPERIMENT = "EXP066_TEMPORAL_STATE_TRANSITION_DISCOVERY"

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

PAIRWISE_CONTINUOUS_INTERACTION_FAMILY_CLOSED = True
EXP066_TEMPORAL_TRANSITION_SOURCE_DESIGN_AUTHORIZED = True
EXP066_SAME_DIMENSION_TRANSITIONS_ONLY = True
EXP066_CROSS_DIMENSION_TRANSITIONS_AUTHORIZED = False
EXP066_SEQUENCE_LONGER_THAN_TWO_STATES_AUTHORIZED = False
EXP066_NEW_RAW_FEATURE_AUTHORIZED = False
EXP066_NEW_SYMBOL_AUTHORIZED = False
EXP066_NEW_TIMEFRAME_AUTHORIZED = False
EXP066_NEW_HORIZON_AUTHORIZED = False
EXP066_ALTERNATIVE_DATA_AUTHORIZED = False
EXP066_MODEL_FAMILY_AUTHORIZED = False

RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def build_exp066_temporal_state_transition_research_direction() -> dict[str, object]:
    if SOURCE_RESULT_DECISION != "DEC-468":
        raise ValueError("DEC-469 source result decision drift")
    if SOURCE_EXPERIMENT_ID == SUCCESSOR_EXPERIMENT_ID:
        raise ValueError("DEC-469 successor experiment identity must be new")
    if GOVERNING_RESEARCH_METHOD != "DEC-268_DISCOVERY_FIRST_MARKET_PATTERN_RESEARCH":
        raise ValueError("DEC-469 governing research method drift")
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
    if not PAIRWISE_CONTINUOUS_INTERACTION_FAMILY_CLOSED:
        raise ValueError("DEC-469 must close the EXP-065 pairwise family")
    if not EXP066_SAME_DIMENSION_TRANSITIONS_ONLY:
        raise ValueError("DEC-469 temporal transition direction must stay same-dimension")
    if EXP066_CROSS_DIMENSION_TRANSITIONS_AUTHORIZED:
        raise ValueError("DEC-469 cannot authorize cross-dimension transitions")
    if EXP066_SEQUENCE_LONGER_THAN_TWO_STATES_AUTHORIZED:
        raise ValueError("DEC-469 cannot authorize longer state sequences")

    guardrail_mapping = {
        "1_market_behaviour_intended_to_discover": (
            "Whether the path into a current leakage-safe market state carries "
            "repeatable information about fixed future outcomes: specifically, "
            "whether a prior state -> current state transition within one accepted "
            "measurement dimension matters beyond observing the current state alone."
        ),
        "2_dec268_measurement_vocabulary_covered": [
            "direction_and_trend_state",
            "sideways_and_range_state",
            "volatility_and_volatility_change",
            "momentum_and_return_structure",
            "candle_and_range_structure",
            "session_and_time_context",
            "location_relative_to_recent_or_session_structure",
            "spread_and_quote_quality_context",
            "fixed_future_return_or_price_path_outcomes",
        ],
        "3_deliberately_omitted": [
            "cross_dimension_transition_interactions",
            "state_sequences_longer_than_prior_to_current",
            "three_plus_feature_combinations",
            "new_raw_features",
            "new_symbols",
            "new_timeframes",
            "new_outcome_horizons",
            "alternative_data",
            "clustering_or_model_family_search",
            "reserved_2023_2026_data",
        ],
        "4_why_useful_after_prior_evidence": (
            "EXP-065 tested static pairwise continuous-feature interactions after "
            "controlling main effects and found no qualifiers. A temporal transition "
            "tests a distinct behavioural question: whether how the market arrived "
            "at a state matters. It is not a threshold relaxation, protocol rewrite, "
            "or rescue of an EXP-065 hypothesis."
        ),
        "5_negative_result_justifies": (
            "Rejecting only the exact frozen EXP-066 same-dimension prior-state -> "
            "current-state representation and protocol if no hypothesis survives."
        ),
        "6_negative_result_does_not_justify": (
            "It does not reject DEC-268 discovery-first market learning, prove that "
            "no market edge exists, or exhaust cross-dimension, longer-sequence, "
            "different-state, statistical, or prospective representations."
        ),
        "7_survivor_rejoins_main_workflow": (
            "A surviving transition remains a pattern hypothesis. It must be frozen, "
            "pass later chronological confirmation and validation without redesign, "
            "then receive separate strategy/model compilation, robustness/backtest, "
            "and prospective shadow/demo gates before any deployment claim."
        ),
    }

    return {
        "decision": POST_EXP065_RESEARCH_DIRECTION_DECISION,
        "version": POST_EXP065_RESEARCH_DIRECTION_VERSION,
        "governing_research_method": GOVERNING_RESEARCH_METHOD,
        "current_sub_experiment": CURRENT_SUB_EXPERIMENT,
        "stage": "EXP066_TEMPORAL_STATE_TRANSITION_PROTOCOL_SOURCE_DESIGN_OPEN",
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
            "shortlist_count": 0,
            "frozen_count": 0,
            "classification": (
                "NO_PAIRWISE_INTERACTION_HYPOTHESIS_PASSED_FROZEN_GATE"
            ),
        },
        "research_direction": {
            "primary_question": (
                "DOES_THE_TEMPORAL_PATH_INTO_AN_EXISTING_LEAKAGE_SAFE_MARKET_"
                "STATE_CARRY_STABLE_INFORMATION_ABOUT_FIXED_FUTURE_OUTCOMES"
            ),
            "pairwise_continuous_interaction_family_closed": True,
            "exp065_threshold_relaxation_permitted": False,
            "exp065_protocol_redefinition_permitted": False,
            "exp065_hypothesis_rescue_permitted": False,
            "temporal_transition_source_design_permitted": True,
            "same_dimension_transitions_only": True,
            "cross_dimension_transitions_permitted": False,
            "state_sequences_longer_than_two_permitted": False,
            "new_raw_feature_permitted": False,
            "alternative_data_permitted": False,
            "model_family_search_permitted": False,
            "exact_transition_lag_set_deferred_to_protocol": True,
            "exact_state_calibration_deferred_to_protocol": True,
            "exact_search_volume_deferred_to_protocol": True,
            "support_and_economic_gates_deferred_to_protocol": True,
            "chronological_discovery_confirmation_validation_must_be_frozen_before_execution": True,
        },
        "guardrail_mapping": guardrail_mapping,
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
            "alternative_data_authorized_by_dec469": False,
            "cross_dimension_transitions_authorized_by_dec469": False,
            "maximum_states_per_transition_hypothesis": 2,
        },
        "chronology": {
            "retrospective_design_start": RETROSPECTIVE_DESIGN_START,
            "retrospective_design_end": RETROSPECTIVE_DESIGN_END,
            "retrospective_design_label": "ALREADY_SEEN_DESIGN_EVIDENCE",
            "2015_2022_may_not_be_called_fresh_validation": True,
            "protocol_must_freeze_chronological_discovery_confirmation_validation": True,
            "reserved_robustness_start": RESERVED_ROBUSTNESS_START,
            "reserved_robustness_end": RESERVED_ROBUSTNESS_END,
            "reserved_robustness_opened": False,
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
    "CURRENT_SUB_EXPERIMENT",
    "GOVERNING_RESEARCH_METHOD",
    "POST_EXP065_RESEARCH_DIRECTION_DECISION",
    "POST_EXP065_RESEARCH_DIRECTION_VERSION",
    "SOURCE_RESULT_BLOB_SHA",
    "SOURCE_RESULT_MERGE_SHA",
    "SUCCESSOR_EXPERIMENT_ID",
    "build_exp066_temporal_state_transition_research_direction",
]
