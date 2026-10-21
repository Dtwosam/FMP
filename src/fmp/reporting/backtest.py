from __future__ import annotations

import hashlib
from collections import Counter
import json
import math
import os
import stat
import tempfile
from dataclasses import fields, is_dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Sequence

from fmp.backtest import BACKTEST_ENGINE_VERSION
from fmp.backtest.costs import apply_adverse_slippage
from fmp.risk import pnl_usd
from fmp.contracts import (
    BacktestRun, Direction, EquityCheckpoint, ExitReason, OrderSide, RejectionCode,
    RejectionRecord, SUPPORTED_SYMBOLS, TradeRecord,
)

ARTIFACT_PROTOCOL = "fmp-phase3-backtest-artifacts-v1"


def _validate_starting_equity(value: float) -> None:
    if type(value) not in (int, float):
        raise ValueError("starting equity must be finite and positive")
    try:
        if not math.isfinite(value) or value <= 0:
            raise ValueError("starting equity must be finite and positive")
    except OverflowError as exc:
        raise ValueError("starting equity must be finite and positive") from exc


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
    # Prevent caller-defined sequence/getter code from creating financial
    # evidence; admit only canonical records in ordinary containers.
    if (
        type(trades) not in (list, tuple)
        or any(type(item) is not TradeRecord for item in trades)
    ):
        raise ValueError("trades must be a list or tuple of TradeRecord records")
    if (
        type(equity_checkpoints) not in (list, tuple)
        or any(type(item) is not EquityCheckpoint for item in equity_checkpoints)
    ):
        raise ValueError(
            "equity checkpoints must be a list or tuple of EquityCheckpoint records"
        )
    for item in trades:
        for field_name in (
            "net_pnl_usd", "slippage_cost_usd",
            "commission_cost_usd", "financing_cost_usd",
        ):
            value = getattr(item, field_name)
            if type(value) not in (int, float):
                raise ValueError(f"trade {field_name} must be finite numeric")
            try:
                if not math.isfinite(value):
                    raise ValueError(f"trade {field_name} must be finite numeric")
            except OverflowError as exc:
                raise ValueError(f"trade {field_name} must be finite numeric") from exc
            if field_name in ("slippage_cost_usd", "commission_cost_usd") and value < 0:
                raise ValueError(f"trade {field_name} must be non-negative")
    # Align win/loss streaks with the writer's canonical exit-time order.
    for trade in trades:
        if type(trade.trade_id) is not str or not trade.trade_id:
            raise ValueError("trade ID must be a nonempty string")
        stamp = trade.exit_timestamp_utc
        if (
            type(stamp) is not datetime or stamp.tzinfo is None
            or stamp.utcoffset() != timedelta(0)
        ):
            raise ValueError("trade exit timestamp must use UTC")
    pnls = [trade.net_pnl_usd for trade in trades]
    streak_pnls = [
        item.net_pnl_usd for item in sorted(
            trades, key=lambda item: (item.exit_timestamp_utc, item.trade_id)
        )
    ]
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
        timestamp = checkpoint.timestamp_utc
        if (
            type(timestamp) is not datetime
            or timestamp.tzinfo is None
            or timestamp.utcoffset() != timedelta(0)
        ):
            raise ValueError("equity checkpoint timestamp must use UTC")
        if previous_timestamp is not None and checkpoint.timestamp_utc < previous_timestamp:
            raise ValueError("equity checkpoints must be chronological")
        previous_timestamp = checkpoint.timestamp_utc
        equity = checkpoint.realized_risk_equity_usd
        if type(equity) not in (int, float):
            raise ValueError("equity checkpoint must be finite numeric")
        try:
            if not math.isfinite(equity):
                raise ValueError("equity checkpoint must be finite numeric")
        except OverflowError as exc:
            raise ValueError("equity checkpoint must be finite numeric") from exc
        if equity > peak:
            peak = equity
        drawdown = peak - equity
        if drawdown > max_drawdown_usd:
            max_drawdown_usd = drawdown
            max_drawdown_fraction = drawdown / peak if peak > 0 else 0.0

    slippage_cost = sum(trade.slippage_cost_usd for trade in trades)
    commission_cost = sum(trade.commission_cost_usd for trade in trades)
    financing_cost = sum(trade.financing_cost_usd for trade in trades)

    try:
        metrics = {
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
        "longest_winning_streak": _longest_streak(streak_pnls, winning=True),
        "longest_losing_streak": _longest_streak(streak_pnls, winning=False),
        "slippage_cost_usd": slippage_cost,
        "commission_cost_usd": commission_cost,
        "financing_cost_usd": financing_cost,
        "total_explicit_cost_usd": slippage_cost + commission_cost + financing_cost,
        }
    except OverflowError as exc:
        raise ValueError("backtest metric calculation must remain finite") from exc
    # Finite individual trades can still overflow during aggregation or
    # ratio calculation. Never return non-finite economic evidence.
    for name, value in metrics.items():
        if type(value) is float and not math.isfinite(value):
            raise ValueError(f"backtest metric {name} must remain finite")
    return metrics


