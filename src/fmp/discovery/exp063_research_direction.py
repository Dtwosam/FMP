from __future__ import annotations


POST_EXP062_RESEARCH_DIRECTION_DECISION = "DEC-443"
POST_EXP062_RESEARCH_DIRECTION_VERSION = (
    "fmp-exp063-persistence-first-research-direction-v1"
)

SOURCE_DIAGNOSTIC_DECISION = "DEC-442"
SOURCE_DIAGNOSTIC_MERGE_SHA = "4e9bc6ea384f4bcf40444567a9585be24787d71b"
SOURCE_DIAGNOSTIC_BLOB_SHA = "2eac2cd32edf151a3eeca806a65a34af914cbea4"

SOURCE_EXPERIMENT_ID = "EXP-20260927-062"
SUCCESSOR_EXPERIMENT_ID = "EXP-20260930-063"

SOURCE_HISTORICAL_RUN_ID = 36714210992
SOURCE_AGGREGATE_EVIDENCE_FINGERPRINT = (
    "b8019226fb7fce14c6711834fe16cdbb52795d9ca8996b1ed98ede7ecfba9506"
)

V1_SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
V1_TIMEFRAMES = ("5m", "15m", "1h")
V1_HORIZONS_MINUTES = (60, 240)

RETROSPECTIVE_DESIGN_START = "2015-01-01"
RETROSPECTIVE_DESIGN_END = "2022-12-31"
RESERVED_ROBUSTNESS_START = "2023-01-01"
RESERVED_ROBUSTNESS_END = "2026-08-20"

SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = True
SUCCESSOR_EXECUTION_AUTHORIZED = False
SUCCESSOR_HISTORICAL_RESULT_AUTHORIZED = False
RERUN_EXP062_AUTHORIZED = False
RETRY_EXP062_AUTHORIZED = False
REPLACEMENT_EXP062_AUTHORIZED = False
THRESHOLD_RELAXATION_AUTHORIZED = False
PATTERN_REDEFINITION_AUTHORIZED = False
SEARCH_UNIVERSE_EXPANSION_AUTHORIZED = False
NEW_SYMBOL_AUTHORIZED = False
NEW_TIMEFRAME_AUTHORIZED = False
NEW_HORIZON_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def build_exp063_persistence_first_research_direction() -> dict[str, object]:
    if SOURCE_DIAGNOSTIC_DECISION != "DEC-442":
        raise ValueError("DEC-443 source diagnostic decision drift")
    if SUCCESSOR_EXPERIMENT_ID == SOURCE_EXPERIMENT_ID:
        raise ValueError("DEC-443 successor experiment identity must be new")
    if V1_SYMBOLS != ("EURUSD", "GBPUSD", "USDJPY"):
        raise ValueError("DEC-443 V1 symbol universe drift")
    if V1_TIMEFRAMES != ("5m", "15m", "1h"):
        raise ValueError("DEC-443 timeframe universe drift")
    if V1_HORIZONS_MINUTES != (60, 240):
        raise ValueError("DEC-443 horizon universe drift")
    if RETROSPECTIVE_DESIGN_END >= RESERVED_ROBUSTNESS_START:
        raise ValueError("DEC-443 retrospective/reserved chronology overlap")

    return {
        "decision": POST_EXP062_RESEARCH_DIRECTION_DECISION,
        "version": POST_EXP062_RESEARCH_DIRECTION_VERSION,
        "stage": "EXP063_PERSISTENCE_FIRST_PROTOCOL_SOURCE_DESIGN_OPEN",
        "source_diagnostic_decision": SOURCE_DIAGNOSTIC_DECISION,
        "source_diagnostic_merge_sha": SOURCE_DIAGNOSTIC_MERGE_SHA,
        "source_diagnostic_blob_sha": SOURCE_DIAGNOSTIC_BLOB_SHA,
        "source_experiment_id": SOURCE_EXPERIMENT_ID,
        "successor_experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "source_historical_run_id": SOURCE_HISTORICAL_RUN_ID,
        "source_aggregate_evidence_fingerprint": (
            SOURCE_AGGREGATE_EVIDENCE_FINGERPRINT
        ),
        "diagnostic_basis": {
            "confirmation_survivor_count": 11,
            "validation_accepted_count": 0,
            "all_confirmation_survivors_horizon_minutes": 240,
            "all_failed_positive_aggregate_validation_mean": True,
            "all_failed_three_of_four_positive_validation_years": True,
            "broad_validation_sample_size_shortage": False,
            "runtime_or_adapter_failure_detected": False,
        },
        "research_direction": {
            "primary_question": (
                "CAN_PERSISTENCE_AWARE_SELECTION_REDUCE_TEMPORAL_EDGE_DECAY_"
                "BEFORE_ANY_RESERVED_ROBUSTNESS_EVALUATION"
            ),
            "persistence_first_selection_required": True,
            "retrospective_year_balance_required": True,
            "single_period_strength_must_not_dominate_selection": True,
            "exact_persistence_metric_deferred_to_protocol": True,
            "exact_internal_chronology_deferred_to_protocol": True,
            "threshold_relaxation_permitted": False,
            "exp062_pattern_rescue_permitted": False,
        },
        "bounded_universe": {
            "symbols": list(V1_SYMBOLS),
            "timeframes": list(V1_TIMEFRAMES),
            "horizons_minutes": list(V1_HORIZONS_MINUTES),
            "new_features_authorized_by_dec443": False,
            "new_symbols_authorized_by_dec443": False,
            "new_timeframes_authorized_by_dec443": False,
            "new_horizons_authorized_by_dec443": False,
        },
        "chronology": {
            "retrospective_design_start": RETROSPECTIVE_DESIGN_START,
            "retrospective_design_end": RETROSPECTIVE_DESIGN_END,
            "retrospective_design_label": "ALREADY_SEEN_DESIGN_EVIDENCE",
            "2019_2022_may_not_be_called_fresh_validation": True,
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
        "rerun_exp062_authorized": RERUN_EXP062_AUTHORIZED,
        "retry_exp062_authorized": RETRY_EXP062_AUTHORIZED,
        "replacement_exp062_authorized": REPLACEMENT_EXP062_AUTHORIZED,
        "threshold_relaxation_authorized": THRESHOLD_RELAXATION_AUTHORIZED,
        "pattern_redefinition_authorized": PATTERN_REDEFINITION_AUTHORIZED,
        "search_universe_expansion_authorized": (
            SEARCH_UNIVERSE_EXPANSION_AUTHORIZED
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
        "next_gate": "SOURCE_ONLY_EXP063_PERSISTENCE_FIRST_PROTOCOL",
    }


__all__ = [
    "POST_EXP062_RESEARCH_DIRECTION_DECISION",
    "POST_EXP062_RESEARCH_DIRECTION_VERSION",
    "SOURCE_DIAGNOSTIC_BLOB_SHA",
    "SOURCE_DIAGNOSTIC_MERGE_SHA",
    "SUCCESSOR_EXPERIMENT_ID",
    "build_exp063_persistence_first_research_direction",
]
