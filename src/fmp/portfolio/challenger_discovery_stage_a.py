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
from typing import Callable, Mapping, Sequence

from fmp.contracts import SUPPORTED_SYMBOLS
from fmp.research.data import ELIGIBLE_TIMEFRAMES

from .challenger_discovery import EXP015_ID, build_exp015_challengers
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
from .selection import annualized_compounded_return

EXP015_STAGE_A_CELL_PROTOCOL = "fmp-phase8a-exp015-stage-a-cell-v1"
EXP015_STAGE_A_GATE_PROTOCOL = "fmp-phase8a-exp015-stage-a-gate-v1"
EXP015_STAGE_A_AUTHORIZATION_PROTOCOL = "fmp-phase8a-exp015-stage-a-authorization-v1"
EXP015_STAGE_A_CELL_ARTIFACT_PROTOCOL = "fmp-phase8a-exp015-stage-a-cell-artifacts-v1"
EXP015_STAGE_A_AUTHORIZATION_ARTIFACT_PROTOCOL = (
    "fmp-phase8a-exp015-stage-a-authorization-artifacts-v1"
)

_STAGE_A_RANGE = RetrospectiveRange(
    start=date(2015, 1, 1),
    end_exclusive=date(2019, 1, 1),
)
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_FAMILIES = (
    "mean_reversion",
    "previous_day_rejection",
    "session_breakout",
    "session_sweep_rejection",
    "trend_continuation",
    "volatility_breakout",
)
_STRATEGY_SOURCE_FILES = (
    "mean_reversion.py",
    "previous_day_rejection.py",
    "session_breakout.py",
    "session_sweep_rejection.py",
    "trend_continuation.py",
    "volatility_breakout.py",
)


def exp015_strategy_source_sha256() -> str:
    root = Path(__file__).resolve().parents[1] / "strategies"
    digest = hashlib.sha256()
    for name in _STRATEGY_SOURCE_FILES:
        path = root / name
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise ValueError(f"cannot read EXP-015 strategy source: {path}") from exc
        encoded_name = name.encode("utf-8")
        digest.update(len(encoded_name).to_bytes(4, "big"))
        digest.update(encoded_name)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def _validate_commit(value: str) -> None:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError("code_commit must be a 40-character lowercase hexadecimal SHA")


def _cell_records(*, symbol: str, timeframe: str, code_commit: str):
    _validate_commit(code_commit)
    if symbol not in SUPPORTED_SYMBOLS:
        raise ValueError(f"unsupported EXP-015 symbol: {symbol!r}")
    if timeframe not in ELIGIBLE_TIMEFRAMES:
        raise ValueError(f"unsupported EXP-015 timeframe: {timeframe!r}")
    records = tuple(
        item
        for item in build_exp015_challengers(code_commit=code_commit)
        if item.strategy.symbol == symbol and item.strategy.timeframe == timeframe
    )
    if len(records) != 63:
        raise RuntimeError("EXP-015 Stage A cell must contain exactly 63 strategies")
    return records


def _validate_loaded(
    loaded: LoadedRetrospectiveBars,
    *,
    symbol: str,
) -> None:
    if loaded.evidence_label != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-015 Stage A source must be explicitly retrospective")
    if loaded.start != _STAGE_A_RANGE.start or loaded.end_exclusive != _STAGE_A_RANGE.end_exclusive:
        raise ValueError("EXP-015 Stage A loaded range does not match frozen range")
    if not loaded.bars:
        raise ValueError("EXP-015 Stage A requires at least one complete signal bar")
    if {item.symbol for item in loaded.bars} != {symbol}:
        raise ValueError("EXP-015 Stage A source bars do not match requested symbol")
    if not _SHA256_RE.fullmatch(loaded.processed_manifest_sha256):
        raise ValueError("EXP-015 Stage A processed manifest identity is malformed")


