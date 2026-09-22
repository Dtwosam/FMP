from __future__ import annotations

import hashlib
import json
import math
import os
import re
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Callable, Mapping

from fmp.contracts import SUPPORTED_SYMBOLS
from fmp.research.data import ELIGIBLE_TIMEFRAMES

from .challengers import EXP013_ID, build_opening_range_momentum_challengers
from .research_data import (
    LoadedRetrospectiveBars,
    PHASE8A_RETROSPECTIVE_LABEL,
    RetrospectiveRange,
    load_phase8a_retrospective_bars,
)
from .research_runner import (
    SLIPPAGE_SCENARIOS,
    Phase8ARetrospectivePlan,
    run_phase8a_retrospective_strategy,
)

EXP013_STAGE_A_CELL_PROTOCOL = "fmp-phase8a-exp013-stage-a-cell-v1"
EXP013_STAGE_A_GATE_PROTOCOL = "fmp-phase8a-exp013-stage-a-gate-v1"
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

def opening_range_momentum_source_sha256() -> str:
    source_path = (
        Path(__file__).resolve().parents[1]
        / "strategies"
        / "opening_range_momentum.py"
    )
    try:
        payload = source_path.read_bytes()
    except OSError as exc:
        raise ValueError(
            "cannot read opening_range_momentum strategy source"
        ) from exc
    return hashlib.sha256(payload).hexdigest()


_STAGE_A_RANGES = {
    "development": RetrospectiveRange(
        start=date(2015, 1, 1),
        end_exclusive=date(2021, 1, 1),
    ),
    "validation": RetrospectiveRange(
        start=date(2021, 1, 1),
        end_exclusive=date(2024, 1, 1),
    ),
}


def _stage_a_range(split_name: str) -> RetrospectiveRange:
    try:
        return _STAGE_A_RANGES[split_name]
    except KeyError as exc:
        raise ValueError(
            "EXP-013 Stage A split_name must be 'development' or 'validation'"
        ) from exc


def _validate_loaded(
    loaded: LoadedRetrospectiveBars,
    *,
    research_range: RetrospectiveRange,
    symbol: str,
) -> None:
    if loaded.evidence_label != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-013 Stage A source must be explicitly retrospective")
    if loaded.start != research_range.start or loaded.end_exclusive != research_range.end_exclusive:
        raise ValueError("EXP-013 loaded range does not match frozen Stage A split")
    if not loaded.bars:
        raise ValueError("EXP-013 Stage A requires at least one complete signal bar")
    symbols = {item.symbol for item in loaded.bars}
    if symbols != {symbol}:
        raise ValueError("EXP-013 Stage A source bars do not match requested symbol")


