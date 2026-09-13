from __future__ import annotations

import math
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

import polars as pl

from .market_hours import is_market_open_minute
from .schema import CANONICAL_SCHEMA_VERSION, INGESTION_VERSION, validate_canonical_frame

_PIP_SCALES = {"EURUSD": 10_000.0, "GBPUSD": 10_000.0, "USDJPY": 100.0}
_PRICE_FIELDS = tuple(
    f"{side}_{field}"
    for side in ("bid", "ask")
    for field in ("open", "high", "low", "close")
)
_VOLUME_FIELDS = ("bid_volume", "ask_volume")


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
    numeric = [float(value) for value in values]
    if any(not math.isfinite(value) for value in numeric):
        return False
    open_, high, low, close = numeric
    return not (low <= open_ <= high and low <= close <= high)


def _duplicate_findings(frame: pl.DataFrame) -> tuple[list[QualityFinding], int, set[tuple[str, datetime]]]:
    counts: Counter[tuple[str, datetime]] = Counter()
    for symbol, timestamp in frame.select("symbol", "timestamp_utc").iter_rows():
        if not isinstance(timestamp, datetime):
            raise ValueError("canonical timestamp_utc must be datetime")
        counts[(str(symbol), timestamp)] += 1

    findings: list[QualityFinding] = []
    duplicate_count = 0
    duplicate_keys: set[tuple[str, datetime]] = set()
    for (symbol, timestamp), count in sorted(counts.items()):
        if count <= 1:
            continue
        duplicate_keys.add((symbol, timestamp))
        duplicate_count += count - 1
        findings.append(
            QualityFinding(
                symbol,
                timestamp,
                None,
                "duplicate_timestamp",
                "error",
                {"row_count": count, "duplicate_rows": count - 1},
            )
        )
    return findings, duplicate_count, duplicate_keys


def _market_segments(missing: list[datetime]) -> list[tuple[bool, list[datetime]]]:
    if not missing:
        return []
    segments: list[tuple[bool, list[datetime]]] = []
    current_open = is_market_open_minute(missing[0])
    current = [missing[0]]
    for timestamp in missing[1:]:
        market_open = is_market_open_minute(timestamp)
        if market_open == current_open:
            current.append(timestamp)
            continue
        segments.append((current_open, current))
        current_open = market_open
        current = [timestamp]
    segments.append((current_open, current))
    return segments


