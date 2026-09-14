from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
from collections import Counter, defaultdict
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Mapping, Sequence

from fmp.contracts import BacktestRun, ExitReason, RejectionCode, TradeRecord


BENCHMARK_ARTIFACT_PROTOCOL = "fmp-phase4-benchmark-artifacts-v1"


def _finite_positive(value: float, *, field: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field} must be finite and positive")


def _trade_summary(trades: Sequence[TradeRecord]) -> dict[str, object]:
    pnls = [trade.net_pnl_usd for trade in trades]
    wins = [value for value in pnls if value > 0]
    losses = [value for value in pnls if value < 0]
    count = len(pnls)
    return {
        "trade_count": count,
        "net_pnl_usd": sum(pnls),
        "expectancy_usd": (sum(pnls) / count) if count else None,
        "win_rate": (len(wins) / count) if count else None,
        "average_win_usd": (sum(wins) / len(wins)) if wins else None,
        "average_loss_usd": (sum(losses) / len(losses)) if losses else None,
    }


def _sample_ratio(values: Sequence[float], *, downside_only: bool = False) -> float | None:
    if downside_only:
        denominator_values = [value for value in values if value < 0]
        if len(denominator_values) < 2:
            return None
        deviation = statistics.stdev(denominator_values)
    else:
        if len(values) < 2:
            return None
        deviation = statistics.stdev(values)
    if deviation == 0:
        return None
    return statistics.mean(values) / deviation * math.sqrt(252.0)


def _breakdown(
    trades: Sequence[TradeRecord],
    key_for_trade: Mapping[str, str] | None = None,
    *,
    direct_key: str | None = None,
) -> dict[str, dict[str, object]]:
    buckets: dict[str, list[TradeRecord]] = defaultdict(list)
    for trade in trades:
        if direct_key == "symbol":
            key = trade.symbol
        elif direct_key == "year":
            key = str(trade.exit_timestamp_utc.year)
        elif key_for_trade is not None:
            key = key_for_trade.get(trade.decision_id, "unclassified")
        else:
            key = "all"
        buckets[key].append(trade)
    return {key: _trade_summary(buckets[key]) for key in sorted(buckets)}


def compute_research_metrics(
    run: BacktestRun,
    *,
    starting_equity_usd: float,
    requested_risk_fraction: float,
    candidate_metadata: Mapping[str, Mapping[str, object]],
    eligible_utc_dates: Sequence[date],
) -> dict[str, object]:
    _finite_positive(starting_equity_usd, field="starting_equity_usd")
    _finite_positive(requested_risk_fraction, field="requested_risk_fraction")

    dates = tuple(eligible_utc_dates)
    if dates != tuple(sorted(set(dates))):
        raise ValueError("eligible_utc_dates must be sorted and unique")

    reward_risk_values: list[float] = []
    for trade in run.trades:
        denominator = trade.risk_equity_before_usd * requested_risk_fraction
        _finite_positive(denominator, field="trade initial risk")
        reward_risk_values.append(trade.net_pnl_usd / denominator)

    pnl_by_date: dict[date, float] = defaultdict(float)
    for trade in run.trades:
        pnl_by_date[trade.exit_timestamp_utc.date()] += trade.net_pnl_usd
    unknown_exit_dates = sorted(set(pnl_by_date) - set(dates))
    if unknown_exit_dates:
        raise ValueError(f"trade exits fall outside eligible research dates: {unknown_exit_dates}")

    current_equity = starting_equity_usd
    daily_realized_returns: list[dict[str, object]] = []
    daily_values: list[float] = []
    for day in dates:
        day_start = current_equity
        _finite_positive(day_start, field="daily start equity")
        realized = pnl_by_date.get(day, 0.0)
        daily_return = realized / day_start
        daily_values.append(daily_return)
        daily_realized_returns.append(
            {
                "date": day.isoformat(),
                "risk_equity_at_start_usd": day_start,
                "realized_net_pnl_usd": realized,
                "return": daily_return,
            }
        )
        current_equity += realized

    session_keys: dict[str, str] = {}
    for trade in run.trades:
        metadata = candidate_metadata.get(trade.decision_id, {})
        session = metadata.get("session_name", "london")
        session_keys[trade.decision_id] = str(session)

    timeframe = str(run.run_identity.get("timeframe", "unknown"))
    timeframe_keys = {trade.decision_id: timeframe for trade in run.trades}
    rejection_counts = Counter(record.code.value for record in run.rejections)
    no_trade_count = rejection_counts.get(RejectionCode.NO_TRADE.value, 0)
    time_exit_count = sum(1 for trade in run.trades if trade.exit_reason is ExitReason.TIME_EXIT)

    rr_summary = {
        "count": len(reward_risk_values),
        "mean": statistics.mean(reward_risk_values) if reward_risk_values else None,
        "min": min(reward_risk_values) if reward_risk_values else None,
        "max": max(reward_risk_values) if reward_risk_values else None,
    }

    return {
        "phase3_metrics": dict(run.metrics),
        "trade_count": len(run.trades),
        "rejection_count": len(run.rejections),
        "no_trade_count": no_trade_count,
        "time_exit_count": time_exit_count,
        "rejection_reason_counts": dict(sorted(rejection_counts.items())),
        "reward_risk_values": reward_risk_values,
        "reward_risk_summary": rr_summary,
        "daily_realized_returns": daily_realized_returns,
        "sharpe": _sample_ratio(daily_values),
        "sortino": _sample_ratio(daily_values, downside_only=True),
        "pair_breakdown": _breakdown(run.trades, direct_key="symbol"),
        "timeframe_breakdown": _breakdown(run.trades, timeframe_keys),
        "session_breakdown": _breakdown(run.trades, session_keys),
        "calendar_year_breakdown": _breakdown(run.trades, direct_key="year"),
    }


def _jsonable(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _jsonable(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("serialized datetime must use UTC")
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("cannot serialize non-finite float")
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported deterministic serialization type: {type(value).__name__}")


def _stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            _jsonable(value),
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def _artifact_record(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.name,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def write_benchmark_artifacts(
    result: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    benchmark_path = root / "benchmark.json"
    _atomic_write(benchmark_path, _stable_json_bytes(dict(result)))
    manifest: dict[str, object] = {
        "protocol": BENCHMARK_ARTIFACT_PROTOCOL,
        "artifacts": [_artifact_record(benchmark_path)],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest
