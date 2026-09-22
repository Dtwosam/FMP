from __future__ import annotations

import hashlib
import json
import math
import os
import re
from datetime import date
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .challenger_discovery import (
    build_exp015_challengers,
    exp015_catalog_identity_sha256,
)
from .challenger_discovery_stage_a import exp015_strategy_source_sha256
from .challenger_discovery_stage_bc import (
    EXP015_FINAL_PROTOCOL,
    resolve_exp015_historical_qualified_records,
)
from .contracts import StrategyLifecycle, StrategyRecord, StrategyVersion
from .historical_inventory import build_phase4_baseline_inventory
from .joint_research import (
    JOINT_PORTFOLIO_PROTOCOL,
    Phase8AJointPortfolioPlan,
    run_phase8a_joint_portfolio,
)
from .research_data import PHASE8A_RETROSPECTIVE_LABEL, RetrospectiveRange
from .research_runner import REQUESTED_RISK_FRACTION, SLIPPAGE_SCENARIOS, STARTING_EQUITY_USD
from .selection import (
    NO_PORTFOLIO_SELECTED,
    PORTFOLIO_SELECTION_PASS,
    PortfolioSelectionRecord,
    SelectionScenarioMetrics,
    annualized_compounded_return,
    enumerate_portfolio_sets,
    evaluate_selection_gates,
    freeze_selection_pool,
    rank_passing_portfolios,
)

DEC042_EXPERIMENT_ID = "EXP-20260922-014"
DEC042_PREFLIGHT_PROTOCOL = "fmp-phase8a-dec042-selection-preflight-v1"
DEC042_PREFLIGHT_ARTIFACT_PROTOCOL = (
    "fmp-phase8a-dec042-selection-preflight-artifacts-v1"
)
DEC042_RESULT_PROTOCOL = "fmp-phase8a-dec042-selection-v1"
DEC042_RESULT_ARTIFACT_PROTOCOL = "fmp-phase8a-dec042-selection-artifacts-v1"

_SELECTION_RANGE = RetrospectiveRange(
    start=date(2019, 1, 1),
    end_exclusive=date(2026, 8, 21),
)
_EXPECTED_YEARS = tuple(range(2019, 2027))
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SELECTION_ELIGIBLE_STATES = frozenset(
    {
        StrategyLifecycle.HISTORICAL_QUALIFIED,
        StrategyLifecycle.SHADOW_CANDIDATE,
        StrategyLifecycle.SHADOW_VALIDATED,
        StrategyLifecycle.DEMO_ELIGIBLE,
    }
)


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
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


