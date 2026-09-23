from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_stability_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC104_MERGED_COMMIT,
    DEC104_PROTOCOL_BLOB_SHA,
    DEC105_CORE_BLOB_SHA,
    DEC105_MERGED_COMMIT,
    DEC106_MERGED_COMMIT,
    DEC106_RUNNER_BLOB_SHA,
    STABILITY_MODEL_FIT_AUTHORIZED,
    PROMOTION_AUTHORIZED,
    STABILITY_CLI_BLOB_SHA,
    STABILITY_MODEL_EXECUTION_GATE_DECISION,
    STABILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    STABILITY_MODEL_RUN_DISPATCH_AUTHORIZED,
    STABILITY_MODEL_WORKFLOW_FILE,
    STABILITY_MODEL_WORKFLOW_NAME,
    STABILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
    STABILITY_WORKFLOW_BLOB_SHA,
    TRADING_AUTHORIZED,
    build_stability_model_workflow_source_gate,
    require_authoritative_stability_model_execution,
    validate_stability_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp046-stability-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp046_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp046-model-run.txt"


class Exp046WorkflowSourceTests(unittest.TestCase):
    def test_source_gate_binds_exact_merged_sources(self) -> None:
        report = validate_stability_model_workflow_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            report["stability_model_execution_gate_decision"],
            STABILITY_MODEL_EXECUTION_GATE_DECISION,
        )
        self.assertEqual(
            STABILITY_MODEL_EXECUTION_GATE_DECISION,
            "DEC-107",
        )
        self.assertEqual(
            report["dec104_merged_commit"],
            DEC104_MERGED_COMMIT,
        )
        self.assertEqual(
            report["dec105_merged_commit"],
            DEC105_MERGED_COMMIT,
        )
        self.assertEqual(
            report["dec106_merged_commit"],
            DEC106_MERGED_COMMIT,
        )
        self.assertEqual(
            report["stability_runner_blob_sha"],
            DEC106_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            report["stability_core_blob_sha"],
            DEC105_CORE_BLOB_SHA,
        )
        self.assertEqual(
            report["stability_protocol_blob_sha"],
            DEC104_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            report["stability_workflow_blob_sha"],
            STABILITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            report["stability_cli_blob_sha"],
            STABILITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            report["authorized_python_version"],
            AUTHORIZED_PYTHON_VERSION,
        )
        self.assertEqual(
            report["runtime_requirements_blob_sha"],
            STABILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )

    def test_source_gate_remains_non_executable(self) -> None:
        report = build_stability_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            report["stage"],
            "STABILITY_MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
        )
        self.assertTrue(
            report["stability_model_workflow_source_frozen"]
        )
        self.assertFalse(
            report["stability_model_run_dispatch_authorized"]
        )
        self.assertFalse(
            report[
                "authoritative_stability_model_result_execution_authorized"
            ]
        )
        self.assertFalse(
            report["model_protocol_result_authorized"]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["demo_order_authorized"])
        self.assertFalse(
            report["broker_mutation_authorized"]
        )
        self.assertFalse(report["live_order_authorized"])
        self.assertFalse(report["real_money_authorized"])
        self.assertFalse(report["trading_authorized"])

        self.assertFalse(
            STABILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertFalse(
            AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(
            STABILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertFalse(STABILITY_MODEL_FIT_AUTHORIZED)
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_require_execution_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "dispatch is not authorized",
        ):
            require_authoritative_stability_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )

    def test_workflow_is_manual_main_only_and_input_free(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp046-stability-model-training",
            text,
        )
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("inputs:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn(
            'test "$GITHUB_REF" = "refs/heads/main"',
            text,
        )
        self.assertIn(
            "contents: read",
            text,
        )
        self.assertIn(
            "actions: read",
            text,
        )
        self.assertNotIn(
            "Reject any prior manual main EXP-046",
            text,
        )

    def test_workflow_uses_exact_matrix_and_pinned_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(
            text.count("- symbol: "),
            9,
        )
        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            self.assertEqual(
                text.count(f"- symbol: {symbol}"),
                3,
            )
        for timeframe in ("5m", "15m", "1h"):
            self.assertEqual(
                text.count(f"timeframe: {timeframe}"),
                3,
            )

        self.assertIn(
            'python-version: "3.12.14"',
            text,
        )
        self.assertIn(
            "requirements/exp046-model-run.txt",
            text,
        )
        self.assertIn(
            "for horizon in 60 240; do",
            text,
        )
        self.assertIn(
            "scripts/phase8a_exp046_model_run.py run-cell",
            text,
        )
        self.assertIn(
            "scripts/phase8a_exp046_model_run.py aggregate",
            text,
        )
        self.assertIn(
            'READINESS_ARTIFACT_ID: "10757578276"',
            text,
        )

    def test_workflow_preserves_partial_and_aggregate_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "if: always()",
            text,
        )
        self.assertIn(
            "include-hidden-files: true",
            text,
        )
        self.assertIn(
            "if-no-files-found: warn",
            text,
        )
        self.assertIn(
            "exp046-stability-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp046-stability-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_routes_only_through_locked_execution_gate(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        self.assertIn(
            "build_stability_model_workflow_source_gate",
            text,
        )
        self.assertIn(
            "require_authoritative_stability_model_execution",
            text,
        )
        self.assertIn(
            "run_stability_model_cell_core",
            text,
        )
        self.assertIn(
            "compile_stability_model_result_evidence",
            text,
        )
        self.assertNotIn("phase8a_exp045", text)
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
