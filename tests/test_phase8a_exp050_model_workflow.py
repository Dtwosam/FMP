from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_temporal_jackknife_utility_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC141_MERGED_COMMIT,
    DEC141_PROTOCOL_BLOB_SHA,
    DEC142_CORE_BLOB_SHA,
    DEC142_MERGED_COMMIT,
    DEC143_MERGED_COMMIT,
    DEC143_RUNNER_BLOB_SHA,
    DEC144_CLI_BLOB_SHA,
    DEC144_GATE_BLOB_SHA,
    DEC144_MERGED_COMMIT,
    DEC144_WORKFLOW_BLOB_SHA,
    DEC145_MERGED_COMMIT,
    DEC145_REVIEW_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_CLI_BLOB_SHA,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_GATE_DECISION,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_FIT_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN,
    TEMPORAL_JACKKNIFE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
    TEMPORAL_JACKKNIFE_UTILITY_WORKFLOW_BLOB_SHA,
    TRADING_AUTHORIZED,
    build_temporal_jackknife_utility_model_workflow_source_gate,
    require_authoritative_temporal_jackknife_utility_model_execution,
    validate_temporal_jackknife_utility_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp050-temporal-jackknife-utility-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp050_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp050-model-run.txt"


class Exp050WorkflowSourceTests(unittest.TestCase):
    def test_exact_sources_open_one_guarded_result_authorization(
        self,
    ) -> None:
        source = (
            validate_temporal_jackknife_utility_model_workflow_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            source[
                "temporal_jackknife_utility_model_execution_gate_decision"
            ],
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_GATE_DECISION,
        )
        self.assertEqual(
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_GATE_DECISION,
            "DEC-144",
        )
        self.assertEqual(
            source[
                "temporal_jackknife_utility_model_execution_authorization_decision"
            ],
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
        )
        self.assertEqual(
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_EXECUTION_AUTHORIZATION_DECISION,
            "DEC-146",
        )
        self.assertEqual(
            source["dec141_merged_commit"],
            DEC141_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec142_merged_commit"],
            DEC142_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec143_merged_commit"],
            DEC143_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec144_merged_commit"],
            DEC144_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC144_MERGED_COMMIT,
            "9f2986c783823cf7d9647ed4b0a50c66470bea21",
        )
        self.assertEqual(
            source["dec145_merged_commit"],
            DEC145_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC145_MERGED_COMMIT,
            "b2907cced930afa4d877596a8268ec3bc49ceb9c",
        )
        self.assertEqual(
            source["dec144_workflow_blob_sha"],
            DEC144_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            DEC144_WORKFLOW_BLOB_SHA,
            "ec8ed4ab3f0b8a18ffc735af92172e059ed29955",
        )
        self.assertEqual(
            source["dec144_cli_blob_sha"],
            DEC144_CLI_BLOB_SHA,
        )
        self.assertEqual(
            DEC144_CLI_BLOB_SHA,
            "70c5e9b8d22888b9727e234fd80ea3e3ba4e5e09",
        )
        self.assertEqual(
            source["dec144_gate_blob_sha"],
            DEC144_GATE_BLOB_SHA,
        )
        self.assertEqual(
            DEC144_GATE_BLOB_SHA,
            "4814f0db86bec943d7282ab13586559b1eb8caa7",
        )
        self.assertEqual(
            source["dec145_review_blob_sha"],
            DEC145_REVIEW_BLOB_SHA,
        )
        self.assertEqual(
            DEC145_REVIEW_BLOB_SHA,
            "e93f7f26e6f0cf8541c9dffd0d359acf0a7ec64e",
        )
        self.assertEqual(
            source[
                "temporal_jackknife_utility_runner_blob_sha"
            ],
            DEC143_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            source[
                "temporal_jackknife_utility_core_blob_sha"
            ],
            DEC142_CORE_BLOB_SHA,
        )
        self.assertEqual(
            source[
                "temporal_jackknife_utility_protocol_blob_sha"
            ],
            DEC141_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            source[
                "temporal_jackknife_utility_workflow_blob_sha"
            ],
            TEMPORAL_JACKKNIFE_UTILITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            TEMPORAL_JACKKNIFE_UTILITY_WORKFLOW_BLOB_SHA,
            "7a5875c69d8cdf33e9aaae58fc321dba0537ce0b",
        )
        self.assertEqual(
            source[
                "temporal_jackknife_utility_cli_blob_sha"
            ],
            TEMPORAL_JACKKNIFE_UTILITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            source["authorized_python_version"],
            AUTHORIZED_PYTHON_VERSION,
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            TEMPORAL_JACKKNIFE_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )

        gate = (
            build_temporal_jackknife_utility_model_workflow_source_gate(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            gate["stage"],
            "TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_REQUIRED",
        )
        self.assertTrue(
            gate[
                "temporal_jackknife_utility_model_workflow_source_frozen"
            ]
        )
        self.assertTrue(
            gate[
                "temporal_jackknife_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            gate[
                "authoritative_temporal_jackknife_utility_model_result_execution_authorized"
            ]
        )
        self.assertTrue(
            gate["model_protocol_result_authorized"]
        )
        self.assertTrue(gate["model_fit_authorized"])
        self.assertFalse(gate["promotion_authorized"])
        self.assertFalse(gate["shadow_authorized"])
        self.assertFalse(gate["demo_order_authorized"])
        self.assertFalse(gate["broker_mutation_authorized"])
        self.assertFalse(gate["live_order_authorized"])
        self.assertFalse(gate["real_money_authorized"])
        self.assertFalse(gate["trading_authorized"])

        self.assertTrue(
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertTrue(
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertTrue(
            AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertTrue(
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertTrue(
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_FIT_AUTHORIZED
        )
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_accepts_exact_authorized_sources(
        self,
    ) -> None:
        result = (
            require_authoritative_temporal_jackknife_utility_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )
        )
        self.assertEqual(result["code_commit"], "a" * 40)
        self.assertTrue(
            result[
                "temporal_jackknife_utility_model_run_dispatch_authorized"
            ]
        )
        self.assertTrue(
            result[
                "authoritative_temporal_jackknife_utility_model_result_execution_authorized"
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
            "name: phase8a-exp050-temporal-jackknife-utility-model-training",
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
            "Reject any prior manual main EXP-050 model run"
        )
        authorization = text.index(
            "Require separately authorized EXP-050 result execution"
        )
        self.assertLess(guard, authorization)
        self.assertIn(
            "actions/workflows/"
            "phase8a-exp050-temporal-jackknife-utility-model-training.yml/runs"
            "?branch=main&event=workflow_dispatch&per_page=100",
            text,
        )
        self.assertIn(
            'current["id"] == int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            'current["name"] == '
            '"phase8a-exp050-temporal-jackknife-utility-model-training"',
            text,
        )
        self.assertIn(
            'current["path"] == '
            '".github/workflows/'
            'phase8a-exp050-temporal-jackknife-utility-model-training.yml"',
            text,
        )
        self.assertIn(
            'item.get("id") != int(os.environ["GITHUB_RUN_ID"])',
            text,
        )
        self.assertIn(
            "prior manual-main EXP-050 model run exists",
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
                "requirements/exp050-model-run.txt -e ."
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
                "scripts/phase8a_exp050_model_run.py"
            ),
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
            "exp050-temporal-jackknife-utility-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp050-temporal-jackknife-utility-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_has_no_dispatch_or_execution_bypass(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_temporal_jackknife_utility_model_execution("
        )
        readiness_load = text.index(
            "load_training_readiness(args.readiness)"
        )
        model_run = text.index(
            "run_temporal_jackknife_utility_model_cell_core("
        )
        aggregate = text.index(
            "compile_temporal_jackknife_utility_model_result_evidence("
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
