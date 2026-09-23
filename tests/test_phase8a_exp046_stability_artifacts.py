from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fmp.market_learning.model_successor_stability_artifacts as artifacts
from fmp.market_learning.model_protocol import MODEL_CELLS
from fmp.market_learning.model_successor_stability_artifacts import (
    AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC105_MERGED_COMMIT,
    DEC105_TRAINING_CORE_BLOB_SHA,
    LEGACY_DATA_LOADER_BLOB_SHA,
    STABILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    STABILITY_MODEL_FIT_AUTHORIZED,
    _validate_status_chain,
    _validate_window,
    compile_stability_model_result_evidence,
    load_stability_model_result_evidence,
    run_authoritative_stability_model_bundle,
    validate_stability_artifact_runner_sources,
    validate_stability_model_result_evidence,
    write_stability_model_result_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
COMMIT = "a" * 40
RESULT_FP = "b" * 64


def _summary_for(cell) -> dict[str, object]:
    return {
        "symbol": cell.symbol,
        "timeframe": cell.timeframe,
        "horizon_minutes": cell.horizon_minutes,
        "result_fingerprint": RESULT_FP,
        "selection_status": "NO_STABLE_MODEL_CHALLENGER",
        "validation_status": "LOCKED_NO_SELECTION",
        "retrospective_holdout_status": "LOCKED_NO_SELECTION",
        "logistic_fit_status": "FITTED",
        "hgb_fit_status": "FITTED",
        "aggregate_selection_pass_variant_count": 1,
        "stable_selection_pass_variant_count": 0,
        "stability_reject_variant_count": 1,
    }


class Exp046StabilityArtifactTests(unittest.TestCase):
    def test_sources_bind_exact_loader_and_merged_core(
        self,
    ) -> None:
        report = validate_stability_artifact_runner_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            report["legacy_data_loader_blob_sha"],
            LEGACY_DATA_LOADER_BLOB_SHA,
        )
        self.assertEqual(
            report["dec105_training_core_blob_sha"],
            DEC105_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            report["dec105_merged_commit"],
            DEC105_MERGED_COMMIT,
        )
        self.assertEqual(
            report["stability_model_artifact_runner_decision"],
            STABILITY_MODEL_ARTIFACT_RUNNER_DECISION,
        )
        self.assertEqual(
            STABILITY_MODEL_ARTIFACT_RUNNER_DECISION,
            "DEC-106",
        )
        self.assertFalse(
            report[
                "authoritative_stability_model_result_execution_authorized"
            ]
        )
        self.assertFalse(
            report["stability_model_fit_authorized"]
        )
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_status_chain_preserves_stability_locking(
        self,
    ) -> None:
        _validate_status_chain(
            selection="NO_STABLE_MODEL_CHALLENGER",
            validation="LOCKED_NO_SELECTION",
            holdout="LOCKED_NO_SELECTION",
        )
        _validate_status_chain(
            selection="SELECTED",
            validation="REJECT",
            holdout="LOCKED_VALIDATION_REJECT",
        )
        _validate_status_chain(
            selection="SELECTED",
            validation="PASS",
            holdout="PASS",
        )
        with self.assertRaisesRegex(
            ValueError,
            "no-stable-challenger validation",
        ):
            _validate_status_chain(
                selection="NO_STABLE_MODEL_CHALLENGER",
                validation="PASS",
                holdout="PASS",
            )

    def test_window_validator_recomputes_share_and_financial_gate(
        self,
    ) -> None:
        window = {
            "name": "selection_2021_h1",
            "start": "2021-01-01",
            "end_exclusive": "2021-07-01",
            "row_count": 100,
            "metrics": {
                "directional_candidate_count": 40,
                "total_net_pips": 120.0,
                "mean_net_pips": 3.0,
                "gross_positive_pips": 150.0,
                "absolute_gross_negative_pips": 30.0,
            },
            "gate": {
                "passed": True,
                "criteria": {
                    "directional_candidate_share>=0.10": True,
                    "total_net_pips>0": True,
                    "mean_net_pips>0": True,
                    (
                        "gross_positive_pips>"
                        "absolute_gross_negative_pips"
                    ): True,
                },
                "directional_candidate_share": 0.2,
            },
        }
        self.assertTrue(
            _validate_window(
                window,
                expected={
                    "name": "selection_2021_h1",
                    "start": "2021-01-01",
                    "end_exclusive": "2021-07-01",
                },
                full_selection_candidate_count=200,
            )
        )

        tampered = {
            **window,
            "gate": {
                **window["gate"],
                "directional_candidate_share": 0.21,
            },
        }
        with self.assertRaisesRegex(
            ValueError,
            "candidate-share mismatch",
        ):
            _validate_window(
                tampered,
                expected={
                    "name": "selection_2021_h1",
                    "start": "2021-01-01",
                    "end_exclusive": "2021-07-01",
                },
                full_selection_candidate_count=200,
            )

    @patch.object(
        artifacts,
        "_validate_stability_cell_result",
    )
    def test_complete_18_cell_evidence_round_trips(
        self,
        validate_cell,
    ) -> None:
        summaries = {
            (
                cell.symbol,
                cell.timeframe,
                cell.horizon_minutes,
            ): _summary_for(cell)
            for cell in MODEL_CELLS
        }

        def side_effect(raw):
            identity = (
                raw["cell"]["symbol"],
                raw["cell"]["timeframe"],
                raw["cell"]["horizon_minutes"],
            )
            return summaries[identity]

        validate_cell.side_effect = side_effect
        rows = [
            {
                "cell": {
                    "symbol": cell.symbol,
                    "timeframe": cell.timeframe,
                    "horizon_minutes": cell.horizon_minutes,
                }
            }
            for cell in MODEL_CELLS
        ]

        evidence = compile_stability_model_result_evidence(
            rows,
            code_commit=COMMIT,
        )
        report = validate_stability_model_result_evidence(
            evidence,
            expected_code_commit=COMMIT,
        )
        self.assertTrue(
            report[
                "stability_model_result_evidence_verified"
            ]
        )
        self.assertEqual(report["verified_cell_count"], 18)
        self.assertEqual(
            report["selected_cell_count"],
            0,
        )
        self.assertEqual(
            report["no_stable_model_challenger_count"],
            18,
        )
        self.assertEqual(
            report[
                "aggregate_selection_pass_variant_count"
            ],
            18,
        )
        self.assertEqual(
            report["stable_selection_pass_variant_count"],
            0,
        )
        self.assertEqual(
            report["stability_reject_variant_count"],
            18,
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            write_stability_model_result_evidence(
                evidence,
                path=path,
            )
            loaded = load_stability_model_result_evidence(
                path,
                expected_code_commit=COMMIT,
            )
            self.assertEqual(loaded, evidence)

    @patch.object(
        artifacts,
        "_validate_stability_cell_result",
    )
    def test_incomplete_evidence_fails_closed(
        self,
        validate_cell,
    ) -> None:
        cells = list(MODEL_CELLS)
        summaries = {
            (
                cell.symbol,
                cell.timeframe,
                cell.horizon_minutes,
            ): _summary_for(cell)
            for cell in cells
        }

        def side_effect(raw):
            identity = (
                raw["cell"]["symbol"],
                raw["cell"]["timeframe"],
                raw["cell"]["horizon_minutes"],
            )
            return summaries[identity]

        validate_cell.side_effect = side_effect
        rows = [
            {
                "cell": {
                    "symbol": cell.symbol,
                    "timeframe": cell.timeframe,
                    "horizon_minutes": cell.horizon_minutes,
                }
            }
            for cell in cells[:-1]
        ]

        with self.assertRaisesRegex(
            ValueError,
            "incomplete",
        ):
            compile_stability_model_result_evidence(
                rows,
                code_commit=COMMIT,
            )

    @patch.object(
        artifacts,
        "validate_authoritative_readiness",
    )
    def test_authoritative_bundle_is_closed_before_loading(
        self,
        readiness_validator,
    ) -> None:
        self.assertFalse(
            AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(STABILITY_MODEL_FIT_AUTHORIZED)

        with self.assertRaisesRegex(
            PermissionError,
            "non-executable",
        ):
            run_authoritative_stability_model_bundle(
                repository_root=ROOT,
                readiness={},
                feature_roots={},
                outcome_roots={},
                code_commit=COMMIT,
            )
        readiness_validator.assert_not_called()

    def test_source_has_no_dispatch_or_broker_action(
        self,
    ) -> None:
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_stability_artifacts.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("order_send", source)


if __name__ == "__main__":
    unittest.main()
