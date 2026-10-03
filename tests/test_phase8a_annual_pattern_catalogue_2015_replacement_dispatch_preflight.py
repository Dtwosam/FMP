from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2015_replacement_dispatch_preflight import (
    build_2015_replacement_dispatch_preflight,
    validate_2015_replacement_dispatch_preflight,
    validate_2015_replacement_dispatch_preflight_sources,
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
    "DEC-497 requires the repaired post-run state",
)
class AnnualPatternCatalogue2015ReplacementDispatchPreflightTests(unittest.TestCase):
    def test_sources_pin_failure_receipt_repair_and_workflow(self) -> None:
        source = validate_2015_replacement_dispatch_preflight_sources(
            repository_root=Path("."),
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
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_exact_failed_run_is_ready_but_replacement_locked(self) -> None:
        value = build_2015_replacement_dispatch_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2015_replacement_dispatch_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-497")
        self.assertEqual(value["prior_run_count"], 1)
        self.assertEqual(value["failed_run_id"], 37126711695)
        self.assertEqual(value["expected_replacement_run_number"], 376)
        self.assertEqual(value["expected_replacement_run_attempt"], 1)
        self.assertFalse(value["replacement_run_authorized"])
        self.assertFalse(value["historical_artifact_read_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["historical_result_production_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertTrue(value["preflight_read_only"])

    def test_zero_or_multiple_runs_are_rejected(self) -> None:
        for rows in ([], _runs()["workflow_runs"] * 2):
            with self.subTest(count=len(rows)):
                with self.assertRaisesRegex(
                    ValueError,
                    "exactly one prior annual-catalogue workflow run",
                ):
                    build_2015_replacement_dispatch_preflight(
                        repository_root=Path("."),
                        main_branch=_main(),
                        annual_workflow_runs={"workflow_runs": rows},
                        expected_head_sha=HEAD,
                    )

    def test_successful_prior_run_is_rejected(self) -> None:
        runs = _runs()
        rows = runs["workflow_runs"]
        assert isinstance(rows, list)
        rows[0] = dict(rows[0])
        rows[0]["conclusion"] = "success"
        with self.assertRaisesRegex(ValueError, "conclusion mismatch"):
            build_2015_replacement_dispatch_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                annual_workflow_runs=runs,
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        script = Path(
            "scripts/phase8a_annual_pattern_catalogue_2015_replacement_dispatch_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
