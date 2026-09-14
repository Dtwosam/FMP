from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import polars as pl


def tf_minutes(timeframe: str) -> int:
    return {"5m": 5, "15m": 15, "1h": 60}[timeframe]


def make_bars(
    *,
    symbol: str = "EURUSD",
    timeframe: str = "1h",
    start: datetime = datetime(2023, 1, 2, tzinfo=timezone.utc),
    count: int = 40,
    base: float | None = None,
    step: float | None = None,
    spread: float | None = None,
) -> pl.DataFrame:
    minutes = tf_minutes(timeframe)
    if base is None:
        base = 1.10 if symbol != "USDJPY" else 130.0
    if step is None:
        step = 0.0001 if symbol != "USDJPY" else 0.01
    if spread is None:
        spread = 0.00002 if symbol != "USDJPY" else 0.002
    rows: list[dict[str, object]] = []
    for i in range(count):
        ts = start + timedelta(minutes=minutes * i)
        mid_open = base + step * i
        mid_close = mid_open + step * 0.4
        mid_high = max(mid_open, mid_close) + abs(step) * 0.3
        mid_low = min(mid_open, mid_close) - abs(step) * 0.2
        half = spread / 2.0
        rows.append(
            {
                "timestamp_utc": ts,
                "symbol": symbol,
                "bid_open": mid_open - half,
                "bid_high": mid_high - half,
                "bid_low": mid_low - half,
                "bid_close": mid_close - half,
                "ask_open": mid_open + half,
                "ask_high": mid_high + half,
                "ask_low": mid_low + half,
                "ask_close": mid_close + half,
                "bid_volume": 1.0 + i,
                "ask_volume": 2.0 + i,
                "source_minutes": minutes,
                "expected_open_minutes": minutes,
                "is_complete": True,
                "timeframe": timeframe,
                "schema_version": "fmp-derived-bars-v1",
            }
        )
    return pl.DataFrame(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_dataset(
    root: Path,
    *,
    symbol: str,
    timeframe: str,
    monthly_frames: dict[str, pl.DataFrame],
) -> Path:
    artifacts: dict[str, dict[str, object]] = {}
    for month, frame in sorted(monthly_frames.items()):
        year, mon = month.split("-")
        path = root / "processed" / "fmp-canonical-1m-v1" / timeframe / symbol / year / f"{mon}.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.write_parquet(path, compression="zstd", compression_level=3, statistics=True)
        artifacts[f"{timeframe}:{month}"] = {
            "path": path.relative_to(root).as_posix(),
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size,
            "row_count": frame.height,
        }
    manifest = {
        "manifest_version": 1,
        "symbol": symbol,
        "schema_version": "fmp-canonical-1m-v1",
        "artifacts": artifacts,
    }
    path = root / "manifests" / "processed" / "fmp-canonical-1m-v1" / f"{symbol}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return path
