from __future__ import annotations

from unittest.mock import patch
import unittest

from fmp.market_learning.model_successor_regime_utility_result_decision import (
    REGIME_UTILITY_MODEL_RESULT_DECISION,
    REVIEWED_AGGREGATE_ARTIFACT_DIGEST,
    REVIEWED_AGGREGATE_ARTIFACT_ID,
    REVIEWED_AGGREGATE_ARTIFACT_NAME,
    REVIEWED_EVIDENCE_FINGERPRINT,
    REVIEWED_MODEL_HEAD_SHA,
    REVIEWED_MODEL_RUN_ID,
    validate_reviewed_regime_utility_model_result,
)


def _run() -> dict[str, object]:
    return {
        "id": REVIEWED_MODEL_RUN_ID,
        "name": "phase8a-exp049-regime-utility-model-training",
        "path": (
            ".github/workflows/"
            "phase8a-exp049-regime-utility-model-training.yml"
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
            "exp049-regime-utility-model-cell-results-"
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
        "stage": "REGIME_UTILITY_MODEL_RESULT_REVIEW_REQUIRED",
        "regime_utility_model_terminal_reviewed": True,
        "regime_utility_model_result_review_decision": "DEC-136",
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": 1,
        "reviewed_model_run_conclusion": "success",
        "persisted_cell_artifact_count": 9,
        "aggregate_artifact_present": True,
        "regime_utility_model_result_evidence_verified": True,
        "verified_cell_count": 18,
        "verified_regressor_count": 108,
        "selected_cell_count": 0,
        "no_regime_utility_stable_model_challenger_count": 18,
        "validation_pass_cell_count": 0,
        "holdout_pass_cell_count": 0,
        "aggregate_selection_pass_variant_count": 8,
        "stable_selection_pass_variant_count": 0,
        "unavailable_budget_variant_count": 31,
        "utility_eligible_selection_row_count": 14158,
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


class Exp049ResultDecisionTests(unittest.TestCase):
    @patch(
        "fmp.market_learning."
        "model_successor_regime_utility_result_decision."
        "validate_regime_utility_model_terminal_review"
    )
    def test_exact_review_closes_without_stable_candidate(
        self,
        terminal_review,
    ) -> None:
        terminal_review.return_value = _terminal_review()

        report = validate_reviewed_regime_utility_model_result(
            run=_run(),
            jobs_payload={"jobs": []},
            artifacts_payload=_artifacts(),
            aggregate_evidence={"fixture": True},
        )

        self.assertEqual(
            report["regime_utility_model_result_decision"],
            REGIME_UTILITY_MODEL_RESULT_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "REGIME_UTILITY_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER",
        )
        self.assertEqual(
            report["accepted_model_candidate_count"],
            0,
        )
        self.assertEqual(report["selected_cell_count"], 0)
        self.assertEqual(
            report[
                "no_regime_utility_stable_model_challenger_count"
            ],
            18,
        )
        self.assertEqual(
            report["verified_regressor_count"],
            108,
        )
        self.assertEqual(
            report["aggregate_selection_pass_variant_count"],
            8,
        )
        self.assertEqual(
            report["stable_selection_pass_variant_count"],
            0,
        )
        self.assertEqual(
            report["unavailable_budget_variant_count"],
            31,
        )
        self.assertEqual(
            report["utility_eligible_selection_row_count"],
            14158,
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
            validate_reviewed_regime_utility_model_result(
                run=run,
                jobs_payload={},
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
            validate_reviewed_regime_utility_model_result(
                run=_run(),
                jobs_payload={},
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
            validate_reviewed_regime_utility_model_result(
                run=_run(),
                jobs_payload={},
                artifacts_payload=artifacts,
                aggregate_evidence={},
            )

    @patch(
        "fmp.market_learning."
        "model_successor_regime_utility_result_decision."
        "validate_regime_utility_model_terminal_review"
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
            validate_reviewed_regime_utility_model_result(
                run=_run(),
                jobs_payload={},
                artifacts_payload=_artifacts(),
                aggregate_evidence={"fixture": True},
            )


if __name__ == "__main__":
    unittest.main()
