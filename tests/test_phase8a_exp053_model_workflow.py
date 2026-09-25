from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_fit_temporal_feature_support_utility_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC174_MERGED_COMMIT,
    DEC174_PROTOCOL_BLOB_SHA,
    DEC175_CORE_BLOB_SHA,
    DEC175_MERGED_COMMIT,
    DEC176_MERGED_COMMIT,
    DEC176_RUNNER_BLOB_SHA,
    DEC177_CLI_BLOB_SHA,
    DEC177_GATE_BLOB_SHA,
    DEC177_MERGED_COMMIT,
    DEC177_WORKFLOW_BLOB_SHA,
    DEC178_MERGED_COMMIT,
    DEC178_REVIEW_BLOB_SHA,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_CLI_BLOB_SHA,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_GATE_DECISION,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_WORKFLOW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    TRADING_AUTHORIZED,
    build_fit_temporal_feature_support_utility_model_workflow_source_gate,
    require_authoritative_fit_temporal_feature_support_utility_model_execution,
    validate_fit_temporal_feature_support_utility_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp053_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp053-model-run.txt"


class Exp053FitTemporalFeatureSupportWorkflowTests(unittest.TestCase):
    def test_exact_sources_open_one_guarded_result_authorization(
        self,
    ) -> None:
        source = (
            validate_fit_temporal_feature_support_utility_model_workflow_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            source[
                "fit_temporal_feature_support_utility_model_execution_gate_decision"
            ],
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_GATE_DECISION,
        )
        self.assertEqual(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_GATE_DECISION,
            "DEC-177",
        )
        self.assertEqual(
            source[
                "fit_temporal_feature_support_utility_model_execution_authorization_decision"
            ],
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
        )
        self.assertEqual(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
            "DEC-179",
        )
        self.assertEqual(
            source["dec163_merged_commit"],
            DEC174_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC174_MERGED_COMMIT,
            "9687eb8ea3920e87d6681adf7366a3ce0bba7154",
        )
        self.assertEqual(
            source["dec164_merged_commit"],
            DEC175_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC175_MERGED_COMMIT,
            "60abce7c2674f9c25e4132037c9eb24cab1baf22",
        )
        self.assertEqual(
            source["dec165_merged_commit"],
            DEC176_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC176_MERGED_COMMIT,
            "a37462015ada9499fccf7ebb0a9f515e74bff1b6",
        )
        self.assertEqual(
            source["fit_temporal_feature_support_utility_runner_blob_sha"],
            DEC176_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            DEC176_RUNNER_BLOB_SHA,
            "431c879bf26d88e33bdf0f0965ec62566b1a3e22",
        )
        self.assertEqual(
            source["fit_temporal_feature_support_utility_core_blob_sha"],
            DEC175_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC175_CORE_BLOB_SHA,
            "4fd0e48302f97e188a8124e1543bde0ffdb43b6f",
        )
        self.assertEqual(
            source["fit_temporal_feature_support_utility_protocol_blob_sha"],
            DEC174_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC174_PROTOCOL_BLOB_SHA,
            "11ae3fc8e68687cc04957ed9243d8c5969227fb8",
        )
        self.assertEqual(
            source[
                "fit_temporal_feature_support_utility_workflow_blob_sha"
            ],
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_WORKFLOW_BLOB_SHA,
            "4cebdc134bd4fd0edc72c4baeccee4c8185e3e1b",
        )
        self.assertEqual(
            source["dec177_merged_commit"],
            DEC177_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC177_MERGED_COMMIT,
            "7faa5e765f08a47062444ebce3756bf9435ef1d4",
        )
        self.assertEqual(
            source["dec178_merged_commit"],
            DEC178_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC178_MERGED_COMMIT,
            "132fa1621771f9fd072ba6b3a396a70e55c6883b",
        )
        self.assertEqual(
            source["dec177_workflow_blob_sha"],
            DEC177_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            DEC177_WORKFLOW_BLOB_SHA,
            "0a6704f75e83b06b7555dbb9dc912cda31443bbc",
        )
        self.assertEqual(
            source["dec177_cli_blob_sha"],
            DEC177_CLI_BLOB_SHA,
        )
        self.assertEqual(
            DEC177_CLI_BLOB_SHA,
            "dbd146100d81be6ffc492de448d8dc4e0a2f4e73",
        )
        self.assertEqual(
            source["dec177_gate_blob_sha"],
            DEC177_GATE_BLOB_SHA,
        )
        self.assertEqual(
            DEC177_GATE_BLOB_SHA,
            "600ea84946fe908d143f3fbe2082b3505733cdf5",
        )
        self.assertEqual(
            source["dec178_review_blob_sha"],
            DEC178_REVIEW_BLOB_SHA,
        )
        self.assertEqual(
            DEC178_REVIEW_BLOB_SHA,
            "c1586f8ddf48ad1125adaed7d8d8f0a476862beb",
        )
        self.assertEqual(
            source["fit_temporal_feature_support_utility_cli_blob_sha"],
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_CLI_BLOB_SHA,
            "dbd146100d81be6ffc492de448d8dc4e0a2f4e73",
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )
        self.assertEqual(
            source["authorized_python_version"],
            AUTHORIZED_PYTHON_VERSION,
        )

        gate = (
            build_fit_temporal_feature_support_utility_model_workflow_source_gate(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            gate["stage"],
            (
                "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_"
                "RUN_DISPATCH_REQUIRED"
            ),
        )
        self.assertTrue(
            gate[
                "fit_temporal_feature_support_utility_model_workflow_source_frozen"
            ]
        )
        self.assertTrue(
            gate[
                "fit_temporal_feature_support_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            gate[
                "authoritative_fit_temporal_feature_support_utility_model_result_execution_authorized"
            ]
        )
        self.assertTrue(
            gate["model_protocol_result_authorized"]
        )
        self.assertTrue(gate["model_fit_authorized"])
        self.assertFalse(gate["promotion_authorized"])
        self.assertFalse(gate["shadow_authorized"])
        self.assertFalse(gate["trading_authorized"])

        self.assertTrue(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertTrue(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertTrue(
            AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertTrue(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertTrue(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED
        )
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_accepts_exact_authorized_sources(
        self,
    ) -> None:
        result = (
            require_authoritative_fit_temporal_feature_support_utility_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )
        )
        self.assertEqual(result["code_commit"], "a" * 40)
        self.assertTrue(
            result[
                "fit_temporal_feature_support_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            result[
                "authoritative_fit_temporal_feature_support_utility_model_result_execution_authorized"
            ]
        )
        self.assertTrue(result["model_protocol_result_authorized"])
        self.assertTrue(result["model_fit_authorized"])
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["shadow_authorized"])
        self.assertFalse(result["trading_authorized"])

    def test_workflow_is_manual_main_only_and_input_free(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp053-fit-temporal-feature-support-utility-model-training",
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

    def test_workflow_enforces_first_manual_main_run_only(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        guard = text.index(
            "Reject any prior manual main EXP-053 model run"
        )
        authorization = text.index(
            "Require separately authorized EXP-053 result execution"
        )
        self.assertLess(guard, authorization)
        self.assertIn(
            "actions/workflows/"
            "phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml/runs"
            "?branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn(
            'current["id"] == int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            'current["name"] == '
            '"phase8a-exp053-fit-temporal-feature-support-utility-model-training"',
            text,
        )
        self.assertIn(
            'current["path"] == '
            '".github/workflows/'
            'phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml"',
            text,
        )
        self.assertIn(
            'item.get("id") != int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            "prior manual-main EXP-053 model run exists",
            text,
        )

    def test_workflow_uses_exact_matrix_and_pinned_runtime(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(text.count("- symbol: "), 9)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            self.assertEqual(text.count(f"- symbol: {symbol}"), 3)
        for timeframe in ("5m", "15m", "1h"):
            self.assertEqual(
                text.count(f"timeframe: {timeframe}"),
                3,
            )
        self.assertEqual(
            text.count('python-version: "3.12.14"'),
            3,
        )
        self.assertEqual(
            text.count(
                "python -m pip install -r "
                "requirements/exp053-model-run.txt -e ."
            ),
            3,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn(
            'READINESS_ARTIFACT_ID: "10757578276"',
            text,
        )
        self.assertEqual(
            text.count("scripts/phase8a_exp053_model_run.py"),
            6,
        )

    def test_workflow_preserves_partial_and_aggregate_evidence(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: always()", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: warn", text)
        self.assertIn(
            "exp053-fit-temporal-feature-support-utility-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp053-fit-temporal-feature-support-utility-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_checks_execution_before_artifact_loading(
        self,
    ) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_fit_temporal_feature_support_utility_model_execution("
        )
        readiness_load = text.index(
            "load_training_readiness(args.readiness)"
        )
        model_run = text.index(
            "run_fit_temporal_feature_support_utility_model_cell_core("
        )
        aggregate = text.index(
            "compile_fit_temporal_feature_support_utility_model_result_evidence("
        )
        self.assertLess(require_call, readiness_load)
        self.assertLess(require_call, model_run)
        self.assertLess(require_call, aggregate)
        self.assertIn(
            "raise SystemExit(str(exc)) from exc",
            text,
        )
        self.assertNotIn("gh workflow run", text)

    def test_runtime_lock_matches_predecessor_numerics(
        self,
    ) -> None:
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
