from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import polars as pl


@dataclass(frozen=True, slots=True)
class QualityFinding:
    symbol: str
    timestamp_start_utc: datetime
    timestamp_end_utc: datetime | None
    code: str
    severity: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _side_missing(row: dict[str, object], side: str) -> bool:
    return all(row[f"{side}_{field}"] is None for field in ("open", "high", "low", "close"))


def _ohlc_invalid(row: dict[str, object], side: str) -> bool:
    values = [row[f"{side}_{field}"] for field in ("open", "high", "low", "close")]
    if any(value is None for value in values):
        return False
    open_, high, low, close = (float(value) for value in values)
    return not (low <= open_ <= high and low <= close <= high)


def analyze_quality(frame: pl.DataFrame) -> dict[str, object]:
    findings: list[QualityFinding] = []
    compare_fields = ("open", "high", "low", "close")

    for row in frame.iter_rows(named=True):
        symbol = str(row["symbol"])
        timestamp = row["timestamp_utc"]
        if not isinstance(timestamp, datetime):
            raise ValueError("canonical timestamp_utc must be datetime")

        for side in ("bid", "ask"):
            if _side_missing(row, side):
                findings.append(
                    QualityFinding(
                        symbol,
                        timestamp,
                        None,
                        f"missing_{side}_side",
                        "error",
                        {},
                    )
                )
            elif _ohlc_invalid(row, side):
                findings.append(
                    QualityFinding(
                        symbol,
                        timestamp,
                        None,
                        f"{side}_ohlc_invalid",
                        "error",
                        {},
                    )
                )

        if not _side_missing(row, "bid") and not _side_missing(row, "ask"):
            breached = [
                field
                for field in compare_fields
                if row[f"ask_{field}"] is not None
                and row[f"bid_{field}"] is not None
                and float(row[f"ask_{field}"]) < float(row[f"bid_{field}"])
            ]
            if breached:
                findings.append(
                    QualityFinding(
                        symbol,
                        timestamp,
                        None,
                        "ask_below_bid",
                        "error",
                        {"fields": breached},
                    )
                )

    findings.sort(key=lambda item: (item.timestamp_start_utc, item.code))
    return {
        "row_count": frame.height,
        "findings": [finding.to_dict() for finding in findings],
    }
