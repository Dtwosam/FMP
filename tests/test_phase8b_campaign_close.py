from __future__ import annotations

import hashlib
import json
import shutil
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fmp.phase8b.acceptance import validate_phase8b_campaign_evidence
from fmp.phase8b.bridge import (
    Phase8BBridgeStartRecord,
    Phase8BBridgeTickRecord,
)
from fmp.phase8b.campaign_close import (
    PHASE8B_CAMPAIGN_EVIDENCE_SNAPSHOT_READY,
    close_phase8b_campaign_directory,
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
from fmp.phase8b.prospective import capture_phase8b_prospective_segment
from fmp.portfolio.contracts import ChampionSet, PHASE8A_EXPERIMENT_ID
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory


UTC = timezone.utc
BASE = datetime(2026, 9, 22, 16, 0, tzinfo=UTC)
ACCOUNT = "a" * 64
SERVER = "FPMarketsSC-Demo"
SEGMENT_COMMIT = "b" * 40
CLOSE_COMMIT = "c" * 40


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


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


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
        champion_set_id="dec053-campaign-close-test",
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
        "prepared_at_utc": BASE.isoformat().replace("+00:00", "Z"),
        "campaign_start_utc": (
            BASE - timedelta(minutes=5)
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
        return tuple(self._batches.pop(0))


def _tails(preflight, *, source_base: datetime):
    result = {}
    for index, symbol in enumerate(preflight["required_symbols"]):
        start = Phase8BBridgeStartRecord(
            protocol=preflight["connector_protocol"],
            bridge_session_id=preflight["bridge_session_id_by_symbol"][symbol],
            symbol=symbol,
            server=preflight["server"],
            account_fingerprint=preflight["account_fingerprint"],
            account_mode="DEMO",
            bridge_start_time_msc=int(BASE.timestamp() * 1000),
        )
        tick = Phase8BBridgeTickRecord(
            protocol=preflight["connector_protocol"],
            bridge_session_id=preflight["bridge_session_id_by_symbol"][symbol],
            symbol=symbol,
            server=preflight["server"],
            account_fingerprint=preflight["account_fingerprint"],
            source_time_msc=int(
                (source_base + timedelta(milliseconds=index)).timestamp()
                * 1000
            ),
            bid=150.0 if symbol == "USDJPY" else 1.10,
            ask=150.02 if symbol == "USDJPY" else 1.1002,
            flags=6,
        )
        result[symbol] = FakeTail(start, [[tick], []])
    return result


class Clock:
    def __init__(self, start: datetime, *, start_ns: int = 1_000_000_000):
        self.utc = start
        self.ns = start_ns

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


def _capture(
    campaign: Path,
    preflight,
    *,
    wall_start: datetime,
    source_start: datetime,
    start_ns: int = 1_000_000_000,
):
    clock = Clock(wall_start, start_ns=start_ns)
    return capture_phase8b_prospective_segment(
        preflight=preflight,
        bridge_tails=_tails(preflight, source_base=source_start),
        code_commit=SEGMENT_COMMIT,
        duration_seconds=1,
        segments_root=campaign / "segments",
        utc_now=clock.utc_now,
        monotonic_ns=clock.monotonic_ns,
        sleep=clock.sleep,
    )


class Phase8BCampaignCloseTests(unittest.TestCase):
    def test_closes_two_segments_with_monotonic_restart_as_valid_dec051_evidence(self) -> None:
        preflight = _preflight()
        with TemporaryDirectory() as tmp:
            campaign = Path(tmp)
            _write_json(campaign / "capture-preflight.json", preflight)
            _capture(
                campaign,
                preflight,
                wall_start=BASE + timedelta(seconds=1),
                source_start=BASE + timedelta(seconds=1),
                start_ns=9_000_000_000,
            )
            _capture(
                campaign,
                preflight,
                wall_start=BASE + timedelta(seconds=30),
                source_start=BASE + timedelta(seconds=30),
                start_ns=1_000_000_000,
            )

            result = close_phase8b_campaign_directory(
                campaign_dir=campaign,
                code_commit=CLOSE_COMMIT,
            )
            self.assertEqual(
                result["outcome"],
                PHASE8B_CAMPAIGN_EVIDENCE_SNAPSHOT_READY,
            )
            evidence = result["campaign_evidence"]
            validate_phase8b_campaign_evidence(evidence)
            self.assertTrue(evidence["prospective_evidence"])
            self.assertTrue(evidence["prospective_segment_closed"])
            self.assertTrue(evidence["replay_match"])
            self.assertEqual(evidence["completed_trade_count_0_2"], 0)
            self.assertEqual(evidence["complete_london_dates"], [])
            self.assertEqual(
                evidence["denominator_london_dates"],
                ["2026-09-22"],
            )
            self.assertGreater(
                evidence["timing"]["p99_processing_latency_ms"],
                0.0,
            )
            for symbol in preflight["required_symbols"]:
                spread = evidence["live_spread_by_symbol"][symbol]
                self.assertEqual(spread["entry_sample_count"], 0)
                self.assertIsNone(spread["entry_median_pips"])
                self.assertEqual(spread["exit_sample_count"], 0)
                self.assertIsNone(spread["exit_p95_pips"])

            closure = (
                campaign
                / "closures"
                / result["closure_id"]
            )
            self.assertTrue((closure / "campaign-evidence.json").is_file())
            self.assertTrue((closure / "runtime" / "segment.json").is_file())
            self.assertTrue((closure / "runtime" / "replay.json").is_file())

    def test_raw_journal_tamper_fails_closed(self) -> None:
        preflight = _preflight()
        with TemporaryDirectory() as tmp:
            campaign = Path(tmp)
            _write_json(campaign / "capture-preflight.json", preflight)
            segment = _capture(
                campaign,
                preflight,
                wall_start=BASE + timedelta(seconds=1),
                source_start=BASE + timedelta(seconds=1),
            )
            raw = (
                campaign
                / "segments"
                / segment["segment_id"]
                / "capture-records.jsonl"
            )
            raw.write_bytes(raw.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "capture.*digest|SHA"):
                close_phase8b_campaign_directory(
                    campaign_dir=campaign,
                    code_commit=CLOSE_COMMIT,
                )

    def test_copied_closed_segment_directory_identity_fails_closed(self) -> None:
        preflight = _preflight()
        with TemporaryDirectory() as tmp:
            campaign = Path(tmp)
            _write_json(campaign / "capture-preflight.json", preflight)
            segment = _capture(
                campaign,
                preflight,
                wall_start=BASE + timedelta(seconds=1),
                source_start=BASE + timedelta(seconds=1),
            )
            original = campaign / "segments" / segment["segment_id"]
            duplicate = campaign / "segments" / "duplicate-copy"
            shutil.copytree(original, duplicate)
            with self.assertRaisesRegex(ValueError, "directory identity mismatch"):
                close_phase8b_campaign_directory(
                    campaign_dir=campaign,
                    code_commit=CLOSE_COMMIT,
                )

    def test_cross_segment_source_time_regression_fails_closed(self) -> None:
        preflight = _preflight()
        with TemporaryDirectory() as tmp:
            campaign = Path(tmp)
            _write_json(campaign / "capture-preflight.json", preflight)
            _capture(
                campaign,
                preflight,
                wall_start=BASE + timedelta(seconds=1),
                source_start=BASE + timedelta(seconds=20),
            )
            _capture(
                campaign,
                preflight,
                wall_start=BASE + timedelta(seconds=30),
                source_start=BASE + timedelta(seconds=10),
            )
            with self.assertRaisesRegex(ValueError, "source time"):
                close_phase8b_campaign_directory(
                    campaign_dir=campaign,
                    code_commit=CLOSE_COMMIT,
                )

    def test_same_segment_set_is_create_only_snapshot(self) -> None:
        preflight = _preflight()
        with TemporaryDirectory() as tmp:
            campaign = Path(tmp)
            _write_json(campaign / "capture-preflight.json", preflight)
            _capture(
                campaign,
                preflight,
                wall_start=BASE + timedelta(seconds=1),
                source_start=BASE + timedelta(seconds=1),
            )
            close_phase8b_campaign_directory(
                campaign_dir=campaign,
                code_commit=CLOSE_COMMIT,
            )
            with self.assertRaises(FileExistsError):
                close_phase8b_campaign_directory(
                    campaign_dir=campaign,
                    code_commit=CLOSE_COMMIT,
                )


if __name__ == "__main__":
    unittest.main()
