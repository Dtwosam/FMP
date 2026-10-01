from __future__ import annotations

import hashlib
import json
import math
from typing import Mapping, Sequence

from fmp.market_learning.evidence import EXPECTED_SOURCE_MANIFEST_SHA256

from .exp064_continuous_stability_miner import (
    ContinuousStabilityHypothesis,
    FeatureRankCalibration,
    InMemoryContinuousStabilityResult,
)
from .exp064_continuous_stability_protocol import (
    CONTINUOUS_FEATURES,
    DESIGN_YEARS,
    DIRECTIONS,
    HORIZONS_MINUTES,
    MAX_FROZEN_GLOBAL,
    MAX_FROZEN_PER_CELL_HORIZON,
    MAX_SHORTLIST_GLOBAL,
    MAX_SHORTLIST_PER_CELL_HORIZON,
    OUTPUT_KIND,
    POLARITIES,
    SYMBOLS,
    TIMEFRAMES,
    AnnualContinuousEffectStat,
    continuous_stability_gate_passes,
    continuous_stability_metrics,
    effect_hypothesis_fingerprint,
    protocol_fingerprint,
)
from .exp064_research_direction import SUCCESSOR_EXPERIMENT_ID


EXP064_EVIDENCE_CONTRACT_DECISION = "DEC-454"
EXP064_CELL_EVIDENCE_VERSION = 1
EXP064_CELL_EVIDENCE_PROTOCOL = (
    "fmp-exp064-continuous-stability-cell-evidence-v1"
)
EXP064_AGGREGATE_EVIDENCE_VERSION = 1
EXP064_AGGREGATE_EVIDENCE_PROTOCOL = (
    "fmp-exp064-continuous-stability-aggregate-evidence-v1"
)

DEC453_MERGE_SHA = "bda820585a568cefca52487d4aefad77be109387"
DEC453_MINER_BLOB_SHA = "b0d799ec1afaf43b0441290c97a9f39c37ecd2fd"
DEC452_PROTOCOL_BLOB_SHA = "c108ea047c7bfb3e588bfbac33993180066c28ad"

EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"

SOURCE_ACCESS_AUTHORIZED = False
HISTORICAL_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False

