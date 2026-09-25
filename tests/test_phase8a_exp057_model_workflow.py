from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_repair_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC220_MERGED_COMMIT,
    DEC220_PROTOCOL_BLOB_SHA,
    DEC221_CORE_BLOB_SHA,
    DEC221_MERGED_COMMIT,
    DEC222_RUNNER_BLOB_SHA,
    DEC223_CLI_BLOB_SHA,
    DEC223_GATE_BLOB_SHA,
    DEC223_MERGED_COMMIT,
    DEC223_WORKFLOW_BLOB_SHA,
    DEC224_MERGED_COMMIT,
    DEC224_REVIEW_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_CLI_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_EXECUTION_GATE_DECISION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RUN_DISPATCH_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_WORKFLOW_SOURCE_FROZEN,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_RUNTIME_REQUIREMENTS_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_WORKFLOW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    TRADING_AUTHORIZED,
    build_fit_temporal_residual_lower_tail_utility_repair_model_workflow_source_gate,
    require_authoritative_fit_temporal_residual_lower_tail_utility_repair_model_execution,
    validate_fit_temporal_residual_lower_tail_utility_repair_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp057_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp057-model-run.txt"


class Exp057ResidualLowerTailWorkflowTests(unittest.TestCase):
    def test_exact_sources_open_one_guarded_result_authorization(self) -> None:
        source = (
            validate_fit_temporal_residual_lower_tail_utility_repair_model_workflow_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_EXECUTION_GATE_DECISION,
            "DEC-223",
        )
        self.assertEqual(
            source[
                "fit_temporal_residual_lower_tail_utility_repair_model_execution_gate_decision"
            ],
            "DEC-223",
        )
        self.assertEqual(
            DEC220_MERGED_COMMIT,
            "865ab1569a0765078ed099008a5722f8a6d310b4",
        )
        self.assertEqual(
            DEC221_MERGED_COMMIT,
            "6ea34dd3c62f72c55376e891eeb44d96ad5de54b",
        )
        self.assertEqual(
            source["dec222_merged_commit"],
            "51e9ccde9feaada7932384fc4547b721c1341588",
        )
        self.assertEqual(source["dec223_merged_commit"], DEC223_MERGED_COMMIT)
        self.assertEqual(
            DEC223_MERGED_COMMIT,
            "160c618352739a1ae12b86c80be9573e4c2f234a",
        )
        self.assertEqual(source["dec224_merged_commit"], DEC224_MERGED_COMMIT)
        self.assertEqual(
            DEC224_MERGED_COMMIT,
            "e0f2328334d6da6b52cad53f23c9a3b05eeb72cd",
        )
        self.assertEqual(
            source[
                "fit_temporal_residual_lower_tail_utility_repair_model_execution_authorization_decision"
            ],
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_EXECUTION_AUTHORIZATION_DECISION,
            "DEC-225",
        )
        self.assertEqual(source["dec223_workflow_blob_sha"], DEC223_WORKFLOW_BLOB_SHA)
        self.assertEqual(DEC223_WORKFLOW_BLOB_SHA, "db9d8ccaa7da674124963acc6ab4e65e6c2ad83f")
        self.assertEqual(source["dec223_cli_blob_sha"], DEC223_CLI_BLOB_SHA)
        self.assertEqual(DEC223_CLI_BLOB_SHA, "889b2daa4e44175e0479377d6c8ea39846da596d")
        self.assertEqual(source["dec223_gate_blob_sha"], DEC223_GATE_BLOB_SHA)
        self.assertEqual(DEC223_GATE_BLOB_SHA, "07c7db8bc7fc29cf595aa617f1d66ec4f77e4879")
        self.assertEqual(source["dec224_review_blob_sha"], DEC224_REVIEW_BLOB_SHA)
        self.assertEqual(DEC224_REVIEW_BLOB_SHA, "1a5f3e86b4d445ba4a77f3496f81de2b16b333cd")
        self.assertEqual(
            source["fit_temporal_residual_lower_tail_utility_repair_runner_blob_sha"],
            DEC222_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            DEC222_RUNNER_BLOB_SHA,
            "d69eb668ade480b66faf992190b3a4929f414960",
        )
        self.assertEqual(
            source["fit_temporal_residual_lower_tail_utility_repair_core_blob_sha"],
            DEC221_CORE_BLOB_SHA,
        )
        self.assertEqual(
            DEC221_CORE_BLOB_SHA,
            "ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd",
        )
        self.assertEqual(
            source["fit_temporal_residual_lower_tail_utility_repair_protocol_blob_sha"],
            DEC220_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC220_PROTOCOL_BLOB_SHA,
            "2f355526476a4d41967bb46e1bfad6aa525cbfa9",
        )
        self.assertEqual(
            source["fit_temporal_residual_lower_tail_utility_repair_workflow_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_WORKFLOW_BLOB_SHA,
            "2f28eea9f1e9cb941a91553bd6a7dc93245da7f8",
        )
        self.assertEqual(
            source["fit_temporal_residual_lower_tail_utility_repair_cli_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_CLI_BLOB_SHA,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_CLI_BLOB_SHA,
            "889b2daa4e44175e0479377d6c8ea39846da596d",
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )
        self.assertEqual(source["authorized_python_version"], AUTHORIZED_PYTHON_VERSION)

        gate = build_fit_temporal_residual_lower_tail_utility_repair_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            gate[
                "fit_temporal_residual_lower_tail_utility_repair_model_workflow_source_frozen"
            ]
        )
        self.assertTrue(
            gate[
                "fit_temporal_residual_lower_tail_utility_repair_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            gate[
                "authoritative_fit_temporal_residual_lower_tail_utility_repair_model_result_execution_authorized"
            ]
        )
        self.assertTrue(gate["model_protocol_result_authorized"])
        self.assertTrue(gate["model_fit_authorized"])
        self.assertFalse(gate["promotion_authorized"])
        self.assertFalse(gate["shadow_authorized"])
        self.assertFalse(gate["trading_authorized"])

        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertTrue(
            AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertTrue(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertTrue(FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_FIT_AUTHORIZED)
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_accepts_exact_authorized_sources(self) -> None:
        result = (
            require_authoritative_fit_temporal_residual_lower_tail_utility_repair_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )
        )
        self.assertEqual(result["code_commit"], "a" * 40)
        self.assertTrue(
            result[
                "fit_temporal_residual_lower_tail_utility_repair_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            result[
                "authoritative_fit_temporal_residual_lower_tail_utility_repair_model_result_execution_authorized"
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
            "name: phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training",
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
            "Reject any prior manual main EXP-057 model run"
        )
        authorization = text.index(
            "Require separately authorized EXP-057 result execution"
        )
        self.assertLess(guard, authorization)
        self.assertIn(
            "actions/workflows/"
            "phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml/runs"
            "?branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn(
            'current["id"] == int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            'current["name"] == '
            '"phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training"',
            text,
        )
        self.assertIn(
            'current["path"] == '
            '".github/workflows/'
            'phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml"',
            text,
        )
        self.assertIn(
            'item.get("id") != int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            "prior manual-main EXP-057 model run exists",
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
                "python -m pip install -r requirements/exp057-model-run.txt -e ."
            ),
            3,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn('READINESS_ARTIFACT_ID: "10757578276"', text)
        self.assertEqual(text.count("scripts/phase8a_exp057_model_run.py"), 6)

    def test_workflow_preserves_partial_and_aggregate_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: always()", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: warn", text)
        self.assertIn(
            "exp057-fit-temporal-residual-lower-tail-utility-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp057-fit-temporal-residual-lower-tail-utility-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_checks_execution_before_artifact_loading(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_fit_temporal_residual_lower_tail_utility_repair_model_execution("
        )
        readiness_load = text.index("load_training_readiness(args.readiness)")
        model_run = text.index(
            "run_fit_temporal_residual_lower_tail_utility_model_cell_core("
        )
        aggregate = text.index(
            "compile_fit_temporal_residual_lower_tail_utility_repair_model_result_evidence("
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
