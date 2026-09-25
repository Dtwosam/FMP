from __future__ import annotations

from pathlib import Path
from unittest.mock import patch
import unittest

from fmp.market_learning.model_protocol import MODEL_CELLS
from fmp.market_learning.model_successor_fit_temporal_support_utility_artifacts import (
    AUTHORITATIVE_FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC164_MERGED_COMMIT,
    DEC164_TRAINING_CORE_BLOB_SHA,
    FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    _validate_consensus_block,
    _validate_fit_block,
    compile_fit_temporal_support_utility_model_result_evidence,
    run_authoritative_fit_temporal_support_utility_model_bundle,
    validate_fit_temporal_support_utility_artifact_runner_sources,
    validate_fit_temporal_support_utility_model_result_evidence,
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


def _support_windows(
    parent: str,
) -> list[tuple[str, str, str]]:
    mapping = {
        "fit_2015_2016": [
            ("fit_2015_h1", "2015-01-01", "2015-07-01"),
            ("fit_2015_h2", "2015-07-01", "2016-01-01"),
            ("fit_2016_h1", "2016-01-01", "2016-07-01"),
            ("fit_2016_h2", "2016-07-01", "2017-01-01"),
        ],
        "fit_2017_2018": [
            ("fit_2017_h1", "2017-01-01", "2017-07-01"),
            ("fit_2017_h2", "2017-07-01", "2018-01-01"),
            ("fit_2018_h1", "2018-01-01", "2018-07-01"),
            ("fit_2018_h2", "2018-07-01", "2019-01-01"),
        ],
        "fit_2019_2020": [
            ("fit_2019_h1", "2019-01-01", "2019-07-01"),
            ("fit_2019_h2", "2019-07-01", "2020-01-01"),
            ("fit_2020_h1", "2020-01-01", "2020-07-01"),
            ("fit_2020_h2", "2020-07-01", "2021-01-01"),
        ],
    }
    return mapping[parent]


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
    pooled: dict[str, object] = {}
    support: dict[str, object] = {}
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
        pooled[name] = {
            "status": "FROZEN",
            "included_regimes": included,
            "excluded_regime": excluded,
            "row_count": 8,
            "target_count": 2,
            "targets": {
                target: {
                    "status": "FROZEN",
                    "excluded_regime": excluded,
                    "row_count": 8,
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
        target_support: dict[str, object] = {}
        for target in (
            "long_net_pips_0p5",
            "short_net_pips_0p5",
        ):
            windows = {
                window_name: {
                    "name": window_name,
                    "parent_regime": excluded,
                    "start": start,
                    "end_exclusive": end,
                    "row_count": 2,
                    "status": "FROZEN",
                    "minimum_prediction": -1.0,
                    "maximum_prediction": 2.0,
                    "mean_prediction": 0.5,
                    "row_bound_prediction_digest": SHA,
                    "sorted_reference_digest": SHA,
                }
                for window_name, start, end in _support_windows(
                    excluded
                )
            }
            target_support[target] = {
                "status": "FROZEN",
                "excluded_regime": excluded,
                "window_count": 4,
                "windows": windows,
            }
        support[name] = {
            "status": "FROZEN",
            "included_regimes": included,
            "excluded_regime": excluded,
            "target_count": 2,
            "support_reference_count": 8,
            "targets": target_support,
        }

    return {
        "jackknife_models": models,
        "jackknife_view_count": 3,
        "regressor_count": 6,
        "out_of_fit_calibration_references": pooled,
        "calibration_reference_count": 6,
        "fit_temporal_support_references": support,
        "fit_temporal_support_reference_count": 24,
        "full_fit_single_model": {
            "status": "FORBIDDEN_BY_DEC150_DEC163",
            "fit_attempt_count": 0,
        },
        "view_weight_search": {
            "status": "FORBIDDEN_BY_DEC150_DEC163",
            "fit_attempt_count": 0,
        },
        "view_fallback": {
            "status": "FORBIDDEN_BY_DEC150_DEC163",
            "fit_attempt_count": 0,
        },
        "selection_window_calibration": {
            "status": "FORBIDDEN_BY_DEC150_DEC163",
            "fit_attempt_count": 0,
        },
        "hist_gradient_boosting_classifier": {
            "status": "EXCLUDED_BY_DEC150_DEC163",
            "fit_attempt_count": 0,
        },
        "logistic_regression": {
            "status": "EXCLUDED_BY_DEC112_DEC150_DEC163",
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
        "minimum_robust_pooled_calibrated_utility": 0.2,
        "maximum_robust_pooled_calibrated_utility": 0.9,
        "minimum_robust_fit_temporal_support": 0.1,
        "maximum_robust_fit_temporal_support": 0.8,
        "view_prediction_digests": {
            view: {
                "long_net_pips_0p5": SHA,
                "short_net_pips_0p5": SHA,
            }
            for view in views
        },
    }


class Exp052FitTemporalSupportArtifactTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(
        self,
    ) -> None:
        report = (
            validate_fit_temporal_support_utility_artifact_runner_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            report["dec164_merged_commit"],
            DEC164_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC164_MERGED_COMMIT,
            "d9f893504b2d790eb73bc49edf4c0919ef2ff914",
        )
        self.assertEqual(
            report["dec164_training_core_blob_sha"],
            DEC164_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC164_TRAINING_CORE_BLOB_SHA,
            "fe5664438752a161134bbed6f55d9985f1c1470a",
        )
        self.assertEqual(
            report[
                "fit_temporal_support_utility_model_artifact_runner_decision"
            ],
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
        )
        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
            "DEC-165",
        )
        self.assertFalse(
            report[
                "authoritative_fit_temporal_support_utility_model_result_execution_authorized"
            ]
        )
        self.assertFalse(
            report[
                "fit_temporal_support_utility_model_fit_authorized"
            ]
        )

    def test_fit_block_requires_6_6_24_evidence(self) -> None:
        regressors, pooled, support = _validate_fit_block(
            _fit_block()
        )
        self.assertEqual(regressors, 6)
        self.assertEqual(pooled, 6)
        self.assertEqual(support, 24)

    def test_support_window_identity_fails_closed(self) -> None:
        drifted = _fit_block()
        support = drifted["fit_temporal_support_references"]
        assert isinstance(support, dict)
        view = support["leave_out_fit_2015_2016"]
        assert isinstance(view, dict)
        targets = view["targets"]
        assert isinstance(targets, dict)
        target = targets["long_net_pips_0p5"]
        assert isinstance(target, dict)
        windows = target["windows"]
        assert isinstance(windows, dict)
        window = windows["fit_2015_h1"]
        assert isinstance(window, dict)
        window["start"] = "2015-02-01"

        with self.assertRaisesRegex(
            ValueError,
            "support window start mismatch",
        ):
            _validate_fit_block(drifted)

    def test_support_reference_count_fails_closed(self) -> None:
        drifted = _fit_block()
        drifted["fit_temporal_support_reference_count"] = 23
        with self.assertRaisesRegex(
            ValueError,
            "support reference count mismatch",
        ):
            _validate_fit_block(drifted)

    def test_consensus_requires_pooled_and_support_bounds(
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
        drifted["maximum_robust_fit_temporal_support"] = 1.1
        with self.assertRaisesRegex(
            ValueError,
            "support bounds out of range",
        ):
            _validate_consensus_block(
                drifted,
                expected_row_count=10,
                field="fixture",
            )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_support_utility_artifacts."
        "_compile_summary"
    )
    def test_complete_evidence_is_canonical_and_revalidates(
        self,
        compile_summary,
    ) -> None:
        summary = {
            "verified_cell_count": 18,
            "selected_cell_count": 0,
            "no_fit_temporal_support_utility_stable_model_challenger_count": 18,
            "aggregate_selection_pass_variant_count": 0,
            "stable_selection_pass_variant_count": 0,
            "unavailable_budget_variant_count": 0,
            "utility_eligible_selection_row_count": 0,
            "verified_regressor_count": 108,
            "verified_pooled_calibration_reference_count": 108,
            "verified_fit_temporal_support_reference_count": 432,
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
            compile_fit_temporal_support_utility_model_result_evidence(
                cells,
                code_commit=commit,
            )
        )
        self.assertEqual(evidence["cell_count"], 18)
        self.assertEqual(evidence["summary"], summary)
        report = (
            validate_fit_temporal_support_utility_model_result_evidence(
                evidence,
                expected_code_commit=commit,
            )
        )
        self.assertTrue(
            report[
                "fit_temporal_support_utility_model_result_evidence_verified"
            ]
        )
        self.assertEqual(report["verified_regressor_count"], 108)
        self.assertEqual(
            report[
                "verified_pooled_calibration_reference_count"
            ],
            108,
        )
        self.assertEqual(
            report[
                "verified_fit_temporal_support_reference_count"
            ],
            432,
        )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_support_utility_artifacts."
        "validate_authoritative_readiness"
    )
    def test_authoritative_bundle_rejects_before_artifact_loading(
        self,
        validate_readiness,
    ) -> None:
        self.assertFalse(
            AUTHORITATIVE_FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        with self.assertRaisesRegex(
            PermissionError,
            "DEC-165 source is non-executable",
        ):
            run_authoritative_fit_temporal_support_utility_model_bundle(
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
            "model_successor_fit_temporal_support_utility_artifacts.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
