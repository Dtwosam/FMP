from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from datetime import date
from pathlib import Path

from .challenger_round1 import (
    _artifact_record,
    _atomic_write,
    _mandatory_metrics_pass,
    _stable_json_bytes,
    _trade_count,
    opening_range_momentum_source_sha256,
)
from .challengers import EXP013_ID, build_opening_range_momentum_challengers
from .contracts import StrategyRecord
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

EXP013_STAGE_B_PROTOCOL = "fmp-phase8a-exp013-stage-b-v1"
EXP013_STAGE_B_ARTIFACT_PROTOCOL = "fmp-phase8a-exp013-stage-b-artifacts-v1"
_STAGE_A_AUTH_PROTOCOL = "fmp-phase8a-exp013-stage-a-authorization-v1"
_STAGE_B_RANGE = RetrospectiveRange(
    start=date(2024, 1, 1),
    end_exclusive=date(2026, 8, 21),
)
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _validate_authorization_shape(
    authorization: Mapping[str, object],
) -> tuple[str, str, tuple[str, ...], tuple[StrategyRecord, ...]]:
    if authorization.get("protocol") != _STAGE_A_AUTH_PROTOCOL:
        raise ValueError("EXP-013 Stage A authorization protocol mismatch")
    if authorization.get("experiment_id") != EXP013_ID:
        raise ValueError("EXP-013 Stage A authorization experiment mismatch")
    if authorization.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-013 Stage A authorization must be retrospective")
    if authorization.get("untouched_oos") is not False:
        raise ValueError("EXP-013 Stage A authorization cannot be untouched OOS")
    if authorization.get("promotion_authorized") is not False:
        raise ValueError("EXP-013 Stage A authorization cannot authorize promotion")
    if authorization.get("historical_status_mutation_authorized") is not False:
        raise ValueError("EXP-013 Stage A authorization cannot mutate historical status")
    if authorization.get("cell_count") != 9:
        raise ValueError("EXP-013 Stage A authorization must contain nine cells")
    if authorization.get("strategy_identity_count") != 36:
        raise ValueError("EXP-013 Stage A authorization must bind 36 strategies")

    stage_a_commit = authorization.get("runner_code_commit")
    if not isinstance(stage_a_commit, str) or not _COMMIT_RE.fullmatch(stage_a_commit):
        raise ValueError("invalid EXP-013 Stage A runner commit")

    source_sha = authorization.get("strategy_source_sha256")
    if not isinstance(source_sha, str) or not _SHA256_RE.fullmatch(source_sha):
        raise ValueError("invalid EXP-013 Stage A strategy source digest")

    raw_survivors = authorization.get("survivor_fingerprints")
    if not isinstance(raw_survivors, list):
        raise ValueError("EXP-013 Stage A survivor_fingerprints must be a list")
    survivors = tuple(sorted(str(item) for item in raw_survivors))
    if len(set(survivors)) != len(survivors):
        raise ValueError("EXP-013 Stage A authorization has duplicate survivors")
    if authorization.get("survivor_count") != len(survivors):
        raise ValueError("EXP-013 Stage A survivor count mismatch")
    expected_source_open = bool(survivors)
    if authorization.get("stage_b_source_open_authorized") is not expected_source_open:
        raise ValueError("EXP-013 Stage B source-open authorization mismatch")

    raw_cells = authorization.get("cells")
    if not isinstance(raw_cells, list) or len(raw_cells) != 9:
        raise ValueError("EXP-013 Stage A authorization cells are malformed")

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
            raise ValueError("EXP-013 Stage A authorization cell must be an object")
        symbol = raw_cell.get("symbol")
        timeframe = raw_cell.get("timeframe")
        if not isinstance(symbol, str) or not isinstance(timeframe, str):
            raise ValueError("EXP-013 Stage A authorization cell identity is malformed")
        cell = (symbol, timeframe)
        if cell not in expected_cells or cell in seen_cells:
            raise ValueError("EXP-013 Stage A authorization cell coverage mismatch")
        seen_cells.add(cell)

        raw_fingerprints = raw_cell.get("strategy_fingerprints")
        raw_cell_survivors = raw_cell.get("survivor_fingerprints")
        if not isinstance(raw_fingerprints, list) or len(raw_fingerprints) != 4:
            raise ValueError("EXP-013 Stage A cell must bind four strategies")
        if not isinstance(raw_cell_survivors, list):
            raise ValueError("EXP-013 Stage A cell survivor list is malformed")

        fingerprints = tuple(sorted(str(item) for item in raw_fingerprints))
        survivors_for_cell = tuple(sorted(str(item) for item in raw_cell_survivors))
        if len(set(fingerprints)) != 4:
            raise ValueError("EXP-013 Stage A cell has duplicate strategies")
        if any(not _SHA256_RE.fullmatch(item) for item in fingerprints):
            raise ValueError("EXP-013 Stage A cell has invalid strategy fingerprint")
        if not set(survivors_for_cell).issubset(set(fingerprints)):
            raise ValueError("EXP-013 Stage A cell survivor is outside its cell")
        if all_fingerprints.intersection(fingerprints):
            raise ValueError("EXP-013 Stage A strategy appears in multiple cells")
        all_fingerprints.update(fingerprints)
        cell_survivors.update(survivors_for_cell)

    if seen_cells != expected_cells:
        raise ValueError("EXP-013 Stage A authorization cell coverage mismatch")
    if len(all_fingerprints) != 36:
        raise ValueError("EXP-013 Stage A authorization must bind 36 unique strategies")
    if tuple(sorted(cell_survivors)) != survivors:
        raise ValueError("EXP-013 Stage A survivor union mismatch")

    catalog = build_opening_range_momentum_challengers(code_commit=stage_a_commit)
    catalog_by_fingerprint = {
        item.strategy.fingerprint: item
        for item in catalog
    }
    if set(catalog_by_fingerprint) != all_fingerprints:
        raise ValueError("EXP-013 Stage A authorization catalog identity mismatch")
    unknown = sorted(set(survivors) - set(catalog_by_fingerprint))
    if unknown:
        raise ValueError(f"unknown EXP-013 Stage A survivor fingerprints: {unknown}")

    records = tuple(catalog_by_fingerprint[item] for item in survivors)
    return stage_a_commit, source_sha, survivors, records


