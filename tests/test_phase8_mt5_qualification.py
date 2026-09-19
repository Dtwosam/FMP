from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

from fmp.shadow.mt5_bridge import (
    BridgeHeartbeatRecord,
    BridgeStartRecord,
    BridgeTickRecord,
)
from fmp.shadow.qualification import (
    QualificationOutcome,
    mt5_boundary_audit,
    qualify_bridge,
)


UTC = timezone.utc
START = datetime(2026, 9, 17, 20, 0, tzinfo=UTC)
SESSION = "a" * 64
FINGERPRINT = "b" * 64
SERVER = "FPMarketsSC-Demo2"
BASE_MSC = int(START.timestamp() * 1000)
TICK_STEP_MSC = 50


def start_record() -> BridgeStartRecord:
    return BridgeStartRecord(
        protocol="fmp-mt5-demo-file-bridge-v1",
        bridge_session_id=SESSION,
        symbol="USDJPY",
        server=SERVER,
        account_fingerprint=FINGERPRINT,
        account_mode="DEMO",
        bridge_start_time_msc=BASE_MSC - 1_000,
    )


def tick_record(index: int, *, ask_delta: float = 0.002) -> BridgeTickRecord:
    bid = 147.100 + (index * 0.001)
    return BridgeTickRecord(
        protocol="fmp-mt5-demo-file-bridge-v1",
        bridge_session_id=SESSION,
        symbol="USDJPY",
        server=SERVER,
        account_fingerprint=FINGERPRINT,
        source_time_msc=BASE_MSC + index * TICK_STEP_MSC,
        bid=bid,
        ask=bid + ask_delta,
        flags=6,
    )


def heartbeat_record(index: int, *, last_tick_time_msc: int | None = None) -> BridgeHeartbeatRecord:
    return BridgeHeartbeatRecord(
        protocol="fmp-mt5-demo-file-bridge-v1",
        bridge_session_id=SESSION,
        symbol="USDJPY",
        server=SERVER,
        account_fingerprint=FINGERPRINT,
        bridge_emitted_time_msc=BASE_MSC + 5_000 + index,
        last_tick_time_msc=last_tick_time_msc,
    )


class FakeClock:
    def __init__(self) -> None:
        self.elapsed = 0.0

    def advance(self, seconds: float) -> None:
        self.elapsed += seconds

    def utc_now(self) -> datetime:
        return START + timedelta(seconds=self.elapsed)

    def monotonic_ns(self) -> int:
        return int(self.elapsed * 1_000_000_000)


class ScriptedTail:
    def __init__(
        self,
        clock: FakeClock,
        script: list[tuple[float, tuple[object, ...] | Exception]],
    ) -> None:
        self.clock = clock
        self.start_record = start_record()
        self.script = list(script)
        self.read_count = 0

    def read_available(self):  # type: ignore[no-untyped-def]
        self.read_count += 1
        if not self.script:
            self.clock.advance(600.0)
            return ()
        delay, value = self.script.pop(0)
        self.clock.advance(delay)
        if isinstance(value, Exception):
            raise value
        return value


