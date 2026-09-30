from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_dispatch_preflight import (
    build_active_one_shot_historical_executor_dispatch_preflight,
    validate_active_one_shot_historical_executor_dispatch_preflight,
    validate_active_one_shot_historical_executor_dispatch_preflight_sources,
)
from fmp.discovery.exp062_runtime_proof_freeze import PROOF_HEAD_SHA, PROOF_RUN_ID


HEAD = "a" * 40


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _proof() -> dict[str, object]:
    return {
        "id": PROOF_RUN_ID,
        "name": "phase8a-exp062-discovery",
        "path": ".github/workflows/phase8a-exp062-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _historical() -> dict[str, object]:
    return {
        "id": 40000000000,
        "name": "phase8a-exp062-discovery",
        "path": ".github/workflows/phase8a-exp062-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": 2,
        "run_attempt": 1,
        "status": "queued",
        "conclusion": None,
    }


def _executor_run() -> dict[str, object]:
    return {
        "id": 50000000000,
        "name": "phase8a-exp062-one-shot-historical-executor",
        "path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": 1,
        "run_attempt": 1,
        "status": "queued",
        "conclusion": None,
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-425 current-state tests require the installed workflow",
)
class Exp062ActiveOneShotHistoricalExecutorDispatchPreflightTests(
    unittest.TestCase
):
    def test_source_bindings_pin_install_receipt_and_active_workflow(self) -> None:
        source = validate_active_one_shot_historical_executor_dispatch_preflight_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec424_install_receipt_blob_sha"],
            "27e714620018413a09ceaf287fb7943bf884ee49",
        )
        self.assertEqual(
            source["active_executor_workflow_blob_sha"],
            "51ce87584369be957482460d81649adb1cb9f05d",
        )

    def test_installed_executor_and_empty_slots_are_read_only_ready(self) -> None:
        plan = build_active_one_shot_historical_executor_dispatch_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            executor_workflow_runs={"workflow_runs": []},
            discovery_workflow_runs={"workflow_runs": [_proof()]},
            expected_head_sha=HEAD,
        )
        self.assertIs(
            validate_active_one_shot_historical_executor_dispatch_preflight(plan),
            plan,
        )
        self.assertEqual(plan["decision"], "DEC-425")
        self.assertTrue(plan["active_executor_workflow_present"])
        self.assertTrue(plan["historical_executor_workflow_installed"])
        self.assertTrue(plan["historical_executor_available"])
        self.assertEqual(plan["executor_workflow_run_count"], 0)
        self.assertEqual(plan["historical_result_attempt_count"], 0)
        self.assertFalse(plan["historical_result_slot_consumed"])
        self.assertTrue(plan["historical_result_slot_verified_available"])
        self.assertFalse(plan["historical_result_dispatch_authorized"])
        self.assertFalse(plan["historical_execute_mode_available"])
        self.assertFalse(plan["trading_authorized"])

    def test_existing_executor_run_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "zero executor workflow runs"):
            build_active_one_shot_historical_executor_dispatch_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                executor_workflow_runs={"workflow_runs": [_executor_run()]},
                discovery_workflow_runs={"workflow_runs": [_proof()]},
                expected_head_sha=HEAD,
            )

    def test_existing_historical_result_run_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unused historical-result slot"):
            build_active_one_shot_historical_executor_dispatch_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                executor_workflow_runs={"workflow_runs": []},
                discovery_workflow_runs={"workflow_runs": [_proof(), _historical()]},
                expected_head_sha=HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        main = _main()
        main["commit"] = {"sha": "b" * 40}
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_active_one_shot_historical_executor_dispatch_preflight(
                repository_root=Path("."),
                main_branch=main,
                executor_workflow_runs={"workflow_runs": []},
                discovery_workflow_runs={"workflow_runs": [_proof()]},
                expected_head_sha=HEAD,
            )

    def test_cli_has_plan_only_and_no_dispatch_surface(self) -> None:
        text = Path(
            "scripts/"
            "phase8a_exp062_active_one_shot_historical_executor_"
            "dispatch_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("plan")', text)
        self.assertNotIn('sub.add_parser("dispatch")', text)
        self.assertNotIn('sub.add_parser("execute")', text)
        self.assertNotIn('sub.add_parser("run")', text)
        self.assertNotIn("gh workflow run ", text)


if __name__ == "__main__":
    unittest.main()