def run_exp013_stage_a_cell(
    *,
    dataset_root: Path,
    manifest_path: Path,
    symbol: str,
    timeframe: str,
    split_name: str,
    code_commit: str,
    bars_loader: Callable[..., LoadedRetrospectiveBars] = load_phase8a_retrospective_bars,
    strategy_runner: Callable[..., Mapping[str, object]] = run_phase8a_retrospective_strategy,
) -> dict[str, object]:
    # Resolve and validate every protocol input before source I/O.
    research_range = _stage_a_range(split_name)
    if symbol not in SUPPORTED_SYMBOLS:
        raise ValueError(f"unsupported EXP-013 symbol: {symbol!r}")
    if timeframe not in ELIGIBLE_TIMEFRAMES:
        raise ValueError(f"unsupported EXP-013 signal timeframe: {timeframe!r}")
    if not _COMMIT_RE.fullmatch(code_commit):
        raise ValueError("code_commit must be a 40-character lowercase hexadecimal SHA")

    strategy_source_sha256 = opening_range_momentum_source_sha256()

    records = tuple(
        item
        for item in build_opening_range_momentum_challengers(code_commit=code_commit)
        if item.strategy.symbol == symbol and item.strategy.timeframe == timeframe
    )
    if len(records) != 4:
        raise RuntimeError("EXP-013 pair/timeframe cell must contain exactly four challengers")

    loaded = bars_loader(
        dataset_root=Path(dataset_root),
        manifest_path=Path(manifest_path),
        symbol=symbol,
        timeframe=timeframe,
        research_range=research_range,
    )
    _validate_loaded(loaded, research_range=research_range, symbol=symbol)

    rows: list[dict[str, object]] = []
    for record in sorted(records, key=lambda item: item.strategy.fingerprint):
        expected_candidate_sha: str | None = None
        for slippage_pips in SLIPPAGE_SCENARIOS:
            plan = Phase8ARetrospectivePlan(
                experiment_id=EXP013_ID,
                strategy=record.strategy,
                research_range=research_range,
                slippage_pips=slippage_pips,
                runner_code_commit=code_commit,
            )
            result = dict(
                strategy_runner(
                    plan=plan,
                    dataset_root=Path(dataset_root),
                    manifest_path=Path(manifest_path),
                    bars_loader=lambda **_: loaded,
                )
            )
            if result.get("strategy_fingerprint") != record.strategy.fingerprint:
                raise ValueError("EXP-013 strategy runner returned the wrong strategy identity")
            if result.get("processed_manifest_sha256") != loaded.processed_manifest_sha256:
                raise ValueError("EXP-013 strategy runner returned the wrong manifest identity")
            candidate_sha = result.get("candidate_sha256")
            if not isinstance(candidate_sha, str) or not candidate_sha:
                raise ValueError("EXP-013 strategy runner omitted candidate_sha256")
            if expected_candidate_sha is None:
                expected_candidate_sha = candidate_sha
            elif candidate_sha != expected_candidate_sha:
                raise ValueError(
                    "EXP-013 candidate sequence changed across slippage scenarios"
                )

            metrics = result.get("metrics")
            run_identity = result.get("run_identity")
            if not isinstance(metrics, Mapping) or not isinstance(run_identity, Mapping):
                raise ValueError("EXP-013 strategy runner returned malformed evidence")

            rows.append(
                {
                    "strategy_fingerprint": record.strategy.fingerprint,
                    "strategy_identity_json": record.strategy.identity_json,
                    "family": record.strategy.family,
                    "version": record.strategy.version,
                    "parameters_json": record.strategy.parameters_json,
                    "historical_lifecycle": record.lifecycle.value,
                    "historical_evidence_id": record.evidence_id,
                    "slippage_pips": slippage_pips,
                    "candidate_sha256": candidate_sha,
                    "run_identity": dict(run_identity),
                    "metrics": dict(metrics),
                }
            )

    return {
        "protocol": EXP013_STAGE_A_CELL_PROTOCOL,
        "experiment_id": EXP013_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "split_name": split_name,
        "range_start": research_range.start.isoformat(),
        "range_end_exclusive": research_range.end_exclusive.isoformat(),
        "runner_code_commit": code_commit,
        "strategy_source_sha256": strategy_source_sha256,
        "processed_manifest_sha256": loaded.processed_manifest_sha256,
        "opened_artifact_months": list(loaded.opened_artifact_months),
        "strategy_identity_count": len(records),
        "scenario_run_count": len(rows),
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "rows": rows,
    }


