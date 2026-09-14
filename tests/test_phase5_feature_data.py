from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

import polars as pl

from tests.phase5_helpers import make_bars, write_dataset


class Phase5FeatureDataTests(unittest.TestCase):
    def test_reader_loads_only_pre2024_selected_partitions(self) -> None:
        from fmp.features.data import load_feature_source

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_dataset(
                root,
                symbol="EURUSD",
                timeframe="1h",
                monthly_frames={
                    "2023-12": make_bars(start=datetime(2023, 12, 1, tzinfo=timezone.utc), count=24),
                    "2024-01": make_bars(start=datetime(2024, 1, 2, tzinfo=timezone.utc), count=24),
                },
            )
            opened: list[Path] = []

            def reader(path: Path) -> pl.DataFrame:
                opened.append(Path(path))
                return pl.read_parquet(path)

            loaded = load_feature_source(
                dataset_root=root,
                manifest_path=manifest,
                symbol="EURUSD",
                timeframe="1h",
                start=date(2023, 12, 1),
                end_exclusive=date(2024, 1, 1),
                parquet_reader=reader,
            )
            self.assertEqual(len(opened), 1)
            self.assertIn("2023/12.parquet", opened[0].as_posix())
            self.assertTrue(all(ts.year == 2023 for ts in loaded.frame["timestamp_utc"].to_list()))
            self.assertEqual(tuple(loaded.opened_months), ("2023-12",))
            self.assertEqual(len(loaded.processed_manifest_sha256), 64)

    def test_reader_rejects_final_period_before_any_parquet_open(self) -> None:
        from fmp.features.data import load_feature_source

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_dataset(
                root,
                symbol="EURUSD",
                timeframe="1h",
                monthly_frames={
                    "2023-12": make_bars(start=datetime(2023, 12, 1, tzinfo=timezone.utc), count=24),
                    "2024-01": make_bars(start=datetime(2024, 1, 2, tzinfo=timezone.utc), count=24),
                },
            )
            opened: list[Path] = []

            def reader(path: Path) -> pl.DataFrame:
                opened.append(Path(path))
                return pl.read_parquet(path)

            with self.assertRaisesRegex(ValueError, "final-test|2024"):
                load_feature_source(
                    dataset_root=root,
                    manifest_path=manifest,
                    symbol="EURUSD",
                    timeframe="1h",
                    start=date(2023, 12, 1),
                    end_exclusive=date(2024, 2, 1),
                    parquet_reader=reader,
                )
            self.assertEqual(opened, [])

    def test_reader_rejects_manifest_identity_and_path_escape(self) -> None:
        from fmp.features.data import load_feature_source

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_dataset(
                root,
                symbol="EURUSD",
                timeframe="1h",
                monthly_frames={"2023-01": make_bars(count=24)},
            )
            value = json.loads(manifest.read_text())
            value["artifacts"]["1h:2023-01"]["path"] = "../escape.parquet"
            manifest.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "escapes"):
                load_feature_source(
                    dataset_root=root,
                    manifest_path=manifest,
                    symbol="EURUSD",
                    timeframe="1h",
                    start=date(2023, 1, 1),
                    end_exclusive=date(2023, 2, 1),
                )

    def test_reader_rejects_unsupported_symbol_and_timeframe(self) -> None:
        from fmp.features.data import load_feature_source

        with self.assertRaises(ValueError):
            load_feature_source(
                dataset_root=Path("."), manifest_path=Path("x"), symbol="AUDUSD", timeframe="1h",
                start=date(2023, 1, 1), end_exclusive=date(2023, 2, 1),
            )
        with self.assertRaises(ValueError):
            load_feature_source(
                dataset_root=Path("."), manifest_path=Path("x"), symbol="EURUSD", timeframe="1m",
                start=date(2023, 1, 1), end_exclusive=date(2023, 2, 1),
            )


if __name__ == "__main__":
    unittest.main()
