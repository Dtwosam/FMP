from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import polars as pl

from fmp.market_learning.features import (
    build_market_feature_frame,
    write_market_feature_artifacts,
)
from fmp.market_learning.materialize import (
    load_verified_feature_cell,
    load_verified_minute_quotes,
    materialize_market_outcome_cell,
    materialize_market_outcome_pair,
)
from fmp.market_learning.outcomes import OUTCOME_FEATURE_IDENTITY_COLUMNS
from tests.phase5_helpers import make_bars, write_dataset


UTC = timezone.utc
FEATURE_COMMIT = "e" * 40
OUTCOME_COMMIT = "f" * 40


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _minute_quotes(
    *,
    symbol: str,
    start: datetime,
    count: int,
) -> pl.DataFrame:
    pip_step = 0.00001 if symbol != "USDJPY" else 0.001
    base = 1.10 if symbol != "USDJPY" else 150.0
    spread = 0.0002 if symbol != "USDJPY" else 0.02
    rows: list[dict[str, object]] = []
    for i in range(count):
        ts = start + timedelta(minutes=i)
        bid = base + pip_step * i
        rows.append(
            {
                "timestamp_utc": ts,
                "symbol": symbol,
                "bid_open": bid,
                "ask_open": bid + spread,
                "schema_version": "fmp-canonical-1m-v1",
            }
        )
    return pl.DataFrame(rows)


def _fixture(root: Path) -> tuple[Path, Path, Path, dict[str, object]]:
    symbol = "EURUSD"
    timeframe = "5m"
    source_root = root / "phase2"
    feature_root = root / "features"

    derived = make_bars(
        symbol=symbol,
        timeframe=timeframe,
        start=datetime(2024, 1, 2, 10, 0, tzinfo=UTC),
        count=6,
    )
    features = build_market_feature_frame(
        derived,
        symbol=symbol,
        timeframe=timeframe,
        processed_manifest_sha256="0" * 64,
    )
    first_available = features["available_at_utc"][0]
    minute_frame = _minute_quotes(
        symbol=symbol,
        start=first_available,
        count=400,
    )
    processed_manifest = write_dataset(
        source_root,
        symbol=symbol,
        timeframe="1m",
        monthly_frames={"2024-01": minute_frame},
    )
    processed_sha = _sha256(processed_manifest)

    features = features.with_columns(
        pl.lit(processed_sha).alias("processed_manifest_sha256")
    )
    feature_manifest = write_market_feature_artifacts(
        features=features,
        output_root=feature_root,
        symbol=symbol,
        timeframe=timeframe,
        processed_manifest_sha256=processed_sha,
        code_commit=FEATURE_COMMIT,
        opened_months=("2024-01",),
        requested_start=date(2024, 1, 1),
        requested_end_exclusive=date(2024, 2, 1),
    )
    feature_manifest_path = feature_root / "manifest.json"
    feature_manifest_sha = _sha256(feature_manifest_path)

    evidence = {
        "code_commit": FEATURE_COMMIT,
        "evidence_fingerprint": "d" * 64,
        "cells": [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "manifest_sha256": feature_manifest_sha,
                "processed_manifest_sha256": processed_sha,
            }
        ],
    }
    assert feature_manifest["processed_manifest_sha256"] == processed_sha
    return feature_root, source_root, processed_manifest, evidence



def _pair_fixture(
    root: Path,
) -> tuple[dict[str, Path], Path, Path, dict[str, object]]:
    symbol = "EURUSD"
    source_root = root / "phase2"
    feature_base = root / "pair-features"
    timeframes = ("5m", "15m", "1h")

    feature_frames: dict[str, pl.DataFrame] = {}
    for timeframe in timeframes:
        derived = make_bars(
            symbol=symbol,
            timeframe=timeframe,
            start=datetime(2024, 1, 2, 10, 0, tzinfo=UTC),
            count=6,
        )
        feature_frames[timeframe] = build_market_feature_frame(
            derived,
            symbol=symbol,
            timeframe=timeframe,
            processed_manifest_sha256="0" * 64,
        )

    first_available = min(
        frame["available_at_utc"][0]
        for frame in feature_frames.values()
    )
    minute_frame = _minute_quotes(
        symbol=symbol,
        start=first_available,
        count=1600,
    )
    processed_manifest = write_dataset(
        source_root,
        symbol=symbol,
        timeframe="1m",
        monthly_frames={"2024-01": minute_frame},
    )
    processed_sha = _sha256(processed_manifest)

    feature_roots: dict[str, Path] = {}
    cells: list[dict[str, object]] = []
    for timeframe in timeframes:
        feature_root = feature_base / timeframe
        feature_roots[timeframe] = feature_root
        frame = feature_frames[timeframe].with_columns(
            pl.lit(processed_sha).alias("processed_manifest_sha256")
        )
        manifest = write_market_feature_artifacts(
            features=frame,
            output_root=feature_root,
            symbol=symbol,
            timeframe=timeframe,
            processed_manifest_sha256=processed_sha,
            code_commit=FEATURE_COMMIT,
            opened_months=("2024-01",),
            requested_start=date(2024, 1, 1),
            requested_end_exclusive=date(2024, 2, 1),
        )
        manifest_sha = _sha256(feature_root / "manifest.json")
        cells.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "manifest_sha256": manifest_sha,
                "processed_manifest_sha256": processed_sha,
            }
        )
        assert manifest["processed_manifest_sha256"] == processed_sha

    evidence = {
        "code_commit": FEATURE_COMMIT,
        "evidence_fingerprint": "d" * 64,
        "cells": cells,
    }
    return feature_roots, source_root, processed_manifest, evidence


