from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_breadth_utility_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC198_MERGED_COMMIT,
    DEC198_PROTOCOL_BLOB_SHA,
    DEC199_CORE_BLOB_SHA,
    DEC199_MERGED_COMMIT,
    DEC200_RUNNER_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_CLI_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_EXECUTION_GATE_DECISION,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_FIT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_WORKFLOW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    TRADING_AUTHORIZED,
    build_fit_temporal_residual_breadth_utility_model_workflow_source_gate,
    require_authoritative_fit_temporal_residual_breadth_utility_model_execution,
    validate_fit_temporal_residual_breadth_utility_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp055-fit-temporal-residual-breadth-utility-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp055_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp055-model-run.txt"


class Exp055ResidualBoundWorkflowTests(unittest.TestCase):
    def test_exact_sources_are_frozen_but_execution_closed(self) -> None:
        source = (
            validate_fit_temporal_residual_breadth_utility_model_workflow_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_EXECUTION_GATE_DECISION,
            "DEC-201",
        )
        self.assertEqual(
            source[
                "fit_temporal_residual_breadth_utility_model_execution_gate_decision"
            ],
            "DEC-201",
        )
        self.assertEqual(
            DEC198_MERGED_COMMIT,
            "670f5d615b837b9268f8fb807aa198e7d14d0f1a",
        )
        self.assertEqual(
            DEC199_MERGED_COMMIT,
            "aaa80ce43a4dbd38e52e418dd16b61642d22b2b5",
        )
        self.assertEqual(
            source["fit_temporal_residual_breadth_utility_runner_blob_sha"],
            DEC200_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            DEC200_RUNNER_BLOB_SHA,
            "65ca27a20d4e4fadd73c22b0b5693dc9d7ebeafb",
        )
        self.assertEqual(
            source["fit_temporal_residual_breadth_utility_core_blob_sha"],
            DEC199_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC199_CORE_BLOB_SHA,
            "c9517b7516940c78621448088c3933aa1c57e281",
        )
        self.assertEqual(
            source["fit_temporal_residual_breadth_utility_protocol_blob_sha"],
            DEC198_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC198_PROTOCOL_BLOB_SHA,
            "0ef3f932cade1a62e1faf946e9a9b87cf9c98744",
        )
        self.assertEqual(
            source["fit_temporal_residual_breadth_utility_workflow_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_WORKFLOW_BLOB_SHA,
            "da5b498deb7c8d15993eaeb686127f138ce9f161",
        )
        self.assertEqual(
            source["fit_temporal_residual_breadth_utility_cli_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_CLI_BLOB_SHA,
            "41eeb09fe0730f5184e71a9f7413a3bc5f568e63",
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )
        self.assertEqual(source["authorized_python_version"], AUTHORIZED_PYTHON_VERSION)

        gate = build_fit_temporal_residual_breadth_utility_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
        )
        self.assertTrue(
            gate[
                "fit_temporal_residual_breadth_utility_model_workflow_source_frozen"
            ]
        )
        self.assertFalse(
            gate[
                "fit_temporal_residual_breadth_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertFalse(
            gate[
                "authoritative_fit_temporal_residual_breadth_utility_model_result_execution_authorized"
            ]
        )
        self.assertFalse(gate["model_protocol_result_authorized"])
        self.assertFalse(gate["model_fit_authorized"])
        self.assertFalse(gate["promotion_authorized"])
        self.assertFalse(gate["shadow_authorized"])
        self.assertFalse(gate["trading_authorized"])

        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertFalse(
            AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertFalse(FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_FIT_AUTHORIZED)
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "DEC-201 freezes EXP-055 workflow source",
        ):
            require_authoritative_fit_temporal_residual_breadth_utility_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )

    def test_workflow_is_manual_main_only_and_input_free(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp055-fit-temporal-residual-breadth-utility-model-training",
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
            "Reject any prior manual main EXP-055 model run",
            text,
        )
        self.assertNotIn(
            "prior manual-main EXP-055 model run exists",
            text,
        )
        self.assertIn(
            "Require separately authorized EXP-055 result execution",
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
                "python -m pip install -r requirements/exp055-model-run.txt -e ."
            ),
            3,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn('READINESS_ARTIFACT_ID: "10757578276"', text)
        self.assertEqual(text.count("scripts/phase8a_exp055_model_run.py"), 6)

    def test_workflow_preserves_partial_and_aggregate_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: always()", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: warn", text)
        self.assertIn(
            "exp055-fit-temporal-residual-breadth-utility-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp055-fit-temporal-residual-breadth-utility-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_checks_execution_before_artifact_loading(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_fit_temporal_residual_breadth_utility_model_execution("
        )
        readiness_load = text.index("load_training_readiness(args.readiness)")
        model_run = text.index(
            "run_fit_temporal_residual_breadth_utility_model_cell_core("
        )
        aggregate = text.index(
            "compile_fit_temporal_residual_breadth_utility_model_result_evidence("
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
