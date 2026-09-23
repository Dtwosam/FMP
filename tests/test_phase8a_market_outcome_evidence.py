from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from fmp.features.schema import FEATURE_COLUMNS
from fmp.market_learning.evidence import (
    EXPECTED_CELLS,
    EXPECTED_SOURCE_MANIFEST_SHA256,
)
from fmp.market_learning.outcome_evidence import (
    compile_outcome_evidence,
    load_outcome_evidence_index,
    write_outcome_evidence,
)
from fmp.market_learning.outcomes import (
    MARKET_OUTCOME_SET_VERSION,
    OUTCOME_COLUMNS,
)


CODE_COMMIT = "a" * 40
FEATURE_EVIDENCE_FINGERPRINT = "b" * 64


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_cell(root: Path, *, symbol: str, timeframe: str) -> Path:
    cell_root = root / f"outcomes-{symbol}-{timeframe}"
    relative = (
        Path("data")
        / "market-outcomes"
        / MARKET_OUTCOME_SET_VERSION
        / symbol
        / timeframe
        / "2024"
        / "01.parquet"
    )
    payload = f"{symbol}|{timeframe}|outcomes".encode("utf-8")
    artifact = cell_root / relative
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(payload)

    manifest = {
        "manifest_version": 1,
        "experiment_id": "EXP-20260923-044",
        "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
        "feature_set_version": "fmp-market-feature-v1",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "code_commit": CODE_COMMIT,
        "feature_manifest_sha256": "c" * 64,
        "feature_evidence_fingerprint": FEATURE_EVIDENCE_FINGERPRINT,
        "processed_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256[symbol],
        "symbol": symbol,
        "timeframe": timeframe,
        "horizons_minutes": [60, 240],
        "slippage_pips_per_fill": [0.2, 0.5, 1.0],
        "source_feature_rows": 10,
        "labeled_rows": 18,
        "labeled_rows_by_horizon": {"60": 9, "240": 9},
        "missing_entry_rows_by_horizon": {"60": 0, "240": 0},
        "missing_exit_rows_by_horizon": {"60": 1, "240": 1},
        "output_start_utc": "2024-01-02T00:00:00Z",
        "output_end_utc": "2024-01-31T23:00:00Z",
        "schema_columns": list(OUTCOME_COLUMNS),
        "schema_sha256": "d" * 64,
        "artifacts": [
            {
                "path": relative.as_posix(),
                "sha256": _sha(payload),
                "size_bytes": len(payload),
                "row_count": 18,
            }
        ],
    }
    manifest_path = cell_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _complete_root(root: Path) -> list[Path]:
    return [
        _write_cell(root, symbol=symbol, timeframe=timeframe)
        for symbol, timeframe in EXPECTED_CELLS
    ]


class MarketOutcomeEvidenceTests(unittest.TestCase):
    def test_complete_outcome_evidence_is_deterministic_and_non_promoting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _complete_root(root)
            first = compile_outcome_evidence(
                root=root,
                expected_code_commit=CODE_COMMIT,
                expected_feature_evidence_fingerprint=FEATURE_EVIDENCE_FINGERPRINT,
            )
            second = compile_outcome_evidence(
                root=root,
                expected_code_commit=CODE_COMMIT,
                expected_feature_evidence_fingerprint=FEATURE_EVIDENCE_FINGERPRINT,
            )
            self.assertEqual(first, second)
            self.assertTrue(first["outcome_evidence_complete"])
            self.assertEqual(first["verified_cell_count"], 9)
            self.assertFalse(first["model_fit_authorized"])
            self.assertFalse(first["shadow_authorized"])
            self.assertFalse(first["demo_order_authorized"])
            self.assertFalse(first["broker_mutation_authorized"])
            self.assertFalse(first["live_order_authorized"])
            self.assertFalse(first["real_money_authorized"])
            self.assertEqual(len(first["evidence_fingerprint"]), 64)

    def test_persisted_outcome_evidence_round_trip_and_tamper_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _complete_root(root)
            evidence = compile_outcome_evidence(
                root=root,
                expected_code_commit=CODE_COMMIT,
                expected_feature_evidence_fingerprint=FEATURE_EVIDENCE_FINGERPRINT,
            )
            path = root / "outcome-evidence.json"
            write_outcome_evidence(evidence=evidence, path=path)
            self.assertEqual(load_outcome_evidence_index(path), evidence)

            tampered = json.loads(path.read_text(encoding="utf-8"))
            tampered["verified_cell_count"] = 8
            path.write_text(
                json.dumps(tampered, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                load_outcome_evidence_index(path)

    def test_missing_cell_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = _complete_root(root)
            cell_root = paths[-1].parent
            for path in sorted(cell_root.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            cell_root.rmdir()
            with self.assertRaisesRegex(ValueError, "exactly 9"):
                compile_outcome_evidence(
                    root=root,
                    expected_code_commit=CODE_COMMIT,
                    expected_feature_evidence_fingerprint=FEATURE_EVIDENCE_FINGERPRINT,
                )

    def test_outcome_artifact_byte_tamper_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = _complete_root(root)
            manifest = json.loads(paths[0].read_text(encoding="utf-8"))
            artifact = paths[0].parent / manifest["artifacts"][0]["path"]
            artifact.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "size mismatch|checksum mismatch"):
                compile_outcome_evidence(
                    root=root,
                    expected_code_commit=CODE_COMMIT,
                    expected_feature_evidence_fingerprint=FEATURE_EVIDENCE_FINGERPRINT,
                )

    def test_feature_evidence_fingerprint_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _complete_root(root)
            with self.assertRaisesRegex(ValueError, "feature evidence fingerprint mismatch"):
                compile_outcome_evidence(
                    root=root,
                    expected_code_commit=CODE_COMMIT,
                    expected_feature_evidence_fingerprint="e" * 64,
                )


if __name__ == "__main__":
    unittest.main()
