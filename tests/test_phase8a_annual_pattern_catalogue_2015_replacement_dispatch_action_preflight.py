from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2015_replacement_dispatch_action_preflight import (
    build_2015_replacement_dispatch_action_preflight,
    validate_2015_replacement_dispatch_action_preflight,
    validate_2015_replacement_dispatch_action_preflight_sources,
)


HEAD = "a" * 40


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _runs() -> dict[str, object]:
    return {
        "workflow_runs": [
            {
                "id": 37126711695,
                "run_number": 1,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": "fd85a886d07234ad584dcca08692b37e6af54b2e",
                "status": "completed",
                "conclusion": "failure",
            }
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-499 requires the authorized repaired replacement state",
)
class AnnualPatternCatalogue2015ReplacementDispatchActionPreflightTests(
    unittest.TestCase
):
    def test_sources_pin_authorization_runtime_and_repaired_workflow(self) -> None:
        source = validate_2015_replacement_dispatch_action_preflight_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["authorization_source_blob_sha"],
            "00f588ae2f641919a79e8baf1b262f73ce5834b2",
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            "457c1ffe9cd012041a3d6c3a5568776d8c6fe68a",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_exact_inventory_is_dispatch_ready(self) -> None:
        value = build_2015_replacement_dispatch_action_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(
            validate_2015_replacement_dispatch_action_preflight(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-499")
        self.assertEqual(value["failed_first_run_id"], 37126711695)
        self.assertEqual(value["expected_replacement_run_number"], 376)
        self.assertEqual(value["expected_replacement_run_attempt"], 1)
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
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["dispatch_command_present"])

    def test_inventory_drift_is_rejected(self) -> None:
        for rows in (
            [],
            _runs()["workflow_runs"] * 2,
        ):
            with self.subTest(count=len(rows)):
                with self.assertRaisesRegex(
                    ValueError,
                    "exactly one prior annual-catalogue workflow run",
                ):
                    build_2015_replacement_dispatch_action_preflight(
                        repository_root=Path("."),
                        main_branch=_main(),
                        annual_workflow_runs={"workflow_runs": rows},
                        expected_head_sha=HEAD,
                    )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2015_replacement_dispatch_action_preflight(
                repository_root=Path("."),
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        script = Path(
            "scripts/phase8a_annual_pattern_catalogue_2015_replacement_dispatch_action_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
