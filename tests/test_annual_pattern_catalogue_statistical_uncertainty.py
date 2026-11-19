from __future__ import annotations

import hashlib
import inspect
import json
import random
import tracemalloc
import unittest
from datetime import datetime, timedelta, timezone

from fmp.discovery import annual_pattern_catalogue_cross_year as cross_year
from fmp.discovery.annual_pattern_catalogue_event_evidence import (
    ANNUAL_RUN_385_CONSUMED,
    DEC629_ADOPTED,
    DEC630_ADOPTED,
    HISTORICAL_ARTIFACT_READ_AUTHORIZED,
    HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
    STATISTICAL_PROMOTION_AUTHORIZED,
    STRATEGY_V1_SYNTHESIS_AUTHORIZED,
    TRADING_AUTHORIZED,
    WORKFLOW_ACTIVATION_AUTHORIZED,
    EventEvidenceProvenance,
    EventObservationSubmission,
    compile_event_evidence,
    event_level_evidence_contract,
    recover_event_ids_from_event_fingerprint,
)
from fmp.discovery.annual_pattern_catalogue_protocol import (
    DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
    protocol_fingerprint,
)
from fmp.discovery.annual_pattern_catalogue_statistical_uncertainty import (
    BOOTSTRAP_DRAWS,
    CLOSED_FORM_REPLICATIONS,
    EXPECTED_PROTOCOL_FINGERPRINT,
    FORBIDDEN_TUNING_SEEDS,
    HOLM_METHOD_CHECK_FAMILY,
    PREDECLARED_BLOCK_LENGTHS,
    PREDECLARED_HAC_LAGS,
    PRIMARY_CALIBRATION_SEED,
    VARIABILITY_SEEDS,
    UncertaintyProvenance,
    assess_event_evidence_uncertainty,
    compile_synthetic_calibration,
    effective_sample_size_from_overlap,
    holm_adjusted_p_values,
    iid_normal_interval,
    independent_column_block_bootstrap_interval,
    measure_representative_workload,
    moving_block_bootstrap_interval,
    newey_west_interval,
    refuse_catalogue_multiple_testing,
    shared_clock_block_bootstrap_interval,
    statistical_uncertainty_contract,
    validate_uncertainty_document,
)


_COMMIT = "10ac7086c18ca1002a4529e37dd36e6c36983043"
_MANIFEST = hashlib.sha256(b"synthetic-statistical-uncertainty-v1\n").hexdigest()
_EVENT_MANIFEST = hashlib.sha256(b"synthetic-event-evidence-v1\n").hexdigest()
_LOW = ("SNAPSHOT_SINGLE", ("return_1h",), ("LOW",), None)
_LONDON = ("SNAPSHOT_SINGLE", ("session_state",), ("LONDON",), None)


def _provenance() -> UncertaintyProvenance:
    return UncertaintyProvenance(
        source_label="synthetic-statistical-uncertainty-v1",
        code_commit=_COMMIT,
        synthetic_manifest_sha256=_MANIFEST,
    )


def _pattern(spec: tuple[str, tuple[str, ...], tuple[str, ...], int | None]):
    from fmp.discovery.annual_pattern_catalogue_protocol import PatternDefinition

    family, dimensions, states, lag = spec
    return PatternDefinition(
        family=family,
        dimensions=dimensions,
        states=states,
        lag_minutes=lag,
    )


def _at(hour: int, minute: int = 0) -> datetime:
    return datetime(2015, 1, 2, hour, minute, tzinfo=timezone.utc)


def _submission(
    observation_id: str,
    available: datetime,
    *,
    horizon: int = 60,
    patterns: tuple[tuple[str, tuple[str, ...], tuple[str, ...], int | None], ...] = (_LOW,),
    base: float = 1.0,
) -> EventObservationSubmission:
    return EventObservationSubmission(
        observation_id=observation_id,
        annual_segment_label="2015",
        symbol="EURUSD",
        timeframe="5m",
        horizon_minutes=horizon,
        available_at_utc=available,
        exit_timestamp_utc=available + timedelta(minutes=horizon),
        direction="LONG",
        net_pips_0p5=base,
        net_pips_1p0=base - 1.0,
        memberships=tuple(_pattern(item) for item in patterns),
    )


