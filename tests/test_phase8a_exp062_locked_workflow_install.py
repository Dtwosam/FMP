from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_workflow_install import (
    ACTIVE_WORKFLOW_INSTALLED,
    EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
    EXPECTED_TEMPLATE_BLOB_SHA,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    PROOF_DISPATCH_AUTHORIZED,
    require_historical_result_dispatch_authorized,
    require_proof_dispatch_authorized,
    validate_installed_paths_from_repo,
    validate_locked_workflow_installation,
)
from fmp.discovery.exp062_workflow_source import (
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
    RESERVED_ACTIVE_WORKFLOW_PATH,
    WORKFLOW_DISPATCH_AUTHORIZED,
)


class Exp062LockedWorkflowInstallTests(unittest.TestCase):
    def test_active_workflow_is_exact_frozen_template(self) -> None:
        report = validate_installed_paths_from_repo()
        self.assertTrue(ACTIVE_WORKFLOW_INSTALLED)
        self.assertEqual(
            report["dormant_template_blob_sha"],
            EXPECTED_TEMPLATE_BLOB_SHA,
        )
        self.assertEqual(
            report["active_workflow_blob_sha"],
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            Path(DORMANT_WORKFLOW_TEMPLATE_PATH).read_bytes(),
            Path(RESERVED_ACTIVE_WORKFLOW_PATH).read_bytes(),
        )

    def test_installation_keeps_every_dispatch_and_trading_gate_closed(self) -> None:
        report = validate_installed_paths_from_repo()
        self.assertFalse(WORKFLOW_DISPATCH_AUTHORIZED)
        self.assertFalse(PROOF_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED)
        for field in (
            "workflow_dispatch_authorized",
            "proof_dispatch_authorized",
            "historical_result_dispatch_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(report[field], field)

    def test_proof_and_historical_dispatch_raise_while_locked(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "proof dispatch remains locked",
        ):
            require_proof_dispatch_authorized()
        with self.assertRaisesRegex(
            PermissionError,
            "historical result dispatch remains locked",
        ):
            require_historical_result_dispatch_authorized(
                code_commit="a" * 40,
            )

    def test_semantically_valid_but_modified_workflow_is_rejected(self) -> None:
        dormant = Path(DORMANT_WORKFLOW_TEMPLATE_PATH).read_text(
            encoding="utf-8"
        )
        modified = dormant + "\n# drift\n"
        with self.assertRaisesRegex(ValueError, "differs from frozen"):
            validate_locked_workflow_installation(
                dormant_text=dormant,
                active_text=modified,
            )


if __name__ == "__main__":
    unittest.main()
