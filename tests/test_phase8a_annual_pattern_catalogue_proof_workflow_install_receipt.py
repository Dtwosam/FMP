from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_workflow_install_preflight_proof_workflow_install_receipt import (
    EXPECTED_AUTHORIZATION_PREFLIGHT_SOURCE_BLOB_SHA,
    EXPECTED_PROOF_WORKFLOW_BLOB_SHA,
    PROOF_WORKFLOW_AVAILABLE,
    PROOF_WORKFLOW_DISPATCH_AUTHORIZED,
    PROOF_WORKFLOW_INSTALLED,
    build_proof_workflow_install_receipt,
    validate_proof_workflow_install_receipt_sources,
)
from fmp.discovery.annual_pattern_catalogue_workflow_install_preflight_proof_workflow_source import (
    DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
    RESERVED_PROOF_WORKFLOW_PATH,
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-485 current-state tests require the installed proof workflow",
)
class AnnualPatternCatalogueProofWorkflowInstallReceiptTests(unittest.TestCase):
    def test_active_workflow_is_exact_frozen_template(self) -> None:
        source = validate_proof_workflow_install_receipt_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["authorization_preflight_source"],
            EXPECTED_AUTHORIZATION_PREFLIGHT_SOURCE_BLOB_SHA,
        )
        self.assertEqual(
            source["dormant_proof_workflow_template"],
            EXPECTED_PROOF_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            source["active_proof_workflow"],
            EXPECTED_PROOF_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            Path(RESERVED_PROOF_WORKFLOW_PATH).read_bytes(),
            Path(DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH).read_bytes(),
        )

    def test_receipt_marks_installed_but_dispatch_locked(self) -> None:
        receipt = build_proof_workflow_install_receipt(repository_root=Path("."))

        self.assertEqual(receipt["decision"], "DEC-485")
        self.assertEqual(
            receipt["authorization_basis"],
            "explicit_operator_authorization",
        )
        self.assertTrue(receipt["proof_workflow_install_authorized"])
        self.assertTrue(receipt["proof_workflow_install_authorization_consumed"])
        self.assertTrue(receipt["proof_workflow_installed"])
        self.assertTrue(receipt["proof_workflow_available"])
        self.assertFalse(receipt["repository_mutation_authorized"])
        self.assertFalse(receipt["proof_workflow_dispatch_authorized"])
        self.assertFalse(receipt["annual_workflow_install_authorized"])
        self.assertFalse(receipt["historical_catalogue_execution_authorized"])
        self.assertFalse(receipt["trading_authorized"])
        self.assertEqual(
            receipt["next_gate"],
            (
                "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_"
                "DISPATCH_AUTHORIZATION_BEFORE_RUN"
            ),
        )

    def test_installed_workflow_is_manual_read_only_proof(self) -> None:
        text = Path(RESERVED_PROOF_WORKFLOW_PATH).read_text(encoding="utf-8")

        self.assertIn("  workflow_dispatch:", text)
        self.assertNotIn("  push:", text)
        self.assertNotIn("  pull_request:", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  actions: write", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertIn(
            "phase8a_annual_pattern_catalogue_workflow_install_preflight.py plan",
            text,
        )

    def test_public_state_separates_availability_from_dispatch(self) -> None:
        self.assertTrue(PROOF_WORKFLOW_INSTALLED)
        self.assertTrue(PROOF_WORKFLOW_AVAILABLE)
        self.assertFalse(PROOF_WORKFLOW_DISPATCH_AUTHORIZED)


if __name__ == "__main__":
    unittest.main()
