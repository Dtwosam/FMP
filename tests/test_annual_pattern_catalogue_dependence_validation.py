"""Synthetic dependence-aware validation. No historical catalogue is opened."""

from __future__ import annotations

import hashlib
import json
import random
import time
import tracemalloc
import unittest
from pathlib import Path

from fmp.discovery.annual_pattern_catalogue_dependence_validation import (
    ALPHA,
    CALIBRATION_MASTER_SEED,
    CLEAR_UNDERCOVERAGE_CEILING,
    DEPENDENCE_VALIDATION_PROTOCOL,
    DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
    EXPECTED_PROTOCOL_FINGERPRINT,
    FAMILY_VALIDATION_SIZE,
    FORBIDDEN_MASTER_SEEDS,
    HOLDOUT_BOOTSTRAP_REPLICATIONS,
    HOLDOUT_MASTER_SEED,
    MIN_DENOMINATOR_TO_VALIDATE,
    PATTERN_TOOL,
    PREDECLARED_BLOCK_LENGTHS,
    PREDECLARED_HAC_LAGS,
    SERIES_LENGTH,
    SHARED_EVENT_COUNT,
    STRONG_AR_PHI,
    WEAK_AR_PHI,
    DependenceValidationProvenance,
    ar1_effective_sample_size,
    ar1_variance_of_mean,
    assess_supplied_events_for_catalogue_inference,
    assumptions_match,
    binomial_monte_carlo_report,
    circular_block_bootstrap_interval,
    compile_dependence_validation,
    declared_model_z_interval,
    dependence_validation_contract,
    fwer_control_status,
    holm_adjusted_p_values,
    horizon_contrast_variance,
    iid_normal_interval,
    independent_column_contrast_interval,
    interval_primary_status,
    long_memory_variance_of_mean,
    moving_block_bootstrap_interval,
    newey_west_interval,
    null_test_primary_status,
    overlapping_mean_variance,
    refuse_episode_groups_as_independent_trials,
    refuse_incorrect_sample_size,
    refuse_method_revision,
    refuse_percentile_interval_as_p_value,
    regime_variance_of_mean,
    shared_clock_contrast_interval,
    studentized_null_centered_p_value,
    validate_dependence_validation_document,
    _last_material_ar_lag,
    _moving_block_indexes,
)
from fmp.discovery.annual_pattern_catalogue_protocol import (
    ANNUAL_CATALOGUE_PROTOCOL_DECISION,
    MAX_SIGN_FLIPS,
    MIN_ANNUAL_EVALUABLE_SUPPORT,
    MIN_BASE_POSITIVE_FRACTION,
    MIN_CROSS_YEAR_EVALUABLE_SEGMENTS,
    MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5,
    MIN_POOLED_MEAN_NET_PIPS_0P5,
    NEAR_DUPLICATE_JACCARD,
    protocol_fingerprint,
)
from fmp.discovery.annual_pattern_catalogue_statistical_uncertainty import (
    EXPECTED_PROTOCOL_FINGERPRINT as UNCERTAINTY_FINGERPRINT,
    FORBIDDEN_TUNING_SEEDS,
    PREDECLARED_BLOCK_LENGTHS as UNCERTAINTY_BLOCKS,
    PREDECLARED_HAC_LAGS as UNCERTAINTY_LAGS,
    PRIMARY_CALIBRATION_SEED,
    STATISTICAL_UNCERTAINTY_PROTOCOL,
    newey_west_interval as uncertainty_newey_west_interval,
)


_COMMIT = "168d4c2b850fb0ff6f97fba3b0d287332d9cfe4f"
_MANIFEST = hashlib.sha256(b"synthetic-dependence-aware-validation-v1\n").hexdigest()
_ROOT = Path(__file__).resolve().parents[1]


def _provenance() -> DependenceValidationProvenance:
    return DependenceValidationProvenance(
        source_label="synthetic-dependence-aware-validation-v1",
        code_commit=_COMMIT,
        synthetic_manifest_sha256=_MANIFEST,
    )


