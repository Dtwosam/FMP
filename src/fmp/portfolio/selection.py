from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Mapping, Sequence

from .contracts import StrategyLifecycle, StrategyRecord

PORTFOLIO_SELECTION_PASS = "PORTFOLIO_SELECTION_PASS"
NO_PORTFOLIO_SELECTED = "NO_PORTFOLIO_SELECTED"

_SELECTION_ELIGIBLE_STATES = frozenset(
    {
        StrategyLifecycle.HISTORICAL_QUALIFIED,
        StrategyLifecycle.SHADOW_CANDIDATE,
        StrategyLifecycle.SHADOW_VALIDATED,
        StrategyLifecycle.DEMO_ELIGIBLE,
    }
)
_REQUIRED_SLIPPAGE = (0.2, 0.5, 1.0)


@dataclass(frozen=True, slots=True)
class SelectionPool:
    records: tuple[StrategyRecord, ...]

    def __post_init__(self) -> None:
        if not 2 <= len(self.records) <= 12:
            raise ValueError("DEC-042 selection pool must contain between 2 and 12 strategies")
        fingerprints = tuple(item.strategy.fingerprint for item in self.records)
        if fingerprints != tuple(sorted(fingerprints)):
            raise ValueError("selection pool must be sorted by strategy fingerprint")
        if len(set(fingerprints)) != len(fingerprints):
            raise ValueError("selection pool contains duplicate strategy identities")
        for record in self.records:
            if record.lifecycle not in _SELECTION_ELIGIBLE_STATES:
                raise ValueError(
                    f"ineligible selection lifecycle: {record.lifecycle.value}"
                )


@dataclass(frozen=True, slots=True)
class SelectionScenarioMetrics:
    slippage_pips: float
    net_return: float
    expectancy_usd: float | None
    profit_factor: float | None
    max_drawdown_fraction: float
    trade_count: int
    annualized_compounded_return: float
    positive_year_count: int
    max_positive_year_pnl_share: float | None
    max_positive_strategy_pnl_share: float | None
    max_positive_pair_pnl_share: float | None
    active_strategy_family_count: int
    active_pair_count: int
    days_ge_10pct_fraction: float | None

    def __post_init__(self) -> None:
        if self.slippage_pips not in _REQUIRED_SLIPPAGE:
            raise ValueError("selection scenario slippage must be exactly 0.2, 0.5, or 1.0")
        for field in (
            "net_return",
            "max_drawdown_fraction",
            "annualized_compounded_return",
        ):
            value = float(getattr(self, field))
            if not math.isfinite(value):
                raise ValueError(f"{field} must be finite")
        if self.expectancy_usd is not None and not math.isfinite(self.expectancy_usd):
            raise ValueError("expectancy_usd must be finite when present")
        if self.profit_factor is not None and (
            not math.isfinite(self.profit_factor) or self.profit_factor < 0
        ):
            raise ValueError("profit_factor must be finite and non-negative when present")
        if self.trade_count < 0:
            raise ValueError("trade_count must be non-negative")
        if self.positive_year_count < 0:
            raise ValueError("positive_year_count must be non-negative")
        if self.active_strategy_family_count < 0 or self.active_pair_count < 0:
            raise ValueError("active diversity counts must be non-negative")
        if self.max_drawdown_fraction < 0:
            raise ValueError("max_drawdown_fraction must be non-negative")
        for field in (
            "max_positive_year_pnl_share",
            "max_positive_strategy_pnl_share",
            "max_positive_pair_pnl_share",
            "days_ge_10pct_fraction",
        ):
            value = getattr(self, field)
            if value is None:
                continue
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{field} must be in [0, 1] when present")


@dataclass(frozen=True, slots=True)
class PortfolioSelectionRecord:
    strategy_fingerprints: tuple[str, ...]
    scenarios: tuple[SelectionScenarioMetrics, ...]

    def __post_init__(self) -> None:
        if not 1 <= len(self.strategy_fingerprints) <= 6:
            raise ValueError("portfolio set must contain between 1 and 6 strategies")
        if self.strategy_fingerprints != tuple(sorted(self.strategy_fingerprints)):
            raise ValueError("portfolio fingerprints must be sorted")
        if len(set(self.strategy_fingerprints)) != len(self.strategy_fingerprints):
            raise ValueError("portfolio contains duplicate strategy fingerprints")
        scenario_map = {item.slippage_pips: item for item in self.scenarios}
        if len(scenario_map) != len(self.scenarios):
            raise ValueError("duplicate slippage scenario")
        if tuple(sorted(scenario_map)) != _REQUIRED_SLIPPAGE:
            raise ValueError("portfolio record requires exactly 0.2, 0.5, and 1.0 scenarios")


@dataclass(frozen=True, slots=True)
class PortfolioGateResult:
    strategy_fingerprints: tuple[str, ...]
    passed: bool
    outcome: str
    gates: Mapping[str, bool]

    def __post_init__(self) -> None:
        object.__setattr__(self, "gates", MappingProxyType(dict(self.gates)))


