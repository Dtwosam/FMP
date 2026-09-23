from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import math
from types import MappingProxyType
from typing import Mapping

from fmp.features.schema import FEATURE_VALUE_COLUMNS

from .contracts import EVIDENCE_LABEL, EXPERIMENT_ID, HORIZONS_MINUTES


MODEL_PROTOCOL_VERSION = "fmp-exp044-model-protocol-v1"
MODEL_PROTOCOL_DECISION = "DEC-088"
SCIKIT_LEARN_VERSION = "1.9.1"
MODEL_RANDOM_SEED = 20260923

MODEL_SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
MODEL_TIMEFRAMES = ("5m", "15m", "1h")
MODEL_HORIZONS_MINUTES = tuple(HORIZONS_MINUTES)

if MODEL_HORIZONS_MINUTES != (60, 240):
    raise RuntimeError("EXP-044 protocol requires exact 60m/240m horizons")

MODEL_INPUT_COLUMNS = tuple(FEATURE_VALUE_COLUMNS)
if len(MODEL_INPUT_COLUMNS) != 48:
    raise RuntimeError("EXP-044 protocol requires exact 48-feature input identity")

TARGET_COLUMN = "best_direction_0p5"
TARGET_SLIPPAGE_PIPS = 0.5
TARGET_CLASSES = ("LONG", "SHORT", "NO_TRADE")

MODEL_FAMILIES = (
    "logistic_regression",
    "hist_gradient_boosting",
)

CONFIDENCE_THRESHOLDS = (0.50, 0.60, 0.70)
MIN_DIRECTIONAL_CANDIDATES = 250

SELECTION_GATE_SCENARIOS = (0.5,)
VALIDATION_GATE_SCENARIOS = (0.5, 1.0)
HOLDOUT_GATE_SCENARIOS = (0.5, 1.0)
DIAGNOSTIC_SCENARIOS = (0.2,)

GATE_REQUIREMENTS = (
    "directional_candidate_count>=250",
    "total_net_pips>0",
    "mean_net_pips>0",
    "gross_positive_pips>absolute_gross_negative_pips",
)

SELECTION_TIE_BREAK = (
    "higher_total_net_pips_0p5",
    "higher_directional_candidate_count",
    "logistic_regression_before_hist_gradient_boosting",
    "higher_confidence_threshold",
)

MODEL_PROTOCOL_RESULT_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False


@dataclass(frozen=True, slots=True)
class ModelProtocolSplit:
    name: str
    start: date
    end_exclusive: date

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("model-protocol split name must be non-empty")
        if self.start >= self.end_exclusive:
            raise ValueError("model-protocol split start must precede end")


@dataclass(frozen=True, slots=True)
class ModelCell:
    symbol: str
    timeframe: str
    horizon_minutes: int


FIT_SPLIT = ModelProtocolSplit(
    "fit",
    date(2015, 1, 1),
    date(2021, 1, 1),
)
SELECTION_SPLIT = ModelProtocolSplit(
    "selection",
    date(2021, 1, 1),
    date(2023, 1, 1),
)
VALIDATION_SPLIT = ModelProtocolSplit(
    "validation",
    date(2023, 1, 1),
    date(2025, 1, 1),
)
RETROSPECTIVE_HOLDOUT_SPLIT = ModelProtocolSplit(
    "retrospective_holdout",
    date(2025, 1, 1),
    date(2026, 8, 21),
)

PROTOCOL_SPLITS = (
    FIT_SPLIT,
    SELECTION_SPLIT,
    VALIDATION_SPLIT,
    RETROSPECTIVE_HOLDOUT_SPLIT,
)

MODEL_CELLS = tuple(
    ModelCell(symbol, timeframe, horizon)
    for symbol in MODEL_SYMBOLS
    for timeframe in MODEL_TIMEFRAMES
    for horizon in MODEL_HORIZONS_MINUTES
)

LOGISTIC_REGRESSION_CONFIG = MappingProxyType(
    {
        "penalty": "l2",
        "C": 1.0,
        "solver": "lbfgs",
        "tol": 1e-8,
        "fit_intercept": True,
        "class_weight": None,
        "max_iter": 2000,
        "warm_start": False,
    }
)

HIST_GRADIENT_BOOSTING_CONFIG = MappingProxyType(
    {
        "loss": "log_loss",
        "learning_rate": 0.05,
        "max_iter": 100,
        "max_leaf_nodes": 15,
        "max_depth": 3,
        "min_samples_leaf": 20,
        "l2_regularization": 1.0,
        "max_features": 1.0,
        "max_bins": 255,
        "early_stopping": False,
        "warm_start": False,
        "class_weight": None,
        "random_state": MODEL_RANDOM_SEED,
    }
)

MODEL_FAMILY_CONFIGS = MappingProxyType(
    {
        "logistic_regression": LOGISTIC_REGRESSION_CONFIG,
        "hist_gradient_boosting": HIST_GRADIENT_BOOSTING_CONFIG,
    }
)


def _require_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


def split_accepts_observation(
    split: ModelProtocolSplit,
    *,
    available_at_utc: datetime,
    exit_timestamp_utc: datetime,
) -> bool:
    _require_utc(available_at_utc, field="available_at_utc")
    _require_utc(exit_timestamp_utc, field="exit_timestamp_utc")
    if exit_timestamp_utc <= available_at_utc:
        raise ValueError("exit_timestamp_utc must follow available_at_utc")

    start = datetime(
        split.start.year,
        split.start.month,
        split.start.day,
        tzinfo=timezone.utc,
    )
    end = datetime(
        split.end_exclusive.year,
        split.end_exclusive.month,
        split.end_exclusive.day,
        tzinfo=timezone.utc,
    )
    return (
        start <= available_at_utc < end
        and exit_timestamp_utc < end
    )


