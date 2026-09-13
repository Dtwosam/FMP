from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from fmp.data.phase2.artifacts import sha256_file
from fmp.data.phase2.full_history import RecordingCompleteRawChunkReader, materialize_pair
from fmp.data.types import RawChunkKey
from test_phase2_cloud_golden import FakeReader, canonical_frame


class FullHistoryOutputTests(unittest.TestCase):
    def test_two_month_materialization_writes_verified_outputs(self) -> None:
        def fake_normalize(reader: RecordingCompleteRawChunkReader, pair: str, day: date):
            reader.read(RawChunkKey(pair, "BID", day))
            reader.read(RawChunkKey(pair, "ASK", day))
            return canonical_frame(pair)

        with tempfile.TemporaryDirectory() as tmp, patch(
            "fmp.data.phase2.full_history_materialize.normalize_day", side_effect=fake_normalize
        ):
            root = Path(tmp)
            summary = materialize_pair(
                FakeReader(), root, "EURUSD",
                start=date(2024, 1, 31), end_exclusive=date(2024, 2, 2),
                code_commit="abc123", workers=2,
            )
            self.assertEqual(summary["month_count"], 2)
            self.assertEqual(summary["raw_read_count"], 4)
            self.assertEqual(summary["raw_read_counts"], {"ASK": 2, "BID": 2})
            self.assertEqual(summary["row_counts"]["1m"], 4)

            manifest_ref = summary["processed_manifest"]
            manifest_path = root / str(manifest_ref["path"])
            manifest = json.loads(manifest_path.read_text())
            expected = {f"{tf}:{month}" for tf in ("1m", "5m", "15m", "1h") for month in ("2024-01", "2024-02")}
            self.assertEqual(set(manifest["artifacts"]) - {"quality"}, expected)

            for key in ("raw_ledger", "quality", "processed_manifest"):
                ref = summary[key]
                path = root / str(ref["path"])
                self.assertTrue(path.is_file())
                self.assertEqual(ref["sha256"], sha256_file(path))
                self.assertEqual(ref["size_bytes"], path.stat().st_size)
            self.assertTrue((root / "summary.json").is_file())


if __name__ == "__main__":
    unittest.main()
