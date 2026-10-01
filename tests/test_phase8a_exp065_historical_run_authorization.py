from __future__ import annotations

import unittest

from fmp.discovery.exp065_historical_run_authorization import (
    DEC464_ACTIVE_WORKFLOW_BLOB_SHA,
    DEC464_CLI_BLOB_SHA,
    DEC464_DORMANT_TEMPLATE_BLOB_SHA,
    DEC464_MERGE_SHA,
    DEC464_RUNTIME_SOURCE_BLOB_SHA,
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
        "name": "phase8a-exp065-pairwise-interaction",
        "path": ".github/workflows/phase8a-exp065-pairwise-interaction.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "run_number": run_number,
        "run_attempt": run_attempt,
        "status": status,
        "conclusion": conclusion,
    }


class Exp065HistoricalRunAuthorizationTests(unittest.TestCase):
    def test_source_contract_keeps_exact_pre_activation_identity(self) -> None:
        self.assertEqual(
            DEC464_MERGE_SHA,
            "698e3e21d7dd0cbe83c3ed7d15f5544cf9c096e9",
        )
        self.assertEqual(
            DEC464_RUNTIME_SOURCE_BLOB_SHA,
            "717b43e3bfd656b51e22819cf948f8cd6485f334",
        )
        self.assertEqual(
            DEC464_ACTIVE_WORKFLOW_BLOB_SHA,
            "75d0e4df56d5c4ced5aff614e236cf0e1bb078e1",
        )
        self.assertEqual(
            DEC464_DORMANT_TEMPLATE_BLOB_SHA,
            "75d0e4df56d5c4ced5aff614e236cf0e1bb078e1",
        )
        self.assertEqual(
            DEC464_CLI_BLOB_SHA,
            "38e3eb9a5c2733655c845291d6bc3160e5fa0291",
        )
        self.assertTrue(HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTION_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_AUTHORIZED)

    def test_zero_manual_runs_means_one_shot_slot_available(self) -> None:
        report = classify_historical_run_inventory({"workflow_runs": []})

        self.assertEqual(
            report["stage"],
            "EXP065_HISTORICAL_RESULT_SLOT_AVAILABLE",
        )
        self.assertEqual(report["historical_result_attempt_count"], 0)
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_source_authorized"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_execution_authorized"])
        self.assertFalse(report["historical_result_authorized"])

    def test_first_queued_or_running_run_consumes_slot_immediately(self) -> None:
        for status in ("queued", "in_progress"):
            with self.subTest(status=status):
                report = classify_historical_run_inventory(
                    {"workflow_runs": [_run(status=status)]}
                )
                self.assertEqual(
                    report["stage"],
                    "EXP065_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED",
                )
                self.assertEqual(report["historical_result_attempt_count"], 1)
                self.assertTrue(report["historical_result_slot_consumed"])
                self.assertEqual(report["historical_result_run_status"], status)
                self.assertIsNone(report["historical_result_run_conclusion"])
                self.assertFalse(report["rerun_authorized"])
                self.assertFalse(report["retry_authorized"])
                self.assertFalse(report["replacement_run_authorized"])

    def test_terminal_success_or_failure_still_consumes_slot(self) -> None:
        for conclusion in ("success", "failure", "cancelled"):
            with self.subTest(conclusion=conclusion):
                report = classify_historical_run_inventory(
                    {
                        "workflow_runs": [
                            _run(status="completed", conclusion=conclusion)
                        ]
                    }
                )
                self.assertTrue(report["historical_result_slot_consumed"])
                self.assertEqual(
                    report["historical_result_run_conclusion"],
                    conclusion,
                )
                self.assertFalse(report["rerun_authorized"])
                self.assertFalse(report["retry_authorized"])
                self.assertFalse(report["replacement_run_authorized"])

    def test_second_attempt_rerun_or_second_run_fails_closed(self) -> None:
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
        unrelated["name"] = "phase8a-exp064-continuous-stability"
        unrelated["path"] = (
            ".github/workflows/phase8a-exp064-continuous-stability.yml"
        )
        report = classify_historical_run_inventory(
            {"workflow_runs": [unrelated]}
        )
        self.assertFalse(report["historical_result_slot_consumed"])

    def test_dec465_remains_source_only_after_successor_activation(self) -> None:
        self.assertTrue(HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTION_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_AUTHORIZED)

        report = classify_historical_run_inventory({"workflow_runs": []})
        self.assertEqual(
            report["stage"],
            "EXP065_HISTORICAL_RESULT_SLOT_AVAILABLE",
        )
        self.assertFalse(report["historical_result_slot_consumed"])


if __name__ == "__main__":
    unittest.main()
