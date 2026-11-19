"""Dependence-aware statistical validation for synthetic annual-catalogue questions.

Governing method: annual pattern catalogue discovery under DEC-469 / DEC-268.
Dependence-aware validation V1 is a pattern tool inside that method. It is not
a new governing method, not a replacement for the annual catalogue, and not a
significance test of historical patterns.

The harness is synthetic. It evaluates predeclared uncertainty procedures
under serial dependence, overlapping windows, shared events, common shocks,
and selection. It does not read market artifacts, mine catalogues, open
annual run 385, change DEC-470, or promote a pattern.

Calibration rows are development context. Acceptance uses the holdout
partition only. A passing synthetic check does not authorize catalogue
inference.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import time
import tracemalloc
from dataclasses import dataclass
from typing import Mapping, Sequence

from .annual_pattern_catalogue_event_evidence import (
    ANNUAL_RUN_385_CONSUMED as EVENT_ANNUAL_RUN_385_CONSUMED,
    DEC629_ADOPTED as EVENT_DEC629_ADOPTED,
    DEC630_ADOPTED as EVENT_DEC630_ADOPTED,
    recover_event_ids_from_event_fingerprint,
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


DEPENDENCE_VALIDATION_VERSION = 1
DEPENDENCE_VALIDATION_PROTOCOL = (
    "fmp-annual-pattern-catalogue-dependence-validation-v1"
)
PATTERN_TOOL = "dependence-aware-validation-v1"
EVIDENCE_BASIS = "SYNTHETIC_DEPENDENCE_VALIDATION_NOT_MARKET_DATA"
EXPECTED_PROTOCOL_FINGERPRINT = (
    "3f883b26f3d9da04840b9680701504833dbcb3ec2c919f74ed191a3ab1bd3d69"
)
CORRELATED_NOISE_CALIBRATION_EXPERIMENT = "EXP-20261118-069"
STATISTICAL_UNCERTAINTY_CONTEXT_EXPERIMENT = "EXP-20261119-072"

# Masters named by EXP-20261118-069 and Statistical Uncertainty V1.
# Child streams redraw if they collide with one of these masters.
FORBIDDEN_MASTER_SEEDS = frozenset(range(20261118, 20261126))
CALIBRATION_MASTER_SEED = 20261126
FAMILY_CALIBRATION_SEED = 20261130
HOLDOUT_MASTER_SEED = 20261211
STABILITY_SEEDS = (20261212, 20261213)
FAMILY_CORRELATED_NULL_SEED = 20261215
FAMILY_INDEPENDENT_NULL_SEED = 20261216
FAMILY_MIXED_SEED = 20261217
FAMILY_REPEATED_SEGMENT_SEED = 20261219
FAMILY_SHARED_COPY_SEED = 20261220
FAMILY_SCALING_FWER_SEED = 20261221
FAMILY_SMALL_SEED = 20261222
BOOTSTRAP_STREAM_SALT = 0x5A17C3D1

SERIES_LENGTH = 120
SHARED_EVENT_COUNT = 60
OVERLAP_HORIZON = 4
WEAK_AR_PHI = 0.3
STRONG_AR_PHI = 0.8
REGIME_AR_PHI = 0.9
LONG_MEMORY_DECAY = 0.6
LONG_MEMORY_TERMS = 24
PLANTED_MEAN = 0.35
VOLATILITY_LOW = 1.0
VOLATILITY_HIGH = 3.0
COMMON_SHOCK_WEIGHT_SQ = 0.49
AUTOCORRELATION_MATERIAL_FLOOR = 0.05
INNOVATION_SIGMA = 1.0

Z_95 = 1.959963984540054
# Phi^{-1}(0.95). A one-sided familywise bound uses this quantile.
# Z_95 is Phi^{-1}(0.975) and answers a different, two-sided question.
Z_ONE_SIDED_95 = 1.6448536269514722
NOMINAL_COVERAGE = 0.95
ALPHA = 0.05
CLEAR_UNDERCOVERAGE_CEILING = 0.90
CLEAR_OVERCOVERAGE_FLOOR = 0.98
CLEAR_REJECTION_FLOOR = 0.15
CLEAR_UNDERREJECTION_CEILING = 0.01
MIN_DENOMINATOR_TO_FAIL = 40
MIN_DENOMINATOR_TO_VALIDATE = 200
MAX_WILSON_HALF_WIDTH_TO_VALIDATE = 0.04
MAX_UNAVAILABLE_FRACTION_FOR_VALIDATION = 0.01

CALIBRATION_CLOSED_FORM_REPLICATIONS = 80
HOLDOUT_CLOSED_FORM_REPLICATIONS = 400
CALIBRATION_BOOTSTRAP_REPLICATIONS = 20
HOLDOUT_BOOTSTRAP_REPLICATIONS = 60
STABILITY_REPLICATIONS = 40
BOOTSTRAP_DRAWS = 99
STUDENTIZED_DRAWS = 49
STUDENTIZED_REPLICATIONS = 60
PREDECLARED_HAC_LAGS = (1, 4, 8, 16)
PREDECLARED_BLOCK_LENGTHS = (1, 4, 8, 16)
MOVING_BLOCK_GRID_LENGTHS = PREDECLARED_BLOCK_LENGTHS
LONG_BLOCK_LENGTH = 16
SHARED_CLOCK_BLOCK_LENGTH = 8
STUDENTIZED_BLOCK_LENGTH = 16
STUDENTIZED_HAC_LAG = 16

FAMILY_VALIDATION_SIZE = 40
FAMILY_VALIDATION_REPLICATIONS = 400
FAMILY_CALIBRATION_REPLICATIONS = 40
FAMILY_SMALL_SIZE = 10
FAMILY_SCALING_SIZE = 160
FAMILY_SCALING_REPLICATIONS = 80
FAMILY_EQUICORRELATION = 0.3
FAMILY_ALTERNATIVE_COUNT = 4
FAMILY_ALTERNATIVE_MEAN = 0.5
REPEATED_SEGMENTS = 4
REPEATED_FAMILY_SIZE = 20
REPEATED_SEGMENT_REPLICATIONS = 400
FAMILY_SCALING_SIZES = (40, 160, 640, 2560, 10240, 89460)

MAX_DIRECT_SERIES_LENGTH = 2000
MAX_SOURCE_LABEL_LENGTH = 128
REQUIRED_SOURCE_LABEL = "synthetic-dependence-aware-validation-v1"

CLOSED_FORM_STREAM = 1
BOOTSTRAP_SCHEDULE_STREAM = 2
STABILITY_STREAM = 3
FAMILY_STREAM = 4

PRIMARY_STATUSES = (
    "EXPLORATORY_ONLY",
    "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL",
    "FAILED_SYNTHETIC_CALIBRATION",
    "INSUFFICIENT_MONTE_CARLO_PRECISION",
    "MODEL_ASSUMPTIONS_UNVERIFIED",
    "P_VALUES_UNAVAILABLE",
    "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
)
DEPENDENCE_ASSUMPTION_CLASSES = (
    "EXACT_FINITE_DEPENDENCE_HORIZON",
    "PRACTICAL_AUTOCORRELATION_TRUNCATION",
    "ASYMPTOTIC_WEAK_DEPENDENCE",
    "UNVERIFIED_APPROXIMATION",
)
METHOD_ROLES = (
    "KNOWN_MODEL_ORACLE",
    "SAMPLE_ESTIMATED",
    "EXPERIMENTAL_BOOTSTRAP",
)
EMPIRICAL_FWER_CLAIMS = (
    "ONE_SIDED_UPPER_BOUND_AT_OR_BELOW_ALPHA",
    "EXCESSIVE_FAMILYWISE_ERROR",
    "INCONCLUSIVE_SIMULATION",
    "MODEL_ASSUMPTIONS_UNVERIFIED",
)
# A source-only generator checksum. Not a holdout seed and not an acceptance threshold.
BOUNDED_REPRODUCTION_SEED = 20261230
BOUNDED_REPRODUCTION_REPLICATIONS = 4
BOUNDED_REPRODUCTION_FAMILY_SIZE = 3

HOLDOUT_PARTITION = "holdout"
CALIBRATION_PARTITION = "calibration"
STABILITY_PARTITION = "stability"

STUDENTIZED_SCENARIOS = (
    "independent_zero_edge",
    "weak_ar1",
    "strong_ar1",
    "overlapping_windows",
)
MOVING_BLOCK_GRID_SCENARIOS = STUDENTIZED_SCENARIOS
LONG_BLOCK_ONLY_SCENARIOS = (
    "long_memory",
    "regime_change",
    "changing_volatility",
    "shared_identical_observations",
)
CIRCULAR_STATIONARY_SCENARIOS = (
    "independent_zero_edge",
    "weak_ar1",
    "strong_ar1",
    "long_memory",
)
CALIBRATION_BOOTSTRAP_TARGETS = (
    ("independent_zero_edge", "primary", "moving_block_16"),
    ("strong_ar1", "primary", "moving_block_16"),
)
STABILITY_EVALUATIONS = (
    ("independent_zero_edge", "primary", "iid_normal_interval"),
    ("independent_zero_edge", "primary", "newey_west_lag_16"),
    ("strong_ar1", "primary", "iid_normal_interval"),
    ("strong_ar1", "primary", "newey_west_lag_16"),
    ("overlapping_windows", "primary", "iid_normal_interval"),
    ("overlapping_windows", "primary", "newey_west_lag_16"),
)

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

_PRIOR_AR1_CONTEXT = {
    "experiment": STATISTICAL_UNCERTAINTY_CONTEXT_EXPERIMENT,
    "process": "AR(1) phi 0.8, as reported by statistical uncertainty V1",
    "iid_coverage": "73/160",
    "newey_west_lag_8_coverage": "117/160",
    "moving_block_length_8_coverage": "13/20",
    "used_as_tuning_target": False,
    "used_as_acceptance_threshold": False,
    "seeds_reused_as_confirmation": False,
}


def _fail(code: str, detail: str) -> None:
    raise ValueError(f"{code}: {detail}")


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _authorizations() -> dict[str, bool]:
    payload = {key: value for key, value in _AUTHORIZATION_FLAGS}
    if any(payload.values()):
        _fail("DEPENDENCE_VALIDATION_AUTHORIZATION_DRIFT", "an authorization flag is open")
    return payload


def _recorded_thresholds() -> dict[str, object]:
    return {
        "decision": ANNUAL_CATALOGUE_PROTOCOL_DECISION,
        "modified": False,
        "min_annual_evaluable_support": MIN_ANNUAL_EVALUABLE_SUPPORT,
        "min_cross_year_evaluable_segments": MIN_CROSS_YEAR_EVALUABLE_SEGMENTS,
        "min_base_positive_fraction": MIN_BASE_POSITIVE_FRACTION,
        "min_stress_positive_fraction": MIN_STRESS_POSITIVE_FRACTION,
        "min_median_annual_mean_net_pips_0p5": MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5,
        "min_pooled_mean_net_pips_0p5": MIN_POOLED_MEAN_NET_PIPS_0P5,
        "require_pooled_stress_mean_positive": REQUIRE_POOLED_STRESS_MEAN_POSITIVE,
        "max_sign_flips": MAX_SIGN_FLIPS,
        "near_duplicate_jaccard": NEAR_DUPLICATE_JACCARD,
        "directional_hypotheses_per_annual_segment": (
            DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT
        ),
    }


def _validate_sha256(value: object) -> str:
    if not isinstance(value, str) or len(value) != 64:
        _fail(
            "DEPENDENCE_VALIDATION_MALFORMED_PROVENANCE",
            "synthetic_manifest_sha256 must be a 64-character sha256",
        )
    try:
        int(value, 16)
    except ValueError:
        _fail(
            "DEPENDENCE_VALIDATION_MALFORMED_PROVENANCE",
            "synthetic_manifest_sha256 must be hexadecimal",
        )
    return value.lower()


def _validate_commit(value: object) -> str:
    if not isinstance(value, str) or len(value) != 40:
        _fail(
            "DEPENDENCE_VALIDATION_MALFORMED_PROVENANCE",
            "code_commit must be a 40-character Git commit",
        )
    try:
        int(value, 16)
    except ValueError:
        _fail(
            "DEPENDENCE_VALIDATION_MALFORMED_PROVENANCE",
            "code_commit must be hexadecimal",
        )
    return value.lower()


@dataclass(frozen=True, slots=True)
class DependenceValidationProvenance:
    source_label: str
    code_commit: str
    synthetic_manifest_sha256: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_label, str)
            or self.source_label != REQUIRED_SOURCE_LABEL
            or len(self.source_label) > MAX_SOURCE_LABEL_LENGTH
        ):
            _fail(
                "DEPENDENCE_VALIDATION_MALFORMED_PROVENANCE",
                "source_label must be the synthetic dependence-validation label",
            )
        object.__setattr__(self, "code_commit", _validate_commit(self.code_commit))
        object.__setattr__(
            self,
            "synthetic_manifest_sha256",
            _validate_sha256(self.synthetic_manifest_sha256),
        )


def _provenance_payload(provenance: DependenceValidationProvenance) -> dict[str, object]:
    return {
        "source_label": provenance.source_label,
        "code_commit": provenance.code_commit,
        "synthetic_manifest_sha256": provenance.synthetic_manifest_sha256,
        "historical_artifact_read": False,
        "caller_supplied": True,
        "synthetic_only": True,
    }


def _require_master_seed(seed: int) -> None:
    if isinstance(seed, bool) or not isinstance(seed, int):
        _fail("DEPENDENCE_VALIDATION_MALFORMED_SEED", "master seed must be an integer")
    if seed in FORBIDDEN_MASTER_SEEDS:
        _fail(
            "DEPENDENCE_VALIDATION_FORBIDDEN_MASTER_SEED",
            "EXP-20261118-069 and statistical-uncertainty V1 masters are not reused",
        )


def _stream_rng(master: int, stream_code: int) -> random.Random:
    _require_master_seed(master)
    if isinstance(stream_code, bool) or not isinstance(stream_code, int):
        _fail("DEPENDENCE_VALIDATION_MALFORMED_SEED", "stream code must be an integer")
    if stream_code < 1 or stream_code > 40:
        _fail("DEPENDENCE_VALIDATION_MALFORMED_SEED", "stream code is outside 1..40")
    rng = random.Random(master)
    for _index in range(stream_code):
        rng.random()
    return rng


def _replication_seeds(master: int, stream_code: int, count: int) -> list[int]:
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        _fail("DEPENDENCE_VALIDATION_MALFORMED_SEED", "replication count must be positive")
    rng = _stream_rng(master, stream_code)
    seeds: list[int] = []
    while len(seeds) < count:
        candidate = rng.randrange(1, 2**31)
        if candidate in FORBIDDEN_MASTER_SEEDS:
            continue
        seeds.append(candidate)
    return seeds


def _standard_normal(rng: random.Random) -> float:
    while True:
        u1 = rng.random()
        if u1 > 0.0:
            break
    u2 = rng.random()
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def _median(values: Sequence[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    count = len(ordered)
    mid = count // 2
    if count % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def _sample_sd(sum_values: float, sum_squares: float, count: int) -> float | None:
    if count < 2:
        return None
    mean = sum_values / count
    variance = (sum_squares - count * mean * mean) / (count - 1)
    if variance < 0.0 and variance > -1e-12:
        variance = 0.0
    if variance < 0.0:
        _fail("DEPENDENCE_VALIDATION_NUMERICAL", "sample variance of means is negative")
    return math.sqrt(variance)


def _require_series(values: Sequence[float]) -> list[float]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        _fail("DEPENDENCE_VALIDATION_MALFORMED_SERIES", "series must be a sequence of numbers")
    if len(values) < 2 or len(values) > MAX_DIRECT_SERIES_LENGTH:
        _fail(
            "DEPENDENCE_VALIDATION_MALFORMED_SERIES",
            "series length must be from 2 through 2000",
        )
    parsed: list[float] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            _fail("DEPENDENCE_VALIDATION_MALFORMED_SERIES", "series values must be finite numbers")
        number = float(value)
        if not math.isfinite(number):
            _fail("DEPENDENCE_VALIDATION_MALFORMED_SERIES", "series values must be finite numbers")
        parsed.append(number)
    return parsed


def _last_material_ar_lag(phi: float, floor: float = AUTOCORRELATION_MATERIAL_FLOOR) -> int:
    """Largest lag whose absolute AR(1) autocorrelation is still at least `floor`.

    This is a practical truncation. Autocorrelation after the returned lag is
    smaller than the floor and is not zero.
    """

    if phi == 0.0:
        return 0
    value = 1.0
    last = 0
    for lag in range(1, SERIES_LENGTH):
        value *= abs(phi)
        if value < floor:
            break
        last = lag
    return last


def _weighted_autocorrelation_sum(n: int, phi: float) -> float:
    if phi == 0.0:
        return 0.0
    weighted = 0.0
    phi_power = 1.0
    for lag in range(1, n):
        phi_power *= phi
        weighted += (1.0 - lag / n) * phi_power
    return weighted


def ar1_variance_of_mean(n: int, phi: float, sigma_e: float) -> float:
    """Exact variance of the sample mean of a stationary Gaussian AR(1)."""

    if n < 2 or abs(phi) >= 1.0 or sigma_e <= 0.0:
        _fail("DEPENDENCE_VALIDATION_MALFORMED_PROCESS", "AR(1) variance is not identified")
    gamma0 = (sigma_e * sigma_e) / (1.0 - phi * phi)
    factor = 1.0 + 2.0 * _weighted_autocorrelation_sum(n, phi)
    return gamma0 * factor / n


def ar1_effective_sample_size(n: int, phi: float) -> float:
    """Finite-sample size matching the AR(1) variance of the mean.

    This is `n / [1 + 2 * sum((1 - k/n) * phi**k)]`. It is not the large-sample
    approximation `n * (1 - phi) / (1 + phi)`, and it is not an event-evidence
    sample size.
    """

    if n < 2 or abs(phi) >= 1.0:
        _fail("DEPENDENCE_VALIDATION_MALFORMED_PROCESS", "AR(1) size is not identified")
    factor = 1.0 + 2.0 * _weighted_autocorrelation_sum(n, phi)
    return n / factor


def overlapping_mean_variance(n: int, horizon: int, sigma: float = 1.0) -> float:
    """Exact variance of the mean of horizon-length overlapping shock averages."""

    if n < 2 or horizon < 2 or sigma <= 0.0:
        _fail("DEPENDENCE_VALIDATION_MALFORMED_PROCESS", "overlap variance is not identified")
    counts = [0] * (n + horizon - 1)
    for start in range(n):
        for offset in range(horizon):
            counts[start + offset] += 1
    variance_of_sum = (sigma * sigma) * sum(count * count for count in counts) / (
        horizon * horizon
    )
    return variance_of_sum / (n * n)


def overlapping_marginal_variance(horizon: int, sigma: float = 1.0) -> float:
    return (sigma * sigma) / horizon


def _ma_gammas(theta: Sequence[float]) -> list[float]:
    order = len(theta) - 1
    gammas: list[float] = []
    for lag in range(order + 1):
        total = 0.0
        for index in range(order - lag + 1):
            total += theta[index] * theta[index + lag]
        gammas.append(total)
    return gammas


def variance_of_mean_from_gammas(n: int, gammas: Sequence[float]) -> float:
    total = n * gammas[0]
    for lag in range(1, n):
        gamma = gammas[lag] if lag < len(gammas) else 0.0
        total += 2.0 * (n - lag) * gamma
    return total / (n * n)


def _long_memory_theta() -> tuple[float, ...]:
    raw = [(index + 1) ** (-LONG_MEMORY_DECAY) for index in range(LONG_MEMORY_TERMS)]
    scale = math.sqrt(sum(weight * weight for weight in raw))
    return tuple(weight / scale for weight in raw)


_LONG_MEMORY_THETA = _long_memory_theta()
_LONG_MEMORY_GAMMAS = tuple(_ma_gammas(_LONG_MEMORY_THETA))


def long_memory_variance_of_mean(n: int) -> float:
    return variance_of_mean_from_gammas(n, _LONG_MEMORY_GAMMAS)


def hetero_variance_of_mean(n: int, low: float, high: float) -> float:
    if n < 2 or n % 2 or low <= 0.0 or high <= 0.0:
        _fail("DEPENDENCE_VALIDATION_MALFORMED_PROCESS", "volatility variance is not identified")
    half = n // 2
    sum_variance = half * low * low + half * high * high
    return sum_variance / (n * n)


def regime_variance_of_mean(n: int, phi: float, sigma_e: float) -> float:
    """Variance of the mean of an iid block followed by an independent AR(1) block."""

    if n < 4 or n % 2:
        _fail("DEPENDENCE_VALIDATION_MALFORMED_PROCESS", "regime variance requires an even n")
    half = n // 2
    variance_sum_first = half * sigma_e * sigma_e
    variance_mean_second = ar1_variance_of_mean(half, phi, sigma_e)
    variance_sum_second = variance_mean_second * half * half
    return (variance_sum_first + variance_sum_second) / (n * n)


def horizon_contrast_variance(n: int, horizon: int, sigma: float = 1.0) -> float:
    """Variance of the mean of overlapping-average minus the window's last shock."""

    shock_count = n + horizon - 1
    coefficients = [0.0] * shock_count
    for start in range(n):
        for offset in range(horizon - 1):
            coefficients[start + offset] += 1.0 / horizon
        coefficients[start + horizon - 1] += 1.0 / horizon - 1.0
    return (sigma * sigma) * sum(value * value for value in coefficients) / (n * n)


