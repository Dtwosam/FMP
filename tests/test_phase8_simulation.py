from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

from fmp.backtest.costs import apply_adverse_slippage
from fmp.contracts import Decision, Direction, ExitReason, OrderSide, ScheduledExit
from fmp.shadow.contracts import NormalizedQuote, ShadowOutcome
from fmp.shadow.simulation import ShadowSimulator


UTC = timezone.utc
BASE = datetime(2026, 1, 15, 8, 15, tzinfo=UTC)


def decision(
    decision_id: str,
    *,
    direction: Direction = Direction.LONG,
    stop: float | None = None,
    target: float | None = None,
) -> Decision:
    if direction is Direction.LONG:
        stop = 139.50 if stop is None else stop
        target = 140.50 if target is None else target
    else:
        stop = 140.50 if stop is None else stop
        target = 139.50 if target is None else target
    return Decision(
        decision_id=decision_id,
        symbol="USDJPY",
        decision_timestamp_utc=BASE - timedelta(minutes=15),
        direction=direction,
        earliest_executable_timestamp_utc=BASE,
        requested_risk_fraction=0.0025,
        stop_price=stop,
        target_price=target,
        reason_code="BREAKOUT",
    )


def scheduled_exit(decision_id: str) -> ScheduledExit:
    return ScheduledExit(
        decision_id=decision_id,
        symbol="USDJPY",
        timestamp_utc=BASE + timedelta(hours=7, minutes=45),
    )


def quote(
    when: datetime,
    *,
    bid: float = 139.99,
    ask: float = 140.01,
    tradeable: bool = True,
) -> NormalizedQuote:
    return NormalizedQuote(
        source_time_utc=when,
        received_at_utc=when + timedelta(milliseconds=20),
        receive_monotonic_ns=1,
        symbol="USDJPY",
        bid=bid,
        ask=ask,
        tradeable=tradeable,
    )


