from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest

from fmp.market_learning.model_successor_execution_gate import (
    AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED,
    AUTHORIZED_PYTHON_VERSION,
    DEC094_FAILURE_REVIEW_BLOB_SHA,
    DEC095_PROTOCOL_BLOB_SHA,
    DEC096_CORE_BLOB_SHA,
    DEC097_MERGED_COMMIT,
    DEC097_RUNNER_BLOB_SHA,
    SUCCESSOR_CLI_BLOB_SHA,
    SUCCESSOR_MODEL_EXECUTION_GATE_DECISION,
    SUCCESSOR_MODEL_FIT_AUTHORIZED,
    SUCCESSOR_MODEL_PROTOCOL_RESULT_AUTHORIZED,
    SUCCESSOR_MODEL_RUN_DISPATCH_AUTHORIZED,
    SUCCESSOR_MODEL_WORKFLOW_SOURCE_FROZEN,
    SUCCESSOR_RUNTIME_REQUIREMENTS_BLOB_SHA,
    SUCCESSOR_WORKFLOW_BLOB_SHA,
    build_successor_model_workflow_source_gate,
    require_authoritative_successor_model_execution,
    validate_successor_model_workflow_sources,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp045-model-training.yml"
)
CLI = ROOT / "scripts/phase8a_exp045_model_run.py"


