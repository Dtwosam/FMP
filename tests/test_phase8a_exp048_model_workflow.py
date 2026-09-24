from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_regime_consensus_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_REGIME_CONSENSUS_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC123_MERGED_COMMIT,
    DEC123_PROTOCOL_BLOB_SHA,
    DEC124_CORE_BLOB_SHA,
    DEC124_MERGED_COMMIT,
    DEC125_MERGED_COMMIT,
    DEC125_RUNNER_BLOB_SHA,
    DEC126_CLI_BLOB_SHA,
    DEC126_GATE_BLOB_SHA,
    DEC126_MERGED_COMMIT,
    DEC126_WORKFLOW_BLOB_SHA,
    DEC127_MERGED_COMMIT,
    DEC127_REVIEW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    REGIME_CONSENSUS_CLI_BLOB_SHA,
    REGIME_CONSENSUS_MODEL_EXECUTION_AUTHORIZATION_DECISION,
    REGIME_CONSENSUS_MODEL_EXECUTION_GATE_DECISION,
    REGIME_CONSENSUS_MODEL_FIT_AUTHORIZED,
    REGIME_CONSENSUS_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    REGIME_CONSENSUS_MODEL_RUN_DISPATCH_AUTHORIZED,
    REGIME_CONSENSUS_MODEL_WORKFLOW_SOURCE_FROZEN,
    REGIME_CONSENSUS_RUNTIME_REQUIREMENTS_BLOB_SHA,
    REGIME_CONSENSUS_WORKFLOW_BLOB_SHA,
    TRADING_AUTHORIZED,
    build_regime_consensus_model_workflow_source_gate,
    require_authoritative_regime_consensus_model_execution,
    validate_regime_consensus_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp048-regime-consensus-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp048_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp048-model-run.txt"


class Exp048WorkflowSourceTests(unittest.TestCase):
    def test_exact_sources_open_one_guarded_result_authorization(self) -> None:
        source = validate_regime_consensus_model_workflow_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            source[
                "regime_consensus_model_execution_gate_decision"
            ],
            REGIME_CONSENSUS_MODEL_EXECUTION_GATE_DECISION,
        )
        self.assertEqual(
            REGIME_CONSENSUS_MODEL_EXECUTION_GATE_DECISION,
            "DEC-126",
        )
        self.assertEqual(
            source["dec123_merged_commit"],
            DEC123_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec124_merged_commit"],
            DEC124_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec125_merged_commit"],
            DEC125_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec126_merged_commit"],
            DEC126_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec127_merged_commit"],
            DEC127_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec126_workflow_blob_sha"],
            DEC126_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            source["dec126_cli_blob_sha"],
            DEC126_CLI_BLOB_SHA,
        )
        self.assertEqual(
            source["dec126_gate_blob_sha"],
            DEC126_GATE_BLOB_SHA,
        )
        self.assertEqual(
            source["dec127_review_blob_sha"],
            DEC127_REVIEW_BLOB_SHA,
        )
        self.assertEqual(
            source[
                "regime_consensus_model_execution_authorization_decision"
            ],
            REGIME_CONSENSUS_MODEL_EXECUTION_AUTHORIZATION_DECISION,
        )
        self.assertEqual(
            REGIME_CONSENSUS_MODEL_EXECUTION_AUTHORIZATION_DECISION,
            "DEC-128",
        )
        self.assertEqual(
            source["regime_consensus_runner_blob_sha"],
            DEC125_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            source["regime_consensus_core_blob_sha"],
            DEC124_CORE_BLOB_SHA,
        )
        self.assertEqual(
            source["regime_consensus_protocol_blob_sha"],
            DEC123_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            source["regime_consensus_workflow_blob_sha"],
            REGIME_CONSENSUS_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            source["regime_consensus_cli_blob_sha"],
            REGIME_CONSENSUS_CLI_BLOB_SHA,
        )
        self.assertEqual(
            source["authorized_python_version"],
            AUTHORIZED_PYTHON_VERSION,
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            REGIME_CONSENSUS_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )

        gate = build_regime_consensus_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "REGIME_CONSENSUS_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            gate[
                "regime_consensus_model_workflow_source_frozen"
            ]
        )
        self.assertTrue(
            gate[
                "regime_consensus_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            gate[
                "authoritative_regime_consensus_model_result_execution_authorized"
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
            REGIME_CONSENSUS_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertTrue(
            REGIME_CONSENSUS_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertTrue(
            AUTHORITATIVE_REGIME_CONSENSUS_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertTrue(
            REGIME_CONSENSUS_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertTrue(
            REGIME_CONSENSUS_MODEL_FIT_AUTHORIZED
        )
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_accepts_exact_authorized_sources(
        self,
    ) -> None:
        result = require_authoritative_regime_consensus_model_execution(
            repository_root=ROOT,
            code_commit="a" * 40,
        )
        self.assertEqual(result["code_commit"], "a" * 40)
        self.assertTrue(
            result[
                "regime_consensus_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            result[
                "authoritative_regime_consensus_model_result_execution_authorized"
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
            "name: phase8a-exp048-regime-consensus-model-training",
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
            "Reject any prior manual main EXP-048 model run"
        )
        authorization = text.index(
            "Require separately authorized EXP-048 result execution"
        )
        self.assertLess(guard, authorization)
        self.assertIn(
            "actions/workflows/"
            "phase8a-exp048-regime-consensus-model-training.yml/runs"
            "?branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn(
            'current["id"] == int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            'current["name"] == '
            '"phase8a-exp048-regime-consensus-model-training"',
            text,
        )
        self.assertIn(
            'current["path"] == '
            '".github/workflows/'
            'phase8a-exp048-regime-consensus-model-training.yml"',
            text,
        )
        self.assertIn(
            'item.get("id") != int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            "prior manual-main EXP-048 model run exists",
            text,
        )

    def test_workflow_uses_exact_matrix_and_pinned_runtime(self) -> None:
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
                "requirements/exp048-model-run.txt -e ."
            ),
            3,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn(
            'READINESS_ARTIFACT_ID: "10757578276"',
            text,
        )
        self.assertEqual(
            text.count(
                "scripts/phase8a_exp048_model_run.py"
            ),
            6,
        )

    def test_workflow_preserves_partial_and_aggregate_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: always()", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: warn", text)
        self.assertIn(
            "exp048-regime-consensus-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp048-regime-consensus-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_has_no_dispatch_or_execution_bypass(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_regime_consensus_model_execution("
        )
        readiness_load = text.index(
            "load_training_readiness(args.readiness)"
        )
        model_run = text.index(
            "run_regime_consensus_model_cell_core("
        )
        aggregate = text.index(
            "compile_regime_consensus_model_result_evidence("
        )
        self.assertLess(require_call, readiness_load)
        self.assertLess(require_call, model_run)
        self.assertLess(require_call, aggregate)
        self.assertIn(
            "raise SystemExit(str(exc)) from exc",
            text,
        )
        self.assertNotIn("gh workflow run", text)
        self.assertNotIn("workflow_dispatch", text)

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