def _event_document() -> dict[str, object]:
    document, _raw = compile_event_evidence(
        [
            _submission("obs-a", _at(0), patterns=(_LOW, _LONDON), base=2.0),
            _submission("obs-a", _at(0), horizon=240, patterns=(_LOW, _LONDON), base=4.0),
            _submission("obs-b", _at(0, 30), patterns=(_LOW,), base=0.0),
            _submission("obs-c", _at(5), patterns=(_LONDON,), base=-2.0),
        ],
        EventEvidenceProvenance(
            source_label="synthetic-event-evidence-v1",
            code_commit=_COMMIT,
            synthetic_manifest_sha256=_EVENT_MANIFEST,
        ),
    )
    return document


def _scenario(document: dict[str, object], name: str) -> dict[str, object]:
    scenarios = document["scenarios"]
    assert isinstance(scenarios, list)
    for scenario in scenarios:
        assert isinstance(scenario, dict)
        if scenario["scenario_name"] == name:
            return scenario
    raise AssertionError(name)


def _rate(scenario: dict[str, object], method: str, field: str) -> float:
    closed = scenario["closed_form"]
    assert isinstance(closed, dict)
    payload = closed[method]
    assert isinstance(payload, dict)
    value = payload[field]
    assert isinstance(value, float)
    return value


def _comparison_width(scenario: dict[str, object], name: str) -> float:
    payload = _comparison_payload(scenario, name)
    value = payload["median_interval_width"]
    assert isinstance(value, float)
    return value


def _comparison_rate(scenario: dict[str, object], name: str, field: str) -> float:
    value = _comparison_payload(scenario, name)[field]
    assert isinstance(value, float)
    return value


def _comparison_payload(scenario: dict[str, object], name: str) -> dict[str, object]:
    comparisons = scenario["dependence_comparisons"]
    assert isinstance(comparisons, dict)
    payload = comparisons[name]
    assert isinstance(payload, dict)
    return payload


_CACHE: dict[str, object] = {}


def setUpModule() -> None:
    tracemalloc.start()
    document, raw = compile_synthetic_calibration(_provenance())
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    _CACHE["document"] = document
    _CACHE["raw"] = raw
    _CACHE["compile_peak_bytes"] = peak


def _document() -> dict[str, object]:
    document = _CACHE["document"]
    assert isinstance(document, dict)
    return document


def _raw() -> bytes:
    raw = _CACHE["raw"]
    assert isinstance(raw, bytes)
    return raw


