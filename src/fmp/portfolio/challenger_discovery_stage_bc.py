from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Callable, Mapping, Sequence
from datetime import date
from pathlib import Path

from .challenger_discovery import (
    EXP015_ID,
    build_exp015_challengers,
    exp015_catalog_identity_sha256,
)
from .challenger_discovery_stage_a import (
    EXP015_STAGE_A_AUTHORIZATION_PROTOCOL,
    _artifact_record,
    _atomic_write,
    _stable_json_bytes,
    exp015_strategy_source_sha256,
)
from .contracts import StrategyLifecycle, StrategyRecord
from .registry import transition_strategy
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

EXP015_STAGE_B_PROTOCOL = "fmp-phase8a-exp015-stage-b-v1"
EXP015_STAGE_B_ARTIFACT_PROTOCOL = "fmp-phase8a-exp015-stage-b-artifacts-v1"
EXP015_STAGE_C_PROTOCOL = "fmp-phase8a-exp015-stage-c-v1"
EXP015_STAGE_C_ARTIFACT_PROTOCOL = "fmp-phase8a-exp015-stage-c-artifacts-v1"
EXP015_FINAL_PROTOCOL = "fmp-phase8a-exp015-final-shortlist-v1"
EXP015_FINAL_ARTIFACT_PROTOCOL = "fmp-phase8a-exp015-final-shortlist-artifacts-v1"

_STAGE_B_RANGE = RetrospectiveRange(
    start=date(2019, 1, 1),
    end_exclusive=date(2023, 1, 1),
)
_STAGE_C_RANGE = RetrospectiveRange(
    start=date(2023, 1, 1),
    end_exclusive=date(2026, 8, 21),
)
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_STAGE_B_YEARS = (2019, 2020, 2021, 2022)
_STAGE_C_YEARS = (2023, 2024, 2025, 2026)
_FINAL_EVIDENCE_ID = f"{EXP015_ID}:FINAL_SHORTLIST"


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _catalog_by_fingerprint(code_commit: str) -> dict[str, StrategyRecord]:
    return {
        item.strategy.fingerprint: item
        for item in build_exp015_challengers(code_commit=code_commit)
    }


def _validate_stage_a_authorization(
    authorization: Mapping[str, object],
) -> tuple[str, str, str, tuple[str, ...], tuple[StrategyRecord, ...]]:
    if authorization.get("protocol") != EXP015_STAGE_A_AUTHORIZATION_PROTOCOL:
        raise ValueError("EXP-015 Stage A authorization protocol mismatch")
    if authorization.get("experiment_id") != EXP015_ID:
        raise ValueError("EXP-015 Stage A authorization experiment mismatch")
    if authorization.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-015 Stage A authorization must be retrospective")
    if authorization.get("untouched_oos") is not False:
        raise ValueError("EXP-015 Stage A authorization cannot be untouched OOS")
    if authorization.get("promotion_authorized") is not False:
        raise ValueError("EXP-015 Stage A authorization cannot authorize broker/shadow promotion")
    if authorization.get("historical_status_mutation_authorized") is not False:
        raise ValueError("EXP-015 Stage A authorization cannot mutate lifecycle")
    if authorization.get("cell_count") != 9:
        raise ValueError("EXP-015 Stage A authorization must contain nine cells")
    if authorization.get("ranking_cell_count") != 54:
        raise ValueError("EXP-015 Stage A authorization must contain 54 ranking cells")
    if authorization.get("strategy_identity_count") != 567:
        raise ValueError("EXP-015 Stage A authorization must bind 567 strategies")
    if authorization.get("maximum_stage_a_survivors") != 108:
        raise ValueError("EXP-015 Stage A authorization survivor ceiling drift")

    stage_a_commit = _validate_commit(
        authorization.get("runner_code_commit"),
        field="EXP-015 Stage A runner commit",
    )
    catalog_sha = _validate_sha256(
        authorization.get("catalog_identity_sha256"),
        field="EXP-015 Stage A catalog digest",
    )
    source_sha = _validate_sha256(
        authorization.get("strategy_source_sha256"),
        field="EXP-015 Stage A strategy source digest",
    )
    if catalog_sha != exp015_catalog_identity_sha256(code_commit=stage_a_commit):
        raise ValueError("EXP-015 Stage A catalog identity mismatch")

    catalog = _catalog_by_fingerprint(stage_a_commit)
    raw_survivors = authorization.get("survivor_fingerprints")
    if not isinstance(raw_survivors, list):
        raise ValueError("EXP-015 Stage A survivor list is malformed")
    survivors = tuple(sorted(str(item) for item in raw_survivors))
    if len(set(survivors)) != len(survivors):
        raise ValueError("EXP-015 Stage A survivor list has duplicates")
    if len(survivors) > 108:
        raise ValueError("EXP-015 Stage A survivor ceiling exceeded")
    if authorization.get("survivor_count") != len(survivors):
        raise ValueError("EXP-015 Stage A survivor count mismatch")
    if authorization.get("stage_b_source_open_authorized") is not bool(survivors):
        raise ValueError("EXP-015 Stage B source-open authorization mismatch")
    if not set(survivors).issubset(catalog):
        raise ValueError("EXP-015 Stage A survivor is outside frozen catalog")

    raw_cells = authorization.get("cells")
    if not isinstance(raw_cells, list) or len(raw_cells) != 9:
        raise ValueError("EXP-015 Stage A authorization cells are malformed")
    expected_cells = {
        (symbol, timeframe)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY")
        for timeframe in ("5m", "15m", "1h")
    }
    seen_cells: set[tuple[str, str]] = set()
    all_fingerprints: set[str] = set()
    cell_survivors: set[str] = set()
    for raw_cell in raw_cells:
        if not isinstance(raw_cell, Mapping):
            raise ValueError("EXP-015 Stage A authorization cell must be an object")
        symbol = raw_cell.get("symbol")
        timeframe = raw_cell.get("timeframe")
        if not isinstance(symbol, str) or not isinstance(timeframe, str):
            raise ValueError("EXP-015 Stage A cell identity is malformed")
        cell = (symbol, timeframe)
        if cell not in expected_cells or cell in seen_cells:
            raise ValueError("EXP-015 Stage A cell coverage mismatch")
        seen_cells.add(cell)

        raw_fingerprints = raw_cell.get("strategy_fingerprints")
        raw_cell_survivors = raw_cell.get("survivor_fingerprints")
        if not isinstance(raw_fingerprints, list) or len(raw_fingerprints) != 63:
            raise ValueError("EXP-015 Stage A cell must bind 63 strategies")
        if not isinstance(raw_cell_survivors, list):
            raise ValueError("EXP-015 Stage A cell survivor list is malformed")
        fingerprints = tuple(sorted(str(item) for item in raw_fingerprints))
        survivors_for_cell = tuple(sorted(str(item) for item in raw_cell_survivors))
        if len(set(fingerprints)) != 63:
            raise ValueError("EXP-015 Stage A cell contains duplicate strategies")
        if len(survivors_for_cell) > 12:
            raise ValueError("EXP-015 Stage A pair/timeframe survivor cap exceeded")
        if not set(survivors_for_cell).issubset(fingerprints):
            raise ValueError("EXP-015 Stage A cell survivor is outside its cell")
        family_counts: dict[str, int] = {}
        for fingerprint in survivors_for_cell:
            record = catalog.get(fingerprint)
            if record is None:
                raise ValueError("EXP-015 Stage A cell survivor is outside catalog")
            family = record.strategy.family
            family_counts[family] = family_counts.get(family, 0) + 1
        if any(value > 2 for value in family_counts.values()):
            raise ValueError("EXP-015 Stage A family-cell survivor cap exceeded")
        if all_fingerprints.intersection(fingerprints):
            raise ValueError("EXP-015 Stage A strategy appears in multiple cells")
        all_fingerprints.update(fingerprints)
        cell_survivors.update(survivors_for_cell)

    if seen_cells != expected_cells:
        raise ValueError("EXP-015 Stage A authorization cell coverage mismatch")
    if all_fingerprints != set(catalog):
        raise ValueError("EXP-015 Stage A authorization catalog coverage mismatch")
    if tuple(sorted(cell_survivors)) != survivors:
        raise ValueError("EXP-015 Stage A survivor union mismatch")

    records = tuple(catalog[item] for item in survivors)
    return stage_a_commit, catalog_sha, source_sha, survivors, records


