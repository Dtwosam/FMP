from __future__ import annotations

from dataclasses import dataclass
from datetime import date


ANNUAL_PATTERN_CATALOGUE_METHOD_DECISION = "DEC-469"
ANNUAL_PATTERN_CATALOGUE_METHOD_VERSION = (
    "fmp-discovery-first-annual-pattern-catalogue-method-v1"
)

GOVERNING_RESEARCH_METHOD = "DISCOVERY_FIRST_ANNUAL_PATTERN_CATALOGUE"
PARENT_DISCOVERY_DECISION = "DEC-268"
SOURCE_TERMINAL_RESULT_DECISION = "DEC-468"

COLLECTION_START = date(2015, 1, 1)
COLLECTION_END_INCLUSIVE = date(2026, 8, 20)
FULL_CALENDAR_YEARS = tuple(range(2015, 2026))
PARTIAL_FINAL_YEAR = 2026
CURRENTLY_OPEN_CATALOGUE_YEARS = tuple(range(2015, 2023))
PROTECTED_CATALOGUE_YEARS = (2023, 2024, 2025, 2026)

YEAR_BY_YEAR_CATALOGUE_REQUIRED = True
FREEZE_EACH_YEAR_BEFORE_CROSS_YEAR_COMPARISON = True
PRESERVE_ALL_SURFACED_PATTERNS = True
CROSS_YEAR_COMPARISON_REQUIRED = True
STRATEGY_V1_SYNTHESIS_REQUIRES_COMPLETE_AUTHORIZED_CATALOGUE = True
STRATEGY_V1_MUST_BE_IMMUTABLE_BEFORE_PROSPECTIVE_EVIDENCE = True
RUNNING_SHADOW_DEMO_MAY_SELF_MODIFY = False
COMPLETED_DEMO_MAY_INFORM_NEW_CHALLENGER = True
NEW_CHALLENGER_REQUIRES_FRESH_PROSPECTIVE_EVIDENCE = True

PROTECTED_2023_2026_ACCESS_AUTHORIZED = False
ANNUAL_CATALOGUE_HISTORICAL_EXECUTION_AUTHORIZED = False
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
class AnnualCatalogueSegment:
    label: str
    start: date
    end_inclusive: date
    complete_calendar_year: bool

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("annual catalogue segment label must be non-empty")
        if self.start > self.end_inclusive:
            raise ValueError("annual catalogue segment must be non-empty")


def collection_segments() -> tuple[AnnualCatalogueSegment, ...]:
    segments = [
        AnnualCatalogueSegment(
            label=str(year),
            start=date(year, 1, 1),
            end_inclusive=date(year, 12, 31),
            complete_calendar_year=True,
        )
        for year in FULL_CALENDAR_YEARS
    ]
    segments.append(
        AnnualCatalogueSegment(
            label="2026_YTD_TO_2026_08_20",
            start=date(2026, 1, 1),
            end_inclusive=COLLECTION_END_INCLUSIVE,
            complete_calendar_year=False,
        )
    )
    return tuple(segments)


