from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fmp.phase8b.bridge import (
    Phase8BBridgeFileTail,
    Phase8BBridgeProtocolError,
    Phase8BBridgeSessionValidator,
    Phase8BBridgeStartRecord,
    Phase8BBridgeTickRecord,
    _discover_phase8b_bridge_file,
    parse_phase8b_bridge_line,
)
from fmp.phase8b.design import BRIDGE_FILE_BY_SYMBOL


UTC = timezone.utc
SESSION = "a" * 64
ACCOUNT = "b" * 64
SERVER = "FPMarketsSC-Demo"
NOW = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)
NOW_MSC = int(NOW.timestamp() * 1000)


def _line(
    *,
    record_type: str,
    symbol: str = "EURUSD",
    session: str = SESSION,
    account: str = ACCOUNT,
    server: str = SERVER,
    source_time_msc: int = NOW_MSC,
) -> bytes:
    common = {
        "record_type": record_type,
        "protocol": "fmp-mt5-demo-multisymbol-file-bridge-v1",
        "bridge_session_id": session,
        "symbol": symbol,
        "server": server,
        "account_fingerprint": account,
    }
    if record_type == "BRIDGE_START":
        common |= {
            "account_mode": "DEMO",
            "bridge_start_time_msc": source_time_msc,
        }
    elif record_type == "TICK":
        common |= {
            "source_time_msc": source_time_msc,
            "bid": 1.1000,
            "ask": 1.1002,
            "flags": 6,
        }
    else:
        common |= {
            "bridge_emitted_time_msc": source_time_msc,
            "last_tick_time_msc": source_time_msc,
        }
    return (
        json.dumps(common, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


class Phase8BBridgeTests(unittest.TestCase):
    def test_parser_accepts_only_v1_symbols_and_new_protocol(self) -> None:
        start = parse_phase8b_bridge_line(_line(record_type="BRIDGE_START"))
        self.assertIsInstance(start, Phase8BBridgeStartRecord)
        self.assertEqual(start.symbol, "EURUSD")

        tick = parse_phase8b_bridge_line(
            _line(record_type="TICK", symbol="GBPUSD")
        )
        self.assertIsInstance(tick, Phase8BBridgeTickRecord)
        self.assertEqual(tick.symbol, "GBPUSD")

        bad = json.loads(_line(record_type="TICK").decode("utf-8"))
        bad["symbol"] = "AUDUSD"
        with self.assertRaisesRegex(Phase8BBridgeProtocolError, "symbol"):
            parse_phase8b_bridge_line(
                (json.dumps(bad, separators=(",", ":")) + "\n").encode()
            )

        bad["symbol"] = "EURUSD"
        bad["protocol"] = "fmp-mt5-demo-file-bridge-v1"
        with self.assertRaisesRegex(Phase8BBridgeProtocolError, "protocol"):
            parse_phase8b_bridge_line(
                (json.dumps(bad, separators=(",", ":")) + "\n").encode()
            )

    def test_session_validator_binds_expected_symbol_identity_and_source_order(self) -> None:
        validator = Phase8BBridgeSessionValidator("EURUSD")
        validator.accept(
            parse_phase8b_bridge_line(_line(record_type="BRIDGE_START")),
            received_at_utc=NOW,
            receive_monotonic_ns=1,
        )
        quote = validator.accept(
            parse_phase8b_bridge_line(_line(record_type="TICK")),
            received_at_utc=NOW,
            receive_monotonic_ns=2,
        )
        self.assertIsNotNone(quote)
        self.assertEqual(quote.symbol, "EURUSD")

        with self.assertRaisesRegex(Phase8BBridgeProtocolError, "symbol"):
            validator.accept(
                parse_phase8b_bridge_line(
                    _line(record_type="TICK", symbol="GBPUSD")
                ),
                received_at_utc=NOW,
                receive_monotonic_ns=3,
            )

        with self.assertRaisesRegex(Phase8BBridgeProtocolError, "regressed"):
            validator.accept(
                parse_phase8b_bridge_line(
                    _line(
                        record_type="TICK",
                        source_time_msc=NOW_MSC - 1,
                    )
                ),
                received_at_utc=NOW,
                receive_monotonic_ns=4,
            )

    def test_tail_snapshots_pre_reader_content_and_rejects_symbol_change(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "feed.jsonl"
            path.write_bytes(
                _line(record_type="BRIDGE_START")
                + _line(record_type="TICK")
            )
            tail = Phase8BBridgeFileTail(
                path,
                expected_symbol="EURUSD",
            )
            self.assertEqual(tail.read_available(), ())

            with path.open("ab") as handle:
                handle.write(
                    _line(
                        record_type="TICK",
                        source_time_msc=NOW_MSC + 1,
                    )
                )
            self.assertEqual(len(tail.read_available()), 1)

            with path.open("ab") as handle:
                handle.write(
                    _line(
                        record_type="TICK",
                        symbol="GBPUSD",
                        source_time_msc=NOW_MSC + 2,
                    )
                )
            with self.assertRaisesRegex(
                Phase8BBridgeProtocolError,
                "expected symbol",
            ):
                tail.read_available()

    def test_fixed_discovery_is_per_symbol_and_rejects_duplicates(self) -> None:
        with TemporaryDirectory() as first_tmp, TemporaryDirectory() as second_tmp:
            first = Path(first_tmp)
            second = Path(second_tmp)
            relative = Path(*BRIDGE_FILE_BY_SYMBOL["EURUSD"].split("/"))
            with self.assertRaises(FileNotFoundError):
                _discover_phase8b_bridge_file("EURUSD", (first, second))

            one = first / relative
            one.parent.mkdir(parents=True)
            one.write_text("", encoding="utf-8")
            self.assertEqual(
                _discover_phase8b_bridge_file("EURUSD", (first, second)),
                one,
            )

            two = second / relative
            two.parent.mkdir(parents=True)
            two.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(
                Phase8BBridgeProtocolError,
                "multiple",
            ):
                _discover_phase8b_bridge_file("EURUSD", (first, second))


class Phase8BMqlBridgeSafetyTests(unittest.TestCase):
    def test_bridge_source_is_fixed_read_only_demo_surface(self) -> None:
        source = Path(
            "mt5/Experts/FMPPhase8BQuoteBridge.mq5"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'fmp-mt5-demo-multisymbol-file-bridge-v1',
            source,
        )
        for symbol, filename in BRIDGE_FILE_BY_SYMBOL.items():
            self.assertIn(symbol, source)
            self.assertIn(filename.replace("/", "\\"), source)
        self.assertIn("ACCOUNT_TRADE_MODE_DEMO", source)
        self.assertIn("FPMarketsSC-Demo", source)
        self.assertIn("FPMarketsSC-Demo2", source)
        self.assertIn("FILE_COMMON", source)
        self.assertIn("TimeGMT()", source)
        self.assertIn("source_time_msc", source)
        self.assertNotIn("input ", source)
        self.assertNotIn("extern ", source)

        forbidden = (
            "OrderSend",
            "CTrade",
            "PositionOpen",
            "PositionClose",
            "PositionModify",
            "Buy(",
            "Sell(",
            "TRADE_ACTION_",
            "MqlTradeRequest",
        )
        for token in forbidden:
            self.assertNotIn(token, source, token)


if __name__ == "__main__":
    unittest.main()
