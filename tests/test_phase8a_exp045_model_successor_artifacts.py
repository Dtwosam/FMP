from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from fmp.market_learning.model_protocol import MODEL_CELLS
from fmp.market_learning.model_successor_artifacts import (
    AUTHORITATIVE_FEATURE_ARTIFACTS,
    AUTHORITATIVE_OUTCOME_ARTIFACTS,
    AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED,
    FAILURE_REVIEW_BLOB_SHA,
    LEGACY_DATA_LOADER_BLOB_SHA,
    SUCCESSOR_MODEL_ARTIFACT_RUNNER_DECISION,
    SUCCESSOR_MODEL_ARTIFACT_RUNNER_VERSION,
    SUCCESSOR_MODEL_FIT_AUTHORIZED,
    SUCCESSOR_PROTOCOL_BLOB_SHA,
    SUCCESSOR_TRAINING_CORE_BLOB_SHA,
    compile_successor_model_result_evidence,
    load_successor_model_result_evidence,
    run_authoritative_successor_model_bundle,
    validate_successor_artifact_runner_sources,
    validate_successor_model_result_evidence,
    write_successor_model_result_evidence,
)
from fmp.market_learning.model_successor_protocol import (
    BASE_PROTOCOL_FINGERPRINT,
    PREDECESSOR_FAILED_MODEL_RUN_ID,
    SUCCESSOR_EXPERIMENT_ID,
    SUCCESSOR_PROTOCOL_DECISION,
    SUCCESSOR_PROTOCOL_VERSION,
    successor_protocol_fingerprint,
)
from fmp.market_learning.model_successor_training import (
    BASE_TRAINING_CORE_BLOB_SHA,
    SUCCESSOR_TRAINING_CORE_DECISION,
    SUCCESSOR_TRAINING_CORE_VERSION,
)


