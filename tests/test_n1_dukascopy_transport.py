from __future__ import annotations

import ast
import hashlib
import json
import lzma
import struct
import subprocess
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from fmp.contracts import ExitReason
from fmp.data.dukascopy import DukascopySource, HttpResponse, UrllibTransport
from fmp.data.types import RawChunkKey
from fmp.research.n1_dukascopy_transport import observe_n1_transport_window
from fmp.research.n1_news_shock import ReleaseKind, ReleaseStatus, required_n1_observation_keys
from fmp.research.n1_prospective_pilot import (
    COLLECTION_LIMITATION_CLASS,
    EVIDENCE_CLASS,
    FROZEN_SIGNAL_COMMIT,
    MANIFEST_FILENAME,
    TRANSPORT_DECISION_COMMIT,
    TRANSPORT_EFFECTIVE_UTC,
    DuplicatePilotObservation,
    TransportProvenance,
)
from tests.test_n1_news_shock import _release, _utc

CPI_DAY = date(2026, 12, 10)
EMPSIT_DAY = date(2026, 12, 4)
REPO_ROOT = Path(__file__).resolve().parents[1]
NEW_YORK = ZoneInfo("America/New_York")
_RECORD = struct.Struct(">IIIIIf")
_DIVISOR = {"EURUSD": 100_000, "GBPUSD": 100_000, "USDJPY": 1_000}


def _cpi(**kwargs):
    return _release(CPI_DAY, release_id="bls-cpi-2026-12-10", **kwargs)


def _empsit(**kwargs):
    return _release(
        EMPSIT_DAY,
        release_id="bls-empsit-2026-12-04",
        kind=ReleaseKind.EMPLOYMENT_SITUATION,
        **kwargs,
    )


def _tick(symbol: str, price: float) -> int:
    return int(round(price * _DIVISOR[symbol]))


def _seconds(day: date, hour: int, minute: int) -> int:
    stamp = _utc(day, hour, minute)
    midnight = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    return int((stamp - midnight).total_seconds())


def _ohlc(
    symbol: str,
    open_px: float,
    close_px: float,
    *,
    high_px: float | None = None,
    low_px: float | None = None,
) -> tuple[int, int, int, int]:
    open_i = _tick(symbol, open_px)
    close_i = _tick(symbol, close_px)
    low_i = min(open_i, close_i) if low_px is None else _tick(symbol, low_px)
    high_i = max(open_i, close_i) if high_px is None else _tick(symbol, high_px)
    low_i = min(low_i, open_i, close_i)
    high_i = max(high_i, open_i, close_i)
    return open_i, close_i, low_i, high_i


def _compress(rows: list[tuple[int, int, int, int, int]]) -> bytes:
    payload = b"".join(
        _RECORD.pack(second, open_i, close_i, low_i, high_i, 0.0)
        for second, open_i, close_i, low_i, high_i in sorted(rows)
    )
    return lzma.compress(payload)


def _strength_bodies(day: date) -> dict[str, bytes]:
    """Whole-day files that also contain minutes the pilot must drop."""

    bases = {
        "EURUSD": (1.10000, 1.10020, 1.09900, 1.09920),
        "GBPUSD": (1.30000, 1.30020, 1.29900, 1.29920),
        "USDJPY": (150.000, 150.020, 150.100, 150.120),
    }
    bodies: dict[str, bytes] = {}
    source = DukascopySource()
    for symbol, (bid, ask, bid_close, ask_close) in bases.items():
        clocks = [(8, minute) for minute in range(29, 36)]
        if symbol == "EURUSD":
            cursor = datetime(day.year, day.month, day.day, 8, 36, tzinfo=NEW_YORK)
            end = datetime(day.year, day.month, day.day, 9, 30, tzinfo=NEW_YORK)
            while cursor <= end:
                clocks.append((cursor.hour, cursor.minute))
                cursor += timedelta(minutes=1)
        for side, open_px, close_px in (("BID", bid, bid_close), ("ASK", ask, ask_close)):
            rows = [(60, *_ohlc(symbol, 9.0, 9.0))]
            for hour, minute in clocks:
                if (hour, minute) == (8, 34):
                    prices = (open_px, close_px)
                elif (hour, minute) == (8, 35):
                    junk = 200.0 if symbol == "USDJPY" else 1.5
                    prices = (junk, junk)
                elif hour > 8 or minute >= 36:
                    entry = bid_close if side == "BID" else ask_close
                    prices = (entry, entry)
                else:
                    prices = (open_px, open_px)
                high = 1.10150 if symbol == "EURUSD" and side == "ASK" and (hour, minute) == (8, 32) else None
                rows.append((_seconds(day, hour, minute), *_ohlc(symbol, prices[0], prices[1], high_px=high)))
            bodies[source.url_for(RawChunkKey(symbol, side, day))] = _compress(rows)
    return bodies


class _GuardedHttp(UrllibTransport):
    """Production-class client whose get() never opens a socket."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def get(self, url: str, timeout_seconds: float) -> HttpResponse:
        self.calls.append(url)
        return HttpResponse(status=404, body=b"")


class _ScriptedTransport:
    def __init__(self, bodies: dict[str, tuple[int, bytes]]) -> None:
        self.bodies = bodies
        self.calls: list[str] = []

    def get(self, url: str, timeout_seconds: float) -> HttpResponse:
        self.calls.append(url)
        status, body = self.bodies.get(url, (404, b""))
        return HttpResponse(status=status, body=body)


def _after_window(day: date) -> datetime:
    return _utc(day, 9, 31)


class N1DukascopyTransportTests(unittest.TestCase):
    def test_transport_decision_timestamp_is_the_decision_commit(self) -> None:
        shown = subprocess.check_output(
            ["git", "show", "-s", "--format=%cI", TRANSPORT_DECISION_COMMIT],
            cwd=REPO_ROOT,
            text=True,
        ).strip()
        self.assertEqual(shown, TRANSPORT_EFFECTIVE_UTC)
        self.assertEqual(TRANSPORT_DECISION_COMMIT, "adc4836ff08ea642a0053982cbc377ab3e6c12c0")
        blob = subprocess.check_output(
            ["git", "hash-object", "src/fmp/research/n1_news_shock.py"],
            cwd=REPO_ROOT,
            text=True,
        ).strip()
        frozen = subprocess.check_output(
            ["git", "rev-parse", f"{FROZEN_SIGNAL_COMMIT}:src/fmp/research/n1_news_shock.py"],
            cwd=REPO_ROOT,
            text=True,
        ).strip()
        self.assertEqual(blob, frozen)

    def test_module_does_not_call_the_historical_acquirer(self) -> None:
        source = (REPO_ROOT / "src/fmp/research/n1_dukascopy_transport.py").read_text()
        tree = ast.parse(source)
        names = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
        self.assertNotIn("acquire_chunk", names)
        self.assertNotIn("acquire_chunk", imported)
        self.assertNotIn("urlopen", names)
        self.assertNotIn("urlopen", source)

    def test_window_and_publication_gates_do_not_download(self) -> None:
        bodies = {url: (200, body) for url, body in _strength_bodies(CPI_DAY).items()}
        transport = _ScriptedTransport(bodies)
        too_early = _utc(CPI_DAY, 9, 30)
        verified = _after_window(CPI_DAY)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                observe_n1_transport_window(
                    _cpi(),
                    transport_directory=root / "transport",
                    evidence_directory=root / "evidence",
                    bls_status_verified_at_utc=verified,
                    now_utc=too_early,
                    transport=transport,
                )
            self.assertEqual(transport.calls, [])
            with self.assertRaises(ValueError):
                observe_n1_transport_window(
                    _cpi(status=ReleaseStatus.NOT_PUBLISHED, actual=None),
                    transport_directory=root / "transport",
                    evidence_directory=root / "evidence",
                    bls_status_verified_at_utc=too_early,
                    now_utc=too_early,
                    transport=transport,
                )
            self.assertEqual(transport.calls, [])

    def test_unpublished_release_is_kept_without_a_download(self) -> None:
        transport = _ScriptedTransport({})
        when = _after_window(CPI_DAY)
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"
            records = observe_n1_transport_window(
                _cpi(status=ReleaseStatus.DELAYED, actual=None),
                transport_directory=Path(tmp) / "transport",
                evidence_directory=evidence,
                bls_status_verified_at_utc=when,
                now_utc=when,
                transport=transport,
            )
        self.assertEqual(transport.calls, [])
        self.assertEqual(records[0].evidence_class, COLLECTION_LIMITATION_CLASS)
        self.assertEqual(records[0].collection_limitation, "publication_not_at_0830")
        self.assertFalse(records[0].qualifying_publication)
        self.assertEqual(records[0].source_files, ())

    def test_daily_files_keep_only_approved_minutes_and_bind_hashes(self) -> None:
        bodies = _strength_bodies(CPI_DAY)
        transport = _ScriptedTransport({url: (200, body) for url, body in bodies.items()})
        when = _after_window(CPI_DAY)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transport_dir = root / "transport"
            evidence = root / "evidence"
            records = observe_n1_transport_window(
                _cpi(),
                transport_directory=transport_dir,
                evidence_directory=evidence,
                bls_status_verified_at_utc=when,
                now_utc=when,
                transport=transport,
            )
            self.assertEqual(len(transport.calls), 6)
            self.assertEqual(set(transport.calls), set(bodies))
            self.assertFalse(any(path.suffix == ".bi5" for path in transport_dir.rglob("*")))
            self.assertFalse((transport_dir / ".n1-bls-cpi-2026-12-10").exists())
            rows = [
                json.loads(line)
                for line in (evidence / "n1-v0-pilot-evidence.jsonl").read_text().splitlines()
            ]
            manifest = json.loads((evidence / MANIFEST_FILENAME).read_text().splitlines()[0])
        self.assertEqual([row["slippage_pips"] for row in rows], [0.5, 0.2, 1.0])
        self.assertTrue(all(row["market_evidence"] is True for row in rows))
        self.assertTrue(all(row["evidence_class"] == EVIDENCE_CLASS for row in rows))
        self.assertEqual(len({row["quote_input_sha256"] for row in rows}), 1)
        self.assertEqual(rows[0]["quote_input_sha256"], manifest["quote_input_sha256"])
        self.assertTrue(manifest["payloads_deleted"])
        self.assertEqual(manifest["transport_decision_commit"], TRANSPORT_DECISION_COMMIT)
        self.assertIsNone(rows[0]["collection_limitation"])
        self.assertEqual(records[0].raw_exit_reason, ExitReason.TIME_EXIT.value)
        self.assertEqual(records[0].quality, "COMPLETE")
        self.assertEqual(records[0].raw_commission_usd, 7.0)
        self.assertEqual(len(records[0].source_files), 6)
        forbidden = _utc(CPI_DAY, 8, 35).isoformat()
        self.assertNotIn(forbidden, json.dumps(rows))
        self.assertNotIn("T00:01:00", json.dumps(rows))
        for item in records[0].source_files:
            self.assertEqual(item.sha256, hashlib.sha256(bodies[item.url]).hexdigest())
            self.assertEqual(item.status, "hashed")
        self.assertEqual(len(required_n1_observation_keys(CPI_DAY)), 73)

    def test_repeat_does_not_download_again(self) -> None:
        bodies = {url: (200, body) for url, body in _strength_bodies(EMPSIT_DAY).items()}
        transport = _ScriptedTransport(bodies)
        when = _after_window(EMPSIT_DAY)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kwargs = {
                "transport_directory": root / "transport",
                "evidence_directory": root / "evidence",
                "bls_status_verified_at_utc": when,
                "now_utc": when,
                "transport": transport,
            }
            observe_n1_transport_window(_empsit(), **kwargs)
            self.assertEqual(len(transport.calls), 6)
            with self.assertRaises(DuplicatePilotObservation):
                observe_n1_transport_window(_empsit(), **kwargs)
            self.assertEqual(len(transport.calls), 6)
            self.assertEqual((root / "evidence" / "n1-v0-pilot-evidence.jsonl").read_text().count("\n"), 3)

    def test_missing_file_is_a_limitation_without_invented_prices(self) -> None:
        bodies = {url: (200, body) for url, body in _strength_bodies(CPI_DAY).items()}
        missing = DukascopySource().url_for(RawChunkKey("EURUSD", "BID", CPI_DAY))
        bodies[missing] = (404, b"")
        transport = _ScriptedTransport(bodies)
        when = _after_window(CPI_DAY)
        with tempfile.TemporaryDirectory() as tmp:
            records = observe_n1_transport_window(
                _cpi(),
                transport_directory=Path(tmp) / "transport",
                evidence_directory=Path(tmp) / "evidence",
                bls_status_verified_at_utc=when,
                now_utc=when,
                transport=transport,
            )
        self.assertEqual(records[0].collection_limitation, "source_not_available")
        self.assertEqual(records[0].quality, "INCOMPLETE")
        eurusd = next(item for item in records[0].source_files if item.pair == "EURUSD" and item.side == "BID")
        self.assertEqual(eurusd.status, "not_found")
        self.assertIsNone(eurusd.sha256)
        self.assertNotIn("1.50000", json.dumps([item.sha256 for item in records[0].source_files]))

    def test_undecodable_file_keeps_the_hash_and_deletes_the_payload(self) -> None:
        bodies = {url: (200, body) for url, body in _strength_bodies(CPI_DAY).items()}
        broken = DukascopySource().url_for(RawChunkKey("USDJPY", "ASK", CPI_DAY))
        bodies[broken] = (200, b"not-lzma")
        transport = _ScriptedTransport(bodies)
        when = _after_window(CPI_DAY)
        with tempfile.TemporaryDirectory() as tmp:
            transport_dir = Path(tmp) / "transport"
            records = observe_n1_transport_window(
                _cpi(),
                transport_directory=transport_dir,
                evidence_directory=Path(tmp) / "evidence",
                bls_status_verified_at_utc=when,
                now_utc=when,
                transport=transport,
            )
            self.assertFalse(any(path.suffix == ".bi5" for path in transport_dir.rglob("*")))
        broken_row = next(item for item in records[0].source_files if item.url == broken)
        self.assertEqual(broken_row.status, "decode_error")
        self.assertEqual(broken_row.sha256, hashlib.sha256(b"not-lzma").hexdigest())
        self.assertEqual(records[0].collection_limitation, "source_undecodable")

    def test_historical_store_and_other_dates_are_refused_before_download(self) -> None:
        transport = _ScriptedTransport({})
        when = _after_window(CPI_DAY)
        with tempfile.TemporaryDirectory() as tmp:
            blocked = Path(tmp) / "raw" / "dukascopy" / "v1"
            blocked.mkdir(parents=True)
            with self.assertRaises(ValueError):
                observe_n1_transport_window(
                    _cpi(),
                    transport_directory=blocked,
                    evidence_directory=Path(tmp) / "evidence",
                    bls_status_verified_at_utc=when,
                    now_utc=when,
                    transport=transport,
                )
            self.assertEqual(transport.calls, [])
            other = _release(date(2026, 11, 6), release_id="bls-empsit-2026-11-06", kind=ReleaseKind.EMPLOYMENT_SITUATION)
            with self.assertRaises(RuntimeError):
                observe_n1_transport_window(
                    other,
                    transport_directory=Path(tmp) / "transport",
                    evidence_directory=Path(tmp) / "evidence",
                    bls_status_verified_at_utc=when,
                    now_utc=when,
                    transport=transport,
                )
            self.assertEqual(transport.calls, [])

    def test_production_http_rejects_a_future_caller_clock(self) -> None:
        early = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)
        future = _after_window(CPI_DAY)
        client = _GuardedHttp()
        with patch("fmp.research.n1_dukascopy_transport._system_utc_now", return_value=early):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                with self.assertRaises(ValueError) as caught:
                    observe_n1_transport_window(
                        _cpi(),
                        transport_directory=root / "transport",
                        evidence_directory=root / "evidence",
                        bls_status_verified_at_utc=future,
                        now_utc=future,
                        transport=client,
                    )
                self.assertIn("not complete", str(caught.exception))
                self.assertEqual(client.calls, [])
                self.assertFalse((root / "evidence" / "n1-v0-pilot-evidence.jsonl").exists())
            with patch.object(UrllibTransport, "get", side_effect=AssertionError("socket")) as get:
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    with self.assertRaises(ValueError):
                        observe_n1_transport_window(
                            _cpi(),
                            transport_directory=root / "transport",
                            evidence_directory=root / "evidence",
                            bls_status_verified_at_utc=future,
                            now_utc=future,
                            transport=None,
                        )
                self.assertEqual(get.call_count, 0)

    def test_caller_clock_cannot_outrun_the_system_clock(self) -> None:
        system = _after_window(CPI_DAY)
        later = system + timedelta(minutes=5)
        client = _GuardedHttp()
        with patch("fmp.research.n1_dukascopy_transport._system_utc_now", return_value=system):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                with self.assertRaises(ValueError) as caught:
                    observe_n1_transport_window(
                        _cpi(),
                        transport_directory=root / "transport",
                        evidence_directory=root / "evidence",
                        bls_status_verified_at_utc=system,
                        now_utc=later,
                        transport=client,
                    )
                self.assertIn("system clock", str(caught.exception))
                self.assertEqual(client.calls, [])

    def test_system_clock_opens_production_http_when_the_caller_clock_is_early(self) -> None:
        system = _after_window(CPI_DAY)
        caller = _utc(CPI_DAY, 9, 30)
        verified = _utc(CPI_DAY, 8, 30)
        client = _GuardedHttp()
        with patch("fmp.research.n1_dukascopy_transport._system_utc_now", return_value=system):
            with tempfile.TemporaryDirectory() as tmp:
                records = observe_n1_transport_window(
                    _cpi(),
                    transport_directory=Path(tmp) / "transport",
                    evidence_directory=Path(tmp) / "evidence",
                    bls_status_verified_at_utc=verified,
                    now_utc=caller,
                    transport=client,
                )
        self.assertEqual(len(client.calls), 6)
        self.assertEqual(records[0].collection_limitation, "source_not_available")
        self.assertEqual(records[0].data_retrieved_at_utc, system.isoformat())

    def test_scripted_transport_keeps_a_deterministic_clock(self) -> None:
        early = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
        bodies = {url: (200, body) for url, body in _strength_bodies(EMPSIT_DAY).items()}
        transport = _ScriptedTransport(bodies)
        when = _after_window(EMPSIT_DAY)
        with patch("fmp.research.n1_dukascopy_transport._system_utc_now", return_value=early):
            with tempfile.TemporaryDirectory() as tmp:
                observe_n1_transport_window(
                    _empsit(),
                    transport_directory=Path(tmp) / "transport",
                    evidence_directory=Path(tmp) / "evidence",
                    bls_status_verified_at_utc=when,
                    now_utc=when,
                    transport=transport,
                )
        self.assertEqual(len(transport.calls), 6)

    def test_verification_timestamp_does_not_prove_publication(self) -> None:
        system = _after_window(CPI_DAY)
        client = _GuardedHttp()
        with patch("fmp.research.n1_dukascopy_transport._system_utc_now", return_value=system):
            with tempfile.TemporaryDirectory() as tmp:
                records = observe_n1_transport_window(
                    _cpi(status=ReleaseStatus.DELAYED, actual=None),
                    transport_directory=Path(tmp) / "transport",
                    evidence_directory=Path(tmp) / "evidence",
                    bls_status_verified_at_utc=system,
                    now_utc=system,
                    transport=client,
                )
        self.assertEqual(client.calls, [])
        self.assertEqual(records[0].collection_limitation, "publication_not_at_0830")
        self.assertFalse(records[0].qualifying_publication)

    def test_forged_provenance_seal_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            TransportProvenance(
                seal=object(),
                source_files=(),
                quote_input_sha256="abc",
                bls_status_verified_at_utc="2026-12-10T14:31:00+00:00",
                data_retrieved_at_utc="2026-12-10T14:31:00+00:00",
                collection_limitation="publication_not_at_0830",
                evidence_class=COLLECTION_LIMITATION_CLASS,
            )


if __name__ == "__main__":
    unittest.main()
