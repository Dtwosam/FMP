from __future__ import annotations

import hashlib
import json
import math
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Callable, Mapping

from fmp.backtest.costs import ZeroCommission, ZeroFinancing, pip_size
from fmp.backtest.engine import BacktestConfig, run_backtest
from fmp.contracts import BacktestRun, Direction, QuoteBar, TradeRecord
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.research.adapter import candidate_to_decision
from fmp.risk import RiskConfig
from fmp.strategies.session_breakout import (
    SessionBreakoutConfig,
    generate_session_breakout_candidates,
)
from fmp.walkforward.contracts import (
    EXPERIMENT_ID,
    REQUESTED_RISK_FRACTION,
    STAGE2_WINDOWS,
    STARTING_EQUITY_USD,
    USDJPY_PHASE2_ARTIFACT_ID,
    USDJPY_PHASE2_ZIP_SHA256,
    USDJPY_PROCESSED_MANIFEST_SHA256,
    allowed_phase7_window,
)
from fmp.walkforward.data import LoadedPhase7Bars, load_phase7_bars


SPREAD_REFERENCE_METHOD_VERSION = "fmp-phase8-spread-reference-v1"
PHASE7_CHECKPOINT_TAG = "fmp-v1-phase7-walk-forward"
PHASE7_CHECKPOINT_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"
PHASE7_OUTCOME = "PASS / PROMOTE"
PHASE7_STAGE2_RUN_ID = 35015277625
FROZEN_CANDIDATE_ID = "session_breakout"
HISTORICAL_SLIPPAGE_PIPS = 0.2
_TIMEFRAME = "15m"
_BAR_WIDTH = timedelta(minutes=15)
_HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _utc_start(value) -> datetime:  # type: ignore[no-untyped-def]
    return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)


def _validate_code_commit(value: str) -> None:
    if not isinstance(value, str) or _HEX40.fullmatch(value) is None:
        raise ValueError("code_commit must be a lowercase 40-character commit SHA")


