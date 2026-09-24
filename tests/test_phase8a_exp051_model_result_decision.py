from __future__ import annotations

from unittest.mock import patch
import unittest

from fmp.market_learning.model_successor_temporal_calibrated_utility_result_decision import (
    REVIEWED_AGGREGATE_ARTIFACT_DIGEST,
    REVIEWED_AGGREGATE_ARTIFACT_ID,
    REVIEWED_AGGREGATE_ARTIFACT_NAME,
    REVIEWED_EVIDENCE_FINGERPRINT,
    REVIEWED_MODEL_HEAD_SHA,
    REVIEWED_MODEL_RUN_ID,
    TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_DECISION,
    validate_reviewed_temporal_calibrated_utility_model_result,
)


def _run() -> dict[str, object]:
    return {
        "id": REVIEWED_MODEL_RUN_ID,
        "name": (
            "phase8a-exp051-temporal-calibrated-utility-model-training"
        ),
        "path": (
            ".github/workflows/"
            "phase8a-exp051-temporal-calibrated-utility-model-training.yml"
        ),
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": REVIEWED_MODEL_HEAD_SHA,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _artifacts() -> dict[str, object]:
    names = [
        (
            "exp051-temporal-calibrated-utility-model-cell-results-"
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
        "stage": (
            "TEMPORAL_CALIBRATED_UTILITY_MODEL_"
            "RESULT_REVIEW_REQUIRED"
        ),
        "temporal_calibrated_utility_model_terminal_reviewed": True,
        "temporal_calibrated_utility_model_result_review_decision": (
            "DEC-154"
        ),
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": 1,
        "reviewed_model_run_conclusion": "success",
        "persisted_cell_artifact_count": 9,
        "aggregate_artifact_present": True,
        "temporal_calibrated_utility_model_result_evidence_verified": True,
        "verified_cell_count": 18,
        "verified_regressor_count": 108,
        "verified_calibration_reference_count": 108,
        "selected_cell_count": 0,
        "no_temporal_calibrated_utility_stable_model_challenger_count": (
            18
        ),
        "validation_pass_cell_count": 0,
        "holdout_pass_cell_count": 0,
        "aggregate_selection_pass_variant_count": 1,
        "stable_selection_pass_variant_count": 0,
        "unavailable_budget_variant_count": 26,
        "utility_eligible_selection_row_count": 26392,
        "evidence_fingerprint": REVIEWED_EVIDENCE_FINGERPRINT,
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


class Exp051ResultDecisionTests(unittest.TestCase):
    @patch(
        "fmp.market_learning."
        "model_successor_temporal_calibrated_utility_result_decision."
        "validate_temporal_calibrated_utility_model_terminal_review"
    )
    def test_exact_review_closes_without_stable_candidate(
        self,
        terminal_review,
    ) -> None:
        terminal_review.return_value = _terminal_review()

        report = (
            validate_reviewed_temporal_calibrated_utility_model_result(
                run=_run(),
                jobs_payload={"jobs": []},
                artifacts_payload=_artifacts(),
                aggregate_evidence={"fixture": True},
            )
        )

        self.assertEqual(
            report["temporal_calibrated_utility_model_result_decision"],
            TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_DECISION,
        )
        self.assertEqual(
            report["stage"],
            (
                "TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_"
                "REVIEWED_NO_STABLE_CHALLENGER"
            ),
        )
        self.assertEqual(
            report["accepted_model_candidate_count"],
            0,
        )
        self.assertEqual(
            report["aggregate_selection_pass_variant_count"],
            1,
        )
        self.assertEqual(
            report["stable_selection_pass_variant_count"],
            0,
        )
        self.assertEqual(
            report["unavailable_budget_variant_count"],
            26,
        )
        self.assertEqual(
            report["utility_eligible_selection_row_count"],
            26392,
        )
        self.assertEqual(
            report[
                "no_temporal_calibrated_utility_stable_model_challenger_count"
            ],
            18,
        )
        self.assertEqual(
            report["verified_calibration_reference_count"],
            108,
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
            validate_reviewed_temporal_calibrated_utility_model_result(
                run=run,
                jobs_payload={},
                artifacts_payload=_artifacts(),
                aggregate_evidence={},
            )

    def test_wrong_aggregate_digest_fails_closed(self) -> None:
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
            validate_reviewed_temporal_calibrated_utility_model_result(
                run=_run(),
                jobs_payload={},
                artifacts_payload=artifacts,
                aggregate_evidence={},
            )

    @patch(
        "fmp.market_learning."
        "model_successor_temporal_calibrated_utility_result_decision."
        "validate_temporal_calibrated_utility_model_terminal_review"
    )
    def test_result_count_drift_fails_closed(
        self,
        terminal_review,
    ) -> None:
        drifted = _terminal_review()
        drifted["stable_selection_pass_variant_count"] = 1
        terminal_review.return_value = drifted

        with self.assertRaisesRegex(
            ValueError,
            "stable_selection_pass_variant_count mismatch",
        ):
            validate_reviewed_temporal_calibrated_utility_model_result(
                run=_run(),
                jobs_payload={},
                artifacts_payload=_artifacts(),
                aggregate_evidence={"fixture": True},
            )


if __name__ == "__main__":
    unittest.main()
