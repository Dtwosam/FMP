from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

import polars as pl

from fmp.research.data import LoadedResearchBars, load_processed_bars


SCHEMA_VERSION = "fmp-canonical-1m-v1"


def row(timestamp: datetime, *, complete: bool = True, symbol: str = "EURUSD") -> dict[str, object]:
    return {
        "timestamp_utc": timestamp,
        "symbol": symbol,
        "bid_open": 1.1000,
        "bid_high": 1.1010,
        "bid_low": 1.0990,
        "bid_close": 1.1004,
        "ask_open": 1.1002,
        "ask_high": 1.1012,
        "ask_low": 1.0992,
        "ask_close": 1.1006,
        "is_complete": complete,
    }


def write_fixture(
    root: Path,
    *,
    manifest_symbol: str = "EURUSD",
    december_rows: list[dict[str, object]] | None = None,
    january_rows: list[dict[str, object]] | None = None,
) -> Path:
    december_rows = december_rows if december_rows is not None else [
        row(datetime(2020, 12, 31, 0, 15, tzinfo=timezone.utc)),
        row(datetime(2020, 12, 31, 0, 0, tzinfo=timezone.utc)),
        row(datetime(2020, 12, 31, 0, 30, tzinfo=timezone.utc), complete=False),
    ]
    january_rows = january_rows if january_rows is not None else [
        row(datetime(2021, 1, 1, 0, 0, tzinfo=timezone.utc)),
    ]

    artifacts: dict[str, dict[str, object]] = {}
    for month, rows in (("2020-12", december_rows), ("2021-01", january_rows)):
        year, month_number = month.split("-")
        relative = Path("processed") / SCHEMA_VERSION / "15m" / "EURUSD" / year / f"{month_number}.parquet"
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        pl.DataFrame(rows).write_parquet(path)
        artifacts[f"15m:{month}"] = {"path": relative.as_posix()}

    manifest = {
        "manifest_version": 1,
        "symbol": manifest_symbol,
        "schema_version": SCHEMA_VERSION,
        "artifacts": artifacts,
    }
    manifest_path = root / "manifests" / "processed" / SCHEMA_VERSION / "EURUSD.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    return manifest_path


class Phase4ResearchDataTests(unittest.TestCase):
    def test_loads_only_complete_development_rows_sorted_with_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = write_fixture(root)
            loaded = load_processed_bars(
                dataset_root=root,
                manifest_path=manifest_path,
                symbol="EURUSD",
                timeframe="15m",
                split_name="development",
            )

            self.assertIsInstance(loaded, LoadedResearchBars)
            self.assertEqual(
                [bar.timestamp_utc for bar in loaded.bars],
                [
                    datetime(2020, 12, 31, 0, 0, tzinfo=timezone.utc),
                    datetime(2020, 12, 31, 0, 15, tzinfo=timezone.utc),
                ],
            )
            self.assertEqual(loaded.excluded_incomplete_count, 1)
            self.assertEqual(loaded.eligible_utc_dates, (date(2020, 12, 31),))

    def test_validation_split_excludes_development_month(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = write_fixture(root)
            loaded = load_processed_bars(
                dataset_root=root,
                manifest_path=manifest_path,
                symbol="EURUSD",
                timeframe="15m",
                split_name="validation",
            )
            self.assertEqual(len(loaded.bars), 1)
            self.assertEqual(loaded.bars[0].timestamp_utc, datetime(2021, 1, 1, tzinfo=timezone.utc))
            self.assertEqual(loaded.excluded_incomplete_count, 0)
            self.assertEqual(loaded.eligible_utc_dates, (date(2021, 1, 1),))

    def test_rejects_manifest_symbol_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = write_fixture(root, manifest_symbol="GBPUSD")
            with self.assertRaisesRegex(ValueError, "manifest symbol"):
                load_processed_bars(
                    dataset_root=root,
                    manifest_path=manifest_path,
                    symbol="EURUSD",
                    timeframe="15m",
                    split_name="development",
                )

    def test_rejects_duplicate_retained_timestamp_identity(self) -> None:
        duplicate_ts = datetime(2020, 12, 31, 0, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = write_fixture(
                root,
                december_rows=[row(duplicate_ts), row(duplicate_ts)],
            )
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_processed_bars(
                    dataset_root=root,
                    manifest_path=manifest_path,
                    symbol="EURUSD",
                    timeframe="15m",
                    split_name="development",
                )

    def test_rejects_unsupported_signal_timeframe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = write_fixture(root)
            with self.assertRaisesRegex(ValueError, "timeframe"):
                load_processed_bars(
                    dataset_root=root,
                    manifest_path=manifest_path,
                    symbol="EURUSD",
                    timeframe="1m",
                    split_name="development",
                )

    def test_normal_loader_cannot_access_final_test(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = write_fixture(root)
            with self.assertRaisesRegex(ValueError, "final test"):
                load_processed_bars(
                    dataset_root=root,
                    manifest_path=manifest_path,
                    symbol="EURUSD",
                    timeframe="15m",
                    split_name="final",
                )

    def test_rejects_wrong_processed_schema_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = write_fixture(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["schema_version"] = "wrong-schema"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "schema"):
                load_processed_bars(
                    dataset_root=root,
                    manifest_path=manifest_path,
                    symbol="EURUSD",
                    timeframe="15m",
                    split_name="development",
                )


if __name__ == "__main__":
    unittest.main()
