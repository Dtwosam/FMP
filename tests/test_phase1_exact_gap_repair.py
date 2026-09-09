from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from fmp.data.acquire import acquire_chunk
from fmp.data.coverage import verify_exact_keys
from fmp.data.dukascopy import HttpResponse
from fmp.data.repair_plan import load_exact_gap_plan
from fmp.data.types import RawChunkKey

from test_phase1 import FakeTransport, make_bi5


class ExactGapPlanTests(unittest.TestCase):
    def _write_plan(self, root: Path, chunks: list[dict[str, str]]) -> Path:
        path = root / "exact-gaps.json"
        path.write_text(
            json.dumps(
                {
                    "plan_version": 1,
                    "frozen_start_date": "2015-01-01",
                    "frozen_end_date_exclusive": "2026-08-21",
                    "chunks": chunks,
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_load_exact_gap_plan_preserves_explicit_chunk_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_plan(
                root,
                [
                    {"pair": "GBPUSD", "side": "ASK", "date_utc": "2019-05-03"},
                    {"pair": "EURUSD", "side": "BID", "date_utc": "2024-06-11"},
                ],
            )

            keys = load_exact_gap_plan(path)

            self.assertEqual(
                keys,
                [
                    RawChunkKey("GBPUSD", "ASK", date(2019, 5, 3)),
                    RawChunkKey("EURUSD", "BID", date(2024, 6, 11)),
                ],
            )

    def test_load_exact_gap_plan_rejects_duplicate_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_plan(
                root,
                [
                    {"pair": "USDJPY", "side": "BID", "date_utc": "2020-07-01"},
                    {"pair": "USDJPY", "side": "BID", "date_utc": "2020-07-01"},
                ],
            )

            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_exact_gap_plan(path)

    def test_load_exact_gap_plan_rejects_chunk_outside_frozen_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_plan(
                root,
                [{"pair": "EURUSD", "side": "ASK", "date_utc": "2026-08-21"}],
            )

            with self.assertRaisesRegex(ValueError, "frozen"):
                load_exact_gap_plan(path)


class ExactGapVerificationTests(unittest.TestCase):
    def test_verify_exact_keys_checks_only_explicit_plan(self) -> None:
        complete = RawChunkKey("EURUSD", "BID", date(2024, 1, 2))
        not_found = RawChunkKey("GBPUSD", "ASK", date(2024, 1, 6))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            acquire_chunk(
                complete,
                root,
                transport=FakeTransport([HttpResponse(status=200, body=make_bi5(2))]),
            )
            acquire_chunk(
                not_found,
                root,
                transport=FakeTransport([HttpResponse(status=404, body=b"")]),
            )

            report = verify_exact_keys(root, [complete, not_found])

            self.assertTrue(report["ready"])
            self.assertEqual(report["planned_chunks"], 2)
            self.assertEqual(report["complete"], 1)
            self.assertEqual(report["not_found"], 1)

    def test_verify_exact_keys_fails_closed_for_missing_planned_manifest(self) -> None:
        key = RawChunkKey("USDJPY", "ASK", date(2024, 2, 7))
        with tempfile.TemporaryDirectory() as tmp:
            report = verify_exact_keys(Path(tmp), [key])

            self.assertFalse(report["ready"])
            self.assertEqual(report["missing_manifest"], 1)


if __name__ == "__main__":
    unittest.main()