def _set_universe_sha256(sets: Sequence[Sequence[str]]) -> str:
    payload = json.dumps(
        [list(item) for item in sets],
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_exp015_final_result(
    final_result: Mapping[str, object],
) -> tuple[StrategyRecord, ...]:
    if final_result.get("protocol") != EXP015_FINAL_PROTOCOL:
        raise ValueError("DEC-042 requires exact EXP-015 final-shortlist evidence")
    if final_result.get("experiment_id") != "EXP-20260922-015":
        raise ValueError("EXP-015 final result experiment mismatch")
    if final_result.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-015 final result must be retrospective")
    if final_result.get("untouched_oos") is not False:
        raise ValueError("EXP-015 final result cannot be untouched OOS")
    if final_result.get("promotion_authorized") is not False:
        raise ValueError("EXP-015 final result cannot authorize broker/shadow promotion")
    if final_result.get("tested_candidate_count") != 567:
        raise ValueError("EXP-015 final result must account for all 567 candidates")

    stage_a_commit = _validate_commit(
        final_result.get("stage_a_runner_code_commit"),
        field="EXP-015 Stage A runner commit",
    )
    catalog_sha = _validate_sha256(
        final_result.get("catalog_identity_sha256"),
        field="EXP-015 catalog digest",
    )
    source_sha = _validate_sha256(
        final_result.get("strategy_source_sha256"),
        field="EXP-015 strategy-source digest",
    )
    if catalog_sha != exp015_catalog_identity_sha256(code_commit=stage_a_commit):
        raise ValueError("EXP-015 final catalog identity mismatch")
    if source_sha != exp015_strategy_source_sha256():
        raise ValueError("EXP-015 strategy source changed after qualification")

    raw_selected = final_result.get("historical_qualified_fingerprints")
    if not isinstance(raw_selected, list):
        raise ValueError("EXP-015 historical-qualified list is malformed")
    selected = tuple(str(item) for item in raw_selected)
    if len(selected) > 11 or len(set(selected)) != len(selected):
        raise ValueError("EXP-015 historical-qualified shortlist is malformed")
    if final_result.get("historical_qualified_count") != len(selected):
        raise ValueError("EXP-015 historical-qualified count mismatch")

    raw_dispositions = final_result.get("lifecycle_dispositions")
    if not isinstance(raw_dispositions, list) or len(raw_dispositions) != 567:
        raise ValueError("EXP-015 final result must contain 567 lifecycle dispositions")
    by_fingerprint: dict[str, Mapping[str, object]] = {}
    for raw in raw_dispositions:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-015 lifecycle disposition must be an object")
        fingerprint = raw.get("strategy_fingerprint")
        if not isinstance(fingerprint, str) or not _SHA256_RE.fullmatch(fingerprint):
            raise ValueError("EXP-015 lifecycle disposition fingerprint is malformed")
        if fingerprint in by_fingerprint:
            raise ValueError("EXP-015 lifecycle disposition is duplicated")
        lifecycle = raw.get("lifecycle")
        if lifecycle not in (
            StrategyLifecycle.HISTORICAL_QUALIFIED.value,
            StrategyLifecycle.RETIRED.value,
        ):
            raise ValueError("EXP-015 final lifecycle disposition is invalid")
        if not isinstance(raw.get("reason"), str) or not str(raw["reason"]).strip():
            raise ValueError("EXP-015 lifecycle disposition reason is missing")
        by_fingerprint[fingerprint] = raw

    catalog = {
        item.strategy.fingerprint: item
        for item in build_exp015_challengers(code_commit=stage_a_commit)
    }
    if set(by_fingerprint) != set(catalog):
        raise ValueError("EXP-015 lifecycle dispositions do not cover exact catalog")

    resolved = resolve_exp015_historical_qualified_records(final_result)
    selected_from_dispositions = tuple(
        sorted(
            fingerprint
            for fingerprint, raw in by_fingerprint.items()
            if raw["lifecycle"] == StrategyLifecycle.HISTORICAL_QUALIFIED.value
        )
    )
    if selected_from_dispositions != tuple(sorted(selected)):
        raise ValueError("EXP-015 shortlist/lifecycle disposition mismatch")
    if tuple(item.strategy.fingerprint for item in resolved) != selected:
        raise ValueError("EXP-015 final shortlist ordering/identity mismatch")

    pair_counts: dict[str, int] = {}
    family_counts: dict[str, int] = {}
    cell_counts: dict[str, int] = {}
    for record in resolved:
        strategy = record.strategy
        pair_counts[strategy.symbol] = pair_counts.get(strategy.symbol, 0) + 1
        family_counts[strategy.family] = family_counts.get(strategy.family, 0) + 1
        cell = f"{strategy.symbol}|{strategy.family}|{strategy.timeframe}"
        cell_counts[cell] = cell_counts.get(cell, 0) + 1
    if any(value > 4 for value in pair_counts.values()):
        raise ValueError("EXP-015 selected pair cap exceeded")
    if any(value > 3 for value in family_counts.values()):
        raise ValueError("EXP-015 selected family cap exceeded")
    if any(value > 2 for value in cell_counts.values()):
        raise ValueError("EXP-015 selected cell cap exceeded")
    if final_result.get("selected_pair_counts") != dict(sorted(pair_counts.items())):
        raise ValueError("EXP-015 selected pair-count evidence mismatch")
    if final_result.get("selected_family_counts") != dict(sorted(family_counts.items())):
        raise ValueError("EXP-015 selected family-count evidence mismatch")
    if final_result.get("selected_cell_counts") != dict(sorted(cell_counts.items())):
        raise ValueError("EXP-015 selected cell-count evidence mismatch")

    expected_outcome = (
        "CHALLENGER_DISCOVERY_PASS"
        if selected
        else "NO_CHALLENGER_QUALIFIED"
    )
    if final_result.get("outcome") != expected_outcome:
        raise ValueError("EXP-015 final outcome mismatch")
    return resolved


def build_dec042_pool_records(
    exp015_final_result: Mapping[str, object],
) -> tuple[StrategyRecord, ...]:
    baseline = tuple(
        item
        for item in build_phase4_baseline_inventory()
        if item.lifecycle in _SELECTION_ELIGIBLE_STATES
    )
    if len(baseline) != 1:
        raise RuntimeError(
            "DEC-042 expects exactly one pre-challenger selection-eligible baseline"
        )
    challengers = _validate_exp015_final_result(exp015_final_result)
    pool = freeze_selection_pool((*baseline, *challengers))
    return pool.records


def _pool_row(record: StrategyRecord) -> dict[str, object]:
    return {
        "fingerprint": record.strategy.fingerprint,
        "identity_json": record.strategy.identity_json,
        "family": record.strategy.family,
        "version": record.strategy.version,
        "symbol": record.strategy.symbol,
        "timeframe": record.strategy.timeframe,
        "parameters_json": record.strategy.parameters_json,
        "signal_contract_version": record.strategy.signal_contract_version,
        "code_commit": record.strategy.code_commit,
        "lifecycle": record.lifecycle.value,
        "evidence_id": record.evidence_id,
    }


def build_dec042_preflight(
    *,
    exp015_final_result: Mapping[str, object],
    exp015_final_sha256: str,
    runner_code_commit: str,
) -> dict[str, object]:
    final_sha = _validate_sha256(
        exp015_final_sha256,
        field="EXP-015 final-shortlist artifact digest",
    )
    code_commit = _validate_commit(
        runner_code_commit,
        field="DEC-042 runner commit",
    )
    pool = freeze_selection_pool(build_dec042_pool_records(exp015_final_result))
    portfolio_sets = enumerate_portfolio_sets(pool)
    return {
        "protocol": DEC042_PREFLIGHT_PROTOCOL,
        "experiment_id": DEC042_EXPERIMENT_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "shadow_candidate_authorized": False,
        "runner_code_commit": code_commit,
        "exp015_final_sha256": final_sha,
        "range_start": _SELECTION_RANGE.start.isoformat(),
        "range_end_exclusive": _SELECTION_RANGE.end_exclusive.isoformat(),
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "starting_equity_usd": STARTING_EQUITY_USD,
        "requested_risk_fraction": REQUESTED_RISK_FRACTION,
        "strategy_count": len(pool.records),
        "pool_strategies": [_pool_row(item) for item in pool.records],
        "set_count": len(portfolio_sets),
        "portfolio_sets": [list(item) for item in portfolio_sets],
        "set_universe_sha256": _set_universe_sha256(portfolio_sets),
    }


def _reconstruct_preflight_records(
    preflight: Mapping[str, object],
) -> tuple[StrategyRecord, ...]:
    raw = preflight.get("pool_strategies")
    if not isinstance(raw, list):
        raise ValueError("DEC-042 preflight pool_strategies is malformed")
    records: list[StrategyRecord] = []
    for row in raw:
        if not isinstance(row, Mapping):
            raise ValueError("DEC-042 preflight strategy row must be an object")
        identity_json = row.get("identity_json")
        if not isinstance(identity_json, str):
            raise ValueError("DEC-042 preflight strategy identity_json is missing")
        try:
            identity = json.loads(identity_json)
        except json.JSONDecodeError as exc:
            raise ValueError("DEC-042 preflight strategy identity_json is malformed") from exc
        if not isinstance(identity, dict):
            raise ValueError("DEC-042 preflight strategy identity must be an object")
        strategy = StrategyVersion.create(
            family=str(identity["family"]),
            version=str(identity["version"]),
            symbol=str(identity["symbol"]),
            timeframe=str(identity["timeframe"]),
            parameters=identity["parameters"],
            signal_contract_version=str(identity["signal_contract_version"]),
            code_commit=str(identity["code_commit"]),
        )
        if strategy.identity_json != identity_json:
            raise ValueError("DEC-042 preflight strategy identity is non-canonical")
        if row.get("fingerprint") != strategy.fingerprint:
            raise ValueError("DEC-042 preflight strategy fingerprint mismatch")
        for key, expected in (
            ("family", strategy.family),
            ("version", strategy.version),
            ("symbol", strategy.symbol),
            ("timeframe", strategy.timeframe),
            ("parameters_json", strategy.parameters_json),
            ("signal_contract_version", strategy.signal_contract_version),
            ("code_commit", strategy.code_commit),
        ):
            if row.get(key) != expected:
                raise ValueError(f"DEC-042 preflight strategy {key} mismatch")
        try:
            lifecycle = StrategyLifecycle(str(row.get("lifecycle")))
        except ValueError as exc:
            raise ValueError("DEC-042 preflight lifecycle is invalid") from exc
        evidence_id = row.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise ValueError("DEC-042 preflight evidence_id is missing")
        records.append(
            StrategyRecord(
                strategy=strategy,
                lifecycle=lifecycle,
                evidence_id=evidence_id,
            )
        )
    pool = freeze_selection_pool(records)
    expected_rows = [_pool_row(item) for item in pool.records]
    if raw != expected_rows:
        raise ValueError("DEC-042 preflight pool ordering/content mismatch")
    return pool.records


def _validate_preflight(
    preflight: Mapping[str, object],
    *,
    code_commit: str,
) -> tuple[tuple[StrategyRecord, ...], tuple[tuple[str, ...], ...]]:
    if preflight.get("protocol") != DEC042_PREFLIGHT_PROTOCOL:
        raise ValueError("DEC-042 preflight protocol mismatch")
    if preflight.get("experiment_id") != DEC042_EXPERIMENT_ID:
        raise ValueError("DEC-042 preflight experiment mismatch")
    if preflight.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("DEC-042 preflight must be retrospective")
    if preflight.get("untouched_oos") is not False:
        raise ValueError("DEC-042 preflight cannot be untouched OOS")
    for field in (
        "promotion_authorized",
        "historical_status_mutation_authorized",
        "shadow_candidate_authorized",
    ):
        if preflight.get(field) is not False:
            raise ValueError(f"DEC-042 preflight {field} must remain false")
    expected_commit = _validate_commit(code_commit, field="DEC-042 runner commit")
    if preflight.get("runner_code_commit") != expected_commit:
        raise ValueError("DEC-042 preflight/runner commit mismatch")
    _validate_sha256(
        preflight.get("exp015_final_sha256"),
        field="EXP-015 final-shortlist artifact digest",
    )
    if preflight.get("range_start") != _SELECTION_RANGE.start.isoformat():
        raise ValueError("DEC-042 preflight range start drift")
    if preflight.get("range_end_exclusive") != _SELECTION_RANGE.end_exclusive.isoformat():
        raise ValueError("DEC-042 preflight range end drift")
    if preflight.get("slippage_scenarios") != list(SLIPPAGE_SCENARIOS):
        raise ValueError("DEC-042 preflight slippage scenario drift")
    if preflight.get("starting_equity_usd") != STARTING_EQUITY_USD:
        raise ValueError("DEC-042 preflight starting equity drift")
    if preflight.get("requested_risk_fraction") != REQUESTED_RISK_FRACTION:
        raise ValueError("DEC-042 preflight requested risk drift")

    records = _reconstruct_preflight_records(preflight)
    if preflight.get("strategy_count") != len(records):
        raise ValueError("DEC-042 preflight strategy count mismatch")
    expected_sets = enumerate_portfolio_sets(freeze_selection_pool(records))
    raw_sets = preflight.get("portfolio_sets")
    if raw_sets != [list(item) for item in expected_sets]:
        raise ValueError("DEC-042 preflight set universe mismatch")
    if preflight.get("set_count") != len(expected_sets):
        raise ValueError("DEC-042 preflight set count mismatch")
    if preflight.get("set_universe_sha256") != _set_universe_sha256(expected_sets):
        raise ValueError("DEC-042 preflight set-universe digest mismatch")
    return records, expected_sets


def _numeric(
    mapping: Mapping[str, object],
    key: str,
    *,
    nullable: bool = False,
) -> float | None:
    value = mapping.get(key)
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"DEC-042 metric {key!r} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"DEC-042 metric {key!r} must be finite")
    return number


def _nonnegative_int(mapping: Mapping[str, object], key: str) -> int:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"DEC-042 metric {key!r} must be a non-negative integer")
    return value