def _gap_findings(frame: pl.DataFrame) -> list[QualityFinding]:
    result: list[QualityFinding] = []
    by_symbol: dict[str, list[datetime]] = {}
    for symbol, timestamp in frame.select("symbol", "timestamp_utc").iter_rows():
        if not isinstance(timestamp, datetime):
            raise ValueError("canonical timestamp_utc must be datetime")
        by_symbol.setdefault(str(symbol), []).append(timestamp)

    for symbol, values in by_symbol.items():
        ordered = sorted(set(values))
        for left, right in zip(ordered, ordered[1:]):
            minutes = int((right - left).total_seconds() // 60) - 1
            if minutes <= 0:
                continue
            missing = [left + timedelta(minutes=i) for i in range(1, minutes + 1)]
            for market_open, segment in _market_segments(missing):
                segment_minutes = len(segment)
                if market_open:
                    result.append(
                        QualityFinding(
                            symbol,
                            segment[0],
                            segment[-1],
                            "missing_open_market_minute",
                            "error",
                            {"missing_minutes": segment_minutes},
                        )
                    )
                    if segment_minutes >= 30:
                        result.append(
                            QualityFinding(
                                symbol,
                                segment[0],
                                segment[-1],
                                "long_weekday_gap",
                                "error",
                                {"missing_minutes": segment_minutes, "threshold_minutes": 30},
                            )
                        )
                else:
                    result.append(
                        QualityFinding(
                            symbol,
                            segment[0],
                            segment[-1],
                            "weekend_closure_gap",
                            "info",
                            {"missing_minutes": segment_minutes},
                        )
                    )
    return result


def _gap_summary(findings: list[QualityFinding]) -> dict[str, object]:
    suspicious = [finding for finding in findings if finding.code == "missing_open_market_minute"]
    weekend = [finding for finding in findings if finding.code == "weekend_closure_gap"]
    suspicious_spans = [
        {
            "symbol": finding.symbol,
            "timestamp_start_utc": finding.timestamp_start_utc,
            "timestamp_end_utc": finding.timestamp_end_utc,
            "missing_minutes": int(finding.details["missing_minutes"]),
        }
        for finding in suspicious
    ]
    suspicious_minutes = [int(finding.details["missing_minutes"]) for finding in suspicious]
    return {
        "missing_open_market_minutes": sum(suspicious_minutes),
        "suspicious_gap_spans": suspicious_spans,
        "max_suspicious_gap_minutes": max(suspicious_minutes, default=0),
        "weekend_closure_gap_count": len(weekend),
        "weekend_closure_minutes": sum(
            int(finding.details["missing_minutes"]) for finding in weekend
        ),
    }


def _iqr_summary(samples: list[tuple[datetime, float]]) -> tuple[dict[str, object], list[tuple[datetime, float]], float | None]:
    if not samples:
        return ({"count": 0, "q1": None, "q3": None, "iqr": None, "threshold": None, "outlier_count": 0}, [], None)

    series = pl.Series("value", [value for _, value in samples], dtype=pl.Float64)
    q1_value = series.quantile(0.25, interpolation="nearest")
    q3_value = series.quantile(0.75, interpolation="nearest")
    if q1_value is None or q3_value is None:
        raise ValueError("unable to calculate deterministic IQR summary")
    q1 = float(q1_value)
    q3 = float(q3_value)
    iqr = q3 - q1
    threshold = q3 if iqr == 0.0 else q3 + 10.0 * iqr
    outliers = [(timestamp, value) for timestamp, value in samples if value > threshold]
    return (
        {
            "count": len(samples),
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "threshold": threshold,
            "outlier_count": len(outliers),
        },
        outliers,
        threshold,
    )


def _spread_analysis(frame: pl.DataFrame, duplicate_keys: set[tuple[str, datetime]]) -> tuple[dict[str, dict[str, object]], list[QualityFinding]]:
    samples_by_symbol: dict[str, list[tuple[datetime, float]]] = {}
    for row in frame.iter_rows(named=True):
        symbol = str(row["symbol"])
        timestamp = row["timestamp_utc"]
        if not isinstance(timestamp, datetime) or (symbol, timestamp) in duplicate_keys:
            continue
        bid = row["bid_close"]
        ask = row["ask_close"]
        if bid is None or ask is None:
            continue
        bid_value = float(bid)
        ask_value = float(ask)
        if not (math.isfinite(bid_value) and math.isfinite(ask_value)):
            continue
        if bid_value <= 0.0 or ask_value <= 0.0 or ask_value < bid_value:
            continue
        scale = _PIP_SCALES.get(symbol)
        if scale is None:
            continue
        samples_by_symbol.setdefault(symbol, []).append((timestamp, (ask_value - bid_value) * scale))

    summaries: dict[str, dict[str, object]] = {}
    findings: list[QualityFinding] = []
    for symbol in sorted(set(frame["symbol"].cast(pl.String).to_list())):
        samples = samples_by_symbol.get(symbol, [])
        summary, outliers, threshold = _iqr_summary(samples)
        summaries[symbol] = summary
        for timestamp, value in outliers:
            findings.append(
                QualityFinding(
                    symbol,
                    timestamp,
                    None,
                    "spread_outlier",
                    "warning",
                    {"spread_pips": value, "threshold_pips": threshold},
                )
            )
    return summaries, findings


def _midpoint_return_analysis(frame: pl.DataFrame, duplicate_keys: set[tuple[str, datetime]]) -> tuple[dict[str, dict[str, object]], list[QualityFinding]]:
    valid_by_symbol: dict[str, list[tuple[datetime, float]]] = {}
    for row in frame.iter_rows(named=True):
        symbol = str(row["symbol"])
        timestamp = row["timestamp_utc"]
        if not isinstance(timestamp, datetime) or (symbol, timestamp) in duplicate_keys:
            continue
        bid = row["bid_close"]
        ask = row["ask_close"]
        if bid is None or ask is None:
            continue
        bid_value = float(bid)
        ask_value = float(ask)
        if not (math.isfinite(bid_value) and math.isfinite(ask_value)):
            continue
        if bid_value <= 0.0 or ask_value <= 0.0 or ask_value < bid_value:
            continue
        valid_by_symbol.setdefault(symbol, []).append((timestamp, (bid_value + ask_value) / 2.0))

    summaries: dict[str, dict[str, object]] = {}
    findings: list[QualityFinding] = []
    all_symbols = sorted(set(frame["symbol"].cast(pl.String).to_list()))
    for symbol in all_symbols:
        values = sorted(valid_by_symbol.get(symbol, []), key=lambda item: item[0])
        samples: list[tuple[datetime, float]] = []
        for (previous_time, previous_mid), (current_time, current_mid) in zip(values, values[1:]):
            if current_time - previous_time != timedelta(minutes=1):
                continue
            samples.append((current_time, abs(current_mid / previous_mid - 1.0)))

        summary, outliers, threshold = _iqr_summary(samples)
        summaries[symbol] = summary
        for timestamp, value in outliers:
            findings.append(
                QualityFinding(
                    symbol,
                    timestamp,
                    None,
                    "price_jump_outlier",
                    "warning",
                    {"absolute_midpoint_return": value, "threshold": threshold},
                )
            )
    return summaries, findings


def analyze_quality(frame: pl.DataFrame) -> dict[str, object]:
    validate_canonical_frame(frame)
    findings: list[QualityFinding] = []
    compare_fields = ("open", "high", "low", "close")
    duplicate_findings, duplicate_count, duplicate_keys = _duplicate_findings(frame)
    findings.extend(duplicate_findings)

    missing_bid_rows = 0
    missing_ask_rows = 0
    required_null_count = 0

    for row in frame.iter_rows(named=True):
        symbol = str(row["symbol"])
        timestamp = row["timestamp_utc"]
        if not isinstance(timestamp, datetime):
            raise ValueError("canonical timestamp_utc must be datetime")

        missing_bid = _side_missing(row, "bid")
        missing_ask = _side_missing(row, "ask")
        missing_bid_rows += int(missing_bid)
        missing_ask_rows += int(missing_ask)
        required_null_count += sum(row[field] is None for field in _PRICE_FIELDS)

        for side in ("bid", "ask"):
            if _side_missing(row, side):
                findings.append(QualityFinding(symbol, timestamp, None, f"missing_{side}_side", "error", {}))
            elif _ohlc_invalid(row, side):
                findings.append(QualityFinding(symbol, timestamp, None, f"{side}_ohlc_invalid", "error", {}))

        non_finite_fields = [
            field
            for field in (*_PRICE_FIELDS, *_VOLUME_FIELDS)
            if row[field] is not None and not math.isfinite(float(row[field]))
        ]
        if non_finite_fields:
            findings.append(
                QualityFinding(
                    symbol,
                    timestamp,
                    None,
                    "non_finite_value",
                    "error",
                    {"fields": non_finite_fields},
                )
            )

        non_positive_price_fields = [
            field
            for field in _PRICE_FIELDS
            if row[field] is not None
            and math.isfinite(float(row[field]))
            and float(row[field]) <= 0.0
        ]
        if non_positive_price_fields:
            findings.append(
                QualityFinding(
                    symbol,
                    timestamp,
                    None,
                    "non_positive_price",
                    "error",
                    {"fields": non_positive_price_fields},
                )
            )

        negative_volume_fields = [
            field
            for field in _VOLUME_FIELDS
            if row[field] is not None
            and math.isfinite(float(row[field]))
            and float(row[field]) < 0.0
        ]
        if negative_volume_fields:
            findings.append(
                QualityFinding(
                    symbol,
                    timestamp,
                    None,
                    "negative_volume",
                    "error",
                    {"fields": negative_volume_fields},
                )
            )

        if not missing_bid and not missing_ask:
            breached = [
                field
                for field in compare_fields
                if row[f"ask_{field}"] is not None
                and row[f"bid_{field}"] is not None
                and math.isfinite(float(row[f"ask_{field}"]))
                and math.isfinite(float(row[f"bid_{field}"]))
                and float(row[f"ask_{field}"]) < float(row[f"bid_{field}"])
            ]
            if breached:
                findings.append(QualityFinding(symbol, timestamp, None, "ask_below_bid", "error", {"fields": breached}))

    gap_findings = _gap_findings(frame)
    gap_summary = _gap_summary(gap_findings)
    findings.extend(gap_findings)
    spread_summary, spread_findings = _spread_analysis(frame, duplicate_keys)
    midpoint_return_summary, jump_findings = _midpoint_return_analysis(frame, duplicate_keys)
    findings.extend(spread_findings)
    findings.extend(jump_findings)
    findings.sort(key=lambda item: (item.timestamp_start_utc, item.code))

    timestamps = [value for value in frame["timestamp_utc"].to_list() if isinstance(value, datetime)]
    finding_counts = Counter(finding.code for finding in findings)
    return {
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "ingestion_version": INGESTION_VERSION,
        "actual_start_utc": min(timestamps) if timestamps else None,
        "actual_end_utc": max(timestamps) if timestamps else None,
        "row_count": frame.height,
        "missing_bid_rows": missing_bid_rows,
        "missing_ask_rows": missing_ask_rows,
        "required_null_count": required_null_count,
        "duplicate_count": duplicate_count,
        **gap_summary,
        "finding_counts": dict(sorted(finding_counts.items())),
        "spread_summary": spread_summary,
        "midpoint_return_summary": midpoint_return_summary,
        "findings": [finding.to_dict() for finding in findings],
    }
