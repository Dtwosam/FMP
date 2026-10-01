from __future__ import annotations

import hashlib
import json
import math
from typing import Mapping, Sequence

from fmp.market_learning.evidence import EXPECTED_SOURCE_MANIFEST_SHA256

from .exp065_pairwise_interaction_miner import (
    FeatureRankCalibration,
    InMemoryPairwiseInteractionResult,
    PairInteractionCalibration,
    PairwiseInteractionHypothesis,
)
from .exp065_pairwise_interaction_protocol import (
    CONTINUOUS_FEATURES,
    DESIGN_YEARS,
    DIRECTIONS,
    EXPERIMENT_ID,
    HORIZONS_MINUTES,
    HYPOTHESES_PER_CELL_HORIZON,
    MAX_FROZEN_GLOBAL,
    MAX_FROZEN_PER_CELL_HORIZON,
    MAX_SHORTLIST_GLOBAL,
    MAX_SHORTLIST_PER_CELL_HORIZON,
    OUTPUT_KIND,
    POLARITIES,
    SYMBOLS,
    TIMEFRAMES,
    AnnualPairwiseInteractionStat,
    canonical_feature_pair,
    feature_pairs,
    pair_hypothesis_fingerprint,
    pairwise_interaction_gate_passes,
    pairwise_interaction_metrics,
    protocol_fingerprint,
)


EXP065_EVIDENCE_CONTRACT_DECISION = "DEC-463"
EXP065_CELL_EVIDENCE_VERSION = 1
EXP065_CELL_EVIDENCE_PROTOCOL = (
    "fmp-exp065-pairwise-interaction-cell-evidence-v1"
)
EXP065_AGGREGATE_EVIDENCE_VERSION = 1
EXP065_AGGREGATE_EVIDENCE_PROTOCOL = (
    "fmp-exp065-pairwise-interaction-aggregate-evidence-v1"
)

DEC462_MERGE_SHA = "735418cd455055a5102de6fb0d621355c4e85592"
DEC462_MINER_BLOB_SHA = "7dac382838d2b8fcc4df5d02c4949ad65c17635b"
DEC461_PROTOCOL_BLOB_SHA = "b54267d790667659749a96123ad23a491ff50dfa"

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


def _feature_calibration_payload(
    value: FeatureRankCalibration,
) -> dict[str, object]:
    return {
        "feature_name": value.feature_name,
        "value_count": len(value.values),
        "distinct_value_count": len(set(value.values)),
        "minimum": value.values[0],
        "maximum": value.values[-1],
        "values_sha256": _sha256_bytes(_canonical_json(list(value.values))),
    }


def _pair_calibration_payload(
    value: PairInteractionCalibration,
) -> dict[str, object]:
    return {
        "feature_a": value.feature_a,
        "feature_b": value.feature_b,
        "value_count": len(value.values),
        "distinct_value_count": len(set(value.values)),
        "minimum": value.values[0],
        "maximum": value.values[-1],
        "values_sha256": _sha256_bytes(_canonical_json(list(value.values))),
    }


def _annual_stat_payload(
    value: AnnualPairwiseInteractionStat,
) -> dict[str, object]:
    return {
        "year": value.year,
        "evaluable_support": value.evaluable_support,
        "selected_tail_support": value.selected_tail_support,
        "signed_partial_interaction_slope_net_pips_0p5": (
            value.signed_partial_interaction_slope_net_pips_0p5
        ),
        "selected_tail_mean_net_pips_0p5": (
            value.selected_tail_mean_net_pips_0p5
        ),
        "selected_tail_incremental_residual_mean_net_pips_0p5": (
            value.selected_tail_incremental_residual_mean_net_pips_0p5
        ),
        "selected_tail_mean_net_pips_1p0": (
            value.selected_tail_mean_net_pips_1p0
        ),
    }


