"""Cross-year comparison of validated annual pattern-catalogue records.

Governing method: annual pattern catalogue discovery under DEC-469 / DEC-268.
This module is the cross-year comparison stage. It is not a new pattern type,
not Strategy V1, and not a significance test.

It joins caller-supplied annual records that already carry DEC-470 canonical
identities. It does not mine patterns, read market artifacts, or change the
frozen gate.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from statistics import median as _median

from .annual_pattern_catalogue_method import (
    GOVERNING_RESEARCH_METHOD,
    collection_segments,
)
from .annual_pattern_catalogue_miner import (
    ANNUAL_CATALOGUE_MINER_DECISION,
    AnnualPatternRecord,
    AnnualPatternStatistics,
)
from .annual_pattern_catalogue_protocol import (
    ANNUAL_CATALOGUE_PROTOCOL_DECISION,
    ANNUAL_CATALOGUE_PROTOCOL_VERSION,
    ANNUAL_SEGMENT_COUNT,
    DISCOVERY_SLIPPAGE_PIPS,
    EVIDENCE_LABEL,
    EXPERIMENT_ID,
    MAX_CROSS_YEAR_SHORTLIST_GLOBAL,
    MAX_CROSS_YEAR_SHORTLIST_PER_CELL_FAMILY,
    MAX_SIGN_FLIPS,
    MIN_ANNUAL_EVALUABLE_SUPPORT,
    MIN_BASE_POSITIVE_FRACTION,
    MIN_CROSS_YEAR_EVALUABLE_SEGMENTS,
    MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5,
    MIN_POOLED_MEAN_NET_PIPS_0P5,
    MIN_STRESS_POSITIVE_FRACTION,
    NEAR_DUPLICATE_JACCARD,
    SOURCE_METHOD_DECISION,
    STRESS_SLIPPAGE_PIPS,
    PatternDefinition,
    annual_record_identity,
    canonical_pattern_fingerprint,
    cross_year_gate_passes,
    enumerate_pattern_definitions,
    protocol_fingerprint,
    protocol_payload,
)


CROSS_YEAR_ENGINE_VERSION = "fmp-annual-pattern-catalogue-cross-year-v1"
GATE_INOPERABLE_LT_9_SEGMENTS = "GATE_INOPERABLE_LT_9_SEGMENTS"
NULL_CALIBRATION_SEED = 20261118

# Harness-only round-trip spread. It is not a measured Dukascopy spread.
# Charged once, inside the synthetic annual nets, and never again by the join.
_HARNESS_SPREAD_ROUND_TRIP_PIPS = 0.8
_HARNESS_NULL_PATTERN_COUNT = 48
_HARNESS_PLANTED_PATTERN_COUNT = 24
_HARNESS_SIGN_REVERSAL_COUNT = 16
_HARNESS_LOW_SUPPORT_COUNT = 16
_HARNESS_EIGHT_SEGMENT_COUNT = 12
_HARNESS_CORRELATION = 0.8

_REUSED = (
    "canonical_pattern_fingerprint",
    "annual_record_identity",
    "cross_year_gate_passes",
    "collection_segments",
    "protocol_fingerprint",
    "protocol_payload",
    "PatternDefinition",
    "AnnualPatternStatistics",
    "DISCOVERY_SLIPPAGE_PIPS",
    "STRESS_SLIPPAGE_PIPS",
    "MIN_ANNUAL_EVALUABLE_SUPPORT",
    "NEAR_DUPLICATE_JACCARD",
    "MAX_CROSS_YEAR_SHORTLIST_PER_CELL_FAMILY",
    "MAX_CROSS_YEAR_SHORTLIST_GLOBAL",
)

_RANK_FIELDS = (
    "base_positive_fraction_desc",
    "stress_positive_fraction_desc",
    "worst_evaluable_annual_mean_net_pips_0p5_desc",
    "median_annual_mean_net_pips_0p5_desc",
    "pooled_mean_net_pips_0p5_desc",
    "pooled_mean_net_pips_1p0_desc",
    "total_support_desc",
    "canonical_pattern_fingerprint_asc",
)


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


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _require_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        parsed = int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    if parsed < 0:
        raise ValueError(f"{field} must be hexadecimal")
    return value.lower()


def _require_commit(value: object) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError("code_commit must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("code_commit must be hexadecimal") from exc
    return value.lower()


def _frozen_cross_year_contract() -> Mapping[str, object]:
    comparison = protocol_payload()["cross_year_comparison"]
    if not isinstance(comparison, Mapping):
        raise ValueError("cross-year contract payload malformed")
    expected = {
        "minimum_evaluable_segments": MIN_CROSS_YEAR_EVALUABLE_SEGMENTS,
        "minimum_base_positive_fraction": MIN_BASE_POSITIVE_FRACTION,
        "minimum_stress_positive_fraction": MIN_STRESS_POSITIVE_FRACTION,
        "minimum_median_annual_mean_net_pips_0p5": (
            MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5
        ),
        "minimum_pooled_mean_net_pips_0p5": MIN_POOLED_MEAN_NET_PIPS_0P5,
        "maximum_sign_flips": MAX_SIGN_FLIPS,
        "near_duplicate_jaccard": NEAR_DUPLICATE_JACCARD,
        "maximum_shortlist_per_cell_family": (
            MAX_CROSS_YEAR_SHORTLIST_PER_CELL_FAMILY
        ),
        "maximum_shortlist_global": MAX_CROSS_YEAR_SHORTLIST_GLOBAL,
    }
    for field, expected_value in expected.items():
        if comparison.get(field) != expected_value:
            raise ValueError(f"cross-year contract drift: {field}")
    if tuple(comparison.get("rank_fields", ())) != _RANK_FIELDS:
        raise ValueError("cross-year rank-field contract drift")
    if MIN_CROSS_YEAR_EVALUABLE_SEGMENTS != 9:
        raise ValueError("cross-year minimum evaluable segments drifted from 9")
    if ANNUAL_SEGMENT_COUNT != 12:
        raise ValueError("annual segment count drift")
    return comparison


@dataclass(frozen=True, slots=True)
class AnnualSegmentProvenance:
    """Provenance for one annual catalogue segment.

    Source commits may differ across segments. DEC-472 requires one commit
    inside a single full-collection aggregate. This join is not that aggregate.
    Each segment still has to name the frozen DEC-470 protocol.
    """

    annual_segment_label: str
    protocol_version: str
    protocol_fingerprint: str
    code_commit: str
    evidence_fingerprint: str
    miner_decision: str = ANNUAL_CATALOGUE_MINER_DECISION
    evidence_label: str = EVIDENCE_LABEL

    def __post_init__(self) -> None:
        object.__setattr__(self, "code_commit", _require_commit(self.code_commit))
        object.__setattr__(
            self,
            "evidence_fingerprint",
            _require_sha256(
                self.evidence_fingerprint,
                field="evidence fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "protocol_fingerprint",
            _require_sha256(
                self.protocol_fingerprint,
                field="protocol fingerprint",
            ),
        )


@dataclass(frozen=True, slots=True)
class ValidatedAnnualPatternSubmission:
    provenance: AnnualSegmentProvenance
    records: tuple[AnnualPatternRecord, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "records", tuple(self.records))


def synthetic_annual_record(
    *,
    pattern: PatternDefinition,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    direction: str,
    annual_segment_label: str,
    support: int,
    mean_net_pips_0p5: float | None,
    mean_net_pips_1p0: float | None,
    median_net_pips_0p5: float | None = None,
    median_net_pips_1p0: float | None = None,
    win_rate_0p5: float | None = None,
    event_token: str | None = None,
) -> AnnualPatternRecord:
    """Build one identity-consistent annual record for synthetic checks.

    The event token is hashed and stored. It is not an event-id set, so it
    cannot support a Jaccard calculation.
    """

    fingerprint = canonical_pattern_fingerprint(
        pattern=pattern,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        direction=direction,
    )
    if support < 0:
        raise ValueError("synthetic annual support cannot be negative")
    if support == 0:
        statistics = AnnualPatternStatistics(
            support=0,
            evaluable=False,
            mean_net_pips_0p5=None,
            median_net_pips_0p5=None,
            win_rate_0p5=None,
            mean_net_pips_1p0=None,
            median_net_pips_1p0=None,
        )
    else:
        if mean_net_pips_0p5 is None or mean_net_pips_1p0 is None:
            raise ValueError("synthetic supported record requires both cost means")
        if median_net_pips_0p5 is None:
            median_net_pips_0p5 = mean_net_pips_0p5
        if median_net_pips_1p0 is None:
            median_net_pips_1p0 = mean_net_pips_1p0
        if win_rate_0p5 is None:
            win_rate_0p5 = 0.6 if mean_net_pips_0p5 > 0.0 else 0.4
        statistics = AnnualPatternStatistics(
            support=support,
            evaluable=support >= MIN_ANNUAL_EVALUABLE_SUPPORT,
            mean_net_pips_0p5=float(mean_net_pips_0p5),
            median_net_pips_0p5=float(median_net_pips_0p5),
            win_rate_0p5=float(win_rate_0p5),
            mean_net_pips_1p0=float(mean_net_pips_1p0),
            median_net_pips_1p0=float(median_net_pips_1p0),
        )
    if event_token is None:
        event_token = (
            f"{annual_segment_label}|{fingerprint}|support:{support}"
        )
    return AnnualPatternRecord(
        annual_record_id=annual_record_identity(
            canonical_pattern_fingerprint_value=fingerprint,
            annual_segment_label=annual_segment_label,
        ),
        canonical_pattern_fingerprint=fingerprint,
        annual_segment_label=annual_segment_label,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        direction=direction,
        family=pattern.family,
        dimensions=pattern.dimensions,
        states=pattern.states,
        lag_minutes=pattern.lag_minutes,
        event_fingerprint=hashlib.sha256(event_token.encode("utf-8")).hexdigest(),
        statistics=statistics,
    )


def synthetic_segment_provenance(
    annual_segment_label: str,
    *,
    code_commit: str,
    evidence_fingerprint: str | None = None,
) -> AnnualSegmentProvenance:
    if evidence_fingerprint is None:
        evidence_fingerprint = hashlib.sha256(
            f"synthetic-evidence:{annual_segment_label}:{code_commit}".encode(
                "utf-8"
            )
        ).hexdigest()
    return AnnualSegmentProvenance(
        annual_segment_label=annual_segment_label,
        protocol_version=ANNUAL_CATALOGUE_PROTOCOL_VERSION,
        protocol_fingerprint=protocol_fingerprint(),
        code_commit=code_commit,
        evidence_fingerprint=evidence_fingerprint,
        miner_decision=ANNUAL_CATALOGUE_MINER_DECISION,
        evidence_label=EVIDENCE_LABEL,
    )


def submissions_for_records(
    records: Sequence[AnnualPatternRecord],
    *,
    code_commit_for_segment: Mapping[str, str] | None = None,
) -> tuple[ValidatedAnnualPatternSubmission, ...]:
    """Bundle records by annual segment.

    Default commits differ by segment on purpose. The join accepts that.
    """

    labels = [segment.label for segment in collection_segments()]
    default_commits = {
        label: format(index + 1, "040x") for index, label in enumerate(labels)
    }
    commits = dict(default_commits)
    if code_commit_for_segment is not None:
        commits.update(code_commit_for_segment)
    grouped: dict[str, list[AnnualPatternRecord]] = {}
    for record in records:
        grouped.setdefault(record.annual_segment_label, []).append(record)
    submissions: list[ValidatedAnnualPatternSubmission] = []
    for label in labels:
        rows = grouped.get(label)
        if not rows:
            continue
        submissions.append(
            ValidatedAnnualPatternSubmission(
                provenance=synthetic_segment_provenance(
                    label,
                    code_commit=commits[label],
                ),
                records=tuple(rows),
            )
        )
    return tuple(submissions)


def _validate_provenance(
    provenance: AnnualSegmentProvenance,
    *,
    expected_fingerprint: str,
    allowed_labels: set[str],
) -> None:
    if not isinstance(provenance, AnnualSegmentProvenance):
        raise ValueError("annual segment provenance type mismatch")
    if provenance.annual_segment_label not in allowed_labels:
        raise ValueError("annual segment label drift")
    if (
        provenance.protocol_version != ANNUAL_CATALOGUE_PROTOCOL_VERSION
        or provenance.protocol_fingerprint != expected_fingerprint
    ):
        raise ValueError("incompatible annual catalogue protocol")
    if (
        provenance.miner_decision != ANNUAL_CATALOGUE_MINER_DECISION
        or provenance.evidence_label != EVIDENCE_LABEL
    ):
        raise ValueError("incompatible annual catalogue provenance")


def _validate_record(record: AnnualPatternRecord, *, segment_label: str) -> None:
    if not isinstance(record, AnnualPatternRecord):
        raise ValueError("annual pattern record type mismatch")
    if record.annual_segment_label != segment_label:
        raise ValueError("annual pattern record segment mismatch")
    if not isinstance(record.statistics, AnnualPatternStatistics):
        raise ValueError("annual pattern statistics type mismatch")
    pattern = PatternDefinition(
        family=record.family,
        dimensions=tuple(record.dimensions),
        states=tuple(record.states),
        lag_minutes=record.lag_minutes,
    )
    expected_fingerprint = canonical_pattern_fingerprint(
        pattern=pattern,
        symbol=record.symbol,
        timeframe=record.timeframe,
        horizon_minutes=record.horizon_minutes,
        direction=record.direction,
    )
    if record.canonical_pattern_fingerprint != expected_fingerprint:
        raise ValueError("canonical pattern fingerprint mismatch")
    expected_id = annual_record_identity(
        canonical_pattern_fingerprint_value=expected_fingerprint,
        annual_segment_label=segment_label,
    )
    if record.annual_record_id != expected_id:
        raise ValueError("annual record identity mismatch")
    _require_sha256(record.event_fingerprint, field="event fingerprint")


def _identity(record: AnnualPatternRecord) -> tuple[object, ...]:
    return (
        record.symbol,
        record.timeframe,
        record.horizon_minutes,
        record.direction,
        record.family,
        tuple(record.dimensions),
        tuple(record.states),
        record.lag_minutes,
    )


def _sign_class(mean_net_pips: float) -> str:
    if mean_net_pips > 0.0:
        return "POSITIVE"
    return "NON_POSITIVE"


def _sign_flips(classes: Sequence[str]) -> int:
    flips = 0
    for previous, current in zip(classes, classes[1:]):
        if previous != current:
            flips += 1
    return flips


def _support_weighted_mean(pairs: Sequence[tuple[int, float]]) -> float | None:
    if not pairs:
        return None
    weight = 0
    products: list[float] = []
    for support, mean in pairs:
        weight += support
        products.append(support * mean)
    if weight <= 0:
        return None
    return math.fsum(products) / weight


def _concentration(
    pairs: Sequence[tuple[int, float, str]],
) -> dict[str, object]:
    if not pairs:
        return {
            "support_concentration_max_year_share": None,
            "support_concentration_max_year": None,
            "support_hhi": None,
            "absolute_effect_concentration_max_year_share": None,
            "absolute_effect_concentration_max_year": None,
        }
    total_support = sum(support for support, _, _ in pairs)
    shares = [support / total_support for support, _, _ in pairs]
    max_support = max(support for support, _, _ in pairs)
    max_support_year = min(
        (label for support, _, label in pairs if support == max_support),
    )
    contributions = [abs(support * mean) for support, mean, _ in pairs]
    total_effect = math.fsum(contributions)
    if total_effect == 0.0:
        effect_share = None
        effect_year = None
    else:
        max_effect = max(contributions)
        effect_share = max_effect / total_effect
        effect_year = min(
            label
            for (_, _, label), contribution in zip(pairs, contributions)
            if contribution == max_effect
        )
    return {
        "support_concentration_max_year_share": max_support / total_support,
        "support_concentration_max_year": max_support_year,
        "support_hhi": math.fsum(share * share for share in shares),
        "absolute_effect_concentration_max_year_share": effect_share,
        "absolute_effect_concentration_max_year": effect_year,
    }


def _panel_row(
    *,
    label: str,
    record: AnnualPatternRecord | None,
    supplied: bool,
    provenance: AnnualSegmentProvenance | None,
) -> dict[str, object]:
    if record is None:
        status = "MISSING_RECORD" if supplied else "SEGMENT_NOT_SUPPLIED"
        return {
            "annual_segment_label": label,
            "present": False,
            "evidence_status": status,
            "annual_record_id": None,
            "event_fingerprint": None,
            "support": None,
            "evaluable": False,
            "mean_net_pips_0p5": None,
            "median_net_pips_0p5": None,
            "win_rate_0p5": None,
            "mean_net_pips_1p0": None,
            "median_net_pips_1p0": None,
            "direction_class": None,
            "code_commit": provenance.code_commit if provenance else None,
            "evidence_fingerprint": (
                provenance.evidence_fingerprint if provenance else None
            ),
        }
    stats = record.statistics
    if stats.support == 0:
        status = "ZERO_SUPPORT"
        direction_class = None
    elif stats.evaluable:
        status = "EVALUABLE"
        assert stats.mean_net_pips_0p5 is not None
        direction_class = _sign_class(stats.mean_net_pips_0p5)
    else:
        status = "INSUFFICIENT_SUPPORT"
        direction_class = None
    assert provenance is not None
    return {
        "annual_segment_label": label,
        "present": True,
        "evidence_status": status,
        "annual_record_id": record.annual_record_id,
        "event_fingerprint": record.event_fingerprint,
        "support": stats.support,
        "evaluable": stats.evaluable,
        "mean_net_pips_0p5": stats.mean_net_pips_0p5,
        "median_net_pips_0p5": stats.median_net_pips_0p5,
        "win_rate_0p5": stats.win_rate_0p5,
        "mean_net_pips_1p0": stats.mean_net_pips_1p0,
        "median_net_pips_1p0": stats.median_net_pips_1p0,
        "direction_class": direction_class,
        "code_commit": provenance.code_commit,
        "evidence_fingerprint": provenance.evidence_fingerprint,
    }


def _summarize_pattern(
    pattern_rows: Sequence[tuple[str, AnnualPatternRecord | None]],
    supplied_labels: set[str],
    provenance_by_label: Mapping[str, AnnualSegmentProvenance],
) -> dict[str, object]:
    present = [
        (label, record)
        for label, record in pattern_rows
        if record is not None
    ]
    if not present:
        raise ValueError("cross-year pattern has no annual records")
    identity = _identity(present[0][1])
    for _, record in present[1:]:
        if _identity(record) != identity:
            raise ValueError("canonical pattern identity conflict")
    anchor = present[0][1]
    panel = [
        _panel_row(
            label=label,
            record=record,
            supplied=label in supplied_labels,
            provenance=provenance_by_label.get(label),
        )
        for label, record in pattern_rows
    ]
    evaluable_pairs: list[tuple[int, float, float, str]] = []
    sign_classes: list[str] = []
    sign_labels: list[str] = []
    failure_years: list[str] = []
    total_support = 0
    for row in panel:
        support = row["support"]
        if isinstance(support, int):
            total_support += support
        if row["evidence_status"] != "EVALUABLE":
            continue
        mean_base = row["mean_net_pips_0p5"]
        mean_stress = row["mean_net_pips_1p0"]
        assert isinstance(support, int)
        assert isinstance(mean_base, float)
        assert isinstance(mean_stress, float)
        label = str(row["annual_segment_label"])
        evaluable_pairs.append((support, mean_base, mean_stress, label))
        sign_class = _sign_class(mean_base)
        sign_classes.append(sign_class)
        sign_labels.append(label)
        if sign_class == "NON_POSITIVE":
            failure_years.append(label)

    evaluable_segments = len(evaluable_pairs)
    base_positive = sum(mean > 0.0 for _, mean, _, _ in evaluable_pairs)
    stress_positive = sum(mean > 0.0 for _, _, mean, _ in evaluable_pairs)
    base_values = [mean for _, mean, _, _ in evaluable_pairs]
    median_base = float(_median(base_values)) if base_values else None
    pooled_base = _support_weighted_mean(
        [(support, mean) for support, mean, _, _ in evaluable_pairs]
    )
    pooled_stress = _support_weighted_mean(
        [(support, mean) for support, _, mean, _ in evaluable_pairs]
    )
    if evaluable_pairs:
        worst_mean, worst_label = min(
            ((mean, label) for _, mean, _, label in evaluable_pairs),
        )
    else:
        worst_mean = None
        worst_label = None
    concentration = _concentration(
        [
            (support, mean, label)
            for support, mean, _, label in evaluable_pairs
        ]
    )
    undefined = median_base is None or pooled_base is None or pooled_stress is None
    gate_inputs = {
        "evaluable_segments": evaluable_segments,
        "base_positive_segments": base_positive,
        "stress_positive_segments": stress_positive,
        "median_annual_mean_net_pips_0p5": (
            0.0 if median_base is None else median_base
        ),
        "pooled_mean_net_pips_0p5": 0.0 if pooled_base is None else pooled_base,
        "pooled_mean_net_pips_1p0": (
            0.0 if pooled_stress is None else pooled_stress
        ),
        "sign_flips": _sign_flips(sign_classes),
    }
    gate_passes = cross_year_gate_passes(**gate_inputs)
    if evaluable_segments < MIN_CROSS_YEAR_EVALUABLE_SEGMENTS:
        if gate_passes:
            raise RuntimeError(
                "frozen cross-year gate accepted fewer than 9 evaluable segments"
            )
        gate_status = GATE_INOPERABLE_LT_9_SEGMENTS
    elif gate_passes:
        gate_status = "PASS"
    else:
        gate_status = "FAIL"
    if pooled_base is None:
        effect_label = "NOT_EVALUABLE"
    elif pooled_base < 0.0:
        effect_label = "NEGATIVE"
    elif pooled_base > 0.0:
        effect_label = "POSITIVE_DESCRIPTIVE"
    else:
        effect_label = "ZERO"
    base_fraction = (
        None
        if evaluable_segments == 0
        else base_positive / evaluable_segments
    )
    stress_fraction = (
        None
        if evaluable_segments == 0
        else stress_positive / evaluable_segments
    )
    total_evaluable_support = sum(support for support, _, _, _ in evaluable_pairs)
    gap = None
    if pooled_base is not None and pooled_stress is not None:
        gap = pooled_base - pooled_stress
    return {
        "canonical_pattern_fingerprint": anchor.canonical_pattern_fingerprint,
        "annual_record_ids": [
            row["annual_record_id"] for row in panel if row["present"]
        ],
        "symbol": anchor.symbol,
        "timeframe": anchor.timeframe,
        "horizon_minutes": anchor.horizon_minutes,
        "direction": anchor.direction,
        "family": anchor.family,
        "dimensions": list(anchor.dimensions),
        "states": list(anchor.states),
        "lag_minutes": anchor.lag_minutes,
        "panel": panel,
        "summary": {
            "segments_present": len(present),
            "segments_missing": ANNUAL_SEGMENT_COUNT - len(present),
            "recurrence_present": len(present),
            "recurrence_evaluable": evaluable_segments,
            "evaluable_segments": evaluable_segments,
            "insufficient_support_segments": sum(
                row["evidence_status"] == "INSUFFICIENT_SUPPORT" for row in panel
            ),
            "zero_support_segments": sum(
                row["evidence_status"] == "ZERO_SUPPORT" for row in panel
            ),
            "segment_not_supplied": sum(
                row["evidence_status"] == "SEGMENT_NOT_SUPPLIED" for row in panel
            ),
            "missing_record_segments": sum(
                row["evidence_status"] == "MISSING_RECORD" for row in panel
            ),
            "base_positive_segments": base_positive,
            "stress_positive_segments": stress_positive,
            "base_positive_fraction": base_fraction,
            "stress_positive_fraction": stress_fraction,
            "median_annual_mean_net_pips_0p5": median_base,
            "pooled_mean_net_pips_0p5": pooled_base,
            "pooled_mean_net_pips_1p0": pooled_stress,
            "pooled_mean_role": "DESCRIPTIVE_SUPPORT_WEIGHTED_MEAN",
            "pooled_mean_uses_evaluable_segments_only": True,
            "independent_trial_estimate": False,
            "worst_evaluable_annual_mean_net_pips_0p5": worst_mean,
            "worst_evaluable_annual_segment": worst_label,
            "sign_flips": gate_inputs["sign_flips"],
            "sign_sequence": sign_classes,
            "sign_sequence_segments": sign_labels,
            "sign_rule": (
                "POSITIVE if evaluable mean_net_pips_0p5 > 0, otherwise "
                "NON_POSITIVE. Missing and non-evaluable years are omitted. "
                "A flip is a change between consecutive evaluable years."
            ),
            "failure_years": failure_years,
            "total_support": total_support,
            "total_evaluable_support": total_evaluable_support,
            **concentration,
            "cost_sensitivity": {
                "base_slippage_pips_per_fill": DISCOVERY_SLIPPAGE_PIPS,
                "stress_slippage_pips_per_fill": STRESS_SLIPPAGE_PIPS,
                "spread_basis": (
                    "historical bid/ask spread is already inside annual net pips"
                ),
                "additional_spread_pips": 0.0,
                "spread_double_charged": False,
                "engine_recomputes_prices": False,
                "pooled_mean_net_pips_0p5": pooled_base,
                "pooled_mean_net_pips_1p0": pooled_stress,
                "observed_base_minus_stress_pips": gap,
                "observed_gap_is_not_an_additional_charge": True,
            },
            "effect_label": effect_label,
            "gate_status": gate_status,
            "gate_passes": gate_passes,
            "gate_pass_is_statistical_significance": False,
            "gate_inputs": gate_inputs,
            "undefined_descriptive_means_encoded_as_zero": undefined,
            "p_value": None,
            "shortlist_status": "NOT_ELIGIBLE",
            "shortlist_rank": None,
            "gate_pass_rank": None,
        },
    }


def _rank_value(field: str, pattern: Mapping[str, object]) -> object:
    summary = pattern["summary"]
    assert isinstance(summary, Mapping)
    if field == "canonical_pattern_fingerprint_asc":
        return pattern["canonical_pattern_fingerprint"]
    mapping = {
        "base_positive_fraction_desc": "base_positive_fraction",
        "stress_positive_fraction_desc": "stress_positive_fraction",
        "worst_evaluable_annual_mean_net_pips_0p5_desc": (
            "worst_evaluable_annual_mean_net_pips_0p5"
        ),
        "median_annual_mean_net_pips_0p5_desc": (
            "median_annual_mean_net_pips_0p5"
        ),
        "pooled_mean_net_pips_0p5_desc": "pooled_mean_net_pips_0p5",
        "pooled_mean_net_pips_1p0_desc": "pooled_mean_net_pips_1p0",
        "total_support_desc": "total_support",
    }
    value = summary[mapping[field]]
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"rank field {field} is undefined for a gate pass")
    return -float(value)


def _apply_shortlist(patterns: list[dict[str, object]]) -> tuple[list[str], list[str]]:
    contract = _frozen_cross_year_contract()
    per_family_limit = int(contract["maximum_shortlist_per_cell_family"])
    global_limit = int(contract["maximum_shortlist_global"])
    passers = [
        pattern
        for pattern in patterns
        if pattern["summary"]["gate_passes"] is True
    ]
    ranked = sorted(
        passers,
        key=lambda pattern: tuple(
            _rank_value(field, pattern) for field in _RANK_FIELDS
        ),
    )
    family_counts: dict[tuple[object, ...], int] = {}
    shortlist: list[str] = []
    capped: list[str] = []
    for rank, pattern in enumerate(ranked, start=1):
        summary = pattern["summary"]
        summary["gate_pass_rank"] = rank
        fingerprint = str(pattern["canonical_pattern_fingerprint"])
        bucket = (
            pattern["symbol"],
            pattern["timeframe"],
            pattern["horizon_minutes"],
            pattern["family"],
        )
        if (
            family_counts.get(bucket, 0) >= per_family_limit
            or len(shortlist) >= global_limit
        ):
            summary["shortlist_status"] = "CAPPED"
            capped.append(fingerprint)
            continue
        family_counts[bucket] = family_counts.get(bucket, 0) + 1
        summary["shortlist_status"] = "SHORTLISTED"
        summary["shortlist_rank"] = len(shortlist) + 1
        shortlist.append(fingerprint)
    return shortlist, capped


def _cost_model() -> dict[str, object]:
    return {
        "base_slippage_pips_per_fill": DISCOVERY_SLIPPAGE_PIPS,
        "stress_slippage_pips_per_fill": STRESS_SLIPPAGE_PIPS,
        "slippage_application": (
            "already_applied_inside_annual_mean_net_pips_0p5_and_mean_net_pips_1p0"
        ),
        "spread_basis": "historical_bid_ask_already_inside_annual_net_pips",
        "additional_spread_pips": 0.0,
        "spread_double_charged": False,
        "commission": "zero_in_source_outcome_labels",
        "financing": "zero_in_source_outcome_labels",
        "engine_recomputes_prices": False,
        "source": (
            "DEC-470 DISCOVERY_SLIPPAGE_PIPS and STRESS_SLIPPAGE_PIPS; "
            "annual records already store both nets"
        ),
    }


def _near_duplicate_block() -> dict[str, object]:
    return {
        "threshold": NEAR_DUPLICATE_JACCARD,
        "scope": "same_cell_family_direction",
        "status": "UNAVAILABLE",
        "applied": False,
        "substitute": None,
        "patterns_removed": 0,
        "reason": (
            "Annual records store an event_fingerprint hash, not the event-id "
            "set. Jaccard similarity cannot be computed from that hash. No "
            "substitute similarity is applied, and no pattern is dropped as a "
            "near duplicate."
        ),
    }


def _statistical_block() -> dict[str, object]:
    return {
        "p_values": "UNAVAILABLE_NOT_COMPUTED",
        "independent_trial_standard_errors": "UNAVAILABLE_NOT_COMPUTED",
        "multiple_comparison_adjustment": "UNAVAILABLE_NOT_COMPUTED",
        "statistical_significance_claimed": False,
        "reason": (
            "Events inside a year overlap in time and are serially dependent. "
            "A support-weighted mean is a descriptive average. It is not an "
            "independent-trial estimate and it is not a p-value."
        ),
    }


def _authorizations() -> dict[str, bool]:
    payload = protocol_payload()["authorizations"]
    if not isinstance(payload, Mapping):
        raise ValueError("protocol authorization payload malformed")
    copied = {str(key): bool(value) for key, value in payload.items()}
    if any(copied.values()):
        raise ValueError("cross-year engine cannot run with an open authorization")
    return copied


def compare_cross_year_patterns(
    submissions: Sequence[ValidatedAnnualPatternSubmission],
) -> dict[str, object]:
    """Join validated annual records and score the frozen cross-year gate.

    Every supplied pattern is retained, including negative, failed, and
    inoperable ones. A passing gate is not a significance claim.
    """

    if not isinstance(submissions, Sequence) or isinstance(submissions, (str, bytes)):
        raise ValueError("cross-year submissions must be a sequence")
    if len(submissions) == 0:
        raise ValueError("cross-year comparison requires at least one annual segment")
    contract = _frozen_cross_year_contract()
    expected_fingerprint = protocol_fingerprint()
    segments = collection_segments()
    allowed = {segment.label for segment in segments}
    by_label: dict[str, ValidatedAnnualPatternSubmission] = {}
    for submission in submissions:
        if not isinstance(submission, ValidatedAnnualPatternSubmission):
            raise ValueError("annual submission type mismatch")
        provenance = submission.provenance
        _validate_provenance(
            provenance,
            expected_fingerprint=expected_fingerprint,
            allowed_labels=allowed,
        )
        label = provenance.annual_segment_label
        if label in by_label:
            raise ValueError("duplicate annual segment submission")
        seen_fingerprints: dict[str, AnnualPatternRecord] = {}
        seen_ids: set[str] = set()
        for record in submission.records:
            _validate_record(record, segment_label=label)
            fingerprint = record.canonical_pattern_fingerprint
            if fingerprint in seen_fingerprints or record.annual_record_id in seen_ids:
                raise ValueError("duplicate annual pattern record")
            seen_fingerprints[fingerprint] = record
            seen_ids.add(record.annual_record_id)
        by_label[label] = submission

    provenance_by_label = {
        label: submission.provenance for label, submission in by_label.items()
    }
    records_by_label: dict[str, dict[str, AnnualPatternRecord]] = {}
    for label, submission in by_label.items():
        records_by_label[label] = {
            record.canonical_pattern_fingerprint: record
            for record in submission.records
        }
    fingerprints = sorted(
        {
            fingerprint
            for rows in records_by_label.values()
            for fingerprint in rows
        }
    )
    patterns: list[dict[str, object]] = []
    for fingerprint in fingerprints:
        rows = [
            (segment.label, records_by_label.get(segment.label, {}).get(fingerprint))
            for segment in segments
        ]
        patterns.append(
            _summarize_pattern(
                rows,
                set(by_label),
                provenance_by_label,
            )
        )
    shortlist, capped = _apply_shortlist(patterns)
    gate_pass_count = sum(
        pattern["summary"]["gate_status"] == "PASS" for pattern in patterns
    )
    gate_fail_count = sum(
        pattern["summary"]["gate_status"] == "FAIL" for pattern in patterns
    )
    gate_inoperable_count = sum(
        pattern["summary"]["gate_status"] == GATE_INOPERABLE_LT_9_SEGMENTS
        for pattern in patterns
    )
    negative_count = sum(
        pattern["summary"]["effect_label"] == "NEGATIVE" for pattern in patterns
    )
    commits = [item.code_commit for item in provenance_by_label.values()]
    supplied = []
    for segment in segments:
        submission = by_label.get(segment.label)
        if submission is None:
            continue
        supplied.append(
            {
                "annual_segment_label": segment.label,
                "code_commit": submission.provenance.code_commit,
                "evidence_fingerprint": submission.provenance.evidence_fingerprint,
                "protocol_version": submission.provenance.protocol_version,
                "protocol_fingerprint": submission.provenance.protocol_fingerprint,
                "miner_decision": submission.provenance.miner_decision,
                "record_count": len(submission.records),
            }
        )
    missing_segments = [
        segment.label for segment in segments if segment.label not in by_label
    ]
    return {
        "engine_version": CROSS_YEAR_ENGINE_VERSION,
        "governing_research_method": GOVERNING_RESEARCH_METHOD,
        "parent_method_decision": SOURCE_METHOD_DECISION,
        "parent_protocol_decision": ANNUAL_CATALOGUE_PROTOCOL_DECISION,
        "experiment_id": EXPERIMENT_ID,
        "protocol_version": ANNUAL_CATALOGUE_PROTOCOL_VERSION,
        "protocol_fingerprint": expected_fingerprint,
        "evidence_basis": "CALLER_SUPPLIED_VALIDATED_ANNUAL_RECORDS",
        "historical_market_artifacts_read": False,
        "identical_source_commit_required": False,
        "distinct_source_commit_count": len(set(commits)),
        "reused": list(_REUSED),
        "rank_fields_applied": list(contract["rank_fields"]),
        "shortlist_limits": {
            "per_cell_family": contract["maximum_shortlist_per_cell_family"],
            "global": contract["maximum_shortlist_global"],
            "cell_family_key": [
                "symbol",
                "timeframe",
                "horizon_minutes",
                "family",
            ],
        },
        "cost_model": _cost_model(),
        "near_duplicate": _near_duplicate_block(),
        "statistical_evidence": _statistical_block(),
        "gate": {
            "function": "cross_year_gate_passes",
            "thresholds_modified": False,
            "minimum_evaluable_segments": MIN_CROSS_YEAR_EVALUABLE_SEGMENTS,
            "status_when_below_minimum": GATE_INOPERABLE_LT_9_SEGMENTS,
            "pass_is_statistical_significance": False,
        },
        "supplied_segments": supplied,
        "missing_segments": missing_segments,
        "pattern_count": len(patterns),
        "patterns": patterns,
        "gate_pass_count": gate_pass_count,
        "gate_fail_count": gate_fail_count,
        "gate_inoperable_count": gate_inoperable_count,
        "negative_effect_count": negative_count,
        "preserved_non_passing_count": len(patterns) - gate_pass_count,
        "shortlist": shortlist,
        "shortlist_count": len(shortlist),
        "capped_fingerprints": capped,
        "patterns_removed_as_near_duplicates": 0,
        "authorizations": _authorizations(),
        "strategy_v1_synthesized": False,
    }


def canonical_cross_year_json(report: Mapping[str, object]) -> bytes:
    return _canonical_json(dict(report))


def cross_year_report_sha256(report: Mapping[str, object]) -> str:
    return _sha256_bytes(canonical_cross_year_json(report))


def render_cross_year_summary(report: Mapping[str, object]) -> str:
    """Concise research summary. The JSON inventory remains the full record."""

    statistical = report["statistical_evidence"]
    near = report["near_duplicate"]
    cost = report["cost_model"]
    assert isinstance(statistical, Mapping)
    assert isinstance(near, Mapping)
    assert isinstance(cost, Mapping)
    lines = [
        "Cross-year pattern comparison",
        f"Engine: {report['engine_version']}",
        f"Method: {report['governing_research_method']}",
        f"Protocol: {report['parent_protocol_decision']} {report['protocol_version']}",
        (
            "Segments supplied: "
            f"{len(report['supplied_segments'])} of {ANNUAL_SEGMENT_COUNT}"
        ),
        f"Patterns retained: {report['pattern_count']}",
        f"Gate pass: {report['gate_pass_count']}",
        f"Gate fail: {report['gate_fail_count']}",
        (
            "Gate inoperable: "
            f"{report['gate_inoperable_count']} {GATE_INOPERABLE_LT_9_SEGMENTS}"
        ),
        f"Negative descriptive pooled effect: {report['negative_effect_count']}",
        f"Preserved non-passing patterns: {report['preserved_non_passing_count']}",
        f"Shortlist: {report['shortlist_count']}",
        (
            "Near-duplicate Jaccard: "
            f"{near['status']}. Removed: {report['patterns_removed_as_near_duplicates']}."
        ),
        f"P-values: {statistical['p_values']}.",
        "A gate pass is not a claim of statistical significance.",
        (
            "Pooled means are descriptive support-weighted statistics. "
            "Overlapping events are not independent trials."
        ),
        (
            "Spread double-charged: "
            f"{cost['spread_double_charged']}. Additional spread pips: "
            f"{cost['additional_spread_pips']}."
        ),
        f"Historical market artifacts read: {report['historical_market_artifacts_read']}.",
        f"Strategy V1 synthesized: {report['strategy_v1_synthesized']}.",
    ]
    patterns = report["patterns"]
    assert isinstance(patterns, list)
    if len(patterns) <= 12:
        for pattern in patterns:
            assert isinstance(pattern, Mapping)
            summary = pattern["summary"]
            assert isinstance(summary, Mapping)
            lines.append(
                " ".join(
                    (
                        str(pattern["canonical_pattern_fingerprint"])[:12],
                        str(pattern["symbol"]),
                        str(pattern["timeframe"]),
                        str(pattern["horizon_minutes"]),
                        str(pattern["direction"]),
                        str(pattern["family"]),
                        str(summary["gate_status"]),
                        str(summary["effect_label"]),
                        f"evaluable={summary['evaluable_segments']}",
                        f"flips={summary['sign_flips']}",
                    )
                )
            )
    else:
        lines.append(
            f"Pattern lines omitted: {len(patterns)} patterns remain in the JSON inventory."
        )
    return "\n".join(lines) + "\n"


def _segment_labels(count: int | None = None) -> list[str]:
    labels = [segment.label for segment in collection_segments()]
    if count is None:
        return labels
    if count < 1 or count > len(labels):
        raise ValueError("synthetic segment count drift")
    return labels[:count]


def _net_from_gross(gross_pips: float) -> tuple[float, float]:
    base = (
        gross_pips
        - _HARNESS_SPREAD_ROUND_TRIP_PIPS
        - (DISCOVERY_SLIPPAGE_PIPS * 2.0)
    )
    stress = (
        gross_pips
        - _HARNESS_SPREAD_ROUND_TRIP_PIPS
        - (STRESS_SLIPPAGE_PIPS * 2.0)
    )
    return base, stress


def _standard_normal(rng: random.Random) -> float:
    draw = rng.random()
    while draw <= 0.0:
        draw = rng.random()
    angle = rng.random()
    return math.sqrt(-2.0 * math.log(draw)) * math.cos(math.tau * angle)


def _records_from_gross(
    gross_by_pattern: Sequence[Sequence[float | None]],
    *,
    labels: Sequence[str],
    support: int,
    definition_offset: int = 0,
) -> list[AnnualPatternRecord]:
    definitions = enumerate_pattern_definitions()
    records: list[AnnualPatternRecord] = []
    for index, yearly in enumerate(gross_by_pattern):
        if len(yearly) != len(labels):
            raise ValueError("synthetic gross path length drift")
        pattern = definitions[definition_offset + index]
        for label, gross in zip(labels, yearly):
            if gross is None:
                continue
            base, stress = _net_from_gross(float(gross))
            records.append(
                synthetic_annual_record(
                    pattern=pattern,
                    symbol="EURUSD",
                    timeframe="5m",
                    horizon_minutes=60,
                    direction="LONG",
                    annual_segment_label=label,
                    support=support,
                    mean_net_pips_0p5=base,
                    mean_net_pips_1p0=stress,
                )
            )
    return records


def _constant_paths(
    pattern_count: int,
    *,
    years: int,
    gross: float,
) -> list[list[float]]:
    return [[gross for _ in range(years)] for _ in range(pattern_count)]


def _independent_paths(
    pattern_count: int,
    *,
    years: int,
    mean: float,
    sigma: float,
    seed: int,
) -> list[list[float]]:
    rng = random.Random(seed)
    paths: list[list[float]] = []
    for _ in range(pattern_count):
        year_values = []
        for _year in range(years):
            year_values.append(mean + sigma * _standard_normal(rng))
        paths.append(year_values)
    return paths


def _correlated_paths(
    pattern_count: int,
    *,
    years: int,
    mean: float,
    sigma: float,
    correlation: float,
    seed: int,
) -> list[list[float]]:
    if not 0.0 <= correlation <= 1.0:
        raise ValueError("synthetic correlation must be inside [0, 1]")
    rng = random.Random(seed)
    shared_weight = math.sqrt(correlation)
    idiosyncratic_weight = math.sqrt(1.0 - correlation)
    paths = [[0.0 for _ in range(years)] for _ in range(pattern_count)]
    for year in range(years):
        common = _standard_normal(rng)
        for index in range(pattern_count):
            idiosyncratic = _standard_normal(rng)
            shock = (
                shared_weight * common + idiosyncratic_weight * idiosyncratic
            )
            paths[index][year] = mean + sigma * shock
    return paths


def _alternating_paths(pattern_count: int, *, years: int) -> list[list[float]]:
    path = [4.0 if index % 2 == 0 else -1.0 for index in range(years)]
    return [list(path) for _ in range(pattern_count)]


def _scenario_from_records(
    name: str,
    records: Sequence[AnnualPatternRecord],
    *,
    kind: str,
    assumptions: str,
) -> dict[str, object]:
    report = compare_cross_year_patterns(submissions_for_records(records))
    passes = 0
    fails = 0
    inoperable = 0
    for pattern in report["patterns"]:
        status = pattern["summary"]["gate_status"]
        if pattern["summary"]["gate_passes"] is True:
            passes += 1
        if status == "FAIL":
            fails += 1
        elif status == GATE_INOPERABLE_LT_9_SEGMENTS:
            inoperable += 1
        elif status != "PASS":
            raise ValueError(f"unexpected gate status {status}")
    pattern_count = int(report["pattern_count"])
    unexpected_pass = kind in {
        "null",
        "negative_after_cost",
        "sign_reversal",
        "low_support",
        "eight_segment",
    }
    false_passes = passes if unexpected_pass else 0
    recovered = passes if kind == "planted" else None
    recovery_rate = None if recovered is None else recovered / pattern_count
    return {
        "name": name,
        "kind": kind,
        "assumptions": assumptions,
        "pattern_count": pattern_count,
        "gate_pass_count": passes,
        "gate_fail_count": fails,
        "gate_inoperable_count": inoperable,
        "false_pass_count": false_passes,
        "planted_recovered": recovered,
        "planted_recovery_rate": recovery_rate,
        "spread_double_charged": report["cost_model"]["spread_double_charged"],
        "statistical_significance_claimed": report["statistical_evidence"][
            "statistical_significance_claimed"
        ],
        "near_duplicate_status": report["near_duplicate"]["status"],
        "report_sha256": cross_year_report_sha256(report),
    }


def run_synthetic_null_calibration(
    *,
    seed: int = NULL_CALIBRATION_SEED,
) -> dict[str, object]:
    """Seeded synthetic calibration of the frozen gate.

    The gate thresholds are read and then left unchanged. Counts are
    descriptive results of this design. They are not a reason to edit DEC-470.
    """

    contract = _frozen_cross_year_contract()
    labels = _segment_labels()
    eight = _segment_labels(8)
    years = len(labels)
    offset = 0

    def take(count: int) -> int:
        nonlocal offset
        start = offset
        offset += count
        if offset > len(enumerate_pattern_definitions()):
            raise ValueError("synthetic calibration exceeded the frozen grammar")
        return start

    scenarios: list[dict[str, object]] = []

    def add(
        name: str,
        paths: Sequence[Sequence[float | None]],
        *,
        kind: str,
        assumptions: str,
        support: int = 100,
        segment_labels: Sequence[str] | None = None,
    ) -> None:
        chosen = labels if segment_labels is None else segment_labels
        start = take(len(paths))
        records = _records_from_gross(
            paths,
            labels=chosen,
            support=support,
            definition_offset=start,
        )
        scenarios.append(
            _scenario_from_records(
                name,
                records,
                kind=kind,
                assumptions=assumptions,
            )
        )

    cost_text = (
        f"gross pips minus one {_HARNESS_SPREAD_ROUND_TRIP_PIPS}-pip round-trip "
        f"spread and slippage of {DISCOVERY_SLIPPAGE_PIPS}*2 or "
        f"{STRESS_SLIPPAGE_PIPS}*2. The comparison engine does not subtract "
        "spread or slippage again."
    )
    add(
        "zero_gross_no_noise",
        _constant_paths(_HARNESS_NULL_PATTERN_COUNT, years=years, gross=0.0),
        kind="null",
        assumptions=f"Gross edge is 0 in every year. {cost_text}",
    )
    add(
        "positive_gross_negative_after_cost",
        _constant_paths(_HARNESS_NULL_PATTERN_COUNT, years=years, gross=0.4),
        kind="negative_after_cost",
        assumptions=(
            "Gross edge is +0.4 pips, which remains negative after the "
            f"stated spread and base slippage. {cost_text}"
        ),
    )
    for sigma in (0.25, 1.0, 3.0):
        add(
            f"independent_zero_gross_sigma_{sigma}",
            _independent_paths(
                _HARNESS_NULL_PATTERN_COUNT,
                years=years,
                mean=0.0,
                sigma=sigma,
                seed=seed + int(sigma * 100),
            ),
            kind="null",
            assumptions=(
                "Independent N(0, sigma^2) gross shocks across pattern-years. "
                f"sigma={sigma}. {cost_text}"
            ),
        )
    for sigma in (1.0, 3.0):
        add(
            f"correlated_zero_gross_sigma_{sigma}",
            _correlated_paths(
                _HARNESS_NULL_PATTERN_COUNT,
                years=years,
                mean=0.0,
                sigma=sigma,
                correlation=_HARNESS_CORRELATION,
                seed=seed + 1000 + int(sigma * 100),
            ),
            kind="null",
            assumptions=(
                f"Shared yearly factor with correlation {_HARNESS_CORRELATION} "
                f"across patterns. sigma={sigma}. Years are otherwise separate. "
                f"{cost_text}"
            ),
        )
    add(
        "strong_planted_no_noise",
        _constant_paths(_HARNESS_PLANTED_PATTERN_COUNT, years=years, gross=4.0),
        kind="planted",
        assumptions=(
            "Constant gross edge of 4.0 pips. After one spread and base "
            f"slippage the net is positive, and the stress net stays positive. {cost_text}"
        ),
    )
    add(
        "strong_planted_sigma_0_25",
        _independent_paths(
            _HARNESS_PLANTED_PATTERN_COUNT,
            years=years,
            mean=4.0,
            sigma=0.25,
            seed=seed + 400,
        ),
        kind="planted",
        assumptions=(
            "Gross edge N(4.0, 0.25^2), independent across pattern-years. "
            f"{cost_text}"
        ),
    )
    add(
        "sign_reversals",
        _alternating_paths(_HARNESS_SIGN_REVERSAL_COUNT, years=years),
        kind="sign_reversal",
        assumptions=(
            "Gross edge alternates +4.0 and -1.0 by year. This is a negative "
            f"control for sign reversals, not a recovery target. {cost_text}"
        ),
    )
    add(
        "low_support",
        _constant_paths(_HARNESS_LOW_SUPPORT_COUNT, years=years, gross=4.0),
        kind="low_support",
        assumptions=(
            f"Support is 40, below {MIN_ANNUAL_EVALUABLE_SUPPORT}. Large means "
            "remain non-evaluable. The nine-segment rule is not relaxed."
        ),
        support=40,
    )
    add(
        "eight_segment_planted",
        _constant_paths(_HARNESS_EIGHT_SEGMENT_COUNT, years=len(eight), gross=4.0),
        kind="eight_segment",
        assumptions=(
            "Strong planted effect on the first eight annual segments only. "
            "The frozen gate needs nine evaluable segments."
        ),
        segment_labels=eight,
    )

    false_pass_total = sum(
        int(row["false_pass_count"])
        for row in scenarios
        if row["kind"] in {"null", "negative_after_cost"}
    )
    null_patterns = sum(
        int(row["pattern_count"])
        for row in scenarios
        if row["kind"] in {"null", "negative_after_cost"}
    )
    planted = [
        row for row in scenarios if row["kind"] == "planted"
    ]
    planted_patterns = sum(int(row["pattern_count"]) for row in planted)
    planted_recovered = sum(int(row["planted_recovered"]) for row in planted)
    return {
        "harness": "synthetic-cross-year-null-calibration-v1",
        "seed": seed,
        "generator": "random.Random plus Box-Muller",
        "market_artifacts_read": False,
        "gate_thresholds_modified_after_simulation": False,
        "statistical_significance_claimed": False,
        "gate_constants": {
            "minimum_evaluable_segments": contract["minimum_evaluable_segments"],
            "minimum_base_positive_fraction": contract[
                "minimum_base_positive_fraction"
            ],
            "minimum_stress_positive_fraction": contract[
                "minimum_stress_positive_fraction"
            ],
            "minimum_median_annual_mean_net_pips_0p5": contract[
                "minimum_median_annual_mean_net_pips_0p5"
            ],
            "minimum_pooled_mean_net_pips_0p5": contract[
                "minimum_pooled_mean_net_pips_0p5"
            ],
            "maximum_sign_flips": contract["maximum_sign_flips"],
        },
        "cost_assumptions": {
            "spread_round_trip_pips": _HARNESS_SPREAD_ROUND_TRIP_PIPS,
            "spread_charged_once": True,
            "base_slippage_pips_per_fill": DISCOVERY_SLIPPAGE_PIPS,
            "stress_slippage_pips_per_fill": STRESS_SLIPPAGE_PIPS,
            "base_slippage_round_trip_pips": DISCOVERY_SLIPPAGE_PIPS * 2.0,
            "stress_slippage_round_trip_pips": STRESS_SLIPPAGE_PIPS * 2.0,
            "formula": (
                "mean_net_pips_0p5 = gross - spread_round_trip - "
                "base_slippage_round_trip; mean_net_pips_1p0 = gross - "
                "spread_round_trip - stress_slippage_round_trip"
            ),
            "spread_is_measured_from_history": False,
        },
        "dependence_assumptions": {
            "within_year_event_overlap": (
                "not simulated; each year is one annual mean"
            ),
            "pooled_mean_interpretation": (
                "descriptive support-weighted mean of annual means"
            ),
            "independent_pattern_scenarios": (
                "pattern-year shocks are independent"
            ),
            "correlated_pattern_scenarios": (
                f"correlation {_HARNESS_CORRELATION} within a year across patterns"
            ),
        },
        "scenarios": scenarios,
        "null_and_negative_pattern_count": null_patterns,
        "null_and_negative_false_pass_count": false_pass_total,
        "strong_planted_pattern_count": planted_patterns,
        "strong_planted_recovered": planted_recovered,
        "strong_planted_recovery_rate": (
            None
            if planted_patterns == 0
            else planted_recovered / planted_patterns
        ),
        "note": (
            "False passes count gate passes under zero-gross or "
            "negative-after-cost designs. Planted recovery counts gate passes "
            "under the strong positive design. Neither count is a p-value, and "
            "neither count was used to change the gate."
        ),
    }


def synthetic_cross_year_records() -> tuple[AnnualPatternRecord, ...]:
    """Fixed records behind ``build_synthetic_cross_year_report``."""

    definitions = enumerate_pattern_definitions()
    labels = _segment_labels()
    records: list[AnnualPatternRecord] = []

    def add(
        index: int,
        chosen: Sequence[str],
        *,
        support: int | Sequence[int],
        base: float | Sequence[float],
        stress: float | Sequence[float],
    ) -> None:
        pattern = definitions[index]
        for position, label in enumerate(chosen):
            support_value = support if isinstance(support, int) else support[position]
            base_value = base if isinstance(base, float) else base[position]
            stress_value = stress if isinstance(stress, float) else stress[position]
            records.append(
                synthetic_annual_record(
                    pattern=pattern,
                    symbol="EURUSD",
                    timeframe="5m",
                    horizon_minutes=60,
                    direction="LONG",
                    annual_segment_label=label,
                    support=support_value,
                    mean_net_pips_0p5=base_value,
                    mean_net_pips_1p0=stress_value,
                )
            )

    add(0, labels[:9], support=100, base=0.5, stress=0.25)
    add(1, labels[:8], support=100, base=0.5, stress=0.25)
    add(2, labels, support=100, base=-0.5, stress=-1.5)
    sign_base: list[float] = []
    sign_stress: list[float] = []
    for index in range(12):
        if index in {2, 7}:
            sign_base.append(-0.25)
            sign_stress.append(-0.125)
        else:
            sign_base.append(0.5)
            sign_stress.append(0.25)
    add(3, labels, support=100, base=sign_base, stress=sign_stress)
    add(4, labels, support=40, base=2.0, stress=1.0)
    add(
        5,
        labels[:3],
        support=[100, 200, 300],
        base=[1.0, 2.0, 3.0],
        stress=[0.0, 1.0, 2.0],
    )
    add(6, labels[:1], support=0, base=0.0, stress=0.0)
    return tuple(records)


def build_synthetic_cross_year_report() -> dict[str, object]:
    """Fixed synthetic catalogue used to inspect the join by hand.

    One pattern clears the frozen gate. The others are negative, sign-reversing,
    low-support, short, or absent. All of them stay in the report.
    """

    return compare_cross_year_patterns(
        submissions_for_records(synthetic_cross_year_records())
    )


__all__ = [
    "CROSS_YEAR_ENGINE_VERSION",
    "GATE_INOPERABLE_LT_9_SEGMENTS",
    "NULL_CALIBRATION_SEED",
    "AnnualSegmentProvenance",
    "ValidatedAnnualPatternSubmission",
    "build_synthetic_cross_year_report",
    "synthetic_cross_year_records",
    "canonical_cross_year_json",
    "compare_cross_year_patterns",
    "cross_year_report_sha256",
    "render_cross_year_summary",
    "run_synthetic_null_calibration",
    "submissions_for_records",
    "synthetic_annual_record",
    "synthetic_segment_provenance",
]
