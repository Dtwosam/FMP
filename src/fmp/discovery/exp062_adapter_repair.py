from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import polars as pl

from .market_learning_adapter import (
    AdaptedCellInputs,
    adapt_feature_frame,
    adapt_outcome_frame,
)
from .pattern_protocol import CONTINUOUS_FEATURES


EXP062_EXPERIMENT_ID = "EXP-20260927-062"
EXP062_ADAPTER_REPAIR_DECISION = "DEC-293"
EXP062_ADAPTER_REPAIR_VERSION = "fmp-exp062-nonfinite-adapter-repair-v1"

HISTORICAL_SOURCE_ACCESS_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


@dataclass(frozen=True, slots=True)
class Exp062AdaptedCellInputs:
    adapted: AdaptedCellInputs
    normalized_nonfinite_counts: tuple[tuple[str, int], ...]

    @property
    def normalized_nonfinite_total(self) -> int:
        return sum(count for _, count in self.normalized_nonfinite_counts)


def normalize_nonfinite_continuous_features(
    frame: pl.DataFrame,
) -> tuple[pl.DataFrame, tuple[tuple[str, int], ...]]:
    missing = [name for name in CONTINUOUS_FEATURES if name not in frame.columns]
    if missing:
        raise ValueError(
            f"EXP-062 feature frame missing continuous columns: {missing}"
        )

    counts: list[tuple[str, int]] = []
    expressions: list[pl.Expr] = []
    for name in CONTINUOUS_FEATURES:
        nonfinite = (
            frame.select(
                (
                    pl.col(name).is_not_null()
                    & ~pl.col(name).is_finite()
                ).sum()
            ).item()
        )
        if not isinstance(nonfinite, int) or isinstance(nonfinite, bool):
            raise ValueError(
                f"EXP-062 non-finite count is invalid for {name}"
            )
        counts.append((name, nonfinite))
        expressions.append(
            pl.when(pl.col(name).is_null())
            .then(pl.lit(None))
            .when(pl.col(name).is_finite())
            .then(pl.col(name))
            .otherwise(pl.lit(None))
            .alias(name)
        )

    normalized = frame.with_columns(expressions)
    return normalized, tuple(counts)


def adapt_market_learning_cell_exp062(
    *,
    feature_frame: pl.DataFrame,
    outcome_frame: pl.DataFrame,
    symbol: str,
    timeframe: str,
) -> Exp062AdaptedCellInputs:
    normalized, counts = normalize_nonfinite_continuous_features(feature_frame)

    feature_observations, processed_sha = adapt_feature_frame(
        normalized,
        symbol=symbol,
        timeframe=timeframe,
    )
    outcome_observations = adapt_outcome_frame(
        outcome_frame,
        symbol=symbol,
        timeframe=timeframe,
        expected_processed_manifest_sha256=processed_sha,
    )

    feature_ids = {row.observation_id for row in feature_observations}
    missing = {
        row.observation_id
        for row in outcome_observations
        if row.observation_id not in feature_ids
    }
    if missing:
        raise ValueError(
            "EXP-062 adapted outcome has no matching feature observation"
        )

    return Exp062AdaptedCellInputs(
        adapted=AdaptedCellInputs(
            symbol=symbol,
            timeframe=timeframe,
            processed_manifest_sha256=processed_sha,
            feature_observations=feature_observations,
            outcome_observations=outcome_observations,
        ),
        normalized_nonfinite_counts=counts,
    )


def exp062_adapter_repair_payload() -> dict[str, object]:
    return {
        "decision": EXP062_ADAPTER_REPAIR_DECISION,
        "version": EXP062_ADAPTER_REPAIR_VERSION,
        "experiment_id": EXP062_EXPERIMENT_ID,
        "repair_scope": (
            "NORMALIZE_NONFINITE_CONTINUOUS_SOURCE_VALUES_TO_NONE"
        ),
        "continuous_feature_count": len(CONTINUOUS_FEATURES),
        "preserves_exp061_feature_calculations": True,
        "preserves_exp061_windows": True,
        "preserves_exp061_thresholds": True,
        "preserves_exp061_cost_assumptions": True,
        "preserves_exp061_outcome_adapter": True,
        "historical_source_access_authorized": (
            HISTORICAL_SOURCE_ACCESS_AUTHORIZED
        ),
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
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
    }


__all__ = [
    "EXP062_ADAPTER_REPAIR_DECISION",
    "EXP062_ADAPTER_REPAIR_VERSION",
    "EXP062_EXPERIMENT_ID",
    "Exp062AdaptedCellInputs",
    "adapt_market_learning_cell_exp062",
    "exp062_adapter_repair_payload",
    "normalize_nonfinite_continuous_features",
]
