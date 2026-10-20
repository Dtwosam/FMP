from __future__ import annotations

import hashlib
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

from fmp.contracts import (
    BacktestRun, Direction, EquityCheckpoint, ExitReason, RejectionCode,
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
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError("artifact evidence must be a regular file")
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
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("artifact evidence must be a regular file")
        # Hash bounded chunks rather than materializing an entire historical
        # evidence JSONL file in memory.
        observed_size = 0
        observed_hash = hashlib.sha256()
        with _open_regular_artifact(path, root_fd=root_fd) as handle:
            while block := handle.read(1024 * 1024):
                observed_size += len(block)
                if observed_size > size:
                    raise ValueError("artifact evidence size or SHA256 mismatch")
                observed_hash.update(block)
        if observed_size != size or observed_hash.hexdigest() != digest:
            raise ValueError("artifact evidence size or SHA256 mismatch")
    if seen != expected_names:
        raise ValueError("artifact evidence filename set mismatch")
    if [entry["path"] for entry in entries] != sorted(expected_names):
        raise ValueError("artifact evidence paths must use canonical order")
    return manifest
