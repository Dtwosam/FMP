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
    PROMOTION_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_CLI_BLOB_SHA,
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
    def test_exact_sources_remain_non_executable(self) -> None:
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
            source["dec141_merged_commit"],
            DEC141_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC141_MERGED_COMMIT,
            "4729da0e769f76f44b97ff6349ee25c5b7c0f5c7",
        )
        self.assertEqual(
            source["dec142_merged_commit"],
            DEC142_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC142_MERGED_COMMIT,
            "fa6fd14a880a84a44795efe4099679ed0f642497",
        )
        self.assertEqual(
            source["dec143_merged_commit"],
            DEC143_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC143_MERGED_COMMIT,
            "f0f584f2bfa1d6f0858af46312e41ffde5fe7d71",
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
            (
                "TEMPORAL_JACKKNIFE_UTILITY_MODEL_"
                "RUN_WORKFLOW_SOURCE_FROZEN"
            ),
        )
        self.assertTrue(
            gate[
                "temporal_jackknife_utility_model_workflow_source_frozen"
            ]
        )
        for field in (
            "temporal_jackknife_utility_model_run_dispatch_authorized",
            "authoritative_temporal_jackknife_utility_model_result_execution_authorized",
            "model_protocol_result_authorized",
            "model_fit_authorized",
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(gate[field], False)

        self.assertTrue(
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertFalse(
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertFalse(
            AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertFalse(
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_FIT_AUTHORIZED
        )
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "model-run dispatch is not authorized",
        ):
            require_authoritative_temporal_jackknife_utility_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )

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

    def test_workflow_has_no_run_authorization_guard_yet(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn(
            "Reject any prior manual main EXP-050 model run",
            text,
        )
        self.assertNotIn(
            "prior manual-main EXP-050 model run exists",
            text,
        )
        self.assertIn(
            "Require separately authorized EXP-050 result execution",
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
