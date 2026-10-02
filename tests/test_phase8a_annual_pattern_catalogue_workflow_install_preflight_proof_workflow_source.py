from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_workflow_install_preflight_proof_workflow_source import (
    DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
    EXPECTED_DORMANT_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
    EXPECTED_PREFLIGHT_CLI_BLOB_SHA,
    EXPECTED_PROOF_CONTRACT_BLOB_SHA,
    RESERVED_PROOF_WORKFLOW_PATH,
    proof_workflow_source_payload,
    validate_dormant_proof_workflow_source,
    validate_dormant_proof_workflow_template,
    validate_proof_workflow_source_dependencies,
)


class AnnualPatternCataloguePreflightProofWorkflowSourceTests(
    unittest.TestCase
):
    def test_dependencies_bind_exact_proof_contract_and_preflight_cli(self) -> None:
        value = validate_proof_workflow_source_dependencies(
            repository_root=Path(".")
        )

        self.assertEqual(
            value["proof_contract"],
            EXPECTED_PROOF_CONTRACT_BLOB_SHA,
        )
        self.assertEqual(
            value["preflight_cli"],
            EXPECTED_PREFLIGHT_CLI_BLOB_SHA,
        )

    def test_dormant_template_exists_but_proof_workflow_is_not_installed(self) -> None:
        value = validate_dormant_proof_workflow_source(
            repository_root=Path(".")
        )

        self.assertTrue(Path(DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH).is_file())
        self.assertFalse(Path(RESERVED_PROOF_WORKFLOW_PATH).exists())
        self.assertFalse(value["proof_workflow_present"])
        self.assertFalse(value["proof_workflow_template_install_authorized"])
        self.assertFalse(value["proof_workflow_installed"])
        self.assertFalse(value["proof_workflow_dispatch_authorized"])

    def test_dormant_template_blob_is_exactly_frozen(self) -> None:
        path = Path(DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH)
        payload = path.read_bytes()
        actual = hashlib.sha1(
            f"blob {len(payload)}\0".encode("ascii") + payload
        ).hexdigest()

        self.assertEqual(
            actual,
            EXPECTED_DORMANT_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
        )
        value = validate_dormant_proof_workflow_source(repository_root=Path("."))
        self.assertEqual(
            value["dormant_template_blob_sha"],
            EXPECTED_DORMANT_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
        )

    def test_template_is_read_only_preflight_plan_and_upload_only(self) -> None:
        text = Path(DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH).read_text(
            encoding="utf-8"
        )
        validate_dormant_proof_workflow_template(text)

        self.assertIn(
            "gh api \"repos/$GITHUB_REPOSITORY/branches/main\"",
            text,
        )
        self.assertIn(
            "phase8a_annual_pattern_catalogue_workflow_install_preflight.py plan",
            text,
        )
        self.assertIn(
            '--expected-head-sha "$GITHUB_SHA"',
            text,
        )
        self.assertIn("actions/upload-artifact@v6", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("phase8a_annual_pattern_catalogue.py cell", text)
        self.assertNotIn("phase8a_annual_pattern_catalogue.py freeze", text)

    def test_template_rejects_execution_surface(self) -> None:
        text = Path(DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH).read_text(
            encoding="utf-8"
        )
        tampered = text + "\n# gh workflow run forbidden\n"

        with self.assertRaisesRegex(ValueError, "forbidden surface"):
            validate_dormant_proof_workflow_template(tampered)

    def test_source_payload_keeps_proof_and_annual_workflows_locked(self) -> None:
        payload = proof_workflow_source_payload(repository_root=Path("."))

        self.assertEqual(payload["decision"], "DEC-482")
        self.assertEqual(payload["source_proof_contract_decision"], "DEC-481")
        self.assertEqual(
            payload["next_gate"],
            (
                "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_"
                "WORKFLOW_INSTALL_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT"
            ),
        )
        for field in (
            "proof_workflow_template_install_authorized",
            "proof_workflow_installed",
            "proof_workflow_dispatch_authorized",
            "annual_workflow_install_authorized",
            "annual_workflow_installed",
            "annual_workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "next_segment_execution_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(payload[field], field)


if __name__ == "__main__":
    unittest.main()