def freeze_selection_pool(records: Sequence[StrategyRecord]) -> SelectionPool:
    materialized = tuple(records)
    if not 2 <= len(materialized) <= 12:
        raise ValueError("DEC-042 selection pool must contain between 2 and 12 strategies")
    for record in materialized:
        if not isinstance(record, StrategyRecord):
            raise TypeError("selection pool must contain StrategyRecord")
        if record.lifecycle not in _SELECTION_ELIGIBLE_STATES:
            raise ValueError(
                f"ineligible selection lifecycle: {record.lifecycle.value}"
            )
    ordered = tuple(sorted(materialized, key=lambda item: item.strategy.fingerprint))
    return SelectionPool(records=ordered)


def enumerate_portfolio_sets(pool: SelectionPool) -> tuple[tuple[str, ...], ...]:
    if not isinstance(pool, SelectionPool):
        raise TypeError("pool must be SelectionPool")
    fingerprints = tuple(item.strategy.fingerprint for item in pool.records)
    sets: list[tuple[str, ...]] = []
    for size in range(1, min(6, len(fingerprints)) + 1):
        sets.extend(itertools.combinations(fingerprints, size))
    return tuple(sets)


def annualized_compounded_return(
    *,
    starting_equity_usd: float,
    ending_equity_usd: float,
    start: date,
    end_exclusive: date,
) -> float:
    if not math.isfinite(starting_equity_usd) or starting_equity_usd <= 0:
        raise ValueError("starting equity must be finite and positive")
    if not math.isfinite(ending_equity_usd) or ending_equity_usd <= 0:
        raise ValueError("ending equity must be finite and positive")
    elapsed_days = (end_exclusive - start).days
    if elapsed_days <= 0:
        raise ValueError("annualization range must contain at least one day")
    return (
        (ending_equity_usd / starting_equity_usd)
        ** (365.2425 / elapsed_days)
        - 1.0
    )


def _scenario_map(
    record: PortfolioSelectionRecord,
) -> dict[float, SelectionScenarioMetrics]:
    return {item.slippage_pips: item for item in record.scenarios}


def evaluate_selection_gates(
    record: PortfolioSelectionRecord,
) -> PortfolioGateResult:
    if not isinstance(record, PortfolioSelectionRecord):
        raise TypeError("record must be PortfolioSelectionRecord")
    scenarios = _scenario_map(record)
    s02 = scenarios[0.2]
    s05 = scenarios[0.5]

    gates = {
        "at_least_two_strategies": len(record.strategy_fingerprints) >= 2,
        "net_return_positive_02": s02.net_return > 0,
        "net_return_positive_05": s05.net_return > 0,
        "expectancy_positive_02": (
            s02.expectancy_usd is not None and s02.expectancy_usd > 0
        ),
        "expectancy_positive_05": (
            s05.expectancy_usd is not None and s05.expectancy_usd > 0
        ),
        "profit_factor_gt_1_02": s02.profit_factor is not None and s02.profit_factor > 1.0,
        "profit_factor_gt_1_05": s05.profit_factor is not None and s05.profit_factor > 1.0,
        "max_drawdown_le_05_02": s02.max_drawdown_fraction <= 0.05,
        "max_drawdown_le_05_05": s05.max_drawdown_fraction <= 0.05,
        "trade_count_ge_200_02": s02.trade_count >= 200,
        "trade_count_ge_200_05": s05.trade_count >= 200,
        "positive_years_ge_5_02": s02.positive_year_count >= 5,
        "max_positive_year_pnl_share_02": (
            s02.max_positive_year_pnl_share is not None
            and s02.max_positive_year_pnl_share <= 0.45
        ),
        "max_strategy_positive_pnl_share_02": (
            s02.max_positive_strategy_pnl_share is not None
            and s02.max_positive_strategy_pnl_share <= 0.60
        ),
        "max_pair_positive_pnl_share_02": (
            s02.max_positive_pair_pnl_share is not None
            and s02.max_positive_pair_pnl_share <= 0.70
        ),
        "active_strategy_families_ge_2_02": s02.active_strategy_family_count >= 2,
        "active_pairs_ge_2_02": s02.active_pair_count >= 2,
    }
    passed = all(gates.values())
    return PortfolioGateResult(
        strategy_fingerprints=record.strategy_fingerprints,
        passed=passed,
        outcome=PORTFOLIO_SELECTION_PASS if passed else NO_PORTFOLIO_SELECTED,
        gates=gates,
    )


def _rank_key(record: PortfolioSelectionRecord) -> tuple[object, ...]:
    scenarios = _scenario_map(record)
    s02 = scenarios[0.2]
    s05 = scenarios[0.5]
    assert s05.profit_factor is not None
    assert s02.max_positive_strategy_pnl_share is not None
    assert s02.max_positive_pair_pnl_share is not None
    return (
        -s05.annualized_compounded_return,
        s05.max_drawdown_fraction,
        -s05.profit_factor,
        -s02.annualized_compounded_return,
        s02.max_positive_strategy_pnl_share,
        s02.max_positive_pair_pnl_share,
        len(record.strategy_fingerprints),
        record.strategy_fingerprints,
    )


def rank_passing_portfolios(
    records: Sequence[PortfolioSelectionRecord],
) -> tuple[PortfolioSelectionRecord, ...]:
    passing = [
        record
        for record in records
        if evaluate_selection_gates(record).passed
    ]
    return tuple(sorted(passing, key=_rank_key))
