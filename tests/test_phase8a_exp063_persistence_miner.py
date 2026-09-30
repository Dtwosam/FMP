from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from fmp.discovery.exp063_persistence_miner import (
    BROKER_MUTATION_AUTHORIZED,
    CANDIDATE_COMPILATION_AUTHORIZED,
    DEMO_ORDER_AUTHORIZED,
    HISTORICAL_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_AUTHORIZED,
    LIVE_ORDER_AUTHORIZED,
    PHASE8B_AUTHORIZED,
    PROMOTION_AUTHORIZED,
    REAL_MONEY_AUTHORIZED,
    RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED,
    SOURCE_ACCESS_AUTHORIZED,
    TRADING_AUTHORIZED,
    mine_persistence_shortlist,
    run_in_memory_persistence_miner,
)
from fmp.discovery.exp063_persistence_protocol import (
    MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON,
)
from fmp.discovery.pattern_miner import (
    FeatureObservation,
    OutcomeObservation,
    calibrate_state_model,
)
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES


def _values(signal: int) -> dict[str, object]:
    values: dict[str, object] = {
        name: 1.0 for name in CONTINUOUS_FEATURES
    }
    values["return_1h"] = float(signal)
    values.update(
        {
            "is_london_new_york_overlap": False,
            "is_london_session": False,
            "is_new_york_session": False,
            "is_asia_session": False,
        }
    )
    return values


def _year_rows(
    year: int,
    *,
    weak_persistence: bool = False,
    reserved_crash: bool = False,
) -> tuple[list[FeatureObservation], list[OutcomeObservation]]:
    features: list[FeatureObservation] = []
    outcomes: list[OutcomeObservation] = []
    start = datetime(year, 1, 1, tzinfo=timezone.utc)

    for index in range(300):
        signal = index
        observation_id = f"{year}-{index:03d}"
        available = start + timedelta(hours=index)
        features.append(
            FeatureObservation(
                observation_id=observation_id,
                symbol="EURUSD",
                timeframe="15m",
                available_at_utc=available,
                values=_values(signal),
            )
        )

        high = signal >= 200
        if reserved_crash and high:
            long_half = -100.0
            long_stress = -101.0
        elif weak_persistence and high:
            long_half = -0.5
            long_stress = 0.4
        elif high:
            long_half = 1.0
            long_stress = 0.4
        else:
            long_half = -1.0
            long_stress = -1.5

        outcomes.append(
            OutcomeObservation(
                observation_id=observation_id,
                symbol="EURUSD",
                timeframe="15m",
                available_at_utc=available,
                exit_timestamp_utc=available + timedelta(minutes=60),
                horizon_minutes=60,
                long_net_pips_0p5=long_half,
                short_net_pips_0p5=-1.0,
                long_net_pips_1p0=long_stress,
                short_net_pips_1p0=-1.5,
            )
        )

    return features, outcomes


def _history(
    *,
    weak_2021_2022: bool = False,
    include_reserved: bool = False,
) -> tuple[
    tuple[FeatureObservation, ...],
    tuple[OutcomeObservation, ...],
]:
    features: list[FeatureObservation] = []
    outcomes: list[OutcomeObservation] = []

    for year in range(2015, 2023):
        f, o = _year_rows(
            year,
            weak_persistence=weak_2021_2022 and year in (2021, 2022),
        )
        features.extend(f)
        outcomes.extend(o)

    if include_reserved:
        for year in (2023, 2024, 2025, 2026):
            f, o = _year_rows(year, reserved_crash=True)
            features.extend(f)
            outcomes.extend(o)

    return tuple(features), tuple(outcomes)