class StatisticalUncertaintyContractTests(unittest.TestCase):
    def test_frozen_universe_and_closed_authorizations(self) -> None:
        self.assertEqual(DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT, 89460)
        self.assertEqual(protocol_fingerprint(), EXPECTED_PROTOCOL_FINGERPRINT)
        contract = statistical_uncertainty_contract()
        self.assertEqual(contract["governing_method"], "DISCOVERY_FIRST_ANNUAL_PATTERN_CATALOGUE")
        self.assertEqual(contract["pattern_tool"], "statistical-uncertainty-v1")
        self.assertFalse(contract["episode_groups_are_independent_trials"])
        self.assertFalse(contract["catalogue_holm_applied"])
        authorizations = contract["authorizations"]
        assert isinstance(authorizations, dict)
        self.assertTrue(authorizations)
        self.assertFalse(any(authorizations.values()))
        self.assertFalse(HISTORICAL_ARTIFACT_READ_AUTHORIZED)
        self.assertFalse(HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED)
        self.assertFalse(STRATEGY_V1_SYNTHESIS_AUTHORIZED)
        self.assertFalse(STATISTICAL_PROMOTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)
        self.assertFalse(WORKFLOW_ACTIVATION_AUTHORIZED)
        self.assertFalse(DEC629_ADOPTED)
        self.assertFalse(DEC630_ADOPTED)
        self.assertFalse(ANNUAL_RUN_385_CONSUMED)
        event_limits = event_level_evidence_contract()["statistical_limits"]
        assert isinstance(event_limits, dict)
        self.assertEqual(event_limits["p_values"], "UNAVAILABLE_NOT_COMPUTED")
        self.assertFalse(event_limits["episode_groups_are_statistically_independent"])
        source = inspect.getsource(cross_year._statistical_block)
        self.assertIn("UNAVAILABLE_NOT_COMPUTED", source)
        self.assertIn("independent_trial_standard_errors", source)
        self.assertIn("multiple_comparison_adjustment", source)

    def test_episode_groups_do_not_become_effective_sample_size(self) -> None:
        payload = effective_sample_size_from_overlap(
            raw_observation_support=12,
            connected_episode_group_count=3,
        )
        self.assertEqual(payload["status"], "UNAVAILABLE")
        self.assertIsNone(payload["value"])
        self.assertFalse(payload["episode_group_count_used_as_value"])
        self.assertFalse(payload["episode_groups_are_independent_trials"])

    def test_catalogue_holm_is_not_applied(self) -> None:
        payload = refuse_catalogue_multiple_testing()
        self.assertEqual(payload["status"], "NOT_APPLIED")
        self.assertFalse(payload["holm_applied_to_catalogue"])
        self.assertEqual(payload["family_size_per_annual_segment"], 89460)
        self.assertFalse(payload["shortlist_only_correction"])
        self.assertEqual(payload["individual_p_values"], "UNAVAILABLE")
        self.assertEqual(payload["selection_uncertainty"], "UNAVAILABLE")
        self.assertFalse(payload["optimized_on_observed_false_passes"])

    def test_holm_hand_calculation_and_refused_sources(self) -> None:
        adjusted = holm_adjusted_p_values(
            [0.01, 0.04, 0.03],
            source="known_sigma_gaussian_synthetic",
            assumptions_verified_for_synthetic_dgp=True,
        )
        self.assertEqual(adjusted["adjusted_p_values"], [0.03, 0.06, 0.06])
        self.assertFalse(adjusted["applied_to_annual_catalogue"])
        self.assertFalse(adjusted["assumptions_verified_for_catalogue"])
        withheld = holm_adjusted_p_values(
            [0.01],
            source="known_sigma_gaussian_synthetic",
            assumptions_verified_for_synthetic_dgp=False,
        )
        self.assertEqual(withheld["status"], "NOT_APPLIED")
        self.assertIsNone(withheld["adjusted_p_values"])
        for source in ("block_bootstrap", "dependence_preserving_resample", "annual_catalogue"):
            with self.assertRaises(ValueError) as caught:
                holm_adjusted_p_values(
                    [0.01],
                    source=source,
                    assumptions_verified_for_synthetic_dgp=True,
                )
            self.assertIn("STATISTICAL_UNCERTAINTY_P_VALUES_NOT_VALID", str(caught.exception))

    def test_intervals_match_hand_calculations(self) -> None:
        degenerate = iid_normal_interval([1.0, 1.0, 1.0, 1.0])
        self.assertEqual(degenerate["status"], "DEGENERATE_VARIANCE")
        self.assertIsNone(degenerate["standard_error"])
        interval = iid_normal_interval([1.0, 2.0, 3.0])
        self.assertAlmostEqual(float(interval["mean"]), 2.0)
        self.assertAlmostEqual(float(interval["standard_error"]), (1.0 / 3.0) ** 0.5)
        hac = newey_west_interval([1.0, 2.0, 3.0], 1)
        self.assertAlmostEqual(float(hac["long_run_variance"]), 2.0 / 3.0)
        self.assertAlmostEqual(float(hac["standard_error"]), (2.0 / 9.0) ** 0.5)
        constant_hac = newey_west_interval([2.0, 2.0, 2.0], 1)
        self.assertEqual(constant_hac["status"], "DEGENERATE_VARIANCE")
        with self.assertRaises(ValueError) as caught:
            newey_west_interval([1.0, 2.0, 3.0], 2)
        self.assertIn("STATISTICAL_UNCERTAINTY_LAG_NOT_PREDECLARED", str(caught.exception))
        self.assertEqual(PREDECLARED_HAC_LAGS, (1, 4, 8))
        self.assertEqual(PREDECLARED_BLOCK_LENGTHS, (1, 4, 8))

    def test_shared_clock_does_not_resample_columns_independently(self) -> None:
        columns = [[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]] * 2
        shared = shared_clock_block_bootstrap_interval(
            columns,
            1,
            draws=12,
            rng=random.Random(7),
        )
        column_intervals = shared["column_intervals"]
        assert isinstance(column_intervals, list)
        self.assertEqual(column_intervals[0]["low"], column_intervals[1]["low"])
        self.assertEqual(column_intervals[0]["high"], column_intervals[1]["high"])
        self.assertTrue(shared["resamples_each_time_once"])
        self.assertEqual(shared["p_value"], "NOT_COMPUTED")
        incorrect = independent_column_block_bootstrap_interval(
            columns,
            1,
            draws=12,
            rng=random.Random(7),
        )
        incorrect_columns = incorrect["column_intervals"]
        assert isinstance(incorrect_columns, list)
        self.assertNotEqual(
            (incorrect_columns[0]["low"], incorrect_columns[0]["high"]),
            (incorrect_columns[1]["low"], incorrect_columns[1]["high"]),
        )
        self.assertTrue(incorrect["independently_resampled_columns"])
        self.assertFalse(incorrect["recommended"])
        block = moving_block_bootstrap_interval(
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
            1,
            draws=BOOTSTRAP_DRAWS,
            rng=random.Random(9),
        )
        self.assertTrue(block["block_length_1_interprets_adjacent_outcomes_as_independent"])
        self.assertFalse(block["recommended"])
        self.assertEqual(block["p_value"], "NOT_COMPUTED")
        repeated = moving_block_bootstrap_interval(
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
            1,
            draws=BOOTSTRAP_DRAWS,
            rng=random.Random(9),
        )
        self.assertEqual(block, repeated)

    def test_stacked_duplicate_is_narrower_than_the_shared_series(self) -> None:
        values = [0.4, -1.2, 0.2, 0.8, -0.5, 1.1, -0.7, 0.3]
        single = iid_normal_interval(values)
        stacked = iid_normal_interval(values + values)
        self.assertLess(float(stacked["standard_error"]), float(single["standard_error"]) * 0.8)
        self.assertFalse(stacked["assumption_correct_for_overlapping_events"])
        self.assertFalse(stacked["portfolio_profit_interval"])

    def test_event_assessment_keeps_inference_unavailable(self) -> None:
        event_document = _event_document()
        assessment, raw = assess_event_evidence_uncertainty(event_document)
        self.assertEqual(assessment["inference_status"], "UNAVAILABLE")
        self.assertFalse(assessment["valid_sampling_uncertainty_established"])
        self.assertFalse(assessment["inference_authorized"])
        self.assertEqual(
            assessment["source_event_evidence_content_sha256"],
            event_document["content_sha256"],
        )
        quantities = assessment["quantities"]
        assert isinstance(quantities, dict)
        effective = quantities["effective_sample_size"]
        assert isinstance(effective, dict)
        self.assertEqual(effective["status"], "UNAVAILABLE")
        self.assertIsNone(effective["value"])
        self.assertFalse(effective["episode_group_count_used_as_value"])
        sampling = quantities["sampling_uncertainty"]
        assert isinstance(sampling, dict)
        self.assertEqual(sampling["status"], "UNAVAILABLE")
        self.assertIsNone(sampling["standard_error"])
        serial = quantities["serial_dependence_beyond_geometric_overlap"]
        assert isinstance(serial, dict)
        self.assertEqual(serial["status"], "UNAVAILABLE")
        multiple = quantities["multiple_hypothesis_and_selection_uncertainty"]
        assert isinstance(multiple, dict)
        self.assertEqual(multiple["family_size_per_annual_segment"], 89460)
        self.assertFalse(multiple["holm_applied_to_catalogue"])
        observed = assessment["observed_mean_net_pips_0p5"]
        assert isinstance(observed, dict)
        self.assertEqual(observed["status"], "DESCRIPTIVE_SAMPLE_MEAN")
        self.assertEqual(observed["sampling_uncertainty"], "UNAVAILABLE")
        self.assertEqual(observed["realizable_portfolio_profit"], "NOT_A_CLAIM")
        self.assertFalse(observed["simultaneously_executable"])
        self.assertEqual(observed["value"], (2.0 + 4.0 + 0.0 + -2.0) / 4.0)
        hypothesis = assessment["hypothesis_dependence"]
        assert isinstance(hypothesis, dict)
        self.assertGreaterEqual(int(hypothesis["events_shared_by_multiple_hypotheses"]), 1)
        self.assertEqual(hypothesis["shared_event_dependence_in_sampling_distribution"], "UNAVAILABLE")
        membership = assessment["membership"]
        assert isinstance(membership, dict)
        self.assertFalse(membership["caller_supplied_membership_is_feature_state_proof"])
        self.assertFalse(membership["asserted_membership_treated_as_feature_evidence"])
        self.assertEqual(assessment["event_fingerprint_recovery"], "REFUSED")
        counts = assessment["descriptive_counts"]
        assert isinstance(counts, dict)
        self.assertFalse(counts["episode_group_count_is_an_independent_trial_count"])
        self.assertFalse(counts["candidate_sum_used_as_effective_sample_size"])
        validated = validate_uncertainty_document(raw, event_document=event_document)
        self.assertEqual(validated["content_sha256"], assessment["content_sha256"])
        with self.assertRaises(ValueError) as independence:
            assess_event_evidence_uncertainty(event_document, assume_independence=True)
        self.assertIn(
            "STATISTICAL_UNCERTAINTY_INDEPENDENCE_ASSUMPTION_REFUSED",
            str(independence.exception),
        )
        with self.assertRaises(ValueError) as trials:
            assess_event_evidence_uncertainty(
                event_document,
                treat_episode_groups_as_independent_trials=True,
            )
        self.assertIn(
            "STATISTICAL_UNCERTAINTY_EPISODE_GROUPS_ARE_NOT_TRIALS",
            str(trials.exception),
        )
        with self.assertRaises(ValueError) as missing:
            validate_uncertainty_document(raw)
        self.assertIn(
            "STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE",
            str(missing.exception),
        )

    def test_event_fingerprint_recovery_stays_refused(self) -> None:
        with self.assertRaises(ValueError) as caught:
            recover_event_ids_from_event_fingerprint("ab" * 32)
        self.assertIn("EVENT_EVIDENCE_EVENT_FINGERPRINT_RECOVERY_REFUSED", str(caught.exception))

    def test_missing_and_invalid_provenance_fail_closed(self) -> None:
        with self.assertRaises(ValueError) as missing:
            compile_synthetic_calibration(None)
        self.assertIn("STATISTICAL_UNCERTAINTY_MISSING_PROVENANCE", str(missing.exception))
        with self.assertRaises(ValueError) as bad_commit:
            UncertaintyProvenance(
                source_label="synthetic-statistical-uncertainty-v1",
                code_commit="not-a-commit",
                synthetic_manifest_sha256=_MANIFEST,
            )
        self.assertIn("STATISTICAL_UNCERTAINTY_MALFORMED_PROVENANCE", str(bad_commit.exception))
        with self.assertRaises(ValueError) as bad_event:
            assess_event_evidence_uncertainty({"evidence_basis": "historical"})
        self.assertIn("EVENT_EVIDENCE_", str(bad_event.exception))

    def test_noncanonical_bytes_are_rejected(self) -> None:
        raw = _raw()
        pretty = json.dumps(json.loads(raw), indent=2).encode("utf-8")
        with self.assertRaises(ValueError) as caught:
            validate_uncertainty_document(pretty)
        self.assertIn("STATISTICAL_UNCERTAINTY_NONCANONICAL_JSON", str(caught.exception))
        duplicate = raw.replace(
            b'"document_kind"',
            b'"document_kind":"EXPLORATORY_SYNTHETIC_CALIBRATION","document_kind"',
            1,
        )
        with self.assertRaises(ValueError) as duplicate_key:
            validate_uncertainty_document(duplicate)
        self.assertIn("STATISTICAL_UNCERTAINTY_", str(duplicate_key.exception))


