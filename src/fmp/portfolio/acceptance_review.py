from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Mapping, Sequence

from .contracts import ChampionSet, StrategyLifecycle, StrategyRecord
from .registry import freeze_shadow_champion_set, transition_strategy
from .research_data import PHASE8A_RETROSPECTIVE_LABEL
from .selection import (
    NO_PORTFOLIO_SELECTED,
    PORTFOLIO_SELECTION_PASS,
    PortfolioSelectionRecord,
    SelectionScenarioMetrics,
    evaluate_selection_gates,
    rank_passing_portfolios,
)
from .selection_runner import (
    DEC042_EXPERIMENT_ID,
    DEC042_PREFLIGHT_PROTOCOL,
    DEC042_RESULT_PROTOCOL,
    _validate_preflight,
)

DEC045_EXPERIMENT_ID = "EXP-20260922-016"
PHASE8A_ACCEPTANCE_PROTOCOL = "fmp-phase8a-acceptance-v1"
PHASE8A_ACCEPTANCE_ARTIFACT_PROTOCOL = "fmp-phase8a-acceptance-artifacts-v1"

PHASE8A_SHADOW_CANDIDATE_ACCEPTED = "PHASE8A_SHADOW_CANDIDATE_ACCEPTED"
PHASE8A_RESEARCH_REJECTED = "PHASE8A_RESEARCH_REJECTED"