def validate_exp015_stage_a_authorization(
    authorization: Mapping[str, object],
) -> tuple[StrategyRecord, ...]:
    _, _, source_sha, _, records = _validate_stage_a_authorization(authorization)
    if source_sha != exp015_strategy_source_sha256():
        raise ValueError("EXP-015 strategy source digest mismatch")
    return records


def _validate_loaded(
    loaded: LoadedRetrospectiveBars,
    *,
    symbol: str,
    research_range: RetrospectiveRange,
    stage_name: str,
) -> None:
    if loaded.evidence_label != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError(f"EXP-015 {stage_name} source must be retrospective")
    if loaded.start != research_range.start or loaded.end_exclusive != research_range.end_exclusive:
        raise ValueError(f"EXP-015 {stage_name} loaded range mismatch")
    if not loaded.bars:
        raise ValueError(f"EXP-015 {stage_name} requires complete signal bars")
    if {item.symbol for item in loaded.bars} != {symbol}:
        raise ValueError(f"EXP-015 {stage_name} source symbol mismatch")
    _validate_sha256(
        loaded.processed_manifest_sha256,
        field=f"EXP-015 {stage_name} processed manifest digest",
    )


def _phase3(row: Mapping[str, object]) -> Mapping[str, object]:
    metrics = row.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("EXP-015 stage row metrics are missing")
    phase3 = metrics.get("phase3_metrics")
    if not isinstance(phase3, Mapping):
        raise ValueError("EXP-015 stage phase3_metrics are missing")
    return phase3


def _metric(row: Mapping[str, object], key: str) -> float | None:
    value = _phase3(row).get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"EXP-015 metric {key!r} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"EXP-015 metric {key!r} must be finite")
    return number


def _trade_count(row: Mapping[str, object]) -> int:
    metrics = row.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("EXP-015 stage row metrics are missing")
    value = metrics.get("trade_count")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("EXP-015 stage trade_count must be a non-negative integer")
    return value


def _scenario_pass(row: Mapping[str, object], *, minimum_trades: int) -> bool:
    net_return = _metric(row, "net_return")
    expectancy = _metric(row, "expectancy_usd")
    profit_factor = _metric(row, "profit_factor")
    max_drawdown = _metric(row, "max_drawdown_fraction")
    if None in (net_return, expectancy, profit_factor, max_drawdown):
        return False
    return (
        float(net_return) > 0.0
        and float(expectancy) > 0.0
        and float(profit_factor) > 1.05
        and float(max_drawdown) <= 0.05
        and _trade_count(row) >= minimum_trades
    )


def _positive_year_count(
    row: Mapping[str, object],
    *,
    expected_years: Sequence[int],
) -> tuple[int, dict[str, float]]:
    metrics = row.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("EXP-015 stage row metrics are missing")
    raw = metrics.get("calendar_year_breakdown")
    if not isinstance(raw, Mapping):
        raise ValueError("EXP-015 stage calendar_year_breakdown is missing")
    expected = {str(year) for year in expected_years}
    unexpected = sorted(set(str(key) for key in raw) - expected)
    if unexpected:
        raise ValueError(f"EXP-015 stage contains unexpected calendar years: {unexpected}")
    pnl_by_year: dict[str, float] = {}
    for year in expected_years:
        key = str(year)
        bucket = raw.get(key)
        if bucket is None:
            pnl_by_year[key] = 0.0
            continue
        if not isinstance(bucket, Mapping):
            raise ValueError("EXP-015 calendar-year bucket must be an object")
        value = bucket.get("net_pnl_usd")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("EXP-015 calendar-year net PnL must be numeric")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("EXP-015 calendar-year net PnL must be finite")
        pnl_by_year[key] = number
    return sum(1 for value in pnl_by_year.values() if value > 0.0), pnl_by_year