def validate_exp013_stage_a_authorization(
    authorization: Mapping[str, object],
) -> tuple[StrategyRecord, ...]:
    _, source_sha, _, records = _validate_authorization_shape(authorization)
    if source_sha != opening_range_momentum_source_sha256():
        raise ValueError("EXP-013 opening_range_momentum source digest mismatch")
    return records


def _validate_loaded(
    loaded: LoadedRetrospectiveBars,
    *,
    symbol: str,
) -> None:
    if loaded.evidence_label != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-013 Stage B source must be explicitly retrospective")
    if loaded.start != _STAGE_B_RANGE.start or loaded.end_exclusive != _STAGE_B_RANGE.end_exclusive:
        raise ValueError("EXP-013 Stage B loaded range does not match frozen confirmation range")
    if not loaded.bars:
        raise ValueError("EXP-013 Stage B requires at least one complete signal bar")
    if {item.symbol for item in loaded.bars} != {symbol}:
        raise ValueError("EXP-013 Stage B source bars do not match requested symbol")
    if not _SHA256_RE.fullmatch(loaded.processed_manifest_sha256):
        raise ValueError("EXP-013 Stage B processed manifest identity is malformed")


def _stage_b_gate(
    rows_by_slippage: Mapping[float, Mapping[str, object]],
) -> dict[str, object]:
    mandatory = (
        rows_by_slippage[0.2],
        rows_by_slippage[0.5],
    )
    mandatory_pass = all(_mandatory_metrics_pass(row) for row in mandatory)
    sample_pass = _trade_count(rows_by_slippage[0.2]) >= 75
    return {
        "mandatory_profitability_drawdown_pass": mandatory_pass,
        "sample_pass": sample_pass,
        "stage_b_pass": mandatory_pass and sample_pass,
    }


