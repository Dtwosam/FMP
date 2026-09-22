from __future__ import annotations

from datetime import date, datetime, time, timezone
import unittest
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.opening_range_momentum import (
    OpeningRangeMomentumConfig,
    generate_opening_range_momentum_candidates,
)


LONDON = ZoneInfo("Europe/London")


def local_label(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute), tzinfo=LONDON).astimezone(
        timezone.utc
    )


def bar(
    ts: datetime,
    *,
    symbol: str = "EURUSD",
    mid_open: float,
    mid_high: float,
    mid_low: float,
    mid_close: float,
) -> QuoteBar:
    half = 0.01 if symbol == "USDJPY" else 0.0001
    return QuoteBar(
        timestamp_utc=ts,
        symbol=symbol,
        bid_open=mid_open - half,
        bid_high=mid_high - half,
        bid_low=mid_low - half,
        bid_close=mid_close - half,
        ask_open=mid_open + half,
        ask_high=mid_high + half,
        ask_low=mid_low + half,
        ask_close=mid_close + half,
    )


def one_hour_day(
    day: date,
    *,
    direction: Direction | None = Direction.LONG,
    body_close: float | None = None,
    symbol: str = "EURUSD",
    omit_hour: int | None = None,
    include_exit: bool = True,
    second_signal: bool = False,
) -> tuple[QuoteBar, ...]:
    if symbol == "USDJPY":
        center = 150.00
        reference_high = 150.10
        reference_low = 149.90
        long_close = 150.20
        short_close = 149.80
        signal_high = 150.25
        signal_low = 149.95
    else:
        center = 1.1000
        reference_high = 1.1010
        reference_low = 1.0990
        long_close = 1.1020
        short_close = 1.0980
        signal_high = 1.1030
        signal_low = 1.1000

    bars: list[QuoteBar] = []
    for hour in (6, 7):
        if hour == omit_hour:
            continue
        high = reference_high if hour == 6 else center + (
            0.0005 if symbol != "USDJPY" else 0.05
        )
        low = reference_low if hour == 7 else center - (
            0.0005 if symbol != "USDJPY" else 0.05
        )
        bars.append(
            bar(
                local_label(day, hour),
                symbol=symbol,
                mid_open=center,
                mid_high=high,
                mid_low=low,
                mid_close=center,
            )
        )

    for hour in range(8, 12):
        if hour == omit_hour:
            continue
        signal = hour == 8 or (second_signal and hour == 9)
        if signal and direction is Direction.LONG:
            close = long_close if body_close is None else body_close
            bars.append(
                bar(
                    local_label(day, hour),
                    symbol=symbol,
                    mid_open=center,
                    mid_high=max(signal_high, close),
                    mid_low=signal_low,
                    mid_close=close,
                )
            )
        elif signal and direction is Direction.SHORT:
            close = short_close if body_close is None else body_close
            bars.append(
                bar(
                    local_label(day, hour),
                    symbol=symbol,
                    mid_open=center,
                    mid_high=(center + (0.0010 if symbol != "USDJPY" else 0.10)),
                    mid_low=min(short_close - (0.0010 if symbol != "USDJPY" else 0.10), close),
                    mid_close=close,
                )
            )
        else:
            bars.append(
                bar(
                    local_label(day, hour),
                    symbol=symbol,
                    mid_open=center,
                    mid_high=center + (0.0005 if symbol != "USDJPY" else 0.05),
                    mid_low=center - (0.0005 if symbol != "USDJPY" else 0.05),
                    mid_close=center,
                )
            )

    if include_exit and omit_hour != 16:
        bars.append(
            bar(
                local_label(day, 16),
                symbol=symbol,
                mid_open=center,
                mid_high=center + (0.0005 if symbol != "USDJPY" else 0.05),
                mid_low=center - (0.0005 if symbol != "USDJPY" else 0.05),
                mid_close=center,
            )
        )
    return tuple(sorted(bars, key=lambda item: item.timestamp_utc))


