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
        "maximum_net_pips": 1.0,
        "mean_net_pips": 0.0,
        "positive_count": 1,
        "negative_count": 1,
        "zero_count": 1,
    }


def _regime_models() -> dict[str, object]:
    out: dict[str, object] = {}
    for regime_index, name in enumerate(
        ("fit_2015_2016", "fit_2017_2018", "fit_2019_2020")
    ):
        regressors: dict[str, object] = {}
        for target_index, target in enumerate(FINANCIAL_TARGET_COLUMNS):
            digit = regime_index * 2 + target_index + 1
            regressors[target] = {
                "status": "FITTED",
                "fit_attempt_count": 1,
                "target_summary": _target_summary(),
                "preprocessor_fingerprint": PREP_FP,
                "model_fingerprint": f"{digit:x}" * 64,
            }
        out[name] = {
            "status": "FITTED",
            "row_count": 3,
            "regressor_count": 2,
            "regressors": regressors,
        }
    return out


def _utility_consensus() -> dict[str, object]:
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


def _financial_metrics(count: int, total: float) -> dict[str, object]:
    mean = total / count if count else None
    return {
        "directional_candidate_count": count,
        "directional_candidate_rate": 0.0,
        "long_candidate_count": count,
        "short_candidate_count": 0,
        "total_net_pips": total,
        "mean_net_pips": mean,
        "gross_positive_pips": max(total, 0.0),
        "absolute_gross_negative_pips": max(-total, 0.0),
        "positive_candidate_count": count if total > 0 else 0,
        "negative_candidate_count": count if total < 0 else 0,
        "zero_candidate_count": count if total == 0 else 0,
        "candidate_identity_digest": FP,
    }


def _financial_gate(metrics: dict[str, object]) -> dict[str, object]:
    count = int(metrics["directional_candidate_count"])
    total = float(metrics["total_net_pips"])
    mean = metrics["mean_net_pips"]
    gross_positive = float(metrics["gross_positive_pips"])
    gross_negative = float(metrics["absolute_gross_negative_pips"])
    criteria = {
        "directional_candidate_count>=250": count >= 250,
        "total_net_pips>0": total > 0.0,
        "mean_net_pips>0": mean is not None and float(mean) > 0.0,
        "gross_positive_pips>absolute_gross_negative_pips": (
            gross_positive > gross_negative
        ),
    }
    return {"passed": all(criteria.values()), "criteria": criteria}


def _stable_variant(budget: int) -> dict[str, object]:
    metrics = _financial_metrics(250, 250.0)
    windows = []
    for window in TEMPORAL_STABILITY_WINDOWS:
        w_metrics = _financial_metrics(25, 25.0)
        windows.append(
            {
                "name": str(window["name"]),
                "start": str(window["start"]),
                "end_exclusive": str(window["end_exclusive"]),
                "row_count": 100,
                "metrics": w_metrics,
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
        )
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
                "metrics": metrics,
                "gate": _financial_gate(metrics),
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
            "regime_utility_consensus": _utility_consensus(),
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
    result["result_fingerprint"] = _sha256(_canonical_json(result))
    return result


def _all_cell_results() -> list[dict[str, object]]:
    return [
        _cell_result(cell.symbol, cell.timeframe, cell.horizon_minutes)
        for cell in MODEL_CELLS
    ]


class Exp049RegimeUtilityArtifactTests(unittest.TestCase):
    def test_source_binds_exact_protocol_core_and_loader(self) -> None:
        report = validate_regime_utility_artifact_runner_sources(
            repository_root=ROOT
        )
        self.assertEqual(report["dec132_merged_commit"], DEC132_MERGED_COMMIT)
        self.assertEqual(report["dec133_merged_commit"], DEC133_MERGED_COMMIT)
        self.assertEqual(
            report["dec133_training_core_blob_sha"],
            DEC133_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC133_MERGED_COMMIT,
            "a6420e35a9219c81e65c5179843488f94b6668d3",
        )
        self.assertEqual(
            DEC133_TRAINING_CORE_BLOB_SHA,
            "e1018b20210b7bb8d666071d8eb878aba5899111",
        )
        self.assertEqual(
            report["regime_utility_model_artifact_runner_decision"],
            REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
        )
        self.assertFalse(
            report[
                "authoritative_regime_utility_model_result_execution_authorized"
            ]
        )
        self.assertFalse(report["regime_utility_model_fit_authorized"])

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
            summary["regime_utility_model_result_evidence_verified"]
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
        self.assertFalse(summary["promotion_authorized"])
        self.assertFalse(summary["shadow_authorized"])
        self.assertFalse(summary["trading_authorized"])

    def test_missing_regressor_fails_closed(self) -> None:
        rows = _all_cell_results()
        models = rows[0]["fit"]["regime_models"]
        assert isinstance(models, dict)
        regime = models["fit_2017_2018"]
        assert isinstance(regime, dict)
        regressors = regime["regressors"]
        assert isinstance(regressors, dict)
        regressors.pop("short_net_pips_0p5")
        rows[0]["result_fingerprint"] = _sha256(
            _canonical_json(
                {
                    key: value
                    for key, value in rows[0].items()
                    if key != "result_fingerprint"
                }
            )
        )
        with self.assertRaisesRegex(
            ValueError,
            "regressor inventory mismatch",
        ):
            compile_regime_utility_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_consensus_prediction_digest_tamper_fails_closed(self) -> None:
        rows = _all_cell_results()
        consensus = rows[0]["selection"]["regime_utility_consensus"]
        assert isinstance(consensus, dict)
        digests = consensus["regime_prediction_digests"]
        assert isinstance(digests, dict)
        digests["fit_2015_2016"]["long_net_pips_0p5"] = "not-a-sha"
        rows[0]["result_fingerprint"] = _sha256(
            _canonical_json(
                {
                    key: value
                    for key, value in rows[0].items()
                    if key != "result_fingerprint"
                }
            )
        )
        with self.assertRaisesRegex(ValueError, "prediction digest"):
            compile_regime_utility_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_stable_variant_cannot_be_hidden(self) -> None:
        rows = _all_cell_results()
        first = rows[0]
        first["selection"]["regime_utility_consensus"] = {
            **_utility_consensus(),
            "consensus_direction_counts": {
                "LONG": 250,
                "SHORT": 0,
                "NO_TRADE": 0,
            },
            "consensus_eligible_row_count": 250,
            "consensus_eligible_rate": 1.0,
            "minimum_robust_utility": 0.7,
            "maximum_robust_utility": 1.1,
        }
        first["selection"]["row_count"] = 250
        first["split_row_counts"]["selection"] = 250
        first["selection"]["variants"][0] = _stable_variant(250)
        first["result_fingerprint"] = _sha256(
            _canonical_json(
                {
                    key: value
                    for key, value in first.items()
                    if key != "result_fingerprint"
                }
            )
        )
        with self.assertRaisesRegex(ValueError, "hides stable variant"):
            compile_regime_utility_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_authoritative_bundle_is_non_executable(self) -> None:
        self.assertFalse(
            AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(REGIME_UTILITY_MODEL_FIT_AUTHORIZED)
        with self.assertRaisesRegex(PermissionError, "non-executable"):
            run_authoritative_regime_utility_model_bundle(
                repository_root=ROOT,
                readiness={},
                feature_roots={},
                outcome_roots={},
                code_commit=CODE_COMMIT,
            )


if __name__ == "__main__":
    unittest.main()
