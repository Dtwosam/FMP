from __future__ import annotations

import unittest
from unittest.mock import patch

from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_result_decision import (
    EXPECTED_MATRIX_FAILURE_EXPORTS,
    FAILURE_CLASSIFICATION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_DECISION,
    PREDECESSOR_TRAINING_MODULE,
    REVIEWED_MODEL_HEAD_SHA,
    REVIEWED_MODEL_RUN_ID,
    validate_reviewed_fit_temporal_residual_lower_tail_utility_failed_result,
)


def _run() -> dict[str, object]:
    return {
        "id": REVIEWED_MODEL_RUN_ID,
        "name": (
            "phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training"
        ),
        "path": (
            ".github/workflows/"
            "phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml"
        ),
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": REVIEWED_MODEL_HEAD_SHA,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _jobs() -> dict[str, object]:
    jobs: list[dict[str, object]] = [
        {
            "id": 108206116932,
            "name": "authorization-preflight",
            "status": "completed",
            "conclusion": "success",
        }
    ]
    for job_id in EXPECTED_MATRIX_FAILURE_EXPORTS:
        jobs.append(
            {
                "id": job_id,
                "name": f"model-cells (synthetic-{job_id})",
                "status": "completed",
                "conclusion": "failure",
            }
        )
    jobs.append(
        {
            "id": 108210729511,
            "name": "aggregate-model-evidence",
            "status": "completed",
            "conclusion": "skipped",
        }
    )
    return {"jobs": jobs}


def _terminal_review() -> dict[str, object]:
    return {
        "fit_temporal_residual_lower_tail_utility_model_terminal_reviewed": True,
        "fit_temporal_residual_lower_tail_utility_model_result_review_decision": (
            "DEC-213"
        ),
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": 1,
        "reviewed_model_run_conclusion": "failure",
        "persisted_cell_artifact_count": 0,
        "aggregate_artifact_present": False,
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_"
            "RUN_FAILURE_REVIEW_REQUIRED"
        ),
        "authorization_preflight_conclusion": "success",
        "successful_matrix_job_count": 0,
        "failed_matrix_job_count": 9,
        "cancelled_matrix_job_count": 0,
        "skipped_matrix_job_count": 0,
        "replacement_model_run_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def _failure_signatures() -> dict[int, str]:
    return {
        job_id: (
            f"AttributeError: module '{PREDECESSOR_TRAINING_MODULE}' "
            f"has no attribute '{export}'"
        )
        for job_id, export in EXPECTED_MATRIX_FAILURE_EXPORTS.items()
    }


class Exp056FailedResultDecisionTests(unittest.TestCase):
    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_lower_tail_utility_result_decision."
        "validate_fit_temporal_residual_lower_tail_utility_model_terminal_review"
    )
    def test_exact_failed_attempt_closes_without_result(
        self,
        terminal_review,
    ) -> None:
        terminal_review.return_value = _terminal_review()
        report = (
            validate_reviewed_fit_temporal_residual_lower_tail_utility_failed_result(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload={"total_count": 0, "artifacts": []},
                failure_signatures=_failure_signatures(),
            )
        )

        self.assertEqual(
            report[
                "fit_temporal_residual_lower_tail_utility_model_result_decision"
            ],
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_DECISION,
        )
        self.assertEqual(
            report["stage"],
            (
                "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_"
                "REVIEWED_FAILED_NO_RESULT"
            ),
        )
        self.assertEqual(
            report["failure_classification"],
            FAILURE_CLASSIFICATION,
        )
        self.assertFalse(report["model_result_produced"])
        self.assertEqual(report["accepted_model_candidate_count"], 0)
        self.assertEqual(
            report["missing_stability_share_export_job_count"],
            8,
        )
        self.assertEqual(
            report["missing_support_count_export_job_count"],
            1,
        )

        for field in (
            "model_run_dispatch_authorized",
            "replacement_model_run_authorized",
            "authoritative_model_result_execution_authorized",
            "model_protocol_result_authorized",
            "model_fit_authorized",
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(report[field], False)

    def test_wrong_run_identity_fails_closed(self) -> None:
        run = _run()
        run["id"] = REVIEWED_MODEL_RUN_ID + 1
        with self.assertRaisesRegex(ValueError, "run id mismatch"):
            validate_reviewed_fit_temporal_residual_lower_tail_utility_failed_result(
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload={"total_count": 0, "artifacts": []},
                failure_signatures=_failure_signatures(),
            )

    def test_any_artifact_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "zero persisted model artifacts"):
            validate_reviewed_fit_temporal_residual_lower_tail_utility_failed_result(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload={
                    "total_count": 1,
                    "artifacts": [{"id": 1, "name": "unexpected"}],
                },
                failure_signatures=_failure_signatures(),
            )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_lower_tail_utility_result_decision."
        "validate_fit_temporal_residual_lower_tail_utility_model_terminal_review"
    )
    def test_failure_signature_drift_fails_closed(
        self,
        terminal_review,
    ) -> None:
        terminal_review.return_value = _terminal_review()
        signatures = _failure_signatures()
        first = next(iter(signatures))
        signatures[first] = signatures[first].replace(
            "MIN_STABILITY_WINDOW_CANDIDATE_SHARE",
            "WRONG_EXPORT",
        )
        with self.assertRaisesRegex(
            ValueError,
            "failure signature mismatch",
        ):
            validate_reviewed_fit_temporal_residual_lower_tail_utility_failed_result(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload={"total_count": 0, "artifacts": []},
                failure_signatures=signatures,
            )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_lower_tail_utility_result_decision."
        "validate_fit_temporal_residual_lower_tail_utility_model_terminal_review"
    )
    def test_terminal_review_summary_drift_fails_closed(
        self,
        terminal_review,
    ) -> None:
        drifted = _terminal_review()
        drifted["failed_matrix_job_count"] = 8
        terminal_review.return_value = drifted
        with self.assertRaisesRegex(
            ValueError,
            "failed_matrix_job_count mismatch",
        ):
            validate_reviewed_fit_temporal_residual_lower_tail_utility_failed_result(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload={"total_count": 0, "artifacts": []},
                failure_signatures=_failure_signatures(),
            )

    def test_source_contains_no_execution_or_broker_path(self) -> None:
        import inspect
        import fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_result_decision as module

        source = inspect.getsource(module)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