class Phase8ShadowSimulationTests(unittest.TestCase):
    def test_three_frozen_scenarios_are_independent_100k_virtual_accounts(self) -> None:
        simulator = ShadowSimulator()
        self.assertEqual(tuple(simulator.states), (0.2, 0.5, 1.0))
        states = tuple(simulator.states.values())
        self.assertEqual([state.risk_state.starting_equity_usd for state in states], [100_000.0] * 3)
        self.assertEqual([state.risk_state.risk_equity_usd for state in states], [100_000.0] * 3)
        self.assertEqual(len({id(state.risk_state) for state in states}), 3)
        self.assertEqual([state.commission_model.to_config() for state in states], [{"model": "zero_commission"}] * 3)
        self.assertEqual([state.financing_model.to_config() for state in states], [{"model": "zero_financing"}] * 3)

    def test_first_tradeable_quote_within_five_seconds_opens_each_scenario_on_executable_side(self) -> None:
        simulator = ShadowSimulator()
        item = decision("long-entry")
        simulator.register_decision(item, scheduled_exit("long-entry"))
        simulator.on_quote(quote(BASE + timedelta(seconds=2), bid=140.00, ask=140.02))

        for slippage, state in simulator.states.items():
            position = state.open_positions["long-entry"]
            self.assertEqual(position.position.entry_reference_price, 140.02)
            self.assertEqual(
                position.position.entry_price,
                apply_adverse_slippage(
                    140.02,
                    side=OrderSide.BUY,
                    pips=slippage,
                    symbol="USDJPY",
                ),
            )
            self.assertGreater(position.position.units, 0)
            self.assertGreater(state.risk_state.total_reserved_risk_usd, 0.0)

        short = decision("short-entry", direction=Direction.SHORT)
        simulator.register_decision(short, scheduled_exit("short-entry"))
        simulator.on_quote(quote(BASE + timedelta(seconds=3), bid=139.98, ask=140.00))
        for slippage, state in simulator.states.items():
            position = state.open_positions["short-entry"]
            self.assertEqual(position.position.entry_reference_price, 139.98)
            self.assertEqual(
                position.position.entry_price,
                apply_adverse_slippage(
                    139.98,
                    side=OrderSide.SELL,
                    pips=slippage,
                    symbol="USDJPY",
                ),
            )

    def test_nontradeable_quotes_do_not_fill_and_missed_entry_deadline_opens_nothing(self) -> None:
        simulator = ShadowSimulator()
        simulator.register_decision(decision("late"), scheduled_exit("late"))
        simulator.on_quote(quote(BASE + timedelta(seconds=4), tradeable=False))
        self.assertTrue(all(not state.open_positions for state in simulator.states.values()))
        simulator.on_time_advance(BASE + timedelta(seconds=6))
        for state in simulator.states.values():
            self.assertEqual(state.outcomes["late"], ShadowOutcome.ENTRY_DEADLINE_MISSED)
            self.assertNotIn("late", state.open_positions)
            self.assertEqual(state.risk_state.total_reserved_risk_usd, 0.0)

    def test_stop_gap_uses_worse_observed_executable_quote_and_target_jump_is_capped(self) -> None:
        stop_sim = ShadowSimulator()
        stop_sim.register_decision(
            decision("stop-gap", stop=139.80, target=140.50),
            scheduled_exit("stop-gap"),
        )
        stop_sim.on_quote(quote(BASE, bid=139.99, ask=140.01))
        stop_sim.on_quote(quote(BASE + timedelta(seconds=10), bid=139.70, ask=139.72))
        for slippage, state in stop_sim.states.items():
            trade = state.completed_trades[-1]
            self.assertEqual(trade.exit_reason, ExitReason.STOP)
            self.assertEqual(trade.exit_reference_price, 139.70)
            self.assertEqual(
                trade.exit_price,
                apply_adverse_slippage(
                    139.70,
                    side=OrderSide.SELL,
                    pips=slippage,
                    symbol="USDJPY",
                ),
            )

        target_sim = ShadowSimulator()
        target_sim.register_decision(
            decision("target-jump", stop=139.50, target=140.20),
            scheduled_exit("target-jump"),
        )
        target_sim.on_quote(quote(BASE, bid=139.99, ask=140.01))
        target_sim.on_quote(quote(BASE + timedelta(seconds=10), bid=140.40, ask=140.42))
        for state in target_sim.states.values():
            trade = state.completed_trades[-1]
            self.assertEqual(trade.exit_reason, ExitReason.TARGET)
            self.assertEqual(trade.exit_reference_price, 140.20)

    def test_scheduled_flat_uses_first_valid_quote_within_deadline_and_missed_deadline_is_invalid(self) -> None:
        simulator = ShadowSimulator()
        simulator.register_decision(decision("time-exit"), scheduled_exit("time-exit"))
        simulator.on_quote(quote(BASE))
        flat = scheduled_exit("time-exit").timestamp_utc
        simulator.on_quote(quote(flat + timedelta(seconds=3), bid=140.10, ask=140.12))
        for state in simulator.states.values():
            trade = state.completed_trades[-1]
            self.assertEqual(trade.exit_reason, ExitReason.TIME_EXIT)
            self.assertEqual(trade.exit_reference_price, 140.10)
            self.assertEqual(state.outcomes["time-exit"], ShadowOutcome.COMPLETED)

        missed = ShadowSimulator()
        missed.register_decision(decision("missed-flat"), scheduled_exit("missed-flat"))
        missed.on_quote(quote(BASE))
        missed.on_time_advance(scheduled_exit("missed-flat").timestamp_utc + timedelta(seconds=6))
        for state in missed.states.values():
            self.assertEqual(state.outcomes["missed-flat"], ShadowOutcome.EXIT_DEADLINE_MISSED)
            self.assertFalse(state.completed_trades)
            self.assertEqual(state.risk_state.risk_equity_usd, 100_000.0)
            self.assertEqual(state.risk_state.total_reserved_risk_usd, 0.0)

    def test_stale_gap_while_open_marks_unknown_and_excludes_financial_result(self) -> None:
        simulator = ShadowSimulator()
        simulator.register_decision(decision("gap"), scheduled_exit("gap"))
        simulator.on_quote(quote(BASE))
        simulator.mark_stale_gap(BASE + timedelta(minutes=1), BASE + timedelta(minutes=2))
        for state in simulator.states.values():
            self.assertEqual(state.outcomes["gap"], ShadowOutcome.OUTCOME_UNKNOWN_AFTER_GAP)
            self.assertFalse(state.completed_trades)
            self.assertEqual(state.risk_state.risk_equity_usd, 100_000.0)
            self.assertEqual(state.risk_state.total_reserved_risk_usd, 0.0)

    def test_completed_trade_updates_each_scenario_equity_independently_with_existing_jpy_pnl(self) -> None:
        simulator = ShadowSimulator()
        simulator.register_decision(
            decision("equity", stop=139.50, target=140.20),
            scheduled_exit("equity"),
        )
        simulator.on_quote(quote(BASE, bid=139.99, ask=140.01))
        simulator.on_quote(quote(BASE + timedelta(seconds=10), bid=140.20, ask=140.22))
        equities = []
        for state in simulator.states.values():
            self.assertEqual(state.outcomes["equity"], ShadowOutcome.COMPLETED)
            self.assertEqual(len(state.completed_trades), 1)
            self.assertEqual(state.completed_trades[0].commission_cost_usd, 0.0)
            self.assertEqual(state.completed_trades[0].financing_cost_usd, 0.0)
            equities.append(state.risk_state.risk_equity_usd)
        self.assertGreater(equities[0], equities[1])
        self.assertGreater(equities[1], equities[2])

    def test_module_reuses_phase3_cost_risk_and_sizing_primitives_and_has_no_broker_submission_surface(self) -> None:
        source = Path("src/fmp/shadow/simulation.py").read_text(encoding="utf-8")
        for required in (
            "apply_adverse_slippage",
            "RiskConfig",
            "RiskState",
            "assess_decision",
            "reserve_risk",
            "release_risk",
            "record_realized_pnl",
            "pnl_usd",
            "ZeroCommission",
            "ZeroFinancing",
        ):
            self.assertIn(required, source)
        for forbidden in ("order_send", "submit_order", "place_order", "api-fxtrade.oanda.com"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
