from __future__ import annotations

from unittest.mock import patch
import unittest

from fmp.market_learning.model_successor_result_decision import (
    REVIEWED_AGGREGATE_ARTIFACT_DIGEST,
    REVIEWED_AGGREGATE_ARTIFACT_ID,
    REVIEWED_AGGREGATE_ARTIFACT_NAME,
    REVIEWED_EVIDENCE_FINGERPRINT,
    REVIEWED_MODEL_HEAD_SHA,
    REVIEWED_MODEL_RUN_ID,
    SUCCESSOR_MODEL_RESULT_DECISION,
    validate_reviewed_successor_model_result,
)


def _run() -> dict[str, object]:
    return {
        "id": REVIEWED_MODEL_RUN_ID,
        "name": "phase8a-exp045-model-training",
        "path": ".github/workflows/phase8a-exp045-model-training.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": REVIEWED_MODEL_HEAD_SHA,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    jobs: list[dict[str, object]] = [
        {
            "id": 1,
            "name": "authorization-preflight",
            "status": "completed",
            "conclusion": "success",
        }
    ]
    for index, (symbol, timeframe) in enumerate(
        (
            ("EURUSD", "5m"),
            ("EURUSD", "15m"),
            ("EURUSD", "1h"),
            ("GBPUSD", "5m"),
            ("GBPUSD", "15m"),
            ("GBPUSD", "1h"),
            ("USDJPY", "5m"),
            ("USDJPY", "15m"),
            ("USDJPY", "1h"),
        ),
        start=2,
    ):
        jobs.append(
            {
                "id": index,
                "name": (
                    f"model-cells ({symbol}, {timeframe}, fixture)"
                ),
                "status": "completed",
                "conclusion": "success",
            }
        )
    jobs.append(
        {
            "id": 11,
            "name": "aggregate-model-evidence",
            "status": "completed",
            "conclusion": "success",
        }
    )
    return {"jobs": jobs}


def _artifacts() -> dict[str, object]:
    names = [
        (
            "exp045-model-cell-results-"
            f"{symbol}-{timeframe}-{REVIEWED_MODEL_HEAD_SHA}"
        )
        for symbol, timeframe in (
            ("EURUSD", "5m"),
            ("EURUSD", "15m"),
            ("EURUSD", "1h"),
            ("GBPUSD", "5m"),
            ("GBPUSD", "15m"),
            ("GBPUSD", "1h"),
            ("USDJPY", "5m"),
            ("USDJPY", "15m"),
            ("USDJPY", "1h"),
        )
    ]
    artifacts: list[dict[str, object]] = [
        {
            "id": 100 + index,
            "name": name,
            "expired": False,
        }
        for index, name in enumerate(names)
    ]
    artifacts.append(
        {
            "id": REVIEWED_AGGREGATE_ARTIFACT_ID,
            "name": REVIEWED_AGGREGATE_ARTIFACT_NAME,
            "digest": REVIEWED_AGGREGATE_ARTIFACT_DIGEST,
            "expired": False,
        }
    )
    return {
        "total_count": 10,
        "artifacts": artifacts,
    }


def _terminal_review() -> dict[str, object]:
    return {
        "stage": "SUCCESSOR_MODEL_RESULT_REVIEW_REQUIRED",
        "successor_model_terminal_reviewed": True,
        "successor_model_result_review_decision": "DEC-100",
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": 1,
        "reviewed_model_run_conclusion": "success",
        "persisted_cell_artifact_count": 9,
        "aggregate_artifact_present": True,
        "successor_model_result_evidence_verified": True,
        "successor_model_result_evidence_fingerprint": (
            REVIEWED_EVIDENCE_FINGERPRINT
        ),
        "successor_model_result_code_commit": (
            REVIEWED_MODEL_HEAD_SHA
        ),
        "verified_cell_count": 18,
        "selected_cell_count": 1,
        "no_model_challenger_count": 17,
        "no_model_family_available_count": 0,
        "validation_pass_count": 0,
        "retrospective_holdout_pass_count": 0,
        "logistic_nonconvergence_cell_count": 6,
        "prior_result_informed": True,
        "untouched_oos": False,
        "replacement_model_run_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


class Exp045ResultDecisionTests(unittest.TestCase):
    @patch(
        "fmp.market_learning.model_successor_result_decision."
        "validate_successor_model_terminal_review"
    )
    def test_exact_review_closes_without_accepted_candidate(
        self,
        terminal_review,
    ) -> None:
        terminal_review.return_value = _terminal_review()

        report = validate_reviewed_successor_model_result(
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            aggregate_evidence={"fixture": True},
        )

        self.assertEqual(
            report["successor_model_result_decision"],
            SUCCESSOR_MODEL_RESULT_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "SUCCESSOR_MODEL_RESULT_REVIEWED_NO_ACCEPTED_CHALLENGER",
        )
        self.assertEqual(
            report["accepted_model_candidate_count"],
            0,
        )
        self.assertEqual(report["selected_cell_count"], 1)
        self.assertEqual(
            report["no_model_challenger_count"],
            17,
        )
        self.assertEqual(
            report["validation_pass_count"],
            0,
        )
        self.assertEqual(
            report["retrospective_holdout_pass_count"],
            0,
        )
        self.assertEqual(
            report["logistic_nonconvergence_cell_count"],
            6,
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

        terminal_review.assert_called_once()

    def test_wrong_run_identity_fails_closed(self) -> None:
        run = _run()
        run["id"] = REVIEWED_MODEL_RUN_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "run id mismatch",
        ):
            validate_reviewed_successor_model_result(
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                aggregate_evidence={},
            )

    def test_wrong_aggregate_artifact_id_fails_closed(
        self,
    ) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows[-1] = {
            **rows[-1],
            "id": REVIEWED_AGGREGATE_ARTIFACT_ID + 1,
        }
        with self.assertRaisesRegex(
            ValueError,
            "artifact id mismatch",
        ):
            validate_reviewed_successor_model_result(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                aggregate_evidence={},
            )

    def test_wrong_aggregate_digest_fails_closed(
        self,
    ) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows[-1] = {
            **rows[-1],
            "digest": "sha256:" + "0" * 64,
        }
        with self.assertRaisesRegex(
            ValueError,
            "artifact digest mismatch",
        ):
            validate_reviewed_successor_model_result(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                aggregate_evidence={},
            )

    @patch(
        "fmp.market_learning.model_successor_result_decision."
        "validate_successor_model_terminal_review"
    )
    def test_result_count_drift_fails_closed(
        self,
        terminal_review,
    ) -> None:
        drifted = _terminal_review()
        drifted["validation_pass_count"] = 1
        terminal_review.return_value = drifted

        with self.assertRaisesRegex(
            ValueError,
            "validation_pass_count mismatch",
        ):
            validate_reviewed_successor_model_result(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                aggregate_evidence={"fixture": True},
            )


if __name__ == "__main__":
    unittest.main()
