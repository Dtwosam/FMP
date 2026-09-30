from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_dispatch_action_preflight import (
    build_active_one_shot_historical_executor_dispatch_action_preflight,
    executor_dispatch_command,
    shell_join,
    validate_active_one_shot_historical_executor_dispatch_action_preflight,
    validate_active_one_shot_historical_executor_dispatch_action_preflight_sources,
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


def _executor() -> dict[str, object]:
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
    "DEC-431 requires the installed executor workflow",
)
class Exp062ActiveOneShotHistoricalExecutorDispatchActionPreflightTests(
    unittest.TestCase
):
    def test_source_bindings_pin_dec430_and_active_workflow(self) -> None:
        source = validate_active_one_shot_historical_executor_dispatch_action_preflight_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec430_dispatch_authorization_blob_sha"],
            "87aada4c5224c633e8eb419f971c8f7f0699b18f",
        )
        self.assertEqual(
            source["active_executor_workflow_blob_sha"],
            "51ce87584369be957482460d81649adb1cb9f05d",
        )

    def test_empty_one_shot_inventories_are_action_ready(self) -> None:
        value = build_active_one_shot_historical_executor_dispatch_action_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            executor_workflow_runs={"workflow_runs": []},
            discovery_workflow_runs={"workflow_runs": [_proof()]},
            expected_head_sha=HEAD,
        )
        self.assertIs(
            validate_active_one_shot_historical_executor_dispatch_action_preflight(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-431")
        self.assertTrue(value["explicit_one_shot_executor_dispatch_authorized"])
        self.assertEqual(value["executor_workflow_run_count"], 0)
        self.assertEqual(value["historical_result_attempt_count"], 0)
        self.assertTrue(value["historical_result_dispatch_authorized"])
        self.assertFalse(value["historical_execute_mode_available"])
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertEqual(
            value["planned_executor_dispatch_command"],
            shell_join(executor_dispatch_command()),
        )

    def test_existing_executor_run_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "zero executor workflow runs"):
            build_active_one_shot_historical_executor_dispatch_action_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                executor_workflow_runs={"workflow_runs": [_executor()]},
                discovery_workflow_runs={"workflow_runs": [_proof()]},
                expected_head_sha=HEAD,
            )

    def test_existing_historical_result_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unused historical-result slot"):
            build_active_one_shot_historical_executor_dispatch_action_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                executor_workflow_runs={"workflow_runs": []},
                discovery_workflow_runs={"workflow_runs": [_proof(), _historical()]},
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        text = Path(
            "scripts/"
            "phase8a_exp062_active_one_shot_historical_executor_"
            "dispatch_action_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("plan")', text)
        self.assertNotIn('sub.add_parser("dispatch")', text)
        self.assertNotIn('sub.add_parser("execute")', text)
        self.assertNotIn("gh workflow run ", text)


if __name__ == "__main__":
    unittest.main()