def _stage_gate(
    scenarios: Mapping[float, Mapping[str, object]],
    *,
    minimum_trades: int,
    expected_years: Sequence[int],
) -> dict[str, object]:
    pass_02 = _scenario_pass(scenarios[0.2], minimum_trades=minimum_trades)
    pass_05 = _scenario_pass(scenarios[0.5], minimum_trades=minimum_trades)
    positive_year_count, pnl_by_year = _positive_year_count(
        scenarios[0.2],
        expected_years=expected_years,
    )
    year_pass = positive_year_count >= 3
    return {
        "scenario_02_pass": pass_02,
        "scenario_05_pass": pass_05,
        "positive_year_count_02": positive_year_count,
        "year_net_pnl_usd_02": pnl_by_year,
        "positive_years_ge_3_02": year_pass,
        "stage_pass": pass_02 and pass_05 and year_pass,
    }


def _run_stage(
    *,
    records: Sequence[StrategyRecord],
    dataset_sources: Mapping[str, tuple[Path, Path]],
    code_commit: str,
    research_range: RetrospectiveRange,
    stage_name: str,
    minimum_trades: int,
    expected_years: Sequence[int],
    bars_loader: Callable[..., LoadedRetrospectiveBars],
    strategy_runner: Callable[..., Mapping[str, object]],
) -> tuple[
    list[dict[str, object]],
    dict[str, dict[str, object]],
    list[str],
    dict[str, str],
    list[dict[str, object]],
]:
    required_symbols = tuple(sorted({item.strategy.symbol for item in records}))
    missing_sources = sorted(set(required_symbols) - set(dataset_sources))
    if missing_sources:
        raise ValueError(
            f"missing EXP-015 {stage_name} dataset sources: {missing_sources}"
        )

    loaded_cache: dict[tuple[str, str], LoadedRetrospectiveBars] = {}
    manifest_by_symbol: dict[str, str] = {}
    rows: list[dict[str, object]] = []
    indexed: dict[str, dict[float, Mapping[str, object]]] = {}

    for record in records:
        strategy = record.strategy
        cell = (strategy.symbol, strategy.timeframe)
        loaded = loaded_cache.get(cell)
        if loaded is None:
            dataset_root, manifest_path = dataset_sources[strategy.symbol]
            loaded = bars_loader(
                dataset_root=Path(dataset_root),
                manifest_path=Path(manifest_path),
                symbol=strategy.symbol,
                timeframe=strategy.timeframe,
                research_range=research_range,
            )
            _validate_loaded(
                loaded,
                symbol=strategy.symbol,
                research_range=research_range,
                stage_name=stage_name,
            )
            previous = manifest_by_symbol.get(strategy.symbol)
            if previous is not None and previous != loaded.processed_manifest_sha256:
                raise ValueError(
                    f"EXP-015 {stage_name} manifest identity changed across timeframes"
                )
            manifest_by_symbol[strategy.symbol] = loaded.processed_manifest_sha256
            loaded_cache[cell] = loaded

        expected_candidate_sha: str | None = None
        scenario_rows: dict[float, Mapping[str, object]] = {}
        for slippage_pips in SLIPPAGE_SCENARIOS:
            plan = Phase8ARetrospectivePlan(
                experiment_id=EXP015_ID,
                strategy=strategy,
                research_range=research_range,
                slippage_pips=slippage_pips,
                runner_code_commit=code_commit,
            )
            result = dict(
                strategy_runner(
                    plan=plan,
                    dataset_root=dataset_sources[strategy.symbol][0],
                    manifest_path=dataset_sources[strategy.symbol][1],
                    bars_loader=lambda **_: loaded,
                )
            )
            if result.get("strategy_fingerprint") != strategy.fingerprint:
                raise ValueError(f"EXP-015 {stage_name} runner returned wrong strategy identity")
            if result.get("processed_manifest_sha256") != loaded.processed_manifest_sha256:
                raise ValueError(f"EXP-015 {stage_name} runner returned wrong manifest identity")
            if result.get("slippage_pips") != slippage_pips:
                raise ValueError(f"EXP-015 {stage_name} runner returned wrong slippage identity")
            candidate_sha = _validate_sha256(
                result.get("candidate_sha256"),
                field=f"EXP-015 {stage_name} candidate digest",
            )
            if expected_candidate_sha is None:
                expected_candidate_sha = candidate_sha
            elif candidate_sha != expected_candidate_sha:
                raise ValueError(
                    f"EXP-015 {stage_name} candidate sequence changed across costs"
                )
            metrics = result.get("metrics")
            run_identity = result.get("run_identity")
            if not isinstance(metrics, Mapping) or not isinstance(run_identity, Mapping):
                raise ValueError(f"EXP-015 {stage_name} runner returned malformed evidence")
            row = {
                "strategy_fingerprint": strategy.fingerprint,
                "strategy_identity_json": strategy.identity_json,
                "family": strategy.family,
                "version": strategy.version,
                "symbol": strategy.symbol,
                "timeframe": strategy.timeframe,
                "parameters_json": strategy.parameters_json,
                "upstream_lifecycle": record.lifecycle.value,
                "upstream_evidence_id": record.evidence_id,
                "slippage_pips": slippage_pips,
                "candidate_sha256": candidate_sha,
                "processed_manifest_sha256": loaded.processed_manifest_sha256,
                "run_identity": dict(run_identity),
                "metrics": dict(metrics),
            }
            rows.append(row)
            scenario_rows[slippage_pips] = row
        indexed[strategy.fingerprint] = scenario_rows

    gates = {
        fingerprint: _stage_gate(
            indexed[fingerprint],
            minimum_trades=minimum_trades,
            expected_years=expected_years,
        )
        for fingerprint in sorted(indexed)
    }
    passers = sorted(
        fingerprint
        for fingerprint, gate in gates.items()
        if gate["stage_pass"]
    )
    opened_cells = [
        {
            "symbol": symbol,
            "timeframe": timeframe,
            "opened_artifact_months": list(loaded.opened_artifact_months),
        }
        for (symbol, timeframe), loaded in sorted(loaded_cache.items())
    ]
    return rows, gates, passers, dict(sorted(manifest_by_symbol.items())), opened_cells


