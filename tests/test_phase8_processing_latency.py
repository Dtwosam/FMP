from __future__ import annotations

import inspect
from datetime import datetime, timezone
import unittest

from fmp.shadow.runner import ShadowRunner, run_live_shadow_capture


UTC = timezone.utc
BASE = datetime(2026, 9, 16, 11, 0, tzinfo=UTC)


class _EvidenceSpy:
    def __init__(self) -> None:
        self.code_commit = "a" * 40
        self.account_fingerprint_sha256 = "b" * 64
        self.normalized_appended = False
        self.operational: list[dict[str, object]] = []

    def append_raw(self, provider_object, *, received_at_utc, receive_monotonic_ns):  # type: ignore[no-untyped-def]
        return None

    def append_normalized(self, event):  # type: ignore[no-untyped-def]
        self.normalized_appended = True

    def append_bar(self, timeframe, item):  # type: ignore[no-untyped-def]
        return None

    def append_decision(self, record):  # type: ignore[no-untyped-def]
        return None

    def append_scenario(self, record):  # type: ignore[no-untyped-def]
        return None

    def append_operational(self, record):  # type: ignore[no-untyped-def]
        self.operational.append(dict(record))


class Phase8ProcessingLatencyEvidenceTests(unittest.TestCase):
    def test_runner_records_receipt_to_completed_normalized_append_latency(self) -> None:
        self.assertIn(
            "processing_monotonic_ns",
            inspect.signature(ShadowRunner).parameters,
            "ShadowRunner must accept the live monotonic clock used for durable-append latency evidence",
        )
        evidence = _EvidenceSpy()

        def completed_append_clock() -> int:
            self.assertTrue(
                evidence.normalized_appended,
                "latency completion time must be sampled only after normalized evidence is durably appended",
            )
            return 1_250_000_000

        runner = ShadowRunner(
            evidence=evidence,
            processing_monotonic_ns=completed_append_clock,
        )
        runner.start(now_utc=BASE, restarted=False)
        runner.process_provider_message(
            {"type": "HEARTBEAT", "time": "2026-09-16T11:00:00Z"},
            received_at_utc=BASE,
            receive_monotonic_ns=1_000_000_000,
        )

        latency = [
            item
            for item in evidence.operational
            if item.get("event") == "normalized_append_latency"
        ]
        self.assertEqual(len(latency), 1)
        self.assertEqual(latency[0]["timestamp_utc"], BASE)
        self.assertEqual(latency[0]["source_time_utc"], BASE)
        self.assertEqual(latency[0]["receive_monotonic_ns"], 1_000_000_000)
        self.assertEqual(latency[0]["append_completed_monotonic_ns"], 1_250_000_000)
        self.assertEqual(latency[0]["processing_latency_ms"], 250.0)

    def test_live_capture_uses_same_segment_monotonic_clock_for_latency_completion(self) -> None:
        source = inspect.getsource(run_live_shadow_capture)
        self.assertIn("processing_monotonic_ns=monotonic_ns", source)


if __name__ == "__main__":
    unittest.main()
