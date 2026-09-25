from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_fit_temporal_support_utility_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC163_MERGED_COMMIT,
    DEC163_PROTOCOL_BLOB_SHA,
    DEC164_CORE_BLOB_SHA,
    DEC164_MERGED_COMMIT,
    DEC165_MERGED_COMMIT,
    DEC165_RUNNER_BLOB_SHA,
    DEC166_CLI_BLOB_SHA,
    DEC166_GATE_BLOB_SHA,
    DEC166_MERGED_COMMIT,
    DEC166_WORKFLOW_BLOB_SHA,
    DEC167_MERGED_COMMIT,
    DEC167_REVIEW_BLOB_SHA,
    FIT_TEMPORAL_SUPPORT_UTILITY_CLI_BLOB_SHA,
    FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
    FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_EXECUTION_GATE_DECISION,
    FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED,
    FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED,
    FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN,
    FIT_TEMPORAL_SUPPORT_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
    FIT_TEMPORAL_SUPPORT_UTILITY_WORKFLOW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    TRADING_AUTHORIZED,
    build_fit_temporal_support_utility_model_workflow_source_gate,
    require_authoritative_fit_temporal_support_utility_model_execution,
    validate_fit_temporal_support_utility_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp052-fit-temporal-support-utility-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp052_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp052-model-run.txt"