def _positive_year_metrics(
    metrics: Mapping[str, object],
) -> tuple[int, float | None, dict[str, float]]:
    raw = metrics.get("calendar_year_breakdown")
    if not isinstance(raw, Mapping):
        raise ValueError("DEC-042 calendar_year_breakdown is missing")
    expected = {str(year) for year in _EXPECTED_YEARS}
    unexpected = sorted(set(str(key) for key in raw) - expected)
    if unexpected:
        raise ValueError(f"DEC-042 unexpected calendar years: {unexpected}")

    pnl_by_year: dict[str, float] = {}
    for year in _EXPECTED_YEARS:
        key = str(year)
        bucket = raw.get(key)
        if bucket is None:
            pnl_by_year[key] = 0.0
            continue
        if not isinstance(bucket, Mapping):
            raise ValueError("DEC-042 calendar-year bucket must be an object")
        value = _numeric(bucket, "net_pnl_usd")
        assert value is not None
        pnl_by_year[key] = value

    positives = [value for value in pnl_by_year.values() if value > 0.0]
    denominator = sum(positives)
    return (
        len(positives),
        (max(positives) / denominator) if denominator > 0 else None,
        pnl_by_year,
    )


def _contribution_metrics(
    raw: object,
    *,
    allowed_keys: set[str],
    label: str,
) -> tuple[float | None, tuple[str, ...]]:
    if not isinstance(raw, Mapping):
        raise ValueError(f"DEC-042 {label} contribution is missing")
    unknown = sorted(set(str(key) for key in raw) - allowed_keys)
    if unknown:
        raise ValueError(f"DEC-042 {label} contribution has unknown keys: {unknown}")
    active: list[str] = []
    shares: list[float] = []
    saw_none = False
    for key in sorted(raw):
        bucket = raw[key]
        if not isinstance(bucket, Mapping):
            raise ValueError(f"DEC-042 {label} contribution bucket must be an object")
        trades = _nonnegative_int(bucket, "trade_count")
        if trades > 0:
            active.append(str(key))
        share = _numeric(bucket, "positive_pnl_share", nullable=True)
        if share is None:
            saw_none = True
        else:
            if not 0.0 <= share <= 1.0:
                raise ValueError(f"DEC-042 {label} positive PnL share must be in [0, 1]")
            shares.append(share)
    maximum = None if saw_none and not shares else (max(shares) if shares else None)
    return maximum, tuple(active)


