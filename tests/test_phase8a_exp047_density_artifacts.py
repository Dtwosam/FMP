from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_protocol import MODEL_CELLS
from fmp.market_learning.model_successor_density_artifacts import (
    AUTHORITATIVE_DENSITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC114_MERGED_COMMIT,
    DEC114_TRAINING_CORE_BLOB_SHA,
    DENSITY_MODEL_ARTIFACT_RUNNER_DECISION,
    DENSITY_MODEL_FIT_AUTHORIZED,
    _canonical_json,
    _sha256,
    compile_density_model_result_evidence,
    run_authoritative_density_model_bundle,
    validate_density_artifact_runner_sources,
    validate_density_model_result_evidence,
)
from fmp.market_learning.model_successor_density_protocol import (
    DENSITY_PROTOCOL_DECISION,
    DENSITY_PROTOCOL_VERSION,
    DENSITY_SUCCESSOR_EXPERIMENT_ID,
    density_protocol_fingerprint,
)
from fmp.market_learning.model_successor_density_training import (
    BASE_TRAINING_CORE_BLOB_SHA,
    DEC113_MERGED_COMMIT,
    DEC113_PROTOCOL_BLOB_SHA,
    DENSITY_TRAINING_CORE_DECISION,
    DENSITY_TRAINING_CORE_VERSION,
)


ROOT = Path(__file__).resolve().parents[1]
CODE_COMMIT = "a" * 40
FP = "b" * 64
PREPROCESSOR_FP = "c" * 64
MODEL_FP = "d" * 64


def _unavailable_variant(budget: int) -> dict[str, object]:
    return {
        "model_family": "hist_gradient_boosting",
        "candidate_budget_anchor": budget,
        "evaluation_status": "BUDGET_UNAVAILABLE",
        "status": "UNAVAILABLE_INSUFFICIENT_DIRECTIONAL_ROWS",
        "eligible_directional_row_count": budget - 1,
        "selection_derived_cutoff": None,
        "aggregate_selection_gate_passed": False,
        "temporal_stability": {
            "status": "BUDGET_UNAVAILABLE",
            "minimum_directional_candidate_share_per_window": 0.10,
            "windows": [],
        },
        "selection_gate_passed": False,
    }


