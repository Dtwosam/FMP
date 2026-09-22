from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import math
import unittest

from fmp.contracts import Decision, Direction, ScheduledExit
from fmp.shadow import (
    BREAKOUT_BUFFER_PIPS,
    FMP_SYMBOL,
    LIVENESS_TIMEOUT_SECONDS,
    NormalizedQuote,
    PHASE7_CHECKPOINT_SHA,
    PHASE7_CHECKPOINT_TAG,
    PHASE8_EXPERIMENT_ID,
    QUOTE_DEADLINE_SECONDS,
    SLIPPAGE_SCENARIOS,
    STARTING_EQUITY_USD,
    STRATEGY_FAMILY,
    TARGET_RANGE_MULTIPLE,
    TIMEFRAME,
    HeartbeatEvent,
    ShadowIntent,
    ShadowOutcome,
)
from fmp.shadow.contracts import (
    MT5_ALLOWED_SERVERS,
    MT5_BRIDGE_FILE,
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
)


class Phase8ContractTests(unittest.TestCase):
    def test_frozen_phase8_identity_and_threshold_constants_are_exact(self) -> None:
        self.assertEqual(PHASE8_EXPERIMENT_ID, "EXP-20260922-011")
        self.assertEqual(PHASE7_CHECKPOINT_TAG, "fmp-v1-phase7-walk-forward")
        self.assertEqual(PHASE7_CHECKPOINT_SHA, "b6fb0176555b071fef6d1070edf3407b03cd60c9")
        self.assertEqual(MT5_BRIDGE_PROTOCOL, "fmp-mt5-demo-file-bridge-v1")
        self.assertEqual(MT5_PROVIDER, "FP_MARKETS_MT5_DEMO")
        self.assertEqual(MT5_TRANSPORT, "MT5_FILE_COMMON_JSONL")
        self.assertEqual(MT5_BRIDGE_FILE, "FMP/phase8-usdjpy-feed.jsonl")
        self.assertEqual(MT5_ALLOWED_SERVERS, ("FPMarketsSC-Demo", "FPMarketsSC-Demo2"))
        self.assertEqual(FMP_SYMBOL, "USDJPY")
        self.assertEqual(STRATEGY_FAMILY, "session_breakout")
        self.assertEqual(TIMEFRAME, "15m")
        self.assertEqual(BREAKOUT_BUFFER_PIPS, 5)
        self.assertEqual(TARGET_RANGE_MULTIPLE, 1.5)
        self.assertEqual(SLIPPAGE_SCENARIOS, (0.2, 0.5, 1.0))
        self.assertEqual(STARTING_EQUITY_USD, 100_000.0)
        self.assertEqual(LIVENESS_TIMEOUT_SECONDS, 15.0)
        self.assertEqual(QUOTE_DEADLINE_SECONDS, 5.0)

    def test_normalized_quote_is_frozen_and_accepts_only_exact_phase8_quote_shape(self) -> None:
        source_time = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)
        received_at = source_time + timedelta(milliseconds=25)
        quote = NormalizedQuote(
            source_time_utc=source_time,
            received_at_utc=received_at,
            receive_monotonic_ns=123,
            symbol="USDJPY",
            bid=140.001,
            ask=140.003,
            tradeable=True,
        )
        self.assertEqual(quote.bid, 140.001)
        self.assertEqual(quote.ask, 140.003)
        with self.assertRaises(FrozenInstanceError):
            quote.bid = 140.0  # type: ignore[misc]

        invalid_kwargs = (
            {"source_time_utc": source_time.replace(tzinfo=None)},
            {"received_at_utc": received_at.replace(tzinfo=None)},
            {"source_time_utc": source_time.astimezone(timezone(timedelta(hours=1)))},
            {"symbol": "EURUSD"},
            {"bid": 0.0},
            {"bid": math.inf},
            {"ask": math.nan},
            {"bid": 140.004, "ask": 140.003},
            {"receive_monotonic_ns": -1},
            {"tradeable": 1},
        )
        base = {
            "source_time_utc": source_time,
            "received_at_utc": received_at,
            "receive_monotonic_ns": 123,
            "symbol": "USDJPY",
            "bid": 140.001,
            "ask": 140.003,
            "tradeable": True,
        }
        for override in invalid_kwargs:
            with self.subTest(override=override), self.assertRaises((TypeError, ValueError)):
                NormalizedQuote(**(base | override))

    def test_heartbeat_is_frozen_and_requires_utc_and_monotonic_timestamp(self) -> None:
        source_time = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)
        heartbeat = HeartbeatEvent(
            source_time_utc=source_time,
            received_at_utc=source_time,
            receive_monotonic_ns=0,
        )
        with self.assertRaises(FrozenInstanceError):
            heartbeat.receive_monotonic_ns = 1  # type: ignore[misc]
        with self.assertRaises(ValueError):
            HeartbeatEvent(
                source_time_utc=source_time.replace(tzinfo=None),
                received_at_utc=source_time,
                receive_monotonic_ns=0,
            )
        with self.assertRaises(ValueError):
            HeartbeatEvent(
                source_time_utc=source_time,
                received_at_utc=source_time,
                receive_monotonic_ns=-1,
            )

    def test_shadow_intent_is_immutable_data_only_and_has_no_broker_submission_surface(self) -> None:
        decision_time = datetime(2026, 9, 15, 8, 0, tzinfo=timezone.utc)
        executable_time = decision_time + timedelta(minutes=15)
        decision = Decision(
            decision_id="shadow-1",
            symbol="USDJPY",
            decision_timestamp_utc=decision_time,
            direction=Direction.LONG,
            earliest_executable_timestamp_utc=executable_time,
            requested_risk_fraction=0.0025,
            stop_price=139.5,
            target_price=141.0,
        )
        scheduled_exit = ScheduledExit(
            decision_id="shadow-1",
            symbol="USDJPY",
            timestamp_utc=datetime(2026, 9, 15, 15, 0, tzinfo=timezone.utc),
        )
        intent = ShadowIntent(
            decision=decision,
            scheduled_exit=scheduled_exit,
            units=10_000,
            reserved_risk_usd=250.0,
            slippage_pips=0.2,
        )
        with self.assertRaises(FrozenInstanceError):
            intent.units = 1  # type: ignore[misc]

        forbidden_names = (
            "send",
            "submit",
            "place",
            "order",
            "execute_broker",
            "broker",
            "broker_adapter",
        )
        for name in forbidden_names:
            self.assertFalse(hasattr(intent, name), name)
            self.assertFalse(hasattr(ShadowIntent, name), name)

        with self.assertRaises(ValueError):
            ShadowIntent(
                decision=decision,
                scheduled_exit=scheduled_exit,
                units=10_000,
                reserved_risk_usd=250.0,
                slippage_pips=0.3,
            )
        with self.assertRaises(ValueError):
            ShadowIntent(
                decision=decision,
                scheduled_exit=scheduled_exit,
                units=0,
                reserved_risk_usd=250.0,
                slippage_pips=0.2,
            )

    def test_shadow_outcome_values_are_exact_and_stable(self) -> None:
        self.assertEqual(
            tuple(item.value for item in ShadowOutcome),
            (
                "COMPLETED",
                "OUTCOME_UNKNOWN_AFTER_GAP",
                "ENTRY_DEADLINE_MISSED",
                "EXIT_DEADLINE_MISSED",
            ),
        )


if __name__ == "__main__":
    unittest.main()
