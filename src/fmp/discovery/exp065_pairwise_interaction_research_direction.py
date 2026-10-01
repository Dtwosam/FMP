from __future__ import annotations

from .pattern_protocol import CONTINUOUS_FEATURES, HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


POST_EXP064_RESEARCH_DIRECTION_DECISION = "DEC-459"
POST_EXP064_RESEARCH_DIRECTION_VERSION = (
    "fmp-exp065-pairwise-interaction-research-direction-v1"
)

SOURCE_RESULT_DECISION = "DEC-458"
SOURCE_RESULT_MERGE_SHA = "e3c2a7a1dbb6592a8438f3949ffa83177e31f4e6"
SOURCE_RESULT_BLOB_SHA = "c5878685950e14a632b4eb8d2616d9540afb12d2"
SOURCE_EXPERIMENT_ID = "EXP-20261001-064"
SUCCESSOR_EXPERIMENT_ID = "EXP-20261001-065"

SOURCE_HISTORICAL_RUN_ID = 36853290904
SOURCE_AGGREGATE_EVIDENCE_FINGERPRINT = (
    "832e8c814ac578b614764d37cba15e64569e2f841dfa6f72f2c9cd9a8fdbcbb1"
)

RETROSPECTIVE_DESIGN_START = "2015-01-01"
RETROSPECTIVE_DESIGN_END = "2022-12-31"
RESERVED_ROBUSTNESS_START = "2023-01-01"
RESERVED_ROBUSTNESS_END = "2026-08-20"

SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = True
SUCCESSOR_EXECUTION_AUTHORIZED = False
SUCCESSOR_HISTORICAL_RESULT_AUTHORIZED = False

RERUN_EXP064_AUTHORIZED = False
RETRY_EXP064_AUTHORIZED = False
REPLACEMENT_EXP064_AUTHORIZED = False

EXP064_THRESHOLD_RELAXATION_AUTHORIZED = False
EXP064_PROTOCOL_REDEFINITION_AUTHORIZED = False
EXP064_HYPOTHESIS_RESCUE_AUTHORIZED = False

DISCRETE_TERTILE_ATOMIC_STATE_FAMILY_CLOSED = True
SINGLE_FEATURE_CONTINUOUS_RANK_FAMILY_CLOSED = True

EXP065_PAIRWISE_INTERACTION_SOURCE_DESIGN_AUTHORIZED = True
EXP065_EXACTLY_TWO_FEATURES_PER_HYPOTHESIS = True
EXP065_THREE_PLUS_FEATURE_INTERACTIONS_AUTHORIZED = False
EXP065_NEW_RAW_FEATURE_AUTHORIZED = False
EXP065_NEW_SYMBOL_AUTHORIZED = False
EXP065_NEW_TIMEFRAME_AUTHORIZED = False
EXP065_NEW_HORIZON_AUTHORIZED = False

RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def build_exp065_pairwise_interaction_research_direction() -> dict[str, object]:
    if SOURCE_RESULT_DECISION != "DEC-458":
        raise ValueError("DEC-459 source result decision drift")
    if SOURCE_EXPERIMENT_ID == SUCCESSOR_EXPERIMENT_ID:
        raise ValueError("DEC-459 successor experiment identity must be new")
    if tuple(SYMBOLS) != ("EURUSD", "GBPUSD", "USDJPY"):
        raise ValueError("DEC-459 symbol universe drift")
    if tuple(TIMEFRAMES) != ("5m", "15m", "1h"):
        raise ValueError("DEC-459 timeframe universe drift")
    if tuple(HORIZONS_MINUTES) != (60, 240):
        raise ValueError("DEC-459 horizon universe drift")
    if len(CONTINUOUS_FEATURES) != 20:
        raise ValueError("DEC-459 requires the same 20 continuous features")
    if RETROSPECTIVE_DESIGN_END >= RESERVED_ROBUSTNESS_START:
        raise ValueError("DEC-459 retrospective/reserved chronology overlap")
    if not DISCRETE_TERTILE_ATOMIC_STATE_FAMILY_CLOSED:
        raise ValueError("DEC-459 must keep the EXP-061/063 atomic-state family closed")
    if not SINGLE_FEATURE_CONTINUOUS_RANK_FAMILY_CLOSED:
        raise ValueError("DEC-459 must close the EXP-064 single-feature family")
    if not EXP065_EXACTLY_TWO_FEATURES_PER_HYPOTHESIS:
        raise ValueError("DEC-459 successor must remain pairwise")
    if EXP065_THREE_PLUS_FEATURE_INTERACTIONS_AUTHORIZED:
        raise ValueError("DEC-459 cannot authorize 3+ feature interactions")

    return {
        "decision": POST_EXP064_RESEARCH_DIRECTION_DECISION,
        "version": POST_EXP064_RESEARCH_DIRECTION_VERSION,
        "stage": "EXP065_PAIRWISE_INTERACTION_PROTOCOL_SOURCE_DESIGN_OPEN",
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
            "hypotheses": 1440,
            "evaluable_hypotheses": 1440,
            "qualifying_hypotheses": 0,
            "deduplicated_hypotheses": 0,
            "continuous_stability_shortlist_count": 0,
            "continuous_stability_frozen_count": 0,
            "classification": (
                "NO_CONTINUOUS_STABILITY_HYPOTHESIS_PASSED_FROZEN_GATE"
            ),
        },
        "research_direction": {
            "primary_question": (
                "CAN_BOUNDED_EXACTLY_TWO_FEATURE_INTERACTIONS_FROM_THE_EXISTING_"
                "LEAKAGE_SAFE_FEATURE_SET_SHOW_STABLE_ECONOMIC_EFFECTS_ACROSS_"
                "ALREADY_SEEN_YEARS_WHERE_SINGLE_FEATURE_EFFECTS_DID_NOT"
            ),
            "discrete_tertile_atomic_state_family_closed": True,
            "single_feature_continuous_rank_family_closed": True,
            "exp064_threshold_relaxation_permitted": False,
            "exp064_protocol_redefinition_permitted": False,
            "exp064_hypothesis_rescue_permitted": False,
            "pairwise_interaction_source_design_permitted": True,
            "exactly_two_features_per_hypothesis": True,
            "three_plus_feature_interactions_permitted": False,
            "new_raw_feature_permitted": False,
            "exact_pair_construction_deferred_to_protocol": True,
            "exact_interaction_transform_deferred_to_protocol": True,
            "exact_interaction_estimator_deferred_to_protocol": True,
            "exact_main_effect_control_policy_deferred_to_protocol": True,
            "exact_search_volume_deferred_to_protocol": True,
            "annual_stability_requirement_must_be_defined_before_execution": True,
            "cost_stress_requirement_must_be_defined_before_execution": True,
            "interaction_incrementality_requirement_must_be_defined_before_execution": (
                True
            ),
        },
        "bounded_universe": {
            "symbols": list(SYMBOLS),
            "timeframes": list(TIMEFRAMES),
            "horizons_minutes": list(HORIZONS_MINUTES),
            "continuous_features": list(CONTINUOUS_FEATURES),
            "new_raw_features_authorized_by_dec459": False,
            "new_symbols_authorized_by_dec459": False,
            "new_timeframes_authorized_by_dec459": False,
            "new_horizons_authorized_by_dec459": False,
            "maximum_features_per_successor_hypothesis": 2,
        },
        "chronology": {
            "retrospective_design_start": RETROSPECTIVE_DESIGN_START,
            "retrospective_design_end": RETROSPECTIVE_DESIGN_END,
            "retrospective_design_label": "ALREADY_SEEN_DESIGN_EVIDENCE",
            "2015_2022_may_not_be_called_fresh_validation": True,
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
        "rerun_exp064_authorized": RERUN_EXP064_AUTHORIZED,
        "retry_exp064_authorized": RETRY_EXP064_AUTHORIZED,
        "replacement_exp064_authorized": REPLACEMENT_EXP064_AUTHORIZED,
        "exp064_threshold_relaxation_authorized": (
            EXP064_THRESHOLD_RELAXATION_AUTHORIZED
        ),
        "exp064_protocol_redefinition_authorized": (
            EXP064_PROTOCOL_REDEFINITION_AUTHORIZED
        ),
        "exp064_hypothesis_rescue_authorized": (
            EXP064_HYPOTHESIS_RESCUE_AUTHORIZED
        ),
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
        "next_gate": "SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_PROTOCOL",
    }


__all__ = [
    "POST_EXP064_RESEARCH_DIRECTION_DECISION",
    "POST_EXP064_RESEARCH_DIRECTION_VERSION",
    "SOURCE_RESULT_BLOB_SHA",
    "SOURCE_RESULT_MERGE_SHA",
    "SUCCESSOR_EXPERIMENT_ID",
    "build_exp065_pairwise_interaction_research_direction",
]