def _validate_stage_a_cell(
    value: Mapping[str, object],
    *,
    expected_split: str,
) -> tuple[str, str, str, dict[str, dict[float, Mapping[str, object]]]]:
    if value.get("protocol") != EXP013_STAGE_A_CELL_PROTOCOL:
        raise ValueError("EXP-013 Stage A cell protocol mismatch")
    if value.get("experiment_id") != EXP013_ID:
        raise ValueError("EXP-013 experiment identity mismatch")
    if value.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-013 Stage A cell is not retrospective")
    if value.get("untouched_oos") is not False:
        raise ValueError("EXP-013 Stage A cannot be marked untouched OOS")
    if value.get("promotion_authorized") is not False:
        raise ValueError("EXP-013 Stage A cell cannot authorize promotion")
    if value.get("split_name") != expected_split:
        raise ValueError(f"expected EXP-013 {expected_split} cell")

    symbol = value.get("symbol")
    timeframe = value.get("timeframe")
    code_commit = value.get("runner_code_commit")
    if not isinstance(symbol, str) or symbol not in SUPPORTED_SYMBOLS:
        raise ValueError("invalid EXP-013 Stage A symbol")
    if not isinstance(timeframe, str) or timeframe not in ELIGIBLE_TIMEFRAMES:
        raise ValueError("invalid EXP-013 Stage A timeframe")
    if not isinstance(code_commit, str) or not _COMMIT_RE.fullmatch(code_commit):
        raise ValueError("invalid EXP-013 Stage A runner commit")

    raw_rows = value.get("rows")
    if not isinstance(raw_rows, list):
        raise ValueError("EXP-013 Stage A rows must be a list")

    indexed: dict[str, dict[float, Mapping[str, object]]] = {}
    parameter_identity: dict[str, str] = {}
    for row in raw_rows:
        if not isinstance(row, Mapping):
            raise ValueError("EXP-013 Stage A row must be an object")
        fingerprint = row.get("strategy_fingerprint")
        params = row.get("parameters_json")
        slippage = row.get("slippage_pips")
        if not isinstance(fingerprint, str) or not fingerprint:
            raise ValueError("EXP-013 row strategy fingerprint is missing")
        if not isinstance(params, str):
            raise ValueError("EXP-013 row parameters_json is missing")
        if not isinstance(slippage, (int, float)) or isinstance(slippage, bool):
            raise ValueError("EXP-013 row slippage is invalid")
        slippage_value = float(slippage)
        if slippage_value not in SLIPPAGE_SCENARIOS:
            raise ValueError("EXP-013 row has unsupported slippage")
        if fingerprint in parameter_identity and parameter_identity[fingerprint] != params:
            raise ValueError("EXP-013 strategy parameters changed within cell")
        parameter_identity[fingerprint] = params
        bucket = indexed.setdefault(fingerprint, {})
        if slippage_value in bucket:
            raise ValueError("duplicate EXP-013 strategy/slippage row")
        bucket[slippage_value] = row

    if len(indexed) != 4:
        raise ValueError("EXP-013 Stage A cell must contain exactly four strategies")
    if any(set(rows) != set(SLIPPAGE_SCENARIOS) for rows in indexed.values()):
        raise ValueError("EXP-013 Stage A strategy is missing a slippage scenario")
    return symbol, timeframe, code_commit, indexed


def _mandatory_metrics_pass(row: Mapping[str, object]) -> bool:
    metrics = row.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("EXP-013 row metrics are missing")
    phase3 = metrics.get("phase3_metrics")
    if not isinstance(phase3, Mapping):
        raise ValueError("EXP-013 phase3_metrics are missing")

    net_return = phase3.get("net_return")
    expectancy = phase3.get("expectancy_usd")
    profit_factor = phase3.get("profit_factor")
    max_drawdown = phase3.get("max_drawdown_fraction")
    values = (net_return, expectancy, profit_factor, max_drawdown)
    if any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in values):
        return False
    return (
        float(net_return) > 0.0
        and float(expectancy) > 0.0
        and float(profit_factor) > 1.0
        and float(max_drawdown) <= 0.05
    )


def _trade_count(row: Mapping[str, object]) -> int:
    metrics = row.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("EXP-013 row metrics are missing")
    value = metrics.get("trade_count")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("EXP-013 trade_count must be a non-negative integer")
    return value


def _parameters(row: Mapping[str, object]) -> dict[str, float]:
    raw = row.get("parameters_json")
    if not isinstance(raw, str):
        raise ValueError("EXP-013 row parameters_json is missing")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("EXP-013 parameters_json is malformed") from exc
    expected = {"body_fraction_threshold", "target_r_multiple"}
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("EXP-013 parameters do not match frozen grid")
    body = value["body_fraction_threshold"]
    target = value["target_r_multiple"]
    if body not in (0.5, 0.7) or target not in (1.0, 1.5):
        raise ValueError("EXP-013 parameters are outside the frozen grid")
    return {
        "body_fraction_threshold": float(body),
        "target_r_multiple": float(target),
    }