def run_exp015_stage_b(
    *,
    authorization: Mapping[str, object],
    stage_a_authorization_sha256: str,
    dataset_sources: Mapping[str, tuple[Path, Path]],
    code_commit: str,
    bars_loader: Callable[..., LoadedRetrospectiveBars] = load_phase8a_retrospective_bars,
    strategy_runner: Callable[..., Mapping[str, object]] = run_phase8a_retrospective_strategy,
) -> dict[str, object]:
    stage_a_sha = _validate_sha256(
        stage_a_authorization_sha256,
        field="EXP-015 Stage A authorization digest",
    )
    stage_b_commit = _validate_commit(code_commit, field="EXP-015 Stage B runner commit")
    stage_a_commit, catalog_sha, source_sha, survivors, records = (
        _validate_stage_a_authorization(authorization)
    )
    if not survivors or authorization.get("stage_b_source_open_authorized") is not True:
        raise ValueError("EXP-015 Stage B source-open is not authorized")
    if source_sha != exp015_strategy_source_sha256():
        raise ValueError("EXP-015 strategy source digest mismatch")

    rows, gates, passers, manifests, opened_cells = _run_stage(
        records=records,
        dataset_sources=dataset_sources,
        code_commit=stage_b_commit,
        research_range=_STAGE_B_RANGE,
        stage_name="Stage B",
        minimum_trades=40,
        expected_years=_STAGE_B_YEARS,
        bars_loader=bars_loader,
        strategy_runner=strategy_runner,
    )
    return {
        "protocol": EXP015_STAGE_B_PROTOCOL,
        "experiment_id": EXP015_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "stage_c_source_open_authorized": bool(passers),
        "stage_a_authorization_sha256": stage_a_sha,
        "stage_a_runner_code_commit": stage_a_commit,
        "stage_b_runner_code_commit": stage_b_commit,
        "catalog_identity_sha256": catalog_sha,
        "strategy_source_sha256": source_sha,
        "range_start": _STAGE_B_RANGE.start.isoformat(),
        "range_end_exclusive": _STAGE_B_RANGE.end_exclusive.isoformat(),
        "stage_a_survivor_fingerprints": list(survivors),
        "strategy_identity_count": len(records),
        "scenario_run_count": len(rows),
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "processed_manifest_sha256_by_symbol": manifests,
        "opened_cells": opened_cells,
        "rows": rows,
        "strategy_gates": gates,
        "stage_b_pass_count": len(passers),
        "stage_b_pass_fingerprints": passers,
    }


def _index_and_validate_stage_rows(
    *,
    result: Mapping[str, object],
    records: Sequence[StrategyRecord],
    expected_range: RetrospectiveRange,
    expected_years: Sequence[int],
    minimum_trades: int,
    stage_name: str,
    runner_code_commit: str,
) -> tuple[dict[str, dict[float, Mapping[str, object]]], list[str]]:
    raw_rows = result.get("rows")
    if not isinstance(raw_rows, list) or len(raw_rows) != len(records) * 3:
        raise ValueError(f"EXP-015 {stage_name} row count mismatch")
    by_fp = {item.strategy.fingerprint: item for item in records}
    indexed: dict[str, dict[float, Mapping[str, object]]] = {}
    for raw in raw_rows:
        if not isinstance(raw, Mapping):
            raise ValueError(f"EXP-015 {stage_name} row must be an object")
        fingerprint = raw.get("strategy_fingerprint")
        slippage = raw.get("slippage_pips")
        if not isinstance(fingerprint, str) or fingerprint not in by_fp:
            raise ValueError(f"EXP-015 {stage_name} row has unknown strategy")
        if slippage not in SLIPPAGE_SCENARIOS:
            raise ValueError(f"EXP-015 {stage_name} row has invalid slippage")
        strategy = by_fp[fingerprint].strategy
        if raw.get("strategy_identity_json") != strategy.identity_json:
            raise ValueError(f"EXP-015 {stage_name} strategy identity mismatch")
        if raw.get("family") != strategy.family:
            raise ValueError(f"EXP-015 {stage_name} family mismatch")
        if raw.get("symbol") != strategy.symbol or raw.get("timeframe") != strategy.timeframe:
            raise ValueError(f"EXP-015 {stage_name} cell identity mismatch")
        if raw.get("parameters_json") != strategy.parameters_json:
            raise ValueError(f"EXP-015 {stage_name} parameters mismatch")
        _validate_sha256(
            raw.get("candidate_sha256"),
            field=f"EXP-015 {stage_name} candidate digest",
        )
        manifest_sha = _validate_sha256(
            raw.get("processed_manifest_sha256"),
            field=f"EXP-015 {stage_name} row manifest digest",
        )
        run_identity = raw.get("run_identity")
        if not isinstance(run_identity, Mapping):
            raise ValueError(f"EXP-015 {stage_name} run identity is malformed")
        if run_identity.get("code_commit") != runner_code_commit:
            raise ValueError(f"EXP-015 {stage_name} row runner commit mismatch")
        if run_identity.get("processed_data_manifest_id") not in (None, manifest_sha):
            raise ValueError(f"EXP-015 {stage_name} row manifest/run identity mismatch")
        bucket = indexed.setdefault(fingerprint, {})
        if slippage in bucket:
            raise ValueError(f"duplicate EXP-015 {stage_name} strategy/slippage row")
        bucket[float(slippage)] = raw
    if set(indexed) != set(by_fp):
        raise ValueError(f"EXP-015 {stage_name} strategy coverage mismatch")

    recalculated_gates: dict[str, dict[str, object]] = {}
    passers: list[str] = []
    for fingerprint in sorted(indexed):
        scenarios = indexed[fingerprint]
        if tuple(sorted(scenarios)) != SLIPPAGE_SCENARIOS:
            raise ValueError(f"EXP-015 {stage_name} cost-scenario coverage mismatch")
        if len({row["candidate_sha256"] for row in scenarios.values()}) != 1:
            raise ValueError(f"EXP-015 {stage_name} candidate sequence changed across costs")
        gate = _stage_gate(
            scenarios,
            minimum_trades=minimum_trades,
            expected_years=expected_years,
        )
        recalculated_gates[fingerprint] = gate
        if gate["stage_pass"]:
            passers.append(fingerprint)

    raw_gates = result.get("strategy_gates")
    if raw_gates != recalculated_gates:
        raise ValueError(f"EXP-015 {stage_name} gate evidence mismatch")
    return indexed, passers


