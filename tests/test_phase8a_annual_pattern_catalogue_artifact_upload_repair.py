from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_artifact_upload_repair import (
    EXPECTED_REPAIRED_WORKFLOW_BLOB_SHA,
    build_artifact_upload_repair_receipt,
    validate_artifact_upload_repair_sources,
)


@unittest.skipIf(\n    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",\n    "DEC-495/496 require the post-run repair state",\n)\nclass AnnualPatternCatalogueArtifactUploadRepairTests(unittest.TestCase):
    def test_sources_pin_failure_receipt_and_workflow_transition(self) -> None:
        source = validate_artifact_upload_repair_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["failure_receipt_source_blob_sha"],
            "1ae96e83dc5d895dce1c5f981f1c785401de22f5",
        )
        self.assertEqual(
            source["pre_repair_workflow_blob_sha"],
            "31633e87b79551f5b7dfa6b0deb76a82eb070129",
        )
        self.assertEqual(
            source["repaired_workflow_blob_sha"],
            EXPECTED_REPAIRED_WORKFLOW_BLOB_SHA,
        )

    def test_repair_is_upload_only_and_replacement_remains_locked(self) -> None:
        value = build_artifact_upload_repair_receipt(
            repository_root=Path("."),
        )
        self.assertEqual(value["decision"], "DEC-496")
        self.assertEqual(value["failed_run_id"], 37126711695)
        self.assertFalse(value["failed_run_cell_execution"])
        self.assertFalse(value["failed_run_result_production"])
        self.assertEqual(value["repair_scope"], "upload_hidden_artifacts_only")
        self.assertEqual(value["repaired_upload_count"], 3)
        self.assertTrue(value["include_hidden_files"])
        self.assertTrue(value["preflight_upload_repaired"])
        self.assertTrue(value["cell_product_upload_repaired"])
        self.assertTrue(value["annual_freeze_upload_repaired"])
        self.assertTrue(value["first_run_authorization_consumed"])
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["retry_authorized"])
        self.assertFalse(value["replacement_run_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertEqual(
            value["next_gate"],
            (
                "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_REPLACEMENT_RUN_"
                "AUTHORIZATION_BEFORE_DISPATCH"
            ),
        )


if __name__ == "__main__":
    unittest.main()
