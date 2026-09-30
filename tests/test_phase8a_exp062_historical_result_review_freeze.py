from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_historical_result_content_review import (
    EXP062_AGGREGATE_ARTIFACT_DIGEST,
    EXP062_AGGREGATE_ARTIFACT_ID,
    EXP062_AGGREGATE_EVIDENCE_FINGERPRINT,
    EXP062_AGGREGATE_JSON_SHA256,
    EXP062_HISTORICAL_RUN_HEAD_SHA,
    EXP062_HISTORICAL_RUN_ID,
)
from fmp.discovery.exp062_historical_result_review_freeze import (
    DEC440_REVIEW_SOURCE_BLOB_SHA,
    EXP062_HISTORICAL_RESULT_REVIEW_FREEZE_DECISION,
    freeze_exp062_historical_result_review,
)
from fmp.discovery.exp062_run_contract import (
    EXP062_EXPERIMENT_ID,
    expected_aggregate_artifact_name,
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


def _reviewed() -> dict[str, object]:
    return {
        "decision": "DEC-440",
        "version": "fmp-exp062-historical-result-content-review-v1",
        "stage": (
            "EXP062_HISTORICAL_RESULT_CONTENT_REVIEWED_"
            "NO_VALIDATION_ACCEPTED"
        ),
        "experiment_id": EXP062_EXPERIMENT_ID,
        "terminal_review_decision": "DEC-334",
        "terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "historical_run_id": EXP062_HISTORICAL_RUN_ID,
        "historical_run_head_sha": EXP062_HISTORICAL_RUN_HEAD_SHA,
        "historical_run_number": 2,
        "historical_run_attempt": 1,
        "historical_run_conclusion": "success",
        "historical_result_slot_consumed": True,
        "aggregate_artifact_id": EXP062_AGGREGATE_ARTIFACT_ID,
        "aggregate_artifact_name": expected_aggregate_artifact_name(
            code_commit=EXP062_HISTORICAL_RUN_HEAD_SHA,
        ),
        "aggregate_artifact_digest": EXP062_AGGREGATE_ARTIFACT_DIGEST,
        "aggregate_json_sha256": EXP062_AGGREGATE_JSON_SHA256,
        "aggregate_evidence_fingerprint": (
            EXP062_AGGREGATE_EVIDENCE_FINGERPRINT
        ),
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "verified_cell_count": 18,
        "discovery_shortlist_count": 67,
        "confirmation_frozen_count": 11,
        "validation_accepted_count": 0,
        "aggregate_result_content_review_required": False,
        "historical_result_review_complete": True,
        "validation_accepted_candidates_present": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": "IMMUTABLE_HISTORICAL_RESULT_REVIEW_FREEZE",
    }


class Exp062HistoricalResultReviewFreezeTests(unittest.TestCase):
    def test_review_freezes_deterministically_without_authority(self) -> None:
        first = freeze_exp062_historical_result_review(_reviewed())
        second = freeze_exp062_historical_result_review(_reviewed())

        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_HISTORICAL_RESULT_REVIEW_FREEZE_DECISION,
        )
        self.assertEqual(
            first["stage"],
            "EXP062_HISTORICAL_RESULT_REVIEWED_AND_FROZEN_"
            "NO_VALIDATION_ACCEPTED",
        )
        self.assertEqual(
            first["source_review_blob_sha"],
            DEC440_REVIEW_SOURCE_BLOB_SHA,
        )
        self.assertTrue(first["historical_result_slot_consumed"])
        self.assertEqual(first["verified_cell_count"], 18)
        self.assertEqual(first["discovery_shortlist_count"], 67)
        self.assertEqual(first["confirmation_frozen_count"], 11)
        self.assertEqual(first["validation_accepted_count"], 0)
        self.assertFalse(first["validation_accepted_candidates_present"])
        self.assertFalse(first["candidate_compilation_authorized"])
        self.assertFalse(first["phase8b_authorized"])
        self.assertFalse(first["trading_authorized"])
        self.assertEqual(
            first["next_gate"],
            "EXPLICIT_POST_EXP062_RESEARCH_DIRECTION_DECISION",
        )

        unsigned = dict(first)
        fingerprint = unsigned.pop("freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_historical_identity_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["historical_run_id"] = 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result historical_run_id mismatch",
        ):
            freeze_exp062_historical_result_review(reviewed)

    def test_aggregate_hash_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["aggregate_json_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result aggregate_json_sha256 mismatch",
        ):
            freeze_exp062_historical_result_review(reviewed)

    def test_result_count_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["validation_accepted_count"] = 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result validation_accepted_count mismatch",
        ):
            freeze_exp062_historical_result_review(reviewed)

        reviewed = _reviewed()
        reviewed["confirmation_frozen_count"] = 10
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result confirmation_frozen_count mismatch",
        ):
            freeze_exp062_historical_result_review(reviewed)

    def test_downstream_authority_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["candidate_compilation_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "candidate_compilation_authorized must remain false",
        ):
            freeze_exp062_historical_result_review(reviewed)

        reviewed = _reviewed()
        reviewed["trading_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "trading_authorized must remain false",
        ):
            freeze_exp062_historical_result_review(reviewed)

    def test_review_must_be_complete_and_non_promoting(self) -> None:
        reviewed = _reviewed()
        reviewed["historical_result_review_complete"] = False
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result historical_result_review_complete mismatch",
        ):
            freeze_exp062_historical_result_review(reviewed)

        reviewed = _reviewed()
        reviewed["validation_accepted_candidates_present"] = True
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result validation_accepted_candidates_present mismatch",
        ):
            freeze_exp062_historical_result_review(reviewed)

    def test_malformed_digest_is_rejected_even_if_shape_is_bypassed(self) -> None:
        reviewed = _reviewed()
        reviewed["aggregate_artifact_digest"] = "sha256:not-a-digest"
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result aggregate_artifact_digest mismatch",
        ):
            freeze_exp062_historical_result_review(reviewed)


if __name__ == "__main__":
    unittest.main()
