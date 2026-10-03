from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fmp.discovery import annual_pattern_catalogue_runtime as runtime
from fmp.discovery.annual_pattern_catalogue_2015_replacement_execution_authorization import (
    build_2015_replacement_execution_authorization,
    require_2015_replacement_execution_authorized,
    validate_2015_replacement_execution_authorization_sources,
)


CODE_COMMIT = "a" * 40


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-498 requires the repaired post-run state",
)
class AnnualPatternCatalogue2015ReplacementExecutionAuthorizationTests(
    unittest.TestCase
):
    def test_sources_pin_preflight_failure_repair_and_workflow(self) -> None:
        source = validate_2015_replacement_execution_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["replacement_preflight_source_blob_sha"],
            "c69f8a9bf1130ae776b06670fba0c63c935afdc1",
        )
        self.assertEqual(
            source["failure_receipt_source_blob_sha"],
            "1ae96e83dc5d895dce1c5f981f1c785401de22f5",
        )
        self.assertEqual(
            source["upload_repair_source_blob_sha"],
            "adfa75b352a561667b8c23efbcfb07af804d1131",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        )

    def test_authorization_scope_is_exact_run_2_attempt_1(self) -> None:
        value = build_2015_replacement_execution_authorization(
            repository_root=Path("."),
        )
        self.assertEqual(value["decision"], "DEC-498")
        self.assertEqual(
            value["authorization_basis"],
            "standing_operator_autonomous_build_authorization",
        )
        self.assertEqual(value["annual_segment_label"], "2015")
        self.assertEqual(value["failed_first_run_id"], 37126711695)
        self.assertEqual(value["expected_run_number"], 2)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertTrue(value["replacement_run_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertFalse(value["rerun_failed_run_authorized"])
        self.assertFalse(value["retry_failed_run_authorized"])
        self.assertFalse(value["third_or_later_run_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_direct_gate_accepts_only_2015_run_2_attempt_1(self) -> None:
        require_2015_replacement_execution_authorized(
            annual_segment_label="2015",
            code_commit=CODE_COMMIT,
            run_number=2,
            run_attempt=1,
        )
        for segment, number, attempt, message in (
            ("2016", 2, 1, "only for annual segment 2015"),
            ("2015", 1, 1, "run number 2"),
            ("2015", 3, 1, "run number 2"),
            ("2015", 2, 2, "run attempt 1"),
        ):
            with self.subTest(
                segment=segment,
                number=number,
                attempt=attempt,
            ):
                with self.assertRaisesRegex(PermissionError, message):
                    require_2015_replacement_execution_authorized(
                        annual_segment_label=segment,
                        code_commit=CODE_COMMIT,
                        run_number=number,
                        run_attempt=attempt,
                    )

    def test_runtime_accepts_exact_explicit_replacement_identity(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            runtime.require_historical_catalogue_execution_authorized(
                code_commit=CODE_COMMIT,
                annual_segment_label="2015",
                run_number=2,
                run_attempt=1,
            )

    def test_runtime_resolves_exact_github_replacement_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            event_path = Path(tmp) / "event.json"
            event_path.write_text(
                json.dumps(
                    {
                        "inputs": {
                            "annual_segment_label": "2015",
                            "previous_annual_freeze_run_id": "",
                        }
                    }
                ),
                encoding="utf-8",
            )
            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event_path),
                    "GITHUB_RUN_NUMBER": "2",
                    "GITHUB_RUN_ATTEMPT": "1",
                },
                clear=True,
            ):
                runtime.require_historical_catalogue_execution_authorized(
                    code_commit=CODE_COMMIT,
                )

    def test_runtime_rejects_third_run(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(PermissionError, "run number 1"):
                runtime.require_historical_catalogue_execution_authorized(
                    code_commit=CODE_COMMIT,
                    annual_segment_label="2015",
                    run_number=3,
                    run_attempt=1,
                )

    def test_runtime_default_call_remains_dec475_locked(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                PermissionError,
                "historical artifact reads remain locked",
            ):
                runtime.require_historical_catalogue_execution_authorized(
                    code_commit=CODE_COMMIT,
                )


if __name__ == "__main__":
    unittest.main()
