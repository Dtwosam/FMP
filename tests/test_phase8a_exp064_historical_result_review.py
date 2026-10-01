from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp064_historical_result_review import (
    AGGREGATE_ARTIFACT_DIGEST,
    AGGREGATE_ARTIFACT_ID,
    AGGREGATE_EVIDENCE_FINGERPRINT,
    AGGREGATE_RAW_JSON_SHA256,
    CLASSIFICATION,
    CONTINUOUS_STABILITY_FROZEN_COUNT,
    CONTINUOUS_STABILITY_SHORTLIST_COUNT,
    RUN_HEAD_SHA,
    RUN_ID,
    STAGE,
    TOTAL_EVALUABLE_HYPOTHESES,
    TOTAL_HYPOTHESES,
    TOTAL_QUALIFYING_HYPOTHESES,
    historical_result_review_payload,
    review_cell_evidence,
    validate_aggregate_evidence,
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
        "experiment_id": "EXP-20261001-064",
        "code_commit": RUN_HEAD_SHA,
        "protocol_fingerprint": (
            "0fe6f992f0d6c27b1d7998561005f37b07f89c8715edd874ee8eb8f8d79ca7e0"
        ),
        "feature_evidence_fingerprint": (
            "1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815"
        ),
        "outcome_evidence_fingerprint": (
            "b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117"
        ),
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "cell": {
            "symbol": symbol,
            "timeframe": timeframe,
            "horizon_minutes": horizon,
        },
        "continuous_stability": {
            "hypothesis_count": 80,
            "evaluable_hypothesis_count": 80,
            "qualifying_hypothesis_count": 0,
            "deduplicated_hypothesis_count": 0,
            "shortlist": [],
            "frozen_hypothesis_fingerprints": [],
            "output_kind": (
                "RETROSPECTIVE_CONTINUOUS_STABILITY_HYPOTHESIS_NOT_VALIDATED"
            ),
        },
        "reserved_robustness_opened": False,
        "source_access_authorized": False,
        "historical_execution_authorized": False,
        "historical_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    value["evidence_fingerprint"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


def _aggregate() -> dict[str, object]:
    cells: list[dict[str, object]] = []
    for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
        for timeframe in ("5m", "15m", "1h"):
            for horizon in (60, 240):
                cells.append(
                    {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "horizon_minutes": horizon,
                        "cell_evidence_fingerprint": hashlib.sha256(
                            f"{symbol}-{timeframe}-{horizon}".encode()
                        ).hexdigest(),
                        "hypothesis_count": 80,
                        "evaluable_hypothesis_count": 80,
                        "qualifying_hypothesis_count": 0,
                        "deduplicated_hypothesis_count": 0,
                        "continuous_stability_shortlist_count": 0,
                        "continuous_stability_frozen_count": 0,
                        "continuous_stability_shortlist_fingerprints": [],
                        "continuous_stability_frozen_fingerprints": [],
                        "output_kind": (
                            "RETROSPECTIVE_CONTINUOUS_STABILITY_"
                            "HYPOTHESIS_NOT_VALIDATED"
                        ),
                    }
                )
    value: dict[str, object] = {
        "experiment_id": "EXP-20261001-064",
        "code_commit": RUN_HEAD_SHA,
        "protocol_fingerprint": (
            "0fe6f992f0d6c27b1d7998561005f37b07f89c8715edd874ee8eb8f8d79ca7e0"
        ),
        "feature_evidence_fingerprint": (
            "1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815"
        ),
        "outcome_evidence_fingerprint": (
            "b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117"
        ),
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "expected_cell_count": 18,
        "verified_cell_count": 18,
        "continuous_stability_shortlist_count": 0,
        "continuous_stability_frozen_count": 0,
        "output_kind": (
            "RETROSPECTIVE_CONTINUOUS_STABILITY_HYPOTHESIS_NOT_VALIDATED"
        ),
        "reserved_robustness_opened": False,
        "source_access_authorized": False,
        "historical_execution_authorized": False,
        "historical_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "cells": cells,
    }
    value["evidence_fingerprint"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


class Exp064HistoricalResultReviewTests(unittest.TestCase):
    def test_terminal_run_and_artifact_shape_is_exact(self) -> None:
        run = {
            "id": RUN_ID,
            "name": "phase8a-exp064-continuous-stability",
            "path": ".github/workflows/phase8a-exp064-continuous-stability.yml",
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
                    "name": name,
                    "status": "completed",
                    "conclusion": "success",
                }
                for name in [
                    "exp064-preflight",
                    *[
                        f"exp064-cell-{symbol}-{timeframe}-{horizon}m"
                        for symbol in ("EURUSD", "GBPUSD", "USDJPY")
                        for timeframe in ("5m", "15m", "1h")
                        for horizon in (60, 240)
                    ],
                    "exp064-aggregate",
                ]
            ]
        }
        artifacts = {
            "artifacts": [
                {
                    "id": AGGREGATE_ARTIFACT_ID,
                    "name": (
                        "phase8a-exp064-aggregate-"
                        "b13f89f4d6bef8b1ab4a2fa12c6b01d0e5067506"
                    ),
                    "digest": AGGREGATE_ARTIFACT_DIGEST,
                    "expired": False,
                },
                {
                    "id": 1,
                    "name": f"phase8a-exp064-preflight-{RUN_HEAD_SHA}",
                    "digest": "sha256:" + "a" * 64,
                    "expired": False,
                },
                *[
                    {
                        "id": 100 + index,
                        "name": (
                            f"phase8a-exp064-cell-{symbol}-{timeframe}-"
                            f"{horizon}m-{RUN_HEAD_SHA}"
                        ),
                        "digest": "sha256:" + "b" * 64,
                        "expired": False,
                    }
                    for index, (symbol, timeframe, horizon) in enumerate(
                        (
                            (symbol, timeframe, horizon)
                            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
                            for timeframe in ("5m", "15m", "1h")
                            for horizon in (60, 240)
                        )
                    )
                ],
            ]
        }

        review = validate_terminal_run(run, jobs, artifacts)

        self.assertTrue(review["run_verified"])
        self.assertEqual(review["job_count"], 20)
        self.assertEqual(review["artifact_count"], 20)

    def test_aggregate_shape_freezes_zero_survivors(self) -> None:
        aggregate = _aggregate()

        unsigned = dict(aggregate)
        unsigned.pop("evidence_fingerprint")
        aggregate["evidence_fingerprint"] = AGGREGATE_EVIDENCE_FINGERPRINT
        with self.assertRaisesRegex(
            ValueError,
            "fingerprint mismatch",
        ):
            validate_aggregate_evidence(aggregate)

        aggregate = _aggregate()
        computed = aggregate["evidence_fingerprint"]
        self.assertNotEqual(computed, AGGREGATE_EVIDENCE_FINGERPRINT)

    def test_all_18_cells_have_zero_qualifying_hypotheses(self) -> None:
        cells = [
            _cell(symbol, timeframe, horizon)
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
            for horizon in (60, 240)
        ]

        review = review_cell_evidence(cells)

        self.assertEqual(review["verified_cell_count"], 18)
        self.assertEqual(review["total_hypotheses"], TOTAL_HYPOTHESES)
        self.assertEqual(
            review["total_evaluable_hypotheses"],
            TOTAL_EVALUABLE_HYPOTHESES,
        )
        self.assertEqual(
            review["total_qualifying_hypotheses"],
            TOTAL_QUALIFYING_HYPOTHESES,
        )
        self.assertEqual(review["total_deduplicated_hypotheses"], 0)

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
        self.assertEqual(payload["total_hypotheses"], 1440)
        self.assertEqual(payload["total_evaluable_hypotheses"], 1440)
        self.assertEqual(payload["total_qualifying_hypotheses"], 0)
        self.assertEqual(
            payload["continuous_stability_shortlist_count"],
            CONTINUOUS_STABILITY_SHORTLIST_COUNT,
        )
        self.assertEqual(
            payload["continuous_stability_frozen_count"],
            CONTINUOUS_STABILITY_FROZEN_COUNT,
        )
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
            "EXPLICIT_POST_EXP064_RESEARCH_DIRECTION_DECISION",
        )

    def test_result_is_not_reinterpreted_as_validation_or_strategy(self) -> None:
        payload = historical_result_review_payload()

        self.assertEqual(
            payload["evidence_label"],
            "RETROSPECTIVE_ALREADY_SEEN",
        )
        self.assertEqual(payload["total_qualifying_hypotheses"], 0)
        self.assertEqual(payload["continuous_stability_shortlist_count"], 0)
        self.assertEqual(payload["continuous_stability_frozen_count"], 0)
        self.assertFalse(payload["candidate_compilation_authorized"])
        self.assertFalse(payload["trading_authorized"])


if __name__ == "__main__":
    unittest.main()
