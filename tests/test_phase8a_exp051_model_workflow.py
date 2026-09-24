from __future__ import annotations

from pathlib import Path
import unittest

from fmp.market_learning.model_successor_temporal_calibrated_utility_execution_gate import (
    AUTHORIZED_PYTHON_VERSION,
    AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED,
    BROKER_MUTATION_AUTHORIZED,
    DEC150_MERGED_COMMIT,
    DEC150_PROTOCOL_BLOB_SHA,
    DEC151_CORE_BLOB_SHA,
    DEC151_MERGED_COMMIT,
    DEC152_MERGED_COMMIT,
    DEC152_RUNNER_BLOB_SHA,
    PROMOTION_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_CLI_BLOB_SHA,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_EXECUTION_GATE_DECISION,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_FIT_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN,
    TEMPORAL_CALIBRATED_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
    TEMPORAL_CALIBRATED_UTILITY_WORKFLOW_BLOB_SHA,
    TRADING_AUTHORIZED,
    build_temporal_calibrated_utility_model_workflow_source_gate,
    require_authoritative_temporal_calibrated_utility_model_execution,
    validate_temporal_calibrated_utility_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp051-temporal-calibrated-utility-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp051_model_run.py"
REQUIREMENTS = ROOT / "requirements/exp051-model-run.txt"


class Exp051TemporalCalibratedUtilityWorkflowTests(
    unittest.TestCase
):
    def test_exact_source_chain_and_closed_authorization(
        self,
    ) -> None:
        source = (
            validate_temporal_calibrated_utility_model_workflow_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            source[
                "temporal_calibrated_utility_model_execution_gate_decision"
            ],
            TEMPORAL_CALIBRATED_UTILITY_MODEL_EXECUTION_GATE_DECISION,
        )
        self.assertEqual(
            TEMPORAL_CALIBRATED_UTILITY_MODEL_EXECUTION_GATE_DECISION,
            "DEC-153",
        )
        self.assertEqual(
            source["dec150_merged_commit"],
            DEC150_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec151_merged_commit"],
            DEC151_MERGED_COMMIT,
        )
        self.assertEqual(
            source["dec152_merged_commit"],
            DEC152_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC152_MERGED_COMMIT,
            "9f8fc93096fb29579924932c5c3b526598afaf28",
        )
        self.assertEqual(
            source["temporal_calibrated_utility_runner_blob_sha"],
            DEC152_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            source["temporal_calibrated_utility_core_blob_sha"],
            DEC151_CORE_BLOB_SHA,
        )
        self.assertEqual(
            source["temporal_calibrated_utility_protocol_blob_sha"],
            DEC150_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            source["temporal_calibrated_utility_workflow_blob_sha"],
            TEMPORAL_CALIBRATED_UTILITY_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            source["temporal_calibrated_utility_cli_blob_sha"],
            TEMPORAL_CALIBRATED_UTILITY_CLI_BLOB_SHA,
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            TEMPORAL_CALIBRATED_UTILITY_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )
        self.assertEqual(
            source["authorized_python_version"],
            AUTHORIZED_PYTHON_VERSION,
        )

        gate = build_temporal_calibrated_utility_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
        )
        self.assertTrue(
            gate[
                "temporal_calibrated_utility_model_workflow_source_frozen"
            ]
        )
        for field in (
            "temporal_calibrated_utility_model_run_dispatch_authorized",
            "authoritative_temporal_calibrated_utility_model_result_execution_authorized",
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
            TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN
        )
        self.assertFalse(
            TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED
        )
        self.assertFalse(
            AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(
            TEMPORAL_CALIBRATED_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED
        )
        self.assertFalse(
            TEMPORAL_CALIBRATED_UTILITY_MODEL_FIT_AUTHORIZED
        )
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(BROKER_MUTATION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_execution_requirement_fails_at_dispatch_authorization(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "EXP-051 model-run dispatch is not authorized",
        ):
            require_authoritative_temporal_calibrated_utility_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )

    def test_workflow_is_manual_main_only_and_input_free(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp051-temporal-calibrated-utility-model-training",
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

    def test_workflow_has_no_first_run_guard_yet(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn(
            "Reject any prior manual main EXP-051 model run",
            text,
        )
        self.assertNotIn(
            "prior manual-main EXP-051 model run exists",
            text,
        )
        self.assertNotIn(
            "actions/workflows/"
            "phase8a-exp051-temporal-calibrated-utility-model-training.yml/runs",
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
                "requirements/exp051-model-run.txt -e ."
            ),
            3,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertIn(
            'READINESS_ARTIFACT_ID: "10757578276"',
            text,
        )
        self.assertEqual(
            text.count("scripts/phase8a_exp051_model_run.py"),
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
            "exp051-temporal-calibrated-utility-model-cell-results-",
            text,
        )
        self.assertIn(
            "exp051-temporal-calibrated-utility-model-result-evidence-",
            text,
        )
        self.assertIn(
            "from-feature-35867307338-outcome-35876715434",
            text,
        )

    def test_cli_gate_precedes_readiness_fit_and_aggregate(
        self,
    ) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_temporal_calibrated_utility_model_execution("
        )
        readiness_load = text.index(
            "load_training_readiness(args.readiness)"
        )
        model_run = text.index(
            "run_temporal_calibrated_utility_model_cell_core("
        )
        aggregate = text.index(
            "compile_temporal_calibrated_utility_model_result_evidence("
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
