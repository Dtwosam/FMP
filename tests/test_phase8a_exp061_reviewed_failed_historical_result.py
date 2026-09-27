from __future__ import annotations

import copy
import unittest

from fmp.discovery.historical_failed_result_decision import (
    ERROR_VOL_1H,
    ERROR_VOL_8H,
    EXECUTOR_ARTIFACT_DIGEST,
    EXECUTOR_ARTIFACT_ID,
    EXECUTOR_ARTIFACT_NAME,
    EXECUTOR_FILE_SHA256,
    EXECUTOR_ZIP_SHA256,
    EXPECTED_CELL_ERRORS,
    EXPECTED_JOBS,
    EXP061_FAILED_RESULT_DECISION,
    HISTORICAL_HEAD_SHA,
    HISTORICAL_RUN_ID,
    PREFLIGHT_ARTIFACT_DIGEST,
    PREFLIGHT_ARTIFACT_ID,
    PREFLIGHT_ARTIFACT_NAME,
    PREFLIGHT_JSON_SHA256,
    PREFLIGHT_ZIP_SHA256,
    ROOT_CAUSE,
    freeze_failed_historical_result,
)


def _run() -> dict[str, object]:
    return {
        "id": HISTORICAL_RUN_ID,
        "name": "phase8a-exp061-discovery",
        "path": ".github/workflows/phase8a-exp061-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HISTORICAL_HEAD_SHA,
        "run_number": 2,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": job_id,
                "name": name,
                "status": "completed",
                "conclusion": conclusion,
            }
            for name, (job_id, conclusion) in EXPECTED_JOBS.items()
        ]
    }


def _historical_artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": PREFLIGHT_ARTIFACT_ID,
                "name": PREFLIGHT_ARTIFACT_NAME,
                "digest": PREFLIGHT_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


def _executor_artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": EXECUTOR_ARTIFACT_ID,
                "name": EXECUTOR_ARTIFACT_NAME,
                "digest": EXECUTOR_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


def _freeze() -> dict[str, object]:
    return freeze_failed_historical_result(
        run=_run(),
        jobs_payload=_jobs(),
        historical_artifacts_payload=_historical_artifacts(),
        executor_artifacts_payload=_executor_artifacts(),
        cell_failure_messages=EXPECTED_CELL_ERRORS,
        executor_zip_sha256=EXECUTOR_ZIP_SHA256,
        executor_file_sha256=EXECUTOR_FILE_SHA256,
        preflight_zip_sha256=PREFLIGHT_ZIP_SHA256,
        preflight_json_sha256=PREFLIGHT_JSON_SHA256,
    )


