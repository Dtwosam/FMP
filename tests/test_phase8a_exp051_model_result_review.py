from __future__ import annotations

import unittest
from unittest.mock import patch

from fmp.market_learning.model_successor_temporal_calibrated_utility_result_review import (
    DEC153_MERGED_COMMIT,
    EXPECTED_DATASETS,
    REPLACEMENT_MODEL_RUN_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_REVIEW_DECISION,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_NAME,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_PATH,
    validate_temporal_calibrated_utility_model_terminal_review,
)


SHA = "a" * 40


def _run(conclusion: str = "success") -> dict[str, object]:
    return {
        "id": 12345,
        "name": TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_NAME,
        "path": TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": SHA,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": conclusion,
    }


def _jobs(
    *,
    preflight_conclusion: str = "success",
    matrix_failure_index: int | None = None,
    aggregate_conclusion: str = "success",
) -> dict[str, object]:
    jobs: list[dict[str, object]] = [
        {
            "id": 1,
            "name": "authorization-preflight",
            "status": "completed",
            "conclusion": preflight_conclusion,
        }
    ]
    for index, (symbol, timeframe) in enumerate(EXPECTED_DATASETS):
        jobs.append(
            {
                "id": 10 + index,
                "name": (
                    f"model-cells ({symbol}, {timeframe}, synthetic)"
                ),
                "status": "completed",
                "conclusion": (
                    "failure"
                    if index == matrix_failure_index
                    else (
                        "skipped"
                        if preflight_conclusion != "success"
                        else "success"
                    )
                ),
            }
        )
    jobs.append(
        {
            "id": 100,
            "name": "aggregate-model-evidence",
            "status": "completed",
            "conclusion": (
                "skipped"
                if preflight_conclusion != "success"
                else aggregate_conclusion
            ),
        }
    )
    return {"jobs": jobs}


def _cell_artifact_names() -> list[str]:
    return [
        (
            "exp051-temporal-calibrated-utility-model-cell-results-"
            f"{symbol}-{timeframe}-{SHA}"
        )
        for symbol, timeframe in EXPECTED_DATASETS
    ]


def _aggregate_artifact_name() -> str:
    return (
        "exp051-temporal-calibrated-utility-model-result-evidence-"
        f"{SHA}-from-feature-35867307338-outcome-35876715434"
    )


def _artifacts(names: list[str]) -> dict[str, object]:
    rows = [
        {
            "id": index + 1000,
            "name": name,
            "expired": False,
        }
        for index, name in enumerate(names)
    ]
    return {
        "total_count": len(rows),
        "artifacts": rows,
    }