def _validate_joint_result(
    *,
    result: Mapping[str, object],
    records: Sequence[StrategyRecord],
    slippage_pips: float,
    code_commit: str,
) -> tuple[SelectionScenarioMetrics, dict[str, object]]:
    if result.get("protocol") != JOINT_PORTFOLIO_PROTOCOL:
        raise ValueError("DEC-042 joint result protocol mismatch")
    if result.get("experiment_id") != DEC042_EXPERIMENT_ID:
        raise ValueError("DEC-042 joint result experiment mismatch")
    if result.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("DEC-042 joint result must be retrospective")
    if result.get("untouched_oos") is not False:
        raise ValueError("DEC-042 joint result cannot be untouched OOS")
    if result.get("promotion_authorized") is not False:
        raise ValueError("DEC-042 joint result cannot authorize promotion")
    if result.get("shared_account") is not True:
        raise ValueError("DEC-042 requires shared-account joint simulation")
    if result.get("execution_timeframe") != "1m":
        raise ValueError("DEC-042 execution timeframe drift")
    if result.get("slippage_pips") != slippage_pips:
        raise ValueError("DEC-042 joint-result slippage mismatch")
    if result.get("starting_equity_usd") != STARTING_EQUITY_USD:
        raise ValueError("DEC-042 joint-result starting equity drift")
    if result.get("requested_risk_fraction") != REQUESTED_RISK_FRACTION:
        raise ValueError("DEC-042 joint-result risk drift")
    if result.get("runner_code_commit") != code_commit:
        raise ValueError("DEC-042 joint-result runner commit mismatch")
    if result.get("range_start") != _SELECTION_RANGE.start.isoformat():
        raise ValueError("DEC-042 joint-result range start drift")
    if result.get("range_end_exclusive") != _SELECTION_RANGE.end_exclusive.isoformat():
        raise ValueError("DEC-042 joint-result range end drift")

    expected_fps = tuple(sorted(item.strategy.fingerprint for item in records))
    raw_fps = result.get("strategy_fingerprints")
    if raw_fps != list(expected_fps):
        raise ValueError("DEC-042 joint-result strategy identity mismatch")
    candidate_sha = _validate_sha256(
        result.get("candidate_sha256"),
        field="DEC-042 joint candidate digest",
    )

    run_identity = result.get("run_identity")
    if not isinstance(run_identity, Mapping):
        raise ValueError("DEC-042 joint run_identity is malformed")
    if run_identity.get("code_commit") != code_commit:
        raise ValueError("DEC-042 joint run_identity commit mismatch")
    if run_identity.get("slippage_pips") not in (None, slippage_pips):
        raise ValueError("DEC-042 joint run_identity slippage mismatch")

    required_symbols = {item.strategy.symbol for item in records}
    manifests = result.get("processed_manifest_sha256_by_symbol")
    if not isinstance(manifests, Mapping) or set(manifests) != required_symbols:
        raise ValueError("DEC-042 joint processed-manifest coverage mismatch")
    manifest_map: dict[str, str] = {}
    for symbol in sorted(required_symbols):
        manifest_map[symbol] = _validate_sha256(
            manifests[symbol],
            field=f"DEC-042 {symbol} processed-manifest digest",
        )

    metrics = result.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("DEC-042 joint metrics are missing")
    phase3 = metrics.get("phase3_metrics")
    if not isinstance(phase3, Mapping):
        raise ValueError("DEC-042 phase3_metrics are missing")
    net_return = _numeric(phase3, "net_return")
    expectancy = _numeric(phase3, "expectancy_usd", nullable=True)
    profit_factor = _numeric(phase3, "profit_factor", nullable=True)
    max_drawdown = _numeric(phase3, "max_drawdown_fraction")
    trade_count = _nonnegative_int(metrics, "trade_count")
    assert net_return is not None and max_drawdown is not None

    positive_year_count, max_year_share, pnl_by_year = _positive_year_metrics(metrics)

    record_by_fp = {item.strategy.fingerprint: item for item in records}
    max_strategy_share, active_strategy_fps = _contribution_metrics(
        result.get("strategy_contribution"),
        allowed_keys=set(record_by_fp),
        label="strategy",
    )
    active_families = {
        record_by_fp[fingerprint].strategy.family
        for fingerprint in active_strategy_fps
    }
    max_pair_share, active_pairs = _contribution_metrics(
        result.get("pair_contribution"),
        allowed_keys=required_symbols,
        label="pair",
    )

    daily = metrics.get("daily_return_summary")
    if not isinstance(daily, Mapping):
        raise ValueError("DEC-042 daily_return_summary is missing")
    days_ge_10 = _numeric(daily, "days_ge_10pct_fraction", nullable=True)
    if days_ge_10 is not None and not 0.0 <= days_ge_10 <= 1.0:
        raise ValueError("DEC-042 >=10% day fraction must be in [0, 1]")

    ending_equity = STARTING_EQUITY_USD * (1.0 + net_return)
    annualized = annualized_compounded_return(
        starting_equity_usd=STARTING_EQUITY_USD,
        ending_equity_usd=ending_equity,
        start=_SELECTION_RANGE.start,
        end_exclusive=_SELECTION_RANGE.end_exclusive,
    )
    scenario = SelectionScenarioMetrics(
        slippage_pips=slippage_pips,
        net_return=net_return,
        expectancy_usd=expectancy,
        profit_factor=profit_factor,
        max_drawdown_fraction=max_drawdown,
        trade_count=trade_count,
        annualized_compounded_return=annualized,
        positive_year_count=positive_year_count,
        max_positive_year_pnl_share=max_year_share,
        max_positive_strategy_pnl_share=max_strategy_share,
        max_positive_pair_pnl_share=max_pair_share,
        active_strategy_family_count=len(active_families),
        active_pair_count=len(active_pairs),
        days_ge_10pct_fraction=days_ge_10,
    )
    detail = {
        "slippage_pips": slippage_pips,
        "candidate_sha256": candidate_sha,
        "processed_manifest_sha256_by_symbol": manifest_map,
        "year_net_pnl_usd": pnl_by_year,
        "strategy_contribution": result.get("strategy_contribution"),
        "pair_contribution": result.get("pair_contribution"),
        "daily_return_summary": dict(daily),
    }
    return scenario, detail


