from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_density_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_DENSITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC113_MERGED_COMMIT,
    DEC113_PROTOCOL_BLOB_SHA,
    DEC114_CORE_BLOB_SHA,
    DEC114_MERGED_COMMIT,
    DEC115_MERGED_COMMIT,
    DEC115_RUNNER_BLOB_SHA,
    DEC116_CLI_BLOB_SHA,
    DEC116_GATE_BLOB_SHA,
    DEC116_MERGED_COMMIT,
    DEC116_WORKFLOW_BLOB_SHA,
    DEC117_MERGED_COMMIT,
    DEC117_REVIEW_BLOB_SHA,
    DENSITY_CLI_BLOB_SHA,
    DENSITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
    DENSITY_MODEL_EXECUTION_GATE_DECISION,
    DENSITY_MODEL_FIT_AUTHORIZED,
    DENSITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    DENSITY_MODEL_RUN_DISPATCH_AUTHORIZED,
    DENSITY_MODEL_WORKFLOW_SOURCE_FROZEN,
    DENSITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
    DENSITY_WORKFLOW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    TRADING_AUTHORIZED,
    build_density_model_workflow_source_gate,
    require_authoritative_density_model_execution,
    validate_density_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp047-density-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp047_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp047-model-run.txt"


class Exp047WorkflowSourceTests(unittest.TestCase):
    def test_exact_sources_open_one_guarded_result_authorization(
        self,
    ) -> None:
        source = validate_density_model_workflow_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            source["density_model_execution_gate_decision"],
            DENSITY_MODEL_EXECUTION_GATE_DECISION,
        )
        self.assertEqual(
            DENSITY_MODEL_EXECUTION_GATE_DECISION,
            "DEC-116",
        )
        self.assertEqual(
            source["dec113_merged_commit"],
            DEC113_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec114_merged_commit"],
            DEC114_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec115_merged_commit"],
            DEC115_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec116_merged_commit"],
            DEC116_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec117_merged_commit"],
            DEC117_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec116_workflow_blob_sha"],
            DEC116_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            source["dec116_cli_blob_sha"],
            DEC116_CLI_BLOB_SHA,
        )
        self.assertEqual(
            source["dec116_gate_blob_sha"],
            DEC116_GATE_BLOB_SHA,
        )
        self.assertEqual(
            source["dec117_review_blob_sha"],
            DEC117_REVIEW_BLOB_SHA,
        )
        self.assertEqual(
            source[
                "density_model_execution_authorization_decision"
            ],
            DENSITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
        )
        self.assertEqual(
            DENSITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
            "DEC-118",
        )
        self.assertEqual(
            source["density_runner_blob_sha"],
            DEC115_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            source["density_core_blob_sha"],
            DEC114_CORE_BLOB_SHA,
        )
        self.assertEqual(
            source["density_protocol_blob_sha"],
            DEC113_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            source["density_workflow_blob_sha"],
            DENSITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            source["density_cli_blob_sha"],
            DENSITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            source["authorized_python_version"],
            AUTHORIZED_PYTHON_VERSION,
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            DENSITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )

        gate = build_density_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "DENSITY_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            gate["density_model_workflow_source_frozen"]
        )
        self.assertTrue(
            gate["density_model_run_dispatch_authorized"]
        )
        self.assertTrue(
            gate[
                "authoritative_density_model_result_execution_authorized"
            ]
        )
        self.assertTrue(
            gate["model_protocol_result_authorized"]
        )
        self.assertTrue(gate["model_fit_authorized"])
        self.assertFalse(gate["promotion_authorized"])
        self.assertFalse(gate["shadow_authorized"])
        self.assertFalse(gate["demo_order_authorized"])
        self.assertFalse(
            gate["broker_mutation_authorized"]
        )
        self.assertFalse(gate["live_order_authorized"])
        self.assertFalse(gate["real_money_authorized"])
        self.assertFalse(gate["trading_authorized"])

        self.assertTrue(
            DENSITY_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertTrue(
            DENSITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertTrue(
            AUTHORITATIVE_DENSITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertTrue(
            DENSITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertTrue(DENSITY_MODEL_FIT_AUTHORIZED)
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_accepts_exact_authorized_sources(
        self,
    ) -> None:
        result = require_authoritative_density_model_execution(
            repository_root=ROOT,
            code_commit="a" * 40,
        )
        self.assertEqual(result["code_commit"], "a" * 40)
        self.assertTrue(
            result["density_model_run_dispatch_authorized"]
        )
        self.assertTrue(
            result[
                "authoritative_density_model_result_execution_authorized"
            ]
        )
        self.assertTrue(
            result["model_protocol_result_authorized"]
        )
        self.assertTrue(result["model_fit_authorized"])
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["shadow_authorized"])
        self.assertFalse(result["trading_authorized"])

    def test_workflow_is_manual_main_only_and_input_free(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp047-density-model-training",
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
            "Reject any prior manual main EXP-047 model run"
        )
        authorization = text.index(
            "Require separately authorized EXP-047 result execution"
        )
        self.assertLess(guard, authorization)
        self.assertIn(
            "actions/workflows/"
            "phase8a-exp047-density-model-training.yml/runs"
            "?branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn(
            'current["id"] == int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            'current["name"] == '
            '"phase8a-exp047-density-model-training"',
            text,
        )
        self.assertIn(
            'current["path"] == '
            '".github/workflows/'
            'phase8a-exp047-density-model-training.yml"',
            text,
        )
        self.assertIn(
            'item.get("id") != int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            "prior manual-main EXP-047 model run exists",
            text,
        )

    def test_workflow_uses_exact_matrix_and_pinned_runtime(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(text.count("- symbol: "), 9)
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

        self.assertEqual(
            text.count('python-version: "3.12.14"'),
            3,
        )
        self.assertEqual(
            text.count(
                "python -m pip install -r "
                "requirements/exp047-model-run.txt -e ."
            ),
            3,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn(
            'READINESS_ARTIFACT_ID: "10757578276"',
            text,
        )

    def test_workflow_preserves_partial_and_aggregate_evidence(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: always()", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: warn", text)
        self.assertIn(
            "exp047-density-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp047-density-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_has_no_dispatch_or_execution_bypass(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_density_model_execution("
        )
        readiness_load = text.index(
            "load_training_readiness(args.readiness)"
        )
        model_run = text.index(
            "run_density_model_cell_core("
        )
        aggregate = text.index(
            "compile_density_model_result_evidence("
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
