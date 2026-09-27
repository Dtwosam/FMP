from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from fmp.discovery.pattern_miner import (
    BROKER_MUTATION_AUTHORIZED,
    CANDIDATE_COMPILATION_AUTHORIZED,
    DEMO_ORDER_AUTHORIZED,
    FeatureObservation,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
    HISTORICAL_SOURCE_ACCESS_AUTHORIZED,
    LIVE_ORDER_AUTHORIZED,
    OutcomeObservation,
    PHASE8B_AUTHORIZED,
    PROMOTION_AUTHORIZED,
    REAL_MONEY_AUTHORIZED,
    RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED,
    StateModel,
    TRADING_AUTHORIZED,
    calibrate_state_model,
    encode_state,
    enumerate_patterns,
    mine_discovery_shortlist,
    run_in_memory_discovery,
)
from fmp.discovery.pattern_protocol import (
    CONTINUOUS_FEATURES,
    MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON,
    SESSION_DIMENSION,
)


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
    validation_negative: bool = False,
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
        elif validation_negative and high:
            long_half = -0.2
            long_stress = -0.8
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
                horizon_minutes=60,
                long_net_pips_0p5=long_half,
                short_net_pips_0p5=-1.0,
                long_net_pips_1p0=long_stress,
                short_net_pips_1p0=-1.5,
            )
        )
    return features, outcomes


def _history(*, include_reserved: bool = False):
    features: list[FeatureObservation] = []
    outcomes: list[OutcomeObservation] = []
    for year in (2015, 2016, 2017, 2018, 2019, 2020, 2021):
        f, o = _year_rows(year)
        features.extend(f)
        outcomes.extend(o)
    f, o = _year_rows(2022, validation_negative=True)
    features.extend(f)
    outcomes.extend(o)
    if include_reserved:
        f, o = _year_rows(2023, reserved_crash=True)
        features.extend(f)
        outcomes.extend(o)
    return tuple(features), tuple(outcomes)


class Exp061PatternMinerCoreTests(unittest.TestCase):
    def test_full_state_model_enumeration_matches_frozen_bound(self) -> None:
        model = StateModel(
            symbol="EURUSD",
            timeframe="15m",
            cutpoints=tuple(
                (name, 0.0, 1.0)
                for name in CONTINUOUS_FEATURES
            ),
        )
        self.assertEqual(
            len(enumerate_patterns(model)),
            MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON,
        )

    def test_calibration_uses_discovery_only_and_skips_tied_dimensions(self) -> None:
        features, _ = _history(include_reserved=True)
        model = calibrate_state_model(
            features,
            symbol="EURUSD",
            timeframe="15m",
        )
        self.assertEqual(model.active_continuous_features, ("return_1h",))
        self.assertEqual(model.cutpoints, (("return_1h", 99.0, 199.0),))

        high = next(
            row
            for row in features
            if row.available_at_utc.year == 2015
            and row.values["return_1h"] == 250.0
        )
        self.assertEqual(
            encode_state(high, model),
            (
                ("return_1h", "HIGH"),
                (SESSION_DIMENSION, "OFF_SESSION"),
            ),
        )

    def test_discovery_finds_data_derived_high_state_and_deduplicates_pair(self) -> None:
        features, outcomes = _history()
        model = calibrate_state_model(
            features,
            symbol="EURUSD",
            timeframe="15m",
        )
        report = mine_discovery_shortlist(
            features,
            outcomes,
            model=model,
            horizon_minutes=60,
        )

        self.assertEqual(report.enumerated_pattern_count, 23)
        self.assertEqual(report.directional_hypothesis_count, 46)
        self.assertEqual(report.qualifying_directional_hypothesis_count, 2)
        self.assertEqual(report.deduplicated_directional_hypothesis_count, 1)
        self.assertEqual(len(report.shortlist), 1)

        candidate = report.shortlist[0]
        self.assertEqual(candidate.direction, "LONG")
        self.assertEqual(candidate.predicates, (("return_1h", "HIGH"),))
        self.assertEqual(candidate.discovery_statistics.total_support, 300)
        self.assertEqual(
            candidate.discovery_statistics.year_support,
            ((2015, 100), (2016, 100), (2017, 100)),
        )
        self.assertEqual(candidate.discovery_statistics.aggregate_mean_net_pips_0p5, 1.0)
        self.assertEqual(candidate.discovery_statistics.aggregate_mean_net_pips_1p0, 0.4)

    def test_end_to_end_freezes_then_validates_without_retuning(self) -> None:
        features, outcomes = _history()
        result = run_in_memory_discovery(
            features,
            outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )

        self.assertEqual(len(result.discovery.shortlist), 1)
        self.assertEqual(len(result.confirmation.evaluations), 1)
        self.assertTrue(result.confirmation.evaluations[0].passed)
        self.assertEqual(result.confirmation.evaluations[0].support, 100)
        self.assertEqual(len(result.confirmation.frozen), 1)

        self.assertEqual(len(result.validation.evaluations), 1)
        evaluation = result.validation.evaluations[0]
        self.assertEqual(evaluation.total_support, 400)
        self.assertEqual(
            evaluation.year_support,
            ((2019, 100), (2020, 100), (2021, 100), (2022, 100)),
        )
        self.assertEqual(evaluation.positive_year_count, 3)
        self.assertAlmostEqual(evaluation.aggregate_mean_net_pips_0p5, 0.7)
        self.assertTrue(evaluation.passed)
        self.assertEqual(len(result.validation.validated), 1)

    def test_reserved_2023_rows_cannot_change_exp061_result(self) -> None:
        features, outcomes = _history(include_reserved=False)
        baseline = run_in_memory_discovery(
            features,
            outcomes,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )
        features_reserved, outcomes_reserved = _history(include_reserved=True)
        with_reserved = run_in_memory_discovery(
            features_reserved,
            outcomes_reserved,
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
        )
        self.assertEqual(baseline, with_reserved)

    def test_duplicate_outcome_identity_fails_closed(self) -> None:
        features, outcomes = _history()
        model = calibrate_state_model(
            features,
            symbol="EURUSD",
            timeframe="15m",
        )
        duplicated = tuple(outcomes) + (outcomes[0],)
        with self.assertRaisesRegex(ValueError, "duplicate EXP-061 outcome observation identity"):
            mine_discovery_shortlist(
                features,
                duplicated,
                model=model,
                horizon_minutes=60,
            )

    def test_all_external_execution_and_trading_paths_remain_locked(self) -> None:
        for value in (
            HISTORICAL_SOURCE_ACCESS_AUTHORIZED,
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
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
