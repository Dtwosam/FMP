from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fmp.shadow.contracts import MT5_BRIDGE_FILE, NormalizedQuote
from fmp.shadow.mt5_bridge import (
    BridgeFileTail,
    BridgeHeartbeatRecord,
    BridgeProtocolError,
    BridgeSessionValidator,
    BridgeStartRecord,
    BridgeTickRecord,
    _discover_bridge_file,
    parse_bridge_line,
)


UTC = timezone.utc
SESSION = "a" * 64
FINGERPRINT = "b" * 64
SERVER = "FPMarketsSC-Demo2"
COMMON = {
    "protocol": "fmp-mt5-demo-file-bridge-v1",
    "bridge_session_id": SESSION,
    "symbol": "USDJPY",
    "server": SERVER,
    "account_fingerprint": FINGERPRINT,
}


def _line(record_type: str, **fields: object) -> bytes:
    payload = {"record_type": record_type, **COMMON, **fields}
    return (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")


def _start_line(**fields: object) -> bytes:
    payload = {"account_mode": "DEMO", "bridge_start_time_msc": 1_789_667_199_000}
    payload.update(fields)
    return _line("BRIDGE_START", **payload)


def _tick_line(**fields: object) -> bytes:
    payload = {"source_time_msc": 1_789_667_200_123, "bid": 147.123, "ask": 147.125, "flags": 6}
    payload.update(fields)
    return _line("TICK", **payload)


def _heartbeat_line(**fields: object) -> bytes:
    payload = {
        "bridge_emitted_time_msc": 1_789_667_205_000,
        "last_tick_time_msc": 1_789_667_200_123,
    }
    payload.update(fields)
    return _line("BRIDGE_HEARTBEAT", **payload)


class Phase8Mt5BridgeParserTests(unittest.TestCase):
    def test_parser_accepts_only_three_exact_record_shapes(self) -> None:
        start = parse_bridge_line(_start_line())
        tick = parse_bridge_line(_tick_line())
        heartbeat = parse_bridge_line(_heartbeat_line())
        heartbeat_before_tick = parse_bridge_line(_heartbeat_line(last_tick_time_msc=None))

        self.assertIsInstance(start, BridgeStartRecord)
        self.assertEqual(start.bridge_session_id, SESSION)
        self.assertEqual(start.account_mode, "DEMO")
        self.assertEqual(start.bridge_start_time_msc, 1_789_667_199_000)
        self.assertIsInstance(tick, BridgeTickRecord)
        self.assertEqual(tick.source_time_msc, 1_789_667_200_123)
        self.assertEqual(tick.bid, 147.123)
        self.assertIsInstance(heartbeat, BridgeHeartbeatRecord)
        self.assertEqual(heartbeat.bridge_emitted_time_msc, 1_789_667_205_000)
        self.assertEqual(heartbeat.last_tick_time_msc, 1_789_667_200_123)
        self.assertIsNone(heartbeat_before_tick.last_tick_time_msc)

        for bad in (
            b"not-json\n",
            b"[]\n",
            _line("UNKNOWN"),
            _start_line(extra="forbidden"),
            _tick_line(extra="forbidden"),
            _heartbeat_line(extra="forbidden"),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(BridgeProtocolError):
                    parse_bridge_line(bad)

    def test_parser_rejects_wrong_identity_and_invalid_values(self) -> None:
        cases = (
            _start_line(protocol="wrong"),
            _start_line(symbol="EURUSD"),
            _start_line(server="FPMarketsSC-Live"),
            _start_line(bridge_session_id="A" * 64),
            _start_line(account_fingerprint="not-hex"),
            _start_line(account_mode="REAL"),
            _start_line(bridge_start_time_msc=0),
            _tick_line(source_time_msc=0),
            _tick_line(bid=0.0),
            _tick_line(ask=float("inf")),
            _tick_line(bid=147.126, ask=147.125),
            _tick_line(flags=-1),
            _heartbeat_line(bridge_emitted_time_msc=0),
            _heartbeat_line(last_tick_time_msc=0),
            _heartbeat_line(last_tick_time_msc=-1),
        )
        for payload in cases:
            with self.subTest(payload=payload):
                with self.assertRaises(BridgeProtocolError):
                    parse_bridge_line(payload)


class Phase8Mt5BridgeSessionTests(unittest.TestCase):
    def test_validator_binds_session_and_only_ticks_become_market_quotes(self) -> None:
        validator = BridgeSessionValidator()
        received = datetime(2026, 9, 17, 20, 0, tzinfo=UTC)

        self.assertIsNone(
            validator.accept(
                parse_bridge_line(_start_line()),
                received_at_utc=received,
                receive_monotonic_ns=10,
            )
        )
        self.assertEqual(validator.bridge_session_id, SESSION)
        self.assertEqual(validator.server, SERVER)
        self.assertEqual(validator.account_fingerprint, FINGERPRINT)
        self.assertEqual(validator.last_bridge_received_at_utc, received)
        self.assertIsNone(validator.last_market_received_at_utc)

        heartbeat_received = datetime(2026, 9, 17, 20, 0, 5, tzinfo=UTC)
        self.assertIsNone(
            validator.accept(
                parse_bridge_line(_heartbeat_line()),
                received_at_utc=heartbeat_received,
                receive_monotonic_ns=20,
            )
        )
        self.assertEqual(validator.last_bridge_received_at_utc, heartbeat_received)
        self.assertIsNone(validator.last_market_received_at_utc)

        tick_received = datetime(2026, 9, 17, 20, 0, 6, tzinfo=UTC)
        quote = validator.accept(
            parse_bridge_line(_tick_line()),
            received_at_utc=tick_received,
            receive_monotonic_ns=30,
        )
        self.assertIsInstance(quote, NormalizedQuote)
        self.assertEqual(quote.symbol, "USDJPY")
        self.assertEqual(quote.bid, 147.123)
        self.assertEqual(quote.ask, 147.125)
        self.assertTrue(quote.tradeable)
        self.assertEqual(quote.source_time_utc.microsecond, 123_000)
        self.assertEqual(validator.last_market_received_at_utc, tick_received)

    def test_validator_dedupes_exact_tick_and_rejects_conflict_or_regression(self) -> None:
        validator = BridgeSessionValidator()
        now = datetime(2026, 9, 17, 20, 0, tzinfo=UTC)
        validator.accept(parse_bridge_line(_start_line()), received_at_utc=now, receive_monotonic_ns=1)
        first = parse_bridge_line(_tick_line())
        self.assertIsNotNone(validator.accept(first, received_at_utc=now, receive_monotonic_ns=2))
        self.assertIsNone(validator.accept(first, received_at_utc=now, receive_monotonic_ns=3))

        with self.assertRaisesRegex(BridgeProtocolError, "conflicting duplicate"):
            validator.accept(
                parse_bridge_line(_tick_line(ask=147.126)),
                received_at_utc=now,
                receive_monotonic_ns=4,
            )
        with self.assertRaisesRegex(BridgeProtocolError, "regressed"):
            validator.accept(
                parse_bridge_line(_tick_line(source_time_msc=1_789_667_200_122)),
                received_at_utc=now,
                receive_monotonic_ns=5,
            )

    def test_validator_rejects_unbound_or_changed_session_identity(self) -> None:
        now = datetime(2026, 9, 17, 20, 0, tzinfo=UTC)
        with self.assertRaisesRegex(BridgeProtocolError, "BRIDGE_START"):
            BridgeSessionValidator().accept(
                parse_bridge_line(_tick_line()), received_at_utc=now, receive_monotonic_ns=1
            )

        validator = BridgeSessionValidator()
        validator.accept(parse_bridge_line(_start_line()), received_at_utc=now, receive_monotonic_ns=1)
        for bad in (
            _tick_line(bridge_session_id="c" * 64),
            _heartbeat_line(account_fingerprint="d" * 64),
            _start_line(),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(BridgeProtocolError):
                    validator.accept(
                        parse_bridge_line(bad), received_at_utc=now, receive_monotonic_ns=2
                    )


class Phase8Mt5BridgeTailTests(unittest.TestCase):
    def test_tail_validates_start_snapshots_eof_and_waits_for_complete_appended_lines(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "feed.jsonl"
            path.write_bytes(_start_line() + _tick_line(bid=147.111, ask=147.113))
            tail = BridgeFileTail(path)
            self.assertEqual(tail.start_record.bridge_session_id, SESSION)
            self.assertEqual(tail.read_available(), ())

            appended = _tick_line(bid=147.120, ask=147.122)
            partial = _heartbeat_line()[:-1]
            with path.open("ab") as handle:
                handle.write(appended)
                handle.write(partial)
            records = tail.read_available()
            self.assertEqual(len(records), 1)
            self.assertIsInstance(records[0], BridgeTickRecord)
            self.assertEqual(records[0].bid, 147.120)
            self.assertEqual(tail.read_available(), ())

            with path.open("ab") as handle:
                handle.write(b"\n")
            records = tail.read_available()
            self.assertEqual(len(records), 1)
            self.assertIsInstance(records[0], BridgeHeartbeatRecord)

    def test_tail_rejects_missing_start_truncation_and_new_session_start(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "feed.jsonl"
            path.write_bytes(_tick_line())
            with self.assertRaisesRegex(BridgeProtocolError, "BRIDGE_START"):
                BridgeFileTail(path)

            path.write_bytes(_start_line())
            tail = BridgeFileTail(path)
            with path.open("ab") as handle:
                handle.write(_tick_line())
            self.assertEqual(len(tail.read_available()), 1)
            path.write_bytes(_start_line())
            with self.assertRaisesRegex(BridgeProtocolError, "truncated"):
                tail.read_available()

            tail = BridgeFileTail(path)
            with path.open("ab") as handle:
                handle.write(_start_line(bridge_session_id="c" * 64))
            with self.assertRaisesRegex(BridgeProtocolError, "session"):
                tail.read_available()

    def test_fixed_file_discovery_is_bounded_and_rejects_zero_or_multiple_matches(self) -> None:
        with TemporaryDirectory() as first_tmp, TemporaryDirectory() as second_tmp:
            first = Path(first_tmp)
            second = Path(second_tmp)
            relative = Path(*MT5_BRIDGE_FILE.split("/"))

            with self.assertRaises(FileNotFoundError):
                _discover_bridge_file((first, second))

            one = first / relative
            one.parent.mkdir(parents=True)
            one.write_text("", encoding="utf-8")
            self.assertEqual(_discover_bridge_file((first, second)), one)

            two = second / relative
            two.parent.mkdir(parents=True)
            two.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(BridgeProtocolError, "multiple"):
                _discover_bridge_file((first, second))


if __name__ == "__main__":
    unittest.main()
