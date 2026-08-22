from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from fmp.data.acquire import AcquisitionError, AcquisitionResult, AcquisitionStatus
from fmp.data.cli import build_parser, process_fetch_plan
from fmp.data.types import RawChunkKey


class FailingMirror:
    def put_object(self, object_path: str, body: bytes) -> str:
        raise RuntimeError("simulated cloud mirror failure")


class ContinueAfterFailureTests(unittest.TestCase):
    def test_fetch_plan_can_continue_after_one_source_failure(self) -> None:
        keys = [
            RawChunkKey("EURUSD", "BID", date(2024, 1, 2)),
            RawChunkKey("EURUSD", "ASK", date(2024, 1, 2)),
            RawChunkKey("EURUSD", "BID", date(2024, 1, 3)),
        ]
        acquired: list[RawChunkKey] = []
        failures: list[tuple[RawChunkKey, str]] = []

        def fake_acquire(key: RawChunkKey, root: Path) -> AcquisitionResult:
            acquired.append(key)
            if key == keys[1]:
                raise AcquisitionError("simulated exhausted retries")
            return AcquisitionResult(key, AcquisitionStatus.COMPLETE, "x", 1, 1, 200)

        with tempfile.TemporaryDirectory() as tmp:
            results = process_fetch_plan(
                keys,
                Path(tmp),
                fake_acquire,
                continue_on_acquisition_error=True,
                on_acquisition_error=lambda key, exc: failures.append((key, str(exc))),
            )

        self.assertEqual(acquired, keys)
        self.assertEqual([result.key for result in results], [keys[0], keys[2]])
        self.assertEqual(failures, [(keys[1], "simulated exhausted retries")])

    def test_continue_mode_does_not_swallow_cloud_mirror_failure(self) -> None:
        key = RawChunkKey("EURUSD", "BID", date(2024, 1, 2))

        def fake_acquire(planned_key: RawChunkKey, root: Path) -> AcquisitionResult:
            raw = root / "raw" / planned_key.relative_raw_path
            manifest = root / "manifests" / planned_key.relative_manifest_path
            raw.parent.mkdir(parents=True, exist_ok=True)
            manifest.parent.mkdir(parents=True, exist_ok=True)
            raw.write_bytes(b"raw")
            manifest.write_bytes(b"manifest")
            return AcquisitionResult(planned_key, AcquisitionStatus.COMPLETE, "x", 1, 3, 200)

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "simulated cloud mirror failure"):
                process_fetch_plan(
                    [key],
                    Path(tmp),
                    fake_acquire,
                    FailingMirror(),
                    continue_on_acquisition_error=True,
                )

    def test_fetch_parser_accepts_continue_on_error_flag(self) -> None:
        args = build_parser().parse_args(
            [
                "fetch",
                "--pair",
                "EURUSD",
                "--start",
                "2024-01-01",
                "--end",
                "2024-01-02",
                "--continue-on-error",
            ]
        )
        self.assertTrue(args.continue_on_error)


if __name__ == "__main__":
    unittest.main()