def _timestamp_text(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("reference timestamps must use UTC")
    return value.isoformat().replace("+00:00", "Z")


def _is_scored_candidate(candidate, *, start: datetime, end: datetime) -> bool:  # type: ignore[no-untyped-def]
    if not (start <= candidate.observation_bar_timestamp_utc < end):
        return False
    if not (start <= candidate.signal_known_timestamp_utc < end):
        return False
    if candidate.latest_exit_timestamp_utc is not None and not (
        start < candidate.latest_exit_timestamp_utc < end
    ):
        return False
    return True


def _run_stage2_window(
    *,
    loaded: LoadedPhase7Bars,
    window_name: str,
    code_commit: str,
    slippage_pips: float,
) -> BacktestRun:
    _validate_code_commit(code_commit)
    if slippage_pips != HISTORICAL_SLIPPAGE_PIPS:
        raise ValueError("Phase 8 spread reference uses only the frozen 0.2-pip Stage 2 path")
    window = allowed_phase7_window(window_name)
    if window not in STAGE2_WINDOWS:
        raise ValueError("Phase 8 spread reference accepts only frozen Stage 2 windows")

    scored_start = _utc_start(window.start)
    scored_end = _utc_start(window.end_exclusive)
    expected_scored = tuple(
        item for item in loaded.bars if scored_start <= item.timestamp_utc < scored_end
    )
    if loaded.scored_bars != expected_scored:
        raise ValueError("loaded Stage 2 scored bars do not match the frozen window")
    if any(item.symbol != "USDJPY" for item in loaded.bars):
        raise ValueError("Phase 8 spread reference supports only USDJPY")

    config = SessionBreakoutConfig(
        buffer_pips=5,
        target_range_multiple=1.5,
        timeframe=_TIMEFRAME,
    )
    generated = generate_session_breakout_candidates(loaded.bars, config=config)
    scored = tuple(
        item
        for item in generated
        if _is_scored_candidate(item, start=scored_start, end=scored_end)
    )

    decisions = []
    scheduled_exits = []
    for candidate in scored:
        decision, scheduled_exit = candidate_to_decision(
            candidate,
            next_bar_timestamp_utc=candidate.signal_known_timestamp_utc,
            requested_risk_fraction=REQUESTED_RISK_FRACTION,
        )
        decisions.append(decision)
        if scheduled_exit is not None:
            scheduled_exits.append(scheduled_exit)

    backtest_config = BacktestConfig(
        starting_equity_usd=STARTING_EQUITY_USD,
        slippage_pips=HISTORICAL_SLIPPAGE_PIPS,
        risk_config=RiskConfig(),
        commission_model=ZeroCommission(),
        financing_model=ZeroFinancing(),
        processed_data_manifest_id=USDJPY_PROCESSED_MANIFEST_SHA256,
        schema_version=CANONICAL_SCHEMA_VERSION,
        timeframe=_TIMEFRAME,
        requested_start_utc=scored_start,
        requested_end_utc=scored_end,
        code_commit=code_commit,
        decision_config={
            "experiment_id": EXPERIMENT_ID,
            "candidate_id": FROZEN_CANDIDATE_ID,
            "window_name": window.name,
            "parameters": {"buffer_pips": 5, "target_range_multiple": 1.5},
            "spread_reference_method": SPREAD_REFERENCE_METHOD_VERSION,
        },
    )
    return run_backtest(
        bars=loaded.scored_bars,
        decisions=tuple(decisions),
        config=backtest_config,
        scheduled_exits=tuple(scheduled_exits),
    )


def _bar_containing(
    bars: tuple[QuoteBar, ...],
    timestamp_utc: datetime,
    *,
    role: str,
) -> QuoteBar:
    matches = tuple(
        item
        for item in bars
        if item.timestamp_utc <= timestamp_utc < item.timestamp_utc + _BAR_WIDTH
    )
    if len(matches) != 1:
        raise ValueError(f"Phase 8 spread reference requires exactly one historical {role} bar")
    return matches[0]


def _spread_pips(item: QuoteBar) -> float:
    spread = (item.ask_open - item.bid_open) / pip_size("USDJPY")
    if not math.isfinite(spread) or spread < 0:
        raise ValueError("historical spread must be finite and non-negative")
    return round(spread, 12)


def _nearest_rank_p95(values: list[float]) -> float:
    if not values:
        raise ValueError("spread reference requires at least one completed trade")
    ordered = sorted(values)
    rank = math.ceil(0.95 * len(ordered))
    return ordered[rank - 1]


def _distribution(values: list[float]) -> dict[str, object]:
    if not values:
        raise ValueError("spread reference requires at least one completed trade")
    return {
        "count": len(values),
        "median": float(median(values)),
        "p95": float(_nearest_rank_p95(values)),
        "p95_method": "nearest_rank",
    }


def _trade_record(
    *,
    window_name: str,
    trade: TradeRecord,
    bars: tuple[QuoteBar, ...],
) -> dict[str, object]:
    entry_bar = _bar_containing(bars, trade.entry_timestamp_utc, role="entry")
    exit_bar = _bar_containing(bars, trade.exit_timestamp_utc, role="exit")
    return {
        "window_name": window_name,
        "trade_id": trade.trade_id,
        "decision_id": trade.decision_id,
        "direction": trade.direction.value,
        "exit_reason": trade.exit_reason.value,
        "entry_timestamp_utc": _timestamp_text(trade.entry_timestamp_utc),
        "exit_timestamp_utc": _timestamp_text(trade.exit_timestamp_utc),
        "entry_bar_timestamp_utc": _timestamp_text(entry_bar.timestamp_utc),
        "exit_bar_timestamp_utc": _timestamp_text(exit_bar.timestamp_utc),
        "entry_spread_pips": _spread_pips(entry_bar),
        "exit_spread_pips": _spread_pips(exit_bar),
    }


def build_spread_reference(
    *,
    dataset_root: Path,
    manifest_path: Path,
    code_commit: str,
    load_window: Callable[..., LoadedPhase7Bars] = load_phase7_bars,
    run_window: Callable[..., BacktestRun] = _run_stage2_window,
) -> dict[str, object]:
    _validate_code_commit(code_commit)
    records: list[dict[str, object]] = []
    seen_trade_ids: set[str] = set()

    for window in STAGE2_WINDOWS:
        loaded = load_window(
            dataset_root=Path(dataset_root),
            manifest_path=Path(manifest_path),
            candidate_id=FROZEN_CANDIDATE_ID,
            window_name=window.name,
        )
        run = run_window(
            loaded=loaded,
            window_name=window.name,
            code_commit=code_commit,
            slippage_pips=HISTORICAL_SLIPPAGE_PIPS,
        )
        if not isinstance(run, BacktestRun):
            raise TypeError("Phase 8 spread-reference runner must return BacktestRun")
        for trade in run.trades:
            if trade.symbol != "USDJPY":
                raise ValueError("Phase 8 spread reference contains a non-USDJPY trade")
            if trade.trade_id in seen_trade_ids:
                raise ValueError("duplicate trade_id in Phase 8 spread reference")
            seen_trade_ids.add(trade.trade_id)
            records.append(
                _trade_record(
                    window_name=window.name,
                    trade=trade,
                    bars=loaded.scored_bars,
                )
            )

    if not records:
        raise ValueError("Phase 8 spread reference requires completed Stage 2 survivor trades")
    entry_values = [float(item["entry_spread_pips"]) for item in records]
    exit_values = [float(item["exit_spread_pips"]) for item in records]

    return {
        "method_version": SPREAD_REFERENCE_METHOD_VERSION,
        "phase7_checkpoint_tag": PHASE7_CHECKPOINT_TAG,
        "phase7_checkpoint_sha": PHASE7_CHECKPOINT_SHA,
        "phase7_experiment": EXPERIMENT_ID,
        "phase7_outcome": PHASE7_OUTCOME,
        "phase7_stage2_run_id": PHASE7_STAGE2_RUN_ID,
        "phase2_artifact_id": USDJPY_PHASE2_ARTIFACT_ID,
        "phase2_zip_sha256": USDJPY_PHASE2_ZIP_SHA256,
        "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
        "code_commit": code_commit,
        "strategy": {
            "id": FROZEN_CANDIDATE_ID,
            "symbol": "USDJPY",
            "timeframe": _TIMEFRAME,
            "buffer_pips": 5,
            "target_range_multiple": 1.5,
        },
        "historical_slippage_pips": HISTORICAL_SLIPPAGE_PIPS,
        "stage2_windows": [item.name for item in STAGE2_WINDOWS],
        "trade_count": len(records),
        "entry_spread_pips": _distribution(entry_values),
        "exit_spread_pips": _distribution(exit_values),
        "trades": records,
    }


def _canonical_bytes(record: Mapping[str, object]) -> bytes:
    return (
        json.dumps(
            dict(record),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _write_exact(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"conflicting Phase 8 spread-reference artifact: {path.name}")
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def write_spread_reference(out_dir: Path, reference: Mapping[str, object]) -> str:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    reference_bytes = _canonical_bytes(reference)
    digest = hashlib.sha256(reference_bytes).hexdigest()
    _write_exact(out_dir / "reference.json", reference_bytes)
    _write_exact(out_dir / "reference.sha256", (digest + "\n").encode("ascii"))
    return digest


def build_and_write_spread_reference(
    *,
    dataset_root: Path,
    manifest_path: Path,
    out_dir: Path,
    code_commit: str,
) -> str:
    reference = build_spread_reference(
        dataset_root=dataset_root,
        manifest_path=manifest_path,
        code_commit=code_commit,
    )
    return write_spread_reference(out_dir, reference)


__all__ = [
    "HISTORICAL_SLIPPAGE_PIPS",
    "PHASE7_CHECKPOINT_SHA",
    "PHASE7_CHECKPOINT_TAG",
    "PHASE7_STAGE2_RUN_ID",
    "SPREAD_REFERENCE_METHOD_VERSION",
    "build_and_write_spread_reference",
    "build_spread_reference",
    "write_spread_reference",
]