def _are_neighbors(left: Mapping[str, float], right: Mapping[str, float]) -> bool:
    body_diff = left["body_fraction_threshold"] != right["body_fraction_threshold"]
    target_diff = left["target_r_multiple"] != right["target_r_multiple"]
    return body_diff ^ target_diff


def evaluate_exp013_stage_a_cell_pair(
    *,
    development: Mapping[str, object],
    validation: Mapping[str, object],
) -> dict[str, object]:
    dev_symbol, dev_timeframe, dev_commit, dev_rows = _validate_stage_a_cell(
        development,
        expected_split="development",
    )
    val_symbol, val_timeframe, val_commit, val_rows = _validate_stage_a_cell(
        validation,
        expected_split="validation",
    )
    if (dev_symbol, dev_timeframe, dev_commit) != (
        val_symbol,
        val_timeframe,
        val_commit,
    ):
        raise ValueError("EXP-013 development/validation cell identity mismatch")
    if set(dev_rows) != set(val_rows):
        raise ValueError("EXP-013 development/validation strategy identities differ")

    core_pass: dict[str, bool] = {}
    sample_pass: dict[str, bool] = {}
    params: dict[str, dict[str, float]] = {}

    for fingerprint in sorted(dev_rows):
        for slippage in SLIPPAGE_SCENARIOS:
            if (
                dev_rows[fingerprint][slippage].get("parameters_json")
                != val_rows[fingerprint][slippage].get("parameters_json")
            ):
                raise ValueError("EXP-013 parameters changed across Stage A splits")
        params[fingerprint] = _parameters(dev_rows[fingerprint][0.2])

        mandatory_rows = (
            dev_rows[fingerprint][0.2],
            dev_rows[fingerprint][0.5],
            val_rows[fingerprint][0.2],
            val_rows[fingerprint][0.5],
        )
        core_pass[fingerprint] = all(
            _mandatory_metrics_pass(row) for row in mandatory_rows
        )
        sample_pass[fingerprint] = (
            _trade_count(dev_rows[fingerprint][0.2]) >= 100
            and _trade_count(val_rows[fingerprint][0.2]) >= 50
        )

    config_gates: dict[str, dict[str, object]] = {}
    survivors: list[str] = []
    for fingerprint in sorted(dev_rows):
        passing_neighbors = [
            other
            for other in sorted(dev_rows)
            if other != fingerprint
            and core_pass[other]
            and _are_neighbors(params[fingerprint], params[other])
        ]
        neighbor_pass = bool(passing_neighbors)
        survivor = core_pass[fingerprint] and sample_pass[fingerprint] and neighbor_pass
        if survivor:
            survivors.append(fingerprint)
        config_gates[fingerprint] = {
            "parameters": params[fingerprint],
            "mandatory_profitability_drawdown_pass": core_pass[fingerprint],
            "sample_pass": sample_pass[fingerprint],
            "neighbor_pass": neighbor_pass,
            "passing_neighbor_fingerprints": passing_neighbors,
            "stage_a_survivor": survivor,
        }

    return {
        "protocol": EXP013_STAGE_A_GATE_PROTOCOL,
        "experiment_id": EXP013_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": dev_symbol,
        "timeframe": dev_timeframe,
        "runner_code_commit": dev_commit,
        "survivor_fingerprints": survivors,
        "config_gates": config_gates,
    }


EXP013_STAGE_A_CELL_ARTIFACT_PROTOCOL = "fmp-phase8a-exp013-stage-a-cell-artifacts-v1"
EXP013_STAGE_A_AUTHORIZATION_PROTOCOL = "fmp-phase8a-exp013-stage-a-authorization-v1"
EXP013_STAGE_A_AUTHORIZATION_ARTIFACT_PROTOCOL = (
    "fmp-phase8a-exp013-stage-a-authorization-artifacts-v1"
)


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
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("cannot serialize non-finite float")
        return value
    if value is None or isinstance(value, (str, int, bool)):
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