ROOT = Path(__file__).resolve().parents[1]
COMMIT = "f" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _cell_result(
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> dict[str, object]:
    variants = []
    for family in (
        "logistic_regression",
        "hist_gradient_boosting",
    ):
        for threshold in (0.5, 0.6, 0.7):
            variants.append(
                {
                    "model_family": family,
                    "confidence_threshold": threshold,
                    "family_fit_status": "FITTED",
                    "evaluation_status": "EVALUATED",
                    "selection_gate_passed": False,
                }
            )

    result: dict[str, object] = {
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "training_core_version": (
            SUCCESSOR_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            SUCCESSOR_TRAINING_CORE_DECISION
        ),
        "base_training_core_blob_sha": (
            BASE_TRAINING_CORE_BLOB_SHA
        ),
        "protocol_decision": SUCCESSOR_PROTOCOL_DECISION,
        "protocol_version": SUCCESSOR_PROTOCOL_VERSION,
        "protocol_fingerprint": (
            successor_protocol_fingerprint()
        ),
        "base_protocol_fingerprint": (
            BASE_PROTOCOL_FINGERPRINT
        ),
        "predecessor_failed_model_run_id": (
            PREDECESSOR_FAILED_MODEL_RUN_ID
        ),
        "prior_result_informed": True,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "cell": {
            "symbol": symbol,
            "timeframe": timeframe,
            "horizon_minutes": horizon_minutes,
        },
        "processed_manifest_sha256": "9" * 64,
        "joined_row_count": 1000,
        "split_row_counts": {
            "fit": 600,
            "selection": 150,
            "validation": 150,
            "retrospective_holdout": 100,
        },
        "fit": {
            "row_count": 600,
            "target_class_counts": {
                "LONG": 200,
                "SHORT": 200,
                "NO_TRADE": 200,
            },
            "families": {
                "logistic_regression": {
                    "status": "FITTED",
                    "fit_attempt_count": 1,
                    "preprocessor_fingerprint": "a" * 64,
                    "model_fingerprint": "b" * 64,
                },
                "hist_gradient_boosting": {
                    "status": "FITTED",
                    "fit_attempt_count": 1,
                    "preprocessor_fingerprint": "c" * 64,
                    "model_fingerprint": "d" * 64,
                },
            },
        },
        "selection": {
            "status": "NO_MODEL_CHALLENGER",
            "row_count": 150,
            "classification_by_family": {},
            "probability_digest_by_family": {},
            "variants": variants,
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
    result["result_fingerprint"] = _sha256(result)
    return result


def _all_results() -> list[dict[str, object]]:
    return [
        _cell_result(
            symbol=cell.symbol,
            timeframe=cell.timeframe,
            horizon_minutes=cell.horizon_minutes,
        )
        for cell in MODEL_CELLS
    ]


class Exp045SuccessorArtifactRunnerTests(unittest.TestCase):
    def test_source_identity_and_artifact_inventory_are_exact(self) -> None:
        report = validate_successor_artifact_runner_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            report["legacy_data_loader_blob_sha"],
            LEGACY_DATA_LOADER_BLOB_SHA,
        )
        self.assertEqual(
            report["failure_review_blob_sha"],
            FAILURE_REVIEW_BLOB_SHA,
        )
        self.assertEqual(
            report["successor_protocol_blob_sha"],
            SUCCESSOR_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            report["successor_training_core_blob_sha"],
            SUCCESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            report["successor_model_artifact_runner_decision"],
            "DEC-097",
        )
        self.assertEqual(
            len(AUTHORITATIVE_FEATURE_ARTIFACTS),
            9,
        )
        self.assertEqual(
            len(AUTHORITATIVE_OUTCOME_ARTIFACTS),
            9,
        )
        self.assertFalse(
            report[
                "authoritative_successor_model_result_execution_authorized"
            ]
        )
        self.assertFalse(
            report["successor_model_fit_authorized"]
        )
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_source_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "src/fmp/market_learning"
            target.mkdir(parents=True)
            for name in (
                "model_artifacts.py",
                "model_run_failure_review.py",
                "model_successor_protocol.py",
                "model_successor_training.py",
            ):
                shutil.copy2(
                    ROOT / "src/fmp/market_learning" / name,
                    target / name,
                )

            validated = (
                validate_successor_artifact_runner_sources(
                    repository_root=root,
                )
            )
            self.assertEqual(
                validated["successor_training_core_blob_sha"],
                SUCCESSOR_TRAINING_CORE_BLOB_SHA,
            )

            protocol = target / "model_successor_protocol.py"
            protocol.write_text(
                protocol.read_text(encoding="utf-8")
                + "\n# drift\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "successor_protocol Git blob mismatch",
            ):
                validate_successor_artifact_runner_sources(
                    repository_root=root,
                )

    def test_authoritative_bundle_refuses_before_artifact_access_or_fit(self) -> None:
        import fmp.market_learning.model_successor_artifacts as artifacts

        self.assertFalse(
            AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(SUCCESSOR_MODEL_FIT_AUTHORIZED)

        with (
            patch.object(
                artifacts,
                "validate_authoritative_readiness",
            ) as readiness_spy,
            patch.object(
                artifacts,
                "load_authoritative_cell_artifacts",
            ) as load_spy,
            patch.object(
                artifacts,
                "run_successor_model_cell_core",
            ) as fit_spy,
        ):
            with self.assertRaisesRegex(
                PermissionError,
                "non-executable",
            ):
                run_authoritative_successor_model_bundle(
                    repository_root=ROOT,
                    readiness={},
                    feature_roots={},
                    outcome_roots={},
                    code_commit=COMMIT,
                )

        readiness_spy.assert_not_called()
        load_spy.assert_not_called()
        fit_spy.assert_not_called()

    def test_aggregate_evidence_requires_all_18_exact_cells(self) -> None:
        results = _all_results()
        evidence = compile_successor_model_result_evidence(
            results,
            code_commit=COMMIT,
        )
        self.assertEqual(
            evidence["runner_version"],
            SUCCESSOR_MODEL_ARTIFACT_RUNNER_VERSION,
        )
        self.assertEqual(
            evidence["runner_decision"],
            SUCCESSOR_MODEL_ARTIFACT_RUNNER_DECISION,
        )
        self.assertEqual(
            evidence["experiment_id"],
            SUCCESSOR_EXPERIMENT_ID,
        )
        self.assertEqual(
            evidence["verified_cell_count"],
            18,
        )
        self.assertEqual(len(evidence["cells"]), 18)
        self.assertTrue(evidence["prior_result_informed"])
        self.assertFalse(evidence["untouched_oos"])
        self.assertFalse(evidence["model_fit_authorized"])
        self.assertFalse(evidence["promotion_authorized"])
        self.assertFalse(evidence["trading_authorized"])
        self.assertEqual(
            len(evidence["evidence_fingerprint"]),
            64,
        )

        with self.assertRaisesRegex(
            ValueError,
            "incomplete",
        ):
            compile_successor_model_result_evidence(
                results[:-1],
                code_commit=COMMIT,
            )

    def test_cell_fingerprint_tamper_fails_closed(self) -> None:
        results = _all_results()
        results[0]["joined_row_count"] = 1001
        with self.assertRaisesRegex(
            ValueError,
            "result fingerprint mismatch",
        ):
            compile_successor_model_result_evidence(
                results,
                code_commit=COMMIT,
            )

    def test_logistic_nonconvergence_record_is_allowed_but_not_promoted(self) -> None:
        results = _all_results()
        first = results[0]
        fit = first["fit"]
        assert isinstance(fit, dict)
        families = fit["families"]
        assert isinstance(families, dict)
        families["logistic_regression"] = {
            "status": "FAILED_NON_CONVERGENCE",
            "failure_reason": "LBFGS_MAX_ITER_REACHED",
            "fit_attempt_count": 1,
            "retry_authorized": False,
        }
        selection = first["selection"]
        assert isinstance(selection, dict)
        variants = selection["variants"]
        assert isinstance(variants, list)
        for row in variants:
            if (
                isinstance(row, dict)
                and row.get("model_family")
                == "logistic_regression"
            ):
                row["family_fit_status"] = (
                    "FAILED_NON_CONVERGENCE"
                )
                row["evaluation_status"] = (
                    "FAMILY_UNAVAILABLE"
                )
                row["failure_reason"] = (
                    "LBFGS_MAX_ITER_REACHED"
                )
                row["selection_gate_passed"] = False
        first.pop("result_fingerprint")
        first["result_fingerprint"] = _sha256(first)

        evidence = compile_successor_model_result_evidence(
            results,
            code_commit=COMMIT,
        )
        matching = [
            row
            for row in evidence["cells"]
            if row["logistic_fit_status"]
            == "FAILED_NON_CONVERGENCE"
        ]
        self.assertEqual(len(matching), 1)
        self.assertFalse(evidence["promotion_authorized"])

    def test_variant_slot_tamper_fails_closed_even_with_recomputed_cell_fingerprint(self) -> None:
        results = _all_results()
        first = results[0]
        selection = first["selection"]
        assert isinstance(selection, dict)
        variants = selection["variants"]
        assert isinstance(variants, list)
        first_variant = variants[0]
        assert isinstance(first_variant, dict)
        first_variant["confidence_threshold"] = 0.6
        first.pop("result_fingerprint")
        first["result_fingerprint"] = _sha256(first)

        with self.assertRaisesRegex(
            ValueError,
            "duplicate EXP-045 model variant slot",
        ):
            compile_successor_model_result_evidence(
                results,
                code_commit=COMMIT,
            )

    def test_persisted_aggregate_evidence_revalidates_and_tamper_fails(self) -> None:
        evidence = compile_successor_model_result_evidence(
            _all_results(),
            code_commit=COMMIT,
        )
        summary = validate_successor_model_result_evidence(
            evidence,
            expected_code_commit=COMMIT,
        )
        self.assertTrue(
            summary["successor_model_result_evidence_verified"]
        )
        self.assertEqual(summary["verified_cell_count"], 18)
        self.assertTrue(summary["prior_result_informed"])
        self.assertFalse(summary["untouched_oos"])
        self.assertFalse(summary["promotion_authorized"])
        self.assertFalse(summary["trading_authorized"])

        tampered = json.loads(json.dumps(evidence))
        tampered["cells"][0]["selection_status"] = "SELECTED"
        with self.assertRaisesRegex(
            ValueError,
            "content fingerprint mismatch",
        ):
            validate_successor_model_result_evidence(
                tampered,
                expected_code_commit=COMMIT,
            )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "successor-evidence.json"
            path.write_text(
                json.dumps(
                    evidence,
                    sort_keys=True,
                    indent=2,
                    allow_nan=False,
                )
                + "\n",
                encoding="utf-8",
            )
            loaded = load_successor_model_result_evidence(
                path,
                expected_code_commit=COMMIT,
            )
            self.assertEqual(
                loaded["evidence_fingerprint"],
                evidence["evidence_fingerprint"],
            )

    def test_aggregate_evidence_is_deterministic_and_write_is_create_only(self) -> None:
        first = compile_successor_model_result_evidence(
            _all_results(),
            code_commit=COMMIT,
        )
        second = compile_successor_model_result_evidence(
            list(reversed(_all_results())),
            code_commit=COMMIT,
        )
        self.assertEqual(first, second)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            write_successor_model_result_evidence(
                first,
                path=path,
            )
            write_successor_model_result_evidence(
                first,
                path=path,
            )
            changed = dict(first)
            changed["code_commit"] = "e" * 40
            with self.assertRaisesRegex(
                ValueError,
                "conflicting existing",
            ):
                write_successor_model_result_evidence(
                    changed,
                    path=path,
                )

    def test_source_has_no_workflow_or_dispatch_authorization(self) -> None:
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_artifacts.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertIn(
            "AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED = False",
            source,
        )
        workflow = (
            ROOT
            / ".github/workflows/"
            "phase8a-exp045-model-training.yml"
        )
        self.assertTrue(workflow.exists())
        workflow_text = workflow.read_text(encoding="utf-8")
        self.assertIn(
            "Require separately authorized EXP-045 result execution",
            workflow_text,
        )


if __name__ == "__main__":
    unittest.main()