class DependenceValidationRuleTests(unittest.TestCase):
    def test_frozen_contracts_and_seeds_stay_closed(self) -> None:
        contract = dependence_validation_contract()
        self.assertEqual(contract["governing_research_method"], "DISCOVERY_FIRST_ANNUAL_PATTERN_CATALOGUE")
        self.assertTrue(contract["pattern_tool_is_not_the_governing_method"])
        self.assertEqual(contract["pattern_tool"], PATTERN_TOOL)
        self.assertEqual(contract["protocol_decision"], "DEC-470")
        self.assertEqual(contract["protocol_fingerprint"], protocol_fingerprint())
        self.assertEqual(contract["protocol_fingerprint"], EXPECTED_PROTOCOL_FINGERPRINT)
        self.assertEqual(contract["directional_hypotheses_per_annual_segment"], 89460)
        self.assertEqual(ANNUAL_CATALOGUE_PROTOCOL_DECISION, "DEC-470")
        self.assertEqual(STATISTICAL_UNCERTAINTY_PROTOCOL, "fmp-annual-pattern-catalogue-statistical-uncertainty-v1")
        self.assertEqual(UNCERTAINTY_FINGERPRINT, EXPECTED_PROTOCOL_FINGERPRINT)
        self.assertEqual(UNCERTAINTY_LAGS, (1, 4, 8))
        self.assertEqual(UNCERTAINTY_BLOCKS, (1, 4, 8))
        self.assertEqual(PRIMARY_CALIBRATION_SEED, 20261121)
        self.assertEqual(FORBIDDEN_TUNING_SEEDS, (20261118, 20261119, 20261120))
        self.assertTrue(set(FORBIDDEN_TUNING_SEEDS).issubset(FORBIDDEN_MASTER_SEEDS))
        self.assertNotIn(HOLDOUT_MASTER_SEED, FORBIDDEN_MASTER_SEEDS)
        self.assertNotIn(CALIBRATION_MASTER_SEED, FORBIDDEN_MASTER_SEEDS)
        self.assertNotEqual(HOLDOUT_MASTER_SEED, CALIBRATION_MASTER_SEED)
        self.assertLess(HOLDOUT_BOOTSTRAP_REPLICATIONS, MIN_DENOMINATOR_TO_VALIDATE)
        self.assertFalse(any(contract["authorizations"].values()))
        self.assertFalse(contract["annual_run_385_consumed"])
        self.assertFalse(contract["dec629_adopted"])
        self.assertFalse(contract["dec630_adopted"])
        self.assertFalse(contract["prior_ar1_context"]["used_as_acceptance_threshold"])
        self.assertFalse(contract["prior_ar1_context"]["used_as_tuning_target"])
        thresholds = contract["recorded_thresholds"]
        self.assertEqual(thresholds["min_annual_evaluable_support"], 75)
        self.assertEqual(thresholds["min_annual_evaluable_support"], MIN_ANNUAL_EVALUABLE_SUPPORT)
        self.assertEqual(thresholds["min_cross_year_evaluable_segments"], 9)
        self.assertEqual(thresholds["min_cross_year_evaluable_segments"], MIN_CROSS_YEAR_EVALUABLE_SEGMENTS)
        self.assertEqual(thresholds["min_base_positive_fraction"], 0.80)
        self.assertEqual(thresholds["min_base_positive_fraction"], MIN_BASE_POSITIVE_FRACTION)
        self.assertEqual(thresholds["min_median_annual_mean_net_pips_0p5"], 0.10)
        self.assertEqual(thresholds["min_median_annual_mean_net_pips_0p5"], MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5)
        self.assertEqual(thresholds["min_pooled_mean_net_pips_0p5"], 0.25)
        self.assertEqual(thresholds["min_pooled_mean_net_pips_0p5"], MIN_POOLED_MEAN_NET_PIPS_0P5)
        self.assertEqual(thresholds["max_sign_flips"], 3)
        self.assertEqual(thresholds["max_sign_flips"], MAX_SIGN_FLIPS)
        self.assertEqual(thresholds["near_duplicate_jaccard"], 0.90)
        self.assertEqual(thresholds["near_duplicate_jaccard"], NEAR_DUPLICATE_JACCARD)
        self.assertFalse(thresholds["modified"])
        self.assertEqual(PREDECLARED_HAC_LAGS, (1, 4, 8, 16))
        self.assertEqual(PREDECLARED_BLOCK_LENGTHS, (1, 4, 8, 16))
        source = (
            _ROOT / "src/fmp/discovery/annual_pattern_catalogue_cross_year.py"
        ).read_text(encoding="utf-8")
        self.assertIn('"p_values": "UNAVAILABLE_NOT_COMPUTED"', source)
        self.assertIn('"multiple_comparison_adjustment": "UNAVAILABLE_NOT_COMPUTED"', source)

    def test_analytic_variance_and_dependence_horizon(self) -> None:
        self.assertAlmostEqual(ar1_variance_of_mean(2, 0.5, 1.0), 1.0)
        self.assertAlmostEqual(ar1_effective_sample_size(2, 0.5), 4.0 / 3.0)
        self.assertAlmostEqual(overlapping_mean_variance(2, 2, 1.0), 0.375)
        self.assertAlmostEqual(long_memory_variance_of_mean(SERIES_LENGTH), long_memory_variance_of_mean(SERIES_LENGTH))
        self.assertGreater(ar1_variance_of_mean(SERIES_LENGTH, STRONG_AR_PHI, 1.0), 1.0 / SERIES_LENGTH)
        self.assertGreater(
            long_memory_variance_of_mean(SERIES_LENGTH),
            1.0 / SERIES_LENGTH,
        )
        self.assertEqual(_last_material_ar_lag(WEAK_AR_PHI), 2)
        self.assertEqual(_last_material_ar_lag(STRONG_AR_PHI), 13)
        self.assertAlmostEqual(
            regime_variance_of_mean(4, 0.0, 1.0),
            1.0 / 4.0,
        )
        self.assertGreater(horizon_contrast_variance(SERIES_LENGTH, 4, 1.0), 0.0)
        large_sample = SERIES_LENGTH * (1.0 - STRONG_AR_PHI) / (1.0 + STRONG_AR_PHI)
        finite = ar1_effective_sample_size(SERIES_LENGTH, STRONG_AR_PHI)
        self.assertNotAlmostEqual(finite, large_sample)
        self.assertGreater(finite, large_sample)

    def test_assumption_map_is_not_chosen_from_coverage(self) -> None:
        self.assertFalse(assumptions_match("strong_ar1", "primary", "iid_normal_interval"))
        self.assertFalse(assumptions_match("strong_ar1", "primary", "newey_west_lag_8"))
        self.assertTrue(assumptions_match("strong_ar1", "primary", "newey_west_lag_16"))
        self.assertFalse(assumptions_match("strong_ar1", "primary", "moving_block_8"))
        self.assertTrue(assumptions_match("strong_ar1", "primary", "moving_block_16"))
        self.assertTrue(assumptions_match("strong_ar1", "primary", "declared_model_z_interval"))
        self.assertFalse(assumptions_match("strong_ar1", "primary", "iid_variance_z_interval"))
        self.assertFalse(assumptions_match("long_memory", "primary", "newey_west_lag_16"))
        self.assertTrue(assumptions_match("long_memory", "primary", "declared_model_z_interval"))
        self.assertFalse(assumptions_match("overlapping_windows", "primary", "newey_west_lag_1"))
        self.assertTrue(assumptions_match("overlapping_windows", "primary", "newey_west_lag_4"))
        self.assertTrue(assumptions_match("overlapping_windows", "primary", "shock_rebuild_bootstrap"))
        self.assertFalse(
            assumptions_match("shared_identical_observations", "duplicated_rows", "iid_normal_interval")
        )
        self.assertTrue(
            assumptions_match("shared_identical_observations", "unique_events", "declared_model_z_interval")
        )
        self.assertTrue(assumptions_match("changing_volatility", "primary", "iid_normal_interval"))
        self.assertFalse(assumptions_match("changing_volatility", "primary", "newey_west_lag_8"))
        self.assertTrue(assumptions_match("changing_volatility", "primary", "moving_block_1"))
        self.assertFalse(assumptions_match("changing_volatility", "primary", "moving_block_16"))
        self.assertFalse(assumptions_match("regime_change", "primary", "iid_normal_interval"))
        self.assertTrue(assumptions_match("regime_change", "primary", "declared_model_z_interval"))
        self.assertFalse(
            assumptions_match("common_shock_cross_symbol", "contrast", "independent_column_block_8")
        )
        self.assertTrue(assumptions_match("common_shock_cross_symbol", "contrast", "shared_clock_block_8"))
        self.assertTrue(assumptions_match("independent_zero_edge", "primary", "studentized_null_centered_mbb_16"))
        self.assertFalse(assumptions_match("long_memory", "primary", "studentized_null_centered_mbb_16"))

    def test_status_rules_reject_success_without_precision(self) -> None:
        validated = interval_primary_status(
            assumptions_match=True,
            covered=380,
            available=400,
            unavailable_count=0,
            replications=400,
        )
        self.assertEqual(validated, "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL")
        failed = interval_primary_status(
            assumptions_match=True,
            covered=200,
            available=400,
            unavailable_count=0,
            replications=400,
        )
        self.assertEqual(failed, "FAILED_SYNTHETIC_CALIBRATION")
        underpowered = interval_primary_status(
            assumptions_match=True,
            covered=57,
            available=60,
            unavailable_count=0,
            replications=60,
        )
        self.assertEqual(underpowered, "INSUFFICIENT_MONTE_CARLO_PRECISION")
        ineligible = interval_primary_status(
            assumptions_match=False,
            covered=380,
            available=400,
            unavailable_count=0,
            replications=400,
        )
        self.assertEqual(ineligible, "MODEL_ASSUMPTIONS_UNVERIFIED")
        ineligible_failure = interval_primary_status(
            assumptions_match=False,
            covered=100,
            available=400,
            unavailable_count=0,
            replications=400,
        )
        self.assertEqual(ineligible_failure, "FAILED_SYNTHETIC_CALIBRATION")
        degenerate = interval_primary_status(
            assumptions_match=False,
            covered=0,
            available=0,
            unavailable_count=400,
            replications=400,
        )
        self.assertEqual(degenerate, "MODEL_ASSUMPTIONS_UNVERIFIED")
        self.assertLess(CLEAR_UNDERCOVERAGE_CEILING, 0.95)
        size_ok = null_test_primary_status(
            assumptions_match=True,
            rejections=20,
            available=400,
            unavailable_count=0,
            replications=400,
        )
        self.assertEqual(size_ok, "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL")
        size_imprecise = null_test_primary_status(
            assumptions_match=True,
            rejections=3,
            available=60,
            unavailable_count=0,
            replications=60,
        )
        self.assertEqual(size_imprecise, "INSUFFICIENT_MONTE_CARLO_PRECISION")
        fwer_ok = fwer_control_status(
            assumptions_match=True, familywise_rejections=10, replications=400
        )
        self.assertEqual(fwer_ok, "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL")
        fwer_noise = fwer_control_status(
            assumptions_match=True, familywise_rejections=26, replications=400
        )
        self.assertEqual(fwer_noise, "INSUFFICIENT_MONTE_CARLO_PRECISION")
        fwer_fail = fwer_control_status(
            assumptions_match=True, familywise_rejections=40, replications=400
        )
        self.assertEqual(fwer_fail, "FAILED_SYNTHETIC_CALIBRATION")
        shortlist = fwer_control_status(
            assumptions_match=False, familywise_rejections=174, replications=400
        )
        self.assertEqual(shortlist, "FAILED_SYNTHETIC_CALIBRATION")
        report = binomial_monte_carlo_report(144, 160)
        self.assertEqual(report["numerator"], 144)
        self.assertEqual(report["denominator"], 160)
        self.assertAlmostEqual(float(report["rate"]), 0.9)
        self.assertEqual(report["wilson_interval_95"]["method"], "wilson_score")
        self.assertIsNone(binomial_monte_carlo_report(0, 0)["wilson_interval_95"])

    def test_holm_hand_calculation_and_interval_agreement(self) -> None:
        self.assertEqual(holm_adjusted_p_values([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
        series = [0.5, -0.25, 0.75, -0.5, 1.0, -1.25]
        ours = newey_west_interval(series, 4)
        theirs = uncertainty_newey_west_interval(series, 4)
        self.assertAlmostEqual(float(ours["low"]), float(theirs["low"]))
        self.assertAlmostEqual(float(ours["high"]), float(theirs["high"]))
        self.assertAlmostEqual(float(ours["standard_error"]), float(theirs["standard_error"]))
        with self.assertRaises(ValueError) as refused:
            uncertainty_newey_west_interval(series, 16)
        self.assertIn("STATISTICAL_UNCERTAINTY_LAG_NOT_PREDECLARED", str(refused.exception))
        extended = newey_west_interval(series, 16)
        self.assertEqual(extended["status"], "UNAVAILABLE")
        iid = iid_normal_interval(series)
        oracle = declared_model_z_interval(series, 1.0 / len(series))
        self.assertEqual(iid["p_value"], "P_VALUES_UNAVAILABLE")
        self.assertIsInstance(oracle["p_value"], float)
        self.assertLess(float(oracle["low"]), float(oracle["high"]))

    def test_resampling_preserves_or_breaks_shared_structure(self) -> None:
        values = [float(index) for index in range(1, 21)]
        indexes = _moving_block_indexes(len(values), 4, random.Random(11))
        self.assertEqual(len(indexes), len(values))
        for start in range(0, len(indexes), 4):
            block = indexes[start : start + 4]
            self.assertEqual(block, list(range(block[0], block[0] + len(block))))
        paired = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        shared = shared_clock_contrast_interval(
            paired, list(paired), 4, draws=11, rng=random.Random(3)
        )
        self.assertEqual(shared["low"], 0.0)
        self.assertEqual(shared["high"], 0.0)
        self.assertTrue(shared["columns_share_indexes"])
        independent = independent_column_contrast_interval(
            paired, list(paired), 4, draws=11, rng=random.Random(3)
        )
        self.assertFalse(independent["columns_share_indexes"])
        self.assertNotEqual(independent["low"], 0.0)
        wrapped = circular_block_bootstrap_interval(values, 4, draws=5, rng=random.Random(2))
        self.assertEqual(wrapped["p_value"], "P_VALUES_UNAVAILABLE")
        moved = moving_block_bootstrap_interval(values, 1, draws=7, rng=random.Random(2))
        self.assertEqual(moved["p_value"], "P_VALUES_UNAVAILABLE")
        with self.assertRaises(ValueError) as converted:
            refuse_percentile_interval_as_p_value(moved)
        self.assertIn("DEPENDENCE_VALIDATION_PERCENTILE_INTERVAL_IS_NOT_A_P_VALUE", str(converted.exception))
        studentized = studentized_null_centered_p_value(
            [0.2, -0.1, 0.4, -0.3, 0.1, -0.2, 0.3, -0.4] * 4,
            block_length=4,
            lag=4,
            draws=9,
            rng=random.Random(5),
        )
        self.assertIn(studentized["status"], {"COMPUTED", "UNAVAILABLE"})
        if studentized["status"] == "COMPUTED":
            self.assertFalse(studentized["percentile_interval_inverted"])
            self.assertEqual(studentized["confidence_interval"], "NOT_INVERTED")

    def test_closed_boundaries_reject_bad_provenance_and_claims(self) -> None:
        with self.assertRaises(ValueError) as episodes:
            refuse_episode_groups_as_independent_trials()
        self.assertIn("DEPENDENCE_VALIDATION_EPISODE_GROUPS_ARE_NOT_TRIALS", str(episodes.exception))
        with self.assertRaises(ValueError) as sample_size:
            refuse_incorrect_sample_size(unique_events=SHARED_EVENT_COUNT, claimed_independent_rows=120)
        self.assertIn("DEPENDENCE_VALIDATION_INCORRECT_SAMPLE_SIZE", str(sample_size.exception))
        refuse_incorrect_sample_size(unique_events=60, claimed_independent_rows=60)
        with self.assertRaises(ValueError) as revision:
            refuse_method_revision("increase the lag")
        self.assertIn("DEPENDENCE_VALIDATION_METHOD_REVISION_REQUIRES_FRESH_HOLDOUT", str(revision.exception))
        with self.assertRaises(ValueError) as missing:
            compile_dependence_validation(None)
        self.assertIn("DEPENDENCE_VALIDATION_MISSING_PROVENANCE", str(missing.exception))
        with self.assertRaises(ValueError) as historical:
            compile_dependence_validation(_provenance(), historical_artifact_path="data/EURUSD.csv")
        self.assertIn("DEPENDENCE_VALIDATION_HISTORICAL_ACCESS_REFUSED", str(historical.exception))
        with self.assertRaises(ValueError) as authorized:
            compile_dependence_validation(_provenance(), authorize_catalogue_inference=True)
        self.assertIn("DEPENDENCE_VALIDATION_CATALOGUE_INFERENCE_REFUSED", str(authorized.exception))
        with self.assertRaises(ValueError) as bad_commit:
            DependenceValidationProvenance(
                source_label="synthetic-dependence-aware-validation-v1",
                code_commit="not-a-commit",
                synthetic_manifest_sha256=_MANIFEST,
            )
        self.assertIn("DEPENDENCE_VALIDATION_MALFORMED_PROVENANCE", str(bad_commit.exception))
        with self.assertRaises(ValueError) as reused:
            from fmp.discovery.annual_pattern_catalogue_dependence_validation import _require_master_seed

            _require_master_seed(20261121)
        self.assertIn("DEPENDENCE_VALIDATION_FORBIDDEN_MASTER_SEED", str(reused.exception))
        assessment = assess_supplied_events_for_catalogue_inference(
            {"evidence_basis": "CALLER_SUPPLIED_SYNTHETIC_EVENTS_NOT_FROZEN_EVIDENCE"}
        )
        self.assertEqual(assessment["primary_status"], "CATALOGUE_INFERENCE_NOT_AUTHORIZED")
        self.assertEqual(assessment["p_values"], "P_VALUES_UNAVAILABLE")
        self.assertEqual(assessment["effective_sample_size"], "UNAVAILABLE")
        self.assertFalse(assessment["intervals_computed"])
        self.assertEqual(assessment["frozen_universe_family_size"], 89460)
        with self.assertRaises(ValueError) as independence:
            assess_supplied_events_for_catalogue_inference(
                {"evidence_basis": "CALLER_SUPPLIED_SYNTHETIC_EVENTS_NOT_FROZEN_EVIDENCE"},
                assume_independence=True,
            )
        self.assertIn("DEPENDENCE_VALIDATION_INDEPENDENCE_ASSUMPTION_REFUSED", str(independence.exception))
        with self.assertRaises(ValueError) as trials:
            assess_supplied_events_for_catalogue_inference(
                {"evidence_basis": "CALLER_SUPPLIED_SYNTHETIC_EVENTS_NOT_FROZEN_EVIDENCE"},
                treat_episode_groups_as_independent_trials=True,
            )
        self.assertIn("DEPENDENCE_VALIDATION_EPISODE_GROUPS_ARE_NOT_TRIALS", str(trials.exception))
        with self.assertRaises(ValueError) as basis:
            assess_supplied_events_for_catalogue_inference({"evidence_basis": "historical"})
        self.assertIn("DEPENDENCE_VALIDATION_EVENT_BASIS_REFUSED", str(basis.exception))


class DependenceValidationHarnessTests(unittest.TestCase):
    document: dict[str, object]
    raw: bytes
    elapsed_seconds: float
    peak_bytes: int

    @classmethod
    def setUpClass(cls) -> None:
        tracemalloc.start()
        started = time.perf_counter()
        cls.document, cls.raw = compile_dependence_validation(_provenance())
        cls.elapsed_seconds = time.perf_counter() - started
        _current, cls.peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    def _holdout(self, scenario_id: str, target: str, method_id: str) -> dict[str, object]:
        partitions = self.document["partitions"]
        assert isinstance(partitions, dict)
        holdout = partitions["holdout"]
        assert isinstance(holdout, dict)
        rows = holdout["rows"]
        assert isinstance(rows, list)
        for row in rows:
            assert isinstance(row, dict)
            if (
                row["scenario_id"] == scenario_id
                and row["target"] == target
                and row["method_id"] == method_id
            ):
                return row
        self.fail(f"missing row {scenario_id} {target} {method_id}")
        raise AssertionError

    def test_document_is_deterministic_canonical_and_closed(self) -> None:
        again, again_raw = compile_dependence_validation(_provenance())
        self.assertEqual(again_raw, self.raw)
        self.assertEqual(again["content_sha256"], self.document["content_sha256"])
        validated = validate_dependence_validation_document(self.raw)
        self.assertEqual(validated["content_sha256"], self.document["content_sha256"])
        pretty = json.dumps(json.loads(self.raw), indent=2).encode("utf-8")
        with self.assertRaises(ValueError) as pretty_error:
            validate_dependence_validation_document(pretty)
        self.assertIn("DEPENDENCE_VALIDATION_NONCANONICAL_JSON", str(pretty_error.exception))
        duplicate = self.raw.replace(
            b'"document_kind"',
            b'"document_kind":"DEPENDENCE_AWARE_SYNTHETIC_VALIDATION","document_kind"',
            1,
        )
        with self.assertRaises(ValueError) as duplicate_error:
            validate_dependence_validation_document(duplicate)
        self.assertIn("DEPENDENCE_VALIDATION_NONCANONICAL_JSON", str(duplicate_error.exception))
        self.assertEqual(self.document["document_kind"], "DEPENDENCE_AWARE_SYNTHETIC_VALIDATION")
        self.assertEqual(self.document["validation_protocol"], DEPENDENCE_VALIDATION_PROTOCOL)
        self.assertFalse(self.document["inference_authorized"])
        self.assertEqual(self.document["catalogue_inference"], "CATALOGUE_INFERENCE_NOT_AUTHORIZED")
        self.assertFalse(self.document["error_control_claimed_for_frozen_universe"])
        self.assertFalse(self.document["dec470_thresholds_modified"])
        self.assertEqual(self.document["directional_hypotheses_per_annual_segment"], 89460)
        self.assertEqual(
            DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
            89460,
        )
        seeds = self.document["seeds"]
        assert isinstance(seeds, dict)
        self.assertFalse(seeds["holdout_pooled_with_calibration"])
        self.assertLess(self.elapsed_seconds, 120.0)
        self.assertGreater(self.peak_bytes, 0)
        self.assertLess(self.peak_bytes, 200_000_000)

    def test_holdout_statuses_obey_the_frozen_rule(self) -> None:
        partitions = self.document["partitions"]
        assert isinstance(partitions, dict)
        for name, partition in partitions.items():
            assert isinstance(partition, dict)
            rows = partition["rows"]
            assert isinstance(rows, list)
            self.assertGreater(len(rows), 0)
            for row in rows:
                assert isinstance(row, dict)
                self.assertEqual(row["catalogue_inference"], "CATALOGUE_INFERENCE_NOT_AUTHORIZED")
                self.assertFalse(row["lag_or_block_selected_from_results"])
                if name != "holdout":
                    self.assertEqual(row["primary_status"], "EXPLORATORY_ONLY")
                if row["primary_status"] == "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL":
                    self.assertTrue(row["assumptions_match"])
                    self.assertEqual(row["partition"], "holdout")
                    self.assertGreaterEqual(int(row["replications"]), MIN_DENOMINATOR_TO_VALIDATE)
                coverage = row.get("coverage")
                if isinstance(coverage, dict) and coverage.get("denominator"):
                    self.assertLessEqual(int(coverage["numerator"]), int(coverage["denominator"]))
                    self.assertIn("wilson_interval_95", coverage)
        strong_iid = self._holdout("strong_ar1", "primary", "iid_normal_interval")
        self.assertNotEqual(strong_iid["primary_status"], "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL")
        self.assertFalse(strong_iid["assumptions_match"])
        wrong_variance = self._holdout("strong_ar1", "primary", "iid_variance_z_interval")
        self.assertNotEqual(wrong_variance["primary_status"], "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL")
        duplicated = self._holdout("shared_identical_observations", "duplicated_rows", "iid_normal_interval")
        self.assertNotEqual(duplicated["primary_status"], "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL")
        duplicated_size = duplicated["effective_sample_size"]
        assert isinstance(duplicated_size, dict)
        self.assertEqual(duplicated_size["value"], float(SHARED_EVENT_COUNT))
        self.assertFalse(duplicated_size["row_count_used_as_effective_sample_size"])
        for scenario_id in (
            "independent_zero_edge",
            "weak_ar1",
            "strong_ar1",
            "overlapping_windows",
            "regime_change",
        ):
            oracle = self._holdout(scenario_id, "primary", "declared_model_z_interval")
            self.assertTrue(oracle["assumptions_match"])
            self.assertNotEqual(oracle["primary_status"], "FAILED_SYNTHETIC_CALIBRATION")
            self.assertNotEqual(oracle["p_value_status"], "P_VALUES_UNAVAILABLE")
        degenerate = self._holdout("degenerate_constant", "primary", "iid_normal_interval")
        self.assertEqual(degenerate["primary_status"], "MODEL_ASSUMPTIONS_UNVERIFIED")
        coverage = degenerate["coverage"]
        assert isinstance(coverage, dict)
        self.assertEqual(coverage["denominator"], 0)
        long_memory = self._holdout("long_memory", "primary", "newey_west_lag_16")
        self.assertFalse(long_memory["assumptions_match"])
        self.assertNotEqual(long_memory["primary_status"], "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL")
        columns = self._holdout("common_shock_cross_symbol", "contrast", "independent_column_block_8")
        self.assertFalse(columns["assumptions_match"])
        self.assertNotEqual(columns["primary_status"], "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL")
        studentized = self._holdout("strong_ar1", "primary", "studentized_null_centered_mbb_16")
        self.assertFalse(studentized["percentile_interval_inverted"])
        self.assertFalse(studentized["valid_p_values_established"])
        self.assertLess(int(studentized["replications"]), MIN_DENOMINATOR_TO_VALIDATE)
        summary = self.document["summary"]
        assert isinstance(summary, dict)
        self.assertTrue(summary["validated_methods_are_not_authorized_for_catalogue_inference"])
        self.assertTrue(summary["synthetic_calibration_is_not_catalogue_validity"])

    def test_multiple_testing_does_not_control_the_frozen_universe(self) -> None:
        multiple = self.document["multiple_testing"]
        assert isinstance(multiple, dict)
        self.assertEqual(multiple["reference_family_size"], 89460)
        self.assertFalse(multiple["bounded_family_replaces_reference_family"])
        self.assertFalse(multiple["familywise_error_estimated_at_reference_family"])
        self.assertEqual(multiple["reference_family_status"], "CATALOGUE_INFERENCE_NOT_AUTHORIZED")
        self.assertFalse(multiple["holm_applied_only_to_shortlisted_winners"])
        studies = multiple["studies"]
        assert isinstance(studies, list)
        by_id = {study["study_id"]: study for study in studies}
        correlated = by_id["holdout_correlated_complete_null"]
        self.assertEqual(correlated["family_size"], FAMILY_VALIDATION_SIZE)
        self.assertNotEqual(correlated["family_size"], 89460)
        self.assertFalse(correlated["replaces_frozen_universe"])
        self.assertTrue(correlated["holm_rejections_do_not_exceed_uncorrected"])
        raw = correlated["uncorrected"]
        assert isinstance(raw, dict)
        self.assertEqual(raw["primary_status"], "FAILED_SYNTHETIC_CALIBRATION")
        self.assertFalse(raw["assumptions_match"])
        shortlist = correlated["shortlist_only_holm"]
        assert isinstance(shortlist, dict)
        self.assertFalse(shortlist["controls_the_original_search"])
        self.assertFalse(shortlist["assumptions_match"])
        self.assertNotEqual(shortlist["primary_status"], "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL")
        scaling = by_id["scaling_family_160_insufficient_by_design"]
        self.assertNotEqual(
            scaling["holm"]["primary_status"],
            "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL",
        )
        repeated = multiple["repeated_annual_segments"]
        assert isinstance(repeated, dict)
        self.assertEqual(repeated["primary_status"], "EXPLORATORY_ONLY")
        self.assertEqual(repeated["catalogue_inference"], "CATALOGUE_INFERENCE_NOT_AUTHORIZED")
        self.assertTrue(repeated["chance_recurrence_is_not_cross_year_confirmation"])
        self.assertEqual(repeated["shared_copy"]["confirmation_p_values"], "P_VALUES_UNAVAILABLE")
        self.assertEqual(repeated["shared_copy"]["mean_correlation"], 1.0)
        self.assertEqual(repeated["independent_segment_confirmation_p_values"], "P_VALUES_UNAVAILABLE")
        self.assertFalse(repeated["frozen_universe_controlled"])
        acceptance = self.document["acceptance_rule"]
        assert isinstance(acceptance, dict)
        self.assertFalse(acceptance["larger_bootstrap_validation_not_run"]["launched"])
        self.assertEqual(acceptance["larger_bootstrap_validation_not_run"]["replications_required"], 200)
        self.assertFalse(acceptance["calibration_partition_can_validate"])
        self.assertFalse(acceptance["holdout_seed_used_to_choose_methods"])
        self.assertEqual(ALPHA, 0.05)


if __name__ == "__main__":
    unittest.main()
