from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import polars as pl

from fmp.contracts import Direction
from fmp.features.schema import FEATURE_VALUE_COLUMNS
from fmp.models.contracts import (
    FIT_SPLIT,
    FROZEN_STRATEGIES,
    PHASE5_CHECKPOINT_SHA,
    USDJPY_PROCESSED_MANIFEST_SHA256,
)
from fmp.research.contracts import ResearchSplit
from fmp.strategies.contracts import SignalCandidate
from tests.phase6_helpers import (
    PHASE5_IMPLEMENTATION_SHA,
    feature_frame,
    feature_row,
    mutate_manifest,
    write_feature_fixture,
)


class Phase6DataTests(unittest.TestCase):
    def test_processed_split_rejects_2024_before_manifest_or_parquet(self) -> None:
        from fmp.research.data import load_processed_bars_for_split

        opened: list[Path] = []

        def reader(path: Path) -> pl.DataFrame:
            opened.append(path)
            raise AssertionError("Parquet reader must not be called")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing_manifest = root / "missing.json"
            bad = ResearchSplit("bad", date(2023, 12, 1), date(2024, 2, 1))
            with self.assertRaisesRegex(ValueError, "final-test|2024"):
                load_processed_bars_for_split(
                    dataset_root=root,
                    manifest_path=missing_manifest,
                    symbol="USDJPY",
                    timeframe="15m",
                    split=bad,
                    parquet_reader=reader,
                )
        self.assertEqual(opened, [])

    def test_feature_split_rejects_2024_before_manifest_or_parquet(self) -> None:
        from fmp.models.data import load_phase6_feature_frame

        opened: list[Path] = []

        def reader(path: Path) -> pl.DataFrame:
            opened.append(path)
            raise AssertionError("Parquet reader must not be called")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing_manifest = root / "missing.json"
            bad = ResearchSplit("bad", date(2023, 12, 1), date(2024, 2, 1))
            with self.assertRaisesRegex(ValueError, "final-test|2024"):
                load_phase6_feature_frame(
                    feature_root=root,
                    feature_manifest_path=missing_manifest,
                    strategy=FROZEN_STRATEGIES["session_breakout"],
                    split=bad,
                    parquet_reader=reader,
                )
        self.assertEqual(opened, [])

    def test_feature_reader_accepts_exact_phase5_identity_and_schema(self) -> None:
        from fmp.models.data import MODEL_INPUT_COLUMNS, load_phase6_feature_frame

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, expected = write_feature_fixture(root)
            loaded = load_phase6_feature_frame(
                feature_root=root,
                feature_manifest_path=manifest_path,
                strategy=FROZEN_STRATEGIES["session_breakout"],
                split=FIT_SPLIT,
            )

            self.assertEqual(loaded.frame.to_dicts(), expected.to_dicts())
            self.assertEqual(loaded.processed_manifest_sha256, USDJPY_PROCESSED_MANIFEST_SHA256)
            self.assertEqual(loaded.phase5_checkpoint_sha, PHASE5_CHECKPOINT_SHA)
            self.assertEqual(loaded.phase5_code_commit, PHASE5_IMPLEMENTATION_SHA)
            self.assertEqual(tuple(loaded.frame.columns)[7:], FEATURE_VALUE_COLUMNS)
            self.assertEqual(MODEL_INPUT_COLUMNS, FEATURE_VALUE_COLUMNS + ("signal_direction",))
            self.assertEqual(len(MODEL_INPUT_COLUMNS), 49)

    def test_feature_reader_rejects_wrong_identity_unsafe_path_and_bad_checksum(self) -> None:
        from fmp.models.data import load_phase6_feature_frame

        cases = (
            ("feature_set_version", "wrong-feature-version", "feature"),
            ("processed_manifest_sha256", "0" * 64, "processed"),
            ("code_commit", "0" * 40, "code|checkpoint|Phase 5"),
        )
        for key, value, pattern in cases:
            with self.subTest(key=key), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                manifest_path, _ = write_feature_fixture(root)
                mutate_manifest(manifest_path, **{key: value})
                with self.assertRaisesRegex(ValueError, pattern):
                    load_phase6_feature_frame(
                        feature_root=root,
                        feature_manifest_path=manifest_path,
                        strategy=FROZEN_STRATEGIES["session_breakout"],
                        split=FIT_SPLIT,
                    )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, _ = write_feature_fixture(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"][0]["path"] = "../escape.parquet"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "escape"):
                load_phase6_feature_frame(
                    feature_root=root,
                    feature_manifest_path=manifest_path,
                    strategy=FROZEN_STRATEGIES["session_breakout"],
                    split=FIT_SPLIT,
                )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, _ = write_feature_fixture(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"][0]["sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "checksum|sha"):
                load_phase6_feature_frame(
                    feature_root=root,
                    feature_manifest_path=manifest_path,
                    strategy=FROZEN_STRATEGIES["session_breakout"],
                    split=FIT_SPLIT,
                )

    def test_feature_reader_rejects_unsorted_or_duplicate_keys(self) -> None:
        from fmp.models.data import load_phase6_feature_frame

        t0 = datetime(2018, 1, 2, 10, 0, tzinfo=timezone.utc)
        t1 = t0 + timedelta(minutes=15)
        for name, frame, pattern in (
            ("unsorted", feature_frame((t1, t0)), "monotonic|sort"),
            (
                "duplicate",
                pl.DataFrame(
                    [
                        feature_row(t0, ordinal=0),
                        feature_row(t0, ordinal=1),
                    ]
                ).select(
                    [
                        "symbol",
                        "timeframe",
                        "bar_start_utc",
                        "bar_end_utc",
                        "available_at_utc",
                        "feature_set_version",
                        "processed_manifest_sha256",
                        *FEATURE_VALUE_COLUMNS,
                    ]
                ),
                "duplicate|unique",
            ),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                manifest_path, _ = write_feature_fixture(root, frame=frame)
                with self.assertRaisesRegex(ValueError, pattern):
                    load_phase6_feature_frame(
                        feature_root=root,
                        feature_manifest_path=manifest_path,
                        strategy=FROZEN_STRATEGIES["session_breakout"],
                        split=FIT_SPLIT,
                    )

    def test_join_uses_true_known_feature_row_and_exact_49_model_inputs(self) -> None:
        from fmp.models.data import (
            MODEL_INPUT_COLUMNS,
            join_directional_candidates_to_features,
            load_phase6_feature_frame,
        )

        t0 = datetime(2018, 1, 2, 10, 0, tzinfo=timezone.utc)
        t1 = t0 + timedelta(minutes=15)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, _ = write_feature_fixture(root, timestamps=(t0, t1))
            loaded = load_phase6_feature_frame(
                feature_root=root,
                feature_manifest_path=manifest_path,
                strategy=FROZEN_STRATEGIES["session_breakout"],
                split=FIT_SPLIT,
            )
            directional = SignalCandidate(
                candidate_id="C-LONG",
                symbol="USDJPY",
                observation_bar_timestamp_utc=t0,
                signal_known_timestamp_utc=t0 + timedelta(minutes=15),
                direction=Direction.LONG,
                stop_price=149.0,
                target_price=151.0,
                latest_exit_timestamp_utc=t0 + timedelta(hours=2),
                reason_code="BREAKOUT_LONG",
                metadata={},
            )
            no_trade = SignalCandidate(
                candidate_id="C-NO",
                symbol="USDJPY",
                observation_bar_timestamp_utc=t1,
                signal_known_timestamp_utc=t1 + timedelta(minutes=15),
                direction=Direction.NO_TRADE,
                stop_price=None,
                target_price=None,
                latest_exit_timestamp_utc=None,
                reason_code="NO_SETUP",
                metadata={},
            )
            joined = join_directional_candidates_to_features((directional, no_trade), loaded)

            self.assertEqual(joined.height, 1)
            self.assertEqual(joined["candidate_id"].to_list(), ["C-LONG"])
            self.assertEqual(joined["signal_direction"].to_list(), [1])
            self.assertEqual(tuple(joined.select(list(MODEL_INPUT_COLUMNS)).columns), MODEL_INPUT_COLUMNS)
            self.assertEqual(len(MODEL_INPUT_COLUMNS), 49)

    def test_join_fails_closed_on_missing_or_wrong_available_time(self) -> None:
        from fmp.models.data import (
            join_directional_candidates_to_features,
            load_phase6_feature_frame,
        )

        t0 = datetime(2018, 1, 2, 10, 0, tzinfo=timezone.utc)
        candidate = SignalCandidate(
            candidate_id="C-LONG",
            symbol="USDJPY",
            observation_bar_timestamp_utc=t0,
            signal_known_timestamp_utc=t0 + timedelta(minutes=15),
            direction=Direction.LONG,
            stop_price=149.0,
            target_price=151.0,
            latest_exit_timestamp_utc=t0 + timedelta(hours=2),
            reason_code="BREAKOUT_LONG",
            metadata={},
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, _ = write_feature_fixture(root, timestamps=(t0,))
            loaded = load_phase6_feature_frame(
                feature_root=root,
                feature_manifest_path=manifest_path,
                strategy=FROZEN_STRATEGIES["session_breakout"],
                split=FIT_SPLIT,
            )
            wrong = replace(
                loaded,
                frame=loaded.frame.with_columns(
                    (pl.col("available_at_utc") + timedelta(minutes=15)).alias("available_at_utc")
                ),
            )
            with self.assertRaisesRegex(ValueError, "available|known"):
                join_directional_candidates_to_features((candidate,), wrong)
            missing = replace(
                loaded,
                frame=loaded.frame.filter(pl.col("bar_start_utc") != t0),
            )
            with self.assertRaisesRegex(ValueError, "missing|feature"):
                join_directional_candidates_to_features((candidate,), missing)

    def test_future_feature_perturbation_does_not_change_earlier_join_rows(self) -> None:
        from fmp.models.data import (
            join_directional_candidates_to_features,
            load_phase6_feature_frame,
        )

        t0 = datetime(2018, 1, 2, 10, 0, tzinfo=timezone.utc)
        times = (t0, t0 + timedelta(minutes=15), t0 + timedelta(minutes=30))
        candidates = tuple(
            SignalCandidate(
                candidate_id=f"C-{index}",
                symbol="USDJPY",
                observation_bar_timestamp_utc=ts,
                signal_known_timestamp_utc=ts + timedelta(minutes=15),
                direction=Direction.LONG if index == 0 else Direction.SHORT,
                stop_price=149.0 if index == 0 else 151.0,
                target_price=151.0 if index == 0 else 149.0,
                latest_exit_timestamp_utc=ts + timedelta(hours=2),
                reason_code="SETUP",
                metadata={},
            )
            for index, ts in enumerate(times[:2])
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, _ = write_feature_fixture(root, timestamps=times)
            loaded = load_phase6_feature_frame(
                feature_root=root,
                feature_manifest_path=manifest_path,
                strategy=FROZEN_STRATEGIES["session_breakout"],
                split=FIT_SPLIT,
            )
            baseline = join_directional_candidates_to_features(candidates, loaded)
            future = loaded.frame.with_columns(
                pl.when(pl.col("bar_start_utc") > times[1])
                .then(pl.lit(999999.0))
                .otherwise(pl.col("return_1bar"))
                .alias("return_1bar")
            )
            perturbed = join_directional_candidates_to_features(
                candidates,
                replace(loaded, frame=future),
            )
            self.assertEqual(baseline.to_dicts(), perturbed.to_dicts())

    def test_frozen_candidate_generator_uses_exact_strategy_configs(self) -> None:
        from fmp.models.data import generate_frozen_candidates

        session_result = (object(),)
        with patch(
            "fmp.models.data.generate_session_breakout_candidates",
            return_value=session_result,
        ) as generate_session:
            self.assertIs(generate_frozen_candidates("session_breakout", ()), session_result)
            config = generate_session.call_args.kwargs["config"]
            self.assertEqual(config.timeframe, "15m")
            self.assertEqual(config.buffer_pips, 5)
            self.assertEqual(config.target_range_multiple, 1.5)

        volatility_result = (object(),)
        with patch(
            "fmp.models.data.generate_volatility_breakout_candidates",
            return_value=volatility_result,
        ) as generate_volatility:
            self.assertIs(generate_frozen_candidates("volatility_breakout", ()), volatility_result)
            config = generate_volatility.call_args.kwargs["config"]
            self.assertEqual(config.timeframe, "1h")
            self.assertEqual(config.range_multiplier, 2.0)
            self.assertEqual(FROZEN_STRATEGIES["volatility_breakout"].parameters["target_r"], 1.0)

        with self.assertRaisesRegex(ValueError, "strategy"):
            generate_frozen_candidates("other", ())


if __name__ == "__main__":
    unittest.main()
