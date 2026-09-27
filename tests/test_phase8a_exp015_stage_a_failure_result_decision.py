from __future__ import annotations

import copy
import unittest

from fmp.portfolio.exp015_stage_a_failure_result_decision import (
    CATALOG_ARTIFACT,
    CELL_ARTIFACTS,
    EXPECTED_FAILURE_SIGNATURE,
    EXP015_STAGE_A_FAILURE_RESULT_DECISION,
    FAILURE_CLASSIFICATION,
    REVIEWED_FAILED_CELL,
    REVIEWED_FAILED_CELL_JOB_ID,
    REVIEWED_STAGE_A_HEAD_SHA,
    REVIEWED_STAGE_A_RUN_ID,
    validate_exp015_stage_a_reviewed_failure,
)


CATALOG_JOB_ID = 108508225193
AUTHORIZE_JOB_ID = 108538985395
SUCCESS_JOB_IDS = (
    108508311689,
    108508311695,
    108508311700,
    108508311733,
    108508311748,
    108508311751,
    108508311765,
    108508311794,
)


def _run() -> dict[str, object]:
    return {
        "id": REVIEWED_STAGE_A_RUN_ID,
        "name": "phase8a-exp015-stage-a",
        "path": ".github/workflows/phase8a-exp015-stage-a.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": REVIEWED_STAGE_A_HEAD_SHA,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _jobs() -> dict[str, object]:
    rows: list[dict[str, object]] = [
        {
            "id": CATALOG_JOB_ID,
            "status": "completed",
            "conclusion": "success",
        },
        {
            "id": REVIEWED_FAILED_CELL_JOB_ID,
            "status": "completed",
            "conclusion": "failure",
        },
        {
            "id": AUTHORIZE_JOB_ID,
            "status": "completed",
            "conclusion": "skipped",
        },
    ]
    rows.extend(
        {
            "id": job_id,
            "status": "completed",
            "conclusion": "success",
        }
        for job_id in SUCCESS_JOB_IDS
    )
    return {"jobs": rows}


def _artifacts() -> dict[str, object]:
    rows: list[dict[str, object]] = [
        {
            **CATALOG_ARTIFACT,
            "expired": False,
        }
    ]
    for (symbol, timeframe), expected in CELL_ARTIFACTS.items():
        rows.append(
            {
                "id": expected["id"],
                "name": (
                    f"phase8a-exp015-stage-a-{symbol}-{timeframe}-"
                    f"{REVIEWED_STAGE_A_HEAD_SHA}"
                ),
                "digest": expected["digest"],
                "expired": False,
            }
        )
    return {"artifacts": rows, "total_count": len(rows)}


class Exp015StageAFailureResultDecisionTests(unittest.TestCase):
    def test_exact_failure_closes_stage_a_without_downstream_authorization(self) -> None:
        report = validate_exp015_stage_a_reviewed_failure(
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            failure_signature=EXPECTED_FAILURE_SIGNATURE,
        )

        self.assertEqual(
            report["exp015_stage_a_failure_result_decision"],
            EXP015_STAGE_A_FAILURE_RESULT_DECISION,
        )
        self.assertEqual(report["stage"], "EXP015_STAGE_A_REVIEWED_FAILED_CLOSED")
        self.assertEqual(report["failure_classification"], FAILURE_CLASSIFICATION)
        self.assertEqual(
            (report["failed_symbol"], report["failed_timeframe"]),
            REVIEWED_FAILED_CELL,
        )
        self.assertEqual(report["successful_cell_count"], 8)
        self.assertEqual(report["failed_cell_count"], 1)
        self.assertEqual(report["persisted_cell_artifact_count"], 8)
        self.assertFalse(report["authorization_artifact_present"])
        self.assertFalse(report["authoritative_stage_a_success_result_produced"])
        self.assertFalse(report["authoritative_survivor_set_produced"])

        for field in (
            "stage_a_retry_authorized",
            "stage_a_replacement_authorized",
            "stage_b_source_open_authorized",
            "stage_b_execution_authorized",
            "stage_c_execution_authorized",
            "portfolio_selection_authorized",
            "phase8a_acceptance_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(report[field], field)

    def test_rejects_wrong_run_identity(self) -> None:
        run = _run()
        run["id"] = REVIEWED_STAGE_A_RUN_ID + 1
        with self.assertRaisesRegex(ValueError, "run id mismatch"):
            validate_exp015_stage_a_reviewed_failure(
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                failure_signature=EXPECTED_FAILURE_SIGNATURE,
            )

    def test_rejects_any_second_failed_job(self) -> None:
        jobs = _jobs()
        rows = jobs["jobs"]
        assert isinstance(rows, list)
        for row in rows:
            if isinstance(row, dict) and row.get("id") == SUCCESS_JOB_IDS[0]:
                row["conclusion"] = "failure"
                break
        with self.assertRaisesRegex(ValueError, "successful cell job conclusion mismatch"):
            validate_exp015_stage_a_reviewed_failure(
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_artifacts(),
                failure_signature=EXPECTED_FAILURE_SIGNATURE,
            )

    def test_rejects_missing_or_tampered_artifact_digest(self) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows[1]["digest"] = "sha256:" + ("0" * 64)
        with self.assertRaisesRegex(ValueError, "artifact digest mismatch"):
            validate_exp015_stage_a_reviewed_failure(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                failure_signature=EXPECTED_FAILURE_SIGNATURE,
            )

    def test_rejects_failed_cell_artifact_or_authorization_artifact(self) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows.append(
            {
                "id": 1,
                "name": (
                    "phase8a-exp015-stage-a-USDJPY-1h-"
                    f"{REVIEWED_STAGE_A_HEAD_SHA}"
                ),
                "digest": "sha256:" + ("0" * 64),
                "expired": False,
            }
        )
        with self.assertRaisesRegex(ValueError, "exactly the catalog plus eight"):
            validate_exp015_stage_a_reviewed_failure(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                failure_signature=EXPECTED_FAILURE_SIGNATURE,
            )

    def test_rejects_failure_signature_drift(self) -> None:
        with self.assertRaisesRegex(ValueError, "failure signature mismatch"):
            validate_exp015_stage_a_reviewed_failure(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                failure_signature="ValueError: something else",
            )


if __name__ == "__main__":
    unittest.main()
