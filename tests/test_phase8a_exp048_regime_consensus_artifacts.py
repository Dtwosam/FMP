from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_protocol import MODEL_CELLS
from fmp.market_learning.model_successor_regime_consensus_artifacts import (
    AUTHORITATIVE_REGIME_CONSENSUS_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC124_MERGED_COMMIT,
    DEC124_TRAINING_CORE_BLOB_SHA,
    REGIME_CONSENSUS_MODEL_ARTIFACT_RUNNER_DECISION,
    REGIME_CONSENSUS_MODEL_FIT_AUTHORIZED,
    _canonical_json,
    _sha256,
    compile_regime_consensus_model_result_evidence,
    run_authoritative_regime_consensus_model_bundle,
    validate_regime_consensus_artifact_runner_sources,
    validate_regime_consensus_model_result_evidence,
)
from fmp.market_learning.model_successor_regime_consensus_protocol import (
    REGIME_CONSENSUS_EXPERIMENT_ID,
    TEMPORAL_STABILITY_WINDOWS,
    REGIME_CONSENSUS_PROTOCOL_DECISION,
    REGIME_CONSENSUS_PROTOCOL_VERSION,
    regime_consensus_protocol_fingerprint,
)
from fmp.market_learning.model_successor_regime_consensus_training import (
    BASE_TRAINING_CORE_BLOB_SHA,
    DEC123_MERGED_COMMIT,
    DEC123_PROTOCOL_BLOB_SHA,
    DENSITY_HELPER_CORE_BLOB_SHA,
    REGIME_CONSENSUS_TRAINING_CORE_DECISION,
    REGIME_CONSENSUS_TRAINING_CORE_VERSION,
)


ROOT = Path(__file__).resolve().parents[1]
CODE_COMMIT = "a" * 40
FP = "b" * 64
PREP_FP = "c" * 64
MODEL_FP = "d" * 64


def _regime_models() -> dict[str, object]:
    out: dict[str, object] = {}
    for index, name in enumerate(
        ("fit_2015_2016", "fit_2017_2018", "fit_2019_2020")
    ):
        out[name] = {
            "status": "FITTED",
            "fit_attempt_count": 1,
            "row_count": 3,
            "target_class_counts": {
                "LONG": 1,
                "SHORT": 1,
                "NO_TRADE": 1,
            },
            "preprocessor_fingerprint": PREP_FP,
            "model_fingerprint": f"{index + 1:x}" * 64,
        }
    return out


def _unavailable_variant(budget: int) -> dict[str, object]:
    return {
        "model_family": "hist_gradient_boosting",
        "candidate_budget_anchor": budget,
        "evaluation_status": "BUDGET_UNAVAILABLE",
        "status": "UNAVAILABLE_INSUFFICIENT_CONSENSUS_ROWS",
        "eligible_consensus_row_count": 0,
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
        "model_family": "hist_gradient_boosting",
        "candidate_budget_anchor": budget,
        "evaluation_status": "EVALUATED",
        "status": "AVAILABLE",
        "eligible_consensus_row_count": 1000,
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
        "minimum_consensus_confidence": None,
        "maximum_consensus_confidence": None,
        "regime_probability_digests": {
            "fit_2015_2016": FP,
            "fit_2017_2018": FP,
            "fit_2019_2020": FP,
        },
    }


