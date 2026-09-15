from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real

import numpy as np
import polars as pl
from sklearn.preprocessing import StandardScaler


class PreprocessingFitFailure(ValueError):
    def __init__(self, *, reason_code: str, column: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.column = column


@dataclass(frozen=True, slots=True)
class PreprocessorState:
    input_columns: tuple[str, ...]
    medians: tuple[float, ...]
    null_counts: tuple[int, ...]
    standardize: bool
    scaler_mean: tuple[float, ...] | None
    scaler_scale: tuple[float, ...] | None


def _numeric_matrix(frame: pl.DataFrame) -> np.ndarray:
    if frame.width == 0:
        raise ValueError("Phase 6 preprocessing requires at least one input column")

    columns: list[list[float]] = []
    for name in frame.columns:
        converted: list[float] = []
        for value in frame.get_column(name).to_list():
            if value is None:
                converted.append(float("nan"))
            elif isinstance(value, (bool, np.bool_)):
                converted.append(1.0 if bool(value) else 0.0)
            elif isinstance(value, Real):
                numeric = float(value)
                converted.append(numeric if math.isfinite(numeric) else float("nan"))
            else:
                raise ValueError(
                    f"Phase 6 preprocessing requires numeric/boolean inputs; {name!r} is invalid"
                )
        columns.append(converted)

    if frame.height == 0:
        return np.empty((0, frame.width), dtype=np.float64)
    return np.asarray(columns, dtype=np.float64).T


def _impute(matrix: np.ndarray, medians: tuple[float, ...]) -> np.ndarray:
    if matrix.shape[1] != len(medians):
        raise ValueError("Phase 6 preprocessing median shape mismatch")
    out = matrix.copy()
    for index, median in enumerate(medians):
        missing = ~np.isfinite(out[:, index])
        out[missing, index] = median
    if not np.isfinite(out).all():
        raise ValueError("Phase 6 preprocessing produced non-finite values")
    return out


def fit_preprocessor(
    frame: pl.DataFrame,
    *,
    standardize: bool,
) -> PreprocessorState:
    if frame.height == 0:
        raise ValueError("Phase 6 preprocessing fit rows must be non-empty")

    matrix = _numeric_matrix(frame)
    medians: list[float] = []
    null_counts: list[int] = []
    for index, name in enumerate(frame.columns):
        column = matrix[:, index]
        finite = np.isfinite(column)
        null_counts.append(int((~finite).sum()))
        values = column[finite]
        if values.size == 0:
            raise PreprocessingFitFailure(
                reason_code="ALL_NULL_FIT_COLUMN",
                column=name,
                message=f"Phase 6 fit column {name!r} is entirely null/all-null",
            )
        median = float(np.median(values))
        if not math.isfinite(median):
            raise ValueError(f"Phase 6 fit median for {name!r} is non-finite")
        medians.append(median)

    frozen_medians = tuple(medians)
    imputed = _impute(matrix, frozen_medians)
    scaler_mean: tuple[float, ...] | None = None
    scaler_scale: tuple[float, ...] | None = None
    if standardize:
        scaler = StandardScaler(copy=True, with_mean=True, with_std=True)
        scaler.fit(imputed)
        scaler_mean = tuple(float(value) for value in scaler.mean_)
        scaler_scale = tuple(float(value) for value in scaler.scale_)
        if not all(math.isfinite(value) for value in scaler_mean + scaler_scale):
            raise ValueError("Phase 6 fit scaler state is non-finite")
        if any(value <= 0 for value in scaler_scale):
            raise ValueError("Phase 6 fit scaler scale must be positive")

    return PreprocessorState(
        input_columns=tuple(frame.columns),
        medians=frozen_medians,
        null_counts=tuple(null_counts),
        standardize=bool(standardize),
        scaler_mean=scaler_mean,
        scaler_scale=scaler_scale,
    )


def transform_features(frame: pl.DataFrame, state: PreprocessorState) -> np.ndarray:
    if tuple(frame.columns) != state.input_columns:
        raise ValueError("Phase 6 transform column order does not match frozen fit state")

    matrix = _impute(_numeric_matrix(frame), state.medians)
    if not state.standardize:
        return matrix

    if state.scaler_mean is None or state.scaler_scale is None:
        raise ValueError("Phase 6 standardized state is missing scaler parameters")
    mean = np.asarray(state.scaler_mean, dtype=np.float64)
    scale = np.asarray(state.scaler_scale, dtype=np.float64)
    transformed = (matrix - mean) / scale
    if not np.isfinite(transformed).all():
        raise ValueError("Phase 6 standardized transform produced non-finite values")
    return transformed
