from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_regime_balance_utility_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC242_MERGED_COMMIT,
    DEC242_PROTOCOL_BLOB_SHA,
    DEC243_CORE_BLOB_SHA,
    DEC243_MERGED_COMMIT,
    DEC244_RUNNER_BLOB_SHA,
    DEC245_CLI_BLOB_SHA,
    DEC245_GATE_BLOB_SHA,
    DEC245_MERGED_COMMIT,
    DEC245_WORKFLOW_BLOB_SHA,
    DEC246_MERGED_COMMIT,
    DEC246_REVIEW_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_CLI_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_EXECUTION_GATE_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_FIT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_WORKFLOW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    TRADING_AUTHORIZED,
    build_fit_temporal_residual_regime_balance_utility_model_workflow_source_gate,
    require_authoritative_fit_temporal_residual_regime_balance_utility_model_execution,
    validate_fit_temporal_residual_regime_balance_utility_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp059_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp059-model-run.txt"


class Exp059ResidualRegimeBalanceWorkflowTests(unittest.TestCase):
    def test_exact_sources_open_one_guarded_result_authorization(self) -> None:
        source = (
            validate_fit_temporal_residual_regime_balance_utility_model_workflow_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_EXECUTION_GATE_DECISION,
            "DEC-245",
        )
        self.assertEqual(
            source[
                "fit_temporal_residual_regime_balance_utility_model_execution_gate_decision"
            ],
            "DEC-245",
        )
        self.assertEqual(
            DEC242_MERGED_COMMIT,
            "a14afb226722d168c3d899d7079776388161a52d",
        )
        self.assertEqual(
            DEC243_MERGED_COMMIT,
            "9f427f06f315288bd9b132de19901beb5a5ddfc8",
        )
        self.assertEqual(
            source["dec233_merged_commit"],
            "b539c48cd62fb8e510ecaa15ce507c114f9401bb",
        )
        self.assertEqual(source["dec245_merged_commit"], DEC245_MERGED_COMMIT)
        self.assertEqual(
            DEC245_MERGED_COMMIT,
            "d33e2f1e6e7f39c12811dbc07c5cd960f8e2442f",
        )
        self.assertEqual(source["dec246_merged_commit"], DEC246_MERGED_COMMIT)
        self.assertEqual(
            DEC246_MERGED_COMMIT,
            "018c8cb223c3553ad4db4ba5b33b339a9a8fa918",
        )
        self.assertEqual(
            source[
                "fit_temporal_residual_regime_balance_utility_model_execution_authorization_decision"
            ],
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
            "DEC-247",
        )
        self.assertEqual(source["dec245_workflow_blob_sha"], DEC245_WORKFLOW_BLOB_SHA)
        self.assertEqual(DEC245_WORKFLOW_BLOB_SHA, "d416c43c9e582f49cd60314c6ee736925e8185e8")
        self.assertEqual(source["dec245_cli_blob_sha"], DEC245_CLI_BLOB_SHA)
        self.assertEqual(DEC245_CLI_BLOB_SHA, "44c084c226c62c30ddf16741027593a4a835605f")
        self.assertEqual(source["dec245_gate_blob_sha"], DEC245_GATE_BLOB_SHA)
        self.assertEqual(DEC245_GATE_BLOB_SHA, "d6556cf3bc3a1189c2ee6648c1870ec307a2178f")
        self.assertEqual(source["dec246_review_blob_sha"], DEC246_REVIEW_BLOB_SHA)
        self.assertEqual(DEC246_REVIEW_BLOB_SHA, "5adc6ad72b2dfab1de1cca09a9bb2bc09663bfc5")
        self.assertEqual(
            source["fit_temporal_residual_regime_balance_utility_runner_blob_sha"],
            DEC244_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            DEC244_RUNNER_BLOB_SHA,
            "a993d8a0a98b181c7810e4f0931be330352437b4",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_balance_utility_core_blob_sha"],
            DEC243_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC243_CORE_BLOB_SHA,
            "4f99c1d0cb18551b67cc89357ad4a3940c190cd2",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_balance_utility_protocol_blob_sha"],
            DEC242_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC242_PROTOCOL_BLOB_SHA,
            "cd4e790098a5c8d99ea2aa5264465b5d4b6b6acc",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_balance_utility_workflow_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_WORKFLOW_BLOB_SHA,
            "6c3e516be8d6eaed834fb1955efccf43f414318f",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_balance_utility_cli_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_CLI_BLOB_SHA,
            "44c084c226c62c30ddf16741027593a4a835605f",
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )
        self.assertEqual(source["authorized_python_version"], AUTHORIZED_PYTHON_VERSION)

        gate = build_fit_temporal_residual_regime_balance_utility_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            gate[
                "fit_temporal_residual_regime_balance_utility_model_workflow_source_frozen"
            ]
        )
        self.assertTrue(
            gate[
                "fit_temporal_residual_regime_balance_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            gate[
                "authoritative_fit_temporal_residual_regime_balance_utility_model_result_execution_authorized"
            ]
        )
        self.assertTrue(gate["model_protocol_result_authorized"])
        self.assertTrue(gate["model_fit_authorized"])
        self.assertFalse(gate["promotion_authorized"])
        self.assertFalse(gate["shadow_authorized"])
        self.assertFalse(gate["trading_authorized"])

        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertTrue(
            AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertTrue(FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_FIT_AUTHORIZED)
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_accepts_exact_authorized_sources(self) -> None:
        result = (
            require_authoritative_fit_temporal_residual_regime_balance_utility_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )
        )
        self.assertEqual(result["code_commit"], "a" * 40)
        self.assertTrue(
            result[
                "fit_temporal_residual_regime_balance_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            result[
                "authoritative_fit_temporal_residual_regime_balance_utility_model_result_execution_authorized"
            ]
        )
        self.assertTrue(result["model_protocol_result_authorized"])
        self.assertTrue(result["model_fit_authorized"])
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["shadow_authorized"])
        self.assertFalse(result["trading_authorized"])

    def test_workflow_is_manual_main_only_and_input_free(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training",
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

    def test_workflow_enforces_first_manual_main_run_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        guard = text.index(
            "Reject any prior manual main EXP-059 model run"
        )
        authorization = text.index(
            "Require separately authorized EXP-059 result execution"
        )
        self.assertLess(guard, authorization)
        self.assertIn(
            "actions/workflows/"
            "phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training.yml/runs"
            "?branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn(
            'current["id"] == int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            'current["name"] == '
            '"phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training"',
            text,
        )
        self.assertIn(
            'current["path"] == '
            '".github/workflows/'
            'phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training.yml"',
            text,
        )
        self.assertIn(
            'item.get("id") != int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            "prior manual-main EXP-059 model run exists",
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
                "python -m pip install -r requirements/exp059-model-run.txt -e ."
            ),
            3,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn('READINESS_ARTIFACT_ID: "10757578276"', text)
        self.assertEqual(text.count("scripts/phase8a_exp059_model_run.py"), 6)

    def test_workflow_preserves_partial_and_aggregate_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: always()", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: warn", text)
        self.assertIn(
            "exp059-fit-temporal-residual-regime-balance-utility-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp059-fit-temporal-residual-regime-balance-utility-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_checks_execution_before_artifact_loading(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_fit_temporal_residual_regime_balance_utility_model_execution("
        )
        readiness_load = text.index("load_training_readiness(args.readiness)")
        model_run = text.index(
            "run_fit_temporal_residual_regime_balance_utility_model_cell_core("
        )
        aggregate = text.index(
            "compile_fit_temporal_residual_regime_balance_utility_model_result_evidence("
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
