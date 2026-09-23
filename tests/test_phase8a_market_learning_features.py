from __future__ import annotations

import json
import tempfile
import unittest
from unittest.mock import patch
from datetime import date, datetime, timezone
from pathlib import Path

from tests.phase5_helpers import make_bars, sha256, write_dataset



def _pair_fixture(root: Path) -> tuple[Path, Path]:
    source = root / "source"
    manifest = None
    all_artifacts: dict[str, dict[str, object]] = {}
    monthly_by_timeframe = {
        "5m": {
            "2025-03": make_bars(
                timeframe="5m",
                start=datetime(2025, 3, 3, tzinfo=timezone.utc),
                count=60,
            )
        },
        "15m": {
            "2025-03": make_bars(
                timeframe="15m",
                start=datetime(2025, 3, 3, tzinfo=timezone.utc),
                count=40,
            )
        },
        "1h": {
            "2025-03": make_bars(
                timeframe="1h",
                start=datetime(2025, 3, 3, tzinfo=timezone.utc),
                count=32,
            )
        },
    }
    for timeframe, monthly in monthly_by_timeframe.items():
        manifest = write_dataset(
            source,
            symbol="EURUSD",
            timeframe=timeframe,
            monthly_frames=monthly,
        )
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        all_artifacts.update(payload["artifacts"])
    assert manifest is not None
    manifest.write_text(
        json.dumps(
            {
                "manifest_version": 1,
                "symbol": "EURUSD",
                "schema_version": "fmp-canonical-1m-v1",
                "artifacts": all_artifacts,
            },
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return source, manifest


class MarketLearningFeatureTests(unittest.TestCase):
    def test_market_reader_can_open_2024_and_2026_without_weakening_phase5_lock(self) -> None:
        from fmp.features.contracts import validate_source_range
        from fmp.market_learning.features import load_market_feature_source

        with self.assertRaisesRegex(ValueError, "final-test|2024"):
            validate_source_range(date(2024, 1, 1), date(2024, 2, 1))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_dataset(
                root,
                symbol="EURUSD",
                timeframe="1h",
                monthly_frames={
                    "2024-01": make_bars(
                        timeframe="1h",
                        start=datetime(2024, 1, 2, tzinfo=timezone.utc),
                        count=24,
                    ),
                    "2026-08": make_bars(
                        timeframe="1h",
                        start=datetime(2026, 8, 20, tzinfo=timezone.utc),
                        count=12,
                    ),
                },
            )
            loaded = load_market_feature_source(
                dataset_root=root,
                manifest_path=manifest,
                symbol="EURUSD",
                timeframe="1h",
                start=date(2024, 1, 1),
                end_exclusive=date(2026, 8, 21),
            )
            self.assertEqual(loaded.opened_months, ("2024-01", "2026-08"))
            years = {ts.year for ts in loaded.frame["timestamp_utc"].to_list()}
            self.assertEqual(years, {2024, 2026})

    def test_market_reader_rejects_beyond_accepted_history_before_manifest_io(self) -> None:
        from fmp.market_learning.features import load_market_feature_source

        with self.assertRaisesRegex(ValueError, "2026-08-20|accepted"):
            load_market_feature_source(
                dataset_root=Path("."),
                manifest_path=Path("does-not-exist.json"),
                symbol="EURUSD",
                timeframe="1h",
                start=date(2026, 8, 1),
                end_exclusive=date(2026, 8, 22),
            )

    def test_market_feature_values_reuse_phase5_definitions_exactly(self) -> None:
        from fmp.features.engine import build_feature_frame
        from fmp.market_learning.contracts import MARKET_FEATURE_SET_VERSION
        from fmp.market_learning.features import build_market_feature_frame

        source = make_bars(
            timeframe="1h",
            start=datetime(2024, 1, 2, tzinfo=timezone.utc),
            count=40,
        )
        old = build_feature_frame(
            source,
            symbol="EURUSD",
            timeframe="1h",
            processed_manifest_sha256="a" * 64,
        )
        new = build_market_feature_frame(
            source,
            symbol="EURUSD",
            timeframe="1h",
            processed_manifest_sha256="a" * 64,
        )
        self.assertEqual(
            old.drop("feature_set_version").to_dicts(),
            new.drop("feature_set_version").to_dicts(),
        )
        self.assertEqual(
            set(new["feature_set_version"].to_list()),
            {MARKET_FEATURE_SET_VERSION},
        )

    def test_writer_uses_new_identity_and_retrospective_evidence_flags(self) -> None:
        from fmp.market_learning.contracts import MARKET_FEATURE_SET_VERSION
        from fmp.market_learning.features import (
            build_market_feature_frame,
            write_market_feature_artifacts,
        )

        features = build_market_feature_frame(
            make_bars(
                timeframe="1h",
                start=datetime(2024, 1, 2, tzinfo=timezone.utc),
                count=30,
            ),
            symbol="EURUSD",
            timeframe="1h",
            processed_manifest_sha256="a" * 64,
        )
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            kwargs = {
                "symbol": "EURUSD",
                "timeframe": "1h",
                "processed_manifest_sha256": "a" * 64,
                "code_commit": "deadbeef",
                "opened_months": ("2024-01",),
                "requested_start": date(2024, 1, 1),
                "requested_end_exclusive": date(2024, 2, 1),
            }
            left = write_market_feature_artifacts(
                features=features, output_root=Path(tmp1), **kwargs
            )
            right = write_market_feature_artifacts(
                features=features, output_root=Path(tmp2), **kwargs
            )
            self.assertEqual(left, right)
            self.assertEqual(left["feature_set_version"], MARKET_FEATURE_SET_VERSION)
            self.assertEqual(left["base_feature_definition_version"], "fmp-feature-v1")
            self.assertEqual(left["evidence_label"], "RETROSPECTIVE_ALREADY_SEEN")
            self.assertFalse(left["untouched_oos"])
            self.assertFalse(left["model_training_authorized"])
            self.assertFalse(left["promotion_authorized"])
            source = left["historical_source"]
            self.assertEqual(source["provider"], "Dukascopy")
            self.assertTrue(source["reuse_existing_accepted_history"])
            self.assertFalse(source["new_acquisition_performed"])
            self.assertEqual(source["phase1_checkpoint"], "fmp-v1-phase1-source-of-truth")
            self.assertEqual(
                source["phase1_frozen_plan_sha256"],
                "2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6",
            )
            rel = left["artifacts"][0]["path"]
            self.assertIn(f"data/features/{MARKET_FEATURE_SET_VERSION}/", rel)
            self.assertEqual(sha256(Path(tmp1) / rel), sha256(Path(tmp2) / rel))

    def test_generation_integration_writes_post2024_versioned_features(self) -> None:
        from fmp.market_learning.features import run_market_feature_generation

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            manifest = write_dataset(
                root,
                symbol="USDJPY",
                timeframe="15m",
                monthly_frames={
                    "2025-03": make_bars(
                        symbol="USDJPY",
                        timeframe="15m",
                        start=datetime(2025, 3, 3, tzinfo=timezone.utc),
                        count=48,
                    )
                },
            )
            out = Path(tmp) / "out"
            result = run_market_feature_generation(
                dataset_root=root,
                manifest_path=manifest,
                symbol="USDJPY",
                timeframe="15m",
                start=date(2025, 3, 1),
                end_exclusive=date(2025, 4, 1),
                output_root=out,
                code_commit="abc123",
            )
            self.assertEqual(result["symbol"], "USDJPY")
            self.assertEqual(result["timeframe"], "15m")
            self.assertEqual(result["opened_source_months"], ["2025-03"])
            self.assertTrue((out / "manifest.json").is_file())
            self.assertEqual(
                json.loads((out / "manifest.json").read_text(encoding="utf-8")),
                result,
            )

    def test_pair_feature_generation_loads_each_timeframe_once(self) -> None:
        from fmp.market_learning.features import (
            load_market_feature_source,
            materialize_market_feature_pair,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, manifest = _pair_fixture(root)
            with patch(
                "fmp.market_learning.features.load_market_feature_source",
                wraps=load_market_feature_source,
            ) as loader:
                result = materialize_market_feature_pair(
                    dataset_root=source,
                    manifest_path=manifest,
                    symbol="EURUSD",
                    start=date(2025, 3, 1),
                    end_exclusive=date(2025, 4, 1),
                    primary_root=root / "primary",
                    verification_root=root / "verification",
                    code_commit="a" * 40,
                )
            self.assertEqual(loader.call_count, 3)
            self.assertEqual(set(result["primary"]), {"5m", "15m", "1h"})
            self.assertEqual(result["primary"], result["verification"])

    def test_pair_feature_generation_matches_single_cell_outputs(self) -> None:
        from fmp.market_learning.features import (
            materialize_market_feature_pair,
            run_market_feature_generation,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, manifest = _pair_fixture(root)
            pair = materialize_market_feature_pair(
                dataset_root=source,
                manifest_path=manifest,
                symbol="EURUSD",
                start=date(2025, 3, 1),
                end_exclusive=date(2025, 4, 1),
                primary_root=root / "primary",
                verification_root=root / "verification",
                code_commit="b" * 40,
            )

            for timeframe in ("5m", "15m", "1h"):
                single_root = root / "single" / f"EURUSD-{timeframe}"
                single = run_market_feature_generation(
                    dataset_root=source,
                    manifest_path=manifest,
                    symbol="EURUSD",
                    timeframe=timeframe,
                    start=date(2025, 3, 1),
                    end_exclusive=date(2025, 4, 1),
                    output_root=single_root,
                    code_commit="b" * 40,
                )
                self.assertEqual(pair["primary"][timeframe], single)

                pair_root = root / "primary" / f"EURUSD-{timeframe}"
                for artifact in single["artifacts"]:
                    rel = artifact["path"]
                    self.assertEqual(
                        (pair_root / rel).read_bytes(),
                        (single_root / rel).read_bytes(),
                    )
                self.assertEqual(
                    (pair_root / "manifest.json").read_bytes(),
                    (single_root / "manifest.json").read_bytes(),
                )

    def test_range_contract_rejects_invalid_requests(self) -> None:
        from fmp.market_learning.features import validate_market_feature_range

        with self.assertRaisesRegex(ValueError, "non-empty"):
            validate_market_feature_range(date(2025, 1, 1), date(2025, 1, 1))
        with self.assertRaisesRegex(ValueError, "2015"):
            validate_market_feature_range(date(2014, 12, 1), date(2015, 2, 1))
        with self.assertRaisesRegex(ValueError, "accepted"):
            validate_market_feature_range(date(2026, 8, 1), date(2026, 9, 1))


if __name__ == "__main__":
    unittest.main()
