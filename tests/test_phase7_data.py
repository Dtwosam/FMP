from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch

import polars as pl

from tests.phase7_helpers import (
    manifest_sha256,
    month_timestamp,
    quote_row,
    refresh_artifact_record,
    write_manifest,
    write_phase7_fixture,
)


STAGE1_MONTHS = (
    "2023-11",
    "2023-12",
    "2024-01",
    "2024-02",
    "2024-03",
    "2024-04",
    "2024-05",
    "2024-06",
    "2024-07",
    "2024-08",
    "2024-09",
    "2024-10",
    "2024-11",
    "2024-12",
    "2025-01",
    "2026-08",
)
EXPECTED_STAGE1_KEYS = ("15m:2023-12",) + tuple(
    f"15m:2024-{month:02d}" for month in range(1, 13)
)


class Phase7DataTests(unittest.TestCase):
    def test_invalid_candidate_and_window_fail_before_manifest_or_parquet_io(self) -> None:
        from fmp.walkforward.data import load_phase7_bars

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing_manifest = root / "must-not-be-opened.json"
            opened: list[Path] = []

            def reader(path: Path) -> pl.DataFrame:
                opened.append(path)
                raise AssertionError("parquet reader must not be called")

            with self.assertRaisesRegex(ValueError, "candidate"):
                load_phase7_bars(
                    dataset_root=root,
                    manifest_path=missing_manifest,
                    candidate_id="other",
                    window_name="stage1-2024",
                    parquet_reader=reader,
                )
            with self.assertRaisesRegex(ValueError, "window"):
                load_phase7_bars(
                    dataset_root=root,
                    manifest_path=missing_manifest,
                    candidate_id="session_breakout",
                    window_name="custom-2024",
                    parquet_reader=reader,
                )
            self.assertEqual(opened, [])

    def test_tampered_warmup_and_endpoint_contracts_fail_before_io(self) -> None:
        from fmp.walkforward.contracts import Phase7Window
        from fmp.walkforward.data import load_phase7_bars

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing_manifest = root / "must-not-be-opened.json"
            opened: list[Path] = []

            def reader(path: Path) -> pl.DataFrame:
                opened.append(path)
                raise AssertionError("parquet reader must not be called")

            with patch("fmp.walkforward.data.MAX_WARMUP_DAYS", 8):
                with self.assertRaisesRegex(ValueError, "warm-up"):
                    load_phase7_bars(
                        dataset_root=root,
                        manifest_path=missing_manifest,
                        candidate_id="session_breakout",
                        window_name="stage1-2024",
                        parquet_reader=reader,
                    )

            tampered = Phase7Window("tampered", date(2026, 8, 1), date(2026, 9, 1))
            with patch("fmp.walkforward.data.allowed_phase7_window", return_value=tampered):
                with self.assertRaisesRegex(ValueError, "endpoint"):
                    load_phase7_bars(
                        dataset_root=root,
                        manifest_path=missing_manifest,
                        candidate_id="session_breakout",
                        window_name="stage1-2024",
                        parquet_reader=reader,
                    )
            self.assertEqual(opened, [])

    def test_stage1_opens_exact_warmup_and_2024_months_only(self) -> None:
        from fmp.walkforward.data import LoadedPhase7Bars, load_phase7_bars

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_phase7_fixture(
                root,
                candidate_id="session_breakout",
                months=STAGE1_MONTHS,
            )
            opened: list[Path] = []

            def reader(path: Path) -> pl.DataFrame:
                opened.append(path)
                return pl.read_parquet(path)

            with patch(
                "fmp.walkforward.data.USDJPY_PROCESSED_MANIFEST_SHA256",
                manifest_sha256(manifest),
            ):
                loaded = load_phase7_bars(
                    dataset_root=root,
                    manifest_path=manifest,
                    candidate_id="session_breakout",
                    window_name="stage1-2024",
                    parquet_reader=reader,
                )

            self.assertIsInstance(loaded, LoadedPhase7Bars)
            self.assertEqual(loaded.opened_partition_keys, EXPECTED_STAGE1_KEYS)
            self.assertEqual(len(opened), len(EXPECTED_STAGE1_KEYS))
            self.assertTrue(all("2025" not in key and "2026" not in key for key in loaded.opened_partition_keys))
            self.assertEqual(
                loaded.warmup_range,
                (
                    datetime(2023, 12, 25, tzinfo=timezone.utc),
                    datetime(2024, 1, 1, tzinfo=timezone.utc),
                ),
            )
            self.assertEqual(loaded.bars[0].timestamp_utc, month_timestamp("2023-12"))
            self.assertNotIn(loaded.bars[0], loaded.scored_bars)
            self.assertEqual(len(loaded.scored_bars), 12)
            self.assertEqual(
                loaded.eligible_scored_dates,
                tuple(date(2024, month, 28) for month in range(1, 13)),
            )

    def test_stage2_opens_only_named_window_plus_immediate_warmup(self) -> None:
        from fmp.walkforward.data import load_phase7_bars

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_phase7_fixture(
                root,
                candidate_id="volatility_breakout",
                months=("2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2026-01"),
            )
            opened: list[Path] = []

            def reader(path: Path) -> pl.DataFrame:
                opened.append(path)
                return pl.read_parquet(path)

            with patch(
                "fmp.walkforward.data.USDJPY_PROCESSED_MANIFEST_SHA256",
                manifest_sha256(manifest),
            ):
                loaded = load_phase7_bars(
                    dataset_root=root,
                    manifest_path=manifest,
                    candidate_id="volatility_breakout",
                    window_name="2025-Q2",
                    parquet_reader=reader,
                )

            self.assertEqual(
                loaded.opened_partition_keys,
                ("1h:2025-03", "1h:2025-04", "1h:2025-05", "1h:2025-06"),
            )
            self.assertEqual(len(opened), 4)
            self.assertEqual(
                loaded.warmup_range,
                (
                    datetime(2025, 3, 25, tzinfo=timezone.utc),
                    datetime(2025, 4, 1, tzinfo=timezone.utc),
                ),
            )
            self.assertEqual(len(loaded.bars), 4)
            self.assertEqual(len(loaded.scored_bars), 3)
            self.assertNotIn(date(2025, 3, 28), loaded.eligible_scored_dates)
            self.assertEqual(
                loaded.eligible_scored_dates,
                (date(2025, 4, 28), date(2025, 5, 28), date(2025, 6, 28)),
            )

    def test_wrong_manifest_sha_fails_before_parquet_open(self) -> None:
        from fmp.walkforward.data import load_phase7_bars

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_phase7_fixture(root, candidate_id="session_breakout", months=STAGE1_MONTHS)
            opened: list[Path] = []

            def reader(path: Path) -> pl.DataFrame:
                opened.append(path)
                return pl.read_parquet(path)

            with self.assertRaisesRegex(ValueError, "manifest sha"):
                load_phase7_bars(
                    dataset_root=root,
                    manifest_path=manifest,
                    candidate_id="session_breakout",
                    window_name="stage1-2024",
                    parquet_reader=reader,
                )
            self.assertEqual(opened, [])

    def test_wrong_schema_symbol_and_path_escape_fail_closed(self) -> None:
        from fmp.walkforward.data import load_phase7_bars

        cases = (("schema_version", "wrong-schema", "schema"), ("symbol", "EURUSD", "symbol"))
        for field, value, message in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                manifest_path = write_phase7_fixture(root, candidate_id="session_breakout", months=STAGE1_MONTHS)
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest[field] = value
                write_manifest(manifest_path, manifest)
                with patch(
                    "fmp.walkforward.data.USDJPY_PROCESSED_MANIFEST_SHA256",
                    manifest_sha256(manifest_path),
                ):
                    with self.assertRaisesRegex(ValueError, message):
                        load_phase7_bars(
                            dataset_root=root,
                            manifest_path=manifest_path,
                            candidate_id="session_breakout",
                            window_name="stage1-2024",
                        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = write_phase7_fixture(root, candidate_id="session_breakout", months=STAGE1_MONTHS)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"]["15m:2024-01"]["path"] = "../escape.parquet"
            write_manifest(manifest_path, manifest)
            with patch(
                "fmp.walkforward.data.USDJPY_PROCESSED_MANIFEST_SHA256",
                manifest_sha256(manifest_path),
            ):
                with self.assertRaisesRegex(ValueError, "escapes"):
                    load_phase7_bars(
                        dataset_root=root,
                        manifest_path=manifest_path,
                        candidate_id="session_breakout",
                        window_name="stage1-2024",
                    )

    def test_missing_columns_duplicate_identity_and_malformed_cadence_fail_closed(self) -> None:
        from fmp.walkforward.data import load_phase7_bars

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = quote_row(month_timestamp("2024-01"))
            bad.pop("ask_close")
            manifest = write_phase7_fixture(
                root,
                candidate_id="session_breakout",
                months=STAGE1_MONTHS,
                rows_by_month={"2024-01": (bad,)},
            )
            with patch("fmp.walkforward.data.USDJPY_PROCESSED_MANIFEST_SHA256", manifest_sha256(manifest)):
                with self.assertRaisesRegex(ValueError, "required columns"):
                    load_phase7_bars(
                        dataset_root=root,
                        manifest_path=manifest,
                        candidate_id="session_breakout",
                        window_name="stage1-2024",
                    )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            duplicate = quote_row(month_timestamp("2024-01"))
            manifest = write_phase7_fixture(
                root,
                candidate_id="session_breakout",
                months=STAGE1_MONTHS,
                rows_by_month={"2024-01": (duplicate, duplicate)},
            )
            with patch("fmp.walkforward.data.USDJPY_PROCESSED_MANIFEST_SHA256", manifest_sha256(manifest)):
                with self.assertRaisesRegex(ValueError, "duplicate"):
                    load_phase7_bars(
                        dataset_root=root,
                        manifest_path=manifest,
                        candidate_id="session_breakout",
                        window_name="stage1-2024",
                    )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            malformed = quote_row(month_timestamp("2024-01", minute=7))
            manifest = write_phase7_fixture(
                root,
                candidate_id="session_breakout",
                months=STAGE1_MONTHS,
                rows_by_month={"2024-01": (malformed,)},
            )
            with patch("fmp.walkforward.data.USDJPY_PROCESSED_MANIFEST_SHA256", manifest_sha256(manifest)):
                with self.assertRaisesRegex(ValueError, "cadence"):
                    load_phase7_bars(
                        dataset_root=root,
                        manifest_path=manifest,
                        candidate_id="session_breakout",
                        window_name="stage1-2024",
                    )


if __name__ == "__main__":
    unittest.main()
