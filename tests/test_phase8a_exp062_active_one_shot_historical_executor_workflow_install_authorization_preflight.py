from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_authorization_preflight import (
    build_active_one_shot_historical_executor_workflow_install_authorization_preflight,
    validate_active_one_shot_historical_executor_workflow_install_authorization_preflight,
    validate_active_one_shot_historical_executor_workflow_install_authorization_preflight_sources,
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


def _runs(*extra: dict[str, object]) -> dict[str, object]:
    return {"workflow_runs": [_proof(), *extra]}


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallAuthorizationPreflightTests(
    unittest.TestCase
):
    def test_source_binding_pins_dec372_contract(self) -> None:
        source = (
            validate_active_one_shot_historical_executor_workflow_install_authorization_preflight_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec372_install_authorization_contract_blob_sha"],
            "ac4876d6b544567c238d9241ee050b763c2ed630",
        )

    def test_empty_slot_and_absent_workflow_are_read_only_ready(self) -> None:
        plan = (
            build_active_one_shot_historical_executor_workflow_install_authorization_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )
        )
        self.assertIs(
            validate_active_one_shot_historical_executor_workflow_install_authorization_preflight(
                plan
            ),
            plan,
        )
        self.assertEqual(plan["decision"], "DEC-373")
        self.assertFalse(plan["executor_workflow_path_exists"])
        self.assertTrue(plan["install_authorization_slot_verified_available"])
        self.assertEqual(plan["historical_result_attempt_count"], 0)
        self.assertFalse(plan["historical_result_slot_consumed"])
        self.assertTrue(plan["historical_result_slot_verified_available"])
        self.assertEqual(plan["expected_target_run_number"], 2)
        self.assertEqual(plan["expected_target_run_attempt"], 1)
        self.assertTrue(
            plan[
                "active_one_shot_historical_executor_workflow_"
                "install_authorization_source_authorized"
            ]
        )
        self.assertFalse(plan["historical_executor_workflow_install_authorized"])
        self.assertFalse(plan["historical_executor_workflow_installed"])
        self.assertFalse(plan["historical_executor_available"])
        self.assertFalse(plan["historical_result_dispatch_authorized"])
        self.assertFalse(plan["historical_execute_mode_available"])

    def test_main_head_drift_is_rejected(self) -> None:
        main = _main()
        main["commit"] = {"sha": "b" * 40}
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_active_one_shot_historical_executor_workflow_install_authorization_preflight(
                repository_root=Path("."),
                main_branch=main,
                workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_existing_historical_run_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unused historical slot"):
            build_active_one_shot_historical_executor_workflow_install_authorization_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                workflow_runs=_runs(_historical()),
                expected_head_sha=HEAD,
            )

    def test_validator_rejects_install_authority_escalation(self) -> None:
        plan = (
            build_active_one_shot_historical_executor_workflow_install_authorization_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )
        )
        plan["historical_executor_workflow_install_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_install_authorized mismatch",
        ):
            validate_active_one_shot_historical_executor_workflow_install_authorization_preflight(
                plan
            )

    def test_cli_has_plan_only_no_install_or_execute_surface(self) -> None:
        text = Path(
            "scripts/"
            "phase8a_exp062_active_one_shot_historical_executor_"
            "workflow_install_authorization_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("plan")', text)
        self.assertNotIn('sub.add_parser("install")', text)
        self.assertNotIn('sub.add_parser("execute")', text)
        self.assertNotIn('sub.add_parser("advance")', text)
        self.assertNotIn("gh workflow run ", text)


if __name__ == "__main__":
    unittest.main()
