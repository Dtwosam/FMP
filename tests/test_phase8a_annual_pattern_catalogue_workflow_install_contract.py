from __future__ import annotations

import copy
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_workflow_install_contract import (
    EXPECTED_CLI_BLOB_SHA,
    EXPECTED_TEMPLATE_BLOB_SHA,
    EXPECTED_WORKFLOW_SOURCE_BLOB_SHA,
    REPOSITORY_MUTATION_AUTHORIZED,
    install_action_payload,
    require_repository_mutation_authorized,
    validate_install_action_payload,
    validate_install_sources,
)
from fmp.discovery.annual_pattern_catalogue_workflow_source import (
    CLI_PATH,
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    RESERVED_ACTIVE_WORKFLOW_PATH,
)


class AnnualPatternCatalogueWorkflowInstallContractTests(unittest.TestCase):
    def test_install_sources_are_exact_and_active_path_is_absent(self) -> None:
        report = validate_install_sources(repository_root=Path("."))

        self.assertEqual(
            report["source_blobs"]["workflow_source"],
            EXPECTED_WORKFLOW_SOURCE_BLOB_SHA,
        )
        self.assertEqual(report["source_blobs"]["cli"], EXPECTED_CLI_BLOB_SHA)
        self.assertEqual(
            report["source_blobs"]["dormant_template"],
            EXPECTED_TEMPLATE_BLOB_SHA,
        )
        self.assertFalse(report["active_workflow_present"])
        self.assertFalse(Path(RESERVED_ACTIVE_WORKFLOW_PATH).exists())

    def test_install_action_allows_only_exact_active_path_creation(self) -> None:
        payload = install_action_payload(repository_root=Path("."))
        mutation = payload["mutation"]

        self.assertEqual(payload["decision"], "DEC-479")
        self.assertEqual(payload["source_workflow_decision"], "DEC-478")
        self.assertEqual(
            mutation["kind"],
            "create_file_from_exact_source_bytes",
        )
        self.assertEqual(
            mutation["source_path"],
            DORMANT_WORKFLOW_TEMPLATE_PATH,
        )
        self.assertEqual(
            mutation["target_path"],
            RESERVED_ACTIVE_WORKFLOW_PATH,
        )
        self.assertTrue(mutation["target_must_be_absent"])
        self.assertTrue(mutation["post_install_bytes_must_equal_source"])
        self.assertEqual(
            mutation["source_template_blob_sha"],
            EXPECTED_TEMPLATE_BLOB_SHA,
        )
        self.assertEqual(
            payload["files_allowed_to_change"],
            [RESERVED_ACTIVE_WORKFLOW_PATH],
        )
        self.assertIn(
            DORMANT_WORKFLOW_TEMPLATE_PATH,
            payload["files_forbidden_to_change"],
        )
        self.assertIn(CLI_PATH, payload["files_forbidden_to_change"])
        self.assertIs(validate_install_action_payload(payload), payload)

    def test_semantic_validator_rejects_nested_target_tampering(self) -> None:
        payload = install_action_payload(repository_root=Path("."))
        tampered = copy.deepcopy(payload)
        mutation = tampered["mutation"]
        assert isinstance(mutation, dict)
        mutation["target_path"] = ".github/workflows/other.yml"

        with self.assertRaisesRegex(ValueError, "mutation payload mismatch"):
            validate_install_action_payload(tampered)

    def test_semantic_validator_rejects_nested_source_blob_tampering(self) -> None:
        payload = install_action_payload(repository_root=Path("."))
        tampered = copy.deepcopy(payload)
        source_validation = tampered["source_validation"]
        assert isinstance(source_validation, dict)
        source_blobs = source_validation["source_blobs"]
        assert isinstance(source_blobs, dict)
        source_blobs["dormant_template"] = "0" * 40

        with self.assertRaisesRegex(
            ValueError,
            "source validation payload mismatch",
        ):
            validate_install_action_payload(tampered)

    def test_all_mutation_execution_and_trading_authority_remains_false(self) -> None:
        payload = install_action_payload(repository_root=Path("."))

        self.assertEqual(
            payload["next_gate"],
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT",
        )
        for field in (
            "repository_mutation_authorized",
            "workflow_template_install_authorized",
            "workflow_installed",
            "workflow_dispatch_authorized",
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