def run_exp015_stage_a_cell(
    *,
    dataset_root: Path,
    manifest_path: Path,
    symbol: str,
    timeframe: str,
    code_commit: str,
    bars_loader: Callable[..., LoadedRetrospectiveBars] = load_phase8a_retrospective_bars,
    strategy_runner: Callable[..., Mapping[str, object]] = run_phase8a_retrospective_strategy,
) -> dict[str, object]:
    records = _cell_records(
        symbol=symbol,
        timeframe=timeframe,
        code_commit=code_commit,
    )
    loaded = bars_loader(
        dataset_root=Path(dataset_root),
        manifest_path=Path(manifest_path),
        symbol=symbol,
        timeframe=timeframe,
        research_range=_STAGE_A_RANGE,
    )
    _validate_loaded(loaded, symbol=symbol)

    rows: list[dict[str, object]] = []
    for record in records:
        expected_candidate_sha: str | None = None
        for slippage_pips in SLIPPAGE_SCENARIOS:
            plan = Phase8ARetrospectivePlan(
                experiment_id=EXP015_ID,
                strategy=record.strategy,
                research_range=_STAGE_A_RANGE,
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
                raise ValueError("EXP-015 Stage A runner returned wrong strategy identity")
            if result.get("processed_manifest_sha256") != loaded.processed_manifest_sha256:
                raise ValueError("EXP-015 Stage A runner returned wrong manifest identity")
            if result.get("slippage_pips") != slippage_pips:
                raise ValueError("EXP-015 Stage A runner returned wrong slippage identity")

            candidate_sha = result.get("candidate_sha256")
            if not isinstance(candidate_sha, str) or not _SHA256_RE.fullmatch(candidate_sha):
                raise ValueError("EXP-015 Stage A runner omitted valid candidate SHA-256")
            if expected_candidate_sha is None:
                expected_candidate_sha = candidate_sha
            elif candidate_sha != expected_candidate_sha:
                raise ValueError(
                    "EXP-015 Stage A candidate sequence changed across slippage scenarios"
                )

            metrics = result.get("metrics")
            run_identity = result.get("run_identity")
            if not isinstance(metrics, Mapping) or not isinstance(run_identity, Mapping):
                raise ValueError("EXP-015 Stage A runner returned malformed evidence")

            rows.append(
                {
                    "strategy_fingerprint": record.strategy.fingerprint,
                    "strategy_identity_json": record.strategy.identity_json,
                    "family": record.strategy.family,
                    "symbol": record.strategy.symbol,
                    "timeframe": record.strategy.timeframe,
                    "parameters_json": record.strategy.parameters_json,
                    "slippage_pips": slippage_pips,
                    "candidate_sha256": candidate_sha,
                    "run_identity": dict(run_identity),
                    "metrics": dict(metrics),
                }
            )

    return {
        "protocol": EXP015_STAGE_A_CELL_PROTOCOL,
        "experiment_id": EXP015_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "runner_code_commit": code_commit,
        "strategy_source_sha256": exp015_strategy_source_sha256(),
        "processed_manifest_sha256": loaded.processed_manifest_sha256,
        "opened_artifact_months": list(loaded.opened_artifact_months),
        "range_start": _STAGE_A_RANGE.start.isoformat(),
        "range_end_exclusive": _STAGE_A_RANGE.end_exclusive.isoformat(),
        "strategy_identity_count": len(records),
        "scenario_run_count": len(rows),
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "strategy_fingerprints": sorted(
            item.strategy.fingerprint for item in records
        ),
        "rows": rows,
    }


def _phase3_metrics(row: Mapping[str, object]) -> Mapping[str, object]:
    metrics = row.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("EXP-015 Stage A row metrics are missing")
    phase3 = metrics.get("phase3_metrics")
    if not isinstance(phase3, Mapping):
        raise ValueError("EXP-015 Stage A phase3_metrics are missing")
    return phase3


def _trade_count(row: Mapping[str, object]) -> int:
    metrics = row.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("EXP-015 Stage A row metrics are missing")
    value = metrics.get("trade_count")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("EXP-015 Stage A trade_count must be a non-negative integer")
    return value


def _numeric_metric(phase3: Mapping[str, object], key: str) -> float | None:
    value = phase3.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"EXP-015 Stage A metric {key!r} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"EXP-015 Stage A metric {key!r} must be finite")
    return number


def _scenario_gate(row: Mapping[str, object]) -> bool:
    phase3 = _phase3_metrics(row)
    net_return = _numeric_metric(phase3, "net_return")
    expectancy = _numeric_metric(phase3, "expectancy_usd")
    profit_factor = _numeric_metric(phase3, "profit_factor")
    max_drawdown = _numeric_metric(phase3, "max_drawdown_fraction")
    if None in (net_return, expectancy, profit_factor, max_drawdown):
        return False
    return (
        float(net_return) > 0.0
        and float(expectancy) > 0.0
        and float(profit_factor) > 1.05
        and float(max_drawdown) <= 0.05
        and _trade_count(row) >= 40
    )


def _annualized(row: Mapping[str, object]) -> float:
    phase3 = _phase3_metrics(row)
    net_return = _numeric_metric(phase3, "net_return")
    if net_return is None or net_return <= -1.0:
        raise ValueError("EXP-015 Stage A net return cannot be annualized")
    return annualized_compounded_return(
        starting_equity_usd=100_000.0,
        ending_equity_usd=100_000.0 * (1.0 + net_return),
        start=_STAGE_A_RANGE.start,
        end_exclusive=_STAGE_A_RANGE.end_exclusive,
    )


def _rank_key(
    fingerprint: str,
    scenarios: Mapping[float, Mapping[str, object]],
) -> tuple[object, ...]:
    s02 = scenarios[0.2]
    s05 = scenarios[0.5]
    pf05 = _numeric_metric(_phase3_metrics(s05), "profit_factor")
    dd05 = _numeric_metric(_phase3_metrics(s05), "max_drawdown_fraction")
    if pf05 is None or dd05 is None:
        raise ValueError("EXP-015 Stage A passing row lacks ranking metrics")
    return (
        -_annualized(s05),
        dd05,
        -pf05,
        -_annualized(s02),
        fingerprint,
    )


def evaluate_exp015_stage_a_cell(
    cell: Mapping[str, object],
) -> dict[str, object]:
    if cell.get("protocol") != EXP015_STAGE_A_CELL_PROTOCOL:
        raise ValueError("EXP-015 Stage A cell protocol mismatch")
    if cell.get("experiment_id") != EXP015_ID:
        raise ValueError("EXP-015 Stage A cell experiment mismatch")
    if cell.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-015 Stage A cell must be retrospective")
    if cell.get("untouched_oos") is not False:
        raise ValueError("EXP-015 Stage A cell cannot be untouched OOS")
    if cell.get("promotion_authorized") is not False:
        raise ValueError("EXP-015 Stage A cell cannot authorize promotion")
    if cell.get("historical_status_mutation_authorized") is not False:
        raise ValueError("EXP-015 Stage A cell cannot mutate lifecycle")

    symbol = cell.get("symbol")
    timeframe = cell.get("timeframe")
    code_commit = cell.get("runner_code_commit")
    source_sha = cell.get("strategy_source_sha256")
    if not isinstance(symbol, str) or not isinstance(timeframe, str):
        raise ValueError("EXP-015 Stage A cell identity is malformed")
    if not isinstance(code_commit, str):
        raise ValueError("EXP-015 Stage A runner commit is missing")
    _validate_commit(code_commit)
    if not isinstance(source_sha, str) or not _SHA256_RE.fullmatch(source_sha):
        raise ValueError("EXP-015 Stage A strategy source digest is malformed")
    if cell.get("range_start") != _STAGE_A_RANGE.start.isoformat():
        raise ValueError("EXP-015 Stage A range start drift")
    if cell.get("range_end_exclusive") != _STAGE_A_RANGE.end_exclusive.isoformat():
        raise ValueError("EXP-015 Stage A range end drift")
    if cell.get("strategy_identity_count") != 63:
        raise ValueError("EXP-015 Stage A cell must bind exactly 63 strategies")
    if cell.get("scenario_run_count") != 189:
        raise ValueError("EXP-015 Stage A cell must contain exactly 189 scenario runs")
    if cell.get("slippage_scenarios") != list(SLIPPAGE_SCENARIOS):
        raise ValueError("EXP-015 Stage A slippage scenario drift")

    records = _cell_records(
        symbol=symbol,
        timeframe=timeframe,
        code_commit=code_commit,
    )
    expected = {
        item.strategy.fingerprint: item.strategy
        for item in records
    }
    expected_fingerprints = sorted(expected)
    if cell.get("strategy_fingerprints") != expected_fingerprints:
        raise ValueError("EXP-015 Stage A frozen strategy identity list mismatch")

    raw_rows = cell.get("rows")
    if not isinstance(raw_rows, list) or len(raw_rows) != 189:
        raise ValueError("EXP-015 Stage A rows are malformed")

    indexed: dict[str, dict[float, Mapping[str, object]]] = {}
    for raw in raw_rows:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-015 Stage A row must be an object")
        fingerprint = raw.get("strategy_fingerprint")
        slippage = raw.get("slippage_pips")
        if not isinstance(fingerprint, str) or fingerprint not in expected:
            raise ValueError("EXP-015 Stage A row has unknown strategy identity")
        if slippage not in SLIPPAGE_SCENARIOS:
            raise ValueError("EXP-015 Stage A row has invalid slippage")
        strategy = expected[fingerprint]
        if raw.get("family") != strategy.family:
            raise ValueError("EXP-015 Stage A row family mismatch")
        if raw.get("symbol") != strategy.symbol or raw.get("timeframe") != strategy.timeframe:
            raise ValueError("EXP-015 Stage A row cell identity mismatch")
        if raw.get("parameters_json") != strategy.parameters_json:
            raise ValueError("EXP-015 Stage A row parameters mismatch")
        if raw.get("strategy_identity_json") != strategy.identity_json:
            raise ValueError("EXP-015 Stage A row strategy identity JSON mismatch")
        candidate_sha = raw.get("candidate_sha256")
        if not isinstance(candidate_sha, str) or not _SHA256_RE.fullmatch(candidate_sha):
            raise ValueError("EXP-015 Stage A row candidate digest is malformed")
        bucket = indexed.setdefault(fingerprint, {})
        if slippage in bucket:
            raise ValueError("duplicate EXP-015 Stage A strategy/slippage row")
        bucket[float(slippage)] = raw

    if set(indexed) != set(expected):
        raise ValueError("EXP-015 Stage A row strategy coverage mismatch")

    strategy_gates: dict[str, dict[str, object]] = {}
    passers_by_family: dict[str, list[str]] = {family: [] for family in _FAMILIES}
    for fingerprint in expected_fingerprints:
        scenarios = indexed[fingerprint]
        if tuple(sorted(scenarios)) != SLIPPAGE_SCENARIOS:
            raise ValueError("EXP-015 Stage A strategy requires exactly three cost scenarios")
        candidate_shas = {row["candidate_sha256"] for row in scenarios.values()}
        if len(candidate_shas) != 1:
            raise ValueError("EXP-015 Stage A candidate sequence changed across costs")

        mandatory = _scenario_gate(scenarios[0.2]) and _scenario_gate(scenarios[0.5])
        strategy = expected[fingerprint]
        strategy_gates[fingerprint] = {
            "family": strategy.family,
            "parameters_json": strategy.parameters_json,
            "mandatory_gate_pass": mandatory,
            "annualized_return_02": _annualized(scenarios[0.2])
            if _numeric_metric(_phase3_metrics(scenarios[0.2]), "net_return") is not None
            and float(_numeric_metric(_phase3_metrics(scenarios[0.2]), "net_return")) > -1.0
            else None,
            "annualized_return_05": _annualized(scenarios[0.5])
            if _numeric_metric(_phase3_metrics(scenarios[0.5]), "net_return") is not None
            and float(_numeric_metric(_phase3_metrics(scenarios[0.5]), "net_return")) > -1.0
            else None,
        }
        if mandatory:
            passers_by_family[strategy.family].append(fingerprint)

    family_rankings: dict[str, dict[str, object]] = {}
    survivors: list[str] = []
    for family in _FAMILIES:
        ranked = sorted(
            passers_by_family[family],
            key=lambda fingerprint: _rank_key(fingerprint, indexed[fingerprint]),
        )
        selected = ranked[:2]
        survivors.extend(selected)
        family_rankings[family] = {
            "passing_fingerprints": ranked,
            "selected_fingerprints": selected,
        }

    survivors = sorted(survivors)
    if len(survivors) > 12:
        raise RuntimeError("EXP-015 Stage A cell survivor cap exceeded")

    return {
        "protocol": EXP015_STAGE_A_GATE_PROTOCOL,
        "experiment_id": EXP015_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "runner_code_commit": code_commit,
        "strategy_source_sha256": source_sha,
        "strategy_fingerprints": expected_fingerprints,
        "survivor_fingerprints": survivors,
        "family_rankings": family_rankings,
        "strategy_gates": strategy_gates,
    }


def aggregate_exp015_stage_a_gates(
    gates: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    materialized = tuple(gates)
    if len(materialized) != 9:
        raise ValueError("EXP-015 Stage A authorization requires exactly nine cell gates")

    expected_cells = {
        (symbol, timeframe)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY")
        for timeframe in ("5m", "15m", "1h")
    }
    seen_cells: set[tuple[str, str]] = set()
    commits: set[str] = set()
    source_digests: set[str] = set()
    all_fingerprints: set[str] = set()
    survivors: set[str] = set()
    cells: list[dict[str, object]] = []

    for gate in materialized:
        if gate.get("protocol") != EXP015_STAGE_A_GATE_PROTOCOL:
            raise ValueError("EXP-015 Stage A gate protocol mismatch")
        if gate.get("experiment_id") != EXP015_ID:
            raise ValueError("EXP-015 Stage A gate experiment mismatch")
        if gate.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
            raise ValueError("EXP-015 Stage A gate must be retrospective")
        if gate.get("untouched_oos") is not False:
            raise ValueError("EXP-015 Stage A gate cannot be untouched OOS")
        if gate.get("promotion_authorized") is not False:
            raise ValueError("EXP-015 Stage A gate cannot authorize promotion")
        if gate.get("historical_status_mutation_authorized") is not False:
            raise ValueError("EXP-015 Stage A gate cannot mutate lifecycle")

        symbol = gate.get("symbol")
        timeframe = gate.get("timeframe")
        code_commit = gate.get("runner_code_commit")
        source_sha = gate.get("strategy_source_sha256")
        if not isinstance(symbol, str) or not isinstance(timeframe, str):
            raise ValueError("EXP-015 Stage A gate cell identity is malformed")
        cell = (symbol, timeframe)
        if cell not in expected_cells or cell in seen_cells:
            raise ValueError("EXP-015 Stage A gate cell coverage mismatch")
        seen_cells.add(cell)
        if not isinstance(code_commit, str):
            raise ValueError("EXP-015 Stage A gate runner commit is missing")
        _validate_commit(code_commit)
        if not isinstance(source_sha, str) or not _SHA256_RE.fullmatch(source_sha):
            raise ValueError("EXP-015 Stage A gate source digest is malformed")
        commits.add(code_commit)
        source_digests.add(source_sha)

        records = _cell_records(
            symbol=symbol,
            timeframe=timeframe,
            code_commit=code_commit,
        )
        expected = sorted(item.strategy.fingerprint for item in records)
        raw_fingerprints = gate.get("strategy_fingerprints")
        if raw_fingerprints != expected:
            raise ValueError("EXP-015 Stage A gate strategy coverage mismatch")
        raw_survivors = gate.get("survivor_fingerprints")
        if not isinstance(raw_survivors, list):
            raise ValueError("EXP-015 Stage A gate survivor list is malformed")
        cell_survivors = tuple(sorted(str(item) for item in raw_survivors))
        if len(set(cell_survivors)) != len(cell_survivors):
            raise ValueError("EXP-015 Stage A gate has duplicate survivors")
        if len(cell_survivors) > 12:
            raise ValueError("EXP-015 Stage A cell survivor cap exceeded")
        if not set(cell_survivors).issubset(set(expected)):
            raise ValueError("EXP-015 Stage A survivor is outside frozen cell")

        if all_fingerprints.intersection(expected):
            raise ValueError("EXP-015 Stage A strategy appears in multiple cells")
        all_fingerprints.update(expected)
        survivors.update(cell_survivors)
        cells.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "strategy_fingerprints": expected,
                "survivor_fingerprints": list(cell_survivors),
            }
        )

    if seen_cells != expected_cells:
        raise ValueError("EXP-015 Stage A authorization cell coverage mismatch")
    if len(commits) != 1:
        raise ValueError("EXP-015 Stage A gate runner commits differ")
    if len(source_digests) != 1:
        raise ValueError("EXP-015 Stage A strategy source digests differ")
    code_commit = next(iter(commits))
    expected_all = {
        item.strategy.fingerprint
        for item in build_exp015_challengers(code_commit=code_commit)
    }
    if all_fingerprints != expected_all or len(all_fingerprints) != 567:
        raise ValueError("EXP-015 Stage A authorization must bind exact 567-strategy catalog")
    if len(survivors) > 108:
        raise ValueError("EXP-015 Stage A absolute survivor cap exceeded")

    ordered_survivors = sorted(survivors)
    return {
        "protocol": EXP015_STAGE_A_AUTHORIZATION_PROTOCOL,
        "experiment_id": EXP015_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "runner_code_commit": code_commit,
        "strategy_source_sha256": next(iter(source_digests)),
        "cell_count": 9,
        "ranking_cell_count": 54,
        "strategy_identity_count": 567,
        "maximum_stage_a_survivors": 108,
        "survivor_count": len(ordered_survivors),
        "survivor_fingerprints": ordered_survivors,
        "stage_b_source_open_authorized": bool(ordered_survivors),
        "cells": sorted(cells, key=lambda item: (str(item["symbol"]), str(item["timeframe"]))),
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
    payload = path.read_bytes()
    return {
        "path": path.name,
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def write_exp015_stage_a_cell_artifacts(
    *,
    cell: Mapping[str, object],
    gate: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    if cell.get("protocol") != EXP015_STAGE_A_CELL_PROTOCOL:
        raise ValueError("EXP-015 Stage A cell artifact protocol mismatch")
    if gate.get("protocol") != EXP015_STAGE_A_GATE_PROTOCOL:
        raise ValueError("EXP-015 Stage A gate artifact protocol mismatch")
    if cell.get("promotion_authorized") is not False or gate.get("promotion_authorized") is not False:
        raise ValueError("EXP-015 Stage A artifacts cannot authorize promotion")
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    _atomic_write(root / "cell.json", _stable_json_bytes(dict(cell)))
    _atomic_write(root / "gate.json", _stable_json_bytes(dict(gate)))
    manifest = {
        "protocol": EXP015_STAGE_A_CELL_ARTIFACT_PROTOCOL,
        "experiment_id": EXP015_ID,
        "promotion_authorized": False,
        "artifacts": [
            _artifact_record(root / name)
            for name in ("cell.json", "gate.json")
        ],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


def write_exp015_stage_a_authorization_artifacts(
    authorization: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    if authorization.get("protocol") != EXP015_STAGE_A_AUTHORIZATION_PROTOCOL:
        raise ValueError("EXP-015 Stage A authorization artifact protocol mismatch")
    if authorization.get("promotion_authorized") is not False:
        raise ValueError("EXP-015 Stage A authorization cannot authorize promotion")
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / "authorization.json"
    _atomic_write(result_path, _stable_json_bytes(dict(authorization)))
    manifest = {
        "protocol": EXP015_STAGE_A_AUTHORIZATION_ARTIFACT_PROTOCOL,
        "experiment_id": EXP015_ID,
        "promotion_authorized": False,
        "artifacts": [_artifact_record(result_path)],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "EXP015_STAGE_A_AUTHORIZATION_PROTOCOL",
    "EXP015_STAGE_A_CELL_PROTOCOL",
    "EXP015_STAGE_A_GATE_PROTOCOL",
    "aggregate_exp015_stage_a_gates",
    "evaluate_exp015_stage_a_cell",
    "exp015_strategy_source_sha256",
    "run_exp015_stage_a_cell",
    "write_exp015_stage_a_authorization_artifacts",
    "write_exp015_stage_a_cell_artifacts",
]