class Phase8AOpeningRangeMomentumTests(unittest.TestCase):
    def test_config_accepts_only_predeclared_grid(self) -> None:
        for threshold in (0.50, 0.70):
            for target in (1.0, 1.5):
                for timeframe in ("5m", "15m", "1h"):
                    config = OpeningRangeMomentumConfig(
                        body_fraction_threshold=threshold,
                        target_r_multiple=target,
                        timeframe=timeframe,
                    )
                    self.assertEqual(config.body_fraction_threshold, threshold)
                    self.assertEqual(config.target_r_multiple, target)

        with self.assertRaises(ValueError):
            OpeningRangeMomentumConfig(0.60, 1.0, "15m")
        with self.assertRaises(ValueError):
            OpeningRangeMomentumConfig(0.50, 2.0, "15m")
        with self.assertRaises(ValueError):
            OpeningRangeMomentumConfig(0.50, 1.0, "1m")

    def test_long_signal_uses_fixed_reference_stop_and_r_target(self) -> None:
        day = date(2024, 1, 9)
        candidate = generate_opening_range_momentum_candidates(
            one_hour_day(day),
            config=OpeningRangeMomentumConfig(0.50, 1.0, "1h"),
        )[0]

        self.assertIs(candidate.direction, Direction.LONG)
        self.assertEqual(candidate.observation_bar_timestamp_utc, local_label(day, 8))
        self.assertEqual(candidate.signal_known_timestamp_utc, local_label(day, 9))
        self.assertEqual(candidate.latest_exit_timestamp_utc, local_label(day, 16))
        self.assertAlmostEqual(candidate.metadata["reference_high"], 1.1010)
        self.assertAlmostEqual(candidate.metadata["reference_low"], 1.0990)
        self.assertAlmostEqual(candidate.metadata["reference_width"], 0.0020)
        self.assertAlmostEqual(candidate.metadata["body_fraction"], 2 / 3)
        self.assertAlmostEqual(candidate.stop_price or 0.0, 1.1005)
        self.assertAlmostEqual(candidate.target_price or 0.0, 1.1035)
        self.assertEqual(candidate.reason_code, "OPENING_RANGE_MOMENTUM_LONG")

    def test_stricter_body_threshold_rejects_same_breakout(self) -> None:
        day = date(2024, 1, 9)
        candidate = generate_opening_range_momentum_candidates(
            one_hour_day(day),
            config=OpeningRangeMomentumConfig(0.70, 1.0, "1h"),
        )[0]
        self.assertIs(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "NO_QUALIFYING_MOMENTUM")

    def test_short_signal_geometry_is_symmetric(self) -> None:
        day = date(2024, 1, 10)
        candidate = generate_opening_range_momentum_candidates(
            one_hour_day(day, direction=Direction.SHORT),
            config=OpeningRangeMomentumConfig(0.50, 1.5, "1h"),
        )[0]
        self.assertIs(candidate.direction, Direction.SHORT)
        self.assertAlmostEqual(candidate.stop_price or 0.0, 1.0995)
        risk = 1.0995 - 1.0980
        self.assertAlmostEqual(candidate.target_price or 0.0, 1.0980 - 1.5 * risk)
        self.assertEqual(candidate.reason_code, "OPENING_RANGE_MOMENTUM_SHORT")

    def test_only_first_qualifying_observation_can_trade(self) -> None:
        day = date(2024, 1, 11)
        candidates = generate_opening_range_momentum_candidates(
            one_hour_day(day, second_signal=True),
            config=OpeningRangeMomentumConfig(0.50, 1.0, "1h"),
        )
        directional = [item for item in candidates if item.direction is not Direction.NO_TRADE]
        self.assertEqual(len(directional), 1)
        self.assertEqual(
            directional[0].observation_bar_timestamp_utc,
            local_label(day, 8),
        )

    def test_missing_reference_or_exit_bar_fails_closed(self) -> None:
        day = date(2024, 1, 12)
        missing_reference = generate_opening_range_momentum_candidates(
            one_hour_day(day, omit_hour=7),
            config=OpeningRangeMomentumConfig(0.50, 1.0, "1h"),
        )[0]
        self.assertIs(missing_reference.direction, Direction.NO_TRADE)
        self.assertEqual(missing_reference.reason_code, "INCOMPLETE_SESSION")

        missing_exit = generate_opening_range_momentum_candidates(
            one_hour_day(day, include_exit=False),
            config=OpeningRangeMomentumConfig(0.50, 1.0, "1h"),
        )[0]
        self.assertIs(missing_exit.direction, Direction.NO_TRADE)
        self.assertEqual(missing_exit.reason_code, "INCOMPLETE_SESSION")

    def test_missing_signal_bar_fails_closed_instead_of_skipping_gap(self) -> None:
        day = date(2024, 1, 15)
        candidate = generate_opening_range_momentum_candidates(
            one_hour_day(day, direction=None, omit_hour=9),
            config=OpeningRangeMomentumConfig(0.50, 1.0, "1h"),
        )[0]
        self.assertIs(candidate.direction, Direction.NO_TRADE)
        self.assertEqual(candidate.reason_code, "INCOMPLETE_SESSION")
        self.assertEqual(
            candidate.metadata["missing_timestamp_utc"],
            local_label(day, 9),
        )

    def test_london_dst_controls_reference_signal_and_exit_labels(self) -> None:
        day = date(2024, 7, 9)
        candidate = generate_opening_range_momentum_candidates(
            one_hour_day(day),
            config=OpeningRangeMomentumConfig(0.50, 1.0, "1h"),
        )[0]
        self.assertEqual(candidate.observation_bar_timestamp_utc.hour, 7)
        self.assertEqual(candidate.signal_known_timestamp_utc.hour, 8)
        self.assertEqual(candidate.latest_exit_timestamp_utc.hour, 15)

    def test_usdjpy_uses_two_pip_buffer_with_jpy_pip_size(self) -> None:
        day = date(2024, 1, 16)
        candidate = generate_opening_range_momentum_candidates(
            one_hour_day(day, symbol="USDJPY"),
            config=OpeningRangeMomentumConfig(0.50, 1.0, "1h"),
        )[0]
        self.assertIs(candidate.direction, Direction.LONG)
        self.assertAlmostEqual(candidate.metadata["breakout_buffer_price"], 0.02)


if __name__ == "__main__":
    unittest.main()
