from __future__ import annotations

import unittest
from unittest.mock import patch

from fmp.market_learning.model_successor_regime_utility_result_review import (
    DEC135_MERGED_COMMIT,
    EXPECTED_DATASETS,
    REGIME_UTILITY_MODEL_RESULT_REVIEW_DECISION,
    REGIME_UTILITY_MODEL_WORKFLOW_NAME,
    REGIME_UTILITY_MODEL_WORKFLOW_PATH,
    REPLACEMENT_MODEL_RUN_AUTHORIZED,
    validate_regime_utility_model_terminal_review,
)


SHA = "a" * 40


def _run(conclusion: str = "success") -> dict[str, object]:
    return {
        "id": 12345,
        "name": REGIME_UTILITY_MODEL_WORKFLOW_NAME,
        "path": REGIME_UTILITY_MODEL_WORKFLOW_PATH,
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
        f"exp049-regime-utility-model-cell-results-{symbol}-{timeframe}-{SHA}"
        for symbol, timeframe in EXPECTED_DATASETS
    ]


def _aggregate_artifact_name() -> str:
    return (
        f"exp049-regime-utility-model-result-evidence-{SHA}-"
        "from-feature-35867307338-outcome-35876715434"
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


class Exp049ModelTerminalReviewTests(unittest.TestCase):
    def test_review_identity_is_predeclared_and_non_authorizing(
        self,
    ) -> None:
        self.assertEqual(
            REGIME_UTILITY_MODEL_RESULT_REVIEW_DECISION,
            "DEC-136",
        )
        self.assertEqual(
            DEC135_MERGED_COMMIT,
            "0fe11d26fd74355e39f7379f3eeba869d848271c",
        )
        self.assertEqual(
            REGIME_UTILITY_MODEL_WORKFLOW_NAME,
            "phase8a-exp049-regime-utility-model-training",
        )
        self.assertEqual(
            REGIME_UTILITY_MODEL_WORKFLOW_PATH,
            ".github/workflows/phase8a-exp049-regime-utility-model-training.yml",
        )
        self.assertFalse(REPLACEMENT_MODEL_RUN_AUTHORIZED)

    def test_success_requires_complete_aggregate_and_stays_non_promotional(
        self,
    ) -> None:
        names = _cell_artifact_names() + [
            _aggregate_artifact_name()
        ]
        summary = {
            "regime_utility_model_result_evidence_verified": True,
            "selected_cell_count": 4,
            "validation_pass_count": 2,
            "retrospective_holdout_pass_count": 1,
            "promotion_authorized": False,
            "shadow_authorized": False,
            "trading_authorized": False,
        }

        with patch(
            "fmp.market_learning."
            "model_successor_regime_utility_result_review."
            "validate_regime_utility_model_result_evidence",
            return_value=summary,
        ) as validate:
            result = validate_regime_utility_model_terminal_review(
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
            result["regime_utility_model_result_review_decision"],
            REGIME_UTILITY_MODEL_RESULT_REVIEW_DECISION,
        )
        self.assertEqual(
            result["stage"],
            "REGIME_UTILITY_MODEL_RESULT_REVIEW_REQUIRED",
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
        result = validate_regime_utility_model_terminal_review(
            run=_run("failure"),
            jobs_payload=_jobs(
                matrix_failure_index=4,
                aggregate_conclusion="skipped",
            ),
            artifacts_payload=_artifacts(names),
        )

        self.assertEqual(
            result["stage"],
            "REGIME_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED",
        )
        self.assertEqual(result["persisted_cell_artifact_count"], 4)
        self.assertFalse(result["aggregate_artifact_present"])
        self.assertEqual(result["successful_matrix_job_count"], 8)
        self.assertEqual(result["failed_matrix_job_count"], 1)
        self.assertFalse(result["replacement_model_run_authorized"])
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["trading_authorized"])

    def test_preflight_failure_can_only_preserve_no_aggregate_result(
        self,
    ) -> None:
        result = validate_regime_utility_model_terminal_review(
            run=_run("failure"),
            jobs_payload=_jobs(
                preflight_conclusion="failure",
                aggregate_conclusion="skipped",
            ),
            artifacts_payload=_artifacts([]),
        )
        self.assertEqual(
            result["authorization_preflight_conclusion"],
            "failure",
        )
        self.assertEqual(result["successful_matrix_job_count"], 0)
        self.assertEqual(result["skipped_matrix_job_count"], 9)
        self.assertFalse(result["aggregate_artifact_present"])
        self.assertFalse(result["replacement_model_run_authorized"])

    def test_rerun_attempt_is_rejected(self) -> None:
        run = _run("failure")
        run["run_attempt"] = 2
        with self.assertRaisesRegex(
            ValueError,
            "forbids rerun attempts",
        ):
            validate_regime_utility_model_terminal_review(
                run=run,
                jobs_payload=_jobs(
                    matrix_failure_index=0,
                    aggregate_conclusion="skipped",
                ),
                artifacts_payload=_artifacts([]),
            )

    def test_success_without_aggregate_evidence_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "requires aggregate evidence",
        ):
            validate_regime_utility_model_terminal_review(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(
                    _cell_artifact_names()
                    + [_aggregate_artifact_name()]
                ),
            )

    def test_non_success_cannot_claim_aggregate_artifact(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "cannot claim aggregate artifact",
        ):
            validate_regime_utility_model_terminal_review(
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
            "unexpected EXP-049 terminal review artifact",
        ):
            validate_regime_utility_model_terminal_review(
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
        run["name"] = "phase8a-exp048-regime-consensus-model-training"
        with self.assertRaisesRegex(
            ValueError,
            "workflow name mismatch",
        ):
            validate_regime_utility_model_terminal_review(
                run=run,
                jobs_payload=_jobs(
                    matrix_failure_index=1,
                    aggregate_conclusion="skipped",
                ),
                artifacts_payload=_artifacts([]),
            )


if __name__ == "__main__":
    unittest.main()
