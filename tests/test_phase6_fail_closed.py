from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import polars as pl

from fmp.models.contracts import (
    PHASE5_CHECKPOINT_SHA,
    USDJPY_PROCESSED_MANIFEST_SHA256,
    ModelFamily,
)
from fmp.models.evaluation import GateResult
from tests.test_phase6_pipeline import _candidates, _financial, _labels, _model_frame


class Phase6FailClosedEvidenceTests(unittest.TestCase):
    def test_all_null_fit_input_is_durable_model_failure_not_process_failure(self) -> None:
        import fmp.models.evaluation as evaluation
        import fmp.models.fail_closed as fail_closed

        candidates_by_split = {
            name: _candidates(name) for name in ("fit", "selection", "validation")
        }

        def bars_loader(**kwargs):
            split = kwargs["split"]
            if split.name == "validation":
                self.fail("validation must remain unopened when every model fails fit preprocessing")
            return SimpleNamespace(
                bars=(split.name,),
                excluded_incomplete_count=0,
                eligible_utc_dates=(),
            )

        def feature_loader(**kwargs):
            split = kwargs["split"]
            if split.name == "validation":
                self.fail("validation features must remain unopened")
            return SimpleNamespace(
                frame=pl.DataFrame(
                    {
                        "available_at_utc": [
                            candidate.signal_known_timestamp_utc
                            for candidate in candidates_by_split[split.name]
                        ]
                    }
                ),
                feature_manifest_sha256=f"feature-{split.name}",
                processed_manifest_sha256=USDJPY_PROCESSED_MANIFEST_SHA256,
                phase5_checkpoint_sha=PHASE5_CHECKPOINT_SHA,
                phase5_code_commit="phase5",
                opened_artifacts=(),
            )

        def generate(_strategy_id, bars):
            return candidates_by_split[str(bars[0])]

        def join(candidates, _features):
            split_name = str(candidates[0].metadata["split"])
            frame = _model_frame(tuple(candidates), offset=0.0 if split_name == "fit" else 10.0)
            if split_name == "fit":
                frame = frame.with_columns(
                    pl.lit(None)
                    .cast(pl.Float64)
                    .alias("minutes_since_new_york_open")
                )
            return frame

        def label_batch(candidates, _bars):
            return _labels(tuple(candidates))

        def backtest(**kwargs):
            return _financial(
                tuple(kwargs["candidates"]), float(kwargs["slippage_pips"])
            )

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
                patch.object(
                    fail_closed, "run_candidate_backtest", side_effect=backtest
                ),
                patch.object(
                    evaluation,
                    "selection_gate",
                    return_value=GateResult(passed=True, criteria={"synthetic": True}),
                ),
            ):
                result = fail_closed.run_phase6_strategy_cell_or_failure(
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

            self.assertEqual(
                result["execution_status"], "FAIL_CLOSED_MODEL_FAILURE"
            )
            self.assertEqual(
                result["selection"]["selected_variant"], "NO_ML_CHALLENGER"
            )
            self.assertEqual(result["validation"]["status"], "NO_ML_CHALLENGER")
            self.assertFalse(result["validation"]["validation_loaded"])
            self.assertEqual(len(result["selection"]["variants"]), 6)
            for family in ModelFamily:
                model = result["selection"]["models"][family.value]
                self.assertEqual(
                    model["fit_status"]["status"], "PREPROCESSING_FAILED"
                )
                self.assertEqual(
                    model["fit_status"]["reason_code"], "ALL_NULL_FIT_COLUMN"
                )
                self.assertEqual(
                    model["fit_status"]["column"],
                    "minutes_since_new_york_open",
                )
                self.assertEqual(model["fit_status"]["fit_count"], 0)
                family_rows = [
                    row
                    for row in result["selection"]["variants"]
                    if row["model_family"] == family.value
                ]
                self.assertEqual(len(family_rows), 3)
                self.assertEqual(
                    {row["status"] for row in family_rows},
                    {"NOT_EVALUATED_MODEL_FIT_FAILED"},
                )

            fail_closed.write_phase6_fail_closed_artifacts(
                result, Path(tmp) / "artifact"
            )


if __name__ == "__main__":
    unittest.main()
