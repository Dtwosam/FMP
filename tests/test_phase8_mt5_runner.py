from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

from fmp.shadow.mt5_bridge import (
    BridgeHeartbeatRecord,
    BridgeProtocolError,
    BridgeStartRecord,
    BridgeTickRecord,
)
from fmp.shadow.runner import ShadowRunner


UTC = timezone.utc
START = datetime(2026, 9, 17, 20, 0, tzinfo=UTC)
SESSION = "a" * 64
FINGERPRINT = "b" * 64
SERVER = "FPMarketsSC-Demo2"
BASE_MSC = 1_789_667_200_000


def bridge_start(*, session: str = SESSION) -> BridgeStartRecord:
    return BridgeStartRecord(
        protocol="fmp-mt5-demo-file-bridge-v1",
        bridge_session_id=session,
        symbol="USDJPY",
        server=SERVER,
        account_fingerprint=FINGERPRINT,
        account_mode="DEMO",
        bridge_start_time_msc=BASE_MSC - 1_000,
    )


def tick(index: int) -> BridgeTickRecord:
    bid = 147.100 + (index * 0.001)
    return BridgeTickRecord(
        protocol="fmp-mt5-demo-file-bridge-v1",
        bridge_session_id=SESSION,
        symbol="USDJPY",
        server=SERVER,
        account_fingerprint=FINGERPRINT,
        source_time_msc=BASE_MSC + index,
        bid=bid,
        ask=bid + 0.002,
        flags=6,
    )


def heartbeat(index: int, *, last_tick_time_msc: int | None = None) -> BridgeHeartbeatRecord:
    return BridgeHeartbeatRecord(
        protocol="fmp-mt5-demo-file-bridge-v1",
        bridge_session_id=SESSION,
        symbol="USDJPY",
        server=SERVER,
        account_fingerprint=FINGERPRINT,
        bridge_emitted_time_msc=BASE_MSC + 5_000 + index,
        last_tick_time_msc=last_tick_time_msc,
    )


class RecordingEvidence:
    code_commit = "c" * 40
    account_fingerprint_sha256 = FINGERPRINT

    def __init__(self) -> None:
        self.raw: list[object] = []
        self.normalized: list[object] = []
        self.bars: list[object] = []
        self.decisions: list[object] = []
        self.scenarios: list[object] = []
        self.operational: list[dict[str, object]] = []

    def append_raw(self, provider_object, *, received_at_utc, receive_monotonic_ns):  # type: ignore[no-untyped-def]
        self.raw.append((provider_object, received_at_utc, receive_monotonic_ns))

    def append_normalized(self, event: object) -> None:
        self.normalized.append(event)

    def append_bar(self, timeframe: str, bar: object) -> None:
        self.bars.append((timeframe, bar))

    def append_decision(self, record) -> None:  # type: ignore[no-untyped-def]
        self.decisions.append(record)

    def append_scenario(self, record) -> None:  # type: ignore[no-untyped-def]
        self.scenarios.append(record)

    def append_operational(self, record) -> None:  # type: ignore[no-untyped-def]
        self.operational.append(dict(record))


class SpyBars:
    def __init__(self) -> None:
        self.quote_calls: list[object] = []
        self.time_advance_calls: list[datetime] = []
        self.stale_intervals: list[tuple[datetime, datetime]] = []

    def on_quote(self, quote):  # type: ignore[no-untyped-def]
        self.quote_calls.append(quote)
        return ()

    def on_time_advance(self, when: datetime):
        self.time_advance_calls.append(when)
        return ()

    def mark_stale_interval(self, start: datetime, end: datetime) -> None:
        self.stale_intervals.append((start, end))

    def drain_completed_minute_bars(self):  # type: ignore[no-untyped-def]
        return ()


class SpySimulator:
    def __init__(self) -> None:
        self.states: dict[float, object] = {}
        self.quote_calls: list[object] = []
        self.time_advance_calls: list[datetime] = []
        self.stale_gaps: list[tuple[datetime, datetime]] = []

    def on_quote(self, quote) -> None:  # type: ignore[no-untyped-def]
        self.quote_calls.append(quote)

    def on_time_advance(self, when: datetime) -> None:
        self.time_advance_calls.append(when)

    def mark_stale_gap(self, start: datetime, end: datetime) -> None:
        self.stale_gaps.append((start, end))

    def register_decision(self, decision, scheduled_exit) -> None:  # type: ignore[no-untyped-def]
        raise AssertionError("strategy must not run in these bridge tests")


