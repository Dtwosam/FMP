from __future__ import annotations

import hashlib
import json
import random
import tracemalloc
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fmp.discovery.annual_pattern_catalogue_event_evidence import (
    ANNUAL_RUN_385_CONSUMED,
    CORRELATED_NOISE_CALIBRATION_EXPERIMENT,
    DEC629_ADOPTED,
    DEC630_ADOPTED,
    EVIDENCE_BASIS,
    HISTORICAL_ARTIFACT_READ_AUTHORIZED,
    HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
    STATISTICAL_PROMOTION_AUTHORIZED,
    STRATEGY_V1_SYNTHESIS_AUTHORIZED,
    TRADING_AUTHORIZED,
    WORKFLOW_ACTIVATION_AUTHORIZED,
    EventEvidenceProvenance,
    EventObservationSubmission,
    compile_event_evidence,
    event_identity_for,
    event_level_evidence_contract,
    recover_event_ids_from_event_fingerprint,
    submission_from_outcome,
    validate_event_evidence,
)
from fmp.discovery.annual_pattern_catalogue_miner import (
    AnnualPatternRecord,
    mine_annual_catalogue_cell,
)
from fmp.discovery.annual_pattern_catalogue_protocol import (
    DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
    DISCOVERY_SLIPPAGE_PIPS,
    MAX_SIGN_FLIPS,
    MIN_ANNUAL_EVALUABLE_SUPPORT,
    MIN_BASE_POSITIVE_FRACTION,
    MIN_CROSS_YEAR_EVALUABLE_SEGMENTS,
    MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5,
    MIN_POOLED_MEAN_NET_PIPS_0P5,
    MIN_STRESS_POSITIVE_FRACTION,
    NEAR_DUPLICATE_JACCARD,
    STRESS_SLIPPAGE_PIPS,
    PatternDefinition,
    protocol_fingerprint,
)
from fmp.discovery.pattern_miner import FeatureObservation, OutcomeObservation
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES


_COMMIT = "85536adadedeee59abdc4a13f02de23ee0b3979a"
_PROTOCOL_FINGERPRINT = "3f883b26f3d9da04840b9680701504833dbcb3ec2c919f74ed191a3ab1bd3d69"
_MANIFEST = hashlib.sha256(b"synthetic-event-evidence-v1\n").hexdigest()
_LOW = PatternDefinition(
    family="SNAPSHOT_SINGLE",
    dimensions=("return_1h",),
    states=("LOW",),
)
_HIGH = PatternDefinition(
    family="SNAPSHOT_SINGLE",
    dimensions=("return_1h",),
    states=("HIGH",),
)
_TRANSITION = PatternDefinition(
    family="SAME_DIMENSION_TRANSITION",
    dimensions=("return_1h",),
    states=("LOW", "HIGH"),
    lag_minutes=60,
)
_SESSION_FLAGS = (
    "is_london_new_york_overlap",
    "is_london_session",
    "is_new_york_session",
    "is_asia_session",
)


def _provenance() -> EventEvidenceProvenance:
    return EventEvidenceProvenance(
        source_label="synthetic-event-evidence-v1",
        code_commit=_COMMIT,
        synthetic_manifest_sha256=_MANIFEST,
    )