def _jsonable(value: object, *, depth: int = 0) -> object:
    # The supported config tree may be 32 levels deep. Leave headroom for
    # run-envelope nesting while preventing uncontrolled Python recursion.
    if depth > 64:
        raise ValueError("deterministic evidence exceeds maximum nesting depth")
    if is_dataclass(value) and not isinstance(value, type):
        # Caller-defined dataclasses may override field getters; evidence
        # serialization accepts only the source-defined record contracts.
        if type(value) not in (TradeRecord, RejectionRecord, EquityCheckpoint):
            raise ValueError("unsupported deterministic evidence dataclass")
        return {
            item.name: _jsonable(getattr(value, item.name), depth=depth + 1)
            for item in fields(value)
        }
    if type(value) in (Direction, ExitReason, RejectionCode):
        return _jsonable(value.value, depth=depth + 1)
    if isinstance(value, Enum):
        raise ValueError("unsupported deterministic evidence enum")
    if type(value) is datetime:
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("serialized datetime must use UTC")
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, datetime):
        raise ValueError("unsupported deterministic datetime subtype")
    if isinstance(value, Mapping):
        # Source identity keys must never be coerced. For example 1 and "1"
        # would otherwise collapse to one JSON key and corrupt provenance.
        if type(value) not in (dict, MappingProxyType):
            raise ValueError("serialized mapping must be an ordinary mapping")
        for key in value:
            if type(key) is not str or not key.isprintable():
                raise ValueError("serialized mapping keys must be printable strings")
        return {
            key: _jsonable(item, depth=depth + 1)
            for key, item in value.items()
        }
    if type(value) in (tuple, list):
        return [_jsonable(item, depth=depth + 1) for item in value]
    if type(value) is float and not math.isfinite(value):
        raise ValueError("cannot serialize non-finite float")
    if type(value) is str:
        if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
            raise ValueError("serialized string cannot contain Unicode surrogates")
        return value
    if type(value) is int:
        if value.bit_length() > 512:
            raise ValueError("serialized integer exceeds safe width")
        return value
    if value is None or type(value) in (float, bool):
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
    # Fixed temporary names could follow a planted symlink. Securely create
    # a distinct temp file in the destination directory, then replace.
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.",
            suffix=".tmp", delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(data)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _artifact_record(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.name,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def write_backtest_artifacts(run: BacktestRun, out_dir: Path) -> dict[str, object]:
    # Validate and serialize evidence before the first filesystem mutation.
    # A malformed run must not create an empty output or partial artifacts.
    if type(run) is not BacktestRun:
        raise ValueError("run must be a BacktestRun record")
    for field, mapping in (
        ("run_identity", run.run_identity),
        ("metrics", run.metrics),
    ):
        if type(mapping) not in (dict, MappingProxyType):
            raise ValueError(f"{field} must be an ordinary mapping")
    for field, records, canonical in (
        ("trades", run.trades, TradeRecord),
        ("rejections", run.rejections, RejectionRecord),
        ("equity_checkpoints", run.equity_checkpoints, EquityCheckpoint),
    ):
        if (
            type(records) not in (tuple, list)
            or any(type(item) is not canonical for item in records)
        ):
            raise ValueError(
                f"{field} must be a list or tuple of {canonical.__name__} records"
            )

    # TradeRecord also permits caller-constructed malformed values. Validate
    # identity, direction, size and chronology before evidence publication.
    for trade in run.trades:
        for field, value in (
            ("trade_id", trade.trade_id),
            ("decision_id", trade.decision_id),
        ):
            if (
                type(value) is not str or not value.strip()
                or len(value) > 512 or not value.isprintable()
            ):
                raise ValueError(f"trade {field} must be bounded printable text")
        if type(trade.symbol) is not str or trade.symbol not in SUPPORTED_SYMBOLS:
            raise ValueError("trade symbol must be an exact supported FX symbol")
        if type(trade.direction) is not Direction or trade.direction not in (
            Direction.LONG, Direction.SHORT,
        ):
            raise ValueError("trade direction must be LONG or SHORT")
        if type(trade.exit_reason) is not ExitReason:
            raise ValueError("trade exit_reason must be an ExitReason enum")
        if type(trade.units) is not int or not (0 < trade.units <= 2 ** 63 - 1):
            raise ValueError("trade units must be a supported positive integer")
        for field, value in (
            ("entry_timestamp_utc", trade.entry_timestamp_utc),
            ("exit_timestamp_utc", trade.exit_timestamp_utc),
        ):
            if (
                type(value) is not datetime or value.tzinfo is None
                or value.utcoffset() != timedelta(0)
            ):
                raise ValueError(f"trade {field} must use UTC")
        if trade.exit_timestamp_utc < trade.entry_timestamp_utc:
            raise ValueError("trade exit cannot precede entry")
        if type(trade.intrabar_ambiguous) is not bool:
            raise ValueError("trade intrabar_ambiguous must be a Boolean")
        for field in (
            "entry_reference_price", "exit_reference_price",
            "entry_price", "exit_price", "stop_price", "target_price",
            "gross_pnl_usd", "slippage_cost_usd", "commission_cost_usd",
            "financing_cost_usd", "net_pnl_usd",
            "risk_equity_before_usd", "risk_equity_after_usd",
        ):
            amount = getattr(trade, field)
            if field == "target_price" and amount is None:
                continue
            if type(amount) not in (int, float):
                raise ValueError(f"trade {field} must be finite numeric")
            try:
                if not math.isfinite(amount):
                    raise ValueError(f"trade {field} must be finite numeric")
            except OverflowError as exc:
                raise ValueError(f"trade {field} must be finite numeric") from exc
            if field.endswith("_price") and amount <= 0:
                raise ValueError(f"trade {field} must be positive")
            if field in ("slippage_cost_usd", "commission_cost_usd") and amount < 0:
                raise ValueError(f"trade {field} must be non-negative")

    # RejectionRecord has no dataclass constructor validation. Recheck each
    # evidence field before sorting or writing anything.
    for rejection in run.rejections:
        for field, value, limit in (
            ("decision_id", rejection.decision_id, 512),
            ("explanation", rejection.explanation, 4096),
        ):
            if (
                type(value) is not str or not value.strip()
                or len(value) > limit or not value.isprintable()
            ):
                raise ValueError(f"rejection {field} must be bounded printable text")
        if type(rejection.symbol) is not str or rejection.symbol not in SUPPORTED_SYMBOLS:
            raise ValueError("rejection symbol must be an exact supported FX symbol")
        if type(rejection.code) is not RejectionCode:
            raise ValueError("rejection code must be a RejectionCode enum")
        for field, value in (
            ("decision_timestamp_utc", rejection.decision_timestamp_utc),
            ("evaluated_timestamp_utc", rejection.evaluated_timestamp_utc),
        ):
            if (
                type(value) is not datetime or value.tzinfo is None
                or value.utcoffset() != timedelta(0)
            ):
                raise ValueError(f"rejection {field} must use UTC")
        if rejection.evaluated_timestamp_utc < rejection.decision_timestamp_utc:
            raise ValueError("rejection evaluation cannot precede decision")

    # Equity checkpoints are constructor-unvalidated records. Preserve
    # chronological realized-risk evidence rather than serializing aliases.
    previous_checkpoint_timestamp: datetime | None = None
    for checkpoint in run.equity_checkpoints:
        timestamp = checkpoint.timestamp_utc
        if (
            type(timestamp) is not datetime or timestamp.tzinfo is None
            or timestamp.utcoffset() != timedelta(0)
        ):
            raise ValueError("equity checkpoint timestamp must use UTC")
        if (
            previous_checkpoint_timestamp is not None
            and timestamp < previous_checkpoint_timestamp
        ):
            raise ValueError("equity checkpoints must be chronological")
        previous_checkpoint_timestamp = timestamp
        equity = checkpoint.realized_risk_equity_usd
        if type(equity) not in (int, float):
            raise ValueError("equity checkpoint must be finite numeric")
        try:
            if not math.isfinite(equity):
                raise ValueError("equity checkpoint must be finite numeric")
        except OverflowError as exc:
            raise ValueError("equity checkpoint must be finite numeric") from exc

    # One input decision can contribute at most one filled trade OR one
    # rejection. Reject duplicated/inconsistent synthetic evidence.
    trade_ids = [trade.trade_id for trade in run.trades]
    trade_decision_ids = [trade.decision_id for trade in run.trades]
    rejection_decision_ids = [record.decision_id for record in run.rejections]
    if len(set(trade_ids)) != len(trade_ids):
        raise ValueError("duplicate trade_id in artifact evidence")
    if len(set(trade_decision_ids)) != len(trade_decision_ids):
        raise ValueError("duplicate trade decision_id in artifact evidence")
    if len(set(rejection_decision_ids)) != len(rejection_decision_ids):
        raise ValueError("duplicate rejection decision_id in artifact evidence")
    if set(trade_decision_ids).intersection(rejection_decision_ids):
        raise ValueError("decision cannot have both trade and rejection evidence")

    # A supplied metric summary must not contradict the published trade
    # ledger. Recompute the two primary count/economic totals before I/O.
    expected_net_pnl = sum(trade.net_pnl_usd for trade in run.trades)
    try:
        if not math.isfinite(expected_net_pnl):
            raise ValueError("trade net PnL aggregate must remain finite")
    except OverflowError as exc:
        raise ValueError("trade net PnL aggregate must remain finite") from exc
    if "trade_count" in run.metrics:
        count = run.metrics["trade_count"]
        if type(count) is not int or count != len(run.trades):
            raise ValueError("metric trade_count conflicts with trade ledger")
    if "net_pnl_usd" in run.metrics:
        claimed = run.metrics["net_pnl_usd"]
        if type(claimed) not in (int, float):
            raise ValueError("metric net_pnl_usd must be finite numeric")
        try:
            if not math.isfinite(claimed):
                raise ValueError("metric net_pnl_usd is non-finite")
            if claimed != expected_net_pnl:
                raise ValueError("metric net_pnl_usd conflicts with trade ledger")
        except OverflowError as exc:
            raise ValueError("metric net_pnl_usd must be finite numeric") from exc

    # Reconcile optional explicit cost metrics to the same trades being
    # written; a self-consistent hash cannot rescue forged cost totals.
    summed_costs = {
        name: sum(getattr(trade, name) for trade in run.trades)
        for name in (
            "slippage_cost_usd", "commission_cost_usd", "financing_cost_usd",
        )
    }
    # Validate subtotal conversion before mixed int/float addition: a
    # finite individual integer can yield a non-float-convertible sum.
    for name, subtotal in summed_costs.items():
        try:
            if not math.isfinite(subtotal):
                raise ValueError(f"trade {name} aggregate must remain finite")
        except OverflowError as exc:
            raise ValueError(f"trade {name} aggregate must remain finite") from exc
    try:
        summed_costs["total_explicit_cost_usd"] = (
            summed_costs["slippage_cost_usd"]
            + summed_costs["commission_cost_usd"]
            + summed_costs["financing_cost_usd"]
        )
    except OverflowError as exc:
        raise ValueError(
            "trade total_explicit_cost_usd aggregate must remain finite"
        ) from exc
    for name, expected in summed_costs.items():
        try:
            if not math.isfinite(expected):
                raise ValueError(f"trade {name} aggregate must remain finite")
        except OverflowError as exc:
            raise ValueError(f"trade {name} aggregate must remain finite") from exc
        if name not in run.metrics:
            continue
        claimed = run.metrics[name]
        if type(claimed) not in (int, float):
            raise ValueError(f"metric {name} must be finite numeric")
        try:
            if not math.isfinite(claimed) or claimed != expected:
                raise ValueError(f"metric {name} conflicts with trade ledger")
        except OverflowError as exc:
            raise ValueError(f"metric {name} must be finite numeric") from exc

    # Recompute core win/loss economics in the same deterministic exit
    # order used for the published trades JSONL (and streak calculations).
    ordered_trades = sorted(
        run.trades, key=lambda item: (item.exit_timestamp_utc, item.trade_id)
    )
    pnls = [trade.net_pnl_usd for trade in ordered_trades]
    profit_usd = sum(value for value in pnls if value > 0)
    loss_usd = -sum(value for value in pnls if value < 0)
    for name, expected in (
        ("gross_profit_usd", profit_usd),
        ("gross_loss_usd", loss_usd),
        ("profit_factor", profit_usd / loss_usd if loss_usd > 0 else None),
    ):
        if expected is not None:
            try:
                if not math.isfinite(expected):
                    raise ValueError(f"trade {name} aggregate must remain finite")
            except OverflowError as exc:
                raise ValueError(f"trade {name} aggregate must remain finite") from exc
        if name not in run.metrics:
            continue
        claimed = run.metrics[name]
        if expected is None:
            if claimed is not None:
                raise ValueError(f"metric {name} conflicts with trade ledger")
            continue
        if type(claimed) not in (int, float):
            raise ValueError(f"metric {name} must be finite numeric")
        try:
            if not math.isfinite(claimed) or claimed != expected:
                raise ValueError(f"metric {name} conflicts with trade ledger")
        except OverflowError as exc:
            raise ValueError(f"metric {name} must be finite numeric") from exc

    # These optional summary fields are deterministic functions of the
    # published trade sequence, not independent editable performance claims.
    winners = [value for value in pnls if value > 0]
    losers = [value for value in pnls if value < 0]
    trade_count = len(pnls)
    expected_distribution = {
        "win_rate": len(winners) / trade_count if trade_count else None,
        "average_win_usd": sum(winners) / len(winners) if winners else None,
        "average_loss_usd": sum(losers) / len(losers) if losers else None,
        "expectancy_usd": expected_net_pnl / trade_count if trade_count else None,
        "longest_winning_streak": _longest_streak(pnls, winning=True),
        "longest_losing_streak": _longest_streak(pnls, winning=False),
    }
    for name, expected in expected_distribution.items():
        if name not in run.metrics:
            continue
        claimed = run.metrics[name]
        if expected is None:
            if claimed is not None:
                raise ValueError(f"metric {name} conflicts with trade ledger")
        elif type(expected) is int:
            if type(claimed) is not int or claimed != expected:
                raise ValueError(f"metric {name} conflicts with trade ledger")
        else:
            if type(claimed) not in (int, float):
                raise ValueError(f"metric {name} must be finite numeric")
            try:
                if not math.isfinite(claimed) or claimed != expected:
                    raise ValueError(f"metric {name} conflicts with trade ledger")
            except OverflowError as exc:
                raise ValueError(f"metric {name} must be finite numeric") from exc

    summary = {
        "protocol": "fmp-phase3-backtest-run-v1",
        "run_identity": run.run_identity,
        "trade_count": len(run.trades),
        "rejection_count": len(run.rejections),
        "equity_checkpoint_count": len(run.equity_checkpoints),
        "equity_checkpoints": run.equity_checkpoints,
    }
    trades = ordered_trades
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
    out_dir = Path(out_dir)
    # Refuse an existing output-directory symlink rather than following it
    # while writing apparently local artifact files.
    if out_dir.is_symlink():
        raise ValueError("artifact output directory must not be a symlink")
    out_dir.mkdir(parents=True, exist_ok=True)
    # Invalidate an old manifest *before* modifying any payload files.
    # If a later file replacement fails, mixed-generation artifacts must
    # not retain a manifest that falsely appears to certify the directory.
    (out_dir / "manifest.json").unlink(missing_ok=True)
    for name, data in payloads.items():
        _atomic_write(out_dir / name, data)

    artifacts = [_artifact_record(out_dir / name) for name in sorted(payloads)]
    manifest: dict[str, object] = {
        "protocol": ARTIFACT_PROTOCOL,
        "artifacts": artifacts,
    }
    _atomic_write(out_dir / "manifest.json", _stable_json_bytes(manifest))
    return manifest


def _manifest_unique_object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("artifact manifest contains duplicate JSON key")
        result[name] = value
    return result


def _open_regular_artifact(path: Path, *, root_fd: int):
    """Open a no-follow regular file without blocking on a FIFO leaf."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    nonblock = getattr(os, "O_NONBLOCK", None)
    if type(nofollow) is not int or type(nonblock) is not int:
        raise ValueError("artifact verification requires no-follow file opening")
    try:
        fd = os.open(
            path.name, os.O_RDONLY | nofollow | nonblock,
            dir_fd=root_fd,
        )
    except OSError as exc:
        raise ValueError("artifact evidence must be a regular file") from exc
    try:
        file_state = os.fstat(fd)
        if not stat.S_ISREG(file_state.st_mode):
            raise ValueError("artifact evidence must be a regular file")
        if file_state.st_nlink != 1:
            raise ValueError("artifact evidence must not be hardlinked")
        return os.fdopen(fd, "rb")
    except BaseException:
        os.close(fd)
        raise


def verify_backtest_artifacts(out_dir: Path) -> dict[str, object]:
    """Verify local artifact bytes against an expected-shape Phase3 manifest.

    This checks internal consistency only, not input-data provenance or
    trading economics. No paths are derived from untrusted manifest names.
    """
    root = Path(out_dir)
    # Reject obvious linked ancestors rather than trusting an output leaf
    # whose apparent parent resolves to a different evidence directory.
    for component in (root.absolute(), *root.absolute().parents):
        if component.is_symlink():
            raise ValueError("artifact root cannot contain symlink ancestors")
    if root.is_symlink() or not root.is_dir():
        raise ValueError("artifact root must be a direct directory")
    directory_flag = getattr(os, "O_DIRECTORY", None)
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if type(directory_flag) is not int or type(nofollow) is not int:
        raise ValueError("artifact verification requires no-follow directory opening")
    try:
        root_fd = os.open(root, os.O_RDONLY | directory_flag | nofollow)
    except OSError as exc:
        raise ValueError("artifact root must be a direct directory") from exc
    try:
        if not stat.S_ISDIR(os.fstat(root_fd).st_mode):
            raise ValueError("artifact root must be a direct directory")
        return _verify_artifacts_in_root(root, root_fd)
    finally:
        os.close(root_fd)


def _verify_artifacts_in_root(root: Path, root_fd: int) -> dict[str, object]:
    manifest_file = root / "manifest.json"
    if manifest_file.is_symlink() or not manifest_file.is_file():
        raise ValueError("artifact manifest must be a regular file")
    with _open_regular_artifact(manifest_file, root_fd=root_fd) as handle:
        if os.fstat(handle.fileno()).st_size > 262_144:
            raise ValueError("artifact manifest exceeds size limit")
        raw_manifest = handle.read(262_145)
    if len(raw_manifest) > 262_144:
        raise ValueError("artifact manifest exceeds size limit")
    try:
        manifest = json.loads(
            raw_manifest, object_pairs_hook=_manifest_unique_object_pairs,
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        # Deliberately retain the duplicate-key ValueError from the
        # object_pairs_hook, rather than hiding a precise tamper reason.
        raise ValueError("artifact manifest must be valid JSON") from exc
    if (
        type(manifest) is not dict
        or set(manifest) != {"protocol", "artifacts"}
        or manifest["protocol"] != ARTIFACT_PROTOCOL
    ):
        raise ValueError("artifact manifest protocol or shape mismatch")
    entries = manifest["artifacts"]
    expected_names = {
        "summary.json", "trades.jsonl", "rejections.jsonl", "metrics.json"
    }
    if type(entries) is not list or len(entries) != len(expected_names):
        raise ValueError("artifact manifest must list four evidence files")
    seen: set[str] = set()
    for entry in entries:
        if type(entry) is not dict or set(entry) != {
            "path", "size_bytes", "sha256"
        }:
            raise ValueError("artifact entry has an invalid shape")
        name = entry["path"]
        if type(name) is not str or name not in expected_names or name in seen:
            raise ValueError("artifact entry path is duplicate or unsupported")
        seen.add(name)
        size = entry["size_bytes"]
        digest = entry["sha256"]
        if type(size) is not int or size < 0:
            raise ValueError("artifact entry size must be a nonnegative integer")
        if (
            type(digest) is not str
            or len(digest) != 64
            or any(ch not in "0123456789abcdef" for ch in digest)
        ):
            raise ValueError("artifact entry digest must be lowercase SHA256")
    if seen != expected_names:
        raise ValueError("artifact evidence filename set mismatch")
    if [entry["path"] for entry in entries] != sorted(expected_names):
        raise ValueError("artifact evidence paths must use canonical order")

    # Admit the *entire* manifest schema and ordered path set before any
    # payload open. A forged path must never cause a misleading hash check.
    for entry in entries:
        name = entry["path"]
        size = entry["size_bytes"]
        digest = entry["sha256"]
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("artifact evidence must be a regular file")
        observed_size = 0
        with _open_regular_artifact(path, root_fd=root_fd) as handle:
            # Inspect the pinned regular-file descriptor before consuming
            # potentially expensive evidence payload bytes.
            before = os.fstat(handle.fileno())
            if before.st_size != size:
                raise ValueError("artifact evidence size or SHA256 mismatch")
            # No digest allocation or payload reads before the size preflight.
            observed_hash = hashlib.sha256()
            while block := handle.read(1024 * 1024):
                observed_size += len(block)
                if observed_size > size:
                    raise ValueError("artifact evidence size or SHA256 mismatch")
                observed_hash.update(block)
            after = os.fstat(handle.fileno())
            if (
                before.st_dev != after.st_dev
                or before.st_ino != after.st_ino
                or before.st_size != after.st_size
                or before.st_mtime_ns != after.st_mtime_ns
                or before.st_ctime_ns != after.st_ctime_ns
            ):
                raise ValueError("artifact evidence changed during verification")
        if observed_size != size or observed_hash.hexdigest() != digest:
            raise ValueError("artifact evidence size or SHA256 mismatch")
    return manifest


def _audit_json_unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("artifact report contains duplicate JSON key")
        result[name] = value
    return result


def _audit_validate_json_tree(value: object, *, depth: int = 0) -> None:
    # Match deterministic writer depth and Unicode/key constraints, including
    # ignored optional metric fields and nested provenance metadata.
    if depth > 64:
        raise ValueError("artifact report exceeds JSON nesting limit")
    if type(value) is dict:
        for key, member in value.items():
            if (
                type(key) is not str or not key.isprintable()
                or any(0xD800 <= ord(ch) <= 0xDFFF for ch in key)
            ):
                raise ValueError("artifact report JSON key must be printable Unicode")
            _audit_validate_json_tree(member, depth=depth + 1)
    elif type(value) is list:
        for member in value:
            _audit_validate_json_tree(member, depth=depth + 1)
    elif type(value) is str:
        if any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
            raise ValueError("artifact report JSON string cannot contain Unicode surrogates")


def _audit_decision_config_tree(
    value: object, *, depth: int = 0, budget: list[int] | None = None,
) -> None:
    """Match engine-frozen decision metadata limits without trusting its SHA."""
    if budget is None:
        budget = [8192]
    budget[0] -= 1
    if budget[0] < 0:
        raise ValueError("artifact report decision_config exceeds node budget")
    if depth > 32:
        raise ValueError("artifact report decision_config exceeds nesting depth")
    if type(value) is dict:
        for key, child in value.items():
            if (
                type(key) is not str or not key
                or any(ord(ch) < 32 or ord(ch) == 127 or
                       0xD800 <= ord(ch) <= 0xDFFF for ch in key)
            ):
                raise ValueError(
                    "artifact report decision_config keys must be printable nonempty strings"
                )
            _audit_decision_config_tree(
                child, depth=depth + 1, budget=budget,
            )
    elif type(value) is list:
        for child in value:
            _audit_decision_config_tree(
                child, depth=depth + 1, budget=budget,
            )
    elif type(value) is str:
        if any(
            ord(ch) < 32 or ord(ch) == 127 or
            0xD800 <= ord(ch) <= 0xDFFF for ch in value
        ):
            raise ValueError(
                "artifact report decision_config strings must be printable"
            )
    elif value is None or type(value) is bool:
        return
    elif type(value) is int:
        if value.bit_length() > 512:
            raise ValueError("artifact report decision_config integer exceeds safe width")
    elif type(value) is float:
        if not math.isfinite(value):
            raise ValueError("artifact report decision_config float must be finite")
    else:
        raise ValueError("artifact report decision_config has unsupported value")


def _audit_load_json(payload: bytes) -> object:
    def refuse_nonfinite(value: str) -> object:
        raise ValueError("artifact report contains non-finite JSON constant")

    def require_finite_number(value: str) -> float:
        # Python's JSON parser accepts an enormous exponent as float('inf')
        # even when allow_nan would reject a writer-created non-finite value.
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("artifact report contains non-finite numeric value")
        return number

    def require_bounded_integer(value: str) -> int:
        # Avoid constructing unbounded integers before checking the
        # serializer's 512-bit integer-width contract.
        if len(value.lstrip("-")) > 156:
            raise ValueError("artifact report integer exceeds safe width")
        number = int(value)
        if number.bit_length() > 512:
            raise ValueError("artifact report integer exceeds safe width")
        return number

    try:
        document = json.loads(
            payload, object_pairs_hook=_audit_json_unique_pairs,
            parse_constant=refuse_nonfinite,
            parse_float=require_finite_number,
            parse_int=require_bounded_integer,
        )
        _audit_validate_json_tree(document)
        return document
    except RecursionError as exc:
        raise ValueError("artifact report exceeds JSON parser nesting limit") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("artifact report must contain valid JSON") from exc


def _audit_parse_utc_timestamp(value: object, label: str) -> datetime:
    if type(value) is not str or not value.endswith("Z"):
        raise ValueError(f"artifact report {label} must use UTC")
    try:
        stamp = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"artifact report {label} invalid UTC timestamp") from exc
    if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
        raise ValueError(f"artifact report {label} must use UTC")
    # The writer publishes only ISO UTC strings with T separator,
    # explicit seconds and canonical microsecond precision.
    if stamp.isoformat().replace("+00:00", "Z") != value:
        raise ValueError(f"artifact report {label} must be canonical UTC")
    return stamp


def audit_backtest_artifact_structure(out_dir: Path) -> dict[str, int]:
    """Independently inspect cross-file counts after digest verification.

    This is a non-atomic local consistency audit, not source authentication.
    """
    root = Path(out_dir)
    manifest = verify_backtest_artifacts(root)
    expected_records = {
        entry["path"]: entry for entry in manifest["artifacts"]
    }
    directory_flag = getattr(os, "O_DIRECTORY", None)
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if type(directory_flag) is not int or type(nofollow) is not int:
        raise ValueError("artifact audit requires no-follow directory opening")
    try:
        root_fd = os.open(root, os.O_RDONLY | directory_flag | nofollow)
    except OSError as exc:
        raise ValueError("artifact audit requires a direct directory") from exc
    try:
        small_json_payloads: dict[str, bytes] = {}

        def read_small_json(name: str) -> object:
            with _open_regular_artifact(root / name, root_fd=root_fd) as handle:
                data = handle.read(1024 * 1024 + 1)
            if len(data) > 1024 * 1024:
                raise ValueError("artifact report JSON exceeds audit size limit")
            if (
                len(data) != expected_records[name]["size_bytes"]
                or hashlib.sha256(data).hexdigest() != expected_records[name]["sha256"]
            ):
                raise ValueError("artifact report changed since verification")
            small_json_payloads[name] = data
            return _audit_load_json(data)

        summary = read_small_json("summary.json")
        metrics = read_small_json("metrics.json")
        if type(summary) is not dict or type(metrics) is not dict:
            raise ValueError("artifact report summary and metrics must be objects")
        if set(summary) != {
            "protocol", "run_identity", "trade_count", "rejection_count",
            "equity_checkpoint_count", "equity_checkpoints",
        } or summary["protocol"] != "fmp-phase3-backtest-run-v1":
            raise ValueError("artifact report summary protocol or fields mismatch")
        if type(summary["run_identity"]) is not dict:
            raise ValueError("artifact report run identity must be an object")
        # The real engine serializes the requested experiment interval as
        # paired canonical UTC datetimes. Treat partially supplied or
        # backdated source-window claims as malformed evidence, while still
        # admitting synthetic envelopes that omit both optional fields.
        source_identity = summary["run_identity"]
        # Validate the source equity domain before any ledger chaining or
        # close-to-checkpoint comparisons. Otherwise a malformed Boolean,
        # zero or negative identity is mislabeled as a continuity failure.
        if "starting_equity_usd" in source_identity:
            identity = source_identity
            starting_equity = identity["starting_equity_usd"]
            if type(starting_equity) not in (int, float):
                raise ValueError(
                    "artifact report starting equity must be finite positive"
                )
            try:
                valid_start = math.isfinite(starting_equity) and starting_equity > 0
            except OverflowError:
                valid_start = False
            if not valid_start:
                raise ValueError(
                    "artifact report starting equity must be finite positive"
                )
        window_fields = ("requested_start_utc", "requested_end_utc")
        present = [field in source_identity for field in window_fields]
        if any(present):
            if not all(present):
                raise ValueError(
                    "artifact report requested window must include both UTC endpoints"
                )
            requested_start = _audit_parse_utc_timestamp(
                source_identity["requested_start_utc"], "requested start"
            )
            requested_end = _audit_parse_utc_timestamp(
                source_identity["requested_end_utc"], "requested end"
            )
            if requested_end < requested_start:
                raise ValueError(
                    "artifact report requested end precedes requested start"
                )

        # Mirror source BacktestConfig's scalar contract without pretending
        # that self-hashed run identity proves external data provenance.
        for label in (
            "backtest_engine_version", "code_commit",
            "processed_data_manifest_id", "schema_version", "timeframe",
        ):
            if label not in source_identity:
                continue
            scalar = source_identity[label]
            if (
                type(scalar) is not str or not scalar.strip()
                or not scalar.isprintable()
            ):
                raise ValueError(
                    f"artifact report run identity {label} must be printable nonempty text"
                )
        if "slippage_pips" in source_identity:
            slippage = source_identity["slippage_pips"]
            if type(slippage) not in (int, float):
                raise ValueError(
                    "artifact report run identity slippage_pips must be finite nonnegative"
                )
            try:
                slippage_valid = math.isfinite(slippage) and slippage >= 0
            except OverflowError:
                slippage_valid = False
            if not slippage_valid:
                raise ValueError(
                    "artifact report run identity slippage_pips must be finite nonnegative"
                )
        if "execution_timing_mode" in source_identity:
            mode = source_identity["execution_timing_mode"]
            if (
                type(mode) is not str
                or mode not in ("NEXT_SUPPLIED_BAR", "DECLARED_EARLIEST_BAR")
            ):
                raise ValueError(
                    "artifact report run identity execution_timing_mode is unsupported"
                )
        # The engine's scheduled-exit run identity is a sorted list of
        # canonical ScheduledExit descriptors, not arbitrary JSON metadata.
        scheduled_exit_by_decision: dict[str, tuple[str, datetime]] = {}
        if "scheduled_exits" in source_identity:
            scheduled = source_identity["scheduled_exits"]
            if type(scheduled) is not list or not scheduled:
                raise ValueError(
                    "artifact report scheduled exits must be a nonempty list"
                )
            previous_exit: tuple[datetime, str, str] | None = None
            scheduled_decisions: set[str] = set()
            for item in scheduled:
                if type(item) is not dict or set(item) != {
                    "decision_id", "symbol", "timestamp_utc",
                }:
                    raise ValueError(
                        "artifact report scheduled exit fields mismatch"
                    )
                decision_id = item["decision_id"]
                if (
                    type(decision_id) is not str or not decision_id.strip()
                    or len(decision_id) > 512 or not decision_id.isprintable()
                ):
                    raise ValueError(
                        "artifact report scheduled exit decision_id must be bounded printable text"
                    )
                symbol = item["symbol"]
                if type(symbol) is not str or symbol not in SUPPORTED_SYMBOLS:
                    raise ValueError(
                        "artifact report scheduled exit symbol is unsupported"
                    )
                timestamp = _audit_parse_utc_timestamp(
                    item["timestamp_utc"], "scheduled exit"
                )
                ordering = (timestamp, symbol, decision_id)
                if previous_exit is not None and ordering < previous_exit:
                    raise ValueError(
                        "artifact report scheduled exits are not in canonical order"
                    )
                if decision_id in scheduled_decisions:
                    raise ValueError(
                        "artifact report duplicate scheduled exit decision_id"
                    )
                previous_exit = ordering
                scheduled_decisions.add(decision_id)
                scheduled_exit_by_decision[decision_id] = (
                    symbol, timestamp,
                )
        if "risk_config" in source_identity:
            # The source RiskConfig.to_config() publishes exactly four
            # positive bounded fractions in a monotone risk hierarchy.
            risk = source_identity["risk_config"]
            risk_names = (
                "default_risk_fraction", "max_risk_fraction",
                "max_simultaneous_risk_fraction", "daily_loss_halt_fraction",
            )
            if type(risk) is not dict or set(risk) != set(risk_names):
                raise ValueError(
                    "artifact report risk_config fields mismatch"
                )
            for key in risk_names:
                value = risk[key]
                if type(value) not in (int, float):
                    raise ValueError(
                        f"artifact report risk_config {key} must be positive bounded numeric"
                    )
                try:
                    valid_fraction = (
                        math.isfinite(value) and 0 < value <= 1
                    )
                except OverflowError:
                    valid_fraction = False
                if not valid_fraction:
                    raise ValueError(
                        f"artifact report risk_config {key} must be positive bounded numeric"
                    )
            if (
                risk["default_risk_fraction"] > risk["max_risk_fraction"]
                or risk["max_risk_fraction"]
                > risk["max_simultaneous_risk_fraction"]
            ):
                raise ValueError(
                    "artifact report risk_config fractions violate risk hierarchy"
                )
        # The built-in commission/financing configurations have strict
        # writer source contracts. A valid custom model's to_config() can
        # publish a distinct model, so only validate recognized built-ins.
        for config_key in ("commission_model", "financing_model"):
            if config_key not in source_identity:
                continue
            model_config = source_identity[config_key]
            if type(model_config) is not dict:
                raise ValueError(
                    f"artifact report {config_key} must be an object"
                )
            model = model_config.get("model")
            if model in ("zero_commission", "zero_financing"):
                expected_config_key = (
                    "commission_model" if model == "zero_commission"
                    else "financing_model"
                )
                if config_key != expected_config_key:
                    raise ValueError(
                        f"artifact report {config_key} model type is incompatible"
                    )
                if set(model_config) != {"model"}:
                    raise ValueError(
                        f"artifact report {config_key} zero model fields mismatch"
                    )
            elif model == "fixed_per_million_per_side":
                if config_key != "commission_model" or set(model_config) != {
                    "model", "usd_per_million_per_side",
                }:
                    raise ValueError(
                        "artifact report fixed commission fields mismatch"
                    )
                rate = model_config["usd_per_million_per_side"]
                if type(rate) not in (int, float):
                    raise ValueError(
                        "artifact report fixed commission rate must be finite nonnegative"
                    )
                try:
                    valid_rate = math.isfinite(rate) and rate >= 0
                except OverflowError:
                    valid_rate = False
                if not valid_rate:
                    raise ValueError(
                        "artifact report fixed commission rate must be finite nonnegative"
                    )
        if "decision_config" in source_identity:
            config = source_identity["decision_config"]
            if type(config) is not dict:
                raise ValueError(
                    "artifact report decision_config must be an object"
                )
            _audit_decision_config_tree(config)
            try:
                config_size = len(json.dumps(
                    config, sort_keys=True, separators=(",", ":"),
                    allow_nan=False,
                ).encode("utf-8"))
            except (OverflowError, TypeError, ValueError, RecursionError) as exc:
                raise ValueError(
                    "artifact report decision_config cannot serialize safely"
                ) from exc
            if config_size > 65536:
                raise ValueError(
                    "artifact report decision_config exceeds 64 KiB"
                )
        counts: dict[str, int] = {}
        for field in ("trade_count", "rejection_count", "equity_checkpoint_count"):
            count = summary.get(field)
            if type(count) is not int or count < 0:
                raise ValueError(f"artifact report {field} must be a nonnegative integer")
            counts[field] = count
        checkpoints = summary.get("equity_checkpoints")
        if type(checkpoints) is not list or len(checkpoints) != counts["equity_checkpoint_count"]:
            raise ValueError("artifact report equity checkpoint count conflicts with summary")
        previous_checkpoint: datetime | None = None
        for checkpoint in checkpoints:
            if type(checkpoint) is not dict or set(checkpoint) != {
                "timestamp_utc", "realized_risk_equity_usd",
            }:
                raise ValueError("artifact report equity checkpoint fields mismatch")
            instant = _audit_parse_utc_timestamp(
                checkpoint["timestamp_utc"], "equity checkpoint"
            )
            if previous_checkpoint is not None and instant < previous_checkpoint:
                raise ValueError("artifact report equity checkpoints must be chronological")
            previous_checkpoint = instant
            value = checkpoint["realized_risk_equity_usd"]
            if type(value) not in (int, float):
                raise ValueError("artifact report equity checkpoint must be finite numeric")
            try:
                if not math.isfinite(value):
                    raise ValueError("artifact report equity checkpoint must be finite numeric")
            except OverflowError as exc:
                raise ValueError("artifact report equity checkpoint must be finite numeric") from exc

        record_fields = {
            "trades.jsonl": {item.name for item in fields(TradeRecord)},
            "rejections.jsonl": {item.name for item in fields(RejectionRecord)},
        }
        # Economic totals must agree with the stored ledger, not just
        # individual row arithmetic and a self-rehashed manifest.
        ledger_profit_usd: int | float = 0
        ledger_loss_usd: int | float = 0
        ledger_totals: dict[str, int | float] = {
            name: 0 for name in (
                "net_pnl_usd", "slippage_cost_usd",
                "commission_cost_usd", "financing_cost_usd",
            )
        }
        sorted_trade_pnls: list[int | float] = []
        # Capture the engine's realized equity transitions in canonical
        # close order. Validate cross-record continuity after row validation.
        trade_equity_transitions: list[tuple[int | float, int | float]] = []
        trade_exit_instants: list[datetime] = []
        earliest_trade_entry: datetime | None = None
        seen_trade_ids: set[str] = set()
        seen_trade_decisions: set[str] = set()
        seen_rejection_decisions: set[str] = set()
        observed_decision_symbols: dict[str, str] = {}
        previous_trade_order: tuple[datetime, str] | None = None
        previous_rejection_order: tuple[datetime, str] | None = None
        for name, field in (("trades.jsonl", "trade_count"),
                            ("rejections.jsonl", "rejection_count")):
            observed = 0
            observed_size = 0
            observed_hash = hashlib.sha256()
            noncanonical_row_seen = False
            with _open_regular_artifact(root / name, root_fd=root_fd) as handle:
                while line := handle.readline(1024 * 1024 + 1):
                    if len(line) > 1024 * 1024:
                        raise ValueError("artifact report JSONL line exceeds audit size limit")
                    observed_size += len(line)
                    observed_hash.update(line)
                    record = _audit_load_json(line)
                    if type(record) is not dict:
                        raise ValueError("artifact report JSONL record must be an object")
                    if set(record) != record_fields[name]:
                        raise ValueError("artifact report JSONL canonical fields mismatch")
                    if name == "trades.jsonl":
                        entry_stamp = _audit_parse_utc_timestamp(
                            record["entry_timestamp_utc"], "trade entry timestamp"
                        )
                        exit_stamp = _audit_parse_utc_timestamp(
                            record["exit_timestamp_utc"], "trade exit timestamp"
                        )
                        if exit_stamp < entry_stamp:
                            raise ValueError("artifact report trade exit precedes entry")
                        if (
                            earliest_trade_entry is None
                            or entry_stamp < earliest_trade_entry
                        ):
                            earliest_trade_entry = entry_stamp
                    else:
                        decision_stamp = _audit_parse_utc_timestamp(
                            record["decision_timestamp_utc"], "rejection decision timestamp"
                        )
                        evaluated_stamp = _audit_parse_utc_timestamp(
                            record["evaluated_timestamp_utc"], "rejection evaluation timestamp"
                        )
                        if evaluated_stamp < decision_stamp:
                            raise ValueError("artifact report rejection evaluation precedes decision")
                    decision = record["decision_id"]
                    if (
                        type(decision) is not str or not decision.strip()
                        or len(decision) > 512 or not decision.isprintable()
                    ):
                        raise ValueError(
                            "artifact report decision_id must be bounded printable text"
                        )
                    if name == "rejections.jsonl":
                        if (
                            type(record["symbol"]) is not str
                            or record["symbol"] not in SUPPORTED_SYMBOLS
                        ):
                            raise ValueError("artifact report rejection symbol is unsupported")
                        if (
                            type(record["code"]) is not str
                            or record["code"] not in {
                                item.value for item in RejectionCode
                            }
                        ):
                            raise ValueError("artifact report rejection code is unsupported")
                        explanation = record["explanation"]
                        if (
                            type(explanation) is not str
                            or not explanation.strip()
                            or len(explanation) > 4096
                            or not explanation.isprintable()
                        ):
                            raise ValueError(
                                "artifact report rejection explanation must be bounded printable text"
                            )
                    if name == "trades.jsonl":
                        trade_id = record["trade_id"]
                        if (
                            type(trade_id) is not str or not trade_id.strip()
                            or len(trade_id) > 512 or not trade_id.isprintable()
                        ):
                            raise ValueError(
                                "artifact report trade_id must be bounded printable text"
                            )
                        if trade_id in seen_trade_ids:
                            raise ValueError("artifact report duplicate trade_id")
                        if (
                            source_identity.get("backtest_engine_version")
                            == BACKTEST_ENGINE_VERSION
                            and trade_id != decision
                        ):
                            raise ValueError(
                                "artifact report source engine trade_id conflicts with decision_id"
                            )
                        if decision in seen_trade_decisions:
                            raise ValueError("artifact report duplicate trade decision_id")
                        # Enforce source-defined trade domains as well as
                        # canonical member names before accepting economics.
                        if (
                            type(record["symbol"]) is not str
                            or record["symbol"] not in SUPPORTED_SYMBOLS
                        ):
                            raise ValueError("artifact report trade symbol is unsupported")
                        if (
                            type(record["direction"]) is not str
                            or record["direction"] not in (
                                Direction.LONG.value, Direction.SHORT.value,
                            )
                        ):
                            raise ValueError("artifact report trade direction is unsupported")
                        units = record["units"]
                        if type(units) is not int or not (0 < units <= 2 ** 63 - 1):
                            raise ValueError("artifact report trade units must be positive")
                        if (
                            type(record["exit_reason"]) is not str
                            or record["exit_reason"] not in {
                                item.value for item in ExitReason
                            }
                        ):
                            raise ValueError("artifact report trade exit reason is unsupported")
                        if type(record["intrabar_ambiguous"]) is not bool:
                            raise ValueError("artifact report trade ambiguity must be Boolean")
                        # TIME_EXIT is produced only by a matching
                        # ScheduledExit for the same decision and symbol,
                        # executed at its declared timestamp. Scheduled
                        # exits for decisions rejected or stopped earlier
                        # need not produce a TIME_EXIT record.
                        if (
                            source_identity.get("backtest_engine_version")
                            == BACKTEST_ENGINE_VERSION
                            and record["exit_reason"] == ExitReason.TIME_EXIT.value
                            and scheduled_exit_by_decision.get(decision)
                            != (record["symbol"], exit_stamp)
                        ):
                            raise ValueError(
                                "artifact report source time exit conflicts with scheduled exit identity"
                            )
                        for price_field in (
                            "entry_reference_price", "exit_reference_price",
                            "entry_price", "exit_price", "stop_price", "target_price",
                        ):
                            price = record[price_field]
                            if price_field == "target_price" and price is None:
                                continue
                            if type(price) not in (int, float):
                                raise ValueError(
                                    f"artifact report trade {price_field} must be finite positive numeric"
                                )
                            try:
                                valid_price = math.isfinite(price) and price > 0
                            except OverflowError:
                                valid_price = False
                            if not valid_price:
                                raise ValueError(
                                    f"artifact report trade {price_field} must be finite positive numeric"
                                )
                        # Phase3 execution uses adverse-only slippage:
                        # buys may fill no lower than their ask reference;
                        # sells may fill no higher than their bid reference.
                        # This applies independently to entry and close,
                        # reversing sides for SHORT trades.
                        direction = record["direction"]
                        entry_ref = record["entry_reference_price"]
                        entry_fill = record["entry_price"]
                        exit_ref = record["exit_reference_price"]
                        exit_fill = record["exit_price"]
                        if direction == Direction.LONG.value:
                            unfavorable = (
                                entry_fill >= entry_ref and exit_fill <= exit_ref
                            )
                        else:
                            unfavorable = (
                                entry_fill <= entry_ref and exit_fill >= exit_ref
                            )
                        if not unfavorable:
                            raise ValueError(
                                "artifact report trade execution prices imply favorable slippage"
                            )
                        stop = record["stop_price"]
                        target = record["target_price"]
                        if direction == Direction.LONG.value:
                            geometry_valid = (
                                stop < entry_ref and
                                (target is None or target > entry_ref)
                            )
                        else:
                            geometry_valid = (
                                stop > entry_ref and
                                (target is None or target < entry_ref)
                            )
                        if not geometry_valid:
                            raise ValueError(
                                "artifact report trade stop/target geometry conflicts with direction"
                            )
                        # The source evaluator emits TARGET only when a
                        # declared target is touched and always records the
                        # declared target itself as its reference close.
                        # Bid/ask quote bars are not published in this
                        # artifact, so this proves internal parity only.
                        if (
                            source_identity.get("backtest_engine_version")
                            == BACKTEST_ENGINE_VERSION
                            and record["exit_reason"] == ExitReason.TARGET.value
                            and (
                                target is None
                                or exit_ref != target
                            )
                        ):
                            raise ValueError(
                                "artifact report source target exit reference conflicts with target_price"
                            )
                        # A real STOP fill is at its stop threshold or
                        # at an adverse bar-open gap through that threshold.
                        # It cannot claim a favorable reference exit past
                        # the stop, even when ambiguity is false.
                        if (
                            source_identity.get("backtest_engine_version")
                            == BACKTEST_ENGINE_VERSION
                            and record["exit_reason"] == ExitReason.STOP.value
                            and (
                                (
                                    direction == Direction.LONG.value
                                    and exit_ref > stop
                                )
                                or (
                                    direction == Direction.SHORT.value
                                    and exit_ref < stop
                                )
                            )
                        ):
                            raise ValueError(
                                "artifact report source stop exit reference improves beyond stop"
                            )
                        # The installed evaluator marks ambiguity only
                        # when stop and target are both touched in one bar.
                        # Its conservative policy exits at the stop, never
                        # at the target, time exit or end-of-data price.
                        if (
                            source_identity.get("backtest_engine_version")
                            == BACKTEST_ENGINE_VERSION
                            and record["intrabar_ambiguous"]
                            and (
                                record["exit_reason"] != ExitReason.STOP.value
                                or target is None
                                or exit_ref != stop
                            )
                        ):
                            raise ValueError(
                                "artifact report source ambiguous stop/target exit witness conflicts"
                            )
                        amounts: dict[str, int | float] = {}
                        for economic in (
                            "gross_pnl_usd", "slippage_cost_usd",
                            "commission_cost_usd", "financing_cost_usd",
                            "net_pnl_usd",
                        ):
                            amount = record[economic]
                            if type(amount) not in (int, float):
                                raise ValueError("artifact report trade economics must be finite numeric")
                            try:
                                if not math.isfinite(amount):
                                    raise ValueError("artifact report trade economics must be finite numeric")
                            except OverflowError as exc:
                                raise ValueError("artifact report trade economics must be finite numeric") from exc
                            amounts[economic] = amount
                        if (
                            amounts["slippage_cost_usd"] < 0
                            or amounts["commission_cost_usd"] < 0
                        ):
                            raise ValueError("artifact report trade execution costs must be nonnegative")
                        try:
                            expected_net = (
                                amounts["gross_pnl_usd"] - amounts["slippage_cost_usd"]
                                - amounts["commission_cost_usd"] - amounts["financing_cost_usd"]
                            )
                            reconciled = (
                                math.isfinite(expected_net)
                                and math.isclose(
                                    expected_net, amounts["net_pnl_usd"],
                                    rel_tol=1e-12, abs_tol=1e-8,
                                )
                            )
                        except OverflowError:
                            reconciled = False
                        if not reconciled:
                            raise ValueError("artifact report trade net PnL cost reconciliation mismatch")
                        # Only the installed source engine commits to this
                        # exact reference-price PnL formula. Generic reporting
                        # envelopes may use synthetic trade economics.
                        if source_identity.get(
                            "backtest_engine_version"
                        ) == BACKTEST_ENGINE_VERSION:
                            try:
                                source_gross = pnl_usd(
                                    symbol=record["symbol"],
                                    direction=Direction(record["direction"]),
                                    units=record["units"],
                                    entry_price=record["entry_reference_price"],
                                    exit_price=record["exit_reference_price"],
                                )
                                gross_matches = math.isclose(
                                    amounts["gross_pnl_usd"], source_gross,
                                    rel_tol=1e-12, abs_tol=1e-8,
                                )
                            except (ValueError, OverflowError) as exc:
                                raise ValueError(
                                    "artifact report source engine gross PnL cannot be calculated"
                                ) from exc
                            if not gross_matches:
                                raise ValueError(
                                    "artifact report source engine gross PnL conflicts with reference-price economics"
                                )
                            # The source engine applies the same declared
                            # pip displacement to entry and exit reference
                            # prices. Economic slippage reconciliation alone
                            # cannot detect a mutually rehashed fill/config.
                            # Optional fields remain optional for synthetic
                            # source-version envelopes.
                            if "slippage_pips" in source_identity:
                                declared_pips = source_identity["slippage_pips"]
                                entry_side = (
                                    OrderSide.BUY
                                    if record["direction"] == Direction.LONG.value
                                    else OrderSide.SELL
                                )
                                exit_side = (
                                    OrderSide.SELL
                                    if entry_side is OrderSide.BUY
                                    else OrderSide.BUY
                                )
                                try:
                                    expected_entry_fill = apply_adverse_slippage(
                                        record["entry_reference_price"],
                                        side=entry_side, pips=declared_pips,
                                        symbol=record["symbol"],
                                    )
                                    expected_exit_fill = apply_adverse_slippage(
                                        record["exit_reference_price"],
                                        side=exit_side, pips=declared_pips,
                                        symbol=record["symbol"],
                                    )
                                except (ValueError, OverflowError) as exc:
                                    raise ValueError(
                                        "artifact report source engine declared slippage cannot be applied"
                                    ) from exc
                                if (
                                    record["entry_price"] != expected_entry_fill
                                    or record["exit_price"] != expected_exit_fill
                                ):
                                    raise ValueError(
                                        "artifact report source engine execution prices conflict with declared slippage_pips"
                                    )
                            # Engine stores the adverse execution penalty
                            # as reference gross minus slipped fill PnL.
                            try:
                                slipped_pnl = pnl_usd(
                                    symbol=record["symbol"],
                                    direction=Direction(record["direction"]),
                                    units=record["units"],
                                    entry_price=record["entry_price"],
                                    exit_price=record["exit_price"],
                                )
                                implied_slippage = max(
                                    0.0, source_gross - slipped_pnl
                                )
                                slippage_matches = (
                                    math.isfinite(implied_slippage)
                                    and math.isclose(
                                        amounts["slippage_cost_usd"],
                                        implied_slippage,
                                        rel_tol=1e-12, abs_tol=1e-8,
                                    )
                                )
                            except (ValueError, OverflowError) as exc:
                                raise ValueError(
                                    "artifact report source engine slipped PnL cannot be calculated"
                                ) from exc
                            if not slippage_matches:
                                raise ValueError(
                                    "artifact report source engine slippage cost conflicts with execution prices"
                                )
                        # For installed source-engine reports only, known
                        # built-in cost models constrain actual trade economics
                        # as well as the shape of their identity configs.
                        if source_identity.get(
                            "backtest_engine_version"
                        ) == BACKTEST_ENGINE_VERSION:
                            commission_config = source_identity.get(
                                "commission_model"
                            )
                            if type(commission_config) is dict:
                                declared_model = commission_config.get("model")
                                if declared_model == "zero_commission":
                                    if amounts["commission_cost_usd"] != 0:
                                        raise ValueError(
                                            "artifact report source zero commission conflicts with trade costs"
                                        )
                                elif declared_model == "fixed_per_million_per_side":
                                    try:
                                        rate = commission_config["usd_per_million_per_side"]
                                        per_side = (
                                            record["units"] / 1_000_000 * rate
                                        )
                                        expected_commission = per_side + per_side
                                        commission_matches = (
                                            math.isfinite(expected_commission)
                                            and math.isclose(
                                                amounts["commission_cost_usd"],
                                                expected_commission,
                                                rel_tol=1e-12, abs_tol=1e-8,
                                            )
                                        )
                                    except (OverflowError, TypeError, KeyError):
                                        commission_matches = False
                                    if not commission_matches:
                                        raise ValueError(
                                            "artifact report source fixed commission conflicts with trade costs"
                                        )
                            financing_config = source_identity.get(
                                "financing_model"
                            )
                            if (
                                type(financing_config) is dict
                                and financing_config.get("model")
                                == "zero_financing"
                                and amounts["financing_cost_usd"] != 0
                            ):
                                raise ValueError(
                                    "artifact report source zero financing conflicts with trade costs"
                                )
                        for economic in ledger_totals:
                            ledger_totals[economic] += amounts[economic]
                        sorted_trade_pnls.append(amounts["net_pnl_usd"])
                        net_value = amounts["net_pnl_usd"]
                        if net_value > 0:
                            ledger_profit_usd += net_value
                        elif net_value < 0:
                            ledger_loss_usd -= net_value
                        # A realized close must carry its own equity change.
                        # Compare after adding net PnL (the engine's update
                        # order) instead of subtracting large equity amounts.
                        prior = record["risk_equity_before_usd"]
                        after = record["risk_equity_after_usd"]
                        for label, value in (
                            ("risk_equity_before_usd", prior),
                            ("risk_equity_after_usd", after),
                        ):
                            if type(value) not in (int, float):
                                raise ValueError(
                                    f"artifact report trade {label} must be finite numeric"
                                )
                            try:
                                finite = math.isfinite(value)
                            except OverflowError:
                                finite = False
                            if not finite:
                                raise ValueError(
                                    f"artifact report trade {label} must be finite numeric"
                                )
                        try:
                            expected_equity = prior + amounts["net_pnl_usd"]
                            equity_matches = (
                                math.isfinite(expected_equity)
                                and math.isclose(
                                    after, expected_equity,
                                    rel_tol=1e-12, abs_tol=1e-8,
                                )
                            )
                        except OverflowError:
                            equity_matches = False
                        if not equity_matches:
                            raise ValueError(
                                "artifact report trade realized equity conflicts with net PnL"
                            )
                        trade_equity_transitions.append((prior, after))
                        trade_exit_instants.append(exit_stamp)
                        trade_order = (exit_stamp, trade_id)
                        if (
                            previous_trade_order is not None
                            and trade_order < previous_trade_order
                        ):
                            raise ValueError("artifact report trades are not in canonical exit order")
                        previous_trade_order = trade_order
                        seen_trade_ids.add(trade_id)
                        seen_trade_decisions.add(decision)
                        observed_decision_symbols[decision] = record["symbol"]
                    else:
                        if decision in seen_rejection_decisions:
                            raise ValueError("artifact report duplicate rejection decision_id")
                        if decision in seen_trade_decisions:
                            raise ValueError("artifact report decision has both trade and rejection")
                        rejection_order = (evaluated_stamp, decision)
                        if (
                            previous_rejection_order is not None
                            and rejection_order < previous_rejection_order
                        ):
                            raise ValueError("artifact report rejections are not in canonical evaluation order")
                        previous_rejection_order = rejection_order
                        seen_rejection_decisions.add(decision)
                        observed_decision_symbols[decision] = record["symbol"]
                    # Complete semantic, economic, identity and chronology
                    # validation first. The byte-format guard must not mask
                    # a more precise tamper finding in the same JSONL row.
                    # The writer emits one compact sorted-key JSON object
                    # followed by exactly one LF. A rehashed but reserialized
                    # or unterminated row is not canonical evidence.
                    expected_line = (
                        json.dumps(
                            record, sort_keys=True, separators=(",", ":"),
                            ensure_ascii=False, allow_nan=False,
                        ) + "\n"
                    ).encode("utf-8")
                    if line != expected_line:
                        noncanonical_row_seen = True
                    observed += 1
            if (
                observed_size != expected_records[name]["size_bytes"]
                or observed_hash.hexdigest() != expected_records[name]["sha256"]
            ):
                raise ValueError("artifact report changed since verification")
            if observed != counts[field]:
                raise ValueError(f"artifact report {field} conflicts with JSONL records")
            # Defer formatting refusal until every row has passed semantic
            # and cross-row checks, preserving precise duplicate-ID reports.
            if noncanonical_row_seen:
                raise ValueError("artifact report JSONL row is not canonical")
        # A scheduled source exit must reference an actual directional
        # decision submitted to this engine. Every such decision is either
        # rejected or filled and eventually closed, so it must appear in
        # one of the validated outcome streams with the same symbol.
        # Do not require it to reach TIME_EXIT: stop/target may win.
        if source_identity.get("backtest_engine_version") == BACKTEST_ENGINE_VERSION:
            for scheduled_decision, (scheduled_symbol, _) in (
                scheduled_exit_by_decision.items()
            ):
                if observed_decision_symbols.get(scheduled_decision) != scheduled_symbol:
                    raise ValueError(
                        "artifact report source scheduled exit has no matching decision outcome"
                    )
        # Generic synthetic evidence has no independent close-sequence
        # witness, so keep its historical canonical-order chain check.
        # Source-engine evidence instead uses the checkpoint close sequence
        # below: trades with equal exit timestamps are sorted by identifier
        # for publication, which need not be their realized close order.
        if (
            "starting_equity_usd" in source_identity
            and source_identity.get("backtest_engine_version")
            != BACKTEST_ENGINE_VERSION
        ):
            last_realized_equity = source_identity["starting_equity_usd"]
            for before, after in trade_equity_transitions:
                if not math.isclose(
                    before, last_realized_equity,
                    rel_tol=1e-12, abs_tol=1e-8,
                ):
                    raise ValueError(
                        "artifact report trade risk equity continuity conflicts with source ledger"
                    )
                last_realized_equity = after
        # Engine-produced evidence publishes one initial checkpoint and
        # then one checkpoint at each realized trade close. Narrow this
        # invariant to the exact declared source engine version: synthetic
        # or alternate providers can publish other checkpoint shapes.
        if (
            source_identity.get("backtest_engine_version")
            == BACKTEST_ENGINE_VERSION
            and "starting_equity_usd" in source_identity
        ):
            if len(checkpoints) != len(trade_equity_transitions) + 1:
                raise ValueError(
                    "artifact report source engine checkpoint count conflicts with trade closes"
                )
            # The source engine creates its first checkpoint from the first
            # supplied quote bar, before any entry can execute. A rehashed
            # source report cannot put that initial witness after a fill.
            initial_stamp = _audit_parse_utc_timestamp(
                checkpoints[0]["timestamp_utc"], "equity checkpoint"
            )
            if (
                earliest_trade_entry is not None
                and initial_stamp > earliest_trade_entry
            ):
                raise ValueError(
                    "artifact report source engine initial checkpoint follows trade entry"
                )
            initial_equity = checkpoints[0]["realized_risk_equity_usd"]
            if not math.isclose(
                initial_equity, source_identity["starting_equity_usd"],
                rel_tol=1e-12, abs_tol=1e-8,
            ):
                raise ValueError(
                    "artifact report source engine initial checkpoint equity conflicts with starting equity"
                )
            # Checkpoints preserve engine realization order, while the
            # canonical trade file sorts same-timestamp closes by ID. Match
            # each checkpoint against one unconsumed exact source transition.
            # Source values are direct copies of risk state into both records,
            # so parsed float equality is exact and needs no rounding guess.
            witnesses = Counter(
                (exit_instant, before, after)
                for (before, after), exit_instant in zip(
                    trade_equity_transitions, trade_exit_instants,
                )
            )
            previous_realized = initial_equity
            for checkpoint in checkpoints[1:]:
                checkpoint_stamp = _audit_parse_utc_timestamp(
                    checkpoint["timestamp_utc"], "equity checkpoint"
                )
                checkpoint_equity = checkpoint["realized_risk_equity_usd"]
                witness = (
                    checkpoint_stamp, previous_realized, checkpoint_equity,
                )
                if witnesses[witness] <= 0:
                    raise ValueError(
                        "artifact report source engine checkpoint conflicts with trade close"
                    )
                witnesses[witness] -= 1
                previous_realized = checkpoint_equity
        ledger_totals["total_explicit_cost_usd"] = (
            ledger_totals["slippage_cost_usd"]
            + ledger_totals["commission_cost_usd"]
            + ledger_totals["financing_cost_usd"]
        )
        for name, expected in ledger_totals.items():
            try:
                finite = math.isfinite(expected)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError("artifact report aggregate trade economics must be finite")
            if name not in metrics:
                continue
            claimed = metrics[name]
            if type(claimed) not in (int, float):
                raise ValueError(f"artifact report metric {name} must be finite numeric")
            try:
                # Serialized trades use canonical exit-time order; allow
                # tiny summation drift versus the input order of the writer.
                matches = math.isfinite(claimed) and math.isclose(
                    claimed, expected, rel_tol=1e-12, abs_tol=1e-8,
                )
            except OverflowError:
                matches = False
            if not matches:
                raise ValueError(f"artifact report metric {name} conflicts with trade ledger")
        # Profitability summaries are claims about the stored realized
        # trade outcomes, not independent trusted economic evidence.
        try:
            profit_factor = (
                ledger_profit_usd / ledger_loss_usd
                if ledger_loss_usd > 0 else None
            )
        except OverflowError as exc:
            raise ValueError("artifact report aggregate profit factor must be finite") from exc
        for name, expected in (
            ("gross_profit_usd", ledger_profit_usd),
            ("gross_loss_usd", ledger_loss_usd),
            ("profit_factor", profit_factor),
        ):
            if expected is not None:
                try:
                    finite = math.isfinite(expected)
                except OverflowError:
                    finite = False
                if not finite:
                    raise ValueError(f"artifact report aggregate {name} must be finite")
            if name not in metrics:
                continue
            claimed = metrics[name]
            if expected is None:
                if claimed is not None:
                    raise ValueError(f"artifact report metric {name} conflicts with trade ledger")
                continue
            if type(claimed) not in (int, float):
                raise ValueError(f"artifact report metric {name} must be finite numeric")
            try:
                matches = math.isfinite(claimed) and math.isclose(
                    claimed, expected, rel_tol=1e-12, abs_tol=1e-8,
                )
            except OverflowError:
                matches = False
            if not matches:
                raise ValueError(f"artifact report metric {name} conflicts with trade ledger")
        winners = [pnl for pnl in sorted_trade_pnls if pnl > 0]
        losers = [pnl for pnl in sorted_trade_pnls if pnl < 0]
        trade_total = len(sorted_trade_pnls)
        expected_distribution: dict[str, int | float | None] = {
            "win_rate": len(winners) / trade_total if trade_total else None,
            "average_win_usd": sum(winners) / len(winners) if winners else None,
            "average_loss_usd": sum(losers) / len(losers) if losers else None,
            "expectancy_usd": (
                ledger_totals["net_pnl_usd"] / trade_total if trade_total else None
            ),
            "longest_winning_streak": _longest_streak(
                sorted_trade_pnls, winning=True
            ),
            "longest_losing_streak": _longest_streak(
                sorted_trade_pnls, winning=False
            ),
        }
        for name, expected in expected_distribution.items():
            if expected is not None and type(expected) is not int:
                try:
                    finite = math.isfinite(expected)
                except OverflowError:
                    finite = False
                if not finite:
                    raise ValueError(
                        f"artifact report aggregate {name} must be finite"
                    )
            if name not in metrics:
                continue
            claimed = metrics[name]
            if expected is None:
                if claimed is not None:
                    raise ValueError(
                        f"artifact report metric {name} conflicts with trade ledger"
                    )
            elif type(expected) is int:
                if type(claimed) is not int or claimed != expected:
                    raise ValueError(
                        f"artifact report metric {name} conflicts with trade ledger"
                    )
            else:
                if type(claimed) not in (int, float):
                    raise ValueError(
                        f"artifact report metric {name} must be finite numeric"
                    )
                try:
                    matches = math.isfinite(claimed) and math.isclose(
                        claimed, expected, rel_tol=1e-12, abs_tol=1e-8,
                    )
                except OverflowError:
                    matches = False
                if not matches:
                    raise ValueError(
                        f"artifact report metric {name} conflicts with trade ledger"
                    )
        # The engine records the starting equity in run_identity. Reconcile
        # its optional net-return claim only when that source-defined base is
        # available; arbitrary synthetic BacktestRun identity dicts may omit it.
        identity = summary["run_identity"]
        if "starting_equity_usd" in identity:
            if "net_return" in metrics:
                expected_return = ledger_totals["net_pnl_usd"] / starting_equity
                claimed_return = metrics["net_return"]
                if type(claimed_return) not in (int, float):
                    raise ValueError(
                        "artifact report metric net_return must be finite numeric"
                    )
                try:
                    matches_return = (
                        math.isfinite(expected_return)
                        and math.isfinite(claimed_return)
                        and math.isclose(
                            claimed_return, expected_return,
                            rel_tol=1e-12, abs_tol=1e-12,
                        )
                    )
                except OverflowError:
                    matches_return = False
                if not matches_return:
                    raise ValueError(
                        "artifact report metric net_return conflicts with starting equity and trade ledger"
                    )
        if "starting_equity_usd" in summary["run_identity"]:
            # The metrics writer starts from the source-defined equity base
            # and walks the checkpoint curve in published chronological order.
            peak_equity = starting_equity
            maximum_drawdown = 0.0
            maximum_drawdown_fraction = 0.0
            for checkpoint in checkpoints:
                realized_equity = checkpoint["realized_risk_equity_usd"]
                if realized_equity > peak_equity:
                    peak_equity = realized_equity
                drawdown = peak_equity - realized_equity
                try:
                    finite_drawdown = math.isfinite(drawdown)
                except OverflowError:
                    finite_drawdown = False
                if not finite_drawdown:
                    raise ValueError("artifact report checkpoint drawdown must be finite")
                if drawdown > maximum_drawdown:
                    maximum_drawdown = drawdown
                    maximum_drawdown_fraction = (
                        drawdown / peak_equity if peak_equity > 0 else 0.0
                    )
            expected_recovery = (
                ledger_totals["net_pnl_usd"] / maximum_drawdown
                if maximum_drawdown > 0 else None
            )
            for metric_name, expected_value in (
                ("max_drawdown_usd", maximum_drawdown),
                ("max_drawdown_fraction", maximum_drawdown_fraction),
                ("recovery_factor", expected_recovery),
            ):
                if metric_name not in metrics:
                    continue
                claimed = metrics[metric_name]
                if expected_value is None:
                    if claimed is not None:
                        raise ValueError(
                            f"artifact report metric {metric_name} conflicts with checkpoint curve"
                        )
                    continue
                if type(claimed) not in (int, float):
                    raise ValueError(
                        f"artifact report metric {metric_name} must be finite numeric"
                    )
                try:
                    matches_drawdown = (
                        math.isfinite(expected_value)
                        and math.isfinite(claimed)
                        and math.isclose(
                            claimed, expected_value,
                            rel_tol=1e-12, abs_tol=1e-8,
                        )
                    )
                except OverflowError:
                    matches_drawdown = False
                if not matches_drawdown:
                    raise ValueError(
                        f"artifact report metric {metric_name} conflicts with checkpoint curve"
                    )
        if "trade_count" in metrics and (
            type(metrics["trade_count"]) is not int
            or metrics["trade_count"] != counts["trade_count"]
        ):
            raise ValueError("artifact report metric trade_count conflicts with summary")
        # Run source-defined semantic checks first so malformed economics
        # still yields its precise rejection reason. Canonical bytes are a
        # separate, final opt-in structural requirement.
        for filename, parsed in (
            ("summary.json", summary), ("metrics.json", metrics),
        ):
            if small_json_payloads[filename] != _stable_json_bytes(parsed):
                raise ValueError(
                    f"artifact report {filename} is not canonical JSON"
                )
        return counts
    finally:
        os.close(root_fd)
