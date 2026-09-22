from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fmp.phase8b.bridge import (
    Phase8BBridgeProtocolError,
    Phase8BBridgeStartRecord,
    Phase8BBridgeTickRecord,
)
from fmp.phase8b.capture import (
    PHASE8B_CAPTURE_EXPERIMENT_ID,
    PHASE8B_CAPTURE_FOUNDATION_READY,
    PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL,
    READER_START_SEMANTICS,
    validate_phase8b_capture_preflight,
)
from fmp.phase8b.design import (
    BRIDGE_FILE_BY_SYMBOL,
    LIVENESS_TIMEOUT_SECONDS,
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
    QUOTE_DEADLINE_SECONDS,
    SLIPPAGE_SCENARIOS,
)
from fmp.phase8b.prospective import (
    PHASE8B_PROSPECTIVE_SEGMENT_CLOSED,
    PHASE8B_PROSPECTIVE_SEGMENT_PROTOCOL,
    capture_phase8b_prospective_segment,
    validate_phase8b_prospective_segment,
)
from fmp.portfolio.contracts import ChampionSet, PHASE8A_EXPERIMENT_ID
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory


UTC = timezone.utc
PREPARED = datetime(2026, 9, 22, 16, 0, tzinfo=UTC)
ACCOUNT = "a" * 64
SERVER = "FPMarketsSC-Demo"
COMMIT = "b" * 40


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _preflight():
    inventory = build_phase4_baseline_inventory()
    selected = []
    symbols = set()
    for record in inventory:
        strategy = record.strategy
        if strategy.symbol in symbols:
            continue
        selected.append(strategy)
        symbols.add(strategy.symbol)
        if len(selected) == 2:
            break
    strategies = tuple(sorted(selected, key=lambda item: item.fingerprint))
    champion = ChampionSet(
        champion_set_id="dec052-prospective-test",
        experiment_id=PHASE8A_EXPERIMENT_ID,
        strategies=strategies,
    )
    rows = [
        {
            "fingerprint": item.fingerprint,
            "identity_json": item.identity_json,
            "family": item.family,
            "symbol": item.symbol,
            "timeframe": item.timeframe,
            "parameters_json": item.parameters_json,
            "code_commit": item.code_commit,
            "lifecycle": "SHADOW_CANDIDATE",
            "evidence_id": "EXP-20260922-016:TEST",
        }
        for item in strategies
    ]
    required_symbols = sorted({item.symbol for item in strategies})
    order = {"5m": 0, "15m": 1, "1h": 2}
    required_timeframes = sorted(
        {item.timeframe for item in strategies},
        key=order.__getitem__,
    )
    sessions = {
        symbol: f"{index + 1:064x}"
        for index, symbol in enumerate(required_symbols)
    }
    payload = {
        "protocol": PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL,
        "experiment_id": PHASE8B_CAPTURE_EXPERIMENT_ID,
        "outcome": PHASE8B_CAPTURE_FOUNDATION_READY,
        "registration_sha256": "1" * 64,
        "registration_fingerprint": "2" * 64,
        "start_authorization_sha256": "3" * 64,
        "start_authorization_fingerprint": "4" * 64,
        "capture_foundation_code_commit": "1" * 40,
        "prepared_at_utc": PREPARED.isoformat().replace("+00:00", "Z"),
        "campaign_start_utc": (
            PREPARED - timedelta(minutes=5)
        ).isoformat().replace("+00:00", "Z"),
        "first_london_date": "2026-09-22",
        "reader_start_semantics": READER_START_SEMANTICS,
        "champion_set_id": champion.champion_set_id,
        "champion_set_fingerprint": champion.fingerprint,
        "strategy_count": len(rows),
        "strategy_fingerprints": [item["fingerprint"] for item in rows],
        "strategies": rows,
        "required_symbols": required_symbols,
        "required_timeframes": required_timeframes,
        "provider": MT5_PROVIDER,
        "transport": MT5_TRANSPORT,
        "connector_protocol": MT5_BRIDGE_PROTOCOL,
        "bridge_file_by_symbol": {
            symbol: BRIDGE_FILE_BY_SYMBOL[symbol]
            for symbol in required_symbols
        },
        "account_fingerprint": ACCOUNT,
        "server": SERVER,
        "bridge_session_id_by_symbol": sessions,
        "liveness": {
            "bridge_timeout_seconds": LIVENESS_TIMEOUT_SECONDS,
            "market_quiet_threshold_seconds": LIVENESS_TIMEOUT_SECONDS,
            "quote_deadline_seconds": QUOTE_DEADLINE_SECONDS,
            "per_required_symbol": True,
            "market_quiet_is_bridge_failure": False,
            "backfill_allowed": False,
            "interpolation_allowed": False,
            "alternate_provider_repair_allowed": False,
        },
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "capture_runtime_ready": True,
        "live_shadow_segment_started": False,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    result = payload | {"capture_preflight_fingerprint": _digest(payload)}
    validate_phase8b_capture_preflight(result)
    return result


class FakeTail:
    def __init__(self, start_record, batches):
        self.start_record = start_record
        self._batches = list(batches)

    def read_available(self):
        if not self._batches:
            return ()
        value = self._batches.pop(0)
        if isinstance(value, Exception):
            raise value
        return tuple(value)


def _tails(preflight, *, fail=False):
    result = {}
    for index, symbol in enumerate(preflight["required_symbols"]):
        start = Phase8BBridgeStartRecord(
            protocol=preflight["connector_protocol"],
            bridge_session_id=preflight["bridge_session_id_by_symbol"][symbol],
            symbol=symbol,
            server=preflight["server"],
            account_fingerprint=preflight["account_fingerprint"],
            account_mode="DEMO",
            bridge_start_time_msc=int(PREPARED.timestamp() * 1000),
        )
        tick = Phase8BBridgeTickRecord(
            protocol=preflight["connector_protocol"],
            bridge_session_id=preflight["bridge_session_id_by_symbol"][symbol],
            symbol=symbol,
            server=preflight["server"],
            account_fingerprint=preflight["account_fingerprint"],
            source_time_msc=int(
                (PREPARED + timedelta(seconds=index + 1)).timestamp() * 1000
            ),
            bid=150.0 if symbol == "USDJPY" else 1.10,
            ask=150.02 if symbol == "USDJPY" else 1.1002,
            flags=6,
        )
        batches = [[tick], []]
        if fail and index == 0:
            batches = [
                [tick],
                Phase8BBridgeProtocolError("test bridge failure"),
            ]
        result[symbol] = FakeTail(start, batches)
    return result


class Clock:
    def __init__(self):
        self.utc = PREPARED + timedelta(seconds=1)
        self.ns = 1_000_000_000

    def utc_now(self):
        value = self.utc
        self.utc += timedelta(milliseconds=10)
        return value

    def monotonic_ns(self):
        value = self.ns
        self.ns += 100_000_000
        return value

    def sleep(self, seconds):
        self.ns += int(seconds * 1_000_000_000)
        self.utc += timedelta(seconds=seconds)


class Phase8BProspectiveCaptureTests(unittest.TestCase):
    def test_clean_segment_is_durable_replayed_and_closed(self) -> None:
        preflight = _preflight()
        clock = Clock()
        with TemporaryDirectory() as tmp:
            result = capture_phase8b_prospective_segment(
                preflight=preflight,
                bridge_tails=_tails(preflight),
                code_commit=COMMIT,
                duration_seconds=1,
                segments_root=Path(tmp),
                utc_now=clock.utc_now,
                monotonic_ns=clock.monotonic_ns,
                sleep=clock.sleep,
            )
            self.assertEqual(
                result["protocol"],
                PHASE8B_PROSPECTIVE_SEGMENT_PROTOCOL,
            )
            self.assertEqual(
                result["outcome"],
                PHASE8B_PROSPECTIVE_SEGMENT_CLOSED,
            )
            self.assertTrue(result["prospective_evidence"])
            self.assertTrue(result["prospective_segment_closed"])
            self.assertTrue(result["replay_match"])
            self.assertFalse(result["acceptance_authorized"])
            self.assertFalse(result["demo_order_authorized"])
            validate_phase8b_prospective_segment(result)

            segment_dir = Path(tmp) / result["segment_id"]
            self.assertTrue((segment_dir / "capture-records.jsonl").is_file())
            self.assertTrue((segment_dir / "audit.jsonl").is_file())
            self.assertTrue((segment_dir / "operational-events.jsonl").is_file())
            self.assertTrue((segment_dir / "runtime" / "segment.json").is_file())
            self.assertTrue((segment_dir / "runtime" / "replay.json").is_file())
            self.assertEqual(
                len((segment_dir / "capture-records.jsonl").read_text().splitlines()),
                result["capture_record_count"],
            )
            self.assertEqual(
                len((segment_dir / "audit.jsonl").read_text().splitlines()),
                result["audit_row_count"],
            )

    def test_existing_segment_directory_fails_closed(self) -> None:
        preflight = _preflight()
        first_clock = Clock()
        with TemporaryDirectory() as tmp:
            first = capture_phase8b_prospective_segment(
                preflight=preflight,
                bridge_tails=_tails(preflight),
                code_commit=COMMIT,
                duration_seconds=1,
                segments_root=Path(tmp),
                utc_now=first_clock.utc_now,
                monotonic_ns=first_clock.monotonic_ns,
                sleep=first_clock.sleep,
            )
            second_clock = Clock()
            with self.assertRaises(FileExistsError):
                capture_phase8b_prospective_segment(
                    preflight=preflight,
                    bridge_tails=_tails(preflight),
                    code_commit=COMMIT,
                    duration_seconds=1,
                    segments_root=Path(tmp),
                    utc_now=second_clock.utc_now,
                    monotonic_ns=second_clock.monotonic_ns,
                    sleep=second_clock.sleep,
                )
            self.assertTrue((Path(tmp) / first["segment_id"]).exists())

    def test_protocol_failure_leaves_segment_unclosed(self) -> None:
        preflight = _preflight()
        clock = Clock()
        with TemporaryDirectory() as tmp:
            with self.assertRaises(Phase8BBridgeProtocolError):
                capture_phase8b_prospective_segment(
                    preflight=preflight,
                    bridge_tails=_tails(preflight, fail=True),
                    code_commit=COMMIT,
                    duration_seconds=2,
                    segments_root=Path(tmp),
                    utc_now=clock.utc_now,
                    monotonic_ns=clock.monotonic_ns,
                    sleep=clock.sleep,
                )
            segment_dirs = list(Path(tmp).iterdir())
            self.assertEqual(len(segment_dirs), 1)
            self.assertFalse(
                (segment_dirs[0] / "prospective-segment.json").exists()
            )
            events = (
                segment_dirs[0] / "operational-events.jsonl"
            ).read_text()
            self.assertIn("PROTOCOL_FAILURE", events)

    def test_duration_bounds_are_frozen(self) -> None:
        preflight = _preflight()
        for value in (0, 86401):
            with self.subTest(value=value):
                with TemporaryDirectory() as tmp:
                    with self.assertRaisesRegex(ValueError, "duration"):
                        capture_phase8b_prospective_segment(
                            preflight=preflight,
                            bridge_tails=_tails(preflight),
                            code_commit=COMMIT,
                            duration_seconds=value,
                            segments_root=Path(tmp),
                        )


if __name__ == "__main__":
    unittest.main()
