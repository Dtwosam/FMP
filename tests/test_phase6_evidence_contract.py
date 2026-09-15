from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import polars as pl

from fmp.models.contracts import FEATURE_SET_VERSION, ModelFamily
from fmp.models.data import MODEL_INPUT_COLUMNS
from fmp.models.evaluation import GateResult
from fmp.models.estimators import EXPERIMENT_SEED
from tests.test_phase6_pipeline import _candidates, _financial, _labels, _model_frame


_REQUIRED_DATASET_FIELDS = {
    "split",
    "candidate_row_count",
    "candidate_digest",
    "labeled_row_count",
    "labeled_digest",
    "unlabelable_counts_by_reason",
    "feature_row_count",
    "joined_row_count",
    "joined_digest",
    "input_columns",
    "label_prevalence",
    "feature_availability_range",
    "label_resolution_range",
    "opened_feature_artifacts",
    "opened_coverage_pre_2024",
}


def _feature_frame(candidates):
    return pl.DataFrame(
        {
            "bar_start_utc": [item.observation_bar_timestamp_utc for item in candidates],
            "available_at_utc": [item.signal_known_timestamp_utc for item in candidates],
        }
    )


class Phase6EvidenceContractTests(unittest.TestCase):
    def test_pipeline_and_writer_bind_complete_section17_evidence(self) -> None:
        import fmp.models.evaluation as evaluation
        from fmp.models.artifacts import write_phase6_artifacts

        candidates_by_split = {
            name: _candidates(name) for name in ("fit", "selection", "validation")
        }

        def bars_loader(**kwargs):
            split = kwargs["split"]
            return SimpleNamespace(
                bars=(split.name,),
                excluded_incomplete_count=0,
                eligible_utc_dates=(),
            )

        def feature_loader(**kwargs):
            split = kwargs["split"]
            year = {"fit": "2017", "selection": "2019", "validation": "2021"}[
                split.name
            ]
            return SimpleNamespace(
                frame=_feature_frame(candidates_by_split[split.name]),
                feature_manifest_sha256=f"feature-{split.name}",
                processed_manifest_sha256="processed",
                phase5_checkpoint_sha="checkpoint",
                phase5_code_commit="phase5",
                opened_artifacts=(
                    f"data/features/fmp-feature-v1/USDJPY/15m/{year}/01.parquet",
                ),
            )

        def generate(_strategy_id, bars):
            return candidates_by_split[str(bars[0])]

        def join(candidates, _features):
            split_name = str(candidates[0].metadata["split"])
            offset = {"fit": 0.0, "selection": 10.0, "validation": 20.0}[
                split_name
            ]
            return _model_frame(tuple(candidates), offset=offset)

        def label_batch(candidates, _bars):
            return _labels(tuple(candidates))

        def backtest(**kwargs):
            return _financial(
                tuple(kwargs["candidates"]), float(kwargs["slippage_pips"])
            )

        always_pass = GateResult(passed=True, criteria={"synthetic": True})

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            with (
                patch.object(
                    evaluation,
                    "load_processed_bars_for_split",
                    side_effect=bars_loader,
                ),
                patch.object(
                    evaluation,
                    "load_phase6_feature_frame",
                    side_effect=feature_loader,
                ),
                patch.object(
                    evaluation,
                    "generate_frozen_candidates",
                    side_effect=generate,
                ),
                patch.object(
                    evaluation,
                    "join_directional_candidates_to_features",
                    side_effect=join,
                ),
                patch.object(evaluation, "label_candidates", side_effect=label_batch),
                patch.object(
                    evaluation, "run_candidate_backtest", side_effect=backtest
                ),
                patch.object(evaluation, "selection_gate", return_value=always_pass),
                patch.object(evaluation, "validation_gate", return_value=always_pass),
            ):
                result = evaluation.run_phase6_strategy_cell(
                    dataset_root=Path("/synthetic/processed"),
                    processed_manifest_path=Path(
                        "/synthetic/processed-manifest.json"
                    ),
                    feature_root=Path("/synthetic/features"),
                    feature_manifest_path=Path("/synthetic/feature-manifest.json"),
                    strategy_id="session_breakout",
                    out_dir=out_dir,
                    code_commit="abc123",
                )

            selection = result["selection"]
            self.assertEqual(selection["feature_set_version"], FEATURE_SET_VERSION)
            self.assertEqual(
                selection["strategy"],
                {
                    "family": "session_breakout",
                    "symbol": "USDJPY",
                    "timeframe": "15m",
                    "parameters": {
                        "buffer_pips": 5,
                        "target_range_multiple": 1.5,
                    },
                },
            )

            datasets = selection["datasets"]
            self.assertEqual(set(datasets), {"fit", "selection"})
            for split_name in ("fit", "selection"):
                dataset = datasets[split_name]
                self.assertTrue(_REQUIRED_DATASET_FIELDS.issubset(dataset))
                self.assertEqual(dataset["candidate_row_count"], 40)
                self.assertEqual(dataset["labeled_row_count"], 40)
                self.assertEqual(dataset["feature_row_count"], 40)
                self.assertEqual(dataset["joined_row_count"], 40)
                self.assertEqual(dataset["input_columns"], list(MODEL_INPUT_COLUMNS))
                self.assertEqual(dataset["unlabelable_counts_by_reason"], {})
                self.assertEqual(dataset["label_prevalence"], 0.5)
                self.assertTrue(dataset["opened_coverage_pre_2024"])
                for digest_name in (
                    "candidate_digest",
                    "labeled_digest",
                    "joined_digest",
                ):
                    self.assertEqual(len(dataset[digest_name]), 64)

            for family in ModelFamily:
                model = selection["models"][family.value]
                self.assertEqual(model["random_seed"], EXPERIMENT_SEED)
                self.assertEqual(model["fit_row_count"], 40)
                self.assertEqual(model["fit_status"]["status"], "FIT_OK")
                self.assertEqual(
                    model["preprocessing"]["input_columns"],
                    list(MODEL_INPUT_COLUMNS),
                )
                self.assertEqual(set(model["transforms"]), {"fit", "selection"})
                for split_name in ("fit", "selection"):
                    transformed = model["transforms"][split_name]
                    self.assertEqual(transformed["row_count"], 40)
                    self.assertEqual(len(transformed["matrix_digest"]), 64)
                    self.assertEqual(
                        len(transformed["null_counts_before"]),
                        len(MODEL_INPUT_COLUMNS),
                    )
                    self.assertEqual(
                        transformed["null_counts_after"],
                        [0] * len(MODEL_INPUT_COLUMNS),
                    )

            validation = result["validation"]
            self.assertEqual(validation["status"], "PROMOTE_ML_FILTER")
            self.assertTrue(_REQUIRED_DATASET_FIELDS.issubset(validation["dataset"]))
            self.assertEqual(validation["dataset"]["candidate_row_count"], 40)
            self.assertEqual(validation["dataset"]["joined_row_count"], 40)
            self.assertEqual(validation["transformation"]["row_count"], 40)
            self.assertEqual(len(validation["transformation"]["matrix_digest"]), 64)
            self.assertEqual(validation["retention"]["candidate_count"], 40)
            self.assertGreater(validation["retention"]["retained_count"], 0)
            self.assertLessEqual(validation["retention"]["retained_count"], 40)
            self.assertGreater(validation["retention"]["retained_rate"], 0.0)
            self.assertLessEqual(validation["retention"]["retained_rate"], 1.0)

            artifact_dir = Path(tmp) / "artifact"
            write_phase6_artifacts(result, artifact_dir)

            incomplete = copy.deepcopy(result)
            del incomplete["selection"]["datasets"]["fit"]["candidate_digest"]
            with self.assertRaisesRegex(ValueError, "evidence|dataset|candidate"):
                write_phase6_artifacts(incomplete, Path(tmp) / "incomplete")


if __name__ == "__main__":
    unittest.main()
