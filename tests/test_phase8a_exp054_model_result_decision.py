from __future__ import annotations

import hashlib
import json
from unittest.mock import patch
import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_bound_utility_result_decision import (
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_DECISION,
    REVIEWED_AGGREGATE_ARTIFACT_DIGEST,
    REVIEWED_AGGREGATE_ARTIFACT_ID,
    REVIEWED_AGGREGATE_ARTIFACT_NAME,
    REVIEWED_AGGREGATE_PASS_VARIANTS,
    REVIEWED_EVIDENCE_FINGERPRINT,
    REVIEWED_MODEL_HEAD_SHA,
    REVIEWED_MODEL_RUN_ID,
    validate_reviewed_fit_temporal_residual_bound_utility_model_result,
)


CELL_ELIGIBLE_ROWS = {
    ("EURUSD", "15m", 60): 233,
    ("EURUSD", "15m", 240): 2759,
    ("EURUSD", "1h", 60): 79,
    ("EURUSD", "1h", 240): 697,
    ("EURUSD", "5m", 60): 769,
    ("EURUSD", "5m", 240): 7208,
    ("GBPUSD", "15m", 60): 139,
    ("GBPUSD", "15m", 240): 1656,
    ("GBPUSD", "1h", 60): 65,
    ("GBPUSD", "1h", 240): 197,
    ("GBPUSD", "5m", 60): 262,
    ("GBPUSD", "5m", 240): 3210,
    ("USDJPY", "15m", 60): 459,
    ("USDJPY", "15m", 240): 1975,
    ("USDJPY", "1h", 60): 139,
    ("USDJPY", "1h", 240): 432,
    ("USDJPY", "5m", 60): 1122,
    ("USDJPY", "5m", 240): 4991,
}


