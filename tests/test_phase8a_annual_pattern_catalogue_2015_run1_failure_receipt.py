from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2015_run1_failure_receipt import (
    build_2015_run1_failure_receipt,
    validate_2015_run1_failure_receipt_sources,
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-495/496 require the post-run repair state",
)
class AnnualPatternCatalogue2015Run1FailureReceiptTests(unittest.TestCase):
    def test_sources_pin_dispatch_preflight_and_pre_repair_workflow(self) -> None:
        source = validate_2015_run1_failure_receipt_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dispatch_preflight_source_blob_sha"],
            "ac78fb75c4743edaa6883203aac24b3ddb23eeeb",
        )
        self.assertEqual(
            source["pre_repair_workflow_blob_sha"],
            "31633e87b79551f5b7dfa6b0deb76a82eb070129",
        )

    def test_failed_run_is_bound_without_result_authority(self) -> None:
        value = build_2015_run1_failure_receipt(repository_root=Path("."))
        self.assertEqual(value["decision"], "DEC-495")
        self.assertEqual(value["run_id"], 37126711695)
        self.assertEqual(value["run_number"], 1)
        self.assertEqual(value["run_attempt"], 1)
        self.assertEqual(value["run_conclusion"], "failure")
        self.assertEqual(value["preflight_job_id"], 111213380390)
        self.assertEqual(
            value["failing_step"],
            "Upload annual catalogue preflight evidence",
        )
        self.assertEqual(
            value["failure_class"],
            "hidden_artifact_path_filtered_by_upload_action",
        )
        self.assertFalse(value["upload_include_hidden_files"])
        self.assertTrue(value["preflight_files_created_before_failure"])
        self.assertFalse(value["preflight_artifact_uploaded"])
        self.assertFalse(value["annual_cell_jobs_executed"])
        self.assertFalse(value["annual_freeze_job_executed"])
        self.assertFalse(value["catalogue_results_produced"])
        self.assertFalse(value["annual_freeze_produced"])
        self.assertTrue(value["first_run_authorization_consumed"])
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["retry_authorized"])
        self.assertFalse(value["replacement_run_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])


if __name__ == "__main__":
    unittest.main()
