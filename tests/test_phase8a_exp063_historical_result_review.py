from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp063_historical_result_review import (
    AGGREGATE_ARTIFACT_DIGEST,
    AGGREGATE_ARTIFACT_ID,
    AGGREGATE_EVIDENCE_FINGERPRINT,
    AGGREGATE_RAW_JSON_SHA256,
    CLASSIFICATION,
    PERSISTENCE_FROZEN_COUNT,
    PERSISTENCE_SHORTLIST_COUNT,
    RUN_HEAD_SHA,
    RUN_ID,
    STAGE,
    TOTAL_DIRECTIONAL_HYPOTHESES,
    TOTAL_QUALIFYING_DIRECTIONAL_HYPOTHESES,
    historical_result_review_payload,
    review_cell_evidence,
    validate_terminal_run,
)


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _cell(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> dict[str, object]:
    value: dict[str, object] = {
        "cell": {
            "symbol": symbol,
            "timeframe": timeframe,
            "horizon_minutes": horizon,
        },
        "persistence": {
            "enumerated_pattern_count": 2075,
            "directional_hypothesis_count": 4150,
            "qualifying_directional_hypothesis_count": 0,
            "deduplicated_directional_hypothesis_count": 0,
            "shortlist": [],
            "frozen_pattern_fingerprints": [],
        },
    }
    value["evidence_fingerprint"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


class Exp063HistoricalResultReviewTests(unittest.TestCase):
    def test_terminal_run_and_artifact_shape_is_exact(self) -> None:
        run = {
            "id": RUN_ID,
            "name": "phase8a-exp063-persistence",
            "path": ".github/workflows/phase8a-exp063-persistence.yml",
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": RUN_HEAD_SHA,
            "run_number": 1,
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "success",
        }
        jobs = {
            "jobs": [
                {
                    "name": "exp063-preflight"
                    if index == 0
                    else (
                        "exp063-aggregate"
                        if index == 19
                        else f"exp063-cell-{index}"
                    ),
                    "status": "completed",
                    "conclusion": "success",
                }
                for index in range(20)
            ]
        }
        artifacts = {
            "artifacts": [
                {
                    "id": AGGREGATE_ARTIFACT_ID,
                    "name": (
                        "phase8a-exp063-aggregate-"
                        "6b106e4514f6ca3f06c677aab66fb04eb37ad881"
                    ),
                    "digest": AGGREGATE_ARTIFACT_DIGEST,
                    "expired": False,
                },
                *[
                    {
                        "id": 2000 + index,
                        "name": f"cell-artifact-{index}",
                        "digest": "sha256:" + "a" * 64,
                        "expired": False,
                    }
                    for index in range(19)
                ],
            ]
        }

        review = validate_terminal_run(run, jobs, artifacts)

        self.assertTrue(review["run_verified"])
        self.assertEqual(review["job_count"], 20)
        self.assertEqual(review["artifact_count"], 20)

    def test_all_18_cells_have_zero_qualifying_hypotheses(self) -> None:
        cells = [
            _cell(symbol, timeframe, horizon)
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
            for horizon in (60, 240)
        ]

        review = review_cell_evidence(cells)

        self.assertEqual(review["verified_cell_count"], 18)
        self.assertEqual(review["total_enumerated_patterns"], 37350)
        self.assertEqual(
            review["total_directional_hypotheses"],
            TOTAL_DIRECTIONAL_HYPOTHESES,
        )
        self.assertEqual(
            review["total_qualifying_directional_hypotheses"],
            TOTAL_QUALIFYING_DIRECTIONAL_HYPOTHESES,
        )
        self.assertEqual(review["total_deduplicated_directional_hypotheses"], 0)

    def test_terminal_review_freezes_negative_result_and_all_locks(self) -> None:
        payload = historical_result_review_payload()

        self.assertEqual(payload["stage"], STAGE)
        self.assertEqual(payload["classification"], CLASSIFICATION)
        self.assertEqual(payload["run_id"], RUN_ID)
        self.assertEqual(payload["run_head_sha"], RUN_HEAD_SHA)
        self.assertEqual(payload["run_number"], 1)
        self.assertEqual(payload["run_attempt"], 1)
        self.assertEqual(payload["run_conclusion"], "success")
        self.assertEqual(payload["job_count"], 20)
        self.assertEqual(payload["artifact_count"], 20)
        self.assertEqual(
            payload["aggregate_raw_json_sha256"],
            AGGREGATE_RAW_JSON_SHA256,
        )
        self.assertEqual(
            payload["aggregate_evidence_fingerprint"],
            AGGREGATE_EVIDENCE_FINGERPRINT,
        )
        self.assertEqual(payload["verified_cell_count"], 18)
        self.assertEqual(payload["total_enumerated_patterns"], 37350)
        self.assertEqual(payload["total_directional_hypotheses"], 74700)
        self.assertEqual(payload["total_qualifying_directional_hypotheses"], 0)
        self.assertEqual(payload["persistence_shortlist_count"], PERSISTENCE_SHORTLIST_COUNT)
        self.assertEqual(payload["persistence_frozen_count"], PERSISTENCE_FROZEN_COUNT)
        self.assertFalse(payload["untouched_oos"])
        self.assertFalse(payload["reserved_robustness_opened"])

        for field in (
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(payload[field], field)

        self.assertEqual(
            payload["next_gate"],
            "EXPLICIT_POST_EXP063_RESEARCH_DIRECTION_DECISION",
        )

    def test_result_is_not_reinterpreted_as_validation_or_strategy(self) -> None:
        payload = historical_result_review_payload()

        self.assertEqual(
            payload["evidence_label"],
            "RETROSPECTIVE_ALREADY_SEEN",
        )
        self.assertEqual(payload["persistence_shortlist_count"], 0)
        self.assertEqual(payload["persistence_frozen_count"], 0)
        self.assertFalse(payload["candidate_compilation_authorized"])
        self.assertFalse(payload["trading_authorized"])


if __name__ == "__main__":
    unittest.main()
