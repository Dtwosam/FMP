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
    DEC107_CLI_BLOB_SHA,
    DEC107_GATE_BLOB_SHA,
    DEC107_MERGED_COMMIT,
    DEC107_WORKFLOW_BLOB_SHA,
    DEC108_MERGED_COMMIT,
    DEC108_REVIEW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    STABILITY_CLI_BLOB_SHA,
    STABILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
    STABILITY_MODEL_EXECUTION_GATE_DECISION,
    STABILITY_MODEL_FIT_AUTHORIZED,
    STABILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    STABILITY_MODEL_RUN_DISPATCH_AUTHORIZED,
    STABILITY_MODEL_WORKFLOW_SOURCE_FROZEN,
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
    def test_exact_sources_open_one_guarded_result_authorization(
        self,
    ) -> None:
        source = validate_stability_model_workflow_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            source["stability_model_execution_gate_decision"],
            STABILITY_MODEL_EXECUTION_GATE_DECISION,
        )
        self.assertEqual(
            STABILITY_MODEL_EXECUTION_GATE_DECISION,
            "DEC-107",
        )
        self.assertEqual(
            source[
                "stability_model_execution_authorization_decision"
            ],
            STABILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
        )
        self.assertEqual(
            STABILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
            "DEC-109",
        )

        self.assertEqual(
            source["dec104_merged_commit"],
            DEC104_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec105_merged_commit"],
            DEC105_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec106_merged_commit"],
            DEC106_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec107_merged_commit"],
            DEC107_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec108_merged_commit"],
            DEC108_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec107_workflow_blob_sha"],
            DEC107_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            source["dec107_cli_blob_sha"],
            DEC107_CLI_BLOB_SHA,
        )
        self.assertEqual(
            source["dec107_gate_blob_sha"],
            DEC107_GATE_BLOB_SHA,
        )
        self.assertEqual(
            source["dec108_review_blob_sha"],
            DEC108_REVIEW_BLOB_SHA,
        )
        self.assertEqual(
            source["stability_runner_blob_sha"],
            DEC106_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            source["stability_core_blob_sha"],
            DEC105_CORE_BLOB_SHA,
        )
        self.assertEqual(
            source["stability_protocol_blob_sha"],
            DEC104_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            source["stability_workflow_blob_sha"],
            STABILITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            source["stability_cli_blob_sha"],
            STABILITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            source["authorized_python_version"],
            AUTHORIZED_PYTHON_VERSION,
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            STABILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )

        gate = build_stability_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "STABILITY_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            gate["stability_model_workflow_source_frozen"]
        )
        self.assertTrue(
            gate["stability_model_run_dispatch_authorized"]
        )
        self.assertTrue(
            gate[
                "authoritative_stability_model_result_execution_authorized"
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
            STABILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertTrue(
            STABILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertTrue(
            AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertTrue(
            STABILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertTrue(STABILITY_MODEL_FIT_AUTHORIZED)
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_accepts_exact_authorized_sources(
        self,
    ) -> None:
        result = require_authoritative_stability_model_execution(
            repository_root=ROOT,
            code_commit="a" * 40,
        )
        self.assertEqual(result["code_commit"], "a" * 40)
        self.assertTrue(
            result["stability_model_run_dispatch_authorized"]
        )
        self.assertTrue(
            result[
                "authoritative_stability_model_result_execution_authorized"
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
            "name: phase8a-exp046-stability-model-training",
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
            "Reject any prior manual main EXP-046 model run"
        )
        authorization = text.index(
            "Require separately authorized EXP-046 result execution"
        )
        self.assertLess(guard, authorization)
        self.assertIn(
            "actions/workflows/"
            "phase8a-exp046-stability-model-training.yml/runs"
            "?branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn(
            'current["id"] == int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            'current["name"] == '
            '"phase8a-exp046-stability-model-training"',
            text,
        )
        self.assertIn(
            'current["path"] == '
            '".github/workflows/'
            'phase8a-exp046-stability-model-training.yml"',
            text,
        )
        self.assertIn(
            'item.get("id") != int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            "prior manual-main EXP-046 model run exists",
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
                "requirements/exp046-model-run.txt -e ."
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

    def test_cli_has_no_dispatch_or_execution_bypass(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_stability_model_execution("
        )
        readiness_load = text.index(
            "load_training_readiness(args.readiness)"
        )
        model_run = text.index(
            "run_stability_model_cell_core("
        )
        aggregate = text.index(
            "compile_stability_model_result_evidence("
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
