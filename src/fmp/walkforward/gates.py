from __future__ import annotations

import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence

from .contracts import GATING_SLIPPAGE_SCENARIOS, SLIPPAGE_SCENARIOS, STAGE1_WINDOW, STAGE2_WINDOWS


@dataclass(frozen=True, slots=True)
class GateResult:
    passed: bool
    criteria: Mapping[str, bool]

    def __post_init__(self) -> None:
        object.__setattr__(self, "criteria", MappingProxyType(dict(self.criteria)))


@dataclass(frozen=True, slots=True)
class AggregateFinancialResult:
    candidate_id: str
    slippage_pips: float
    window_count: int
    net_return: float
    trade_count: int
    net_pnl_usd: float
    expectancy_usd: float | None
    gross_profit_usd: float
    gross_loss_usd: float
    profit_factor: float | None
    max_drawdown_fraction: float
    positive_window_count: int
    max_positive_window_share: float | None


def _finite_number(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{field} must be finite")
    return numeric


def _trade_count(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _optional_positive_metric(value: object, *, field: str) -> float | None:
    if value is None:
        return None
    return _finite_number(value, field=field)


def _validate_result_identity(result: object, *, expected_slippage: float, expected_window: str) -> str:
    candidate_id = getattr(result, "candidate_id", None)
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("Phase 7 gate result candidate_id must be non-empty")
    window_name = getattr(result, "window_name", None)
    if window_name != expected_window:
        raise ValueError("Phase 7 gate result window identity mismatch")
    slippage = _finite_number(getattr(result, "slippage_pips", None), field="slippage_pips")
    if slippage != expected_slippage:
        raise ValueError("Phase 7 gate result slippage identity mismatch")
    return candidate_id


def _validated_slippage_mapping(results_by_slippage: Mapping[float, object]) -> Mapping[float, object]:
    if not isinstance(results_by_slippage, Mapping):
        raise ValueError("Phase 7 gate results must be a mapping")
    if set(results_by_slippage) != set(SLIPPAGE_SCENARIOS):
        raise ValueError("Phase 7 gate results must contain exactly the frozen slippage scenarios")
    return results_by_slippage


def _positive(value: object, *, field: str) -> bool:
    return _finite_number(value, field=field) > 0.0


def _profit_factor_gt_one(value: object, *, field: str) -> bool:
    numeric = _optional_positive_metric(value, field=field)
    return numeric is not None and numeric > 1.0


def _drawdown_at_most_five_percent(value: object, *, field: str) -> bool:
    numeric = _finite_number(value, field=field)
    if numeric < 0.0:
        raise ValueError(f"{field} must be non-negative")
    return numeric <= 0.05


def stage1_gate(results_by_slippage: Mapping[float, object]) -> GateResult:
    rows = _validated_slippage_mapping(results_by_slippage)
    candidate_ids: set[str] = set()
    for slippage in SLIPPAGE_SCENARIOS:
        candidate_ids.add(
            _validate_result_identity(
                rows[slippage],
                expected_slippage=slippage,
                expected_window=STAGE1_WINDOW.name,
            )
        )
    if len(candidate_ids) != 1:
        raise ValueError("Stage 1 gate results must belong to exactly one frozen candidate")

    criteria: dict[str, bool] = {}
    for slippage in GATING_SLIPPAGE_SCENARIOS:
        row = rows[slippage]
        prefix = f"{slippage:.1f}"
        criteria[f"{prefix}_net_return_positive"] = _positive(
            getattr(row, "net_return", None), field=f"{prefix} net_return"
        )
        criteria[f"{prefix}_expectancy_positive"] = _positive(
            getattr(row, "expectancy_usd", None), field=f"{prefix} expectancy_usd"
        )
        criteria[f"{prefix}_profit_factor_gt_one"] = _profit_factor_gt_one(
            getattr(row, "profit_factor", None), field=f"{prefix} profit_factor"
        )
        criteria[f"{prefix}_max_drawdown_at_most_5pct"] = _drawdown_at_most_five_percent(
            getattr(row, "max_drawdown_fraction", None),
            field=f"{prefix} max_drawdown_fraction",
        )

    criteria["0.2_trade_count_at_least_40"] = (
        _trade_count(getattr(rows[0.2], "trade_count", None), field="0.2 trade_count") >= 40
    )
    return GateResult(passed=all(criteria.values()), criteria=criteria)


def aggregate_windows(results: Sequence[object]) -> AggregateFinancialResult:
    rows = tuple(results)
    expected_names = tuple(window.name for window in STAGE2_WINDOWS)
    if len(rows) != len(expected_names):
        raise ValueError("Phase 7 Stage 2 aggregate requires exactly seven windows")
    names = tuple(getattr(row, "window_name", None) for row in rows)
    if names != expected_names:
        raise ValueError("Phase 7 Stage 2 window identity/order mismatch")

    candidate_ids = {getattr(row, "candidate_id", None) for row in rows}
    if len(candidate_ids) != 1:
        raise ValueError("Phase 7 Stage 2 aggregate requires exactly one candidate")
    candidate_id = next(iter(candidate_ids))
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("Phase 7 Stage 2 candidate_id must be non-empty")

    slippages = {
        _finite_number(getattr(row, "slippage_pips", None), field="slippage_pips")
        for row in rows
    }
    if len(slippages) != 1:
        raise ValueError("Phase 7 Stage 2 aggregate requires one slippage scenario")
    slippage = next(iter(slippages))
    if slippage not in SLIPPAGE_SCENARIOS:
        raise ValueError("Phase 7 Stage 2 aggregate slippage is not frozen")

    net_returns: list[float] = []
    trade_counts: list[int] = []
    net_pnls: list[float] = []
    gross_profits: list[float] = []
    gross_losses: list[float] = []
    drawdowns: list[float] = []
    for row in rows:
        net_returns.append(_finite_number(getattr(row, "net_return", None), field="net_return"))
        trade_counts.append(_trade_count(getattr(row, "trade_count", None), field="trade_count"))
        net_pnls.append(_finite_number(getattr(row, "net_pnl_usd", None), field="net_pnl_usd"))
        gross_profit = _finite_number(
            getattr(row, "gross_profit_usd", None), field="gross_profit_usd"
        )
        gross_loss = _finite_number(
            getattr(row, "gross_loss_usd", None), field="gross_loss_usd"
        )
        drawdown = _finite_number(
            getattr(row, "max_drawdown_fraction", None), field="max_drawdown_fraction"
        )
        if gross_profit < 0.0 or gross_loss < 0.0 or drawdown < 0.0:
            raise ValueError("Phase 7 aggregate gross metrics and drawdown must be non-negative")
        gross_profits.append(gross_profit)
        gross_losses.append(gross_loss)
        drawdowns.append(drawdown)

    trade_count = sum(trade_counts)
    net_pnl = sum(net_pnls)
    gross_profit = sum(gross_profits)
    gross_loss = sum(gross_losses)
    positive_pnls = [value for value in net_pnls if value > 0.0]
    positive_total = sum(positive_pnls)
    max_positive_share = (
        max(positive_pnls) / positive_total if positive_pnls and positive_total > 0.0 else None
    )

    return AggregateFinancialResult(
        candidate_id=candidate_id,
        slippage_pips=slippage,
        window_count=len(rows),
        net_return=sum(net_returns),
        trade_count=trade_count,
        net_pnl_usd=net_pnl,
        expectancy_usd=(net_pnl / trade_count) if trade_count else None,
        gross_profit_usd=gross_profit,
        gross_loss_usd=gross_loss,
        profit_factor=(gross_profit / gross_loss) if gross_loss > 0.0 else None,
        max_drawdown_fraction=max(drawdowns),
        positive_window_count=len(positive_pnls),
        max_positive_window_share=max_positive_share,
    )


def stage2_gate(results_by_slippage: Mapping[float, Sequence[object]]) -> GateResult:
    rows = _validated_slippage_mapping(results_by_slippage)
    aggregates = {slippage: aggregate_windows(rows[slippage]) for slippage in SLIPPAGE_SCENARIOS}
    candidate_ids = {aggregate.candidate_id for aggregate in aggregates.values()}
    if len(candidate_ids) != 1:
        raise ValueError("Stage 2 gate results must belong to exactly one frozen candidate")
    for slippage, aggregate in aggregates.items():
        if aggregate.slippage_pips != slippage:
            raise ValueError("Stage 2 gate result slippage identity mismatch")

    criteria: dict[str, bool] = {}
    for slippage in GATING_SLIPPAGE_SCENARIOS:
        aggregate = aggregates[slippage]
        prefix = f"{slippage:.1f}"
        criteria[f"{prefix}_aggregate_net_return_positive"] = aggregate.net_return > 0.0
        criteria[f"{prefix}_aggregate_expectancy_positive"] = (
            aggregate.expectancy_usd is not None and aggregate.expectancy_usd > 0.0
        )
        criteria[f"{prefix}_aggregate_profit_factor_gt_one"] = (
            aggregate.profit_factor is not None and aggregate.profit_factor > 1.0
        )
        criteria[f"{prefix}_aggregate_max_drawdown_at_most_5pct"] = (
            aggregate.max_drawdown_fraction <= 0.05
        )

    baseline = aggregates[0.2]
    criteria["0.2_trade_count_at_least_100"] = baseline.trade_count >= 100
    criteria["0.2_positive_windows_at_least_4_of_7"] = baseline.positive_window_count >= 4
    criteria["0.2_max_positive_window_share_at_most_50pct"] = (
        baseline.max_positive_window_share is not None
        and baseline.max_positive_window_share <= 0.50
    )
    return GateResult(passed=all(criteria.values()), criteria=criteria)
