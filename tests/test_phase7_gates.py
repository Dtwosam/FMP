from __future__ import annotations

import unittest
from types import SimpleNamespace


STAGE2_WINDOWS = (
    "2025-Q1",
    "2025-Q2",
    "2025-Q3",
    "2025-Q4",
    "2026-Q1",
    "2026-Q2",
    "2026-partial-Q3",
)


def result(
    *,
    slippage: float,
    window: str = "stage1-2024",
    trades: int = 40,
    net_return: float = 0.01,
    net_pnl: float = 1_000.0,
    expectancy: float | None = 25.0,
    gross_profit: float = 2_000.0,
    gross_loss: float = 1_000.0,
    profit_factor: float | None = 2.0,
    drawdown: float = 0.05,
    candidate: str = "session_breakout",
):
    return SimpleNamespace(
        candidate_id=candidate,
        window_name=window,
        slippage_pips=slippage,
        trade_count=trades,
        net_return=net_return,
        net_pnl_usd=net_pnl,
        expectancy_usd=expectancy,
        gross_profit_usd=gross_profit,
        gross_loss_usd=gross_loss,
        profit_factor=profit_factor,
        max_drawdown_fraction=drawdown,
    )


def stage1_mapping(**overrides):
    rows = {
        0.2: result(slippage=0.2),
        0.5: result(slippage=0.5),
        1.0: result(slippage=1.0),
    }
    rows.update(overrides)
    return rows


def stage2_mapping(*, positive_pnls=None, trades_per_window: int = 15):
    if positive_pnls is None:
        positive_pnls = (100.0, 100.0, 100.0, 100.0, -50.0, -50.0, -50.0)
    out = {}
    for slippage in (0.2, 0.5, 1.0):
        rows = []
        for window, pnl in zip(STAGE2_WINDOWS, positive_pnls, strict=True):
            gross_profit = max(pnl, 0.0) + 200.0
            gross_loss = gross_profit - pnl
            rows.append(
                result(
                    slippage=slippage,
                    window=window,
                    trades=trades_per_window,
                    net_return=pnl / 100_000.0,
                    net_pnl=pnl,
                    expectancy=pnl / trades_per_window,
                    gross_profit=gross_profit,
                    gross_loss=gross_loss,
                    profit_factor=gross_profit / gross_loss if gross_loss > 0 else None,
                    drawdown=0.04,
                )
            )
        out[slippage] = tuple(rows)
    return out


