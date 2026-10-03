from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2015_execution_preflight import (
    EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
    EXPECTED_INSTALL_RECEIPT_BLOB_SHA,
    EXPECTED_RUNTIME_SOURCE_BLOB_SHA,
    build_2015_execution_preflight,
    validate_2015_execution_preflight,
    validate_2015_execution_preflight_sources,
)


HEAD = "a" * 40


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _runs() -> dict[str, object]:
    return {"workflow_runs": []}


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-492 requires the installed annual catalogue workflow",
)
class AnnualPatternCatalogue2015ExecutionPreflightTests(unittest.TestCase):
    def test_sources_pin_receipt_runtime_and_active_workflow(self) -> None:
        source = validate_2015_execution_preflight_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["install_receipt_blob_sha"],
            EXPECTED_INSTALL_RECEIPT_BLOB_SHA,
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            EXPECTED_RUNTIME_SOURCE_BLOB_SHA,
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        )

    def test_zero_run_2015_state_is_ready_but_authorization_locked(self) -> None:
        value = build_2015_execution_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2015_execution_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-492")
        self.assertEqual(value["annual_segment_label"], "2015")
        self.assertFalse(value["prior_segment_required"])
        self.assertIsNone(value["prior_segment_label"])
        self.assertIsNone(value["previous_annual_freeze_run_id"])
        self.assertEqual(value["annual_workflow_run_count"], 0)
        self.assertEqual(value["expected_first_run_number"], 1)
        self.assertEqual(value["expected_first_run_attempt"], 1)
        self.assertTrue(value["annual_workflow_installed"])
        self.assertTrue(value["annual_workflow_available"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_artifact_read_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["historical_result_production_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertEqual(
            value["next_gate"],
            (
                "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_EXECUTION_"
                "AUTHORIZATION_BEFORE_RUN"
            ),
        )

    def test_existing_annual_run_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "requires zero annual-catalogue workflow runs",
        ):
            build_2015_execution_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                annual_workflow_runs={
                    "workflow_runs": [{"id": 1, "run_number": 1}]
                },
                expected_head_sha=HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2015_execution_preflight(
                repository_root=Path("."),
                main_branch={
                    "name": "main",
                    "commit": {"sha": "b" * 40},
                },
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_non_main_metadata_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "requires main branch metadata",
        ):
            build_2015_execution_preflight(
                repository_root=Path("."),
                main_branch={"name": "dev", "commit": {"sha": HEAD}},
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        script = Path(
            "scripts/phase8a_annual_pattern_catalogue_2015_execution_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
