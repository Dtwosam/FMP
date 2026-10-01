from __future__ import annotations

from .pattern_protocol import CONTINUOUS_FEATURES, HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


POST_EXP063_RESEARCH_DIRECTION_DECISION = "DEC-451"
POST_EXP063_RESEARCH_DIRECTION_VERSION = (
    "fmp-exp064-continuous-stability-research-direction-v1"
)

SOURCE_RESULT_DECISION = "DEC-450"
SOURCE_RESULT_MERGE_SHA = "839af1e85b526c3c2a11b228e4aa8d3865589f06"
SOURCE_RESULT_BLOB_SHA = "b572dbf4801c211b72285049654ebf4d96744cf1"
SOURCE_EXPERIMENT_ID = "EXP-20260930-063"
SUCCESSOR_EXPERIMENT_ID = "EXP-20261001-064"

SOURCE_HISTORICAL_RUN_ID = 36773288493
SOURCE_AGGREGATE_EVIDENCE_FINGERPRINT = (
    "d0562d29da38c8ee4c0d3b28c35b3de7c9c42a5157910eef319a91b67ca4be42"
)

RETROSPECTIVE_DESIGN_START = "2015-01-01"
RETROSPECTIVE_DESIGN_END = "2022-12-31"
RESERVED_ROBUSTNESS_START = "2023-01-01"
RESERVED_ROBUSTNESS_END = "2026-08-20"

SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = True
SUCCESSOR_EXECUTION_AUTHORIZED = False
SUCCESSOR_HISTORICAL_RESULT_AUTHORIZED = False

RERUN_EXP063_AUTHORIZED = False
RETRY_EXP063_AUTHORIZED = False
REPLACEMENT_EXP063_AUTHORIZED = False

EXP063_THRESHOLD_RELAXATION_AUTHORIZED = False
EXP063_PATTERN_REDEFINITION_AUTHORIZED = False
EXP063_PATTERN_RESCUE_AUTHORIZED = False

DISCRETE_TERTILE_ATOMIC_STATE_FAMILY_CLOSED = True
EXP064_NEW_RAW_FEATURE_AUTHORIZED = False
EXP064_NEW_SYMBOL_AUTHORIZED = False
EXP064_NEW_TIMEFRAME_AUTHORIZED = False
EXP064_NEW_HORIZON_AUTHORIZED = False
EXP064_EXISTING_FEATURE_TRANSFORM_SOURCE_DESIGN_AUTHORIZED = True
EXP064_CONTINUOUS_OR_RANK_EFFECT_SOURCE_DESIGN_AUTHORIZED = True

RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def build_exp064_continuous_stability_research_direction() -> dict[str, object]:
    if SOURCE_RESULT_DECISION != "DEC-450":
        raise ValueError("DEC-451 source result decision drift")
    if SOURCE_EXPERIMENT_ID == SUCCESSOR_EXPERIMENT_ID:
        raise ValueError("DEC-451 successor experiment identity must be new")
    if tuple(SYMBOLS) != ("EURUSD", "GBPUSD", "USDJPY"):
        raise ValueError("DEC-451 symbol universe drift")
    if tuple(TIMEFRAMES) != ("5m", "15m", "1h"):
        raise ValueError("DEC-451 timeframe universe drift")
    if tuple(HORIZONS_MINUTES) != (60, 240):
        raise ValueError("DEC-451 horizon universe drift")
    if len(CONTINUOUS_FEATURES) != 20:
        raise ValueError("DEC-451 requires the same 20 continuous features")
    if RETROSPECTIVE_DESIGN_END >= RESERVED_ROBUSTNESS_START:
        raise ValueError("DEC-451 retrospective/reserved chronology overlap")
    if not DISCRETE_TERTILE_ATOMIC_STATE_FAMILY_CLOSED:
        raise ValueError("DEC-451 must close the EXP-061/063 atomic-state family")

    return {
        "decision": POST_EXP063_RESEARCH_DIRECTION_DECISION,
        "version": POST_EXP063_RESEARCH_DIRECTION_VERSION,
        "stage": "EXP064_CONTINUOUS_STABILITY_PROTOCOL_SOURCE_DESIGN_OPEN",
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
            "enumerated_patterns": 37350,
            "directional_hypotheses": 74700,
            "qualifying_directional_hypotheses": 0,
            "persistence_shortlist_count": 0,
            "persistence_frozen_count": 0,
            "classification": (
                "NO_DIRECTIONAL_HYPOTHESIS_PASSED_FROZEN_PERSISTENCE_GATE"
            ),
        },
        "research_direction": {
            "primary_question": (
                "CAN_SIMPLE_CONTINUOUS_OR_RANK_BASED_EFFECTS_FROM_THE_EXISTING_"
                "LEAKAGE_SAFE_FEATURE_SET_SHOW_STABLE_SIGN_AND_ECONOMIC_EFFECT_"
                "ACROSS_ALREADY_SEEN_YEARS_WITHOUT_TERTILE_ATOMIC_STATE_SEARCH"
            ),
            "discrete_tertile_atomic_state_family_closed": True,
            "exp061_exp063_one_two_predicate_family_closed": True,
            "threshold_relaxation_permitted": False,
            "exp063_pattern_rescue_permitted": False,
            "continuous_or_rank_effect_source_design_permitted": True,
            "deterministic_existing_feature_transforms_permitted": True,
            "new_raw_feature_permitted": False,
            "exact_effect_estimator_deferred_to_protocol": True,
            "exact_normalization_or_rank_method_deferred_to_protocol": True,
            "exact_interaction_policy_deferred_to_protocol": True,
            "exact_search_volume_deferred_to_protocol": True,
            "annual_stability_requirement_must_be_defined_before_execution": True,
            "cost_stress_requirement_must_be_defined_before_execution": True,
        },
        "bounded_universe": {
            "symbols": list(SYMBOLS),
            "timeframes": list(TIMEFRAMES),
            "horizons_minutes": list(HORIZONS_MINUTES),
            "continuous_features": list(CONTINUOUS_FEATURES),
            "new_raw_features_authorized_by_dec451": False,
            "new_symbols_authorized_by_dec451": False,
            "new_timeframes_authorized_by_dec451": False,
            "new_horizons_authorized_by_dec451": False,
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
        "rerun_exp063_authorized": RERUN_EXP063_AUTHORIZED,
        "retry_exp063_authorized": RETRY_EXP063_AUTHORIZED,
        "replacement_exp063_authorized": REPLACEMENT_EXP063_AUTHORIZED,
        "exp063_threshold_relaxation_authorized": (
            EXP063_THRESHOLD_RELAXATION_AUTHORIZED
        ),
        "exp063_pattern_redefinition_authorized": (
            EXP063_PATTERN_REDEFINITION_AUTHORIZED
        ),
        "exp063_pattern_rescue_authorized": EXP063_PATTERN_RESCUE_AUTHORIZED,
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
        "next_gate": "SOURCE_ONLY_EXP064_CONTINUOUS_STABILITY_PROTOCOL",
    }


__all__ = [
    "POST_EXP063_RESEARCH_DIRECTION_DECISION",
    "POST_EXP063_RESEARCH_DIRECTION_VERSION",
    "SOURCE_RESULT_BLOB_SHA",
    "SOURCE_RESULT_MERGE_SHA",
    "SUCCESSOR_EXPERIMENT_ID",
    "build_exp064_continuous_stability_research_direction",
]
