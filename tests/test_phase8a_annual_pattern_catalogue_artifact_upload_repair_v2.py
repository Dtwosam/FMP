from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_artifact_upload_repair_v2 import (
    EXPECTED_CORRECTED_WORKFLOW_BLOB_SHA,
    build_artifact_upload_repair_v2_receipt,
    validate_artifact_upload_repair_v2_sources,
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-500 requires the corrected post-run workflow state",
)
class AnnualPatternCatalogueArtifactUploadRepairV2Tests(unittest.TestCase):
    def test_sources_pin_prior_repair_and_exact_workflow_transition(self) -> None:
        source = validate_artifact_upload_repair_v2_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["prior_repair_source_blob_sha"],
            "adfa75b352a561667b8c23efbcfb07af804d1131",
        )
        self.assertEqual(
            source["failed_repair_workflow_blob_sha"],
            "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        )
        self.assertEqual(
            source["corrected_workflow_blob_sha"],
            EXPECTED_CORRECTED_WORKFLOW_BLOB_SHA,
        )

    def test_each_upload_site_has_exactly_one_hidden_file_flag(self) -> None:
        receipt = build_artifact_upload_repair_v2_receipt(
            repository_root=Path("."),
        )
        self.assertEqual(receipt["decision"], "DEC-500")
        self.assertEqual(receipt["corrected_upload_count"], 3)
        self.assertEqual(receipt["preflight_hidden_upload_flag_count"], 1)
        self.assertEqual(receipt["cell_hidden_upload_flag_count"], 1)
        self.assertEqual(receipt["freeze_hidden_upload_flag_count"], 1)
        self.assertFalse(receipt["replacement_run_authorized"])
        self.assertFalse(receipt["next_segment_execution_authorized"])
        self.assertFalse(receipt["strategy_v1_synthesis_authorized"])
        self.assertFalse(receipt["promotion_authorized"])
        self.assertFalse(receipt["phase8b_authorized"])
        self.assertFalse(receipt["demo_order_authorized"])
        self.assertFalse(receipt["broker_mutation_authorized"])
        self.assertFalse(receipt["live_order_authorized"])
        self.assertFalse(receipt["real_money_authorized"])
        self.assertFalse(receipt["trading_authorized"])

    def test_corrected_workflow_has_one_flag_per_expected_upload(self) -> None:
        text = Path(
            ".github/workflows/phase8a-annual-pattern-catalogue.yml"
        ).read_text(encoding="utf-8")
        marker = "uses: actions/upload-artifact@v6"
        blocks = [marker + suffix for suffix in text.split(marker)[1:]]
        self.assertEqual(len(blocks), 3)

        expectations = (
            ("phase8a-annual-catalogue-preflight-", "path: .preflight"),
            ("phase8a-annual-catalogue-cell-", "path: .result"),
            (
                "phase8a-annual-catalogue-freeze-",
                "path: .annual-freeze/annual-freeze.json",
            ),
        )
        for name, path in expectations:
            with self.subTest(name=name):
                matches = [block for block in blocks if name in block]
                self.assertEqual(len(matches), 1)
                self.assertIn(path, matches[0])
                self.assertEqual(
                    matches[0].count("include-hidden-files: true"),
                    1,
                )


if __name__ == "__main__":
    unittest.main()