def _at(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


def _submission(
    observation_id: str,
    available: datetime,
    *,
    horizon: int = 60,
    direction: str = "LONG",
    patterns: tuple[PatternDefinition, ...] = (_LOW,),
    segment: str = "2015",
    symbol: str = "EURUSD",
    timeframe: str = "5m",
    base: float = 1.0,
    stress: float = 0.5,
    exit_at: datetime | None = None,
) -> EventObservationSubmission:
    return EventObservationSubmission(
        observation_id=observation_id,
        annual_segment_label=segment,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon,
        available_at_utc=available,
        exit_timestamp_utc=(
            available + timedelta(minutes=horizon) if exit_at is None else exit_at
        ),
        direction=direction,
        net_pips_0p5=base,
        net_pips_1p0=stress,
        memberships=patterns,
    )


def _outcome(
    observation_id: str,
    available: datetime,
    *,
    horizon: int = 60,
    symbol: str = "EURUSD",
    timeframe: str = "5m",
) -> OutcomeObservation:
    return OutcomeObservation(
        observation_id=observation_id,
        symbol=symbol,
        timeframe=timeframe,
        available_at_utc=available,
        exit_timestamp_utc=available + timedelta(minutes=horizon),
        horizon_minutes=horizon,
        long_net_pips_0p5=1.25,
        short_net_pips_0p5=-1.25,
        long_net_pips_1p0=0.25,
        short_net_pips_1p0=-2.25,
    )


def _feature(observation_id: str, available: datetime) -> FeatureObservation:
    values: dict[str, object] = {name: None for name in CONTINUOUS_FEATURES}
    values["return_1h"] = 0.0
    values.update({name: False for name in _SESSION_FLAGS})
    return FeatureObservation(
        observation_id=observation_id,
        symbol="EURUSD",
        timeframe="5m",
        available_at_utc=available,
        values=values,
    )


def _scope(document: dict[str, object], scope_id: str) -> dict[str, object]:
    scopes = document["overlap_scopes"]
    assert isinstance(scopes, list)
    for scope in scopes:
        assert isinstance(scope, dict)
        if scope["scope_id"] == scope_id:
            return scope
    raise AssertionError(scope_id)


def _cross(document: dict[str, object], scope_id: str) -> dict[str, object]:
    scopes = document["cross_horizon_scopes"]
    assert isinstance(scopes, list)
    for scope in scopes:
        assert isinstance(scope, dict)
        if scope["scope_id"] == scope_id:
            return scope
    raise AssertionError(scope_id)


def _pattern(
    document: dict[str, object],
    *,
    direction: str,
    state: str,
) -> dict[str, object]:
    rows = document["pattern_memberships"]
    assert isinstance(rows, list)
    matches = [
        row
        for row in rows
        if isinstance(row, dict)
        and row["direction"] == direction
        and row["states"] == [state]
    ]
    if len(matches) != 1:
        raise AssertionError(matches)
    return matches[0]


class EventLevelEvidenceTests(unittest.TestCase):
    def test_dec470_thresholds_and_search_universe_stay_frozen(self) -> None:
        self.assertEqual(protocol_fingerprint(), _PROTOCOL_FINGERPRINT)
        self.assertEqual(DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT, 89460)
        self.assertEqual(MIN_ANNUAL_EVALUABLE_SUPPORT, 75)
        self.assertEqual(MIN_CROSS_YEAR_EVALUABLE_SEGMENTS, 9)
        self.assertEqual(MIN_BASE_POSITIVE_FRACTION, 0.80)
        self.assertEqual(MIN_STRESS_POSITIVE_FRACTION, 2.0 / 3.0)
        self.assertEqual(MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5, 0.10)
        self.assertEqual(MIN_POOLED_MEAN_NET_PIPS_0P5, 0.25)
        self.assertEqual(MAX_SIGN_FLIPS, 3)
        self.assertEqual(NEAR_DUPLICATE_JACCARD, 0.90)
        self.assertEqual(DISCOVERY_SLIPPAGE_PIPS, 0.5)
        self.assertEqual(STRESS_SLIPPAGE_PIPS, 1.0)
        contract = event_level_evidence_contract()
        recorded = contract["dec470_thresholds_recorded_not_applied"]
        assert isinstance(recorded, dict)
        self.assertFalse(recorded["applied_as_event_acceptance_gate"])
        self.assertFalse(recorded["retuned"])
        self.assertEqual(recorded["minimum_annual_evaluable_support"], 75)
        self.assertEqual(
            contract["search_universe_directional_hypotheses_per_annual_segment"],
            89460,
        )
        calibration = contract["correlated_noise_calibration"]
        assert isinstance(calibration, dict)
        self.assertEqual(calibration["experiment_id"], CORRELATED_NOISE_CALIBRATION_EXPERIMENT)
        self.assertEqual(calibration["status"], "RECORDED_CONSTRAINT_NOT_A_THRESHOLD")
        self.assertFalse(calibration["used_to_retune_dec470"])
        self.assertIn("4922", str(calibration["summary"]))
        self.assertFalse(contract["dec470_thresholds_modified"])
        self.assertFalse(HISTORICAL_ARTIFACT_READ_AUTHORIZED)
        self.assertFalse(HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED)
        self.assertFalse(STRATEGY_V1_SYNTHESIS_AUTHORIZED)
        self.assertFalse(STATISTICAL_PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)
        self.assertFalse(WORKFLOW_ACTIVATION_AUTHORIZED)
        self.assertFalse(DEC629_ADOPTED)
        self.assertFalse(DEC630_ADOPTED)
        self.assertFalse(ANNUAL_RUN_385_CONSUMED)

    def test_non_overlapping_and_touching_windows_stay_separate_events(self) -> None:
        start = _at(2015, 1, 2)
        document, raw = compile_event_evidence(
            (
                _submission("a", start),
                _submission("b", start + timedelta(minutes=60)),
            ),
            _provenance(),
        )
        scope = _scope(document, "2015|EURUSD|5m|60")
        self.assertEqual(scope["raw_observation_support"], 2)
        self.assertEqual(scope["unique_observed_event_count"], 2)
        self.assertEqual(scope["overlapping_event_count"], 0)
        self.assertEqual(scope["overlapping_pair_count"], 0)
        self.assertEqual(scope["connected_episode_group_count"], 2)
        self.assertEqual(scope["candidate_effective_independent_sample_size"], 2)
        self.assertFalse(
            scope["candidate_effective_independent_sample_size_is_an_independent_trial_count"]
        )
        self.assertFalse(scope["episode_groups_are_statistically_independent"])
        groups = scope["episode_groups"]
        assert isinstance(groups, list)
        self.assertTrue(
            all(
                isinstance(group, dict)
                and group["statistically_independent_of_other_groups"] is False
                for group in groups
            )
        )
        self.assertTrue(raw.endswith(b"\n"))
        self.assertEqual(json.loads(raw), document)

    def test_partial_overlap_is_one_episode_and_not_two_trials(self) -> None:
        start = _at(2015, 2, 2)
        document, _raw = compile_event_evidence(
            (
                _submission("left", start),
                _submission("right", start + timedelta(minutes=30)),
            ),
            _provenance(),
        )
        scope = _scope(document, "2015|EURUSD|5m|60")
        self.assertEqual(scope["overlapping_event_count"], 2)
        self.assertEqual(scope["overlapping_pair_count"], 1)
        self.assertEqual(scope["connected_episode_group_count"], 1)
        self.assertEqual(scope["candidate_effective_independent_sample_size"], 1)
        self.assertFalse(
            scope["candidate_effective_independent_sample_size_is_an_independent_trial_count"]
        )

    def test_chained_overlap_connects_events_that_do_not_overlap_directly(self) -> None:
        start = _at(2015, 3, 2)
        document, _raw = compile_event_evidence(
            (
                _submission("c", start + timedelta(minutes=80), patterns=(_LOW,)),
                _submission("a", start, patterns=(_LOW,)),
                _submission("b", start + timedelta(minutes=30), patterns=(_HIGH,)),
            ),
            _provenance(),
        )
        scope = _scope(document, "2015|EURUSD|5m|60")
        self.assertEqual(scope["unique_observed_event_count"], 3)
        self.assertEqual(scope["overlapping_pair_count"], 2)
        self.assertEqual(scope["connected_episode_group_count"], 1)
        self.assertEqual(scope["candidate_effective_independent_sample_size"], 1)
        ends = _pattern(document, direction="LONG", state="LOW")
        middle = _pattern(document, direction="LONG", state="HIGH")
        self.assertEqual(ends["raw_membership_support"], 2)
        self.assertEqual(ends["direct_overlap_component_count"], 2)
        self.assertEqual(ends["direct_overlapping_pair_count"], 0)
        self.assertEqual(ends["candidate_effective_independent_sample_size"], 1)
        self.assertFalse(ends["support_is_an_independent_trial_count"])
        self.assertEqual(middle["candidate_effective_independent_sample_size"], 1)
        dependence = document["hypothesis_dependence"]
        assert isinstance(dependence, dict)
        self.assertEqual(dependence["events_shared_by_multiple_hypotheses"], 0)
        self.assertFalse(dependence["independence_across_hypotheses_established"])
        self.assertFalse(dependence["near_duplicate_jaccard_threshold_applied"])
        self.assertEqual(dependence["patterns_dropped"], 0)

    def test_nested_horizons_share_a_cross_horizon_episode(self) -> None:
        start = _at(2015, 4, 2)
        document, _raw = compile_event_evidence(
            (
                _submission("bar-1", start, horizon=240, base=2.0, stress=1.0),
                _submission(
                    "bar-1",
                    start + timedelta(minutes=60),
                    horizon=60,
                    base=-0.5,
                    stress=-1.5,
                ),
            ),
            _provenance(),
        )
        long_horizon = _scope(document, "2015|EURUSD|5m|240")
        short_horizon = _scope(document, "2015|EURUSD|5m|60")
        self.assertEqual(long_horizon["candidate_effective_independent_sample_size"], 1)
        self.assertEqual(short_horizon["candidate_effective_independent_sample_size"], 1)
        self.assertEqual(long_horizon["overlapping_pair_count"], 0)
        cross = _cross(document, "2015|EURUSD|5m|horizons")
        self.assertEqual(cross["groups_containing_multiple_horizons"], 1)
        self.assertEqual(cross["overlapping_pair_count"], 1)
        self.assertEqual(cross["connected_episode_group_count"], 1)
        self.assertEqual(cross["within_horizon_candidate_sum"], 2)
        self.assertFalse(
            cross["within_horizon_candidate_sum_is_a_global_independent_sample_size"]
        )
        self.assertFalse(
            cross["candidate_effective_independent_sample_size_is_an_independent_trial_count"]
        )
        reuse = document["observation_id_reuse"]
        assert isinstance(reuse, dict)
        expected = reuse["expected_multi_horizon"]
        assert isinstance(expected, list)
        self.assertEqual(len(expected), 1)
        assert isinstance(expected[0], dict)
        self.assertEqual(expected[0]["horizons_minutes"], [60, 240])
        self.assertFalse(expected[0]["merged_into_one_event"])
        self.assertEqual(reuse["unresolved_reuse"], [])
        counts = document["counts"]
        assert isinstance(counts, dict)
        self.assertEqual(counts["event_count"], 2)
        self.assertEqual(counts["sum_of_within_horizon_candidate_sizes"], 2)
        self.assertFalse(
            counts["sum_of_within_horizon_candidate_sizes_is_a_global_independent_sample_size"]
        )

    def test_duplicate_and_contradictory_events_fail(self) -> None:
        start = _at(2015, 5, 2)
        original = _submission("dup", start)
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_DUPLICATE_MEASUREMENT"):
            compile_event_evidence((original, original), _provenance())
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_CONTRADICTORY_OUTCOME"):
            compile_event_evidence(
                (original, _submission("dup", start, base=3.0, stress=2.0)),
                _provenance(),
            )
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_CONTRADICTORY_MEMBERSHIP"):
            compile_event_evidence(
                (original, _submission("dup", start, patterns=(_HIGH,))),
                _provenance(),
            )
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_CONTRADICTORY_TIMESTAMPS"):
            compile_event_evidence(
                (original, _submission("dup", start + timedelta(minutes=120))),
                _provenance(),
            )
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_DUPLICATE_MEMBERSHIP"):
            _submission("dup", start, patterns=(_LOW, _LOW))

    def test_shared_events_and_both_directions_are_dependent_hypotheses(self) -> None:
        start = _at(2015, 6, 2)
        outcome = _outcome("shared", start)
        feature = _feature("shared", start)
        long_row = submission_from_outcome(
            outcome,
            annual_segment_label="2015",
            direction="LONG",
            memberships=(_LOW, _HIGH),
            feature=feature,
        )
        short_row = submission_from_outcome(
            outcome,
            annual_segment_label="2015",
            direction="SHORT",
            memberships=(_LOW,),
            feature=feature,
        )
        self.assertEqual(long_row.net_pips_0p5, 1.25)
        self.assertEqual(short_row.net_pips_1p0, -2.25)
        self.assertEqual(long_row.event_identity, short_row.event_identity)
        document, _raw = compile_event_evidence((short_row, long_row), _provenance())
        scope = _scope(document, "2015|EURUSD|5m|60")
        self.assertEqual(scope["raw_observation_support"], 2)
        self.assertEqual(scope["unique_observed_event_count"], 1)
        self.assertEqual(scope["candidate_effective_independent_sample_size"], 1)
        dependence = document["hypothesis_dependence"]
        assert isinstance(dependence, dict)
        self.assertEqual(dependence["events_shared_by_multiple_hypotheses"], 1)
        self.assertEqual(dependence["max_hypotheses_sharing_one_event"], 3)
        self.assertEqual(dependence["hypotheses_that_share_an_event"], 3)
        self.assertFalse(dependence["independence_across_hypotheses_established"])
        self.assertEqual(dependence["patterns_dropped"], 0)
        events = document["events"]
        assert isinstance(events, list) and len(events) == 1
        assert isinstance(events[0], dict)
        self.assertFalse(events[0]["recovered_from_event_fingerprint"])
        self.assertEqual(events[0]["observation_id"], "shared")
        legacy_fingerprint = hashlib.sha256(b"shared").hexdigest()
        self.assertNotEqual(events[0]["event_identity"], legacy_fingerprint)
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_FEATURE_OUTCOME_MISMATCH"):
            submission_from_outcome(
                outcome,
                annual_segment_label="2015",
                direction="LONG",
                memberships=(_LOW,),
                feature=_feature("other", start),
            )

    def test_cross_symbol_and_cross_timeframe_events_are_not_declared_independent(self) -> None:
        start = _at(2015, 7, 2)
        document, _raw = compile_event_evidence(
            (
                _submission("same-label", start, symbol="EURUSD", timeframe="5m"),
                _submission("same-label", start, symbol="GBPUSD", timeframe="5m"),
                _submission("other", start, symbol="EURUSD", timeframe="1h"),
            ),
            _provenance(),
        )
        self.assertEqual(len(document["overlap_scopes"]), 3)
        for scope in document["overlap_scopes"]:
            assert isinstance(scope, dict)
            self.assertEqual(scope["unique_observed_event_count"], 1)
            self.assertFalse(
                scope["candidate_effective_independent_sample_size_is_an_independent_trial_count"]
            )
        cross_scope = document["cross_scope_dependence"]
        assert isinstance(cross_scope, dict)
        self.assertFalse(cross_scope["cross_symbol_dependence_measured"])
        self.assertFalse(cross_scope["cross_timeframe_dependence_measured"])
        self.assertFalse(cross_scope["independence_established"])
        counts = document["counts"]
        assert isinstance(counts, dict)
        self.assertEqual(counts["sum_of_within_horizon_candidate_sizes"], 3)
        self.assertFalse(
            counts["sum_of_within_horizon_candidate_sizes_is_a_global_independent_sample_size"]
        )
        reuse = document["observation_id_reuse"]
        assert isinstance(reuse, dict)
        unresolved = reuse["unresolved_reuse"]
        assert isinstance(unresolved, list) and len(unresolved) == 1
        assert isinstance(unresolved[0], dict)
        self.assertEqual(unresolved[0]["observation_id"], "same-label")
        self.assertFalse(unresolved[0]["merged"])
        self.assertFalse(unresolved[0]["independence_established"])

    def test_annual_segment_boundaries_reject_windows_that_leave_the_segment(self) -> None:
        inside = _submission(
            "ytd",
            _at(2026, 8, 20, 22),
            segment="2026_YTD_TO_2026_08_20",
        )
        document, _raw = compile_event_evidence((inside,), _provenance())
        self.assertEqual(
            _scope(document, "2026_YTD_TO_2026_08_20|EURUSD|5m|60")[
                "unique_observed_event_count"
            ],
            1,
        )
        cases = (
            ("late", lambda: _submission("late", _at(2015, 12, 31, 23, 30))),
            ("next-year", lambda: _submission("next-year", _at(2016, 1, 1), segment="2015")),
            (
                "ytd-late",
                lambda: _submission(
                    "ytd-late",
                    _at(2026, 8, 20, 23),
                    segment="2026_YTD_TO_2026_08_20",
                ),
            ),
            (
                "ytd-long",
                lambda: _submission(
                    "ytd-long",
                    _at(2026, 8, 20, 20),
                    horizon=240,
                    segment="2026_YTD_TO_2026_08_20",
                ),
            ),
        )
        for name, build in cases:
            with self.subTest(observation_id=name):
                with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_SEGMENT_BOUNDARY"):
                    build()
        early = _at(2015, 1, 2)
        later = _at(2016, 1, 2)
        separated, _raw = compile_event_evidence(
            (
                _submission("year-a", early, segment="2015"),
                _submission("year-b", later, segment="2016"),
            ),
            _provenance(),
        )
        self.assertEqual(len(separated["pattern_memberships"]), 2)
        self.assertEqual(
            {row["annual_segment_label"] for row in separated["pattern_memberships"]},
            {"2015", "2016"},
        )

    def test_missing_or_malformed_event_provenance_fails(self) -> None:
        start = _at(2015, 1, 3)
        valid = _submission("ok", start, patterns=(_TRANSITION,))
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_MALFORMED_PROVENANCE"):
            EventEvidenceProvenance(
                source_label="",
                code_commit=_COMMIT,
                synthetic_manifest_sha256=_MANIFEST,
            )
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_MALFORMED_PROVENANCE"):
            EventEvidenceProvenance(
                source_label="synthetic",
                code_commit="main",
                synthetic_manifest_sha256=_MANIFEST,
            )
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_MALFORMED_PROVENANCE"):
            EventEvidenceProvenance(
                source_label="synthetic",
                code_commit=_COMMIT,
                synthetic_manifest_sha256="not-a-hash",
            )
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_TIMESTAMP_NOT_UTC"):
            _submission("naive", datetime(2015, 1, 3))
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_WINDOW_BOUNDARY"):
            _submission("bad-exit", start, exit_at=start + timedelta(minutes=61))
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_MALFORMED_OUTCOME"):
            _submission("nan", start, base=float("nan"))
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_MALFORMED_OBSERVATION"):
            _submission("bad-symbol", start, symbol="BTCUSD")
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_MALFORMED_OBSERVATION"):
            _submission("bad-horizon", start, horizon=15)
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_MALFORMED_OBSERVATION"):
            _submission("bad-direction", start, direction="BOTH")
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_INCOMPLETE_MEMBERSHIP"):
            _submission("empty-membership", start, patterns=())
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_MALFORMED_OBSERVATION"):
            _submission("bad\nid", start)
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_INCOMPLETE"):
            compile_event_evidence((), _provenance())
        document, raw = compile_event_evidence((valid,), _provenance())
        membership = document["pattern_memberships"][0]
        self.assertEqual(membership["lag_minutes"], 60)
        self.assertEqual(membership["family"], "SAME_DIMENSION_TRANSITION")
        validate_event_evidence(document)
        validate_event_evidence(raw)

    def test_output_is_identical_across_repeated_and_reordered_executions(self) -> None:
        start = _at(2015, 8, 3)
        rows = [
            _submission("z", start + timedelta(minutes=180), direction="SHORT", patterns=(_HIGH,)),
            _submission("a", start, patterns=(_TRANSITION, _LOW)),
            _submission("m", start + timedelta(minutes=30), symbol="USDJPY"),
        ]
        first, first_raw = compile_event_evidence(rows, _provenance())
        second, second_raw = compile_event_evidence(tuple(reversed(rows)), _provenance())
        third, third_raw = compile_event_evidence(rows, _provenance())
        self.assertEqual(first_raw, second_raw)
        self.assertEqual(second_raw, third_raw)
        self.assertEqual(first["content_sha256"], second["content_sha256"])
        body = {key: value for key, value in third.items() if key != "content_sha256"}
        self.assertEqual(
            third["content_sha256"],
            hashlib.sha256(
                (
                    json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False)
                    + "\n"
                ).encode("utf-8")
            ).hexdigest(),
        )
        self.assertEqual(
            [event["observation_id"] for event in first["events"]],
            ["a", "z", "m"],
        )

    def test_independence_and_significance_claims_are_rejected(self) -> None:
        document, _raw = compile_event_evidence(
            (_submission("solo", _at(2015, 9, 2)),),
            _provenance(),
        )
        limits = document["statistical_limits"]
        assert isinstance(limits, dict)
        self.assertFalse(limits["statistical_inference_performed"])
        self.assertEqual(limits["p_values"], "UNAVAILABLE_NOT_COMPUTED")
        self.assertEqual(limits["confidence_intervals"], "UNAVAILABLE_NOT_COMPUTED")
        self.assertEqual(limits["multiple_comparison_adjustment"], "UNAVAILABLE_NOT_COMPUTED")
        self.assertFalse(limits["statistical_significance_claimed"])
        self.assertFalse(limits["profitability_claimed"])
        self.assertFalse(limits["annual_aggregate_counts_are_significance"])
        self.assertFalse(limits["episode_groups_are_statistically_independent"])
        self.assertIn("89460", limits["subsequent_requirements"]["multiple_hypothesis_correction"])
        self.assertFalse(
            document["structural_validation_is_independent_frozen_evidence_validation"]
        )
        self.assertEqual(document["evidence_basis"], EVIDENCE_BASIS)

        tampered = json.loads(json.dumps(document))
        tampered["statistical_limits"]["statistical_significance_claimed"] = True
        tampered["statistical_limits"]["p_values"] = 0.01
        body = {key: value for key, value in tampered.items() if key != "content_sha256"}
        tampered["content_sha256"] = hashlib.sha256(
            (json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode(
                "utf-8"
            )
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_INDEPENDENCE_CLAIM"):
            validate_event_evidence(tampered)

        groups = document["overlap_scopes"][0]["episode_groups"]
        group_tamper = json.loads(json.dumps(document))
        group_tamper["overlap_scopes"][0]["episode_groups"][0][
            "statistically_independent_of_other_groups"
        ] = True
        group_body = {
            key: value for key, value in group_tamper.items() if key != "content_sha256"
        }
        group_tamper["content_sha256"] = hashlib.sha256(
            (
                json.dumps(group_body, sort_keys=True, separators=(",", ":"), allow_nan=False)
                + "\n"
            ).encode("utf-8")
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_INDEPENDENCE_CLAIM"):
            validate_event_evidence(group_tamper)
        self.assertEqual(len(groups), 1)

    def test_integrity_failures_and_fingerprint_recovery_refusal(self) -> None:
        document, raw = compile_event_evidence(
            (_submission("intact", _at(2015, 10, 2)),),
            _provenance(),
        )
        broken = bytearray(raw)
        broken[-4] = (broken[-4] + 1) % 256
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_INTEGRITY"):
            validate_event_evidence(bytes(broken))
        edited = json.loads(raw)
        edited["counts"]["event_count"] = 99
        body = {key: value for key, value in edited.items() if key != "content_sha256"}
        edited["content_sha256"] = hashlib.sha256(
            (json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode(
                "utf-8"
            )
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_INTEGRITY"):
            validate_event_evidence(edited)
        fingerprint_edit = json.loads(raw)
        fingerprint_edit["events"][0]["directional_outcomes"][0]["memberships"][0][
            "canonical_pattern_fingerprint"
        ] = "0" * 64
        fingerprint_body = {
            key: value for key, value in fingerprint_edit.items() if key != "content_sha256"
        }
        fingerprint_edit["content_sha256"] = hashlib.sha256(
            (
                json.dumps(
                    fingerprint_body,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "EVENT_EVIDENCE_FINGERPRINT_MISMATCH"):
            validate_event_evidence(fingerprint_edit)
        with self.assertRaisesRegex(
            ValueError,
            "EVENT_EVIDENCE_EVENT_FINGERPRINT_RECOVERY_REFUSED",
        ):
            recover_event_ids_from_event_fingerprint(document["events"][0]["event_identity"])
        identity = event_identity_for(
            observation_id="intact",
            annual_segment_label="2015",
            symbol="EURUSD",
            timeframe="5m",
            horizon_minutes=60,
        )
        self.assertEqual(document["events"][0]["event_identity"], identity)
        self.assertNotEqual(identity, hashlib.sha256(b"intact").hexdigest())

    def test_large_synthetic_input_counts_pairs_without_unbounded_memory(self) -> None:
        clique_size = 2000
        separated_size = 2000
        clique_start = _at(2015, 1, 5)
        separated_start = _at(2016, 1, 5)
        rows: list[EventObservationSubmission] = []
        for index in range(clique_size):
            rows.append(_submission(f"clique-{index}", clique_start, base=float(index % 7)))
        for index in range(separated_size):
            rows.append(
                _submission(
                    f"separated-{index}",
                    separated_start + timedelta(minutes=60 * index),
                    segment="2016",
                    base=0.0,
                    stress=-1.0,
                )
            )
        order = list(range(len(rows)))
        random.Random(20261119).shuffle(order)
        shuffled = [rows[index] for index in order]
        tracemalloc.start()
        document, raw = compile_event_evidence(shuffled, _provenance())
        repeated, repeated_raw = compile_event_evidence(rows, _provenance())
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertEqual(raw, repeated_raw)
        self.assertEqual(document["content_sha256"], repeated["content_sha256"])
        clique = _scope(document, "2015|EURUSD|5m|60")
        separated = _scope(document, "2016|EURUSD|5m|60")
        self.assertEqual(clique["unique_observed_event_count"], clique_size)
        self.assertEqual(clique["overlapping_pair_count"], clique_size * (clique_size - 1) // 2)
        self.assertEqual(clique["connected_episode_group_count"], 1)
        self.assertEqual(clique["candidate_effective_independent_sample_size"], 1)
        self.assertFalse(
            clique["candidate_effective_independent_sample_size_is_an_independent_trial_count"]
        )
        self.assertEqual(separated["overlapping_pair_count"], 0)
        self.assertEqual(separated["connected_episode_group_count"], separated_size)
        self.assertEqual(
            separated["candidate_effective_independent_sample_size"],
            separated_size,
        )
        self.assertFalse(
            separated["candidate_effective_independent_sample_size_is_an_independent_trial_count"]
        )
        counts = document["counts"]
        assert isinstance(counts, dict)
        self.assertEqual(counts["event_count"], clique_size + separated_size)
        self.assertFalse(
            counts["sum_of_within_horizon_candidate_sizes_is_a_global_independent_sample_size"]
        )
        self.assertLess(peak, 80 * 1024 * 1024)
        self.assertLess(len(raw), 20 * 1024 * 1024)

    def test_existing_miner_fingerprints_stay_unchanged(self) -> None:
        available = _at(2015, 1, 2)
        feature = _feature("miner-row", available)
        outcome = _outcome("miner-row", available)

        def snapshot() -> tuple[object, ...]:
            result = mine_annual_catalogue_cell(
                (feature,),
                (outcome,),
                symbol="EURUSD",
                timeframe="5m",
                horizon_minutes=60,
                annual_segment_label="2015",
            )
            return tuple(
                (
                    row.annual_record_id,
                    row.canonical_pattern_fingerprint,
                    row.event_fingerprint,
                    row.statistics.support,
                    row.statistics.evaluable,
                    row.family,
                    row.dimensions,
                    row.states,
                    row.lag_minutes,
                    row.direction,
                    row.symbol,
                    row.timeframe,
                    row.horizon_minutes,
                    row.annual_segment_label,
                )
                for row in result.records
            )

        before = snapshot()
        compile_event_evidence(
            (
                submission_from_outcome(
                    outcome,
                    annual_segment_label="2015",
                    direction="LONG",
                    memberships=(_LOW,),
                    feature=feature,
                ),
            ),
            _provenance(),
        )
        after = snapshot()
        self.assertEqual(before, after)
        self.assertEqual(len(before), 4970)
        self.assertEqual(
            set(AnnualPatternRecord.__dataclass_fields__),
            {
                "annual_record_id",
                "canonical_pattern_fingerprint",
                "annual_segment_label",
                "symbol",
                "timeframe",
                "horizon_minutes",
                "direction",
                "family",
                "dimensions",
                "states",
                "lag_minutes",
                "event_fingerprint",
                "statistics",
            },
        )
        source = Path(
            "src/fmp/discovery/annual_pattern_catalogue_event_evidence.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("requests", source)

    def test_event_identity_does_not_depend_on_submission_order_or_direction(self) -> None:
        start = _at(2015, 11, 2)
        long_row = _submission("stable", start, direction="LONG", base=1.0, stress=0.0)
        short_row = _submission("stable", start, direction="SHORT", base=-1.0, stress=-2.0)
        self.assertEqual(long_row.event_identity, short_row.event_identity)
        self.assertEqual(
            long_row.event_identity,
            event_identity_for(
                observation_id="stable",
                annual_segment_label="2015",
                symbol="EURUSD",
                timeframe="5m",
                horizon_minutes=60,
            ),
        )
        document, _raw = compile_event_evidence((short_row, long_row), _provenance())
        self.assertEqual(document["protocol_fingerprint"], _PROTOCOL_FINGERPRINT)
        self.assertFalse(document["annual_catalogue_schema_modified"])
        self.assertFalse(document["recovered_event_ids_from_event_fingerprint"])
        self.assertFalse(document["provenance"]["historical_artifact_read"])