class Phase8Mt5RunnerTests(unittest.TestCase):
    def make_runner(self, *, processing_clock=None):  # type: ignore[no-untyped-def]
        evidence = RecordingEvidence()
        bars = SpyBars()
        simulator = SpySimulator()
        runner = ShadowRunner(
            evidence=evidence,
            bar_builder=bars,
            simulator=simulator,
            strategy_adapter=lambda _: (),
            processing_monotonic_ns=processing_clock,
        )
        runner.start(now_utc=START, restarted=False)
        return runner, evidence, bars, simulator

    def test_bridge_heartbeat_is_raw_liveness_only_and_never_advances_market_time(self) -> None:
        runner, evidence, bars, simulator = self.make_runner()
        runner.process_bridge_record(
            bridge_start(), received_at_utc=START, receive_monotonic_ns=0
        )
        runner.process_bridge_record(
            heartbeat(1),
            received_at_utc=START + timedelta(seconds=5),
            receive_monotonic_ns=5_000_000_000,
        )

        self.assertEqual(len(evidence.raw), 2)
        self.assertEqual(evidence.normalized, [])
        self.assertEqual(bars.quote_calls, [])
        self.assertEqual(bars.time_advance_calls, [])
        self.assertEqual(simulator.quote_calls, [])
        self.assertEqual(simulator.time_advance_calls, [])
        self.assertFalse(runner.stale)

    def test_tick_reuses_normalized_quote_pipeline_and_durable_processing_latency(self) -> None:
        completion_ns = 1_005_000_000
        runner, evidence, bars, simulator = self.make_runner(
            processing_clock=lambda: completion_ns
        )
        runner.process_bridge_record(
            bridge_start(), received_at_utc=START, receive_monotonic_ns=0
        )
        runner.process_bridge_record(
            tick(1),
            received_at_utc=START + timedelta(seconds=1),
            receive_monotonic_ns=1_000_000_000,
        )

        self.assertEqual(len(evidence.raw), 2)
        self.assertEqual(len(evidence.normalized), 1)
        self.assertEqual(len(bars.quote_calls), 1)
        self.assertEqual(len(simulator.quote_calls), 1)
        self.assertEqual(bars.time_advance_calls, [])
        self.assertEqual(simulator.time_advance_calls, [])
        latency = [
            row for row in evidence.operational if row.get("event") == "normalized_append_latency"
        ]
        self.assertEqual(len(latency), 1)
        self.assertEqual(latency[0]["processing_latency_ms"], 5.0)

    def test_market_liveness_stales_even_while_bridge_heartbeats_continue(self) -> None:
        runner, evidence, bars, simulator = self.make_runner()
        runner.process_bridge_record(
            bridge_start(), received_at_utc=START, receive_monotonic_ns=0
        )
        for seconds in (5, 10, 15):
            runner.process_bridge_record(
                heartbeat(seconds),
                received_at_utc=START + timedelta(seconds=seconds),
                receive_monotonic_ns=seconds * 1_000_000_000,
            )

        self.assertTrue(runner.stale)
        self.assertEqual(bars.time_advance_calls, [])
        self.assertEqual(simulator.time_advance_calls, [])
        self.assertEqual(len(bars.stale_intervals), 1)
        self.assertEqual(len(simulator.stale_gaps), 1)
        stale = [row for row in evidence.operational if row.get("event") == "stale"]
        self.assertEqual(stale[-1]["liveness_reason"], "market")

    def test_bridge_liveness_gap_is_distinct_and_invalidates_date(self) -> None:
        runner, evidence, bars, simulator = self.make_runner()
        runner.process_bridge_record(
            bridge_start(), received_at_utc=START, receive_monotonic_ns=0
        )
        runner.process_bridge_record(
            heartbeat(16),
            received_at_utc=START + timedelta(seconds=16),
            receive_monotonic_ns=16_000_000_000,
        )

        self.assertTrue(runner.stale)
        stale = [row for row in evidence.operational if row.get("event") == "stale"]
        self.assertEqual(stale[-1]["liveness_reason"], "bridge")
        self.assertIn(START.astimezone().date(), runner.ineligible_london_dates)

    def test_first_fresh_tick_recovers_runtime_but_date_stays_ineligible(self) -> None:
        runner, evidence, bars, simulator = self.make_runner()
        runner.process_bridge_record(
            bridge_start(), received_at_utc=START, receive_monotonic_ns=0
        )
        for seconds in (5, 10, 15):
            runner.process_bridge_record(
                heartbeat(seconds),
                received_at_utc=START + timedelta(seconds=seconds),
                receive_monotonic_ns=seconds * 1_000_000_000,
            )
        self.assertTrue(runner.stale)

        runner.process_bridge_record(
            tick(1),
            received_at_utc=START + timedelta(seconds=16),
            receive_monotonic_ns=16_000_000_000,
        )
        self.assertFalse(runner.stale)
        self.assertTrue(runner.ineligible_london_dates)
        self.assertTrue(any(row.get("event") == "recovered" for row in evidence.operational))

    def test_session_change_is_rejected_before_continuity_can_be_claimed(self) -> None:
        runner, evidence, bars, simulator = self.make_runner()
        runner.process_bridge_record(
            bridge_start(), received_at_utc=START, receive_monotonic_ns=0
        )
        with self.assertRaises(BridgeProtocolError):
            runner.process_bridge_record(
                bridge_start(session="c" * 64),
                received_at_utc=START + timedelta(seconds=1),
                receive_monotonic_ns=1_000_000_000,
            )
        rejection = [row for row in evidence.operational if row.get("event") == "rejection"]
        self.assertEqual(rejection[-1]["reason"], "bridge_record_rejected")

    def test_runner_source_imports_no_mt5_python_or_trading_surface(self) -> None:
        source = Path("src/fmp/shadow/runner.py").read_text(encoding="utf-8").casefold()
        for forbidden in (
            "import metatrader5",
            "from metatrader5",
            "order_send",
            "ordersend",
            "mqltraderequest",
            "ctrade",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