def _scenario_payload(value: SelectionScenarioMetrics) -> dict[str, object]:
    return {
        "slippage_pips": value.slippage_pips,
        "net_return": value.net_return,
        "expectancy_usd": value.expectancy_usd,
        "profit_factor": value.profit_factor,
        "max_drawdown_fraction": value.max_drawdown_fraction,
        "trade_count": value.trade_count,
        "annualized_compounded_return": value.annualized_compounded_return,
        "positive_year_count": value.positive_year_count,
        "max_positive_year_pnl_share": value.max_positive_year_pnl_share,
        "max_positive_strategy_pnl_share": value.max_positive_strategy_pnl_share,
        "max_positive_pair_pnl_share": value.max_positive_pair_pnl_share,
        "active_strategy_family_count": value.active_strategy_family_count,
        "active_pair_count": value.active_pair_count,
        "days_ge_10pct_fraction": value.days_ge_10pct_fraction,
    }


def run_dec042_selection(
    *,
    preflight: Mapping[str, object],
    preflight_sha256: str,
    dataset_sources: Mapping[str, tuple[Path, Path]],
    code_commit: str,
    joint_command: Callable[..., Mapping[str, object]] = run_phase8a_joint_portfolio,
) -> dict[str, object]:
    preflight_sha = _validate_sha256(
        preflight_sha256,
        field="DEC-042 preflight artifact digest",
    )
    code_commit = _validate_commit(code_commit, field="DEC-042 runner commit")
    records, portfolio_sets = _validate_preflight(preflight, code_commit=code_commit)
    record_by_fp = {item.strategy.fingerprint: item for item in records}

    required_symbols = {item.strategy.symbol for item in records}
    missing = sorted(required_symbols - set(dataset_sources))
    if missing:
        raise ValueError(f"missing DEC-042 dataset sources: {missing}")

    global_manifest_by_symbol: dict[str, str] = {}
    selection_records: list[PortfolioSelectionRecord] = []
    evidence_rows: list[dict[str, object]] = []

    for fingerprints in portfolio_sets:
        set_records = tuple(record_by_fp[item] for item in fingerprints)
        scenario_values: list[SelectionScenarioMetrics] = []
        scenario_details: list[dict[str, object]] = []
        expected_candidate_sha: str | None = None
        set_manifest_by_symbol: dict[str, str] | None = None
        set_sources = {
            symbol: dataset_sources[symbol]
            for symbol in sorted({item.strategy.symbol for item in set_records})
        }

        for slippage_pips in SLIPPAGE_SCENARIOS:
            plan = Phase8AJointPortfolioPlan(
                experiment_id=DEC042_EXPERIMENT_ID,
                strategies=tuple(item.strategy for item in set_records),
                research_range=_SELECTION_RANGE,
                slippage_pips=slippage_pips,
                runner_code_commit=code_commit,
            )
            result = dict(
                joint_command(
                    plan=plan,
                    dataset_sources=set_sources,
                )
            )
            scenario, detail = _validate_joint_result(
                result=result,
                records=set_records,
                slippage_pips=slippage_pips,
                code_commit=code_commit,
            )
            candidate_sha = str(detail["candidate_sha256"])
            if expected_candidate_sha is None:
                expected_candidate_sha = candidate_sha
            elif candidate_sha != expected_candidate_sha:
                raise ValueError(
                    "DEC-042 candidate sequence changed across slippage scenarios"
                )

            manifests = dict(detail["processed_manifest_sha256_by_symbol"])
            if set_manifest_by_symbol is None:
                set_manifest_by_symbol = manifests
            elif manifests != set_manifest_by_symbol:
                raise ValueError(
                    "DEC-042 processed-manifest identity changed across cost scenarios"
                )
            for symbol, manifest_sha in manifests.items():
                previous = global_manifest_by_symbol.get(symbol)
                if previous is not None and previous != manifest_sha:
                    raise ValueError(
                        "DEC-042 processed-manifest identity changed across portfolio sets"
                    )
                global_manifest_by_symbol[symbol] = manifest_sha

            scenario_values.append(scenario)
            scenario_details.append(detail)

        record = PortfolioSelectionRecord(
            strategy_fingerprints=tuple(fingerprints),
            scenarios=tuple(scenario_values),
        )
        gate_result = evaluate_selection_gates(record)
        selection_records.append(record)
        evidence_rows.append(
            {
                "strategy_fingerprints": list(fingerprints),
                "scenarios": [_scenario_payload(item) for item in scenario_values],
                "scenario_diagnostics": scenario_details,
                "gates": dict(gate_result.gates),
                "passed": gate_result.passed,
                "outcome": gate_result.outcome,
            }
        )

    ranked = rank_passing_portfolios(selection_records)
    selected = ranked[0].strategy_fingerprints if ranked else None
    outcome = PORTFOLIO_SELECTION_PASS if selected is not None else NO_PORTFOLIO_SELECTED
    return {
        "protocol": DEC042_RESULT_PROTOCOL,
        "experiment_id": DEC042_EXPERIMENT_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "shadow_candidate_authorized": False,
        "preflight_sha256": preflight_sha,
        "exp015_final_sha256": preflight["exp015_final_sha256"],
        "runner_code_commit": code_commit,
        "range_start": _SELECTION_RANGE.start.isoformat(),
        "range_end_exclusive": _SELECTION_RANGE.end_exclusive.isoformat(),
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "strategy_count": len(records),
        "set_universe_sha256": preflight["set_universe_sha256"],
        "evaluated_set_count": len(selection_records),
        "passing_set_count": len(ranked),
        "processed_manifest_sha256_by_symbol": dict(
            sorted(global_manifest_by_symbol.items())
        ),
        "outcome": outcome,
        "selected_strategy_fingerprints": (
            list(selected) if selected is not None else None
        ),
        "ranked_passing_sets": [
            list(item.strategy_fingerprints)
            for item in ranked
        ],
        "set_results": evidence_rows,
    }


