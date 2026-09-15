from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

from fmp.shadow.qualification import (
    QualificationOutcome,
    practice_boundary_audit,
    qualify_stream,
)
from fmp.shadow.oanda import OandaPracticeStreamError


UTC = timezone.utc
START = datetime(2026, 9, 15, 12, 0, tzinfo=UTC)


def price_line(second: int, *, bid: str = "140.001", ask: str = "140.003") -> bytes:
    return (
        '{"type":"PRICE","time":"2026-09-15T12:%02d:%02dZ",'
        '"instrument":"USD_JPY","tradeable":true,'
        '"bids":[{"price":"%s"}],"asks":[{"price":"%s"}]}'
        % (second // 60, second % 60, bid, ask)
    ).encode("utf-8")


def heartbeat_line(second: int) -> bytes:
    return (
        '{"type":"HEARTBEAT","time":"2026-09-15T12:%02d:%02dZ"}'
        % (second // 60, second % 60)
    ).encode("utf-8")


class FakeClock:
    def __init__(self) -> None:
        self.elapsed = 0.0

    def advance(self, seconds: float) -> None:
        self.elapsed += seconds

    def utc_now(self) -> datetime:
        return START + timedelta(seconds=self.elapsed)

    def monotonic_ns(self) -> int:
        return int(self.elapsed * 1_000_000_000)


class FakeStream:
    def __init__(
        self,
        clock: FakeClock,
        records: list[tuple[float, bytes]],
        *,
        error: Exception | None = None,
    ) -> None:
        self.clock = clock
        self.records = records
        self.error = error
        self.consumed = 0

    def iter_lines(self):  # type: ignore[no-untyped-def]
        for delay, line in self.records:
            self.clock.advance(delay)
            self.consumed += 1
            yield line
        if self.error is not None:
            raise self.error


class Phase8QualificationTests(unittest.TestCase):
    def test_boundary_audit_is_exact_fixed_practice_get_surface(self) -> None:
        self.assertEqual(
            practice_boundary_audit(),
            {
                "method": "GET",
                "host": "stream-fxpractice.oanda.com",
                "path_template": "/v3/accounts/{account_id}/pricing/stream",
                "instrument": "USD_JPY",
                "snapshot": True,
                "include_home_conversions": False,
            },
        )

    def test_pass_requires_100_prices_and_6_heartbeats_and_stops_early(self) -> None:
        clock = FakeClock()
        records: list[tuple[float, bytes]] = []
        for index in range(100):
            records.append((0.1, price_line(index)))
            if index in (10, 20, 30, 40, 50, 60):
                records.append((0.1, heartbeat_line(index)))
        records.append((0.1, b'{"type":"ORDER"}'))
        stream = FakeStream(clock, records)

        result = qualify_stream(
            stream,
            utc_now=clock.utc_now,
            monotonic_ns=clock.monotonic_ns,
            account_fingerprint="a" * 64,
        )

        self.assertEqual(result.outcome, QualificationOutcome.PASS)
        self.assertEqual(result.price_count, 100)
        self.assertEqual(result.heartbeat_count, 6)
        self.assertLess(stream.consumed, len(records))
        self.assertLessEqual(result.elapsed_seconds, 600.0)
        self.assertLessEqual(result.max_liveness_gap_seconds, 15.0)
        self.assertEqual(result.boundary_audit, practice_boundary_audit())

    def test_low_activity_without_integrity_failure_is_inconclusive(self) -> None:
        clock = FakeClock()
        stream = FakeStream(
            clock,
            [(1.0, price_line(0)), (1.0, heartbeat_line(1))],
        )
        result = qualify_stream(
            stream,
            utc_now=clock.utc_now,
            monotonic_ns=clock.monotonic_ns,
            account_fingerprint="b" * 64,
        )
        self.assertEqual(result.outcome, QualificationOutcome.INCONCLUSIVE)
        self.assertEqual(result.price_count, 1)
        self.assertEqual(result.heartbeat_count, 1)

    def test_ten_minute_limit_returns_inconclusive_without_processing_late_record(self) -> None:
        clock = FakeClock()
        stream = FakeStream(
            clock,
            [(599.0, price_line(0)), (2.0, b'{"type":"ORDER"}')],
        )
        result = qualify_stream(
            stream,
            utc_now=clock.utc_now,
            monotonic_ns=clock.monotonic_ns,
            account_fingerprint="c" * 64,
        )
        self.assertEqual(result.outcome, QualificationOutcome.INCONCLUSIVE)
        self.assertEqual(result.price_count, 1)
        self.assertEqual(result.heartbeat_count, 0)
        self.assertLessEqual(result.elapsed_seconds, 600.0)

    def test_liveness_gap_over_15_seconds_is_connector_rejected(self) -> None:
        clock = FakeClock()
        stream = FakeStream(
            clock,
            [(0.0, price_line(0)), (15.001, heartbeat_line(15))],
        )
        result = qualify_stream(
            stream,
            utc_now=clock.utc_now,
            monotonic_ns=clock.monotonic_ns,
            account_fingerprint="d" * 64,
        )
        self.assertEqual(result.outcome, QualificationOutcome.CONNECTOR_REJECTED)
        self.assertIn("LIVENESS_GAP", result.rejection_codes)

    def test_malformed_unknown_or_integrity_invalid_message_is_rejected(self) -> None:
        cases = (
            b"not-json",
            b'{"type":"ORDER","time":"2026-09-15T12:00:00Z"}',
            price_line(0, bid="140.004", ask="140.003"),
        )
        for line in cases:
            with self.subTest(line=line):
                clock = FakeClock()
                result = qualify_stream(
                    FakeStream(clock, [(0.0, line)]),
                    utc_now=clock.utc_now,
                    monotonic_ns=clock.monotonic_ns,
                    account_fingerprint="e" * 64,
                )
                self.assertEqual(result.outcome, QualificationOutcome.CONNECTOR_REJECTED)
                self.assertTrue(result.rejection_codes)

    def test_transport_or_auth_availability_failure_is_connector_unavailable(self) -> None:
        clock = FakeClock()
        stream = FakeStream(
            clock,
            [],
            error=OandaPracticeStreamError("OANDA Practice pricing stream returned HTTP 401"),
        )
        result = qualify_stream(
            stream,
            utc_now=clock.utc_now,
            monotonic_ns=clock.monotonic_ns,
            account_fingerprint="f" * 64,
        )
        self.assertEqual(result.outcome, QualificationOutcome.CONNECTOR_UNAVAILABLE)
        self.assertEqual(result.rejection_codes, ("STREAM_UNAVAILABLE",))

    def test_qualification_module_has_no_strategy_or_risk_imports(self) -> None:
        source = Path("src/fmp/shadow/qualification.py").read_text(encoding="utf-8")
        for forbidden in ("fmp.strategies", "fmp.research.adapter", "fmp.risk"):
            self.assertNotIn(forbidden, source)

    def test_account_fingerprint_is_validated_but_plain_account_id_is_not_part_of_result(self) -> None:
        clock = FakeClock()
        with self.assertRaises(ValueError):
            qualify_stream(
                FakeStream(clock, []),
                utc_now=clock.utc_now,
                monotonic_ns=clock.monotonic_ns,
                account_fingerprint="not-a-sha",
            )
        result = qualify_stream(
            FakeStream(clock, []),
            utc_now=clock.utc_now,
            monotonic_ns=clock.monotonic_ns,
            account_fingerprint="0" * 64,
        )
        self.assertEqual(result.account_fingerprint, "0" * 64)
        self.assertFalse(hasattr(result, "account_id"))
        self.assertFalse(hasattr(result, "token"))


if __name__ == "__main__":
    unittest.main()
