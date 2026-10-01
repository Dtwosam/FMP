from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp065_historical_dispatch_operator import (
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    build_historical_dispatch_plan,
    historical_dispatch_command,
    validate_historical_dispatch_operator_sources,
    validate_historical_dispatch_plan,
)
from fmp.discovery.exp065_historical_execution_authorization import (
    HISTORICAL_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_AUTHORIZED,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    historical_execution_authorization_payload,
    require_historical_execution_authorized,
    validate_historical_execution_authorization_sources,
)


CODE_COMMIT = "a" * 40


def _env(**overrides: str) -> dict[str, str]:
    value = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": "Dtwosam/FMP",
        "GITHUB_WORKFLOW": "phase8a-exp065-pairwise-interaction",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_RUN_NUMBER": "1",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_RUN_ID": "123456789",
        "GITHUB_SHA": CODE_COMMIT,
    }
    value.update(overrides)
    return value


def _run(
    *,
    run_id: int = 123456789,
    status: str = "queued",
    conclusion: str | None = None,
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": "phase8a-exp065-pairwise-interaction",
        "path": ".github/workflows/phase8a-exp065-pairwise-interaction.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": CODE_COMMIT,
        "run_number": 1,
        "run_attempt": 1,
        "status": status,
        "conclusion": conclusion,
    }


