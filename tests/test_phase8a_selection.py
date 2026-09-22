from datetime import date
import unittest

from fmp.portfolio import (
    StrategyLifecycle,
    StrategyRecord,
    StrategyVersion,
    build_phase4_baseline_inventory,
)
from fmp.portfolio.selection import (
    NO_PORTFOLIO_SELECTED,
    PORTFOLIO_SELECTION_PASS,
    SelectionScenarioMetrics,
    PortfolioSelectionRecord,
    annualized_compounded_return,
    enumerate_portfolio_sets,
    freeze_selection_pool,
    evaluate_selection_gates,
    rank_passing_portfolios,
)


COMMIT = "a" * 40


def _version(index: int, symbol: str = "EURUSD") -> StrategyVersion:
    return StrategyVersion.create(
        family=f"family_{index}",
        version=f"v{index}",
        symbol=symbol,
        timeframe="15m",
        parameters={"index": index},
        signal_contract_version="selection-test-v1",
        code_commit=COMMIT,
    )


def _record(index: int, lifecycle: StrategyLifecycle = StrategyLifecycle.HISTORICAL_QUALIFIED) -> StrategyRecord:
    return StrategyRecord(
        strategy=_version(index, symbol=("EURUSD", "GBPUSD", "USDJPY")[index % 3]),
        lifecycle=lifecycle,
        evidence_id=f"EVIDENCE-{index}",
    )


def _scenario(
    slippage: float,
    *,
    net_return: float = 0.20,
    expectancy: float | None = 10.0,
    pf: float = 1.5,
    dd: float = 0.04,
    trades: int = 300,
    annualized: float = 0.025,
    positive_years: int = 6,
    year_share: float = 0.30,
    strategy_share: float = 0.50,
    pair_share: float = 0.60,
    families: int = 2,
    pairs: int = 2,
) -> SelectionScenarioMetrics:
    return SelectionScenarioMetrics(
        slippage_pips=slippage,
        net_return=net_return,
        expectancy_usd=expectancy,
        profit_factor=pf,
        max_drawdown_fraction=dd,
        trade_count=trades,
        annualized_compounded_return=annualized,
        positive_year_count=positive_years,
        max_positive_year_pnl_share=year_share,
        max_positive_strategy_pnl_share=strategy_share,
        max_positive_pair_pnl_share=pair_share,
        active_strategy_family_count=families,
        active_pair_count=pairs,
        days_ge_10pct_fraction=0.0,
    )


