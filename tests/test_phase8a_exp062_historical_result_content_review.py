from __future__ import annotations

from unittest.mock import patch
import unittest

from fmp.discovery.exp062_historical_result_content_review import (
    EXP062_AGGREGATE_ARTIFACT_DIGEST,
    EXP062_AGGREGATE_ARTIFACT_ID,
    EXP062_AGGREGATE_EVIDENCE_FINGERPRINT,
    EXP062_AGGREGATE_JSON_SHA256,
    EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION,
    EXP062_HISTORICAL_RUN_HEAD_SHA,
    EXP062_HISTORICAL_RUN_ID,
    review_exp062_historical_result,
)
from fmp.discovery.exp062_run_contract import expected_aggregate_artifact_name


def _terminal() -> dict[str, object]:
    return {
        "decision": "DEC-334",
        "version": "fmp-exp062-historical-terminal-review-contract-v1",
        "stage": "EXP062_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED",
        "historical_run_id": EXP062_HISTORICAL_RUN_ID,
        "historical_run_head_sha": EXP062_HISTORICAL_RUN_HEAD_SHA,
        "historical_run_number": 2,
        "historical_run_attempt": 1,
        "historical_run_conclusion": "success",
        "historical_result_slot_consumed": True,
        "historical_result_success_complete": True,
        "materialized_job_count": 20,
        "job_conclusion_counts": {"success": 20},
        "github_unexpanded_matrix_placeholder_present": False,
        "artifact_count": 20,
        "aggregate_result_content_review_required": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "trading_authorized": False,
    }


def _aggregate() -> dict[str, object]:
    return {
        "experiment_id": "EXP-20260927-062",
        "code_commit": EXP062_HISTORICAL_RUN_HEAD_SHA,
        "evidence_fingerprint": EXP062_AGGREGATE_EVIDENCE_FINGERPRINT,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "expected_cell_count": 18,
        "verified_cell_count": 18,
        "discovery_shortlist_count": 67,
        "confirmation_frozen_count": 11,
        "validation_accepted_count": 0,
        "untouched_oos": False,
        "reserved_robustness_opened": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": EXP062_AGGREGATE_ARTIFACT_ID,
                "name": expected_aggregate_artifact_name(
                    code_commit=EXP062_HISTORICAL_RUN_HEAD_SHA,
                ),
                "digest": EXP062_AGGREGATE_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


class Exp062HistoricalResultContentReviewTests(unittest.TestCase):
    def _review(
        self,
        *,
        terminal: dict[str, object] | None = None,
        aggregate: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        aggregate_json_sha256: str = EXP062_AGGREGATE_JSON_SHA256,
    ) -> dict[str, object]:
        terminal = _terminal() if terminal is None else terminal
        aggregate = _aggregate() if aggregate is None else aggregate
        artifacts = _artifacts() if artifacts is None else artifacts
        with (
            patch(
                "fmp.discovery.exp062_historical_result_content_review."
                "classify_historical_terminal_result",
                return_value=terminal,
            ),
            patch(
                "fmp.discovery.exp062_historical_result_content_review."
                "validate_aggregate_evidence",
                return_value=aggregate,
            ),
        ):
            return review_exp062_historical_result(
                run={},
                jobs_payload={},
                artifacts_payload=artifacts,
                aggregate_evidence=aggregate,
                aggregate_json_sha256=aggregate_json_sha256,
            )

    def test_successful_result_is_reviewed_without_unlocking_downstream(self) -> None:
        report = self._review()
        self.assertEqual(
            report["decision"],
            EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "EXP062_HISTORICAL_RESULT_CONTENT_REVIEWED_NO_VALIDATION_ACCEPTED",
        )
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_review_complete"])
        self.assertFalse(report["aggregate_result_content_review_required"])
        self.assertEqual(report["discovery_shortlist_count"], 67)
        self.assertEqual(report["confirmation_frozen_count"], 11)
        self.assertEqual(report["validation_accepted_count"], 0)
        self.assertFalse(report["validation_accepted_candidates_present"])
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["phase8b_authorized"])
        self.assertFalse(report["trading_authorized"])
        self.assertEqual(
            report["next_gate"],
            "IMMUTABLE_HISTORICAL_RESULT_REVIEW_FREEZE",
        )

    def test_aggregate_artifact_identity_is_exact(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["digest"] = "sha256:" + ("0" * 64)
        with self.assertRaisesRegex(ValueError, "aggregate artifact digest mismatch"):
            self._review(artifacts=artifacts)

    def test_aggregate_json_hash_is_exact(self) -> None:
        with self.assertRaisesRegex(ValueError, "aggregate JSON SHA-256 mismatch"):
            self._review(aggregate_json_sha256="0" * 64)

    def test_zero_validation_accepted_is_frozen(self) -> None:
        aggregate = _aggregate()
        aggregate["validation_accepted_count"] = 1
        with self.assertRaisesRegex(
            ValueError,
            "aggregate evidence validation_accepted_count mismatch",
        ):
            self._review(aggregate=aggregate)

    def test_terminal_review_must_remain_fail_closed_downstream(self) -> None:
        terminal = _terminal()
        terminal["candidate_compilation_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "terminal review candidate_compilation_authorized mismatch",
        ):
            self._review(terminal=terminal)

    def test_aggregate_cannot_open_phase8b_or_trading(self) -> None:
        aggregate = _aggregate()
        aggregate["phase8b_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "aggregate evidence phase8b_authorized mismatch",
        ):
            self._review(aggregate=aggregate)

        aggregate = _aggregate()
        aggregate["trading_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "aggregate evidence trading_authorized mismatch",
        ):
            self._review(aggregate=aggregate)


if __name__ == "__main__":
    unittest.main()
