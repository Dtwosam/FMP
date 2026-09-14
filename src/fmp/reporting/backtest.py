from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import fields, is_dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Mapping, Sequence

from fmp.contracts import BacktestRun, EquityCheckpoint, RejectionRecord, TradeRecord

ARTIFACT_PROTOCOL = "fmp-phase3-backtest-artifacts-v1"


def _validate_starting_equity(value: float) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError("starting equity must be finite and positive")


def _longest_streak(values: Sequence[float], *, winning: bool) -> int:
    longest = 0
    current = 0
    for value in values:
        match = value > 0 if winning else value < 0
        if match:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def compute_backtest_metrics(
    *,
    starting_equity_usd: float,
    trades: Sequence[TradeRecord],
    equity_checkpoints: Sequence[EquityCheckpoint],
) -> dict[str, object]:
    _validate_starting_equity(starting_equity_usd)
    pnls = [trade.net_pnl_usd for trade in trades]
    if any(not math.isfinite(value) for value in pnls):
        raise ValueError("trade net PnL must be finite")

    net_pnl = sum(pnls)
    wins = [value for value in pnls if value > 0]
    losses = [value for value in pnls if value < 0]
    trade_count = len(pnls)
    gross_profit = sum(wins)
    gross_loss = -sum(losses)

    peak = starting_equity_usd
    max_drawdown_usd = 0.0
    max_drawdown_fraction = 0.0
    previous_timestamp: datetime | None = None
    for checkpoint in equity_checkpoints:
        if checkpoint.timestamp_utc.tzinfo is None or checkpoint.timestamp_utc.utcoffset() != timedelta(0):
            raise ValueError("equity checkpoint timestamp must use UTC")
        if previous_timestamp is not None and checkpoint.timestamp_utc < previous_timestamp:
            raise ValueError("equity checkpoints must be chronological")
        previous_timestamp = checkpoint.timestamp_utc
        equity = checkpoint.realized_risk_equity_usd
        if not math.isfinite(equity):
            raise ValueError("equity checkpoint must be finite")
        if equity > peak:
            peak = equity
        drawdown = peak - equity
        if drawdown > max_drawdown_usd:
            max_drawdown_usd = drawdown
            max_drawdown_fraction = drawdown / peak if peak > 0 else 0.0

    slippage_cost = sum(trade.slippage_cost_usd for trade in trades)
    commission_cost = sum(trade.commission_cost_usd for trade in trades)
    financing_cost = sum(trade.financing_cost_usd for trade in trades)

    return {
        "net_pnl_usd": net_pnl,
        "net_return": net_pnl / starting_equity_usd,
        "trade_count": trade_count,
        "win_rate": (len(wins) / trade_count) if trade_count else None,
        "average_win_usd": (sum(wins) / len(wins)) if wins else None,
        "average_loss_usd": (sum(losses) / len(losses)) if losses else None,
        "expectancy_usd": (net_pnl / trade_count) if trade_count else None,
        "gross_profit_usd": gross_profit,
        "gross_loss_usd": gross_loss,
        "profit_factor": (gross_profit / gross_loss) if gross_loss > 0 else None,
        "max_drawdown_usd": max_drawdown_usd,
        "max_drawdown_fraction": max_drawdown_fraction,
        "recovery_factor": (net_pnl / max_drawdown_usd) if max_drawdown_usd > 0 else None,
        "longest_winning_streak": _longest_streak(pnls, winning=True),
        "longest_losing_streak": _longest_streak(pnls, winning=False),
        "slippage_cost_usd": slippage_cost,
        "commission_cost_usd": commission_cost,
        "financing_cost_usd": financing_cost,
        "total_explicit_cost_usd": slippage_cost + commission_cost + financing_cost,
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


def _stable_jsonl_bytes(values: Sequence[object]) -> bytes:
    lines = [
        json.dumps(
            _jsonable(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        for value in values
    ]
    return (("\n".join(lines) + "\n") if lines else "").encode("utf-8")


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


def write_backtest_artifacts(run: BacktestRun, out_dir: Path) -> dict[str, object]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "protocol": "fmp-phase3-backtest-run-v1",
        "run_identity": run.run_identity,
        "trade_count": len(run.trades),
        "rejection_count": len(run.rejections),
        "equity_checkpoint_count": len(run.equity_checkpoints),
        "equity_checkpoints": run.equity_checkpoints,
    }
    trades = sorted(run.trades, key=lambda item: (item.exit_timestamp_utc, item.trade_id))
    rejections = sorted(
        run.rejections,
        key=lambda item: (item.evaluated_timestamp_utc, item.decision_id),
    )

    payloads = {
        "summary.json": _stable_json_bytes(summary),
        "trades.jsonl": _stable_jsonl_bytes(trades),
        "rejections.jsonl": _stable_jsonl_bytes(rejections),
        "metrics.json": _stable_json_bytes(run.metrics),
    }
    for name, data in payloads.items():
        _atomic_write(out_dir / name, data)

    artifacts = [_artifact_record(out_dir / name) for name in sorted(payloads)]
    manifest: dict[str, object] = {
        "protocol": ARTIFACT_PROTOCOL,
        "artifacts": artifacts,
    }
    _atomic_write(out_dir / "manifest.json", _stable_json_bytes(manifest))
    return manifest
