from __future__ import annotations

from pathlib import Path
from unittest.mock import patch
import unittest

from fmp.market_learning.model_protocol import MODEL_CELLS
from fmp.market_learning.model_successor_fit_temporal_feature_support_utility_artifacts import (
    AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC175_MERGED_COMMIT,
    DEC175_TRAINING_CORE_BLOB_SHA,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    _validate_consensus_block,
    _validate_feature_references,
    compile_fit_temporal_feature_support_utility_model_result_evidence,
    run_authoritative_fit_temporal_feature_support_utility_model_bundle,
    validate_fit_temporal_feature_support_utility_artifact_runner_sources,
    validate_fit_temporal_feature_support_utility_model_result_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
SHA = "a" * 64


def _feature_refs() -> dict[str, object]:
    views = {
        "leave_out_fit_2015_2016": (
            ["fit_2017_2018", "fit_2019_2020"],
            "fit_2015_2016",
            (
                ("fit_2015_h1", "2015-01-01", "2015-07-01"),
                ("fit_2015_h2", "2015-07-01", "2016-01-01"),
                ("fit_2016_h1", "2016-01-01", "2016-07-01"),
                ("fit_2016_h2", "2016-07-01", "2017-01-01"),
            ),
        ),
        "leave_out_fit_2017_2018": (
            ["fit_2015_2016", "fit_2019_2020"],
            "fit_2017_2018",
            (
                ("fit_2017_h1", "2017-01-01", "2017-07-01"),
                ("fit_2017_h2", "2017-07-01", "2018-01-01"),
                ("fit_2018_h1", "2018-01-01", "2018-07-01"),
                ("fit_2018_h2", "2018-07-01", "2019-01-01"),
            ),
        ),
        "leave_out_fit_2019_2020": (
            ["fit_2015_2016", "fit_2017_2018"],
            "fit_2019_2020",
            (
                ("fit_2019_h1", "2019-01-01", "2019-07-01"),
                ("fit_2019_h2", "2019-07-01", "2020-01-01"),
                ("fit_2020_h1", "2020-01-01", "2020-07-01"),
                ("fit_2020_h2", "2020-07-01", "2021-01-01"),
            ),
        ),
    }
    out: dict[str, object] = {}
    for view, (included, excluded, windows) in views.items():
        out[view] = {
            "status": "FROZEN",
            "included_regimes": included,
            "excluded_regime": excluded,
            "reference_count": 4,
            "windows": {
                name: {
                    "status": "FROZEN",
                    "name": name,
                    "parent_regime": excluded,
                    "start": start,
                    "end_exclusive": end,
                    "row_count": 10,
                    "transformed_dimension_count": 8,
                    "active_dimension_count": 6,
                    "preprocessor_fingerprint": SHA,
                    "center_digest": SHA,
                    "scale_digest": SHA,
                    "active_dimension_mask_digest": SHA,
                    "minimum_reference_distance": 0.0,
                    "maximum_reference_distance": 4.0,
                    "mean_reference_distance": 1.5,
                    "sorted_reference_distance_digest": SHA,
                }
                for name, start, end in windows
            },
        }
    return out


def _consensus() -> dict[str, object]:
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
        "minimum_robust_pooled_calibrated_utility": 0.2,
        "maximum_robust_pooled_calibrated_utility": 0.9,
        "minimum_robust_fit_temporal_support": 0.1,
        "maximum_robust_fit_temporal_support": 0.8,
        "minimum_robust_fit_temporal_feature_support": 0.05,
        "maximum_robust_fit_temporal_feature_support": 0.95,
        "fit_temporal_feature_support_reference_count": 12,
        "view_prediction_digests": {
            view: {
                "long_net_pips_0p5": SHA,
                "short_net_pips_0p5": SHA,
            }
            for view in views
        },
    }


