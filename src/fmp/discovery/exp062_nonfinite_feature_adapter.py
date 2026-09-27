from __future__ import annotations

import math

import polars as pl

from .market_learning_adapter import (
    AdaptedCellInputs,
    EXP061_INPUT_END_EXCLUSIVE_UTC,
    EXP061_INPUT_START_UTC,
    _FEATURE_IDENTITY_COLUMNS,
    _SESSION_FLAG_COLUMNS,
    _observation_id,
    _require_columns,
    _require_utc,
    _validate_cell_identity,
    _validate_common_frame_identity,
    adapt_outcome_frame,
)
from .pattern_miner import FeatureObservation
from .pattern_protocol import CONTINUOUS_FEATURES


EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION = "DEC-293"
EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION = (
    "fmp-exp062-nonfinite-feature-normalization-v1"
)


def _normalize_continuous_feature_value(value: object) -> object:
    if value is None:
        return None
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and not math.isfinite(float(value))
    ):
        return None
    return value


def adapt_feature_frame(
    frame: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
) -> tuple[tuple[FeatureObservation, ...], str]:
    _validate_cell_identity(symbol, timeframe)
    required = (
        *_FEATURE_IDENTITY_COLUMNS,
        *CONTINUOUS_FEATURES,
        *_SESSION_FLAG_COLUMNS,
    )
    _require_columns(frame, required, label="EXP-062 feature frame")
    processed_sha = _validate_common_frame_identity(
        frame,
        symbol=symbol,
        timeframe=timeframe,
        label="EXP-062 feature frame",
    )

    unique = frame.select(
        pl.struct(["symbol", "timeframe", "bar_start_utc"]).n_unique()
    ).item()
    if unique != frame.height:
        raise ValueError("duplicate EXP-062 feature-frame identity")

    rows = frame.sort(["bar_start_utc"]).iter_rows(named=True)
    observations: list[FeatureObservation] = []
    seen: set[str] = set()
    for row in rows:
        available = _require_utc(row["available_at_utc"], field="available_at_utc")
        if not (
            EXP061_INPUT_START_UTC
            <= available
            < EXP061_INPUT_END_EXCLUSIVE_UTC
        ):
            raise ValueError(
                "EXP-062 feature adapter received row outside 2015-2022 input range"
            )
        observation_id = _observation_id(row)
        if observation_id in seen:
            raise ValueError("duplicate EXP-062 adapted feature observation id")
        seen.add(observation_id)

        values = {
            name: _normalize_continuous_feature_value(row[name])
            for name in CONTINUOUS_FEATURES
        }
        values.update({name: row[name] for name in _SESSION_FLAG_COLUMNS})
        observations.append(
            FeatureObservation(
                observation_id=observation_id,
                symbol=symbol,
                timeframe=timeframe,
                available_at_utc=available,
                values=values,
            )
        )

    return tuple(observations), processed_sha


def adapt_market_learning_cell(
    *,
    feature_frame: pl.DataFrame,
    outcome_frame: pl.DataFrame,
    symbol: str,
    timeframe: str,
) -> AdaptedCellInputs:
    feature_observations, processed_sha = adapt_feature_frame(
        feature_frame,
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
    return AdaptedCellInputs(
        symbol=symbol,
        timeframe=timeframe,
        processed_manifest_sha256=processed_sha,
        feature_observations=feature_observations,
        outcome_observations=outcome_observations,
    )


__all__ = [
    "EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION",
    "EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION",
    "adapt_feature_frame",
    "adapt_market_learning_cell",
]
