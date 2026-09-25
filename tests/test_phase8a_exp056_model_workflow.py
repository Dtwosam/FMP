from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC209_MERGED_COMMIT,
    DEC209_PROTOCOL_BLOB_SHA,
    DEC210_CORE_BLOB_SHA,
    DEC210_MERGED_COMMIT,
    DEC211_RUNNER_BLOB_SHA,
    DEC212_CLI_BLOB_SHA,
    DEC212_GATE_BLOB_SHA,
    DEC212_MERGED_COMMIT,
    DEC212_WORKFLOW_BLOB_SHA,
    DEC213_MERGED_COMMIT,
    DEC213_REVIEW_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_CLI_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_EXECUTION_GATE_DECISION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_FIT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_WORKFLOW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    TRADING_AUTHORIZED,
    build_fit_temporal_residual_lower_tail_utility_model_workflow_source_gate,
    require_authoritative_fit_temporal_residual_lower_tail_utility_model_execution,
    validate_fit_temporal_residual_lower_tail_utility_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp056_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp056-model-run.txt"


class Exp056ResidualLowerTailWorkflowTests(unittest.TestCase):
    def test_exact_sources_open_one_guarded_result_authorization(self) -> None:
        source = (
            validate_fit_temporal_residual_lower_tail_utility_model_workflow_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_EXECUTION_GATE_DECISION,
            "DEC-212",
        )
        self.assertEqual(
            source[
                "fit_temporal_residual_lower_tail_utility_model_execution_gate_decision"
            ],
            "DEC-212",
        )
        self.assertEqual(
            DEC209_MERGED_COMMIT,
            "d2e1aabba6c0f283da6802fe315a5a29b22b503c",
        )
        self.assertEqual(
            DEC210_MERGED_COMMIT,
            "029159999fae7eaa67811f8b3d8bf2bf8834e491",
        )
        self.assertEqual(
            source["dec211_merged_commit"],
            "193312de6d03dc8286956f7594602f67688b1d23",
        )
        self.assertEqual(source["dec212_merged_commit"], DEC212_MERGED_COMMIT)
        self.assertEqual(
            DEC212_MERGED_COMMIT,
            "3da30377a5d358471e79a32466f93fd80cf3a02f",
        )
        self.assertEqual(source["dec213_merged_commit"], DEC213_MERGED_COMMIT)
        self.assertEqual(
            DEC213_MERGED_COMMIT,
            "af6083303e1fac29265c7ffc59eb355a313d892d",
        )
        self.assertEqual(
            source[
                "fit_temporal_residual_lower_tail_utility_model_execution_authorization_decision"
            ],
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
            "DEC-214",
        )
        self.assertEqual(source["dec212_workflow_blob_sha"], DEC212_WORKFLOW_BLOB_SHA)
        self.assertEqual(DEC212_WORKFLOW_BLOB_SHA, "83e5434c065167294b854b58308fec6d39d800db")
        self.assertEqual(source["dec212_cli_blob_sha"], DEC212_CLI_BLOB_SHA)
        self.assertEqual(DEC212_CLI_BLOB_SHA, "30e79ef7ef20d12d75fc97103b9411b7b467ecef")
        self.assertEqual(source["dec212_gate_blob_sha"], DEC212_GATE_BLOB_SHA)
        self.assertEqual(DEC212_GATE_BLOB_SHA, "a81f746c8b19abc63f1bb83da0c32f1023644b94")
        self.assertEqual(source["dec213_review_blob_sha"], DEC213_REVIEW_BLOB_SHA)
        self.assertEqual(DEC213_REVIEW_BLOB_SHA, "0bfc50d39d04d82e95c731b7284c7be143191efd")
        self.assertEqual(
            source["fit_temporal_residual_lower_tail_utility_runner_blob_sha"],
            DEC211_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            DEC211_RUNNER_BLOB_SHA,
            "f554011c092f5c4ec5d3f9b8e2330bfc974376f8",
        )
        self.assertEqual(
            source["fit_temporal_residual_lower_tail_utility_core_blob_sha"],
            DEC210_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC210_CORE_BLOB_SHA,
            "c472ed48e7b79d22056d43deb0fe09166ccf34c9",
        )
        self.assertEqual(
            source["fit_temporal_residual_lower_tail_utility_protocol_blob_sha"],
            DEC209_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC209_PROTOCOL_BLOB_SHA,
            "14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d",
        )
        self.assertEqual(
            source["fit_temporal_residual_lower_tail_utility_workflow_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_WORKFLOW_BLOB_SHA,
            "cf9585ebdfea689c7b0e3ca82ac4c43488559b2a",
        )
        self.assertEqual(
            source["fit_temporal_residual_lower_tail_utility_cli_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_CLI_BLOB_SHA,
            "30e79ef7ef20d12d75fc97103b9411b7b467ecef",
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )
        self.assertEqual(source["authorized_python_version"], AUTHORIZED_PYTHON_VERSION)

        gate = build_fit_temporal_residual_lower_tail_utility_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            gate[
                "fit_temporal_residual_lower_tail_utility_model_workflow_source_frozen"
            ]
        )
        self.assertTrue(
            gate[
                "fit_temporal_residual_lower_tail_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            gate[
                "authoritative_fit_temporal_residual_lower_tail_utility_model_result_execution_authorized"
            ]
        )
        self.assertTrue(gate["model_protocol_result_authorized"])
        self.assertTrue(gate["model_fit_authorized"])
        self.assertFalse(gate["promotion_authorized"])
        self.assertFalse(gate["shadow_authorized"])
        self.assertFalse(gate["trading_authorized"])

        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertTrue(
            AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertTrue(FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_FIT_AUTHORIZED)
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_accepts_exact_authorized_sources(self) -> None:
        result = (
            require_authoritative_fit_temporal_residual_lower_tail_utility_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )
        )
        self.assertEqual(result["code_commit"], "a" * 40)
        self.assertTrue(
            result[
                "fit_temporal_residual_lower_tail_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            result[
                "authoritative_fit_temporal_residual_lower_tail_utility_model_result_execution_authorized"
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
            "name: phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training",
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
            "Reject any prior manual main EXP-056 model run"
        )
        authorization = text.index(
            "Require separately authorized EXP-056 result execution"
        )
        self.assertLess(guard, authorization)
        self.assertIn(
            "actions/workflows/"
            "phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml/runs"
            "?branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn(
            'current["id"] == int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            'current["name"] == '
            '"phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training"',
            text,
        )
        self.assertIn(
            'current["path"] == '
            '".github/workflows/'
            'phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml"',
            text,
        )
        self.assertIn(
            'item.get("id") != int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            "prior manual-main EXP-056 model run exists",
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
                "python -m pip install -r requirements/exp056-model-run.txt -e ."
            ),
            3,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn('READINESS_ARTIFACT_ID: "10757578276"', text)
        self.assertEqual(text.count("scripts/phase8a_exp056_model_run.py"), 6)

    def test_workflow_preserves_partial_and_aggregate_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: always()", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: warn", text)
        self.assertIn(
            "exp056-fit-temporal-residual-lower-tail-utility-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp056-fit-temporal-residual-lower-tail-utility-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_checks_execution_before_artifact_loading(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_fit_temporal_residual_lower_tail_utility_model_execution("
        )
        readiness_load = text.index("load_training_readiness(args.readiness)")
        model_run = text.index(
            "run_fit_temporal_residual_lower_tail_utility_model_cell_core("
        )
        aggregate = text.index(
            "compile_fit_temporal_residual_lower_tail_utility_model_result_evidence("
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
