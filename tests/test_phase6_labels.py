from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.contracts import SignalCandidate


UTC = timezone.utc


def bar(
    timestamp: datetime,
    *,
    bid_open: float = 150.00,
    bid_high: float = 150.40,
    bid_low: float = 149.60,
    bid_close: float = 150.10,
    spread: float = 0.02,
) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=timestamp,
        symbol="USDJPY",
        bid_open=bid_open,
        bid_high=bid_high,
        bid_low=bid_low,
        bid_close=bid_close,
        ask_open=bid_open + spread,
        ask_high=bid_high + spread,
        ask_low=bid_low + spread,
        ask_close=bid_close + spread,
    )


def candidate(
    *,
    direction: Direction,
    observation: datetime,
    width: timedelta = timedelta(minutes=15),
    stop: float | None = None,
    target: float | None = None,
    latest_exit: datetime | None = None,
    candidate_id: str = "C1",
) -> SignalCandidate:
    if stop is None:
        stop = 149.0 if direction is Direction.LONG else 151.0
    if target is None:
        target = 151.0 if direction is Direction.LONG else 149.0
    return SignalCandidate(
        candidate_id=candidate_id,
        symbol="USDJPY",
        observation_bar_timestamp_utc=observation,
        signal_known_timestamp_utc=observation + width,
        direction=direction,
        stop_price=stop,
        target_price=target,
        latest_exit_timestamp_utc=latest_exit or observation + 4 * width,
        reason_code="SETUP",
        metadata={},
    )