def _canonical_hash(value: object) -> str:
    payload = (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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


def _cell(
    symbol: str,
    timeframe: str,
    horizon: int,
    eligible_rows: int,
) -> dict[str, object]:
    variants: list[dict[str, object]] = []
    for budget in (250, 500, 1000):
        aggregate_passed = (
            (symbol, timeframe, horizon, budget)
            in REVIEWED_AGGREGATE_PASS_VARIANTS
        )
        variants.append(
            {
                "candidate_budget_anchor": budget,
                "status": (
                    "AVAILABLE"
                    if eligible_rows >= budget
                    else "BUDGET_UNAVAILABLE"
                ),
                "eligible_selection_row_count": eligible_rows,
                "aggregate_selection_gate_passed": aggregate_passed,
                "selection_gate_passed": False,
            }
        )

    row: dict[str, object] = {
        "cell": {
            "symbol": symbol,
            "timeframe": timeframe,
            "horizon_minutes": horizon,
        },
        "fit": {
            "regressor_count": 6,
            "calibration_reference_count": 6,
            "fit_temporal_support_reference_count": 24,
            "fit_temporal_feature_support_reference_count": 12,
            "fit_temporal_residual_reference_count": 24,
        },
        "selection": {
            "status": (
                "NO_FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_"
                "STABLE_MODEL_CHALLENGER"
            ),
            "selected_variant": None,
            "variants": variants,
        },
        "validation": {"status": "LOCKED_NO_SELECTION"},
        "retrospective_holdout": {"status": "LOCKED_NO_SELECTION"},
    }
    row["result_fingerprint"] = _canonical_hash(row)
    return row


def _aggregate_evidence() -> dict[str, object]:
    cells = [
        _cell(symbol, timeframe, horizon, eligible_rows)
        for (symbol, timeframe, horizon), eligible_rows
        in CELL_ELIGIBLE_ROWS.items()
    ]
    return {"cells": cells}


def _terminal_review() -> dict[str, object]:
    return {
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_"
            "RESULT_REVIEW_REQUIRED"
        ),
        "fit_temporal_residual_bound_utility_model_terminal_reviewed": True,
        "fit_temporal_residual_bound_utility_model_result_review_decision": (
            "DEC-190"
        ),
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": 1,
        "reviewed_model_run_conclusion": "success",
        "persisted_cell_artifact_count": 9,
        "aggregate_artifact_present": True,
        "fit_temporal_residual_bound_utility_model_result_evidence_verified": (
            True
        ),
        "verified_cell_count": 18,
        "verified_fit_temporal_residual_reference_count": 432,
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


class Exp054ResultDecisionTests(unittest.TestCase):
    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_bound_utility_result_decision."
        "validate_fit_temporal_residual_bound_utility_model_terminal_review"
    )
    def test_exact_review_closes_without_stable_candidate(
        self,
        terminal_review,
    ) -> None:
        terminal_review.return_value = _terminal_review()
        report = (
            validate_reviewed_fit_temporal_residual_bound_utility_model_result(
                run=_run(),
                jobs_payload={"jobs": []},
                artifacts_payload=_artifacts(),
                aggregate_evidence=_aggregate_evidence(),
            )
        )

        self.assertEqual(
            report[
                "fit_temporal_residual_bound_utility_model_result_decision"
            ],
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_DECISION,
        )
        self.assertEqual(
            report["stage"],
            (
                "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_"
                "REVIEWED_NO_STABLE_CHALLENGER"
            ),
        )
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
            report["verified_fit_temporal_residual_reference_count"],
            432,
        )
        self.assertEqual(report["total_variant_count"], 54)
        self.assertEqual(report["available_budget_variant_count"], 28)
        self.assertEqual(report["unavailable_budget_variant_count"], 26)
        self.assertEqual(
            report["utility_eligible_selection_row_count"],
            26392,
        )
        self.assertEqual(
            report["aggregate_selection_pass_variant_count"],
            2,
        )
        self.assertEqual(
            report["stable_selection_pass_variant_count"],
            0,
        )
        self.assertEqual(report["selected_cell_count"], 0)
        self.assertEqual(report["accepted_model_candidate_count"], 0)
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
        with self.assertRaisesRegex(ValueError, "run id mismatch"):
            validate_reviewed_fit_temporal_residual_bound_utility_model_result(
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
            validate_reviewed_fit_temporal_residual_bound_utility_model_result(
                run=_run(),
                jobs_payload={},
                artifacts_payload=artifacts,
                aggregate_evidence=_aggregate_evidence(),
            )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_bound_utility_result_decision."
        "validate_fit_temporal_residual_bound_utility_model_terminal_review"
    )
    def test_summary_drift_fails_closed(
        self,
        terminal_review,
    ) -> None:
        terminal_review.return_value = _terminal_review()
        evidence = _aggregate_evidence()
        cells = evidence["cells"]
        assert isinstance(cells, list)
        fit = cells[0]["fit"]
        assert isinstance(fit, dict)
        fit["regressor_count"] = 5
        supplied = dict(cells[0])
        supplied.pop("result_fingerprint")
        cells[0]["result_fingerprint"] = _canonical_hash(supplied)

        with self.assertRaisesRegex(
            ValueError,
            "verified_regressor_count mismatch",
        ):
            validate_reviewed_fit_temporal_residual_bound_utility_model_result(
                run=_run(),
                jobs_payload={},
                artifacts_payload=_artifacts(),
                aggregate_evidence=evidence,
            )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_bound_utility_result_decision."
        "validate_fit_temporal_residual_bound_utility_model_terminal_review"
    )
    def test_aggregate_pass_inventory_drift_fails_closed(
        self,
        terminal_review,
    ) -> None:
        terminal_review.return_value = _terminal_review()
        evidence = _aggregate_evidence()
        cells = evidence["cells"]
        assert isinstance(cells, list)

        target = next(
            row
            for row in cells
            if row["cell"] == {
                "symbol": "USDJPY",
                "timeframe": "5m",
                "horizon_minutes": 60,
            }
        )
        selection = target["selection"]
        assert isinstance(selection, dict)
        variants = selection["variants"]
        assert isinstance(variants, list)
        variants[0]["aggregate_selection_gate_passed"] = False
        supplied = dict(target)
        supplied.pop("result_fingerprint")
        target["result_fingerprint"] = _canonical_hash(supplied)

        with self.assertRaisesRegex(
            ValueError,
            "aggregate_selection_pass_variant_count mismatch",
        ):
            validate_reviewed_fit_temporal_residual_bound_utility_model_result(
                run=_run(),
                jobs_payload={},
                artifacts_payload=_artifacts(),
                aggregate_evidence=evidence,
            )

    @patch(
        "fmp.market_learning."
        "model_successor_fit_temporal_residual_bound_utility_result_decision."
        "validate_fit_temporal_residual_bound_utility_model_terminal_review"
    )
    def test_cell_fingerprint_drift_fails_closed(
        self,
        terminal_review,
    ) -> None:
        terminal_review.return_value = _terminal_review()
        evidence = _aggregate_evidence()
        cells = evidence["cells"]
        assert isinstance(cells, list)
        cells[0]["result_fingerprint"] = "0" * 64

        with self.assertRaisesRegex(
            ValueError,
            "cell result fingerprint mismatch",
        ):
            validate_reviewed_fit_temporal_residual_bound_utility_model_result(
                run=_run(),
                jobs_payload={},
                artifacts_payload=_artifacts(),
                aggregate_evidence=evidence,
            )


if __name__ == "__main__":
    unittest.main()
