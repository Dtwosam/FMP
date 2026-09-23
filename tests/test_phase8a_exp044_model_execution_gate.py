from pathlib import Path
import shutil
import tempfile
import unittest

from fmp.market_learning.model_execution_gate import (
    AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC088_PROTOCOL_BLOB_SHA,
    DEC090_CORE_BLOB_SHA,
    DEC091_RUNNER_BLOB_SHA,
    DEC092_CLI_BLOB_SHA,
    DEC092_MERGED_COMMIT,
    DEC092_WORKFLOW_BLOB_SHA,
    DEC093_WORKFLOW_BLOB_SHA,
    DEC094_WORKFLOW_BLOB_SHA,
    MODEL_EXECUTION_AUTHORIZATION_DECISION,
    MODEL_EXECUTION_CLOSURE_DECISION,
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    MODEL_RUN_DISPATCH_AUTHORIZED,
    MODEL_RUN_WORKFLOW_SOURCE_FROZEN,
    build_model_workflow_source_gate,
    require_authoritative_model_execution,
    validate_authorized_model_execution_sources,
    validate_frozen_model_sources,
)
from fmp.market_learning.operator import dispatch_command_for_next_report


ROOT = Path(__file__).resolve().parents[1]


class Exp044ModelExecutionGateTests(unittest.TestCase):
    def test_exact_sources_are_preserved_but_v1_execution_is_closed(self) -> None:
        source = validate_frozen_model_sources(repository_root=ROOT)
        self.assertEqual(
            source["artifact_runner_blob_sha"],
            DEC091_RUNNER_BLOB_SHA,
        )
        self.assertEqual(
            source["training_core_blob_sha"],
            DEC090_CORE_BLOB_SHA,
        )
        self.assertEqual(
            source["model_protocol_blob_sha"],
            DEC088_PROTOCOL_BLOB_SHA,
        )

        execution = validate_authorized_model_execution_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            execution["dec092_merged_commit"],
            DEC092_MERGED_COMMIT,
        )
        self.assertEqual(
            execution["dec092_workflow_blob_sha"],
            DEC092_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            execution["dec093_workflow_blob_sha"],
            DEC093_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            execution["dec094_workflow_blob_sha"],
            DEC094_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            execution["dec092_cli_blob_sha"],
            DEC092_CLI_BLOB_SHA,
        )

        gate = build_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "MODEL_RUN_EXECUTION_CLOSED",
        )
        self.assertEqual(
            gate["model_execution_authorization_decision"],
            MODEL_EXECUTION_AUTHORIZATION_DECISION,
        )
        self.assertEqual(
            gate["model_execution_closure_decision"],
            MODEL_EXECUTION_CLOSURE_DECISION,
        )
        self.assertIs(MODEL_RUN_WORKFLOW_SOURCE_FROZEN, True)
        self.assertIs(MODEL_RUN_DISPATCH_AUTHORIZED, False)
        self.assertIs(
            AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED,
            False,
        )
        self.assertIs(MODEL_PROTOCOL_RESULT_AUTHORIZED, False)
        self.assertIs(MODEL_FIT_AUTHORIZED, False)
        self.assertIs(gate["model_run_dispatch_authorized"], False)
        self.assertIs(
            gate["authoritative_model_result_execution_authorized"],
            False,
        )
        self.assertIs(
            gate["model_protocol_result_authorized"],
            False,
        )
        self.assertIs(gate["model_fit_authorized"], False)
        self.assertIs(gate["promotion_authorized"], False)
        self.assertIs(gate["trading_authorized"], False)

    def test_authoritative_execution_is_closed_after_reviewed_failure(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "model-run dispatch is not authorized",
        ):
            require_authoritative_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )

    def test_repaired_workflow_blob_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            market = root / "src/fmp/market_learning"
            market.mkdir(parents=True)
            for name in (
                "model_artifacts.py",
                "model_training.py",
                "model_protocol.py",
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
            requirements = root / "requirements"
            requirements.mkdir()
            shutil.copy2(
                ROOT / "requirements/exp044-model-run.txt",
                requirements / "exp044-model-run.txt",
            )
            shutil.copy2(
                ROOT / "pyproject.toml",
                root / "pyproject.toml",
            )

            workflow = (
                root
                / ".github/workflows/"
                "phase8a-exp044-model-training.yml"
            )
            workflow.parent.mkdir(parents=True)
            shutil.copy2(
                ROOT
                / ".github/workflows/"
                "phase8a-exp044-model-training.yml",
                workflow,
            )

            cli = root / "scripts/phase8a_exp044_model_run.py"
            cli.parent.mkdir(parents=True)
            shutil.copy2(
                ROOT / "scripts/phase8a_exp044_model_run.py",
                cli,
            )

            validated = validate_authorized_model_execution_sources(
                repository_root=root,
            )
            self.assertEqual(
                validated["dec094_workflow_blob_sha"],
                DEC094_WORKFLOW_BLOB_SHA,
            )

            workflow.write_text(
                workflow.read_text(encoding="utf-8") + "\n# drift\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "model_workflow Git blob mismatch",
            ):
                validate_authorized_model_execution_sources(
                    repository_root=root,
                )

    def test_reviewed_failure_stage_is_not_dispatchable(self) -> None:
        report = {
            "read_only": True,
            "stage": "MODEL_RUN_FAILURE_REVIEWED",
            "model_protocol_result_authorized": False,
            "model_fit_authorized": False,
            "promotion_authorized": False,
            "trading_authorized": False,
        }
        self.assertIsNone(
            dispatch_command_for_next_report(report)
        )


if __name__ == "__main__":
    unittest.main()
