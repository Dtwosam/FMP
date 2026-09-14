from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

import polars as pl

from tests.phase5_helpers import make_bars, sha256, write_dataset


class Phase5FeatureArtifactTests(unittest.TestCase):
    def test_writer_uses_frozen_layout_and_deterministic_manifest(self) -> None:
        from fmp.features.artifacts import write_feature_artifacts
        from fmp.features.engine import build_feature_frame

        features = build_feature_frame(
            make_bars(timeframe="1h", start=datetime(2023, 1, 1, tzinfo=timezone.utc), count=30),
            symbol="EURUSD", timeframe="1h", processed_manifest_sha256="a" * 64,
        )
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            kwargs = {
                "symbol": "EURUSD",
                "timeframe": "1h",
                "processed_manifest_sha256": "a" * 64,
                "code_commit": "deadbeef",
                "opened_months": ("2023-01",),
                "requested_start": date(2023, 1, 1),
                "requested_end_exclusive": date(2023, 2, 1),
            }
            m1 = write_feature_artifacts(features=features, output_root=Path(tmp1), **kwargs)
            m2 = write_feature_artifacts(features=features, output_root=Path(tmp2), **kwargs)
            self.assertEqual(m1, m2)
            self.assertEqual(m1["feature_set_version"], "fmp-feature-v1")
            self.assertEqual(m1["code_commit"], "deadbeef")
            self.assertEqual(m1["processed_manifest_sha256"], "a" * 64)
            self.assertEqual(m1["opened_source_months"], ["2023-01"])
            self.assertEqual(
                m1["generation_parameters"],
                {
                    "requested_start": "2023-01-01",
                    "requested_end_exclusive": "2023-02-01",
                },
            )
            self.assertEqual(m1["row_count"], features.height)
            self.assertEqual(m1["unique_key_count"], features.height)
            self.assertEqual(len(m1["schema_sha256"]), 64)
            self.assertIn("null_counts", m1)
            self.assertEqual(len(m1["artifacts"]), 1)
            rel = m1["artifacts"][0]["path"]
            self.assertEqual(rel, "data/features/fmp-feature-v1/EURUSD/1h/2023/01.parquet")
            p1 = Path(tmp1) / rel
            p2 = Path(tmp2) / rel
            self.assertEqual(sha256(p1), sha256(p2))

    def test_writer_rejects_2024_rows(self) -> None:
        from fmp.features.artifacts import write_feature_artifacts
        from fmp.features.engine import build_feature_frame

        features = build_feature_frame(
            make_bars(timeframe="1h", start=datetime(2024, 1, 2, tzinfo=timezone.utc), count=2),
            symbol="EURUSD", timeframe="1h", processed_manifest_sha256="a" * 64,
        )
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "final-test|2024"):
                write_feature_artifacts(
                    features=features, output_root=Path(tmp), symbol="EURUSD", timeframe="1h",
                    processed_manifest_sha256="a" * 64, code_commit="deadbeef", opened_months=("2024-01",),
                    requested_start=date(2023, 12, 1), requested_end_exclusive=date(2024, 1, 1),
                )

    def test_writer_rejects_processed_manifest_identity_mismatch(self) -> None:
        from fmp.features.artifacts import write_feature_artifacts
        from fmp.features.engine import build_feature_frame

        features = build_feature_frame(
            make_bars(timeframe="1h", start=datetime(2023, 1, 1, tzinfo=timezone.utc), count=2),
            symbol="EURUSD", timeframe="1h", processed_manifest_sha256="a" * 64,
        ).with_columns(pl.lit("b" * 64).alias("processed_manifest_sha256"))
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "processed.*manifest.*identity|identity.*mismatch"):
                write_feature_artifacts(
                    features=features, output_root=Path(tmp), symbol="EURUSD", timeframe="1h",
                    processed_manifest_sha256="a" * 64, code_commit="deadbeef", opened_months=("2023-01",),
                    requested_start=date(2023, 1, 1), requested_end_exclusive=date(2023, 2, 1),
                )

    def test_generation_cli_integration_stays_pre2024_and_records_source_identity(self) -> None:
        from fmp.features.cli import run_feature_generation

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            manifest = write_dataset(
                root, symbol="EURUSD", timeframe="1h",
                monthly_frames={"2023-01": make_bars(timeframe="1h", count=30)},
            )
            out = Path(tmp) / "out"
            result = run_feature_generation(
                dataset_root=root, manifest_path=manifest, symbol="EURUSD", timeframe="1h",
                start=date(2023, 1, 1), end_exclusive=date(2023, 2, 1),
                output_root=out, code_commit="abc123",
            )
            self.assertEqual(result["symbol"], "EURUSD")
            self.assertEqual(result["timeframe"], "1h")
            self.assertEqual(result["code_commit"], "abc123")
            self.assertEqual(result["opened_source_months"], ["2023-01"])
            self.assertEqual(
                result["generation_parameters"],
                {
                    "requested_start": "2023-01-01",
                    "requested_end_exclusive": "2023-02-01",
                },
            )
            self.assertTrue((out / "manifest.json").is_file())
            loaded = json.loads((out / "manifest.json").read_text())
            self.assertEqual(loaded, result)

    def test_cli_rejects_final_period_before_reader(self) -> None:
        from fmp.features.cli import validate_generation_request

        with self.assertRaisesRegex(ValueError, "final-test|2024"):
            validate_generation_request(
                symbol="EURUSD", timeframe="1h",
                start=date(2023, 1, 1), end_exclusive=date(2024, 2, 1),
            )


if __name__ == "__main__":
    unittest.main()
