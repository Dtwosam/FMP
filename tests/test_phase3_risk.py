from __future__ import annotations

import math
import unittest
from datetime import date, datetime, timedelta, timezone

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

    def test_risk_price_and_budget_reject_boolean_and_nonnumeric_values(self):
        for value in (True, False, None, "1.1000", [], 10 ** 400):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError, "entry price"):
                    loss_usd_per_unit("EURUSD", value, 1.0990)
                with self.assertRaisesRegex(ValueError, "allowed risk"):
                    size_units(
                        symbol="EURUSD", entry_price=1.1,
                        stop_price=1.099, allowed_risk_usd=value,
                    )

    def test_risk_sizing_refuses_unhashable_and_nonstring_symbols(self):
        for symbol in ([], {}, ["EURUSD"], None, True, b"EURUSD"):
            with self.subTest(symbol=repr(symbol)):
                with self.assertRaisesRegex(ValueError, "unsupported symbol"):
                    loss_usd_per_unit(symbol, 1.1, 1.099)
                with self.assertRaisesRegex(ValueError, "unsupported symbol"):
                    pnl_usd(
                        symbol=symbol, direction=Direction.LONG,
                        units=100, entry_price=1.1, exit_price=1.101,
                    )

    def test_risk_pnl_rejects_untyped_direction_and_position_size(self):
        for direction in ("LONG", None, [], {}, True):
            with self.subTest(direction=repr(direction)):
                with self.assertRaisesRegex(ValueError, "direction"):
                    pnl_usd(
                        symbol="EURUSD", direction=direction, units=100,
                        entry_price=1.1, exit_price=1.101,
                    )
        for units in (1.0, True, False, None, "100", [], -1, 0):
            with self.subTest(units=repr(units)):
                with self.assertRaisesRegex(ValueError, "units"):
                    pnl_usd(
                        symbol="EURUSD", direction=Direction.LONG,
                        units=units, entry_price=1.1, exit_price=1.101,
                    )

    def test_position_sizing_rejects_unrealistically_huge_unit_count(self):
        with self.assertRaisesRegex(ValueError, "safety limit"):
            size_units(
                symbol="EURUSD", entry_price=1.1, stop_price=1.099,
                allowed_risk_usd=1e30,
            )

    def test_jpy_loss_per_unit_rejects_infinite_derived_conversion(self):
        with self.assertRaisesRegex(ValueError, "loss per unit must remain finite"):
            loss_usd_per_unit("USDJPY", 1e308, 1e-308)

    def test_usd_pnl_rejects_nonfinite_derived_result(self):
        for symbol in ("EURUSD", "USDJPY"):
            with self.subTest(symbol=symbol):
                with self.assertRaisesRegex(ValueError, "trade PnL must remain finite"):
                    pnl_usd(
                        symbol=symbol, direction=Direction.LONG,
                        units=10 ** 310,
                        entry_price=1e308 if symbol == "USDJPY" else 1.0,
                        exit_price=1e-308 if symbol == "USDJPY" else 1.1,
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

    def test_risk_assessment_rejects_untyped_config_without_day_mutation(self):
        for invalid in (None, True, "RiskConfig", [], {}, object()):
            with self.subTest(config_type=type(invalid).__name__):
                state = RiskState(starting_equity_usd=10_000.0)
                reserve_risk(state, position_id="held", amount_usd=15.0)
                with self.assertRaisesRegex(ValueError, "RiskConfig"):
                    assess_decision(
                        decision=directional_decision(),
                        reference_entry_price=1.1,
                        timestamp_utc=self.ts,
                        config=invalid,
                        state=state,
                    )
                self.assertIsNone(state.current_utc_date)
                self.assertEqual(state.risk_equity_usd, 10_000.0)
                self.assertEqual(state.reservations_usd, {"held": 15.0})
                self.assertFalse(state.daily_halt_active)

    def test_risk_assessment_rejects_hostile_decision_and_invalid_state(self):
        class HostileDecision:
            @property
            def direction(self):
                raise AssertionError("hostile decision getter was evaluated")

        state = RiskState(starting_equity_usd=10_000.0)
        with self.assertRaisesRegex(ValueError, "Decision"):
            assess_decision(
                decision=HostileDecision(), reference_entry_price=1.1,
                timestamp_utc=self.ts, config=self.config, state=state,
            )
        self.assertIsNone(state.current_utc_date)
        for invalid_state in (None, {}, object()):
            with self.subTest(state=type(invalid_state).__name__):
                with self.assertRaisesRegex(ValueError, "RiskState"):
                    assess_decision(
                        decision=directional_decision(),
                        reference_entry_price=1.1, timestamp_utc=self.ts,
                        config=self.config, state=invalid_state,
                    )

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

    def test_risk_state_rejects_invalid_initial_equity_without_bool_alias(self):
        for value in (True, False, None, "10000", [], 10 ** 400,
                      float("nan"), float("inf"), 0):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError, "equity"):
                    RiskState(starting_equity_usd=value)

    def test_public_risk_day_and_pnl_reject_invalid_state_records(self):
        class HostileState:
            @property
            def current_utc_date(self):
                raise AssertionError("invalid risk-state getter accessed")

        for invalid in (None, {}, [], HostileState()):
            with self.subTest(state_type=type(invalid).__name__):
                with self.assertRaisesRegex(ValueError, "RiskState"):
                    roll_utc_day(invalid, timestamp_utc=self.ts)
                with self.assertRaisesRegex(ValueError, "RiskState"):
                    record_realized_pnl(
                        invalid, timestamp_utc=self.ts,
                        pnl_usd=10.0, config=self.config,
                    )

    def test_reserve_and_release_reject_invalid_state_without_getters(self):
        class HostileState:
            @property
            def reservations_usd(self):
                raise AssertionError("invalid reservations getter accessed")

        for invalid in (None, {}, [], HostileState()):
            with self.subTest(state_type=type(invalid).__name__):
                with self.assertRaisesRegex(ValueError, "RiskState"):
                    reserve_risk(
                        invalid, position_id="SYNTHETIC", amount_usd=25.0,
                    )
                with self.assertRaisesRegex(ValueError, "RiskState"):
                    release_risk(invalid, position_id="SYNTHETIC")

    def test_real_risk_state_preserves_public_reservation_and_pnl_controls(self):
        state = RiskState(starting_equity_usd=10_000.0)
        reserve_risk(state, position_id="SYNTHETIC", amount_usd=25.0)
        self.assertEqual(release_risk(state, position_id="SYNTHETIC"), 25.0)
        record_realized_pnl(
            state, timestamp_utc=self.ts, pnl_usd=-25.0,
            config=self.config,
        )
        self.assertEqual(state.risk_equity_usd, 9_975.0)
        self.assertEqual(state.current_utc_date, self.ts.date())
        self.assertEqual(state.day_realized_pnl_usd, -25.0)
        self.assertFalse(state.daily_halt_active)

    def test_risk_reservation_rejects_invalid_amount_before_mutation(self):
        for value in (True, False, None, "25", [], float("inf"),
                      float("nan"), 10 ** 400, -1):
            with self.subTest(value=repr(value)):
                state = RiskState(starting_equity_usd=10_000.0)
                with self.assertRaisesRegex(ValueError, "risk amount"):
                    reserve_risk(state, position_id="synthetic", amount_usd=value)
                self.assertEqual(state.reservations_usd, {})

    def test_huge_risk_amount_classifies_invalid_amount_not_aggregate(self):
        state = RiskState(starting_equity_usd=10_000.0)
        with self.assertRaisesRegex(ValueError, "risk amount"):
            reserve_risk(state, position_id="huge", amount_usd=10 ** 400)
        self.assertEqual(state.reservations_usd, {})
        self.assertEqual(state.total_reserved_risk_usd, 0.0)

    def test_real_aggregate_overflow_remains_atomic_and_distinct(self):
        state = RiskState(starting_equity_usd=1e308)
        reserve_risk(state, position_id="first", amount_usd=1e308)
        with self.assertRaisesRegex(ValueError, "aggregate"):
            reserve_risk(state, position_id="second", amount_usd=1e308)
        self.assertEqual(state.reservations_usd, {"first": 1e308})

    def test_risk_reservation_rejects_invalid_identifier_before_mutation(self):
        for bad in (None, [], {}, 17, True, "", " ",
                    "bad" + chr(10), "bad" + chr(27)):
            with self.subTest(position_id=repr(bad)):
                state = RiskState(starting_equity_usd=10_000.0)
                with self.assertRaisesRegex(ValueError, "position_id"):
                    reserve_risk(state, position_id=bad, amount_usd=25.0)
                with self.assertRaisesRegex(ValueError, "position_id"):
                    release_risk(state, position_id=bad)
                self.assertEqual(state.reservations_usd, {})

    def test_risk_reservation_rejects_aggregate_overflow_atomically(self):
        state = RiskState(starting_equity_usd=1e308)
        reserve_risk(state, position_id="first", amount_usd=1e308)
        with self.assertRaisesRegex(ValueError, "aggregate"):
            reserve_risk(state, position_id="second", amount_usd=1e308)
        self.assertEqual(state.reservations_usd, {"first": 1e308})
        self.assertEqual(release_risk(state, position_id="first"), 1e308)
        self.assertEqual(state.reservations_usd, {})

    def test_corrupted_reservations_refuse_risk_approval_before_day_roll(self):
        for amount in (float("nan"), float("inf"), -25.0, 0.0,
                       True, "25", 10 ** 400):
            with self.subTest(value=repr(amount)):
                state = RiskState(starting_equity_usd=10_000.0)
                state.reservations_usd["existing"] = amount
                with self.assertRaisesRegex(ValueError, "reserved risk state"):
                    assess_decision(
                        decision=directional_decision(),
                        reference_entry_price=1.1, timestamp_utc=self.ts,
                        config=self.config, state=state,
                    )
                self.assertIsNone(state.current_utc_date)
                self.assertEqual(state.risk_equity_usd, 10_000.0)
                with self.assertRaisesRegex(ValueError, "reserved risk state"):
                    reserve_risk(
                        state, position_id="another", amount_usd=25.0,
                    )
                self.assertNotIn("another", state.reservations_usd)

    def test_reservation_map_identity_type_and_aggregate_are_validated(self):
        bad = (
            {"bad\nkey": 25.0},
            {7: 25.0},
            {"valid": None},
            {"one": 1e308, "two": 1e308},
            [],
        )
        for reservations in bad:
            with self.subTest(reservations=repr(reservations)):
                state = RiskState(starting_equity_usd=10_000.0)
                state.reservations_usd = reservations
                with self.assertRaisesRegex(ValueError, "reserved risk state"):
                    _ = state.total_reserved_risk_usd

    def test_normal_reservation_sum_preserves_add_and_release(self):
        state = RiskState(starting_equity_usd=10_000.0)
        reserve_risk(state, position_id="A", amount_usd=25.0)
        reserve_risk(state, position_id="B", amount_usd=50.0)
        self.assertEqual(state.total_reserved_risk_usd, 75.0)
        self.assertEqual(release_risk(state, position_id="A"), 25.0)
        self.assertEqual(state.total_reserved_risk_usd, 50.0)

    def test_release_returns_exact_reserved_risk(self) -> None:
        reserve_risk(self.state, position_id="P-1", amount_usd=25.0)
        self.assertEqual(release_risk(self.state, position_id="P-1"), 25.0)
        self.assertEqual(self.state.total_reserved_risk_usd, 0.0)

    def test_realized_pnl_rejects_untyped_config_without_state_mutation(self):
        for invalid in (None, True, 0, "RiskConfig", {}, [], object()):
            with self.subTest(config_type=type(invalid).__name__):
                state = RiskState(starting_equity_usd=10_000.0)
                reserve_risk(state, position_id="existing", amount_usd=25.0)
                with self.assertRaisesRegex(ValueError, "RiskConfig"):
                    record_realized_pnl(
                        state, timestamp_utc=self.ts, pnl_usd=-20.0,
                        config=invalid,
                    )
                self.assertEqual(state.risk_equity_usd, 10_000.0)
                self.assertIsNone(state.current_utc_date)
                self.assertEqual(state.day_realized_pnl_usd, 0.0)
                self.assertEqual(state.reservations_usd, {"existing": 25.0})
                self.assertFalse(state.daily_halt_active)

    def test_realized_pnl_does_not_read_hostile_config_getters(self):
        class HostileConfig:
            @property
            def daily_loss_halt_fraction(self):
                raise AssertionError("unexpected config property access")

        state = RiskState(starting_equity_usd=10_000.0)
        with self.assertRaisesRegex(ValueError, "RiskConfig"):
            record_realized_pnl(
                state, timestamp_utc=self.ts, pnl_usd=25.0,
                config=HostileConfig(),
            )
        self.assertEqual(state.risk_equity_usd, 10_000.0)
        self.assertIsNone(state.current_utc_date)

    def test_realized_equity_overflow_fails_before_mutating_risk_state(self):
        state = RiskState(starting_equity_usd=1e308)
        self.assertIsNone(state.current_utc_date)
        with self.assertRaisesRegex(ValueError, "must remain finite"):
            record_realized_pnl(
                state, timestamp_utc=self.ts, pnl_usd=1e308,
                config=self.config,
            )
        self.assertEqual(state.risk_equity_usd, 1e308)
        self.assertIsNone(state.current_utc_date)
        self.assertEqual(state.day_realized_pnl_usd, 0.0)
        self.assertFalse(state.daily_halt_active)

    def test_invalid_realized_pnl_types_fail_without_utc_day_change(self):
        for pnl in (True, False, None, "1.0", float("nan"),
                    float("inf"), 10 ** 400):
            with self.subTest(pnl=repr(pnl)):
                state = RiskState(starting_equity_usd=10_000.0)
                with self.assertRaisesRegex(ValueError, "realized PnL|remain finite"):
                    record_realized_pnl(
                        state, timestamp_utc=self.ts, pnl_usd=pnl,
                        config=self.config,
                    )
                self.assertIsNone(state.current_utc_date)
                self.assertEqual(state.risk_equity_usd, 10_000.0)

    def test_finite_realized_gain_and_loss_preserve_same_day_accounting(self):
        state = RiskState(starting_equity_usd=10_000.0)
        record_realized_pnl(
            state, timestamp_utc=self.ts, pnl_usd=25.0,
            config=self.config,
        )
        record_realized_pnl(
            state, timestamp_utc=self.ts + timedelta(minutes=1),
            pnl_usd=-15.0, config=self.config,
        )
        self.assertAlmostEqual(state.risk_equity_usd, 10_010.0)
        self.assertAlmostEqual(state.day_realized_pnl_usd, 10.0)
        self.assertEqual(state.current_utc_date, self.ts.date())
        self.assertFalse(state.daily_halt_active)

    def test_risk_utc_rolling_rejects_non_datetime_without_state_changes(self):
        for bad in (None, "2026-09-14T00:00Z", 123, {}, date(2026, 9, 14)):
            with self.subTest(value=repr(bad)):
                state = RiskState(starting_equity_usd=10_000.0)
                with self.assertRaisesRegex(ValueError, "UTC"):
                    roll_utc_day(state, timestamp_utc=bad)
                self.assertIsNone(state.current_utc_date)
                self.assertEqual(state.risk_equity_usd, 10_000.0)

    def test_risk_record_rejects_invalid_time_before_pnl_update(self):
        for bad in (None, [], "2026-09-14", 1):
            with self.subTest(value=repr(bad)):
                state = RiskState(starting_equity_usd=10_000.0)
                with self.assertRaisesRegex(ValueError, "UTC"):
                    record_realized_pnl(
                        state, timestamp_utc=bad, pnl_usd=10.0,
                        config=self.config,
                    )
                self.assertEqual(state.risk_equity_usd, 10_000.0)
                self.assertIsNone(state.current_utc_date)

    def test_risk_day_rejects_backward_roll_without_resetting_halt(self):
        state = RiskState(starting_equity_usd=10_000.0)
        record_realized_pnl(
            state, timestamp_utc=self.ts, pnl_usd=-200.0,
            config=self.config,
        )
        self.assertTrue(state.daily_halt_active)
        saved = (
            state.current_utc_date, state.day_start_equity_usd,
            state.day_realized_pnl_usd, state.halt_timestamp_utc,
            state.risk_equity_usd,
        )
        with self.assertRaisesRegex(ValueError, "backward"):
            roll_utc_day(
                state, timestamp_utc=self.ts - timedelta(days=1),
            )
        self.assertTrue(state.daily_halt_active)
        self.assertEqual(saved, (
            state.current_utc_date, state.day_start_equity_usd,
            state.day_realized_pnl_usd, state.halt_timestamp_utc,
            state.risk_equity_usd,
        ))

    def test_realized_pnl_rejects_backdated_mutation_atomically(self):
        state = RiskState(starting_equity_usd=10_000.0)
        next_day = self.ts + timedelta(days=1)
        record_realized_pnl(
            state, timestamp_utc=next_day, pnl_usd=25.0,
            config=self.config,
        )
        with self.assertRaisesRegex(ValueError, "backward"):
            record_realized_pnl(
                state, timestamp_utc=self.ts, pnl_usd=75.0,
                config=self.config,
            )
        self.assertEqual(state.risk_equity_usd, 10_025.0)
        self.assertEqual(state.day_realized_pnl_usd, 25.0)
        self.assertEqual(state.current_utc_date, next_day.date())

    def test_risk_assessment_refuses_backdated_day_without_mutation(self):
        state = RiskState(starting_equity_usd=10_000.0)
        next_day = self.ts + timedelta(days=1)
        roll_utc_day(state, timestamp_utc=next_day)
        reserve_risk(state, position_id="held", amount_usd=25.0)
        with self.assertRaisesRegex(ValueError, "backward"):
            assess_decision(
                decision=directional_decision(),
                reference_entry_price=1.1,
                timestamp_utc=self.ts, config=self.config, state=state,
            )
        self.assertEqual(state.current_utc_date, next_day.date())
        self.assertEqual(state.reservations_usd, {"held": 25.0})
        self.assertEqual(state.day_realized_pnl_usd, 0.0)

    def test_risk_utc_rolling_still_accepts_real_utc_dates(self):
        state = RiskState(starting_equity_usd=10_000.0)
        roll_utc_day(state, timestamp_utc=self.ts)
        self.assertEqual(state.current_utc_date, self.ts.date())
        self.assertEqual(state.day_start_equity_usd, 10_000.0)

    def test_risk_fraction_config_rejects_boolean_and_non_numeric_values(self):
        fields = (
            "default_risk_fraction",
            "max_risk_fraction",
            "max_simultaneous_risk_fraction",
            "daily_loss_halt_fraction",
        )
        for field in fields:
            for value in (True, False, None, "0.01", [], {}):
                with self.subTest(field=field, value=repr(value)):
                    kwargs = {field: value}
                    with self.assertRaisesRegex(ValueError, field):
                        RiskConfig(**kwargs)

    def test_risk_fraction_config_rejects_nonfinite_or_overflowed_numeric(self):
        for field in (
            "default_risk_fraction", "max_risk_fraction",
            "max_simultaneous_risk_fraction", "daily_loss_halt_fraction",
        ):
            for value in (float("nan"), float("inf"), -float("inf"), 10 ** 400):
                with self.subTest(field=field, value=repr(value)):
                    with self.assertRaisesRegex(ValueError, field):
                        RiskConfig(**{field: value})

    def test_risk_fraction_config_rejects_any_value_over_one(self):
        for field in (
            "default_risk_fraction",
            "max_risk_fraction",
            "max_simultaneous_risk_fraction",
            "daily_loss_halt_fraction",
        ):
            for value in (1.000001, 2, 100.0):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, field):
                        RiskConfig(**{field: value})

    def test_risk_fraction_config_accepts_consistent_one_bounds(self):
        cfg = RiskConfig(
            default_risk_fraction=1.0,
            max_risk_fraction=1.0,
            max_simultaneous_risk_fraction=1.0,
            daily_loss_halt_fraction=1.0,
        )
        self.assertEqual(cfg.max_risk_fraction, 1.0)
        self.assertEqual(cfg.daily_loss_halt_fraction, 1.0)
        self.assertEqual(RiskConfig().default_risk_fraction, 0.0025)

    def test_risk_fraction_defaults_remain_positive_and_ordered(self):
        cfg = RiskConfig()
        self.assertGreater(cfg.default_risk_fraction, 0)
        self.assertLessEqual(cfg.default_risk_fraction, cfg.max_risk_fraction)
        self.assertLessEqual(
            cfg.max_risk_fraction, cfg.max_simultaneous_risk_fraction,
        )
        self.assertGreater(cfg.daily_loss_halt_fraction, 0)

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

    def test_risk_assessment_rejects_malformed_reference_without_state_change(self):
        for value in (True, False, None, [], {}, "1.1000", 0,
                      -1.0, float("nan"), float("inf"), 10 ** 400):
            with self.subTest(value=repr(value)):
                state = RiskState(starting_equity_usd=10_000.0)
                assessed = assess_decision(
                    decision=directional_decision(),
                    reference_entry_price=value,
                    timestamp_utc=self.ts,
                    config=self.config, state=state,
                )
                self.assertFalse(assessed.approved)
                self.assertEqual(assessed.rejection_code, RejectionCode.INVALID_SIZE)
                self.assertIsNone(state.current_utc_date)
                self.assertEqual(state.risk_equity_usd, 10_000.0)
                self.assertEqual(state.reservations_usd, {})

    def test_risk_assessment_still_rolls_valid_reference_and_approves(self):
        state = RiskState(starting_equity_usd=10_000.0)
        assessed = assess_decision(
            decision=directional_decision(),
            reference_entry_price=1.1000, timestamp_utc=self.ts,
            config=self.config, state=state,
        )
        self.assertTrue(assessed.approved)
        self.assertEqual(state.current_utc_date, self.ts.date())
        self.assertEqual(state.risk_equity_usd, 10_000.0)

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
