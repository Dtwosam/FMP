from __future__ import annotations

import copy
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_workflow_install_preflight_proof_workflow_install_contract import (
    EXPECTED_PROOF_WORKFLOW_SOURCE_BLOB_SHA,
    EXPECTED_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
    PROOF_CONTRACT_SOURCE_PATH,
    PROOF_WORKFLOW_SOURCE_PATH,
    REPOSITORY_MUTATION_AUTHORIZED,
    install_action_payload,
    require_repository_mutation_authorized,
    validate_install_action_payload,
    validate_install_sources,
)
from fmp.discovery.annual_pattern_catalogue_workflow_install_preflight_proof_workflow_source import (
    DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
    PREFLIGHT_CLI_PATH,
    RESERVED_PROOF_WORKFLOW_PATH,
)


class AnnualPatternCataloguePreflightProofWorkflowInstallContractTests(
    unittest.TestCase
):
    def test_install_sources_are_exact_and_active_path_is_absent(self) -> None:
        report = validate_install_sources(repository_root=Path("."))

        self.assertEqual(report["decision"], "DEC-483")
        self.assertEqual(
            report["source_blobs"]["proof_workflow_source"],
            EXPECTED_PROOF_WORKFLOW_SOURCE_BLOB_SHA,
        )
        self.assertEqual(
            report["source_blobs"]["dormant_template"],
            EXPECTED_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
        )
        self.assertFalse(report["proof_workflow_present"])
        self.assertFalse(Path(RESERVED_PROOF_WORKFLOW_PATH).exists())

    def test_install_action_allows_only_exact_proof_workflow_creation(self) -> None:
        payload = install_action_payload(repository_root=Path("."))
        mutation = payload["mutation"]

        self.assertEqual(payload["decision"], "DEC-483")
        self.assertEqual(payload["source_proof_workflow_decision"], "DEC-482")
        self.assertEqual(
            mutation["kind"],
            "create_file_from_exact_source_bytes",
        )
        self.assertEqual(
            mutation["source_path"],
            DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
        )
        self.assertEqual(
            mutation["target_path"],
            RESERVED_PROOF_WORKFLOW_PATH,
        )
        self.assertTrue(mutation["target_must_be_absent"])
        self.assertTrue(mutation["post_install_bytes_must_equal_source"])
        self.assertEqual(
            mutation["source_template_blob_sha"],
            EXPECTED_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
        )
        self.assertEqual(
            payload["files_allowed_to_change"],
            [RESERVED_PROOF_WORKFLOW_PATH],
        )
        for path in (
            DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
            PROOF_WORKFLOW_SOURCE_PATH,
            PROOF_CONTRACT_SOURCE_PATH,
            PREFLIGHT_CLI_PATH,
        ):
            self.assertIn(path, payload["files_forbidden_to_change"])
        self.assertIs(validate_install_action_payload(payload), payload)

    def test_semantic_validator_rejects_nested_target_tampering(self) -> None:
        payload = install_action_payload(repository_root=Path("."))
        tampered = copy.deepcopy(payload)
        mutation = tampered["mutation"]
        assert isinstance(mutation, dict)
        mutation["target_path"] = ".github/workflows/other-proof.yml"

        with self.assertRaisesRegex(ValueError, "mutation payload mismatch"):
            validate_install_action_payload(tampered)

    def test_semantic_validator_rejects_nested_source_tampering(self) -> None:
        payload = install_action_payload(repository_root=Path("."))
        tampered = copy.deepcopy(payload)
        source_validation = tampered["source_validation"]
        assert isinstance(source_validation, dict)
        source_dependencies = source_validation["source_dependencies"]
        assert isinstance(source_dependencies, dict)
        source_dependencies["proof_contract"] = "0" * 40

        with self.assertRaisesRegex(
            ValueError,
            "source validation payload mismatch",
        ):
            validate_install_action_payload(tampered)

    def test_semantic_validator_rejects_extra_field(self) -> None:
        payload = install_action_payload(repository_root=Path("."))
        tampered = copy.deepcopy(payload)
        tampered["unexpected_authority"] = True

        with self.assertRaisesRegex(ValueError, "key set mismatch"):
            validate_install_action_payload(tampered)

    def test_all_mutation_execution_and_trading_authority_remains_false(self) -> None:
        payload = install_action_payload(repository_root=Path("."))

        self.assertEqual(
            payload["next_gate"],
            (
                "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_"
                "PROOF_WORKFLOW_INSTALL_PREFLIGHT"
            ),
        )
        for field in (
            "repository_mutation_authorized",
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

    def test_repository_mutation_gate_is_hard_closed(self) -> None:
        self.assertFalse(REPOSITORY_MUTATION_AUTHORIZED)
        with self.assertRaisesRegex(
            PermissionError,
            "repository mutation remains locked",
        ):
            require_repository_mutation_authorized()


if __name__ == "__main__":
    unittest.main()