def _cell_result(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> dict[str, object]:
    result: dict[str, object] = {
        "experiment_id": DENSITY_SUCCESSOR_EXPERIMENT_ID,
        "training_core_version": DENSITY_TRAINING_CORE_VERSION,
        "training_core_decision": DENSITY_TRAINING_CORE_DECISION,
        "dec113_merged_commit": DEC113_MERGED_COMMIT,
        "dec113_protocol_blob_sha": DEC113_PROTOCOL_BLOB_SHA,
        "base_training_core_blob_sha": BASE_TRAINING_CORE_BLOB_SHA,
        "protocol_decision": DENSITY_PROTOCOL_DECISION,
        "protocol_version": DENSITY_PROTOCOL_VERSION,
        "protocol_fingerprint": density_protocol_fingerprint(),
        "prior_result_informed": True,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "cell": {
            "symbol": symbol,
            "timeframe": timeframe,
            "horizon_minutes": horizon,
        },
        "processed_manifest_sha256": FP,
        "joined_row_count": 1,
        "split_row_counts": {
            "fit": 1,
            "selection": 1,
            "validation": 1,
            "retrospective_holdout": 1,
        },
        "fit": {
            "row_count": 1,
            "target_class_counts": {
                "LONG": 1,
                "SHORT": 1,
                "NO_TRADE": 1,
            },
            "families": {
                "hist_gradient_boosting": {
                    "status": "FITTED",
                    "fit_attempt_count": 1,
                    "preprocessor_fingerprint": PREPROCESSOR_FP,
                    "model_fingerprint": MODEL_FP,
                },
                "logistic_regression": {
                    "status": "EXCLUDED_BY_DEC112_DEC113",
                    "fit_attempt_count": 0,
                },
            },
        },
        "selection": {
            "status": "NO_DENSITY_STABLE_MODEL_CHALLENGER",
            "row_count": 1,
            "classification": {},
            "probability_digest": FP,
            "variants": [
                _unavailable_variant(250),
                _unavailable_variant(500),
                _unavailable_variant(1000),
            ],
            "selected_variant": None,
        },
        "validation": {
            "status": "LOCKED_NO_SELECTION",
        },
        "retrospective_holdout": {
            "status": "LOCKED_NO_SELECTION",
        },
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


class Exp047DensityArtifactContractTests(unittest.TestCase):
    def test_source_binds_exact_protocol_core_and_loader(
        self,
    ) -> None:
        report = validate_density_artifact_runner_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            report["dec113_merged_commit"],
            DEC113_MERGED_COMMIT,
        )
        self.assertEqual(
            report["dec114_merged_commit"],
            DEC114_MERGED_COMMIT,
        )
        self.assertEqual(
            report["dec113_protocol_blob_sha"],
            DEC113_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            report["dec114_training_core_blob_sha"],
            DEC114_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC114_MERGED_COMMIT,
            "3e236169ae71074630ece7d78516d5e6586abe1f",
        )
        self.assertEqual(
            DEC114_TRAINING_CORE_BLOB_SHA,
            "8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945",
        )
        self.assertEqual(
            report["density_protocol_fingerprint"],
            density_protocol_fingerprint(),
        )
        self.assertEqual(
            report["density_model_artifact_runner_decision"],
            DENSITY_MODEL_ARTIFACT_RUNNER_DECISION,
        )
        self.assertFalse(
            report[
                "authoritative_density_model_result_execution_authorized"
            ]
        )
        self.assertFalse(report["density_model_fit_authorized"])

    def test_compile_and_validate_exact_18_cell_evidence(
        self,
    ) -> None:
        evidence = compile_density_model_result_evidence(
            _all_cell_results(),
            code_commit=CODE_COMMIT,
        )
        summary = validate_density_model_result_evidence(
            evidence,
            expected_code_commit=CODE_COMMIT,
        )

        self.assertTrue(
            summary["density_model_result_evidence_verified"]
        )
        self.assertEqual(
            summary["verified_cell_count"],
            18,
        )
        self.assertEqual(
            summary["selected_cell_count"],
            0,
        )
        self.assertEqual(
            summary[
                "no_density_stable_model_challenger_count"
            ],
            18,
        )
        self.assertEqual(
            summary["unavailable_budget_variant_count"],
            54,
        )
        self.assertEqual(
            summary["stable_selection_pass_variant_count"],
            0,
        )
        self.assertFalse(
            summary["promotion_authorized"]
        )
        self.assertFalse(summary["shadow_authorized"])
        self.assertFalse(summary["trading_authorized"])

    def test_incomplete_evidence_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "incomplete",
        ):
            compile_density_model_result_evidence(
                _all_cell_results()[:-1],
                code_commit=CODE_COMMIT,
            )

    def test_cell_fingerprint_tamper_fails_closed(self) -> None:
        rows = _all_cell_results()
        rows[0]["selection"]["status"] = "SELECTED"

        with self.assertRaisesRegex(
            ValueError,
            "selected cell lacks variant identity|fingerprint",
        ):
            compile_density_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_logistic_reintroduction_fails_closed(self) -> None:
        rows = _all_cell_results()
        families = rows[0]["fit"]["families"]
        assert isinstance(families, dict)
        families["logistic_regression"] = {
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
            "logistic exclusion record mismatch",
        ):
            compile_density_model_result_evidence(
                rows,
                code_commit=CODE_COMMIT,
            )

    def test_authoritative_bundle_is_locked_before_loading(
        self,
    ) -> None:
        self.assertFalse(
            AUTHORITATIVE_DENSITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(DENSITY_MODEL_FIT_AUTHORIZED)

        with self.assertRaisesRegex(
            PermissionError,
            "DEC-115 source is non-executable",
        ):
            run_authoritative_density_model_bundle(
                repository_root=ROOT,
                readiness={},
                feature_roots={},
                outcome_roots={},
                code_commit=CODE_COMMIT,
            )


if __name__ == "__main__":
    unittest.main()