class Phase7GateTests(unittest.TestCase):
    def test_stage1_trade_count_boundary_is_39_fail_40_pass_at_baseline_only(self) -> None:
        from fmp.walkforward.gates import stage1_gate

        rows = stage1_mapping()
        rows[0.2] = result(slippage=0.2, trades=39)
        self.assertFalse(stage1_gate(rows).passed)

        rows[0.2] = result(slippage=0.2, trades=40)
        rows[0.5] = result(slippage=0.5, trades=1)
        self.assertTrue(stage1_gate(rows).passed)

    def test_stage1_strict_profitability_boundaries_and_drawdown_inclusive_boundary(self) -> None:
        from fmp.walkforward.gates import stage1_gate

        for slippage in (0.2, 0.5):
            rows = stage1_mapping()
            rows[slippage] = result(slippage=slippage, net_return=0.0)
            self.assertFalse(stage1_gate(rows).passed)

            rows = stage1_mapping()
            rows[slippage] = result(slippage=slippage, expectancy=0.0)
            self.assertFalse(stage1_gate(rows).passed)

            rows = stage1_mapping()
            rows[slippage] = result(slippage=slippage, profit_factor=1.0)
            self.assertFalse(stage1_gate(rows).passed)

            rows = stage1_mapping()
            rows[slippage] = result(slippage=slippage, drawdown=0.0500001)
            self.assertFalse(stage1_gate(rows).passed)

            rows = stage1_mapping()
            rows[slippage] = result(slippage=slippage, drawdown=0.05)
            self.assertTrue(stage1_gate(rows).passed)

    def test_stage1_one_pip_is_diagnostic_only(self) -> None:
        from fmp.walkforward.gates import stage1_gate

        rows = stage1_mapping()
        rows[1.0] = result(
            slippage=1.0,
            trades=0,
            net_return=-1.0,
            net_pnl=-100_000.0,
            expectancy=-1_000.0,
            gross_profit=0.0,
            gross_loss=100_000.0,
            profit_factor=0.0,
            drawdown=1.0,
        )
        self.assertTrue(stage1_gate(rows).passed)

    def test_aggregate_windows_uses_independent_window_arithmetic(self) -> None:
        from fmp.walkforward.gates import aggregate_windows

        rows = tuple(
            result(
                slippage=0.2,
                window=window,
                trades=index + 1,
                net_return=(index + 1) / 1000.0,
                net_pnl=float((index + 1) * 100),
                expectancy=1.0,
                gross_profit=float((index + 1) * 150),
                gross_loss=float((index + 1) * 50),
                profit_factor=3.0,
                drawdown=(index + 1) / 100.0,
            )
            for index, window in enumerate(STAGE2_WINDOWS)
        )
        aggregate = aggregate_windows(rows)
        self.assertEqual(aggregate.window_count, 7)
        self.assertAlmostEqual(aggregate.net_return, sum(row.net_return for row in rows))
        self.assertEqual(aggregate.trade_count, sum(row.trade_count for row in rows))
        self.assertAlmostEqual(aggregate.net_pnl_usd, sum(row.net_pnl_usd for row in rows))
        self.assertAlmostEqual(
            aggregate.expectancy_usd,
            aggregate.net_pnl_usd / aggregate.trade_count,
        )
        self.assertAlmostEqual(
            aggregate.gross_profit_usd,
            sum(row.gross_profit_usd for row in rows),
        )
        self.assertAlmostEqual(
            aggregate.gross_loss_usd,
            sum(row.gross_loss_usd for row in rows),
        )
        self.assertAlmostEqual(
            aggregate.profit_factor,
            aggregate.gross_profit_usd / aggregate.gross_loss_usd,
        )
        self.assertEqual(
            aggregate.max_drawdown_fraction,
            max(row.max_drawdown_fraction for row in rows),
        )

    def test_aggregate_profit_factor_preserves_phase3_zero_loss_convention(self) -> None:
        from fmp.walkforward.gates import aggregate_windows

        rows = tuple(
            result(
                slippage=0.2,
                window=window,
                trades=1,
                net_return=0.001,
                net_pnl=100.0,
                expectancy=100.0,
                gross_profit=100.0,
                gross_loss=0.0,
                profit_factor=None,
                drawdown=0.0,
            )
            for window in STAGE2_WINDOWS
        )
        self.assertIsNone(aggregate_windows(rows).profit_factor)

    def test_stage2_requires_four_of_seven_positive_windows(self) -> None:
        from fmp.walkforward.gates import stage2_gate

        rows = stage2_mapping(
            positive_pnls=(100.0, 100.0, 100.0, -10.0, -10.0, -10.0, -10.0),
            trades_per_window=15,
        )
        self.assertFalse(stage2_gate(rows).passed)

        rows = stage2_mapping(
            positive_pnls=(100.0, 100.0, 100.0, 100.0, -10.0, -10.0, -10.0),
            trades_per_window=15,
        )
        self.assertTrue(stage2_gate(rows).passed)

    def test_stage2_positive_window_concentration_boundary_is_50_percent_inclusive(self) -> None:
        from fmp.walkforward.gates import stage2_gate

        rows = stage2_mapping(
            positive_pnls=(300.0, 100.0, 100.0, 100.0, -10.0, -10.0, -10.0),
            trades_per_window=15,
        )
        self.assertTrue(stage2_gate(rows).passed)

        rows = stage2_mapping(
            positive_pnls=(301.0, 100.0, 100.0, 100.0, -10.0, -10.0, -10.0),
            trades_per_window=15,
        )
        self.assertFalse(stage2_gate(rows).passed)

    def test_stage2_trade_count_boundary_is_99_fail_100_pass_at_point_two_only(self) -> None:
        from fmp.walkforward.gates import stage2_gate

        rows = stage2_mapping(trades_per_window=15)
        rows[0.2] = tuple(
            result(
                slippage=0.2,
                window=window,
                trades=14 if index == 0 else 15,
                net_return=row.net_return,
                net_pnl=row.net_pnl_usd,
                expectancy=row.expectancy_usd,
                gross_profit=row.gross_profit_usd,
                gross_loss=row.gross_loss_usd,
                profit_factor=row.profit_factor,
                drawdown=row.max_drawdown_fraction,
            )
            for index, (window, row) in enumerate(zip(STAGE2_WINDOWS, rows[0.2], strict=True))
        )
        self.assertEqual(sum(row.trade_count for row in rows[0.2]), 104)
        rows_99 = dict(rows)
        rows_99[0.2] = tuple(
            result(
                slippage=0.2,
                window=window,
                trades=(15 if index < 6 else 9),
                net_return=row.net_return,
                net_pnl=row.net_pnl_usd,
                expectancy=row.expectancy_usd,
                gross_profit=row.gross_profit_usd,
                gross_loss=row.gross_loss_usd,
                profit_factor=row.profit_factor,
                drawdown=row.max_drawdown_fraction,
            )
            for index, (window, row) in enumerate(zip(STAGE2_WINDOWS, rows[0.2], strict=True))
        )
        self.assertEqual(sum(row.trade_count for row in rows_99[0.2]), 99)
        self.assertFalse(stage2_gate(rows_99).passed)

        rows_100 = dict(rows_99)
        last = rows_100[0.2][-1]
        rows_100[0.2] = (*rows_100[0.2][:-1], result(
            slippage=0.2,
            window=last.window_name,
            trades=10,
            net_return=last.net_return,
            net_pnl=last.net_pnl_usd,
            expectancy=last.expectancy_usd,
            gross_profit=last.gross_profit_usd,
            gross_loss=last.gross_loss_usd,
            profit_factor=last.profit_factor,
            drawdown=last.max_drawdown_fraction,
        ))
        self.assertEqual(sum(row.trade_count for row in rows_100[0.2]), 100)
        self.assertTrue(stage2_gate(rows_100).passed)

    def test_stage2_point_five_failures_are_independent_and_one_pip_is_diagnostic_only(self) -> None:
        from fmp.walkforward.gates import stage2_gate

        rows = stage2_mapping(trades_per_window=15)
        bad_05 = list(rows[0.5])
        bad_05[0] = result(
            slippage=0.5,
            window=bad_05[0].window_name,
            trades=bad_05[0].trade_count,
            net_return=-0.02,
            net_pnl=-2_000.0,
            expectancy=-100.0,
            gross_profit=100.0,
            gross_loss=2_100.0,
            profit_factor=0.05,
            drawdown=0.06,
        )
        rows[0.5] = tuple(bad_05)
        self.assertFalse(stage2_gate(rows).passed)

        rows = stage2_mapping(trades_per_window=15)
        rows[1.0] = tuple(
            result(
                slippage=1.0,
                window=window,
                trades=0,
                net_return=-1.0,
                net_pnl=-100_000.0,
                expectancy=-1_000.0,
                gross_profit=0.0,
                gross_loss=100_000.0,
                profit_factor=0.0,
                drawdown=1.0,
            )
            for window in STAGE2_WINDOWS
        )
        self.assertTrue(stage2_gate(rows).passed)


if __name__ == "__main__":
    unittest.main()
