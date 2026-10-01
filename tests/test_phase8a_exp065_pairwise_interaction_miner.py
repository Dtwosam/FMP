from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from fmp.discovery.exp065_pairwise_interaction_miner import (
    CANDIDATE_COMPILATION_AUTHORIZED,
    DEC461_MERGE_SHA,
    DEC461_PROTOCOL_BLOB_SHA,
    HISTORICAL_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_AUTHORIZED,
    PHASE8B_AUTHORIZED,
    RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED,
    SOURCE_ACCESS_AUTHORIZED,
    TRADING_AUTHORIZED,
    run_in_memory_pairwise_interaction_miner,
)
from fmp.discovery.pattern_miner import FeatureObservation, OutcomeObservation
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES


_SESSION_FLAGS = (
    "is_london_new_york_overlap",
    "is_london_session",
    "is_new_york_session",
    "is_asia_session",
)


def _feature_values(
    index: int,
    *,
    duplicate_pair_feature: bool = False,
) -> dict[str, object]:
    values: dict[str, object] = {
        name: 0.0 for name in CONTINUOUS_FEATURES
    }
    values["return_1h"] = float(index)
    paired = float((index * 73) % 300)
    values["return_24h"] = paired
    if duplicate_pair_feature:
        values["return_7d"] = paired
    values.update({name: False for name in _SESSION_FLAGS})
    return values


def _interaction_raw_for_index(index: int) -> float:
    percentile_a = (index + 0.5) / 300.0
    percentile_b = (((index * 73) % 300) + 0.5) / 300.0
    return (
        2.0
        * (percentile_a - 0.5)
        * (percentile_b - 0.5)
    )


def _fixture(
    *,
    weak_2021_2022: bool = False,
    include_reserve: bool = False,
    duplicate_pair_feature: bool = False,
) -> tuple[tuple[FeatureObservation, ...], tuple[OutcomeObservation, ...]]:
    features: list[FeatureObservation] = []
    outcomes: list[OutcomeObservation] = []

    for year in range(2015, 2023):
        for index in range(300):
            available = datetime(
                year,
                1,
                1,
                tzinfo=timezone.utc,
            ) + timedelta(hours=index)
            observation_id = f"{year}-{index:03d}"
            interaction_raw = _interaction_raw_for_index(index)
            long_half = 8.0 * interaction_raw
            if weak_2021_2022 and year in (2021, 2022):
                long_half = -long_half
            short_half = -long_half

            features.append(
                FeatureObservation(
                    observation_id=observation_id,
                    symbol="EURUSD",
                    timeframe="15m",
                    available_at_utc=available,
                    values=_feature_values(
                        index,
                        duplicate_pair_feature=duplicate_pair_feature,
                    ),
                )
            )
            outcomes.append(
                OutcomeObservation(
                    observation_id=observation_id,
                    symbol="EURUSD",
                    timeframe="15m",
                    available_at_utc=available,
                    exit_timestamp_utc=available + timedelta(minutes=60),
                    horizon_minutes=60,
                    long_net_pips_0p5=long_half,
                    short_net_pips_0p5=short_half,
                    long_net_pips_1p0=long_half - 0.5,
                    short_net_pips_1p0=short_half - 0.5,
                )
            )

    if include_reserve:
        for year in range(2023, 2027):
            for index in range(100):
                available = datetime(
                    year,
                    1,
                    1,
                    tzinfo=timezone.utc,
                ) + timedelta(hours=index)
                observation_id = f"reserve-{year}-{index:03d}"
                features.append(
                    FeatureObservation(
                        observation_id=observation_id,
                        symbol="EURUSD",
                        timeframe="15m",
                        available_at_utc=available,
                        values=_feature_values(
                            index,
                            duplicate_pair_feature=duplicate_pair_feature,
                        ),
                    )
                )
                outcomes.append(
                    OutcomeObservation(
                        observation_id=observation_id,
                        symbol="EURUSD",
                        timeframe="15m",
                        available_at_utc=available,
                        exit_timestamp_utc=available + timedelta(minutes=60),
                        horizon_minutes=60,
                        long_net_pips_0p5=-100.0,
                        short_net_pips_0p5=-100.0,
                        long_net_pips_1p0=-101.0,
                        short_net_pips_1p0=-101.0,
                    )
                )

    return tuple(features), tuple(outcomes)