def directional_candidate(
    probabilities: Mapping[str, float],
    *,
    threshold: float,
) -> str:
    if threshold not in CONFIDENCE_THRESHOLDS:
        raise ValueError("unsupported EXP-044 confidence threshold")
    if set(probabilities) != set(TARGET_CLASSES):
        raise ValueError("EXP-044 probabilities must contain exact target classes")

    values = {name: float(probabilities[name]) for name in TARGET_CLASSES}
    if any(
        not math.isfinite(value) or value < 0.0 or value > 1.0
        for value in values.values()
    ):
        raise ValueError("EXP-044 class probabilities must be finite in [0, 1]")
    if not math.isclose(
        sum(values.values()),
        1.0,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise ValueError("EXP-044 class probabilities must sum to one")

    long_probability = values["LONG"]
    short_probability = values["SHORT"]
    no_trade_probability = values["NO_TRADE"]

    if (
        long_probability > short_probability
        and long_probability > no_trade_probability
        and long_probability >= threshold
    ):
        return "LONG"

    if (
        short_probability > long_probability
        and short_probability > no_trade_probability
        and short_probability >= threshold
    ):
        return "SHORT"

    return "NO_TRADE"


def protocol_payload() -> dict[str, object]:
    return {
        "protocol_version": MODEL_PROTOCOL_VERSION,
        "decision": MODEL_PROTOCOL_DECISION,
        "experiment_id": EXPERIMENT_ID,
        "evidence_label": EVIDENCE_LABEL,
        "scikit_learn_version": SCIKIT_LEARN_VERSION,
        "random_seed": MODEL_RANDOM_SEED,
        "cells": [
            {
                "symbol": cell.symbol,
                "timeframe": cell.timeframe,
                "horizon_minutes": cell.horizon_minutes,
            }
            for cell in MODEL_CELLS
        ],
        "input_columns": list(MODEL_INPUT_COLUMNS),
        "target": {
            "column": TARGET_COLUMN,
            "slippage_pips_per_fill": TARGET_SLIPPAGE_PIPS,
            "classes": list(TARGET_CLASSES),
        },
        "splits": [
            {
                "name": split.name,
                "start": split.start.isoformat(),
                "end_exclusive": split.end_exclusive.isoformat(),
            }
            for split in PROTOCOL_SPLITS
        ],
        "split_membership": (
            "available_at_utc>=start AND available_at_utc<end_exclusive "
            "AND exit_timestamp_utc<end_exclusive"
        ),
        "preprocessing": {
            "imputation": "fit_split_median",
            "all_null_fit_column": "FAIL_CLOSED",
            "logistic_regression_standardize": True,
            "hist_gradient_boosting_standardize": False,
            "class_weight": None,
            "resampling": None,
            "probability_calibration": None,
        },
        "model_family_configs": {
            family: dict(MODEL_FAMILY_CONFIGS[family])
            for family in MODEL_FAMILIES
        },
        "confidence_thresholds": list(CONFIDENCE_THRESHOLDS),
        "minimum_directional_candidates": MIN_DIRECTIONAL_CANDIDATES,
        "selection_gate_scenarios": list(SELECTION_GATE_SCENARIOS),
        "validation_gate_scenarios": list(VALIDATION_GATE_SCENARIOS),
        "holdout_gate_scenarios": list(HOLDOUT_GATE_SCENARIOS),
        "diagnostic_scenarios": list(DIAGNOSTIC_SCENARIOS),
        "gate_requirements": list(GATE_REQUIREMENTS),
        "selection_tie_break": list(SELECTION_TIE_BREAK),
        "no_refit_after_fit": True,
        "pooled_models_authorized": False,
        "probability_based_sizing_authorized": False,
        "model_protocol_result_authorized": MODEL_PROTOCOL_RESULT_AUTHORIZED,
        "model_fit_authorized": MODEL_FIT_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "shadow_authorized": SHADOW_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
    }


def protocol_fingerprint() -> str:
    payload = (
        json.dumps(
            protocol_payload(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "CONFIDENCE_THRESHOLDS",
    "DEMO_ORDER_AUTHORIZED",
    "DIAGNOSTIC_SCENARIOS",
    "FIT_SPLIT",
    "GATE_REQUIREMENTS",
    "HIST_GRADIENT_BOOSTING_CONFIG",
    "HOLDOUT_GATE_SCENARIOS",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_REGRESSION_CONFIG",
    "MIN_DIRECTIONAL_CANDIDATES",
    "MODEL_CELLS",
    "MODEL_FAMILIES",
    "MODEL_FAMILY_CONFIGS",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_HORIZONS_MINUTES",
    "MODEL_INPUT_COLUMNS",
    "MODEL_PROTOCOL_DECISION",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "MODEL_PROTOCOL_VERSION",
    "MODEL_RANDOM_SEED",
    "MODEL_SYMBOLS",
    "MODEL_TIMEFRAMES",
    "PROMOTION_AUTHORIZED",
    "PROTOCOL_SPLITS",
    "REAL_MONEY_AUTHORIZED",
    "RETROSPECTIVE_HOLDOUT_SPLIT",
    "SCIKIT_LEARN_VERSION",
    "SELECTION_GATE_SCENARIOS",
    "SELECTION_SPLIT",
    "SELECTION_TIE_BREAK",
    "SHADOW_AUTHORIZED",
    "TARGET_CLASSES",
    "TARGET_COLUMN",
    "TARGET_SLIPPAGE_PIPS",
    "VALIDATION_GATE_SCENARIOS",
    "VALIDATION_SPLIT",
    "ModelCell",
    "ModelProtocolSplit",
    "directional_candidate",
    "protocol_fingerprint",
    "protocol_payload",
    "split_accepts_observation",
]
