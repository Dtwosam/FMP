from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Mapping


EXPERIMENT_ID = "EXP-20260915-008"
PHASE6_CHECKPOINT_SHA = "5d387b7ca93d04c498eb04c376e0dd92f1fe1953"
USDJPY_PHASE2_ARTIFACT_ID = 10327600628
USDJPY_PHASE2_ZIP_SHA256 = (
    "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72"
)
USDJPY_PROCESSED_MANIFEST_SHA256 = (
    "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d"
)

SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)
GATING_SLIPPAGE_SCENARIOS = (0.2, 0.5)
MAX_WARMUP_DAYS = 7
STARTING_EQUITY_USD = 100_000.0
REQUESTED_RISK_FRACTION = 0.0025


@dataclass(frozen=True, slots=True)
class Phase7Window:
    name: str
    start: date
    end_exclusive: date

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Phase 7 window name must be non-empty")
        if self.start >= self.end_exclusive:
            raise ValueError("Phase 7 window start must be before end_exclusive")


STAGE1_WINDOW = Phase7Window(
    name="stage1-2024",
    start=date(2024, 1, 1),
    end_exclusive=date(2025, 1, 1),
)
STAGE2_WINDOWS = (
    Phase7Window("2025-Q1", date(2025, 1, 1), date(2025, 4, 1)),
    Phase7Window("2025-Q2", date(2025, 4, 1), date(2025, 7, 1)),
    Phase7Window("2025-Q3", date(2025, 7, 1), date(2025, 10, 1)),
    Phase7Window("2025-Q4", date(2025, 10, 1), date(2026, 1, 1)),
    Phase7Window("2026-Q1", date(2026, 1, 1), date(2026, 4, 1)),
    Phase7Window("2026-Q2", date(2026, 4, 1), date(2026, 7, 1)),
    Phase7Window("2026-partial-Q3", date(2026, 7, 1), date(2026, 8, 21)),
)

_ALLOWED_WINDOWS = MappingProxyType(
    {window.name: window for window in (STAGE1_WINDOW, *STAGE2_WINDOWS)}
)


def allowed_phase7_window(name: str) -> Phase7Window:
    try:
        return _ALLOWED_WINDOWS[name]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"unsupported Phase 7 window: {name!r}") from exc


@dataclass(frozen=True, slots=True)
class FrozenPhase7Candidate:
    candidate_id: str
    symbol: str
    timeframe: str
    parameters: Mapping[str, float | int]

    def __post_init__(self) -> None:
        for field_name in ("candidate_id", "symbol", "timeframe"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must be non-empty")
        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))


FROZEN_CANDIDATES = MappingProxyType(
    {
        "session_breakout": FrozenPhase7Candidate(
            candidate_id="session_breakout",
            symbol="USDJPY",
            timeframe="15m",
            parameters={"buffer_pips": 5, "target_range_multiple": 1.5},
        ),
        "volatility_breakout": FrozenPhase7Candidate(
            candidate_id="volatility_breakout",
            symbol="USDJPY",
            timeframe="1h",
            parameters={"range_multiplier": 2.0, "target_r": 1.0},
        ),
    }
)