class Exp065HistoricalRuntimeActivationTests(unittest.TestCase):
    def test_authorization_sources_bind_exact_activated_runtime(self) -> None:
        report = validate_historical_execution_authorization_sources(
            repository_root=Path("."),
        )

        self.assertEqual(
            report["dec465_run_authorization_blob_sha"],
            "96aac63a75d7873e6b6508d34b983d0742858a02",
        )
        self.assertEqual(
            report["runtime_source_blob_sha"],
            "717b43e3bfd656b51e22819cf948f8cd6485f334",
        )
        self.assertEqual(
            report["active_workflow_blob_sha"],
            "75d0e4df56d5c4ced5aff614e236cf0e1bb078e1",
        )
        self.assertEqual(
            report["dormant_workflow_template_blob_sha"],
            "75d0e4df56d5c4ced5aff614e236cf0e1bb078e1",
        )
        self.assertEqual(
            report["activated_cli_blob_sha"],
            "4448d1bf43ce1ddb9dba9c4d38bb18829b95ae38",
        )
        self.assertEqual(
            report["dec465_merge_sha"],
            "c44d787eff659838f904955ccf95dc69a43a852d",
        )
        self.assertEqual(
            report["evidence_contract_blob_sha"],
            "ca68622ddfc9866f00569d558b2ab927be23686d",
        )
        self.assertEqual(
            report["pairwise_interaction_miner_blob_sha"],
            "7dac382838d2b8fcc4df5d02c4949ad65c17635b",
        )
        self.assertEqual(
            report["pairwise_interaction_protocol_blob_sha"],
            "b54267d790667659749a96123ad23a491ff50dfa",
        )
        self.assertEqual(
            report["repaired_adapter_blob_sha"],
            "491ba8c92cb6e6e4c715bfb1ecb934b6949e1596",
        )
        self.assertEqual(
            report["range_limited_loader_blob_sha"],
            "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea",
        )
        self.assertEqual(
            report["runtime_requirements_blob_sha"],
            "1ff32214dee10d877a067e750cd69ffad96d5fe5",
        )
        self.assertTrue(report["historical_result_dispatch_authorized"])
        self.assertTrue(report["historical_execution_authorized"])
        self.assertTrue(report["historical_result_authorized"])
        self.assertFalse(report["rerun_authorized"])
        self.assertFalse(report["retry_authorized"])
        self.assertFalse(report["replacement_run_authorized"])
        self.assertFalse(report["reserved_robustness_access_authorized"])
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["phase8b_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_dispatch_operator_binds_exact_activation_sources(self) -> None:
        report = validate_historical_dispatch_operator_sources(
            repository_root=Path("."),
        )

        self.assertEqual(
            report["dec466_execution_authorization"],
            "ccc99179a51145534e1b48b8520b2f743580c217",
        )
        self.assertEqual(
            report["dec465_run_authorization"],
            "96aac63a75d7873e6b6508d34b983d0742858a02",
        )

    def test_exact_run_one_attempt_one_runtime_identity_is_authorized(self) -> None:
        report = require_historical_execution_authorized(
            code_commit=CODE_COMMIT,
            environment=_env(),
            repository_root=Path("."),
        )

        self.assertEqual(
            report["stage"],
            "EXP065_ONE_SHOT_HISTORICAL_EXECUTION_RUNTIME_AUTHORIZED",
        )
        self.assertEqual(report["runtime_workflow_run_id"], 123456789)
        self.assertEqual(report["runtime_workflow_run_number"], 1)
        self.assertEqual(report["runtime_workflow_run_attempt"], 1)
        self.assertTrue(report["runtime_identity_verified"])

    def test_second_run_rerun_and_non_actions_context_fail_closed(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "GITHUB_RUN_NUMBER='1'",
        ):
            require_historical_execution_authorized(
                code_commit=CODE_COMMIT,
                environment=_env(GITHUB_RUN_NUMBER="2"),
                repository_root=Path("."),
            )

        with self.assertRaisesRegex(
            PermissionError,
            "GITHUB_RUN_ATTEMPT='1'",
        ):
            require_historical_execution_authorized(
                code_commit=CODE_COMMIT,
                environment=_env(GITHUB_RUN_ATTEMPT="2"),
                repository_root=Path("."),
            )

        with self.assertRaisesRegex(
            PermissionError,
            "GITHUB_ACTIONS='true'",
        ):
            require_historical_execution_authorized(
                code_commit=CODE_COMMIT,
                environment=_env(GITHUB_ACTIONS="false"),
                repository_root=Path("."),
            )

    def test_wrong_commit_repo_workflow_or_ref_fails_closed(self) -> None:
        for field, replacement in (
            ("GITHUB_SHA", "b" * 40),
            ("GITHUB_REPOSITORY", "other/repo"),
            ("GITHUB_WORKFLOW", "other-workflow"),
            ("GITHUB_REF", "refs/heads/other"),
        ):
            with self.subTest(field=field):
                with self.assertRaises(PermissionError):
                    require_historical_execution_authorized(
                        code_commit=CODE_COMMIT,
                        environment=_env(**{field: replacement}),
                        repository_root=Path("."),
                    )

    def test_authorization_payload_opens_only_historical_run_surface(self) -> None:
        payload = historical_execution_authorization_payload(
            code_commit=CODE_COMMIT,
        )

        self.assertTrue(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertTrue(HISTORICAL_EXECUTION_AUTHORIZED)
        self.assertTrue(HISTORICAL_RESULT_AUTHORIZED)
        self.assertTrue(payload["historical_result_dispatch_authorized"])
        self.assertTrue(payload["historical_execution_authorized"])
        self.assertTrue(payload["historical_result_authorized"])
        for field in (
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
            self.assertFalse(payload[field], field)

    def test_read_only_dispatch_plan_requires_exact_main_and_empty_slot(self) -> None:
        plan = build_historical_dispatch_plan(
            repository_root=Path("."),
            main_branch={"name": "main", "commit": {"sha": CODE_COMMIT}},
            workflow_runs={"workflow_runs": []},
            expected_head_sha=CODE_COMMIT,
        )
        validate_historical_dispatch_plan(plan)

        self.assertEqual(plan["stage"], "EXP065_ONE_SHOT_DISPATCH_READY")
        self.assertEqual(
            plan["planned_dispatch_command"],
            "gh workflow run phase8a-exp065-pairwise-interaction.yml --ref main",
        )
        self.assertEqual(
            historical_dispatch_command(),
            (
                "gh",
                "workflow",
                "run",
                "phase8a-exp065-pairwise-interaction.yml",
                "--ref",
                "main",
            ),
        )
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)

    def test_present_run_removes_dispatch_command_permanently(self) -> None:
        plan = build_historical_dispatch_plan(
            repository_root=Path("."),
            main_branch={"name": "main", "commit": {"sha": CODE_COMMIT}},
            workflow_runs={"workflow_runs": [_run()]},
            expected_head_sha=CODE_COMMIT,
        )
        validate_historical_dispatch_plan(plan)

        self.assertEqual(
            plan["stage"],
            "EXP065_ONE_SHOT_SLOT_CONSUMED_REVIEW_REQUIRED",
        )
        self.assertTrue(plan["historical_result_slot_consumed"])
        self.assertIsNone(plan["planned_dispatch_command"])
        self.assertFalse(plan["rerun_authorized"])
        self.assertFalse(plan["retry_authorized"])
        self.assertFalse(plan["replacement_run_authorized"])

    def test_dispatch_plan_rejects_main_head_drift(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_historical_dispatch_plan(
                repository_root=Path("."),
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                workflow_runs={"workflow_runs": []},
                expected_head_sha=CODE_COMMIT,
            )

    def test_cli_uses_dec466_gate_before_historical_reads(self) -> None:
        script = Path("scripts/phase8a_exp065.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "exp065_historical_execution_authorization import",
            script,
        )
        self.assertNotIn(
            "from fmp.discovery.exp065_runtime_source import (\n"
            "    require_historical_execution_authorized",
            script,
        )

        cell_start = script.index("def _cmd_cell")
        cell_gate = script.index(
            "require_historical_execution_authorized",
            cell_start,
        )
        cell_loader = script.index(
            "load_verified_exp061_cell_from_indexes",
            cell_start,
        )
        self.assertLess(cell_gate, cell_loader)

        aggregate_start = script.index("def _cmd_aggregate")
        aggregate_gate = script.index(
            "require_historical_execution_authorized",
            aggregate_start,
        )
        aggregate_read = script.index(
            "_load_cell_evidence",
            aggregate_start,
        )
        self.assertLess(aggregate_gate, aggregate_read)


if __name__ == "__main__":
    unittest.main()
