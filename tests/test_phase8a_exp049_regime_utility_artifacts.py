from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_protocol import MODEL_CELLS
from fmp.market_learning.model_successor_regime_utility_artifacts import (
    AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC133_MERGED_COMMIT,
    DEC133_TRAINING_CORE_BLOB_SHA,
    REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    REGIME_UTILITY_MODEL_FIT_AUTHORIZED,
    _canonical_json,
    _sha256,
    compile_regime_utility_model_result_evidence,
    run_authoritative_regime_utility_model_bundle,
    validate_regime_utility_artifact_runner_sources,
    validate_regime_utility_model_result_evidence,
)
from fmp.market_learning.model_successor_regime_utility_protocol import (
    FINANCIAL_TARGET_COLUMNS,
    REGIME_UTILITY_EXPERIMENT_ID,
    REGIME_UTILITY_PROTOCOL_DECISION,
    REGIME_UTILITY_PROTOCOL_VERSION,
    TEMPORAL_STABILITY_WINDOWS,
    regime_utility_protocol_fingerprint,
)
from fmp.market_learning.model_successor_regime_utility_training import (
    BASE_TRAINING_CORE_BLOB_SHA,
    DEC132_MERGED_COMMIT,
    DEC132_PROTOCOL_BLOB_SHA,
    DENSITY_HELPER_CORE_BLOB_SHA,
    REGIME_UTILITY_TRAINING_CORE_DECISION,
    REGIME_UTILITY_TRAINING_CORE_VERSION,
)


ROOT = Path(__file__).resolve().parents[1]
CODE_COMMIT = "a" * 40
FP = "b" * 64
PREP_FP = "c" * 64


def _target_summary() -> dict[str, object]:
    return {
        "row_count": 3,
        "minimum_net_pips": -1.0,
        "maximum_net_pips": 2.0,
        "mean_net_pips": 0.5,
        "positive_count": 2,
        "negative_count": 1,
        "zero_count": 0,
    }


def _regime_models() -> dict[str, object]:
    out: dict[str, object] = {}
    for regime_index, name in enumerate(
        ("fit_2015_2016", "fit_2017_2018", "fit_2019_2020")
    ):
        regressors: dict[str, object] = {}
        for target_index, target in enumerate(
            FINANCIAL_TARGET_COLUMNS
        ):
            regressors[target] = {
                "status": "FITTED",
                "fit_attempt_count": 1,
                "target_summary": _target_summary(),
                "preprocessor_fingerprint": PREP_FP,
                "model_fingerprint": (
                    f"{regime_index + target_index + 1:x}" * 64
                )[:64],
            }
        out[name] = {
            "status": "FITTED",
            "row_count": 3,
            "regressor_count": 2,
            "regressors": regressors,
        }
    return out


def _unavailable_variant(budget: int) -> dict[str, object]:
    return {
        "model_family": "hist_gradient_boosting_regression",
        "candidate_budget_anchor": budget,
        "evaluation_status": "BUDGET_UNAVAILABLE",
        "status": "UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS",
        "eligible_utility_row_count": 0,
        "selection_derived_cutoff": None,
        "aggregate_selection_gate_passed": False,
        "temporal_stability": {
            "status": "BUDGET_UNAVAILABLE",
            "minimum_directional_candidate_share_per_window": 0.10,
            "windows": [],
        },
        "selection_gate_passed": False,
    }


def _stable_variant(budget: int) -> dict[str, object]:
    criteria = {
        "directional_candidate_count>=250": True,
        "total_net_pips>0": True,
        "mean_net_pips>0": True,
        "gross_positive_pips>absolute_gross_negative_pips": True,
    }
    windows = [
        {
            "name": str(window["name"]),
            "start": str(window["start"]),
            "end_exclusive": str(window["end_exclusive"]),
            "row_count": 100,
            "metrics": {
                "directional_candidate_count": 25,
                "total_net_pips": 25.0,
                "mean_net_pips": 1.0,
                "gross_positive_pips": 25.0,
                "absolute_gross_negative_pips": 0.0,
            },
            "gate": {
                "passed": True,
                "criteria": {
                    "directional_candidate_share>=0.10": True,
                    "total_net_pips>0": True,
                    "mean_net_pips>0": True,
                    "gross_positive_pips>absolute_gross_negative_pips": True,
                },
                "directional_candidate_share": 0.10,
            },
        }
        for window in TEMPORAL_STABILITY_WINDOWS
    ]
    return {
        "model_family": "hist_gradient_boosting_regression",
        "candidate_budget_anchor": budget,
        "evaluation_status": "EVALUATED",
        "status": "AVAILABLE",
        "eligible_utility_row_count": 250,
        "selection_derived_cutoff": 0.7,
        "selection_candidate_count_at_cutoff": 250,
        "scenarios": {
            "0.5": {
                "metrics": {
                    "directional_candidate_count": 250,
                    "total_net_pips": 250.0,
                    "mean_net_pips": 1.0,
                    "gross_positive_pips": 250.0,
                    "absolute_gross_negative_pips": 0.0,
                },
                "gate": {
                    "passed": True,
                    "criteria": criteria,
                },
            }
        },
        "aggregate_selection_gate_passed": True,
        "temporal_stability": {
            "status": "PASS",
            "minimum_directional_candidate_share_per_window": 0.10,
            "windows": windows,
        },
        "selection_gate_passed": True,
    }