class Phase8Mt5QualificationTests(unittest.TestCase):
    def test_boundary_audit_is_exact_fixed_read_only_mt5_surface(self) -> None:
        self.assertEqual(
            mt5_boundary_audit(),
            {
                "connector_protocol": "fmp-mt5-demo-file-bridge-v1",
                "provider": "FP_MARKETS_MT5_DEMO",
                "transport": "MT5_FILE_COMMON_JSONL",
                "bridge_file": "FMP/phase8-usdjpy-feed.jsonl",
                "instrument": "USDJPY",
                "allowed_servers": ["FPMarketsSC-Demo", "FPMarketsSC-Demo2"],
            },
        )

    def test_pass_requires_100_distinct_ticks_and_6_heartbeats_after_reader_start(self) -> None:
        clock = FakeClock()
        script: list[tuple[float, tuple[object, ...] | Exception]] = []
        heartbeat_indexes = {10, 20, 30, 40, 50, 60}
        for index in range(100):
            script.append((0.05, (tick_record(index),)))
            if index in heartbeat_indexes:
                script.append(
                    (
                        0.05,
                        (
                            heartbeat_record(
                                index,
                                last_tick_time_msc=BASE_MSC + index * TICK_STEP_MSC,
                            ),
                        ),
                    )
                )
        script.append((0.05, (tick_record(100),)))
        tail = ScriptedTail(clock, script)

        result = qualify_bridge(
            tail,
            utc_now=clock.utc_now,
            monotonic_ns=clock.monotonic_ns,
        )

        self.assertEqual(result.outcome, QualificationOutcome.PASS)
        self.assertEqual(result.price_count, 100)
        self.assertEqual(result.heartbeat_count, 6)
        self.assertEqual(result.bridge_session_id, SESSION)
        self.assertEqual(result.server, SERVER)
        self.assertEqual(result.account_fingerprint, FINGERPRINT)
        self.assertLess(tail.read_count, 107)
        self.assertLessEqual(result.elapsed_seconds, 600.0)
        self.assertLessEqual(result.max_bridge_liveness_gap_seconds, 15.0)
        self.assertLessEqual(result.max_market_liveness_gap_seconds, 15.0)
        self.assertEqual(result.boundary_audit, mt5_boundary_audit())

    def test_exact_duplicate_tick_does_not_count_twice(self) -> None:
        clock = FakeClock()
        duplicate = tick_record(1)
        tail = ScriptedTail(
            clock,
            [
                (0.1, (duplicate,)),
                (0.1, (duplicate,)),
                (5.0, (heartbeat_record(1, last_tick_time_msc=BASE_MSC + TICK_STEP_MSC),)),
                (5.0, (heartbeat_record(2, last_tick_time_msc=BASE_MSC + 1),)),
                (5.0, (heartbeat_record(3, last_tick_time_msc=BASE_MSC + 1),)),
                (0.001, (heartbeat_record(4, last_tick_time_msc=BASE_MSC + 1),)),
            ],
        )
        result = qualify_bridge(tail, utc_now=clock.utc_now, monotonic_ns=clock.monotonic_ns)
        self.assertEqual(result.outcome, QualificationOutcome.INCONCLUSIVE)
        self.assertEqual(result.price_count, 1)
        self.assertEqual(result.rejection_codes, ("MARKET_LIVENESS_GAP",))

    def test_no_post_start_bridge_activity_is_connector_unavailable(self) -> None:
        clock = FakeClock()
        tail = ScriptedTail(clock, [(15.001, ())])
        result = qualify_bridge(tail, utc_now=clock.utc_now, monotonic_ns=clock.monotonic_ns)
        self.assertEqual(result.outcome, QualificationOutcome.CONNECTOR_UNAVAILABLE)
        self.assertEqual(result.rejection_codes, ("BRIDGE_INACTIVE",))

    def test_bridge_gap_after_activity_is_connector_rejected(self) -> None:
        clock = FakeClock()
        tail = ScriptedTail(
            clock,
            [
                (0.1, (tick_record(1),)),
                (15.001, ()),
            ],
        )
        result = qualify_bridge(tail, utc_now=clock.utc_now, monotonic_ns=clock.monotonic_ns)
        self.assertEqual(result.outcome, QualificationOutcome.CONNECTOR_REJECTED)
        self.assertEqual(result.rejection_codes, ("BRIDGE_LIVENESS_GAP",))

    def test_market_gap_with_continuing_heartbeats_is_inconclusive(self) -> None:
        clock = FakeClock()
        tail = ScriptedTail(
            clock,
            [
                (5.0, (heartbeat_record(1),)),
                (5.0, (heartbeat_record(2),)),
                (5.0, (heartbeat_record(3),)),
                (0.001, (heartbeat_record(4),)),
            ],
        )
        result = qualify_bridge(tail, utc_now=clock.utc_now, monotonic_ns=clock.monotonic_ns)
        self.assertEqual(result.outcome, QualificationOutcome.INCONCLUSIVE)
        self.assertEqual(result.rejection_codes, ("MARKET_LIVENESS_GAP",))
        self.assertGreater(result.max_market_liveness_gap_seconds, 15.0)
        self.assertLessEqual(result.max_bridge_liveness_gap_seconds, 15.0)

    def test_three_hour_broker_clock_offset_is_rejected_as_source_time_skew(self) -> None:
        clock = FakeClock()
        skewed = tick_record(1)
        object.__setattr__(
            skewed,
            "source_time_msc",
            int((START + timedelta(hours=3)).timestamp() * 1000),
        )
        tail = ScriptedTail(clock, [(0.1, (skewed,))])

        result = qualify_bridge(
            tail,
            utc_now=clock.utc_now,
            monotonic_ns=clock.monotonic_ns,
        )

        self.assertEqual(result.outcome, QualificationOutcome.CONNECTOR_REJECTED)
        self.assertEqual(result.rejection_codes, ("SOURCE_TIME_SKEW",))

    def test_identity_source_regression_and_conflicting_duplicate_are_rejected(self) -> None:
        cases: list[tuple[tuple[object, ...], str]] = []
        wrong_session = heartbeat_record(1)
        object.__setattr__(wrong_session, "bridge_session_id", "c" * 64)
        cases.append(((wrong_session,), "BRIDGE_INTEGRITY"))
        cases.append(((tick_record(2), tick_record(1)), "BRIDGE_INTEGRITY"))
        conflict = tick_record(3)
        conflicting = BridgeTickRecord(
            protocol=conflict.protocol,
            bridge_session_id=conflict.bridge_session_id,
            symbol=conflict.symbol,
            server=conflict.server,
            account_fingerprint=conflict.account_fingerprint,
            source_time_msc=conflict.source_time_msc,
            bid=conflict.bid,
            ask=conflict.ask + 0.001,
            flags=conflict.flags,
        )
        cases.append(((conflict, conflicting), "BRIDGE_INTEGRITY"))

        for records, code in cases:
            with self.subTest(records=records):
                clock = FakeClock()
                tail = ScriptedTail(clock, [(0.1, records)])
                result = qualify_bridge(
                    tail,
                    utc_now=clock.utc_now,
                    monotonic_ns=clock.monotonic_ns,
                )
                self.assertEqual(result.outcome, QualificationOutcome.CONNECTOR_REJECTED)
                self.assertEqual(result.rejection_codes, (code,))

    def test_ten_minute_limit_is_inconclusive_without_late_processing(self) -> None:
        clock = FakeClock()
        script: list[tuple[float, tuple[object, ...] | Exception]] = [
            (12.0, (tick_record(index),)) for index in range(50)
        ]
        script.append((1.0, (tick_record(50),)))
        tail = ScriptedTail(clock, script)
        result = qualify_bridge(tail, utc_now=clock.utc_now, monotonic_ns=clock.monotonic_ns)
        self.assertEqual(result.outcome, QualificationOutcome.INCONCLUSIVE)
        self.assertEqual(result.price_count, 49)
        self.assertEqual(result.heartbeat_count, 0)
        self.assertLessEqual(result.elapsed_seconds, 600.0)
        self.assertEqual(tail.read_count, 50)

    def test_qualification_module_has_no_strategy_bar_simulator_or_risk_imports(self) -> None:
        source = Path("src/fmp/shadow/qualification.py").read_text(encoding="utf-8")
        for forbidden in (
            "fmp.strategies",
            "fmp.research.adapter",
            "fmp.risk",
            ".bars",
            ".simulation",
            ".strategy",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