def _require_binomial_count(numerator: int, denominator: int) -> None:
    if isinstance(numerator, bool) or not isinstance(numerator, int):
        _fail("DEPENDENCE_VALIDATION_MALFORMED_COUNTS", "numerator must be an integer")
    if isinstance(denominator, bool) or not isinstance(denominator, int):
        _fail("DEPENDENCE_VALIDATION_MALFORMED_COUNTS", "denominator must be an integer")
    if numerator < 0 or denominator < 0 or numerator > denominator:
        _fail(
            "DEPENDENCE_VALIDATION_MALFORMED_COUNTS",
            "numerator and denominator are not a binomial count",
        )


def _wilson_centre_half(rate: float, denominator: int, z_value: float) -> tuple[float, float]:
    z_squared = z_value * z_value
    wilson_denominator = 1.0 + z_squared / denominator
    centre = (rate + z_squared / (2.0 * denominator)) / wilson_denominator
    half = (
        z_value
        * math.sqrt(
            rate * (1.0 - rate) / denominator
            + z_squared / (4.0 * denominator * denominator)
        )
        / wilson_denominator
    )
    return centre, half


def one_sided_wilson_95(numerator: int, denominator: int) -> dict[str, object]:
    """One-sided 95 percent Wilson bounds. The quantile is Phi^{-1}(0.95)."""

    _require_binomial_count(numerator, denominator)
    if denominator == 0:
        return {
            "low": None,
            "high": None,
            "z": Z_ONE_SIDED_95,
            "confidence_level": 0.95,
            "sided": "one",
            "method": "wilson_score_one_sided",
        }
    rate = numerator / denominator
    centre, half = _wilson_centre_half(rate, denominator, Z_ONE_SIDED_95)
    return {
        "low": max(0.0, centre - half),
        "high": min(1.0, centre + half),
        "z": Z_ONE_SIDED_95,
        "confidence_level": 0.95,
        "sided": "one",
        "method": "wilson_score_one_sided",
    }


def binomial_monte_carlo_report(numerator: int, denominator: int) -> dict[str, object]:
    """Wilson score interval for a Monte Carlo rate. The rate is not a population constant."""

    _require_binomial_count(numerator, denominator)
    if denominator == 0:
        return {
            "numerator": 0,
            "denominator": 0,
            "rate": None,
            "binomial_standard_error": None,
            "wilson_interval_95": None,
            "wilson_half_width": None,
            "interval_status": "UNAVAILABLE",
            "empirical_rate_is_exact_population_error_rate": False,
            "z_95": Z_95,
        }
    rate = numerator / denominator
    standard_error = math.sqrt(rate * (1.0 - rate) / denominator)
    centre, half = _wilson_centre_half(rate, denominator, Z_95)
    low = max(0.0, centre - half)
    high = min(1.0, centre + half)
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": rate,
        "binomial_standard_error": standard_error,
        "binomial_standard_error_understates_boundary_uncertainty": standard_error == 0.0,
        "wilson_interval_95": {
            "low": low,
            "high": high,
            "method": "wilson_score",
            "z": Z_95,
            "confidence_level": 0.95,
        },
        "wilson_half_width": (high - low) / 2.0,
        "interval_status": "REPORTED",
        "empirical_rate_is_exact_population_error_rate": False,
        "z_95": Z_95,
    }


def _wilson_bounds(report: Mapping[str, object]) -> tuple[float, float, float]:
    interval = report["wilson_interval_95"]
    if not isinstance(interval, Mapping):
        _fail("DEPENDENCE_VALIDATION_MALFORMED_COUNTS", "Wilson interval is missing")
    low = float(interval["low"])
    high = float(interval["high"])
    half = float(report["wilson_half_width"])
    return low, high, half


def _precise(denominator: int, half_width: float) -> bool:
    return (
        denominator >= MIN_DENOMINATOR_TO_VALIDATE
        and half_width <= MAX_WILSON_HALF_WIDTH_TO_VALIDATE
    )


def _excess_unavailable(unavailable_count: int, replications: int) -> bool:
    if replications <= 0:
        return True
    return unavailable_count / replications > MAX_UNAVAILABLE_FRACTION_FOR_VALIDATION


def interval_primary_status(
    *,
    assumptions_match: bool,
    covered: int,
    available: int,
    unavailable_count: int,
    replications: int,
) -> str:
    """Predeclared interval status. It does not read observed calibration targets.

    Success requires the Wilson interval to contain 95 percent, a predeclared
    Monte Carlo precision, and a matching assumption. A Wilson upper bound
    below 90 percent, or a lower bound above 98 percent, is a clear failure.
    A narrower miss is insufficient precision, not a license to retune.
    """

    if available == 0:
        return "MODEL_ASSUMPTIONS_UNVERIFIED"
    report = binomial_monte_carlo_report(covered, available)
    low, high, half = _wilson_bounds(report)
    nominal_inside = low <= NOMINAL_COVERAGE <= high
    clear_failure = available >= MIN_DENOMINATOR_TO_FAIL and (
        high < CLEAR_UNDERCOVERAGE_CEILING or low > CLEAR_OVERCOVERAGE_FLOOR
    )
    precise = _precise(available, half)
    if assumptions_match and nominal_inside and precise:
        if _excess_unavailable(unavailable_count, replications):
            return "FAILED_SYNTHETIC_CALIBRATION"
        return "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL"
    if clear_failure:
        return "FAILED_SYNTHETIC_CALIBRATION"
    if assumptions_match:
        return "INSUFFICIENT_MONTE_CARLO_PRECISION"
    return "MODEL_ASSUMPTIONS_UNVERIFIED"


def null_test_primary_status(
    *,
    assumptions_match: bool,
    rejections: int,
    available: int,
    unavailable_count: int,
    replications: int,
    p_values_computed: bool = False,
) -> str:
    """Size calibration for a justified null test. Nominal rejection is 5 percent."""

    if not assumptions_match:
        if available == 0:
            return "P_VALUES_UNAVAILABLE"
        report = binomial_monte_carlo_report(rejections, available)
        low, _high, half = _wilson_bounds(report)
        if available >= MIN_DENOMINATOR_TO_FAIL and low > CLEAR_REJECTION_FLOOR:
            return "FAILED_SYNTHETIC_CALIBRATION"
        if p_values_computed:
            if _precise(available, half):
                return "MODEL_ASSUMPTIONS_UNVERIFIED"
            return "INSUFFICIENT_MONTE_CARLO_PRECISION"
        return "P_VALUES_UNAVAILABLE"
    if available == 0:
        return "P_VALUES_UNAVAILABLE"
    report = binomial_monte_carlo_report(rejections, available)
    low, high, half = _wilson_bounds(report)
    nominal_inside = low <= ALPHA <= high
    precise = _precise(available, half)
    clear_failure = available >= MIN_DENOMINATOR_TO_FAIL and (
        low > CLEAR_REJECTION_FLOOR or (precise and high < CLEAR_UNDERREJECTION_CEILING)
    )
    if nominal_inside and precise:
        if _excess_unavailable(unavailable_count, replications):
            return "FAILED_SYNTHETIC_CALIBRATION"
        return "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL"
    if clear_failure:
        return "FAILED_SYNTHETIC_CALIBRATION"
    return "INSUFFICIENT_MONTE_CARLO_PRECISION"


def empirical_fwer_assessment(
    *,
    assumptions_match: bool,
    familywise_rejections: int,
    replications: int,
) -> dict[str, object]:
    """Monte Carlo claim about familywise error. Holm's theorem is separate.

    Empirical control requires the one-sided 95 percent Wilson upper bound to
    lie at or below alpha, the predeclared precision floor, and valid marginal
    p-values. The quantile is Phi^{-1}(0.95). A point estimate at or below
    alpha is not control when that upper bound exceeds alpha.

    Excessive error keeps the predeclared two-sided rule: the Wilson lower
    bound is above alpha and the denominator is at least 40. That failure
    rule was not loosened and was not fit to the inspected 17/400 or 19/400
    counts. Every other matched result is inconclusive.

    A count that satisfies the upper bound is a property of this function.
    It is not a fresh confirmation of the already inspected holdout.
    """

    if replications <= 0:
        return {
            "empirical_fwer_claim": "INCONCLUSIVE_SIMULATION",
            "primary_status": "INSUFFICIENT_MONTE_CARLO_PRECISION",
            "one_sided_wilson_95": one_sided_wilson_95(0, 0),
            "rate": None,
            "point_estimate_at_or_below_alpha": None,
            "one_sided_upper_bound_at_or_below_alpha": False,
            "two_sided_wilson_lower_bound": None,
            "precision_floor_met": False,
            "inspected_holdout_used": False,
        }
    report = binomial_monte_carlo_report(familywise_rejections, replications)
    low, _high, half = _wilson_bounds(report)
    one_sided = one_sided_wilson_95(familywise_rejections, replications)
    upper = one_sided["high"]
    if not isinstance(upper, float):
        _fail("DEPENDENCE_VALIDATION_NUMERICAL", "one-sided Wilson bound is missing")
    rate = float(report["rate"])
    excessive = replications >= MIN_DENOMINATOR_TO_FAIL and low > ALPHA
    upper_ok = upper <= ALPHA
    precise = _precise(replications, half)
    if excessive:
        claim = "EXCESSIVE_FAMILYWISE_ERROR"
        primary = "FAILED_SYNTHETIC_CALIBRATION"
    elif not assumptions_match:
        claim = "MODEL_ASSUMPTIONS_UNVERIFIED"
        primary = "MODEL_ASSUMPTIONS_UNVERIFIED"
    elif precise and upper_ok:
        claim = "ONE_SIDED_UPPER_BOUND_AT_OR_BELOW_ALPHA"
        primary = "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL"
    else:
        claim = "INCONCLUSIVE_SIMULATION"
        primary = "INSUFFICIENT_MONTE_CARLO_PRECISION"
    return {
        "empirical_fwer_claim": claim,
        "primary_status": primary,
        "one_sided_wilson_95": one_sided,
        "rate": rate,
        "point_estimate_at_or_below_alpha": rate <= ALPHA,
        "one_sided_upper_bound_at_or_below_alpha": upper_ok,
        "two_sided_wilson_lower_bound": low,
        "precision_floor_met": precise,
        "inspected_holdout_used": False,
    }


def fwer_control_status(
    *,
    assumptions_match: bool,
    familywise_rejections: int,
    replications: int,
) -> str:
    """Map the empirical familywise claim onto the frozen status vocabulary."""

    return str(
        empirical_fwer_assessment(
            assumptions_match=assumptions_match,
            familywise_rejections=familywise_rejections,
            replications=replications,
        )["primary_status"]
    )


def _theoretical_holm_guarantee(*, applies: bool) -> dict[str, object]:
    """Holm's finite-sample guarantee. It is not a Monte Carlo result."""

    return {
        "statement": "FWER_AT_MOST_ALPHA_IF_MARGINAL_P_VALUES_ARE_VALID",
        "procedure": "holm_step_down",
        "alpha": ALPHA,
        "requires_valid_marginal_p_values": True,
        "dependence_restriction_beyond_valid_marginal_p_values": False,
        "guarantee_applies": applies,
        "established_by_simulation": False,
    }


def _normal_two_sided_p(z_value: float) -> float:
    if not math.isfinite(z_value):
        _fail("DEPENDENCE_VALIDATION_NUMERICAL", "z statistic is not finite")
    return math.erfc(abs(z_value) / math.sqrt(2.0))