def _consensus() -> dict[str, object]:
    return {
        "row_count": 1,
        "consensus_direction_counts": {
            "LONG": 0,
            "SHORT": 0,
            "NO_TRADE": 1,
        },
        "consensus_eligible_row_count": 0,
        "consensus_eligible_rate": 0.0,
        "minimum_robust_utility": None,
        "maximum_robust_utility": None,
        "regime_prediction_digests": {
            regime: {
                target: FP
                for target in FINANCIAL_TARGET_COLUMNS
            }
            for regime in (
                "fit_2015_2016",
                "fit_2017_2018",
                "fit_2019_2020",
            )
        },
    }


def _cell_result(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> dict[str, object]:
    result: dict[str, object] = {
        "experiment_id": REGIME_UTILITY_EXPERIMENT_ID,
        "training_core_version": REGIME_UTILITY_TRAINING_CORE_VERSION,
        "training_core_decision": REGIME_UTILITY_TRAINING_CORE_DECISION,
        "dec132_merged_commit": DEC132_MERGED_COMMIT,
        "dec132_protocol_blob_sha": DEC132_PROTOCOL_BLOB_SHA,
        "base_training_core_blob_sha": BASE_TRAINING_CORE_BLOB_SHA,
        "density_helper_core_blob_sha": DENSITY_HELPER_CORE_BLOB_SHA,
        "protocol_decision": REGIME_UTILITY_PROTOCOL_DECISION,
        "protocol_version": REGIME_UTILITY_PROTOCOL_VERSION,
        "protocol_fingerprint": regime_utility_protocol_fingerprint(),
        "prior_result_informed": True,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "cell": {
            "symbol": symbol,
            "timeframe": timeframe,
            "horizon_minutes": horizon,
        },
        "processed_manifest_sha256": FP,
        "joined_row_count": 4,
        "split_row_counts": {
            "fit": 1,
            "selection": 1,
            "validation": 1,
            "retrospective_holdout": 1,
        },
        "fit": {
            "regime_models": _regime_models(),
            "regime_model_count": 3,
            "regressor_count": 6,
            "full_fit_single_model": {
                "status": "FORBIDDEN_BY_DEC132",
                "fit_attempt_count": 0,
            },
            "hist_gradient_boosting_classifier": {
                "status": "EXCLUDED_BY_DEC132",
                "fit_attempt_count": 0,
            },
            "logistic_regression": {
                "status": "EXCLUDED_BY_DEC112_DEC132",
                "fit_attempt_count": 0,
            },
        },
        "selection": {
            "status": "NO_REGIME_UTILITY_STABLE_MODEL_CHALLENGER",
            "row_count": 1,
            "regime_utility_consensus": _consensus(),
            "regime_utility_consensus_digest": FP,
            "variants": [
                _unavailable_variant(250),
                _unavailable_variant(500),
                _unavailable_variant(1000),
            ],
            "selected_variant": None,
        },
        "validation": {"status": "LOCKED_NO_SELECTION"},
        "retrospective_holdout": {"status": "LOCKED_NO_SELECTION"},
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    result["result_fingerprint"] = _sha256(
        _canonical_json(result)
    )
    return result


def _all_cell_results() -> list[dict[str, object]]:
    return [
        _cell_result(
            cell.symbol,
            cell.timeframe,
            cell.horizon_minutes,
        )
        for cell in MODEL_CELLS
    ]


def _refresh_result_fingerprint(row: dict[str, object]) -> None:
    row["result_fingerprint"] = _sha256(
        _canonical_json(
            {
                key: value
                for key, value in row.items()
                if key != "result_fingerprint"
            }
        )
    )


class Exp049RegimeUtilityArtifactTests(unittest.TestCase):
    def test_source_binds_exact_protocol_core_and_loader(self) -> None:
        report = validate_regime_utility_artifact_runner_sources(
            repository_root=ROOT
        )
        self.assertEqual(
            report["dec132_merged_commit"],
            DEC132_MERGED_COMMIT,
        )
        self.assertEqual(
            report["dec133_merged_commit"],
            DEC133_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC133_MERGED_COMMIT,
            "a6420e35a9219c81e65c5179843488f94b6668d3",
        )
        self.assertEqual(
            report["dec133_training_core_blob_sha"],
            DEC133_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC133_TRAINING_CORE_BLOB_SHA,
            "e1018b20210b7bb8d666071d8eb878aba5899111",
        )
        self.assertEqual(
            report["regime_utility_model_artifact_runner_decision"],
            REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
        )
        self.assertEqual(
            REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
            "DEC-134",
        )
        self.assertFalse(
            report[
                "authoritative_regime_utility_model_result_execution_authorized"
            ]
        )
        self.assertFalse(
            report["regime_utility_model_fit_authorized"]
        )

    def test_compile_and_validate_exact_18_cell_evidence(self) -> None:
        evidence = compile_regime_utility_model_result_evidence(
            _all_cell_results(),
            code_commit=CODE_COMMIT,
        )
        summary = validate_regime_utility_model_result_evidence(
            evidence,
            expected_code_commit=CODE_COMMIT,
        )
        self.assertTrue(
            summary[
                "regime_utility_model_result_evidence_verified"
            ]
        )
        self.assertEqual(summary["verified_cell_count"], 18)
        self.assertEqual(summary["selected_cell_count"], 0)
        self.assertEqual(
            summary[
                "no_regime_utility_stable_model_challenger_count"
            ],
            18,
        )
        self.assertEqual(
            summary["unavailable_budget_variant_count"],
            54,
        )
        self.assertEqual(
            summary["utility_eligible_selection_row_count"],
            0,
        )
        self.assertEqual(
            summary["verified_regressor_count"],
            108,
        )
        self.assertFalse(summary["promotion_authorized"])
        self.assertFalse(summary["shadow_authorized"])
        self.assertFalse(summary["trading_authorized"])

    def test_incomplete_evidence_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "incomplete"):
            compile_regime_utility_model_result_evidence(
                _all_cell_results()[:-1],
                code_commit=CODE_COMMIT,
            )

    def test_missing_target_regressor_fails_closed(self) -> None:
        rows = _all_cell_results()
        models = rows[0]["fit"]["regime_models"]
        assert isinstance(models, dict)
        regime = models["fit_2017_2018"]
        assert isinstance(regime, dict)
        regressors = regime["regressors"]
        assert isinstance(regressors, dict)
        regressors.pop("short_net_pips_0p5")
        _refresh_result_fingerprint(rows[0])

        with self.assertRaisesRegex(
            ValueError,
            "regressor inventory mismatch",
        ):
            compile_regime_utility_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_utility_accounting_tamper_fails_closed(self) -> None:
        rows = _all_cell_results()
        consensus = rows[0]["selection"][
            "regime_utility_consensus"
        ]
        assert isinstance(consensus, dict)
        consensus["consensus_eligible_row_count"] = 1
        _refresh_result_fingerprint(rows[0])

        with self.assertRaisesRegex(
            ValueError,
            "consensus eligible count mismatch",
        ):
            compile_regime_utility_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_variant_utility_count_drift_fails_closed(self) -> None:
        rows = _all_cell_results()
        variants = rows[0]["selection"]["variants"]
        assert isinstance(variants, list)
        variants[0]["eligible_utility_row_count"] = 1
        _refresh_result_fingerprint(rows[0])

        with self.assertRaisesRegex(
            ValueError,
            "variant utility eligible count mismatch",
        ):
            compile_regime_utility_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_no_challenger_cannot_hide_stable_variant(self) -> None:
        rows = _all_cell_results()
        selection = rows[0]["selection"]
        assert isinstance(selection, dict)
        selection["regime_utility_consensus"] = {
            **_consensus(),
            "consensus_direction_counts": {
                "LONG": 250,
                "SHORT": 0,
                "NO_TRADE": 750,
            },
            "consensus_eligible_row_count": 250,
            "consensus_eligible_rate": 0.25,
            "minimum_robust_utility": 0.5,
            "maximum_robust_utility": 0.9,
            "row_count": 1000,
        }
        selection["row_count"] = 1000
        split_counts = rows[0]["split_row_counts"]
        assert isinstance(split_counts, dict)
        split_counts["selection"] = 1000
        variants = selection["variants"]
        assert isinstance(variants, list)
        variants[0] = _stable_variant(250)
        for item in variants[1:]:
            item["eligible_utility_row_count"] = 250
        _refresh_result_fingerprint(rows[0])

        with self.assertRaisesRegex(
            ValueError,
            "no-challenger status hides stable variant",
        ):
            compile_regime_utility_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_full_fit_fallback_fails_closed(self) -> None:
        rows = _all_cell_results()
        fit = rows[0]["fit"]
        assert isinstance(fit, dict)
        fit["full_fit_single_model"] = {
            "status": "FITTED",
            "fit_attempt_count": 1,
        }
        _refresh_result_fingerprint(rows[0])

        with self.assertRaisesRegex(
            ValueError,
            "full-fit fallback record mismatch",
        ):
            compile_regime_utility_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_authoritative_bundle_is_locked_before_loading(self) -> None:
        self.assertFalse(
            AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(REGIME_UTILITY_MODEL_FIT_AUTHORIZED)
        with self.assertRaisesRegex(
            PermissionError,
            "DEC-134 source is non-executable",
        ):
            run_authoritative_regime_utility_model_bundle(
                repository_root=ROOT,
                readiness={},
                feature_roots={},
                outcome_roots={},
                code_commit=CODE_COMMIT,
            )


if __name__ == "__main__":
    unittest.main()
