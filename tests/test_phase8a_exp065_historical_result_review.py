from __future__ import annotations

import unittest
from unittest.mock import patch

from fmp.discovery.exp065_historical_result_review import (
    AGGREGATE_ARTIFACT_DIGEST,
    AGGREGATE_ARTIFACT_ID,
    AGGREGATE_EVIDENCE_FINGERPRINT,
    AGGREGATE_RAW_JSON_SHA256,
    CLASSIFICATION,
    DISCOVERY_FIRST_METHOD_REJECTED,
    EXPECTED_CELL_EVIDENCE_FINGERPRINTS,
    NEGATIVE_RESULT_SCOPE,
    NEXT_GATE,
    RUN_HEAD_SHA,
    RUN_ID,
    STAGE,
    TOTAL_EVALUABLE_HYPOTHESES,
    TOTAL_HYPOTHESES,
    TOTAL_QUALIFYING_HYPOTHESES,
    historical_result_review_payload,
    review_frozen_success_evidence,
    validate_terminal_run,
)


def _run() -> dict[str, object]:
    return {
        "id": RUN_ID,
        "name": "phase8a-exp065-pairwise-interaction",
        "path": ".github/workflows/phase8a-exp065-pairwise-interaction.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": RUN_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    names = [
        "exp065-preflight",
        *[
            f"exp065-cell-{symbol}-{timeframe}-{horizon}m"
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
            for horizon in (60, 240)
        ],
        "exp065-aggregate",
    ]
    return {
        "jobs": [
            {"name": name, "status": "completed", "conclusion": "success"}
            for name in names
        ]
    }


def _artifacts() -> dict[str, object]:
    names = [
        f"phase8a-exp065-preflight-{RUN_HEAD_SHA}",
        *[
            f"phase8a-exp065-cell-{symbol}-{timeframe}-{horizon}m-{RUN_HEAD_SHA}"
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
            for horizon in (60, 240)
        ],
        f"phase8a-exp065-aggregate-{RUN_HEAD_SHA}",
    ]
    rows = []
    for index, name in enumerate(names, start=1):
        rows.append(
            {
                "id": AGGREGATE_ARTIFACT_ID if "-aggregate-" in name else index,
                "name": name,
                "digest": (
                    AGGREGATE_ARTIFACT_DIGEST
                    if "-aggregate-" in name
                    else "sha256:" + f"{index:064x}"[-64:]
                ),
                "expired": False,
            }
        )
    return {"artifacts": rows}


def _cells() -> list[dict[str, object]]:
    values: list[dict[str, object]] = []
    for identity, fingerprint in EXPECTED_CELL_EVIDENCE_FINGERPRINTS.items():
        symbol, timeframe, horizon = identity
        values.append(
            {
                "cell": {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "horizon_minutes": horizon,
                },
                "evidence_fingerprint": fingerprint,
                "pairwise_interaction": {
                    "hypothesis_count": 760,
                    "evaluable_hypothesis_count": 760,
                    "qualifying_hypothesis_count": 0,
                    "deduplicated_hypothesis_count": 0,
                    "shortlist": [],
                    "frozen_hypothesis_fingerprints": [],
                    "output_kind": (
                        "RETROSPECTIVE_PAIRWISE_INTERACTION_HYPOTHESIS_NOT_VALIDATED"
                    ),
                },
            }
        )
    return values


class Exp065HistoricalResultReviewTests(unittest.TestCase):
    def test_terminal_run_freezes_exact_aggregate_artifact(self) -> None:
        review = validate_terminal_run(_run(), _jobs(), _artifacts())
        self.assertTrue(review["run_verified"])
        self.assertEqual(review["job_count"], 20)
        self.assertEqual(review["artifact_count"], 20)
        self.assertEqual(review["aggregate_artifact_id"], AGGREGATE_ARTIFACT_ID)
        self.assertEqual(review["aggregate_artifact_digest"], AGGREGATE_ARTIFACT_DIGEST)

    def test_frozen_success_evidence_is_exact_zero_qualifier_result(self) -> None:
        dec467 = {
            "evidence_verified": True,
            "result_state": "ZERO_PAIRWISE_INTERACTION_QUALIFIERS",
            "aggregate_evidence_fingerprint": AGGREGATE_EVIDENCE_FINGERPRINT,
            "protocol_fingerprint": (
                "437e86d53094a52445b02956498b6b1bafcc91575efad1661dddf8aefaf0c4f0"
            ),
            "feature_evidence_fingerprint": (
                "1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815"
            ),
            "outcome_evidence_fingerprint": (
                "b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117"
            ),
            "verified_cell_count": 18,
            "total_hypotheses": 13680,
            "total_evaluable_hypotheses": 13680,
            "total_qualifying_hypotheses": 0,
            "total_deduplicated_hypotheses": 0,
            "pairwise_interaction_shortlist_count": 0,
            "pairwise_interaction_frozen_count": 0,
            "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
            "untouched_oos": False,
            "reserved_robustness_opened": False,
        }
        with patch(
            "fmp.discovery.exp065_historical_result_review.review_dec467_success_evidence",
            return_value=dec467,
        ):
            review = review_frozen_success_evidence(
                aggregate={},
                cell_evidence=_cells(),
            )
        self.assertEqual(review["classification"], CLASSIFICATION)
        self.assertEqual(review["total_hypotheses"], TOTAL_HYPOTHESES)
        self.assertEqual(
            review["total_evaluable_hypotheses"],
            TOTAL_EVALUABLE_HYPOTHESES,
        )
        self.assertEqual(
            review["total_qualifying_hypotheses"],
            TOTAL_QUALIFYING_HYPOTHESES,
        )
        self.assertFalse(review["discovery_first_method_rejected"])

    def test_cell_fingerprint_identity_drift_fails_closed(self) -> None:
        dec467 = {
            "evidence_verified": True,
            "result_state": "ZERO_PAIRWISE_INTERACTION_QUALIFIERS",
            "aggregate_evidence_fingerprint": AGGREGATE_EVIDENCE_FINGERPRINT,
            "protocol_fingerprint": (
                "437e86d53094a52445b02956498b6b1bafcc91575efad1661dddf8aefaf0c4f0"
            ),
            "feature_evidence_fingerprint": (
                "1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815"
            ),
            "outcome_evidence_fingerprint": (
                "b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117"
            ),
            "verified_cell_count": 18,
            "total_hypotheses": 13680,
            "total_evaluable_hypotheses": 13680,
            "total_qualifying_hypotheses": 0,
            "total_deduplicated_hypotheses": 0,
            "pairwise_interaction_shortlist_count": 0,
            "pairwise_interaction_frozen_count": 0,
            "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
            "untouched_oos": False,
            "reserved_robustness_opened": False,
        }
        cells = _cells()
        cells[0]["evidence_fingerprint"] = "0" * 64
        with patch(
            "fmp.discovery.exp065_historical_result_review.review_dec467_success_evidence",
            return_value=dec467,
        ):
            with self.assertRaisesRegex(ValueError, "fingerprint identity drift"):
                review_frozen_success_evidence(aggregate={}, cell_evidence=cells)

    def test_payload_preserves_discovery_first_scope_and_all_locks(self) -> None:
        payload = historical_result_review_payload()
        self.assertEqual(payload["stage"], STAGE)
        self.assertEqual(payload["classification"], CLASSIFICATION)
        self.assertEqual(payload["result_state"], "ZERO_PAIRWISE_INTERACTION_QUALIFIERS")
        self.assertEqual(payload["negative_result_scope"], NEGATIVE_RESULT_SCOPE)
        self.assertFalse(payload["discovery_first_method_rejected"])
        self.assertEqual(payload["run_id"], RUN_ID)
        self.assertEqual(payload["aggregate_raw_json_sha256"], AGGREGATE_RAW_JSON_SHA256)
        self.assertEqual(payload["aggregate_evidence_fingerprint"], AGGREGATE_EVIDENCE_FINGERPRINT)
        self.assertEqual(payload["total_hypotheses"], 13680)
        self.assertEqual(payload["total_evaluable_hypotheses"], 13680)
        self.assertEqual(payload["total_qualifying_hypotheses"], 0)
        self.assertEqual(payload["pairwise_interaction_shortlist_count"], 0)
        self.assertEqual(payload["pairwise_interaction_frozen_count"], 0)
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
        self.assertEqual(payload["next_gate"], NEXT_GATE)


if __name__ == "__main__":
    unittest.main()