class Exp063PersistenceMinerCoreTests(unittest.TestCase):
    def test_persistence_miner_reuses_bounded_enumeration_and_dedup(self) -> None:
        features, outcomes = _history()
        model = calibrate_state_model(
            features,
            symbol="EURUSD",
            timeframe="15m",
        )
        report = mine_persistence_shortlist(
            features,
            outcomes,
            model=model,
            horizon_minutes=60,
        )

        self.assertEqual(report.enumerated_pattern_count, 23)
        self.assertLessEqual(
            report.enumerated_pattern_count,
            MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON,
        )
        self.assertEqual(report.directional_hypothesis_count, 46)
        self.assertEqual(report.qualifying_directional_hypothesis_count, 2)
        self.assertEqual(report.deduplicated_directional_hypothesis_count, 1)
        self.assertEqual(len(report.shortlist), 1)
        self.assertEqual(len(report.frozen), 1)

        candidate = report.frozen[0]
        self.assertEqual(candidate.direction, "LONG")
        self.assertEqual(candidate.predicates, (("return_1h", "HIGH"),))
        self.assertEqual(candidate.total_support, 800)
        self.assertEqual(candidate.minimum_year_support, 100)
        self.assertEqual(candidate.positive_year_count, 8)
        self.assertEqual(candidate.aggregate_mean_net_pips_0p5, 1.0)
        self.assertEqual(candidate.aggregate_mean_net_pips_1p0, 0.4)
        self.assertEqual(
            candidate.lower_half_annual_mean_net_pips_0p5,
            1.0,
        )
        self.assertEqual(
            candidate.minimum_two_year_block_mean_net_pips_0p5,
            1.0,
        )
        self.assertEqual(
            report.output_kind,
            "RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED",
        )

    def test_negative_2021_2022_block_rejects_otherwise_strong_pattern(self) -> None:
        features, outcomes = _history(weak_2021_2022=True)
        result = run_in_memory_persistence_miner(
            features,
            outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )

        self.assertEqual(result.report.qualifying_directional_hypothesis_count, 0)
        self.assertEqual(result.report.shortlist, ())
        self.assertEqual(result.report.frozen, ())

    def test_reserved_2023_2026_rows_cannot_change_exp063_result(self) -> None:
        features, outcomes = _history(include_reserved=False)
        baseline = run_in_memory_persistence_miner(
            features,
            outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )

        reserved_features, reserved_outcomes = _history(include_reserved=True)
        with_reserved = run_in_memory_persistence_miner(
            reserved_features,
            reserved_outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )

        self.assertEqual(baseline, with_reserved)

    def test_duplicate_design_outcome_identity_fails_closed(self) -> None:
        features, outcomes = _history()
        model = calibrate_state_model(
            features,
            symbol="EURUSD",
            timeframe="15m",
        )
        duplicated = tuple(outcomes) + (outcomes[0],)

        with self.assertRaisesRegex(
            ValueError,
            "duplicate EXP-063 outcome observation identity",
        ):
            mine_persistence_shortlist(
                features,
                duplicated,
                model=model,
                horizon_minutes=60,
            )

    def test_state_calibration_remains_2015_2017_only(self) -> None:
        features, _ = _history(include_reserved=True)
        model = calibrate_state_model(
            features,
            symbol="EURUSD",
            timeframe="15m",
        )

        self.assertEqual(model.active_continuous_features, ("return_1h",))
        self.assertEqual(
            model.cutpoints,
            (("return_1h", 99.0, 199.0),),
        )

    def test_all_external_execution_and_trading_paths_remain_locked(self) -> None:
        for value in (
            SOURCE_ACCESS_AUTHORIZED,
            HISTORICAL_EXECUTION_AUTHORIZED,
            HISTORICAL_RESULT_AUTHORIZED,
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED,
            CANDIDATE_COMPILATION_AUTHORIZED,
            PROMOTION_AUTHORIZED,
            PHASE8B_AUTHORIZED,
            DEMO_ORDER_AUTHORIZED,
            BROKER_MUTATION_AUTHORIZED,
            LIVE_ORDER_AUTHORIZED,
            REAL_MONEY_AUTHORIZED,
            TRADING_AUTHORIZED,
        ):
            self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
