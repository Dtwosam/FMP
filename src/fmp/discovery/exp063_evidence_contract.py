from __future__ import annotations

import hashlib
import json
import math
from typing import Mapping, Sequence

from fmp.market_learning.evidence import EXPECTED_SOURCE_MANIFEST_SHA256

from .exp063_persistence_miner import (
    InMemoryPersistenceResult,
    PersistencePatternHypothesis,
)
from .exp063_persistence_protocol import (
    CONTINUOUS_FEATURES,
    DESIGN_YEARS,
    DIRECTIONS,
    HORIZONS_MINUTES,
    MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON,
    MAX_FROZEN_PATTERN_HYPOTHESES,
    MAX_FROZEN_PER_CELL_HORIZON,
    MAX_PERSISTENCE_SHORTLIST_GLOBAL,
    MAX_PERSISTENCE_SHORTLIST_PER_CELL_HORIZON,
    MIN_TOTAL_SUPPORT,
    MIN_YEAR_SUPPORT,
    SYMBOLS,
    TIMEFRAMES,
    AnnualPersistenceStat,
    pattern_fingerprint,
    persistence_gate_passes,
    persistence_metrics,
    protocol_fingerprint,
)
from .exp063_research_direction import SUCCESSOR_EXPERIMENT_ID


EXP063_EVIDENCE_CONTRACT_DECISION = "DEC-446"
EXP063_CELL_EVIDENCE_VERSION = 1
EXP063_CELL_EVIDENCE_PROTOCOL = "fmp-exp063-persistence-cell-evidence-v1"
EXP063_AGGREGATE_EVIDENCE_VERSION = 1
EXP063_AGGREGATE_EVIDENCE_PROTOCOL = (
    "fmp-exp063-persistence-aggregate-evidence-v1"
)

DEC445_MERGE_SHA = "f13988c78470ae00e3c3b9944a774bf2fed42f59"
DEC445_MINER_BLOB_SHA = "40c49a372b35dbc113dbfb71374b1ae5fc7acc45"
DEC444_PROTOCOL_BLOB_SHA = "2c781dd2811b66d2d88f008007bf5c8bcf99f14f"

EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"
OUTPUT_KIND = "RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED"

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


def _expected_pattern_count(active_continuous_count: int) -> int:
    group_sizes = [3] * active_continuous_count + [5]
    total = sum(group_sizes)
    singles = total
    all_pairs = total * (total - 1) // 2
    same_dimension_pairs = sum(
        size * (size - 1) // 2 for size in group_sizes
    )
    return singles + all_pairs - same_dimension_pairs


def _annual_stat_payload(value: AnnualPersistenceStat) -> dict[str, object]:
    return {
        "year": value.year,
        "support": value.support,
        "total_net_pips_0p5": value.total_net_pips_0p5,
        "total_net_pips_1p0": value.total_net_pips_1p0,
    }


def _hypothesis_payload(
    value: PersistencePatternHypothesis,
) -> dict[str, object]:
    return {
        "symbol": value.symbol,
        "timeframe": value.timeframe,
        "horizon_minutes": value.horizon_minutes,
        "direction": value.direction,
        "predicates": [[name, state] for name, state in value.predicates],
        "fingerprint": value.fingerprint,
        "annual_stats": [
            _annual_stat_payload(item) for item in value.annual_stats
        ],
        "total_support": value.total_support,
        "minimum_year_support": value.minimum_year_support,
        "aggregate_mean_net_pips_0p5": value.aggregate_mean_net_pips_0p5,
        "aggregate_mean_net_pips_1p0": value.aggregate_mean_net_pips_1p0,
        "positive_year_count": value.positive_year_count,
        "worst_annual_mean_net_pips_0p5": (
            value.worst_annual_mean_net_pips_0p5
        ),
        "lower_half_annual_mean_net_pips_0p5": (
            value.lower_half_annual_mean_net_pips_0p5
        ),
        "two_year_block_mean_net_pips_0p5": [
            [name, mean]
            for name, mean in value.two_year_block_mean_net_pips_0p5
        ],
        "minimum_two_year_block_mean_net_pips_0p5": (
            value.minimum_two_year_block_mean_net_pips_0p5
        ),
    }