class Exp053FitTemporalFeatureSupportArtifactTests(
    unittest.TestCase
):
    def test_source_binding_and_authorization_are_exact(
        self,
    ) -> None:
        report = (
            validate_fit_temporal_feature_support_utility_artifact_runner_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
            "DEC-176",
        )
        self.assertEqual(
            DEC175_MERGED_COMMIT,
            "60abce7c2674f9c25e4132037c9eb24cab1baf22",
        )
        self.assertEqual(
            report["dec175_training_core_blob_sha"],
            DEC175_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC175_TRAINING_CORE_BLOB_SHA,
            "4fd0e48302f97e188a8124e1543bde0ffdb43b6f",
        )
        self.assertFalse(
            report[
                "authoritative_fit_temporal_feature_support_utility_model_result_execution_authorized"
            ]
        )
        self.assertFalse(
            report[
                "fit_temporal_feature_support_utility_model_fit_authorized"
            ]
        )

    def test_feature_references_require_exact_12(self) -> None:
        fit = {
            "fit_temporal_feature_support_references": (
                _feature_refs()
            ),
            "fit_temporal_feature_support_reference_count": 12,
        }
        self.assertEqual(
            _validate_feature_references(fit),
            12,
        )

        drifted = {
            **fit,
            "fit_temporal_feature_support_reference_count": 11,
        }
        with self.assertRaisesRegex(
            ValueError,
            "reference count mismatch",
        ):
            _validate_feature_references(drifted)

    def test_feature_reference_identity_and_bounds_fail_closed(
        self,
    ) -> None:
        fit = {
            "fit_temporal_feature_support_references": (
                _feature_refs()
            ),
            "fit_temporal_feature_support_reference_count": 12,
        }
        refs = fit[
            "fit_temporal_feature_support_references"
        ]
        assert isinstance(refs, dict)
        view = refs["leave_out_fit_2015_2016"]
        assert isinstance(view, dict)
        windows = view["windows"]
        assert isinstance(windows, dict)
        window = windows["fit_2015_h1"]
        assert isinstance(window, dict)
        window["start"] = "2015-02-01"

        with self.assertRaisesRegex(
            ValueError,
            "window start mismatch",
        ):
            _validate_feature_references(fit)

        fit = {
            "fit_temporal_feature_support_references": (
                _feature_refs()
            ),
            "fit_temporal_feature_support_reference_count": 12,
        }
        refs = fit[
            "fit_temporal_feature_support_references"
        ]
        assert isinstance(refs, dict)
        view = refs["leave_out_fit_2015_2016"]
        assert isinstance(view, dict)
        windows = view["windows"]
        assert isinstance(windows, dict)
        window = windows["fit_2015_h1"]
        assert isinstance(window, dict)
        window["mean_reference_distance"] = 5.0
        with self.assertRaisesRegex(
            ValueError,
            "distance bounds invalid",
        ):
            _validate_feature_references(fit)

    def test_consensus_requires_feature_support_bounds(
        self,
    ) -> None:
        self.assertEqual(
            _validate_consensus_block(
                _consensus(),
                expected_row_count=10,
                field="fixture",
            ),
            5,
        )
        drifted = _consensus()
        drifted[
            "maximum_robust_fit_temporal_feature_support"
        ] = 1.1
        with self.assertRaisesRegex(
            ValueError,
            "feature-support bounds invalid",
        ):
            _validate_consensus_block(
                drifted,
                expected_row_count=10,
                field="fixture",
            )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_feature_support_utility_artifacts."
        "_compile_summary"
    )
    def test_complete_evidence_requires_216_feature_references(
        self,
        compile_summary,
    ) -> None:
        summary = {
            "verified_cell_count": 18,
            "selected_cell_count": 0,
            "no_fit_temporal_feature_support_utility_stable_model_challenger_count": 18,
            "aggregate_selection_pass_variant_count": 0,
            "stable_selection_pass_variant_count": 0,
            "unavailable_budget_variant_count": 0,
            "utility_eligible_selection_row_count": 0,
            "verified_regressor_count": 108,
            "verified_pooled_calibration_reference_count": 108,
            "verified_fit_temporal_support_reference_count": 432,
            "verified_fit_temporal_feature_support_reference_count": 216,
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
            compile_fit_temporal_feature_support_utility_model_result_evidence(
                cells,
                code_commit=commit,
            )
        )
        report = (
            validate_fit_temporal_feature_support_utility_model_result_evidence(
                evidence,
                expected_code_commit=commit,
            )
        )
        self.assertTrue(
            report[
                "fit_temporal_feature_support_utility_model_result_evidence_verified"
            ]
        )
        self.assertEqual(
            report[
                "verified_fit_temporal_feature_support_reference_count"
            ],
            216,
        )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_feature_support_utility_artifacts."
        "validate_authoritative_readiness"
    )
    def test_authoritative_bundle_rejects_before_artifact_loading(
        self,
        validate_readiness,
    ) -> None:
        self.assertFalse(
            AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        with self.assertRaisesRegex(
            PermissionError,
            "DEC-176 source is non-executable",
        ):
            run_authoritative_fit_temporal_feature_support_utility_model_bundle(
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
            "model_successor_fit_temporal_feature_support_utility_artifacts.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
