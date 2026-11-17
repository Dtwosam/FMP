"""Opt-in retention of Phase 7 trade and rejection rows.

Governing method: annual pattern catalogue discovery under DEC-469 / DEC-268.
This module is a pattern-evidence writer for one frozen rule. It is not the
annual catalogue, a new backtester, or permission to read historical data.

``evaluate_window`` still returns only the aggregate. ``retain_phase7_window``
uses that same execution and keeps the ``BacktestRun`` rows the engine already
produced. The writer puts those rows in a separate directory. It does not edit
``write_stage2_evidence`` output and it does not mark the 199-trade Stage 2
series as recovered.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping, Sequence

from fmp.contracts import Direction, RejectionRecord, TradeRecord
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.research.trade_level_evidence import (
    REQUESTED_RISK_R_DEFINITION,
    EvidenceProvenance,
    SubmittedTrade,
    TradeSubmission,
    WindowAggregate,
)
from fmp.risk.sizing import pnl_usd

from .artifacts import _atomic_write, _jsonable, _stable_json_bytes
from .contracts import (
    EXPERIMENT_ID,
    FROZEN_CANDIDATES,
    PHASE6_CHECKPOINT_SHA,
    REQUESTED_RISK_FRACTION,
    SLIPPAGE_SCENARIOS,
    STARTING_EQUITY_USD,
    USDJPY_PHASE2_ARTIFACT_ID,
    USDJPY_PHASE2_ZIP_SHA256,
    USDJPY_PROCESSED_MANIFEST_SHA256,
    allowed_phase7_window,
)
from .evaluation import LoadedPhase7Bars, WindowFinancialResult, _execute_window

PHASE7_TRADE_RETENTION_PROTOCOL = "fmp-phase7-trade-retention-v1"
ORIGINAL_STAGE2_RUN_ID = "35015277625"
ORIGINAL_STAGE2_ARTIFACT_ID = "10414817824"
ORIGINAL_STAGE2_CODE = "a1f8a0466463c79fdbceb9d6ebad9e3ea809474d"
ORIGINAL_STAGE2_RESULT_SHA256 = "ce7ef3f732bf2da7cd9c0df5e5d695dcdadd63e309c9428a6f572801fcb197b7"
ORIGINAL_STAGE2_WINDOWS_SHA256 = "66a1d35b12b68a0762dd98cd6838a2befcaf57ef9ae43bce181241fe4d23a4f0"
ORIGINAL_STAGE2_ZIP_SHA256 = "2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4"
SPREAD_BASIS = "included_in_bid_ask_reference"
_CONTENT_FILES = ("rejections.jsonl", "trades.jsonl", "window-index.json")
_MONEY = 1e-6
_PROVENANCE_ROLES = frozenset({"synthetic_fixture", "separately_authorized_submission"})


@dataclass(frozen=True, slots=True)
class RetainedPhase7Window:
    financial: WindowFinancialResult
    trades: tuple[TradeRecord, ...]
    rejections: tuple[RejectionRecord, ...]


@dataclass(frozen=True, slots=True)
class LoadedTradeRetention:
    manifest: Mapping[str, object]
    submissions: tuple[TradeSubmission, ...]
    authentic_stage2_series_recovered: bool
    r_definition: str


def retain_phase7_window(
    loaded: LoadedPhase7Bars,
    *,
    candidate_id: str,
    window_name: str,
    code_commit: str,
    slippage_pips: float,
) -> RetainedPhase7Window:
    """Return the aggregate and the engine rows from one existing evaluation."""

    financial, trades, rejections = _execute_window(
        loaded,
        candidate_id=candidate_id,
        window_name=window_name,
        code_commit=code_commit,
        slippage_pips=slippage_pips,
    )
    return RetainedPhase7Window(
        financial=financial,
        trades=trades,
        rejections=rejections,
    )


def write_phase7_trade_retention(
    *,
    retention_dir: Path,
    windows: Sequence[RetainedPhase7Window],
    code_commit: str,
    aggregate_dir: Path | None = None,
    provenance_role: str = "synthetic_fixture",
    provenance_label: str = "synthetic-retained-window",
    source_run_id: str | None = None,
    source_artifact_id: str | None = None,
    source_commit: str | None = None,
) -> dict[str, object]:
    """Write trade and rejection rows beside, not into, the aggregate directory."""

    if provenance_role not in _PROVENANCE_ROLES:
        raise ValueError("trade retention provenance role is not recognized")
    if not isinstance(provenance_label, str) or not provenance_label.strip():
        raise ValueError("trade retention provenance label must be non-empty")
    if not isinstance(code_commit, str) or not code_commit.strip():
        raise ValueError("trade retention code_commit must be non-empty")
    if provenance_role == "synthetic_fixture" and any(
        value is not None for value in (source_run_id, source_artifact_id, source_commit)
    ):
        raise ValueError("a synthetic retention file cannot carry a historical source identity")
    if not windows:
        raise ValueError("trade retention requires at least one window")

    destination = Path(retention_dir)
    _require_separate_directory(destination, aggregate_dir)
    rows = _validated_windows(windows, code_commit=code_commit)
    trades = _trade_lines(rows)
    rejections = _rejection_lines(rows)
    index = {
        "protocol": PHASE7_TRADE_RETENTION_PROTOCOL,
        "windows": [_window_index_row(item) for item in rows],
    }
    destination.mkdir(parents=True, exist_ok=True)
    payloads = {
        "trades.jsonl": _jsonl_bytes(trades),
        "rejections.jsonl": _jsonl_bytes(rejections),
        "window-index.json": _stable_json_bytes(index),
    }
    for name in _CONTENT_FILES:
        _atomic_write(destination / name, payloads[name])

    manifest = _manifest(
        code_commit=code_commit,
        provenance_role=provenance_role,
        provenance_label=provenance_label,
        source_run_id=source_run_id,
        source_artifact_id=source_artifact_id,
        source_commit=source_commit,
        artifacts=[_artifact_record(destination / name) for name in _CONTENT_FILES],
        window_count=len(rows),
        trade_count=len(trades),
        rejection_count=len(rejections),
    )
    _atomic_write(destination / "manifest.json", _stable_json_bytes(manifest))
    return manifest


def load_phase7_trade_retention(retention_dir: Path) -> LoadedTradeRetention:
    """Read a retention directory and build one validator submission per slippage."""

    root = Path(retention_dir)
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("missing retention file: manifest.json")
    manifest = _load_json_object(manifest_path, label="manifest.json")
    _check_manifest_contract(manifest)
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("malformed retention manifest")
    by_path = _artifact_map(artifacts)
    for name in _CONTENT_FILES:
        record = by_path.get(name)
        if record is None:
            raise ValueError(f"missing retention file: {name}")
        data = _read_checked(root / name, record)
        if name == "window-index.json":
            index = _parse_json_bytes(data, label=name)
        elif name == "trades.jsonl":
            trade_rows = _parse_jsonl(data, label=name)
        else:
            rejection_rows = _parse_jsonl(data, label=name)
    if not isinstance(index, Mapping):
        raise ValueError("malformed retention file: window-index.json")
    windows = index.get("windows")
    if not isinstance(windows, list) or not windows:
        raise ValueError("malformed retention file: window-index.json")
    _check_rows(windows, trade_rows, rejection_rows)
    submissions = _submissions(manifest, windows, trade_rows)
    recovered = manifest.get("authentic_stage2_series_recovered")
    if recovered is not False:
        raise ValueError("inconsistent trade retention: the Stage 2 series is not recovered")
    return LoadedTradeRetention(
        manifest=manifest,
        submissions=submissions,
        authentic_stage2_series_recovered=False,
        r_definition=REQUESTED_RISK_R_DEFINITION,
    )


def _execute_identity(code_commit: str, financial: WindowFinancialResult) -> dict[str, object]:
    candidate = FROZEN_CANDIDATES[financial.candidate_id]
    window = allowed_phase7_window(financial.window_name)
    return {
        "experiment_id": EXPERIMENT_ID,
        "code_commit": code_commit,
        "candidate_id": candidate.candidate_id,
        "symbol": candidate.symbol,
        "timeframe": candidate.timeframe,
        "parameters": dict(candidate.parameters),
        "window_name": window.name,
        "slippage_pips": financial.slippage_pips,
        "phase2_artifact_id": USDJPY_PHASE2_ARTIFACT_ID,
        "phase2_zip_sha256": USDJPY_PHASE2_ZIP_SHA256,
        "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
        "canonical_schema_version": CANONICAL_SCHEMA_VERSION,
        "phase6_checkpoint_sha": PHASE6_CHECKPOINT_SHA,
        "reproduction_target_run_id": ORIGINAL_STAGE2_RUN_ID,
        "reproduction_target_artifact_id": ORIGINAL_STAGE2_ARTIFACT_ID,
        "reproduction_target_code": ORIGINAL_STAGE2_CODE,
        "reproduction_target_result_sha256": ORIGINAL_STAGE2_RESULT_SHA256,
        "reproduction_target_windows_sha256": ORIGINAL_STAGE2_WINDOWS_SHA256,
        "reproduction_target_zip_sha256": ORIGINAL_STAGE2_ZIP_SHA256,
        "authentic_stage2_series_recovered": False,
        "original_artifact_modified": False,
        "r_definition": REQUESTED_RISK_R_DEFINITION,
        "requested_risk_fraction": REQUESTED_RISK_FRACTION,
        "starting_equity_usd": STARTING_EQUITY_USD,
        "spread_basis": SPREAD_BASIS,
    }


def _validated_windows(
    windows: Sequence[RetainedPhase7Window], *, code_commit: str
) -> tuple[RetainedPhase7Window, ...]:
    seen: set[tuple[str, float]] = set()
    candidate_ids: set[str] = set()
    for item in windows:
        financial = item.financial
        if not isinstance(financial, WindowFinancialResult):
            raise ValueError("malformed trade retention window")
        if financial.slippage_pips not in SLIPPAGE_SCENARIOS:
            raise ValueError("trade retention slippage must be one of the frozen scenarios")
        allowed_phase7_window(financial.window_name)
        if financial.candidate_id not in FROZEN_CANDIDATES:
            raise ValueError("trade retention candidate is not a frozen Phase 7 rule")
        key = (financial.window_name, float(financial.slippage_pips))
        if key in seen:
            raise ValueError("duplicate trade retention window")
        seen.add(key)
        candidate_ids.add(financial.candidate_id)
        if financial.run_identity.get("code_commit") != code_commit:
            raise ValueError("inconsistent trade retention: code commit does not match the engine")
        if financial.trade_count != len(item.trades):
            raise ValueError("inconsistent trade retention: trade count does not match the rows")
        rejection_count = financial.metrics.get("rejection_count")
        if rejection_count != len(item.rejections):
            raise ValueError("inconsistent trade retention: rejection count does not match the rows")
        _check_engine_economics(financial, item.trades)
        _check_chronology(item)
    if len(candidate_ids) != 1:
        raise ValueError("trade retention cannot mix frozen candidates")
    return tuple(
        sorted(
            windows,
            key=lambda item: (
                item.financial.slippage_pips,
                item.financial.scored_start_utc,
                item.financial.window_name,
            ),
        )
    )


def _check_engine_economics(financial: WindowFinancialResult, trades: Sequence[TradeRecord]) -> None:
    nets = [float(trade.net_pnl_usd) for trade in trades]
    losses = [value for value in nets if value < 0]
    gross_profit = math.fsum(value for value in nets if value > 0)
    gross_loss = -math.fsum(losses)
    net = math.fsum(nets)
    if abs(financial.gross_profit_usd - gross_profit) > _MONEY:
        raise ValueError("inconsistent trade retention: gross profit does not match the rows")
    if financial.gross_loss_usd < 0 or abs(financial.gross_loss_usd - gross_loss) > _MONEY:
        raise ValueError("inconsistent trade retention: gross loss must be the positive Phase 3 magnitude")
    if abs(financial.net_pnl_usd - net) > _MONEY:
        raise ValueError("inconsistent trade retention: net PnL does not match the rows")
    running = STARTING_EQUITY_USD
    for trade in trades:
        _check_trade_prices(trade)
        if abs(float(trade.risk_equity_before_usd) - running) > _MONEY:
            raise ValueError("inconsistent trade retention: equity chain does not match exit order")
        if abs(float(trade.risk_equity_after_usd) - (float(trade.risk_equity_before_usd) + float(trade.net_pnl_usd))) > _MONEY:
            raise ValueError("inconsistent trade retention: equity after the trade does not match net PnL")
        running = float(trade.risk_equity_after_usd)


def _check_trade_prices(trade: TradeRecord) -> None:
    gross = pnl_usd(
        symbol=trade.symbol,
        direction=trade.direction,
        units=trade.units,
        entry_price=trade.entry_reference_price,
        exit_price=trade.exit_reference_price,
    )
    slipped = pnl_usd(
        symbol=trade.symbol,
        direction=trade.direction,
        units=trade.units,
        entry_price=trade.entry_price,
        exit_price=trade.exit_price,
    )
    slippage = max(0.0, gross - slipped)
    net = gross - slippage - float(trade.commission_cost_usd) - float(trade.financing_cost_usd)
    if abs(float(trade.gross_pnl_usd) - gross) > _MONEY:
        raise ValueError("inconsistent trade retention: gross PnL does not match the prices")
    if abs(float(trade.slippage_cost_usd) - slippage) > _MONEY:
        raise ValueError("inconsistent trade retention: slippage does not match the prices")
    if abs(float(trade.net_pnl_usd) - net) > _MONEY:
        raise ValueError("inconsistent trade retention: net PnL does not match the prices")
    if float(trade.commission_cost_usd) < 0 or float(trade.slippage_cost_usd) < 0:
        raise ValueError("inconsistent trade retention: costs must be non-negative")


def _check_chronology(item: RetainedPhase7Window) -> None:
    trades = item.trades
    ordered = tuple(sorted(trades, key=lambda trade: (trade.exit_timestamp_utc, trade.trade_id)))
    if trades != ordered:
        raise ValueError("trade records are not chronological")
    rejections = tuple(item.rejections)
    ordered_rejections = tuple(
        sorted(rejections, key=lambda row: (row.evaluated_timestamp_utc, row.decision_id))
    )
    if rejections != ordered_rejections:
        raise ValueError("rejection records are not chronological")
    trade_ids = [trade.trade_id for trade in trades]
    if len(trade_ids) != len(set(trade_ids)):
        raise ValueError("duplicate trade record")
    decision_ids = [trade.decision_id for trade in trades]
    if len(decision_ids) != len(set(decision_ids)):
        raise ValueError("duplicate trade record")


def _trade_lines(windows: Sequence[RetainedPhase7Window]) -> list[dict[str, object]]:
    lines: list[dict[str, object]] = []
    for item in windows:
        identity = _execute_identity(str(item.financial.run_identity["code_commit"]), item.financial)
        for trade in item.trades:
            ambiguous = bool(trade.intrabar_ambiguous)
            equity = float(trade.risk_equity_before_usd)
            lines.append(
                {
                    **identity,
                    "record_kind": "trade",
                    "spread_cost_usd": 0.0,
                    "intrabar_resolution": "conservative_adverse" if ambiguous else "not_applicable",
                    "claimed_net_r": float(trade.net_pnl_usd) / (equity * REQUESTED_RISK_FRACTION),
                    "record": trade,
                }
            )
    return lines


def _rejection_lines(windows: Sequence[RetainedPhase7Window]) -> list[dict[str, object]]:
    lines: list[dict[str, object]] = []
    for item in windows:
        identity = _execute_identity(str(item.financial.run_identity["code_commit"]), item.financial)
        for rejection in item.rejections:
            lines.append({**identity, "record_kind": "rejection", "record": rejection})
    return lines


def _window_index_row(item: RetainedPhase7Window) -> dict[str, object]:
    financial = item.financial
    identity = _execute_identity(str(financial.run_identity["code_commit"]), financial)
    return {
        **identity,
        "trade_count": financial.trade_count,
        "rejection_count": len(item.rejections),
        "net_pnl_usd": financial.net_pnl_usd,
        "gross_profit_usd": financial.gross_profit_usd,
        "gross_loss_usd": financial.gross_loss_usd,
        "slippage_cost_usd": math.fsum(float(trade.slippage_cost_usd) for trade in item.trades),
        "commission_cost_usd": math.fsum(float(trade.commission_cost_usd) for trade in item.trades),
        "financing_cost_usd": math.fsum(float(trade.financing_cost_usd) for trade in item.trades),
        "scored_start_utc": financial.scored_start_utc,
        "scored_end_utc": financial.scored_end_utc,
        "warmup_start_utc": financial.warmup_range[0],
        "warmup_end_utc": financial.warmup_range[1],
        "refit_status": financial.refit_status,
        "trade_ids": [trade.trade_id for trade in item.trades],
        "rejection_decision_ids": [row.decision_id for row in item.rejections],
    }


def _manifest(**payload: object) -> dict[str, object]:
    return {
        "protocol": PHASE7_TRADE_RETENTION_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "authentic_stage2_series_recovered": False,
        "original_artifact_modified": False,
        "original_artifact_id": ORIGINAL_STAGE2_ARTIFACT_ID,
        "reproduction_authorized": False,
        "owner_authorization_recorded": False,
        "reproduction_target": {
            "run_id": ORIGINAL_STAGE2_RUN_ID,
            "artifact_id": ORIGINAL_STAGE2_ARTIFACT_ID,
            "code": ORIGINAL_STAGE2_CODE,
            "result_sha256": ORIGINAL_STAGE2_RESULT_SHA256,
            "windows_sha256": ORIGINAL_STAGE2_WINDOWS_SHA256,
            "zip_sha256": ORIGINAL_STAGE2_ZIP_SHA256,
        },
        "r_definition": REQUESTED_RISK_R_DEFINITION,
        **payload,
    }


def _require_separate_directory(retention_dir: Path, aggregate_dir: Path | None) -> None:
    if aggregate_dir is None:
        return
    left = retention_dir.resolve()
    right = Path(aggregate_dir).resolve()
    if left == right or _is_inside(left, right) or _is_inside(right, left):
        raise ValueError("trade retention directory must be separate from the Phase 7 aggregate directory")


def _is_inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return path != parent


def _artifact_record(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
    }


def _jsonl_bytes(rows: Sequence[object]) -> bytes:
    if not rows:
        return b""
    lines = [
        json.dumps(_jsonable(row), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        for row in rows
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _load_json_object(path: Path, *, label: str) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"malformed retention file: {label}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"malformed retention file: {label}")
    return value


def _parse_json_bytes(data: bytes, *, label: str) -> object:
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"malformed retention file: {label}") from exc


def _parse_jsonl(data: bytes, *, label: str) -> list[dict[str, object]]:
    if data == b"":
        return []
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise ValueError(f"malformed retention file: {label}") from exc
    if not text.endswith("\n"):
        raise ValueError(f"malformed retention file: {label}")
    rows: list[dict[str, object]] = []
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed retention file: {label}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"malformed retention file: {label}")
        rows.append(value)
    return rows


def _check_manifest_contract(manifest: Mapping[str, object]) -> None:
    if manifest.get("protocol") != PHASE7_TRADE_RETENTION_PROTOCOL:
        raise ValueError("malformed retention manifest")
    if manifest.get("authentic_stage2_series_recovered") is not False:
        raise ValueError("inconsistent trade retention: the Stage 2 series is not recovered")
    if manifest.get("original_artifact_modified") is not False:
        raise ValueError("inconsistent trade retention: the original artifact is unchanged")
    if manifest.get("reproduction_authorized") is not False or manifest.get("owner_authorization_recorded") is not False:
        raise ValueError("inconsistent trade retention: owner authorization is not recorded here")
    role = manifest.get("provenance_role")
    if role not in _PROVENANCE_ROLES:
        raise ValueError("malformed retention manifest")
    if role == "synthetic_fixture" and any(
        manifest.get(name) is not None for name in ("source_run_id", "source_artifact_id", "source_commit")
    ):
        raise ValueError("inconsistent trade retention: a synthetic file cannot cite a historical source")
    if manifest.get("claims_trades_from_stage2_zip") is True:
        raise ValueError("inconsistent trade retention: the Stage 2 ZIP has no trade ledger")


def _artifact_map(artifacts: list[object]) -> dict[str, Mapping[str, object]]:
    mapped: dict[str, Mapping[str, object]] = {}
    for item in artifacts:
        if not isinstance(item, Mapping) or not isinstance(item.get("path"), str):
            raise ValueError("malformed retention manifest")
        path = str(item["path"])
        if path in mapped:
            raise ValueError("duplicate trade retention artifact")
        mapped[path] = item
    return mapped


def _read_checked(path: Path, record: Mapping[str, object]) -> bytes:
    if not path.is_file():
        raise ValueError(f"missing retention file: {path.name}")
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if record.get("sha256") != digest or record.get("size_bytes") != len(data):
        raise ValueError(f"trade retention checksum mismatch: {path.name}")
    return data


def _check_rows(
    windows: Sequence[object],
    trades: Sequence[Mapping[str, object]],
    rejections: Sequence[Mapping[str, object]],
) -> None:
    indexed: dict[tuple[str, float], Mapping[str, object]] = {}
    for window in windows:
        if not isinstance(window, Mapping):
            raise ValueError("malformed retention file: window-index.json")
        _check_identity_block(window)
        if window.get("gross_loss_usd") is not None and float(window["gross_loss_usd"]) < 0:
            raise ValueError("inconsistent trade retention: gross loss must be the positive Phase 3 magnitude")
        key = (str(window["window_name"]), float(window["slippage_pips"]))
        if key in indexed:
            raise ValueError("duplicate trade retention window")
        indexed[key] = window
    seen_keys: set[tuple[float, str, str]] = set()
    grouped: dict[tuple[str, float], list[Mapping[str, object]]] = {key: [] for key in indexed}
    for row in trades:
        key = _row_key(row, indexed)
        record = row.get("record")
        if not isinstance(record, Mapping) or not isinstance(record.get("trade_id"), str):
            raise ValueError("malformed retention file: trades.jsonl")
        identity = (key[1], key[0], str(record["trade_id"]))
        if identity in seen_keys:
            raise ValueError("duplicate trade record")
        seen_keys.add(identity)
        grouped[key].append(row)
        _check_serialized_trade(row)
    for key, window in indexed.items():
        rows = grouped[key]
        expected_ids = window.get("trade_ids")
        found_ids = [row["record"]["trade_id"] for row in rows]
        if not isinstance(expected_ids, list) or len(found_ids) < len(expected_ids):
            raise ValueError("missing trade record")
        if found_ids != expected_ids:
            raise ValueError("inconsistent trade retention: trade rows do not match the index")
        if window.get("trade_count") != len(rows):
            raise ValueError("inconsistent trade retention: trade count does not match the rows")
        _check_serialized_totals(window, rows)
    rejection_groups: dict[tuple[str, float], list[str]] = {key: [] for key in indexed}
    for row in rejections:
        key = _row_key(row, indexed)
        record = row.get("record")
        if not isinstance(record, Mapping) or not isinstance(record.get("decision_id"), str):
            raise ValueError("malformed retention file: rejections.jsonl")
        rejection_groups[key].append(str(record["decision_id"]))
    for key, window in indexed.items():
        expected = window.get("rejection_decision_ids")
        if expected != rejection_groups[key]:
            raise ValueError("inconsistent trade retention: rejection records do not match the index")


def _row_key(
    row: Mapping[str, object], indexed: Mapping[tuple[str, float], Mapping[str, object]]
) -> tuple[str, float]:
    _check_identity_block(row)
    if row.get("authentic_stage2_series_recovered") is not False:
        raise ValueError("inconsistent trade retention: the Stage 2 series is not recovered")
    try:
        key = (str(row["window_name"]), float(row["slippage_pips"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("malformed retention file") from exc
    window = indexed.get(key)
    if window is None:
        raise ValueError("inconsistent trade retention: row is outside the window index")
    for field in (
        "code_commit",
        "candidate_id",
        "experiment_id",
        "phase2_artifact_id",
        "reproduction_target_run_id",
        "reproduction_target_artifact_id",
    ):
        if row.get(field) != window.get(field):
            raise ValueError("inconsistent trade retention: source identity does not match the window")
    return key


def _check_identity_block(row: Mapping[str, object]) -> None:
    required = (
        "experiment_id",
        "code_commit",
        "candidate_id",
        "window_name",
        "slippage_pips",
        "phase2_artifact_id",
        "phase2_zip_sha256",
        "processed_manifest_sha256",
        "reproduction_target_run_id",
        "reproduction_target_artifact_id",
        "reproduction_target_code",
        "reproduction_target_result_sha256",
        "reproduction_target_windows_sha256",
        "reproduction_target_zip_sha256",
    )
    if any(field not in row for field in required):
        raise ValueError("malformed retention file")
    if row.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("inconsistent trade retention: experiment identity does not match")
    if row.get("phase2_artifact_id") != USDJPY_PHASE2_ARTIFACT_ID:
        raise ValueError("inconsistent trade retention: Phase 2 artifact identity does not match")
    if row.get("phase2_zip_sha256") != USDJPY_PHASE2_ZIP_SHA256:
        raise ValueError("inconsistent trade retention: Phase 2 ZIP identity does not match")
    if row.get("processed_manifest_sha256") != USDJPY_PROCESSED_MANIFEST_SHA256:
        raise ValueError("inconsistent trade retention: processed manifest identity does not match")
    if row.get("reproduction_target_run_id") != ORIGINAL_STAGE2_RUN_ID:
        raise ValueError("inconsistent trade retention: reproduction target does not match")
    if row.get("reproduction_target_artifact_id") != ORIGINAL_STAGE2_ARTIFACT_ID:
        raise ValueError("inconsistent trade retention: reproduction target does not match")
    if row.get("reproduction_target_result_sha256") != ORIGINAL_STAGE2_RESULT_SHA256:
        raise ValueError("inconsistent trade retention: reproduction target does not match")
    if row.get("reproduction_target_windows_sha256") != ORIGINAL_STAGE2_WINDOWS_SHA256:
        raise ValueError("inconsistent trade retention: reproduction target does not match")
    if row.get("reproduction_target_zip_sha256") != ORIGINAL_STAGE2_ZIP_SHA256:
        raise ValueError("inconsistent trade retention: reproduction target does not match")
    if row.get("reproduction_target_code") != ORIGINAL_STAGE2_CODE:
        raise ValueError("inconsistent trade retention: reproduction target does not match")


def _check_serialized_trade(row: Mapping[str, object]) -> None:
    record = row["record"]
    assert isinstance(record, Mapping)
    try:
        direction = Direction(str(record["direction"]))
        units = int(record["units"])
        gross = pnl_usd(
            symbol=str(record["symbol"]),
            direction=direction,
            units=units,
            entry_price=float(record["entry_reference_price"]),
            exit_price=float(record["exit_reference_price"]),
        )
        slipped = pnl_usd(
            symbol=str(record["symbol"]),
            direction=direction,
            units=units,
            entry_price=float(record["entry_price"]),
            exit_price=float(record["exit_price"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("malformed retention file: trades.jsonl") from exc
    slippage = max(0.0, gross - slipped)
    commission = float(record["commission_cost_usd"])
    financing = float(record["financing_cost_usd"])
    net = gross - slippage - commission - financing
    if abs(float(record["gross_pnl_usd"]) - gross) > _MONEY or abs(float(record["net_pnl_usd"]) - net) > _MONEY:
        raise ValueError("inconsistent trade retention: net PnL does not match the prices")
    if abs(float(record["slippage_cost_usd"]) - slippage) > _MONEY:
        raise ValueError("inconsistent trade retention: slippage does not match the prices")
    if row.get("spread_basis") != SPREAD_BASIS or float(row.get("spread_cost_usd", -1)) != 0.0:
        raise ValueError("inconsistent trade retention: bid/ask spread is already in the fill")
    ambiguous = record.get("intrabar_ambiguous")
    if not isinstance(ambiguous, bool):
        raise ValueError("malformed retention file: trades.jsonl")
    expected_resolution = "conservative_adverse" if ambiguous else "not_applicable"
    if row.get("intrabar_resolution") != expected_resolution:
        raise ValueError("inconsistent trade retention: intrabar resolution does not match the engine flag")
    equity = float(record["risk_equity_before_usd"])
    claimed = float(row["claimed_net_r"])
    if abs(claimed - (float(record["net_pnl_usd"]) / (equity * REQUESTED_RISK_FRACTION))) > 1e-8:
        raise ValueError("inconsistent trade retention: claimed R does not match recorded exit equity")


def _check_serialized_totals(window: Mapping[str, object], rows: Sequence[Mapping[str, object]]) -> None:
    nets = [float(row["record"]["net_pnl_usd"]) for row in rows]
    losses = [value for value in nets if value < 0]
    gross_profit = math.fsum(value for value in nets if value > 0)
    gross_loss = -math.fsum(losses)
    if abs(float(window["gross_profit_usd"]) - gross_profit) > _MONEY:
        raise ValueError("inconsistent trade retention: gross profit does not match the rows")
    if float(window["gross_loss_usd"]) < 0 or abs(float(window["gross_loss_usd"]) - gross_loss) > _MONEY:
        raise ValueError("inconsistent trade retention: gross loss must be the positive Phase 3 magnitude")
    if abs(float(window["net_pnl_usd"]) - math.fsum(nets)) > _MONEY:
        raise ValueError("inconsistent trade retention: net PnL does not match the rows")
    for field, record_field in (
        ("slippage_cost_usd", "slippage_cost_usd"),
        ("commission_cost_usd", "commission_cost_usd"),
        ("financing_cost_usd", "financing_cost_usd"),
    ):
        total = math.fsum(float(row["record"][record_field]) for row in rows)
        if abs(float(window[field]) - total) > _MONEY:
            raise ValueError("inconsistent trade retention: cost total does not match the rows")


def _submissions(
    manifest: Mapping[str, object],
    windows: Sequence[object],
    trades: Sequence[Mapping[str, object]],
) -> tuple[TradeSubmission, ...]:
    by_slippage: dict[float, list[Mapping[str, object]]] = {}
    for window in windows:
        assert isinstance(window, Mapping)
        by_slippage.setdefault(float(window["slippage_pips"]), []).append(window)
    submissions: list[TradeSubmission] = []
    for slippage in sorted(by_slippage):
        selected = by_slippage[slippage]
        window_names = {str(window["window_name"]) for window in selected}
        trade_rows = [
            row
            for row in trades
            if float(row["slippage_pips"]) == slippage and str(row["window_name"]) in window_names
        ]
        submissions.append(
            TradeSubmission(
                provenance=EvidenceProvenance(
                    role=str(manifest["provenance_role"]),
                    label=str(manifest["provenance_label"]),
                    source_run_id=_optional_str(manifest.get("source_run_id")),
                    source_artifact_id=_optional_str(manifest.get("source_artifact_id")),
                    source_commit=_optional_str(manifest.get("source_commit")),
                ),
                requested_risk_fraction=REQUESTED_RISK_FRACTION,
                windows=tuple(_aggregate(window) for window in selected),
                trades=tuple(_submitted(row) for row in trade_rows),
                expected_trade_ids=tuple(
                    trade_id
                    for window in selected
                    for trade_id in window["trade_ids"]
                ),
                claims_trades_from_stage2_zip=False,
            )
        )
    return tuple(submissions)


def _aggregate(window: Mapping[str, object]) -> WindowAggregate:
    return WindowAggregate(
        window_id=str(window["window_name"]),
        start_utc=_parse_utc(window["scored_start_utc"]),
        end_exclusive_utc=_parse_utc(window["scored_end_utc"]),
        starting_equity_usd=float(window["starting_equity_usd"]),
        trade_count=int(window["trade_count"]),
        net_pnl_usd=float(window["net_pnl_usd"]),
        gross_profit_usd=float(window["gross_profit_usd"]),
        gross_loss_usd=float(window["gross_loss_usd"]),
        slippage_cost_usd=float(window["slippage_cost_usd"]),
        commission_cost_usd=float(window["commission_cost_usd"]),
        financing_cost_usd=float(window["financing_cost_usd"]),
        overlap_role="none",
    )


def _submitted(row: Mapping[str, object]) -> SubmittedTrade:
    record = row["record"]
    assert isinstance(record, Mapping)
    return SubmittedTrade(
        trade_id=str(record["trade_id"]),
        decision_id=str(record["decision_id"]),
        window_id=str(row["window_name"]),
        symbol=str(record["symbol"]),
        direction=str(record["direction"]),
        units=int(record["units"]),
        entry_timestamp_utc=_parse_utc(record["entry_timestamp_utc"]),
        exit_timestamp_utc=_parse_utc(record["exit_timestamp_utc"]),
        entry_reference_price=float(record["entry_reference_price"]),
        exit_reference_price=float(record["exit_reference_price"]),
        entry_price=float(record["entry_price"]),
        exit_price=float(record["exit_price"]),
        stop_price=float(record["stop_price"]),
        target_price=None if record.get("target_price") is None else float(record["target_price"]),
        exit_reason=str(record["exit_reason"]),
        intrabar_ambiguous=bool(record["intrabar_ambiguous"]),
        intrabar_resolution=str(row["intrabar_resolution"]),
        gross_pnl_usd=float(record["gross_pnl_usd"]),
        slippage_cost_usd=float(record["slippage_cost_usd"]),
        commission_cost_usd=float(record["commission_cost_usd"]),
        financing_cost_usd=float(record["financing_cost_usd"]),
        spread_cost_usd=0.0,
        spread_basis=SPREAD_BASIS,
        net_pnl_usd=float(record["net_pnl_usd"]),
        risk_equity_before_usd=float(record["risk_equity_before_usd"]),
        risk_equity_after_usd=float(record["risk_equity_after_usd"]),
        claimed_net_r=float(row["claimed_net_r"]),
    )


def _parse_utc(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("malformed retention timestamp")
    text = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError("malformed retention timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("malformed retention timestamp")
    return parsed


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError("malformed retention manifest")
    return value
