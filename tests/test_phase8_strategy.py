from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
import unittest
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar
from fmp.shadow.strategy import (
    FROZEN_SESSION_BREAKOUT_CONFIG,
    REQUESTED_RISK_FRACTION,
    generate_shadow_strategy_decisions,
)


LONDON = ZoneInfo("Europe/London")


def utc_label(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute), tzinfo=LONDON).astimezone(timezone.utc)


def bar(label: datetime, *, bid_close: float = 139.99, ask_close: float = 140.01) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=label,
        symbol="USDJPY",
        bid_open=139.99,
        bid_high=max(140.09, bid_close),
        bid_low=min(139.89, bid_close),
        bid_close=bid_close,
        ask_open=140.01,
        ask_high=max(140.11, ask_close),
        ask_low=min(139.91, ask_close),
        ask_close=ask_close,
    )


def live_long_context(day: date) -> tuple[QuoteBar, ...]:
    bars: list[QuoteBar] = []
    current = datetime.combine(day, time(0, 0), tzinfo=LONDON)
    end = datetime.combine(day, time(8, 0), tzinfo=LONDON)
    while current < end:
        bars.append(bar(current.astimezone(timezone.utc)))
        current += timedelta(minutes=15)
    bars.append(
        bar(
            utc_label(day, 8, 0),
            bid_close=140.20,
            ask_close=140.22,
        )
    )
    return tuple(bars)


class Phase8StrategyParityTests(unittest.TestCase):
    def test_adapter_freezes_only_promoted_session_breakout_config(self) -> None:
        self.assertEqual(FROZEN_SESSION_BREAKOUT_CONFIG.buffer_pips, 5)
        self.assertEqual(FROZEN_SESSION_BREAKOUT_CONFIG.target_range_multiple, 1.5)
        self.assertEqual(FROZEN_SESSION_BREAKOUT_CONFIG.timeframe, "15m")
        self.assertEqual(REQUESTED_RISK_FRACTION, 0.0025)

    def test_live_adapter_emits_directional_decision_without_future_exit_bar(self) -> None:
        day = date(2026, 1, 15)
        bars = live_long_context(day)
        self.assertNotIn(utc_label(day, 16), {item.timestamp_utc for item in bars})

        events = generate_shadow_strategy_decisions(bars)
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.candidate.direction, Direction.LONG)
        self.assertEqual(event.decision.direction, Direction.LONG)
        self.assertEqual(
            event.candidate.signal_known_timestamp_utc,
            event.candidate.observation_bar_timestamp_utc + timedelta(minutes=15),
        )
        self.assertEqual(
            event.decision.earliest_executable_timestamp_utc,
            event.candidate.signal_known_timestamp_utc,
        )
        self.assertEqual(event.decision.requested_risk_fraction, 0.0025)
        self.assertIsNotNone(event.scheduled_exit)
        assert event.scheduled_exit is not None
        self.assertEqual(event.scheduled_exit.timestamp_utc, utc_label(day, 16))

    def test_london_dst_keeps_signal_and_scheduled_exit_on_local_clock(self) -> None:
        day = date(2026, 7, 15)
        event = generate_shadow_strategy_decisions(live_long_context(day))[0]
        self.assertEqual(event.candidate.observation_bar_timestamp_utc, utc_label(day, 8))
        self.assertEqual(event.candidate.signal_known_timestamp_utc, utc_label(day, 8, 15))
        assert event.scheduled_exit is not None
        self.assertEqual(event.scheduled_exit.timestamp_utc, utc_label(day, 16))
        self.assertEqual(event.scheduled_exit.timestamp_utc.hour, 15)

    def test_missing_required_15m_context_never_becomes_directional_candidate(self) -> None:
        day = date(2026, 1, 15)
        bars = tuple(
            item for item in live_long_context(day) if item.timestamp_utc != utc_label(day, 3, 15)
        )
        events = generate_shadow_strategy_decisions(bars)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].candidate.direction, Direction.NO_TRADE)
        self.assertEqual(events[0].decision.direction, Direction.NO_TRADE)
        self.assertIsNone(events[0].scheduled_exit)
        self.assertEqual(events[0].candidate.reason_code, "INCOMPLETE_SESSION")

    def test_adapter_rejects_non_usdjpy_input_before_strategy_call(self) -> None:
        day = date(2026, 1, 15)
        bad = QuoteBar(
            timestamp_utc=utc_label(day, 0),
            symbol="EURUSD",
            bid_open=1.10,
            bid_high=1.11,
            bid_low=1.09,
            bid_close=1.10,
            ask_open=1.1002,
            ask_high=1.1102,
            ask_low=1.0902,
            ask_close=1.1002,
        )
        with self.assertRaises(ValueError):
            generate_shadow_strategy_decisions((bad,))

    def test_adapter_reuses_existing_generator_and_decision_bridge_without_ml_surface(self) -> None:
        source = Path("src/fmp/shadow/strategy.py").read_text(encoding="utf-8")
        self.assertIn("generate_session_breakout_candidates", source)
        self.assertIn("candidate_to_decision", source)
        self.assertIn("require_scheduled_exit_bar=False", source)
        for forbidden in ("sklearn", "fmp.phase6", "fmp.ml", "predict_proba", "model.fit"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
