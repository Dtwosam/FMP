from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_fit_temporal_residual_bound_utility_training import (
    DEC185_MERGED_COMMIT,
    DEC185_PROTOCOL_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION,
    MODEL_FIT_AUTHORIZED,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    _derive_residual_bound_cutoff,
    _downside_residual,
    _passes_residual_bound_cutoff,
    validate_fit_temporal_residual_bound_utility_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp054FitTemporalResidualBoundTrainingTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(
        self,
    ) -> None:
        report = (
            validate_fit_temporal_residual_bound_utility_training_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION,
            "DEC-186",
        )
        self.assertEqual(
            DEC185_MERGED_COMMIT,
            "3578491ab24b3fa6209ea674e02e1bce5dd99895",
        )
        self.assertEqual(
            report["dec185_protocol_blob_sha"],
            DEC185_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC185_PROTOCOL_BLOB_SHA,
            "3ffac844f9ed5308512dc3313e850cc84fb6d144",
        )
        self.assertEqual(
            report["predecessor_training_core_blob_sha"],
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "4fd0e48302f97e188a8124e1543bde0ffdb43b6f",
        )
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(
            report[
                "fit_temporal_residual_bound_utility_result_execution_authorized"
            ]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_downside_residual_uses_exact_lower_quartile_index(
        self,
    ) -> None:
        index, value = _downside_residual(
            np.asarray(
                [-5.0, -2.0, 1.0, 4.0, 9.0],
                dtype=np.float64,
            )
        )
        self.assertEqual(index, 1)
        self.assertEqual(value, -2.0)

        index4, value4 = _downside_residual(
            np.asarray(
                [-8.0, -3.0, 2.0, 7.0],
                dtype=np.float64,
            )
        )
        self.assertEqual(index4, 0)
        self.assertEqual(value4, -8.0)

    def test_downside_residual_rejects_bad_references(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "reference is invalid",
        ):
            _downside_residual(
                np.asarray([], dtype=np.float64)
            )
        with self.assertRaisesRegex(
            ValueError,
            "reference must be sorted",
        ):
            _downside_residual(
                np.asarray(
                    [0.0, -1.0, 2.0],
                    dtype=np.float64,
                )
            )

    def test_residual_bound_is_primary_cutoff_component(self) -> None:
        self.assertTrue(
            _passes_residual_bound_cutoff(
                residual_bound=0.51,
                feature_support=0.0,
                utility_support=0.0,
                pooled=0.0,
                raw=0.1,
                residual_cutoff=0.50,
                feature_cutoff=0.99,
                utility_cutoff=0.99,
                pooled_cutoff=0.99,
                raw_cutoff=99.0,
            )
        )
        self.assertFalse(
            _passes_residual_bound_cutoff(
                residual_bound=0.49,
                feature_support=1.0,
                utility_support=1.0,
                pooled=1.0,
                raw=999.0,
                residual_cutoff=0.50,
                feature_cutoff=0.0,
                utility_cutoff=0.0,
                pooled_cutoff=0.0,
                raw_cutoff=0.1,
            )
        )
        self.assertTrue(
            _passes_residual_bound_cutoff(
                residual_bound=0.50,
                feature_support=0.80,
                utility_support=0.70,
                pooled=0.60,
                raw=5.0,
                residual_cutoff=0.50,
                feature_cutoff=0.80,
                utility_cutoff=0.70,
                pooled_cutoff=0.60,
                raw_cutoff=5.0,
            )
        )

    def test_budget250_cutoff_is_residual_bound_first(self) -> None:
        count = 250
        directions = np.asarray(
            ["LONG"] * count,
            dtype=object,
        )
        residual = np.linspace(
            1000.0,
            751.0,
            num=count,
            dtype=np.float64,
        )
        feature = np.linspace(
            0.01,
            0.99,
            num=count,
            dtype=np.float64,
        )
        utility = np.linspace(
            0.99,
            0.01,
            num=count,
            dtype=np.float64,
        )
        pooled = np.linspace(
            0.25,
            0.75,
            num=count,
            dtype=np.float64,
        )
        raw = np.linspace(
            1.0,
            2.0,
            num=count,
            dtype=np.float64,
        )
        row_ids = tuple(
            f"row-{index:03d}"
            for index in range(count)
        )

        record = _derive_residual_bound_cutoff(
            directions=directions,
            raw_utility=raw,
            pooled_calibrated_utility=pooled,
            fit_temporal_support=utility,
            feature_support=feature,
            residual_bound=residual,
            row_ids=row_ids,
            budget=250,
        )
        self.assertEqual(record["status"], "AVAILABLE")
        self.assertEqual(
            record["selection_candidate_count_at_cutoff"],
            250,
        )
        self.assertAlmostEqual(
            record["selection_derived_residual_bound_cutoff"],
            751.0,
        )

    def test_source_has_no_artifact_loading_or_dispatch_path(
        self,
    ) -> None:
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_bound_utility_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("load_authoritative_cell_artifacts", source)
        self.assertNotIn("validate_authoritative_readiness", source)
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