def write_dec042_preflight_artifacts(
    preflight: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    if preflight.get("protocol") != DEC042_PREFLIGHT_PROTOCOL:
        raise ValueError("DEC-042 preflight artifact protocol mismatch")
    if preflight.get("promotion_authorized") is not False:
        raise ValueError("DEC-042 preflight cannot authorize promotion")
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / "preflight.json"
    _atomic_write(result_path, _stable_json_bytes(dict(preflight)))
    manifest = {
        "protocol": DEC042_PREFLIGHT_ARTIFACT_PROTOCOL,
        "experiment_id": DEC042_EXPERIMENT_ID,
        "promotion_authorized": False,
        "artifacts": [_artifact_record(result_path)],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


def write_dec042_result_artifacts(
    result: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    if result.get("protocol") != DEC042_RESULT_PROTOCOL:
        raise ValueError("DEC-042 selection artifact protocol mismatch")
    if result.get("promotion_authorized") is not False:
        raise ValueError("DEC-042 selection result cannot authorize promotion")
    if result.get("shadow_candidate_authorized") is not False:
        raise ValueError("DEC-042 selection result cannot authorize shadow")
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / "selection.json"
    _atomic_write(result_path, _stable_json_bytes(dict(result)))
    manifest = {
        "protocol": DEC042_RESULT_ARTIFACT_PROTOCOL,
        "experiment_id": DEC042_EXPERIMENT_ID,
        "promotion_authorized": False,
        "artifacts": [_artifact_record(result_path)],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "DEC042_EXPERIMENT_ID",
    "DEC042_PREFLIGHT_PROTOCOL",
    "DEC042_RESULT_PROTOCOL",
    "build_dec042_pool_records",
    "build_dec042_preflight",
    "run_dec042_selection",
    "write_dec042_preflight_artifacts",
    "write_dec042_result_artifacts",
]
