from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_dispatch_authorization import (
    DEC429_RUNTIME_FREEZE_FINGERPRINT_SHA256,
    EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZED,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_dispatch_authorization,
    validate_active_one_shot_historical_executor_dispatch_authorization_sources,
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-430 requires the installed executor workflow",
)
class Exp062ActiveOneShotHistoricalExecutorDispatchAuthorizationTests(
    unittest.TestCase
):
    def test_source_bindings_pin_dec429_and_active_workflow(self) -> None:
        source = validate_active_one_shot_historical_executor_dispatch_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec429_runtime_freeze"],
            "98fbb04a78efeef0a9a1fc919b5e5d61093c09de",
        )
        self.assertEqual(
            source["active_executor_workflow"],
            "51ce87584369be957482460d81649adb1cb9f05d",
        )

    def test_authorization_is_one_shot_and_does_not_add_trading_authority(self) -> None:
        value = build_active_one_shot_historical_executor_dispatch_authorization(
            repository_root=Path("."),
        )
        self.assertEqual(value["decision"], "DEC-430")
        self.assertTrue(value["explicit_one_shot_executor_dispatch_authorized"])
        self.assertTrue(value["historical_executor_workflow_installed"])
        self.assertTrue(value["historical_executor_available"])
        self.assertTrue(value["historical_result_dispatch_authorized"])
        self.assertEqual(value["executor_workflow_run_count"], 0)
        self.assertEqual(value["expected_executor_run_number"], 1)
        self.assertEqual(value["expected_executor_run_attempt"], 1)
        self.assertEqual(value["historical_result_attempt_count"], 0)
        self.assertEqual(value["expected_target_run_number"], 2)
        self.assertEqual(value["expected_target_run_attempt"], 1)
        self.assertFalse(value["historical_execute_mode_available"])
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["retry_authorized"])
        self.assertFalse(value["replacement_run_authorized"])
        self.assertFalse(value["reserved_robustness_access_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertEqual(
            value["next_gate"],
            "READ_ONLY_CURRENT_MAIN_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_BEFORE_RUN",
        )

    def test_public_constants_match_authorized_boundary(self) -> None:
        self.assertTrue(EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZED)
        self.assertTrue(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertTrue(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertTrue(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)
        self.assertEqual(
            DEC429_RUNTIME_FREEZE_FINGERPRINT_SHA256,
            "a561a4a66111c5c2edc3183e68a978b01ead42f9b8f8c8c061244b50fc751dac",
        )


if __name__ == "__main__":
    unittest.main()
