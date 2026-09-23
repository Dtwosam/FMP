from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from fmp.data.phase2.artifacts import PHASE1_FROZEN_PLAN_SHA256, PHASE1_SOURCE_CHECKPOINT
from fmp.features.contracts import PROCESSED_SCHEMA_VERSION
from fmp.features.schema import FEATURE_COLUMNS, FEATURE_VALUE_COLUMNS
from fmp.market_learning.evidence import (
    EXPECTED_CELLS,
    EXPECTED_SOURCE_MANIFEST_SHA256,
    compile_feature_evidence,
)


CODE_COMMIT = "a" * 40


def _months() -> list[str]:
    out: list[str] = []
    year, month = 2015, 1
    while (year, month) <= (2026, 8):
        out.append(f"{year:04d}-{month:02d}")
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return out


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_cell(root: Path, *, symbol: str, timeframe: str) -> Path:
    cell_root = root / f"exp044-market-features-{symbol}-{timeframe}-{CODE_COMMIT}"
    artifacts: list[dict[str, object]] = []
    for month in _months():
        year, mon = month.split("-")
        relative = (
            Path("data")
            / "features"
            / "fmp-market-feature-v1"
            / symbol
            / timeframe
            / year
            / f"{mon}.parquet"
        )
        payload = f"{symbol}|{timeframe}|{month}".encode("utf-8")
        path = cell_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        artifacts.append(
            {
                "path": relative.as_posix(),
                "sha256": _sha(payload),
                "size_bytes": len(payload),
                "row_count": 1,
            }
        )

    manifest = {
        "manifest_version": 1,
        "experiment_id": "EXP-20260923-044",
        "feature_set_version": "fmp-market-feature-v1",
        "base_feature_definition_version": "fmp-feature-v1",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "model_training_authorized": False,
        "promotion_authorized": False,
        "historical_source": {
            "provider": "Dukascopy",
            "reuse_existing_accepted_history": True,
            "new_acquisition_performed": False,
            "phase1_checkpoint": PHASE1_SOURCE_CHECKPOINT,
            "phase1_frozen_plan_sha256": PHASE1_FROZEN_PLAN_SHA256,
            "phase2_schema_version": PROCESSED_SCHEMA_VERSION,
        },
        "code_commit": CODE_COMMIT,
        "processed_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256[symbol],
        "symbol": symbol,
        "timeframe": timeframe,
        "generation_parameters": {
            "requested_start": "2015-01-01",
            "requested_end_exclusive": "2026-08-21",
        },
        "opened_source_months": _months(),
        "output_start_utc": "2015-01-02T00:00:00Z",
        "output_end_utc": "2026-08-20T23:59:00Z",
        "row_count": len(artifacts),
        "unique_key_count": len(artifacts),
        "feature_columns": list(FEATURE_VALUE_COLUMNS),
        "schema_columns": list(FEATURE_COLUMNS),
        "schema_sha256": "b" * 64,
        "null_counts": {name: 0 for name in FEATURE_VALUE_COLUMNS},
        "writer": {
            "format": "parquet",
            "compression": "zstd",
            "compression_level": 3,
            "statistics": True,
        },
        "artifacts": artifacts,
    }
    manifest_path = cell_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _write_complete_root(root: Path) -> list[Path]:
    return [
        _write_cell(root, symbol=symbol, timeframe=timeframe)
        for symbol, timeframe in EXPECTED_CELLS
    ]


class MarketFeatureEvidenceTests(unittest.TestCase):
    def test_complete_nine_cell_evidence_binds_existing_dukascopy_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_complete_root(root)
            first = compile_feature_evidence(
                root=root,
                expected_code_commit=CODE_COMMIT,
            )
            second = compile_feature_evidence(
                root=root,
                expected_code_commit=CODE_COMMIT,
            )

            self.assertEqual(first, second)
            self.assertTrue(first["feature_evidence_complete"])
            self.assertEqual(first["verified_cell_count"], 9)
            self.assertEqual(first["expected_cell_count"], 9)
            self.assertFalse(first["model_fit_authorized"])
            self.assertFalse(first["shadow_authorized"])
            self.assertFalse(first["demo_order_authorized"])
            self.assertFalse(first["broker_mutation_authorized"])
            source = first["historical_source"]
            self.assertTrue(source["reuse_existing_accepted_history"])
            self.assertFalse(source["new_acquisition_performed"])
            self.assertEqual(source["provider"], "Dukascopy")
            self.assertEqual(len(first["evidence_fingerprint"]), 64)

    def test_missing_cell_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = _write_complete_root(root)
            cell_root = paths[-1].parent
            for path in sorted(cell_root.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            cell_root.rmdir()
            with self.assertRaisesRegex(ValueError, "exactly 9"):
                compile_feature_evidence(
                    root=root,
                    expected_code_commit=CODE_COMMIT,
                )

    def test_wrong_accepted_source_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = _write_complete_root(root)
            target = paths[0]
            manifest = json.loads(target.read_text(encoding="utf-8"))
            manifest["processed_manifest_sha256"] = "0" * 64
            target.write_text(
                json.dumps(manifest, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "processed manifest identity"):
                compile_feature_evidence(
                    root=root,
                    expected_code_commit=CODE_COMMIT,
                )

    def test_artifact_byte_tamper_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = _write_complete_root(root)
            manifest = json.loads(paths[0].read_text(encoding="utf-8"))
            artifact = paths[0].parent / manifest["artifacts"][0]["path"]
            artifact.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "size mismatch|checksum mismatch"):
                compile_feature_evidence(
                    root=root,
                    expected_code_commit=CODE_COMMIT,
                )


if __name__ == "__main__":
    unittest.main()
