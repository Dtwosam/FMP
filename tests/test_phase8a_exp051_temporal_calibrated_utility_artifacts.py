from __future__ import annotations

from pathlib import Path
from unittest.mock import patch
import unittest

from fmp.market_learning.model_protocol import MODEL_CELLS
from fmp.market_learning.model_successor_temporal_calibrated_utility_artifacts import (
    AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC151_MERGED_COMMIT,
    DEC151_TRAINING_CORE_BLOB_SHA,
    LEGACY_DATA_LOADER_BLOB_SHA,
    PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    _validate_consensus_block,
    _validate_fit_block,
    compile_temporal_calibrated_utility_model_result_evidence,
    run_authoritative_temporal_calibrated_utility_model_bundle,
    validate_temporal_calibrated_utility_artifact_runner_sources,
    validate_temporal_calibrated_utility_model_result_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
SHA = "a" * 64


def _target_summary(row_count: int) -> dict[str, object]:
    return {
        "row_count": row_count,
        "minimum_net_pips": -2.0,
        "maximum_net_pips": 3.0,
        "mean_net_pips": 0.25,
        "positive_count": row_count // 2,
        "negative_count": row_count - row_count // 2,
        "zero_count": 0,
    }


def _fit_block() -> dict[str, object]:
    views = {
        "leave_out_fit_2015_2016": (
            ["fit_2017_2018", "fit_2019_2020"],
            "fit_2015_2016",
        ),
        "leave_out_fit_2017_2018": (
            ["fit_2015_2016", "fit_2019_2020"],
            "fit_2017_2018",
        ),
        "leave_out_fit_2019_2020": (
            ["fit_2015_2016", "fit_2017_2018"],
            "fit_2019_2020",
        ),
    }
    models: dict[str, object] = {}
    references: dict[str, object] = {}
    for name, (included, excluded) in views.items():
        models[name] = {
            "status": "FITTED",
            "included_regimes": included,
            "excluded_regime": excluded,
            "row_count": 10,
            "regressor_count": 2,
            "regressors": {
                target: {
                    "status": "FITTED",
                    "fit_attempt_count": 1,
                    "target_summary": _target_summary(10),
                    "preprocessor_fingerprint": SHA,
                    "model_fingerprint": SHA,
                }
                for target in (
                    "long_net_pips_0p5",
                    "short_net_pips_0p5",
                )
            },
        }
        references[name] = {
            "status": "FROZEN",
            "included_regimes": included,
            "excluded_regime": excluded,
            "row_count": 5,
            "target_count": 2,
            "targets": {
                target: {
                    "status": "FROZEN",
                    "excluded_regime": excluded,
                    "row_count": 5,
                    "minimum_prediction": -1.0,
                    "maximum_prediction": 2.0,
                    "mean_prediction": 0.5,
                    "row_bound_prediction_digest": SHA,
                    "sorted_reference_digest": SHA,
                }
                for target in (
                    "long_net_pips_0p5",
                    "short_net_pips_0p5",
                )
            },
        }
    return {
        "jackknife_models": models,
        "jackknife_view_count": 3,
        "regressor_count": 6,
        "out_of_fit_calibration_references": references,
        "calibration_reference_count": 6,
        "calibration_reference_rule": "fixture",
        "calibrated_percentile_rule": "fixture",
        "robust_calibrated_score_rule": "fixture",
        "full_fit_single_model": {
            "status": "FORBIDDEN_BY_DEC150",
            "fit_attempt_count": 0,
        },
        "view_weight_search": {
            "status": "FORBIDDEN_BY_DEC150",
            "fit_attempt_count": 0,
        },
        "view_fallback": {
            "status": "FORBIDDEN_BY_DEC150",
            "fit_attempt_count": 0,
        },
        "selection_window_calibration": {
            "status": "FORBIDDEN_BY_DEC150",
            "fit_attempt_count": 0,
        },
        "hist_gradient_boosting_classifier": {
            "status": "EXCLUDED_BY_DEC150",
            "fit_attempt_count": 0,
        },
        "logistic_regression": {
            "status": "EXCLUDED_BY_DEC112_DEC150",
            "fit_attempt_count": 0,
        },
    }


def _consensus_block() -> dict[str, object]:
    views = (
        "leave_out_fit_2015_2016",
        "leave_out_fit_2017_2018",
        "leave_out_fit_2019_2020",
    )
    return {
        "row_count": 10,
        "consensus_direction_counts": {
            "LONG": 3,
            "SHORT": 2,
            "NO_TRADE": 5,
        },
        "consensus_eligible_row_count": 5,
        "consensus_eligible_rate": 0.5,
        "minimum_robust_raw_utility": 0.1,
        "maximum_robust_raw_utility": 2.0,
        "minimum_robust_calibrated_utility": 0.2,
        "maximum_robust_calibrated_utility": 0.9,
        "view_prediction_digests": {
            view: {
                "long_net_pips_0p5": SHA,
                "short_net_pips_0p5": SHA,
            }
            for view in views
        },
    }


class Exp051TemporalCalibratedUtilityArtifactTests(
    unittest.TestCase
):
    def test_source_binding_and_authorization_are_exact(
        self,
    ) -> None:
        report = (
            validate_temporal_calibrated_utility_artifact_runner_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            report["dec151_merged_commit"],
            DEC151_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC151_MERGED_COMMIT,
            "68028ef37b72e3f0695b475928434ede40ad7690",
        )
        self.assertEqual(
            report["dec151_training_core_blob_sha"],
            DEC151_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC151_TRAINING_CORE_BLOB_SHA,
            "959fbfd52f41c08de3c1a26769e0e7fd2545b92a",
        )
        self.assertEqual(
            report["legacy_data_loader_blob_sha"],
            LEGACY_DATA_LOADER_BLOB_SHA,
        )
        self.assertEqual(
            report["predecessor_artifact_helper_blob_sha"],
            PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA,
        )
        self.assertEqual(
            report[
                "temporal_calibrated_utility_model_artifact_runner_decision"
            ],
            TEMPORAL_CALIBRATED_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
        )
        self.assertEqual(
            TEMPORAL_CALIBRATED_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
            "DEC-152",
        )
        self.assertFalse(
            report[
                "authoritative_temporal_calibrated_utility_model_result_execution_authorized"
            ]
        )
        self.assertFalse(
            report[
                "temporal_calibrated_utility_model_fit_authorized"
            ]
        )

    def test_fit_block_requires_six_models_and_six_references(
        self,
    ) -> None:
        regressors, references = _validate_fit_block(
            _fit_block()
        )
        self.assertEqual(regressors, 6)
        self.assertEqual(references, 6)

        drifted = _fit_block()
        refs = drifted[
            "out_of_fit_calibration_references"
        ]
        assert isinstance(refs, dict)
        view = refs["leave_out_fit_2017_2018"]
        assert isinstance(view, dict)
        view["excluded_regime"] = "fit_2015_2016"
        with self.assertRaisesRegex(
            ValueError,
            "calibration excluded-regime mismatch",
        ):
            _validate_fit_block(drifted)

    def test_calibration_prediction_summary_fails_closed(
        self,
    ) -> None:
        drifted = _fit_block()
        refs = drifted[
            "out_of_fit_calibration_references"
        ]
        assert isinstance(refs, dict)
        view = refs["leave_out_fit_2015_2016"]
        assert isinstance(view, dict)
        targets = view["targets"]
        assert isinstance(targets, dict)
        target = targets["long_net_pips_0p5"]
        assert isinstance(target, dict)
        target["mean_prediction"] = 3.0

        with self.assertRaisesRegex(
            ValueError,
            "calibration mean outside bounds",
        ):
            _validate_fit_block(drifted)

    def test_consensus_requires_raw_and_calibrated_bounds(
        self,
    ) -> None:
        self.assertEqual(
            _validate_consensus_block(
                _consensus_block(),
                expected_row_count=10,
                field="fixture",
            ),
            5,
        )

        drifted = _consensus_block()
        drifted[
            "maximum_robust_calibrated_utility"
        ] = 1.1
        with self.assertRaisesRegex(
            ValueError,
            "calibrated maximum is invalid",
        ):
            _validate_consensus_block(
                drifted,
                expected_row_count=10,
                field="fixture",
            )

    @patch(
        "fmp.market_learning."
        "model_successor_temporal_calibrated_utility_artifacts."
        "_compile_summary"
    )
    def test_complete_evidence_is_canonical_and_revalidates(
        self,
        compile_summary,
    ) -> None:
        summary = {
            "verified_cell_count": 18,
            "selected_cell_count": 0,
            "no_temporal_calibrated_utility_stable_model_challenger_count": 18,
            "aggregate_selection_pass_variant_count": 0,
            "stable_selection_pass_variant_count": 0,
            "unavailable_budget_variant_count": 0,
            "utility_eligible_selection_row_count": 0,
            "verified_regressor_count": 108,
            "verified_calibration_reference_count": 108,
            "validation_pass_cell_count": 0,
            "holdout_pass_cell_count": 0,
        }
        compile_summary.return_value = summary
        cells = [
            {
                "cell": {
                    "symbol": cell.symbol,
                    "timeframe": cell.timeframe,
                    "horizon_minutes": cell.horizon_minutes,
                }
            }
            for cell in MODEL_CELLS
        ]
        commit = "b" * 40
        evidence = (
            compile_temporal_calibrated_utility_model_result_evidence(
                cells,
                code_commit=commit,
            )
        )
        self.assertEqual(evidence["cell_count"], 18)
        self.assertEqual(evidence["summary"], summary)
        self.assertEqual(
            len(evidence["evidence_fingerprint"]),
            64,
        )
        report = (
            validate_temporal_calibrated_utility_model_result_evidence(
                evidence,
                expected_code_commit=commit,
            )
        )
        self.assertTrue(
            report[
                "temporal_calibrated_utility_model_result_evidence_verified"
            ]
        )
        self.assertEqual(
            report["verified_regressor_count"],
            108,
        )
        self.assertEqual(
            report[
                "verified_calibration_reference_count"
            ],
            108,
        )

    @patch(
        "fmp.market_learning."
        "model_successor_temporal_calibrated_utility_artifacts."
        "validate_authoritative_readiness"
    )
    def test_authoritative_bundle_rejects_before_artifact_loading(
        self,
        validate_readiness,
    ) -> None:
        self.assertFalse(
            AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        with self.assertRaisesRegex(
            PermissionError,
            "DEC-152 source is non-executable",
        ):
            run_authoritative_temporal_calibrated_utility_model_bundle(
                repository_root=ROOT,
                readiness={},
                feature_roots={},
                outcome_roots={},
                code_commit="b" * 40,
            )
        validate_readiness.assert_not_called()

    def test_source_has_no_dispatch_or_broker_path(self) -> None:
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_temporal_calibrated_utility_artifacts.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
