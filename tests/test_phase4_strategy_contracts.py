from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from fmp.contracts import Direction
from fmp.research.adapter import candidate_to_decision
from fmp.strategies.contracts import SignalCandidate, StrategyConfig


T = datetime(2020, 1, 2, 8, 0, tzinfo=timezone.utc)


class Phase4StrategyContractTests(unittest.TestCase):
    def test_strategy_config_serialization_is_mapping_order_independent(self) -> None:
        first = StrategyConfig(
            family_id="session-breakout",
            strategy_version="v1",
            timeframe="15m",
            parameters={"buffer_pips": 2, "target_range_multiple": 1.0},
            timezone_name="Europe/London",
        )
        second = StrategyConfig(
            family_id="session-breakout",
            strategy_version="v1",
            timeframe="15m",
            parameters={"target_range_multiple": 1.0, "buffer_pips": 2},
            timezone_name="Europe/London",
        )
        self.assertEqual(first.stable_json_bytes(), second.stable_json_bytes())

    def test_signal_candidate_serialization_is_deterministic(self) -> None:
        candidate = SignalCandidate(
            candidate_id="SB-EURUSD-20200102-001",
            symbol="EURUSD",
            observation_bar_timestamp_utc=T,
            signal_known_timestamp_utc=T + timedelta(minutes=15),
            direction=Direction.LONG,
            stop_price=1.0990,
            target_price=1.1030,
            latest_exit_timestamp_utc=T + timedelta(hours=8),
            reason_code="BREAKOUT_LONG",
            metadata={"session_date": "2020-01-02", "range_width": 0.0020},
        )
        self.assertEqual(candidate.stable_json_bytes(), candidate.stable_json_bytes())
        self.assertIn(b'"candidate_id":"SB-EURUSD-20200102-001"', candidate.stable_json_bytes())

    def test_candidate_requires_utc_and_true_known_time_after_observation(self) -> None:
        with self.assertRaisesRegex(ValueError, "UTC"):
            SignalCandidate(
                candidate_id="BAD-UTC",
                symbol="EURUSD",
                observation_bar_timestamp_utc=T.replace(tzinfo=None),
                signal_known_timestamp_utc=T + timedelta(minutes=15),
                direction=Direction.LONG,
                stop_price=1.0990,
                target_price=1.1030,
                latest_exit_timestamp_utc=T + timedelta(hours=8),
                reason_code="BREAKOUT_LONG",
                metadata={},
            )
        with self.assertRaisesRegex(ValueError, "known"):
            SignalCandidate(
                candidate_id="BAD-TIME",
                symbol="EURUSD",
                observation_bar_timestamp_utc=T,
                signal_known_timestamp_utc=T,
                direction=Direction.LONG,
                stop_price=1.0990,
                target_price=1.1030,
                latest_exit_timestamp_utc=T + timedelta(hours=8),
                reason_code="BREAKOUT_LONG",
                metadata={},
            )

    def test_adapter_preserves_observation_label_but_executes_at_true_known_next_bar(self) -> None:
        candidate = SignalCandidate(
            candidate_id="LONG-1",
            symbol="EURUSD",
            observation_bar_timestamp_utc=T,
            signal_known_timestamp_utc=T + timedelta(minutes=15),
            direction=Direction.LONG,
            stop_price=1.0990,
            target_price=1.1030,
            latest_exit_timestamp_utc=T + timedelta(hours=8),
            reason_code="BREAKOUT_LONG",
            metadata={"session_date": "2020-01-02"},
        )
        decision, scheduled_exit = candidate_to_decision(
            candidate,
            next_bar_timestamp_utc=T + timedelta(minutes=15),
        )
        self.assertEqual(decision.decision_id, candidate.candidate_id)
        self.assertEqual(decision.decision_timestamp_utc, T)
        self.assertEqual(decision.earliest_executable_timestamp_utc, T + timedelta(minutes=15))
        self.assertNotEqual(decision.earliest_executable_timestamp_utc, T)
        self.assertEqual(decision.requested_risk_fraction, 0.0025)
        self.assertIsNotNone(scheduled_exit)
        assert scheduled_exit is not None
        self.assertEqual(scheduled_exit.timestamp_utc, T + timedelta(hours=8))

    def test_adapter_rejects_next_bar_that_differs_from_true_known_time(self) -> None:
        candidate = SignalCandidate(
            candidate_id="LONG-LATE",
            symbol="EURUSD",
            observation_bar_timestamp_utc=T,
            signal_known_timestamp_utc=T + timedelta(minutes=15),
            direction=Direction.LONG,
            stop_price=1.0990,
            target_price=1.1030,
            latest_exit_timestamp_utc=T + timedelta(hours=8),
            reason_code="BREAKOUT_LONG",
            metadata={},
        )
        with self.assertRaisesRegex(ValueError, "known"):
            candidate_to_decision(
                candidate,
                next_bar_timestamp_utc=T + timedelta(minutes=30),
            )

    def test_no_trade_candidate_adapts_without_execution_or_schedule(self) -> None:
        candidate = SignalCandidate(
            candidate_id="NT-1",
            symbol="EURUSD",
            observation_bar_timestamp_utc=T,
            signal_known_timestamp_utc=T + timedelta(minutes=15),
            direction=Direction.NO_TRADE,
            stop_price=None,
            target_price=None,
            latest_exit_timestamp_utc=None,
            reason_code="NO_BREAKOUT",
            metadata={"session_date": "2020-01-02"},
        )
        decision, scheduled_exit = candidate_to_decision(
            candidate,
            next_bar_timestamp_utc=T + timedelta(minutes=15),
        )
        self.assertEqual(decision.direction, Direction.NO_TRADE)
        self.assertIsNone(decision.earliest_executable_timestamp_utc)
        self.assertIsNone(scheduled_exit)
        self.assertEqual(decision.reason_code, "NO_BREAKOUT")


if __name__ == "__main__":
    unittest.main()
