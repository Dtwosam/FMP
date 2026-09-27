from __future__ import annotations

import copy
import unittest

from fmp.discovery.historical_failure_result_decision import (
    EXP061_EXECUTOR_ARTIFACT_DIGEST,
    EXP061_EXECUTOR_ARTIFACT_ID,
    EXP061_EXECUTOR_ARTIFACT_NAME,
    EXP061_EXECUTOR_HISTORICAL_RUNS_JSON_SHA256,
    EXP061_EXECUTOR_HISTORICAL_RUN_JSON_SHA256,
    EXP061_EXECUTOR_JSON_SHA256,
    EXP061_HISTORICAL_FAILURE_FREEZE_DECISION,
    EXP061_HISTORICAL_RUN_HEAD_SHA,
    EXP061_HISTORICAL_RUN_ID,
    EXP061_PREFLIGHT_ARTIFACT_DIGEST,
    EXP061_PREFLIGHT_ARTIFACT_ID,
    EXP061_PREFLIGHT_ARTIFACT_NAME,
    EXP061_PREFLIGHT_JSON_SHA256,
    freeze_exp061_historical_failure,
)
from fmp.discovery.run_contract import expected_job_names


def _run() -> dict[str, object]:
    return {
        "id": EXP061_HISTORICAL_RUN_ID,
        "name": "phase8a-exp061-discovery",
        "path": ".github/workflows/phase8a-exp061-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": EXP061_HISTORICAL_RUN_HEAD_SHA,
        "run_number": 2,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _jobs() -> dict[str, object]:
    rows = []
    for name in expected_job_names():
        conclusion = "failure"
        if name == "exp061-preflight":
            conclusion = "success"
        elif name == "exp061-aggregate":
            conclusion = "skipped"
        rows.append(
            {
                "id": abs(hash(name)) + 1,
                "name": name,
                "status": "completed",
                "conclusion": conclusion,
            }
        )
    return {"jobs": rows}


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": EXP061_PREFLIGHT_ARTIFACT_ID,
                "name": EXP061_PREFLIGHT_ARTIFACT_NAME,
                "digest": EXP061_PREFLIGHT_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


def _executor_run() -> dict[str, object]:
    return {
        "id": 36335739823,
        "name": "phase8a-exp061-historical-one-shot-execute",
        "path": ".github/workflows/phase8a-exp061-historical-one-shot-execute.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": EXP061_HISTORICAL_RUN_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _executor_artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": EXP061_EXECUTOR_ARTIFACT_ID,
                "name": EXP061_EXECUTOR_ARTIFACT_NAME,
                "digest": EXP061_EXECUTOR_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


def _freeze() -> dict[str, object]:
    return freeze_exp061_historical_failure(
        run=_run(),
        jobs_payload=_jobs(),
        artifacts_payload=_artifacts(),
        executor_run=_executor_run(),
        executor_artifacts_payload=_executor_artifacts(),
        executor_zip_sha256=EXP061_EXECUTOR_ARTIFACT_DIGEST.removeprefix(
            "sha256:"
        ),
        executor_json_sha256=EXP061_EXECUTOR_JSON_SHA256,
        historical_run_json_sha256=(
            EXP061_EXECUTOR_HISTORICAL_RUN_JSON_SHA256
        ),
        historical_runs_json_sha256=(
            EXP061_EXECUTOR_HISTORICAL_RUNS_JSON_SHA256
        ),
        preflight_zip_sha256=EXP061_PREFLIGHT_ARTIFACT_DIGEST.removeprefix(
            "sha256:"
        ),
        preflight_json_sha256=EXP061_PREFLIGHT_JSON_SHA256,
    )


class Exp061HistoricalFailureFreezeTests(unittest.TestCase):
    def test_exact_failure_freezes_exp061_without_retry(self) -> None:
        report = _freeze()
        self.assertEqual(
            report["decision"],
            EXP061_HISTORICAL_FAILURE_FREEZE_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "EXP061_HISTORICAL_FAILURE_FROZEN_NO_RETRY",
        )
        self.assertEqual(report["failed_cell_job_count"], 18)
        self.assertEqual(report["preflight_job_conclusion"], "success")
        self.assertEqual(report["aggregate_job_conclusion"], "skipped")
        self.assertEqual(report["cell_artifact_count"], 0)
        self.assertEqual(report["aggregate_artifact_count"], 0)
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertFalse(report["exp061_reusable_as_result"])
        self.assertTrue(report["new_experiment_identity_required_for_repair"])
        self.assertEqual(
            report["failure_interpretation"],
            "IMPLEMENTATION_INPUT_NORMALIZATION_FAILURE_NOT_MARKET_RESULT",
        )
        for field in (
            "exp061_retry_authorized",
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

    def test_job_shape_drift_is_rejected(self) -> None:
        jobs = _jobs()
        rows = jobs["jobs"]
        assert isinstance(rows, list)
        rows[1]["conclusion"] = "success"
        with self.assertRaisesRegex(
            ValueError,
            "terminal job conclusion counts mismatch",
        ):
            freeze_exp061_historical_failure(
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_artifacts(),
                executor_run=_executor_run(),
                executor_artifacts_payload=_executor_artifacts(),
                executor_zip_sha256=(
                    EXP061_EXECUTOR_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                executor_json_sha256=EXP061_EXECUTOR_JSON_SHA256,
                historical_run_json_sha256=(
                    EXP061_EXECUTOR_HISTORICAL_RUN_JSON_SHA256
                ),
                historical_runs_json_sha256=(
                    EXP061_EXECUTOR_HISTORICAL_RUNS_JSON_SHA256
                ),
                preflight_zip_sha256=(
                    EXP061_PREFLIGHT_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                preflight_json_sha256=EXP061_PREFLIGHT_JSON_SHA256,
            )

    def test_run_or_artifact_identity_drift_is_rejected(self) -> None:
        run = _run()
        run["run_number"] = 3
        with self.assertRaisesRegex(ValueError, "run_number mismatch"):
            freeze_exp061_historical_failure(
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                executor_run=_executor_run(),
                executor_artifacts_payload=_executor_artifacts(),
                executor_zip_sha256=(
                    EXP061_EXECUTOR_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                executor_json_sha256=EXP061_EXECUTOR_JSON_SHA256,
                historical_run_json_sha256=(
                    EXP061_EXECUTOR_HISTORICAL_RUN_JSON_SHA256
                ),
                historical_runs_json_sha256=(
                    EXP061_EXECUTOR_HISTORICAL_RUNS_JSON_SHA256
                ),
                preflight_zip_sha256=(
                    EXP061_PREFLIGHT_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                preflight_json_sha256=EXP061_PREFLIGHT_JSON_SHA256,
            )

        artifacts = _artifacts()
        artifacts["artifacts"][0]["id"] = EXP061_PREFLIGHT_ARTIFACT_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "preflight evidence id mismatch",
        ):
            freeze_exp061_historical_failure(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                executor_run=_executor_run(),
                executor_artifacts_payload=_executor_artifacts(),
                executor_zip_sha256=(
                    EXP061_EXECUTOR_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                executor_json_sha256=EXP061_EXECUTOR_JSON_SHA256,
                historical_run_json_sha256=(
                    EXP061_EXECUTOR_HISTORICAL_RUN_JSON_SHA256
                ),
                historical_runs_json_sha256=(
                    EXP061_EXECUTOR_HISTORICAL_RUNS_JSON_SHA256
                ),
                preflight_zip_sha256=(
                    EXP061_PREFLIGHT_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                preflight_json_sha256=EXP061_PREFLIGHT_JSON_SHA256,
            )

    def test_downloaded_evidence_hash_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "executor_json_sha256 mismatch"):
            freeze_exp061_historical_failure(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                executor_run=_executor_run(),
                executor_artifacts_payload=_executor_artifacts(),
                executor_zip_sha256=(
                    EXP061_EXECUTOR_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                executor_json_sha256="0" * 64,
                historical_run_json_sha256=(
                    EXP061_EXECUTOR_HISTORICAL_RUN_JSON_SHA256
                ),
                historical_runs_json_sha256=(
                    EXP061_EXECUTOR_HISTORICAL_RUNS_JSON_SHA256
                ),
                preflight_zip_sha256=(
                    EXP061_PREFLIGHT_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                preflight_json_sha256=EXP061_PREFLIGHT_JSON_SHA256,
            )


if __name__ == "__main__":
    unittest.main()