class MarketOutcomeMaterializerTests(unittest.TestCase):
    def test_materializer_binds_feature_and_phase2_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_root, source_root, processed_manifest, evidence = _fixture(root)
            out = root / "out"
            manifest = materialize_market_outcome_cell(
                feature_root=feature_root,
                feature_evidence=evidence,
                dataset_root=source_root,
                processed_manifest_path=processed_manifest,
                symbol="EURUSD",
                timeframe="5m",
                output_root=out,
                code_commit=OUTCOME_COMMIT,
            )
            self.assertEqual(manifest["feature_evidence_fingerprint"], "d" * 64)
            self.assertEqual(
                manifest["processed_manifest_sha256"],
                evidence["cells"][0]["processed_manifest_sha256"],
            )
            self.assertGreater(manifest["labeled_rows"], 0)
            self.assertFalse(manifest["model_fit_authorized"])
            self.assertFalse(manifest["promotion_authorized"])
            self.assertTrue((out / "manifest.json").is_file())

    def test_feature_artifact_tamper_fails_before_outcome_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_root, source_root, processed_manifest, evidence = _fixture(root)
            manifest = json.loads(
                (feature_root / "manifest.json").read_text(encoding="utf-8")
            )
            artifact = feature_root / manifest["artifacts"][0]["path"]
            artifact.write_bytes(artifact.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "size mismatch|checksum mismatch"):
                materialize_market_outcome_cell(
                    feature_root=feature_root,
                    feature_evidence=evidence,
                    dataset_root=source_root,
                    processed_manifest_path=processed_manifest,
                    symbol="EURUSD",
                    timeframe="5m",
                    output_root=root / "out",
                    code_commit=OUTCOME_COMMIT,
                )

    def test_wrong_phase2_manifest_identity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_root, source_root, processed_manifest, evidence = _fixture(root)
            evidence["cells"][0]["processed_manifest_sha256"] = "1" * 64
            with self.assertRaisesRegex(
                ValueError,
                "Phase 2 identity|processed manifest sha256",
            ):
                materialize_market_outcome_cell(
                    feature_root=feature_root,
                    feature_evidence=evidence,
                    dataset_root=source_root,
                    processed_manifest_path=processed_manifest,
                    symbol="EURUSD",
                    timeframe="5m",
                    output_root=root / "out",
                    code_commit=OUTCOME_COMMIT,
                )


    def test_projected_feature_loader_retains_only_outcome_identity_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_root, _, _, evidence = _fixture(root)
            loaded = load_verified_feature_cell(
                feature_root=feature_root,
                feature_evidence=evidence,
                symbol="EURUSD",
                timeframe="5m",
                retain_columns=OUTCOME_FEATURE_IDENTITY_COLUMNS,
            )
            self.assertEqual(
                tuple(loaded.frame.columns),
                OUTCOME_FEATURE_IDENTITY_COLUMNS,
            )

    def test_pair_materializer_loads_quotes_once_and_matches_cell_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_roots, source_root, processed_manifest, evidence = _pair_fixture(root)

            with patch(
                "fmp.market_learning.materialize.load_verified_minute_quotes",
                wraps=load_verified_minute_quotes,
            ) as quote_loader:
                pair_manifests = materialize_market_outcome_pair(
                    feature_roots=feature_roots,
                    feature_evidence=evidence,
                    dataset_root=source_root,
                    processed_manifest_path=processed_manifest,
                    symbol="EURUSD",
                    output_root=root / "pair-out",
                    code_commit=OUTCOME_COMMIT,
                )
            self.assertEqual(quote_loader.call_count, 1)
            self.assertEqual(set(pair_manifests), {"5m", "15m", "1h"})

            for timeframe in ("5m", "15m", "1h"):
                separate = materialize_market_outcome_cell(
                    feature_root=feature_roots[timeframe],
                    feature_evidence=evidence,
                    dataset_root=source_root,
                    processed_manifest_path=processed_manifest,
                    symbol="EURUSD",
                    timeframe=timeframe,
                    output_root=root / "separate-out" / f"EURUSD-{timeframe}",
                    code_commit=OUTCOME_COMMIT,
                )
                self.assertEqual(pair_manifests[timeframe], separate)

    def test_pair_materializer_requires_exact_three_timeframes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_roots, source_root, processed_manifest, evidence = _pair_fixture(root)
            feature_roots.pop("1h")
            with self.assertRaisesRegex(ValueError, "exact 5m/15m/1h"):
                materialize_market_outcome_pair(
                    feature_roots=feature_roots,
                    feature_evidence=evidence,
                    dataset_root=source_root,
                    processed_manifest_path=processed_manifest,
                    symbol="EURUSD",
                    output_root=root / "pair-out",
                    code_commit=OUTCOME_COMMIT,
                )


if __name__ == "__main__":
    unittest.main()