def _validate_stage_b_result(
    *,
    stage_b: Mapping[str, object],
    stage_a_sha: str,
    stage_a_commit: str,
    catalog_sha: str,
    source_sha: str,
    stage_a_survivors: Sequence[str],
    stage_a_records: Sequence[StrategyRecord],
) -> tuple[dict[str, dict[float, Mapping[str, object]]], tuple[str, ...], tuple[StrategyRecord, ...]]:
    if stage_b.get("protocol") != EXP015_STAGE_B_PROTOCOL:
        raise ValueError("EXP-015 Stage B protocol mismatch")
    if stage_b.get("experiment_id") != EXP015_ID:
        raise ValueError("EXP-015 Stage B experiment mismatch")
    if stage_b.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-015 Stage B must be retrospective")
    if stage_b.get("untouched_oos") is not False:
        raise ValueError("EXP-015 Stage B cannot be untouched OOS")
    if stage_b.get("promotion_authorized") is not False:
        raise ValueError("EXP-015 Stage B cannot authorize broker/shadow promotion")
    if stage_b.get("historical_status_mutation_authorized") is not False:
        raise ValueError("EXP-015 Stage B cannot mutate lifecycle")
    if stage_b.get("stage_a_authorization_sha256") != stage_a_sha:
        raise ValueError("EXP-015 Stage B Stage A authorization digest mismatch")
    if stage_b.get("stage_a_runner_code_commit") != stage_a_commit:
        raise ValueError("EXP-015 Stage B Stage A commit mismatch")
    _validate_commit(stage_b.get("stage_b_runner_code_commit"), field="EXP-015 Stage B runner commit")
    if stage_b.get("catalog_identity_sha256") != catalog_sha:
        raise ValueError("EXP-015 Stage B catalog digest mismatch")
    if stage_b.get("strategy_source_sha256") != source_sha:
        raise ValueError("EXP-015 Stage B strategy source digest mismatch")
    if stage_b.get("range_start") != _STAGE_B_RANGE.start.isoformat():
        raise ValueError("EXP-015 Stage B range start drift")
    if stage_b.get("range_end_exclusive") != _STAGE_B_RANGE.end_exclusive.isoformat():
        raise ValueError("EXP-015 Stage B range end drift")
    if stage_b.get("stage_a_survivor_fingerprints") != list(stage_a_survivors):
        raise ValueError("EXP-015 Stage B Stage A survivor list mismatch")
    if stage_b.get("strategy_identity_count") != len(stage_a_records):
        raise ValueError("EXP-015 Stage B strategy count mismatch")
    if stage_b.get("scenario_run_count") != len(stage_a_records) * 3:
        raise ValueError("EXP-015 Stage B scenario count mismatch")
    if stage_b.get("slippage_scenarios") != list(SLIPPAGE_SCENARIOS):
        raise ValueError("EXP-015 Stage B slippage scenario drift")
    raw_manifests = stage_b.get("processed_manifest_sha256_by_symbol")
    if not isinstance(raw_manifests, Mapping):
        raise ValueError("EXP-015 Stage B manifest map is malformed")
    expected_symbols = {item.strategy.symbol for item in stage_a_records}
    if set(raw_manifests) != expected_symbols:
        raise ValueError("EXP-015 Stage B manifest symbol coverage mismatch")
    for value in raw_manifests.values():
        _validate_sha256(value, field="EXP-015 Stage B processed manifest digest")

    indexed, passers = _index_and_validate_stage_rows(
        result=stage_b,
        records=stage_a_records,
        expected_range=_STAGE_B_RANGE,
        expected_years=_STAGE_B_YEARS,
        minimum_trades=40,
        stage_name="Stage B",
        runner_code_commit=str(stage_b["stage_b_runner_code_commit"]),
    )
    if stage_b.get("stage_b_pass_count") != len(passers):
        raise ValueError("EXP-015 Stage B pass count mismatch")
    if stage_b.get("stage_b_pass_fingerprints") != passers:
        raise ValueError("EXP-015 Stage B pass fingerprint mismatch")
    if stage_b.get("stage_c_source_open_authorized") is not bool(passers):
        raise ValueError("EXP-015 Stage C source-open authorization mismatch")
    by_fp = {item.strategy.fingerprint: item for item in stage_a_records}
    return indexed, tuple(passers), tuple(by_fp[item] for item in passers)


