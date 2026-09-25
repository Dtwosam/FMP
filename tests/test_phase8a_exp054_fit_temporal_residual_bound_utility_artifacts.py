from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_protocol import MODEL_CELLS
from fmp.market_learning.model_successor_fit_temporal_residual_bound_utility_artifacts import (
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC186_MERGED_COMMIT,
    DEC186_TRAINING_CORE_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
    compile_fit_temporal_residual_bound_utility_model_result_evidence,
    run_authoritative_fit_temporal_residual_bound_utility_model_bundle,
    validate_fit_temporal_residual_bound_utility_artifact_contract_sources,
    validate_fit_temporal_residual_references,
    validate_residual_bound_cutoff,
)
from fmp.market_learning.model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_WINDOWS,
)
from fmp.market_learning.model_successor_temporal_jackknife_utility_protocol import (
    FINANCIAL_TARGET_COLUMNS,
    FIT_JACKKNIFE_VIEWS,
)

ROOT = Path(__file__).resolve().parents[1]
SHA = "a" * 64


def _refs() -> dict[str, object]:
    by_parent: dict[str, list[str]] = {}
    for raw in FIT_TEMPORAL_SUPPORT_WINDOWS:
        by_parent.setdefault(str(raw["parent_regime"]), []).append(str(raw["name"]))
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
                        "target_column": target,
                        "row_count": 10,
                        "prediction_digest": SHA,
                        "sorted_residual_digest": SHA,
                        "downside_residual": -0.25,
                    }
                    for window in by_parent[excluded]
                }
                for target in FINANCIAL_TARGET_COLUMNS
            },
        }
    return out


class Exp054ArtifactContractTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(self) -> None:
        report = validate_fit_temporal_residual_bound_utility_artifact_contract_sources(
            repository_root=ROOT
        )
        self.assertEqual(FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION, "DEC-187")
        self.assertEqual(DEC186_MERGED_COMMIT, "0fc2192152824ca2c3411517dff192d240ea9cd2")
        self.assertEqual(report["dec186_training_core_blob_sha"], DEC186_TRAINING_CORE_BLOB_SHA)
        self.assertFalse(report["authoritative_result_execution_authorized"])
        self.assertFalse(report["model_fit_authorized"])

    def test_residual_references_require_exact_24(self) -> None:
        fit = {
            "fit_temporal_residual_references": _refs(),
            "fit_temporal_residual_reference_count": 24,
        }
        self.assertEqual(validate_fit_temporal_residual_references(fit), 24)
        fit["fit_temporal_residual_reference_count"] = 23
        with self.assertRaisesRegex(ValueError, "reference count mismatch"):
            validate_fit_temporal_residual_references(fit)

    def test_residual_reference_identity_fails_closed(self) -> None:
        fit = {
            "fit_temporal_residual_references": _refs(),
            "fit_temporal_residual_reference_count": 24,
        }
        view = next(iter(fit["fit_temporal_residual_references"].values()))
        target = next(iter(view["targets"].values()))
        window = next(iter(target.values()))
        window["target_column"] = "wrong"
        with self.assertRaisesRegex(ValueError, "window identity mismatch"):
            validate_fit_temporal_residual_references(fit)

    def test_quintuple_cutoff_is_exact_and_finite(self) -> None:
        raw = {
            "selection_derived_residual_bound_cutoff": -0.2,
            "selection_derived_feature_support_cutoff": 0.8,
            "selection_derived_support_cutoff": 0.7,
            "selection_derived_pooled_calibrated_cutoff": 0.6,
            "selection_derived_raw_cutoff": 0.1,
        }
        self.assertEqual(validate_residual_bound_cutoff(raw), (-0.2, 0.8, 0.7, 0.6, 0.1))
        raw["selection_derived_feature_support_cutoff"] = 1.1
        with self.assertRaisesRegex(ValueError, "out of range"):
            validate_residual_bound_cutoff(raw)

    def test_complete_evidence_requires_432_residual_references(self) -> None:
        cells = [
            {
                "cell": {
                    "symbol": cell.symbol,
                    "timeframe": cell.timeframe,
                    "horizon_minutes": cell.horizon_minutes,
                },
                "fit": {
                    "fit_temporal_residual_references": _refs(),
                    "fit_temporal_residual_reference_count": 24,
                },
            }
            for cell in MODEL_CELLS
        ]
        evidence = compile_fit_temporal_residual_bound_utility_model_result_evidence(
            cells, code_commit="b" * 40
        )
        self.assertEqual(evidence["verified_fit_temporal_residual_reference_count"], 432)
        self.assertFalse(evidence["trading_authorized"])

    def test_authoritative_bundle_rejects_before_any_execution(self) -> None:
        self.assertFalse(
            AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        with self.assertRaisesRegex(PermissionError, "DEC-187 source is non-executable"):
            run_authoritative_fit_temporal_residual_bound_utility_model_bundle()

    def test_source_has_no_dispatch_or_broker_path(self) -> None:
        source = (
            ROOT / "src/fmp/market_learning/model_successor_fit_temporal_residual_bound_utility_artifacts.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
