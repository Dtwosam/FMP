from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_fit_temporal_feature_support_utility_training import (
    DEC174_MERGED_COMMIT,
    DEC174_PROTOCOL_BLOB_SHA,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
    MODEL_FIT_AUTHORIZED,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    _candidate_directions_feature_support,
    _derive_feature_support_cutoff,
    _reference_distances,
    _survival_percentiles,
    validate_fit_temporal_feature_support_utility_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp053FitTemporalFeatureSupportTrainingTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(
        self,
    ) -> None:
        report = (
            validate_fit_temporal_feature_support_utility_training_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
            "DEC-175",
        )
        self.assertEqual(
            DEC174_MERGED_COMMIT,
            "9687eb8ea3920e87d6681adf7366a3ce0bba7154",
        )
        self.assertEqual(
            report["dec174_protocol_blob_sha"],
            DEC174_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC174_PROTOCOL_BLOB_SHA,
            "11ae3fc8e68687cc04957ed9243d8c5969227fb8",
        )
        self.assertEqual(
            report["predecessor_training_core_blob_sha"],
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "fe5664438752a161134bbed6f55d9985f1c1470a",
        )
        self.assertFalse(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(
            report[
                "fit_temporal_feature_support_utility_result_execution_authorized"
            ]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_survival_percentile_includes_ties(self) -> None:
        reference = np.asarray(
            [0.0, 1.0, 1.0, 3.0],
            dtype=np.float64,
        )
        scored = np.asarray(
            [0.0, 1.0, 2.0, 4.0],
            dtype=np.float64,
        )
        result = _survival_percentiles(
            reference,
            scored,
        )
        np.testing.assert_allclose(
            result,
            np.asarray(
                [1.0, 0.75, 0.25, 0.0],
                dtype=np.float64,
            ),
            rtol=0.0,
            atol=0.0,
        )

    def test_reference_distance_uses_positive_scale_only(
        self,
    ) -> None:
        transformed = np.asarray(
            [
                [0.0, 10.0, 2.0],
                [2.0, 10.0, 6.0],
            ],
            dtype=np.float64,
        )
        center = np.asarray(
            [1.0, 10.0, 4.0],
            dtype=np.float64,
        )
        scale = np.asarray(
            [1.0, 0.0, 2.0],
            dtype=np.float64,
        )
        active = np.asarray(
            [True, False, True],
            dtype=np.bool_,
        )
        distances = _reference_distances(
            transformed,
            center=center,
            scale=scale,
            active_mask=active,
        )
        np.testing.assert_allclose(
            distances,
            np.asarray([1.0, 1.0]),
            rtol=0.0,
            atol=0.0,
        )

        with self.assertRaisesRegex(
            ValueError,
            "zero active dimensions",
        ):
            _reference_distances(
                transformed,
                center=center,
                scale=scale,
                active_mask=np.asarray(
                    [False, False, False],
                    dtype=np.bool_,
                ),
            )

    def test_feature_support_cutoff_is_primary_and_lexicographic(
        self,
    ) -> None:
        row_count = 251
        directions = np.full(
            row_count,
            "LONG",
            dtype=object,
        )
        raw = np.full(
            row_count,
            10.0,
            dtype=np.float64,
        )
        pooled = np.full(
            row_count,
            0.80,
            dtype=np.float64,
        )
        utility = np.full(
            row_count,
            0.80,
            dtype=np.float64,
        )
        feature = np.full(
            row_count,
            1.0,
            dtype=np.float64,
        )

        # 248 unquestionably top-ranked rows, one cutoff row,
        # and two lower feature-support rows with stronger
        # secondary scores that must still rank below it.
        feature[248] = 0.85
        utility[248] = 0.60
        pooled[248] = 0.70
        raw[248] = 30.0

        feature[249] = 0.50
        utility[249] = 0.99
        pooled[249] = 0.99
        raw[249] = 50.0

        feature[250] = 0.40
        utility[250] = 1.00
        pooled[250] = 1.00
        raw[250] = 100.0

        row_ids = tuple(
            f"row-{index:03d}"
            for index in range(row_count)
        )
        record = _derive_feature_support_cutoff(
            directions=directions,
            raw_utility=raw,
            pooled_calibrated_utility=pooled,
            fit_temporal_support=utility,
            feature_support=feature,
            row_ids=row_ids,
            budget=250,
        )
        self.assertEqual(record["status"], "AVAILABLE")
        self.assertEqual(
            record[
                "selection_derived_feature_support_cutoff"
            ],
            0.50,
        )
        self.assertEqual(
            record[
                "selection_derived_support_cutoff"
            ],
            0.99,
        )
        self.assertEqual(
            record[
                "selection_derived_pooled_calibrated_cutoff"
            ],
            0.99,
        )
        self.assertEqual(
            record["selection_derived_raw_cutoff"],
            50.0,
        )
        self.assertEqual(
            record["selection_candidate_count_at_cutoff"],
            250,
        )

        candidates = _candidate_directions_feature_support(
            directions=directions,
            raw_utility=raw,
            pooled_calibrated_utility=pooled,
            fit_temporal_support=utility,
            feature_support=feature,
            feature_cutoff=0.50,
            utility_cutoff=0.99,
            pooled_cutoff=0.99,
            raw_cutoff=50.0,
        )
        self.assertEqual(
            int(np.count_nonzero(candidates != "NO_TRADE")),
            250,
        )
        self.assertEqual(candidates[248], "LONG")
        self.assertEqual(candidates[249], "LONG")
        self.assertEqual(candidates[250], "NO_TRADE")

    def test_exact_quadruple_tie_may_exceed_budget(
        self,
    ) -> None:
        row_count = 251
        directions = np.asarray(
            [
                "LONG" if index % 2 == 0 else "SHORT"
                for index in range(row_count)
            ],
            dtype=object,
        )
        raw = np.full(
            row_count,
            5.0,
            dtype=np.float64,
        )
        pooled = np.full(
            row_count,
            0.7,
            dtype=np.float64,
        )
        utility = np.full(
            row_count,
            0.8,
            dtype=np.float64,
        )
        feature = np.full(
            row_count,
            0.9,
            dtype=np.float64,
        )
        record = _derive_feature_support_cutoff(
            directions=directions,
            raw_utility=raw,
            pooled_calibrated_utility=pooled,
            fit_temporal_support=utility,
            feature_support=feature,
            row_ids=tuple(
                f"row-{index:03d}"
                for index in range(row_count)
            ),
            budget=250,
        )
        self.assertEqual(
            record["selection_candidate_count_at_cutoff"],
            251,
        )

    def test_source_has_no_artifact_loading_or_dispatch_path(
        self,
    ) -> None:
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_feature_support_utility_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("load_authoritative_cell_artifacts", source)
        self.assertNotIn("validate_authoritative_readiness", source)
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
