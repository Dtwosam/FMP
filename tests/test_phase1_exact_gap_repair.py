from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch
from datetime import date
from pathlib import Path

from fmp.data.acquire import AcquisitionResult, AcquisitionStatus, acquire_chunk
from fmp.data.cli import build_parser
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
                    "audited_at_utc": "2026-09-09T10:00:00Z",
                    "present_manifests_at_audit": 25500 - len(chunks),
                    "missing_manifests_at_audit": len(chunks),
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

    def test_load_exact_gap_plan_rejects_unknown_root_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "exact-gaps.json"
            path.write_text(
                json.dumps(
                    {
                        "plan_version": 1,
                        "frozen_start_date": "2015-01-01",
                        "frozen_end_date_exclusive": "2026-08-21",
                        "audited_at_utc": "2026-09-09T10:00:00Z",
                        "present_manifests_at_audit": 25499,
                        "missing_manifests_at_audit": 1,
                        "chunks": [
                            {"pair": "EURUSD", "side": "BID", "date_utc": "2024-01-02"}
                        ],
                        "months": ["2024-01"],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "root"):
                load_exact_gap_plan(path)

    def test_load_exact_gap_plan_rejects_inconsistent_audit_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "exact-gaps.json"
            path.write_text(
                json.dumps(
                    {
                        "plan_version": 1,
                        "frozen_start_date": "2015-01-01",
                        "frozen_end_date_exclusive": "2026-08-21",
                        "audited_at_utc": "2026-09-09T10:00:00Z",
                        "present_manifests_at_audit": 25498,
                        "missing_manifests_at_audit": 1,
                        "chunks": [
                            {"pair": "EURUSD", "side": "BID", "date_utc": "2024-01-02"}
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "25,500"):
                load_exact_gap_plan(path)

    def test_load_exact_gap_plan_rejects_missing_count_that_differs_from_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "exact-gaps.json"
            path.write_text(
                json.dumps(
                    {
                        "plan_version": 1,
                        "frozen_start_date": "2015-01-01",
                        "frozen_end_date_exclusive": "2026-08-21",
                        "audited_at_utc": "2026-09-09T10:00:00Z",
                        "present_manifests_at_audit": 25499,
                        "missing_manifests_at_audit": 1,
                        "chunks": [
                            {"pair": "EURUSD", "side": "BID", "date_utc": "2024-01-02"},
                            {"pair": "GBPUSD", "side": "ASK", "date_utc": "2024-01-03"},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "chunk count"):
                load_exact_gap_plan(path)

    def test_load_exact_gap_plan_requires_timezone_aware_audit_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "exact-gaps.json"
            path.write_text(
                json.dumps(
                    {
                        "plan_version": 1,
                        "frozen_start_date": "2015-01-01",
                        "frozen_end_date_exclusive": "2026-08-21",
                        "audited_at_utc": "2026-09-09T10:00:00",
                        "present_manifests_at_audit": 25499,
                        "missing_manifests_at_audit": 1,
                        "chunks": [
                            {"pair": "EURUSD", "side": "BID", "date_utc": "2024-01-02"}
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "timezone"):
                load_exact_gap_plan(path)

    def test_load_exact_gap_plan_rejects_noncanonical_chunk_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_plan(
                root,
                [
                    {"pair": "EURUSD", "side": "BID", "date_utc": "2024-06-11"},
                    {"pair": "GBPUSD", "side": "ASK", "date_utc": "2019-05-03"},
                ],
            )

            with self.assertRaisesRegex(ValueError, "canonical"):
                load_exact_gap_plan(path)

    def test_load_exact_gap_plan_rejects_unknown_chunk_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_plan(
                root,
                [
                    {
                        "pair": "EURUSD",
                        "side": "ASK",
                        "date_utc": "2024-01-02",
                        "month": "2024-01",
                    }
                ],
            )

            with self.assertRaisesRegex(ValueError, "exactly"):
                load_exact_gap_plan(path)


class ExactGapCliTests(unittest.TestCase):
    def test_cli_exposes_fetch_plan_and_verify_plan_commands(self) -> None:
        parser = build_parser()

        fetch_args = parser.parse_args(
            [
                "fetch-plan",
                "--plan",
                "docs/phase1-exact-gap-queue.json",
                "--out",
                ".exact-gap",
                "--attempts",
                "8",
                "--source-delay",
                "5",
                "--continue-on-error",
            ]
        )
        self.assertEqual(fetch_args.command, "fetch-plan")
        self.assertEqual(fetch_args.plan, "docs/phase1-exact-gap-queue.json")
        self.assertTrue(fetch_args.continue_on_error)

        verify_args = parser.parse_args(
            [
                "verify-plan",
                "--plan",
                "docs/phase1-exact-gap-queue.json",
                "--out",
                ".exact-gap",
            ]
        )
        self.assertEqual(verify_args.command, "verify-plan")
        self.assertEqual(verify_args.plan, "docs/phase1-exact-gap-queue.json")


class ExactGapExecutionSafetyTests(unittest.TestCase):
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

    def test_fetch_plan_attempts_only_explicit_keys_in_plan_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = self._write_plan(
                root,
                [
                    {"pair": "GBPUSD", "side": "ASK", "date_utc": "2019-05-03"},
                    {"pair": "EURUSD", "side": "BID", "date_utc": "2024-06-11"},
                ],
            )
            expected = [
                RawChunkKey("GBPUSD", "ASK", date(2019, 5, 3)),
                RawChunkKey("EURUSD", "BID", date(2024, 6, 11)),
            ]
            observed: list[RawChunkKey] = []

            def fake_acquire(key: RawChunkKey, _root: Path, **_kwargs: object) -> AcquisitionResult:
                observed.append(key)
                return AcquisitionResult(
                    key=key,
                    status=AcquisitionStatus.NOT_FOUND,
                    sha256=None,
                    records=None,
                    compressed_size=None,
                    http_status=404,
                )

            args = build_parser().parse_args(
                [
                    "fetch-plan",
                    "--plan",
                    str(plan),
                    "--out",
                    str(root / "out"),
                ]
            )
            with patch("fmp.data.cli.acquire_chunk", side_effect=fake_acquire):
                with redirect_stdout(StringIO()):
                    code = args.func(args)

            self.assertEqual(code, 0)
            self.assertEqual(observed, expected)

    def test_invalid_plan_fails_before_any_acquisition_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = root / "invalid.json"
            plan.write_text(
                json.dumps(
                    {
                        "plan_version": 1,
                        "frozen_start_date": "2015-01-01",
                        "frozen_end_date_exclusive": "2026-08-21",
                        "chunks": [
                            {
                                "pair": "EURUSD",
                                "side": "BID",
                                "date_utc": "2026-08-21",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            args = build_parser().parse_args(
                [
                    "fetch-plan",
                    "--plan",
                    str(plan),
                    "--out",
                    str(root / "out"),
                ]
            )
            with patch("fmp.data.cli.acquire_chunk") as acquire:
                with self.assertRaises(ValueError):
                    args.func(args)

            acquire.assert_not_called()


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