def run_exp015_stage_c(
    *,
    stage_a_authorization: Mapping[str, object],
    stage_a_authorization_sha256: str,
    stage_b_result: Mapping[str, object],
    stage_b_result_sha256: str,
    dataset_sources: Mapping[str, tuple[Path, Path]],
    code_commit: str,
    bars_loader: Callable[..., LoadedRetrospectiveBars] = load_phase8a_retrospective_bars,
    strategy_runner: Callable[..., Mapping[str, object]] = run_phase8a_retrospective_strategy,
) -> dict[str, object]:
    stage_a_sha = _validate_sha256(
        stage_a_authorization_sha256,
        field="EXP-015 Stage A authorization digest",
    )
    stage_b_sha = _validate_sha256(
        stage_b_result_sha256,
        field="EXP-015 Stage B result digest",
    )
    stage_c_commit = _validate_commit(code_commit, field="EXP-015 Stage C runner commit")
    stage_a_commit, catalog_sha, source_sha, stage_a_survivors, stage_a_records = (
        _validate_stage_a_authorization(stage_a_authorization)
    )
    if source_sha != exp015_strategy_source_sha256():
        raise ValueError("EXP-015 strategy source digest mismatch")

    _, stage_b_passers, stage_b_records = _validate_stage_b_result(
        stage_b=stage_b_result,
        stage_a_sha=stage_a_sha,
        stage_a_commit=stage_a_commit,
        catalog_sha=catalog_sha,
        source_sha=source_sha,
        stage_a_survivors=stage_a_survivors,
        stage_a_records=stage_a_records,
    )
    if not stage_b_passers or stage_b_result.get("stage_c_source_open_authorized") is not True:
        raise ValueError("EXP-015 Stage C source-open is not authorized")

    rows, gates, passers, manifests, opened_cells = _run_stage(
        records=stage_b_records,
        dataset_sources=dataset_sources,
        code_commit=stage_c_commit,
        research_range=_STAGE_C_RANGE,
        stage_name="Stage C",
        minimum_trades=30,
        expected_years=_STAGE_C_YEARS,
        bars_loader=bars_loader,
        strategy_runner=strategy_runner,
    )
    return {
        "protocol": EXP015_STAGE_C_PROTOCOL,
        "experiment_id": EXP015_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "final_shortlist_review_authorized": bool(passers),
        "stage_a_authorization_sha256": stage_a_sha,
        "stage_b_result_sha256": stage_b_sha,
        "stage_a_runner_code_commit": stage_a_commit,
        "stage_b_runner_code_commit": stage_b_result["stage_b_runner_code_commit"],
        "stage_c_runner_code_commit": stage_c_commit,
        "catalog_identity_sha256": catalog_sha,
        "strategy_source_sha256": source_sha,
        "range_start": _STAGE_C_RANGE.start.isoformat(),
        "range_end_exclusive": _STAGE_C_RANGE.end_exclusive.isoformat(),
        "stage_b_pass_fingerprints": list(stage_b_passers),
        "strategy_identity_count": len(stage_b_records),
        "scenario_run_count": len(rows),
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "processed_manifest_sha256_by_symbol": manifests,
        "opened_cells": opened_cells,
        "rows": rows,
        "strategy_gates": gates,
        "stage_c_pass_count": len(passers),
        "stage_c_pass_fingerprints": passers,
    }


def _validate_stage_c_result(
    *,
    stage_c: Mapping[str, object],
    stage_a_sha: str,
    stage_b_sha: str,
    stage_a_commit: str,
    catalog_sha: str,
    source_sha: str,
    stage_b_commit: str,
    stage_b_passers: Sequence[str],
    stage_b_records: Sequence[StrategyRecord],
) -> tuple[dict[str, dict[float, Mapping[str, object]]], tuple[str, ...]]:
    if stage_c.get("protocol") != EXP015_STAGE_C_PROTOCOL:
        raise ValueError("EXP-015 Stage C protocol mismatch")
    if stage_c.get("experiment_id") != EXP015_ID:
        raise ValueError("EXP-015 Stage C experiment mismatch")
    if stage_c.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-015 Stage C must be retrospective")
    if stage_c.get("untouched_oos") is not False:
        raise ValueError("EXP-015 Stage C cannot be untouched OOS")
    if stage_c.get("promotion_authorized") is not False:
        raise ValueError("EXP-015 Stage C cannot authorize broker/shadow promotion")
    if stage_c.get("historical_status_mutation_authorized") is not False:
        raise ValueError("EXP-015 Stage C cannot mutate lifecycle automatically")
    if stage_c.get("stage_a_authorization_sha256") != stage_a_sha:
        raise ValueError("EXP-015 Stage C Stage A authorization digest mismatch")
    if stage_c.get("stage_b_result_sha256") != stage_b_sha:
        raise ValueError("EXP-015 Stage C Stage B result digest mismatch")
    if stage_c.get("stage_a_runner_code_commit") != stage_a_commit:
        raise ValueError("EXP-015 Stage C Stage A commit mismatch")
    if stage_c.get("stage_b_runner_code_commit") != stage_b_commit:
        raise ValueError("EXP-015 Stage C Stage B commit mismatch")
    _validate_commit(stage_c.get("stage_c_runner_code_commit"), field="EXP-015 Stage C runner commit")
    if stage_c.get("catalog_identity_sha256") != catalog_sha:
        raise ValueError("EXP-015 Stage C catalog digest mismatch")
    if stage_c.get("strategy_source_sha256") != source_sha:
        raise ValueError("EXP-015 Stage C strategy source digest mismatch")
    if stage_c.get("range_start") != _STAGE_C_RANGE.start.isoformat():
        raise ValueError("EXP-015 Stage C range start drift")
    if stage_c.get("range_end_exclusive") != _STAGE_C_RANGE.end_exclusive.isoformat():
        raise ValueError("EXP-015 Stage C range end drift")
    if stage_c.get("stage_b_pass_fingerprints") != list(stage_b_passers):
        raise ValueError("EXP-015 Stage C Stage B passer list mismatch")
    if stage_c.get("strategy_identity_count") != len(stage_b_records):
        raise ValueError("EXP-015 Stage C strategy count mismatch")
    if stage_c.get("scenario_run_count") != len(stage_b_records) * 3:
        raise ValueError("EXP-015 Stage C scenario count mismatch")
    if stage_c.get("slippage_scenarios") != list(SLIPPAGE_SCENARIOS):
        raise ValueError("EXP-015 Stage C slippage scenario drift")
    raw_manifests = stage_c.get("processed_manifest_sha256_by_symbol")
    if not isinstance(raw_manifests, Mapping):
        raise ValueError("EXP-015 Stage C manifest map is malformed")
    expected_symbols = {item.strategy.symbol for item in stage_b_records}
    if set(raw_manifests) != expected_symbols:
        raise ValueError("EXP-015 Stage C manifest symbol coverage mismatch")
    for value in raw_manifests.values():
        _validate_sha256(value, field="EXP-015 Stage C processed manifest digest")

    indexed, passers = _index_and_validate_stage_rows(
        result=stage_c,
        records=stage_b_records,
        expected_range=_STAGE_C_RANGE,
        expected_years=_STAGE_C_YEARS,
        minimum_trades=30,
        stage_name="Stage C",
        runner_code_commit=str(stage_c["stage_c_runner_code_commit"]),
    )
    if stage_c.get("stage_c_pass_count") != len(passers):
        raise ValueError("EXP-015 Stage C pass count mismatch")
    if stage_c.get("stage_c_pass_fingerprints") != passers:
        raise ValueError("EXP-015 Stage C pass fingerprint mismatch")
    if stage_c.get("final_shortlist_review_authorized") is not bool(passers):
        raise ValueError("EXP-015 final shortlist authorization mismatch")
    return indexed, tuple(passers)


