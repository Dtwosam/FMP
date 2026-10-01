from __future__ import annotations

from pathlib import Path
from unittest.mock import patch
import unittest

import numpy as np
import polars as pl

from fmp.market_learning.model_protocol import ModelCell
from fmp.market_learning.model_successor_fit_temporal_residual_bound_utility_evaluation import (
    DEC186_TRAINING_CORE_BLOB_SHA,
    DEC187_ARTIFACT_CONTRACT_BLOB_SHA,
    DEC187_MERGED_COMMIT,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EVALUATION_CORE_DECISION,
    MODEL_FIT_AUTHORIZED,
    RESULT_EXECUTION_AUTHORIZED,
    _evaluate_residual_bound_cutoff,
    _score_residual_bound_consensus,
    run_fit_temporal_residual_bound_utility_model_cell_core,
    validate_fit_temporal_residual_bound_evaluation_sources,
)

ROOT = Path(__file__).resolve().parents[1]


class Exp054EvaluationCoreTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(self) -> None:
        report = validate_fit_temporal_residual_bound_evaluation_sources(
            repository_root=ROOT
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EVALUATION_CORE_DECISION,
            "DEC-188",
        )
        self.assertEqual(
            DEC187_MERGED_COMMIT,
            "1c56ec7241d5795791ac83f1b58ac875b74e9645",
        )
        self.assertEqual(
            report["dec186_training_core_blob_sha"],
            DEC186_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            report["dec187_artifact_contract_blob_sha"],
            DEC187_ARTIFACT_CONTRACT_BLOB_SHA,
        )
        self.assertFalse(RESULT_EXECUTION_AUTHORIZED)
        self.assertFalse(MODEL_FIT_AUTHORIZED)

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_bound_utility_evaluation."
        "_robust_residual_bound_utility"
    )
    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_bound_utility_evaluation."
        "_score_view_predictions"
    )
    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_bound_utility_evaluation."
        "_score_fit_temporal_feature_support_consensus"
    )
    def test_residual_bound_score_preserves_exp053_eligibility(
        self,
        score_predecessor,
        score_views,
        score_residual,
    ) -> None:
        directions = np.asarray(["LONG", "NO_TRADE", "SHORT"], dtype=object)
        row_ids = ("a", "b", "c")
        score_predecessor.return_value = (
            directions,
            np.asarray([1.0, 0.0, 0.8]),
            np.asarray([0.9, 0.0, 0.7]),
            np.asarray([0.8, 0.0, 0.6]),
            np.asarray([0.7, 0.0, 0.5]),
            {"consensus_eligible_row_count": 2},
            row_ids,
            "a" * 64,
        )
        score_views.return_value = (
            {},
            {
                "v1": {
                    "long_net_pips_0p5": "b" * 64,
                    "short_net_pips_0p5": "c" * 64,
                }
            },
        )
        score_residual.return_value = np.asarray([0.4, -np.inf, 0.2])
        frame = pl.DataFrame({"x": [1, 2, 3]})

        result = _score_residual_bound_consensus(
            fitted_models={},
            pooled_calibration_references={},
            support_references={},
            feature_references={},
            residual_references={},
            frame=frame,
            cell=ModelCell("EURUSD", "5m", 60),
        )
        self.assertEqual(result[0].tolist(), ["LONG", "NO_TRADE", "SHORT"])
        self.assertEqual(result[5].tolist(), [0.4, -np.inf, 0.2])
        self.assertEqual(
            result[6]["fit_temporal_residual_reference_count"],
            24,
        )
        self.assertEqual(
            result[6][
                "minimum_robust_fit_temporal_residual_bound_utility"
            ],
            0.2,
        )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_bound_utility_evaluation."
        "_base._financial_gate"
    )
    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_bound_utility_evaluation."
        "_base._financial_metrics"
    )
    def test_evaluation_applies_five_part_cutoff(
        self,
        financial_metrics,
        financial_gate,
    ) -> None:
        financial_metrics.return_value = {
            "directional_candidate_count": 1
        }
        financial_gate.return_value = {"passed": True}
        frame = pl.DataFrame({"x": [1, 2]})
        evaluated = _evaluate_residual_bound_cutoff(
            frame,
            directions=np.asarray(["LONG", "LONG"], dtype=object),
            raw_utility=np.asarray([1.0, 1.0]),
            pooled_calibrated_utility=np.asarray([0.9, 0.9]),
            fit_temporal_support=np.asarray([0.8, 0.8]),
            feature_support=np.asarray([0.7, 0.7]),
            residual_bound_utility=np.asarray([0.5, 0.4]),
            residual_bound_cutoff=0.5,
            feature_cutoff=0.7,
            utility_cutoff=0.8,
            pooled_cutoff=0.9,
            raw_cutoff=1.0,
            budget=250,
            scenarios=(0.5,),
            row_ids=("a", "b"),
        )
        self.assertEqual(
            evaluated["selection_derived_residual_bound_cutoff"],
            0.5,
        )
        candidates = financial_metrics.call_args.args[1]
        self.assertEqual(candidates.tolist(), ["LONG", "NO_TRADE"])

    def test_full_cell_runner_is_present_but_source_only(self) -> None:
        self.assertTrue(callable(run_fit_temporal_residual_bound_utility_model_cell_core))
        self.assertFalse(RESULT_EXECUTION_AUTHORIZED)
        self.assertFalse(MODEL_FIT_AUTHORIZED)

    def test_source_has_no_artifact_loading_dispatch_or_broker_path(self) -> None:
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_bound_utility_evaluation.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("load_authoritative_cell_artifacts", source)
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