def build_annual_pattern_catalogue_method() -> dict[str, object]:
    segments = collection_segments()
    if segments[0].start != COLLECTION_START:
        raise ValueError("DEC-469 annual catalogue collection start drift")
    if segments[-1].end_inclusive != COLLECTION_END_INCLUSIVE:
        raise ValueError("DEC-469 annual catalogue collection end drift")
    if tuple(segment.start.year for segment in segments) != tuple(range(2015, 2027)):
        raise ValueError("DEC-469 annual catalogue year coverage drift")
    if not YEAR_BY_YEAR_CATALOGUE_REQUIRED:
        raise ValueError("DEC-469 requires year-by-year cataloguing")
    if not FREEZE_EACH_YEAR_BEFORE_CROSS_YEAR_COMPARISON:
        raise ValueError("DEC-469 requires per-year freeze before comparison")
    if not PRESERVE_ALL_SURFACED_PATTERNS:
        raise ValueError("DEC-469 requires preservation of all surfaced patterns")
    if RUNNING_SHADOW_DEMO_MAY_SELF_MODIFY:
        raise ValueError("DEC-469 forbids in-place shadow/demo self-modification")
    if PROTECTED_2023_2026_ACCESS_AUTHORIZED:
        raise ValueError("DEC-469 method amendment cannot silently open protected history")
    if STRATEGY_V1_SYNTHESIS_AUTHORIZED:
        raise ValueError("DEC-469 does not yet authorize Strategy V1 synthesis")

    return {
        "decision": ANNUAL_PATTERN_CATALOGUE_METHOD_DECISION,
        "version": ANNUAL_PATTERN_CATALOGUE_METHOD_VERSION,
        "parent_discovery_decision": PARENT_DISCOVERY_DECISION,
        "source_terminal_result_decision": SOURCE_TERMINAL_RESULT_DECISION,
        "governing_research_method": GOVERNING_RESEARCH_METHOD,
        "core_question": (
            "WHAT_REPEATABLE_MARKET_BEHAVIOURS_APPEAR_WITHIN_EACH_HISTORICAL_YEAR_"
            "AND_WHICH_OF_THOSE_BEHAVIOURS_RECUR_ACROSS_YEARS_STRONGLY_ENOUGH_TO_"
            "SYNTHESIZE_THE_FIRST_IMMUTABLE_STRATEGY"
        ),
        "collection": {
            "start": COLLECTION_START.isoformat(),
            "end_inclusive": COLLECTION_END_INCLUSIVE.isoformat(),
            "segments": [
                {
                    "label": segment.label,
                    "start": segment.start.isoformat(),
                    "end_inclusive": segment.end_inclusive.isoformat(),
                    "complete_calendar_year": segment.complete_calendar_year,
                }
                for segment in segments
            ],
            "currently_open_catalogue_years": list(CURRENTLY_OPEN_CATALOGUE_YEARS),
            "protected_catalogue_years": list(PROTECTED_CATALOGUE_YEARS),
            "protected_2023_2026_access_authorized": (
                PROTECTED_2023_2026_ACCESS_AUTHORIZED
            ),
        },
        "annual_catalogue": {
            "process_each_year_independently_first": True,
            "use_same_frozen_measurement_vocabulary_and_search_grammar": True,
            "preserve_every_pattern_surfaced_by_frozen_search": True,
            "preserve_failed_and_negative_patterns": True,
            "record_effective_search_volume": True,
            "record_support_and_after_cost_outcomes": True,
            "record_pair_timeframe_horizon_and_context": True,
            "freeze_each_year_catalogue_before_cross_year_comparison": True,
            "state_transitions_are_pattern_type_not_method": True,
            "pairwise_interactions_are_pattern_type_not_method": True,
            "named_strategy_families_are_pattern_type_or_benchmark_not_method": True,
        },
        "cross_year_comparison": {
            "begins_only_after_required_annual_catalogues_are_frozen": True,
            "canonical_pattern_identity_required": True,
            "compare_recurrence_count": True,
            "compare_support_by_year": True,
            "compare_effect_direction_and_magnitude_by_year": True,
            "compare_after_cost_economics_by_year": True,
            "compare_pair_timeframe_horizon_context": True,
            "compare_regime_session_location_spread_context": True,
            "record_failure_years_and_sign_flips": True,
            "check_concentration_in_single_year_or_small_event_set": True,
            "single_best_year_cannot_define_strategy_v1": True,
        },
        "strategy_v1": {
            "synthesis_requires_cross_year_evidence": True,
            "synthesis_requires_complete_authorized_catalogue": True,
            "may_combine_multiple_recurring_patterns": True,
            "must_define_long_short_no_trade_semantics": True,
            "must_define_applicability_and_conflict_rules": True,
            "must_define_cost_and_risk_interface": True,
            "must_receive_new_immutable_version_identity": True,
            "must_be_frozen_before_prospective_evidence": True,
            "strategy_v1_synthesis_authorized_now": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        },
        "prospective_learning_loop": {
            "first_strategy_is_strategy_v1": True,
            "prospective_shadow_precedes_demo_orders": True,
            "demo_uses_fixed_strategy_version": True,
            "running_shadow_demo_may_self_modify": RUNNING_SHADOW_DEMO_MAY_SELF_MODIFY,
            "completed_demo_may_inform_new_challenger": (
                COMPLETED_DEMO_MAY_INFORM_NEW_CHALLENGER
            ),
            "demo_observations_used_for_revision_become_training_evidence": True,
            "revised_strategy_gets_new_version_identity": True,
            "new_challenger_requires_fresh_prospective_evidence": (
                NEW_CHALLENGER_REQUIRES_FRESH_PROSPECTIVE_EVIDENCE
            ),
        },
        "authorizations": {
            "annual_catalogue_historical_execution_authorized": (
                ANNUAL_CATALOGUE_HISTORICAL_EXECUTION_AUTHORIZED
            ),
            "protected_2023_2026_access_authorized": (
                PROTECTED_2023_2026_ACCESS_AUTHORIZED
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
        "next_gate": (
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_PROTOCOL_AND_PROTECTED_HISTORY_"
            "ACCESS_DECISION"
        ),
    }


__all__ = [
    "ANNUAL_PATTERN_CATALOGUE_METHOD_DECISION",
    "ANNUAL_PATTERN_CATALOGUE_METHOD_VERSION",
    "CURRENTLY_OPEN_CATALOGUE_YEARS",
    "GOVERNING_RESEARCH_METHOD",
    "PROTECTED_CATALOGUE_YEARS",
    "build_annual_pattern_catalogue_method",
    "collection_segments",
]