def _hypothesis_payload(
    value: PairwiseInteractionHypothesis,
) -> dict[str, object]:
    return {
        "symbol": value.symbol,
        "timeframe": value.timeframe,
        "horizon_minutes": value.horizon_minutes,
        "feature_a": value.feature_a,
        "feature_b": value.feature_b,
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
        "positive_partial_slope_year_count": (
            value.positive_partial_slope_year_count
        ),
        "positive_raw_tail_mean_year_count": (
            value.positive_raw_tail_mean_year_count
        ),
        "positive_incremental_tail_mean_year_count": (
            value.positive_incremental_tail_mean_year_count
        ),
        "equal_year_signed_partial_slope_net_pips_0p5": (
            value.equal_year_signed_partial_slope_net_pips_0p5
        ),
        "equal_year_raw_tail_mean_net_pips_0p5": (
            value.equal_year_raw_tail_mean_net_pips_0p5
        ),
        "equal_year_incremental_tail_mean_net_pips_0p5": (
            value.equal_year_incremental_tail_mean_net_pips_0p5
        ),
        "equal_year_raw_tail_mean_net_pips_1p0": (
            value.equal_year_raw_tail_mean_net_pips_1p0
        ),
        "lower_half_signed_partial_slope_net_pips_0p5": (
            value.lower_half_signed_partial_slope_net_pips_0p5
        ),
        "lower_half_raw_tail_mean_net_pips_0p5": (
            value.lower_half_raw_tail_mean_net_pips_0p5
        ),
        "lower_half_incremental_tail_mean_net_pips_0p5": (
            value.lower_half_incremental_tail_mean_net_pips_0p5
        ),
        "two_year_block_signed_partial_slope_net_pips_0p5": [
            [name, metric]
            for name, metric in (
                value.two_year_block_signed_partial_slope_net_pips_0p5
            )
        ],
        "minimum_two_year_block_signed_partial_slope_net_pips_0p5": (
            value.minimum_two_year_block_signed_partial_slope_net_pips_0p5
        ),
        "two_year_block_raw_tail_mean_net_pips_0p5": [
            [name, metric]
            for name, metric in value.two_year_block_raw_tail_mean_net_pips_0p5
        ],
        "minimum_two_year_block_raw_tail_mean_net_pips_0p5": (
            value.minimum_two_year_block_raw_tail_mean_net_pips_0p5
        ),
        "two_year_block_incremental_tail_mean_net_pips_0p5": [
            [name, metric]
            for name, metric in (
                value.two_year_block_incremental_tail_mean_net_pips_0p5
            )
        ],
        "minimum_two_year_block_incremental_tail_mean_net_pips_0p5": (
            value.minimum_two_year_block_incremental_tail_mean_net_pips_0p5
        ),
    }


