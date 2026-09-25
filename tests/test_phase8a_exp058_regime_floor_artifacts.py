from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

from fmp.market_learning.model_protocol import MODEL_CELLS
from fmp.market_learning.model_successor_fit_temporal_residual_regime_floor_utility_artifacts import (
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC232_MERGED_COMMIT,
    DEC232_TRAINING_CORE_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    compile_fit_temporal_residual_regime_floor_utility_model_result_evidence,
    run_authoritative_fit_temporal_residual_regime_floor_utility_model_bundle,
    validate_fit_temporal_residual_regime_floor_utility_artifact_contract_sources,
    validate_residual_regime_floor_cutoff,
)
from fmp.market_learning.model_successor_fit_temporal_residual_regime_floor_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_DECISION,
)
from fmp.market_learning.model_successor_fit_temporal_residual_regime_floor_utility_training import (
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_TRAINING_CORE_DECISION,
)
from fmp.market_learning.model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_WINDOWS,
)
from fmp.market_learning.model_successor_regime_utility_artifacts import (
    _canonical_json,
)
from fmp.market_learning.model_successor_temporal_jackknife_utility_protocol import (
    FINANCIAL_TARGET_COLUMNS,
    FIT_JACKKNIFE_VIEWS,
)


ROOT = Path(__file__).resolve().parents[1]
SHA = "a" * 64


def _refs() -> dict[str, object]:
    by_parent: dict[str, list[tuple[str, str, str]]] = {}
    for raw in FIT_TEMPORAL_SUPPORT_WINDOWS:
        by_parent.setdefault(str(raw["parent_regime"]), []).append(
            (
                str(raw["name"]),
                str(raw["start"]),
                str(raw["end_exclusive"]),
            )
        )

    out: dict[str, object] = {}
    for raw in FIT_JACKKNIFE_VIEWS:
        name = str(raw["name"])
        excluded = str(raw["excluded_regime"])
        out[name] = {
            "status": "FROZEN",
            "included_regimes": list(raw["included_regimes"]),
            "excluded_regime": excluded,
            "targets": {
                target: {
                    window: {
                        "status": "FROZEN",
                        "name": window,
                        "parent_regime": excluded,
                        "start": start,
                        "end_exclusive": end,
                        "target_column": target,
                        "row_count": 10,
                        "prediction_digest": SHA,
                        "sorted_residual_digest": SHA,
                        "downside_residual": -0.25,
                    }
                    for window, start, end in by_parent[excluded]
                }
                for target in FINANCIAL_TARGET_COLUMNS
            },
        }
    return out