def holm_adjusted_p_values(p_values: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values. The input p-values must already be valid."""

    if isinstance(p_values, (str, bytes)) or not isinstance(p_values, Sequence) or not p_values:
        _fail("DEPENDENCE_VALIDATION_MALFORMED_FAMILY", "p-values must be a non-empty sequence")
    parsed: list[float] = []
    for value in p_values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            _fail("DEPENDENCE_VALIDATION_MALFORMED_FAMILY", "p-values must be probabilities")
        number = float(value)
        if not math.isfinite(number) or number < 0.0 or number > 1.0:
            _fail("DEPENDENCE_VALIDATION_MALFORMED_FAMILY", "p-values must lie in [0, 1]")
        parsed.append(number)
    family_size = len(parsed)
    if family_size > DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT:
        _fail(
            "DEPENDENCE_VALIDATION_FAMILY_ABOVE_FROZEN_UNIVERSE",
            "the synthetic family is larger than one annual segment",
        )
    order = sorted(range(family_size), key=lambda index: (parsed[index], index))
    adjusted = [0.0] * family_size
    running = 0.0
    for rank, index in enumerate(order):
        raw = (family_size - rank) * parsed[index]
        if raw > 1.0:
            raw = 1.0
        if raw > running:
            running = raw
        adjusted[index] = running
    return adjusted


def refuse_percentile_interval_as_p_value(interval: Mapping[str, object]) -> None:
    """A percentile bootstrap interval is not a null p-value."""

    if interval.get("p_value") not in (None, "NOT_COMPUTED", "P_VALUES_UNAVAILABLE"):
        _fail(
            "DEPENDENCE_VALIDATION_PERCENTILE_INTERVAL_IS_NOT_A_P_VALUE",
            "percentile intervals are not converted into p-values",
        )
    _fail(
        "DEPENDENCE_VALIDATION_PERCENTILE_INTERVAL_IS_NOT_A_P_VALUE",
        "percentile intervals are not converted into p-values",
    )


def refuse_episode_groups_as_independent_trials() -> None:
    _fail(
        "DEPENDENCE_VALIDATION_EPISODE_GROUPS_ARE_NOT_TRIALS",
        "episode groups are not an independently justified trial model",
    )


def refuse_incorrect_sample_size(*, unique_events: int, claimed_independent_rows: int) -> None:
    if unique_events < 1 or claimed_independent_rows < unique_events:
        _fail(
            "DEPENDENCE_VALIDATION_MALFORMED_COUNTS",
            "claimed rows cannot be smaller than the event count",
        )
    if claimed_independent_rows != unique_events:
        _fail(
            "DEPENDENCE_VALIDATION_INCORRECT_SAMPLE_SIZE",
            "duplicated observations are not additional independent trials",
        )


def refuse_method_revision(_reason: str) -> None:
    """Revising a method after inspection requires a fresh holdout. This build does not revise."""

    _fail(
        "DEPENDENCE_VALIDATION_METHOD_REVISION_REQUIRES_FRESH_HOLDOUT",
        "lags, block lengths, and thresholds are frozen; a revision needs a new holdout",
    )


def _autocovariances(values: Sequence[float], max_lag: int) -> list[float] | None:
    parsed = _require_series(values)
    n = len(parsed)
    if n < 2 or max_lag < 1 or max_lag >= n:
        return None
    center = _mean(parsed)
    centered = [value - center for value in parsed]
    if all(value == 0.0 for value in centered):
        return None
    gammas: list[float] = []
    for step in range(max_lag + 1):
        gamma = sum(
            centered[index] * centered[index + step] for index in range(n - step)
        ) / n
        gammas.append(gamma)
    return gammas


def _long_run_variance(gammas: Sequence[float], lag: int) -> float:
    long_run = gammas[0]
    for step in range(1, lag + 1):
        weight = 1.0 - (step / (lag + 1.0))
        long_run += 2.0 * weight * gammas[step]
    return long_run


def _unavailable_interval(reason: str, mean: float | None, n: int) -> dict[str, object]:
    return {
        "status": "UNAVAILABLE",
        "reason": reason,
        "mean": mean,
        "n": n,
        "standard_error": None,
        "low": None,
        "high": None,
        "p_value": "P_VALUES_UNAVAILABLE",
        "inference_authorized": False,
    }


def iid_normal_interval(values: Sequence[float]) -> dict[str, object]:
    parsed = _require_series(values)
    n = len(parsed)
    center = _mean(parsed)
    sum_squares = sum((value - center) ** 2 for value in parsed)
    if sum_squares <= 0.0:
        return _unavailable_interval("SAMPLE_VARIANCE_IS_ZERO", center, n)
    standard_error = math.sqrt((sum_squares / (n - 1)) / n)
    half = Z_95 * standard_error
    return {
        "status": "COMPUTED",
        "reason": "IID_NORMAL_INTERVAL",
        "mean": center,
        "n": n,
        "standard_error": standard_error,
        "low": center - half,
        "high": center + half,
        "p_value": "P_VALUES_UNAVAILABLE",
        "inference_authorized": False,
        "sample_size_used": n,
    }


def newey_west_interval(values: Sequence[float], lag: int) -> dict[str, object]:
    if isinstance(lag, bool) or not isinstance(lag, int) or lag not in PREDECLARED_HAC_LAGS:
        _fail(
            "DEPENDENCE_VALIDATION_LAG_NOT_PREDECLARED",
            "HAC lag must be one of 1, 4, 8, or 16",
        )
    parsed = _require_series(values)
    n = len(parsed)
    center = _mean(parsed)
    gammas = _autocovariances(parsed, lag)
    if gammas is None:
        reason = "LAG_NOT_IDENTIFIED" if lag >= n else "SAMPLE_VARIANCE_IS_ZERO"
        return _unavailable_interval(reason, center, n)
    long_run = _long_run_variance(gammas, lag)
    if long_run <= 0.0:
        return _unavailable_interval("NONPOSITIVE_LONG_RUN_VARIANCE", center, n)
    standard_error = math.sqrt(long_run / n)
    half = Z_95 * standard_error
    return {
        "status": "COMPUTED",
        "reason": "NEWEY_WEST_BARTLETT",
        "mean": center,
        "n": n,
        "lag": lag,
        "lag_selected_from_data": False,
        "long_run_variance": long_run,
        "standard_error": standard_error,
        "low": center - half,
        "high": center + half,
        "kernel": "Bartlett",
        "gamma_divisor": "n",
        "p_value": "P_VALUES_UNAVAILABLE",
        "inference_authorized": False,
        "sample_size_used": n,
    }


def declared_model_z_interval(
    values: Sequence[float],
    variance_of_mean: float,
) -> dict[str, object]:
    """Interval and null p-value using a caller-declared exact variance of the mean.

    The variance is part of the synthetic model. It is not estimated from the
    series and it is not available for event evidence.
    """

    parsed = _require_series(values)
    n = len(parsed)
    center = _mean(parsed)
    if (
        isinstance(variance_of_mean, bool)
        or not isinstance(variance_of_mean, (int, float))
        or not math.isfinite(float(variance_of_mean))
        or float(variance_of_mean) <= 0.0
    ):
        return _unavailable_interval("DECLARED_VARIANCE_UNAVAILABLE", center, n)
    standard_error = math.sqrt(float(variance_of_mean))
    half = Z_95 * standard_error
    z_value = center / standard_error
    return {
        "status": "COMPUTED",
        "reason": "DECLARED_GAUSSIAN_MODEL",
        "mean": center,
        "n": n,
        "standard_error": standard_error,
        "low": center - half,
        "high": center + half,
        "z_statistic_for_zero_null": z_value,
        "p_value": _normal_two_sided_p(z_value),
        "p_value_construction": "exact_gaussian_tail_under_declared_variance",
        "variance_estimated_from_sample": False,
        "inference_authorized": False,
        "sample_size_used": None,
        "catalogue_inference": "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
    }


def _percentile_bounds(samples: Sequence[float]) -> tuple[float, float]:
    ordered = sorted(samples)
    draws = len(ordered)
    low_index = math.floor(0.025 * (draws - 1))
    high_index = math.ceil(0.975 * (draws - 1))
    if high_index >= draws:
        high_index = draws - 1
    if low_index < 0:
        low_index = 0
    return ordered[low_index], ordered[high_index]


def _moving_block_indexes(n: int, block_length: int, rng: random.Random) -> list[int]:
    if block_length > n or block_length < 1:
        _fail("DEPENDENCE_VALIDATION_BLOCK_NOT_PREDECLARED", "block length does not fit the series")
    starts = n - block_length + 1
    block_count = math.ceil(n / block_length)
    indexes: list[int] = []
    for _block in range(block_count):
        start = rng.randrange(starts)
        for offset in range(block_length):
            if len(indexes) == n:
                break
            indexes.append(start + offset)
    return indexes


def _resample_mean(values: Sequence[float], indexes: Sequence[int]) -> float:
    return sum(values[index] for index in indexes) / len(indexes)


def _bootstrap_interval_from_means(
    sample_mean: float,
    n: int,
    bootstrap_means: Sequence[float],
    *,
    reason: str,
    block_length: int | None,
) -> dict[str, object]:
    low, high = _percentile_bounds(bootstrap_means)
    return {
        "status": "COMPUTED",
        "reason": reason,
        "mean": sample_mean,
        "n": n,
        "block_length": block_length,
        "block_length_selected_from_data": False,
        "standard_error": None,
        "low": low,
        "high": high,
        "draws": len(bootstrap_means),
        "p_value": "P_VALUES_UNAVAILABLE",
        "valid_p_value_claimed": False,
        "inference_authorized": False,
        "sample_size_used": n,
    }


def moving_block_bootstrap_interval(
    values: Sequence[float],
    block_length: int,
    *,
    draws: int,
    rng: random.Random,
) -> dict[str, object]:
    if block_length not in PREDECLARED_BLOCK_LENGTHS:
        _fail(
            "DEPENDENCE_VALIDATION_BLOCK_NOT_PREDECLARED",
            "block length must be one of 1, 4, 8, or 16",
        )
    parsed = _require_series(values)
    n = len(parsed)
    center = _mean(parsed)
    if all(value == parsed[0] for value in parsed):
        return _unavailable_interval("SAMPLE_VARIANCE_IS_ZERO", center, n)
    means: list[float] = []
    for _draw in range(draws):
        indexes = _moving_block_indexes(n, block_length, rng)
        means.append(_resample_mean(parsed, indexes))
    return _bootstrap_interval_from_means(
        center,
        n,
        means,
        reason="MOVING_BLOCK_PERCENTILE",
        block_length=block_length,
    )


def circular_block_bootstrap_interval(
    values: Sequence[float],
    block_length: int,
    *,
    draws: int,
    rng: random.Random,
) -> dict[str, object]:
    """Circular block bootstrap. Wrapping is justified only for a stationary series."""

    if block_length not in PREDECLARED_BLOCK_LENGTHS:
        _fail("DEPENDENCE_VALIDATION_BLOCK_NOT_PREDECLARED", "block length is not predeclared")
    parsed = _require_series(values)
    n = len(parsed)
    center = _mean(parsed)
    if all(value == parsed[0] for value in parsed):
        return _unavailable_interval("SAMPLE_VARIANCE_IS_ZERO", center, n)
    block_count = math.ceil(n / block_length)
    means: list[float] = []
    for _draw in range(draws):
        total = 0.0
        produced = 0
        for _block in range(block_count):
            start = rng.randrange(n)
            for offset in range(block_length):
                if produced == n:
                    break
                total += parsed[(start + offset) % n]
                produced += 1
        means.append(total / n)
    return _bootstrap_interval_from_means(
        center,
        n,
        means,
        reason="CIRCULAR_BLOCK_PERCENTILE",
        block_length=block_length,
    )


def stationary_bootstrap_interval(
    values: Sequence[float],
    mean_block_length: int,
    *,
    draws: int,
    rng: random.Random,
) -> dict[str, object]:
    """Politis-Romano stationary bootstrap. The mean block length is 1/p. The path wraps."""

    if mean_block_length not in PREDECLARED_BLOCK_LENGTHS:
        _fail("DEPENDENCE_VALIDATION_BLOCK_NOT_PREDECLARED", "mean block length is not predeclared")
    parsed = _require_series(values)
    n = len(parsed)
    center = _mean(parsed)
    if all(value == parsed[0] for value in parsed):
        return _unavailable_interval("SAMPLE_VARIANCE_IS_ZERO", center, n)
    probability = 1.0 / mean_block_length
    means: list[float] = []
    for _draw in range(draws):
        index = rng.randrange(n)
        total = 0.0
        for _step in range(n):
            total += parsed[index]
            if rng.random() < probability:
                index = rng.randrange(n)
            else:
                index = (index + 1) % n
        means.append(total / n)
    return _bootstrap_interval_from_means(
        center,
        n,
        means,
        reason="STATIONARY_BOOTSTRAP_PERCENTILE",
        block_length=mean_block_length,
    )


def shared_clock_contrast_interval(
    left: Sequence[float],
    right: Sequence[float],
    block_length: int,
    *,
    draws: int,
    rng: random.Random,
) -> dict[str, object]:
    """One block index is applied to both series. Chronology inside a block is kept."""

    parsed_left = _require_series(left)
    parsed_right = _require_series(right)
    if len(parsed_left) != len(parsed_right):
        _fail("DEPENDENCE_VALIDATION_MALFORMED_SERIES", "shared-clock series must have equal length")
    n = len(parsed_left)
    contrast = [first - second for first, second in zip(parsed_left, parsed_right)]
    center = _mean(contrast)
    if all(value == contrast[0] for value in contrast):
        # Every shared-clock draw of a constant contrast is that same constant.
        # A normal standard error is still unavailable.
        interval = _unavailable_interval("SAMPLE_VARIANCE_IS_ZERO", center, n)
        interval["low"] = center
        interval["high"] = center
        interval["columns_share_indexes"] = True
        interval["authentic_timestamps_aligned"] = False
        interval["resampled_contrast_is_identically_constant"] = True
        return interval
    means: list[float] = []
    for _draw in range(draws):
        indexes = _moving_block_indexes(n, block_length, rng)
        total = 0.0
        for index in indexes:
            total += parsed_left[index] - parsed_right[index]
        means.append(total / n)
    interval = _bootstrap_interval_from_means(
        center,
        n,
        means,
        reason="SHARED_CLOCK_CONTRAST",
        block_length=block_length,
    )
    interval["columns_share_indexes"] = True
    interval["authentic_timestamps_aligned"] = False
    return interval


def independent_column_contrast_interval(
    left: Sequence[float],
    right: Sequence[float],
    block_length: int,
    *,
    draws: int,
    rng: random.Random,
) -> dict[str, object]:
    """Invalid diagnostic: each series draws its own block indexes."""

    parsed_left = _require_series(left)
    parsed_right = _require_series(right)
    if len(parsed_left) != len(parsed_right):
        _fail("DEPENDENCE_VALIDATION_MALFORMED_SERIES", "contrast series must have equal length")
    n = len(parsed_left)
    contrast = [first - second for first, second in zip(parsed_left, parsed_right)]
    center = _mean(contrast)
    means: list[float] = []
    for _draw in range(draws):
        left_indexes = _moving_block_indexes(n, block_length, rng)
        right_indexes = _moving_block_indexes(n, block_length, rng)
        total = 0.0
        for left_index, right_index in zip(left_indexes, right_indexes):
            total += parsed_left[left_index] - parsed_right[right_index]
        means.append(total / n)
    interval = _bootstrap_interval_from_means(
        center,
        n,
        means,
        reason="INDEPENDENT_COLUMN_CONTRAST",
        block_length=block_length,
    )
    interval["columns_share_indexes"] = False
    interval["dependence_preserved"] = False
    return interval


def cluster_event_bootstrap_interval(
    events: Sequence[float],
    *,
    draws: int,
    rng: random.Random,
) -> dict[str, object]:
    """Resample event identities. Copied hypothesis rows are not extra trials."""

    parsed = _require_series(events)
    n = len(parsed)
    center = _mean(parsed)
    means = [
        sum(parsed[rng.randrange(n)] for _index in range(n)) / n for _draw in range(draws)
    ]
    interval = _bootstrap_interval_from_means(
        center,
        n,
        means,
        reason="CLUSTER_EVENT_BOOTSTRAP",
        block_length=1,
    )
    interval["sample_size_used"] = n
    interval["duplicated_rows_used_as_sample_size"] = False
    return interval


def shock_rebuild_bootstrap_interval(
    shocks: Sequence[float],
    horizon: int,
    *,
    draws: int,
    rng: random.Random,
) -> dict[str, object]:
    """Resample underlying shocks and rebuild overlapping windows from those shocks."""

    if isinstance(shocks, (str, bytes)) or not isinstance(shocks, Sequence):
        _fail("DEPENDENCE_VALIDATION_MALFORMED_SERIES", "shocks must be a sequence")
    parsed = [float(value) for value in shocks]
    if len(parsed) < horizon + 1:
        _fail("DEPENDENCE_VALIDATION_MALFORMED_SERIES", "shock series is shorter than the horizon")
    n = len(parsed) - horizon + 1
    observed = [sum(parsed[start : start + horizon]) / horizon for start in range(n)]
    center = _mean(observed)
    shock_count = len(parsed)
    means: list[float] = []
    for _draw in range(draws):
        drawn = [parsed[rng.randrange(shock_count)] for _index in range(shock_count)]
        total = 0.0
        for start in range(n):
            total += sum(drawn[start : start + horizon]) / horizon
        means.append(total / n)
    interval = _bootstrap_interval_from_means(
        center,
        n,
        means,
        reason="SHOCK_REBUILD_OVERLAP",
        block_length=1,
    )
    interval["resampled_unit"] = "underlying_shock"
    interval["outcome_windows_rebuilt"] = True
    return interval


def studentized_null_centered_p_value(
    values: Sequence[float],
    *,
    block_length: int,
    lag: int,
    draws: int,
    rng: random.Random,
) -> dict[str, object]:
    """Null-centered studentized moving-block test of a zero mean.

    Blocks are drawn from the centered series. The statistic is the mean
    divided by a predeclared Newey-West standard error. This is not an
    inversion of a percentile interval.
    """

    if block_length not in PREDECLARED_BLOCK_LENGTHS or lag not in PREDECLARED_HAC_LAGS:
        _fail("DEPENDENCE_VALIDATION_BLOCK_NOT_PREDECLARED", "studentized lag or block is not predeclared")
    parsed = _require_series(values)
    n = len(parsed)
    center = _mean(parsed)
    gammas = _autocovariances(parsed, lag)
    if gammas is None:
        return {
            "status": "UNAVAILABLE",
            "reason": "STUDENTIZED_STANDARD_ERROR_UNAVAILABLE",
            "p_value": "P_VALUES_UNAVAILABLE",
            "rejected_at_alpha": None,
        }
    long_run = _long_run_variance(gammas, lag)
    if long_run <= 0.0:
        return {
            "status": "UNAVAILABLE",
            "reason": "NONPOSITIVE_LONG_RUN_VARIANCE",
            "p_value": "P_VALUES_UNAVAILABLE",
            "rejected_at_alpha": None,
        }
    t_observed = center / math.sqrt(long_run / n)
    centered = [value - center for value in parsed]
    exceed = 0
    available = 0
    for _draw in range(draws):
        indexes = _moving_block_indexes(n, block_length, rng)
        sample = [centered[index] for index in indexes]
        sample_gammas = _autocovariances(sample, lag)
        if sample_gammas is None:
            continue
        sample_long_run = _long_run_variance(sample_gammas, lag)
        if sample_long_run <= 0.0:
            continue
        t_bootstrap = _mean(sample) / math.sqrt(sample_long_run / n)
        available += 1
        if abs(t_bootstrap) >= abs(t_observed):
            exceed += 1
    if available != draws:
        return {
            "status": "UNAVAILABLE",
            "reason": "STUDENTIZED_BOOTSTRAP_DRAW_DEGENERATE",
            "p_value": "P_VALUES_UNAVAILABLE",
            "rejected_at_alpha": None,
            "available_draws": available,
            "requested_draws": draws,
        }
    p_value = (1.0 + exceed) / (1.0 + available)
    return {
        "status": "COMPUTED",
        "reason": "NULL_CENTERED_STUDENTIZED_MOVING_BLOCK",
        "p_value": p_value,
        "rejected_at_alpha": p_value <= ALPHA,
        "alpha": ALPHA,
        "block_length": block_length,
        "lag": lag,
        "draws": draws,
        "plus_one_correction": True,
        "percentile_interval_inverted": False,
        "confidence_interval": "NOT_INVERTED",
        "inference_authorized": False,
        "finite_sample_limitation": (
            "The bootstrap p-value approximates the null distribution. "
            "It is not exact, and this build's replication count is below "
            "the predeclared validation precision."
        ),
    }


def _iid_series(rng: random.Random, n: int, mean: float, sigma: float) -> list[float]:
    return [mean + sigma * _standard_normal(rng) for _index in range(n)]


def _ar1_series(
    rng: random.Random,
    n: int,
    mean: float,
    sigma_e: float,
    phi: float,
) -> list[float]:
    marginal = sigma_e / math.sqrt(1.0 - phi * phi)
    current = mean + marginal * _standard_normal(rng)
    values = [current]
    for _index in range(1, n):
        current = mean + phi * (current - mean) + sigma_e * _standard_normal(rng)
        values.append(current)
    return values


def _ma_series(rng: random.Random, n: int, theta: Sequence[float], mean: float) -> list[float]:
    order = len(theta) - 1
    shocks = [_standard_normal(rng) for _index in range(n + order)]
    values: list[float] = []
    for end in range(order, order + n):
        total = 0.0
        for lag, weight in enumerate(theta):
            total += weight * shocks[end - lag]
        values.append(mean + total)
    return values


def _scenario_targets() -> dict[str, tuple[str, ...]]:
    return {
        "independent_zero_edge": ("primary",),
        "weak_ar1": ("primary",),
        "strong_ar1": ("primary",),
        "long_memory": ("primary",),
        "overlapping_windows": ("primary",),
        "shared_identical_observations": ("unique_events", "duplicated_rows"),
        "common_shock_cross_symbol": ("primary", "contrast"),
        "multiple_horizons": ("primary", "secondary", "contrast"),
        "changing_volatility": ("primary",),
        "regime_change": ("primary",),
        "planted_positive": ("primary",),
        "planted_negative": ("primary",),
        "degenerate_constant": ("primary",),
    }


_ZERO_HORIZON_TARGETS = frozenset(
    {
        ("independent_zero_edge", "primary"),
        ("shared_identical_observations", "unique_events"),
        ("common_shock_cross_symbol", "primary"),
        ("common_shock_cross_symbol", "contrast"),
        ("multiple_horizons", "primary"),
        ("planted_positive", "primary"),
        ("planted_negative", "primary"),
        ("changing_volatility", "primary"),
    }
)
_OVERLAP_HORIZON_TARGETS = frozenset(
    {
        ("overlapping_windows", "primary"),
        ("multiple_horizons", "secondary"),
        ("multiple_horizons", "contrast"),
    }
)


def _exact_finite_horizon(scenario_id: str, target: str) -> int | None:
    """Lag after which the declared autocovariance is exactly zero.

    None means there is no exact finite horizon. An AR(1) returns None.
    """

    key = (scenario_id, target)
    if key in _ZERO_HORIZON_TARGETS:
        return 0
    if key in _OVERLAP_HORIZON_TARGETS:
        return OVERLAP_HORIZON - 1
    if key == ("long_memory", "primary"):
        return LONG_MEMORY_TERMS - 1
    return None


def _practical_truncation_lag(scenario_id: str, target: str) -> int | None:
    """AR(1) lag at the autocorrelation floor. Later lags are small, not absent."""

    if target != "primary":
        return None
    if scenario_id == "weak_ar1":
        return _last_material_ar_lag(WEAK_AR_PHI)
    if scenario_id == "strong_ar1":
        return _last_material_ar_lag(STRONG_AR_PHI)
    return None


def _process_dependence_class(scenario_id: str, target: str) -> str:
    if _exact_finite_horizon(scenario_id, target) is not None:
        return "EXACT_FINITE_DEPENDENCE_HORIZON"
    if _practical_truncation_lag(scenario_id, target) is not None:
        return "ASYMPTOTIC_WEAK_DEPENDENCE"
    return "UNVERIFIED_APPROXIMATION"


def _method_role(method_id: str) -> str:
    if method_id in {"declared_model_z_interval", "iid_variance_z_interval"}:
        return "KNOWN_MODEL_ORACLE"
    if method_id == "iid_normal_interval" or method_id.startswith("newey_west_lag_"):
        return "SAMPLE_ESTIMATED"
    return "EXPERIMENTAL_BOOTSTRAP"


def _known_target(scenario_id: str, target: str) -> bool:
    targets = _scenario_targets()
    return scenario_id in targets and target in targets[scenario_id]


def dependence_assumption_assessment(
    scenario_id: str,
    target: str,
    method_id: str,
) -> dict[str, object]:
    """Classify dependence assumptions without reading coverage.

    `finite_sample_assumptions_exact` is true only when the sampling model
    matches the declared process exactly. A floor truncation, a Bartlett lag,
    and a fixed block are not that match. `captures_all_dependence` stays
    false for every lag and block procedure.
    """

    known = _known_target(scenario_id, target)
    horizon = _exact_finite_horizon(scenario_id, target) if known else None
    truncation = _practical_truncation_lag(scenario_id, target) if known else None
    variance_break = known and scenario_id == "changing_volatility" and target == "primary"
    role = _method_role(method_id)
    process_class = (
        _process_dependence_class(scenario_id, target)
        if known
        else "UNVERIFIED_APPROXIMATION"
    )
    finite_exact = False
    design_applies = False
    method_class = "UNVERIFIED_APPROXIMATION"
    window_includes: bool | None = None
    captures_all = False
    statement = "The finite-sample dependence assumption is not exact."
    if not known:
        statement = "The scenario and target are not in the declared catalogue."
    elif method_id == "iid_normal_interval":
        finite_exact = horizon == 0 or variance_break
        design_applies = finite_exact
        if finite_exact:
            method_class = "EXACT_FINITE_DEPENDENCE_HORIZON"
            captures_all = True
            statement = (
                "Serial dependence ends at lag 0. The interval uses the sample "
                "variance and is not a known-model oracle."
            )
        else:
            statement = "The IID interval does not match this dependence."
    elif method_id.startswith("newey_west_lag_"):
        lag = int(method_id.rsplit("_", 1)[1])
        if truncation is not None and lag >= truncation:
            design_applies = True
            method_class = "PRACTICAL_AUTOCORRELATION_TRUNCATION"
            window_includes = False
            statement = (
                "The lag reaches the autocorrelation floor. Autocorrelation "
                "continues beyond that floor. The Bartlett lag does not capture "
                "all dependence."
            )
        elif truncation is not None:
            method_class = "UNVERIFIED_APPROXIMATION"
            window_includes = False
            statement = (
                "The lag ends before the autocorrelation floor, and "
                "autocorrelation continues past the floor."
            )
        elif horizon is not None and not variance_break and lag >= horizon:
            design_applies = True
            method_class = "ASYMPTOTIC_WEAK_DEPENDENCE"
            window_includes = True
            statement = (
                "The lag window includes every nonzero population autocovariance. "
                "Bartlett weights are not the exact long-run variance. The lag "
                "has not captured all dependence."
            )
        elif horizon is not None and not variance_break:
            window_includes = False
            statement = "The lag window omits nonzero population autocovariance."
        else:
            window_includes = False
            statement = "No exact stationary horizon makes this fixed lag an identity."
    elif method_id in {"declared_model_z_interval", "iid_variance_z_interval"}:
        finite_exact = _z_assumptions(scenario_id, target, method_id)
        design_applies = finite_exact
        method_class = process_class if finite_exact else "UNVERIFIED_APPROXIMATION"
        if finite_exact:
            statement = (
                "Known-model oracle. The interval uses a declared variance of "
                "the mean. It does not estimate dependence from the sample, and "
                "an oracle pass does not validate a practical dependence estimator."
            )
        else:
            statement = "The plugged-in variance is not the declared variance of the mean."
    elif method_id.startswith("moving_block_") or method_id in {
        "circular_block_16",
        "stationary_block_16",
        "shared_clock_block_8",
    }:
        if method_id.startswith("moving_block_"):
            block = int(method_id.rsplit("_", 1)[1])
        elif method_id == "shared_clock_block_8":
            block = SHARED_CLOCK_BLOCK_LENGTH
        else:
            block = LONG_BLOCK_LENGTH
        if method_id.startswith("moving_block_") and block == 1 and (horizon == 0 or variance_break):
            finite_exact = True
            design_applies = True
            method_class = "EXACT_FINITE_DEPENDENCE_HORIZON"
            statement = "Block length 1 resamples serially independent observations."
        elif truncation is not None and block >= truncation:
            design_applies = True
            method_class = "PRACTICAL_AUTOCORRELATION_TRUNCATION"
            statement = (
                "The block reaches the autocorrelation floor. Autocorrelation "
                "remains beyond that floor. The block does not contain all dependence."
            )
        elif horizon is not None and not variance_break and block >= max(horizon, 1):
            design_applies = True
            method_class = "ASYMPTOTIC_WEAK_DEPENDENCE"
            window_includes = True
            statement = (
                "The block length meets an exact finite horizon. A fixed-block "
                "bootstrap is an asymptotic approximation and does not reproduce "
                "the process exactly."
            )
        elif variance_break:
            statement = (
                "A block longer than 1 is not the independent resampling model "
                "for this variance break."
            )
        else:
            if horizon is not None:
                window_includes = False
            statement = "The fixed block is not an exact sampling model for this process."
    elif method_id == "independent_column_block_8":
        statement = (
            "Separate column indexes break a shared shock. This diagnostic is "
            "not a dependence model."
        )
    elif method_id == "cluster_event_bootstrap":
        finite_exact = (scenario_id, target) == (
            "shared_identical_observations",
            "unique_events",
        )
        design_applies = finite_exact
        method_class = (
            "EXACT_FINITE_DEPENDENCE_HORIZON" if finite_exact else "UNVERIFIED_APPROXIMATION"
        )
        statement = (
            "Unique events are the resampling units."
            if finite_exact
            else "Copied rows are not extra independent trials."
        )
    elif method_id == "shock_rebuild_bootstrap":
        finite_exact = (scenario_id, target) == ("overlapping_windows", "primary")
        design_applies = finite_exact
        method_class = (
            "EXACT_FINITE_DEPENDENCE_HORIZON" if finite_exact else "UNVERIFIED_APPROXIMATION"
        )
        statement = (
            "Resamples the known iid shocks and rebuilds every overlap. It does "
            "not estimate a truncation lag. The percentile interval remains an "
            "experimental bootstrap."
            if finite_exact
            else "Shock rebuilding applies only to the declared overlapping-window process."
        )
    elif method_id == "studentized_null_centered_mbb_16":
        block_assessment = dependence_assumption_assessment(
            scenario_id, target, "moving_block_16"
        )
        hac_assessment = dependence_assumption_assessment(
            scenario_id, target, "newey_west_lag_16"
        )
        design_applies = bool(block_assessment["predeclared_design_applies"]) and bool(
            hac_assessment["predeclared_design_applies"]
        )
        classes = {
            str(block_assessment["method_dependence_class"]),
            str(hac_assessment["method_dependence_class"]),
        }
        if "UNVERIFIED_APPROXIMATION" in classes:
            method_class = "UNVERIFIED_APPROXIMATION"
        elif "PRACTICAL_AUTOCORRELATION_TRUNCATION" in classes:
            method_class = "PRACTICAL_AUTOCORRELATION_TRUNCATION"
        else:
            method_class = "ASYMPTOTIC_WEAK_DEPENDENCE"
        window_includes = False
        statement = (
            "Studentized moving-block p-values use fixed-lag Newey-West and a "
            "fixed block. Neither is an exact finite-sample dependence model."
        )
    if scenario_id == "long_memory" and known:
        statement = (
            "The simulator is an MA(23), not an infinite long-memory process. " + statement
        )
    if method_class not in DEPENDENCE_ASSUMPTION_CLASSES:
        _fail("DEPENDENCE_VALIDATION_NUMERICAL", "dependence class is not recognized")
    if role not in METHOD_ROLES:
        _fail("DEPENDENCE_VALIDATION_NUMERICAL", "method role is not recognized")
    return {
        "autocorrelation_remains_beyond_every_finite_lag": truncation is not None,
        "captures_all_dependence": captures_all,
        "exact_finite_horizon": horizon,
        "finite_sample_assumptions_exact": finite_exact,
        "known_model_oracle": role == "KNOWN_MODEL_ORACLE",
        "method_dependence_class": method_class,
        "method_role": role,
        "practical_autocorrelation_truncation_lag": truncation,
        "predeclared_design_applies": design_applies,
        "process_dependence_class": process_class,
        "simulated_process_is_infinite_long_memory": False,
        "statement": statement,
        "window_includes_every_nonzero_population_autocovariance": window_includes,
    }


def assumptions_match(scenario_id: str, target: str, method_id: str) -> bool:
    """Whether the finite-sample dependence assumption is exact.

    The decision uses the known data-generating process. It does not use
    coverage from either partition. A truncated lag or a fixed block returns
    false.
    """

    return bool(
        dependence_assumption_assessment(scenario_id, target, method_id)[
            "finite_sample_assumptions_exact"
        ]
    )


def _population_moments(scenario_id: str, target: str) -> dict[str, float | None]:
    n = SERIES_LENGTH
    sigma = INNOVATION_SIGMA
    if scenario_id == "independent_zero_edge" or scenario_id.startswith("planted"):
        exact = (sigma * sigma) / n
        return {"exact": exact, "marginal": sigma * sigma, "ess": float(n), "true_mean": _planted_mean(scenario_id)}
    if scenario_id == "weak_ar1":
        exact = ar1_variance_of_mean(n, WEAK_AR_PHI, sigma)
        marginal = (sigma * sigma) / (1.0 - WEAK_AR_PHI * WEAK_AR_PHI)
        return {"exact": exact, "marginal": marginal, "ess": marginal / exact, "true_mean": 0.0}
    if scenario_id == "strong_ar1":
        exact = ar1_variance_of_mean(n, STRONG_AR_PHI, sigma)
        marginal = (sigma * sigma) / (1.0 - STRONG_AR_PHI * STRONG_AR_PHI)
        return {"exact": exact, "marginal": marginal, "ess": marginal / exact, "true_mean": 0.0}
    if scenario_id == "long_memory":
        exact = long_memory_variance_of_mean(n)
        return {"exact": exact, "marginal": 1.0, "ess": 1.0 / exact, "true_mean": 0.0}
    if scenario_id == "overlapping_windows":
        exact = overlapping_mean_variance(n, OVERLAP_HORIZON, sigma)
        marginal = overlapping_marginal_variance(OVERLAP_HORIZON, sigma)
        return {"exact": exact, "marginal": marginal, "ess": marginal / exact, "true_mean": 0.0}
    if scenario_id == "shared_identical_observations":
        exact = (sigma * sigma) / SHARED_EVENT_COUNT
        if target == "unique_events":
            return {
                "exact": exact,
                "marginal": sigma * sigma,
                "ess": float(SHARED_EVENT_COUNT),
                "true_mean": 0.0,
            }
        return {"exact": exact, "marginal": sigma * sigma, "ess": float(SHARED_EVENT_COUNT), "true_mean": 0.0}
    if scenario_id == "common_shock_cross_symbol":
        if target == "contrast":
            marginal = 2.0 * (1.0 - COMMON_SHOCK_WEIGHT_SQ)
            exact = marginal / n
            return {"exact": exact, "marginal": marginal, "ess": float(n), "true_mean": 0.0}
        exact = 1.0 / n
        return {"exact": exact, "marginal": 1.0, "ess": float(n), "true_mean": 0.0}
    if scenario_id == "multiple_horizons":
        if target == "primary":
            exact = 1.0 / n
            return {"exact": exact, "marginal": 1.0, "ess": float(n), "true_mean": 0.0}
        if target == "secondary":
            exact = overlapping_mean_variance(n, OVERLAP_HORIZON, sigma)
            marginal = overlapping_marginal_variance(OVERLAP_HORIZON, sigma)
            return {"exact": exact, "marginal": marginal, "ess": marginal / exact, "true_mean": 0.0}
        exact = horizon_contrast_variance(n, OVERLAP_HORIZON, sigma)
        return {"exact": exact, "marginal": None, "ess": None, "true_mean": 0.0}
    if scenario_id == "changing_volatility":
        exact = hetero_variance_of_mean(n, VOLATILITY_LOW, VOLATILITY_HIGH)
        return {"exact": exact, "marginal": None, "ess": float(n), "true_mean": 0.0}
    if scenario_id == "regime_change":
        exact = regime_variance_of_mean(n, REGIME_AR_PHI, sigma)
        return {"exact": exact, "marginal": None, "ess": None, "true_mean": 0.0}
    if scenario_id == "degenerate_constant":
        return {"exact": None, "marginal": None, "ess": None, "true_mean": 0.0}
    _fail("DEPENDENCE_VALIDATION_UNKNOWN_SCENARIO", scenario_id)
    raise AssertionError


def _planted_mean(scenario_id: str) -> float:
    if scenario_id == "planted_positive":
        return PLANTED_MEAN
    if scenario_id == "planted_negative":
        return -PLANTED_MEAN
    return 0.0


def _z_assumptions(scenario_id: str, target: str, method_id: str) -> bool:
    if target == "duplicated_rows" or scenario_id == "degenerate_constant":
        return False
    moments = _population_moments(scenario_id, target)
    exact = moments["exact"]
    marginal = moments["marginal"]
    if exact is None:
        return False
    if method_id == "declared_model_z_interval":
        return True
    if marginal is None:
        return False
    n = SHARED_EVENT_COUNT if target == "unique_events" else SERIES_LENGTH
    iid_variance = float(marginal) / n
    return abs(iid_variance - float(exact)) <= 1e-9


def _draw_scenario(scenario_id: str, rng: random.Random) -> dict[str, object]:
    n = SERIES_LENGTH
    sigma = INNOVATION_SIGMA
    if scenario_id == "independent_zero_edge":
        return {"primary": _iid_series(rng, n, 0.0, sigma)}
    if scenario_id == "weak_ar1":
        return {"primary": _ar1_series(rng, n, 0.0, sigma, WEAK_AR_PHI)}
    if scenario_id == "strong_ar1":
        return {"primary": _ar1_series(rng, n, 0.0, sigma, STRONG_AR_PHI)}
    if scenario_id == "long_memory":
        return {"primary": _ma_series(rng, n, _LONG_MEMORY_THETA, 0.0)}
    if scenario_id == "overlapping_windows":
        shocks = _iid_series(rng, n + OVERLAP_HORIZON - 1, 0.0, sigma)
        primary = [
            sum(shocks[start : start + OVERLAP_HORIZON]) / OVERLAP_HORIZON for start in range(n)
        ]
        return {"primary": primary, "shocks": shocks}
    if scenario_id == "shared_identical_observations":
        events = _iid_series(rng, SHARED_EVENT_COUNT, 0.0, sigma)
        duplicated: list[float] = []
        for value in events:
            duplicated.append(value)
            duplicated.append(value)
        return {"unique_events": events, "duplicated_rows": duplicated}
    if scenario_id == "common_shock_cross_symbol":
        weight = math.sqrt(COMMON_SHOCK_WEIGHT_SQ)
        idiosyncratic = math.sqrt(1.0 - COMMON_SHOCK_WEIGHT_SQ)
        left: list[float] = []
        right: list[float] = []
        for _index in range(n):
            factor = _standard_normal(rng)
            left.append(weight * factor + idiosyncratic * _standard_normal(rng))
            right.append(weight * factor + idiosyncratic * _standard_normal(rng))
        return {
            "primary": left,
            "companion": right,
            "contrast": [first - second for first, second in zip(left, right)],
        }
    if scenario_id == "multiple_horizons":
        shocks = _iid_series(rng, n + OVERLAP_HORIZON - 1, 0.0, sigma)
        secondary = [
            sum(shocks[start : start + OVERLAP_HORIZON]) / OVERLAP_HORIZON for start in range(n)
        ]
        primary = shocks[OVERLAP_HORIZON - 1 : OVERLAP_HORIZON - 1 + n]
        return {
            "primary": primary,
            "secondary": secondary,
            "companion": secondary,
            "contrast": [long - short for long, short in zip(secondary, primary)],
            "left_for_clock": primary,
            "right_for_clock": secondary,
            "shocks": shocks,
        }
    if scenario_id == "changing_volatility":
        values = []
        for index in range(n):
            scale = VOLATILITY_LOW if index < n // 2 else VOLATILITY_HIGH
            values.append(scale * _standard_normal(rng))
        return {"primary": values}
    if scenario_id == "regime_change":
        half = n // 2
        return {
            "primary": _iid_series(rng, half, 0.0, sigma)
            + _ar1_series(rng, half, 0.0, sigma, REGIME_AR_PHI)
        }
    if scenario_id == "planted_positive":
        return {"primary": _iid_series(rng, n, PLANTED_MEAN, sigma)}
    if scenario_id == "planted_negative":
        return {"primary": _iid_series(rng, n, -PLANTED_MEAN, sigma)}
    if scenario_id == "degenerate_constant":
        return {"primary": [0.0 for _index in range(n)]}
    _fail("DEPENDENCE_VALIDATION_UNKNOWN_SCENARIO", scenario_id)
    raise AssertionError


def _closed_form_methods() -> tuple[str, ...]:
    return (
        "iid_normal_interval",
        "iid_variance_z_interval",
        "declared_model_z_interval",
        "newey_west_lag_1",
        "newey_west_lag_4",
        "newey_west_lag_8",
        "newey_west_lag_16",
    )


def _interval_for_method(
    method_id: str,
    series: Sequence[float],
    moments: Mapping[str, float | None],
    *,
    target: str,
) -> dict[str, object]:
    if method_id == "iid_normal_interval":
        return iid_normal_interval(series)
    if method_id.startswith("newey_west_lag_"):
        return newey_west_interval(series, int(method_id.rsplit("_", 1)[1]))
    n = SHARED_EVENT_COUNT if target == "unique_events" else len(series)
    marginal = moments["marginal"]
    exact = moments["exact"]
    if method_id == "iid_variance_z_interval":
        if marginal is None:
            return _unavailable_interval("MARGINAL_VARIANCE_UNAVAILABLE", _mean(series), n)
        return declared_model_z_interval(series, float(marginal) / n)
    if method_id == "declared_model_z_interval":
        if exact is None:
            return _unavailable_interval("DECLARED_VARIANCE_UNAVAILABLE", _mean(series), n)
        return declared_model_z_interval(series, float(exact))
    _fail("DEPENDENCE_VALIDATION_UNKNOWN_METHOD", method_id)
    raise AssertionError


class _IntervalBucket:
    def __init__(self) -> None:
        self.covered = 0
        self.available = 0
        self.unavailable = 0
        self.excludes_zero = 0
        self.entirely_above_zero = 0
        self.entirely_below_zero = 0
        self.zero_null_rejections = 0
        self.p_available = 0
        self.p_unavailable = 0
        self.sum_means = 0.0
        self.sum_square_means = 0.0
        self.mean_count = 0
        self.sum_se = 0.0
        self.se_count = 0
        self.widths: list[float] = []

    def add(self, result: Mapping[str, object], true_mean: float) -> None:
        mean = result.get("mean")
        if isinstance(mean, float):
            self.sum_means += mean
            self.sum_square_means += mean * mean
            self.mean_count += 1
        low = result.get("low")
        high = result.get("high")
        if not isinstance(low, float) or not isinstance(high, float):
            self.unavailable += 1
            if result.get("p_value") == "P_VALUES_UNAVAILABLE":
                self.p_unavailable += 1
            return
        self.available += 1
        self.widths.append(high - low)
        if low <= true_mean <= high:
            self.covered += 1
        excludes = low > 0.0 or high < 0.0
        if excludes:
            self.excludes_zero += 1
        if low > 0.0:
            self.entirely_above_zero += 1
        if high < 0.0:
            self.entirely_below_zero += 1
        standard_error = result.get("standard_error")
        if isinstance(standard_error, float):
            self.sum_se += standard_error
            self.se_count += 1
        p_value = result.get("p_value")
        if isinstance(p_value, float):
            self.p_available += 1
            if p_value <= ALPHA:
                self.zero_null_rejections += 1
        else:
            self.p_unavailable += 1


def _ess_payload(scenario_id: str, target: str) -> dict[str, object]:
    moments = _population_moments(scenario_id, target)
    ess = moments["ess"]
    if ess is None:
        return {
            "scenario_id": scenario_id,
            "target": target,
            "status": "UNAVAILABLE",
            "value": None,
            "reason": "NOT_IDENTIFIED_FROM_THE_DECLARED_MODEL",
            "row_count_used_as_effective_sample_size": False,
            "estimated_from_sample_autocovariance": False,
            "applied_to_event_evidence": False,
        }
    definition = "marginal_variance_over_variance_of_the_mean"
    if scenario_id == "changing_volatility":
        definition = "average_innovation_variance_matches_n_independent_observations"
    return {
        "scenario_id": scenario_id,
        "target": target,
        "status": "IDENTIFIED_FROM_DECLARED_MODEL",
        "value": ess,
        "definition": definition,
        "row_count_used_as_effective_sample_size": False,
        "duplicated_row_count_rejected": target == "duplicated_rows",
        "estimated_from_sample_autocovariance": False,
        "applied_to_event_evidence": False,
    }


def _interval_row(
    *,
    partition: str,
    scenario_id: str,
    target: str,
    method_id: str,
    bucket: _IntervalBucket,
    replications: int,
) -> dict[str, object]:
    moments = _population_moments(scenario_id, target)
    true_mean = float(moments["true_mean"])
    assessment = dependence_assumption_assessment(scenario_id, target, method_id)
    matched = bool(assessment["finite_sample_assumptions_exact"])
    numeric_status = interval_primary_status(
        assumptions_match=matched,
        covered=bucket.covered,
        available=bucket.available,
        unavailable_count=bucket.unavailable,
        replications=replications,
    )
    primary = numeric_status if partition == HOLDOUT_PARTITION else "EXPLORATORY_ONLY"
    coverage = binomial_monte_carlo_report(bucket.covered, bucket.available)
    zero_role = "false_exclusion_of_true_null" if true_mean == 0.0 else "power_or_sign_diagnostic"
    zero_report = binomial_monte_carlo_report(bucket.excludes_zero, bucket.available)
    p_status: object
    if method_id in {"declared_model_z_interval", "iid_variance_z_interval"}:
        if true_mean != 0.0:
            p_status = "EXPLORATORY_ONLY"
        elif bucket.p_available == 0:
            p_status = "P_VALUES_UNAVAILABLE"
        else:
            test_status = null_test_primary_status(
                assumptions_match=matched,
                rejections=bucket.zero_null_rejections,
                available=bucket.p_available,
                unavailable_count=bucket.p_unavailable,
                replications=replications,
            )
            p_status = test_status if partition == HOLDOUT_PARTITION else "EXPLORATORY_ONLY"
    else:
        p_status = "P_VALUES_UNAVAILABLE"
    monte_carlo_sd = _sample_sd(bucket.sum_means, bucket.sum_square_means, bucket.mean_count)
    mean_estimate = bucket.sum_means / bucket.mean_count if bucket.mean_count else None
    return {
        "kind": "interval",
        "partition": partition,
        "scenario_id": scenario_id,
        "target": target,
        "method_id": method_id,
        "assumptions_match": matched,
        "method_role": assessment["method_role"],
        "dependence_assessment": assessment,
        "primary_status": primary,
        "numeric_status": numeric_status,
        "catalogue_inference": "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
        "p_value_status": p_status,
        "valid_p_values_established": p_status == "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL",
        "coverage": coverage,
        "zero_exclusion": {
            "role": zero_role,
            "acceptance_gate": False,
            **zero_report,
        },
        "entirely_above_zero": binomial_monte_carlo_report(
            bucket.entirely_above_zero, bucket.available
        ),
        "entirely_below_zero": binomial_monte_carlo_report(
            bucket.entirely_below_zero, bucket.available
        ),
        "null_rejections": binomial_monte_carlo_report(
            bucket.zero_null_rejections, bucket.p_available
        ),
        "width_mean": (sum(bucket.widths) / len(bucket.widths)) if bucket.widths else None,
        "width_median": _median(bucket.widths),
        "bias": None if mean_estimate is None else mean_estimate - true_mean,
        "mean_reported_standard_error": (
            bucket.sum_se / bucket.se_count if bucket.se_count else None
        ),
        "monte_carlo_standard_deviation_of_mean": monte_carlo_sd,
        "unavailable_count": bucket.unavailable,
        "replications": replications,
        "true_mean": true_mean,
        "effective_sample_size": _ess_payload(scenario_id, target),
        "lag_or_block_selected_from_results": False,
    }


def _evaluate_closed_form(
    *,
    master_seed: int,
    replications: int,
    partition: str,
    stream_code: int,
) -> list[dict[str, object]]:
    seeds = _replication_seeds(master_seed, stream_code, replications)
    buckets = {
        (scenario_id, target, method_id): _IntervalBucket()
        for scenario_id, targets in _scenario_targets().items()
        for target in targets
        for method_id in _closed_form_methods()
    }
    for seed in seeds:
        for scenario_id in _scenario_targets():
            draw = _draw_scenario(scenario_id, random.Random(seed))
            for target in _scenario_targets()[scenario_id]:
                series = draw[target]
                if not isinstance(series, list):
                    _fail("DEPENDENCE_VALIDATION_NUMERICAL", "drawn target is missing")
                moments = _population_moments(scenario_id, target)
                true_mean = float(moments["true_mean"])
                for method_id in _closed_form_methods():
                    result = _interval_for_method(
                        method_id, series, moments, target=target
                    )
                    buckets[(scenario_id, target, method_id)].add(result, true_mean)
    return [
        _interval_row(
            partition=partition,
            scenario_id=scenario_id,
            target=target,
            method_id=method_id,
            bucket=bucket,
            replications=replications,
        )
        for (scenario_id, target, method_id), bucket in buckets.items()
    ]


def _bootstrap_rng(replication_seed: int, method_code: int) -> random.Random:
    rng = random.Random(replication_seed ^ BOOTSTRAP_STREAM_SALT)
    for _index in range(method_code):
        rng.random()
    return rng


def _bootstrap_plan(partition: str) -> tuple[tuple[str, str, str, int], ...]:
    if partition == CALIBRATION_PARTITION:
        return tuple(
            (scenario_id, target, method_id, 16)
            for scenario_id, target, method_id in CALIBRATION_BOOTSTRAP_TARGETS
        )
    plan: list[tuple[str, str, str, int]] = []
    for scenario_id in MOVING_BLOCK_GRID_SCENARIOS:
        for block_length in MOVING_BLOCK_GRID_LENGTHS:
            plan.append((scenario_id, "primary", f"moving_block_{block_length}", block_length))
    for scenario_id in LONG_BLOCK_ONLY_SCENARIOS:
        target = "duplicated_rows" if scenario_id == "shared_identical_observations" else "primary"
        plan.append((scenario_id, target, "moving_block_16", 16))
    for scenario_id in CIRCULAR_STATIONARY_SCENARIOS:
        plan.append((scenario_id, "primary", "circular_block_16", 16))
        plan.append((scenario_id, "primary", "stationary_block_16", 16))
    plan.append(("common_shock_cross_symbol", "contrast", "shared_clock_block_8", 8))
    plan.append(("multiple_horizons", "contrast", "shared_clock_block_8", 8))
    plan.append(("common_shock_cross_symbol", "contrast", "independent_column_block_8", 8))
    plan.append(("multiple_horizons", "contrast", "independent_column_block_8", 8))
    plan.append(("shared_identical_observations", "unique_events", "cluster_event_bootstrap", 1))
    plan.append(("overlapping_windows", "primary", "shock_rebuild_bootstrap", 1))
    return tuple(plan)


def _evaluate_bootstrap(
    *,
    master_seed: int,
    replications: int,
    partition: str,
) -> list[dict[str, object]]:
    plan = _bootstrap_plan(partition)
    seeds = _replication_seeds(master_seed, BOOTSTRAP_SCHEDULE_STREAM, replications)
    buckets = {(item[0], item[1], item[2]): _IntervalBucket() for item in plan}
    draws = BOOTSTRAP_DRAWS
    for seed in seeds:
        draws_by_scenario: dict[str, dict[str, object]] = {}
        for scenario_id, target, method_id, block_length in plan:
            if scenario_id not in draws_by_scenario:
                draws_by_scenario[scenario_id] = _draw_scenario(
                    scenario_id, random.Random(seed)
                )
            draw = draws_by_scenario[scenario_id]
            moments = _population_moments(scenario_id, target)
            true_mean = float(moments["true_mean"])
            method_code = 1 + plan.index((scenario_id, target, method_id, block_length))
            rng = _bootstrap_rng(seed, method_code)
            result = _bootstrap_result(
                method_id,
                draw,
                target,
                block_length=block_length,
                draws=draws,
                rng=rng,
            )
            refuse_percentile_interval_as_p_value_silently(result)
            buckets[(scenario_id, target, method_id)].add(result, true_mean)
    return [
        _interval_row(
            partition=partition,
            scenario_id=scenario_id,
            target=target,
            method_id=method_id,
            bucket=bucket,
            replications=replications,
        )
        for (scenario_id, target, method_id), bucket in buckets.items()
    ]


def refuse_percentile_interval_as_p_value_silently(result: Mapping[str, object]) -> None:
    """Bootstrap interval builders must not carry a numeric p-value."""

    p_value = result.get("p_value")
    if isinstance(p_value, float):
        _fail(
            "DEPENDENCE_VALIDATION_PERCENTILE_INTERVAL_IS_NOT_A_P_VALUE",
            "a bootstrap percentile interval returned a numeric p-value",
        )


def _bootstrap_result(
    method_id: str,
    draw: Mapping[str, object],
    target: str,
    *,
    block_length: int,
    draws: int,
    rng: random.Random,
) -> dict[str, object]:
    if method_id.startswith("moving_block_"):
        series = draw[target]
        if not isinstance(series, list):
            _fail("DEPENDENCE_VALIDATION_NUMERICAL", "bootstrap series is missing")
        return moving_block_bootstrap_interval(
            series, block_length, draws=draws, rng=rng
        )
    if method_id == "circular_block_16":
        series = draw[target]
        if not isinstance(series, list):
            _fail("DEPENDENCE_VALIDATION_NUMERICAL", "bootstrap series is missing")
        return circular_block_bootstrap_interval(series, block_length, draws=draws, rng=rng)
    if method_id == "stationary_block_16":
        series = draw[target]
        if not isinstance(series, list):
            _fail("DEPENDENCE_VALIDATION_NUMERICAL", "bootstrap series is missing")
        return stationary_bootstrap_interval(series, block_length, draws=draws, rng=rng)
    if method_id in {"shared_clock_block_8", "independent_column_block_8"}:
        if "left_for_clock" in draw:
            left = draw["left_for_clock"]
            right = draw["right_for_clock"]
        else:
            left = draw["primary"]
            right = draw["companion"]
        if not isinstance(left, list) or not isinstance(right, list):
            _fail("DEPENDENCE_VALIDATION_NUMERICAL", "paired series are missing")
        if method_id == "shared_clock_block_8":
            return shared_clock_contrast_interval(
                left, right, block_length, draws=draws, rng=rng
            )
        return independent_column_contrast_interval(
            left, right, block_length, draws=draws, rng=rng
        )
    if method_id == "cluster_event_bootstrap":
        events = draw["unique_events"]
        if not isinstance(events, list):
            _fail("DEPENDENCE_VALIDATION_NUMERICAL", "events are missing")
        return cluster_event_bootstrap_interval(events, draws=draws, rng=rng)
    if method_id == "shock_rebuild_bootstrap":
        shocks = draw["shocks"]
        if not isinstance(shocks, list):
            _fail("DEPENDENCE_VALIDATION_NUMERICAL", "shocks are missing")
        return shock_rebuild_bootstrap_interval(
            shocks, OVERLAP_HORIZON, draws=draws, rng=rng
        )
    _fail("DEPENDENCE_VALIDATION_UNKNOWN_METHOD", method_id)
    raise AssertionError


def _evaluate_studentized(
    *,
    master_seed: int,
    replications: int,
    partition: str,
) -> list[dict[str, object]]:
    seeds = _replication_seeds(master_seed, BOOTSTRAP_SCHEDULE_STREAM + 7, replications)
    rows: list[dict[str, object]] = []
    for scenario_id in STUDENTIZED_SCENARIOS:
        rejections = 0
        available = 0
        unavailable = 0
        assessment = dependence_assumption_assessment(
            scenario_id, "primary", "studentized_null_centered_mbb_16"
        )
        matched = bool(assessment["finite_sample_assumptions_exact"])
        for seed in seeds:
            draw = _draw_scenario(scenario_id, random.Random(seed))
            series = draw["primary"]
            if not isinstance(series, list):
                _fail("DEPENDENCE_VALIDATION_NUMERICAL", "studentized series is missing")
            result = studentized_null_centered_p_value(
                series,
                block_length=STUDENTIZED_BLOCK_LENGTH,
                lag=STUDENTIZED_HAC_LAG,
                draws=STUDENTIZED_DRAWS,
                rng=_bootstrap_rng(seed, 30),
            )
            if result["status"] != "COMPUTED":
                unavailable += 1
                continue
            available += 1
            if result["rejected_at_alpha"] is True:
                rejections += 1
        numeric = null_test_primary_status(
            assumptions_match=matched,
            rejections=rejections,
            available=available,
            unavailable_count=unavailable,
            replications=replications,
            p_values_computed=True,
        )
        rows.append(
            {
                "kind": "null_test",
                "partition": partition,
                "scenario_id": scenario_id,
                "target": "primary",
                "method_id": "studentized_null_centered_mbb_16",
                "assumptions_match": matched,
                "method_role": assessment["method_role"],
                "dependence_assessment": assessment,
                "p_values_computed": True,
                "primary_status": numeric if partition == HOLDOUT_PARTITION else "EXPLORATORY_ONLY",
                "numeric_status": numeric,
                "catalogue_inference": "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
                "p_value_status": numeric if partition == HOLDOUT_PARTITION else "EXPLORATORY_ONLY",
                "valid_p_values_established": numeric == "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL"
                and partition == HOLDOUT_PARTITION,
                "null_hypothesis": "mean_equals_zero",
                "construction": "null_centered_studentized_moving_block",
                "percentile_interval_inverted": False,
                "lag_or_block_selected_from_results": False,
                "rejections": binomial_monte_carlo_report(rejections, available),
                "unavailable_count": unavailable,
                "replications": replications,
                "finite_sample_limitation": (
                    "Sixty Monte Carlo replications and 49 bootstrap draws "
                    "are below the predeclared validation precision. The fixed "
                    "lag and block are not an exact finite-sample dependence model."
                ),
            }
        )
    return rows


def _factor_means(
    rng: random.Random,
    means: Sequence[float],
    *,
    rho: float,
    standard_error: float,
) -> list[float]:
    common = _standard_normal(rng)
    drawn: list[float] = []
    idiosyncratic_scale = math.sqrt(1.0 - rho)
    common_scale = math.sqrt(rho)
    for mean in means:
        shock = common_scale * common + idiosyncratic_scale * _standard_normal(rng)
        drawn.append(mean + standard_error * shock)
    return drawn


def _family_means(size: int, alternative_count: int, alternative_mean: float) -> list[float]:
    if alternative_count > size:
        _fail("DEPENDENCE_VALIDATION_MALFORMED_FAMILY", "alternatives exceed the family")
    means = [0.0] * (size - alternative_count)
    means.extend([alternative_mean] * alternative_count)
    return means


def _evaluate_family(
    *,
    seed: int,
    replications: int,
    family_size: int,
    rho: float,
    alternative_count: int,
    alternative_mean: float,
    partition: str,
    study_id: str,
    assumptions_for_control: bool,
) -> dict[str, object]:
    _require_master_seed(seed)
    standard_error = 1.0 / math.sqrt(SERIES_LENGTH)
    hypotheses = _family_means(family_size, alternative_count, alternative_mean)
    rng = random.Random(seed)
    holm_family_rejections = 0
    raw_family_rejections = 0
    true_null_holm = 0
    shortlist_rejections = 0
    alternative_holm_hits = 0
    alternative_opportunities = 0
    absolute_inflation = 0.0
    selected_nulls = 0
    null_indexes = [index for index, mean in enumerate(hypotheses) if mean == 0.0]
    alternative_indexes = [index for index, mean in enumerate(hypotheses) if mean != 0.0]
    for _replication in range(replications):
        drawn = _factor_means(
            rng, hypotheses, rho=rho, standard_error=standard_error
        )
        p_values = [_normal_two_sided_p(value / standard_error) for value in drawn]
        adjusted = holm_adjusted_p_values(p_values)
        if any(value <= ALPHA for value in p_values):
            raw_family_rejections += 1
        if any(value <= ALPHA for value in adjusted):
            holm_family_rejections += 1
        if any(adjusted[index] <= ALPHA for index in null_indexes):
            true_null_holm += 1
        winner = max(range(family_size), key=lambda index: (abs(drawn[index]), -index))
        if p_values[winner] <= ALPHA:
            shortlist_rejections += 1
        absolute_inflation += abs(drawn[winner]) - abs(hypotheses[winner])
        if hypotheses[winner] == 0.0:
            selected_nulls += 1
        if alternative_indexes:
            alternative_opportunities += len(alternative_indexes)
            alternative_holm_hits += sum(
                1 for index in alternative_indexes if adjusted[index] <= ALPHA
            )
    control_count = true_null_holm if alternative_count else holm_family_rejections
    holm_assessment = empirical_fwer_assessment(
        assumptions_match=assumptions_for_control,
        familywise_rejections=control_count,
        replications=replications,
    )
    shortlist_assessment = empirical_fwer_assessment(
        assumptions_match=False,
        familywise_rejections=shortlist_rejections,
        replications=replications,
    )
    raw_assessment = empirical_fwer_assessment(
        assumptions_match=False,
        familywise_rejections=raw_family_rejections,
        replications=replications,
    )
    numeric = str(holm_assessment["primary_status"])
    shortlist_numeric = str(shortlist_assessment["primary_status"])
    raw_numeric = str(raw_assessment["primary_status"])
    primary = numeric if partition == HOLDOUT_PARTITION else "EXPLORATORY_ONLY"
    inspected = {
        "newly_established_independent_pass": False,
        "inspected_outcomes_reused_as_fresh_confirmation": False,
        "acceptance_interpretation": (
            "METHODOLOGICAL_CORRECTION_OF_AN_INSPECTED_HOLDOUT"
            if partition == HOLDOUT_PARTITION
            else "NOT_AN_ACCEPTANCE_PARTITION"
        ),
    }
    return {
        "study_id": study_id,
        "partition": partition,
        "family_size": family_size,
        "frozen_universe_family_size": DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
        "replaces_frozen_universe": False,
        "rho": rho,
        "alternative_count": alternative_count,
        "alternative_mean": alternative_mean,
        "replications": replications,
        "seed": seed,
        "marginal_p_values": "exact_gaussian_under_declared_standard_error",
        "holm": {
            "assumptions_match": assumptions_for_control,
            "primary_status": primary,
            "numeric_status": numeric,
            "empirical_fwer_claim": holm_assessment["empirical_fwer_claim"],
            "one_sided_wilson_95": holm_assessment["one_sided_wilson_95"],
            "point_estimate_at_or_below_alpha": holm_assessment[
                "point_estimate_at_or_below_alpha"
            ],
            "theoretical_holm_guarantee": _theoretical_holm_guarantee(
                applies=assumptions_for_control
            ),
            **inspected,
            "familywise_false_positives": binomial_monte_carlo_report(
                control_count, replications
            ),
            "any_holm_rejection": binomial_monte_carlo_report(
                holm_family_rejections, replications
            ),
        },
        "uncorrected": {
            "assumptions_match": False,
            "primary_status": raw_numeric if partition == HOLDOUT_PARTITION else "EXPLORATORY_ONLY",
            "numeric_status": raw_numeric,
            "empirical_fwer_claim": raw_assessment["empirical_fwer_claim"],
            "one_sided_wilson_95": raw_assessment["one_sided_wilson_95"],
            "point_estimate_at_or_below_alpha": raw_assessment[
                "point_estimate_at_or_below_alpha"
            ],
            "theoretical_holm_guarantee": _theoretical_holm_guarantee(applies=False),
            **inspected,
            "familywise_false_positives": binomial_monte_carlo_report(
                raw_family_rejections, replications
            ),
        },
        "shortlist_only_holm": {
            "assumptions_match": False,
            "controls_the_original_search": False,
            "primary_status": (
                shortlist_numeric if partition == HOLDOUT_PARTITION else "EXPLORATORY_ONLY"
            ),
            "numeric_status": shortlist_numeric,
            "empirical_fwer_claim": shortlist_assessment["empirical_fwer_claim"],
            "one_sided_wilson_95": shortlist_assessment["one_sided_wilson_95"],
            "point_estimate_at_or_below_alpha": shortlist_assessment[
                "point_estimate_at_or_below_alpha"
            ],
            "theoretical_holm_guarantee": _theoretical_holm_guarantee(applies=False),
            **inspected,
            "winner_rejections": binomial_monte_carlo_report(
                shortlist_rejections, replications
            ),
            "note": "Holm on the single winner does not correct the search that chose the winner.",
        },
        "winners_curse": {
            "primary_status": "EXPLORATORY_ONLY",
            "mean_absolute_inflation": absolute_inflation / replications,
            "selected_true_nulls": binomial_monte_carlo_report(selected_nulls, replications),
            "acceptance_gate": False,
        },
        "alternative_holm_power": (
            None
            if alternative_opportunities == 0
            else {
                "primary_status": "EXPLORATORY_ONLY",
                "acceptance_gate": False,
                **binomial_monte_carlo_report(alternative_holm_hits, alternative_opportunities),
            }
        ),
        "catalogue_inference": "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
        "holm_rejections_do_not_exceed_uncorrected": holm_family_rejections
        <= raw_family_rejections,
    }


def _repeated_selection(seed: int) -> dict[str, object]:
    _require_master_seed(seed)
    standard_error = 1.0 / math.sqrt(SERIES_LENGTH)
    hypotheses = [0.0] * REPEATED_FAMILY_SIZE
    rng = random.Random(seed)
    recurrent = 0
    correlation_total = 0.0
    for _replication in range(REPEATED_SEGMENT_REPLICATIONS):
        winners: list[int] = []
        first: list[float] | None = None
        second: list[float] | None = None
        for segment in range(REPEATED_SEGMENTS):
            drawn = _factor_means(
                rng,
                hypotheses,
                rho=FAMILY_EQUICORRELATION,
                standard_error=standard_error,
            )
            if segment == 0:
                first = drawn
            elif segment == 1:
                second = drawn
            winners.append(max(range(REPEATED_FAMILY_SIZE), key=lambda index: abs(drawn[index])))
        counts: dict[int, int] = {}
        for winner in winners:
            counts[winner] = counts.get(winner, 0) + 1
        if max(counts.values()) >= 2:
            recurrent += 1
        if first is None or second is None:
            _fail("DEPENDENCE_VALIDATION_NUMERICAL", "repeated segments did not draw two means")
        correlation_total += _pearson(first, second)
    shared_rng = random.Random(FAMILY_SHARED_COPY_SEED)
    shared_correlation = 0.0
    for _replication in range(REPEATED_SEGMENT_REPLICATIONS):
        drawn = _factor_means(
            shared_rng,
            hypotheses,
            rho=FAMILY_EQUICORRELATION,
            standard_error=standard_error,
        )
        shared_correlation += _pearson(drawn, list(drawn))
    return {
        "partition": HOLDOUT_PARTITION,
        "primary_status": "EXPLORATORY_ONLY",
        "catalogue_inference": "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
        "segments": REPEATED_SEGMENTS,
        "family_size": REPEATED_FAMILY_SIZE,
        "replications": REPEATED_SEGMENT_REPLICATIONS,
        "complete_null": True,
        "chance_recurrence": binomial_monte_carlo_report(
            recurrent, REPEATED_SEGMENT_REPLICATIONS
        ),
        "chance_recurrence_is_not_cross_year_confirmation": True,
        "independent_segment_mean_correlation": correlation_total / REPEATED_SEGMENT_REPLICATIONS,
        "shared_copy": {
            "identical_copy": True,
            "mean_correlation": shared_correlation / REPEATED_SEGMENT_REPLICATIONS,
            "confirmation_p_values": "P_VALUES_UNAVAILABLE",
            "reason": "Shared observations are not an independent confirmation sample.",
        },
        "independent_segment_confirmation_p_values": "P_VALUES_UNAVAILABLE",
        "frozen_universe_controlled": False,
    }


def _pearson(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        _fail("DEPENDENCE_VALIDATION_NUMERICAL", "correlation series do not match")
    mean_left = _mean(left)
    mean_right = _mean(right)
    numerator = sum(
        (first - mean_left) * (second - mean_right) for first, second in zip(left, right)
    )
    left_scale = math.sqrt(sum((value - mean_left) ** 2 for value in left))
    right_scale = math.sqrt(sum((value - mean_right) ** 2 for value in right))
    if left_scale == 0.0 or right_scale == 0.0:
        return 1.0 if left == right else 0.0
    return numerator / (left_scale * right_scale)


def _stability_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for seed in STABILITY_SEEDS:
        _require_master_seed(seed)
        evaluated = {
            (scenario_id, target, method_id): _IntervalBucket()
            for scenario_id, target, method_id in STABILITY_EVALUATIONS
        }
        for replication_seed in _replication_seeds(seed, STABILITY_STREAM, STABILITY_REPLICATIONS):
            draws = {
                scenario_id: _draw_scenario(scenario_id, random.Random(replication_seed))
                for scenario_id, _target, _method in STABILITY_EVALUATIONS
            }
            for scenario_id, target, method_id in STABILITY_EVALUATIONS:
                series = draws[scenario_id][target]
                if not isinstance(series, list):
                    _fail("DEPENDENCE_VALIDATION_NUMERICAL", "stability series is missing")
                moments = _population_moments(scenario_id, target)
                result = _interval_for_method(method_id, series, moments, target=target)
                evaluated[(scenario_id, target, method_id)].add(
                    result, float(moments["true_mean"])
                )
        for (scenario_id, target, method_id), bucket in evaluated.items():
            rows.append(
                _interval_row(
                    partition=STABILITY_PARTITION,
                    scenario_id=scenario_id,
                    target=target,
                    method_id=method_id,
                    bucket=bucket,
                    replications=STABILITY_REPLICATIONS,
                )
            )
    return rows


def _stability_spans(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[float]] = {}
    for row in rows:
        if row.get("partition") != STABILITY_PARTITION:
            continue
        coverage = row.get("coverage")
        if not isinstance(coverage, Mapping) or coverage.get("rate") is None:
            continue
        key = (str(row["scenario_id"]), str(row["target"]), str(row["method_id"]))
        grouped.setdefault(key, []).append(float(coverage["rate"]))
    spans: list[dict[str, object]] = []
    for (scenario_id, target, method_id), rates in grouped.items():
        spans.append(
            {
                "scenario_id": scenario_id,
                "target": target,
                "method_id": method_id,
                "seeds": list(STABILITY_SEEDS),
                "rates": rates,
                "minimum": min(rates),
                "maximum": max(rates),
                "span": max(rates) - min(rates),
                "pooled_into_holdout_denominator": False,
                "primary_status": "EXPLORATORY_ONLY",
                "span_is_not_a_binomial_standard_error": True,
            }
        )
    return spans


def _scenario_catalogue() -> list[dict[str, object]]:
    descriptions = {
        "independent_zero_edge": "120 independent N(0, 1) observations.",
        "weak_ar1": (
            "Stationary AR(1), phi 0.3, innovation sigma 1, mean 0. "
            "Autocorrelation continues past every finite lag."
        ),
        "strong_ar1": (
            "Stationary AR(1), phi 0.8, innovation sigma 1, mean 0. "
            "Autocorrelation continues past every finite lag."
        ),
        "long_memory": (
            "Finite MA(23) with weights (k+1)^(-0.6), normalized to variance 1. "
            "This is not an infinite long-memory process."
        ),
        "overlapping_windows": "Means of 4 consecutive iid shocks. The windows overlap.",
        "shared_identical_observations": "60 iid events, each copied into two adjacent rows.",
        "common_shock_cross_symbol": "Two series share a factor with weight squared 0.49.",
        "multiple_horizons": "The same shocks scored at horizon 1 and as a 4-shock average.",
        "changing_volatility": "Independent observations, sigma 1 then sigma 3 at the midpoint.",
        "regime_change": "An iid block followed by an independent AR(1) block with phi 0.9.",
        "planted_positive": "Independent N(0.35, 1) observations.",
        "planted_negative": "Independent N(-0.35, 1) observations.",
        "degenerate_constant": "120 zeros. Variance estimators are unavailable.",
    }
    catalogue = []
    for scenario_id, text in descriptions.items():
        catalogue.append(
            {
                "scenario_id": scenario_id,
                "data_generating_process": text,
                "targets": list(_scenario_targets()[scenario_id]),
                "null_mean": 0.0,
                "estimand": "mean of the named target series",
                "selected_after_seeing_results": False,
            }
        )
    return catalogue


def _method_catalogue() -> list[dict[str, object]]:
    return [
        {
            "method_id": "iid_normal_interval",
            "assumptions": "Independent observations with finite variance. Sample variance uses n-1.",
        },
        {
            "method_id": "newey_west_bartlett",
            "method_role": "SAMPLE_ESTIMATED",
            "lags": list(PREDECLARED_HAC_LAGS),
            "assumptions": (
                "Asymptotic weak dependence. A lag at an autocorrelation floor is a "
                "practical truncation, not an exact horizon. Bartlett weights are "
                "not the exact long-run variance."
            ),
            "captures_all_dependence": False,
            "lag_selected_from_results": False,
        },
        {
            "method_id": "declared_model_z_interval",
            "method_role": "KNOWN_MODEL_ORACLE",
            "assumptions": (
                "The Gaussian data-generating variance of the mean is known. "
                "This is not an estimator of unknown dependence."
            ),
        },
        {
            "method_id": "iid_variance_z_interval",
            "method_role": "KNOWN_MODEL_ORACLE",
            "assumptions": (
                "Marginal variance divided by the row count equals the variance "
                "of the mean. The variance is declared, not estimated from sample autocovariance."
            ),
        },
        {
            "method_id": "moving_block",
            "method_role": "EXPERIMENTAL_BOOTSTRAP",
            "block_lengths": list(PREDECLARED_BLOCK_LENGTHS),
            "assumptions": (
                "Length 1 resamples serially independent observations. A longer "
                "fixed block is an asymptotic approximation and does not contain "
                "all AR(1) dependence."
            ),
            "captures_all_dependence": False,
        },
        {
            "method_id": "circular_block_16",
            "method_role": "EXPERIMENTAL_BOOTSTRAP",
            "assumptions": (
                "Stationary wrapping is an asymptotic device. The block does not "
                "capture all dependence."
            ),
            "captures_all_dependence": False,
        },
        {
            "method_id": "stationary_block_16",
            "method_role": "EXPERIMENTAL_BOOTSTRAP",
            "assumptions": (
                "Stationarity. Geometric blocks have mean length 16 and wrap. "
                "This is an asymptotic approximation."
            ),
            "captures_all_dependence": False,
        },
        {
            "method_id": "shared_clock_block_8",
            "assumptions": "Series share a synthetic index. One block path is applied to every series.",
        },
        {
            "method_id": "independent_column_block_8",
            "assumptions": "None. This diagnostic breaks a common shock on purpose.",
        },
        {
            "method_id": "cluster_event_bootstrap",
            "assumptions": "Event identities are the resampling units.",
        },
        {
            "method_id": "shock_rebuild_bootstrap",
            "assumptions": "Overlapping outcomes are functions of iid shocks that can be resampled.",
        },
        {
            "method_id": "studentized_null_centered_mbb_16",
            "method_role": "EXPERIMENTAL_BOOTSTRAP",
            "assumptions": (
                "Uses fixed-lag Newey-West and a fixed moving block. Neither is "
                "an exact finite-sample dependence model."
            ),
            "captures_all_dependence": False,
            "produces_confidence_interval": False,
        },
    ]


def _acceptance_rule() -> dict[str, object]:
    return {
        "nominal_coverage": NOMINAL_COVERAGE,
        "alpha": ALPHA,
        "wilson_method": "wilson_score",
        "z_95": Z_95,
        "clear_undercoverage_ceiling": CLEAR_UNDERCOVERAGE_CEILING,
        "clear_overcoverage_floor": CLEAR_OVERCOVERAGE_FLOOR,
        "clear_rejection_floor": CLEAR_REJECTION_FLOOR,
        "min_denominator_to_fail": MIN_DENOMINATOR_TO_FAIL,
        "min_denominator_to_validate": MIN_DENOMINATOR_TO_VALIDATE,
        "max_wilson_half_width_to_validate": MAX_WILSON_HALF_WIDTH_TO_VALIDATE,
        "max_unavailable_fraction_for_validation": MAX_UNAVAILABLE_FRACTION_FOR_VALIDATION,
        "calibration_partition_can_validate": False,
        "holdout_seed_used_to_choose_methods": False,
        "prior_ar1_counts_used_as_thresholds": False,
        "fwer_failure_rule": "two-sided Wilson lower bound above alpha",
        "fwer_positive_claim": (
            "one-sided 95 percent Wilson upper bound at or below alpha, "
            "the predeclared precision floor, and valid marginal p-values"
        ),
        "fwer_z_one_sided_95": Z_ONE_SIDED_95,
        "fwer_point_estimate_at_or_below_alpha_is_sufficient": False,
        "fwer_rule_selected_from_inspected_counts": False,
        "inspected_holdout_is_a_fresh_independent_validation_of_the_revised_rule": False,
        "new_large_fwer_validation_launched": False,
        "bootstrap_replications_below_validation_precision": (
            HOLDOUT_BOOTSTRAP_REPLICATIONS < MIN_DENOMINATOR_TO_VALIDATE
        ),
        "larger_bootstrap_validation_not_run": {
            "replications_required": MIN_DENOMINATOR_TO_VALIDATE,
            "current_bootstrap_replications": HOLDOUT_BOOTSTRAP_REPLICATIONS,
            "current_bootstrap_draws": BOOTSTRAP_DRAWS,
            "approximate_replication_multiplier": (
                MIN_DENOMINATOR_TO_VALIDATE / HOLDOUT_BOOTSTRAP_REPLICATIONS
            ),
            "launched": False,
            "reason": (
                "A validation claim for bootstrap intervals needs at least "
                "200 Monte Carlo replications and a Wilson half-width of at most 0.04. "
                "That larger run is documented and was not started."
            ),
        },
    }


def _summary(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    counts = {status: 0 for status in PRIMARY_STATUSES}
    validated: list[dict[str, str]] = []
    failed: list[dict[str, str]] = []
    oracles: list[dict[str, str]] = []
    sample_estimators: list[dict[str, str]] = []
    experimental_bootstraps: list[dict[str, str]] = []
    dependence_estimators: list[dict[str, str]] = []
    for row in rows:
        if row.get("partition") != HOLDOUT_PARTITION:
            continue
        status = str(row["primary_status"])
        counts[status] = counts.get(status, 0) + 1
        identity = {
            "scenario_id": str(row["scenario_id"]),
            "target": str(row["target"]),
            "method_id": str(row["method_id"]),
        }
        if status == "FAILED_SYNTHETIC_CALIBRATION":
            failed.append(identity)
        if status != "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL":
            continue
        validated.append(identity)
        role = str(row.get("method_role"))
        method_id = identity["method_id"]
        if role == "KNOWN_MODEL_ORACLE":
            oracles.append(identity)
        elif role == "SAMPLE_ESTIMATED":
            sample_estimators.append(identity)
            if method_id.startswith("newey_west_lag_"):
                dependence_estimators.append(identity)
        elif role == "EXPERIMENTAL_BOOTSTRAP":
            experimental_bootstraps.append(identity)
            dependence_estimators.append(identity)
    return {
        "holdout_status_counts": counts,
        "validated_under_declared_synthetic_model": validated,
        "validated_known_model_oracles": oracles,
        "validated_sample_estimators": sample_estimators,
        "validated_experimental_bootstraps": experimental_bootstraps,
        "validated_practical_dependence_estimators": dependence_estimators,
        "oracle_pass_validates_a_practical_dependence_estimator": False,
        "failed_synthetic_calibration": failed,
        "validated_methods_are_not_authorized_for_catalogue_inference": True,
        "software_correctness_is_not_synthetic_calibration": True,
        "synthetic_calibration_is_not_catalogue_validity": True,
    }


def _multiple_testing(provenance_seed_note: str) -> dict[str, object]:
    del provenance_seed_note
    studies = [
        _evaluate_family(
            seed=FAMILY_CALIBRATION_SEED,
            replications=FAMILY_CALIBRATION_REPLICATIONS,
            family_size=FAMILY_VALIDATION_SIZE,
            rho=FAMILY_EQUICORRELATION,
            alternative_count=0,
            alternative_mean=0.0,
            partition=CALIBRATION_PARTITION,
            study_id="calibration_correlated_complete_null",
            assumptions_for_control=True,
        ),
        _evaluate_family(
            seed=FAMILY_CORRELATED_NULL_SEED,
            replications=FAMILY_VALIDATION_REPLICATIONS,
            family_size=FAMILY_VALIDATION_SIZE,
            rho=FAMILY_EQUICORRELATION,
            alternative_count=0,
            alternative_mean=0.0,
            partition=HOLDOUT_PARTITION,
            study_id="holdout_correlated_complete_null",
            assumptions_for_control=True,
        ),
        _evaluate_family(
            seed=FAMILY_INDEPENDENT_NULL_SEED,
            replications=FAMILY_VALIDATION_REPLICATIONS,
            family_size=FAMILY_VALIDATION_SIZE,
            rho=0.0,
            alternative_count=0,
            alternative_mean=0.0,
            partition=HOLDOUT_PARTITION,
            study_id="holdout_independent_complete_null",
            assumptions_for_control=True,
        ),
        _evaluate_family(
            seed=FAMILY_MIXED_SEED,
            replications=FAMILY_VALIDATION_REPLICATIONS,
            family_size=FAMILY_VALIDATION_SIZE,
            rho=FAMILY_EQUICORRELATION,
            alternative_count=FAMILY_ALTERNATIVE_COUNT,
            alternative_mean=FAMILY_ALTERNATIVE_MEAN,
            partition=HOLDOUT_PARTITION,
            study_id="holdout_mixed_null_and_alternative",
            assumptions_for_control=True,
        ),
        _evaluate_family(
            seed=FAMILY_SMALL_SEED,
            replications=FAMILY_VALIDATION_REPLICATIONS,
            family_size=FAMILY_SMALL_SIZE,
            rho=0.0,
            alternative_count=0,
            alternative_mean=0.0,
            partition=HOLDOUT_PARTITION,
            study_id="holdout_independent_family_10",
            assumptions_for_control=True,
        ),
        _evaluate_family(
            seed=FAMILY_SCALING_FWER_SEED,
            replications=FAMILY_SCALING_REPLICATIONS,
            family_size=FAMILY_SCALING_SIZE,
            rho=FAMILY_EQUICORRELATION,
            alternative_count=0,
            alternative_mean=0.0,
            partition=HOLDOUT_PARTITION,
            study_id="scaling_family_160_insufficient_by_design",
            assumptions_for_control=True,
        ),
    ]
    return {
        "reference_family_size": DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
        "bounded_family_replaces_reference_family": False,
        "familywise_error_estimated_at_reference_family": False,
        "reference_family_status": "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
        "empirical_fwer_rule_revision": {
            "previous_positive_rule_accepted_a_point_estimate_at_or_below_alpha": True,
            "corrected_positive_rule": "one_sided_wilson_upper_bound_at_or_below_alpha",
            "z_one_sided_95": Z_ONE_SIDED_95,
            "inspected_holdout_reused_as_independent_confirmation": False,
            "new_validation_experiment_launched": False,
        },
        "studies": studies,
        "repeated_annual_segments": _repeated_selection(FAMILY_REPEATED_SEGMENT_SEED),
        "scaling_sizes_timed_outside_the_hashed_document": list(FAMILY_SCALING_SIZES),
        "holm_applied_only_to_shortlisted_winners": False,
    }


def _rows_from_body(body: Mapping[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    partitions = body["partitions"]
    if not isinstance(partitions, Mapping):
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "partitions are missing")
    for name in (CALIBRATION_PARTITION, HOLDOUT_PARTITION, STABILITY_PARTITION):
        partition = partitions.get(name)
        if not isinstance(partition, Mapping):
            _fail("DEPENDENCE_VALIDATION_INTEGRITY", f"{name} partition is missing")
        partition_rows = partition.get("rows")
        if not isinstance(partition_rows, list):
            _fail("DEPENDENCE_VALIDATION_INTEGRITY", f"{name} rows are missing")
        rows.extend(partition_rows)
    return rows


def _expected_numeric_status(row: Mapping[str, object]) -> str:
    kind = row.get("kind")
    if kind == "interval":
        coverage = row.get("coverage")
        if not isinstance(coverage, Mapping):
            _fail("DEPENDENCE_VALIDATION_INTEGRITY", "coverage is missing")
        return interval_primary_status(
            assumptions_match=bool(row.get("assumptions_match")),
            covered=int(coverage["numerator"]),
            available=int(coverage["denominator"]),
            unavailable_count=int(row["unavailable_count"]),
            replications=int(row["replications"]),
        )
    if kind == "null_test":
        rejections = row.get("rejections")
        if not isinstance(rejections, Mapping):
            _fail("DEPENDENCE_VALIDATION_INTEGRITY", "rejections are missing")
        return null_test_primary_status(
            assumptions_match=bool(row.get("assumptions_match")),
            rejections=int(rejections["numerator"]),
            available=int(rejections["denominator"]),
            unavailable_count=int(row["unavailable_count"]),
            replications=int(row["replications"]),
            p_values_computed=bool(row.get("p_values_computed")),
        )
    _fail("DEPENDENCE_VALIDATION_INTEGRITY", "row kind is not recognized")
    raise AssertionError


def _check_row(row: Mapping[str, object]) -> None:
    if row.get("catalogue_inference") != "CATALOGUE_INFERENCE_NOT_AUTHORIZED":
        _fail("DEPENDENCE_VALIDATION_AUTHORIZATION", "catalogue inference was authorized")
    if row.get("lag_or_block_selected_from_results") is True:
        _fail("DEPENDENCE_VALIDATION_AUTHORIZATION", "a lag or block was selected from results")
    status = row.get("primary_status")
    if status not in PRIMARY_STATUSES:
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "primary status is not in the frozen vocabulary")
    numeric = _expected_numeric_status(row)
    if row.get("numeric_status") != numeric:
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "numeric status does not match the frozen rule")
    partition = row.get("partition")
    if partition == HOLDOUT_PARTITION:
        if status != numeric:
            _fail("DEPENDENCE_VALIDATION_INTEGRITY", "holdout status does not match the frozen rule")
    elif status != "EXPLORATORY_ONLY":
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "a non-holdout row was used as a validation result",
        )
    if status == "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL" and row.get("assumptions_match") is not True:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "a method validated outside its declared assumptions",
        )
    scenario_id = row.get("scenario_id")
    target = row.get("target")
    method_id = row.get("method_id")
    if not isinstance(scenario_id, str) or not isinstance(target, str) or not isinstance(method_id, str):
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "a row identity is missing")
    expected_assessment = dependence_assumption_assessment(scenario_id, target, method_id)
    if bool(row.get("assumptions_match")) is not bool(
        expected_assessment["finite_sample_assumptions_exact"]
    ):
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "assumptions_match does not match the declared process",
        )
    if row.get("method_role") != expected_assessment["method_role"]:
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "method role does not match the procedure")
    stored_assessment = row.get("dependence_assessment")
    if stored_assessment != expected_assessment:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "dependence classification does not match the declared process",
        )
    if method_id.startswith("newey_west_lag_") and stored_assessment["captures_all_dependence"] is True:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "a Newey-West lag was described as capturing all dependence",
        )
    if (
        status == "VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL"
        and expected_assessment["method_role"] == "KNOWN_MODEL_ORACLE"
        and row.get("method_role") != "KNOWN_MODEL_ORACLE"
    ):
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "an oracle pass was relabeled as a practical estimator",
        )


def _body(provenance: DependenceValidationProvenance) -> dict[str, object]:
    calibration_rows = _evaluate_closed_form(
        master_seed=CALIBRATION_MASTER_SEED,
        replications=CALIBRATION_CLOSED_FORM_REPLICATIONS,
        partition=CALIBRATION_PARTITION,
        stream_code=CLOSED_FORM_STREAM,
    )
    calibration_rows.extend(
        _evaluate_bootstrap(
            master_seed=CALIBRATION_MASTER_SEED,
            replications=CALIBRATION_BOOTSTRAP_REPLICATIONS,
            partition=CALIBRATION_PARTITION,
        )
    )
    holdout_rows = _evaluate_closed_form(
        master_seed=HOLDOUT_MASTER_SEED,
        replications=HOLDOUT_CLOSED_FORM_REPLICATIONS,
        partition=HOLDOUT_PARTITION,
        stream_code=CLOSED_FORM_STREAM,
    )
    holdout_rows.extend(
        _evaluate_bootstrap(
            master_seed=HOLDOUT_MASTER_SEED,
            replications=HOLDOUT_BOOTSTRAP_REPLICATIONS,
            partition=HOLDOUT_PARTITION,
        )
    )
    holdout_rows.extend(
        _evaluate_studentized(
            master_seed=HOLDOUT_MASTER_SEED,
            replications=STUDENTIZED_REPLICATIONS,
            partition=HOLDOUT_PARTITION,
        )
    )
    stability = _stability_rows()
    partitions = {
        CALIBRATION_PARTITION: {
            "role": "development_not_acceptance",
            "master_seed": CALIBRATION_MASTER_SEED,
            "used_to_choose_methods": False,
            "rows": calibration_rows,
        },
        HOLDOUT_PARTITION: {
            "role": "acceptance",
            "master_seed": HOLDOUT_MASTER_SEED,
            "rows": holdout_rows,
        },
        STABILITY_PARTITION: {
            "role": "seed_span_not_pooled",
            "seeds": list(STABILITY_SEEDS),
            "rows": stability,
            "spans": _stability_spans(stability),
        },
    }
    body: dict[str, object] = {
        "schema_version": DEPENDENCE_VALIDATION_VERSION,
        "document_kind": "DEPENDENCE_AWARE_SYNTHETIC_VALIDATION",
        "validation_protocol": DEPENDENCE_VALIDATION_PROTOCOL,
        "pattern_tool": PATTERN_TOOL,
        "governing_research_method": GOVERNING_RESEARCH_METHOD,
        "pattern_tool_is_not_the_governing_method": True,
        "protocol_decision": ANNUAL_CATALOGUE_PROTOCOL_DECISION,
        "protocol_fingerprint": protocol_fingerprint(),
        "directional_hypotheses_per_annual_segment": (
            DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT
        ),
        "inference_authorized": False,
        "catalogue_inference": "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
        "error_control_claimed_for_frozen_universe": False,
        "statistical_promotion_authorized": False,
        "portfolio_profit_claimed": False,
        "dec470_thresholds_modified": False,
        "authorizations": _authorizations(),
        "recorded_thresholds": _recorded_thresholds(),
        "prior_ar1_context": dict(_PRIOR_AR1_CONTEXT),
        "seeds": {
            "forbidden_master_seeds": sorted(FORBIDDEN_MASTER_SEEDS),
            "calibration_master_seed": CALIBRATION_MASTER_SEED,
            "holdout_master_seed": HOLDOUT_MASTER_SEED,
            "stability_seeds": list(STABILITY_SEEDS),
            "family_seeds": [
                FAMILY_CALIBRATION_SEED,
                FAMILY_CORRELATED_NULL_SEED,
                FAMILY_INDEPENDENT_NULL_SEED,
                FAMILY_MIXED_SEED,
                FAMILY_REPEATED_SEGMENT_SEED,
                FAMILY_SHARED_COPY_SEED,
                FAMILY_SCALING_FWER_SEED,
                FAMILY_SMALL_SEED,
            ],
            "holdout_pooled_with_calibration": False,
        },
        "acceptance_rule": _acceptance_rule(),
        "scenarios": _scenario_catalogue(),
        "methods": _method_catalogue(),
        "effective_sample_sizes": [
            _ess_payload(scenario_id, target)
            for scenario_id, targets in _scenario_targets().items()
            for target in targets
        ],
        "partitions": partitions,
        "multiple_testing": _multiple_testing(""),
        "provenance": _provenance_payload(provenance),
    }
    body["summary"] = _summary(_rows_from_body(body))
    return body


def _finalize(body: dict[str, object]) -> tuple[dict[str, object], bytes]:
    digest = _sha256_json(body)
    document = dict(body)
    document["content_sha256"] = digest
    return document, _canonical_json(document)


def compile_dependence_validation(
    provenance: DependenceValidationProvenance | None,
    *,
    historical_artifact_path: str | None = None,
    authorize_catalogue_inference: bool = False,
) -> tuple[dict[str, object], bytes]:
    """Run the frozen synthetic harness and return canonical bytes."""

    if historical_artifact_path is not None:
        _fail(
            "DEPENDENCE_VALIDATION_HISTORICAL_ACCESS_REFUSED",
            "historical market artifacts are not inputs",
        )
    if authorize_catalogue_inference:
        _fail(
            "DEPENDENCE_VALIDATION_CATALOGUE_INFERENCE_REFUSED",
            "synthetic validation does not authorize catalogue inference",
        )
    if provenance is None:
        _fail("DEPENDENCE_VALIDATION_MISSING_PROVENANCE", "provenance is required")
    document, raw = _finalize(_body(provenance))
    validate_dependence_validation_document(raw)
    return document, raw


def _object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    parsed: dict[str, object] = {}
    for key, value in pairs:
        if key in parsed:
            _fail(
                "DEPENDENCE_VALIDATION_NONCANONICAL_JSON",
                f"duplicate JSON object key {key!r}",
            )
        parsed[key] = value
    return parsed


def _require_canonical_bytes(raw: bytes) -> dict[str, object]:
    if raw.startswith(b"\xef\xbb\xbf"):
        _fail("DEPENDENCE_VALIDATION_NONCANONICAL_JSON", "UTF-8 BOM is not canonical JSON")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        _fail("DEPENDENCE_VALIDATION_NONCANONICAL_JSON", "document must be UTF-8 JSON")
        raise AssertionError
    try:
        parsed = json.loads(text, object_pairs_hook=_object_without_duplicate_keys)
    except json.JSONDecodeError:
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "document is not JSON")
        raise AssertionError
    if not isinstance(parsed, dict):
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "document must be a JSON object")
    digest = parsed.get("content_sha256")
    body = {key: value for key, value in parsed.items() if key != "content_sha256"}
    try:
        canonical = _canonical_json(parsed)
        recomputed = _sha256_json(body)
    except (TypeError, ValueError):
        _fail("DEPENDENCE_VALIDATION_NONCANONICAL_JSON", "document is not canonical JSON")
        raise AssertionError
    if raw != canonical or digest != recomputed:
        _fail(
            "DEPENDENCE_VALIDATION_NONCANONICAL_JSON",
            "serialized validation must match canonical JSON bytes",
        )
    return parsed


def _wilson_mapping_matches(stored: object, expected: object) -> bool:
    if not isinstance(stored, Mapping) or not isinstance(expected, Mapping):
        return False
    if set(stored) != set(expected):
        return False
    for key, value in expected.items():
        other = stored[key]
        if isinstance(value, float):
            if isinstance(other, bool) or not isinstance(other, (int, float)):
                return False
            if not math.isclose(float(other), value, rel_tol=0.0, abs_tol=1e-12):
                return False
        elif other != value:
            return False
    return True


def _check_fwer_block(
    block: Mapping[str, object],
    *,
    assumptions_match: bool,
    numerator_key: str,
    holdout: bool,
) -> None:
    if block.get("assumptions_match") is not assumptions_match:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "familywise assumptions do not match the procedure",
        )
    report = block.get(numerator_key)
    if not isinstance(report, Mapping):
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "familywise counts are missing")
    assessment = empirical_fwer_assessment(
        assumptions_match=assumptions_match,
        familywise_rejections=int(report["numerator"]),
        replications=int(report["denominator"]),
    )
    if block.get("numeric_status") != assessment["primary_status"]:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "familywise status does not match the corrected rule",
        )
    if block.get("empirical_fwer_claim") != assessment["empirical_fwer_claim"]:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "familywise claim does not match the corrected rule",
        )
    if not _wilson_mapping_matches(
        block.get("one_sided_wilson_95"),
        assessment["one_sided_wilson_95"],
    ):
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "one-sided Wilson bound does not match the recorded counts",
        )
    if holdout and block.get("primary_status") != assessment["primary_status"]:
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "holdout familywise status drifted")
    theory = block.get("theoretical_holm_guarantee")
    if not isinstance(theory, Mapping) or theory.get("established_by_simulation") is not False:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "a simulation was described as Holm's theorem",
        )
    if theory.get("guarantee_applies") is not assumptions_match:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "the Holm guarantee was detached from its condition",
        )
    if block.get("newly_established_independent_pass") is not False:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "inspected familywise counts were labeled as a new independent pass",
        )
    if block.get("inspected_outcomes_reused_as_fresh_confirmation") is not False:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "inspected familywise counts were reused as fresh confirmation",
        )


def reproduce_bounded_synthetic_case() -> dict[str, object]:
    """Re-run one tiny synthetic family twice.

    Agreement shows that this process repeats the generator. The count is not
    an acceptance threshold, and the run is not the inspected holdout.
    """

    def once() -> int:
        study = _evaluate_family(
            seed=BOUNDED_REPRODUCTION_SEED,
            replications=BOUNDED_REPRODUCTION_REPLICATIONS,
            family_size=BOUNDED_REPRODUCTION_FAMILY_SIZE,
            rho=0.0,
            alternative_count=0,
            alternative_mean=0.0,
            partition=CALIBRATION_PARTITION,
            study_id="bounded_source_reproduction",
            assumptions_for_control=True,
        )
        holm = study["holm"]
        if not isinstance(holm, Mapping):
            _fail("DEPENDENCE_VALIDATION_NUMERICAL", "bounded Holm block is missing")
        report = holm["familywise_false_positives"]
        if not isinstance(report, Mapping):
            _fail("DEPENDENCE_VALIDATION_NUMERICAL", "bounded familywise count is missing")
        return int(report["numerator"])

    if BOUNDED_REPRODUCTION_SEED in FORBIDDEN_MASTER_SEEDS:
        _fail("DEPENDENCE_VALIDATION_FORBIDDEN_MASTER_SEED", "bounded seed is forbidden")
    if BOUNDED_REPRODUCTION_SEED == HOLDOUT_MASTER_SEED:
        _fail("DEPENDENCE_VALIDATION_FORBIDDEN_MASTER_SEED", "bounded seed reuses the holdout")
    if BOUNDED_REPRODUCTION_REPLICATIONS >= MIN_DENOMINATOR_TO_VALIDATE:
        _fail(
            "DEPENDENCE_VALIDATION_NUMERICAL",
            "bounded reproduction is large enough to look like validation",
        )
    first = once()
    second = once()
    if first != second:
        _fail("DEPENDENCE_VALIDATION_NUMERICAL", "bounded reproduction was not deterministic")
    return {
        "kind": "BOUNDED_SYNTHETIC_REPRODUCTION",
        "deterministic": True,
        "seed": BOUNDED_REPRODUCTION_SEED,
        "replications": BOUNDED_REPRODUCTION_REPLICATIONS,
        "family_size": BOUNDED_REPRODUCTION_FAMILY_SIZE,
        "familywise_rejections": first,
        "full_monte_carlo_reproduced": False,
        "holdout_reproduced": False,
        "used_as_acceptance_threshold": False,
        "catalogue_inference": "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
    }


def validate_dependence_validation_document(document: Mapping[str, object] | bytes | str) -> dict[str, object]:
    """Recompute statuses and the authorization boundary.

    This does not regenerate the Monte Carlo experiment. A recomputed SHA-256
    of altered counts is not independently reproduced evidence. A separate
    bounded synthetic case checks that the generator repeats; it does not
    certify the recorded holdout counts.
    """

    if isinstance(document, str):
        raw = document.encode("utf-8")
    elif isinstance(document, bytes):
        raw = document
    elif isinstance(document, Mapping):
        raw = _canonical_json(dict(document))
    else:
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "document type is not supported")
        raise AssertionError
    parsed = _require_canonical_bytes(raw)
    if parsed.get("validation_protocol") != DEPENDENCE_VALIDATION_PROTOCOL:
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "protocol id drifted")
    if parsed.get("protocol_fingerprint") != EXPECTED_PROTOCOL_FINGERPRINT:
        _fail("DEPENDENCE_VALIDATION_PROTOCOL_FINGERPRINT_DRIFT", "DEC-470 fingerprint drifted")
    if parsed.get("directional_hypotheses_per_annual_segment") != 89460:
        _fail("DEPENDENCE_VALIDATION_UNIVERSE_DRIFT", "the frozen universe changed")
    if parsed.get("catalogue_inference") != "CATALOGUE_INFERENCE_NOT_AUTHORIZED":
        _fail("DEPENDENCE_VALIDATION_AUTHORIZATION", "catalogue inference is open")
    if parsed.get("inference_authorized") is not False:
        _fail("DEPENDENCE_VALIDATION_AUTHORIZATION", "inference is open")
    if parsed.get("dec470_thresholds_modified") is not False:
        _fail("DEPENDENCE_VALIDATION_AUTHORIZATION", "DEC-470 thresholds were modified")
    authorizations = parsed.get("authorizations")
    if not isinstance(authorizations, Mapping) or any(authorizations.values()):
        _fail("DEPENDENCE_VALIDATION_AUTHORIZATION", "an authorization flag is open")
    prior = parsed.get("prior_ar1_context")
    if not isinstance(prior, Mapping) or prior.get("used_as_acceptance_threshold") is not False:
        _fail("DEPENDENCE_VALIDATION_AUTHORIZATION", "prior AR(1) counts were used as thresholds")
    for row in _rows_from_body(parsed):
        if not isinstance(row, Mapping):
            _fail("DEPENDENCE_VALIDATION_INTEGRITY", "a row is not an object")
        _check_row(row)
    multiple = parsed.get("multiple_testing")
    if not isinstance(multiple, Mapping):
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "multiple testing is missing")
    if multiple.get("familywise_error_estimated_at_reference_family") is not False:
        _fail(
            "DEPENDENCE_VALIDATION_AUTHORIZATION",
            "familywise error was claimed for the 89460 universe",
        )
    if multiple.get("reference_family_status") != "CATALOGUE_INFERENCE_NOT_AUTHORIZED":
        _fail("DEPENDENCE_VALIDATION_AUTHORIZATION", "the reference family was authorized")
    studies = multiple.get("studies")
    if not isinstance(studies, list):
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "family studies are missing")
    for study in studies:
        if not isinstance(study, Mapping):
            _fail("DEPENDENCE_VALIDATION_INTEGRITY", "a family study is not an object")
        holm = study.get("holm")
        if not isinstance(holm, Mapping):
            _fail("DEPENDENCE_VALIDATION_INTEGRITY", "Holm block is missing")
        if study.get("marginal_p_values") != "exact_gaussian_under_declared_standard_error":
            _fail(
                "DEPENDENCE_VALIDATION_INTEGRITY",
                "family marginal p-values are not the declared Gaussian reference",
            )
        _check_fwer_block(
            holm,
            assumptions_match=True,
            numerator_key="familywise_false_positives",
            holdout=study.get("partition") == HOLDOUT_PARTITION,
        )
        uncorrected = study.get("uncorrected")
        shortlist = study.get("shortlist_only_holm")
        if not isinstance(uncorrected, Mapping) or not isinstance(shortlist, Mapping):
            _fail("DEPENDENCE_VALIDATION_INTEGRITY", "familywise comparison blocks are missing")
        _check_fwer_block(
            uncorrected,
            assumptions_match=False,
            numerator_key="familywise_false_positives",
            holdout=study.get("partition") == HOLDOUT_PARTITION,
        )
        _check_fwer_block(
            shortlist,
            assumptions_match=False,
            numerator_key="winner_rejections",
            holdout=study.get("partition") == HOLDOUT_PARTITION,
        )
        if study.get("replaces_frozen_universe") is not False:
            _fail("DEPENDENCE_VALIDATION_AUTHORIZATION", "a bounded family replaced the universe")
    summary = parsed.get("summary")
    if not isinstance(summary, Mapping):
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "summary is missing")
    recomputed = _summary(_rows_from_body(parsed))
    if summary.get("holdout_status_counts") != recomputed["holdout_status_counts"]:
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "summary counts drifted")
    if (
        summary.get("validated_practical_dependence_estimators")
        != recomputed["validated_practical_dependence_estimators"]
    ):
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "practical dependence-estimator summary drifted",
        )
    if summary.get("validated_known_model_oracles") != recomputed["validated_known_model_oracles"]:
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "oracle summary drifted")
    if summary.get("oracle_pass_validates_a_practical_dependence_estimator") is not False:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "an oracle pass was treated as a practical dependence estimator",
        )
    acceptance = parsed.get("acceptance_rule")
    if not isinstance(acceptance, Mapping):
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "acceptance rule is missing")
    if acceptance.get("fwer_point_estimate_at_or_below_alpha_is_sufficient") is not False:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "a point estimate was treated as familywise control",
        )
    if acceptance.get("fwer_z_one_sided_95") != Z_ONE_SIDED_95:
        _fail("DEPENDENCE_VALIDATION_INTEGRITY", "the one-sided Wilson quantile drifted")
    if (
        acceptance.get("inspected_holdout_is_a_fresh_independent_validation_of_the_revised_rule")
        is not False
    ):
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "the inspected holdout was reused as a fresh confirmation",
        )
    if acceptance.get("new_large_fwer_validation_launched") is not False:
        _fail("DEPENDENCE_VALIDATION_AUTHORIZATION", "a new familywise validation was launched")
    revision = multiple.get("empirical_fwer_rule_revision")
    if not isinstance(revision, Mapping) or revision.get(
        "inspected_holdout_reused_as_independent_confirmation"
    ) is not False:
        _fail(
            "DEPENDENCE_VALIDATION_INTEGRITY",
            "the revised familywise rule was marked as independently confirmed",
        )
    return {
        "document": parsed,
        "canonical_json_checked": True,
        "statuses_recomputed_from_recorded_counts": True,
        "authorization_boundary_checked": True,
        "assumption_classes_recomputed_from_the_declared_process": True,
        "numerical_experiment_regenerated": False,
        "full_monte_carlo_reproduced": False,
        "independently_reproduced_evidence": False,
        "recomputed_digest_of_altered_counts_is_independent_reproduction": False,
        "bounded_synthetic_reproduction": reproduce_bounded_synthetic_case(),
    }


def assess_supplied_events_for_catalogue_inference(
    document: Mapping[str, object] | None,
    *,
    treat_episode_groups_as_independent_trials: bool = False,
    assume_independence: bool = False,
) -> dict[str, object]:
    """Refuse catalogue inference for event evidence. No interval is computed."""

    if treat_episode_groups_as_independent_trials:
        refuse_episode_groups_as_independent_trials()
    if assume_independence:
        _fail(
            "DEPENDENCE_VALIDATION_INDEPENDENCE_ASSUMPTION_REFUSED",
            "event evidence does not justify independence",
        )
    if not isinstance(document, Mapping):
        _fail("DEPENDENCE_VALIDATION_MALFORMED_EVENTS", "event evidence must be an object")
    if document.get("evidence_basis") != "CALLER_SUPPLIED_SYNTHETIC_EVENTS_NOT_FROZEN_EVIDENCE":
        _fail(
            "DEPENDENCE_VALIDATION_EVENT_BASIS_REFUSED",
            "only the caller-supplied synthetic event basis is recognized, and it is not inferred",
        )
    return {
        "primary_status": "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
        "p_values": "P_VALUES_UNAVAILABLE",
        "effective_sample_size": "UNAVAILABLE",
        "sampling_uncertainty": "UNAVAILABLE",
        "episode_groups_are_independent_trials": False,
        "intervals_computed": False,
        "catalogue_multiple_testing_applied": False,
        "frozen_universe_family_size": DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
    }


def dependence_validation_contract() -> dict[str, object]:
    """Protocol identity without running the Monte Carlo harness."""

    return {
        "validation_protocol": DEPENDENCE_VALIDATION_PROTOCOL,
        "pattern_tool": PATTERN_TOOL,
        "governing_research_method": GOVERNING_RESEARCH_METHOD,
        "pattern_tool_is_not_the_governing_method": True,
        "protocol_decision": ANNUAL_CATALOGUE_PROTOCOL_DECISION,
        "protocol_fingerprint": protocol_fingerprint(),
        "directional_hypotheses_per_annual_segment": DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
        "forbidden_master_seeds": sorted(FORBIDDEN_MASTER_SEEDS),
        "calibration_master_seed": CALIBRATION_MASTER_SEED,
        "holdout_master_seed": HOLDOUT_MASTER_SEED,
        "acceptance_rule": _acceptance_rule(),
        "authorizations": _authorizations(),
        "recorded_thresholds": _recorded_thresholds(),
        "prior_ar1_context": dict(_PRIOR_AR1_CONTEXT),
        "catalogue_inference": "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
        "annual_run_385_consumed": ANNUAL_RUN_385_CONSUMED,
        "dec629_adopted": DEC629_ADOPTED,
        "dec630_adopted": DEC630_ADOPTED,
    }


def measure_representative_workload(
    provenance: DependenceValidationProvenance,
) -> dict[str, object]:
    """Time one canonical compile and one Holm pass at the frozen universe size."""

    tracemalloc.start()
    started = time.perf_counter()
    document, raw = compile_dependence_validation(provenance)
    compile_seconds = time.perf_counter() - started
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rng = random.Random(FAMILY_SCALING_FWER_SEED)
    timings: list[dict[str, object]] = []
    for size in FAMILY_SCALING_SIZES:
        p_values = [rng.random() for _index in range(size)]
        tick = time.perf_counter()
        holm_adjusted_p_values(p_values)
        timings.append(
            {
                "family_size": size,
                "holm_seconds": time.perf_counter() - tick,
                "fwer_estimated": False,
                "catalogue_inference": "CATALOGUE_INFERENCE_NOT_AUTHORIZED",
            }
        )
    return {
        "compile_seconds": compile_seconds,
        "tracemalloc_peak_bytes": peak,
        "canonical_bytes": len(raw),
        "content_sha256": document["content_sha256"],
        "holm_scaling_seconds": timings,
        "full_universe_fwer_monte_carlo_launched": False,
        "historical_artifact_read": False,
    }


def _assert_frozen_boundaries() -> None:
    if GOVERNING_RESEARCH_METHOD != "DISCOVERY_FIRST_ANNUAL_PATTERN_CATALOGUE":
        raise ValueError("DEPENDENCE_VALIDATION_METHOD_DRIFT")
    if ANNUAL_CATALOGUE_PROTOCOL_DECISION != "DEC-470":
        raise ValueError("DEPENDENCE_VALIDATION_PROTOCOL_DRIFT")
    if DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT != 89460:
        raise ValueError("DEPENDENCE_VALIDATION_UNIVERSE_DRIFT")
    if protocol_fingerprint() != EXPECTED_PROTOCOL_FINGERPRINT:
        raise ValueError("DEPENDENCE_VALIDATION_PROTOCOL_FINGERPRINT_DRIFT")
    if EVENT_ANNUAL_RUN_385_CONSUMED or ANNUAL_RUN_385_CONSUMED:
        raise ValueError("DEPENDENCE_VALIDATION_ANNUAL_RUN_CONSUMED")
    if EVENT_DEC629_ADOPTED or EVENT_DEC630_ADOPTED or DEC629_ADOPTED or DEC630_ADOPTED:
        raise ValueError("DEPENDENCE_VALIDATION_DEC629_OR_DEC630_ADOPTED")
    masters = [
        CALIBRATION_MASTER_SEED,
        FAMILY_CALIBRATION_SEED,
        HOLDOUT_MASTER_SEED,
        *STABILITY_SEEDS,
        FAMILY_CORRELATED_NULL_SEED,
        FAMILY_INDEPENDENT_NULL_SEED,
        FAMILY_MIXED_SEED,
        FAMILY_REPEATED_SEGMENT_SEED,
        FAMILY_SHARED_COPY_SEED,
        FAMILY_SCALING_FWER_SEED,
        FAMILY_SMALL_SEED,
    ]
    if len(masters) != len(set(masters)):
        raise ValueError("DEPENDENCE_VALIDATION_SEED_DRIFT")
    if any(seed in FORBIDDEN_MASTER_SEEDS for seed in masters):
        raise ValueError("DEPENDENCE_VALIDATION_SEED_DRIFT")
    if HOLDOUT_BOOTSTRAP_REPLICATIONS >= MIN_DENOMINATOR_TO_VALIDATE:
        raise ValueError("DEPENDENCE_VALIDATION_BOOTSTRAP_PRECISION_DRIFT")
    if STUDENTIZED_REPLICATIONS >= MIN_DENOMINATOR_TO_VALIDATE:
        raise ValueError("DEPENDENCE_VALIDATION_BOOTSTRAP_PRECISION_DRIFT")
    if _last_material_ar_lag(WEAK_AR_PHI) != 2:
        raise ValueError("DEPENDENCE_VALIDATION_HORIZON_DRIFT")
    if _last_material_ar_lag(STRONG_AR_PHI) != 13:
        raise ValueError("DEPENDENCE_VALIDATION_HORIZON_DRIFT")
    truncation = dependence_assumption_assessment("strong_ar1", "primary", "newey_west_lag_16")
    if truncation["finite_sample_assumptions_exact"] or truncation["captures_all_dependence"]:
        raise ValueError("DEPENDENCE_VALIDATION_TRUNCATION_TREATED_AS_EXACT")
    if truncation["method_dependence_class"] != "PRACTICAL_AUTOCORRELATION_TRUNCATION":
        raise ValueError("DEPENDENCE_VALIDATION_TRUNCATION_TREATED_AS_EXACT")
    if BOUNDED_REPRODUCTION_SEED in FORBIDDEN_MASTER_SEEDS:
        raise ValueError("DEPENDENCE_VALIDATION_SEED_DRIFT")
    if BOUNDED_REPRODUCTION_SEED == HOLDOUT_MASTER_SEED:
        raise ValueError("DEPENDENCE_VALIDATION_SEED_DRIFT")
    if BOUNDED_REPRODUCTION_REPLICATIONS >= MIN_DENOMINATOR_TO_VALIDATE:
        raise ValueError("DEPENDENCE_VALIDATION_BOOTSTRAP_PRECISION_DRIFT")
    if abs(ar1_variance_of_mean(2, 0.5, 1.0) - 1.0) > 1e-12:
        raise ValueError("DEPENDENCE_VALIDATION_AR1_VARIANCE_DRIFT")
    if abs(ar1_effective_sample_size(2, 0.5) - (4.0 / 3.0)) > 1e-12:
        raise ValueError("DEPENDENCE_VALIDATION_AR1_SIZE_DRIFT")
    if abs(overlapping_mean_variance(2, 2, 1.0) - 0.375) > 1e-12:
        raise ValueError("DEPENDENCE_VALIDATION_OVERLAP_VARIANCE_DRIFT")
    if abs(sum(_LONG_MEMORY_GAMMAS[0:1]) - 1.0) > 1e-12:
        raise ValueError("DEPENDENCE_VALIDATION_LONG_MEMORY_DRIFT")
    try:
        recover_event_ids_from_event_fingerprint("ab" * 32)
    except ValueError as exc:
        if "EVENT_EVIDENCE_EVENT_FINGERPRINT_RECOVERY_REFUSED" not in str(exc):
            raise
    else:
        raise ValueError("DEPENDENCE_VALIDATION_EVENT_FINGERPRINT_RECOVERY")
    if any(value for _key, value in _AUTHORIZATION_FLAGS):
        raise ValueError("DEPENDENCE_VALIDATION_AUTHORIZATION_DRIFT")


_assert_frozen_boundaries()