EXPECTED_CELLS = tuple(
    (symbol, timeframe, horizon)
    for symbol in SYMBOLS
    for timeframe in TIMEFRAMES
    for horizon in HORIZONS_MINUTES
)
EXPECTED_CELL_COUNT = 18


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


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def _validate_commit(value: object, *, field: str = "code_commit") -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def _finite_float(value: object, *, field: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise ValueError(f"{field} must be finite")
    return float(value)


def _nonnegative_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _positive_int(value: object, *, field: str) -> int:
    result = _nonnegative_int(value, field=field)
    if result <= 0:
        raise ValueError(f"{field} must be positive")
    return result


def _calibration_payload(
    value: FeatureRankCalibration,
) -> dict[str, object]:
    distinct_count = len(set(value.values))
    return {
        "feature_name": value.feature_name,
        "value_count": len(value.values),
        "distinct_value_count": distinct_count,
        "minimum": value.values[0],
        "maximum": value.values[-1],
        "values_sha256": _sha256_bytes(_canonical_json(list(value.values))),
    }


def _annual_stat_payload(
    value: AnnualContinuousEffectStat,
) -> dict[str, object]:
    return {
        "year": value.year,
        "evaluable_support": value.evaluable_support,
        "selected_tail_support": value.selected_tail_support,
        "signed_rank_slope_net_pips_0p5": (
            value.signed_rank_slope_net_pips_0p5
        ),
        "selected_tail_mean_net_pips_0p5": (
            value.selected_tail_mean_net_pips_0p5
        ),
        "selected_tail_mean_net_pips_1p0": (
            value.selected_tail_mean_net_pips_1p0
        ),
    }


def _hypothesis_payload(
    value: ContinuousStabilityHypothesis,
) -> dict[str, object]:
    return {
        "symbol": value.symbol,
        "timeframe": value.timeframe,
        "horizon_minutes": value.horizon_minutes,
        "feature_name": value.feature_name,
        "direction": value.direction,
        "polarity": value.polarity,
        "fingerprint": value.fingerprint,
        "annual_stats": [
            _annual_stat_payload(item) for item in value.annual_stats
        ],
        "total_selected_tail_support": value.total_selected_tail_support,
        "minimum_year_selected_tail_support": (
            value.minimum_year_selected_tail_support
        ),
        "positive_slope_year_count": value.positive_slope_year_count,
        "positive_tail_mean_year_count": (
            value.positive_tail_mean_year_count
        ),
        "equal_year_signed_rank_slope_net_pips_0p5": (
            value.equal_year_signed_rank_slope_net_pips_0p5
        ),
        "lower_half_annual_signed_rank_slope_net_pips_0p5": (
            value.lower_half_annual_signed_rank_slope_net_pips_0p5
        ),
        "equal_year_selected_tail_mean_net_pips_0p5": (
            value.equal_year_selected_tail_mean_net_pips_0p5
        ),
        "equal_year_selected_tail_mean_net_pips_1p0": (
            value.equal_year_selected_tail_mean_net_pips_1p0
        ),
        "lower_half_annual_selected_tail_mean_net_pips_0p5": (
            value.lower_half_annual_selected_tail_mean_net_pips_0p5
        ),
        "two_year_block_signed_rank_slope_net_pips_0p5": [
            [name, metric]
            for name, metric in (
                value.two_year_block_signed_rank_slope_net_pips_0p5
            )
        ],
        "minimum_two_year_block_signed_rank_slope_net_pips_0p5": (
            value.minimum_two_year_block_signed_rank_slope_net_pips_0p5
        ),
        "two_year_block_selected_tail_mean_net_pips_0p5": [
            [name, metric]
            for name, metric in (
                value.two_year_block_selected_tail_mean_net_pips_0p5
            )
        ],
        "minimum_two_year_block_selected_tail_mean_net_pips_0p5": (
            value.minimum_two_year_block_selected_tail_mean_net_pips_0p5
        ),
    }


def compile_cell_evidence(
    result: InMemoryContinuousStabilityResult,
    *,
    code_commit: str,
    processed_manifest_sha256: str,
    feature_manifest_sha256: str,
    outcome_manifest_sha256: str,
    feature_evidence_fingerprint: str,
    outcome_evidence_fingerprint: str,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    for field, raw in (
        ("processed_manifest_sha256", processed_manifest_sha256),
        ("feature_manifest_sha256", feature_manifest_sha256),
        ("outcome_manifest_sha256", outcome_manifest_sha256),
        ("feature_evidence_fingerprint", feature_evidence_fingerprint),
        ("outcome_evidence_fingerprint", outcome_evidence_fingerprint),
    ):
        _validate_sha256(raw, field=field)

    report = result.report
    identity = (report.symbol, report.timeframe, report.horizon_minutes)
    if identity not in EXPECTED_CELLS:
        raise ValueError("DEC-454 result cell identity mismatch")

    calibration_names = tuple(item.feature_name for item in result.calibrations)
    if calibration_names != report.active_continuous_features:
        raise ValueError("DEC-454 calibration/report feature identity mismatch")
    if len(calibration_names) != len(set(calibration_names)):
        raise ValueError("DEC-454 calibration feature identity duplicated")

    evidence: dict[str, object] = {
        "evidence_version": EXP064_CELL_EVIDENCE_VERSION,
        "evidence_protocol": EXP064_CELL_EVIDENCE_PROTOCOL,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": "DEC-453",
        "miner_source_blob_sha": DEC453_MINER_BLOB_SHA,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "code_commit": code_commit,
        "processed_manifest_sha256": processed_manifest_sha256,
        "feature_manifest_sha256": feature_manifest_sha256,
        "outcome_manifest_sha256": outcome_manifest_sha256,
        "feature_evidence_fingerprint": feature_evidence_fingerprint,
        "outcome_evidence_fingerprint": outcome_evidence_fingerprint,
        "cell": {
            "symbol": report.symbol,
            "timeframe": report.timeframe,
            "horizon_minutes": report.horizon_minutes,
        },
        "rank_calibrations": [
            _calibration_payload(item) for item in result.calibrations
        ],
        "continuous_stability": {
            "active_continuous_features": list(
                report.active_continuous_features
            ),
            "hypothesis_count": report.hypothesis_count,
            "evaluable_hypothesis_count": report.evaluable_hypothesis_count,
            "qualifying_hypothesis_count": report.qualifying_hypothesis_count,
            "deduplicated_hypothesis_count": (
                report.deduplicated_hypothesis_count
            ),
            "shortlist": [
                _hypothesis_payload(item) for item in report.shortlist
            ],
            "frozen_hypothesis_fingerprints": [
                item.fingerprint for item in report.frozen
            ],
            "output_kind": report.output_kind,
        },
        "reserved_robustness_opened": False,
        "source_access_authorized": SOURCE_ACCESS_AUTHORIZED,
        "historical_execution_authorized": HISTORICAL_EXECUTION_AUTHORIZED,
        "historical_result_authorized": HISTORICAL_RESULT_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": (
            CANDIDATE_COMPILATION_AUTHORIZED
        ),
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }
    evidence["evidence_fingerprint"] = _sha256_bytes(
        _canonical_json(evidence)
    )
    validate_cell_evidence(evidence)
    return evidence


def _validate_annual_stats(
    value: object,
) -> tuple[AnnualContinuousEffectStat, ...]:
    if not isinstance(value, list) or len(value) != len(DESIGN_YEARS):
        raise ValueError("DEC-454 annual stats must cover exactly 2015-2022")
    out: list[AnnualContinuousEffectStat] = []
    for raw, year in zip(value, DESIGN_YEARS):
        if not isinstance(raw, Mapping) or raw.get("year") != year:
            raise ValueError("DEC-454 annual stat year identity mismatch")
        out.append(
            AnnualContinuousEffectStat(
                year=year,
                evaluable_support=_positive_int(
                    raw.get("evaluable_support"),
                    field=f"DEC-454 {year} evaluable support",
                ),
                selected_tail_support=_positive_int(
                    raw.get("selected_tail_support"),
                    field=f"DEC-454 {year} selected-tail support",
                ),
                signed_rank_slope_net_pips_0p5=_finite_float(
                    raw.get("signed_rank_slope_net_pips_0p5"),
                    field=f"DEC-454 {year} signed rank slope",
                ),
                selected_tail_mean_net_pips_0p5=_finite_float(
                    raw.get("selected_tail_mean_net_pips_0p5"),
                    field=f"DEC-454 {year} selected-tail 0.5-pip mean",
                ),
                selected_tail_mean_net_pips_1p0=_finite_float(
                    raw.get("selected_tail_mean_net_pips_1p0"),
                    field=f"DEC-454 {year} selected-tail 1.0-pip mean",
                ),
            )
        )
    return tuple(out)


def _validate_calibrations(
    value: object,
    *,
    active_features: list[object],
) -> None:
    if not isinstance(value, list):
        raise ValueError("DEC-454 rank calibrations must be a list")
    if len(value) != len(active_features):
        raise ValueError("DEC-454 rank calibration count mismatch")

    names: list[str] = []
    for raw in value:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-454 rank calibration malformed")
        feature_name = raw.get("feature_name")
        if feature_name not in CONTINUOUS_FEATURES:
            raise ValueError("DEC-454 rank calibration feature mismatch")
        names.append(str(feature_name))
        count = _positive_int(
            raw.get("value_count"),
            field="DEC-454 rank calibration value count",
        )
        distinct = _positive_int(
            raw.get("distinct_value_count"),
            field="DEC-454 rank calibration distinct count",
        )
        if count < 600:
            raise ValueError("DEC-454 rank calibration row count below protocol")
        if distinct < 20 or distinct > count:
            raise ValueError(
                "DEC-454 rank calibration distinct count outside protocol"
            )
        minimum = _finite_float(
            raw.get("minimum"),
            field="DEC-454 rank calibration minimum",
        )
        maximum = _finite_float(
            raw.get("maximum"),
            field="DEC-454 rank calibration maximum",
        )
        if minimum > maximum:
            raise ValueError("DEC-454 rank calibration range invalid")
        _validate_sha256(
            raw.get("values_sha256"),
            field="DEC-454 rank calibration values fingerprint",
        )

    if names != active_features:
        raise ValueError("DEC-454 rank calibration feature order mismatch")
    if len(names) != len(set(names)):
        raise ValueError("DEC-454 rank calibration feature duplicated")


def _validate_hypothesis(
    raw: object,
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> tuple[str, tuple[object, ...]]:
    if not isinstance(raw, Mapping):
        raise ValueError("DEC-454 shortlist row must be an object")
    if (
        raw.get("symbol") != symbol
        or raw.get("timeframe") != timeframe
        or raw.get("horizon_minutes") != horizon_minutes
    ):
        raise ValueError("DEC-454 shortlist cell identity mismatch")

    feature_name = raw.get("feature_name")
    direction = raw.get("direction")
    polarity = raw.get("polarity")
    if feature_name not in CONTINUOUS_FEATURES:
        raise ValueError("DEC-454 shortlist feature mismatch")
    if direction not in DIRECTIONS:
        raise ValueError("DEC-454 shortlist direction mismatch")
    if polarity not in POLARITIES:
        raise ValueError("DEC-454 shortlist polarity mismatch")

    expected_fingerprint = effect_hypothesis_fingerprint(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        feature_name=str(feature_name),
        direction=str(direction),
        polarity=str(polarity),
    )
    if raw.get("fingerprint") != expected_fingerprint:
        raise ValueError("DEC-454 shortlist fingerprint mismatch")

    annual_stats = _validate_annual_stats(raw.get("annual_stats"))
    if not continuous_stability_gate_passes(annual_stats):
        raise ValueError(
            "DEC-454 shortlist hypothesis fails continuous-stability gate"
        )
    metrics = continuous_stability_metrics(annual_stats)

    expected_values = {
        "total_selected_tail_support": int(
            metrics["total_selected_tail_support"]
        ),
        "minimum_year_selected_tail_support": int(
            metrics["minimum_year_selected_tail_support"]
        ),
        "positive_slope_year_count": int(
            metrics["positive_slope_year_count"]
        ),
        "positive_tail_mean_year_count": int(
            metrics["positive_tail_mean_year_count"]
        ),
        "equal_year_signed_rank_slope_net_pips_0p5": float(
            metrics["equal_year_signed_rank_slope_net_pips_0p5"]
        ),
        "lower_half_annual_signed_rank_slope_net_pips_0p5": float(
            metrics[
                "lower_half_annual_signed_rank_slope_net_pips_0p5"
            ]
        ),
        "equal_year_selected_tail_mean_net_pips_0p5": float(
            metrics["equal_year_selected_tail_mean_net_pips_0p5"]
        ),
        "equal_year_selected_tail_mean_net_pips_1p0": float(
            metrics["equal_year_selected_tail_mean_net_pips_1p0"]
        ),
        "lower_half_annual_selected_tail_mean_net_pips_0p5": float(
            metrics[
                "lower_half_annual_selected_tail_mean_net_pips_0p5"
            ]
        ),
        "minimum_two_year_block_signed_rank_slope_net_pips_0p5": float(
            metrics[
                "minimum_two_year_block_signed_rank_slope_net_pips_0p5"
            ]
        ),
        "minimum_two_year_block_selected_tail_mean_net_pips_0p5": float(
            metrics[
                "minimum_two_year_block_selected_tail_mean_net_pips_0p5"
            ]
        ),
    }
    for field, expected in expected_values.items():
        if raw.get(field) != expected:
            raise ValueError(f"DEC-454 shortlist {field} mismatch")

    slope_blocks = metrics[
        "two_year_block_signed_rank_slope_net_pips_0p5"
    ]
    tail_blocks = metrics[
        "two_year_block_selected_tail_mean_net_pips_0p5"
    ]
    if not isinstance(slope_blocks, dict) or not isinstance(tail_blocks, dict):
        raise ValueError("DEC-454 two-year block metric malformed")
    if raw.get("two_year_block_signed_rank_slope_net_pips_0p5") != [
        [name, float(metric)] for name, metric in slope_blocks.items()
    ]:
        raise ValueError("DEC-454 signed-slope block metric mismatch")
    if raw.get("two_year_block_selected_tail_mean_net_pips_0p5") != [
        [name, float(metric)] for name, metric in tail_blocks.items()
    ]:
        raise ValueError("DEC-454 selected-tail block metric mismatch")

    rank_key: tuple[object, ...] = (
        -expected_values[
            "lower_half_annual_selected_tail_mean_net_pips_0p5"
        ],
        -expected_values[
            "minimum_two_year_block_selected_tail_mean_net_pips_0p5"
        ],
        -expected_values[
            "lower_half_annual_signed_rank_slope_net_pips_0p5"
        ],
        -expected_values[
            "minimum_two_year_block_signed_rank_slope_net_pips_0p5"
        ],
        -expected_values["positive_tail_mean_year_count"],
        -expected_values["positive_slope_year_count"],
        -expected_values["equal_year_selected_tail_mean_net_pips_1p0"],
        -expected_values["total_selected_tail_support"],
        str(feature_name),
        str(direction),
        str(polarity),
        expected_fingerprint,
    )
    return expected_fingerprint, rank_key


def _cell_identity(
    value: Mapping[str, object],
) -> tuple[str, str, int]:
    raw = value.get("cell")
    if not isinstance(raw, Mapping):
        raise ValueError("DEC-454 aggregate cell identity missing")
    identity = (
        raw.get("symbol"),
        raw.get("timeframe"),
        raw.get("horizon_minutes"),
    )
    if identity not in EXPECTED_CELLS:
        raise ValueError(f"DEC-454 unexpected cell identity: {identity!r}")
    return str(identity[0]), str(identity[1]), int(identity[2])


def _validate_nested_cell_semantics(
    value: Mapping[str, object],
) -> None:
    symbol, timeframe, horizon = _cell_identity(value)

    section = value.get("continuous_stability")
    if not isinstance(section, Mapping):
        raise ValueError(
            "DEC-454 continuous-stability section must be an object"
        )
    active = section.get("active_continuous_features")
    if not isinstance(active, list):
        raise ValueError("DEC-454 active feature inventory malformed")
    if any(item not in CONTINUOUS_FEATURES for item in active):
        raise ValueError("DEC-454 active feature inventory mismatch")
    if len(active) != len(set(active)):
        raise ValueError("DEC-454 active feature inventory duplicated")

    _validate_calibrations(
        value.get("rank_calibrations"),
        active_features=active,
    )

    if section.get("hypothesis_count") != 80:
        raise ValueError("DEC-454 frozen hypothesis count mismatch")
    evaluable = _nonnegative_int(
        section.get("evaluable_hypothesis_count"),
        field="DEC-454 evaluable hypothesis count",
    )
    qualifying = _nonnegative_int(
        section.get("qualifying_hypothesis_count"),
        field="DEC-454 qualifying hypothesis count",
    )
    deduplicated = _nonnegative_int(
        section.get("deduplicated_hypothesis_count"),
        field="DEC-454 deduplicated hypothesis count",
    )
    if evaluable > len(active) * len(DIRECTIONS) * len(POLARITIES):
        raise ValueError("DEC-454 evaluable count exceeds active search")
    if qualifying > evaluable:
        raise ValueError("DEC-454 qualifying count exceeds evaluable count")
    if deduplicated > qualifying:
        raise ValueError("DEC-454 deduplicated count exceeds qualifying count")

    shortlist = section.get("shortlist")
    if not isinstance(shortlist, list):
        raise ValueError("DEC-454 shortlist must be a list")
    if len(shortlist) > MAX_SHORTLIST_PER_CELL_HORIZON:
        raise ValueError("DEC-454 shortlist exceeds frozen cap")
    if len(shortlist) > deduplicated:
        raise ValueError("DEC-454 shortlist exceeds deduplicated count")

    fingerprints: list[str] = []
    rank_keys: list[tuple[object, ...]] = []
    for raw in shortlist:
        fingerprint, rank_key = _validate_hypothesis(
            raw,
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon,
        )
        fingerprints.append(fingerprint)
        rank_keys.append(rank_key)
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("DEC-454 shortlist fingerprints duplicated")
    if rank_keys != sorted(rank_keys):
        raise ValueError("DEC-454 shortlist rank order mismatch")

    expected_frozen = fingerprints[:MAX_FROZEN_PER_CELL_HORIZON]
    if section.get("frozen_hypothesis_fingerprints") != expected_frozen:
        raise ValueError("DEC-454 frozen fingerprint inventory mismatch")
    if section.get("output_kind") != OUTPUT_KIND:
        raise ValueError("DEC-454 output kind mismatch")


def validate_cell_evidence(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="DEC-454 cell evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-454 cell evidence fingerprint mismatch")

    expected = {
        "evidence_version": EXP064_CELL_EVIDENCE_VERSION,
        "evidence_protocol": EXP064_CELL_EVIDENCE_PROTOCOL,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": "DEC-453",
        "miner_source_blob_sha": DEC453_MINER_BLOB_SHA,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "reserved_robustness_opened": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-454 cell evidence {field} mismatch")

    _validate_commit(value.get("code_commit"))
    for field in (
        "processed_manifest_sha256",
        "feature_manifest_sha256",
        "outcome_manifest_sha256",
        "feature_evidence_fingerprint",
        "outcome_evidence_fingerprint",
    ):
        _validate_sha256(value.get(field), field=field)

    for field in (
        "source_access_authorized",
        "historical_execution_authorized",
        "historical_result_authorized",
        "reserved_robustness_access_authorized",
        "candidate_compilation_authorized",
        "promotion_authorized",
        "phase8b_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"DEC-454 cell evidence {field} must remain false")

    _validate_nested_cell_semantics(value)
    identity = _cell_identity(value)
    if value.get("processed_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256[
        identity[0]
    ]:
        raise ValueError("DEC-454 cell Phase 2 source identity mismatch")
    return value


def compile_aggregate_evidence(
    cell_evidence: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError(
            f"DEC-454 aggregate requires exactly {EXPECTED_CELL_COUNT} cells"
        )

    seen: dict[tuple[str, str, int], Mapping[str, object]] = {}
    source_by_symbol: dict[str, str] = {}
    manifest_pair_by_symbol_timeframe: dict[
        tuple[str, str], tuple[str, str]
    ] = {}
    feature_fingerprints: set[str] = set()
    outcome_fingerprints: set[str] = set()
    summaries: list[dict[str, object]] = []

    for raw in cell_evidence:
        validated = validate_cell_evidence(raw)
        if validated.get("code_commit") != code_commit:
            raise ValueError("DEC-454 aggregate cell code commit mismatch")
        identity = _cell_identity(validated)
        if identity in seen:
            raise ValueError(f"DEC-454 duplicate cell: {identity!r}")
        seen[identity] = validated
        symbol, timeframe, horizon = identity

        processed = _validate_sha256(
            validated.get("processed_manifest_sha256"),
            field="processed_manifest_sha256",
        )
        if processed != EXPECTED_SOURCE_MANIFEST_SHA256[symbol]:
            raise ValueError("DEC-454 Phase 2 source identity mismatch")
        prior_processed = source_by_symbol.setdefault(symbol, processed)
        if prior_processed != processed:
            raise ValueError("DEC-454 symbol source identity drift")

        feature_manifest = _validate_sha256(
            validated.get("feature_manifest_sha256"),
            field="feature_manifest_sha256",
        )
        outcome_manifest = _validate_sha256(
            validated.get("outcome_manifest_sha256"),
            field="outcome_manifest_sha256",
        )
        pair_key = (symbol, timeframe)
        pair = (feature_manifest, outcome_manifest)
        prior_pair = manifest_pair_by_symbol_timeframe.setdefault(
            pair_key,
            pair,
        )
        if prior_pair != pair:
            raise ValueError(
                "DEC-454 manifest identity differs across horizons"
            )

        feature_fingerprints.add(
            _validate_sha256(
                validated.get("feature_evidence_fingerprint"),
                field="feature_evidence_fingerprint",
            )
        )
        outcome_fingerprints.add(
            _validate_sha256(
                validated.get("outcome_evidence_fingerprint"),
                field="outcome_evidence_fingerprint",
            )
        )

        section = validated.get("continuous_stability")
        if not isinstance(section, Mapping):
            raise ValueError("DEC-454 cell section missing")
        shortlist = section.get("shortlist")
        frozen = section.get("frozen_hypothesis_fingerprints")
        if not isinstance(shortlist, list) or not isinstance(frozen, list):
            raise ValueError("DEC-454 cell shortlist inventory malformed")

        summaries.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "horizon_minutes": horizon,
                "processed_manifest_sha256": processed,
                "feature_manifest_sha256": feature_manifest,
                "outcome_manifest_sha256": outcome_manifest,
                "feature_evidence_fingerprint": validated.get(
                    "feature_evidence_fingerprint"
                ),
                "outcome_evidence_fingerprint": validated.get(
                    "outcome_evidence_fingerprint"
                ),
                "cell_evidence_fingerprint": validated.get(
                    "evidence_fingerprint"
                ),
                "active_continuous_features": list(
                    section.get("active_continuous_features", [])
                ),
                "hypothesis_count": section.get("hypothesis_count"),
                "evaluable_hypothesis_count": section.get(
                    "evaluable_hypothesis_count"
                ),
                "qualifying_hypothesis_count": section.get(
                    "qualifying_hypothesis_count"
                ),
                "deduplicated_hypothesis_count": section.get(
                    "deduplicated_hypothesis_count"
                ),
                "continuous_stability_shortlist_count": len(shortlist),
                "continuous_stability_frozen_count": len(frozen),
                "continuous_stability_shortlist_fingerprints": [
                    item.get("fingerprint")
                    for item in shortlist
                    if isinstance(item, Mapping)
                ],
                "continuous_stability_frozen_fingerprints": list(frozen),
                "output_kind": section.get("output_kind"),
            }
        )

    if set(seen) != set(EXPECTED_CELLS):
        raise ValueError("DEC-454 aggregate cell inventory mismatch")
    if len(feature_fingerprints) != 1 or len(outcome_fingerprints) != 1:
        raise ValueError("DEC-454 aggregate upstream evidence identity mismatch")

    summaries.sort(
        key=lambda row: (
            str(row["symbol"]),
            str(row["timeframe"]),
            int(row["horizon_minutes"]),
        )
    )
    shortlist_count = sum(
        int(row["continuous_stability_shortlist_count"])
        for row in summaries
    )
    frozen_count = sum(
        int(row["continuous_stability_frozen_count"])
        for row in summaries
    )

    evidence: dict[str, object] = {
        "evidence_version": EXP064_AGGREGATE_EVIDENCE_VERSION,
        "evidence_protocol": EXP064_AGGREGATE_EVIDENCE_PROTOCOL,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": "DEC-453",
        "miner_source_blob_sha": DEC453_MINER_BLOB_SHA,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "code_commit": code_commit,
        "feature_evidence_fingerprint": next(iter(feature_fingerprints)),
        "outcome_evidence_fingerprint": next(iter(outcome_fingerprints)),
        "expected_cell_count": EXPECTED_CELL_COUNT,
        "verified_cell_count": EXPECTED_CELL_COUNT,
        "continuous_stability_shortlist_count": shortlist_count,
        "continuous_stability_frozen_count": frozen_count,
        "cells": summaries,
        "output_kind": OUTPUT_KIND,
        "reserved_robustness_opened": False,
        "source_access_authorized": SOURCE_ACCESS_AUTHORIZED,
        "historical_execution_authorized": HISTORICAL_EXECUTION_AUTHORIZED,
        "historical_result_authorized": HISTORICAL_RESULT_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": (
            CANDIDATE_COMPILATION_AUTHORIZED
        ),
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }
    evidence["evidence_fingerprint"] = _sha256_bytes(
        _canonical_json(evidence)
    )
    validate_aggregate_evidence(evidence)
    return evidence


def validate_aggregate_evidence(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="DEC-454 aggregate evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-454 aggregate evidence fingerprint mismatch")

    expected = {
        "evidence_version": EXP064_AGGREGATE_EVIDENCE_VERSION,
        "evidence_protocol": EXP064_AGGREGATE_EVIDENCE_PROTOCOL,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": "DEC-453",
        "miner_source_blob_sha": DEC453_MINER_BLOB_SHA,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "expected_cell_count": EXPECTED_CELL_COUNT,
        "verified_cell_count": EXPECTED_CELL_COUNT,
        "output_kind": OUTPUT_KIND,
        "reserved_robustness_opened": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-454 aggregate evidence {field} mismatch")

    _validate_commit(value.get("code_commit"))
    _validate_sha256(
        value.get("feature_evidence_fingerprint"),
        field="feature_evidence_fingerprint",
    )
    _validate_sha256(
        value.get("outcome_evidence_fingerprint"),
        field="outcome_evidence_fingerprint",
    )

    for field in (
        "source_access_authorized",
        "historical_execution_authorized",
        "historical_result_authorized",
        "reserved_robustness_access_authorized",
        "candidate_compilation_authorized",
        "promotion_authorized",
        "phase8b_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-454 aggregate evidence {field} must remain false"
            )

    cells = value.get("cells")
    if not isinstance(cells, list) or len(cells) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-454 aggregate cells inventory mismatch")

    identities: list[tuple[str, str, int]] = []
    cell_fingerprints: list[str] = []
    shortlist_count = 0
    frozen_count = 0
    feature_fingerprints: set[str] = set()
    outcome_fingerprints: set[str] = set()
    manifest_pairs: dict[tuple[str, str], tuple[str, str]] = {}

    for row in cells:
        if not isinstance(row, Mapping):
            raise ValueError("DEC-454 aggregate cell summary malformed")
        identity = (
            row.get("symbol"),
            row.get("timeframe"),
            row.get("horizon_minutes"),
        )
        if identity not in EXPECTED_CELLS:
            raise ValueError("DEC-454 aggregate cell identity mismatch")
        symbol = str(identity[0])
        timeframe = str(identity[1])
        horizon = int(identity[2])
        identities.append((symbol, timeframe, horizon))

        cell_fingerprints.append(
            _validate_sha256(
                row.get("cell_evidence_fingerprint"),
                field="DEC-454 cell evidence fingerprint",
            )
        )
        if row.get("processed_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256[
            symbol
        ]:
            raise ValueError("DEC-454 aggregate Phase 2 source identity mismatch")

        feature_manifest = _validate_sha256(
            row.get("feature_manifest_sha256"),
            field="DEC-454 aggregate feature manifest",
        )
        outcome_manifest = _validate_sha256(
            row.get("outcome_manifest_sha256"),
            field="DEC-454 aggregate outcome manifest",
        )
        key = (symbol, timeframe)
        pair = (feature_manifest, outcome_manifest)
        prior_pair = manifest_pairs.setdefault(key, pair)
        if prior_pair != pair:
            raise ValueError(
                "DEC-454 aggregate manifest identity differs across horizons"
            )

        feature_fingerprints.add(
            _validate_sha256(
                row.get("feature_evidence_fingerprint"),
                field="DEC-454 aggregate feature evidence fingerprint",
            )
        )
        outcome_fingerprints.add(
            _validate_sha256(
                row.get("outcome_evidence_fingerprint"),
                field="DEC-454 aggregate outcome evidence fingerprint",
            )
        )

        active = row.get("active_continuous_features")
        if not isinstance(active, list):
            raise ValueError("DEC-454 aggregate active feature inventory malformed")
        if any(item not in CONTINUOUS_FEATURES for item in active):
            raise ValueError("DEC-454 aggregate active feature mismatch")
        if row.get("hypothesis_count") != 80:
            raise ValueError("DEC-454 aggregate hypothesis count mismatch")

        evaluable = _nonnegative_int(
            row.get("evaluable_hypothesis_count"),
            field="DEC-454 aggregate evaluable count",
        )
        qualifying = _nonnegative_int(
            row.get("qualifying_hypothesis_count"),
            field="DEC-454 aggregate qualifying count",
        )
        deduplicated = _nonnegative_int(
            row.get("deduplicated_hypothesis_count"),
            field="DEC-454 aggregate deduplicated count",
        )
        if qualifying > evaluable or deduplicated > qualifying:
            raise ValueError("DEC-454 aggregate hypothesis counts inconsistent")

        shortlist_fingerprints = row.get(
            "continuous_stability_shortlist_fingerprints"
        )
        frozen_fingerprints = row.get(
            "continuous_stability_frozen_fingerprints"
        )
        if (
            not isinstance(shortlist_fingerprints, list)
            or not isinstance(frozen_fingerprints, list)
        ):
            raise ValueError(
                "DEC-454 aggregate cell fingerprint inventories malformed"
            )
        for item in shortlist_fingerprints + frozen_fingerprints:
            _validate_sha256(item, field="DEC-454 hypothesis fingerprint")
        if len(shortlist_fingerprints) > MAX_SHORTLIST_PER_CELL_HORIZON:
            raise ValueError("DEC-454 aggregate cell shortlist exceeds cap")
        if len(frozen_fingerprints) > MAX_FROZEN_PER_CELL_HORIZON:
            raise ValueError("DEC-454 aggregate cell frozen exceeds cap")
        if frozen_fingerprints != shortlist_fingerprints[
            :MAX_FROZEN_PER_CELL_HORIZON
        ]:
            raise ValueError(
                "DEC-454 aggregate frozen/shortlist identity mismatch"
            )
        if row.get("continuous_stability_shortlist_count") != len(
            shortlist_fingerprints
        ):
            raise ValueError("DEC-454 aggregate shortlist count mismatch")
        if row.get("continuous_stability_frozen_count") != len(
            frozen_fingerprints
        ):
            raise ValueError("DEC-454 aggregate frozen count mismatch")
        if row.get("output_kind") != OUTPUT_KIND:
            raise ValueError("DEC-454 aggregate cell output kind mismatch")

        shortlist_count += len(shortlist_fingerprints)
        frozen_count += len(frozen_fingerprints)

    if tuple(identities) != tuple(sorted(EXPECTED_CELLS)):
        raise ValueError("DEC-454 aggregate cells are not exact/sorted")
    if len(cell_fingerprints) != len(set(cell_fingerprints)):
        raise ValueError(
            "DEC-454 aggregate cell evidence fingerprints duplicated"
        )
    if feature_fingerprints != {value.get("feature_evidence_fingerprint")}:
        raise ValueError("DEC-454 aggregate feature evidence identity mismatch")
    if outcome_fingerprints != {value.get("outcome_evidence_fingerprint")}:
        raise ValueError("DEC-454 aggregate outcome evidence identity mismatch")
    if value.get("continuous_stability_shortlist_count") != shortlist_count:
        raise ValueError("DEC-454 aggregate total shortlist count mismatch")
    if value.get("continuous_stability_frozen_count") != frozen_count:
        raise ValueError("DEC-454 aggregate total frozen count mismatch")
    if shortlist_count > MAX_SHORTLIST_GLOBAL:
        raise ValueError("DEC-454 aggregate shortlist exceeds global cap")
    if frozen_count > MAX_FROZEN_GLOBAL:
        raise ValueError("DEC-454 aggregate frozen count exceeds global cap")
    return value


__all__ = [
    "DEC452_PROTOCOL_BLOB_SHA",
    "DEC453_MERGE_SHA",
    "DEC453_MINER_BLOB_SHA",
    "EXPECTED_CELL_COUNT",
    "EXPECTED_CELLS",
    "EXP064_AGGREGATE_EVIDENCE_PROTOCOL",
    "EXP064_AGGREGATE_EVIDENCE_VERSION",
    "EXP064_CELL_EVIDENCE_PROTOCOL",
    "EXP064_CELL_EVIDENCE_VERSION",
    "EXP064_EVIDENCE_CONTRACT_DECISION",
    "compile_aggregate_evidence",
    "compile_cell_evidence",
    "validate_aggregate_evidence",
    "validate_cell_evidence",
]
