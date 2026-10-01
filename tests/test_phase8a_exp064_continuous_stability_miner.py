from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from fmp.discovery.exp064_continuous_stability_miner import (
    HISTORICAL_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_AUTHORIZED,
    RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED,
    SOURCE_ACCESS_AUTHORIZED,
    CANDIDATE_COMPILATION_AUTHORIZED,
    PHASE8B_AUTHORIZED,
    TRADING_AUTHORIZED,
    run_in_memory_continuous_stability_miner,
)
from fmp.discovery.exp064_continuous_stability_protocol import (
    CONTINUOUS_FEATURES,
)
from fmp.discovery.pattern_miner import (
    FeatureObservation,
    OutcomeObservation,
)


_SESSION_FLAGS = (
    "is_london_new_york_overlap",
    "is_london_session",
    "is_new_york_session",
    "is_asia_session",
)


def _feature_values(
    value: float,
    *,
    duplicate_feature: bool = False,
) -> dict[str, object]:
    values: dict[str, object] = {
        name: 0.0 for name in CONTINUOUS_FEATURES
    }
    values["return_1h"] = value
    if duplicate_feature:
        values["return_24h"] = value
    values.update({name: False for name in _SESSION_FLAGS})
    return values


def _fixture(
    *,
    weak_2021_2022: bool = False,
    include_reserve: bool = False,
    duplicate_feature: bool = False,
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
            percentile = (index + 0.5) / 300.0
            centered = percentile - 0.5
            long_half = 4.0 * centered
            if weak_2021_2022 and year in (2021, 2022):
                long_half = -long_half
            long_stress = long_half - 0.5
            short_half = -long_half
            short_stress = short_half - 0.5

            features.append(
                FeatureObservation(
                    observation_id=observation_id,
                    symbol="EURUSD",
                    timeframe="15m",
                    available_at_utc=available,
                    values=_feature_values(
                        float(index),
                        duplicate_feature=duplicate_feature,
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
                    long_net_pips_1p0=long_stress,
                    short_net_pips_1p0=short_stress,
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
                            10000.0 + index,
                            duplicate_feature=duplicate_feature,
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


class Exp064ContinuousStabilityMinerTests(unittest.TestCase):
    def test_miner_finds_only_stable_monotone_single_feature_effects(self) -> None:
        features, outcomes = _fixture()

        result = run_in_memory_continuous_stability_miner(
            features,
            outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )
        report = result.report

        self.assertEqual(report.hypothesis_count, 80)
        self.assertEqual(report.evaluable_hypothesis_count, 4)
        self.assertEqual(report.qualifying_hypothesis_count, 2)
        self.assertEqual(report.deduplicated_hypothesis_count, 2)
        self.assertEqual(len(report.shortlist), 2)
        self.assertEqual(len(report.frozen), 2)
        self.assertEqual(report.active_continuous_features, ("return_1h",))

        identities = {
            (
                item.feature_name,
                item.direction,
                item.polarity,
            )
            for item in report.frozen
        }
        self.assertEqual(
            identities,
            {
                ("return_1h", "LONG", "INCREASING"),
                ("return_1h", "SHORT", "DECREASING"),
            },
        )
        for item in report.frozen:
            self.assertEqual(item.total_selected_tail_support, 600)
            self.assertEqual(item.minimum_year_selected_tail_support, 75)
            self.assertEqual(item.positive_slope_year_count, 8)
            self.assertEqual(item.positive_tail_mean_year_count, 8)
            self.assertAlmostEqual(
                item.equal_year_signed_rank_slope_net_pips_0p5,
                4.0,
            )
            self.assertGreater(
                item.equal_year_selected_tail_mean_net_pips_0p5,
                1.0,
            )
            self.assertGreater(
                item.equal_year_selected_tail_mean_net_pips_1p0,
                0.5,
            )

        calibration = result.calibrations[0]
        self.assertEqual(calibration.feature_name, "return_1h")
        self.assertEqual(len(calibration.values), 2400)
        self.assertEqual(calibration.values[0], 0.0)
        self.assertEqual(calibration.values[-1], 299.0)

    def test_identical_feature_tail_events_are_jaccard_deduplicated(self) -> None:
        features, outcomes = _fixture(duplicate_feature=True)

        result = run_in_memory_continuous_stability_miner(
            features,
            outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )
        report = result.report

        self.assertEqual(
            report.active_continuous_features,
            ("return_1h", "return_24h"),
        )
        self.assertEqual(report.evaluable_hypothesis_count, 8)
        self.assertEqual(report.qualifying_hypothesis_count, 4)
        self.assertEqual(report.deduplicated_hypothesis_count, 2)
        self.assertEqual(len(report.shortlist), 2)
        self.assertEqual(
            {item.feature_name for item in report.shortlist},
            {"return_1h"},
        )

    def test_weak_final_two_year_block_rejects_otherwise_strong_effect(self) -> None:
        features, outcomes = _fixture(weak_2021_2022=True)

        result = run_in_memory_continuous_stability_miner(
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

        baseline = run_in_memory_continuous_stability_miner(
            base_features,
            base_outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )
        with_reserve = run_in_memory_continuous_stability_miner(
            reserve_features,
            reserve_outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )

        self.assertEqual(with_reserve, baseline)

    def test_duplicate_design_feature_identity_fails_closed(self) -> None:
        features, outcomes = _fixture()
        duplicated = features + (features[0],)

        with self.assertRaisesRegex(
            ValueError,
            "duplicate DEC-453 feature observation identity",
        ):
            run_in_memory_continuous_stability_miner(
                duplicated,
                outcomes,
                symbol="EURUSD",
                timeframe="15m",
                horizon_minutes=60,
            )

    def test_duplicate_design_outcome_identity_fails_closed(self) -> None:
        features, outcomes = _fixture()
        duplicated = outcomes + (outcomes[0],)

        with self.assertRaisesRegex(
            ValueError,
            "duplicate DEC-453 outcome observation identity",
        ):
            run_in_memory_continuous_stability_miner(
                features,
                duplicated,
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
