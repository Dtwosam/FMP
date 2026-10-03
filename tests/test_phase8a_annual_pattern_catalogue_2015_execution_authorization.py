from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fmp.discovery import annual_pattern_catalogue_runtime as runtime
from fmp.discovery.annual_pattern_catalogue_2015_execution_authorization import (
    EXPECTED_ANNUAL_WORKFLOW_RUN_ATTEMPT,
    EXPECTED_ANNUAL_WORKFLOW_RUN_NUMBER,
    build_2015_execution_authorization,
    require_2015_execution_authorized,
    validate_2015_execution_authorization_sources,
)


CODE_COMMIT = "a" * 40


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-493 requires the installed annual catalogue workflow",
)
class AnnualPatternCatalogue2015ExecutionAuthorizationTests(unittest.TestCase):
    def test_sources_pin_preflight_receipt_and_active_workflow(self) -> None:
        source = validate_2015_execution_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["execution_preflight_blob_sha"],
            "d36343a6f2c69ccc2f942e537f5599cbc92b263b",
        )
        self.assertEqual(
            source["install_receipt_blob_sha"],
            "970ab466dfa5f87c6955ad65da4653a993e9d6fd",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "31633e87b79551f5b7dfa6b0deb76a82eb070129",
        )

    def test_authorization_scope_is_exact_first_2015_run_only(self) -> None:
        value = build_2015_execution_authorization(repository_root=Path("."))
        self.assertEqual(value["decision"], "DEC-493")
        self.assertEqual(value["annual_segment_label"], "2015")
        self.assertEqual(
            value["expected_run_number"],
            EXPECTED_ANNUAL_WORKFLOW_RUN_NUMBER,
        )
        self.assertEqual(
            value["expected_run_attempt"],
            EXPECTED_ANNUAL_WORKFLOW_RUN_ATTEMPT,
        )
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["retry_authorized"])
        self.assertFalse(value["replacement_run_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["cross_year_result_production_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_direct_authorization_accepts_only_2015_run_1_attempt_1(self) -> None:
        require_2015_execution_authorized(
            annual_segment_label="2015",
            code_commit=CODE_COMMIT,
            run_number=1,
            run_attempt=1,
        )

        for segment, number, attempt, message in (
            ("2016", 1, 1, "only for 2015"),
            ("2015", 2, 1, "run number 1"),
            ("2015", 1, 2, "run attempt 1"),
        ):
            with self.subTest(segment=segment, number=number, attempt=attempt):
                with self.assertRaisesRegex(PermissionError, message):
                    require_2015_execution_authorized(
                        annual_segment_label=segment,
                        code_commit=CODE_COMMIT,
                        run_number=number,
                        run_attempt=attempt,
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

    def test_runtime_accepts_exact_explicit_2015_identity(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            runtime.require_historical_catalogue_execution_authorized(
                code_commit=CODE_COMMIT,
                annual_segment_label="2015",
                run_number=1,
                run_attempt=1,
            )

    def test_runtime_resolves_github_dispatch_event_and_run_identity(self) -> None:
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
                    "GITHUB_RUN_NUMBER": "1",
                    "GITHUB_RUN_ATTEMPT": "1",
                },
                clear=True,
            ):
                runtime.require_historical_catalogue_execution_authorized(
                    code_commit=CODE_COMMIT,
                )

    def test_runtime_rejects_later_segment_from_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            event_path = Path(tmp) / "event.json"
            event_path.write_text(
                json.dumps({"inputs": {"annual_segment_label": "2016"}}),
                encoding="utf-8",
            )
            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event_path),
                    "GITHUB_RUN_NUMBER": "1",
                    "GITHUB_RUN_ATTEMPT": "1",
                },
                clear=True,
            ):
                with self.assertRaisesRegex(
                    PermissionError,
                    "only for 2015",
                ):
                    runtime.require_historical_catalogue_execution_authorized(
                        code_commit=CODE_COMMIT,
                    )


if __name__ == "__main__":
    unittest.main()