def run_exp013_stage_b(
    *,
    authorization: Mapping[str, object],
    stage_a_authorization_sha256: str,
    dataset_sources: Mapping[str, tuple[Path, Path]],
    code_commit: str,
    bars_loader: Callable[..., LoadedRetrospectiveBars] = load_phase8a_retrospective_bars,
    strategy_runner: Callable[..., Mapping[str, object]] = run_phase8a_retrospective_strategy,
) -> dict[str, object]:
    if not isinstance(stage_a_authorization_sha256, str) or not _SHA256_RE.fullmatch(
        stage_a_authorization_sha256
    ):
        raise ValueError("invalid EXP-013 Stage A authorization SHA-256")
    if not isinstance(code_commit, str) or not _COMMIT_RE.fullmatch(code_commit):
        raise ValueError("invalid EXP-013 Stage B runner commit")

    stage_a_commit, source_sha, survivors, records = _validate_authorization_shape(
        authorization
    )
    if not authorization.get("stage_b_source_open_authorized") or not survivors:
        raise ValueError("EXP-013 Stage B source-open is not authorized")
    if source_sha != opening_range_momentum_source_sha256():
        raise ValueError("EXP-013 opening_range_momentum source digest mismatch")

    required_symbols = tuple(sorted({item.strategy.symbol for item in records}))
    missing_sources = sorted(set(required_symbols) - set(dataset_sources))
    if missing_sources:
        raise ValueError(
            f"missing EXP-013 Stage B dataset sources: {missing_sources}"
        )

    loaded_cache: dict[tuple[str, str], LoadedRetrospectiveBars] = {}
    manifest_by_symbol: dict[str, str] = {}
    rows: list[dict[str, object]] = []
    indexed_rows: dict[str, dict[float, Mapping[str, object]]] = {}

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
                research_range=_STAGE_B_RANGE,
            )
            _validate_loaded(loaded, symbol=strategy.symbol)
            previous_manifest = manifest_by_symbol.get(strategy.symbol)
            if (
                previous_manifest is not None
                and previous_manifest != loaded.processed_manifest_sha256
            ):
                raise ValueError("EXP-013 Stage B manifest identity changed across timeframes")
            manifest_by_symbol[strategy.symbol] = loaded.processed_manifest_sha256
            loaded_cache[cell] = loaded

        expected_candidate_sha: str | None = None
        scenario_rows: dict[float, Mapping[str, object]] = {}
        for slippage_pips in SLIPPAGE_SCENARIOS:
            plan = Phase8ARetrospectivePlan(
                experiment_id=EXP013_ID,
                strategy=strategy,
                research_range=_STAGE_B_RANGE,
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
                raise ValueError("EXP-013 Stage B runner returned wrong strategy identity")
            if result.get("processed_manifest_sha256") != loaded.processed_manifest_sha256:
                raise ValueError("EXP-013 Stage B runner returned wrong manifest identity")
            if result.get("slippage_pips") != slippage_pips:
                raise ValueError("EXP-013 Stage B runner returned wrong slippage identity")

            candidate_sha = result.get("candidate_sha256")
            if not isinstance(candidate_sha, str) or not _SHA256_RE.fullmatch(candidate_sha):
                raise ValueError("EXP-013 Stage B runner omitted valid candidate SHA-256")
            if expected_candidate_sha is None:
                expected_candidate_sha = candidate_sha
            elif expected_candidate_sha != candidate_sha:
                raise ValueError(
                    "EXP-013 Stage B candidate sequence changed across slippage scenarios"
                )

            metrics = result.get("metrics")
            run_identity = result.get("run_identity")
            if not isinstance(metrics, Mapping) or not isinstance(run_identity, Mapping):
                raise ValueError("EXP-013 Stage B runner returned malformed evidence")

            row = {
                "strategy_fingerprint": strategy.fingerprint,
                "strategy_identity_json": strategy.identity_json,
                "family": strategy.family,
                "version": strategy.version,
                "symbol": strategy.symbol,
                "timeframe": strategy.timeframe,
                "parameters_json": strategy.parameters_json,
                "stage_a_lifecycle": record.lifecycle.value,
                "stage_a_evidence_id": record.evidence_id,
                "slippage_pips": slippage_pips,
                "candidate_sha256": candidate_sha,
                "run_identity": dict(run_identity),
                "metrics": dict(metrics),
            }
            rows.append(row)
            scenario_rows[slippage_pips] = row
        indexed_rows[strategy.fingerprint] = scenario_rows

    gates = {
        fingerprint: _stage_b_gate(indexed_rows[fingerprint])
        for fingerprint in sorted(indexed_rows)
    }
    passers = sorted(
        fingerprint
        for fingerprint, gate in gates.items()
        if gate["stage_b_pass"]
    )

    return {
        "protocol": EXP013_STAGE_B_PROTOCOL,
        "experiment_id": EXP013_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "historical_qualification_review_authorized": bool(passers),
        "historical_qualification_candidate_fingerprints": passers,
        "stage_a_authorization_sha256": stage_a_authorization_sha256,
        "stage_a_runner_code_commit": stage_a_commit,
        "stage_b_runner_code_commit": code_commit,
        "strategy_source_sha256": source_sha,
        "range_start": _STAGE_B_RANGE.start.isoformat(),
        "range_end_exclusive": _STAGE_B_RANGE.end_exclusive.isoformat(),
        "survivor_fingerprints": list(survivors),
        "strategy_identity_count": len(records),
        "scenario_run_count": len(rows),
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "processed_manifest_sha256_by_symbol": dict(sorted(manifest_by_symbol.items())),
        "opened_cells": [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "opened_artifact_months": list(loaded.opened_artifact_months),
            }
            for (symbol, timeframe), loaded in sorted(loaded_cache.items())
        ],
        "rows": rows,
        "strategy_gates": gates,
    }


def write_exp013_stage_b_artifacts(
    result: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    if result.get("protocol") != EXP013_STAGE_B_PROTOCOL:
        raise ValueError("EXP-013 Stage B result protocol mismatch")
    if result.get("promotion_authorized") is not False:
        raise ValueError("EXP-013 Stage B cannot authorize promotion")
    if result.get("historical_status_mutation_authorized") is not False:
        raise ValueError("EXP-013 Stage B cannot mutate lifecycle automatically")

    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / "stage-b.json"
    payload = _stable_json_bytes(dict(result))
    _atomic_write(result_path, payload)

    manifest = {
        "protocol": EXP013_STAGE_B_ARTIFACT_PROTOCOL,
        "experiment_id": EXP013_ID,
        "promotion_authorized": False,
        "artifacts": [_artifact_record(result_path)],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest
