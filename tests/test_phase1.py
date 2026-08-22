from __future__ import annotations

import hashlib
import json
import lzma
import struct
import tempfile
import unittest
from datetime import date
from pathlib import Path

from fmp.data.acquire import AcquisitionError, AcquisitionStatus, acquire_chunk
from fmp.data.dukascopy import DukascopySource, HttpResponse
from fmp.data.manifest import load_manifest
from fmp.data.types import RawChunkKey


def make_bi5(records: int = 3) -> bytes:
    payload = b"".join(
        struct.pack(">IIIIIf", idx * 60, 110000 + idx, 110010 + idx, 109990 + idx, 110020 + idx, 1.5)
        for idx in range(records)
    )
    return lzma.compress(payload)


class FakeTransport:
    def __init__(self, responses: list[HttpResponse]):
        self.responses = list(responses)
        self.calls: list[str] = []

    def get(self, url: str, timeout_seconds: float) -> HttpResponse:
        self.calls.append(url)
        if not self.responses:
            raise AssertionError("unexpected transport call")
        return self.responses.pop(0)


class Phase1Tests(unittest.TestCase):
    def test_source_url_uses_zero_based_month_and_side(self) -> None:
        source = DukascopySource()
        key = RawChunkKey("EURUSD", "ASK", date(2024, 1, 2))
        self.assertEqual(
            source.url_for(key),
            "https://datafeed.dukascopy.com/datafeed/EURUSD/2024/00/02/ASK_candles_min_1.bi5",
        )

    def test_relative_path_is_deterministic(self) -> None:
        key = RawChunkKey("USDJPY", "BID", date(2025, 12, 31))
        self.assertEqual(
            key.relative_raw_path.as_posix(),
            "dukascopy/v1/USDJPY/2025/11/31/BID_candles_min_1.bi5",
        )
        self.assertEqual(
            key.relative_manifest_path.as_posix(),
            "dukascopy/v1/USDJPY/2025/11/31/BID_candles_min_1.json",
        )

    def test_successful_chunk_is_atomic_and_manifested(self) -> None:
        body = make_bi5(4)
        transport = FakeTransport([HttpResponse(status=200, body=body)])
        key = RawChunkKey("EURUSD", "BID", date(2024, 1, 2))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = acquire_chunk(key, root, transport=transport)
            self.assertEqual(result.status, AcquisitionStatus.COMPLETE)
            raw_path = root / "raw" / key.relative_raw_path
            manifest_path = root / "manifests" / key.relative_manifest_path
            self.assertTrue(raw_path.is_file())
            self.assertTrue(manifest_path.is_file())
            self.assertFalse(list(raw_path.parent.glob("*.part-*")))
            self.assertEqual(hashlib.sha256(raw_path.read_bytes()).hexdigest(), result.sha256)
            manifest = load_manifest(manifest_path)
            self.assertEqual(manifest["records"], 4)
            self.assertEqual(manifest["sha256"], result.sha256)
            self.assertEqual(manifest["status"], "complete")
            self.assertEqual(manifest["side"], "BID")

    def test_resume_skips_verified_existing_chunk_without_network(self) -> None:
        body = make_bi5(2)
        key = RawChunkKey("GBPUSD", "ASK", date(2024, 2, 5))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = FakeTransport([HttpResponse(status=200, body=body)])
            acquire_chunk(key, root, transport=first)
            second = FakeTransport([])
            result = acquire_chunk(key, root, transport=second)
            self.assertEqual(result.status, AcquisitionStatus.ALREADY_VERIFIED)
            self.assertEqual(second.calls, [])

    def test_existing_raw_with_bad_checksum_fails_closed(self) -> None:
        body = make_bi5(2)
        key = RawChunkKey("EURUSD", "BID", date(2024, 2, 6))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            acquire_chunk(key, root, transport=FakeTransport([HttpResponse(status=200, body=body)]))
            raw_path = root / "raw" / key.relative_raw_path
            raw_path.write_bytes(b"tampered")
            with self.assertRaises(AcquisitionError):
                acquire_chunk(key, root, transport=FakeTransport([]))

    def test_partial_or_corrupt_lzma_response_is_rejected(self) -> None:
        key = RawChunkKey("EURUSD", "ASK", date(2024, 2, 7))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(AcquisitionError):
                acquire_chunk(key, root, transport=FakeTransport([HttpResponse(status=200, body=b"not-lzma")]))
            self.assertFalse((root / "raw" / key.relative_raw_path).exists())

    def test_404_is_recorded_as_not_found_without_raw_file(self) -> None:
        key = RawChunkKey("USDJPY", "BID", date(2024, 2, 10))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = acquire_chunk(key, root, transport=FakeTransport([HttpResponse(status=404, body=b"")]))
            self.assertEqual(result.status, AcquisitionStatus.NOT_FOUND)
            self.assertFalse((root / "raw" / key.relative_raw_path).exists())
            manifest_path = root / "manifests" / key.relative_manifest_path
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "not_found")
            self.assertEqual(manifest["http_status"], 404)

    def test_default_retry_budget_survives_three_transient_503s(self) -> None:
        body = make_bi5(2)
        key = RawChunkKey("USDJPY", "BID", date(2024, 3, 6))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transport = FakeTransport([
                HttpResponse(status=503, body=b""),
                HttpResponse(status=503, body=b""),
                HttpResponse(status=503, body=b""),
                HttpResponse(status=200, body=body),
            ])
            result = acquire_chunk(key, root, transport=transport, backoff_seconds=0)
            self.assertEqual(result.status, AcquisitionStatus.COMPLETE)
            self.assertEqual(len(transport.calls), 4)

    def test_not_found_can_be_explicitly_rechecked_and_completed(self) -> None:
        body = make_bi5(2)
        key = RawChunkKey("EURUSD", "ASK", date(2024, 3, 5))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = acquire_chunk(
                key, root, transport=FakeTransport([HttpResponse(status=404, body=b"")])
            )
            self.assertEqual(first.status, AcquisitionStatus.NOT_FOUND)
            second = acquire_chunk(
                key,
                root,
                transport=FakeTransport([HttpResponse(status=200, body=body)]),
                recheck_not_found=True,
            )
            self.assertEqual(second.status, AcquisitionStatus.COMPLETE)
            self.assertTrue((root / "raw" / key.relative_raw_path).is_file())
            manifest = load_manifest(root / "manifests" / key.relative_manifest_path)
            self.assertEqual(manifest["status"], "complete")

    def test_duplicate_retry_does_not_replace_good_file(self) -> None:
        body = make_bi5(2)
        key = RawChunkKey("USDJPY", "ASK", date(2024, 3, 4))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = acquire_chunk(key, root, transport=FakeTransport([HttpResponse(status=200, body=body)]))
            raw_path = root / "raw" / key.relative_raw_path
            original = raw_path.read_bytes()
            second = acquire_chunk(key, root, transport=FakeTransport([]))
            self.assertEqual(second.status, AcquisitionStatus.ALREADY_VERIFIED)
            self.assertEqual(raw_path.read_bytes(), original)
            self.assertEqual(first.sha256, second.sha256)

    def test_plan_all_pairs_and_sides_for_two_days(self) -> None:
        from fmp.data.cli import plan_keys

        keys = plan_keys(("EURUSD", "GBPUSD", "USDJPY"), date(2024, 1, 1), date(2024, 1, 3))
        self.assertEqual(len(keys), 12)
        self.assertEqual(keys[0], RawChunkKey("EURUSD", "BID", date(2024, 1, 1)))
        self.assertEqual(keys[-1], RawChunkKey("USDJPY", "ASK", date(2024, 1, 2)))

    def test_coverage_summary_counts_manifest_statuses(self) -> None:
        from fmp.data.coverage import build_coverage_report

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            keys = [
                RawChunkKey("EURUSD", "BID", date(2024, 1, 2)),
                RawChunkKey("EURUSD", "ASK", date(2024, 1, 2)),
                RawChunkKey("EURUSD", "BID", date(2024, 1, 6)),
            ]
            acquire_chunk(keys[0], root, transport=FakeTransport([HttpResponse(status=200, body=make_bi5(2))]))
            acquire_chunk(keys[1], root, transport=FakeTransport([HttpResponse(status=200, body=make_bi5(2))]))
            acquire_chunk(keys[2], root, transport=FakeTransport([HttpResponse(status=404, body=b"")]))
            report = build_coverage_report(root)
            self.assertEqual(report["totals"]["complete"], 2)
            self.assertEqual(report["totals"]["not_found"], 1)
            self.assertEqual(report["totals"]["manifests"], 3)
            self.assertEqual(report["pairs"]["EURUSD"]["complete"], 2)


if __name__ == "__main__":
    unittest.main()