class Phase8ASelectionTests(unittest.TestCase):
    def test_pool_accepts_only_selection_eligible_lifecycle_states(self) -> None:
        allowed = (
            StrategyLifecycle.HISTORICAL_QUALIFIED,
            StrategyLifecycle.SHADOW_CANDIDATE,
            StrategyLifecycle.SHADOW_VALIDATED,
            StrategyLifecycle.DEMO_ELIGIBLE,
        )
        records = tuple(_record(i, state) for i, state in enumerate(allowed))
        pool = freeze_selection_pool(records)
        self.assertEqual(len(pool.records), 4)
        self.assertEqual(
            tuple(item.strategy.fingerprint for item in pool.records),
            tuple(sorted(item.strategy.fingerprint for item in records)),
        )

        for state in (
            StrategyLifecycle.DISCOVERY,
            StrategyLifecycle.CHALLENGER,
            StrategyLifecycle.RETIRED,
        ):
            with self.assertRaises(ValueError):
                freeze_selection_pool((_record(0), _record(1, state)))


    def test_current_historical_inventory_has_only_one_selection_eligible_strategy(self) -> None:
        eligible = tuple(
            item
            for item in build_phase4_baseline_inventory()
            if item.lifecycle
            in {
                StrategyLifecycle.HISTORICAL_QUALIFIED,
                StrategyLifecycle.SHADOW_CANDIDATE,
                StrategyLifecycle.SHADOW_VALIDATED,
                StrategyLifecycle.DEMO_ELIGIBLE,
            }
        )
        self.assertEqual(len(eligible), 1)
        with self.assertRaisesRegex(ValueError, "between 2 and 12"):
            freeze_selection_pool(eligible)

    def test_pool_fails_closed_below_two_or_above_twelve(self) -> None:
        with self.assertRaises(ValueError):
            freeze_selection_pool((_record(0),))
        with self.assertRaises(ValueError):
            freeze_selection_pool(tuple(_record(i) for i in range(13)))

    def test_portfolio_enumeration_is_deterministic_and_bounded_to_six(self) -> None:
        pool = freeze_selection_pool(tuple(_record(i) for i in range(4)))
        sets = enumerate_portfolio_sets(pool)
        self.assertEqual(len(sets), 15)
        self.assertEqual(
            tuple(len(item) for item in sets),
            (1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4),
        )

        pool_12 = freeze_selection_pool(tuple(_record(i) for i in range(12)))
        sets_12 = enumerate_portfolio_sets(pool_12)
        self.assertEqual(len(sets_12), 2509)
        self.assertEqual(max(map(len, sets_12)), 6)

    def test_annualized_return_uses_frozen_formula(self) -> None:
        value = annualized_compounded_return(
            starting_equity_usd=100_000.0,
            ending_equity_usd=121_000.0,
            start=date(2020, 1, 1),
            end_exclusive=date(2022, 1, 1),
        )
        self.assertAlmostEqual(value, 0.09993, places=4)

    def test_gate_passes_only_when_both_costs_and_02_stability_pass(self) -> None:
        fps = tuple(sorted((_version(1).fingerprint, _version(2, "GBPUSD").fingerprint)))
        record = PortfolioSelectionRecord(
            strategy_fingerprints=fps,
            scenarios=(
                _scenario(0.2),
                _scenario(0.5, annualized=0.020),
                _scenario(1.0, net_return=-0.02, expectancy=-1.0, pf=0.95, annualized=-0.003),
            ),
        )
        result = evaluate_selection_gates(record)
        self.assertTrue(result.passed)
        self.assertEqual(result.outcome, PORTFOLIO_SELECTION_PASS)
        self.assertTrue(all(result.gates.values()))

        failed = PortfolioSelectionRecord(
            strategy_fingerprints=fps,
            scenarios=(
                _scenario(0.2, strategy_share=0.61),
                _scenario(0.5),
                _scenario(1.0),
            ),
        )
        failed_result = evaluate_selection_gates(failed)
        self.assertFalse(failed_result.passed)
        self.assertFalse(failed_result.gates["max_strategy_positive_pnl_share_02"])
        self.assertEqual(failed_result.outcome, NO_PORTFOLIO_SELECTED)

    def test_null_expectancy_fails_gate_without_schema_error(self) -> None:
        fps = tuple(
            sorted((_version(1).fingerprint, _version(2, "GBPUSD").fingerprint))
        )
        record = PortfolioSelectionRecord(
            strategy_fingerprints=fps,
            scenarios=(
                _scenario(0.2, expectancy=None),
                _scenario(0.5),
                _scenario(1.0),
            ),
        )
        result = evaluate_selection_gates(record)
        self.assertFalse(result.passed)
        self.assertFalse(result.gates["expectancy_positive_02"])

    def test_one_strategy_control_can_never_be_selected_as_multistrategy_winner(self) -> None:
        record = PortfolioSelectionRecord(
            strategy_fingerprints=(_version(1).fingerprint,),
            scenarios=(_scenario(0.2), _scenario(0.5), _scenario(1.0)),
        )
        result = evaluate_selection_gates(record)
        self.assertFalse(result.passed)
        self.assertFalse(result.gates["at_least_two_strategies"])

    def test_ranking_uses_exact_dec041_lexicographic_order(self) -> None:
        a = PortfolioSelectionRecord(
            strategy_fingerprints=tuple(sorted((_version(1).fingerprint, _version(2).fingerprint))),
            scenarios=(
                _scenario(0.2, annualized=0.05),
                _scenario(0.5, annualized=0.03, dd=0.04, pf=1.5),
                _scenario(1.0),
            ),
        )
        b = PortfolioSelectionRecord(
            strategy_fingerprints=tuple(sorted((_version(3).fingerprint, _version(4).fingerprint))),
            scenarios=(
                _scenario(0.2, annualized=0.04),
                _scenario(0.5, annualized=0.04, dd=0.049, pf=1.4),
                _scenario(1.0),
            ),
        )
        ranked = rank_passing_portfolios((a, b))
        self.assertEqual(ranked[0].strategy_fingerprints, b.strategy_fingerprints)

    def test_ranking_rejects_failed_records_and_returns_no_selection_when_none_pass(self) -> None:
        bad = PortfolioSelectionRecord(
            strategy_fingerprints=tuple(sorted((_version(1).fingerprint, _version(2).fingerprint))),
            scenarios=(
                _scenario(0.2, net_return=-0.01),
                _scenario(0.5),
                _scenario(1.0),
            ),
        )
        ranked = rank_passing_portfolios((bad,))
        self.assertEqual(ranked, ())


if __name__ == "__main__":
    unittest.main()
