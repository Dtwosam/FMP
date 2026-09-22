from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping

from fmp.contracts import SUPPORTED_SYMBOLS
from fmp.research.data import ELIGIBLE_TIMEFRAMES

from .contracts import StrategyRecord
from .historical_inventory import build_phase4_baseline_inventory
from .research_data import (
    LoadedRetrospectiveBars,
    PHASE8A_RETROSPECTIVE_LABEL,
    RetrospectiveRange,
    load_phase8a_retrospective_bars,
)
from .research_runner import (
    PHASE8A_RETROSPECTIVE_LABEL as RUNNER_RETROSPECTIVE_LABEL,
    SLIPPAGE_SCENARIOS,
    Phase8ARetrospectivePlan,
    run_phase8a_retrospective_strategy,
)

PHASE8A_BATCH_PROTOCOL = "fmp-phase8a-retrospective-batch-v1"
PHASE8A_BATCH_ARTIFACT_PROTOCOL = "fmp-phase8a-retrospective-batch-artifacts-v1"
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_FAMILIES = frozenset(
    {
        "session_breakout",
        "trend_continuation",
        "mean_reversion",
        "previous_day_rejection",
        "volatility_breakout",
        "session_sweep_rejection",
    }
)


@dataclass(frozen=True, slots=True)
class Phase8ABatchPlan:
    experiment_id: str
    symbol: str
    timeframe: str
    research_range: RetrospectiveRange
    runner_code_commit: str
    families: tuple[str, ...] = tuple(sorted(_FAMILIES))
    slippage_scenarios: tuple[float, ...] = SLIPPAGE_SCENARIOS

    def __post_init__(self) -> None:
        if not isinstance(self.experiment_id, str) or not self.experiment_id.strip():
            raise ValueError("experiment_id must be non-empty")
        if self.symbol not in SUPPORTED_SYMBOLS:
            raise ValueError(f"unsupported Phase 8A symbol: {self.symbol!r}")
        if self.timeframe not in ELIGIBLE_TIMEFRAMES:
            raise ValueError(f"unsupported Phase 8A timeframe: {self.timeframe!r}")
        if not isinstance(self.research_range, RetrospectiveRange):
            raise TypeError("research_range must be RetrospectiveRange")
        if not _COMMIT_RE.fullmatch(self.runner_code_commit):
            raise ValueError("runner_code_commit must be a 40-character lowercase hexadecimal SHA")
        normalized = tuple(sorted(set(self.families)))
        if not normalized:
            raise ValueError("batch must include at least one strategy family")
        unknown = set(normalized) - _FAMILIES
        if unknown:
            raise ValueError(f"unsupported Phase 8A strategy families: {sorted(unknown)}")
        if tuple(self.slippage_scenarios) != SLIPPAGE_SCENARIOS:
            raise ValueError("historical batch must run exactly 0.2, 0.5, and 1.0-pip scenarios")
        object.__setattr__(self, "families", normalized)


def select_historical_inventory(
    *,
    symbol: str,
    timeframe: str,
    families: Iterable[str] | None = None,
) -> tuple[StrategyRecord, ...]:
    if symbol not in SUPPORTED_SYMBOLS:
        raise ValueError(f"unsupported Phase 8A symbol: {symbol!r}")
    if timeframe not in ELIGIBLE_TIMEFRAMES:
        raise ValueError(f"unsupported Phase 8A timeframe: {timeframe!r}")

    selected_families = _FAMILIES if families is None else frozenset(families)
    if not selected_families:
        raise ValueError("at least one strategy family is required")
    unknown = selected_families - _FAMILIES
    if unknown:
        raise ValueError(f"unsupported Phase 8A strategy families: {sorted(unknown)}")

    rows = tuple(
        item
        for item in build_phase4_baseline_inventory()
        if item.strategy.symbol == symbol
        and item.strategy.timeframe == timeframe
        and item.strategy.family in selected_families
    )
    return tuple(sorted(rows, key=lambda item: item.strategy.fingerprint))


def run_phase8a_retrospective_batch(
    *,
    plan: Phase8ABatchPlan,
    dataset_root: Path,
    manifest_path: Path,
    bars_loader: Callable[..., LoadedRetrospectiveBars] = load_phase8a_retrospective_bars,
    strategy_runner: Callable[..., Mapping[str, object]] = run_phase8a_retrospective_strategy,
) -> dict[str, object]:
    if not isinstance(plan, Phase8ABatchPlan):
        raise TypeError("plan must be Phase8ABatchPlan")

    loaded = bars_loader(
        dataset_root=dataset_root,
        manifest_path=manifest_path,
        symbol=plan.symbol,
        timeframe=plan.timeframe,
        research_range=plan.research_range,
    )
    if loaded.evidence_label != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("batch source must be explicitly retrospective")
    if RUNNER_RETROSPECTIVE_LABEL != PHASE8A_RETROSPECTIVE_LABEL:
        raise RuntimeError("retrospective evidence-label contract drift")
    if loaded.start != plan.research_range.start or loaded.end_exclusive != plan.research_range.end_exclusive:
        raise ValueError("loaded retrospective range does not match batch plan")

    inventory = select_historical_inventory(
        symbol=plan.symbol,
        timeframe=plan.timeframe,
        families=plan.families,
    )
    results: list[dict[str, object]] = []
    for record in inventory:
        for slippage in plan.slippage_scenarios:
            run_plan = Phase8ARetrospectivePlan(
                experiment_id=plan.experiment_id,
                strategy=record.strategy,
                research_range=plan.research_range,
                slippage_pips=slippage,
                runner_code_commit=plan.runner_code_commit,
            )
            result = dict(
                strategy_runner(
                    plan=run_plan,
                    dataset_root=dataset_root,
                    manifest_path=manifest_path,
                    bars_loader=lambda **_: loaded,
                )
            )
            results.append(
                {
                    "historical_lifecycle": record.lifecycle.value,
                    "historical_evidence_id": record.evidence_id,
                    "promotion_authorized": False,
                    "result": result,
                }
            )

    return {
        "protocol": PHASE8A_BATCH_PROTOCOL,
        "experiment_id": plan.experiment_id,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": plan.symbol,
        "timeframe": plan.timeframe,
        "families": list(plan.families),
        "range_start": plan.research_range.start.isoformat(),
        "range_end_exclusive": plan.research_range.end_exclusive.isoformat(),
        "runner_code_commit": plan.runner_code_commit,
        "processed_manifest_sha256": loaded.processed_manifest_sha256,
        "opened_artifact_months": list(loaded.opened_artifact_months),
        "strategy_identity_count": len(inventory),
        "scenario_run_count": len(results),
        "slippage_scenarios": list(plan.slippage_scenarios),
        "results": results,
    }


def _stable_json_bytes(value: Mapping[str, object]) -> bytes:
    return (
        json.dumps(
            dict(value),
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


def write_phase8a_batch_artifacts(
    result: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / "batch.json"
    payload = _stable_json_bytes(result)
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE8A_BATCH_ARTIFACT_PROTOCOL,
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
