from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.historical_execution_authorization import (
    DISCOVERY_RESULT_AUTHORIZED,
    EXPECTED_WORKFLOW_RUN_ATTEMPT,
    EXPECTED_WORKFLOW_RUN_NUMBER,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
    HISTORICAL_EXECUTION_SOURCE_AUTHORIZED,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    historical_execution_authorization_payload,
    require_historical_execution_authorized,
    validate_historical_execution_authorization_sources,
)


HEAD = "a" * 40


def _environment(**overrides: str) -> dict[str, str]:
    value = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": "Dtwosam/FMP",
        "GITHUB_WORKFLOW": "phase8a-exp061-discovery",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_RUN_NUMBER": "2",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_RUN_ID": "40000000000",
        "GITHUB_SHA": HEAD,
    }
    value.update(overrides)
    return value


class Exp061HistoricalExecutionAuthorizationTests(unittest.TestCase):
    def test_source_transition_binds_reviewed_proof_and_opens_only_runtime(self) -> None:
        report = validate_historical_execution_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(report["decision"], "DEC-285")
        self.assertTrue(HISTORICAL_EXECUTION_SOURCE_AUTHORIZED)
        self.assertTrue(report["historical_execution_source_authorized"])
        self.assertFalse(report["legacy_workflow_source_execution_authorized"])
        self.assertTrue(HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED)
        self.assertTrue(DISCOVERY_RESULT_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertEqual(
            report["expected_workflow_run_number"],
            EXPECTED_WORKFLOW_RUN_NUMBER,
        )
        self.assertEqual(
            report["expected_workflow_run_attempt"],
            EXPECTED_WORKFLOW_RUN_ATTEMPT,
        )
        self.assertEqual(
            report["historical_data_end_exclusive"],
            "2023-01-01T00:00:00Z",
        )
        for field in (
            "historical_result_dispatch_authorized",
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
            self.assertFalse(report[field], field)

    def test_runtime_accepts_only_workflow_run_two_attempt_one(self) -> None:
        report = require_historical_execution_authorized(
            code_commit=HEAD,
            environment=_environment(),
        )
        self.assertEqual(
            report["stage"],
            "EXP061_HISTORICAL_EXECUTION_RUNTIME_AUTHORIZED",
        )
        self.assertTrue(report["runtime_identity_verified"])
        self.assertEqual(report["runtime_workflow_run_number"], 2)
        self.assertEqual(report["runtime_workflow_run_attempt"], 1)
        self.assertTrue(report["historical_discovery_execution_authorized"])
        self.assertTrue(report["discovery_result_authorized"])
        self.assertFalse(report["historical_result_dispatch_authorized"])

    def test_run_number_one_or_three_is_rejected(self) -> None:
        for run_number in ("1", "3"):
            with self.subTest(run_number=run_number):
                with self.assertRaisesRegex(
                    PermissionError,
                    "GITHUB_RUN_NUMBER='2'",
                ):
                    require_historical_execution_authorized(
                        code_commit=HEAD,
                        environment=_environment(
                            GITHUB_RUN_NUMBER=run_number,
                        ),
                    )

    def test_rerun_attempt_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "GITHUB_RUN_ATTEMPT='1'",
        ):
            require_historical_execution_authorized(
                code_commit=HEAD,
                environment=_environment(GITHUB_RUN_ATTEMPT="2"),
            )

    def test_wrong_repo_event_ref_or_workflow_is_rejected(self) -> None:
        cases = {
            "GITHUB_REPOSITORY": "someone/FMP",
            "GITHUB_WORKFLOW": "other-workflow",
            "GITHUB_EVENT_NAME": "push",
            "GITHUB_REF": "refs/heads/dev",
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                with self.assertRaisesRegex(PermissionError, field):
                    require_historical_execution_authorized(
                        code_commit=HEAD,
                        environment=_environment(**{field: value}),
                    )

    def test_code_commit_must_equal_runtime_sha(self) -> None:
        with self.assertRaisesRegex(PermissionError, "GITHUB_SHA"):
            require_historical_execution_authorized(
                code_commit=HEAD,
                environment=_environment(GITHUB_SHA="b" * 40),
            )

    def test_gate_proof_run_id_and_head_cannot_be_reused(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "distinct positive historical-result run id",
        ):
            require_historical_execution_authorized(
                code_commit=HEAD,
                environment=_environment(GITHUB_RUN_ID="36319888985"),
            )

        proof_head = "041b7b2f5aac8821156fab346df8ab30f4be2a7b"
        with self.assertRaisesRegex(
            PermissionError,
            "cannot reuse the gate-proof head",
        ):
            require_historical_execution_authorized(
                code_commit=proof_head,
                environment=_environment(GITHUB_SHA=proof_head),
            )

    def test_payload_keeps_dispatch_and_all_downstream_paths_locked(self) -> None:
        report = historical_execution_authorization_payload(
            code_commit=HEAD,
        )
        self.assertTrue(report["historical_execution_source_authorized"])
        self.assertTrue(report["historical_discovery_execution_authorized"])
        self.assertTrue(report["discovery_result_authorized"])
        for field in (
            "historical_result_dispatch_authorized",
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
            self.assertFalse(report[field], field)

    def test_public_cli_uses_dec285_gate_before_historical_reads(self) -> None:
        script = Path("scripts/phase8a_exp061.py").read_text(encoding="utf-8")
        self.assertIn(
            "from fmp.discovery.historical_execution_authorization import (",
            script,
        )
        self.assertIn(
            "historical_execution_authorization_payload",
            script,
        )

        cell_start = script.index("def _cmd_cell")
        aggregate_start = script.index("def _cmd_aggregate")
        cell_gate = script.index(
            "require_historical_execution_authorized",
            cell_start,
        )
        cell_loader = script.index(
            "load_verified_exp061_cell_from_indexes",
            cell_start,
        )
        aggregate_gate = script.index(
            "require_historical_execution_authorized",
            aggregate_start,
        )
        aggregate_read = script.index(
            "_load_cell_evidence",
            aggregate_start,
        )
        self.assertLess(cell_gate, cell_loader)
        self.assertLess(aggregate_gate, aggregate_read)
        self.assertIn(
            'value["execution_authorization"]',
            script,
        )


if __name__ == "__main__":
    unittest.main()
