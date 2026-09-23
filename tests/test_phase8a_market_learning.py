from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from fmp.contracts import Direction, QuoteBar
from fmp.market_learning.contracts import (
    EVIDENCE_LABEL,
    HORIZONS_MINUTES,
    SLIPPAGE_PIPS,
    MarketObservation,
)
from fmp.market_learning.labels import label_market_outcome, label_market_outcomes


UTC = timezone.utc


def bar(
    timestamp: datetime,
    *,
    symbol: str = "EURUSD",
    bid_open: float = 1.1000,
    spread: float = 0.0002,
) -> QuoteBar:
    ask_open = bid_open + spread
    return QuoteBar(
        timestamp_utc=timestamp,
        symbol=symbol,
        bid_open=bid_open,
        bid_high=bid_open + 0.0010,
        bid_low=bid_open - 0.0010,
        bid_close=bid_open,
        ask_open=ask_open,
        ask_high=ask_open + 0.0010,
        ask_low=ask_open - 0.0010,
        ask_close=ask_open,
    )


def observation(
    *,
    symbol: str = "EURUSD",
    timeframe: str = "5m",
    start: datetime | None = None,
) -> MarketObservation:
    start = start or datetime(2020, 1, 2, 10, 0, tzinfo=UTC)
    width = {"5m": 5, "15m": 15, "1h": 60}[timeframe]
    return MarketObservation(
        symbol=symbol,
        timeframe=timeframe,
        bar_start_utc=start,
        available_at_utc=start + timedelta(minutes=width),
    )


class MarketLearningContractTests(unittest.TestCase):
    def test_observation_identity_is_stable_and_timing_is_exact(self) -> None:
        first = observation()
        second = observation()
        self.assertEqual(first.fingerprint, second.fingerprint)
        with self.assertRaisesRegex(ValueError, "exact timeframe"):
            MarketObservation(
                symbol="EURUSD",
                timeframe="5m",
                bar_start_utc=first.bar_start_utc,
                available_at_utc=first.bar_start_utc + timedelta(minutes=15),
            )


class MarketLearningLabelTests(unittest.TestCase):
    def test_long_market_outcome_uses_bid_ask_and_two_sided_slippage(self) -> None:
        obs = observation()
        entry = obs.available_at_utc
        exit_ = entry + timedelta(minutes=60)
        result = label_market_outcome(
            obs,
            (
                bar(entry, bid_open=1.1000),
                bar(exit_, bid_open=1.1015),
            ),
            horizon_minutes=60,
            slippage_pips=0.2,
        )

        self.assertEqual(result.reason_code, "LABELED")
        assert result.label is not None
        self.assertEqual(result.label.best_direction, Direction.LONG)
        self.assertEqual(result.label.evidence_label, EVIDENCE_LABEL)
        self.assertAlmostEqual(result.label.future_mid_move_pips, 15.0)
        self.assertAlmostEqual(result.label.long_net_pips, 12.6)
        self.assertAlmostEqual(result.label.short_net_pips, -17.4)

    def test_short_outcome_respects_usdjpy_pip_size(self) -> None:
        obs = observation(symbol="USDJPY", timeframe="15m")
        entry = obs.available_at_utc
        exit_ = entry + timedelta(minutes=240)
        result = label_market_outcome(
            obs,
            (
                bar(entry, symbol="USDJPY", bid_open=150.00, spread=0.02),
                bar(exit_, symbol="USDJPY", bid_open=149.50, spread=0.02),
            ),
            horizon_minutes=240,
            slippage_pips=0.5,
        )

        assert result.label is not None
        self.assertEqual(result.label.best_direction, Direction.SHORT)
        self.assertAlmostEqual(result.label.future_mid_move_pips, -50.0)
        self.assertAlmostEqual(result.label.short_net_pips, 47.0)
        self.assertAlmostEqual(result.label.long_net_pips, -53.0)

    def test_flat_move_is_no_trade_after_spread_and_slippage(self) -> None:
        obs = observation()
        entry = obs.available_at_utc
        exit_ = entry + timedelta(minutes=60)
        result = label_market_outcome(
            obs,
            (
                bar(entry, bid_open=1.1000),
                bar(exit_, bid_open=1.1000),
            ),
            horizon_minutes=60,
            slippage_pips=0.2,
        )

        assert result.label is not None
        self.assertEqual(result.label.best_direction, Direction.NO_TRADE)
        self.assertLess(result.label.long_net_pips, 0)
        self.assertLess(result.label.short_net_pips, 0)

    def test_missing_exact_horizon_is_unavailable_not_shifted(self) -> None:
        obs = observation()
        entry = obs.available_at_utc
        result = label_market_outcome(
            obs,
            (
                bar(entry),
                bar(entry + timedelta(minutes=65), bid_open=1.1010),
            ),
            horizon_minutes=60,
            slippage_pips=0.2,
        )

        self.assertIsNone(result.label)
        self.assertEqual(result.reason_code, "MISSING_EXACT_HORIZON_BAR")

    def test_duplicate_bar_identity_fails_closed(self) -> None:
        obs = observation()
        entry = obs.available_at_utc
        duplicate = bar(entry)
        with self.assertRaisesRegex(ValueError, "duplicate quote-bar"):
            label_market_outcome(
                obs,
                (duplicate, duplicate),
                horizon_minutes=60,
                slippage_pips=0.2,
            )

    def test_only_frozen_horizons_and_costs_are_allowed(self) -> None:
        obs = observation()
        self.assertEqual(HORIZONS_MINUTES, (60, 240))
        self.assertEqual(SLIPPAGE_PIPS, (0.2, 0.5, 1.0))
        with self.assertRaisesRegex(ValueError, "horizon"):
            label_market_outcome(
                obs,
                (),
                horizon_minutes=30,
                slippage_pips=0.2,
            )
        with self.assertRaisesRegex(ValueError, "slippage"):
            label_market_outcome(
                obs,
                (),
                horizon_minutes=60,
                slippage_pips=0.3,
            )

    def test_batch_output_is_deterministic_and_complete(self) -> None:
        first = observation(symbol="EURUSD")
        second = observation(
            symbol="GBPUSD",
            start=datetime(2020, 1, 2, 9, 0, tzinfo=UTC),
        )
        bars = []
        for obs in (first, second):
            bars.extend(
                (
                    bar(
                        obs.available_at_utc,
                        symbol=obs.symbol,
                        bid_open=1.2000 if obs.symbol == "GBPUSD" else 1.1000,
                    ),
                    bar(
                        obs.available_at_utc + timedelta(minutes=60),
                        symbol=obs.symbol,
                        bid_open=1.2010 if obs.symbol == "GBPUSD" else 1.1010,
                    ),
                    bar(
                        obs.available_at_utc + timedelta(minutes=240),
                        symbol=obs.symbol,
                        bid_open=1.2020 if obs.symbol == "GBPUSD" else 1.1020,
                    ),
                )
            )
        bars = tuple(sorted(bars, key=lambda item: (item.timestamp_utc, item.symbol)))

        forward = label_market_outcomes((first, second), bars)
        reverse = label_market_outcomes((second, first), bars)
        self.assertEqual(forward, reverse)
        self.assertEqual(len(forward), 2 * len(HORIZONS_MINUTES) * len(SLIPPAGE_PIPS))

    def test_duplicate_observation_identity_fails_closed(self) -> None:
        obs = observation()
        with self.assertRaisesRegex(ValueError, "duplicate market-learning observation"):
            label_market_outcomes((obs, obs), ())


if __name__ == "__main__":
    unittest.main()