class Phase6LabelTests(unittest.TestCase):
    def test_long_target_before_stop_is_positive(self) -> None:
        from fmp.models.labels import label_candidate

        t0 = datetime(2020, 1, 2, 10, 0, tzinfo=UTC)
        c = candidate(direction=Direction.LONG, observation=t0)
        result = label_candidate(
            c,
            (
                bar(t0 + timedelta(minutes=15)),
                bar(t0 + timedelta(minutes=30), bid_high=151.2, bid_low=149.7),
            ),
        )
        self.assertEqual(result.label, 1)
        self.assertEqual(result.reason_code, "TARGET_BEFORE_STOP")
        self.assertEqual(result.resolved_timestamp_utc, t0 + timedelta(minutes=30))

    def test_short_target_before_stop_is_positive(self) -> None:
        from fmp.models.labels import label_candidate

        t0 = datetime(2020, 1, 2, 10, 0, tzinfo=UTC)
        c = candidate(direction=Direction.SHORT, observation=t0)
        result = label_candidate(
            c,
            (
                bar(t0 + timedelta(minutes=15)),
                bar(
                    t0 + timedelta(minutes=30),
                    bid_open=150.0,
                    bid_high=150.3,
                    bid_low=148.7,
                    bid_close=149.2,
                ),
            ),
        )
        self.assertEqual(result.label, 1)
        self.assertEqual(result.reason_code, "TARGET_BEFORE_STOP")

    def test_stop_first_and_same_bar_ambiguity_are_negative(self) -> None:
        from fmp.models.labels import label_candidate

        t0 = datetime(2020, 1, 2, 10, 0, tzinfo=UTC)
        c = candidate(direction=Direction.LONG, observation=t0)
        stopped = label_candidate(
            c,
            (
                bar(t0 + timedelta(minutes=15)),
                bar(t0 + timedelta(minutes=30), bid_high=150.4, bid_low=148.8),
            ),
        )
        self.assertEqual((stopped.label, stopped.reason_code), (0, "STOP_BEFORE_TARGET"))

        ambiguous = label_candidate(
            c,
            (
                bar(t0 + timedelta(minutes=15)),
                bar(t0 + timedelta(minutes=30), bid_high=151.2, bid_low=148.8),
            ),
        )
        self.assertEqual((ambiguous.label, ambiguous.reason_code), (0, "STOP_FIRST_AMBIGUOUS"))

    def test_scheduled_time_exit_precedes_same_bar_thresholds(self) -> None:
        from fmp.models.labels import label_candidate

        t0 = datetime(2020, 1, 2, 10, 0, tzinfo=UTC)
        exit_ts = t0 + timedelta(minutes=45)
        c = candidate(direction=Direction.LONG, observation=t0, latest_exit=exit_ts)
        result = label_candidate(
            c,
            (
                bar(t0 + timedelta(minutes=15)),
                bar(t0 + timedelta(minutes=30)),
                bar(exit_ts, bid_high=151.5, bid_low=148.5),
            ),
        )
        self.assertEqual((result.label, result.reason_code), (0, "TIME_EXIT"))
        self.assertEqual(result.resolved_timestamp_utc, exit_ts)

    def test_missing_entry_bar_is_unlabeled(self) -> None:
        from fmp.models.labels import label_candidate

        t0 = datetime(2020, 1, 2, 10, 0, tzinfo=UTC)
        c = candidate(direction=Direction.LONG, observation=t0)
        result = label_candidate(c, (bar(t0 + timedelta(minutes=30)),))
        self.assertIsNone(result.label)
        self.assertEqual(result.reason_code, "MISSING_ENTRY_BAR")
        self.assertIsNone(result.resolved_timestamp_utc)

    def test_invalid_executable_side_geometry_is_unlabeled(self) -> None:
        from fmp.models.labels import label_candidate

        t0 = datetime(2020, 1, 2, 10, 0, tzinfo=UTC)
        c = candidate(
            direction=Direction.LONG,
            observation=t0,
            stop=150.03,
            target=151.0,
        )
        result = label_candidate(c, (bar(t0 + timedelta(minutes=15)),))
        self.assertIsNone(result.label)
        self.assertEqual(result.reason_code, "INVALID_EXECUTABLE_GEOMETRY")

    def test_missing_exact_exit_and_missing_path_before_resolution_are_unlabeled(self) -> None:
        from fmp.models.labels import label_candidate

        t0 = datetime(2020, 1, 2, 10, 0, tzinfo=UTC)
        c = candidate(direction=Direction.LONG, observation=t0)
        missing_exit = label_candidate(
            c,
            (
                bar(t0 + timedelta(minutes=15)),
                bar(t0 + timedelta(minutes=30)),
                bar(t0 + timedelta(minutes=45)),
            ),
        )
        self.assertIsNone(missing_exit.label)
        self.assertEqual(missing_exit.reason_code, "MISSING_SCHEDULED_EXIT")

        gap_before_target = label_candidate(
            c,
            (
                bar(t0 + timedelta(minutes=15)),
                bar(t0 + timedelta(minutes=45), bid_high=151.2, bid_low=149.7),
                bar(t0 + timedelta(minutes=60)),
            ),
        )
        self.assertIsNone(gap_before_target.label)
        self.assertEqual(gap_before_target.reason_code, "MISSING_EXECUTABLE_PATH")

    def test_no_trade_is_unlabeled_and_batch_order_is_deterministic(self) -> None:
        from fmp.models.labels import label_candidates

        t0 = datetime(2020, 1, 2, 10, 0, tzinfo=UTC)
        directional = candidate(direction=Direction.LONG, observation=t0, candidate_id="B")
        no_trade = SignalCandidate(
            candidate_id="A",
            symbol="USDJPY",
            observation_bar_timestamp_utc=t0,
            signal_known_timestamp_utc=t0 + timedelta(minutes=15),
            direction=Direction.NO_TRADE,
            stop_price=None,
            target_price=None,
            latest_exit_timestamp_utc=None,
            reason_code="NO_SETUP",
            metadata={},
        )
        results = label_candidates(
            (directional, no_trade),
            (
                bar(t0 + timedelta(minutes=15)),
                bar(t0 + timedelta(minutes=30), bid_high=151.2, bid_low=149.7),
            ),
        )
        self.assertEqual(tuple(result.candidate_id for result in results), ("A", "B"))
        self.assertEqual((results[0].label, results[0].reason_code), (None, "NO_TRADE"))
        self.assertEqual(results[1].label, 1)

    def test_label_request_requiring_2024_bar_fails_closed(self) -> None:
        from fmp.models.labels import label_candidate

        observation = datetime(2023, 12, 31, 23, 45, tzinfo=UTC)
        c = candidate(
            direction=Direction.LONG,
            observation=observation,
            latest_exit=datetime(2024, 1, 1, 0, 30, tzinfo=UTC),
        )
        with self.assertRaisesRegex(ValueError, "final-test|2024"):
            label_candidate(c, ())


if __name__ == "__main__":
    unittest.main()