def _cell_result(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> dict[str, object]:
    result: dict[str, object] = {
        "experiment_id": REGIME_CONSENSUS_EXPERIMENT_ID,
        "training_core_version": REGIME_CONSENSUS_TRAINING_CORE_VERSION,
        "training_core_decision": REGIME_CONSENSUS_TRAINING_CORE_DECISION,
        "dec123_merged_commit": DEC123_MERGED_COMMIT,
        "dec123_protocol_blob_sha": DEC123_PROTOCOL_BLOB_SHA,
        "base_training_core_blob_sha": BASE_TRAINING_CORE_BLOB_SHA,
        "density_helper_core_blob_sha": DENSITY_HELPER_CORE_BLOB_SHA,
        "protocol_decision": REGIME_CONSENSUS_PROTOCOL_DECISION,
        "protocol_version": REGIME_CONSENSUS_PROTOCOL_VERSION,
        "protocol_fingerprint": regime_consensus_protocol_fingerprint(),
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
            "full_fit_single_model": {
                "status": "FORBIDDEN_BY_DEC123",
                "fit_attempt_count": 0,
            },
            "logistic_regression": {
                "status": "EXCLUDED_BY_DEC112_DEC123",
                "fit_attempt_count": 0,
            },
        },
        "selection": {
            "status": "NO_REGIME_CONSENSUS_STABLE_MODEL_CHALLENGER",
            "row_count": 1,
            "consensus": _consensus(),
            "consensus_digest": FP,
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


class Exp048RegimeConsensusArtifactTests(unittest.TestCase):
    def test_source_binds_exact_protocol_core_and_loader(self) -> None:
        report = validate_regime_consensus_artifact_runner_sources(
            repository_root=ROOT
        )
        self.assertEqual(
            report["dec123_merged_commit"],
            DEC123_MERGED_COMMIT,
        )
        self.assertEqual(
            report["dec124_merged_commit"],
            DEC124_MERGED_COMMIT,
        )
        self.assertEqual(
            report["dec124_training_core_blob_sha"],
            DEC124_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC124_MERGED_COMMIT,
            "83c5b40eebae884cda9b2b65a8494dcd63bcbb7a",
        )
        self.assertEqual(
            DEC124_TRAINING_CORE_BLOB_SHA,
            "d902f9601ef3b04e0deaead18951d43350cb09be",
        )
        self.assertEqual(
            report["regime_consensus_model_artifact_runner_decision"],
            REGIME_CONSENSUS_MODEL_ARTIFACT_RUNNER_DECISION,
        )
        self.assertFalse(
            report[
                "authoritative_regime_consensus_model_result_execution_authorized"
            ]
        )
        self.assertFalse(
            report["regime_consensus_model_fit_authorized"]
        )

    def test_compile_and_validate_exact_18_cell_evidence(self) -> None:
        evidence = compile_regime_consensus_model_result_evidence(
            _all_cell_results(),
            code_commit=CODE_COMMIT,
        )
        summary = validate_regime_consensus_model_result_evidence(
            evidence,
            expected_code_commit=CODE_COMMIT,
        )
        self.assertTrue(
            summary[
                "regime_consensus_model_result_evidence_verified"
            ]
        )
        self.assertEqual(summary["verified_cell_count"], 18)
        self.assertEqual(summary["selected_cell_count"], 0)
        self.assertEqual(
            summary[
                "no_regime_consensus_stable_model_challenger_count"
            ],
            18,
        )
        self.assertEqual(
            summary["unavailable_budget_variant_count"],
            54,
        )
        self.assertEqual(
            summary["consensus_eligible_selection_row_count"],
            0,
        )
        self.assertFalse(summary["promotion_authorized"])
        self.assertFalse(summary["shadow_authorized"])
        self.assertFalse(summary["trading_authorized"])

    def test_incomplete_evidence_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "incomplete"):
            compile_regime_consensus_model_result_evidence(
                _all_cell_results()[:-1],
                code_commit=CODE_COMMIT,
            )

    def test_missing_regime_model_fails_closed(self) -> None:
        rows = _all_cell_results()
        models = rows[0]["fit"]["regime_models"]
        assert isinstance(models, dict)
        models.pop("fit_2017_2018")
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
            "regime fit inventory mismatch",
        ):
            compile_regime_consensus_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_consensus_accounting_tamper_fails_closed(self) -> None:
        rows = _all_cell_results()
        rows[0]["selection"]["consensus"][
            "consensus_eligible_row_count"
        ] = 1
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
            "consensus eligible count mismatch",
        ):
            compile_regime_consensus_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_variant_consensus_count_drift_fails_closed(self) -> None:
        rows = _all_cell_results()
        rows[0]["selection"]["variants"][0][
            "eligible_consensus_row_count"
        ] = 1
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
            "variant consensus eligible count mismatch",
        ):
            compile_regime_consensus_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_no_challenger_cannot_hide_stable_variant(self) -> None:
        rows = _all_cell_results()
        rows[0]["selection"]["consensus"] = {
            **_consensus(),
            "consensus_direction_counts": {
                "LONG": 1000,
                "SHORT": 0,
                "NO_TRADE": 0,
            },
            "consensus_eligible_row_count": 1000,
            "consensus_eligible_rate": 1.0,
            "minimum_consensus_confidence": 0.5,
            "maximum_consensus_confidence": 0.9,
            "row_count": 1000,
        }
        rows[0]["selection"]["row_count"] = 1000
        rows[0]["split_row_counts"]["selection"] = 1000
        rows[0]["selection"]["variants"][0] = _stable_variant(250)
        for item in rows[0]["selection"]["variants"][1:]:
            item["eligible_consensus_row_count"] = 1000
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
            "no-challenger status hides stable variant",
        ):
            compile_regime_consensus_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_full_fit_fallback_fails_closed(self) -> None:
        rows = _all_cell_results()
        rows[0]["fit"]["full_fit_single_model"] = {
            "status": "FITTED",
            "fit_attempt_count": 1,
        }
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
            "full-fit fallback record mismatch",
        ):
            compile_regime_consensus_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_authoritative_bundle_is_locked_before_loading(self) -> None:
        self.assertFalse(
            AUTHORITATIVE_REGIME_CONSENSUS_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(REGIME_CONSENSUS_MODEL_FIT_AUTHORIZED)
        with self.assertRaisesRegex(
            PermissionError,
            "DEC-125 source is non-executable",
        ):
            run_authoritative_regime_consensus_model_bundle(
                repository_root=ROOT,
                readiness={},
                feature_roots={},
                outcome_roots={},
                code_commit=CODE_COMMIT,
            )


if __name__ == "__main__":
    unittest.main()
