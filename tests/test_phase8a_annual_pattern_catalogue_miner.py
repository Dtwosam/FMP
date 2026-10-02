from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from fmp.discovery.annual_pattern_catalogue_miner import (
    HISTORICAL_ARTIFACT_READ_AUTHORIZED,
    HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_PRODUCTION_AUTHORIZED,
    STRATEGY_V1_SYNTHESIS_AUTHORIZED,
    TRADING_AUTHORIZED,
    encode_annual_states,
    mine_annual_catalogue_cell,
    miner_contract_payload,
)
from fmp.discovery.pattern_miner import FeatureObservation, OutcomeObservation
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES


_SESSION_FLAGS = (
    "is_london_new_york_overlap",
    "is_london_session",
    "is_new_york_session",
    "is_asia_session",
)


def _values(
    *,
    return_1h: float | None = None,
    london: bool = False,
) -> dict[str, object]:
    values: dict[str, object] = {name: None for name in CONTINUOUS_FEATURES}
    values["return_1h"] = return_1h
    values.update({name: False for name in _SESSION_FLAGS})
    values["is_london_session"] = london
    return values


def _feature(
    observation_id: str,
    available: datetime,
    *,
    return_1h: float | None = None,
    london: bool = False,
) -> FeatureObservation:
    return FeatureObservation(
        observation_id=observation_id,
        symbol="EURUSD",
        timeframe="5m",
        available_at_utc=available,
        values=_values(return_1h=return_1h, london=london),
    )


def _outcome(
    observation_id: str,
    available: datetime,
    *,
    horizon: int = 60,
    long_half: float = 1.0,
    short_half: float = -1.0,
) -> OutcomeObservation:
    return OutcomeObservation(
        observation_id=observation_id,
        symbol="EURUSD",
        timeframe="5m",
        available_at_utc=available,
        exit_timestamp_utc=available + timedelta(minutes=horizon),
        horizon_minutes=horizon,
        long_net_pips_0p5=long_half,
        short_net_pips_0p5=short_half,
        long_net_pips_1p0=long_half - 0.5,
        short_net_pips_1p0=short_half - 0.5,
    )


