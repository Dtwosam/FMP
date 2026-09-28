from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_preflight import (
    build_active_one_shot_historical_executor_workflow_install_preflight,
    validate_active_one_shot_historical_executor_workflow_install_preflight,
    validate_active_one_shot_historical_executor_workflow_install_preflight_sources,
)
from fmp.discovery.exp062_runtime_proof_freeze import (
    PROOF_HEAD_SHA,
    PROOF_RUN_ID,
)


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


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallPreflightTests(
    unittest.TestCase
):
    def test_source_bindings_pin_dec360_and_dormant_template(self) -> None:
        source = (
            validate_active_one_shot_historical_executor_workflow_install_preflight_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec360_active_install_contract"],
            "63d645115dec87a4ec2bbec8448a26ea7cdded34",
        )
        self.assertEqual(
            source["dormant_executor_workflow_template"],
            "51ce87584369be957482460d81649adb1cb9f05d",
        )

    def test_empty_slot_and_absent_active_workflow_are_ready(self) -> None:
        plan = (
            build_active_one_shot_historical_executor_workflow_install_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )
        )
        self.assertIs(
            validate_active_one_shot_historical_executor_workflow_install_preflight(
                plan
            ),
            plan,
        )
        self.assertEqual(plan["decision"], "DEC-361")
        self.assertEqual(
            plan["stage"],
            (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "PREFLIGHT_ACTIVE_WORKFLOW_ABSENT_SLOT_AVAILABLE"
            ),
        )
        self.assertTrue(plan["dormant_executor_workflow_template_present"])
        self.assertFalse(plan["executor_workflow_path_exists"])
        self.assertEqual(plan["historical_result_attempt_count"], 0)
        self.assertFalse(plan["historical_result_slot_consumed"])
        self.assertTrue(plan["historical_result_slot_verified_available"])
        self.assertEqual(plan["expected_target_run_number"], 2)
        self.assertEqual(plan["expected_target_run_attempt"], 1)
        self.assertTrue(
            plan[
                "active_one_shot_historical_executor_workflow_install_source_authorized"
            ]
        )
        self.assertFalse(
            plan["historical_executor_workflow_install_authorized"]
        )
        self.assertFalse(plan["historical_executor_workflow_installed"])
        self.assertFalse(plan["historical_executor_available"])
        self.assertFalse(plan["historical_result_dispatch_authorized"])
        self.assertFalse(plan["historical_execute_mode_available"])

    def test_main_head_drift_is_rejected(self) -> None:
        main = _main()
        main["commit"] = {"sha": "b" * 40}
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_active_one_shot_historical_executor_workflow_install_preflight(
                repository_root=Path("."),
                main_branch=main,
                workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_existing_historical_run_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unused historical slot"):
            build_active_one_shot_historical_executor_workflow_install_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                workflow_runs=_runs(_historical()),
                expected_head_sha=HEAD,
            )

    def test_validator_rejects_install_authority_escalation(self) -> None:
        plan = (
            build_active_one_shot_historical_executor_workflow_install_preflight(
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
            validate_active_one_shot_historical_executor_workflow_install_preflight(
                plan
            )

    def test_validator_rejects_dispatch_authority_escalation(self) -> None:
        plan = (
            build_active_one_shot_historical_executor_workflow_install_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )
        )
        plan["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized mismatch",
        ):
            validate_active_one_shot_historical_executor_workflow_install_preflight(
                plan
            )

    def test_cli_has_plan_only_no_install_or_execute_surface(self) -> None:
        text = Path(
            "scripts/"
            "phase8a_exp062_active_one_shot_historical_executor_"
            "workflow_install_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("plan")', text)
        self.assertNotIn('sub.add_parser("install")', text)
        self.assertNotIn('sub.add_parser("execute")', text)
        self.assertNotIn('sub.add_parser("advance")', text)
        self.assertNotIn("gh workflow run ", text)


if __name__ == "__main__":
    unittest.main()
