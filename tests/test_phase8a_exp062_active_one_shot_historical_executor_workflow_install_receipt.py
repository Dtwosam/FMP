from __future__ import annotations

from pathlib import Path
import os
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_receipt import (
    ACTIVE_EXECUTOR_WORKFLOW_PATH,
    EXECUTOR_WORKFLOW_BLOB_SHA,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_install_receipt,
    validate_active_one_shot_historical_executor_workflow_install_receipt_sources,
)


@unittest.skipIf(\n    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",\n    "DEC-424 current-state tests require the installed workflow",\n)\nclass Exp062ActiveOneShotHistoricalExecutorWorkflowInstallReceiptTests(
    unittest.TestCase
):
    def test_active_workflow_is_exact_pinned_template(self) -> None:
        source = validate_active_one_shot_historical_executor_workflow_install_receipt_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec423_mutation_authorization"],
            "df6a80d1f6ee6315f3e3095433ed6704666ccd33",
        )
        self.assertEqual(
            source["dormant_executor_workflow_template"],
            EXECUTOR_WORKFLOW_BLOB_SHA,
        )
        self.assertEqual(
            source["active_executor_workflow"],
            EXECUTOR_WORKFLOW_BLOB_SHA,
        )
        active = Path(ACTIVE_EXECUTOR_WORKFLOW_PATH).read_bytes()
        dormant = Path(
            "docs/superpowers/templates/"
            "phase8a-exp062-one-shot-historical-executor.yml.disabled"
        ).read_bytes()
        self.assertEqual(active, dormant)

    def test_receipt_marks_installed_but_dispatch_locked(self) -> None:
        receipt = build_active_one_shot_historical_executor_workflow_install_receipt(
            repository_root=Path("."),
        )
        self.assertEqual(receipt["decision"], "DEC-424")
        self.assertTrue(receipt["explicit_repository_mutation_authorized"])
        self.assertTrue(receipt["historical_executor_workflow_install_authorized"])
        self.assertTrue(receipt["historical_executor_workflow_installed"])
        self.assertTrue(receipt["historical_executor_available"])
        self.assertFalse(receipt["historical_result_dispatch_authorized"])
        self.assertFalse(receipt["historical_execute_mode_available"])
        self.assertFalse(receipt["trading_authorized"])
        self.assertEqual(
            receipt["next_gate"],
            "EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZATION_BEFORE_RUN",
        )

    def test_installed_workflow_is_manual_only(self) -> None:
        text = Path(ACTIVE_EXECUTOR_WORKFLOW_PATH).read_text(encoding="utf-8")
        self.assertIn("  workflow_dispatch:", text)
        self.assertNotIn("  push:", text)
        self.assertNotIn("  pull_request:", text)
        self.assertIn("  actions: write", text)
        self.assertIn(
            "gh workflow run phase8a-exp062-discovery.yml --ref main",
            text,
        )

    def test_public_state_separates_availability_from_dispatch(self) -> None:
        self.assertTrue(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertTrue(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)


if __name__ == "__main__":
    unittest.main()
