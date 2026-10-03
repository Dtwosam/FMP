from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_proof_workflow_dispatch_authorization import (
    EXPECTED_DISPATCH_PREFLIGHT_BLOB_SHA,
    EXPECTED_PROOF_WORKFLOW_RUN_ATTEMPT,
    EXPECTED_PROOF_WORKFLOW_RUN_NUMBER,
    EXPLICIT_PROOF_WORKFLOW_DISPATCH_AUTHORIZED,
    build_proof_workflow_dispatch_authorization,
    validate_proof_workflow_dispatch_authorization_sources,
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-487 requires the installed proof workflow",
)
class AnnualPatternCatalogueProofWorkflowDispatchAuthorizationTests(
    unittest.TestCase
):
    def test_sources_pin_dec486_and_active_workflow(self) -> None:
        source = validate_proof_workflow_dispatch_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dispatch_preflight_blob_sha"],
            EXPECTED_DISPATCH_PREFLIGHT_BLOB_SHA,
        )
        self.assertEqual(
            source["active_proof_workflow_blob_sha"],
            "0d6c93e2af04501f9ac2589fd24d6672b2b41910",
        )

    def test_authorization_is_one_shot_and_proof_only(self) -> None:
        value = build_proof_workflow_dispatch_authorization(
            repository_root=Path("."),
        )
        self.assertEqual(value["decision"], "DEC-487")
        self.assertEqual(
            value["authorization_basis"],
            "explicit_operator_authorization",
        )
        self.assertTrue(value["explicit_proof_workflow_dispatch_authorized"])
        self.assertTrue(value["proof_workflow_dispatch_authorized"])
        self.assertEqual(
            value["proof_workflow_run_count_before_authorized_action"],
            0,
        )
        self.assertEqual(
            value["expected_proof_workflow_run_number"],
            EXPECTED_PROOF_WORKFLOW_RUN_NUMBER,
        )
        self.assertEqual(
            value["expected_proof_workflow_run_attempt"],
            EXPECTED_PROOF_WORKFLOW_RUN_ATTEMPT,
        )
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["retry_authorized"])
        self.assertFalse(value["replacement_run_authorized"])
        self.assertFalse(value["repository_mutation_authorized"])
        self.assertFalse(value["annual_workflow_install_authorized"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertEqual(
            value["next_gate"],
            (
                "EXACT_FIRST_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_"
                "DISPATCH_ON_CURRENT_MAIN"
            ),
        )

    def test_public_constants_match_first_run_scope(self) -> None:
        self.assertTrue(EXPLICIT_PROOF_WORKFLOW_DISPATCH_AUTHORIZED)
        self.assertEqual(EXPECTED_PROOF_WORKFLOW_RUN_NUMBER, 1)
        self.assertEqual(EXPECTED_PROOF_WORKFLOW_RUN_ATTEMPT, 1)


if __name__ == "__main__":
    unittest.main()
