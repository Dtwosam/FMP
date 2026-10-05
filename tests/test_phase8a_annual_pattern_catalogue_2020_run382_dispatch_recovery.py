from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2020_run382_dispatch_recovery_authorization import (
    build_2020_run382_dispatch_recovery_authorization,
    validate_2020_run382_dispatch_recovery_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PREINSTALL_SNAPSHOT = os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1"
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2020-run382-dispatch-recovery.yml"
)


@unittest.skipIf(
    PREINSTALL_SNAPSHOT,
    "DEC-578 requires the installed 2020 runtime state",
)
class AnnualPatternCatalogue2020Run382DispatchRecoveryTests(unittest.TestCase):
    def test_authorization_pins_failed_dispatcher_and_empty_slot(self) -> None:
        value = build_2020_run382_dispatch_recovery_authorization(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(value["decision"], "DEC-578")
        self.assertEqual(value["failed_dispatcher_decision"], "DEC-576")
        self.assertEqual(value["failed_dispatcher_run_id"], 37390547252)
        self.assertEqual(value["failed_dispatcher_job_id"], 112034309419)
        self.assertEqual(
            value["failed_dispatcher_head_sha"],
            "3baf4b86a53b4d53d2fc5788b9776006eeacfeee",
        )
        self.assertEqual(value["failed_dispatcher_run_number"], 1)
        self.assertEqual(value["failed_dispatcher_run_attempt"], 1)
        self.assertEqual(value["failed_dispatcher_conclusion"], "failure")
        self.assertFalse(value["failed_dispatcher_dispatched_annual_run"])
        self.assertEqual(value["annual_run_382_attempt_count"], 0)
        self.assertFalse(value["annual_run_382_slot_consumed"])
        self.assertTrue(value["annual_run_382_slot_verified_available"])
        self.assertEqual(value["expected_recovery_run_number"], 1)
        self.assertEqual(value["expected_recovery_run_attempt"], 1)
        self.assertEqual(value["expected_target_run_number"], 382)
        self.assertEqual(value["expected_target_run_attempt"], 1)
        self.assertTrue(value["explicit_recovery_dispatch_authorized"])
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["retry_authorized"])
        self.assertFalse(value["replacement_run_authorized"])
        self.assertFalse(value["run_383_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])
        fingerprint = value["authorization_fingerprint_sha256"]
        self.assertIsInstance(fingerprint, str)
        self.assertEqual(len(fingerprint), 64)
        int(fingerprint, 16)

    def test_authorization_sources_preserve_failed_executor_and_runtime(self) -> None:
        source = validate_2020_run382_dispatch_recovery_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["dec575_source_blob_sha"],
            "26b2148f0d1f49eb8b817f2b2504a11dcb99199a",
        )
        self.assertEqual(
            source["original_dispatcher_workflow_blob_sha"],
            "8da7e442ee91e68dc0f4d22947d46c7709f10022",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "695a50b418da752e1bd37d6302f209033ab611f5",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "4e124365430672fa63825b272001937c60151644",
        )

    def test_recovery_is_exact_first_push_executor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-run382-dispatch-recovery",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  actions: write", text)
        self.assertIn("  contents: read", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)

    def test_failed_dec576_provenance_is_fail_closed(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37390547252",
            "112034309419",
            "3baf4b86a53b4d53d2fc5788b9776006eeacfeee",
        ):
            self.assertIn(value, text)
        self.assertIn(
            'steps["Fetch and verify exact DEC-575 final preflight"] == "failure"',
            text,
        )
        self.assertIn(
            'steps["Dispatch exact 2020 annual run 382"] == "skipped"',
            text,
        )
        self.assertIn(
            'steps["Write immutable DEC-576 dispatch receipt"] == "skipped"',
            text,
        )
        self.assertIn("assert artifacts == []", text)
        self.assertNotIn("gh run rerun", text)

    def test_recovery_verifies_dec575_says_run382(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'assert value["expected_run_number"] == 382',
            text,
        )
        self.assertNotIn(
            'assert value["expected_run_number"] == 381',
            text,
        )
        self.assertIn(
            "f0aad3d285539bbe2f0124db0a0869cc9a6813892c5be75252c46ade933a0a92",
            text,
        )

    def test_recovery_dispatches_exactly_one_fresh_run382(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(text.count(command), 1)
        self.assertIn("--ref main", text)
        self.assertIn("-f annual_segment_label=2020", text)
        self.assertIn(
            "-f previous_annual_freeze_run_id=37310525635",
            text,
        )
        self.assertIn('row.get("run_number") == 382', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertIn('row["run_number"] >= 383', text)
        self.assertNotIn("-f annual_segment_label=2021", text)

    def test_recovery_receipt_keeps_all_later_authority_locked(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-578"', text)
        self.assertIn(
            '"stage": "ANNUAL_CATALOGUE_2020_RUN_382_RECOVERY_DISPATCH_SUBMITTED"',
            text,
        )
        self.assertIn('"failed_dispatcher_decision": "DEC-576"', text)
        self.assertIn('"dispatch_submitted": True', text)
        self.assertIn('"result_claimed": False', text)
        for field in (
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "run_383_or_later_authorized",
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
            self.assertIn(f'"{field}": False', text)


if __name__ == "__main__":
    unittest.main()
