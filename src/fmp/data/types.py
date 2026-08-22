from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

Pair = Literal["EURUSD", "GBPUSD", "USDJPY"]
Side = Literal["BID", "ASK"]

_ALLOWED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}
_ALLOWED_SIDES = {"BID", "ASK"}


@dataclass(frozen=True, slots=True)
class RawChunkKey:
    pair: Pair
    side: Side
    day: date

    def __post_init__(self) -> None:
        if self.pair not in _ALLOWED_PAIRS:
            raise ValueError(f"unsupported V1 pair: {self.pair}")
        if self.side not in _ALLOWED_SIDES:
            raise ValueError(f"unsupported side: {self.side}")

    @property
    def zero_based_month(self) -> int:
        return self.day.month - 1

    @property
    def filename(self) -> str:
        return f"{self.side}_candles_min_1.bi5"

    @property
    def manifest_filename(self) -> str:
        return f"{self.side}_candles_min_1.json"

    @property
    def relative_raw_path(self) -> Path:
        return Path(
            "dukascopy",
            "v1",
            self.pair,
            f"{self.day.year:04d}",
            f"{self.zero_based_month:02d}",
            f"{self.day.day:02d}",
            self.filename,
        )

    @property
    def relative_manifest_path(self) -> Path:
        return Path(
            "dukascopy",
            "v1",
            self.pair,
            f"{self.day.year:04d}",
            f"{self.zero_based_month:02d}",
            f"{self.day.day:02d}",
            self.manifest_filename,
        )