def _annualized(row: Mapping[str, object], research_range: RetrospectiveRange) -> float:
    net_return = _metric(row, "net_return")
    if net_return is None or net_return <= -1.0:
        raise ValueError("EXP-015 passing strategy has non-annualizable return")
    return annualized_compounded_return(
        starting_equity_usd=100_000.0,
        ending_equity_usd=100_000.0 * (1.0 + net_return),
        start=research_range.start,
        end_exclusive=research_range.end_exclusive,
    )


def _final_rank_key(
    fingerprint: str,
    stage_b_rows: Mapping[str, Mapping[float, Mapping[str, object]]],
    stage_c_rows: Mapping[str, Mapping[float, Mapping[str, object]]],
) -> tuple[object, ...]:
    b05 = stage_b_rows[fingerprint][0.5]
    c05 = stage_c_rows[fingerprint][0.5]
    b02 = stage_b_rows[fingerprint][0.2]
    c02 = stage_c_rows[fingerprint][0.2]
    b_pf = _metric(b05, "profit_factor")
    c_pf = _metric(c05, "profit_factor")
    b_dd = _metric(b05, "max_drawdown_fraction")
    c_dd = _metric(c05, "max_drawdown_fraction")
    b_pnl = _metric(b02, "net_pnl_usd")
    c_pnl = _metric(c02, "net_pnl_usd")
    if None in (b_pf, c_pf, b_dd, c_dd, b_pnl, c_pnl):
        raise ValueError("EXP-015 final shortlist passing metrics are incomplete")
    return (
        -min(
            _annualized(b05, _STAGE_B_RANGE),
            _annualized(c05, _STAGE_C_RANGE),
        ),
        max(float(b_dd), float(c_dd)),
        -min(float(b_pf), float(c_pf)),
        -(float(b_pnl) + float(c_pnl)),
        fingerprint,
    )


def finalize_exp015_shortlist(
    *,
    stage_a_authorization: Mapping[str, object],
    stage_a_authorization_sha256: str,
    stage_b_result: Mapping[str, object],
    stage_b_result_sha256: str,
    stage_c_result: Mapping[str, object],
    stage_c_result_sha256: str,
) -> dict[str, object]:
    stage_a_sha = _validate_sha256(
        stage_a_authorization_sha256,
        field="EXP-015 Stage A authorization digest",
    )
    stage_b_sha = _validate_sha256(
        stage_b_result_sha256,
        field="EXP-015 Stage B result digest",
    )
    stage_c_sha = _validate_sha256(
        stage_c_result_sha256,
        field="EXP-015 Stage C result digest",
    )
    stage_a_commit, catalog_sha, source_sha, stage_a_survivors, stage_a_records = (
        _validate_stage_a_authorization(stage_a_authorization)
    )
    if source_sha != exp015_strategy_source_sha256():
        raise ValueError("EXP-015 strategy source digest mismatch")
    stage_b_rows, stage_b_passers, stage_b_records = _validate_stage_b_result(
        stage_b=stage_b_result,
        stage_a_sha=stage_a_sha,
        stage_a_commit=stage_a_commit,
        catalog_sha=catalog_sha,
        source_sha=source_sha,
        stage_a_survivors=stage_a_survivors,
        stage_a_records=stage_a_records,
    )
    stage_c_rows, stage_c_passers = _validate_stage_c_result(
        stage_c=stage_c_result,
        stage_a_sha=stage_a_sha,
        stage_b_sha=stage_b_sha,
        stage_a_commit=stage_a_commit,
        catalog_sha=catalog_sha,
        source_sha=source_sha,
        stage_b_commit=str(stage_b_result["stage_b_runner_code_commit"]),
        stage_b_passers=stage_b_passers,
        stage_b_records=stage_b_records,
    )

    ranked = sorted(
        stage_c_passers,
        key=lambda fp: _final_rank_key(fp, stage_b_rows, stage_c_rows),
    )
    catalog = _catalog_by_fingerprint(stage_a_commit)
    selected: list[str] = []
    skipped_reasons: dict[str, str] = {}
    pair_counts: dict[str, int] = {}
    family_counts: dict[str, int] = {}
    cell_counts: dict[tuple[str, str, str], int] = {}

    for fingerprint in ranked:
        strategy = catalog[fingerprint].strategy
        cell = (strategy.symbol, strategy.family, strategy.timeframe)
        if len(selected) >= 11:
            skipped_reasons[fingerprint] = "FINAL_SHORTLIST_LIMIT"
            continue
        if pair_counts.get(strategy.symbol, 0) >= 4:
            skipped_reasons[fingerprint] = "PAIR_DIVERSITY_CAP"
            continue
        if family_counts.get(strategy.family, 0) >= 3:
            skipped_reasons[fingerprint] = "FAMILY_DIVERSITY_CAP"
            continue
        if cell_counts.get(cell, 0) >= 2:
            skipped_reasons[fingerprint] = "CELL_DIVERSITY_CAP"
            continue
        selected.append(fingerprint)
        pair_counts[strategy.symbol] = pair_counts.get(strategy.symbol, 0) + 1
        family_counts[strategy.family] = family_counts.get(strategy.family, 0) + 1
        cell_counts[cell] = cell_counts.get(cell, 0) + 1

    stage_a_set = set(stage_a_survivors)
    stage_b_set = set(stage_b_passers)
    stage_c_set = set(stage_c_passers)
    selected_set = set(selected)
    dispositions: list[dict[str, object]] = []
    for fingerprint in sorted(catalog):
        record = catalog[fingerprint]
        if fingerprint in selected_set:
            transitioned = transition_strategy(
                record,
                StrategyLifecycle.HISTORICAL_QUALIFIED,
                evidence_id=_FINAL_EVIDENCE_ID,
            )
            reason = "SELECTED_FINAL_SHORTLIST"
        else:
            transitioned = transition_strategy(
                record,
                StrategyLifecycle.RETIRED,
                evidence_id=_FINAL_EVIDENCE_ID,
            )
            if fingerprint not in stage_a_set:
                reason = "NOT_STAGE_A_SURVIVOR"
            elif fingerprint not in stage_b_set:
                reason = "FAILED_STAGE_B"
            elif fingerprint not in stage_c_set:
                reason = "FAILED_STAGE_C"
            else:
                reason = skipped_reasons[fingerprint]
        dispositions.append(
            {
                "strategy_fingerprint": fingerprint,
                "symbol": record.strategy.symbol,
                "family": record.strategy.family,
                "timeframe": record.strategy.timeframe,
                "lifecycle": transitioned.lifecycle.value,
                "evidence_id": transitioned.evidence_id,
                "reason": reason,
            }
        )

    return {
        "protocol": EXP015_FINAL_PROTOCOL,
        "experiment_id": EXP015_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "stage_a_authorization_sha256": stage_a_sha,
        "stage_b_result_sha256": stage_b_sha,
        "stage_c_result_sha256": stage_c_sha,
        "stage_a_runner_code_commit": stage_a_commit,
        "stage_b_runner_code_commit": stage_b_result["stage_b_runner_code_commit"],
        "stage_c_runner_code_commit": stage_c_result["stage_c_runner_code_commit"],
        "catalog_identity_sha256": catalog_sha,
        "strategy_source_sha256": source_sha,
        "tested_candidate_count": 567,
        "stage_a_survivor_count": len(stage_a_survivors),
        "stage_b_pass_count": len(stage_b_passers),
        "stage_c_pass_count": len(stage_c_passers),
        "final_ranked_fingerprints": ranked,
        "historical_qualified_count": len(selected),
        "historical_qualified_fingerprints": selected,
        "selected_pair_counts": dict(sorted(pair_counts.items())),
        "selected_family_counts": dict(sorted(family_counts.items())),
        "selected_cell_counts": {
            "|".join(key): value
            for key, value in sorted(cell_counts.items())
        },
        "outcome": (
            "CHALLENGER_DISCOVERY_PASS"
            if selected
            else "NO_CHALLENGER_QUALIFIED"
        ),
        "lifecycle_dispositions": dispositions,
    }


