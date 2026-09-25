from __future__ import annotations

from unittest.mock import patch
import unittest

from fmp.market_learning.model_successor_fit_temporal_feature_support_utility_result_decision import (
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_DECISION,
    REVIEWED_AGGREGATE_ARTIFACT_DIGEST,
    REVIEWED_AGGREGATE_ARTIFACT_ID,
    REVIEWED_AGGREGATE_ARTIFACT_NAME,
    REVIEWED_AGGREGATE_PASS_VARIANTS,
    REVIEWED_EVIDENCE_FINGERPRINT,
    REVIEWED_MODEL_HEAD_SHA,
    REVIEWED_MODEL_RUN_ID,
    validate_reviewed_fit_temporal_feature_support_utility_model_result,
)


def _run() -> dict[str, object]:
    return {
        "id": REVIEWED_MODEL_RUN_ID,
        "head_sha": REVIEWED_MODEL_HEAD_SHA,
        "run_attempt": 1,
        "conclusion": "success",
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": REVIEWED_AGGREGATE_ARTIFACT_ID,
                "name": REVIEWED_AGGREGATE_ARTIFACT_NAME,
                "digest": REVIEWED_AGGREGATE_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


def _aggregate_evidence() -> dict[str, object]:
    grouped: dict[
        tuple[str, str, int],
        list[int],
    ] = {}
    for symbol, timeframe, horizon, budget in (
        REVIEWED_AGGREGATE_PASS_VARIANTS
    ):
        grouped.setdefault(
            (symbol, timeframe, horizon),
            [],
        ).append(budget)

    cells: list[dict[str, object]] = []
    for (symbol, timeframe, horizon), budgets in grouped.items():
        cells.append(
            {
                "cell": {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "horizon_minutes": horizon,
                },
                "selection": {
                    "variants": [
                        {
                            "candidate_budget_anchor": budget,
                            "aggregate_selection_gate_passed": True,
                        }
                        for budget in budgets
                    ]
                },
            }
        )
    return {"cells": cells}


def _terminal_review() -> dict[str, object]:
    return {
        "stage": (
            "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_"
            "RESULT_REVIEW_REQUIRED"
        ),
        "fit_temporal_feature_support_utility_model_terminal_reviewed": True,
        "fit_temporal_feature_support_utility_model_result_review_decision": (
            "DEC-178"
        ),
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": 1,
        "reviewed_model_run_conclusion": "success",
        "persisted_cell_artifact_count": 9,
        "aggregate_artifact_present": True,
        "fit_temporal_feature_support_utility_model_result_evidence_verified": (
            True
        ),
        "verified_cell_count": 18,
        "verified_regressor_count": 108,
        "verified_pooled_calibration_reference_count": 108,
        "verified_fit_temporal_support_reference_count": 432,
        "verified_fit_temporal_feature_support_reference_count": 216,
        "selected_cell_count": 0,
        "no_fit_temporal_feature_support_utility_stable_model_challenger_count": (
            18
        ),
        "validation_pass_cell_count": 0,
        "holdout_pass_cell_count": 0,
        "aggregate_selection_pass_variant_count": 10,
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


class Exp053ResultDecisionTests(unittest.TestCase):
    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_feature_support_utility_result_decision."
        "validate_fit_temporal_feature_support_utility_model_terminal_review"
    )
    def test_exact_review_closes_without_stable_candidate(
        self,
        terminal_review,
    ) -> None:
        terminal_review.return_value = _terminal_review()
        report = (
            validate_reviewed_fit_temporal_feature_support_utility_model_result(
                run=_run(),
                jobs_payload={"jobs": []},
                artifacts_payload=_artifacts(),
                aggregate_evidence=_aggregate_evidence(),
            )
        )

        self.assertEqual(
            report[
                "fit_temporal_feature_support_utility_model_result_decision"
            ],
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_DECISION,
        )
        self.assertEqual(
            report["stage"],
            (
                "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_"
                "REVIEWED_NO_STABLE_CHALLENGER"
            ),
        )
        self.assertEqual(report["accepted_model_candidate_count"], 0)
        self.assertEqual(report["verified_regressor_count"], 108)
        self.assertEqual(
            report["verified_pooled_calibration_reference_count"],
            108,
        )
        self.assertEqual(
            report["verified_fit_temporal_support_reference_count"],
            432,
        )
        self.assertEqual(
            report[
                "verified_fit_temporal_feature_support_reference_count"
            ],
            216,
        )
        self.assertEqual(
            report["aggregate_selection_pass_variant_count"],
            10,
        )
        self.assertEqual(
            report["stable_selection_pass_variant_count"],
            0,
        )
        self.assertEqual(
            report["reviewed_aggregate_pass_variants"],
            [
                list(value)
                for value in REVIEWED_AGGREGATE_PASS_VARIANTS
            ],
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
        with self.assertRaisesRegex(
            ValueError,
            "run id mismatch",
        ):
            validate_reviewed_fit_temporal_feature_support_utility_model_result(
                run=run,
                jobs_payload={},
                artifacts_payload=_artifacts(),
                aggregate_evidence=_aggregate_evidence(),
            )

    def test_wrong_aggregate_digest_fails_closed(self) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows[0] = {
            **rows[0],
            "digest": "sha256:" + "0" * 64,
        }
        with self.assertRaisesRegex(
            ValueError,
            "artifact digest mismatch",
        ):
            validate_reviewed_fit_temporal_feature_support_utility_model_result(
                run=_run(),
                jobs_payload={},
                artifacts_payload=artifacts,
                aggregate_evidence=_aggregate_evidence(),
            )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_feature_support_utility_result_decision."
        "validate_fit_temporal_feature_support_utility_model_terminal_review"
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
            validate_reviewed_fit_temporal_feature_support_utility_model_result(
                run=_run(),
                jobs_payload={},
                artifacts_payload=_artifacts(),
                aggregate_evidence=_aggregate_evidence(),
            )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_feature_support_utility_result_decision."
        "validate_fit_temporal_feature_support_utility_model_terminal_review"
    )
    def test_aggregate_pass_inventory_drift_fails_closed(
        self,
        terminal_review,
    ) -> None:
        terminal_review.return_value = _terminal_review()
        drifted = _aggregate_evidence()
        cells = drifted["cells"]
        assert isinstance(cells, list)
        selection = cells[0]["selection"]
        assert isinstance(selection, dict)
        variants = selection["variants"]
        assert isinstance(variants, list)
        variants.pop()

        with self.assertRaisesRegex(
            ValueError,
            "aggregate pass inventory mismatch",
        ):
            validate_reviewed_fit_temporal_feature_support_utility_model_result(
                run=_run(),
                jobs_payload={},
                artifacts_payload=_artifacts(),
                aggregate_evidence=drifted,
            )


if __name__ == "__main__":
    unittest.main()
