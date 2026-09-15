from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from types import MappingProxyType
from typing import Mapping


EXPERIMENT_ID = "EXP-20260915-007"
FEATURE_SET_VERSION = "fmp-feature-v1"
PHASE5_CHECKPOINT_SHA = "e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0"
USDJPY_PROCESSED_MANIFEST_SHA256 = (
    "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d"
)
FINAL_START = date(2024, 1, 1)


@dataclass(frozen=True)
class Phase6Split:
    name: str
    start: date
    end_exclusive: date

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("split name must be non-empty")
        if self.start >= self.end_exclusive:
            raise ValueError("split start must be before end_exclusive")
        if self.end_exclusive > FINAL_START:
            raise ValueError("Phase 6 final-test data at 2024-01-01 or later is locked")


FIT_SPLIT = Phase6Split("fit", date(2015, 1, 1), date(2019, 1, 1))
SELECTION_SPLIT = Phase6Split("selection", date(2019, 1, 1), date(2021, 1, 1))
VALIDATION_SPLIT = Phase6Split("validation", date(2021, 1, 1), FINAL_START)

_SPLITS = MappingProxyType(
    {
        FIT_SPLIT.name: FIT_SPLIT,
        SELECTION_SPLIT.name: SELECTION_SPLIT,
        VALIDATION_SPLIT.name: VALIDATION_SPLIT,
    }
)


def allowed_phase6_split(name: str) -> Phase6Split:
    try:
        return _SPLITS[name]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"unsupported Phase 6 split: {name!r}") from exc


@dataclass(frozen=True)
class FrozenStrategySpec:
    symbol: str
    timeframe: str
    family: str
    parameters: Mapping[str, float | int]

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))


FROZEN_STRATEGIES = MappingProxyType(
    {
        "session_breakout": FrozenStrategySpec(
            symbol="USDJPY",
            timeframe="15m",
            family="session_breakout",
            parameters={"buffer_pips": 5, "target_range_multiple": 1.5},
        ),
        "volatility_breakout": FrozenStrategySpec(
            symbol="USDJPY",
            timeframe="1h",
            family="volatility_breakout",
            parameters={"range_multiplier": 2.0, "target_r": 1.0},
        ),
    }
)


class ModelFamily(str, Enum):
    LOGISTIC_REGRESSION = "logistic_regression"
    HIST_GRADIENT_BOOSTING = "hist_gradient_boosting"