_PHASE7_BASELINE_EVIDENCE_ID = (
    "EXP-20260915-008:PHASE7_PROMOTE_TO_SHADOW_DESIGN"
)
_ACCEPTANCE_EVIDENCE_ID = (
    "EXP-20260922-016:PHASE8A_ACCEPT_SHADOW_CANDIDATE"
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _scenario_from_payload(
    value: Mapping[str, object],
) -> SelectionScenarioMetrics:
    def numeric(key: str, *, nullable: bool = False) -> float | None:
        raw = value.get(key)
        if raw is None and nullable:
            return None
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ValueError(f"DEC-045 scenario metric {key!r} must be numeric")
        number = float(raw)
        if not math.isfinite(number):
            raise ValueError(f"DEC-045 scenario metric {key!r} must be finite")
        return number

    def integer(key: str) -> int:
        raw = value.get(key)
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise ValueError(f"DEC-045 scenario metric {key!r} must be an integer")
        return raw

    slippage = numeric("slippage_pips")
    net_return = numeric("net_return")
    max_drawdown = numeric("max_drawdown_fraction")
    annualized = numeric("annualized_compounded_return")
    assert slippage is not None
    assert net_return is not None
    assert max_drawdown is not None
    assert annualized is not None
    return SelectionScenarioMetrics(
        slippage_pips=slippage,
        net_return=net_return,
        expectancy_usd=numeric("expectancy_usd", nullable=True),
        profit_factor=numeric("profit_factor", nullable=True),
        max_drawdown_fraction=max_drawdown,
        trade_count=integer("trade_count"),
        annualized_compounded_return=annualized,
        positive_year_count=integer("positive_year_count"),
        max_positive_year_pnl_share=numeric(
            "max_positive_year_pnl_share",
            nullable=True,
        ),
        max_positive_strategy_pnl_share=numeric(
            "max_positive_strategy_pnl_share",
            nullable=True,
        ),
        max_positive_pair_pnl_share=numeric(
            "max_positive_pair_pnl_share",
            nullable=True,
        ),
        active_strategy_family_count=integer("active_strategy_family_count"),
        active_pair_count=integer("active_pair_count"),
        days_ge_10pct_fraction=numeric(
            "days_ge_10pct_fraction",
            nullable=True,
        ),
    )


def _selection_record_from_row(
    row: Mapping[str, object],
) -> PortfolioSelectionRecord:
    raw_fingerprints = row.get("strategy_fingerprints")
    raw_scenarios = row.get("scenarios")
    if not isinstance(raw_fingerprints, list):
        raise ValueError("DEC-045 set-result fingerprints must be a list")
    if not isinstance(raw_scenarios, list):
        raise ValueError("DEC-045 set-result scenarios must be a list")
    fingerprints = tuple(str(item) for item in raw_fingerprints)
    scenarios = tuple(
        _scenario_from_payload(item)
        for item in raw_scenarios
        if isinstance(item, Mapping)
    )
    if len(scenarios) != len(raw_scenarios):
        raise ValueError("DEC-045 set-result scenario must be an object")
    return PortfolioSelectionRecord(
        strategy_fingerprints=fingerprints,
        scenarios=scenarios,
    )


def _scenario_map(
    record: PortfolioSelectionRecord,
) -> dict[float, SelectionScenarioMetrics]:
    return {item.slippage_pips: item for item in record.scenarios}


def _validate_dec042_evidence(
    *,
    preflight: Mapping[str, object],
    preflight_sha256: str,
    selection: Mapping[str, object],
    selection_sha256: str,
) -> tuple[
    tuple[StrategyRecord, ...],
    tuple[PortfolioSelectionRecord, ...],
    str,
]:
    preflight_sha = _validate_sha256(
        preflight_sha256,
        field="DEC-042 preflight digest",
    )
    selection_sha = _validate_sha256(
        selection_sha256,
        field="DEC-042 selection digest",
    )
    if preflight.get("protocol") != DEC042_PREFLIGHT_PROTOCOL:
        raise ValueError("DEC-045 DEC-042 preflight protocol mismatch")
    if selection.get("protocol") != DEC042_RESULT_PROTOCOL:
        raise ValueError("DEC-045 DEC-042 selection protocol mismatch")
    if preflight.get("experiment_id") != DEC042_EXPERIMENT_ID:
        raise ValueError("DEC-045 DEC-042 preflight experiment mismatch")
    if selection.get("experiment_id") != DEC042_EXPERIMENT_ID:
        raise ValueError("DEC-045 DEC-042 selection experiment mismatch")

    for label, value in (("preflight", preflight), ("selection", selection)):
        if value.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
            raise ValueError(f"DEC-045 {label} must be retrospective")
        if value.get("untouched_oos") is not False:
            raise ValueError(f"DEC-045 {label} cannot be untouched OOS")
        if value.get("promotion_authorized") is not False:
            raise ValueError(f"DEC-045 {label} cannot authorize promotion")
        if value.get("historical_status_mutation_authorized") is not False:
            raise ValueError(f"DEC-045 {label} cannot mutate lifecycle")
        if value.get("shadow_candidate_authorized") is not False:
            raise ValueError(f"DEC-045 {label} cannot pre-authorize shadow")

    code_commit = _validate_commit(
        selection.get("runner_code_commit"),
        field="DEC-042 selection runner commit",
    )
    if preflight.get("runner_code_commit") != code_commit:
        raise ValueError("DEC-045 DEC-042 runner commit mismatch")
    if selection.get("preflight_sha256") != preflight_sha:
        raise ValueError("DEC-045 selection/preflight digest mismatch")
    if selection.get("set_universe_sha256") != preflight.get(
        "set_universe_sha256"
    ):
        raise ValueError("DEC-045 DEC-042 set-universe digest mismatch")
    if selection.get("range_start") != preflight.get("range_start"):
        raise ValueError("DEC-045 DEC-042 range start mismatch")
    if selection.get("range_end_exclusive") != preflight.get(
        "range_end_exclusive"
    ):
        raise ValueError("DEC-045 DEC-042 range end mismatch")
    if selection.get("slippage_scenarios") != preflight.get(
        "slippage_scenarios"
    ):
        raise ValueError("DEC-045 DEC-042 slippage scenario mismatch")

    pool_records, expected_sets = _validate_preflight(
        preflight,
        code_commit=code_commit,
    )
    if selection.get("strategy_count") != len(pool_records):
        raise ValueError("DEC-045 DEC-042 strategy count mismatch")
    if selection.get("evaluated_set_count") != len(expected_sets):
        raise ValueError("DEC-045 DEC-042 evaluated set count mismatch")

    raw_rows = selection.get("set_results")
    if not isinstance(raw_rows, list) or len(raw_rows) != len(expected_sets):
        raise ValueError("DEC-045 DEC-042 set-results coverage mismatch")

    records: list[PortfolioSelectionRecord] = []
    rows_by_set: dict[tuple[str, ...], Mapping[str, object]] = {}
    for raw in raw_rows:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-045 DEC-042 set result must be an object")
        record = _selection_record_from_row(raw)
        fingerprints = record.strategy_fingerprints
        if fingerprints in rows_by_set:
            raise ValueError("DEC-045 DEC-042 duplicate set result")
        rows_by_set[fingerprints] = raw
        records.append(record)

        recomputed = evaluate_selection_gates(record)
        if raw.get("gates") != dict(recomputed.gates):
            raise ValueError("DEC-045 DEC-042 stored gates do not replay")
        if raw.get("passed") is not recomputed.passed:
            raise ValueError("DEC-045 DEC-042 stored pass flag does not replay")
        if raw.get("outcome") != recomputed.outcome:
            raise ValueError("DEC-045 DEC-042 stored outcome does not replay")

    if set(rows_by_set) != set(expected_sets):
        raise ValueError("DEC-045 DEC-042 set-results universe mismatch")

    ranked = rank_passing_portfolios(records)
    ranked_sets = [list(item.strategy_fingerprints) for item in ranked]
    if selection.get("ranked_passing_sets") != ranked_sets:
        raise ValueError("DEC-045 DEC-042 ranking does not replay")
    if selection.get("passing_set_count") != len(ranked):
        raise ValueError("DEC-045 DEC-042 passing-set count mismatch")

    selected = (
        list(ranked[0].strategy_fingerprints)
        if ranked
        else None
    )
    expected_outcome = (
        PORTFOLIO_SELECTION_PASS
        if selected is not None
        else NO_PORTFOLIO_SELECTED
    )
    if selection.get("outcome") != expected_outcome:
        raise ValueError("DEC-045 DEC-042 outcome mismatch")
    if selection.get("selected_strategy_fingerprints") != selected:
        raise ValueError("DEC-045 DEC-042 selected set mismatch")

    return tuple(pool_records), tuple(records), selection_sha


def _baseline_record(
    pool_records: Sequence[StrategyRecord],
) -> StrategyRecord:
    baseline = [
        item
        for item in pool_records
        if item.evidence_id == _PHASE7_BASELINE_EVIDENCE_ID
    ]
    if len(baseline) != 1:
        raise ValueError("DEC-045 requires exactly one Phase 7 baseline control")
    return baseline[0]


def _record_map(
    records: Sequence[PortfolioSelectionRecord],
) -> dict[tuple[str, ...], PortfolioSelectionRecord]:
    return {
        item.strategy_fingerprints: item
        for item in records
    }


def _diagnostic_delta(
    selected: SelectionScenarioMetrics,
    baseline: SelectionScenarioMetrics,
) -> dict[str, float | None]:
    def delta(
        left: float | None,
        right: float | None,
    ) -> float | None:
        if left is None or right is None:
            return None
        return left - right

    return {
        "net_return_delta": selected.net_return - baseline.net_return,
        "annualized_compounded_return_delta": (
            selected.annualized_compounded_return
            - baseline.annualized_compounded_return
        ),
        "max_drawdown_fraction_delta": (
            selected.max_drawdown_fraction
            - baseline.max_drawdown_fraction
        ),
        "profit_factor_delta": delta(
            selected.profit_factor,
            baseline.profit_factor,
        ),
        "trade_count_delta": float(
            selected.trade_count - baseline.trade_count
        ),
    }


def _strategy_row(
    before: StrategyRecord,
    after: StrategyRecord,
) -> dict[str, object]:
    return {
        "fingerprint": before.strategy.fingerprint,
        "identity_json": before.strategy.identity_json,
        "family": before.strategy.family,
        "symbol": before.strategy.symbol,
        "timeframe": before.strategy.timeframe,
        "parameters_json": before.strategy.parameters_json,
        "code_commit": before.strategy.code_commit,
        "prior_lifecycle": before.lifecycle.value,
        "prior_evidence_id": before.evidence_id,
        "lifecycle": after.lifecycle.value,
        "evidence_id": after.evidence_id,
    }


def review_phase8a_acceptance(
    *,
    preflight: Mapping[str, object],
    preflight_sha256: str,
    selection: Mapping[str, object],
    selection_sha256: str,
) -> dict[str, object]:
    pool_records, selection_records, verified_selection_sha = (
        _validate_dec042_evidence(
            preflight=preflight,
            preflight_sha256=preflight_sha256,
            selection=selection,
            selection_sha256=selection_sha256,
        )
    )
    baseline = _baseline_record(pool_records)
    record_map = _record_map(selection_records)
    baseline_key = (baseline.strategy.fingerprint,)
    if baseline_key not in record_map:
        raise ValueError("DEC-045 Phase 7 baseline control result is missing")

    baseline_scenarios = _scenario_map(record_map[baseline_key])
    selected_fingerprints = selection.get("selected_strategy_fingerprints")
    common = {
        "protocol": PHASE8A_ACCEPTANCE_PROTOCOL,
        "experiment_id": DEC045_EXPERIMENT_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
        "dec042_preflight_sha256": preflight_sha256,
        "dec042_selection_sha256": verified_selection_sha,
        "dec042_runner_code_commit": selection["runner_code_commit"],
        "baseline_strategy_fingerprint": baseline.strategy.fingerprint,
        "baseline_control_02": {
            "annualized_compounded_return": baseline_scenarios[
                0.2
            ].annualized_compounded_return,
            "net_return": baseline_scenarios[0.2].net_return,
            "max_drawdown_fraction": baseline_scenarios[
                0.2
            ].max_drawdown_fraction,
            "profit_factor": baseline_scenarios[0.2].profit_factor,
            "trade_count": baseline_scenarios[0.2].trade_count,
        },
        "baseline_control_05": {
            "annualized_compounded_return": baseline_scenarios[
                0.5
            ].annualized_compounded_return,
            "net_return": baseline_scenarios[0.5].net_return,
            "max_drawdown_fraction": baseline_scenarios[
                0.5
            ].max_drawdown_fraction,
            "profit_factor": baseline_scenarios[0.5].profit_factor,
            "trade_count": baseline_scenarios[0.5].trade_count,
        },
    }

    if selected_fingerprints is None:
        return common | {
            "outcome": PHASE8A_RESEARCH_REJECTED,
            "rejection_reason": "NO_DEC042_PORTFOLIO_SELECTED",
            "shadow_candidate_authorized": False,
            "phase8b_design_authorized": False,
            "selected_strategy_fingerprints": None,
            "economic_improvement_gate_passed": False,
            "shadow_candidate": None,
        }

    selected_key = tuple(str(item) for item in selected_fingerprints)
    selected_record = record_map.get(selected_key)
    if selected_record is None:
        raise ValueError("DEC-045 selected set result is missing")
    selected_gate = evaluate_selection_gates(selected_record)
    if not selected_gate.passed:
        raise ValueError("DEC-045 selected set does not replay as passing")
    if len(selected_key) < 2:
        raise ValueError("DEC-045 selected set must contain at least two strategies")

    selected_scenarios = _scenario_map(selected_record)
    improvement = (
        selected_scenarios[0.5].annualized_compounded_return
        > baseline_scenarios[0.5].annualized_compounded_return
    )
    diagnostics = {
        "selected_02": {
            "annualized_compounded_return": selected_scenarios[
                0.2
            ].annualized_compounded_return,
            "net_return": selected_scenarios[0.2].net_return,
            "max_drawdown_fraction": selected_scenarios[
                0.2
            ].max_drawdown_fraction,
            "profit_factor": selected_scenarios[0.2].profit_factor,
            "trade_count": selected_scenarios[0.2].trade_count,
        },
        "selected_05": {
            "annualized_compounded_return": selected_scenarios[
                0.5
            ].annualized_compounded_return,
            "net_return": selected_scenarios[0.5].net_return,
            "max_drawdown_fraction": selected_scenarios[
                0.5
            ].max_drawdown_fraction,
            "profit_factor": selected_scenarios[0.5].profit_factor,
            "trade_count": selected_scenarios[0.5].trade_count,
        },
        "diagnostic_delta_02": _diagnostic_delta(
            selected_scenarios[0.2],
            baseline_scenarios[0.2],
        ),
        "diagnostic_delta_05": _diagnostic_delta(
            selected_scenarios[0.5],
            baseline_scenarios[0.5],
        ),
        "selected_dec042_gates": dict(selected_gate.gates),
    }

    if not improvement:
        return common | diagnostics | {
            "outcome": PHASE8A_RESEARCH_REJECTED,
            "rejection_reason": (
                "NO_STRICT_05_ANNUALIZED_IMPROVEMENT_OVER_PHASE7_BASELINE"
            ),
            "shadow_candidate_authorized": False,
            "phase8b_design_authorized": False,
            "selected_strategy_fingerprints": list(selected_key),
            "economic_improvement_gate_passed": False,
            "shadow_candidate": None,
        }

    by_fingerprint = {
        item.strategy.fingerprint: item
        for item in pool_records
    }
    selected_records: list[StrategyRecord] = []
    for fingerprint in selected_key:
        record = by_fingerprint.get(fingerprint)
        if record is None:
            raise ValueError("DEC-045 selected strategy is outside DEC-042 pool")
        if record.lifecycle is not StrategyLifecycle.HISTORICAL_QUALIFIED:
            raise ValueError(
                "DEC-045 selected strategy must enter from HISTORICAL_QUALIFIED"
            )
        selected_records.append(record)

    transitioned = tuple(
        transition_strategy(
            record,
            StrategyLifecycle.SHADOW_CANDIDATE,
            evidence_id=_ACCEPTANCE_EVIDENCE_ID,
        )
        for record in selected_records
    )
    selected_digest = hashlib.sha256(
        json.dumps(
            list(selected_key),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    champion_set_id = f"phase8a-exp016-{selected_digest}"
    champion_set = freeze_shadow_champion_set(
        transitioned,
        champion_set_id=champion_set_id,
    )

    return common | diagnostics | {
        "outcome": PHASE8A_SHADOW_CANDIDATE_ACCEPTED,
        "rejection_reason": None,
        "shadow_candidate_authorized": True,
        "phase8b_design_authorized": True,
        "selected_strategy_fingerprints": list(selected_key),
        "economic_improvement_gate_passed": True,
        "shadow_candidate": {
            "champion_set_id": champion_set.champion_set_id,
            "champion_set_experiment_id": champion_set.experiment_id,
            "champion_set_fingerprint": champion_set.fingerprint,
            "strategy_fingerprints": [
                item.fingerprint
                for item in champion_set.strategies
            ],
            "strategies": [
                _strategy_row(before, after)
                for before, after in zip(
                    sorted(
                        selected_records,
                        key=lambda item: item.strategy.fingerprint,
                    ),
                    sorted(
                        transitioned,
                        key=lambda item: item.strategy.fingerprint,
                    ),
                )
            ],
        },
    }


def resolve_phase8a_shadow_candidate_records(
    acceptance: Mapping[str, object],
) -> tuple[StrategyRecord, ...]:
    if acceptance.get("protocol") != PHASE8A_ACCEPTANCE_PROTOCOL:
        raise ValueError("Phase 8A acceptance protocol mismatch")
    if acceptance.get("outcome") != PHASE8A_SHADOW_CANDIDATE_ACCEPTED:
        raise ValueError("Phase 8A acceptance did not produce a shadow candidate")
    if acceptance.get("shadow_candidate_authorized") is not True:
        raise ValueError("Phase 8A shadow candidate is not authorized")
    raw_candidate = acceptance.get("shadow_candidate")
    if not isinstance(raw_candidate, Mapping):
        raise ValueError("Phase 8A shadow-candidate manifest is missing")
    raw_strategies = raw_candidate.get("strategies")
    if not isinstance(raw_strategies, list) or not raw_strategies:
        raise ValueError("Phase 8A shadow-candidate strategies are malformed")

    records: list[StrategyRecord] = []
    for raw in raw_strategies:
        if not isinstance(raw, Mapping):
            raise ValueError("Phase 8A shadow-candidate strategy row is malformed")
        if raw.get("lifecycle") != StrategyLifecycle.SHADOW_CANDIDATE.value:
            raise ValueError("Phase 8A candidate lifecycle mismatch")
        identity_json = raw.get("identity_json")
        if not isinstance(identity_json, str):
            raise ValueError("Phase 8A candidate identity_json is missing")
        identity = json.loads(identity_json)
        from .contracts import StrategyVersion

        strategy = StrategyVersion.create(
            family=str(identity["family"]),
            version=str(identity["version"]),
            symbol=str(identity["symbol"]),
            timeframe=str(identity["timeframe"]),
            parameters=identity["parameters"],
            signal_contract_version=str(identity["signal_contract_version"]),
            code_commit=str(identity["code_commit"]),
        )
        if strategy.fingerprint != raw.get("fingerprint"):
            raise ValueError("Phase 8A candidate strategy fingerprint mismatch")
        records.append(
            StrategyRecord(
                strategy=strategy,
                lifecycle=StrategyLifecycle.SHADOW_CANDIDATE,
                evidence_id=str(raw["evidence_id"]),
            )
        )

    ordered = tuple(
        sorted(records, key=lambda item: item.strategy.fingerprint)
    )
    champion = freeze_shadow_champion_set(
        ordered,
        champion_set_id=str(raw_candidate["champion_set_id"]),
    )
    if champion.fingerprint != raw_candidate.get("champion_set_fingerprint"):
        raise ValueError("Phase 8A champion-set fingerprint mismatch")
    if [
        item.strategy.fingerprint
        for item in ordered
    ] != raw_candidate.get("strategy_fingerprints"):
        raise ValueError("Phase 8A champion strategy list mismatch")
    return ordered


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


def write_phase8a_acceptance_artifacts(
    result: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    if result.get("protocol") != PHASE8A_ACCEPTANCE_PROTOCOL:
        raise ValueError("Phase 8A acceptance artifact protocol mismatch")
    if result.get("promotion_authorized") is not False:
        raise ValueError("Phase 8A acceptance cannot authorize broker promotion")
    if result.get("demo_order_authorized") is not False:
        raise ValueError("Phase 8A acceptance cannot authorize demo orders")
    if result.get("live_order_authorized") is not False:
        raise ValueError("Phase 8A acceptance cannot authorize live orders")
    if result.get("broker_mutation_authorized") is not False:
        raise ValueError("Phase 8A acceptance cannot authorize broker mutation")
    if result.get("real_money_authorized") is not False:
        raise ValueError("Phase 8A acceptance cannot authorize real money")

    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / "acceptance.json"
    payload = _stable_json_bytes(dict(result))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE8A_ACCEPTANCE_ARTIFACT_PROTOCOL,
        "experiment_id": DEC045_EXPERIMENT_ID,
        "promotion_authorized": False,
        "artifacts": [
            {
                "path": result_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "DEC045_EXPERIMENT_ID",
    "PHASE8A_ACCEPTANCE_PROTOCOL",
    "PHASE8A_RESEARCH_REJECTED",
    "PHASE8A_SHADOW_CANDIDATE_ACCEPTED",
    "resolve_phase8a_shadow_candidate_records",
    "review_phase8a_acceptance",
    "write_phase8a_acceptance_artifacts",
]
