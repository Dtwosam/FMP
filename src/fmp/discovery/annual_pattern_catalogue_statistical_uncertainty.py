"""Source-only statistical uncertainty for annual pattern catalogue events.

Governing method: annual pattern catalogue discovery under DEC-469 / DEC-268.
Statistical uncertainty V1 is a pattern tool inside that method. It is not a
new governing method, not a replacement for the annual catalogue, and not a
significance test of historical patterns.

The tool consumes caller-supplied synthetic event evidence and predeclared
synthetic series. It does not read market artifacts, mine catalogues, open
annual run 385, change DEC-470, or promote a pattern.

On event evidence, overlap counts stay descriptive. Episode groups are not
independent trials. Sampling uncertainty, effective sample size, and
multiple-testing adjustments stay unavailable when the supplied evidence does
not identify them. Exploratory intervals exist only inside the synthetic
calibration harness and are not catalogue inference.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
import time
import tracemalloc
from dataclasses import dataclass
from typing import Mapping, Sequence

from .annual_pattern_catalogue_event_evidence import (
    ANNUAL_RUN_385_CONSUMED as EVENT_ANNUAL_RUN_385_CONSUMED,
    DEC629_ADOPTED as EVENT_DEC629_ADOPTED,
    DEC630_ADOPTED as EVENT_DEC630_ADOPTED,
    HISTORICAL_ARTIFACT_READ_AUTHORIZED as EVENT_HISTORICAL_ARTIFACT_READ_AUTHORIZED,
    HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED as EVENT_HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
    STATISTICAL_PROMOTION_AUTHORIZED as EVENT_STATISTICAL_PROMOTION_AUTHORIZED,
    STRATEGY_V1_SYNTHESIS_AUTHORIZED as EVENT_STRATEGY_V1_SYNTHESIS_AUTHORIZED,
    TRADING_AUTHORIZED as EVENT_TRADING_AUTHORIZED,
    WORKFLOW_ACTIVATION_AUTHORIZED as EVENT_WORKFLOW_ACTIVATION_AUTHORIZED,
    recover_event_ids_from_event_fingerprint,
    validate_event_evidence,
)
from .annual_pattern_catalogue_method import GOVERNING_RESEARCH_METHOD
from .annual_pattern_catalogue_protocol import (
    ANNUAL_CATALOGUE_PROTOCOL_DECISION,
    DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
    MAX_SIGN_FLIPS,
    MIN_ANNUAL_EVALUABLE_SUPPORT,
    MIN_BASE_POSITIVE_FRACTION,
    MIN_CROSS_YEAR_EVALUABLE_SEGMENTS,
    MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5,
    MIN_POOLED_MEAN_NET_PIPS_0P5,
    MIN_STRESS_POSITIVE_FRACTION,
    NEAR_DUPLICATE_JACCARD,
    REQUIRE_POOLED_STRESS_MEAN_POSITIVE,
    protocol_fingerprint,
)


STATISTICAL_UNCERTAINTY_VERSION = 1
STATISTICAL_UNCERTAINTY_PROTOCOL = (
    "fmp-annual-pattern-catalogue-statistical-uncertainty-v1"
)
PATTERN_TOOL = "statistical-uncertainty-v1"
EVIDENCE_BASIS = "CALLER_SUPPLIED_SYNTHETIC_EVENTS_NOT_FROZEN_EVIDENCE"
EXPECTED_PROTOCOL_FINGERPRINT = (
    "3f883b26f3d9da04840b9680701504833dbcb3ec2c919f74ed191a3ab1bd3d69"
)
CORRELATED_NOISE_CALIBRATION_EXPERIMENT = "EXP-20261118-069"
PRIMARY_CALIBRATION_SEED = 20261121
VARIABILITY_SEEDS = (20261121, 20261122, 20261123)
HOLM_METHOD_CHECK_SEED = 20261124
FORBIDDEN_TUNING_SEEDS = (20261118, 20261119, 20261120)
CLOSED_FORM_REPLICATIONS = 160
BOOTSTRAP_REPLICATIONS = 20
BOOTSTRAP_DRAWS = 99
PREDECLARED_HAC_LAGS = (1, 4, 8)
PREDECLARED_BLOCK_LENGTHS = (1, 4, 8)
HOLM_METHOD_CHECK_FAMILY = 40
HOLM_METHOD_CHECK_REPLICATIONS = 160
HOLM_METHOD_CHECK_SERIES_LENGTH = 30
HOLM_ALPHA = 0.05
HOLM_CORRELATED_NULL_SEED = 20261125
Z_95 = 1.959963984540054
MAX_DIRECT_SERIES_LENGTH = 2000
MAX_DECLARED_AR1_SAMPLE_SIZE = 2000
MAX_SOURCE_LABEL_LENGTH = 128
VARIABILITY_SCENARIO_NAMES = (
    "zero_edge_independent",
    "serial_correlated_noise",
    "shared_event_membership",
    "overlapping_horizons",
    "common_shock_cross_symbol",
)
_SYNTHETIC_CLOCK_ID = re.compile(r"^synthetic-clock-[a-z0-9]+(?:-[a-z0-9]+)*$")
_DIAGNOSTIC_ROLES = {
    "iid_normal_interval": "iid_assumption",
    "newey_west_lag_1": "dependence_aware",
    "newey_west_lag_4": "dependence_aware",
    "newey_west_lag_8": "dependence_aware",
    "moving_block_1": "incorrect_independence_diagnostic",
    "moving_block_4": "dependence_aware",
    "moving_block_8": "dependence_aware",
    "shared_clock_block_4": "dependence_aware_shared_clock",
    "incorrect_independent_columns_block_4": "incorrect_independence_diagnostic",
    "incorrect_stacked_iid": "incorrect_independence_diagnostic",
    "preserving_single_series_iid": "paired_single_series",
    "short_horizon_iid": "paired_short_horizon",
    "long_horizon_iid": "paired_long_horizon",
    "contemporaneous_average_iid": "paired_contemporaneous_average",
}

HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED = False
STRATEGY_V1_SYNTHESIS_AUTHORIZED = False
STATISTICAL_PROMOTION_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False
WORKFLOW_ACTIVATION_AUTHORIZED = False
DEC629_ADOPTED = False
DEC630_ADOPTED = False
ANNUAL_RUN_385_CONSUMED = False

_AUTHORIZATION_FLAGS = (
    ("historical_artifact_read_authorized", HISTORICAL_ARTIFACT_READ_AUTHORIZED),
    ("historical_catalogue_execution_authorized", HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED),
    ("historical_result_production_authorized", HISTORICAL_RESULT_PRODUCTION_AUTHORIZED),
    ("cross_year_result_production_authorized", CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED),
    ("strategy_v1_synthesis_authorized", STRATEGY_V1_SYNTHESIS_AUTHORIZED),
    ("statistical_promotion_authorized", STATISTICAL_PROMOTION_AUTHORIZED),
    ("candidate_compilation_authorized", CANDIDATE_COMPILATION_AUTHORIZED),
    ("promotion_authorized", PROMOTION_AUTHORIZED),
    ("phase8b_authorized", PHASE8B_AUTHORIZED),
    ("demo_order_authorized", DEMO_ORDER_AUTHORIZED),
    ("broker_mutation_authorized", BROKER_MUTATION_AUTHORIZED),
    ("live_order_authorized", LIVE_ORDER_AUTHORIZED),
    ("real_money_authorized", REAL_MONEY_AUTHORIZED),
    ("trading_authorized", TRADING_AUTHORIZED),
    ("workflow_activation_authorized", WORKFLOW_ACTIVATION_AUTHORIZED),
    ("dec629_adopted", DEC629_ADOPTED),
    ("dec630_adopted", DEC630_ADOPTED),
    ("annual_run_385_consumed", ANNUAL_RUN_385_CONSUMED),
)

_BOOTSTRAP_SCENARIOS = frozenset(
    {
        "serial_correlated_noise",
        "shared_event_membership",
        "overlapping_horizons",
        "common_shock_cross_symbol",
    }
)

_SCENARIOS: tuple[dict[str, object], ...] = (
    {
        "name": "zero_edge_independent",
        "kind": "iid",
        "n": 80,
        "true_mean": 0.0,
        "sigma": 1.0,
        "primary_false_positive": "interval_excludes_zero",
    },
    {
        "name": "negative_after_cost",
        "kind": "iid_minus_cost",
        "n": 80,
        "true_mean": -0.5,
        "sigma": 1.0,
        "cost_pips": 0.5,
        "primary_false_positive": "interval_entirely_above_zero",
    },
    {
        "name": "planted_positive_edge",
        "kind": "iid",
        "n": 80,
        "true_mean": 0.4,
        "sigma": 1.0,
        "primary_false_positive": "not_a_size_diagnostic",
    },
    {
        "name": "serial_correlated_noise",
        "kind": "ar1",
        "n": 80,
        "true_mean": 0.0,
        "sigma": 1.0,
        "phi": 0.8,
        "primary_false_positive": "interval_excludes_zero",
    },
    {
        "name": "shared_event_membership",
        "kind": "shared_event",
        "n": 80,
        "true_mean": 0.0,
        "sigma": 1.0,
        "primary_false_positive": "interval_excludes_zero",
    },
    {
        "name": "overlapping_horizons",
        "kind": "overlap_horizons",
        "n": 80,
        "true_mean": 0.0,
        "sigma": 1.0,
        "overlap_span": 4,
        "primary_false_positive": "interval_excludes_zero",
    },
    {
        "name": "common_shock_cross_symbol",
        "kind": "common_shock",
        "n": 80,
        "true_mean": 0.0,
        "sigma": 1.0,
        "primary_false_positive": "interval_excludes_zero",
    },
    {
        "name": "sparse_support",
        "kind": "iid",
        "n": 12,
        "true_mean": 0.0,
        "sigma": 1.0,
        "primary_false_positive": "interval_excludes_zero",
    },
    {
        "name": "dense_support",
        "kind": "iid",
        "n": 240,
        "true_mean": 0.0,
        "sigma": 1.0,
        "primary_false_positive": "interval_excludes_zero",
    },
    {
        "name": "degenerate_constant_outcomes",
        "kind": "constant",
        "n": 20,
        "true_mean": 0.0,
        "constant": 0.0,
        "primary_false_positive": "not_defined",
    },
)


def _fail(code: str, detail: str) -> None:
    raise ValueError(f"{code}: {detail}")


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _authorizations() -> dict[str, bool]:
    payload = {key: value for key, value in _AUTHORIZATION_FLAGS}
    if any(payload.values()):
        _fail("STATISTICAL_UNCERTAINTY_AUTHORIZATION_DRIFT", "an authorization flag is open")
    return payload


def _method_catalogue() -> list[dict[str, object]]:
    return [
        {
            "method_id": "iid_normal_interval",
            "version": "normal-z-95-sample-variance-v1",
            "estimand": "unweighted mean of one supplied numeric series",
            "interval": "sample mean plus or minus the predeclared 95 percent normal quantile times the usual standard error",
            "variance_divisor": "n-1",
            "z_95": Z_95,
            "assumptions": [
                "The observations are independent.",
                "The sample mean is approximately normal.",
                "The sample variance estimates the marginal variance.",
                "No hypothesis was selected because its outcome looked large.",
                "The series is not a portfolio of overlapping positions.",
            ],
            "failure_modes": [
                "Outcome windows that overlap make neighboring observations dependent, so the usual standard error is too small.",
                "Serial correlation beyond geometric overlap has the same effect.",
                "A common shock shared by two symbols is hidden if the rows are stacked and treated as independent.",
                "A short sample makes the normal quantile anti-conservative relative to a t interval.",
                "A constant sample has no sampling variance to estimate.",
            ],
            "recommended_for_overlapping_or_serially_dependent_series": False,
            "produces_p_values": False,
            "portfolio_profit_interval": False,
            "selected_by_observed_coverage": False,
        },
        {
            "method_id": "newey_west_bartlett",
            "version": "newey-west-bartlett-predeclared-lags-v1",
            "estimand": "unweighted mean of one supplied numeric series",
            "lags": list(PREDECLARED_HAC_LAGS),
            "lag_selection": "predeclared",
            "kernel": "Bartlett",
            "weight": "1 - k / (lag + 1)",
            "gamma_divisor": "n",
            "assumptions": [
                "The series is covariance stationary and weakly dependent.",
                "The predeclared lag is long enough for the autocorrelation that is present.",
                "The series is univariate. A second symbol or horizon is not inside this variance.",
                "The mean was not chosen by searching a catalogue.",
                "A positive long-run variance is an assumption, not something this estimator may invent by clipping.",
            ],
            "failure_modes": [
                "A lag that is too short leaves serial dependence in the standard error.",
                "A lag that is long relative to the sample makes the long-run variance noisy.",
                "The Bartlett quadratic form can be non-positive. That replication is unavailable rather than given a zero standard error.",
                "Overlapping horizons and cross-symbol shocks are not modeled by a univariate lag.",
                "The estimator is not a p-value and it is not a portfolio profit.",
            ],
            "recommended_for_catalogue_claims": False,
            "produces_p_values": False,
            "portfolio_profit_interval": False,
            "selected_by_observed_coverage": False,
        },
        {
            "method_id": "moving_block_bootstrap",
            "version": "moving-block-percentile-predeclared-lengths-v1",
            "estimand": "unweighted mean of one supplied numeric series",
            "block_lengths": list(PREDECLARED_BLOCK_LENGTHS),
            "block_length_selection": "predeclared",
            "draws": BOOTSTRAP_DRAWS,
            "percentile": "sorted draw floor(0.025*(draws-1)) and ceil(0.975*(draws-1))",
            "wrapping": False,
            "assumptions": [
                "Dependence is weak and is mostly carried inside a block of the predeclared length.",
                "Blocks may be concatenated as if the join does not matter.",
                "The percentile interval of the bootstrap means is only an exploratory range.",
                "Block length 1 is an independent resample. It is present so the incorrect independence assumption can be seen. It is not a recommended estimator when serial dependence exists.",
            ],
            "failure_modes": [
                "Block length 1 breaks serial dependence and outcome-window overlap.",
                "A block that is shorter than the overlap horizon leaves dependence outside the block.",
                "A block that is long relative to the sample leaves few distinct blocks.",
                "The percentile interval is coarse at the predeclared draw count.",
                "Resampling a univariate series does not carry a shock that lives on another symbol.",
                "A bootstrap interval is not treated as a valid p-value.",
            ],
            "block_length_1_is_an_incorrect_independence_diagnostic": True,
            "recommended_for_catalogue_claims": False,
            "produces_p_values": False,
            "portfolio_profit_interval": False,
            "selected_by_observed_coverage": False,
        },
        {
            "method_id": "shared_clock_block_bootstrap",
            "version": "shared-clock-moving-block-synthetic-identity-v1",
            "estimand": "mean of caller-supplied synthetic series, resampling each declared index once",
            "assumptions": [
                "Inputs are caller-supplied numeric series. Equal length does not prove timestamp alignment.",
                "A validated clock id uses the synthetic-clock prefix. That id is not an authentic event timeline.",
                "When a synthetic clock is declared, one draw of an index block is applied to every series.",
                "The contemporaneous average is formed before the interval, so a common shock stays inside the index.",
            ],
            "failure_modes": [
                "Treating equal length as proof that market timestamps were aligned.",
                "Independent column resampling assigns different indexes to series that shared a shock.",
                "Stacking those series and using an independent-observation interval counts one shock more than once.",
                "The shared clock does not by itself create a valid p-value.",
                "A scalar effective sample size is not implied by a shared-clock interval.",
            ],
            "equal_length_proves_timestamp_alignment": False,
            "authentic_event_timelines_aligned": False,
            "resamples_each_time_once": True,
            "produces_p_values": False,
            "portfolio_profit_interval": False,
            "selected_by_observed_coverage": False,
        },
        {
            "method_id": "holm_method_check",
            "version": "holm-step-down-v1",
            "family_size": HOLM_METHOD_CHECK_FAMILY,
            "alpha": HOLM_ALPHA,
            "assumptions": [
                "Each individual p-value is valid under the synthetic complete null.",
                "This check uses a known-sigma Gaussian mean, so the p-value does not come from a bootstrap.",
                "Holm controls familywise error under arbitrary dependence only when those individual p-values are valid.",
                "The independent-null and correlated-null checks use the same family size. The correlated null keeps valid marginal p-values and adds a shared shock.",
                "The check family is not the 89460-hypothesis per-segment universe.",
                "89460 is the frozen search universe of one annual segment. It does not prove that selection across years is controlled.",
            ],
            "failure_modes": [
                "Dependence-preserving resampling is not assumed to produce valid p-values, so those resamples are not passed to Holm.",
                "Applying Holm only to shortlisted winners does not control the search that produced the shortlist.",
                "A caller declaration that p-values are valid is not a proof that catalogue p-values exist.",
                "A bounded method check does not control the catalogue or selection across years.",
            ],
            "applied_to_annual_catalogue": False,
            "produces_catalogue_p_values": False,
            "catalogue_wide_error_control_claimed": False,
            "selected_by_observed_false_passes": False,
            "selected_by_observed_coverage": False,
        },
    ]


def _scaling_limits() -> dict[str, object]:
    return {
        "frozen_directional_hypotheses_per_annual_segment": (
            DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT
        ),
        "full_universe_resample_executed": False,
        "full_universe_holm_executed": False,
        "scientific_blocker": (
            "Valid individual p-values are not available for the annual "
            "catalogue, and dependence and selection are not verified. Holm "
            "arithmetic at 89460 hypotheses would be cheap. That cost is not "
            "why the catalogue adjustment is withheld."
        ),
        "per_segment_hypothesis_count_proves_cross_year_error_control": False,
        "bounded_holm_method_check_family": HOLM_METHOD_CHECK_FAMILY,
        "bounded_method_check_is_the_annual_universe": False,
        "bounded_method_check_controls_catalogue_wide_error": False,
        "max_predeclared_series_length": max(int(item["n"]) for item in _SCENARIOS),
        "max_direct_series_length": MAX_DIRECT_SERIES_LENGTH,
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "bootstrap_replications": BOOTSTRAP_REPLICATIONS,
        "closed_form_replications": CLOSED_FORM_REPLICATIONS,
        "pair_lists_materialized": False,
    }


def _recorded_boundaries() -> dict[str, object]:
    return {
        "protocol_decision": ANNUAL_CATALOGUE_PROTOCOL_DECISION,
        "protocol_fingerprint": protocol_fingerprint(),
        "protocol_fingerprint_expected": EXPECTED_PROTOCOL_FINGERPRINT,
        "dec470_thresholds_modified": False,
        "event_evidence_schema_modified": False,
        "annual_miner_modified": False,
        "cross_year_engine_modified": False,
        "cross_year_engine_statistical_compatibility": {
            "p_values": "UNAVAILABLE_NOT_COMPUTED",
            "independent_trial_standard_errors": "UNAVAILABLE_NOT_COMPUTED",
            "multiple_comparison_adjustment": "UNAVAILABLE_NOT_COMPUTED",
            "reviewed_without_importing_the_engine": True,
        },
        "search_universe_directional_hypotheses_per_annual_segment": (
            DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT
        ),
        "search_universe_meaning": (
            "89460 is the frozen directional search universe of one annual "
            "segment. It is not proof that multiple testing or selection "
            "across years has been controlled."
        ),
        "exp_20261118_069": {
            "experiment_id": CORRELATED_NOISE_CALIBRATION_EXPERIMENT,
            "used_observed_outcomes_to_tune_this_module": False,
            "forbidden_tuning_seeds": list(FORBIDDEN_TUNING_SEEDS),
            "note": (
                "The historical synthetic false-pass counts, including 4922 "
                "correlated zero-gross passes at 8 pips on seed 20261120, "
                "stay context. They are not a target, a weight, or a "
                "threshold in this module."
            ),
        },
    }


@dataclass(frozen=True, slots=True)
class UncertaintyProvenance:
    source_label: str
    code_commit: str
    synthetic_manifest_sha256: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_label, str)
            or not self.source_label
            or self.source_label != self.source_label.strip()
            or len(self.source_label) > MAX_SOURCE_LABEL_LENGTH
            or any(character in self.source_label for character in "\r\n")
        ):
            _fail(
                "STATISTICAL_UNCERTAINTY_MALFORMED_PROVENANCE",
                "source_label must be a single non-empty line",
            )
        object.__setattr__(
            self,
            "code_commit",
            _validate_commit(self.code_commit),
        )
        object.__setattr__(
            self,
            "synthetic_manifest_sha256",
            _validate_sha256(self.synthetic_manifest_sha256),
        )


def _validate_sha256(value: object) -> str:
    if not isinstance(value, str) or len(value) != 64:
        _fail(
            "STATISTICAL_UNCERTAINTY_MALFORMED_PROVENANCE",
            "synthetic_manifest_sha256 must be a 64-character sha256",
        )
    try:
        int(value, 16)
    except ValueError:
        _fail(
            "STATISTICAL_UNCERTAINTY_MALFORMED_PROVENANCE",
            "synthetic_manifest_sha256 must be hexadecimal",
        )
    return value.lower()


def _validate_commit(value: object) -> str:
    if not isinstance(value, str) or len(value) != 40:
        _fail(
            "STATISTICAL_UNCERTAINTY_MALFORMED_PROVENANCE",
            "code_commit must be a 40-character Git commit",
        )
    try:
        int(value, 16)
    except ValueError:
        _fail(
            "STATISTICAL_UNCERTAINTY_MALFORMED_PROVENANCE",
            "code_commit must be hexadecimal",
        )
    return value.lower()


def _provenance_payload(provenance: UncertaintyProvenance) -> dict[str, object]:
    return {
        "source_label": provenance.source_label,
        "code_commit": provenance.code_commit,
        "synthetic_manifest_sha256": provenance.synthetic_manifest_sha256,
        "historical_artifact_read": False,
        "caller_supplied": True,
    }


def _require_series(values: Sequence[float]) -> list[float]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "series must be a sequence of numbers")
    if len(values) == 0:
        _fail("STATISTICAL_UNCERTAINTY_EMPTY_SAMPLE", "series is empty")
    if len(values) > MAX_DIRECT_SERIES_LENGTH:
        _fail(
            "STATISTICAL_UNCERTAINTY_SERIES_TOO_LARGE",
            "direct series length exceeds the source bound",
        )
    parsed: list[float] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "series values must be finite numbers")
        number = float(value)
        if not math.isfinite(number):
            _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "series values must be finite numbers")
        parsed.append(number)
    return parsed


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def _sample_variance(values: Sequence[float], mean: float) -> float:
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def _unavailable_interval(
    *,
    status: str,
    reason: str,
    mean: float | None,
    n: int,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "status": status,
        "reason": reason,
        "mean": mean,
        "n": n,
        "standard_error": None,
        "low": None,
        "high": None,
        "inference_authorized": False,
        "portfolio_profit_interval": False,
        "p_value": "NOT_COMPUTED",
    }
    if extra:
        payload.update(extra)
    return payload


def iid_normal_interval(values: Sequence[float]) -> dict[str, object]:
    """Exploratory normal interval for a mean. Independence is assumed and is often false."""

    parsed = _require_series(values)
    n = len(parsed)
    mean = _mean(parsed)
    if n < 2:
        return _unavailable_interval(
            status="UNAVAILABLE",
            reason="SAMPLE_SIZE_BELOW_TWO",
            mean=mean,
            n=n,
        )
    sum_squares = sum((value - mean) ** 2 for value in parsed)
    if sum_squares <= 0.0:
        return _unavailable_interval(
            status="DEGENERATE_VARIANCE",
            reason="SAMPLE_VARIANCE_IS_ZERO",
            mean=mean,
            n=n,
        )
    standard_error = math.sqrt((sum_squares / (n - 1)) / n)
    half = Z_95 * standard_error
    return {
        "status": "EXPLORATORY_NOT_INFERENCE",
        "reason": "INTERVAL_UNDER_DECLARED_IID_NORMAL_ASSUMPTION",
        "mean": mean,
        "n": n,
        "standard_error": standard_error,
        "low": mean - half,
        "high": mean + half,
        "z_95": Z_95,
        "variance_divisor": "n-1",
        "independence_assumed": True,
        "assumption_correct_for_overlapping_events": False,
        "inference_authorized": False,
        "portfolio_profit_interval": False,
        "p_value": "NOT_COMPUTED",
    }


def newey_west_interval(values: Sequence[float], lag: int) -> dict[str, object]:
    """Exploratory Newey-West interval. The lag must be one of the predeclared lags."""

    if isinstance(lag, bool) or not isinstance(lag, int) or lag not in PREDECLARED_HAC_LAGS:
        _fail(
            "STATISTICAL_UNCERTAINTY_LAG_NOT_PREDECLARED",
            "HAC lag must be one of 1, 4, or 8",
        )
    parsed = _require_series(values)
    n = len(parsed)
    mean = _mean(parsed)
    if n < 2:
        return _unavailable_interval(
            status="UNAVAILABLE",
            reason="SAMPLE_SIZE_BELOW_TWO",
            mean=mean,
            n=n,
            extra={"lag": lag},
        )
    if all(value == parsed[0] for value in parsed):
        return _unavailable_interval(
            status="DEGENERATE_VARIANCE",
            reason="SAMPLE_VARIANCE_IS_ZERO",
            mean=mean,
            n=n,
            extra={"lag": lag},
        )
    if lag >= n:
        return _unavailable_interval(
            status="UNAVAILABLE",
            reason="LAG_NOT_IDENTIFIED",
            mean=mean,
            n=n,
            extra={"lag": lag},
        )
    centered = [value - mean for value in parsed]
    gamma0 = sum(value * value for value in centered) / n
    long_run = gamma0
    for step in range(1, lag + 1):
        gamma = sum(
            centered[index] * centered[index + step] for index in range(n - step)
        ) / n
        weight = 1.0 - (step / (lag + 1.0))
        long_run += 2.0 * weight * gamma
    if long_run <= 0.0:
        return _unavailable_interval(
            status="UNAVAILABLE",
            reason="NONPOSITIVE_LONG_RUN_VARIANCE",
            mean=mean,
            n=n,
            extra={"lag": lag, "long_run_variance": long_run},
        )
    standard_error = math.sqrt(long_run / n)
    half = Z_95 * standard_error
    return {
        "status": "EXPLORATORY_NOT_INFERENCE",
        "reason": "INTERVAL_UNDER_PREDECLARED_HAC_LAG",
        "mean": mean,
        "n": n,
        "lag": lag,
        "lag_selected_from_data": False,
        "long_run_variance": long_run,
        "standard_error": standard_error,
        "low": mean - half,
        "high": mean + half,
        "z_95": Z_95,
        "gamma_divisor": "n",
        "kernel": "Bartlett",
        "inference_authorized": False,
        "portfolio_profit_interval": False,
        "p_value": "NOT_COMPUTED",
    }


def _percentile_bounds(samples: Sequence[float]) -> tuple[int, int, float, float]:
    ordered = sorted(samples)
    draws = len(ordered)
    low_index = math.floor(0.025 * (draws - 1))
    high_index = math.ceil(0.975 * (draws - 1))
    if high_index >= draws:
        high_index = draws - 1
    if low_index < 0:
        low_index = 0
    return low_index, high_index, ordered[low_index], ordered[high_index]


def _block_means(
    values: Sequence[float],
    block_length: int,
    draws: int,
    rng: random.Random,
) -> list[float]:
    n = len(values)
    if block_length > n:
        _fail(
            "STATISTICAL_UNCERTAINTY_BLOCK_LONGER_THAN_SERIES",
            "block length exceeds the series",
        )
    starts = n - block_length + 1
    block_count = math.ceil(n / block_length)
    means: list[float] = []
    for _draw in range(draws):
        total = 0.0
        produced = 0
        for _block in range(block_count):
            start = rng.randrange(starts)
            for offset in range(block_length):
                if produced == n:
                    break
                total += values[start + offset]
                produced += 1
            if produced == n:
                break
        means.append(total / n)
    return means


def moving_block_bootstrap_interval(
    values: Sequence[float],
    block_length: int,
    *,
    draws: int,
    rng: random.Random,
) -> dict[str, object]:
    """Exploratory moving-block percentile interval. It does not produce a p-value."""

    if (
        isinstance(block_length, bool)
        or not isinstance(block_length, int)
        or block_length not in PREDECLARED_BLOCK_LENGTHS
    ):
        _fail(
            "STATISTICAL_UNCERTAINTY_BLOCK_NOT_PREDECLARED",
            "block length must be one of 1, 4, or 8",
        )
    if isinstance(draws, bool) or not isinstance(draws, int) or draws < 2:
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_BOOTSTRAP", "draws must be an integer above 1")
    if not isinstance(rng, random.Random):
        _fail("STATISTICAL_UNCERTAINTY_MISSING_SEED", "bootstrap requires random.Random")
    parsed = _require_series(values)
    n = len(parsed)
    mean = _mean(parsed)
    if n < 2:
        return _unavailable_interval(
            status="UNAVAILABLE",
            reason="SAMPLE_SIZE_BELOW_TWO",
            mean=mean,
            n=n,
            extra={"block_length": block_length},
        )
    if all(value == parsed[0] for value in parsed):
        return _unavailable_interval(
            status="DEGENERATE_VARIANCE",
            reason="SAMPLE_VARIANCE_IS_ZERO",
            mean=mean,
            n=n,
            extra={"block_length": block_length},
        )
    if block_length > n:
        return _unavailable_interval(
            status="UNAVAILABLE",
            reason="BLOCK_LONGER_THAN_SERIES",
            mean=mean,
            n=n,
            extra={"block_length": block_length},
        )
    samples = _block_means(parsed, block_length, draws, rng)
    low_index, high_index, low, high = _percentile_bounds(samples)
    return {
        "status": "EXPLORATORY_NOT_INFERENCE",
        "reason": "PERCENTILE_INTERVAL_UNDER_PREDECLARED_BLOCK_LENGTH",
        "mean": mean,
        "n": n,
        "block_length": block_length,
        "block_length_selected_from_data": False,
        "block_length_1_interprets_adjacent_outcomes_as_independent": block_length == 1,
        "recommended": False,
        "draws": draws,
        "percentile_low_index": low_index,
        "percentile_high_index": high_index,
        "low": low,
        "high": high,
        "standard_error": None,
        "inference_authorized": False,
        "portfolio_profit_interval": False,
        "p_value": "NOT_COMPUTED",
        "valid_p_value_claimed": False,
    }


def _aligned_rows(columns: Sequence[Sequence[float]]) -> list[list[float]]:
    if isinstance(columns, (str, bytes)) or not isinstance(columns, Sequence) or len(columns) < 2:
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "at least two aligned series are required")
    parsed = [_require_series(column) for column in columns]
    width = len(parsed[0])
    if any(len(column) != width for column in parsed):
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "aligned series must share a length")
    return [[column[index] for column in parsed] for index in range(width)]


def _synthetic_index_label(index: int) -> str:
    return f"synthetic-index-{index:04d}"


def _refuse_authentic_timeline(authentic_event_timeline: bool) -> None:
    if authentic_event_timeline is not False:
        _fail(
            "STATISTICAL_UNCERTAINTY_AUTHENTIC_TIMELINE_REFUSED",
            "authentic event timelines are not aligned by this method",
        )


def synthetic_clock_identity(
    *,
    length: int,
    series_count: int,
    clock_id: str | None,
    timestamps: Sequence[str] | None = None,
    authentic_event_timeline: bool = False,
) -> dict[str, object]:
    """Validate a caller-declared synthetic clock, or record that none was supplied.

    Equal length is not timestamp alignment. A synthetic clock id does not
    assert that authentic event timelines were aligned.
    """

    _refuse_authentic_timeline(authentic_event_timeline)
    if isinstance(length, bool) or not isinstance(length, int) or length < 1:
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "clock length must be a positive integer")
    if isinstance(series_count, bool) or not isinstance(series_count, int) or series_count < 2:
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "a shared clock needs at least two series")
    if timestamps is not None and clock_id is None:
        _fail(
            "STATISTICAL_UNCERTAINTY_CLOCK_IDENTITY_NOT_SYNTHETIC",
            "timestamps require a synthetic clock id",
        )
    if clock_id is None:
        return {
            "status": "NOT_SUPPLIED",
            "synthetic_clock_identity_validated": False,
            "equal_length_proves_timestamp_alignment": False,
            "authentic_event_timelines_aligned": False,
            "series_count": series_count,
            "length": length,
            "timestamp_status": "NOT_SUPPLIED",
            "reason": (
                "The inputs are caller-supplied numeric series. Equal length "
                "does not prove that those series share timestamps. No "
                "authentic event timeline was aligned."
            ),
        }
    if not isinstance(clock_id, str) or _SYNTHETIC_CLOCK_ID.fullmatch(clock_id) is None:
        _fail(
            "STATISTICAL_UNCERTAINTY_CLOCK_IDENTITY_NOT_SYNTHETIC",
            "clock id must be a synthetic-clock slug",
        )
    if len(clock_id) > 80:
        _fail(
            "STATISTICAL_UNCERTAINTY_CLOCK_IDENTITY_NOT_SYNTHETIC",
            "clock id exceeds the synthetic label bound",
        )
    timestamp_status = "NOT_SUPPLIED"
    if timestamps is not None:
        if isinstance(timestamps, (str, bytes)) or not isinstance(timestamps, Sequence):
            _fail(
                "STATISTICAL_UNCERTAINTY_CLOCK_TIMESTAMPS_NOT_SYNTHETIC",
                "timestamps must be synthetic index labels",
            )
        expected = [_synthetic_index_label(index) for index in range(length)]
        if list(timestamps) != expected:
            _fail(
                "STATISTICAL_UNCERTAINTY_CLOCK_TIMESTAMPS_NOT_SYNTHETIC",
                "timestamps must be the synthetic index labels for this length",
            )
        timestamp_status = "SYNTHETIC_INDEX_LABELS"
    return {
        "status": "SYNTHETIC_CLOCK_IDENTITY_VALIDATED",
        "clock_id": clock_id,
        "synthetic_clock_identity_validated": True,
        "equal_length_proves_timestamp_alignment": False,
        "authentic_event_timelines_aligned": False,
        "series_count": series_count,
        "length": length,
        "timestamp_status": timestamp_status,
        "reason": (
            "The caller declared a synthetic clock identity. Validation checks "
            "the synthetic id and, when supplied, the synthetic index labels. "
            "It does not read or align authentic event timelines."
        ),
    }


def _synthetic_clock_arguments(name: str, length: int) -> tuple[str, tuple[str, ...]]:
    clock_id = f"synthetic-clock-{name.replace('_', '-')}"
    timestamps = tuple(_synthetic_index_label(index) for index in range(length))
    return clock_id, timestamps


def _attach_clock(
    payload: dict[str, object],
    clock: Mapping[str, object],
    *,
    uses_shared_clock: bool,
) -> dict[str, object]:
    payload["clock_identity"] = dict(clock)
    payload["equal_length_proves_timestamp_alignment"] = False
    payload["authentic_event_timelines_aligned"] = False
    payload["inputs_are_caller_supplied_numeric_series"] = True
    payload["uses_declared_shared_clock"] = uses_shared_clock
    return payload


def shared_clock_block_bootstrap_interval(
    columns: Sequence[Sequence[float]],
    block_length: int,
    *,
    draws: int,
    rng: random.Random,
    clock_id: str | None = None,
    timestamps: Sequence[str] | None = None,
    authentic_event_timeline: bool = False,
) -> dict[str, object]:
    """Resample index blocks once and apply each draw to every supplied series.

    The series are caller-supplied numbers. Equal length does not prove that
    timestamps match, and a synthetic clock id is not an authentic timeline.
    """

    _refuse_authentic_timeline(authentic_event_timeline)
    if (
        isinstance(block_length, bool)
        or not isinstance(block_length, int)
        or block_length not in PREDECLARED_BLOCK_LENGTHS
    ):
        _fail(
            "STATISTICAL_UNCERTAINTY_BLOCK_NOT_PREDECLARED",
            "block length must be one of 1, 4, or 8",
        )
    if isinstance(draws, bool) or not isinstance(draws, int) or draws < 2:
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_BOOTSTRAP", "draws must be an integer above 1")
    if not isinstance(rng, random.Random):
        _fail("STATISTICAL_UNCERTAINTY_MISSING_SEED", "bootstrap requires random.Random")
    rows = _aligned_rows(columns)
    n = len(rows)
    width = len(rows[0])
    clock = synthetic_clock_identity(
        length=n,
        series_count=width,
        clock_id=clock_id,
        timestamps=timestamps,
        authentic_event_timeline=False,
    )
    point = [
        sum(row[column] for row in rows) / n
        for column in range(width)
    ]
    if n < 2 or block_length > n:
        return _attach_clock(
            _unavailable_interval(
                status="UNAVAILABLE",
                reason="SHARED_CLOCK_NOT_IDENTIFIED",
                mean=sum(point) / width,
                n=n,
                extra={"block_length": block_length, "series_count": width},
            ),
            clock,
            uses_shared_clock=True,
        )
    if all(row == rows[0] for row in rows):
        return _attach_clock(
            _unavailable_interval(
                status="DEGENERATE_VARIANCE",
                reason="SAMPLE_VARIANCE_IS_ZERO",
                mean=sum(point) / width,
                n=n,
                extra={"block_length": block_length, "series_count": width},
            ),
            clock,
            uses_shared_clock=True,
        )
    starts = n - block_length + 1
    block_count = math.ceil(n / block_length)
    column_draws = [[] for _column in range(width)]
    average_draws: list[float] = []
    for _draw in range(draws):
        chosen: list[list[float]] = []
        for _block in range(block_count):
            start = rng.randrange(starts)
            chosen.extend(rows[start : start + block_length])
            if len(chosen) >= n:
                break
        chosen = chosen[:n]
        draw_means = [
            sum(row[column] for row in chosen) / n
            for column in range(width)
        ]
        for column, value in enumerate(draw_means):
            column_draws[column].append(value)
        average_draws.append(sum(draw_means) / width)
    intervals = []
    for column, samples in enumerate(column_draws):
        low_index, high_index, low, high = _percentile_bounds(samples)
        intervals.append(
            {
                "column": column,
                "mean": point[column],
                "low": low,
                "high": high,
                "percentile_low_index": low_index,
                "percentile_high_index": high_index,
            }
        )
    avg_low_index, avg_high_index, avg_low, avg_high = _percentile_bounds(average_draws)
    return _attach_clock(
        {
            "status": "EXPLORATORY_NOT_INFERENCE",
            "reason": "SHARED_CLOCK_RESAMPLED_EACH_INDEX_ONCE",
            "n": n,
            "series_count": width,
            "block_length": block_length,
            "draws": draws,
            "resamples_each_time_once": True,
            "independently_resampled_columns": False,
            "column_intervals": intervals,
            "unweighted_average_of_column_means": {
                "mean": sum(point) / width,
                "low": avg_low,
                "high": avg_high,
                "percentile_low_index": avg_low_index,
                "percentile_high_index": avg_high_index,
                "simultaneously_executable_portfolio": False,
            },
            "inference_authorized": False,
            "portfolio_profit_interval": False,
            "p_value": "NOT_COMPUTED",
            "valid_p_value_claimed": False,
        },
        clock,
        uses_shared_clock=True,
    )


def independent_column_block_bootstrap_interval(
    columns: Sequence[Sequence[float]],
    block_length: int,
    *,
    draws: int,
    rng: random.Random,
    clock_id: str | None = None,
    timestamps: Sequence[str] | None = None,
    authentic_event_timeline: bool = False,
) -> dict[str, object]:
    """Incorrect diagnostic: resample each series on its own index sequence.

    This exists to show the failure mode. It is not a recommended estimator.
    A declared synthetic clock is recorded and then ignored.
    """

    _refuse_authentic_timeline(authentic_event_timeline)
    if (
        isinstance(block_length, bool)
        or not isinstance(block_length, int)
        or block_length not in PREDECLARED_BLOCK_LENGTHS
    ):
        _fail(
            "STATISTICAL_UNCERTAINTY_BLOCK_NOT_PREDECLARED",
            "block length must be one of 1, 4, or 8",
        )
    if isinstance(draws, bool) or not isinstance(draws, int) or draws < 2:
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_BOOTSTRAP", "draws must be an integer above 1")
    if not isinstance(rng, random.Random):
        _fail("STATISTICAL_UNCERTAINTY_MISSING_SEED", "bootstrap requires random.Random")
    rows = _aligned_rows(columns)
    n = len(rows)
    width = len(rows[0])
    clock = synthetic_clock_identity(
        length=n,
        series_count=width,
        clock_id=clock_id,
        timestamps=timestamps,
        authentic_event_timeline=False,
    )
    parsed = [[row[column] for row in rows] for column in range(width)]
    point = [_mean(column) for column in parsed]
    average_draws: list[float] = []
    column_draw_sets: list[list[float]] = []
    for column in parsed:
        column_draw_sets.append(_block_means(column, block_length, draws, rng))
    for draw in range(draws):
        average_draws.append(
            sum(column_draw_sets[column][draw] for column in range(width)) / width
        )
    low_index, high_index, low, high = _percentile_bounds(average_draws)
    column_intervals = []
    for column, samples in enumerate(column_draw_sets):
        column_low_index, column_high_index, column_low, column_high = _percentile_bounds(
            samples
        )
        column_intervals.append(
            {
                "column": column,
                "mean": point[column],
                "low": column_low,
                "high": column_high,
                "percentile_low_index": column_low_index,
                "percentile_high_index": column_high_index,
            }
        )
    return _attach_clock(
        {
            "status": "EXPLORATORY_NOT_INFERENCE",
            "reason": "INCORRECT_INDEPENDENT_COLUMN_RESAMPLE",
            "assumption_label": "incorrect_independence_across_series_that_share_an_index",
            "recommended": False,
            "n": n,
            "series_count": width,
            "block_length": block_length,
            "draws": draws,
            "resamples_each_time_once": False,
            "independently_resampled_columns": True,
            "declared_synthetic_clock_ignored": True,
            "column_intervals": column_intervals,
            "unweighted_average_of_independently_resampled_means": {
                "mean": sum(point) / width,
                "low": low,
                "high": high,
                "percentile_low_index": low_index,
                "percentile_high_index": high_index,
                "simultaneously_executable_portfolio": False,
            },
            "inference_authorized": False,
            "portfolio_profit_interval": False,
            "p_value": "NOT_COMPUTED",
            "valid_p_value_claimed": False,
        },
        clock,
        uses_shared_clock=False,
    )


def _normal_two_sided_p(z_value: float) -> float:
    p_value = math.erfc(abs(z_value) / math.sqrt(2.0))
    if p_value <= 0.0:
        return math.ldexp(1.0, -1074)
    if p_value > 1.0:
        return 1.0
    return p_value


def holm_adjusted_p_values(
    p_values: Sequence[float],
    *,
    source: str,
    assumptions_verified_for_synthetic_dgp: bool,
) -> dict[str, object]:
    """Holm step-down on caller-supplied p-values.

    The annual catalogue does not have valid individual p-values. This
    function refuses bootstrap sources and refuses the catalogue source.
    A true assumptions flag is a caller declaration about a synthetic DGP.
    It is not evidence about market data.
    """

    if source in {
        "block_bootstrap",
        "dependence_preserving_resample",
        "annual_catalogue",
        "event_evidence",
    }:
        _fail(
            "STATISTICAL_UNCERTAINTY_P_VALUES_NOT_VALID",
            "this source does not supply valid individual p-values",
        )
    if source != "known_sigma_gaussian_synthetic":
        _fail(
            "STATISTICAL_UNCERTAINTY_P_VALUE_SOURCE_REFUSED",
            "Holm accepts only the predeclared known-sigma synthetic source",
        )
    if assumptions_verified_for_synthetic_dgp is not True:
        return {
            "status": "NOT_APPLIED",
            "adjusted_p_values": None,
            "reason": "Individual p-values were not declared valid for the synthetic DGP.",
            "applied_to_annual_catalogue": False,
            "inference_authorized": False,
        }
    if isinstance(p_values, (str, bytes)) or not isinstance(p_values, Sequence):
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_P_VALUES", "p-values must be a sequence")
    cleaned: list[float] = []
    for value in p_values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            _fail("STATISTICAL_UNCERTAINTY_MALFORMED_P_VALUES", "p-values must be numbers in (0, 1]")
        p_value = float(value)
        if not math.isfinite(p_value) or p_value <= 0.0 or p_value > 1.0:
            _fail("STATISTICAL_UNCERTAINTY_MALFORMED_P_VALUES", "p-values must be numbers in (0, 1]")
        cleaned.append(p_value)
    family = len(cleaned)
    if family == 0:
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_P_VALUES", "the testing family is empty")
    if family > DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT:
        _fail(
            "STATISTICAL_UNCERTAINTY_FAMILY_ABOVE_FROZEN_UNIVERSE",
            "the family is larger than the frozen annual search universe",
        )
    order = sorted(range(family), key=lambda index: (cleaned[index], index))
    adjusted = [0.0] * family
    running = 0.0
    for rank, index in enumerate(order):
        raw = (family - rank) * cleaned[index]
        if raw > 1.0:
            raw = 1.0
        if raw > running:
            running = raw
        adjusted[index] = running
    return {
        "status": "EXPLORATORY_METHOD_CHECK",
        "adjusted_p_values": adjusted,
        "family_size": family,
        "alpha": HOLM_ALPHA,
        "source": source,
        "assumptions_verified_for_synthetic_dgp": True,
        "assumptions_verified_for_catalogue": False,
        "applied_to_annual_catalogue": False,
        "inference_authorized": False,
        "caller_declaration_is_not_market_evidence": True,
    }


def refuse_catalogue_multiple_testing() -> dict[str, object]:
    """The annual family is recorded. Holm is not applied to it."""

    return {
        "status": "NOT_APPLIED",
        "holm_applied_to_catalogue": False,
        "family_definition": "complete_frozen_annual_search_universe",
        "family_size_per_annual_segment": DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
        "shortlist_only_correction": False,
        "individual_p_values": "UNAVAILABLE",
        "selection_uncertainty": "UNAVAILABLE",
        "shared_event_dependence_accounted_in_a_valid_p_value": False,
        "dependence_preserving_resample_treated_as_p_value": False,
        "optimized_on_observed_false_passes": False,
        "per_segment_hypothesis_count_proves_cross_year_error_control": False,
        "multiple_testing_across_years_controlled": False,
        "selection_across_years_controlled": False,
        "real_catalogue_p_values_authorized": False,
        "strategy_v1_significance_claimed": False,
        "frozen_count_meaning": (
            "89460 is the frozen directional search universe of one annual "
            "segment. It is not proof that multiple testing or selection "
            "across years has been controlled."
        ),
        "reason": (
            "Event evidence and the cross-year engine do not supply valid "
            "individual p-values. Holm is withheld. A bounded synthetic "
            "method check does not stand in for the 89460-hypothesis family "
            "and does not control selection across years."
        ),
    }


def effective_sample_size_from_overlap(
    *,
    raw_observation_support: int,
    connected_episode_group_count: int,
) -> dict[str, object]:
    """Overlap counts do not identify an effective sample size."""

    if isinstance(raw_observation_support, bool) or not isinstance(raw_observation_support, int):
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_COUNTS", "raw support must be an integer")
    if isinstance(connected_episode_group_count, bool) or not isinstance(
        connected_episode_group_count, int
    ):
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_COUNTS", "episode group count must be an integer")
    if raw_observation_support < 0 or connected_episode_group_count < 0:
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_COUNTS", "counts must be non-negative")
    return {
        "status": "UNAVAILABLE",
        "value": None,
        "raw_observation_support": raw_observation_support,
        "connected_episode_group_count": connected_episode_group_count,
        "episode_group_count_used_as_value": False,
        "episode_groups_are_independent_trials": False,
        "ar1_finite_sample_formula_applied": False,
        "ar1_asymptotic_formula_applied": False,
        "authentic_event_evidence_requires_justified_dependence_model": True,
        "reason": (
            "A connected component of geometric overlap is not an independent "
            "trial. Serial dependence can remain between groups that do not "
            "overlap. No effective sample size is identified from these counts. "
            "Neither the finite-sample AR(1) variance-equivalent size nor the "
            "large-sample approximation is applied without a justified "
            "dependence model."
        ),
    }


def _standard_normal(rng: random.Random) -> float:
    while True:
        u1 = rng.random()
        if u1 > 0.0:
            break
    u2 = rng.random()
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


def _iid_series(rng: random.Random, n: int, mean: float, sigma: float) -> list[float]:
    return [mean + sigma * _standard_normal(rng) for _index in range(n)]


def _ar1_series(
    rng: random.Random,
    n: int,
    mean: float,
    sigma: float,
    phi: float,
) -> list[float]:
    stationary = sigma / math.sqrt(1.0 - phi * phi)
    current = mean + stationary * _standard_normal(rng)
    values = [current]
    for _index in range(1, n):
        shock = sigma * _standard_normal(rng)
        current = mean + phi * (current - mean) + shock
        values.append(current)
    return values


def _draw_scenario(
    spec: Mapping[str, object],
    rng: random.Random,
) -> dict[str, object]:
    kind = str(spec["kind"])
    n = int(spec["n"])
    true_mean = float(spec["true_mean"])
    sigma = float(spec.get("sigma", 1.0))
    if kind == "iid":
        primary = _iid_series(rng, n, true_mean, sigma)
        return {"primary": primary, "true_mean": true_mean}
    if kind == "iid_minus_cost":
        cost = float(spec["cost_pips"])
        primary = [value - cost for value in _iid_series(rng, n, 0.0, sigma)]
        return {
            "primary": primary,
            "true_mean": true_mean,
            "cost_pips_subtracted": cost,
            "cost_is_a_synthetic_shift_not_a_broker_model": True,
        }
    if kind == "ar1":
        phi = float(spec["phi"])
        primary = _ar1_series(rng, n, true_mean, sigma, phi)
        return {"primary": primary, "true_mean": true_mean, "phi": phi}
    if kind == "shared_event":
        primary = _iid_series(rng, n, true_mean, sigma)
        return {
            "primary": primary,
            "copy": list(primary),
            "true_mean": true_mean,
            "shared_event_count": n,
            "hypothesis_row_count": n * 2,
        }
    if kind == "overlap_horizons":
        span = int(spec["overlap_span"])
        shocks = _iid_series(rng, n + span - 1, 0.0, sigma)
        short = shocks[:n]
        long = [
            sum(shocks[index : index + span]) / span
            for index in range(n)
        ]
        return {
            "primary": long,
            "short_horizon": short,
            "true_mean": true_mean,
            "overlap_span": span,
        }
    if kind == "common_shock":
        common = _iid_series(rng, n, 0.0, sigma)
        symbol_a = [common[index] + sigma * _standard_normal(rng) for index in range(n)]
        symbol_b = [common[index] + sigma * _standard_normal(rng) for index in range(n)]
        pair = [(symbol_a[index] + symbol_b[index]) / 2.0 for index in range(n)]
        return {
            "primary": pair,
            "symbol_a": symbol_a,
            "symbol_b": symbol_b,
            "stacked": symbol_a + symbol_b,
            "true_mean": true_mean,
        }
    if kind == "constant":
        constant = float(spec["constant"])
        return {
            "primary": [constant for _index in range(n)],
            "true_mean": true_mean,
        }
    _fail("STATISTICAL_UNCERTAINTY_UNKNOWN_SCENARIO", kind)
    raise AssertionError


def binomial_monte_carlo_report(numerator: int, denominator: int) -> dict[str, object]:
    """Wilson interval and binomial standard error for a Monte Carlo rate.

    The Wilson interval uses the same 95 percent normal quantile as the
    exploratory normal intervals. A reported rate is not an exact population
    error rate. A zero denominator leaves the interval unavailable.
    """

    if isinstance(numerator, bool) or not isinstance(numerator, int):
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_COUNTS", "numerator must be an integer")
    if isinstance(denominator, bool) or not isinstance(denominator, int):
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_COUNTS", "denominator must be an integer")
    if numerator < 0 or denominator < 0 or numerator > denominator:
        _fail(
            "STATISTICAL_UNCERTAINTY_MALFORMED_COUNTS",
            "numerator and denominator are not a binomial count",
        )
    method = "sqrt(rate * (1 - rate) / denominator)"
    if denominator == 0:
        return {
            "numerator": numerator,
            "denominator": 0,
            "rate": None,
            "binomial_standard_error": None,
            "binomial_standard_error_method": method,
            "binomial_standard_error_understates_boundary_uncertainty": False,
            "wilson_interval_95": None,
            "interval_status": "UNAVAILABLE",
            "empirical_rate_is_exact_population_error_rate": False,
            "z_95": Z_95,
        }
    rate = numerator / denominator
    standard_error = math.sqrt(rate * (1.0 - rate) / denominator)
    z_squared = Z_95 * Z_95
    wilson_denominator = 1.0 + z_squared / denominator
    centre = (rate + z_squared / (2.0 * denominator)) / wilson_denominator
    half = (
        Z_95
        * math.sqrt(
            rate * (1.0 - rate) / denominator
            + z_squared / (4.0 * denominator * denominator)
        )
        / wilson_denominator
    )
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": rate,
        "binomial_standard_error": standard_error,
        "binomial_standard_error_method": method,
        "binomial_standard_error_understates_boundary_uncertainty": standard_error == 0.0,
        "wilson_interval_95": {
            "low": max(0.0, centre - half),
            "high": min(1.0, centre + half),
            "method": "wilson_score",
            "z": Z_95,
            "confidence_level": 0.95,
        },
        "interval_status": "REPORTED",
        "empirical_rate_is_exact_population_error_rate": False,
        "z_95": Z_95,
    }


def _ar1_weighted_autocorrelation_sum(n: int, phi: float) -> float:
    if phi == 0.0:
        return 0.0
    weighted_sum = 0.0
    phi_power = 1.0
    for lag in range(1, n):
        phi_power *= phi
        weighted_sum += (1.0 - lag / n) * phi_power
    return weighted_sum


def declared_ar1_effective_sample_size(n: int, phi: float) -> dict[str, object]:
    """Compare the finite-sample AR(1) size with its large-sample approximation.

    Both numbers use a declared phi. This function does not estimate phi and
    does not promote either number to authentic event evidence.
    """

    if isinstance(n, bool) or not isinstance(n, int):
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_COUNTS", "sample size must be an integer")
    if isinstance(phi, bool) or not isinstance(phi, (int, float)):
        _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "phi must be a finite number")
    phi_value = float(phi)
    if n < 2 or n > MAX_DECLARED_AR1_SAMPLE_SIZE:
        return {
            "status": "UNAVAILABLE",
            "value": None,
            "n": n,
            "phi": phi_value,
            "phi_estimated_from_sample": False,
            "identified_for_event_evidence": False,
            "promoted_to_authentic_event_evidence": False,
            "authentic_event_evidence_requires_justified_dependence_model": True,
            "reason": "The declared sample size is outside the bounded AR(1) formula.",
        }
    if not math.isfinite(phi_value) or abs(phi_value) >= 1.0:
        return {
            "status": "UNAVAILABLE",
            "value": None,
            "n": n,
            "phi": phi_value,
            "phi_estimated_from_sample": False,
            "identified_for_event_evidence": False,
            "promoted_to_authentic_event_evidence": False,
            "authentic_event_evidence_requires_justified_dependence_model": True,
            "reason": (
                "A stationary AR(1) autocorrelation phi**k requires absolute "
                "phi below 1. No effective sample size is reported."
            ),
        }
    weighted_sum = _ar1_weighted_autocorrelation_sum(n, phi_value)
    denominator = 1.0 + 2.0 * weighted_sum
    if denominator <= 0.0:
        return {
            "status": "UNAVAILABLE",
            "value": None,
            "n": n,
            "phi": phi_value,
            "phi_estimated_from_sample": False,
            "identified_for_event_evidence": False,
            "promoted_to_authentic_event_evidence": False,
            "reason": "The finite-sample variance weight was not positive.",
        }
    finite_sample = n / denominator
    asymptotic = n * (1.0 - phi_value) / (1.0 + phi_value)
    return {
        "status": "IDENTIFIED_UNDER_DECLARED_AR1_ASSUMPTION",
        "value": finite_sample,
        "value_definition": (
            "finite_sample_variance_equivalent_under_declared_stationary_autocorrelation"
        ),
        "n": n,
        "phi": phi_value,
        "phi_estimated_from_sample": False,
        "asymptotic_approximation_used_as_value": False,
        "finite_sample_variance_equivalent": {
            "value": finite_sample,
            "formula": "n / (1 + 2 * sum_{k=1}^{n-1} (1 - k/n) * phi**k)",
            "interpretation": (
                "Variance-equivalent sample size for the mean of a second-order "
                "stationary series whose autocorrelation at lag k is phi**k. "
                "The weights are the exact finite-sample weights. Phi is declared, "
                "not estimated."
            ),
        },
        "asymptotic_large_sample_approximation": {
            "value": asymptotic,
            "formula": "n * (1 - phi) / (1 + phi)",
            "interpretation": (
                "Large-sample approximation for a stationary AR(1). It replaces "
                "the finite-sample weights by an infinite sum. It is not the "
                "exact finite-sample variance of the mean."
            ),
        },
        "finite_minus_asymptotic": finite_sample - asymptotic,
        "formulas_are_the_same_expression": False,
        "marginal_variance_equivalent": True,
        "episode_group_count_used_as_value": False,
        "identified_for_event_evidence": False,
        "promoted_to_authentic_event_evidence": False,
        "authentic_event_evidence_requires_justified_dependence_model": True,
        "failure_mode": (
            "Both formulas use the declared phi. An estimated autocorrelation, "
            "or either formula applied to event evidence without that model, "
            "would be a different claim."
        ),
    }


class _Aggregate:
    def __init__(self) -> None:
        self.replications = 0
        self.available = 0
        self.unavailable = 0
        self.covering = 0
        self.excludes_zero = 0
        self.entirely_above_zero = 0
        self.width_sum = 0.0
        self.mean_sum = 0.0
        self.widths: list[float] = []

    def add(self, interval: Mapping[str, object], true_mean: float) -> None:
        self.replications += 1
        mean = interval.get("mean")
        if isinstance(mean, (int, float)) and not isinstance(mean, bool):
            self.mean_sum += float(mean)
        low = interval.get("low")
        high = interval.get("high")
        if (
            interval.get("status") == "EXPLORATORY_NOT_INFERENCE"
            and isinstance(low, (int, float))
            and isinstance(high, (int, float))
            and not isinstance(low, bool)
            and not isinstance(high, bool)
        ):
            low_value = float(low)
            high_value = float(high)
            self.available += 1
            width = high_value - low_value
            self.width_sum += width
            self.widths.append(width)
            if low_value <= true_mean <= high_value:
                self.covering += 1
            if high_value < 0.0 or low_value > 0.0:
                self.excludes_zero += 1
            if low_value > 0.0:
                self.entirely_above_zero += 1
        else:
            self.unavailable += 1

    def payload(self, true_mean: float) -> dict[str, object]:
        coverage_report = binomial_monte_carlo_report(self.covering, self.available)
        exclusion_report = binomial_monte_carlo_report(self.excludes_zero, self.available)
        above_report = binomial_monte_carlo_report(self.entirely_above_zero, self.available)
        if self.available == 0:
            mean_width = None
            median_width = None
            status = "DEGENERATE_VARIANCE" if self.unavailable == self.replications else "UNAVAILABLE"
            monte_carlo_conclusion = "UNAVAILABLE"
        else:
            mean_width = self.width_sum / self.available
            median_width = _median(self.widths)
            status = "EXPLORATORY_NOT_INFERENCE"
            monte_carlo_conclusion = "REPORTED_WITH_MONTE_CARLO_UNCERTAINTY"
        return {
            "status": status,
            "replications": self.replications,
            "intervals_available": self.available,
            "intervals_unavailable": self.unavailable,
            "coverage_of_true_mean_among_available": coverage_report["rate"],
            "coverage_of_true_mean": coverage_report,
            "coverage_counts_as_calibrated_error_control": False,
            "empirical_coverage_is_exact_population_error_rate": False,
            "intervals_excluding_zero": self.excludes_zero,
            "rate_excluding_zero_among_available": exclusion_report["rate"],
            "excluding_zero": exclusion_report,
            "intervals_entirely_above_zero": self.entirely_above_zero,
            "rate_entirely_above_zero_among_available": above_report["rate"],
            "entirely_above_zero": above_report,
            "monte_carlo_conclusion": monte_carlo_conclusion,
            "mean_interval_width": mean_width,
            "median_interval_width": median_width,
            "mean_of_sample_means": (
                self.mean_sum / self.replications if self.replications else None
            ),
            "true_mean": true_mean,
            "inference_authorized": False,
            "p_values_produced": False,
        }


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    count = len(ordered)
    mid = count // 2
    if count % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def _replication_seeds(seed: int, replications: int) -> list[int]:
    if seed in FORBIDDEN_TUNING_SEEDS:
        _fail(
            "STATISTICAL_UNCERTAINTY_FORBIDDEN_TUNING_SEED",
            "EXP-20261118-069 seeds are not reused",
        )
    rng = random.Random(seed)
    return [rng.randrange(2**31) for _index in range(replications)]


def _closed_form_names() -> tuple[tuple[str, int | None], ...]:
    names: list[tuple[str, int | None]] = [("iid_normal_interval", None)]
    for lag in PREDECLARED_HAC_LAGS:
        names.append((f"newey_west_lag_{lag}", lag))
    return tuple(names)


def _evaluate_closed_form(
    series: Sequence[float],
    method_name: str,
    lag: int | None,
) -> dict[str, object]:
    if method_name == "iid_normal_interval":
        return iid_normal_interval(series)
    if lag is None:
        _fail("STATISTICAL_UNCERTAINTY_LAG_NOT_PREDECLARED", "missing HAC lag")
    return newey_west_interval(series, lag)


def _scenario_effective_sample_size(spec: Mapping[str, object]) -> dict[str, object]:
    kind = str(spec["kind"])
    n = int(spec["n"])
    if kind == "constant":
        return {
            "status": "DEGENERATE_VARIANCE",
            "value": None,
            "reason": "A constant series does not identify a sampling variance.",
            "episode_group_count_used_as_value": False,
        }
    if kind == "iid" or kind == "iid_minus_cost":
        return {
            "status": "IDENTIFIED_UNDER_DECLARED_IID_ASSUMPTION",
            "value": n,
            "assumption": "The scenario declares independent observations.",
            "phi_estimated_from_sample": False,
            "episode_group_count_used_as_value": False,
            "identified_for_event_evidence": False,
        }
    if kind == "ar1":
        return declared_ar1_effective_sample_size(n, float(spec["phi"]))
    if kind == "shared_event":
        return {
            "status": "IDENTIFIED_UNDER_DECLARED_SHARED_EVENT_MODEL",
            "value": n,
            "incorrect_independent_hypothesis_rows": n * 2,
            "incorrect_row_count_used_as_value": False,
            "episode_group_count_used_as_value": False,
            "assumption": (
                "Both hypotheses copy one independent event series. The sample "
                "size of the shared mean is the event count."
            ),
            "identified_for_event_evidence": False,
        }
    return {
        "status": "UNAVAILABLE",
        "value": None,
        "reason": (
            "More than one dependence channel is present. No single effective "
            "sample size was predeclared for this scenario."
        ),
        "episode_group_count_used_as_value": False,
        "identified_for_event_evidence": False,
    }


def _run_scenario(spec: Mapping[str, object], seed: int) -> dict[str, object]:
    name = str(spec["name"])
    true_mean = float(spec["true_mean"])
    closed: dict[str, _Aggregate] = {
        method_name: _Aggregate() for method_name, _lag in _closed_form_names()
    }
    comparison: dict[str, _Aggregate] = {}
    if name == "shared_event_membership":
        comparison["incorrect_stacked_iid"] = _Aggregate()
        comparison["preserving_single_series_iid"] = _Aggregate()
    if name == "overlapping_horizons":
        comparison["short_horizon_iid"] = _Aggregate()
        comparison["long_horizon_iid"] = _Aggregate()
    if name == "common_shock_cross_symbol":
        comparison["incorrect_stacked_iid"] = _Aggregate()
        comparison["contemporaneous_average_iid"] = _Aggregate()
    bootstrap: dict[str, _Aggregate] = {}
    if name in _BOOTSTRAP_SCENARIOS:
        for block_length in PREDECLARED_BLOCK_LENGTHS:
            bootstrap[f"moving_block_{block_length}"] = _Aggregate()
        bootstrap["shared_clock_block_4"] = _Aggregate()
        bootstrap["incorrect_independent_columns_block_4"] = _Aggregate()

    for replication_seed in _replication_seeds(seed, CLOSED_FORM_REPLICATIONS):
        drawn = _draw_scenario(spec, random.Random(replication_seed))
        primary = drawn["primary"]
        if not isinstance(primary, list):
            _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "primary series missing")
        for method_name, lag in _closed_form_names():
            closed[method_name].add(
                _evaluate_closed_form(primary, method_name, lag),
                true_mean,
            )
        if name == "shared_event_membership":
            copy = drawn["copy"]
            if not isinstance(copy, list):
                _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "shared copy missing")
            stacked = primary + copy
            comparison["incorrect_stacked_iid"].add(iid_normal_interval(stacked), true_mean)
            comparison["preserving_single_series_iid"].add(
                iid_normal_interval(primary),
                true_mean,
            )
        if name == "overlapping_horizons":
            short = drawn["short_horizon"]
            if not isinstance(short, list):
                _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "short horizon missing")
            comparison["short_horizon_iid"].add(iid_normal_interval(short), true_mean)
            comparison["long_horizon_iid"].add(iid_normal_interval(primary), true_mean)
        if name == "common_shock_cross_symbol":
            stacked = drawn["stacked"]
            if not isinstance(stacked, list):
                _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "stacked series missing")
            comparison["incorrect_stacked_iid"].add(iid_normal_interval(stacked), true_mean)
            comparison["contemporaneous_average_iid"].add(
                iid_normal_interval(primary),
                true_mean,
            )
    if name in _BOOTSTRAP_SCENARIOS:
        for replication_seed in _replication_seeds(seed + 17, BOOTSTRAP_REPLICATIONS):
            drawn = _draw_scenario(spec, random.Random(replication_seed))
            primary = drawn["primary"]
            if not isinstance(primary, list):
                _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "primary series missing")
            for block_length in PREDECLARED_BLOCK_LENGTHS:
                bootstrap[f"moving_block_{block_length}"].add(
                    moving_block_bootstrap_interval(
                        primary,
                        block_length,
                        draws=BOOTSTRAP_DRAWS,
                        rng=random.Random(replication_seed + block_length),
                    ),
                    true_mean,
                )
            columns: list[list[float]]
            if name == "shared_event_membership":
                copy = drawn["copy"]
                if not isinstance(copy, list):
                    _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "shared copy missing")
                columns = [primary, copy]
            elif name == "common_shock_cross_symbol":
                symbol_a = drawn["symbol_a"]
                symbol_b = drawn["symbol_b"]
                if not isinstance(symbol_a, list) or not isinstance(symbol_b, list):
                    _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "symbol series missing")
                columns = [symbol_a, symbol_b]
            elif name == "overlapping_horizons":
                short = drawn["short_horizon"]
                if not isinstance(short, list):
                    _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "short horizon missing")
                columns = [short, primary]
            else:
                columns = [primary, list(primary)]
            clock_id, timestamps = _synthetic_clock_arguments(name, len(primary))
            shared = shared_clock_block_bootstrap_interval(
                columns,
                4,
                draws=BOOTSTRAP_DRAWS,
                rng=random.Random(replication_seed + 101),
                clock_id=clock_id,
                timestamps=timestamps,
                authentic_event_timeline=False,
            )
            average = shared["unweighted_average_of_column_means"]
            if isinstance(average, Mapping):
                shared_interval = {
                    "status": shared["status"],
                    "mean": average["mean"],
                    "low": average["low"],
                    "high": average["high"],
                }
                bootstrap["shared_clock_block_4"].add(shared_interval, true_mean)
            incorrect = independent_column_block_bootstrap_interval(
                columns,
                4,
                draws=BOOTSTRAP_DRAWS,
                rng=random.Random(replication_seed + 202),
                clock_id=clock_id,
                timestamps=timestamps,
                authentic_event_timeline=False,
            )
            incorrect_average = incorrect[
                "unweighted_average_of_independently_resampled_means"
            ]
            if isinstance(incorrect_average, Mapping):
                incorrect_interval = {
                    "status": incorrect["status"],
                    "mean": incorrect_average["mean"],
                    "low": incorrect_average["low"],
                    "high": incorrect_average["high"],
                }
                bootstrap["incorrect_independent_columns_block_4"].add(
                    incorrect_interval,
                    true_mean,
                )
    bootstrap_payload: dict[str, object]
    if name in _BOOTSTRAP_SCENARIOS:
        bootstrap_payload = {
            "status": "EXPLORATORY_NOT_INFERENCE",
            "p_values_produced": False,
            "valid_p_value_claimed": False,
            "establishes_calibrated_confidence_intervals": False,
            "monte_carlo_conclusion": "UNRESOLVED",
            "monte_carlo_conclusion_reason": (
                "Twenty bootstrap replications describe exploratory percentile "
                "intervals. They do not establish calibrated confidence intervals, "
                "and the empirical rates are not population error rates."
            ),
            "synthetic_clock": {
                "clock_id": f"synthetic-clock-{name.replace('_', '-')}",
                "timestamp_label_rule": "synthetic-index-0000 through the last index",
                "synthetic_clock_identity_validated": True,
                "equal_length_proves_timestamp_alignment": False,
                "authentic_event_timelines_aligned": False,
            },
            "methods": {
                key: aggregate.payload(true_mean) for key, aggregate in bootstrap.items()
            },
        }
    else:
        bootstrap_payload = {
            "status": "NOT_RUN_FOR_THIS_SCENARIO",
            "reason": (
                "Block resampling is reserved for the predeclared dependence "
                "scenarios. Closed-form diagnostics still run."
            ),
            "p_values_produced": False,
        }
    return {
        "scenario_name": name,
        "predeclared": True,
        "kind": spec["kind"],
        "series_length": spec["n"],
        "true_mean": true_mean,
        "sigma": spec.get("sigma"),
        "phi": spec.get("phi"),
        "cost_pips": spec.get("cost_pips"),
        "overlap_span": spec.get("overlap_span"),
        "primary_false_positive": spec["primary_false_positive"],
        "primary_seed": seed,
        "closed_form_replications": CLOSED_FORM_REPLICATIONS,
        "estimand": "mean of the synthetic net-pip series",
        "portfolio_profit": False,
        "overlapping_signals_are_simultaneously_executable_independent_trades": False,
        "closed_form": {
            method_name: aggregate.payload(true_mean)
            for method_name, aggregate in closed.items()
        },
        "dependence_comparisons": {
            key: aggregate.payload(true_mean) for key, aggregate in comparison.items()
        },
        "bootstrap": bootstrap_payload,
        "effective_sample_size": _scenario_effective_sample_size(spec),
        "inference_authorized": False,
    }


def _holm_null_totals(rng: random.Random, *, correlated: bool) -> list[float]:
    if not correlated:
        totals: list[float] = []
        for _hypothesis in range(HOLM_METHOD_CHECK_FAMILY):
            total = 0.0
            for _index in range(HOLM_METHOD_CHECK_SERIES_LENGTH):
                total += _standard_normal(rng)
            totals.append(total)
        return totals
    sums = [0.0 for _hypothesis in range(HOLM_METHOD_CHECK_FAMILY)]
    scale = math.sqrt(2.0)
    for _index in range(HOLM_METHOD_CHECK_SERIES_LENGTH):
        common = _standard_normal(rng)
        for hypothesis in range(HOLM_METHOD_CHECK_FAMILY):
            idiosyncratic = _standard_normal(rng)
            sums[hypothesis] += (common + idiosyncratic) / scale
    return sums


def _holm_complete_null(*, seed: int, correlated: bool) -> dict[str, object]:
    if seed in FORBIDDEN_TUNING_SEEDS:
        _fail(
            "STATISTICAL_UNCERTAINTY_FORBIDDEN_TUNING_SEED",
            "EXP-20261118-069 seeds are not reused",
        )
    rng = random.Random(seed)
    uncorrected = 0
    holm_rejections = 0
    standard_error = math.sqrt(1.0 / HOLM_METHOD_CHECK_SERIES_LENGTH)
    for _replication in range(HOLM_METHOD_CHECK_REPLICATIONS):
        p_values: list[float] = []
        for total in _holm_null_totals(rng, correlated=correlated):
            mean = total / HOLM_METHOD_CHECK_SERIES_LENGTH
            p_values.append(_normal_two_sided_p(mean / standard_error))
        adjusted = holm_adjusted_p_values(
            p_values,
            source="known_sigma_gaussian_synthetic",
            assumptions_verified_for_synthetic_dgp=True,
        )
        values = adjusted["adjusted_p_values"]
        if not isinstance(values, list):
            _fail("STATISTICAL_UNCERTAINTY_MALFORMED_P_VALUES", "Holm result missing")
        if any(p_value <= HOLM_ALPHA for p_value in p_values):
            uncorrected += 1
        if any(float(p_value) <= HOLM_ALPHA for p_value in values):
            holm_rejections += 1
    uncorrected_report = binomial_monte_carlo_report(
        uncorrected,
        HOLM_METHOD_CHECK_REPLICATIONS,
    )
    holm_report = binomial_monte_carlo_report(
        holm_rejections,
        HOLM_METHOD_CHECK_REPLICATIONS,
    )
    return {
        "seed": seed,
        "correlated_null": correlated,
        "dependence": "shared_gaussian_shock" if correlated else "independent_hypotheses",
        "marginal_variance": 1.0,
        "marginal_p_values_valid_under_synthetic_dgp": True,
        "catalogue_p_values_used": False,
        "uncorrected_familywise_rejections": uncorrected,
        "holm_familywise_rejections": holm_rejections,
        "uncorrected_familywise_rate": uncorrected_report["rate"],
        "holm_familywise_rate": holm_report["rate"],
        "uncorrected_familywise": uncorrected_report,
        "holm_familywise": holm_report,
        "familywise_calibration_conclusion": "UNRESOLVED",
        "familywise_calibration_reason": (
            "These replications do not establish a calibrated familywise error "
            "rate. The check is not the annual catalogue and it does not control "
            "selection across years."
        ),
        "empirical_rate_is_exact_population_error_rate": False,
    }


def _holm_method_check() -> dict[str, object]:
    independent = _holm_complete_null(seed=HOLM_METHOD_CHECK_SEED, correlated=False)
    correlated = _holm_complete_null(seed=HOLM_CORRELATED_NULL_SEED, correlated=True)
    return {
        "status": "EXPLORATORY_METHOD_CHECK",
        "inference_authorized": False,
        "applied_to_annual_catalogue": False,
        "holm_applied_to_catalogue": False,
        "source": "known_sigma_gaussian_synthetic",
        "seed": HOLM_METHOD_CHECK_SEED,
        "family_size": HOLM_METHOD_CHECK_FAMILY,
        "annual_family_size": DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
        "method_check_is_the_annual_universe": False,
        "replications": HOLM_METHOD_CHECK_REPLICATIONS,
        "series_length": HOLM_METHOD_CHECK_SERIES_LENGTH,
        "sigma_known": True,
        "alpha": HOLM_ALPHA,
        "complete_null": True,
        "uncorrected_familywise_rejections": independent["uncorrected_familywise_rejections"],
        "holm_familywise_rejections": independent["holm_familywise_rejections"],
        "uncorrected_familywise_rate": independent["uncorrected_familywise_rate"],
        "holm_familywise_rate": independent["holm_familywise_rate"],
        "uncorrected_familywise": independent["uncorrected_familywise"],
        "holm_familywise": independent["holm_familywise"],
        "familywise_calibration_conclusion": "UNRESOLVED",
        "independent_complete_null": independent,
        "correlated_complete_null": correlated,
        "error_control_claimed_for_catalogue": False,
        "bounded_method_check_controls_catalogue_wide_error": False,
        "bounded_method_check_controls_selection_across_years": False,
        "frozen_per_segment_search_universe": DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
        "per_segment_hypothesis_count_proves_cross_year_error_control": False,
        "real_catalogue_p_values_authorized": False,
        "strategy_v1_significance_claimed": False,
        "bootstrap_p_values_used": False,
        "optimized_on_observed_false_passes": False,
        "empirical_rate_is_exact_population_error_rate": False,
    }


def _mapping_payload(value: object, detail: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _fail("STATISTICAL_UNCERTAINTY_INTEGRITY", detail)
    return value


def _diagnostic(method_id: str, payload: Mapping[str, object]) -> dict[str, object]:
    role = _DIAGNOSTIC_ROLES.get(method_id)
    if role is None:
        _fail(
            "STATISTICAL_UNCERTAINTY_UNKNOWN_SCENARIO",
            f"no diagnostic role for {method_id}",
        )
    coverage = _mapping_payload(
        payload.get("coverage_of_true_mean"),
        "coverage Monte Carlo report is missing",
    )
    exclusion = _mapping_payload(
        payload.get("excluding_zero"),
        "exclusion Monte Carlo report is missing",
    )
    return {
        "method_id": method_id,
        "role": role,
        "coverage_of_true_mean": dict(coverage),
        "excluding_zero": dict(exclusion),
        "intervals_available": payload.get("intervals_available"),
        "intervals_unavailable": payload.get("intervals_unavailable"),
        "replications": payload.get("replications"),
        "empirical_coverage_is_exact_population_error_rate": False,
        "selected_by_observed_coverage": False,
    }


def _scenario_diagnostics(scenario: Mapping[str, object]) -> list[dict[str, object]]:
    diagnostics: list[dict[str, object]] = []
    closed = _mapping_payload(scenario.get("closed_form"), "closed form diagnostics are missing")
    for method_name, _lag in _closed_form_names():
        diagnostics.append(
            _diagnostic(method_name, _mapping_payload(closed.get(method_name), method_name))
        )
    comparisons = _mapping_payload(
        scenario.get("dependence_comparisons"),
        "dependence comparisons are missing",
    )
    for method_name, payload in comparisons.items():
        diagnostics.append(
            _diagnostic(
                str(method_name),
                _mapping_payload(payload, str(method_name)),
            )
        )
    bootstrap = _mapping_payload(scenario.get("bootstrap"), "bootstrap record is missing")
    methods = bootstrap.get("methods")
    if isinstance(methods, Mapping):
        for method_name, payload in methods.items():
            diagnostics.append(
                _diagnostic(
                    str(method_name),
                    _mapping_payload(payload, str(method_name)),
                )
            )
    return diagnostics


def _numeric_span(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "max": None, "range": None}
    low = min(values)
    high = max(values)
    return {"min": low, "max": high, "range": high - low}


def _rates_across_seeds(
    rows: Sequence[Mapping[str, object]],
    method_id: str,
    block_name: str,
) -> dict[str, float | None]:
    values: list[float] = []
    for row in rows:
        diagnostics = row.get("diagnostics")
        if not isinstance(diagnostics, list):
            continue
        for diagnostic in diagnostics:
            if not isinstance(diagnostic, Mapping) or diagnostic.get("method_id") != method_id:
                continue
            block = diagnostic.get(block_name)
            if isinstance(block, Mapping):
                rate = block.get("rate")
                if isinstance(rate, float):
                    values.append(rate)
    return _numeric_span(values)


def _variability_row(scenario: Mapping[str, object], seed: int) -> dict[str, object]:
    closed = _mapping_payload(scenario.get("closed_form"), "closed form diagnostics are missing")
    iid = _mapping_payload(closed.get("iid_normal_interval"), "iid interval is missing")
    return {
        "seed": seed,
        "scenario_name": scenario.get("scenario_name"),
        "paired_with_primary_calibration": seed == PRIMARY_CALIBRATION_SEED,
        "scenario_restarts_at_this_seed": True,
        "mean_of_sample_means": iid.get("mean_of_sample_means"),
        "diagnostics": _scenario_diagnostics(scenario),
    }


def _legacy_zero_edge_row(row: Mapping[str, object]) -> dict[str, object]:
    diagnostics = row.get("diagnostics")
    if not isinstance(diagnostics, list):
        _fail("STATISTICAL_UNCERTAINTY_INTEGRITY", "variability diagnostics are missing")
    iid = None
    for diagnostic in diagnostics:
        if isinstance(diagnostic, Mapping) and diagnostic.get("method_id") == "iid_normal_interval":
            iid = diagnostic
            break
    if not isinstance(iid, Mapping):
        _fail("STATISTICAL_UNCERTAINTY_INTEGRITY", "zero-edge iid diagnostic is missing")
    coverage = _mapping_payload(iid.get("coverage_of_true_mean"), "coverage report is missing")
    exclusion = _mapping_payload(iid.get("excluding_zero"), "exclusion report is missing")
    return {
        "seed": row.get("seed"),
        "scenario_name": "zero_edge_independent",
        "method_id": "iid_normal_interval",
        "coverage_of_true_mean_among_available": coverage.get("rate"),
        "coverage_numerator": coverage.get("numerator"),
        "coverage_denominator": coverage.get("denominator"),
        "coverage_wilson_interval_95": coverage.get("wilson_interval_95"),
        "rate_excluding_zero_among_available": exclusion.get("rate"),
        "excluding_zero_numerator": exclusion.get("numerator"),
        "excluding_zero_denominator": exclusion.get("denominator"),
        "excluding_zero_wilson_interval_95": exclusion.get("wilson_interval_95"),
        "mean_of_sample_means": row.get("mean_of_sample_means"),
        "empirical_coverage_is_exact_population_error_rate": False,
    }


def _variability(primary_scenarios: Sequence[Mapping[str, object]]) -> dict[str, object]:
    specs = {str(spec["name"]): spec for spec in _SCENARIOS}
    primary_by_name = {
        str(scenario.get("scenario_name")): scenario for scenario in primary_scenarios
    }
    scenario_reports: list[dict[str, object]] = []
    for name in VARIABILITY_SCENARIO_NAMES:
        spec = specs.get(name)
        primary = primary_by_name.get(name)
        if spec is None or primary is None:
            _fail("STATISTICAL_UNCERTAINTY_UNKNOWN_SCENARIO", name)
        rows: list[dict[str, object]] = []
        for seed in VARIABILITY_SEEDS:
            if seed in FORBIDDEN_TUNING_SEEDS:
                _fail(
                    "STATISTICAL_UNCERTAINTY_FORBIDDEN_TUNING_SEED",
                    "EXP-20261118-069 seeds are not reused",
                )
            scenario = primary if seed == PRIMARY_CALIBRATION_SEED else _run_scenario(spec, seed)
            rows.append(_variability_row(scenario, seed))
        method_ids: list[str] = []
        first_diagnostics = rows[0]["diagnostics"]
        if isinstance(first_diagnostics, list):
            for diagnostic in first_diagnostics:
                if isinstance(diagnostic, Mapping) and isinstance(diagnostic.get("method_id"), str):
                    method_ids.append(str(diagnostic["method_id"]))
        scenario_reports.append(
            {
                "scenario_name": name,
                "true_mean": 0.0,
                "excluding_zero_is_false_exclusion": True,
                "rows": rows,
                "coverage_across_seeds": {
                    method_id: _rates_across_seeds(rows, method_id, "coverage_of_true_mean")
                    for method_id in method_ids
                },
                "false_exclusion_across_seeds": {
                    method_id: _rates_across_seeds(rows, method_id, "excluding_zero")
                    for method_id in method_ids
                },
            }
        )
    if not scenario_reports or scenario_reports[0]["scenario_name"] != "zero_edge_independent":
        _fail("STATISTICAL_UNCERTAINTY_UNKNOWN_SCENARIO", "zero-edge variability is missing")
    zero_report = scenario_reports[0]
    zero_rows = zero_report["rows"]
    if not isinstance(zero_rows, list):
        _fail("STATISTICAL_UNCERTAINTY_INTEGRITY", "zero-edge variability rows are missing")
    legacy_rows = [
        _legacy_zero_edge_row(_mapping_payload(row, "variability row is missing"))
        for row in zero_rows
    ]
    coverages = [
        float(row["coverage_of_true_mean_among_available"])
        for row in legacy_rows
        if isinstance(row["coverage_of_true_mean_among_available"], float)
    ]
    return {
        "status": "EXPLORATORY_NOT_INFERENCE",
        "interpretation": "VARIABILITY_ACROSS_SEEDS_NOT_INDEPENDENT_REPLICATION_UNCERTAINTY",
        "seeds": list(VARIABILITY_SEEDS),
        "forbidden_tuning_seeds_excluded": list(FORBIDDEN_TUNING_SEEDS),
        "seeds_pooled_into_one_denominator": False,
        "seed_range_is_not_a_binomial_standard_error": True,
        "variability_across_seeds_is_independent_replication_uncertainty": False,
        "paired_noise_paths": (
            "Each scenario restarts at the supplied seed. Scenarios that "
            "consume the same normal draws share a noise path. The row at "
            "the primary seed is the primary calibration row, not an "
            "additional sample."
        ),
        "rows": legacy_rows,
        "coverage_span_scope": "zero_edge_independent iid_normal_interval across variability seeds",
        "coverage_min": min(coverages) if coverages else None,
        "coverage_max": max(coverages) if coverages else None,
        "coverage_range": (max(coverages) - min(coverages)) if coverages else None,
        "scenarios": scenario_reports,
        "used_to_choose_a_method": False,
        "used_to_choose_a_lag_block_length_or_threshold": False,
    }


def _monte_carlo_uncertainty_statement() -> dict[str, object]:
    return {
        "status": "REPORTED",
        "coverage_interval_method": "wilson_score",
        "rejection_interval_method": "wilson_score",
        "standard_error_method": "binomial sqrt(rate * (1 - rate) / denominator)",
        "z_95": Z_95,
        "closed_form_replications": CLOSED_FORM_REPLICATIONS,
        "bootstrap_replications": BOOTSTRAP_REPLICATIONS,
        "numerator_and_denominator_recorded": True,
        "unavailable_intervals_excluded_from_coverage_denominator": True,
        "unavailable_interval_count_recorded": True,
        "empirical_coverage_from_closed_form_replications_is_exact_population_error_rate": False,
        "exploratory_bootstrap_establishes_calibrated_confidence_intervals": False,
        "bootstrap_calibration_conclusion": "UNRESOLVED",
        "bootstrap_calibration_reason": (
            "Twenty bootstrap replications are an exploratory diagnostic. "
            "They do not establish calibrated confidence intervals."
        ),
        "seed_variability_is_independent_replication_uncertainty": False,
    }


def _calibration_body(provenance: UncertaintyProvenance) -> dict[str, object]:
    scenarios = [_run_scenario(spec, PRIMARY_CALIBRATION_SEED) for spec in _SCENARIOS]
    return {
        "uncertainty_version": STATISTICAL_UNCERTAINTY_VERSION,
        "uncertainty_protocol": STATISTICAL_UNCERTAINTY_PROTOCOL,
        "document_kind": "EXPLORATORY_SYNTHETIC_CALIBRATION",
        "governing_method": GOVERNING_RESEARCH_METHOD,
        "pattern_tool": PATTERN_TOOL,
        "evidence_basis": EVIDENCE_BASIS,
        "inference_status": "EXPLORATORY_NOT_INFERENCE",
        "inference_authorized": False,
        "error_control_claimed": False,
        "calibrated_error_control_claimed": False,
        "statistical_significance_claimed": False,
        "portfolio_profit_claimed": False,
        "overlapping_signals_are_simultaneously_executable_independent_trades": False,
        "used_exp_20261118_069_outcomes_to_tune": False,
        "used_to_retune_dec470": False,
        "caller_supplied_membership_is_feature_state_proof": False,
        "event_ids_recovered_from_event_fingerprint": False,
        "methods": _method_catalogue(),
        "scenarios": scenarios,
        "monte_carlo_uncertainty": _monte_carlo_uncertainty_statement(),
        "variability_across_seeds": _variability(scenarios),
        "multiple_testing": {
            "catalogue": refuse_catalogue_multiple_testing(),
            "synthetic_method_check": _holm_method_check(),
        },
        "scaling": _scaling_limits(),
        "recorded_boundaries": _recorded_boundaries(),
        "authorizations": _authorizations(),
        "provenance": _provenance_payload(provenance),
        "generator": {
            "name": "python-random-box-muller-v1",
            "primary_seed": PRIMARY_CALIBRATION_SEED,
            "replication_seed_rule": (
                "random.Random(primary_seed).randrange(2**31) draws one seed "
                "per closed-form replication. Each replication then uses "
                "random.Random(that seed). Each scenario restarts at the "
                "primary seed, so scenarios that consume the same normal draws "
                "share a noise path. Bootstrap replications use primary_seed "
                "+ 17 and do not advance the closed-form stream. Variability "
                "seeds are separate Random streams and are not pooled with "
                "the Monte Carlo denominator. The primary-seed variability "
                "row reuses the primary scenario."
            ),
            "box_muller": "sqrt(-2 log u1) cos(2 pi u2), redrawing u1 until it is positive",
        },
    }


def _finalize(body: dict[str, object]) -> tuple[dict[str, object], bytes]:
    digest = _sha256_json(body)
    document = dict(body)
    document["content_sha256"] = digest
    raw = _canonical_json(document)
    return document, raw


def compile_synthetic_calibration(
    provenance: UncertaintyProvenance | None,
) -> tuple[dict[str, object], bytes]:
    """Run the predeclared synthetic calibration. The result is not catalogue inference."""

    if provenance is None:
        _fail(
            "STATISTICAL_UNCERTAINTY_MISSING_PROVENANCE",
            "calibration requires provenance",
        )
    if not isinstance(provenance, UncertaintyProvenance):
        _fail(
            "STATISTICAL_UNCERTAINTY_MALFORMED_PROVENANCE",
            "provenance type mismatch",
        )
    document, raw = _finalize(_calibration_body(provenance))
    validate_uncertainty_document(raw)
    return document, raw


def _mapping(value: object, code: str, detail: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _fail(code, detail)
    return value


def _descriptive_scope(scope: Mapping[str, object]) -> dict[str, object]:
    return {
        "scope_id": scope.get("scope_id"),
        "raw_observation_support": scope.get("raw_observation_support"),
        "unique_observed_event_count": scope.get("unique_observed_event_count"),
        "overlapping_pair_count": scope.get("overlapping_pair_count"),
        "connected_episode_group_count": scope.get("connected_episode_group_count"),
        "candidate_effective_independent_sample_size_from_event_contract": scope.get(
            "candidate_effective_independent_sample_size"
        ),
        "candidate_count_used_as_effective_sample_size": False,
        "episode_groups_are_independent_trials": False,
    }


def _observed_mean(events: object) -> dict[str, object]:
    if not isinstance(events, list) or len(events) == 0:
        _fail("STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE", "events are missing")
    values: list[float] = []
    for event in events:
        if not isinstance(event, Mapping):
            _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "event payload is malformed")
        outcomes = event.get("directional_outcomes")
        if not isinstance(outcomes, list):
            _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "directional outcomes are missing")
        for outcome in outcomes:
            if not isinstance(outcome, Mapping):
                _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "directional outcome is malformed")
            value = outcome.get("net_pips_0p5")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "net pips are missing")
            number = float(value)
            if not math.isfinite(number):
                _fail("STATISTICAL_UNCERTAINTY_MALFORMED_SERIES", "net pips must be finite")
            values.append(number)
    if len(values) == 0:
        _fail("STATISTICAL_UNCERTAINTY_EMPTY_SAMPLE", "no directional nets were supplied")
    return {
        "status": "DESCRIPTIVE_SAMPLE_MEAN",
        "value": sum(values) / len(values),
        "observation_count": len(values),
        "sampling_uncertainty": "UNAVAILABLE",
        "standard_error": None,
        "confidence_interval": None,
        "realizable_portfolio_profit": "NOT_A_CLAIM",
        "overlapping_observations_counted_as_separate_sample_points": True,
        "simultaneously_executable": False,
        "reason": (
            "The number is the unweighted mean of supplied base nets. "
            "Dependence is not identified, so no standard error is attached. "
            "Overlapping signals are not simultaneously executable trades."
        ),
    }


def _assessment_body(event_document: Mapping[str, object]) -> dict[str, object]:
    counts = _mapping(
        event_document.get("counts"),
        "STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE",
        "event counts are missing",
    )
    scopes = event_document.get("overlap_scopes")
    if not isinstance(scopes, list):
        _fail("STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE", "overlap scopes are missing")
    cross_horizon = event_document.get("cross_horizon_scopes")
    if not isinstance(cross_horizon, list):
        _fail(
            "STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE",
            "cross-horizon scopes are missing",
        )
    cross_scope = _mapping(
        event_document.get("cross_scope_dependence"),
        "STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE",
        "cross-scope dependence is missing",
    )
    for key in (
        "cross_symbol_dependence_measured",
        "cross_timeframe_dependence_measured",
        "cross_direction_independence_established",
        "independence_established",
    ):
        if cross_scope.get(key) is not False:
            _fail(
                "STATISTICAL_UNCERTAINTY_EVENT_CONTRACT_DEPENDENCE_FLAG",
                f"{key} is not the frozen false flag",
            )
    hypothesis = _mapping(
        event_document.get("hypothesis_dependence"),
        "STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE",
        "hypothesis dependence is missing",
    )
    if hypothesis.get("independence_across_hypotheses_established") is not False:
        _fail(
            "STATISTICAL_UNCERTAINTY_EVENT_CONTRACT_DEPENDENCE_FLAG",
            "hypothesis independence is not established",
        )
    membership = _mapping(
        event_document.get("membership_validation"),
        "STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE",
        "membership validation is missing",
    )
    if membership.get("caller_supplied_membership_is_feature_state_proof") is not False:
        _fail(
            "STATISTICAL_UNCERTAINTY_MEMBERSHIP_BOUNDARY",
            "asserted membership is not feature-state proof",
        )
    statistical_limits = _mapping(
        event_document.get("statistical_limits"),
        "STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE",
        "event statistical limits are missing",
    )
    if statistical_limits.get("p_values") != "UNAVAILABLE_NOT_COMPUTED":
        _fail(
            "STATISTICAL_UNCERTAINTY_P_VALUES_NOT_VALID",
            "event evidence p-values are not available",
        )
    provenance = event_document.get("provenance")
    if not isinstance(provenance, Mapping):
        _fail(
            "STATISTICAL_UNCERTAINTY_MISSING_PROVENANCE",
            "event provenance is missing",
        )
    digest = event_document.get("content_sha256")
    if not isinstance(digest, str):
        _fail("STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE", "event content hash is missing")
    descriptive_scopes = [
        _descriptive_scope(_mapping(scope, "STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE", "scope"))
        for scope in scopes
    ]
    episode_counts = [
        int(scope["connected_episode_group_count"])
        for scope in descriptive_scopes
        if isinstance(scope["connected_episode_group_count"], int)
    ]
    return {
        "uncertainty_version": STATISTICAL_UNCERTAINTY_VERSION,
        "uncertainty_protocol": STATISTICAL_UNCERTAINTY_PROTOCOL,
        "document_kind": "EVENT_EVIDENCE_UNCERTAINTY_ASSESSMENT",
        "governing_method": GOVERNING_RESEARCH_METHOD,
        "pattern_tool": PATTERN_TOOL,
        "evidence_basis": EVIDENCE_BASIS,
        "inference_status": "UNAVAILABLE",
        "inference_authorized": False,
        "valid_sampling_uncertainty_established": False,
        "statistical_significance_claimed": False,
        "error_control_claimed": False,
        "portfolio_profit_claimed": False,
        "source_event_evidence_content_sha256": digest,
        "source_event_provenance": {
            "source_label": provenance.get("source_label"),
            "code_commit": provenance.get("code_commit"),
            "synthetic_manifest_sha256": provenance.get("synthetic_manifest_sha256"),
            "historical_artifact_read": False,
        },
        "descriptive_counts": {
            "raw_observation_support": counts.get("raw_observation_support"),
            "unique_observed_event_count": counts.get("event_count"),
            "within_horizon_scopes": descriptive_scopes,
            "cross_horizon_scope_ids": [
                scope.get("scope_id")
                for scope in cross_horizon
                if isinstance(scope, Mapping)
            ],
            "sum_of_connected_episode_group_counts": sum(episode_counts),
            "episode_group_count_is_an_independent_trial_count": False,
            "sum_of_within_horizon_candidate_sizes_from_event_contract": counts.get(
                "sum_of_within_horizon_candidate_sizes"
            ),
            "candidate_sum_used_as_effective_sample_size": False,
        },
        "observed_mean_net_pips_0p5": _observed_mean(event_document.get("events")),
        "quantities": {
            "serial_dependence_beyond_geometric_overlap": {
                "status": "UNAVAILABLE",
                "reason": (
                    "The overlap graph is not an autocovariance model. Groups "
                    "that only touch, and groups that are separate, can still "
                    "be serially dependent."
                ),
            },
            "dependence_across_horizons_symbols_and_timeframes": {
                "status": "UNAVAILABLE",
                "event_contract_cross_symbol_dependence_measured": False,
                "event_contract_cross_timeframe_dependence_measured": False,
                "event_contract_independence_established": False,
                "reason": (
                    "The event contract records these channels as unmeasured. "
                    "This assessment does not add a measurement."
                ),
            },
            "effective_sample_size": effective_sample_size_from_overlap(
                raw_observation_support=int(counts["raw_observation_support"]),
                connected_episode_group_count=sum(episode_counts),
            ),
            "sampling_uncertainty": {
                "status": "UNAVAILABLE",
                "confidence_interval": None,
                "standard_error": None,
                "reason": "No dependence model is identified from the event document.",
            },
            "multiple_hypothesis_and_selection_uncertainty": refuse_catalogue_multiple_testing(),
        },
        "hypothesis_dependence": {
            "events_shared_by_multiple_hypotheses": hypothesis.get(
                "events_shared_by_multiple_hypotheses"
            ),
            "max_hypotheses_sharing_one_event": hypothesis.get(
                "max_hypotheses_sharing_one_event"
            ),
            "independence_across_hypotheses_established": False,
            "shared_event_dependence_in_sampling_distribution": "UNAVAILABLE",
        },
        "membership": {
            "caller_supplied_membership_is_feature_state_proof": False,
            "asserted_membership_treated_as_feature_evidence": False,
        },
        "event_fingerprint_recovery": "REFUSED",
        "methods_not_applied_to_event_evidence": [
            "iid_normal_interval",
            "newey_west_bartlett",
            "moving_block_bootstrap",
            "shared_clock_block_bootstrap",
            "holm_method_check",
        ],
        "scaling": _scaling_limits(),
        "recorded_boundaries": _recorded_boundaries(),
        "authorizations": _authorizations(),
    }


def assess_event_evidence_uncertainty(
    document: Mapping[str, object] | bytes | str,
    *,
    assume_independence: bool = False,
    treat_episode_groups_as_independent_trials: bool = False,
) -> tuple[dict[str, object], bytes]:
    """Describe uncertainty limits of a validated synthetic event document.

    Inferential quantities stay unavailable. Independence and episode-group
    trial counts are refused rather than estimated.
    """

    if assume_independence:
        _fail(
            "STATISTICAL_UNCERTAINTY_INDEPENDENCE_ASSUMPTION_REFUSED",
            "event evidence does not justify an independence assumption",
        )
    if treat_episode_groups_as_independent_trials:
        _fail(
            "STATISTICAL_UNCERTAINTY_EPISODE_GROUPS_ARE_NOT_TRIALS",
            "episode groups are not independent trials",
        )
    validated = validate_event_evidence(document)
    try:
        recover_event_ids_from_event_fingerprint("0" * 64)
    except ValueError as exc:
        if not str(exc).startswith("EVENT_EVIDENCE_EVENT_FINGERPRINT_RECOVERY_REFUSED"):
            raise
    else:
        _fail(
            "STATISTICAL_UNCERTAINTY_EVENT_FINGERPRINT_RECOVERY",
            "event fingerprint recovery did not fail closed",
        )
    body = _assessment_body(validated)
    assessment, raw = _finalize(body)
    validate_uncertainty_document(raw, event_document=validated)
    return assessment, raw


def _object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    parsed: dict[str, object] = {}
    for key, value in pairs:
        if key in parsed:
            _fail(
                "STATISTICAL_UNCERTAINTY_NONCANONICAL_JSON",
                f"duplicate JSON object key {key!r}",
            )
        parsed[key] = value
    return parsed


def _require_canonical_bytes(raw: bytes) -> dict[str, object]:
    if raw.startswith(b"\xef\xbb\xbf"):
        _fail("STATISTICAL_UNCERTAINTY_NONCANONICAL_JSON", "UTF-8 BOM is not canonical JSON")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        _fail(
            "STATISTICAL_UNCERTAINTY_NONCANONICAL_JSON",
            "serialized uncertainty must be canonical UTF-8 JSON",
        )
        raise AssertionError
    try:
        parsed = json.loads(text, object_pairs_hook=_object_without_duplicate_keys)
    except json.JSONDecodeError:
        _fail("STATISTICAL_UNCERTAINTY_INTEGRITY", "document is not JSON")
        raise AssertionError
    if not isinstance(parsed, dict):
        _fail("STATISTICAL_UNCERTAINTY_INTEGRITY", "document must be a JSON object")
    try:
        canonical = _canonical_json(parsed)
    except (TypeError, ValueError):
        _fail(
            "STATISTICAL_UNCERTAINTY_NONCANONICAL_JSON",
            "serialized uncertainty is not canonical JSON",
        )
        raise AssertionError
    if raw != canonical:
        _fail(
            "STATISTICAL_UNCERTAINTY_NONCANONICAL_JSON",
            "serialized uncertainty must match canonical JSON bytes",
        )
    return parsed


def _reject_closed_boundary(document: Mapping[str, object]) -> None:
    if document.get("inference_authorized") is not False:
        _fail("STATISTICAL_UNCERTAINTY_AUTHORIZATION", "inference is not authorized")
    if document.get("error_control_claimed") is not False:
        _fail("STATISTICAL_UNCERTAINTY_AUTHORIZATION", "error control is not claimed")
    if document.get("statistical_significance_claimed") is not False:
        _fail("STATISTICAL_UNCERTAINTY_AUTHORIZATION", "significance is not claimed")
    if document.get("portfolio_profit_claimed") is not False:
        _fail("STATISTICAL_UNCERTAINTY_AUTHORIZATION", "portfolio profit is not claimed")
    authorizations = document.get("authorizations")
    if not isinstance(authorizations, Mapping) or any(authorizations.values()):
        _fail("STATISTICAL_UNCERTAINTY_AUTHORIZATION", "an authorization flag is open")
    if document.get("used_to_retune_dec470") is True:
        _fail("STATISTICAL_UNCERTAINTY_AUTHORIZATION", "DEC-470 was not retuned")
    boundaries = document.get("recorded_boundaries")
    if isinstance(boundaries, Mapping) and boundaries.get("dec470_thresholds_modified") is not False:
        _fail("STATISTICAL_UNCERTAINTY_AUTHORIZATION", "DEC-470 thresholds were modified")


def validate_uncertainty_document(
    document: Mapping[str, object] | bytes | str,
    event_document: Mapping[str, object] | bytes | str | None = None,
) -> dict[str, object]:
    """Recompute a canonical uncertainty document and reject tampered bytes."""

    if isinstance(document, str):
        document = document.encode("utf-8")
    if isinstance(document, bytes):
        parsed = _require_canonical_bytes(document)
    elif isinstance(document, Mapping):
        parsed = dict(document)
    else:
        _fail("STATISTICAL_UNCERTAINTY_INTEGRITY", "document must be a mapping or canonical bytes")
        raise AssertionError
    digest = parsed.get("content_sha256")
    body = {key: value for key, value in parsed.items() if key != "content_sha256"}
    if digest != _sha256_json(body):
        _fail("STATISTICAL_UNCERTAINTY_INTEGRITY", "content sha256 does not match the canonical body")
    _reject_closed_boundary(parsed)
    kind = parsed.get("document_kind")
    if kind == "EXPLORATORY_SYNTHETIC_CALIBRATION":
        if parsed.get("used_exp_20261118_069_outcomes_to_tune") is not False:
            _fail(
                "STATISTICAL_UNCERTAINTY_AUTHORIZATION",
                "EXP-20261118-069 outcomes were used to tune the calibration",
            )
        provenance_raw = parsed.get("provenance")
        if not isinstance(provenance_raw, Mapping):
            _fail("STATISTICAL_UNCERTAINTY_MISSING_PROVENANCE", "provenance is missing")
        provenance = UncertaintyProvenance(
            source_label=str(provenance_raw.get("source_label")),
            code_commit=str(provenance_raw.get("code_commit")),
            synthetic_manifest_sha256=str(provenance_raw.get("synthetic_manifest_sha256")),
        )
        rebuilt = _calibration_body(provenance)
        if rebuilt != body:
            _fail(
                "STATISTICAL_UNCERTAINTY_INTEGRITY",
                "document does not match the canonical calibration",
            )
    elif kind == "EVENT_EVIDENCE_UNCERTAINTY_ASSESSMENT":
        if event_document is None:
            _fail(
                "STATISTICAL_UNCERTAINTY_MISSING_EVENT_EVIDENCE",
                "assessment validation requires the source event document",
            )
        validated = validate_event_evidence(event_document)
        if validated.get("content_sha256") != parsed.get("source_event_evidence_content_sha256"):
            _fail(
                "STATISTICAL_UNCERTAINTY_INTEGRITY",
                "event evidence hash does not match the assessment",
            )
        if parsed.get("valid_sampling_uncertainty_established") is not False:
            _fail(
                "STATISTICAL_UNCERTAINTY_AUTHORIZATION",
                "sampling uncertainty was not established",
            )
        quantities = parsed.get("quantities")
        if not isinstance(quantities, Mapping):
            _fail("STATISTICAL_UNCERTAINTY_INTEGRITY", "quantities are missing")
        effective = quantities.get("effective_sample_size")
        if not isinstance(effective, Mapping) or effective.get("value") is not None:
            _fail(
                "STATISTICAL_UNCERTAINTY_EPISODE_GROUPS_ARE_NOT_TRIALS",
                "effective sample size is unavailable",
            )
        if effective.get("episode_group_count_used_as_value") is not False:
            _fail(
                "STATISTICAL_UNCERTAINTY_EPISODE_GROUPS_ARE_NOT_TRIALS",
                "episode groups were used as the effective sample size",
            )
        multiple = quantities.get("multiple_hypothesis_and_selection_uncertainty")
        if not isinstance(multiple, Mapping) or multiple.get("holm_applied_to_catalogue") is not False:
            _fail(
                "STATISTICAL_UNCERTAINTY_P_VALUES_NOT_VALID",
                "Holm was applied to the catalogue",
            )
        rebuilt = _assessment_body(validated)
        if rebuilt != body:
            _fail(
                "STATISTICAL_UNCERTAINTY_INTEGRITY",
                "document does not match the canonical assessment",
            )
    else:
        _fail("STATISTICAL_UNCERTAINTY_INTEGRITY", "document kind is not recognized")
    parsed["content_sha256"] = digest
    return parsed


def statistical_uncertainty_contract() -> dict[str, object]:
    """Static contract. It contains no observations and no inference."""

    return {
        "uncertainty_version": STATISTICAL_UNCERTAINTY_VERSION,
        "uncertainty_protocol": STATISTICAL_UNCERTAINTY_PROTOCOL,
        "governing_method": GOVERNING_RESEARCH_METHOD,
        "pattern_tool": PATTERN_TOOL,
        "evidence_basis": EVIDENCE_BASIS,
        "recorded_boundaries": _recorded_boundaries(),
        "methods": _method_catalogue(),
        "scaling": _scaling_limits(),
        "authorizations": _authorizations(),
        "event_evidence_inference_status": "UNAVAILABLE",
        "episode_groups_are_independent_trials": False,
        "catalogue_holm_applied": False,
    }


def measure_representative_workload(
    provenance: UncertaintyProvenance,
) -> dict[str, object]:
    """Time and peak traced memory for one predeclared calibration."""

    tracemalloc.start()
    started = time.perf_counter()
    document, raw = compile_synthetic_calibration(provenance)
    elapsed = time.perf_counter() - started
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "elapsed_seconds": elapsed,
        "tracemalloc_peak_bytes": peak,
        "canonical_bytes": len(raw),
        "content_sha256": document["content_sha256"],
        "scenario_count": len(document["scenarios"]) if isinstance(document.get("scenarios"), list) else 0,
        "historical_artifact_read": False,
    }


if DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT != 89460:
    raise ValueError("STATISTICAL_UNCERTAINTY_SEARCH_UNIVERSE_DRIFT")
if protocol_fingerprint() != EXPECTED_PROTOCOL_FINGERPRINT:
    raise ValueError("STATISTICAL_UNCERTAINTY_PROTOCOL_FINGERPRINT_DRIFT")
if MIN_ANNUAL_EVALUABLE_SUPPORT != 75:
    raise ValueError("STATISTICAL_UNCERTAINTY_THRESHOLD_DRIFT")
if MIN_CROSS_YEAR_EVALUABLE_SEGMENTS != 9:
    raise ValueError("STATISTICAL_UNCERTAINTY_THRESHOLD_DRIFT")
if MIN_BASE_POSITIVE_FRACTION != 0.80:
    raise ValueError("STATISTICAL_UNCERTAINTY_THRESHOLD_DRIFT")
if MIN_STRESS_POSITIVE_FRACTION != 2.0 / 3.0:
    raise ValueError("STATISTICAL_UNCERTAINTY_THRESHOLD_DRIFT")
if MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5 != 0.10:
    raise ValueError("STATISTICAL_UNCERTAINTY_THRESHOLD_DRIFT")
if MIN_POOLED_MEAN_NET_PIPS_0P5 != 0.25:
    raise ValueError("STATISTICAL_UNCERTAINTY_THRESHOLD_DRIFT")
if REQUIRE_POOLED_STRESS_MEAN_POSITIVE is not True:
    raise ValueError("STATISTICAL_UNCERTAINTY_THRESHOLD_DRIFT")
if MAX_SIGN_FLIPS != 3:
    raise ValueError("STATISTICAL_UNCERTAINTY_THRESHOLD_DRIFT")
if NEAR_DUPLICATE_JACCARD != 0.90:
    raise ValueError("STATISTICAL_UNCERTAINTY_THRESHOLD_DRIFT")
if GOVERNING_RESEARCH_METHOD != "DISCOVERY_FIRST_ANNUAL_PATTERN_CATALOGUE":
    raise ValueError("STATISTICAL_UNCERTAINTY_METHOD_DRIFT")
if PRIMARY_CALIBRATION_SEED not in VARIABILITY_SEEDS:
    raise ValueError("STATISTICAL_UNCERTAINTY_SEED_DRIFT")
if HOLM_CORRELATED_NULL_SEED in FORBIDDEN_TUNING_SEEDS or HOLM_CORRELATED_NULL_SEED in VARIABILITY_SEEDS:
    raise ValueError("STATISTICAL_UNCERTAINTY_SEED_DRIFT")
if HOLM_CORRELATED_NULL_SEED == HOLM_METHOD_CHECK_SEED:
    raise ValueError("STATISTICAL_UNCERTAINTY_SEED_DRIFT")
if set(VARIABILITY_SEEDS) & set(FORBIDDEN_TUNING_SEEDS):
    raise ValueError("STATISTICAL_UNCERTAINTY_SEED_DRIFT")
if any(
    (
        EVENT_HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        EVENT_HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
        EVENT_STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        EVENT_STATISTICAL_PROMOTION_AUTHORIZED,
        EVENT_TRADING_AUTHORIZED,
        EVENT_WORKFLOW_ACTIVATION_AUTHORIZED,
        EVENT_DEC629_ADOPTED,
        EVENT_DEC630_ADOPTED,
        EVENT_ANNUAL_RUN_385_CONSUMED,
    )
):
    raise ValueError("STATISTICAL_UNCERTAINTY_AUTHORIZATION_DRIFT")
if any(value for _key, value in _AUTHORIZATION_FLAGS):
    raise ValueError("STATISTICAL_UNCERTAINTY_AUTHORIZATION_DRIFT")


__all__ = [
    "ANNUAL_RUN_385_CONSUMED",
    "BOOTSTRAP_DRAWS",
    "BOOTSTRAP_REPLICATIONS",
    "CLOSED_FORM_REPLICATIONS",
    "DEC629_ADOPTED",
    "DEC630_ADOPTED",
    "EXPECTED_PROTOCOL_FINGERPRINT",
    "FORBIDDEN_TUNING_SEEDS",
    "HISTORICAL_ARTIFACT_READ_AUTHORIZED",
    "HOLM_CORRELATED_NULL_SEED",
    "HOLM_METHOD_CHECK_FAMILY",
    "PATTERN_TOOL",
    "PREDECLARED_BLOCK_LENGTHS",
    "PREDECLARED_HAC_LAGS",
    "PRIMARY_CALIBRATION_SEED",
    "STATISTICAL_UNCERTAINTY_PROTOCOL",
    "STATISTICAL_UNCERTAINTY_VERSION",
    "TRADING_AUTHORIZED",
    "VARIABILITY_SCENARIO_NAMES",
    "VARIABILITY_SEEDS",
    "WORKFLOW_ACTIVATION_AUTHORIZED",
    "UncertaintyProvenance",
    "assess_event_evidence_uncertainty",
    "binomial_monte_carlo_report",
    "compile_synthetic_calibration",
    "declared_ar1_effective_sample_size",
    "effective_sample_size_from_overlap",
    "holm_adjusted_p_values",
    "iid_normal_interval",
    "independent_column_block_bootstrap_interval",
    "measure_representative_workload",
    "moving_block_bootstrap_interval",
    "newey_west_interval",
    "refuse_catalogue_multiple_testing",
    "shared_clock_block_bootstrap_interval",
    "synthetic_clock_identity",
    "statistical_uncertainty_contract",
    "validate_uncertainty_document",
]
