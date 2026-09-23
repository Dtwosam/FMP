from pathlib import Path
import shutil
import tempfile
import unittest

from fmp.market_learning.model_execution_gate import (
    AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED,
    DEC088_PROTOCOL_BLOB_SHA,
    DEC090_CORE_BLOB_SHA,
    DEC091_RUNNER_BLOB_SHA,
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    MODEL_RUN_DISPATCH_AUTHORIZED,
    MODEL_RUN_WORKFLOW_SOURCE_FROZEN,
    build_model_workflow_source_gate,
    require_authoritative_model_execution,
    validate_frozen_model_sources,
)
from fmp.market_learning.operator import dispatch_command_for_next_report


ROOT = Path(__file__).resolve().parents[1]


class Exp044ModelExecutionGateTests(unittest.TestCase):
    def test_exact_frozen_sources_open_workflow_source_only(self) -> None:
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

        gate = build_model_workflow_source_gate(
            repository_root=ROOT,
        )
        self.assertEqual(
            gate["stage"],
            "MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
        )
        self.assertIs(MODEL_RUN_WORKFLOW_SOURCE_FROZEN, True)
        self.assertIs(MODEL_RUN_DISPATCH_AUTHORIZED, False)
        self.assertIs(
            AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED,
            False,
        )
        self.assertIs(MODEL_PROTOCOL_RESULT_AUTHORIZED, False)
        self.assertIs(MODEL_FIT_AUTHORIZED, False)
        self.assertIs(
            gate["model_run_dispatch_authorized"],
            False,
        )
        self.assertIs(
            gate["authoritative_model_result_execution_authorized"],
            False,
        )

    def test_authoritative_execution_is_fail_closed(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "dispatch is not authorized",
        ):
            require_authoritative_model_execution(
                repository_root=ROOT,
                code_commit="a" * 40,
            )

    def test_frozen_workflow_stage_is_not_operator_dispatchable(self) -> None:
        report = {
            "read_only": True,
            "stage": "MODEL_RUN_WORKFLOW_SOURCE_FROZEN",
            "model_protocol_result_authorized": False,
            "model_fit_authorized": False,
            "promotion_authorized": False,
            "trading_authorized": False,
        }
        self.assertIsNone(dispatch_command_for_next_report(report))

    def test_frozen_source_blob_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "src/fmp/market_learning"
            target.mkdir(parents=True)
            for name in (
                "model_artifacts.py",
                "model_training.py",
                "model_protocol.py",
            ):
                shutil.copy2(
                    ROOT / "src/fmp/market_learning" / name,
                    target / name,
                )
            (target / "model_artifacts.py").write_text(
                (target / "model_artifacts.py").read_text(
                    encoding="utf-8"
                )
                + "\n# drift\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "artifact_runner Git blob mismatch",
            ):
                validate_frozen_model_sources(
                    repository_root=root,
                )


if __name__ == "__main__":
    unittest.main()
