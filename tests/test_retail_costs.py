from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fmp.contracts import Direction
from fmp.research.retail_costs import (
    ACCESS_DATE,
    OANDA_EXAMPLE_EURUSD_PRICE,
    OANDA_EXAMPLE_LONG_ANNUAL_RATE,
    STANDARD_LOT_UNITS,
    DoubleCountedSpreadError,
    MissingCostError,
    assemble_cost,
    commission_round_turn_usd,
    cost_for_timestamps,
    hypothetical_cost_sensitivity,
    ic_eurusd_financing_cost_usd,
    oanda_signed_financing_usd,
    phase7_documented_revaluation,
    pip_value_usd,
    pips_to_r,
    published_spreads,
    reject_spread_on_bid_ask,
    rollover_day_count,
    session_spread_pips,
    swap_points_usd,
    typical_spread_pips,
    zero_edge_is_not_rescued_by_sizing,
)
from fmp.research.trial_ledger import (
    LEDGER_PATH,
    append_trial,
    documented_backfill,
    load_trials,
)
from fmp.simulation.return_vs_ruin import documented_phase7_monthly_inputs

ET = ZoneInfo("America/New_York")


def _et(year: int, month: int, day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=ET)


class RetailCostTests(unittest.TestCase):
    def test_pip_values_match_phase3_quote_conventions(self) -> None:
        self.assertEqual(pip_value_usd("EURUSD", STANDARD_LOT_UNITS, None), 10.0)
        self.assertEqual(pip_value_usd("GBPUSD", 10_000, None), 1.0)
        self.assertAlmostEqual(pip_value_usd("USDJPY", STANDARD_LOT_UNITS, 150.0), 20.0 / 3.0)
        with self.assertRaises(MissingCostError):
            pip_value_usd("USDJPY", STANDARD_LOT_UNITS, None)

    def test_pip_cost_in_r_cancels_the_conversion_and_commission_does_not(self) -> None:
        self.assertAlmostEqual(pips_to_r(1.4, 15.0), 1.4 / 15.0)
        eurusd = commission_round_turn_usd(STANDARD_LOT_UNITS, usd_per_standard_lot_per_side=3.5)
        self.assertAlmostEqual(eurusd, 7.0)
        eurusd_r = 7.0 / (15.0 * 10.0)
        jpy_r = 7.0 / (15.0 * pip_value_usd("USDJPY", STANDARD_LOT_UNITS, 150.0))
        self.assertGreater(jpy_r, eurusd_r)
        self.assertAlmostEqual(jpy_r, 0.07)

    def test_advertised_minimum_is_not_a_typical_spread(self) -> None:
        pepperstone = published_spreads("EURUSD", account_type="Razor")
        standard = published_spreads("GBPUSD", account_type="Standard, MetaTrader")
        raw = published_spreads("EURUSD", account_type="Raw Spread, MetaTrader")
        self.assertEqual(pepperstone.advertised_minimum_pips, 0.0)
        self.assertIsNone(pepperstone.published_average_pips)
        with self.assertRaises(MissingCostError):
            typical_spread_pips(pepperstone)
        with self.assertRaises(MissingCostError):
            typical_spread_pips(standard)
        self.assertEqual(typical_spread_pips(raw), 0.1)
        self.assertEqual(raw.published_average_pips, 0.06)
        self.assertEqual(ACCESS_DATE.isoformat(), "2026-11-17")

    def test_bid_ask_fill_rejects_a_second_spread(self) -> None:
        reject_spread_on_bid_ask(0.0)
        with self.assertRaises(DoubleCountedSpreadError):
            reject_spread_on_bid_ask(0.2)
        incomplete = assemble_cost(
            symbol="EURUSD",
            units=STANDARD_LOT_UNITS,
            stop_pips=15.0,
            conversion_price=None,
            fill_basis="bid_ask",
            slippage_pips_per_side=None,
            slippage_provenance="assumption",
        )
        self.assertFalse(incomplete.complete)
        self.assertIn("slippage", incomplete.missing)
        self.assertIn("commission", incomplete.missing)
        with self.assertRaises(MissingCostError):
            incomplete.require_complete()

    def test_oanda_example_and_financing_sign(self) -> None:
        signed = oanda_signed_financing_usd(
            "EURUSD",
            100_000,
            OANDA_EXAMPLE_EURUSD_PRICE,
            OANDA_EXAMPLE_LONG_ANNUAL_RATE,
            1,
        )
        self.assertAlmostEqual(signed, -9.52, places=2)
        self.assertGreater(
            -signed,
            0.0,
        )
        long_cost = ic_eurusd_financing_cost_usd(long=True, lots=1.0, day_count=1)
        short_cost = ic_eurusd_financing_cost_usd(long=False, lots=1.0, day_count=1)
        self.assertAlmostEqual(long_cost, 8.239)
        self.assertAlmostEqual(short_cost, -1.521)
        self.assertAlmostEqual(
            ic_eurusd_financing_cost_usd(long=True, lots=1.0, day_count=3),
            24.717,
        )
        with self.assertRaises(MissingCostError):
            swap_points_usd("USDJPY")
        with self.assertRaises(MissingCostError):
            swap_points_usd("GBPUSD")

    def test_rollover_boundaries_and_wednesday_triple(self) -> None:
        wednesday = _et(2026, 11, 18, 16)
        self.assertEqual(wednesday.weekday(), 2)
        self.assertEqual(
            rollover_day_count(wednesday, _et(2026, 11, 18, 18), triple_wednesday=True),
            3,
        )
        self.assertEqual(
            rollover_day_count(wednesday, _et(2026, 11, 18, 18), triple_wednesday=False),
            1,
        )
        self.assertEqual(
            rollover_day_count(_et(2026, 11, 18, 17), _et(2026, 11, 19, 16), triple_wednesday=True),
            0,
        )
        self.assertEqual(
            rollover_day_count(_et(2026, 11, 17, 16), _et(2026, 11, 17, 17), triple_wednesday=True),
            1,
        )
        with self.assertRaises(ValueError):
            rollover_day_count(datetime(2026, 11, 17, 16), _et(2026, 11, 17, 18), triple_wednesday=True)
        with self.assertRaises(MissingCostError):
            cost_for_timestamps(
                symbol="EURUSD",
                units=STANDARD_LOT_UNITS,
                stop_pips=15.0,
                conversion_price=None,
                fill_basis="mid",
                entry_utc=_et(2026, 11, 20, 16),
                exit_utc=_et(2026, 11, 23, 10),
                slippage_pips_per_side=0.0,
                slippage_provenance="assumption",
            )
        overnight = cost_for_timestamps(
            symbol="EURUSD",
            units=STANDARD_LOT_UNITS,
            stop_pips=15.0,
            conversion_price=None,
            fill_basis="mid",
            entry_utc=_et(2026, 11, 17, 16),
            exit_utc=_et(2026, 11, 17, 18),
            slippage_pips_per_side=0.0,
            slippage_provenance="assumption",
            direction=Direction.SHORT,
        )
        financing = next(line for line in overnight.lines if line.name == "financing")
        self.assertAlmostEqual(financing.usd or 0.0, -1.521)
        self.assertLess(financing.r_multiple or 0.0, 0.0)
        self.assertTrue(overnight.complete)
        self.assertEqual(overnight.package, "IC Markets EU Raw Spread MetaTrader USD")

    def test_session_curve_and_shrinking_stress_are_rejected(self) -> None:
        with self.assertRaises(MissingCostError):
            session_spread_pips("USDJPY", "london")
        with self.assertRaises(ValueError):
            assemble_cost(
                symbol="EURUSD",
                units=STANDARD_LOT_UNITS,
                stop_pips=15.0,
                conversion_price=None,
                fill_basis="mid",
                slippage_pips_per_side=0.0,
                slippage_provenance="assumption",
                stress_multiplier=0.5,
            )

    def test_zero_edge_stays_unprofitable_at_every_fixed_fraction(self) -> None:
        for cost in (0.0, 0.08):
            for row in zero_edge_is_not_rescued_by_sizing(
                reward_to_risk=1.5,
                cost_r=cost,
                trades=60,
            ):
                self.assertLessEqual(row["net_expectancy_r"], 0.0)
                self.assertLess(row["log_growth_per_trade"], 0.0)
                if cost == 0.0:
                    self.assertAlmostEqual(row["net_expectancy_r"], 0.0)
                    self.assertAlmostEqual(row["expected_terminal_multiple"], 1.0)
                else:
                    self.assertLess(row["expected_terminal_multiple"], 1.0)

    def test_cost_changes_the_lattice_and_phase7_probabilities_stay_unavailable(self) -> None:
        rows = hypothetical_cost_sensitivity()
        by_label = {row["label"]: row for row in rows}
        plain = by_label["published_intraday_no_slippage_assumption"]
        slipped = by_label["published_plus_0.5_pip_per_side_assumption"]
        stressed = by_label["published_plus_0.5_pip_and_2x_stress_assumption"]
        self.assertGreater(slipped["cost_r"], plain["cost_r"])
        self.assertGreater(stressed["cost_r"], slipped["cost_r"])
        self.assertLess(slipped["expected_log_growth"], plain["expected_log_growth"])
        self.assertLess(stressed["expected_log_growth"], slipped["expected_log_growth"])
        self.assertLess(slipped["net_expectancy_r"], plain["net_expectancy_r"])
        self.assertFalse(plain["phase7_probability_estimate"])
        phase7 = phase7_documented_revaluation()
        self.assertFalse(phase7["reliable_probability_estimate"])
        self.assertIsNone(phase7["incremental_commission_r"])
        self.assertIsNone(phase7["incremental_financing_r"])
        documented = documented_phase7_monthly_inputs()
        self.assertAlmostEqual(
            phase7["stage2_mean_r_estimate"][1.0],
            documented["stage2_mean_r_estimate"][1.0],
        )
        self.assertLess(phase7["stage2_mean_r_estimate"][1.0], 0.0)
        self.assertGreater(phase7["stage2_mean_r_estimate"][0.5], 0.0)

    def test_ledger_is_append_only_and_does_not_launder_old_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trial-ledger.jsonl"
            first = documented_backfill()[0]
            append_trial(first, path)
            before = path.read_text(encoding="utf-8")
            append_trial(documented_backfill()[1], path)
            self.assertTrue(path.read_text(encoding="utf-8").startswith(before))
            with self.assertRaises(ValueError):
                append_trial(first, path)
            broken = dict(first)
            broken["trial_id"] = "EXP-TEST"
            del broken["hypothesis"]
            with self.assertRaises(ValueError):
                append_trial(broken, path)
            touched = dict(documented_backfill()[1])
            touched["trial_id"] = "EXP-TOUCHED"
            exposure = dict(touched["data_exposure"])
            exposure["untouched_validation"] = True
            touched["data_exposure"] = exposure
            with self.assertRaises(ValueError):
                append_trial(touched, path)
        self.assertTrue(LEDGER_PATH.exists())
        stored = load_trials(LEDGER_PATH)
        self.assertEqual([row["trial_id"] for row in stored], [row["trial_id"] for row in documented_backfill()])
        census = stored[0]["statistical_evidence"]
        self.assertIsNone(census["trial_count"])
        self.assertFalse(stored[1]["data_exposure"]["untouched_validation"])
        self.assertTrue(stored[1]["data_exposure"]["overlaps_2015_2022"])
        encoded = [json.loads(line) for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(encoded[2]["statistical_evidence"]["trade_level_r_series"], False)


if __name__ == "__main__":
    unittest.main()
