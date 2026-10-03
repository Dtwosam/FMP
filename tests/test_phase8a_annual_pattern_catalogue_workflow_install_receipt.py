from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_workflow_install_receipt import (
    ANNUAL_WORKFLOW_AVAILABLE,
    ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED,
    ANNUAL_WORKFLOW_INSTALLED,
    EXPECTED_ANNUAL_WORKFLOW_BLOB_SHA,
    build_annual_workflow_install_receipt,
    validate_annual_workflow_install_receipt_sources,
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-491 requires the installed annual catalogue workflow",
)
class AnnualPatternCatalogueWorkflowInstallReceiptTests(unittest.TestCase):
    def test_sources_pin_runtime_binding_contract_and_exact_workflow(self) -> None:
        source = validate_annual_workflow_install_receipt_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["runtime_evidence_binding_source"],
            "ed6eccd796a6c35f9ed768a4bc1ce2d4ae78f830",
        )
        self.assertEqual(
            source["install_contract_source"],
            "f9ac5dc517ec3efbb50057ade66c5b5aab2f52b3",
        )
        self.assertEqual(
            source["dormant_annual_workflow_template"],
            EXPECTED_ANNUAL_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            source["active_annual_workflow"],
            EXPECTED_ANNUAL_WORKFLOW_BLOB_SHA,
        )

    def test_receipt_consumes_install_authorization_only(self) -> None:
        value = build_annual_workflow_install_receipt(
            repository_root=Path("."),
        )
        self.assertEqual(value["decision"], "DEC-491")
        self.assertEqual(
            value["stage"],
            "ANNUAL_CATALOGUE_WORKFLOW_INSTALLED_EXECUTION_LOCKED",
        )
        self.assertEqual(
            value["authorization_basis"],
            "explicit_operator_authorization",
        )
        self.assertTrue(value["annual_workflow_install_authorized"])
        self.assertTrue(value["annual_workflow_install_authorization_consumed"])
        self.assertTrue(value["annual_workflow_installed"])
        self.assertTrue(value["annual_workflow_available"])
        self.assertEqual(value["execution_gate_count"], 3)
        self.assertFalse(value["repository_mutation_authorized"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_artifact_read_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["historical_result_production_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["cross_year_result_production_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["promotion_authorized"])
        self.assertFalse(value["phase8b_authorized"])
        self.assertFalse(value["demo_order_authorized"])
        self.assertFalse(value["broker_mutation_authorized"])
        self.assertFalse(value["live_order_authorized"])
        self.assertFalse(value["real_money_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertEqual(
            value["next_gate"],
            (
                "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_EXECUTION_"
                "AUTHORIZATION_BEFORE_RUN"
            ),
        )

    def test_public_installed_state_is_dispatch_locked(self) -> None:
        self.assertTrue(ANNUAL_WORKFLOW_INSTALLED)
        self.assertTrue(ANNUAL_WORKFLOW_AVAILABLE)
        self.assertFalse(ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED)


if __name__ == "__main__":
    unittest.main()