def compile_cell_evidence(
    result: InMemoryPairwiseInteractionResult,
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
        raise ValueError("DEC-463 result cell identity mismatch")

    feature_names = tuple(
        item.feature_name for item in result.feature_calibrations
    )
    if feature_names != report.active_continuous_features:
        raise ValueError("DEC-463 feature calibration/report identity mismatch")
    if len(feature_names) != len(set(feature_names)):
        raise ValueError("DEC-463 feature calibration identity duplicated")

    pair_names = tuple(
        (item.feature_a, item.feature_b) for item in result.pair_calibrations
    )
    if pair_names != report.active_feature_pairs:
        raise ValueError("DEC-463 pair calibration/report identity mismatch")
    if len(pair_names) != len(set(pair_names)):
        raise ValueError("DEC-463 pair calibration identity duplicated")

    evidence: dict[str, object] = {
        "evidence_version": EXP065_CELL_EVIDENCE_VERSION,
        "evidence_protocol": EXP065_CELL_EVIDENCE_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "protocol_source_blob_sha": DEC461_PROTOCOL_BLOB_SHA,
        "miner_decision": "DEC-462",
        "miner_source_blob_sha": DEC462_MINER_BLOB_SHA,
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
        "feature_rank_calibrations": [
            _feature_calibration_payload(item)
            for item in result.feature_calibrations
        ],
        "pair_interaction_calibrations": [
            _pair_calibration_payload(item)
            for item in result.pair_calibrations
        ],
        "pairwise_interaction": {
            "active_continuous_features": list(
                report.active_continuous_features
            ),
            "active_feature_pairs": [
                list(pair) for pair in report.active_feature_pairs
            ],
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
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
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
) -> tuple[AnnualPairwiseInteractionStat, ...]:
    if not isinstance(value, list) or len(value) != len(DESIGN_YEARS):
        raise ValueError("DEC-463 annual stats must cover exactly 2015-2022")
    out: list[AnnualPairwiseInteractionStat] = []
    for raw, year in zip(value, DESIGN_YEARS):
        if not isinstance(raw, Mapping) or raw.get("year") != year:
            raise ValueError("DEC-463 annual stat year identity mismatch")
        out.append(
            AnnualPairwiseInteractionStat(
                year=year,
                evaluable_support=_positive_int(
                    raw.get("evaluable_support"),
                    field=f"DEC-463 {year} evaluable support",
                ),
                selected_tail_support=_positive_int(
                    raw.get("selected_tail_support"),
                    field=f"DEC-463 {year} selected-tail support",
                ),
                signed_partial_interaction_slope_net_pips_0p5=_finite_float(
                    raw.get(
                        "signed_partial_interaction_slope_net_pips_0p5"
                    ),
                    field=f"DEC-463 {year} signed partial slope",
                ),
                selected_tail_mean_net_pips_0p5=_finite_float(
                    raw.get("selected_tail_mean_net_pips_0p5"),
                    field=f"DEC-463 {year} raw tail mean",
                ),
                selected_tail_incremental_residual_mean_net_pips_0p5=(
                    _finite_float(
                        raw.get(
                            "selected_tail_incremental_residual_mean_net_pips_0p5"
                        ),
                        field=f"DEC-463 {year} incremental tail mean",
                    )
                ),
                selected_tail_mean_net_pips_1p0=_finite_float(
                    raw.get("selected_tail_mean_net_pips_1p0"),
                    field=f"DEC-463 {year} stress tail mean",
                ),
            )
        )
    return tuple(out)


def _validate_feature_calibrations(
    value: object,
    *,
    active_features: list[object],
) -> None:
    if not isinstance(value, list):
        raise ValueError("DEC-463 feature rank calibrations must be a list")
    if len(value) != len(active_features):
        raise ValueError("DEC-463 feature calibration count mismatch")

    names: list[str] = []
    for raw in value:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-463 feature rank calibration malformed")
        feature_name = raw.get("feature_name")
        if feature_name not in CONTINUOUS_FEATURES:
            raise ValueError("DEC-463 feature calibration identity mismatch")
        names.append(str(feature_name))
        count = _positive_int(
            raw.get("value_count"),
            field="DEC-463 feature calibration value count",
        )
        distinct = _positive_int(
            raw.get("distinct_value_count"),
            field="DEC-463 feature calibration distinct count",
        )
        if count < 600:
            raise ValueError("DEC-463 feature calibration row count below protocol")
        if distinct < 20 or distinct > count:
            raise ValueError(
                "DEC-463 feature calibration distinct count outside protocol"
            )
        minimum = _finite_float(
            raw.get("minimum"),
            field="DEC-463 feature calibration minimum",
        )
        maximum = _finite_float(
            raw.get("maximum"),
            field="DEC-463 feature calibration maximum",
        )
        if minimum > maximum:
            raise ValueError("DEC-463 feature calibration range invalid")
        _validate_sha256(
            raw.get("values_sha256"),
            field="DEC-463 feature calibration values fingerprint",
        )

    if names != active_features:
        raise ValueError("DEC-463 feature calibration order mismatch")
    if len(names) != len(set(names)):
        raise ValueError("DEC-463 feature calibration identity duplicated")


def _validate_pair_calibrations(
    value: object,
    *,
    active_pairs: list[object],
    active_features: list[object],
) -> None:
    if not isinstance(value, list):
        raise ValueError("DEC-463 pair calibrations must be a list")
    if len(value) != len(active_pairs):
        raise ValueError("DEC-463 pair calibration count mismatch")

    names: list[list[str]] = []
    allowed_pairs = set(feature_pairs())
    for raw in value:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-463 pair calibration malformed")
        feature_a = raw.get("feature_a")
        feature_b = raw.get("feature_b")
        if not isinstance(feature_a, str) or not isinstance(feature_b, str):
            raise ValueError("DEC-463 pair calibration identity malformed")
        pair = canonical_feature_pair(feature_a, feature_b)
        if pair != (feature_a, feature_b) or pair not in allowed_pairs:
            raise ValueError("DEC-463 pair calibration canonical order mismatch")
        if feature_a not in active_features or feature_b not in active_features:
            raise ValueError("DEC-463 pair calibration inactive constituent")
        names.append([feature_a, feature_b])

        count = _positive_int(
            raw.get("value_count"),
            field="DEC-463 pair calibration value count",
        )
        distinct = _positive_int(
            raw.get("distinct_value_count"),
            field="DEC-463 pair calibration distinct count",
        )
        if count < 600:
            raise ValueError("DEC-463 pair calibration row count below protocol")
        if distinct < 20 or distinct > count:
            raise ValueError(
                "DEC-463 pair calibration distinct count outside protocol"
            )
        minimum = _finite_float(
            raw.get("minimum"),
            field="DEC-463 pair calibration minimum",
        )
        maximum = _finite_float(
            raw.get("maximum"),
            field="DEC-463 pair calibration maximum",
        )
        if minimum > maximum:
            raise ValueError("DEC-463 pair calibration range invalid")
        _validate_sha256(
            raw.get("values_sha256"),
            field="DEC-463 pair calibration values fingerprint",
        )

    if names != active_pairs:
        raise ValueError("DEC-463 pair calibration order mismatch")
    if len({tuple(item) for item in names}) != len(names):
        raise ValueError("DEC-463 pair calibration identity duplicated")


def _metric_expected_values(
    annual_stats: tuple[AnnualPairwiseInteractionStat, ...],
) -> tuple[dict[str, object], dict[str, float], dict[str, float], dict[str, float]]:
    metrics = pairwise_interaction_metrics(annual_stats)
    partial_blocks = metrics[
        "two_year_block_signed_partial_slope_net_pips_0p5"
    ]
    raw_blocks = metrics["two_year_block_raw_tail_mean_net_pips_0p5"]
    incremental_blocks = metrics[
        "two_year_block_incremental_tail_mean_net_pips_0p5"
    ]
    if not all(
        isinstance(value, dict)
        for value in (partial_blocks, raw_blocks, incremental_blocks)
    ):
        raise ValueError("DEC-463 two-year block metric malformed")

    expected: dict[str, object] = {
        "total_selected_tail_support": int(
            metrics["total_selected_tail_support"]
        ),
        "minimum_year_selected_tail_support": int(
            metrics["minimum_year_selected_tail_support"]
        ),
        "positive_partial_slope_year_count": int(
            metrics["positive_partial_slope_year_count"]
        ),
        "positive_raw_tail_mean_year_count": int(
            metrics["positive_raw_tail_mean_year_count"]
        ),
        "positive_incremental_tail_mean_year_count": int(
            metrics["positive_incremental_tail_mean_year_count"]
        ),
        "equal_year_signed_partial_slope_net_pips_0p5": float(
            metrics["equal_year_signed_partial_slope_net_pips_0p5"]
        ),
        "equal_year_raw_tail_mean_net_pips_0p5": float(
            metrics["equal_year_raw_tail_mean_net_pips_0p5"]
        ),
        "equal_year_incremental_tail_mean_net_pips_0p5": float(
            metrics["equal_year_incremental_tail_mean_net_pips_0p5"]
        ),
        "equal_year_raw_tail_mean_net_pips_1p0": float(
            metrics["equal_year_raw_tail_mean_net_pips_1p0"]
        ),
        "lower_half_signed_partial_slope_net_pips_0p5": float(
            metrics["lower_half_signed_partial_slope_net_pips_0p5"]
        ),
        "lower_half_raw_tail_mean_net_pips_0p5": float(
            metrics["lower_half_raw_tail_mean_net_pips_0p5"]
        ),
        "lower_half_incremental_tail_mean_net_pips_0p5": float(
            metrics["lower_half_incremental_tail_mean_net_pips_0p5"]
        ),
        "minimum_two_year_block_signed_partial_slope_net_pips_0p5": float(
            metrics[
                "minimum_two_year_block_signed_partial_slope_net_pips_0p5"
            ]
        ),
        "minimum_two_year_block_raw_tail_mean_net_pips_0p5": float(
            metrics["minimum_two_year_block_raw_tail_mean_net_pips_0p5"]
        ),
        "minimum_two_year_block_incremental_tail_mean_net_pips_0p5": float(
            metrics[
                "minimum_two_year_block_incremental_tail_mean_net_pips_0p5"
            ]
        ),
    }
    return (
        expected,
        {str(k): float(v) for k, v in partial_blocks.items()},
        {str(k): float(v) for k, v in raw_blocks.items()},
        {str(k): float(v) for k, v in incremental_blocks.items()},
    )


def _validate_hypothesis(
    raw: object,
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> tuple[str, tuple[object, ...]]:
    if not isinstance(raw, Mapping):
        raise ValueError("DEC-463 shortlist row must be an object")
    if (
        raw.get("symbol") != symbol
        or raw.get("timeframe") != timeframe
        or raw.get("horizon_minutes") != horizon_minutes
    ):
        raise ValueError("DEC-463 shortlist cell identity mismatch")

    feature_a = raw.get("feature_a")
    feature_b = raw.get("feature_b")
    direction = raw.get("direction")
    polarity = raw.get("polarity")
    if not isinstance(feature_a, str) or not isinstance(feature_b, str):
        raise ValueError("DEC-463 shortlist feature pair malformed")
    pair = canonical_feature_pair(feature_a, feature_b)
    if pair != (feature_a, feature_b):
        raise ValueError("DEC-463 shortlist pair order mismatch")
    if direction not in DIRECTIONS:
        raise ValueError("DEC-463 shortlist direction mismatch")
    if polarity not in POLARITIES:
        raise ValueError("DEC-463 shortlist polarity mismatch")

    expected_fingerprint = pair_hypothesis_fingerprint(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        feature_a=feature_a,
        feature_b=feature_b,
        direction=str(direction),
        polarity=str(polarity),
    )
    if raw.get("fingerprint") != expected_fingerprint:
        raise ValueError("DEC-463 shortlist fingerprint mismatch")

    annual_stats = _validate_annual_stats(raw.get("annual_stats"))
    if not pairwise_interaction_gate_passes(annual_stats):
        raise ValueError(
            "DEC-463 shortlist hypothesis fails pairwise-interaction gate"
        )

    expected, partial_blocks, raw_blocks, incremental_blocks = (
        _metric_expected_values(annual_stats)
    )
    for field, expected_value in expected.items():
        if raw.get(field) != expected_value:
            raise ValueError(f"DEC-463 shortlist {field} mismatch")

    if raw.get("two_year_block_signed_partial_slope_net_pips_0p5") != [
        [name, metric] for name, metric in partial_blocks.items()
    ]:
        raise ValueError("DEC-463 partial-slope block metric mismatch")
    if raw.get("two_year_block_raw_tail_mean_net_pips_0p5") != [
        [name, metric] for name, metric in raw_blocks.items()
    ]:
        raise ValueError("DEC-463 raw-tail block metric mismatch")
    if raw.get("two_year_block_incremental_tail_mean_net_pips_0p5") != [
        [name, metric] for name, metric in incremental_blocks.items()
    ]:
        raise ValueError("DEC-463 incremental-tail block metric mismatch")

    rank_key: tuple[object, ...] = (
        -float(expected["lower_half_incremental_tail_mean_net_pips_0p5"]),
        -float(
            expected[
                "minimum_two_year_block_incremental_tail_mean_net_pips_0p5"
            ]
        ),
        -float(expected["lower_half_raw_tail_mean_net_pips_0p5"]),
        -float(expected["minimum_two_year_block_raw_tail_mean_net_pips_0p5"]),
        -float(expected["lower_half_signed_partial_slope_net_pips_0p5"]),
        -float(
            expected[
                "minimum_two_year_block_signed_partial_slope_net_pips_0p5"
            ]
        ),
        -int(expected["positive_incremental_tail_mean_year_count"]),
        -int(expected["positive_raw_tail_mean_year_count"]),
        -int(expected["positive_partial_slope_year_count"]),
        -float(expected["equal_year_raw_tail_mean_net_pips_1p0"]),
        -int(expected["total_selected_tail_support"]),
        feature_a,
        feature_b,
        str(direction),
        str(polarity),
    )
    return expected_fingerprint, rank_key


def _cell_identity(value: Mapping[str, object]) -> tuple[str, str, int]:
    cell = value.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError("DEC-463 cell identity missing")
    identity = (
        cell.get("symbol"),
        cell.get("timeframe"),
        cell.get("horizon_minutes"),
    )
    if identity not in EXPECTED_CELLS:
        raise ValueError("DEC-463 cell identity mismatch")
    return str(identity[0]), str(identity[1]), int(identity[2])


def _validate_nested_cell_semantics(value: Mapping[str, object]) -> None:
    symbol, timeframe, horizon = _cell_identity(value)
    section = value.get("pairwise_interaction")
    if not isinstance(section, Mapping):
        raise ValueError("DEC-463 pairwise interaction section missing")

    active_features = section.get("active_continuous_features")
    if not isinstance(active_features, list):
        raise ValueError("DEC-463 active feature inventory malformed")
    if any(item not in CONTINUOUS_FEATURES for item in active_features):
        raise ValueError("DEC-463 active feature mismatch")
    if len(active_features) != len(set(active_features)):
        raise ValueError("DEC-463 active feature inventory duplicated")
    expected_feature_order = [
        feature for feature in CONTINUOUS_FEATURES if feature in active_features
    ]
    if active_features != expected_feature_order:
        raise ValueError("DEC-463 active feature order mismatch")

    active_pairs = section.get("active_feature_pairs")
    if not isinstance(active_pairs, list):
        raise ValueError("DEC-463 active pair inventory malformed")
    allowed_pair_order = [list(pair) for pair in feature_pairs()]
    normalized_pairs: list[list[str]] = []
    for raw_pair in active_pairs:
        if (
            not isinstance(raw_pair, list)
            or len(raw_pair) != 2
            or not all(isinstance(item, str) for item in raw_pair)
        ):
            raise ValueError("DEC-463 active pair identity malformed")
        pair = [str(raw_pair[0]), str(raw_pair[1])]
        if pair not in allowed_pair_order:
            raise ValueError("DEC-463 active pair identity mismatch")
        if pair[0] not in active_features or pair[1] not in active_features:
            raise ValueError("DEC-463 active pair has inactive constituent")
        normalized_pairs.append(pair)
    expected_pair_order = [
        pair for pair in allowed_pair_order if pair in normalized_pairs
    ]
    if normalized_pairs != expected_pair_order:
        raise ValueError("DEC-463 active pair order mismatch")
    if len({tuple(pair) for pair in normalized_pairs}) != len(normalized_pairs):
        raise ValueError("DEC-463 active pair inventory duplicated")

    if section.get("hypothesis_count") != HYPOTHESES_PER_CELL_HORIZON:
        raise ValueError("DEC-463 nominal hypothesis count mismatch")

    evaluable = _nonnegative_int(
        section.get("evaluable_hypothesis_count"),
        field="DEC-463 evaluable hypothesis count",
    )
    qualifying = _nonnegative_int(
        section.get("qualifying_hypothesis_count"),
        field="DEC-463 qualifying hypothesis count",
    )
    deduplicated = _nonnegative_int(
        section.get("deduplicated_hypothesis_count"),
        field="DEC-463 deduplicated hypothesis count",
    )
    if evaluable > len(normalized_pairs) * len(DIRECTIONS) * len(POLARITIES):
        raise ValueError("DEC-463 evaluable count exceeds active pair search")
    if qualifying > evaluable or deduplicated > qualifying:
        raise ValueError("DEC-463 hypothesis counts inconsistent")

    shortlist = section.get("shortlist")
    frozen = section.get("frozen_hypothesis_fingerprints")
    if not isinstance(shortlist, list) or not isinstance(frozen, list):
        raise ValueError("DEC-463 shortlist inventory malformed")
    if len(shortlist) > MAX_SHORTLIST_PER_CELL_HORIZON:
        raise ValueError("DEC-463 shortlist exceeds per-cell cap")
    if len(shortlist) > deduplicated:
        raise ValueError("DEC-463 shortlist exceeds deduplicated count")
    if len(frozen) > MAX_FROZEN_PER_CELL_HORIZON:
        raise ValueError("DEC-463 frozen inventory exceeds per-cell cap")

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
        raise ValueError("DEC-463 shortlist fingerprint duplicated")
    if rank_keys != sorted(rank_keys):
        raise ValueError("DEC-463 shortlist rank order mismatch")

    if frozen != fingerprints[:MAX_FROZEN_PER_CELL_HORIZON]:
        raise ValueError("DEC-463 frozen fingerprint inventory mismatch")
    for item in frozen:
        _validate_sha256(item, field="DEC-463 frozen hypothesis fingerprint")

    _validate_feature_calibrations(
        value.get("feature_rank_calibrations"),
        active_features=active_features,
    )
    _validate_pair_calibrations(
        value.get("pair_interaction_calibrations"),
        active_pairs=active_pairs,
        active_features=active_features,
    )

    if section.get("output_kind") != OUTPUT_KIND:
        raise ValueError("DEC-463 cell output kind mismatch")


def validate_cell_evidence(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="DEC-463 cell evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-463 cell evidence fingerprint mismatch")

    expected = {
        "evidence_version": EXP065_CELL_EVIDENCE_VERSION,
        "evidence_protocol": EXP065_CELL_EVIDENCE_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "protocol_source_blob_sha": DEC461_PROTOCOL_BLOB_SHA,
        "miner_decision": "DEC-462",
        "miner_source_blob_sha": DEC462_MINER_BLOB_SHA,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "reserved_robustness_opened": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-463 cell evidence {field} mismatch")

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
            raise ValueError(f"DEC-463 cell evidence {field} must remain false")

    _validate_nested_cell_semantics(value)
    identity = _cell_identity(value)
    if value.get("processed_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256[
        identity[0]
    ]:
        raise ValueError("DEC-463 cell Phase 2 source identity mismatch")
    return value


def compile_aggregate_evidence(
    cell_evidence: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError(
            f"DEC-463 aggregate requires exactly {EXPECTED_CELL_COUNT} cells"
        )

    seen: dict[tuple[str, str, int], Mapping[str, object]] = {}
    manifest_pair_by_symbol_timeframe: dict[
        tuple[str, str], tuple[str, str]
    ] = {}
    feature_fingerprints: set[str] = set()
    outcome_fingerprints: set[str] = set()
    summaries: list[dict[str, object]] = []

    for raw in cell_evidence:
        validated = validate_cell_evidence(raw)
        if validated.get("code_commit") != code_commit:
            raise ValueError("DEC-463 aggregate cell code commit mismatch")
        identity = _cell_identity(validated)
        if identity in seen:
            raise ValueError(f"DEC-463 duplicate cell: {identity!r}")
        seen[identity] = validated
        symbol, timeframe, horizon = identity

        processed = _validate_sha256(
            validated.get("processed_manifest_sha256"),
            field="processed_manifest_sha256",
        )
        if processed != EXPECTED_SOURCE_MANIFEST_SHA256[symbol]:
            raise ValueError("DEC-463 Phase 2 source identity mismatch")

        feature_manifest = _validate_sha256(
            validated.get("feature_manifest_sha256"),
            field="feature_manifest_sha256",
        )
        outcome_manifest = _validate_sha256(
            validated.get("outcome_manifest_sha256"),
            field="outcome_manifest_sha256",
        )
        pair_key = (symbol, timeframe)
        manifest_pair = (feature_manifest, outcome_manifest)
        prior_pair = manifest_pair_by_symbol_timeframe.setdefault(
            pair_key,
            manifest_pair,
        )
        if prior_pair != manifest_pair:
            raise ValueError(
                "DEC-463 manifest identity differs across horizons"
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

        section = validated.get("pairwise_interaction")
        if not isinstance(section, Mapping):
            raise ValueError("DEC-463 cell section missing")
        shortlist = section.get("shortlist")
        frozen = section.get("frozen_hypothesis_fingerprints")
        if not isinstance(shortlist, list) or not isinstance(frozen, list):
            raise ValueError("DEC-463 cell shortlist inventory malformed")

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
                "active_feature_pairs": list(
                    section.get("active_feature_pairs", [])
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
                "pairwise_interaction_shortlist_count": len(shortlist),
                "pairwise_interaction_frozen_count": len(frozen),
                "pairwise_interaction_shortlist_fingerprints": [
                    item.get("fingerprint")
                    for item in shortlist
                    if isinstance(item, Mapping)
                ],
                "pairwise_interaction_frozen_fingerprints": list(frozen),
                "output_kind": section.get("output_kind"),
            }
        )

    if set(seen) != set(EXPECTED_CELLS):
        raise ValueError("DEC-463 aggregate cell inventory mismatch")
    if len(feature_fingerprints) != 1 or len(outcome_fingerprints) != 1:
        raise ValueError("DEC-463 aggregate upstream evidence identity mismatch")

    summaries.sort(
        key=lambda row: (
            str(row["symbol"]),
            str(row["timeframe"]),
            int(row["horizon_minutes"]),
        )
    )
    shortlist_count = sum(
        int(row["pairwise_interaction_shortlist_count"])
        for row in summaries
    )
    frozen_count = sum(
        int(row["pairwise_interaction_frozen_count"])
        for row in summaries
    )

    evidence: dict[str, object] = {
        "evidence_version": EXP065_AGGREGATE_EVIDENCE_VERSION,
        "evidence_protocol": EXP065_AGGREGATE_EVIDENCE_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "protocol_source_blob_sha": DEC461_PROTOCOL_BLOB_SHA,
        "miner_decision": "DEC-462",
        "miner_source_blob_sha": DEC462_MINER_BLOB_SHA,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "code_commit": code_commit,
        "feature_evidence_fingerprint": next(iter(feature_fingerprints)),
        "outcome_evidence_fingerprint": next(iter(outcome_fingerprints)),
        "expected_cell_count": EXPECTED_CELL_COUNT,
        "verified_cell_count": EXPECTED_CELL_COUNT,
        "pairwise_interaction_shortlist_count": shortlist_count,
        "pairwise_interaction_frozen_count": frozen_count,
        "cells": summaries,
        "output_kind": OUTPUT_KIND,
        "reserved_robustness_opened": False,
        "source_access_authorized": SOURCE_ACCESS_AUTHORIZED,
        "historical_execution_authorized": HISTORICAL_EXECUTION_AUTHORIZED,
        "historical_result_authorized": HISTORICAL_RESULT_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
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
        field="DEC-463 aggregate evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-463 aggregate evidence fingerprint mismatch")

    expected = {
        "evidence_version": EXP065_AGGREGATE_EVIDENCE_VERSION,
        "evidence_protocol": EXP065_AGGREGATE_EVIDENCE_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "protocol_source_blob_sha": DEC461_PROTOCOL_BLOB_SHA,
        "miner_decision": "DEC-462",
        "miner_source_blob_sha": DEC462_MINER_BLOB_SHA,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "expected_cell_count": EXPECTED_CELL_COUNT,
        "verified_cell_count": EXPECTED_CELL_COUNT,
        "output_kind": OUTPUT_KIND,
        "reserved_robustness_opened": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-463 aggregate evidence {field} mismatch")

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
                f"DEC-463 aggregate evidence {field} must remain false"
            )

    cells = value.get("cells")
    if not isinstance(cells, list) or len(cells) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-463 aggregate cells inventory mismatch")

    identities: list[tuple[str, str, int]] = []
    cell_fingerprints: list[str] = []
    shortlist_count = 0
    frozen_count = 0
    feature_fingerprints: set[str] = set()
    outcome_fingerprints: set[str] = set()
    manifest_pairs: dict[tuple[str, str], tuple[str, str]] = {}

    for row in cells:
        if not isinstance(row, Mapping):
            raise ValueError("DEC-463 aggregate cell summary malformed")
        identity = (
            row.get("symbol"),
            row.get("timeframe"),
            row.get("horizon_minutes"),
        )
        if identity not in EXPECTED_CELLS:
            raise ValueError("DEC-463 aggregate cell identity mismatch")
        symbol = str(identity[0])
        timeframe = str(identity[1])
        horizon = int(identity[2])
        identities.append((symbol, timeframe, horizon))

        cell_fingerprints.append(
            _validate_sha256(
                row.get("cell_evidence_fingerprint"),
                field="DEC-463 cell evidence fingerprint",
            )
        )
        if row.get("processed_manifest_sha256") != EXPECTED_SOURCE_MANIFEST_SHA256[
            symbol
        ]:
            raise ValueError("DEC-463 aggregate Phase 2 source identity mismatch")

        feature_manifest = _validate_sha256(
            row.get("feature_manifest_sha256"),
            field="DEC-463 aggregate feature manifest",
        )
        outcome_manifest = _validate_sha256(
            row.get("outcome_manifest_sha256"),
            field="DEC-463 aggregate outcome manifest",
        )
        key = (symbol, timeframe)
        manifest_pair = (feature_manifest, outcome_manifest)
        prior_pair = manifest_pairs.setdefault(key, manifest_pair)
        if prior_pair != manifest_pair:
            raise ValueError(
                "DEC-463 aggregate manifest identity differs across horizons"
            )

        feature_fingerprints.add(
            _validate_sha256(
                row.get("feature_evidence_fingerprint"),
                field="DEC-463 aggregate feature evidence fingerprint",
            )
        )
        outcome_fingerprints.add(
            _validate_sha256(
                row.get("outcome_evidence_fingerprint"),
                field="DEC-463 aggregate outcome evidence fingerprint",
            )
        )

        active_features = row.get("active_continuous_features")
        active_pairs = row.get("active_feature_pairs")
        if not isinstance(active_features, list) or not isinstance(
            active_pairs,
            list,
        ):
            raise ValueError("DEC-463 aggregate active inventory malformed")
        if any(item not in CONTINUOUS_FEATURES for item in active_features):
            raise ValueError("DEC-463 aggregate active feature mismatch")
        if active_features != [
            feature for feature in CONTINUOUS_FEATURES if feature in active_features
        ]:
            raise ValueError("DEC-463 aggregate active feature order mismatch")
        if len(active_features) != len(set(active_features)):
            raise ValueError("DEC-463 aggregate active feature duplicated")

        allowed_pairs = [list(pair) for pair in feature_pairs()]
        normalized_pairs: list[list[str]] = []
        for raw_pair in active_pairs:
            if (
                not isinstance(raw_pair, list)
                or len(raw_pair) != 2
                or raw_pair not in allowed_pairs
            ):
                raise ValueError("DEC-463 aggregate active pair mismatch")
            normalized_pairs.append([str(raw_pair[0]), str(raw_pair[1])])
        if normalized_pairs != [
            pair for pair in allowed_pairs if pair in normalized_pairs
        ]:
            raise ValueError("DEC-463 aggregate active pair order mismatch")
        if len({tuple(pair) for pair in normalized_pairs}) != len(
            normalized_pairs
        ):
            raise ValueError("DEC-463 aggregate active pair duplicated")

        if row.get("hypothesis_count") != HYPOTHESES_PER_CELL_HORIZON:
            raise ValueError("DEC-463 aggregate nominal hypothesis count mismatch")
        evaluable = _nonnegative_int(
            row.get("evaluable_hypothesis_count"),
            field="DEC-463 aggregate evaluable count",
        )
        qualifying = _nonnegative_int(
            row.get("qualifying_hypothesis_count"),
            field="DEC-463 aggregate qualifying count",
        )
        deduplicated = _nonnegative_int(
            row.get("deduplicated_hypothesis_count"),
            field="DEC-463 aggregate deduplicated count",
        )
        if evaluable > len(normalized_pairs) * len(DIRECTIONS) * len(POLARITIES):
            raise ValueError(
                "DEC-463 aggregate evaluable count exceeds active pair search"
            )
        if qualifying > evaluable or deduplicated > qualifying:
            raise ValueError("DEC-463 aggregate hypothesis counts inconsistent")

        shortlist_fingerprints = row.get(
            "pairwise_interaction_shortlist_fingerprints"
        )
        frozen_fingerprints = row.get(
            "pairwise_interaction_frozen_fingerprints"
        )
        if (
            not isinstance(shortlist_fingerprints, list)
            or not isinstance(frozen_fingerprints, list)
        ):
            raise ValueError(
                "DEC-463 aggregate cell fingerprint inventories malformed"
            )
        for item in shortlist_fingerprints + frozen_fingerprints:
            _validate_sha256(item, field="DEC-463 hypothesis fingerprint")
        if len(shortlist_fingerprints) > MAX_SHORTLIST_PER_CELL_HORIZON:
            raise ValueError("DEC-463 aggregate cell shortlist exceeds cap")
        if len(shortlist_fingerprints) > deduplicated:
            raise ValueError(
                "DEC-463 aggregate cell shortlist exceeds deduplicated count"
            )
        if len(frozen_fingerprints) > MAX_FROZEN_PER_CELL_HORIZON:
            raise ValueError("DEC-463 aggregate cell frozen exceeds cap")
        if frozen_fingerprints != shortlist_fingerprints[
            :MAX_FROZEN_PER_CELL_HORIZON
        ]:
            raise ValueError(
                "DEC-463 aggregate frozen/shortlist identity mismatch"
            )
        if row.get("pairwise_interaction_shortlist_count") != len(
            shortlist_fingerprints
        ):
            raise ValueError("DEC-463 aggregate shortlist count mismatch")
        if row.get("pairwise_interaction_frozen_count") != len(
            frozen_fingerprints
        ):
            raise ValueError("DEC-463 aggregate frozen count mismatch")
        if row.get("output_kind") != OUTPUT_KIND:
            raise ValueError("DEC-463 aggregate cell output kind mismatch")

        shortlist_count += len(shortlist_fingerprints)
        frozen_count += len(frozen_fingerprints)

    if tuple(identities) != tuple(sorted(EXPECTED_CELLS)):
        raise ValueError("DEC-463 aggregate cells are not exact/sorted")
    if len(cell_fingerprints) != len(set(cell_fingerprints)):
        raise ValueError(
            "DEC-463 aggregate cell evidence fingerprints duplicated"
        )
    if feature_fingerprints != {value.get("feature_evidence_fingerprint")}:
        raise ValueError("DEC-463 aggregate feature evidence identity mismatch")
    if outcome_fingerprints != {value.get("outcome_evidence_fingerprint")}:
        raise ValueError("DEC-463 aggregate outcome evidence identity mismatch")
    if value.get("pairwise_interaction_shortlist_count") != shortlist_count:
        raise ValueError("DEC-463 aggregate total shortlist count mismatch")
    if value.get("pairwise_interaction_frozen_count") != frozen_count:
        raise ValueError("DEC-463 aggregate total frozen count mismatch")
    if shortlist_count > MAX_SHORTLIST_GLOBAL:
        raise ValueError("DEC-463 aggregate shortlist exceeds global cap")
    if frozen_count > MAX_FROZEN_GLOBAL:
        raise ValueError("DEC-463 aggregate frozen exceeds global cap")
    return value


__all__ = [
    "DEC461_PROTOCOL_BLOB_SHA",
    "DEC462_MERGE_SHA",
    "DEC462_MINER_BLOB_SHA",
    "EXPECTED_CELL_COUNT",
    "EXPECTED_CELLS",
    "EXP065_AGGREGATE_EVIDENCE_PROTOCOL",
    "EXP065_AGGREGATE_EVIDENCE_VERSION",
    "EXP065_CELL_EVIDENCE_PROTOCOL",
    "EXP065_CELL_EVIDENCE_VERSION",
    "EXP065_EVIDENCE_CONTRACT_DECISION",
    "compile_aggregate_evidence",
    "compile_cell_evidence",
    "validate_aggregate_evidence",
    "validate_cell_evidence",
]
