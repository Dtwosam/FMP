from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.workflow_install import (
    ACTIVE_WORKFLOW_DISPATCH_AUTHORIZED,
    ACTIVE_WORKFLOW_INSTALLED,
    ACTIVE_WORKFLOW_SOURCE_REVIEWED,
    HISTORICAL_RESULT_RUN_AUTHORIZED,
    REVIEWED_WORKFLOW_BLOB_SHA,
    validate_installed_workflow,
    validate_installed_workflow_paths,
    workflow_install_payload,
)
from fmp.discovery.workflow_source import (
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    RESERVED_ACTIVE_WORKFLOW_PATH,
    require_historical_execution_authorized,
)


CODE_COMMIT = "a" * 40


class Exp061GuardedWorkflowInstallTests(unittest.TestCase):
    def test_active_workflow_is_exact_reviewed_template(self) -> None:
        dormant = Path(DORMANT_WORKFLOW_TEMPLATE_PATH).read_text(encoding="utf-8")
        active = Path(RESERVED_ACTIVE_WORKFLOW_PATH).read_text(encoding="utf-8")
        self.assertEqual(active, dormant)
        validate_installed_workflow(
            dormant_text=dormant,
            active_text=active,
        )
        validate_installed_workflow_paths(repository_root=Path("."))

    def test_active_workflow_contains_gate_before_cell_execution(self) -> None:
        text = Path(RESERVED_ACTIVE_WORKFLOW_PATH).read_text(encoding="utf-8")
        preflight_gate = text.index(
            "python scripts/phase8a_exp061.py require-execution"
        )
        cell_job = text.index("  exp061_cell:")
        self.assertLess(preflight_gate, cell_job)
        self.assertIn("name: exp061-preflight", text)
        self.assertIn("name: exp061-aggregate", text)
        self.assertIn("workflow_dispatch:", text)

    def test_install_payload_separates_presence_from_authority(self) -> None:
        payload = workflow_install_payload()
        self.assertTrue(ACTIVE_WORKFLOW_INSTALLED)
        self.assertTrue(ACTIVE_WORKFLOW_SOURCE_REVIEWED)
        self.assertTrue(payload["manual_dispatch_surface_present"])
        self.assertEqual(
            payload["reviewed_workflow_blob_sha"],
            REVIEWED_WORKFLOW_BLOB_SHA,
        )
        self.assertFalse(ACTIVE_WORKFLOW_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_RUN_AUTHORIZED)
        for field in (
            "workflow_dispatch_authorized",
            "historical_result_run_authorized",
            "historical_discovery_execution_authorized",
            "historical_discovery_result_authorized",
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
            self.assertFalse(payload[field], field)

    def test_historical_execution_gate_still_raises_after_install(self) -> None:
        with self.assertRaisesRegex(PermissionError, "execution remains locked"):
            require_historical_execution_authorized(code_commit=CODE_COMMIT)

    def test_mutated_active_workflow_is_rejected(self) -> None:
        dormant = Path(DORMANT_WORKFLOW_TEMPLATE_PATH).read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "must equal reviewed dormant template"):
            validate_installed_workflow(
                dormant_text=dormant,
                active_text=dormant + "\n# drift\n",
            )


if __name__ == "__main__":
    unittest.main()
