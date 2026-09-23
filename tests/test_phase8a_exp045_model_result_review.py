from __future__ import annotations

import unittest
from unittest.mock import patch

from fmp.market_learning.model_successor_result_review import (
    EXPECTED_DATASETS,
    SUCCESSOR_MODEL_RESULT_REVIEW_DECISION,
    validate_successor_model_terminal_review,
)


SHA = "a" * 40


def _run(conclusion: str = "success") -> dict[str, object]:
    return {
        "id": 12345,
        "name": "phase8a-exp045-model-training",
        "path": ".github/workflows/phase8a-exp045-model-training.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": SHA,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": conclusion,
    }


def _jobs(
    *,
    matrix_failure_index: int | None = None,
    aggregate_conclusion: str = "success",
) -> dict[str, object]:
    jobs: list[dict[str, object]] = [
        {
            "id": 1,
            "name": "authorization-preflight",
            "status": "completed",
            "conclusion": "success",
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
                    else "success"
                ),
            }
        )
    jobs.append(
        {
            "id": 100,
            "name": "aggregate-model-evidence",
            "status": "completed",
            "conclusion": aggregate_conclusion,
        }
    )
    return {"jobs": jobs}


def _cell_artifact_names() -> list[str]:
    return [
        f"exp045-model-cell-results-{symbol}-{timeframe}-{SHA}"
        for symbol, timeframe in EXPECTED_DATASETS
    ]


def _artifacts(
    names: list[str],
) -> dict[str, object]:
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


class Exp045ModelTerminalReviewTests(unittest.TestCase):
    def test_success_requires_complete_aggregate_and_stays_non_promotional(
        self,
    ) -> None:
        aggregate_name = (
            f"exp045-model-result-evidence-{SHA}-"
            "from-feature-35867307338-outcome-35876715434"
        )
        names = _cell_artifact_names() + [aggregate_name]
        summary = {
            "successor_model_result_evidence_verified": True,
            "selected_cell_count": 4,
            "validation_pass_count": 2,
            "retrospective_holdout_pass_count": 1,
            "promotion_authorized": False,
            "shadow_authorized": False,
            "trading_authorized": False,
        }

        with patch(
            "fmp.market_learning.model_successor_result_review."
            "validate_successor_model_result_evidence",
            return_value=summary,
        ) as validate:
            result = validate_successor_model_terminal_review(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(names),
                aggregate_evidence={"synthetic": True},
            )

        validate.assert_called_once_with(
            {"synthetic": True},
            expected_code_commit=SHA,
        )
        self.assertEqual(
            result["successor_model_result_review_decision"],
            SUCCESSOR_MODEL_RESULT_REVIEW_DECISION,
        )
        self.assertEqual(
            result["stage"],
            "SUCCESSOR_MODEL_RESULT_REVIEW_REQUIRED",
        )
        self.assertEqual(result["persisted_cell_artifact_count"], 9)
        self.assertTrue(result["aggregate_artifact_present"])
        self.assertTrue(result["prior_result_informed"])
        self.assertFalse(result["untouched_oos"])
        self.assertFalse(result["replacement_model_run_authorized"])
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["shadow_authorized"])
        self.assertFalse(result["trading_authorized"])

    def test_terminal_failure_preserves_partial_evidence_without_retry(
        self,
    ) -> None:
        names = _cell_artifact_names()[:4]
        result = validate_successor_model_terminal_review(
            run=_run("failure"),
            jobs_payload=_jobs(
                matrix_failure_index=4,
                aggregate_conclusion="skipped",
            ),
            artifacts_payload=_artifacts(names),
        )

        self.assertEqual(
            result["stage"],
            "SUCCESSOR_MODEL_RUN_FAILURE_REVIEW_REQUIRED",
        )
        self.assertEqual(result["persisted_cell_artifact_count"], 4)
        self.assertFalse(result["aggregate_artifact_present"])
        self.assertEqual(result["successful_matrix_job_count"], 8)
        self.assertEqual(result["failed_matrix_job_count"], 1)
        self.assertFalse(result["replacement_model_run_authorized"])
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["trading_authorized"])

    def test_rerun_attempt_is_rejected(self) -> None:
        run = _run("failure")
        run["run_attempt"] = 2
        with self.assertRaisesRegex(
            ValueError,
            "forbids rerun attempts",
        ):
            validate_successor_model_terminal_review(
                run=run,
                jobs_payload=_jobs(
                    matrix_failure_index=0,
                    aggregate_conclusion="skipped",
                ),
                artifacts_payload=_artifacts([]),
            )

    def test_success_without_aggregate_evidence_fails_closed(self) -> None:
        aggregate_name = (
            f"exp045-model-result-evidence-{SHA}-"
            "from-feature-35867307338-outcome-35876715434"
        )
        with self.assertRaisesRegex(
            ValueError,
            "requires aggregate evidence",
        ):
            validate_successor_model_terminal_review(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(
                    _cell_artifact_names() + [aggregate_name]
                ),
            )

    def test_unexpected_artifact_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "unexpected EXP-045 terminal review artifact",
        ):
            validate_successor_model_terminal_review(
                run=_run("failure"),
                jobs_payload=_jobs(
                    matrix_failure_index=1,
                    aggregate_conclusion="skipped",
                ),
                artifacts_payload=_artifacts(
                    ["unexpected-result.zip"]
                ),
            )


if __name__ == "__main__":
    unittest.main()
