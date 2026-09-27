from __future__ import annotations

from unittest.mock import patch
import unittest

from fmp.discovery.historical_result_content_review import (
    EXP061_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION,
    review_successful_historical_result_content,
)


HEAD = "a" * 40


def _terminal() -> dict[str, object]:
    return {
        "decision": "DEC-290",
        "version": "fmp-exp061-historical-terminal-review-contract-v1",
        "stage": "EXP061_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED",
        "historical_run_id": 40000000000,
        "historical_run_head_sha": HEAD,
        "historical_run_number": 2,
        "historical_run_attempt": 1,
        "historical_result_slot_consumed": True,
        "historical_result_success_complete": True,
        "materialized_job_count": 20,
        "artifact_count": 20,
        "github_unexpanded_matrix_placeholder_present": False,
        "aggregate_result_content_review_required": True,
        "partial_evidence_may_be_preserved": False,
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
    }


def _cells() -> list[dict[str, object]]:
    return [
        {
            "code_commit": HEAD,
            "cell": {"index": index},
        }
        for index in range(18)
    ]


def _aggregate(*, accepted: int = 2) -> dict[str, object]:
    cell_summaries: list[dict[str, object]] = []
    for index in range(18):
        values: list[str] = []
        if index < accepted:
            values = [f"{index + 1:064x}"]
        cell_summaries.append(
            {
                "symbol": ("EURUSD", "GBPUSD", "USDJPY")[index // 6],
                "timeframe": ("5m", "15m", "1h")[(index // 2) % 3],
                "horizon_minutes": (60, 240)[index % 2],
                "validation_accepted_fingerprints": values,
            }
        )
    return {
        "code_commit": HEAD,
        "evidence_fingerprint": "f" * 64,
        "discovery_shortlist_count": 18,
        "confirmation_frozen_count": 7,
        "validation_accepted_count": accepted,
        "cells": cell_summaries,
    }


class Exp061HistoricalResultContentReviewTests(unittest.TestCase):
    def _review(
        self,
        *,
        terminal: dict[str, object] | None = None,
        cells: list[dict[str, object]] | None = None,
        aggregate: dict[str, object] | None = None,
    ) -> dict[str, object]:
        terminal = _terminal() if terminal is None else terminal
        cells = _cells() if cells is None else cells
        aggregate = _aggregate() if aggregate is None else aggregate
        with (
            patch(
                "fmp.discovery.historical_result_content_review.validate_cell_evidence",
                side_effect=lambda value: value,
            ),
            patch(
                "fmp.discovery.historical_result_content_review.validate_aggregate_evidence",
                side_effect=lambda value: value,
            ),
            patch(
                "fmp.discovery.historical_result_content_review.compile_aggregate_evidence",
                return_value=aggregate,
            ),
        ):
            return review_successful_historical_result_content(
                terminal_review=terminal,
                cell_evidence=cells,
                aggregate_evidence=aggregate,
                expected_head_sha=HEAD,
            )

    def test_validated_pattern_hypotheses_are_reported_not_promoted(self) -> None:
        report = self._review()
        self.assertEqual(
            report["decision"],
            EXP061_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "EXP061_HISTORICAL_RESULT_REVIEWED_VALIDATED_PATTERN_HYPOTHESES_PRESENT",
        )
        self.assertEqual(report["verified_cell_evidence_count"], 18)
        self.assertTrue(report["aggregate_evidence_verified"])
        self.assertEqual(report["discovery_shortlist_count"], 18)
        self.assertEqual(report["confirmation_frozen_count"], 7)
        self.assertEqual(report["validation_accepted_count"], 2)
        self.assertEqual(len(report["validated_pattern_fingerprints"]), 2)
        self.assertTrue(report["validated_pattern_hypotheses_present"])
        self.assertEqual(
            report["output_meaning"],
            "PATTERN_HYPOTHESIS_NOT_EXECUTABLE_STRATEGY",
        )
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_zero_validated_patterns_is_valid_negative_result(self) -> None:
        aggregate = _aggregate(accepted=0)
        report = self._review(aggregate=aggregate)
        self.assertEqual(
            report["stage"],
            "EXP061_HISTORICAL_RESULT_REVIEWED_NO_VALIDATED_PATTERNS",
        )
        self.assertEqual(report["validation_accepted_count"], 0)
        self.assertFalse(report["validated_pattern_hypotheses_present"])
        self.assertEqual(report["validated_pattern_fingerprints"], [])

    def test_non_success_terminal_shape_cannot_enter_content_review(self) -> None:
        terminal = _terminal()
        terminal["stage"] = "EXP061_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED"
        terminal["historical_result_success_complete"] = False
        with self.assertRaisesRegex(
            ValueError,
            "terminal review stage mismatch",
        ):
            self._review(terminal=terminal)

    def test_requires_exact_eighteen_cells_and_commit_binding(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "exactly 18 cell evidence objects",
        ):
            self._review(cells=_cells()[:-1])

        cells = _cells()
        cells[0]["code_commit"] = "b" * 40
        with self.assertRaisesRegex(
            ValueError,
            "cell evidence code commit mismatch",
        ):
            self._review(cells=cells)

    def test_aggregate_must_match_deterministic_recompilation(self) -> None:
        aggregate = _aggregate()
        different = dict(aggregate)
        different["confirmation_frozen_count"] = 8
        with (
            patch(
                "fmp.discovery.historical_result_content_review.validate_cell_evidence",
                side_effect=lambda value: value,
            ),
            patch(
                "fmp.discovery.historical_result_content_review.validate_aggregate_evidence",
                return_value=aggregate,
            ),
            patch(
                "fmp.discovery.historical_result_content_review.compile_aggregate_evidence",
                return_value=different,
            ),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "deterministic cell recompilation",
            ):
                review_successful_historical_result_content(
                    terminal_review=_terminal(),
                    cell_evidence=_cells(),
                    aggregate_evidence=aggregate,
                    expected_head_sha=HEAD,
                )

    def test_duplicate_global_pattern_fingerprint_is_rejected(self) -> None:
        aggregate = _aggregate(accepted=2)
        cells = aggregate["cells"]
        assert isinstance(cells, list)
        first = cells[0]
        second = cells[1]
        assert isinstance(first, dict)
        assert isinstance(second, dict)
        second["validation_accepted_fingerprints"] = list(
            first["validation_accepted_fingerprints"]
        )
        with self.assertRaisesRegex(
            ValueError,
            "globally unique",
        ):
            self._review(aggregate=aggregate)

    def test_terminal_locks_must_remain_closed(self) -> None:
        terminal = _terminal()
        terminal["candidate_compilation_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "candidate_compilation_authorized mismatch",
        ):
            self._review(terminal=terminal)


if __name__ == "__main__":
    unittest.main()