def write_exp013_stage_a_cell_artifacts(
    *,
    development: Mapping[str, object],
    validation: Mapping[str, object],
    gate: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    if development.get("protocol") != EXP013_STAGE_A_CELL_PROTOCOL:
        raise ValueError("EXP-013 development artifact protocol mismatch")
    if validation.get("protocol") != EXP013_STAGE_A_CELL_PROTOCOL:
        raise ValueError("EXP-013 validation artifact protocol mismatch")
    if gate.get("protocol") != EXP013_STAGE_A_GATE_PROTOCOL:
        raise ValueError("EXP-013 gate artifact protocol mismatch")
    if development.get("split_name") != "development":
        raise ValueError("EXP-013 development artifact has wrong split")
    if validation.get("split_name") != "validation":
        raise ValueError("EXP-013 validation artifact has wrong split")
    if development.get("range_start") != "2015-01-01":
        raise ValueError("EXP-013 development range start drift")
    if development.get("range_end_exclusive") != "2021-01-01":
        raise ValueError("EXP-013 development range end drift")
    if validation.get("range_start") != "2021-01-01":
        raise ValueError("EXP-013 validation range start drift")
    if validation.get("range_end_exclusive") != "2024-01-01":
        raise ValueError("EXP-013 validation range end drift")
    identities = {
        (
            value.get("symbol"),
            value.get("timeframe"),
            value.get("runner_code_commit"),
        )
        for value in (development, validation, gate)
    }
    if len(identities) != 1:
        raise ValueError("EXP-013 Stage A artifact identity mismatch")
    if any(value.get("promotion_authorized") is not False for value in (development, validation, gate)):
        raise ValueError("EXP-013 Stage A artifacts cannot authorize promotion")

    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    payloads = {
        "development.json": _stable_json_bytes(dict(development)),
        "validation.json": _stable_json_bytes(dict(validation)),
        "gate.json": _stable_json_bytes(dict(gate)),
    }
    for name, payload in payloads.items():
        _atomic_write(root / name, payload)

    manifest = {
        "protocol": EXP013_STAGE_A_CELL_ARTIFACT_PROTOCOL,
        "experiment_id": EXP013_ID,
        "promotion_authorized": False,
        "artifacts": [
            _artifact_record(root / name)
            for name in sorted(payloads)
        ],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


def _validate_exp013_stage_a_gate(
    value: Mapping[str, object],
) -> tuple[str, str, str, tuple[str, ...], tuple[str, ...]]:
    if value.get("protocol") != EXP013_STAGE_A_GATE_PROTOCOL:
        raise ValueError("EXP-013 Stage A gate protocol mismatch")
    if value.get("experiment_id") != EXP013_ID:
        raise ValueError("EXP-013 Stage A gate experiment mismatch")
    if value.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-013 Stage A gate must be retrospective")
    if value.get("untouched_oos") is not False:
        raise ValueError("EXP-013 Stage A gate cannot be untouched OOS")
    if value.get("promotion_authorized") is not False:
        raise ValueError("EXP-013 Stage A gate cannot authorize promotion")
    if value.get("historical_status_mutation_authorized") is not False:
        raise ValueError("EXP-013 Stage A gate cannot mutate historical status")

    symbol = value.get("symbol")
    timeframe = value.get("timeframe")
    code_commit = value.get("runner_code_commit")
    if not isinstance(symbol, str) or symbol not in SUPPORTED_SYMBOLS:
        raise ValueError("invalid EXP-013 Stage A gate symbol")
    if not isinstance(timeframe, str) or timeframe not in ELIGIBLE_TIMEFRAMES:
        raise ValueError("invalid EXP-013 Stage A gate timeframe")
    if not isinstance(code_commit, str) or not _COMMIT_RE.fullmatch(code_commit):
        raise ValueError("invalid EXP-013 Stage A gate runner commit")

    raw_config_gates = value.get("config_gates")
    if not isinstance(raw_config_gates, Mapping) or len(raw_config_gates) != 4:
        raise ValueError("EXP-013 Stage A gate must contain exactly four configs")
    fingerprints = tuple(sorted(str(item) for item in raw_config_gates))
    if len(set(fingerprints)) != 4:
        raise ValueError("EXP-013 Stage A gate has duplicate strategy identities")
    if any(not re.fullmatch(r"[0-9a-f]{64}", item) for item in fingerprints):
        raise ValueError("EXP-013 Stage A gate has invalid strategy fingerprint")

    raw_survivors = value.get("survivor_fingerprints")
    if not isinstance(raw_survivors, list):
        raise ValueError("EXP-013 Stage A survivor_fingerprints must be a list")
    survivors = tuple(sorted(str(item) for item in raw_survivors))
    if len(set(survivors)) != len(survivors):
        raise ValueError("EXP-013 Stage A survivor list contains duplicates")
    if not set(survivors).issubset(set(fingerprints)):
        raise ValueError("EXP-013 Stage A survivor is outside its frozen cell")
    for fingerprint in fingerprints:
        gate = raw_config_gates[fingerprint]
        if not isinstance(gate, Mapping):
            raise ValueError("EXP-013 Stage A config gate must be an object")
        expected = fingerprint in survivors
        if gate.get("stage_a_survivor") is not expected:
            raise ValueError("EXP-013 Stage A survivor flag/list mismatch")

    return symbol, timeframe, code_commit, fingerprints, survivors


def aggregate_exp013_stage_a_gates(
    gates: list[Mapping[str, object]] | tuple[Mapping[str, object], ...],
) -> dict[str, object]:
    materialized = tuple(gates)
    if len(materialized) != 9:
        raise ValueError("EXP-013 Stage A authorization requires exactly nine cell gates")

    expected_cells = {
        (symbol, timeframe)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY")
        for timeframe in ("5m", "15m", "1h")
    }
    seen_cells: set[tuple[str, str]] = set()
    commits: set[str] = set()
    all_fingerprints: set[str] = set()
    survivors: set[str] = set()
    cells: list[dict[str, object]] = []

    for gate in materialized:
        symbol, timeframe, code_commit, fingerprints, cell_survivors = (
            _validate_exp013_stage_a_gate(gate)
        )
        cell = (symbol, timeframe)
        if cell in seen_cells:
            raise ValueError("duplicate EXP-013 Stage A cell gate")
        seen_cells.add(cell)
        commits.add(code_commit)
        if all_fingerprints.intersection(fingerprints):
            raise ValueError("EXP-013 Stage A strategy identity appears in multiple cells")
        all_fingerprints.update(fingerprints)
        survivors.update(cell_survivors)
        cells.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "strategy_fingerprints": list(fingerprints),
                "survivor_fingerprints": list(cell_survivors),
            }
        )

    if seen_cells != expected_cells:
        raise ValueError("EXP-013 Stage A authorization cell coverage mismatch")
    if len(commits) != 1:
        raise ValueError("EXP-013 Stage A gate runner commits differ")
    if len(all_fingerprints) != 36:
        raise ValueError("EXP-013 Stage A authorization must bind exactly 36 strategies")

    ordered_survivors = sorted(survivors)
    return {
        "protocol": EXP013_STAGE_A_AUTHORIZATION_PROTOCOL,
        "experiment_id": EXP013_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "runner_code_commit": next(iter(commits)),
        "cell_count": 9,
        "strategy_identity_count": 36,
        "survivor_count": len(ordered_survivors),
        "survivor_fingerprints": ordered_survivors,
        "stage_b_source_open_authorized": bool(ordered_survivors),
        "cells": sorted(cells, key=lambda item: (str(item["symbol"]), str(item["timeframe"]))),
    }


def write_exp013_stage_a_authorization_artifacts(
    authorization: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    if authorization.get("protocol") != EXP013_STAGE_A_AUTHORIZATION_PROTOCOL:
        raise ValueError("EXP-013 Stage A authorization protocol mismatch")
    if authorization.get("promotion_authorized") is not False:
        raise ValueError("EXP-013 Stage A authorization cannot authorize promotion")

    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / "authorization.json"
    payload = _stable_json_bytes(dict(authorization))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": EXP013_STAGE_A_AUTHORIZATION_ARTIFACT_PROTOCOL,
        "experiment_id": EXP013_ID,
        "promotion_authorized": False,
        "artifacts": [_artifact_record(result_path)],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest
