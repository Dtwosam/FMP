from __future__ import annotations

import unittest

from fmp.discovery.exp063_historical_run_authorization import (
    DEC447_ACTIVE_WORKFLOW_BLOB_SHA,
    DEC447_CLI_BLOB_SHA,
    DEC447_MERGE_SHA,
    DEC447_RUNTIME_SOURCE_BLOB_SHA,
    HISTORICAL_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_AUTHORIZED,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED,
    classify_historical_run_inventory,
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
        "name": "phase8a-exp063-persistence",
        "path": ".github/workflows/phase8a-exp063-persistence.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "run_number": run_number,
        "run_attempt": run_attempt,
        "status": status,
        "conclusion": conclusion,
    }


class Exp063HistoricalRunAuthorizationTests(unittest.TestCase):
    def test_source_contract_keeps_exact_pre_activation_identity(self) -> None:
        self.assertEqual(
            DEC447_MERGE_SHA,
            "cbd7f5adce4cae062ba427bf61c3239e77dc5b72",
        )
        self.assertEqual(
            DEC447_RUNTIME_SOURCE_BLOB_SHA,
            "6e7804a037fd386016fd45145be73b8dc00563f2",
        )
        self.assertEqual(
            DEC447_ACTIVE_WORKFLOW_BLOB_SHA,
            "1038beb4b704ddead4e5841a6f799858732189e6",
        )
        self.assertEqual(
            DEC447_CLI_BLOB_SHA,
            "1b969668f79b37bc68f701da103b3a2bb53b13c1",
        )
        self.assertTrue(HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTION_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_AUTHORIZED)

    def test_zero_manual_runs_means_one_shot_slot_available(self) -> None:
        report = classify_historical_run_inventory({"workflow_runs": []})

        self.assertEqual(
            report["stage"],
            "EXP063_HISTORICAL_RESULT_SLOT_AVAILABLE",
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
            "EXP063_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED",
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

    def test_dec448_remains_source_only_after_successor_activation(self) -> None:
        self.assertTrue(HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTION_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_AUTHORIZED)

        report = classify_historical_run_inventory({"workflow_runs": []})
        self.assertEqual(
            report["stage"],
            "EXP063_HISTORICAL_RESULT_SLOT_AVAILABLE",
        )
        self.assertFalse(report["historical_result_slot_consumed"])



if __name__ == "__main__":
    unittest.main()
