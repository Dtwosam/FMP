from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from fmp.contracts import Direction
from fmp.strategies.contracts import SignalCandidate


UTC = timezone.utc


def candidate(candidate_id: str, *, direction: Direction) -> SignalCandidate:
    observation = datetime(2020, 1, 2, 9, 0, tzinfo=UTC)
    known = observation + timedelta(minutes=15)
    if direction is Direction.NO_TRADE:
        return SignalCandidate(
            candidate_id=candidate_id,
            symbol="USDJPY",
            observation_bar_timestamp_utc=observation,
            signal_known_timestamp_utc=known,
            direction=direction,
            stop_price=None,
            target_price=None,
            latest_exit_timestamp_utc=None,
            reason_code="RULE_NO_TRADE",
            metadata={"origin": "rule"},
        )
    return SignalCandidate(
        candidate_id=candidate_id,
        symbol="USDJPY",
        observation_bar_timestamp_utc=observation,
        signal_known_timestamp_utc=known,
        direction=direction,
        stop_price=149.50 if direction is Direction.LONG else 150.50,
        target_price=150.50 if direction is Direction.LONG else 149.50,
        latest_exit_timestamp_utc=observation + timedelta(hours=7),
        reason_code="RULE_SIGNAL",
        metadata={"origin": "rule"},
    )


class Phase6FilteringTests(unittest.TestCase):
    def test_admitted_candidates_are_original_objects_and_no_trade_passes_through(self) -> None:
        from fmp.models.filtering import filter_candidates
        from fmp.models.thresholds import ScoreCutoff

        admitted = candidate("A", direction=Direction.LONG)
        no_trade = candidate("N", direction=Direction.NO_TRADE)
        cutoff = ScoreCutoff(0.5, 1, 0.6, 3, 2, 2 / 3)
        result = filter_candidates(
            (no_trade, admitted),
            {"A": 0.6},
            cutoff,
            "logistic_regression",
        )
        self.assertIs(result[0], no_trade)
        self.assertIs(result[1], admitted)

    def test_rejected_directional_candidate_becomes_explicit_no_trade_with_provenance(self) -> None:
        from fmp.models.contracts import FEATURE_SET_VERSION
        from fmp.models.filtering import filter_candidates
        from fmp.models.thresholds import ScoreCutoff

        original = candidate("A", direction=Direction.SHORT)
        cutoff = ScoreCutoff(0.5, 1, 0.6, 3, 2, 2 / 3)
        rejected = filter_candidates(
            (original,),
            {"A": 0.59},
            cutoff,
            "hist_gradient_boosting",
        )[0]

        self.assertEqual(rejected.candidate_id, original.candidate_id)
        self.assertEqual(rejected.observation_bar_timestamp_utc, original.observation_bar_timestamp_utc)
        self.assertEqual(rejected.signal_known_timestamp_utc, original.signal_known_timestamp_utc)
        self.assertIs(rejected.direction, Direction.NO_TRADE)
        self.assertIsNone(rejected.stop_price)
        self.assertIsNone(rejected.target_price)
        self.assertIsNone(rejected.latest_exit_timestamp_utc)
        self.assertEqual(rejected.reason_code, "ML_FILTER_REJECTED")
        self.assertEqual(rejected.metadata["model_id"], "hist_gradient_boosting")
        self.assertEqual(rejected.metadata["model_score"], 0.59)
        self.assertEqual(rejected.metadata["cutoff"], 0.6)
        self.assertEqual(rejected.metadata["original_direction"], "SHORT")
        self.assertEqual(rejected.metadata["strategy_candidate_id"], "A")
        self.assertEqual(rejected.metadata["feature_set_version"], FEATURE_SET_VERSION)
        self.assertEqual(
            rejected.metadata["feature_row_identity"],
            {
                "symbol": "USDJPY",
                "bar_start_utc": original.observation_bar_timestamp_utc,
                "available_at_utc": original.signal_known_timestamp_utc,
            },
        )
        self.assertEqual(rejected.metadata["original_stop_price"], original.stop_price)
        self.assertEqual(rejected.metadata["original_target_price"], original.target_price)
        self.assertEqual(
            rejected.metadata["original_latest_exit_timestamp_utc"],
            original.latest_exit_timestamp_utc,
        )

    def test_missing_or_extra_directional_scores_fail_closed(self) -> None:
        from fmp.models.filtering import filter_candidates
        from fmp.models.thresholds import ScoreCutoff

        original = candidate("A", direction=Direction.LONG)
        cutoff = ScoreCutoff(0.5, 1, 0.6, 3, 2, 2 / 3)
        with self.assertRaisesRegex(ValueError, "score"):
            filter_candidates((original,), {}, cutoff, "logistic_regression")
        with self.assertRaisesRegex(ValueError, "score"):
            filter_candidates(
                (original,),
                {"A": 0.7, "UNKNOWN": 0.9},
                cutoff,
                "logistic_regression",
            )


if __name__ == "__main__":
    unittest.main()