def resolve_exp015_historical_qualified_records(
    final_result: Mapping[str, object],
) -> tuple[StrategyRecord, ...]:
    if final_result.get("protocol") != EXP015_FINAL_PROTOCOL:
        raise ValueError("EXP-015 final shortlist protocol mismatch")
    stage_a_commit = _validate_commit(
        final_result.get("stage_a_runner_code_commit"),
        field="EXP-015 Stage A runner commit",
    )
    raw = final_result.get("historical_qualified_fingerprints")
    if not isinstance(raw, list) or len(raw) > 11:
        raise ValueError("EXP-015 historical-qualified fingerprint list is malformed")
    fingerprints = tuple(str(item) for item in raw)
    if len(set(fingerprints)) != len(fingerprints):
        raise ValueError("EXP-015 historical-qualified list contains duplicates")
    catalog = _catalog_by_fingerprint(stage_a_commit)
    if not set(fingerprints).issubset(catalog):
        raise ValueError("EXP-015 historical-qualified identity is outside catalog")
    return tuple(
        transition_strategy(
            catalog[fingerprint],
            StrategyLifecycle.HISTORICAL_QUALIFIED,
            evidence_id=_FINAL_EVIDENCE_ID,
        )
        for fingerprint in fingerprints
    )


def _write_stage_artifacts(
    *,
    result: Mapping[str, object],
    out_dir: Path,
    filename: str,
    expected_protocol: str,
    artifact_protocol: str,
) -> dict[str, object]:
    if result.get("protocol") != expected_protocol:
        raise ValueError("EXP-015 stage artifact protocol mismatch")
    if result.get("promotion_authorized") is not False:
        raise ValueError("EXP-015 stage artifact cannot authorize broker/shadow promotion")
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / filename
    _atomic_write(result_path, _stable_json_bytes(dict(result)))
    manifest = {
        "protocol": artifact_protocol,
        "experiment_id": EXP015_ID,
        "promotion_authorized": False,
        "artifacts": [_artifact_record(result_path)],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


def write_exp015_stage_b_artifacts(
    result: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    return _write_stage_artifacts(
        result=result,
        out_dir=out_dir,
        filename="stage-b.json",
        expected_protocol=EXP015_STAGE_B_PROTOCOL,
        artifact_protocol=EXP015_STAGE_B_ARTIFACT_PROTOCOL,
    )


def write_exp015_stage_c_artifacts(
    result: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    return _write_stage_artifacts(
        result=result,
        out_dir=out_dir,
        filename="stage-c.json",
        expected_protocol=EXP015_STAGE_C_PROTOCOL,
        artifact_protocol=EXP015_STAGE_C_ARTIFACT_PROTOCOL,
    )


def write_exp015_final_artifacts(
    result: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    return _write_stage_artifacts(
        result=result,
        out_dir=out_dir,
        filename="final-shortlist.json",
        expected_protocol=EXP015_FINAL_PROTOCOL,
        artifact_protocol=EXP015_FINAL_ARTIFACT_PROTOCOL,
    )


__all__ = [
    "EXP015_FINAL_PROTOCOL",
    "EXP015_STAGE_B_PROTOCOL",
    "EXP015_STAGE_C_PROTOCOL",
    "finalize_exp015_shortlist",
    "resolve_exp015_historical_qualified_records",
    "run_exp015_stage_b",
    "run_exp015_stage_c",
    "validate_exp015_stage_a_authorization",
    "write_exp015_final_artifacts",
    "write_exp015_stage_b_artifacts",
    "write_exp015_stage_c_artifacts",
]
