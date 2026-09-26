from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_regime_balance_utility_repair_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC253_MERGED_COMMIT,
    DEC253_PROTOCOL_BLOB_SHA,
    DEC254_CORE_BLOB_SHA,
    DEC254_MERGED_COMMIT,
    DEC255_RUNNER_BLOB_SHA,
    DEC256_CLI_BLOB_SHA,
    DEC256_GATE_BLOB_SHA,
    DEC256_MERGED_COMMIT,
    DEC256_WORKFLOW_BLOB_SHA,
    DEC257_MERGED_COMMIT,
    DEC257_REVIEW_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_CLI_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_EXECUTION_GATE_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RUN_DISPATCH_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_SOURCE_FROZEN,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_WORKFLOW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    TRADING_AUTHORIZED,
    build_fit_temporal_residual_regime_balance_utility_repair_model_workflow_source_gate,
    require_authoritative_fit_temporal_residual_regime_balance_utility_repair_model_execution,
    validate_fit_temporal_residual_regime_balance_utility_repair_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp060_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp060-model-run.txt"


class Exp060ResidualRegimeBalanceWorkflowTests(unittest.TestCase):
    def test_exact_sources_open_one_guarded_result_authorization(self) -> None:
        source = (
            validate_fit_temporal_residual_regime_balance_utility_repair_model_workflow_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_EXECUTION_GATE_DECISION,
            "DEC-256",
        )
        self.assertEqual(
            source[
                "fit_temporal_residual_regime_balance_utility_repair_model_execution_gate_decision"
            ],
            "DEC-256",
        )
        self.assertEqual(
            DEC253_MERGED_COMMIT,
            "7e5b399cb7960d385d956b33e5d96cea85bb2c28",
        )
        self.assertEqual(
            DEC254_MERGED_COMMIT,
            "c8cac108bc098dbceda4b8903f5a56ac7f62bf47",
        )
        self.assertEqual(
            source["dec255_merged_commit"],
            "d3a52722c178c96eb865791be096661007d16dd5",
        )
        self.assertEqual(source["dec256_merged_commit"], DEC256_MERGED_COMMIT)
        self.assertEqual(
            DEC256_MERGED_COMMIT,
            "cef9f6d201bf2b025f08c924a11c84e9684b9ba0",
        )
        self.assertEqual(source["dec257_merged_commit"], DEC257_MERGED_COMMIT)
        self.assertEqual(
            DEC257_MERGED_COMMIT,
            "5998292b80c0986bdcc0b9f2a91cb024ef92158a",
        )
        self.assertEqual(
            source[
                "fit_temporal_residual_regime_balance_utility_repair_model_execution_authorization_decision"
            ],
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION,
            "DEC-258",
        )
        self.assertEqual(source["dec256_workflow_blob_sha"], DEC256_WORKFLOW_BLOB_SHA)
        self.assertEqual(DEC256_WORKFLOW_BLOB_SHA, "20af1bf2f9057274a8c50d5b48becbf5f683ef86")
        self.assertEqual(source["dec256_cli_blob_sha"], DEC256_CLI_BLOB_SHA)
        self.assertEqual(DEC256_CLI_BLOB_SHA, "90c6bc9e893c813d394e3a9c4adc5a155e938af0")
        self.assertEqual(source["dec256_gate_blob_sha"], DEC256_GATE_BLOB_SHA)
        self.assertEqual(DEC256_GATE_BLOB_SHA, "82f51bf85ccb1793b3a980b2884f3e122a03c8db")
        self.assertEqual(source["dec257_review_blob_sha"], DEC257_REVIEW_BLOB_SHA)
        self.assertEqual(DEC257_REVIEW_BLOB_SHA, "989ebc7b0cc33e5076f83ea94337fe6581c321e3")
        self.assertEqual(
            source["fit_temporal_residual_regime_balance_utility_repair_runner_blob_sha"],
            DEC255_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            DEC255_RUNNER_BLOB_SHA,
            "2a6c550dcafac2e7013136fcbbef95b13c2e7d18",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_balance_utility_repair_core_blob_sha"],
            DEC254_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC254_CORE_BLOB_SHA,
            "202dcaa8ba4ad25324fbe53d00e812c60fbb37dd",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_balance_utility_repair_protocol_blob_sha"],
            DEC253_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC253_PROTOCOL_BLOB_SHA,
            "82d336250e2cdd9894afa5554c6b422e0de6b1fe",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_balance_utility_workflow_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_WORKFLOW_BLOB_SHA,
            "91a5bb720ca10b261533409e36f6143994afcca3",
        )
        self.assertEqual(
            source["fit_temporal_residual_regime_balance_utility_cli_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_CLI_BLOB_SHA,
            "90c6bc9e893c813d394e3a9c4adc5a155e938af0",
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )
        self.assertEqual(source["authorized_python_version"], AUTHORIZED_PYTHON_VERSION)

        gate = build_fit_temporal_residual_regime_balance_utility_repair_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            gate[
                "fit_temporal_residual_regime_balance_utility_repair_model_workflow_source_frozen"
            ]
        )
        self.assertTrue(
            gate[
                "fit_temporal_residual_regime_balance_utility_repair_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            gate[
                "authoritative_fit_temporal_residual_regime_balance_utility_repair_model_result_execution_authorized"
            ]
        )
        self.assertTrue(gate["model_protocol_result_authorized"])
        self.assertTrue(gate["model_fit_authorized"])
        self.assertFalse(gate["promotion_authorized"])
        self.assertFalse(gate["shadow_authorized"])
        self.assertFalse(gate["demo_order_authorized"])
        self.assertFalse(gate["broker_mutation_authorized"])
        self.assertFalse(gate["live_order_authorized"])
        self.assertFalse(gate["real_money_authorized"])
        self.assertFalse(gate["trading_authorized"])

        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertTrue(
            AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertTrue(FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED)
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_accepts_exact_authorized_sources(self) -> None:
        result = require_authoritative_fit_temporal_residual_regime_balance_utility_repair_model_execution(
            repository_root=ROOT,
            code_commit="a" * 40,
        )
        self.assertEqual(result["code_commit"], "a" * 40)
        self.assertTrue(
            result[
                "fit_temporal_residual_regime_balance_utility_repair_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            result[
                "authoritative_fit_temporal_residual_regime_balance_utility_repair_model_result_execution_authorized"
            ]
        )
        self.assertTrue(result["model_protocol_result_authorized"])
        self.assertTrue(result["model_fit_authorized"])
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["shadow_authorized"])
        self.assertFalse(result["demo_order_authorized"])
        self.assertFalse(result["broker_mutation_authorized"])
        self.assertFalse(result["live_order_authorized"])
        self.assertFalse(result["real_money_authorized"])
        self.assertFalse(result["trading_authorized"])

    def test_workflow_is_manual_main_only_and_input_free(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training",
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

    def test_workflow_enforces_first_manual_main_attempt_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        guard = text.index("Reject any prior manual main EXP-060 model run")
        authorization = text.index(
            "Require separately authorized EXP-060 result execution"
        )
        self.assertLess(guard, authorization)
        self.assertIn(
            "actions/workflows/"
            "phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml/runs"
            "?branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn(
            'current["id"] == int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            'current["name"] == '
            '"phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training"',
            text,
        )
        self.assertIn(
            'current["path"] == '
            '".github/workflows/'
            'phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml"',
            text,
        )
        self.assertIn('current["run_attempt"] == 1', text)
        self.assertIn(
            'item.get("id") != int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn("prior manual-main EXP-060 model run exists", text)

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
                "python -m pip install -r requirements/exp060-model-run.txt -e ."
            ),
            3,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn('READINESS_ARTIFACT_ID: "10757578276"', text)
        self.assertEqual(text.count("scripts/phase8a_exp060_model_run.py"), 6)

    def test_workflow_preserves_partial_and_aggregate_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: always()", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: warn", text)
        self.assertIn(
            "exp060-fit-temporal-residual-regime-balance-utility-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp060-fit-temporal-residual-regime-balance-utility-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_checks_execution_before_artifact_loading(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_fit_temporal_residual_regime_balance_utility_repair_model_execution("
        )
        readiness_load = text.index("load_training_readiness(args.readiness)")
        model_run = text.index(
            "run_fit_temporal_residual_regime_balance_utility_model_cell_core("
        )
        aggregate = text.index(
            "compile_fit_temporal_residual_regime_balance_utility_repair_model_result_evidence("
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
