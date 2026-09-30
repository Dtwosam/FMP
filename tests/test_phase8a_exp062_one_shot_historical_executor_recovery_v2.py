from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_recovery_v2_authorization import (
    build_recovery_v2_authorization,
    validate_recovery_v2_authorization_sources,
)


WORKFLOW = Path(
    ".github/workflows/"
    "phase8a-exp062-one-shot-historical-executor-recovery-v2.yml"
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-439 recovery v2 exists only after the failed DEC-436 recovery",
)
class Exp062RecoveryV2Tests(unittest.TestCase):
    def test_authorization_pins_both_failures_and_locks(self) -> None:
        value = build_recovery_v2_authorization(repository_root=Path("."))
        self.assertEqual(value["decision"], "DEC-439")
        self.assertEqual(value["failed_original_executor_run_id"], 36702494195)
        self.assertEqual(value["failed_recovery_run_id"], 36707978889)
        self.assertEqual(value["failed_recovery_job_id"], 109862691026)
        self.assertFalse(value["failed_recovery_dispatched_historical_result"])
        self.assertEqual(value["historical_result_attempt_count"], 0)
        self.assertTrue(value["historical_result_slot_verified_available"])
        self.assertEqual(value["expected_recovery_v2_run_number"], 1)
        self.assertEqual(value["expected_recovery_v2_run_attempt"], 1)
        self.assertEqual(value["expected_target_run_number"], 2)
        self.assertEqual(value["expected_target_run_attempt"], 1)
        self.assertTrue(
            value["explicit_one_shot_executor_recovery_v2_dispatch_authorized"]
        )
        for field in (
            "historical_execute_mode_available",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
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
            self.assertFalse(value[field], field)

    def test_source_bindings_pin_runtime_and_workflows(self) -> None:
        source = validate_recovery_v2_authorization_sources(
            repository_root=Path(".")
        )
        self.assertEqual(
            source["pinned_runtime"],
            "1ff32214dee10d877a067e750cd69ffad96d5fe5",
        )
        self.assertEqual(
            source["dec436_recovery_workflow"],
            "a2520a108373d25d67dd470794eeb4f0fc9e3187",
        )

    def test_workflow_installs_runtime_before_fmp_import(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        install = text.index(
            "python -m pip install -r requirements/exp061-discovery-run.txt"
        )
        import_step = text.index("Require exact DEC-439 authorization")
        self.assertLess(install, import_step)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_workflow_pins_failed_dec436_and_only_dispatches_discovery(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("36707978889", text)
        self.assertIn("109862691026", text)
        self.assertIn(
            'assert steps["Dispatch the sole historical result run"] == "skipped"',
            text,
        )
        command = "gh workflow run phase8a-exp062-discovery.yml --ref main"
        self.assertEqual(text.count(command), 2)
        self.assertEqual(
            text.count('row.get("head_sha") == os.environ["GITHUB_SHA"]'),
            2,
        )
        self.assertNotIn("gh workflow run phase8b", text.lower())
        self.assertNotIn("gh workflow run phase9", text.lower())


if __name__ == "__main__":
    unittest.main()