class StatisticalUncertaintyCalibrationTests(unittest.TestCase):
    def test_predeclared_scenarios_and_determinism(self) -> None:
        document = _document()
        self.assertEqual(document["document_kind"], "EXPLORATORY_SYNTHETIC_CALIBRATION")
        self.assertEqual(document["inference_status"], "EXPLORATORY_NOT_INFERENCE")
        self.assertFalse(document["inference_authorized"])
        self.assertFalse(document["error_control_claimed"])
        self.assertFalse(document["calibrated_error_control_claimed"])
        self.assertFalse(document["statistical_significance_claimed"])
        self.assertFalse(document["portfolio_profit_claimed"])
        self.assertFalse(document["used_exp_20261118_069_outcomes_to_tune"])
        self.assertFalse(document["used_to_retune_dec470"])
        self.assertFalse(
            document["overlapping_signals_are_simultaneously_executable_independent_trades"]
        )
        names = []
        scenarios = document["scenarios"]
        assert isinstance(scenarios, list)
        for scenario in scenarios:
            assert isinstance(scenario, dict)
            names.append(scenario["scenario_name"])
            self.assertFalse(scenario["portfolio_profit"])
            self.assertEqual(scenario["primary_seed"], PRIMARY_CALIBRATION_SEED)
        self.assertEqual(
            names,
            [
                "zero_edge_independent",
                "negative_after_cost",
                "planted_positive_edge",
                "serial_correlated_noise",
                "shared_event_membership",
                "overlapping_horizons",
                "common_shock_cross_symbol",
                "sparse_support",
                "dense_support",
                "degenerate_constant_outcomes",
            ],
        )
        self.assertEqual(PRIMARY_CALIBRATION_SEED, 20261121)
        self.assertEqual(VARIABILITY_SEEDS, (20261121, 20261122, 20261123))
        self.assertFalse(set(VARIABILITY_SEEDS) & set(FORBIDDEN_TUNING_SEEDS))
        second, second_raw = compile_synthetic_calibration(_provenance())
        self.assertEqual(second_raw, _raw())
        self.assertEqual(second["content_sha256"], document["content_sha256"])
        methods = document["methods"]
        assert isinstance(methods, list)
        self.assertTrue(all(method["selected_by_observed_coverage"] is False for method in methods))

    def test_zero_negative_and_planted_diagnostics(self) -> None:
        document = _document()
        zero = _scenario(document, "zero_edge_independent")
        self.assertGreaterEqual(_rate(zero, "iid_normal_interval", "coverage_of_true_mean_among_available"), 0.85)
        self.assertLessEqual(_rate(zero, "iid_normal_interval", "rate_excluding_zero_among_available"), 0.15)
        self.assertEqual(zero["effective_sample_size"]["status"], "IDENTIFIED_UNDER_DECLARED_IID_ASSUMPTION")
        self.assertEqual(zero["effective_sample_size"]["value"], 80)
        self.assertFalse(zero["effective_sample_size"]["identified_for_event_evidence"])
        negative = _scenario(document, "negative_after_cost")
        self.assertLessEqual(
            _rate(negative, "iid_normal_interval", "rate_entirely_above_zero_among_available"),
            0.05,
        )
        self.assertEqual(negative["cost_pips"], 0.5)
        planted = _scenario(document, "planted_positive_edge")
        self.assertGreaterEqual(
            _rate(planted, "iid_normal_interval", "coverage_of_true_mean_among_available"),
            0.85,
        )
        self.assertGreaterEqual(
            _rate(planted, "iid_normal_interval", "rate_entirely_above_zero_among_available"),
            0.80,
        )
        planted_closed = planted["closed_form"]
        assert isinstance(planted_closed, dict)
        planted_iid = planted_closed["iid_normal_interval"]
        assert isinstance(planted_iid, dict)
        self.assertLess(abs(float(planted_iid["mean_of_sample_means"]) - 0.4), 0.1)
        self.assertEqual(planted_iid["replications"], CLOSED_FORM_REPLICATIONS)

    def test_dependence_sensitivity_and_incorrect_independence(self) -> None:
        document = _document()
        zero = _scenario(document, "zero_edge_independent")
        serial = _scenario(document, "serial_correlated_noise")
        self.assertLess(
            _rate(serial, "iid_normal_interval", "coverage_of_true_mean_among_available") + 0.10,
            _rate(zero, "iid_normal_interval", "coverage_of_true_mean_among_available"),
        )
        self.assertGreater(
            _rate(serial, "iid_normal_interval", "rate_excluding_zero_among_available"),
            _rate(zero, "iid_normal_interval", "rate_excluding_zero_among_available") + 0.15,
        )
        serial_closed = serial["closed_form"]
        assert isinstance(serial_closed, dict)
        serial_iid = serial_closed["iid_normal_interval"]
        serial_hac = serial_closed["newey_west_lag_8"]
        assert isinstance(serial_iid, dict)
        assert isinstance(serial_hac, dict)
        self.assertGreater(
            float(serial_hac["median_interval_width"]),
            float(serial_iid["median_interval_width"]) * 1.15,
        )
        self.assertFalse(serial_hac["p_values_produced"])
        effective = serial["effective_sample_size"]
        assert isinstance(effective, dict)
        self.assertEqual(effective["status"], "IDENTIFIED_UNDER_DECLARED_AR1_ASSUMPTION")
        self.assertEqual(effective["phi"], 0.8)
        self.assertFalse(effective["phi_estimated_from_sample"])
        self.assertFalse(effective["episode_group_count_used_as_value"])
        bootstrap = serial["bootstrap"]
        assert isinstance(bootstrap, dict)
        methods = bootstrap["methods"]
        assert isinstance(methods, dict)
        block_1 = methods["moving_block_1"]
        block_8 = methods["moving_block_8"]
        assert isinstance(block_1, dict)
        assert isinstance(block_8, dict)
        self.assertGreater(
            float(block_8["median_interval_width"]),
            float(block_1["median_interval_width"]),
        )
        self.assertFalse(bootstrap["valid_p_value_claimed"])
        shared = _scenario(document, "shared_event_membership")
        self.assertLess(
            _comparison_width(shared, "incorrect_stacked_iid"),
            _comparison_width(shared, "preserving_single_series_iid") * 0.85,
        )
        self.assertEqual(shared["effective_sample_size"]["value"], 80)
        self.assertEqual(shared["effective_sample_size"]["incorrect_independent_hypothesis_rows"], 160)
        self.assertFalse(shared["effective_sample_size"]["incorrect_row_count_used_as_value"])
        overlap = _scenario(document, "overlapping_horizons")
        self.assertLess(
            _comparison_rate(overlap, "long_horizon_iid", "coverage_of_true_mean_among_available"),
            _comparison_rate(overlap, "short_horizon_iid", "coverage_of_true_mean_among_available"),
        )
        overlap_closed = overlap["closed_form"]
        assert isinstance(overlap_closed, dict)
        overlap_iid = overlap_closed["iid_normal_interval"]
        overlap_hac = overlap_closed["newey_west_lag_8"]
        assert isinstance(overlap_iid, dict)
        assert isinstance(overlap_hac, dict)
        self.assertGreater(
            float(overlap_hac["median_interval_width"]),
            float(overlap_iid["median_interval_width"]),
        )
        self.assertEqual(overlap["effective_sample_size"]["status"], "UNAVAILABLE")
        common = _scenario(document, "common_shock_cross_symbol")
        self.assertLess(
            _comparison_width(common, "incorrect_stacked_iid"),
            _comparison_width(common, "contemporaneous_average_iid") * 0.95,
        )
        self.assertEqual(common["effective_sample_size"]["status"], "UNAVAILABLE")
        sparse = _scenario(document, "sparse_support")
        dense = _scenario(document, "dense_support")
        self.assertGreater(_rate_width(sparse), _rate_width(dense) * 3.0)
        degenerate = _scenario(document, "degenerate_constant_outcomes")
        degenerate_closed = degenerate["closed_form"]
        assert isinstance(degenerate_closed, dict)
        degenerate_iid = degenerate_closed["iid_normal_interval"]
        assert isinstance(degenerate_iid, dict)
        self.assertEqual(degenerate_iid["status"], "DEGENERATE_VARIANCE")
        self.assertIsNone(degenerate_iid["coverage_of_true_mean_among_available"])
        self.assertEqual(degenerate_iid["intervals_available"], 0)
        self.assertEqual(degenerate["effective_sample_size"]["status"], "DEGENERATE_VARIANCE")

    def test_multiple_testing_method_check_is_not_the_catalogue(self) -> None:
        document = _document()
        multiple = document["multiple_testing"]
        assert isinstance(multiple, dict)
        catalogue = multiple["catalogue"]
        check = multiple["synthetic_method_check"]
        assert isinstance(catalogue, dict)
        assert isinstance(check, dict)
        self.assertFalse(catalogue["holm_applied_to_catalogue"])
        self.assertEqual(catalogue["family_size_per_annual_segment"], 89460)
        self.assertEqual(check["family_size"], HOLM_METHOD_CHECK_FAMILY)
        self.assertFalse(check["method_check_is_the_annual_universe"])
        self.assertFalse(check["applied_to_annual_catalogue"])
        self.assertFalse(check["bootstrap_p_values_used"])
        self.assertFalse(check["error_control_claimed_for_catalogue"])
        self.assertGreaterEqual(float(check["uncorrected_familywise_rate"]), 0.70)
        self.assertLessEqual(float(check["holm_familywise_rate"]), 0.12)
        self.assertLess(
            float(check["holm_familywise_rate"]),
            float(check["uncorrected_familywise_rate"]),
        )
        variability = document["variability_across_seeds"]
        assert isinstance(variability, dict)
        self.assertFalse(variability["used_to_choose_a_method"])
        rows = variability["rows"]
        assert isinstance(rows, list)
        self.assertEqual(len(rows), 3)
        zero_coverage = _rate(
            _scenario(document, "zero_edge_independent"),
            "iid_normal_interval",
            "coverage_of_true_mean_among_available",
        )
        for row in rows:
            assert isinstance(row, dict)
            self.assertGreaterEqual(float(row["coverage_of_true_mean_among_available"]), 0.80)
            self.assertNotIn(row["seed"], FORBIDDEN_TUNING_SEEDS)
            if row["seed"] == PRIMARY_CALIBRATION_SEED:
                self.assertEqual(row["coverage_of_true_mean_among_available"], zero_coverage)
        scaling = document["scaling"]
        assert isinstance(scaling, dict)
        self.assertFalse(scaling["full_universe_resample_executed"])
        self.assertFalse(scaling["full_universe_holm_executed"])
        self.assertEqual(scaling["frozen_directional_hypotheses_per_annual_segment"], 89460)


def _rate_width(scenario: dict[str, object]) -> float:
    closed = scenario["closed_form"]
    assert isinstance(closed, dict)
    payload = closed["iid_normal_interval"]
    assert isinstance(payload, dict)
    value = payload["median_interval_width"]
    assert isinstance(value, float)
    return value


class StatisticalUncertaintyWorkloadTests(unittest.TestCase):
    def test_representative_workload_is_bounded(self) -> None:
        measurement = measure_representative_workload(_provenance())
        self.assertGreater(float(measurement["elapsed_seconds"]), 0.0)
        self.assertLess(float(measurement["elapsed_seconds"]), 180.0)
        self.assertGreater(int(measurement["tracemalloc_peak_bytes"]), 0)
        self.assertLess(int(measurement["tracemalloc_peak_bytes"]), 80_000_000)
        self.assertGreater(int(measurement["canonical_bytes"]), 0)
        self.assertFalse(measurement["historical_artifact_read"])
        self.assertEqual(measurement["content_sha256"], _document()["content_sha256"])
        self.assertIsInstance(_CACHE["compile_peak_bytes"], int)


if __name__ == "__main__":
    unittest.main()
