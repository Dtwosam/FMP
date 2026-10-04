from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_workflow_corrected_install_receipt import (
    validate_corrected_annual_workflow_install_receipt_sources,
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "corrected installed-state validator requires active annual workflow",
)
class AnnualCatalogueCorrectedInstallReceiptTests(unittest.TestCase):
    def test_historical_and_corrected_workflow_blobs_are_distinct_and_exact(self) -> None:
        value = validate_corrected_annual_workflow_install_receipt_sources(
            repository_root=Path("."),
        )
        self.assertEqual(value["decision"], "DEC-520")
        self.assertEqual(value["historical_install_receipt_decision"], "DEC-491")
        self.assertEqual(
            value["dormant_annual_workflow_template_blob_sha"],
            "31633e87b79551f5b7dfa6b0deb76a82eb070129",
        )
        self.assertEqual(
            value["active_annual_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertNotEqual(
            value["dormant_annual_workflow_template_blob_sha"],
            value["active_annual_workflow_blob_sha"],
        )


if __name__ == "__main__":
    unittest.main()
