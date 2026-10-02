from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Sequence

from .annual_pattern_catalogue_method import (
    ANNUAL_PATTERN_CATALOGUE_METHOD_DECISION,
    GOVERNING_RESEARCH_METHOD,
    collection_segments,
)
from .pattern_protocol import (
    CONTINUOUS_FEATURES,
    DIRECTIONS,
    HORIZONS_MINUTES,
    QUANTILE_STATES,
    SESSION_DIMENSION,
    SESSION_STATES,
    SYMBOLS,
    TIMEFRAMES,
    empirical_tertile_cutpoints,
    quantile_state,
)


ANNUAL_CATALOGUE_PROTOCOL_DECISION = "DEC-470"
ANNUAL_CATALOGUE_PROTOCOL_VERSION = "fmp-annual-pattern-catalogue-protocol-v1"
EXPERIMENT_ID = "EXP-20261002-067"
SOURCE_METHOD_DECISION = "DEC-469"
SOURCE_METHOD_MERGE_SHA = "248ee27036d54c2ce3ad3ad051dcc8b0cbbbcfd1"

EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"
UNTOUCHED_OOS = False

PATTERN_FAMILIES = (
    "SNAPSHOT_SINGLE",
    "SNAPSHOT_PAIR",
    "SAME_DIMENSION_TRANSITION",
)
DIMENSION_STATES = {
    **{name: QUANTILE_STATES for name in CONTINUOUS_FEATURES},
    SESSION_DIMENSION: SESSION_STATES,
}
TRANSITION_LAGS_MINUTES = (60, 240)
MIN_PRIOR_CALIBRATION_ROWS = 300
MIN_ANNUAL_EVALUABLE_SUPPORT = 75

DISCOVERY_SLIPPAGE_PIPS = 0.5
STRESS_SLIPPAGE_PIPS = 1.0

MIN_CROSS_YEAR_EVALUABLE_SEGMENTS = 9
MIN_BASE_POSITIVE_FRACTION = 0.80
MIN_STRESS_POSITIVE_FRACTION = 2.0 / 3.0
MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5 = 0.10
MIN_POOLED_MEAN_NET_PIPS_0P5 = 0.25
REQUIRE_POOLED_STRESS_MEAN_POSITIVE = True
MAX_SIGN_FLIPS = 3

NEAR_DUPLICATE_JACCARD = 0.90
MAX_CROSS_YEAR_SHORTLIST_PER_CELL_FAMILY = 5

FULL_COLLECTION_CATALOGUE_USE_AUTHORIZED = True
FORMER_EXP061_RESERVED_2023_2026_CATALOGUE_USE_AUTHORIZED = True
FORMER_EXP061_RESERVED_2023_2026_REMAINS_UNTOUCHED_OOS_FOR_STRATEGY_V1 = False

NEW_RAW_DATA_AUTHORIZED = False
NEW_FEATURE_AUTHORIZED = False
NEW_SYMBOL_AUTHORIZED = False
NEW_TIMEFRAME_AUTHORIZED = False
NEW_HORIZON_AUTHORIZED = False
ALTERNATIVE_DATA_AUTHORIZED = False

HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED = False
STRATEGY_V1_SYNTHESIS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


