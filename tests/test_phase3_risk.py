from __future__ import annotations

import math
import unittest
from datetime import datetime, timedelta, timezone

from fmp.contracts import Decision, Direction, RejectionCode
from fmp.risk import (
    RiskConfig,
    RiskState,
    assess_decision,
    record_realized_pnl,
    release_risk,
    reserve_risk,
    roll_utc_day,
)
from fmp.risk.sizing import loss_usd_per_unit, pnl_usd, size_units


def directional_decision(
    *,
    decision_id: str = "D-001",
    symbol: str = "EURUSD",
    direction: Direction = Direction.LONG,
    requested_risk_fraction: float | None = None,
    stop_price: float = 1.0990,
    target_price: float | None = 1.1020,
    timestamp: datetime | None = None,
) -> Decision:
    timestamp = timestamp or datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
    return Decision(
        decision_id=decision_id,
        symbol=symbol,
        decision_timestamp_utc=timestamp,
        direction=direction,
        earliest_executable_timestamp_utc=timestamp + timedelta(minutes=1),
        requested_risk_fraction=requested_risk_fraction,
        stop_price=stop_price,
        target_price=target_price,
    )


class Phase3SizingTests(unittest.TestCase):
    def test_eurusd_long_pnl_is_quote_usd(self) -> None:
        self.assertAlmostEqual(
            pnl_usd(
                symbol="EURUSD",
                direction=Direction.LONG,
                units=10_000,
                entry_price=1.1000,
                exit_price=1.1010,
            ),
            10.0,
        )

    def test_gbpusd_short_pnl_is_quote_usd(self) -> None:
        self.assertAlmostEqual(
            pnl_usd(
                symbol="GBPUSD",
                direction=Direction.SHORT,
                units=20_000,
                entry_price=1.3000,
                exit_price=1.2990,
            ),
            20.0,
        )

    def test_usdjpy_pnl_converts_at_executable_exit_price(self) -> None:
        expected = (150.10 - 150.00) * 10_000 / 150.10
        self.assertAlmostEqual(
            pnl_usd(
                symbol="USDJPY",
                direction=Direction.LONG,
                units=10_000,
                entry_price=150.00,
                exit_price=150.10,
            ),
            expected,
        )

    def test_eurusd_position_sizing_is_stop_loss_based(self) -> None:
        self.assertAlmostEqual(loss_usd_per_unit("EURUSD", 1.1000, 1.0990), 0.001)
        self.assertEqual(
            size_units(
                symbol="EURUSD",
                entry_price=1.1000,
                stop_price=1.0990,
                allowed_risk_usd=25.0,
            ),
            25_000,
        )

    def test_usdjpy_position_sizing_uses_stop_price_conversion(self) -> None:
        expected_loss = abs(150.00 - 149.90) / 149.90
        expected_units = math.floor(25.0 / expected_loss)
        self.assertAlmostEqual(loss_usd_per_unit("USDJPY", 150.00, 149.90), expected_loss)
        self.assertEqual(
            size_units(
                symbol="USDJPY",
                entry_price=150.00,
                stop_price=149.90,
                allowed_risk_usd=25.0,
            ),
            expected_units,
        )

    def test_sizing_rejects_zero_stop_distance(self) -> None:
        with self.assertRaisesRegex(ValueError, "stop distance"):
            size_units(
                symbol="EURUSD",
                entry_price=1.1000,
                stop_price=1.1000,
                allowed_risk_usd=25.0,
            )

    def test_sizing_rejects_non_positive_risk(self) -> None:
        with self.assertRaisesRegex(ValueError, "allowed risk"):
            size_units(
                symbol="EURUSD",
                entry_price=1.1000,
                stop_price=1.0990,
                allowed_risk_usd=0.0,
            )

    def test_pnl_rejects_unsupported_symbol(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported symbol"):
            pnl_usd(
                symbol="AUDUSD",
                direction=Direction.LONG,
                units=10_000,
                entry_price=1.0,
                exit_price=1.1,
            )


class Phase3RiskPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = RiskConfig()
        self.state = RiskState(starting_equity_usd=10_000.0)
        self.ts = datetime(2026, 9, 14, 0, 1, tzinfo=timezone.utc)

    def test_default_quarter_percent_risk_is_approved(self) -> None:
        result = assess_decision(
            decision=directional_decision(),
            reference_entry_price=1.1000,
            timestamp_utc=self.ts,
            config=self.config,
            state=self.state,
        )
        self.assertTrue(result.approved)
        self.assertAlmostEqual(result.approved_risk_usd, 25.0)
        self.assertEqual(result.approved_units, 25_000)
        self.assertIsNone(result.rejection_code)

    def test_exact_half_percent_is_allowed_but_above_is_rejected(self) -> None:
        allowed = assess_decision(
            decision=directional_decision(requested_risk_fraction=0.005),
            reference_entry_price=1.1000,
            timestamp_utc=self.ts,
            config=self.config,
            state=self.state,
        )
        self.assertTrue(allowed.approved)
        self.assertAlmostEqual(allowed.approved_risk_usd, 50.0)

        rejected = assess_decision(
            decision=directional_decision(
                decision_id="D-002",
                requested_risk_fraction=0.005001,
            ),
            reference_entry_price=1.1000,
            timestamp_utc=self.ts,
            config=self.config,
            state=self.state,
        )
        self.assertFalse(rejected.approved)
        self.assertEqual(rejected.rejection_code, RejectionCode.PER_TRADE_RISK)

    def test_exact_one_percent_simultaneous_risk_is_allowed(self) -> None:
        reserve_risk(self.state, position_id="existing", amount_usd=75.0)
        result = assess_decision(
            decision=directional_decision(),
            reference_entry_price=1.1000,
            timestamp_utc=self.ts,
            config=self.config,
            state=self.state,
        )
        self.assertTrue(result.approved)
        self.assertAlmostEqual(result.approved_risk_usd, 25.0)

    def test_above_one_percent_simultaneous_risk_is_rejected(self) -> None:
        reserve_risk(self.state, position_id="existing", amount_usd=75.01)
        result = assess_decision(
            decision=directional_decision(),
            reference_entry_price=1.1000,
            timestamp_utc=self.ts,
            config=self.config,
            state=self.state,
        )
        self.assertFalse(result.approved)
        self.assertEqual(result.rejection_code, RejectionCode.SIMULTANEOUS_RISK)

    def test_release_returns_exact_reserved_risk(self) -> None:
        reserve_risk(self.state, position_id="P-1", amount_usd=25.0)
        self.assertEqual(release_risk(self.state, position_id="P-1"), 25.0)
        self.assertEqual(self.state.total_reserved_risk_usd, 0.0)

    def test_realized_risk_equity_changes_only_by_realized_net_pnl(self) -> None:
        record_realized_pnl(
            self.state,
            timestamp_utc=self.ts,
            pnl_usd=-100.0,
            config=self.config,
        )
        self.assertAlmostEqual(self.state.risk_equity_usd, 9_900.0)
        self.assertAlmostEqual(self.state.day_realized_pnl_usd, -100.0)

    def test_daily_halt_uses_utc_day_start_equity_basis(self) -> None:
        roll_utc_day(self.state, timestamp_utc=self.ts)
        self.assertAlmostEqual(self.state.day_start_equity_usd, 10_000.0)

        record_realized_pnl(
            self.state,
            timestamp_utc=self.ts,
            pnl_usd=-150.0,
            config=self.config,
        )
        self.assertTrue(self.state.daily_halt_active)
        self.assertEqual(self.state.halt_timestamp_utc, self.ts)

        rejected = assess_decision(
            decision=directional_decision(decision_id="D-HALT"),
            reference_entry_price=1.1000,
            timestamp_utc=self.ts + timedelta(hours=1),
            config=self.config,
            state=self.state,
        )
        self.assertFalse(rejected.approved)
        self.assertEqual(rejected.rejection_code, RejectionCode.DAILY_HALT)

    def test_next_utc_day_resets_halt_with_current_equity_basis(self) -> None:
        record_realized_pnl(
            self.state,
            timestamp_utc=self.ts,
            pnl_usd=-150.0,
            config=self.config,
        )
        self.assertTrue(self.state.daily_halt_active)

        next_day = datetime(2026, 9, 15, 0, 0, tzinfo=timezone.utc)
        roll_utc_day(self.state, timestamp_utc=next_day)
        self.assertFalse(self.state.daily_halt_active)
        self.assertIsNone(self.state.halt_timestamp_utc)
        self.assertAlmostEqual(self.state.day_start_equity_usd, 9_850.0)
        self.assertAlmostEqual(self.state.day_realized_pnl_usd, 0.0)

    def test_invalid_stop_geometry_is_rejected(self) -> None:
        result = assess_decision(
            decision=directional_decision(stop_price=1.1010),
            reference_entry_price=1.1000,
            timestamp_utc=self.ts,
            config=self.config,
            state=self.state,
        )
        self.assertFalse(result.approved)
        self.assertEqual(result.rejection_code, RejectionCode.INVALID_STOP_TARGET)

    def test_short_stop_must_be_above_entry(self) -> None:
        decision = directional_decision(
            direction=Direction.SHORT,
            stop_price=1.0990,
            target_price=1.0980,
        )
        result = assess_decision(
            decision=decision,
            reference_entry_price=1.1000,
            timestamp_utc=self.ts,
            config=self.config,
            state=self.state,
        )
        self.assertFalse(result.approved)
        self.assertEqual(result.rejection_code, RejectionCode.INVALID_STOP_TARGET)


if __name__ == "__main__":
    unittest.main()