class Exp065PairwiseInteractionMinerTests(unittest.TestCase):
    def test_miner_binds_repaired_dec461_protocol(self) -> None:
        self.assertEqual(
            DEC461_MERGE_SHA,
            "2a8127b505c9b0d9e1adb562bd18a5cafc171df6",
        )
        self.assertEqual(
            DEC461_PROTOCOL_BLOB_SHA,
            "b54267d790667659749a96123ad23a491ff50dfa",
        )

    def test_miner_finds_stable_incremental_pairwise_interaction(self) -> None:
        features, outcomes = _fixture()

        result = run_in_memory_pairwise_interaction_miner(
            features,
            outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )
        report = result.report

        self.assertEqual(report.hypothesis_count, 760)
        self.assertEqual(
            report.active_continuous_features,
            ("return_1h", "return_24h"),
        )
        self.assertEqual(
            report.active_feature_pairs,
            (("return_1h", "return_24h"),),
        )
        self.assertEqual(report.evaluable_hypothesis_count, 4)
        self.assertEqual(report.qualifying_hypothesis_count, 2)
        self.assertEqual(report.deduplicated_hypothesis_count, 2)
        self.assertEqual(len(report.shortlist), 2)
        self.assertEqual(len(report.frozen), 1)

        identities = {
            (
                item.feature_a,
                item.feature_b,
                item.direction,
                item.polarity,
            )
            for item in report.shortlist
        }
        self.assertEqual(
            identities,
            {
                ("return_1h", "return_24h", "LONG", "INCREASING"),
                ("return_1h", "return_24h", "SHORT", "DECREASING"),
            },
        )

        for item in report.shortlist:
            self.assertEqual(item.total_selected_tail_support, 600)
            self.assertEqual(item.minimum_year_selected_tail_support, 75)
            self.assertEqual(item.positive_partial_slope_year_count, 8)
            self.assertEqual(item.positive_raw_tail_mean_year_count, 8)
            self.assertEqual(
                item.positive_incremental_tail_mean_year_count,
                8,
            )
            self.assertGreater(
                item.equal_year_signed_partial_slope_net_pips_0p5,
                4.0,
            )
            self.assertGreater(
                item.equal_year_raw_tail_mean_net_pips_0p5,
                1.0,
            )
            self.assertGreater(
                item.equal_year_incremental_tail_mean_net_pips_0p5,
                1.0,
            )
            self.assertGreater(
                item.equal_year_raw_tail_mean_net_pips_1p0,
                0.5,
            )

        self.assertEqual(len(result.feature_calibrations), 2)
        self.assertEqual(len(result.pair_calibrations), 1)
        self.assertEqual(len(result.pair_calibrations[0].values), 2400)

    def test_duplicate_pair_event_sets_are_jaccard_deduplicated(self) -> None:
        features, outcomes = _fixture(duplicate_pair_feature=True)

        result = run_in_memory_pairwise_interaction_miner(
            features,
            outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )
        report = result.report

        self.assertEqual(
            report.active_continuous_features,
            ("return_1h", "return_24h", "return_7d"),
        )
        self.assertIn(
            ("return_1h", "return_24h"),
            report.active_feature_pairs,
        )
        self.assertIn(
            ("return_1h", "return_7d"),
            report.active_feature_pairs,
        )
        self.assertGreaterEqual(report.qualifying_hypothesis_count, 4)
        self.assertLess(
            report.deduplicated_hypothesis_count,
            report.qualifying_hypothesis_count,
        )

    def test_weak_final_two_year_block_rejects_interaction(self) -> None:
        features, outcomes = _fixture(weak_2021_2022=True)

        result = run_in_memory_pairwise_interaction_miner(
            features,
            outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )

        self.assertEqual(result.report.qualifying_hypothesis_count, 0)
        self.assertEqual(result.report.deduplicated_hypothesis_count, 0)
        self.assertEqual(result.report.shortlist, ())
        self.assertEqual(result.report.frozen, ())

    def test_reserved_2023_2026_rows_cannot_change_any_result(self) -> None:
        base_features, base_outcomes = _fixture()
        reserve_features, reserve_outcomes = _fixture(include_reserve=True)

        baseline = run_in_memory_pairwise_interaction_miner(
            base_features,
            base_outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )
        with_reserve = run_in_memory_pairwise_interaction_miner(
            reserve_features,
            reserve_outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )

        self.assertEqual(with_reserve, baseline)

    def test_duplicate_design_feature_identity_fails_closed(self) -> None:
        features, outcomes = _fixture()

        with self.assertRaisesRegex(
            ValueError,
            "duplicate DEC-462 feature observation identity",
        ):
            run_in_memory_pairwise_interaction_miner(
                features + (features[0],),
                outcomes,
                symbol="EURUSD",
                timeframe="15m",
                horizon_minutes=60,
            )

    def test_duplicate_design_outcome_identity_fails_closed(self) -> None:
        features, outcomes = _fixture()

        with self.assertRaisesRegex(
            ValueError,
            "duplicate DEC-462 outcome observation identity",
        ):
            run_in_memory_pairwise_interaction_miner(
                features,
                outcomes + (outcomes[0],),
                symbol="EURUSD",
                timeframe="15m",
                horizon_minutes=60,
            )

    def test_all_external_execution_and_trading_paths_remain_false(self) -> None:
        self.assertFalse(SOURCE_ACCESS_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTION_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_AUTHORIZED)
        self.assertFalse(RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED)
        self.assertFalse(CANDIDATE_COMPILATION_AUTHORIZED)
        self.assertFalse(PHASE8B_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)


if __name__ == "__main__":
    unittest.main()