def _cell(symbol: str, timeframe: str, horizon: int) -> dict[str, object]:
    row: dict[str, object] = {
        "experiment_id": (
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_EXPERIMENT_ID
        ),
        "protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_DECISION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec231_merged_commit": (
            "a6926703d787a7fe0e2ba34261d14c4c4d362df2"
        ),
        "dec231_protocol_blob_sha": (
            "8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2"
        ),
        "predecessor_training_core_blob_sha": (
            "ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd"
        ),
        "cell": {
            "symbol": symbol,
            "timeframe": timeframe,
            "horizon_minutes": horizon,
        },
        "fit": {
            "regressor_count": 6,
            "calibration_reference_count": 6,
            "fit_temporal_support_reference_count": 24,
            "fit_temporal_feature_support_reference_count": 12,
            "fit_temporal_residual_references": _refs(),
            "fit_temporal_residual_reference_count": 24,
            "fit_temporal_residual_breadth_bound_count_per_row": 12,
            "fit_temporal_residual_lower_tail_bound_count_per_row": 12,
            "fit_temporal_residual_lower_tail_count": 3,
            "fit_temporal_residual_regime_count": 3,
            "fit_temporal_residual_windows_per_regime": 4,
            "fit_temporal_residual_regime_floor_bound_count_per_row": 12,
        },
        "selection": {
            "status": (
                "NO_FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_"
                "STABLE_MODEL_CHALLENGER"
            ),
            "fit_temporal_residual_regime_floor_utility_consensus": {
                "fit_temporal_residual_reference_count": 24,
                "fit_temporal_residual_breadth_bound_count_per_row": 12,
                "minimum_fit_temporal_residual_breadth": 0.0,
                "maximum_fit_temporal_residual_breadth": 1.0,
                "fit_temporal_residual_lower_tail_bound_count_per_row": 12,
                "fit_temporal_residual_lower_tail_count": 3,
            "fit_temporal_residual_regime_count": 3,
            "fit_temporal_residual_windows_per_regime": 4,
            "fit_temporal_residual_regime_floor_bound_count_per_row": 12,
                "minimum_fit_temporal_residual_lower_tail_mean": -0.5,
                "maximum_fit_temporal_residual_lower_tail_mean": 1.0,
                "fit_temporal_residual_regime_count": 3,
                "fit_temporal_residual_windows_per_regime": 4,
                "fit_temporal_residual_regime_floor_bound_count_per_row": 12,
                "minimum_fit_temporal_residual_regime_floor_utility": -0.25,
                "maximum_fit_temporal_residual_regime_floor_utility": 1.25,
            },
            "fit_temporal_residual_regime_floor_utility_consensus_digest": SHA,
            "variants": [
                {
                    "candidate_budget_anchor": budget,
                    "status": "BUDGET_UNAVAILABLE",
                    "evaluation_status": "BUDGET_UNAVAILABLE",
                    "eligible_selection_row_count": 0,
                    "selection_derived_residual_regime_floor_cutoff": None,
                    "selection_derived_residual_lower_tail_cutoff": None,
                    "selection_derived_residual_breadth_cutoff": None,
                    "selection_derived_residual_bound_cutoff": None,
                    "selection_derived_feature_support_cutoff": None,
                    "selection_derived_support_cutoff": None,
                    "selection_derived_pooled_calibrated_cutoff": None,
                    "selection_derived_raw_cutoff": None,
                    "aggregate_selection_gate_passed": False,
                    "selection_gate_passed": False,
                    "temporal_stability": {
                        "status": "BUDGET_UNAVAILABLE",
                        "windows": [],
                    },
                }
                for budget in (250, 500, 1000)
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
    row["result_fingerprint"] = hashlib.sha256(
        _canonical_json(row)
    ).hexdigest()
    return row


class Exp058RegimeFloorArtifactContractTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(self) -> None:
        report = (
            validate_fit_temporal_residual_regime_floor_utility_artifact_contract_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
            "DEC-233",
        )
        self.assertEqual(
            DEC232_MERGED_COMMIT,
            "24cb20bb0b1e3aa25f1ea87e1cfbba22587a0ae6",
        )
        self.assertEqual(
            report["dec232_training_core_blob_sha"],
            DEC232_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC232_TRAINING_CORE_BLOB_SHA,
            "77f2010574b3d8ecc958930d5bfadf7ddb4f2231",
        )
        self.assertFalse(
            report["authoritative_result_execution_authorized"]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_octuple_cutoff_is_exact_and_finite(self) -> None:
        raw = {
            "selection_derived_residual_regime_floor_cutoff": -0.6,
            "selection_derived_residual_lower_tail_cutoff": -0.4,
            "selection_derived_residual_breadth_cutoff": 0.75,
            "selection_derived_residual_bound_cutoff": -0.2,
            "selection_derived_feature_support_cutoff": 0.8,
            "selection_derived_support_cutoff": 0.7,
            "selection_derived_pooled_calibrated_cutoff": 0.6,
            "selection_derived_raw_cutoff": 0.1,
        }
        self.assertEqual(
            validate_residual_regime_floor_cutoff(raw),
            (-0.6, -0.4, 0.75, -0.2, 0.8, 0.7, 0.6, 0.1),
        )
        raw["selection_derived_residual_breadth_cutoff"] = 1.1
        with self.assertRaisesRegex(
            ValueError,
            "breadth cutoff out of range",
        ):
            validate_residual_regime_floor_cutoff(raw)

    def test_complete_evidence_requires_full_inherited_counts(self) -> None:
        cells = [
            _cell(
                cell.symbol,
                cell.timeframe,
                cell.horizon_minutes,
            )
            for cell in MODEL_CELLS
        ]
        evidence = (
            compile_fit_temporal_residual_regime_floor_utility_model_result_evidence(
                cells,
                code_commit="b" * 40,
            )
        )
        self.assertEqual(evidence["cell_count"], 18)
        self.assertEqual(evidence["verified_regressor_count"], 108)
        self.assertEqual(
            evidence["verified_pooled_calibration_reference_count"],
            108,
        )
        self.assertEqual(
            evidence["verified_fit_temporal_support_reference_count"],
            432,
        )
        self.assertEqual(
            evidence[
                "verified_fit_temporal_feature_support_reference_count"
            ],
            216,
        )
        self.assertEqual(
            evidence["verified_fit_temporal_residual_reference_count"],
            432,
        )
        self.assertEqual(
            evidence[
                "verified_fit_temporal_residual_breadth_bound_count_per_row"
            ],
            12,
        )
        self.assertEqual(
            evidence[
                "verified_fit_temporal_residual_lower_tail_bound_count_per_row"
            ],
            12,
        )
        self.assertEqual(
            evidence["verified_fit_temporal_residual_lower_tail_count"],
            3,
        )
        self.assertEqual(
            evidence["verified_fit_temporal_residual_regime_count"],
            3,
        )
        self.assertEqual(
            evidence["verified_fit_temporal_residual_windows_per_regime"],
            4,
        )
        self.assertEqual(
            evidence[
                "verified_fit_temporal_residual_regime_floor_bound_count_per_row"
            ],
            12,
        )
        self.assertEqual(len(evidence["evidence_fingerprint"]), 64)
        self.assertFalse(evidence["trading_authorized"])

    def test_cell_fingerprint_drift_fails_closed(self) -> None:
        cells = [
            _cell(
                cell.symbol,
                cell.timeframe,
                cell.horizon_minutes,
            )
            for cell in MODEL_CELLS
        ]
        cells[0]["result_fingerprint"] = "0" * 64
        with self.assertRaisesRegex(
            ValueError,
            "cell result fingerprint mismatch",
        ):
            compile_fit_temporal_residual_regime_floor_utility_model_result_evidence(
                cells,
                code_commit="b" * 40,
            )

    def test_lower_tail_inventory_drift_fails_closed(self) -> None:
        cells = [
            _cell(
                cell.symbol,
                cell.timeframe,
                cell.horizon_minutes,
            )
            for cell in MODEL_CELLS
        ]
        fit = cells[0]["fit"]
        assert isinstance(fit, dict)
        fit["fit_temporal_residual_lower_tail_count"] = 4
        supplied = dict(cells[0])
        supplied.pop("result_fingerprint")
        cells[0]["result_fingerprint"] = hashlib.sha256(
            _canonical_json(supplied)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "lower_tail_count mismatch",
        ):
            compile_fit_temporal_residual_regime_floor_utility_model_result_evidence(
                cells,
                code_commit="b" * 40,
            )

    def test_regime_floor_inventory_drift_fails_closed(self) -> None:
        cells = [
            _cell(
                cell.symbol,
                cell.timeframe,
                cell.horizon_minutes,
            )
            for cell in MODEL_CELLS
        ]
        fit = cells[0]["fit"]
        assert isinstance(fit, dict)
        fit["fit_temporal_residual_regime_count"] = 4
        supplied = dict(cells[0])
        supplied.pop("result_fingerprint")
        cells[0]["result_fingerprint"] = hashlib.sha256(
            _canonical_json(supplied)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "residual_regime_count mismatch",
        ):
            compile_fit_temporal_residual_regime_floor_utility_model_result_evidence(
                cells,
                code_commit="b" * 40,
            )

    def test_regime_floor_provenance_drift_fails_closed(self) -> None:
        cells = [
            _cell(
                cell.symbol,
                cell.timeframe,
                cell.horizon_minutes,
            )
            for cell in MODEL_CELLS
        ]
        cells[0]["dec231_protocol_blob_sha"] = "0" * 40
        supplied = dict(cells[0])
        supplied.pop("result_fingerprint")
        cells[0]["result_fingerprint"] = hashlib.sha256(
            _canonical_json(supplied)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "regime-floor protocol blob mismatch",
        ):
            compile_fit_temporal_residual_regime_floor_utility_model_result_evidence(
                cells,
                code_commit="b" * 40,
            )

    def test_authoritative_bundle_rejects_before_execution(self) -> None:
        self.assertFalse(
            AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        with self.assertRaisesRegex(
            PermissionError,
            "DEC-222 source is non-executable",
        ):
            run_authoritative_fit_temporal_residual_regime_floor_utility_model_bundle()

    def test_source_has_no_dispatch_or_broker_path(self) -> None:
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_floor_utility_artifacts.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