class Exp061ReviewedFailedHistoricalResultTests(unittest.TestCase):
    def test_exact_failed_result_is_frozen_and_closed(self) -> None:
        report = _freeze()
        self.assertEqual(report["decision"], EXP061_FAILED_RESULT_DECISION)
        self.assertEqual(
            report["stage"],
            "EXP061_HISTORICAL_RESULT_FAILED_REVIEWED_AND_CLOSED",
        )
        self.assertEqual(report["historical_run_id"], HISTORICAL_RUN_ID)
        self.assertEqual(report["failed_cell_job_count"], 18)
        self.assertEqual(report["cell_artifact_count"], 0)
        self.assertEqual(report["aggregate_artifact_count"], 0)
        self.assertEqual(report["root_cause"], ROOT_CAUSE)
        self.assertEqual(report["realized_vol_1h_failure_count"], 8)
        self.assertEqual(report["realized_vol_8h_failure_count"], 10)
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertTrue(report["exp061_closed"])
        self.assertTrue(report["new_experiment_identity_required_for_repair"])
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
            self.assertFalse(report[field], field)

    def test_failure_split_is_exact(self) -> None:
        self.assertEqual(
            sum(value == ERROR_VOL_1H for value in EXPECTED_CELL_ERRORS.values()),
            8,
        )
        self.assertEqual(
            sum(value == ERROR_VOL_8H for value in EXPECTED_CELL_ERRORS.values()),
            10,
        )
        self.assertEqual(len(EXPECTED_CELL_ERRORS), 18)

    def test_job_identity_tamper_is_rejected(self) -> None:
        jobs = _jobs()
        rows = jobs["jobs"]
        assert isinstance(rows, list)
        rows[1]["id"] = int(rows[1]["id"]) + 1
        with self.assertRaisesRegex(ValueError, "job id mismatch"):
            freeze_failed_historical_result(
                run=_run(),
                jobs_payload=jobs,
                historical_artifacts_payload=_historical_artifacts(),
                executor_artifacts_payload=_executor_artifacts(),
                cell_failure_messages=EXPECTED_CELL_ERRORS,
                executor_zip_sha256=EXECUTOR_ZIP_SHA256,
                executor_file_sha256=EXECUTOR_FILE_SHA256,
                preflight_zip_sha256=PREFLIGHT_ZIP_SHA256,
                preflight_json_sha256=PREFLIGHT_JSON_SHA256,
            )

    def test_failure_message_tamper_is_rejected(self) -> None:
        messages = dict(EXPECTED_CELL_ERRORS)
        key = next(iter(messages))
        messages[key] = "different failure"
        with self.assertRaisesRegex(ValueError, "cell failure messages mismatch"):
            freeze_failed_historical_result(
                run=_run(),
                jobs_payload=_jobs(),
                historical_artifacts_payload=_historical_artifacts(),
                executor_artifacts_payload=_executor_artifacts(),
                cell_failure_messages=messages,
                executor_zip_sha256=EXECUTOR_ZIP_SHA256,
                executor_file_sha256=EXECUTOR_FILE_SHA256,
                preflight_zip_sha256=PREFLIGHT_ZIP_SHA256,
                preflight_json_sha256=PREFLIGHT_JSON_SHA256,
            )

    def test_preflight_artifact_tamper_is_rejected(self) -> None:
        artifacts = _historical_artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows[0]["digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(ValueError, "artifact digest mismatch"):
            freeze_failed_historical_result(
                run=_run(),
                jobs_payload=_jobs(),
                historical_artifacts_payload=artifacts,
                executor_artifacts_payload=_executor_artifacts(),
                cell_failure_messages=EXPECTED_CELL_ERRORS,
                executor_zip_sha256=EXECUTOR_ZIP_SHA256,
                executor_file_sha256=EXECUTOR_FILE_SHA256,
                preflight_zip_sha256=PREFLIGHT_ZIP_SHA256,
                preflight_json_sha256=PREFLIGHT_JSON_SHA256,
            )

    def test_executor_file_hash_tamper_is_rejected(self) -> None:
        hashes = copy.deepcopy(EXECUTOR_FILE_SHA256)
        hashes["executor.json"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "executor file hashes mismatch"):
            freeze_failed_historical_result(
                run=_run(),
                jobs_payload=_jobs(),
                historical_artifacts_payload=_historical_artifacts(),
                executor_artifacts_payload=_executor_artifacts(),
                cell_failure_messages=EXPECTED_CELL_ERRORS,
                executor_zip_sha256=EXECUTOR_ZIP_SHA256,
                executor_file_sha256=hashes,
                preflight_zip_sha256=PREFLIGHT_ZIP_SHA256,
                preflight_json_sha256=PREFLIGHT_JSON_SHA256,
            )

    def test_wrong_run_head_or_number_is_rejected(self) -> None:
        run = _run()
        run["head_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "head_sha mismatch"):
            freeze_failed_historical_result(
                run=run,
                jobs_payload=_jobs(),
                historical_artifacts_payload=_historical_artifacts(),
                executor_artifacts_payload=_executor_artifacts(),
                cell_failure_messages=EXPECTED_CELL_ERRORS,
                executor_zip_sha256=EXECUTOR_ZIP_SHA256,
                executor_file_sha256=EXECUTOR_FILE_SHA256,
                preflight_zip_sha256=PREFLIGHT_ZIP_SHA256,
                preflight_json_sha256=PREFLIGHT_JSON_SHA256,
            )


if __name__ == "__main__":
    unittest.main()