@dataclass(frozen=True, slots=True)
class PatternDefinition:
    family: str
    dimensions: tuple[str, ...]
    states: tuple[str, ...]
    lag_minutes: int | None = None

    def __post_init__(self) -> None:
        if self.family not in PATTERN_FAMILIES:
            raise ValueError("unsupported DEC-470 pattern family")
        if not self.dimensions or not self.states:
            raise ValueError("DEC-470 pattern definition cannot be empty")
        if self.family == "SNAPSHOT_SINGLE":
            if len(self.dimensions) != 1 or len(self.states) != 1:
                raise ValueError("DEC-470 single snapshot shape drift")
            if self.lag_minutes is not None:
                raise ValueError("DEC-470 snapshot single cannot have lag")
        elif self.family == "SNAPSHOT_PAIR":
            if len(self.dimensions) != 2 or len(self.states) != 2:
                raise ValueError("DEC-470 snapshot pair shape drift")
            if self.dimensions[0] == self.dimensions[1]:
                raise ValueError("DEC-470 snapshot pair dimensions must differ")
            if self.lag_minutes is not None:
                raise ValueError("DEC-470 snapshot pair cannot have lag")
        else:
            if len(self.dimensions) != 1 or len(self.states) != 2:
                raise ValueError("DEC-470 transition shape drift")
            if self.lag_minutes not in TRANSITION_LAGS_MINUTES:
                raise ValueError("DEC-470 transition lag drift")

        for dimension in self.dimensions:
            if dimension not in DIMENSION_STATES:
                raise ValueError("DEC-470 pattern dimension drift")
        if self.family == "SAME_DIMENSION_TRANSITION":
            allowed = DIMENSION_STATES[self.dimensions[0]]
            if any(state not in allowed for state in self.states):
                raise ValueError("DEC-470 transition state drift")
        else:
            for dimension, state in zip(self.dimensions, self.states):
                if state not in DIMENSION_STATES[dimension]:
                    raise ValueError("DEC-470 snapshot state drift")


def _dimension_states() -> tuple[tuple[str, tuple[str, ...]], ...]:
    values = [(name, QUANTILE_STATES) for name in CONTINUOUS_FEATURES]
    values.append((SESSION_DIMENSION, SESSION_STATES))
    return tuple(values)


def enumerate_pattern_definitions() -> tuple[PatternDefinition, ...]:
    dimensions = _dimension_states()
    patterns: list[PatternDefinition] = []

    for name, states in dimensions:
        for state in states:
            patterns.append(
                PatternDefinition(
                    family="SNAPSHOT_SINGLE",
                    dimensions=(name,),
                    states=(state,),
                )
            )

    for left_index, (left_name, left_states) in enumerate(dimensions):
        for right_name, right_states in dimensions[left_index + 1 :]:
            for left_state in left_states:
                for right_state in right_states:
                    patterns.append(
                        PatternDefinition(
                            family="SNAPSHOT_PAIR",
                            dimensions=(left_name, right_name),
                            states=(left_state, right_state),
                        )
                    )

    for name, states in dimensions:
        for lag_minutes in TRANSITION_LAGS_MINUTES:
            for prior_state in states:
                for current_state in states:
                    patterns.append(
                        PatternDefinition(
                            family="SAME_DIMENSION_TRANSITION",
                            dimensions=(name,),
                            states=(prior_state, current_state),
                            lag_minutes=lag_minutes,
                        )
                    )

    return tuple(patterns)


def pattern_family_counts() -> dict[str, int]:
    counts = {family: 0 for family in PATTERN_FAMILIES}
    for pattern in enumerate_pattern_definitions():
        counts[pattern.family] += 1
    return counts


PATTERN_FAMILY_COUNTS = pattern_family_counts()
PATTERN_CONDITION_COUNT = sum(PATTERN_FAMILY_COUNTS.values())
CELL_HORIZON_COUNT = len(SYMBOLS) * len(TIMEFRAMES) * len(HORIZONS_MINUTES)
DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT = (
    PATTERN_CONDITION_COUNT * CELL_HORIZON_COUNT * len(DIRECTIONS)
)
ANNUAL_SEGMENT_COUNT = len(collection_segments())
TOTAL_ANNUAL_DIRECTIONAL_RECORDS = (
    DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT * ANNUAL_SEGMENT_COUNT
)
CANONICAL_CROSS_YEAR_HYPOTHESIS_COUNT = DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT
MAX_CROSS_YEAR_SHORTLIST_GLOBAL = (
    CELL_HORIZON_COUNT
    * len(PATTERN_FAMILIES)
    * MAX_CROSS_YEAR_SHORTLIST_PER_CELL_FAMILY
)


def annual_prior_tertile_cutpoints(
    prior_values: Sequence[float | int | None],
) -> tuple[float, float] | None:
    if len(
        [
            value
            for value in prior_values
            if isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
        ]
    ) < MIN_PRIOR_CALIBRATION_ROWS:
        return None
    return empirical_tertile_cutpoints(prior_values)