class Exp052FitTemporalSupportWorkflowTests(unittest.TestCase):
    def test_exact_sources_open_one_guarded_result_authorization(
        self,
    ) -> None:
        source = (
            validate_fit_temporal_support_utility_model_workflow_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            source[
                "fit_temporal_support_utility_model_execution_gate_decision"
            ],
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_EXECUTION_GATE_DECISION,
        )
        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_EXECUTION_GATE_DECISION,
            "DEC-166",
        )
        self.assertEqual(
            source[
                "fit_temporal_support_utility_model_execution_authorization_decision"
            ],
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
        )
        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
            "DEC-168",
        )
        self.assertEqual(
            source["dec163_merged_commit"],
            DEC163_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC163_MERGED_COMMIT,
            "9108cd170b2eccf73bddb6cbf8d6d7118dbd9cd1",
        )
        self.assertEqual(
            source["dec164_merged_commit"],
            DEC164_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC164_MERGED_COMMIT,
            "d9f893504b2d790eb73bc49edf4c0919ef2ff914",
        )
        self.assertEqual(
            source["dec165_merged_commit"],
            DEC165_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC165_MERGED_COMMIT,
            "0753e85546bcef430863eceb99bdc38f43572477",
        )
        self.assertEqual(
            source["dec166_merged_commit"],
            DEC166_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC166_MERGED_COMMIT,
            "2883cc46c65ff7c672c9f8d7192fc7fb240a9835",
        )
        self.assertEqual(
            source["dec167_merged_commit"],
            DEC167_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC167_MERGED_COMMIT,
            "32af27a80cdb50a8be069b21ffe1757f0b6aaa10",
        )
        self.assertEqual(
            source["dec166_workflow_blob_sha"],
            DEC166_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            DEC166_WORKFLOW_BLOB_SHA,
            "c4310d4d4a58436eca75afaf147fa570ac725088",
        )
        self.assertEqual(
            source["dec166_cli_blob_sha"],
            DEC166_CLI_BLOB_SHA,
        )
        self.assertEqual(
            DEC166_CLI_BLOB_SHA,
            "728691476a2285ec4cdec594a020aa5c84b04c5e",
        )
        self.assertEqual(
            source["dec166_gate_blob_sha"],
            DEC166_GATE_BLOB_SHA,
        )
        self.assertEqual(
            DEC166_GATE_BLOB_SHA,
            "139028be1c354a99599a3ed6505a1a4725889c02",
        )
        self.assertEqual(
            source["dec167_review_blob_sha"],
            DEC167_REVIEW_BLOB_SHA,
        )
        self.assertEqual(
            DEC167_REVIEW_BLOB_SHA,
            "dbccea23117adbc50fa54345ec418fde54f254a3",
        )
        self.assertEqual(
            source["fit_temporal_support_utility_runner_blob_sha"],
            DEC165_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            DEC165_RUNNER_BLOB_SHA,
            "ae06184b9a84405119b6ed434a8973139d8ae006",
        )
        self.assertEqual(
            source["fit_temporal_support_utility_core_blob_sha"],
            DEC164_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC164_CORE_BLOB_SHA,
            "fe5664438752a161134bbed6f55d9985f1c1470a",
        )
        self.assertEqual(
            source["fit_temporal_support_utility_protocol_blob_sha"],
            DEC163_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC163_PROTOCOL_BLOB_SHA,
            "01d5080560ec5d41653694b4df086ff2f10e770d",
        )
        self.assertEqual(
            source[
                "fit_temporal_support_utility_workflow_blob_sha"
            ],
            FIT_TEMPORAL_SUPPORT_UTILITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_UTILITY_WORKFLOW_BLOB_SHA,
            "a49af5daeb14177a44154ef96b135f64a98a85bf",
        )
        self.assertEqual(
            source["fit_temporal_support_utility_cli_blob_sha"],
            FIT_TEMPORAL_SUPPORT_UTILITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_UTILITY_CLI_BLOB_SHA,
            "728691476a2285ec4cdec594a020aa5c84b04c5e",
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            FIT_TEMPORAL_SUPPORT_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )
        self.assertEqual(
            source["authorized_python_version"],
            AUTHORIZED_PYTHON_VERSION,
        )

        gate = (
            build_fit_temporal_support_utility_model_workflow_source_gate(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            gate["stage"],
            (
                "FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_"
                "RUN_DISPATCH_REQUIRED"
            ),
        )
        self.assertTrue(
            gate[
                "fit_temporal_support_utility_model_workflow_source_frozen"
            ]
        )
        self.assertTrue(
            gate[
                "fit_temporal_support_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            gate[
                "authoritative_fit_temporal_support_utility_model_result_execution_authorized"
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
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertTrue(
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertTrue(
            AUTHORITATIVE_FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertTrue(
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertTrue(
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED
        )
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_accepts_exact_authorized_sources(
        self,
    ) -> None:
        result = (
            require_authoritative_fit_temporal_support_utility_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )
        )
        self.assertEqual(result["code_commit"], "a" * 40)
        self.assertTrue(
            result[
                "fit_temporal_support_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            result[
                "authoritative_fit_temporal_support_utility_model_result_execution_authorized"
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
            "name: phase8a-exp052-fit-temporal-support-utility-model-training",
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
            "Reject any prior manual main EXP-052 model run"
        )
        authorization = text.index(
            "Require separately authorized EXP-052 result execution"
        )
        self.assertLess(guard, authorization)
        self.assertIn(
            "actions/workflows/"
            "phase8a-exp052-fit-temporal-support-utility-model-training.yml/runs"
            "?branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn(
            'current["id"] == int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            'current["name"] == '
            '"phase8a-exp052-fit-temporal-support-utility-model-training"',
            text,
        )
        self.assertIn(
            'current["path"] == '
            '".github/workflows/'
            'phase8a-exp052-fit-temporal-support-utility-model-training.yml"',
            text,
        )
        self.assertIn(
            'item.get("id") != int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            "prior manual-main EXP-052 model run exists",
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
                "requirements/exp052-model-run.txt -e ."
            ),
            3,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn(
            'READINESS_ARTIFACT_ID: "10757578276"',
            text,
        )
        self.assertEqual(
            text.count("scripts/phase8a_exp052_model_run.py"),
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
            "exp052-fit-temporal-support-utility-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp052-fit-temporal-support-utility-model-result-evidence-",
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
            "require_authoritative_fit_temporal_support_utility_model_execution("
        )
        readiness_load = text.index(
            "load_training_readiness(args.readiness)"
        )
        model_run = text.index(
            "run_fit_temporal_support_utility_model_cell_core("
        )
        aggregate = text.index(
            "compile_fit_temporal_support_utility_model_result_evidence("
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