def compile_cell_evidence(
    result: InMemoryPersistenceResult,
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
    if (
        result.state_model.symbol != report.symbol
        or result.state_model.timeframe != report.timeframe
    ):
        raise ValueError("DEC-446 result/state-model identity mismatch")
    if (report.symbol, report.timeframe, report.horizon_minutes) not in EXPECTED_CELLS:
        raise ValueError("DEC-446 result cell identity mismatch")

    evidence: dict[str, object] = {
        "evidence_version": EXP063_CELL_EVIDENCE_VERSION,
        "evidence_protocol": EXP063_CELL_EVIDENCE_PROTOCOL,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": "DEC-445",
        "miner_source_blob_sha": DEC445_MINER_BLOB_SHA,
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
        "state_model": {
            "cutpoints": [
                [name, lower, upper]
                for name, lower, upper in result.state_model.cutpoints
            ],
        },
        "persistence": {
            "active_continuous_features": list(
                report.active_continuous_features
            ),
            "enumerated_pattern_count": report.enumerated_pattern_count,
            "directional_hypothesis_count": (
                report.directional_hypothesis_count
            ),
            "qualifying_directional_hypothesis_count": (
                report.qualifying_directional_hypothesis_count
            ),
            "deduplicated_directional_hypothesis_count": (
                report.deduplicated_directional_hypothesis_count
            ),
            "shortlist": [
                _hypothesis_payload(item) for item in report.shortlist
            ],
            "frozen_pattern_fingerprints": [
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
) -> tuple[AnnualPersistenceStat, ...]:
    if not isinstance(value, list) or len(value) != len(DESIGN_YEARS):
        raise ValueError("DEC-446 annual stats must cover exactly 2015-2022")
    out: list[AnnualPersistenceStat] = []
    for raw, year in zip(value, DESIGN_YEARS):
        if not isinstance(raw, Mapping) or raw.get("year") != year:
            raise ValueError("DEC-446 annual stat year identity mismatch")
        out.append(
            AnnualPersistenceStat(
                year=year,
                support=_nonnegative_int(
                    raw.get("support"),
                    field=f"DEC-446 {year} support",
                ),
                total_net_pips_0p5=_finite_float(
                    raw.get("total_net_pips_0p5"),
                    field=f"DEC-446 {year} total 0.5-pip net",
                ),
                total_net_pips_1p0=_finite_float(
                    raw.get("total_net_pips_1p0"),
                    field=f"DEC-446 {year} total 1.0-pip net",
                ),
            )
        )
    return tuple(out)


def _validate_hypothesis(
    raw: object,
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> tuple[str, tuple[object, ...]]:
    if not isinstance(raw, Mapping):
        raise ValueError("DEC-446 shortlist row must be an object")
    if (
        raw.get("symbol") != symbol
        or raw.get("timeframe") != timeframe
        or raw.get("horizon_minutes") != horizon_minutes
    ):
        raise ValueError("DEC-446 shortlist cell identity mismatch")

    direction = raw.get("direction")
    if direction not in DIRECTIONS:
        raise ValueError("DEC-446 shortlist direction mismatch")
    predicates_raw = raw.get("predicates")
    if (
        not isinstance(predicates_raw, list)
        or not 1 <= len(predicates_raw) <= 2
    ):
        raise ValueError("DEC-446 shortlist predicate depth mismatch")
    predicates: list[tuple[str, str]] = []
    for item in predicates_raw:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or not isinstance(item[0], str)
            or not isinstance(item[1], str)
        ):
            raise ValueError("DEC-446 shortlist predicate malformed")
        predicates.append((item[0], item[1]))

    expected_fingerprint = pattern_fingerprint(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        direction=str(direction),
        predicates=tuple(predicates),
    )
    if raw.get("fingerprint") != expected_fingerprint:
        raise ValueError("DEC-446 shortlist fingerprint mismatch")

    annual_stats = _validate_annual_stats(raw.get("annual_stats"))
    if not persistence_gate_passes(annual_stats):
        raise ValueError("DEC-446 shortlist hypothesis fails persistence gate")
    metrics = persistence_metrics(annual_stats)

    expected_values = {
        "total_support": int(metrics["total_support"]),
        "minimum_year_support": int(metrics["minimum_year_support"]),
        "aggregate_mean_net_pips_0p5": float(
            metrics["aggregate_mean_net_pips_0p5"]
        ),
        "aggregate_mean_net_pips_1p0": float(
            metrics["aggregate_mean_net_pips_1p0"]
        ),
        "positive_year_count": int(metrics["positive_year_count"]),
        "worst_annual_mean_net_pips_0p5": float(
            metrics["worst_annual_mean_net_pips_0p5"]
        ),
        "lower_half_annual_mean_net_pips_0p5": float(
            metrics["lower_half_annual_mean_net_pips_0p5"]
        ),
        "minimum_two_year_block_mean_net_pips_0p5": float(
            metrics["minimum_two_year_block_mean_net_pips_0p5"]
        ),
    }
    for field, expected in expected_values.items():
        if raw.get(field) != expected:
            raise ValueError(f"DEC-446 shortlist {field} mismatch")

    blocks = metrics["two_year_block_mean_net_pips_0p5"]
    if not isinstance(blocks, dict):
        raise ValueError("DEC-446 persistence block metric malformed")
    expected_blocks = [[name, float(mean)] for name, mean in blocks.items()]
    if raw.get("two_year_block_mean_net_pips_0p5") != expected_blocks:
        raise ValueError("DEC-446 two-year block metric mismatch")

    rank_key: tuple[object, ...] = (
        -expected_values["lower_half_annual_mean_net_pips_0p5"],
        -expected_values["minimum_two_year_block_mean_net_pips_0p5"],
        -expected_values["positive_year_count"],
        -expected_values["worst_annual_mean_net_pips_0p5"],
        -expected_values["aggregate_mean_net_pips_0p5"],
        -expected_values["aggregate_mean_net_pips_1p0"],
        -expected_values["total_support"],
        len(predicates),
        expected_fingerprint,
    )
    return expected_fingerprint, rank_key


def _validate_nested_cell_semantics(
    value: Mapping[str, object],
) -> None:
    cell = value.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError("DEC-446 cell identity must be an object")
    identity = (
        cell.get("symbol"),
        cell.get("timeframe"),
        cell.get("horizon_minutes"),
    )
    if identity not in EXPECTED_CELLS:
        raise ValueError("DEC-446 cell identity mismatch")
    symbol, timeframe, horizon = (
        str(identity[0]),
        str(identity[1]),
        int(identity[2]),
    )

    state_model = value.get("state_model")
    if not isinstance(state_model, Mapping):
        raise ValueError("DEC-446 state model must be an object")
    cutpoints = state_model.get("cutpoints")
    if not isinstance(cutpoints, list):
        raise ValueError("DEC-446 state-model cutpoints must be a list")
    names: list[str] = []
    for raw in cutpoints:
        if (
            not isinstance(raw, list)
            or len(raw) != 3
            or raw[0] not in CONTINUOUS_FEATURES
        ):
            raise ValueError("DEC-446 state-model cutpoint malformed")
        lower = _finite_float(raw[1], field="DEC-446 lower cutpoint")
        upper = _finite_float(raw[2], field="DEC-446 upper cutpoint")
        if not lower < upper:
            raise ValueError("DEC-446 state-model cutpoints not ordered")
        names.append(str(raw[0]))
    if len(names) != len(set(names)):
        raise ValueError("DEC-446 state model has duplicate dimensions")

    persistence = value.get("persistence")
    if not isinstance(persistence, Mapping):
        raise ValueError("DEC-446 persistence section must be an object")
    if persistence.get("active_continuous_features") != names:
        raise ValueError("DEC-446 active-feature identity mismatch")

    expected_patterns = _expected_pattern_count(len(names))
    if expected_patterns > MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON:
        raise ValueError("DEC-446 expected pattern count exceeds protocol")
    if persistence.get("enumerated_pattern_count") != expected_patterns:
        raise ValueError("DEC-446 enumerated pattern count mismatch")
    if persistence.get("directional_hypothesis_count") != expected_patterns * len(
        DIRECTIONS
    ):
        raise ValueError("DEC-446 directional search count mismatch")

    qualifying = _nonnegative_int(
        persistence.get("qualifying_directional_hypothesis_count"),
        field="DEC-446 qualifying count",
    )
    deduplicated = _nonnegative_int(
        persistence.get("deduplicated_directional_hypothesis_count"),
        field="DEC-446 deduplicated count",
    )
    if deduplicated > qualifying:
        raise ValueError("DEC-446 deduplicated count exceeds qualifying count")

    shortlist = persistence.get("shortlist")
    if not isinstance(shortlist, list):
        raise ValueError("DEC-446 shortlist must be a list")
    if len(shortlist) > MAX_PERSISTENCE_SHORTLIST_PER_CELL_HORIZON:
        raise ValueError("DEC-446 shortlist exceeds frozen cap")
    if len(shortlist) > deduplicated:
        raise ValueError("DEC-446 shortlist exceeds deduplicated count")

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
        raise ValueError("DEC-446 shortlist fingerprints duplicated")
    if rank_keys != sorted(rank_keys):
        raise ValueError("DEC-446 shortlist rank order mismatch")

    expected_frozen = fingerprints[:MAX_FROZEN_PER_CELL_HORIZON]
    if persistence.get("frozen_pattern_fingerprints") != expected_frozen:
        raise ValueError("DEC-446 frozen fingerprint inventory mismatch")
    if persistence.get("output_kind") != OUTPUT_KIND:
        raise ValueError("DEC-446 output kind mismatch")


def validate_cell_evidence(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="DEC-446 cell evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-446 cell evidence fingerprint mismatch")

    expected = {
        "evidence_version": EXP063_CELL_EVIDENCE_VERSION,
        "evidence_protocol": EXP063_CELL_EVIDENCE_PROTOCOL,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": "DEC-445",
        "miner_source_blob_sha": DEC445_MINER_BLOB_SHA,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "reserved_robustness_opened": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-446 cell evidence {field} mismatch")

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
            raise ValueError(f"DEC-446 cell evidence {field} must remain false")

    _validate_nested_cell_semantics(value)
    return value


def _cell_identity(
    value: Mapping[str, object],
) -> tuple[str, str, int]:
    raw = value.get("cell")
    if not isinstance(raw, Mapping):
        raise ValueError("DEC-446 aggregate cell identity missing")
    identity = (
        raw.get("symbol"),
        raw.get("timeframe"),
        raw.get("horizon_minutes"),
    )
    if identity not in EXPECTED_CELLS:
        raise ValueError(f"DEC-446 unexpected cell identity: {identity!r}")
    return str(identity[0]), str(identity[1]), int(identity[2])


def compile_aggregate_evidence(
    cell_evidence: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError(
            f"DEC-446 aggregate requires exactly {EXPECTED_CELL_COUNT} cells"
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
            raise ValueError("DEC-446 aggregate cell code commit mismatch")
        identity = _cell_identity(validated)
        if identity in seen:
            raise ValueError(f"DEC-446 duplicate cell: {identity!r}")
        seen[identity] = validated
        symbol, timeframe, horizon = identity

        processed = _validate_sha256(
            validated.get("processed_manifest_sha256"),
            field="processed_manifest_sha256",
        )
        if processed != EXPECTED_SOURCE_MANIFEST_SHA256[symbol]:
            raise ValueError("DEC-446 Phase 2 source identity mismatch")
        prior_processed = source_by_symbol.setdefault(symbol, processed)
        if prior_processed != processed:
            raise ValueError("DEC-446 symbol source identity drift")

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
                "DEC-446 manifest identity differs across horizons"
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

        persistence = validated.get("persistence")
        if not isinstance(persistence, Mapping):
            raise ValueError("DEC-446 persistence summary malformed")
        shortlist = persistence.get("shortlist")
        frozen = persistence.get("frozen_pattern_fingerprints")
        if not isinstance(shortlist, list) or not isinstance(frozen, list):
            raise ValueError("DEC-446 persistence inventories malformed")

        summaries.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "horizon_minutes": horizon,
                "cell_evidence_fingerprint": _validate_sha256(
                    validated.get("evidence_fingerprint"),
                    field="cell evidence fingerprint",
                ),
                "processed_manifest_sha256": processed,
                "feature_manifest_sha256": feature_manifest,
                "outcome_manifest_sha256": outcome_manifest,
                "persistence_shortlist_count": len(shortlist),
                "persistence_shortlist_fingerprints": [
                    str(item["fingerprint"])
                    for item in shortlist
                    if isinstance(item, Mapping)
                ],
                "persistence_frozen_count": len(frozen),
                "persistence_frozen_fingerprints": list(frozen),
                "output_kind": OUTPUT_KIND,
            }
        )

    if set(seen) != set(EXPECTED_CELLS):
        raise ValueError("DEC-446 aggregate cell inventory mismatch")
    if len(feature_fingerprints) != 1:
        raise ValueError(
            "DEC-446 feature evidence fingerprint is not singular"
        )
    if len(outcome_fingerprints) != 1:
        raise ValueError(
            "DEC-446 outcome evidence fingerprint is not singular"
        )

    summaries.sort(
        key=lambda row: (
            str(row["symbol"]),
            str(row["timeframe"]),
            int(row["horizon_minutes"]),
        )
    )
    shortlist_count = sum(
        int(row["persistence_shortlist_count"]) for row in summaries
    )
    frozen_count = sum(
        int(row["persistence_frozen_count"]) for row in summaries
    )
    if shortlist_count > MAX_PERSISTENCE_SHORTLIST_GLOBAL:
        raise ValueError("DEC-446 aggregate shortlist exceeds global cap")
    if frozen_count > MAX_FROZEN_PATTERN_HYPOTHESES:
        raise ValueError("DEC-446 aggregate frozen count exceeds global cap")

    evidence: dict[str, object] = {
        "evidence_version": EXP063_AGGREGATE_EVIDENCE_VERSION,
        "evidence_protocol": EXP063_AGGREGATE_EVIDENCE_PROTOCOL,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": "DEC-445",
        "miner_source_blob_sha": DEC445_MINER_BLOB_SHA,
        "code_commit": code_commit,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "expected_cell_count": EXPECTED_CELL_COUNT,
        "verified_cell_count": len(summaries),
        "feature_evidence_fingerprint": next(
            iter(feature_fingerprints)
        ),
        "outcome_evidence_fingerprint": next(
            iter(outcome_fingerprints)
        ),
        "cells": summaries,
        "persistence_shortlist_count": shortlist_count,
        "persistence_frozen_count": frozen_count,
        "output_kind": OUTPUT_KIND,
        "reserved_robustness_opened": False,
        "source_access_authorized": False,
        "historical_execution_authorized": False,
        "historical_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
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
        field="DEC-446 aggregate evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-446 aggregate evidence fingerprint mismatch")

    expected = {
        "evidence_version": EXP063_AGGREGATE_EVIDENCE_VERSION,
        "evidence_protocol": EXP063_AGGREGATE_EVIDENCE_PROTOCOL,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": "DEC-445",
        "miner_source_blob_sha": DEC445_MINER_BLOB_SHA,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "expected_cell_count": EXPECTED_CELL_COUNT,
        "verified_cell_count": EXPECTED_CELL_COUNT,
        "output_kind": OUTPUT_KIND,
        "reserved_robustness_opened": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(
                f"DEC-446 aggregate evidence {field} mismatch"
            )

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
                f"DEC-446 aggregate evidence {field} must remain false"
            )

    cells = value.get("cells")
    if not isinstance(cells, list) or len(cells) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-446 aggregate cells inventory mismatch")

    identities: list[tuple[str, str, int]] = []
    cell_fingerprints: list[str] = []
    shortlist_count = 0
    frozen_count = 0
    for row in cells:
        if not isinstance(row, Mapping):
            raise ValueError("DEC-446 aggregate cell summary malformed")
        identity = (
            row.get("symbol"),
            row.get("timeframe"),
            row.get("horizon_minutes"),
        )
        if identity not in EXPECTED_CELLS:
            raise ValueError("DEC-446 aggregate cell identity mismatch")
        identities.append(
            (str(identity[0]), str(identity[1]), int(identity[2]))
        )
        cell_fingerprints.append(
            _validate_sha256(
                row.get("cell_evidence_fingerprint"),
                field="DEC-446 cell evidence fingerprint",
            )
        )
        if row.get("output_kind") != OUTPUT_KIND:
            raise ValueError("DEC-446 aggregate cell output kind mismatch")
        shortlist_fingerprints = row.get(
            "persistence_shortlist_fingerprints"
        )
        frozen_fingerprints = row.get(
            "persistence_frozen_fingerprints"
        )
        if (
            not isinstance(shortlist_fingerprints, list)
            or not isinstance(frozen_fingerprints, list)
        ):
            raise ValueError(
                "DEC-446 aggregate cell fingerprint inventories malformed"
            )
        if row.get("persistence_shortlist_count") != len(
            shortlist_fingerprints
        ):
            raise ValueError("DEC-446 aggregate shortlist count mismatch")
        if row.get("persistence_frozen_count") != len(
            frozen_fingerprints
        ):
            raise ValueError("DEC-446 aggregate frozen count mismatch")
        for item in shortlist_fingerprints + frozen_fingerprints:
            _validate_sha256(item, field="DEC-446 pattern fingerprint")
        if frozen_fingerprints != shortlist_fingerprints[
            :MAX_FROZEN_PER_CELL_HORIZON
        ]:
            raise ValueError(
                "DEC-446 aggregate frozen/shortlist identity mismatch"
            )
        shortlist_count += len(shortlist_fingerprints)
        frozen_count += len(frozen_fingerprints)

    if tuple(identities) != tuple(sorted(EXPECTED_CELLS)):
        raise ValueError("DEC-446 aggregate cells are not exact/sorted")
    if len(cell_fingerprints) != len(set(cell_fingerprints)):
        raise ValueError(
            "DEC-446 aggregate cell evidence fingerprints duplicated"
        )
    if value.get("persistence_shortlist_count") != shortlist_count:
        raise ValueError("DEC-446 aggregate total shortlist count mismatch")
    if value.get("persistence_frozen_count") != frozen_count:
        raise ValueError("DEC-446 aggregate total frozen count mismatch")
    if shortlist_count > MAX_PERSISTENCE_SHORTLIST_GLOBAL:
        raise ValueError("DEC-446 aggregate shortlist exceeds global cap")
    if frozen_count > MAX_FROZEN_PATTERN_HYPOTHESES:
        raise ValueError("DEC-446 aggregate frozen count exceeds global cap")
    return value


__all__ = [
    "DEC444_PROTOCOL_BLOB_SHA",
    "DEC445_MERGE_SHA",
    "DEC445_MINER_BLOB_SHA",
    "EXPECTED_CELL_COUNT",
    "EXPECTED_CELLS",
    "EXP063_AGGREGATE_EVIDENCE_PROTOCOL",
    "EXP063_AGGREGATE_EVIDENCE_VERSION",
    "EXP063_CELL_EVIDENCE_PROTOCOL",
    "EXP063_CELL_EVIDENCE_VERSION",
    "EXP063_EVIDENCE_CONTRACT_DECISION",
    "compile_aggregate_evidence",
    "compile_cell_evidence",
    "validate_aggregate_evidence",
    "validate_cell_evidence",
]