def annual_quantile_state(
    value: float | int | None,
    prior_values: Sequence[float | int | None],
) -> str | None:
    return quantile_state(value, annual_prior_tertile_cutpoints(prior_values))


def _condition_payload(pattern: PatternDefinition) -> dict[str, object]:
    payload: dict[str, object] = {
        "family": pattern.family,
        "dimensions": list(pattern.dimensions),
        "states": list(pattern.states),
    }
    if pattern.lag_minutes is not None:
        payload["lag_minutes"] = pattern.lag_minutes
    return payload


def canonical_pattern_fingerprint(
    *,
    pattern: PatternDefinition,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    direction: str,
) -> str:
    if symbol not in SYMBOLS:
        raise ValueError("unsupported DEC-470 pattern symbol")
    if timeframe not in TIMEFRAMES:
        raise ValueError("unsupported DEC-470 pattern timeframe")
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("unsupported DEC-470 pattern horizon")
    if direction not in DIRECTIONS:
        raise ValueError("unsupported DEC-470 pattern direction")

    payload = {
        "protocol_version": ANNUAL_CATALOGUE_PROTOCOL_VERSION,
        "pattern": _condition_payload(pattern),
        "symbol": symbol,
        "timeframe": timeframe,
        "horizon_minutes": horizon_minutes,
        "direction": direction,
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def annual_record_identity(
    *,
    canonical_pattern_fingerprint_value: str,
    annual_segment_label: str,
) -> str:
    if len(canonical_pattern_fingerprint_value) != 64:
        raise ValueError("DEC-470 canonical pattern fingerprint must be sha256")
    try:
        int(canonical_pattern_fingerprint_value, 16)
    except ValueError as exc:
        raise ValueError("DEC-470 canonical pattern fingerprint must be hexadecimal") from exc
    allowed = {segment.label for segment in collection_segments()}
    if annual_segment_label not in allowed:
        raise ValueError("DEC-470 annual segment label drift")
    payload = {
        "canonical_pattern_fingerprint": canonical_pattern_fingerprint_value,
        "annual_segment_label": annual_segment_label,
    }
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def cross_year_gate_passes(
    *,
    evaluable_segments: int,
    base_positive_segments: int,
    stress_positive_segments: int,
    median_annual_mean_net_pips_0p5: float,
    pooled_mean_net_pips_0p5: float,
    pooled_mean_net_pips_1p0: float,
    sign_flips: int,
) -> bool:
    if evaluable_segments < 0 or evaluable_segments > ANNUAL_SEGMENT_COUNT:
        raise ValueError("DEC-470 evaluable segment count drift")
    if base_positive_segments < 0 or stress_positive_segments < 0:
        raise ValueError("DEC-470 positive segment counts cannot be negative")
    if evaluable_segments < MIN_CROSS_YEAR_EVALUABLE_SEGMENTS:
        return False
    if base_positive_segments > evaluable_segments:
        raise ValueError("DEC-470 base-positive count exceeds evaluable count")
    if stress_positive_segments > evaluable_segments:
        raise ValueError("DEC-470 stress-positive count exceeds evaluable count")
    if sign_flips < 0:
        raise ValueError("DEC-470 sign flips cannot be negative")
    if (base_positive_segments / evaluable_segments) < MIN_BASE_POSITIVE_FRACTION:
        return False
    if (
        stress_positive_segments / evaluable_segments
    ) < MIN_STRESS_POSITIVE_FRACTION:
        return False
    if median_annual_mean_net_pips_0p5 < MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5:
        return False
    if pooled_mean_net_pips_0p5 < MIN_POOLED_MEAN_NET_PIPS_0P5:
        return False
    if REQUIRE_POOLED_STRESS_MEAN_POSITIVE and pooled_mean_net_pips_1p0 <= 0.0:
        return False
    if sign_flips > MAX_SIGN_FLIPS:
        return False
    return True


def protocol_payload() -> dict[str, object]:
    segments = collection_segments()
    return {
        "decision": ANNUAL_CATALOGUE_PROTOCOL_DECISION,
        "version": ANNUAL_CATALOGUE_PROTOCOL_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "source_method_decision": SOURCE_METHOD_DECISION,
        "source_method_merge_sha": SOURCE_METHOD_MERGE_SHA,
        "parent_discovery_decision": ANNUAL_PATTERN_CATALOGUE_METHOD_DECISION,
        "governing_research_method": GOVERNING_RESEARCH_METHOD,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": UNTOUCHED_OOS,
        "market_universe": {
            "symbols": list(SYMBOLS),
            "timeframes": list(TIMEFRAMES),
            "horizons_minutes": list(HORIZONS_MINUTES),
            "continuous_features": list(CONTINUOUS_FEATURES),
            "session_dimension": SESSION_DIMENSION,
            "session_states": list(SESSION_STATES),
            "new_raw_data_authorized": NEW_RAW_DATA_AUTHORIZED,
            "new_feature_authorized": NEW_FEATURE_AUTHORIZED,
            "new_symbol_authorized": NEW_SYMBOL_AUTHORIZED,
            "new_timeframe_authorized": NEW_TIMEFRAME_AUTHORIZED,
            "new_horizon_authorized": NEW_HORIZON_AUTHORIZED,
            "alternative_data_authorized": ALTERNATIVE_DATA_AUTHORIZED,
        },
        "annual_segments": [
            {
                "label": segment.label,
                "start": segment.start.isoformat(),
                "end_inclusive": segment.end_inclusive.isoformat(),
                "complete_calendar_year": segment.complete_calendar_year,
            }
            for segment in segments
        ],
        "annual_boundary_rule": (
            "available_at_utc and fixed-horizon exit_timestamp_utc must both "
            "remain inside the same annual segment; late-year outcomes crossing "
            "the annual boundary are excluded from that annual catalogue"
        ),
        "state_encoding": {
            "continuous_method": "strict_prior_only_expanding_empirical_tertiles",
            "minimum_prior_finite_rows": MIN_PRIOR_CALIBRATION_ROWS,
            "prior_scope": (
                "same symbol/timeframe/annual segment and available_at_utc strictly "
                "earlier than the current observation"
            ),
            "quantile_states": list(QUANTILE_STATES),
            "quantile_index_formula": "floor((n-1)/3), floor(2*(n-1)/3)",
            "tied_cutpoint_policy": "state_unavailable_for_that_observation",
            "session_state_method": "existing_deterministic_session_precedence",
            "future_rows_may_not_affect_current_state": True,
        },
        "pattern_grammar": {
            "families": list(PATTERN_FAMILIES),
            "snapshot_single_count": PATTERN_FAMILY_COUNTS["SNAPSHOT_SINGLE"],
            "snapshot_pair_count": PATTERN_FAMILY_COUNTS["SNAPSHOT_PAIR"],
            "same_dimension_transition_count": (
                PATTERN_FAMILY_COUNTS["SAME_DIMENSION_TRANSITION"]
            ),
            "transition_lags_minutes": list(TRANSITION_LAGS_MINUTES),
            "transition_requires_exact_prior_timestamp": True,
            "cross_dimension_transition_sequences_authorized": False,
            "sequences_longer_than_prior_to_current_authorized": False,
            "three_plus_snapshot_predicates_authorized": False,
            "condition_count": PATTERN_CONDITION_COUNT,
            "directions": list(DIRECTIONS),
            "cell_horizon_count": CELL_HORIZON_COUNT,
            "directional_hypotheses_per_annual_segment": (
                DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT
            ),
            "annual_segment_count": ANNUAL_SEGMENT_COUNT,
            "total_annual_directional_records": TOTAL_ANNUAL_DIRECTIONAL_RECORDS,
            "canonical_cross_year_hypothesis_count": (
                CANONICAL_CROSS_YEAR_HYPOTHESIS_COUNT
            ),
        },
        "annual_evidence": {
            "preserve_every_nominal_pattern_record": True,
            "minimum_support_for_evaluable_label": MIN_ANNUAL_EVALUABLE_SUPPORT,
            "insufficient_support_records_are_preserved": True,
            "required_statistics": [
                "support",
                "mean_net_pips_0p5",
                "median_net_pips_0p5",
                "win_rate_0p5",
                "mean_net_pips_1p0",
                "median_net_pips_1p0",
            ],
            "discovery_slippage_pips": DISCOVERY_SLIPPAGE_PIPS,
            "stress_slippage_pips": STRESS_SLIPPAGE_PIPS,
            "annual_catalogue_selects_winners": False,
            "annual_catalogue_reranks_patterns": False,
        },
        "cross_year_comparison": {
            "canonical_pattern_fingerprint_excludes_year": True,
            "minimum_evaluable_segments": MIN_CROSS_YEAR_EVALUABLE_SEGMENTS,
            "minimum_base_positive_fraction": MIN_BASE_POSITIVE_FRACTION,
            "minimum_stress_positive_fraction": MIN_STRESS_POSITIVE_FRACTION,
            "minimum_median_annual_mean_net_pips_0p5": (
                MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5
            ),
            "minimum_pooled_mean_net_pips_0p5": (
                MIN_POOLED_MEAN_NET_PIPS_0P5
            ),
            "require_pooled_stress_mean_positive": (
                REQUIRE_POOLED_STRESS_MEAN_POSITIVE
            ),
            "maximum_sign_flips": MAX_SIGN_FLIPS,
            "rank_fields": [
                "base_positive_fraction_desc",
                "stress_positive_fraction_desc",
                "worst_evaluable_annual_mean_net_pips_0p5_desc",
                "median_annual_mean_net_pips_0p5_desc",
                "pooled_mean_net_pips_0p5_desc",
                "pooled_mean_net_pips_1p0_desc",
                "total_support_desc",
                "canonical_pattern_fingerprint_asc",
            ],
            "near_duplicate_jaccard": NEAR_DUPLICATE_JACCARD,
            "dedup_scope": "same_cell_family_direction",
            "maximum_shortlist_per_cell_family": (
                MAX_CROSS_YEAR_SHORTLIST_PER_CELL_FAMILY
            ),
            "maximum_shortlist_global": MAX_CROSS_YEAR_SHORTLIST_GLOBAL,
            "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        },
        "historical_access_decision": {
            "full_collection_catalogue_use_authorized": (
                FULL_COLLECTION_CATALOGUE_USE_AUTHORIZED
            ),
            "former_exp061_reserved_2023_2026_catalogue_use_authorized": (
                FORMER_EXP061_RESERVED_2023_2026_CATALOGUE_USE_AUTHORIZED
            ),
            "former_exp061_reserved_2023_2026_remains_untouched_oos_for_strategy_v1": (
                FORMER_EXP061_RESERVED_2023_2026_REMAINS_UNTOUCHED_OOS_FOR_STRATEGY_V1
            ),
            "scope": (
                "annual_pattern_catalogue_and_later_strategy_v1_research_only; "
                "does_not_reopen_exp061_exp062_exp063_exp064_or_exp065"
            ),
            "historical_artifact_read_authorized_now": (
                HISTORICAL_ARTIFACT_READ_AUTHORIZED
            ),
            "historical_catalogue_execution_authorized_now": (
                HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED
            ),
            "fresh_strategy_v1_evidence_begins_after_strategy_v1_freeze": True,
        },
        "authorizations": {
            "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
            "historical_catalogue_execution_authorized": (
                HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED
            ),
            "historical_result_production_authorized": (
                HISTORICAL_RESULT_PRODUCTION_AUTHORIZED
            ),
            "cross_year_result_production_authorized": (
                CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED
            ),
            "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
            "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
            "promotion_authorized": PROMOTION_AUTHORIZED,
            "phase8b_authorized": PHASE8B_AUTHORIZED,
            "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
            "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
            "live_order_authorized": LIVE_ORDER_AUTHORIZED,
            "real_money_authorized": REAL_MONEY_AUTHORIZED,
            "trading_authorized": TRADING_AUTHORIZED,
        },
        "next_gate": "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_MINER",
    }


def protocol_fingerprint() -> str:
    encoded = (
        json.dumps(
            protocol_payload(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            default=str,
        )
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_protocol() -> None:
    if SOURCE_METHOD_DECISION != "DEC-469":
        raise ValueError("DEC-470 source method decision drift")
    if ANNUAL_PATTERN_CATALOGUE_METHOD_DECISION != "DEC-469":
        raise ValueError("DEC-470 parent method decision drift")
    if GOVERNING_RESEARCH_METHOD != "DISCOVERY_FIRST_ANNUAL_PATTERN_CATALOGUE":
        raise ValueError("DEC-470 governing method drift")
    if len(collection_segments()) != 12:
        raise ValueError("DEC-470 requires 12 annual collection segments")
    if PATTERN_FAMILY_COUNTS != {
        "SNAPSHOT_SINGLE": 65,
        "SNAPSHOT_PAIR": 2010,
        "SAME_DIMENSION_TRANSITION": 410,
    }:
        raise ValueError("DEC-470 pattern-family count drift")
    if PATTERN_CONDITION_COUNT != 2485:
        raise ValueError("DEC-470 pattern-condition count drift")
    if CELL_HORIZON_COUNT != 18:
        raise ValueError("DEC-470 cell/horizon count drift")
    if DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT != 89460:
        raise ValueError("DEC-470 annual directional count drift")
    if TOTAL_ANNUAL_DIRECTIONAL_RECORDS != 1073520:
        raise ValueError("DEC-470 total annual record count drift")
    if CANONICAL_CROSS_YEAR_HYPOTHESIS_COUNT != 89460:
        raise ValueError("DEC-470 canonical cross-year count drift")
    if MAX_CROSS_YEAR_SHORTLIST_GLOBAL != 270:
        raise ValueError("DEC-470 shortlist cap drift")
    if not FULL_COLLECTION_CATALOGUE_USE_AUTHORIZED:
        raise ValueError("DEC-470 must authorize full collection for catalogue research")
    if not FORMER_EXP061_RESERVED_2023_2026_CATALOGUE_USE_AUTHORIZED:
        raise ValueError("DEC-470 must explicitly open 2023-2026 for catalogue research")
    if FORMER_EXP061_RESERVED_2023_2026_REMAINS_UNTOUCHED_OOS_FOR_STRATEGY_V1:
        raise ValueError("DEC-470 cannot preserve untouched-OOS claim after research opening")
    for value in (
        NEW_RAW_DATA_AUTHORIZED,
        NEW_FEATURE_AUTHORIZED,
        NEW_SYMBOL_AUTHORIZED,
        NEW_TIMEFRAME_AUTHORIZED,
        NEW_HORIZON_AUTHORIZED,
        ALTERNATIVE_DATA_AUTHORIZED,
        HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
        HISTORICAL_RESULT_PRODUCTION_AUTHORIZED,
        CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED,
        STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        CANDIDATE_COMPILATION_AUTHORIZED,
        PROMOTION_AUTHORIZED,
        PHASE8B_AUTHORIZED,
        DEMO_ORDER_AUTHORIZED,
        BROKER_MUTATION_AUTHORIZED,
        LIVE_ORDER_AUTHORIZED,
        REAL_MONEY_AUTHORIZED,
        TRADING_AUTHORIZED,
    ):
        if value:
            raise ValueError("DEC-470 source-only authority drift")


validate_protocol()


__all__ = [
    "ANNUAL_CATALOGUE_PROTOCOL_DECISION",
    "ANNUAL_CATALOGUE_PROTOCOL_VERSION",
    "ANNUAL_SEGMENT_COUNT",
    "CANONICAL_CROSS_YEAR_HYPOTHESIS_COUNT",
    "DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT",
    "EXPERIMENT_ID",
    "FULL_COLLECTION_CATALOGUE_USE_AUTHORIZED",
    "MIN_ANNUAL_EVALUABLE_SUPPORT",
    "PATTERN_CONDITION_COUNT",
    "PATTERN_FAMILY_COUNTS",
    "PatternDefinition",
    "TOTAL_ANNUAL_DIRECTIONAL_RECORDS",
    "TRANSITION_LAGS_MINUTES",
    "annual_prior_tertile_cutpoints",
    "annual_quantile_state",
    "annual_record_identity",
    "canonical_pattern_fingerprint",
    "cross_year_gate_passes",
    "enumerate_pattern_definitions",
    "protocol_fingerprint",
    "protocol_payload",
    "validate_protocol",
]