class AnnualPatternCatalogueMinerTests(unittest.TestCase):
    def test_miner_binds_exact_merged_dec470_protocol(self) -> None:
        payload = miner_contract_payload()

        self.assertEqual(payload["source_protocol_decision"], "DEC-470")
        self.assertEqual(
            payload["source_protocol_merge_sha"],
            "e5b20a2d8b45e5eda54673060060fbb9f480f545",
        )
        self.assertEqual(
            payload["source_protocol_blob_sha"],
            "5ddd987cc480e6e31c0cd45328eba16cf690dee9",
        )

    def test_miner_emits_every_nominal_directional_record_without_selection(self) -> None:
        available = datetime(2015, 1, 2, tzinfo=timezone.utc)
        feature = _feature("x", available)
        outcome = _outcome("x", available)

        result = mine_annual_catalogue_cell(
            (feature,),
            (outcome,),
            symbol="EURUSD",
            timeframe="5m",
            horizon_minutes=60,
            annual_segment_label="2015",
        )

        self.assertEqual(len(result.records), 4970)
        self.assertEqual(
            len({row.annual_record_id for row in result.records}),
            4970,
        )
        self.assertEqual(
            len({row.canonical_pattern_fingerprint for row in result.records}),
            4970,
        )
        self.assertEqual(result.feature_observation_count, 1)
        self.assertEqual(result.outcome_observation_count, 1)
        self.assertFalse(miner_contract_payload()["selects_winners"])
        self.assertFalse(miner_contract_payload()["reranks_patterns"])

        off_long = next(
            row
            for row in result.records
            if row.family == "SNAPSHOT_SINGLE"
            and row.dimensions == ("session_state",)
            and row.states == ("OFF_SESSION",)
            and row.direction == "LONG"
        )
        self.assertEqual(off_long.statistics.support, 1)
        self.assertFalse(off_long.statistics.evaluable)
        self.assertEqual(off_long.statistics.mean_net_pips_0p5, 1.0)

        london_long = next(
            row
            for row in result.records
            if row.family == "SNAPSHOT_SINGLE"
            and row.dimensions == ("session_state",)
            and row.states == ("LONDON",)
            and row.direction == "LONG"
        )
        self.assertEqual(london_long.statistics.support, 0)
        self.assertIsNone(london_long.statistics.mean_net_pips_0p5)

    def test_continuous_state_uses_strictly_prior_rows_only(self) -> None:
        start = datetime(2015, 1, 1, tzinfo=timezone.utc)
        features = tuple(
            _feature(
                f"x-{index:03d}",
                start + timedelta(hours=index),
                return_1h=float(index),
            )
            for index in range(301)
        )

        encoded = encode_annual_states(
            features,
            symbol="EURUSD",
            timeframe="5m",
            annual_segment_label="2015",
        )
        before = dict(encoded[299].states)
        first_ready = dict(encoded[300].states)

        self.assertNotIn("return_1h", before)
        self.assertEqual(first_ready["return_1h"], "HIGH")

        extended = features + (
            _feature(
                "future-extreme",
                start + timedelta(hours=301),
                return_1h=-1_000_000.0,
            ),
        )
        encoded_extended = encode_annual_states(
            extended,
            symbol="EURUSD",
            timeframe="5m",
            annual_segment_label="2015",
        )
        self.assertEqual(encoded_extended[:301], encoded)

    def test_transition_requires_exact_prior_timestamp(self) -> None:
        start = datetime(2015, 1, 2, tzinfo=timezone.utc)
        exact_features = (
            _feature("prior", start),
            _feature("current", start + timedelta(minutes=60)),
        )
        current_outcome = _outcome(
            "current",
            start + timedelta(minutes=60),
        )

        exact = mine_annual_catalogue_cell(
            exact_features,
            (current_outcome,),
            symbol="EURUSD",
            timeframe="5m",
            horizon_minutes=60,
            annual_segment_label="2015",
        )
        exact_transition = next(
            row
            for row in exact.records
            if row.family == "SAME_DIMENSION_TRANSITION"
            and row.dimensions == ("session_state",)
            and row.states == ("OFF_SESSION", "OFF_SESSION")
            and row.lag_minutes == 60
            and row.direction == "LONG"
        )
        self.assertEqual(exact_transition.statistics.support, 1)

        near_features = (
            _feature("near-prior", start + timedelta(minutes=1)),
            _feature("current", start + timedelta(minutes=60)),
        )
        near = mine_annual_catalogue_cell(
            near_features,
            (current_outcome,),
            symbol="EURUSD",
            timeframe="5m",
            horizon_minutes=60,
            annual_segment_label="2015",
        )
        near_transition = next(
            row
            for row in near.records
            if row.family == "SAME_DIMENSION_TRANSITION"
            and row.dimensions == ("session_state",)
            and row.states == ("OFF_SESSION", "OFF_SESSION")
            and row.lag_minutes == 60
            and row.direction == "LONG"
        )
        self.assertEqual(near_transition.statistics.support, 0)

    def test_outcome_crossing_annual_boundary_is_excluded(self) -> None:
        available = datetime(
            2015,
            12,
            31,
            22,
            0,
            tzinfo=timezone.utc,
        )
        feature = _feature("boundary", available)
        outcome = _outcome("boundary", available, horizon=240)

        result = mine_annual_catalogue_cell(
            (feature,),
            (outcome,),
            symbol="EURUSD",
            timeframe="5m",
            horizon_minutes=240,
            annual_segment_label="2015",
        )

        self.assertEqual(result.feature_observation_count, 1)
        self.assertEqual(result.outcome_observation_count, 0)
        self.assertTrue(
            all(row.statistics.support == 0 for row in result.records)
        )

    def test_duplicate_feature_and_outcome_identities_fail_closed(self) -> None:
        available = datetime(2015, 1, 2, tzinfo=timezone.utc)
        feature = _feature("x", available)
        outcome = _outcome("x", available)

        with self.assertRaisesRegex(
            ValueError,
            "duplicate DEC-471 feature observation identity",
        ):
            mine_annual_catalogue_cell(
                (feature, feature),
                (outcome,),
                symbol="EURUSD",
                timeframe="5m",
                horizon_minutes=60,
                annual_segment_label="2015",
            )

        with self.assertRaisesRegex(
            ValueError,
            "duplicate DEC-471 outcome observation identity",
        ):
            mine_annual_catalogue_cell(
                (feature,),
                (outcome, outcome),
                symbol="EURUSD",
                timeframe="5m",
                horizon_minutes=60,
                annual_segment_label="2015",
            )

    def test_all_runtime_strategy_and_trading_paths_remain_locked(self) -> None:
        self.assertFalse(HISTORICAL_ARTIFACT_READ_AUTHORIZED)
        self.assertFalse(HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_PRODUCTION_AUTHORIZED)
        self.assertFalse(STRATEGY_V1_SYNTHESIS_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)
        for field, enabled in miner_contract_payload()["authorizations"].items():
            self.assertFalse(enabled, field)

    def test_next_gate_is_source_only_evidence_contract(self) -> None:
        self.assertEqual(
            miner_contract_payload()["next_gate"],
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_EVIDENCE_CONTRACT",
        )


if __name__ == "__main__":
    unittest.main()
