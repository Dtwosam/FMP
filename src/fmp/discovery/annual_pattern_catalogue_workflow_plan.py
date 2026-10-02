from __future__ import annotations

from .annual_pattern_catalogue_method import collection_segments
from .pattern_protocol import HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


ANNUAL_CATALOGUE_WORKFLOW_PLAN_DECISION = "DEC-476"
ANNUAL_CATALOGUE_WORKFLOW_PLAN_VERSION = (
    "fmp-annual-pattern-catalogue-workflow-plan-v1"
)
SOURCE_RUNTIME_DECISION = "DEC-475"
SOURCE_RUNTIME_MERGE_SHA = "db8285dab5a0311abbbb77c60c958771b17074a5"

WORKFLOW_SOURCE_AUTHORIZED = False
WORKFLOW_INSTALLED = False
WORKFLOW_DISPATCH_AUTHORIZED = False
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

CELLS_PER_SEGMENT = len(SYMBOLS) * len(TIMEFRAMES) * len(HORIZONS_MINUTES)
JOBS_PER_SEGMENT_RUN = CELLS_PER_SEGMENT + 2
ARTIFACTS_PER_SEGMENT_RUN = CELLS_PER_SEGMENT + 2
SEGMENT_COUNT = len(collection_segments())
FULL_COLLECTION_CELL_COUNT = SEGMENT_COUNT * CELLS_PER_SEGMENT


def _segment_labels() -> tuple[str, ...]:
    return tuple(segment.label for segment in collection_segments())


def expected_segment_cells(
    annual_segment_label: str,
) -> tuple[tuple[str, str, int], ...]:
    if annual_segment_label not in _segment_labels():
        raise ValueError("DEC-476 annual segment label drift")
    return tuple(
        (symbol, timeframe, horizon)
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
    )


def expected_cell_job_name(
    annual_segment_label: str,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> str:
    if (symbol, timeframe, horizon_minutes) not in expected_segment_cells(
        annual_segment_label
    ):
        raise ValueError("DEC-476 unsupported annual catalogue cell")
    safe_segment = annual_segment_label.lower()
    return (
        f"annual-cell-{safe_segment}-{symbol.lower()}-"
        f"{timeframe.lower()}-{horizon_minutes}m"
    )


def expected_job_names(annual_segment_label: str) -> tuple[str, ...]:
    cells = expected_segment_cells(annual_segment_label)
    return (
        f"annual-preflight-{annual_segment_label.lower()}",
        *(
            expected_cell_job_name(
                annual_segment_label,
                symbol,
                timeframe,
                horizon,
            )
            for symbol, timeframe, horizon in cells
        ),
        f"annual-freeze-{annual_segment_label.lower()}",
    )


def segment_run_plan(annual_segment_label: str) -> dict[str, object]:
    cells = expected_segment_cells(annual_segment_label)
    jobs = expected_job_names(annual_segment_label)
    if len(cells) != 18 or len(set(cells)) != 18:
        raise ValueError("DEC-476 annual segment cell inventory drift")
    if len(jobs) != 20 or len(set(jobs)) != 20:
        raise ValueError("DEC-476 annual segment job inventory drift")
    return {
        "annual_segment_label": annual_segment_label,
        "cell_count": len(cells),
        "job_count": len(jobs),
        "artifact_count": ARTIFACTS_PER_SEGMENT_RUN,
        "cells": [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "horizon_minutes": horizon,
                "job_name": expected_cell_job_name(
                    annual_segment_label,
                    symbol,
                    timeframe,
                    horizon,
                ),
            }
            for symbol, timeframe, horizon in cells
        ],
        "preflight_job": jobs[0],
        "annual_freeze_job": jobs[-1],
        "annual_freeze_depends_on_all_18_cells": True,
        "next_segment_must_wait_for_prior_segment_freeze": True,
        "cross_year_comparison_in_this_run": False,
    }


def workflow_plan_payload() -> dict[str, object]:
    labels = _segment_labels()
    if SEGMENT_COUNT != 12:
        raise ValueError("DEC-476 annual segment count drift")
    if CELLS_PER_SEGMENT != 18:
        raise ValueError("DEC-476 per-segment cell count drift")
    if FULL_COLLECTION_CELL_COUNT != 216:
        raise ValueError("DEC-476 full collection cell count drift")
    return {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_PLAN_DECISION,
        "version": ANNUAL_CATALOGUE_WORKFLOW_PLAN_VERSION,
        "source_runtime_decision": SOURCE_RUNTIME_DECISION,
        "source_runtime_merge_sha": SOURCE_RUNTIME_MERGE_SHA,
        "run_unit": "one_annual_segment",
        "annual_segments_in_required_order": list(labels),
        "annual_segment_count": SEGMENT_COUNT,
        "cells_per_segment_run": CELLS_PER_SEGMENT,
        "jobs_per_segment_run": JOBS_PER_SEGMENT_RUN,
        "artifacts_per_segment_run": ARTIFACTS_PER_SEGMENT_RUN,
        "full_collection_cell_count": FULL_COLLECTION_CELL_COUNT,
        "sequential_segment_freeze_required": True,
        "cross_year_comparison_waits_for_all_segment_freezes": True,
        "single_216_cell_workflow_forbidden": True,
        "segment_runs": [segment_run_plan(label) for label in labels],
        "workflow_source_authorized": WORKFLOW_SOURCE_AUTHORIZED,
        "workflow_installed": WORKFLOW_INSTALLED,
        "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
        "historical_result_production_authorized": HISTORICAL_RESULT_PRODUCTION_AUTHORIZED,
        "cross_year_result_production_authorized": CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED,
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_SEGMENT_FREEZE_CONTRACT",
    }


__all__ = [
    "ANNUAL_CATALOGUE_WORKFLOW_PLAN_DECISION",
    "ANNUAL_CATALOGUE_WORKFLOW_PLAN_VERSION",
    "ARTIFACTS_PER_SEGMENT_RUN",
    "CELLS_PER_SEGMENT",
    "FULL_COLLECTION_CELL_COUNT",
    "JOBS_PER_SEGMENT_RUN",
    "SEGMENT_COUNT",
    "expected_cell_job_name",
    "expected_job_names",
    "expected_segment_cells",
    "segment_run_plan",
    "workflow_plan_payload",
]