class Exp051ModelTerminalReviewTests(unittest.TestCase):
    def test_review_identity_is_predeclared_and_non_authorizing(
        self,
    ) -> None:
        self.assertEqual(
            TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_REVIEW_DECISION,
            "DEC-154",
        )
        self.assertEqual(
            DEC153_MERGED_COMMIT,
            "b0fb55aca2d818e7306a15b200b1e10fcc151ad2",
        )
        self.assertEqual(
            TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_NAME,
            "phase8a-exp051-temporal-calibrated-utility-model-training",
        )
        self.assertEqual(
            TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_PATH,
            ".github/workflows/"
            "phase8a-exp051-temporal-calibrated-utility-model-training.yml",
        )
        self.assertFalse(REPLACEMENT_MODEL_RUN_AUTHORIZED)

    def test_success_requires_complete_aggregate_and_revalidates_dec152(
        self,
    ) -> None:
        names = _cell_artifact_names() + [
            _aggregate_artifact_name()
        ]
        summary = {
            "temporal_calibrated_utility_model_result_evidence_verified": True,
            "verified_cell_count": 18,
            "verified_regressor_count": 108,
            "verified_calibration_reference_count": 108,
            "selected_cell_count": 0,
            "validation_pass_cell_count": 0,
            "holdout_pass_cell_count": 0,
            "promotion_authorized": False,
            "shadow_authorized": False,
            "trading_authorized": False,
        }

        with patch(
            "fmp.market_learning."
            "model_successor_temporal_calibrated_utility_result_review."
            "validate_temporal_calibrated_utility_model_result_evidence",
            return_value=summary,
        ) as validate:
            result = (
                validate_temporal_calibrated_utility_model_terminal_review(
                    run=_run(),
                    jobs_payload=_jobs(),
                    artifacts_payload=_artifacts(names),
                    aggregate_evidence={"synthetic": True},
                )
            )

        validate.assert_called_once_with(
            {"synthetic": True},
            expected_code_commit=SHA,
        )
        self.assertEqual(
            result[
                "temporal_calibrated_utility_model_result_review_decision"
            ],
            TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_REVIEW_DECISION,
        )
        self.assertEqual(
            result["stage"],
            "TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_REVIEW_REQUIRED",
        )
        self.assertEqual(
            result["persisted_cell_artifact_count"],
            9,
        )
        self.assertTrue(result["aggregate_artifact_present"])
        self.assertEqual(
            result["verified_regressor_count"],
            108,
        )
        self.assertEqual(
            result["verified_calibration_reference_count"],
            108,
        )
        self.assertFalse(
            result["replacement_model_run_authorized"]
        )
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["trading_authorized"])

    def test_terminal_failure_preserves_partial_evidence_without_retry(
        self,
    ) -> None:
        result = (
            validate_temporal_calibrated_utility_model_terminal_review(
                run=_run("failure"),
                jobs_payload=_jobs(
                    matrix_failure_index=4,
                    aggregate_conclusion="skipped",
                ),
                artifacts_payload=_artifacts(
                    _cell_artifact_names()[:4]
                ),
            )
        )

        self.assertEqual(
            result["stage"],
            "TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED",
        )
        self.assertEqual(
            result["persisted_cell_artifact_count"],
            4,
        )
        self.assertFalse(result["aggregate_artifact_present"])
        self.assertEqual(
            result["successful_matrix_job_count"],
            8,
        )
        self.assertEqual(result["failed_matrix_job_count"], 1)
        self.assertFalse(
            result["replacement_model_run_authorized"]
        )

    def test_preflight_failure_keeps_all_result_paths_closed(
        self,
    ) -> None:
        result = (
            validate_temporal_calibrated_utility_model_terminal_review(
                run=_run("failure"),
                jobs_payload=_jobs(
                    preflight_conclusion="failure",
                    aggregate_conclusion="skipped",
                ),
                artifacts_payload=_artifacts([]),
            )
        )
        self.assertEqual(
            result["authorization_preflight_conclusion"],
            "failure",
        )
        self.assertEqual(
            result["successful_matrix_job_count"],
            0,
        )
        self.assertEqual(
            result["skipped_matrix_job_count"],
            9,
        )
        self.assertFalse(result["aggregate_artifact_present"])

    def test_rerun_attempt_is_rejected(self) -> None:
        run = _run("failure")
        run["run_attempt"] = 2
        with self.assertRaisesRegex(
            ValueError,
            "forbids rerun attempts",
        ):
            validate_temporal_calibrated_utility_model_terminal_review(
                run=run,
                jobs_payload=_jobs(
                    matrix_failure_index=0,
                    aggregate_conclusion="skipped",
                ),
                artifacts_payload=_artifacts([]),
            )

    def test_success_without_aggregate_evidence_fails_closed(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "requires aggregate evidence",
        ):
            validate_temporal_calibrated_utility_model_terminal_review(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(
                    _cell_artifact_names()
                    + [_aggregate_artifact_name()]
                ),
            )

    def test_non_success_cannot_claim_aggregate_artifact(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "cannot claim aggregate artifact",
        ):
            validate_temporal_calibrated_utility_model_terminal_review(
                run=_run("failure"),
                jobs_payload=_jobs(
                    matrix_failure_index=1,
                    aggregate_conclusion="skipped",
                ),
                artifacts_payload=_artifacts(
                    [_aggregate_artifact_name()]
                ),
            )

    def test_unexpected_artifact_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "unexpected EXP-051 terminal review artifact",
        ):
            validate_temporal_calibrated_utility_model_terminal_review(
                run=_run("failure"),
                jobs_payload=_jobs(
                    matrix_failure_index=1,
                    aggregate_conclusion="skipped",
                ),
                artifacts_payload=_artifacts(
                    ["unexpected-result.zip"]
                ),
            )

    def test_wrong_workflow_identity_is_rejected(self) -> None:
        run = _run("failure")
        run["name"] = (
            "phase8a-exp050-temporal-jackknife-utility-model-training"
        )
        with self.assertRaisesRegex(
            ValueError,
            "workflow name mismatch",
        ):
            validate_temporal_calibrated_utility_model_terminal_review(
                run=run,
                jobs_payload=_jobs(
                    matrix_failure_index=1,
                    aggregate_conclusion="skipped",
                ),
                artifacts_payload=_artifacts([]),
            )


if __name__ == "__main__":
    unittest.main()