class Exp045ModelWorkflowSourceTests(unittest.TestCase):
    def test_exact_source_gate_is_frozen_and_non_executable(self) -> None:
        source = validate_successor_model_workflow_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            source["dec097_merged_commit"],
            DEC097_MERGED_COMMIT,
        )
        self.assertEqual(
            source["successor_runner_blob_sha"],
            DEC097_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            source["successor_core_blob_sha"],
            DEC096_CORE_BLOB_SHA,
        )
        self.assertEqual(
            source["successor_protocol_blob_sha"],
            DEC095_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            source["failure_review_blob_sha"],
            DEC094_FAILURE_REVIEW_BLOB_SHA,
        )
        self.assertEqual(
            source["successor_workflow_blob_sha"],
            SUCCESSOR_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            source["successor_cli_blob_sha"],
            SUCCESSOR_CLI_BLOB_SHA,
        )
        self.assertEqual(
            source["runtime_requirements_blob_sha"],
            SUCCESSOR_RUNTIME_REQUIREMENTS_BLOB_SHA,
        )
        self.assertEqual(
            source["authorized_python_version"],
            AUTHORIZED_PYTHON_VERSION,
        )

        gate = build_successor_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "SUCCESSOR_MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
        )
        self.assertEqual(
            gate["successor_model_execution_gate_decision"],
            SUCCESSOR_MODEL_EXECUTION_GATE_DECISION,
        )
        self.assertIs(
            SUCCESSOR_MODEL_WORKFLOW_SOURCE_FROZEN,
            True,
        )
        self.assertIs(
            SUCCESSOR_MODEL_RUN_DISPATCH_AUTHORIZED,
            False,
        )
        self.assertIs(
            AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED,
            False,
        )
        self.assertIs(
            SUCCESSOR_MODEL_PROTOCOL_RESULT_AUTHORIZED,
            False,
        )
        self.assertIs(SUCCESSOR_MODEL_FIT_AUTHORIZED, False)
        self.assertIs(
            gate["successor_model_run_dispatch_authorized"],
            False,
        )
        self.assertIs(
            gate[
                "authoritative_successor_model_result_execution_authorized"
            ],
            False,
        )
        self.assertIs(
            gate["model_protocol_result_authorized"],
            False,
        )
        self.assertIs(gate["model_fit_authorized"], False)
        self.assertIs(gate["promotion_authorized"], False)
        self.assertIs(gate["trading_authorized"], False)

    def test_execution_requirement_refuses_before_any_model_work(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "model-run dispatch is not authorized",
        ):
            require_authoritative_successor_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )

    def test_bound_source_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            market = root / "src/fmp/market_learning"
            market.mkdir(parents=True)
            for name in (
                "model_successor_artifacts.py",
                "model_successor_training.py",
                "model_successor_protocol.py",
                "model_run_failure_review.py",
                "model_artifacts.py",
                "contracts.py",
                "outcomes.py",
            ):
                shutil.copy2(
                    ROOT / "src/fmp/market_learning" / name,
                    market / name,
                )

            models = root / "src/fmp/models"
            models.mkdir(parents=True)
            shutil.copy2(
                ROOT / "src/fmp/models/preprocessing.py",
                models / "preprocessing.py",
            )

            features = root / "src/fmp/features"
            features.mkdir(parents=True)
            shutil.copy2(
                ROOT / "src/fmp/features/schema.py",
                features / "schema.py",
            )

            workflow = (
                root
                / ".github/workflows/"
                "phase8a-exp045-model-training.yml"
            )
            workflow.parent.mkdir(parents=True)
            shutil.copy2(WORKFLOW, workflow)

            cli = root / "scripts/phase8a_exp045_model_run.py"
            cli.parent.mkdir(parents=True)
            shutil.copy2(CLI, cli)

            requirements = root / "requirements"
            requirements.mkdir()
            shutil.copy2(
                ROOT / "requirements/exp045-model-run.txt",
                requirements / "exp045-model-run.txt",
            )
            shutil.copy2(
                ROOT / "pyproject.toml",
                root / "pyproject.toml",
            )

            validate_successor_model_workflow_sources(
                repository_root=root,
            )

            workflow.write_text(
                workflow.read_text(encoding="utf-8")
                + "\n# drift\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "workflow Git blob mismatch",
            ):
                validate_successor_model_workflow_sources(
                    repository_root=root,
                )

    def test_workflow_is_manual_main_only_and_has_no_user_inputs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("inputs:", text)
        self.assertNotIn("push:", text)
        self.assertIn(
            'test "$GITHUB_EVENT_NAME" = "workflow_dispatch"',
            text,
        )
        self.assertIn(
            'test "$GITHUB_REF" = "refs/heads/main"',
            text,
        )

    def test_authorization_preflight_blocks_all_result_jobs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        authorization = text.index("authorization-preflight:")
        cells = text.index("model-cells:")
        aggregate = text.index("aggregate-model-evidence:")
        self.assertLess(authorization, cells)
        self.assertLess(cells, aggregate)
        self.assertIn(
            "needs: authorization-preflight",
            text[cells:aggregate],
        )
        self.assertIn(
            "needs: model-cells",
            text[aggregate:],
        )
        self.assertLess(
            text.index(
                "Require separately authorized EXP-045 result execution"
            ),
            text.index(
                "Download exact frozen feature, outcome, and readiness artifacts"
            ),
        )

    def test_workflow_preserves_successor_evidence_policy(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        pair = text.index(
            "Upload pair/timeframe EXP-045 model-cell evidence"
        )
        aggregate = text.index(
            "Upload aggregate EXP-045 model-result evidence"
        )
        pair_block = text[pair:aggregate]
        self.assertIn("if: always()", pair_block)
        self.assertIn("path: .results", pair_block)
        self.assertIn("if-no-files-found: warn", pair_block)
        self.assertIn(
            "include-hidden-files: true",
            pair_block,
        )
        self.assertIn(
            "path: .model-evidence/model-result-evidence.json",
            text[aggregate:],
        )
        self.assertIn(
            "include-hidden-files: true",
            text[aggregate:],
        )

    def test_workflow_freezes_exact_artifacts_horizons_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(text.count("feature_artifact_id:"), 9)
        self.assertEqual(text.count("outcome_artifact_id:"), 9)
        self.assertEqual(text.count("feature_zip_sha256:"), 9)
        self.assertEqual(text.count("outcome_zip_sha256:"), 9)
        self.assertIn("READINESS_ARTIFACT_ID: \"10757578276\"", text)
        self.assertIn(
            "d35248b0690531561818ce13ec6bf371bf31eeaf120182d75eb788417a97ffa8",
            text,
        )
        self.assertIn("for horizon in 60 240; do", text)
        self.assertEqual(
            text.count('python-version: "3.12.14"'),
            3,
        )
        self.assertEqual(
            text.count(
                "python -m pip install -r "
                "requirements/exp045-model-run.txt -e ."
            ),
            3,
        )

        requirements = (
            ROOT / "requirements/exp045-model-run.txt"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            requirements,
            "numpy==2.5.3\n"
            "scipy==1.18.1\n"
            "scikit-learn==1.9.1\n"
            "joblib==1.6.0\n"
            "threadpoolctl==3.7.0\n"
            "cloudpickle==3.1.2\n"
            "narwhals==2.26.0\n"
            "polars==1.44.2\n"
            "polars-runtime-32==1.44.2\n",
        )

    def test_cli_has_no_bypass_around_execution_gate(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        require_call = text.index(
            "require_authoritative_successor_model_execution("
        )
        readiness_load = text.index(
            "load_training_readiness(args.readiness)"
        )
        model_run = text.index(
            "run_successor_model_cell_core("
        )
        aggregate = text.index(
            "compile_successor_model_result_evidence("
        )
        self.assertLess(require_call, readiness_load)
        self.assertLess(require_call, model_run)
        self.assertLess(require_call, aggregate)
        self.assertIn(
            "raise SystemExit(str(exc)) from exc",
            text,
        )


if __name__ == "__main__":
    unittest.main()
