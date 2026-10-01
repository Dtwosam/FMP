from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp064_historical_run_authorization import (
    DEC455_MERGE_SHA,
    HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED,
    build_historical_run_authorization_contract,
    classify_historical_run_inventory,
    validate_historical_run_authorization_sources,
)


def _run(
    *,
    run_id: int = 1,
    head_sha: str = "b" * 40,
    status: str = "queued",
    conclusion: str | None = None,
    run_number: int = 1,
    run_attempt: int = 1,
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": "phase8a-exp064-continuous-stability",
        "path": ".github/workflows/phase8a-exp064-continuous-stability.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "run_number": run_number,
        "run_attempt": run_attempt,
        "status": status,
        "conclusion": conclusion,
    }


class Exp064HistoricalRunAuthorizationTests(unittest.TestCase):
    def test_source_contract_binds_exact_merged_runtime(self) -> None:
        report = validate_historical_run_authorization_sources(
            repository_root=Path("."),
        )

        self.assertEqual(
            DEC455_MERGE_SHA,
            "c388def44d251c96832572f07de43d9dc6a909ee",
        )
        self.assertEqual(
            report["runtime_source_blob_sha"],
            "07e5ccebb6416c04621aa54e170cd4eb1e0a2a04",
        )
        self.assertEqual(
            report["active_workflow_blob_sha"],
            "caca62672ad9796764c18be6b8da9785b98c9733",
        )
        self.assertEqual(
            report["cli_blob_sha"],
            "a44aed6d890e25a781b7b92d7efb3dabe06f9047",
        )
        self.assertEqual(
            report["evidence_contract_blob_sha"],
            "9aee3f9e273e20329c9de5a7079ed924ffee0a9a",
        )
        self.assertEqual(
            report["continuous_stability_miner_blob_sha"],
            "b0d799ec1afaf43b0441290c97a9f39c37ecd2fd",
        )
        self.assertEqual(
            report["continuous_stability_protocol_blob_sha"],
            "c108ea047c7bfb3e588bfbac33993180066c28ad",
        )
        self.assertEqual(report["historical_data_start"], "2015-01-01T00:00:00Z")
        self.assertEqual(
            report["historical_data_end_exclusive"],
            "2023-01-01T00:00:00Z",
        )
        self.assertEqual(
            report["reserved_robustness_start"],
            "2023-01-01T00:00:00Z",
        )
        self.assertEqual(
            report["reserved_robustness_end_exclusive"],
            "2026-08-21T00:00:00Z",
        )
        self.assertEqual(report["expected_first_run_number"], 1)
        self.assertEqual(report["expected_run_attempt"], 1)
        self.assertTrue(report["historical_result_slot_source_authorized"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_execution_authorized"])
        self.assertFalse(report["historical_result_authorized"])
        self.assertFalse(report["reserved_robustness_access_authorized"])
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["phase8b_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_zero_manual_runs_means_one_shot_slot_available(self) -> None:
        report = classify_historical_run_inventory({"workflow_runs": []})

        self.assertEqual(
            report["stage"],
            "EXP064_HISTORICAL_RESULT_SLOT_AVAILABLE",
        )
        self.assertEqual(report["historical_result_attempt_count"], 0)
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_source_authorized"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_execution_authorized"])

    def test_first_queued_run_consumes_slot_immediately(self) -> None:
        report = classify_historical_run_inventory(
            {"workflow_runs": [_run(status="queued")]}
        )

        self.assertEqual(
            report["stage"],
            "EXP064_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED",
        )
        self.assertEqual(report["historical_result_attempt_count"], 1)
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertEqual(report["historical_result_run_status"], "queued")
        self.assertIsNone(report["historical_result_run_conclusion"])
        self.assertFalse(report["rerun_authorized"])
        self.assertFalse(report["retry_authorized"])
        self.assertFalse(report["replacement_run_authorized"])

    def test_terminal_failure_still_consumes_slot(self) -> None:
        report = classify_historical_run_inventory(
            {
                "workflow_runs": [
                    _run(status="completed", conclusion="failure")
                ]
            }
        )

        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertEqual(report["historical_result_run_conclusion"], "failure")
        self.assertFalse(report["rerun_authorized"])
        self.assertFalse(report["retry_authorized"])
        self.assertFalse(report["replacement_run_authorized"])

    def test_second_attempt_or_rerun_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "multiple attempts"):
            classify_historical_run_inventory(
                {"workflow_runs": [_run(run_id=1), _run(run_id=2)]}
            )

        with self.assertRaisesRegex(ValueError, "run attempt must remain 1"):
            classify_historical_run_inventory(
                {"workflow_runs": [_run(run_attempt=2)]}
            )

        with self.assertRaisesRegex(ValueError, "run number must remain 1"):
            classify_historical_run_inventory(
                {"workflow_runs": [_run(run_number=2)]}
            )

    def test_unrelated_workflows_do_not_consume_slot(self) -> None:
        unrelated = _run()
        unrelated["name"] = "phase8a-exp062-discovery"
        unrelated["path"] = ".github/workflows/phase8a-exp062-discovery.yml"

        report = classify_historical_run_inventory(
            {"workflow_runs": [unrelated]}
        )
        self.assertFalse(report["historical_result_slot_consumed"])

    def test_contract_opens_source_slot_only_and_no_execute_path(self) -> None:
        report = build_historical_run_authorization_contract(
            repository_root=Path("."),
            workflow_runs_payload={"workflow_runs": []},
        )

        self.assertTrue(HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED)
        self.assertEqual(
            report["stage"],
            "EXP064_ONE_SHOT_SLOT_SOURCE_AUTHORIZED_DISPATCH_LOCKED",
        )
        self.assertTrue(report["first_manual_main_run_consumes_slot"])
        self.assertTrue(report["queued_or_running_run_consumes_slot"])
        self.assertTrue(report["terminal_outcome_consumes_slot"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_execution_authorized"])
        self.assertFalse(report["historical_result_authorized"])
        self.assertFalse(report["reserved_robustness_access_authorized"])
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["trading_authorized"])


if __name__ == "__main__":
    unittest.main()
