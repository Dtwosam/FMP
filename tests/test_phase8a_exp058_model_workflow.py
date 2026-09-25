from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_regime_floor_utility_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC231_MERGED_COMMIT,
    DEC231_PROTOCOL_BLOB_SHA,
    DEC232_CORE_BLOB_SHA,
    DEC232_MERGED_COMMIT,
    DEC233_RUNNER_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_CLI_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_EXECUTION_GATE_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_FIT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_WORKFLOW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    TRADING_AUTHORIZED,
    build_fit_temporal_residual_regime_floor_utility_model_workflow_source_gate,
    require_authoritative_fit_temporal_residual_regime_floor_utility_model_execution,
    validate_fit_temporal_residual_regime_floor_utility_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp058-fit-temporal-residual-lower-tail-utility-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp058_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp058-model-run.txt"


class Exp058ResidualLowerTailWorkflowTests(unittest.TestCase):
    def test_exact_sources_are_frozen_but_execution_closed(self) -> None:
        source = (
            validate_fit_temporal_residual_regime_floor_utility_model_workflow_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_EXECUTION_GATE_DECISION,
            "DEC-234",
        )
        self.assertEqual(
            source[
                "fit_temporal_residual_regime_floor_utility_model_execution_gate_decision"
            ],
            "DEC-234",
        )
        self.assertEqual(
            DEC231_MERGED_COMMIT,
            "a6926703d787a7fe0e2ba34261d14c4c4d362df2",
        )
        self.assertEqual(
            DEC232_MERGED_COMMIT,
            "24cb20bb0b1e3aa25f1ea87e1cfbba22587a0ae6",
        )
        self.assertEqual(
            source["dec233_merged_commit"],
            "5425184a53b2bd5241291f9d561f47b69ca4d134",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_floor_utility_runner_blob_sha"],
            DEC233_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            DEC233_RUNNER_BLOB_SHA,
            "5a34f354b68e14bb7116c79f15f9cfebe149a811",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_floor_utility_core_blob_sha"],
            DEC232_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC232_CORE_BLOB_SHA,
            "77f2010574b3d8ecc958930d5bfadf7ddb4f2231",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_floor_utility_protocol_blob_sha"],
            DEC231_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC231_PROTOCOL_BLOB_SHA,
            "8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_floor_utility_workflow_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_WORKFLOW_BLOB_SHA,
            "78e9bf66ade5f6fb42ebe27e28b7ba24f36741b8",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_floor_utility_cli_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_CLI_BLOB_SHA,
            "e35a6ee0ff11bd3928b3bf05bf19f3572f64952c",
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )
        self.assertEqual(source["authorized_python_version"], AUTHORIZED_PYTHON_VERSION)

        gate = build_fit_temporal_residual_regime_floor_utility_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
        )
        self.assertTrue(
            gate[
                "fit_temporal_residual_regime_floor_utility_model_workflow_source_frozen"
            ]
        )
        self.assertFalse(
            gate[
                "fit_temporal_residual_regime_floor_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertFalse(
            gate[
                "authoritative_fit_temporal_residual_regime_floor_utility_model_result_execution_authorized"
            ]
        )
        self.assertFalse(gate["model_protocol_result_authorized"])
        self.assertFalse(gate["model_fit_authorized"])
        self.assertFalse(gate["promotion_authorized"])
        self.assertFalse(gate["shadow_authorized"])
        self.assertFalse(gate["trading_authorized"])

        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertFalse(
            AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertFalse(FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_FIT_AUTHORIZED)
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "DEC-234 freezes EXP-058 workflow source",
        ):
            require_authoritative_fit_temporal_residual_regime_floor_utility_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )

    def test_workflow_is_manual_main_only_and_input_free(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp058-fit-temporal-residual-lower-tail-utility-model-training",
            text,
        )
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("inputs:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn(
            'test "$GITHUB_EVENT_NAME" = "workflow_dispatch"',
            text,
        )
        self.assertIn(
            'test "$GITHUB_REF" = "refs/heads/main"',
            text,
        )
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)

    def test_workflow_has_no_first_run_guard_before_authorization(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn(
            "Reject any prior manual main EXP-058 model run",
            text,
        )
        self.assertNotIn(
            "prior manual-main EXP-058 model run exists",
            text,
        )
        self.assertIn(
            "Require separately authorized EXP-058 result execution",
            text,
        )

    def test_workflow_uses_exact_matrix_and_pinned_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(text.count("- symbol: "), 9)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            self.assertEqual(text.count(f"- symbol: {symbol}"), 3)
        for timeframe in ("5m", "15m", "1h"):
            self.assertEqual(text.count(f"timeframe: {timeframe}"), 3)
        self.assertEqual(text.count('python-version: "3.12.14"'), 3)
        self.assertEqual(
            text.count(
                "python -m pip install -r requirements/exp058-model-run.txt -e ."
            ),
            3,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn('READINESS_ARTIFACT_ID: "10757578276"', text)
        self.assertEqual(text.count("scripts/phase8a_exp058_model_run.py"), 6)

    def test_workflow_preserves_partial_and_aggregate_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: always()", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: warn", text)
        self.assertIn(
            "exp058-fit-temporal-residual-lower-tail-utility-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp058-fit-temporal-residual-lower-tail-utility-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_checks_execution_before_artifact_loading(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_fit_temporal_residual_regime_floor_utility_model_execution("
        )
        readiness_load = text.index("load_training_readiness(args.readiness)")
        model_run = text.index(
            "run_fit_temporal_residual_lower_tail_utility_model_cell_core("
        )
        aggregate = text.index(
            "compile_fit_temporal_residual_regime_floor_utility_model_result_evidence("
        )
        self.assertLess(require_call, readiness_load)
        self.assertLess(require_call, model_run)
        self.assertLess(require_call, aggregate)
        self.assertIn("raise SystemExit(str(exc)) from exc", text)
        self.assertNotIn("gh workflow run", text)

    def test_runtime_lock_matches_predecessor_numerics(self) -> None:
        self.assertEqual(
            REQUIREMENTS.read_text(encoding="utf-8"),
            (
                "numpy==2.5.3\n"
                "scipy==1.18.1\n"
                "scikit-learn==1.9.1\n"
                "joblib==1.6.0\n"
                "threadpoolctl==3.7.0\n"
                "cloudpickle==3.1.2\n"
                "narwhals==2.26.0\n"
                "polars==1.44.2\n"
                "polars-runtime-32==1.44.2\n"
            ),
        )


if __name__ == "__main__":
    unittest.main()
