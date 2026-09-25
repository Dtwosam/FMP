from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

from fmp.market_learning.model_protocol import MODEL_CELLS
from fmp.market_learning.model_successor_fit_temporal_residual_breadth_utility_artifacts import (
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC199_MERGED_COMMIT,
    DEC199_TRAINING_CORE_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    compile_fit_temporal_residual_breadth_utility_model_result_evidence,
    run_authoritative_fit_temporal_residual_breadth_utility_model_bundle,
    validate_fit_temporal_residual_breadth_utility_artifact_contract_sources,
    validate_residual_breadth_cutoff,
)
from fmp.market_learning.model_successor_fit_temporal_residual_breadth_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_PROTOCOL_DECISION,
)
from fmp.market_learning.model_successor_fit_temporal_residual_breadth_utility_training import (
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_TRAINING_CORE_DECISION,
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
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_EXPERIMENT_ID
        ),
        "protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_PROTOCOL_DECISION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_TRAINING_CORE_DECISION
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
        },
        "selection": {
            "status": (
                "NO_FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_"
                "STABLE_MODEL_CHALLENGER"
            ),
            "fit_temporal_residual_breadth_utility_consensus": {
                "fit_temporal_residual_reference_count": 24,
                "fit_temporal_residual_breadth_bound_count_per_row": 12,
                "minimum_fit_temporal_residual_breadth": 0.0,
                "maximum_fit_temporal_residual_breadth": 1.0,
            },
            "fit_temporal_residual_breadth_utility_consensus_digest": SHA,
            "variants": [
                {
                    "candidate_budget_anchor": budget,
                    "status": "BUDGET_UNAVAILABLE",
                    "evaluation_status": "BUDGET_UNAVAILABLE",
                    "eligible_selection_row_count": 0,
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


class Exp055ArtifactContractTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(self) -> None:
        report = (
            validate_fit_temporal_residual_breadth_utility_artifact_contract_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
            "DEC-200",
        )
        self.assertEqual(
            DEC199_MERGED_COMMIT,
            "aaa80ce43a4dbd38e52e418dd16b61642d22b2b5",
        )
        self.assertEqual(
            report["dec199_training_core_blob_sha"],
            DEC199_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC199_TRAINING_CORE_BLOB_SHA,
            "c9517b7516940c78621448088c3933aa1c57e281",
        )
        self.assertFalse(
            report["authoritative_result_execution_authorized"]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_sextuple_cutoff_is_exact_and_finite(self) -> None:
        raw = {
            "selection_derived_residual_breadth_cutoff": 0.75,
            "selection_derived_residual_bound_cutoff": -0.2,
            "selection_derived_feature_support_cutoff": 0.8,
            "selection_derived_support_cutoff": 0.7,
            "selection_derived_pooled_calibrated_cutoff": 0.6,
            "selection_derived_raw_cutoff": 0.1,
        }
        self.assertEqual(
            validate_residual_breadth_cutoff(raw),
            (0.75, -0.2, 0.8, 0.7, 0.6, 0.1),
        )
        raw["selection_derived_residual_breadth_cutoff"] = 1.1
        with self.assertRaisesRegex(ValueError, "breadth cutoff out of range"):
            validate_residual_breadth_cutoff(raw)

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
            compile_fit_temporal_residual_breadth_utility_model_result_evidence(
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
            compile_fit_temporal_residual_breadth_utility_model_result_evidence(
                cells,
                code_commit="b" * 40,
            )

    def test_breadth_inventory_drift_fails_closed(self) -> None:
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
        fit["fit_temporal_residual_breadth_bound_count_per_row"] = 11
        supplied = dict(cells[0])
        supplied.pop("result_fingerprint")
        cells[0]["result_fingerprint"] = hashlib.sha256(
            _canonical_json(supplied)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "breadth_bound_count_per_row mismatch",
        ):
            compile_fit_temporal_residual_breadth_utility_model_result_evidence(
                cells,
                code_commit="b" * 40,
            )

    def test_authoritative_bundle_rejects_before_execution(self) -> None:
        self.assertFalse(
            AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        with self.assertRaisesRegex(
            PermissionError,
            "DEC-200 source is non-executable",
        ):
            run_authoritative_fit_temporal_residual_breadth_utility_model_bundle()

    def test_source_has_no_dispatch_or_broker_path(self) -> None:
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_breadth_utility_artifacts.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
