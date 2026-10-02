from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Mapping, Sequence

from .annual_pattern_catalogue_method import collection_segments
from .annual_pattern_catalogue_miner import (
    ANNUAL_CATALOGUE_MINER_DECISION,
    AnnualCatalogueCellResult,
)
from .annual_pattern_catalogue_protocol import (
    ANNUAL_CATALOGUE_PROTOCOL_VERSION,
    EVIDENCE_LABEL,
    EXPERIMENT_ID,
    MIN_ANNUAL_EVALUABLE_SUPPORT,
    PATTERN_CONDITION_COUNT,
    annual_record_identity,
    canonical_pattern_fingerprint,
    enumerate_pattern_definitions,
    protocol_fingerprint,
)
from .pattern_protocol import DIRECTIONS, HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


ANNUAL_CATALOGUE_EVIDENCE_DECISION = "DEC-472"
ANNUAL_CATALOGUE_CELL_EVIDENCE_VERSION = 1
ANNUAL_CATALOGUE_CELL_EVIDENCE_PROTOCOL = (
    "fmp-annual-pattern-catalogue-cell-evidence-v1"
)
ANNUAL_CATALOGUE_AGGREGATE_EVIDENCE_VERSION = 1
ANNUAL_CATALOGUE_AGGREGATE_EVIDENCE_PROTOCOL = (
    "fmp-annual-pattern-catalogue-aggregate-evidence-v1"
)

SOURCE_MINER_DECISION = "DEC-471"
SOURCE_MINER_MERGE_SHA = "3926daa8b64ca18c69d5a95a7b31b960dddde27b"
SOURCE_MINER_BLOB_SHA = "2f4c9327a2b9600aceaa1e272dc613dfd4e7d0b7"

DIRECTIONAL_RECORDS_PER_ANNUAL_CELL = PATTERN_CONDITION_COUNT * len(DIRECTIONS)
EXPECTED_ANNUAL_CELL_IDENTITIES = tuple(
    (segment.label, symbol, timeframe, horizon)
    for segment in collection_segments()
    for symbol in SYMBOLS
    for timeframe in TIMEFRAMES
    for horizon in HORIZONS_MINUTES
)
EXPECTED_ANNUAL_CELL_COUNT = len(EXPECTED_ANNUAL_CELL_IDENTITIES)
EXPECTED_TOTAL_DIRECTIONAL_RECORDS = (
    EXPECTED_ANNUAL_CELL_COUNT * DIRECTIONAL_RECORDS_PER_ANNUAL_CELL
)

HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED = False
STRATEGY_V1_SYNTHESIS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


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


def _nonnegative_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _finite_float(value: object, *, field: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise ValueError(f"{field} must be finite")
    return float(value)


def _stats_payload(record: object) -> dict[str, object]:
    stats = record.statistics
    return {
        "support": stats.support,
        "evaluable": stats.evaluable,
        "mean_net_pips_0p5": stats.mean_net_pips_0p5,
        "median_net_pips_0p5": stats.median_net_pips_0p5,
        "win_rate_0p5": stats.win_rate_0p5,
        "mean_net_pips_1p0": stats.mean_net_pips_1p0,
        "median_net_pips_1p0": stats.median_net_pips_1p0,
    }


def _record_payload(record: object) -> dict[str, object]:
    return {
        "annual_record_id": record.annual_record_id,
        "canonical_pattern_fingerprint": record.canonical_pattern_fingerprint,
        "annual_segment_label": record.annual_segment_label,
        "symbol": record.symbol,
        "timeframe": record.timeframe,
        "horizon_minutes": record.horizon_minutes,
        "direction": record.direction,
        "family": record.family,
        "dimensions": list(record.dimensions),
        "states": list(record.states),
        "lag_minutes": record.lag_minutes,
        "event_fingerprint": record.event_fingerprint,
        "statistics": _stats_payload(record),
    }


def cell_catalogue_payload(result: AnnualCatalogueCellResult) -> dict[str, object]:
    return {
        "catalogue_payload_version": 1,
        "protocol_version": ANNUAL_CATALOGUE_PROTOCOL_VERSION,
        "protocol_fingerprint": result.protocol_fingerprint,
        "miner_decision": ANNUAL_CATALOGUE_MINER_DECISION,
        "annual_segment_label": result.annual_segment_label,
        "cell": {
            "symbol": result.symbol,
            "timeframe": result.timeframe,
            "horizon_minutes": result.horizon_minutes,
        },
        "feature_observation_count": result.feature_observation_count,
        "outcome_observation_count": result.outcome_observation_count,
        "directional_record_count": len(result.records),
        "records": [_record_payload(record) for record in result.records],
    }


def serialize_cell_catalogue(result: AnnualCatalogueCellResult) -> bytes:
    return _canonical_json(cell_catalogue_payload(result))


def _summary_counts_from_payload(
    payload: Mapping[str, object],
) -> dict[str, int]:
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("DEC-472 catalogue records must be a list")
    evaluable = 0
    zero_support = 0
    total_support = 0
    for raw in records:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-472 catalogue record malformed")
        stats = raw.get("statistics")
        if not isinstance(stats, Mapping):
            raise ValueError("DEC-472 catalogue statistics malformed")
        support = _nonnegative_int(
            stats.get("support"),
            field="DEC-472 record support",
        )
        total_support += support
        if support == 0:
            zero_support += 1
        if stats.get("evaluable") is True:
            evaluable += 1
    return {
        "directional_record_count": len(records),
        "evaluable_record_count": evaluable,
        "zero_support_record_count": zero_support,
        "total_support": total_support,
    }


def compile_cell_evidence(
    result: AnnualCatalogueCellResult,
    *,
    code_commit: str,
    processed_manifest_sha256: str,
    feature_manifest_sha256: str,
    outcome_manifest_sha256: str,
    feature_evidence_fingerprint: str,
    outcome_evidence_fingerprint: str,
) -> tuple[dict[str, object], bytes]:
    code_commit = _validate_commit(code_commit)
    for field, raw in (
        ("processed_manifest_sha256", processed_manifest_sha256),
        ("feature_manifest_sha256", feature_manifest_sha256),
        ("outcome_manifest_sha256", outcome_manifest_sha256),
        ("feature_evidence_fingerprint", feature_evidence_fingerprint),
        ("outcome_evidence_fingerprint", outcome_evidence_fingerprint),
    ):
        _validate_sha256(raw, field=field)

    payload_bytes = serialize_cell_catalogue(result)
    payload = json.loads(payload_bytes)
    counts = _summary_counts_from_payload(payload)
    evidence: dict[str, object] = {
        "evidence_version": ANNUAL_CATALOGUE_CELL_EVIDENCE_VERSION,
        "evidence_protocol": ANNUAL_CATALOGUE_CELL_EVIDENCE_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": SOURCE_MINER_DECISION,
        "miner_merge_sha": SOURCE_MINER_MERGE_SHA,
        "miner_source_blob_sha": SOURCE_MINER_BLOB_SHA,
        "code_commit": code_commit,
        "annual_segment_label": result.annual_segment_label,
        "cell": {
            "symbol": result.symbol,
            "timeframe": result.timeframe,
            "horizon_minutes": result.horizon_minutes,
        },
        "processed_manifest_sha256": processed_manifest_sha256,
        "feature_manifest_sha256": feature_manifest_sha256,
        "outcome_manifest_sha256": outcome_manifest_sha256,
        "feature_evidence_fingerprint": feature_evidence_fingerprint,
        "outcome_evidence_fingerprint": outcome_evidence_fingerprint,
        "catalogue_payload_sha256": _sha256_bytes(payload_bytes),
        "catalogue_payload_size_bytes": len(payload_bytes),
        **counts,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": (
            HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED
        ),
        "historical_result_production_authorized": (
            HISTORICAL_RESULT_PRODUCTION_AUTHORIZED
        ),
        "cross_year_result_production_authorized": (
            CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED
        ),
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }
    evidence["evidence_fingerprint"] = _sha256_bytes(_canonical_json(evidence))
    validate_cell_evidence(evidence, payload_bytes)
    return evidence, payload_bytes


def _cell_identity_from_evidence(
    value: Mapping[str, object],
) -> tuple[str, str, str, int]:
    segment = value.get("annual_segment_label")
    cell = value.get("cell")
    if not isinstance(segment, str) or not isinstance(cell, Mapping):
        raise ValueError("DEC-472 cell evidence identity malformed")
    symbol = cell.get("symbol")
    timeframe = cell.get("timeframe")
    horizon = cell.get("horizon_minutes")
    identity = (segment, symbol, timeframe, horizon)
    if identity not in EXPECTED_ANNUAL_CELL_IDENTITIES:
        raise ValueError("DEC-472 annual cell identity mismatch")
    return (
        segment,
        str(symbol),
        str(timeframe),
        int(horizon),
    )


def _validate_statistics(
    raw: object,
) -> tuple[int, bool]:
    if not isinstance(raw, Mapping):
        raise ValueError("DEC-472 record statistics malformed")
    support = _nonnegative_int(raw.get("support"), field="DEC-472 record support")
    evaluable = raw.get("evaluable")
    if not isinstance(evaluable, bool):
        raise ValueError("DEC-472 record evaluable flag must be boolean")
    if evaluable != (support >= MIN_ANNUAL_EVALUABLE_SUPPORT):
        raise ValueError("DEC-472 record evaluable/support relation mismatch")
    metric_names = (
        "mean_net_pips_0p5",
        "median_net_pips_0p5",
        "win_rate_0p5",
        "mean_net_pips_1p0",
        "median_net_pips_1p0",
    )
    if support == 0:
        if any(raw.get(name) is not None for name in metric_names):
            raise ValueError("DEC-472 zero-support metrics must be null")
    else:
        for name in metric_names:
            _finite_float(raw.get(name), field=f"DEC-472 {name}")
        win_rate = float(raw["win_rate_0p5"])
        if not 0.0 <= win_rate <= 1.0:
            raise ValueError("DEC-472 win rate outside [0,1]")
    return support, evaluable


def _validate_catalogue_payload(
    payload: Mapping[str, object],
    evidence: Mapping[str, object],
) -> dict[str, int]:
    expected_top = {
        "catalogue_payload_version",
        "protocol_version",
        "protocol_fingerprint",
        "miner_decision",
        "annual_segment_label",
        "cell",
        "feature_observation_count",
        "outcome_observation_count",
        "directional_record_count",
        "records",
    }
    if set(payload) != expected_top:
        raise ValueError("DEC-472 catalogue payload key inventory mismatch")
    if payload.get("catalogue_payload_version") != 1:
        raise ValueError("DEC-472 catalogue payload version mismatch")
    if payload.get("protocol_version") != ANNUAL_CATALOGUE_PROTOCOL_VERSION:
        raise ValueError("DEC-472 catalogue protocol version mismatch")
    if payload.get("protocol_fingerprint") != protocol_fingerprint():
        raise ValueError("DEC-472 catalogue protocol fingerprint mismatch")
    if payload.get("miner_decision") != SOURCE_MINER_DECISION:
        raise ValueError("DEC-472 catalogue miner decision mismatch")

    identity = _cell_identity_from_evidence(evidence)
    segment, symbol, timeframe, horizon = identity
    if payload.get("annual_segment_label") != segment:
        raise ValueError("DEC-472 catalogue annual segment mismatch")
    if payload.get("cell") != {
        "symbol": symbol,
        "timeframe": timeframe,
        "horizon_minutes": horizon,
    }:
        raise ValueError("DEC-472 catalogue cell identity mismatch")
    _nonnegative_int(
        payload.get("feature_observation_count"),
        field="DEC-472 feature observation count",
    )
    _nonnegative_int(
        payload.get("outcome_observation_count"),
        field="DEC-472 outcome observation count",
    )

    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("DEC-472 catalogue records must be a list")
    if len(records) != DIRECTIONAL_RECORDS_PER_ANNUAL_CELL:
        raise ValueError("DEC-472 catalogue directional record count mismatch")
    if payload.get("directional_record_count") != len(records):
        raise ValueError("DEC-472 catalogue record-count field mismatch")

    expected_patterns = enumerate_pattern_definitions()
    expected_index = [
        (pattern, direction)
        for pattern in expected_patterns
        for direction in DIRECTIONS
    ]
    if len(expected_index) != len(records):
        raise ValueError("DEC-472 expected record universe drift")

    seen_annual: set[str] = set()
    seen_canonical: set[str] = set()
    evaluable_count = 0
    zero_support_count = 0
    total_support = 0

    for raw, (pattern, direction) in zip(records, expected_index):
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-472 catalogue record malformed")
        expected_keys = {
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
        }
        if set(raw) != expected_keys:
            raise ValueError("DEC-472 catalogue record key inventory mismatch")
        if (
            raw.get("annual_segment_label") != segment
            or raw.get("symbol") != symbol
            or raw.get("timeframe") != timeframe
            or raw.get("horizon_minutes") != horizon
            or raw.get("direction") != direction
            or raw.get("family") != pattern.family
            or raw.get("dimensions") != list(pattern.dimensions)
            or raw.get("states") != list(pattern.states)
            or raw.get("lag_minutes") != pattern.lag_minutes
        ):
            raise ValueError("DEC-472 catalogue record semantic identity mismatch")

        canonical = canonical_pattern_fingerprint(
            pattern=pattern,
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon,
            direction=direction,
        )
        if raw.get("canonical_pattern_fingerprint") != canonical:
            raise ValueError("DEC-472 canonical pattern fingerprint mismatch")
        annual_id = annual_record_identity(
            canonical_pattern_fingerprint_value=canonical,
            annual_segment_label=segment,
        )
        if raw.get("annual_record_id") != annual_id:
            raise ValueError("DEC-472 annual record identity mismatch")
        _validate_sha256(
            raw.get("event_fingerprint"),
            field="DEC-472 event fingerprint",
        )
        if annual_id in seen_annual or canonical in seen_canonical:
            raise ValueError("DEC-472 duplicate catalogue identity")
        seen_annual.add(annual_id)
        seen_canonical.add(canonical)

        support, evaluable = _validate_statistics(raw.get("statistics"))
        total_support += support
        if support == 0:
            zero_support_count += 1
        if evaluable:
            evaluable_count += 1

    for index in range(0, len(records), len(DIRECTIONS)):
        pair = records[index : index + len(DIRECTIONS)]
        event_fingerprints = {
            item.get("event_fingerprint")
            for item in pair
            if isinstance(item, Mapping)
        }
        if len(event_fingerprints) != 1:
            raise ValueError("DEC-472 direction pair event fingerprint mismatch")

    return {
        "directional_record_count": len(records),
        "evaluable_record_count": evaluable_count,
        "zero_support_record_count": zero_support_count,
        "total_support": total_support,
    }


def validate_cell_evidence(
    value: Mapping[str, object],
    catalogue_payload_bytes: bytes,
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="DEC-472 cell evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-472 cell evidence fingerprint mismatch")

    expected = {
        "evidence_version": ANNUAL_CATALOGUE_CELL_EVIDENCE_VERSION,
        "evidence_protocol": ANNUAL_CATALOGUE_CELL_EVIDENCE_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": SOURCE_MINER_DECISION,
        "miner_merge_sha": SOURCE_MINER_MERGE_SHA,
        "miner_source_blob_sha": SOURCE_MINER_BLOB_SHA,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-472 cell evidence {field} mismatch")

    _validate_commit(value.get("code_commit"))
    for field in (
        "processed_manifest_sha256",
        "feature_manifest_sha256",
        "outcome_manifest_sha256",
        "feature_evidence_fingerprint",
        "outcome_evidence_fingerprint",
    ):
        _validate_sha256(value.get(field), field=field)
    _cell_identity_from_evidence(value)

    if not isinstance(catalogue_payload_bytes, bytes):
        raise ValueError("DEC-472 catalogue payload must be bytes")
    if value.get("catalogue_payload_size_bytes") != len(catalogue_payload_bytes):
        raise ValueError("DEC-472 catalogue payload size mismatch")
    if value.get("catalogue_payload_sha256") != _sha256_bytes(
        catalogue_payload_bytes
    ):
        raise ValueError("DEC-472 catalogue payload sha256 mismatch")
    try:
        payload = json.loads(catalogue_payload_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("DEC-472 catalogue payload JSON malformed") from exc
    if not isinstance(payload, Mapping):
        raise ValueError("DEC-472 catalogue payload must be an object")
    counts = _validate_catalogue_payload(payload, value)
    for field, expected_value in counts.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-472 cell evidence {field} mismatch")

    for field in (
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
        "cross_year_result_production_authorized",
        "strategy_v1_synthesis_authorized",
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
            raise ValueError(f"DEC-472 cell evidence {field} must remain false")
    return value


@dataclass(frozen=True, slots=True)
class ValidatedAnnualCellSummary:
    annual_segment_label: str
    symbol: str
    timeframe: str
    horizon_minutes: int
    code_commit: str
    evidence_fingerprint: str
    catalogue_payload_sha256: str
    processed_manifest_sha256: str
    feature_manifest_sha256: str
    outcome_manifest_sha256: str
    feature_evidence_fingerprint: str
    outcome_evidence_fingerprint: str
    directional_record_count: int
    evaluable_record_count: int
    zero_support_record_count: int
    total_support: int

    def __post_init__(self) -> None:
        if (
            self.annual_segment_label,
            self.symbol,
            self.timeframe,
            self.horizon_minutes,
        ) not in EXPECTED_ANNUAL_CELL_IDENTITIES:
            raise ValueError("DEC-472 validated summary cell identity mismatch")
        _validate_commit(self.code_commit)
        for field in (
            "evidence_fingerprint",
            "catalogue_payload_sha256",
            "processed_manifest_sha256",
            "feature_manifest_sha256",
            "outcome_manifest_sha256",
            "feature_evidence_fingerprint",
            "outcome_evidence_fingerprint",
        ):
            _validate_sha256(getattr(self, field), field=f"DEC-472 summary {field}")
        if self.directional_record_count != DIRECTIONAL_RECORDS_PER_ANNUAL_CELL:
            raise ValueError("DEC-472 validated summary record-count drift")
        if not 0 <= self.evaluable_record_count <= self.directional_record_count:
            raise ValueError("DEC-472 validated summary evaluable count drift")
        if not 0 <= self.zero_support_record_count <= self.directional_record_count:
            raise ValueError("DEC-472 validated summary zero-support count drift")
        if self.total_support < 0:
            raise ValueError("DEC-472 validated summary total support drift")


def validated_cell_summary(
    evidence: Mapping[str, object],
    catalogue_payload_bytes: bytes,
) -> ValidatedAnnualCellSummary:
    validate_cell_evidence(evidence, catalogue_payload_bytes)
    segment, symbol, timeframe, horizon = _cell_identity_from_evidence(evidence)
    return ValidatedAnnualCellSummary(
        annual_segment_label=segment,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon,
        code_commit=str(evidence["code_commit"]),
        evidence_fingerprint=str(evidence["evidence_fingerprint"]),
        catalogue_payload_sha256=str(evidence["catalogue_payload_sha256"]),
        processed_manifest_sha256=str(evidence["processed_manifest_sha256"]),
        feature_manifest_sha256=str(evidence["feature_manifest_sha256"]),
        outcome_manifest_sha256=str(evidence["outcome_manifest_sha256"]),
        feature_evidence_fingerprint=str(evidence["feature_evidence_fingerprint"]),
        outcome_evidence_fingerprint=str(evidence["outcome_evidence_fingerprint"]),
        directional_record_count=int(evidence["directional_record_count"]),
        evaluable_record_count=int(evidence["evaluable_record_count"]),
        zero_support_record_count=int(evidence["zero_support_record_count"]),
        total_support=int(evidence["total_support"]),
    )


def _summary_payload(value: ValidatedAnnualCellSummary) -> dict[str, object]:
    return {
        "annual_segment_label": value.annual_segment_label,
        "symbol": value.symbol,
        "timeframe": value.timeframe,
        "horizon_minutes": value.horizon_minutes,
        "code_commit": value.code_commit,
        "evidence_fingerprint": value.evidence_fingerprint,
        "catalogue_payload_sha256": value.catalogue_payload_sha256,
        "processed_manifest_sha256": value.processed_manifest_sha256,
        "feature_manifest_sha256": value.feature_manifest_sha256,
        "outcome_manifest_sha256": value.outcome_manifest_sha256,
        "feature_evidence_fingerprint": value.feature_evidence_fingerprint,
        "outcome_evidence_fingerprint": value.outcome_evidence_fingerprint,
        "directional_record_count": value.directional_record_count,
        "evaluable_record_count": value.evaluable_record_count,
        "zero_support_record_count": value.zero_support_record_count,
        "total_support": value.total_support,
    }


def compile_aggregate_evidence(
    summaries: Sequence[ValidatedAnnualCellSummary],
    *,
    code_commit: str,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    if len(summaries) != EXPECTED_ANNUAL_CELL_COUNT:
        raise ValueError(
            f"DEC-472 aggregate requires exactly {EXPECTED_ANNUAL_CELL_COUNT} annual cells"
        )
    seen: dict[tuple[str, str, str, int], ValidatedAnnualCellSummary] = {}
    for summary in summaries:
        identity = (
            summary.annual_segment_label,
            summary.symbol,
            summary.timeframe,
            summary.horizon_minutes,
        )
        if identity in seen:
            raise ValueError(f"DEC-472 duplicate annual cell: {identity!r}")
        if summary.code_commit != code_commit:
            raise ValueError("DEC-472 aggregate cell code commit mismatch")
        seen[identity] = summary
    if set(seen) != set(EXPECTED_ANNUAL_CELL_IDENTITIES):
        raise ValueError("DEC-472 aggregate annual cell universe mismatch")

    ordered = [seen[identity] for identity in EXPECTED_ANNUAL_CELL_IDENTITIES]
    cells = [_summary_payload(item) for item in ordered]
    segment_summaries = []
    for segment in collection_segments():
        segment_cells = [
            item for item in ordered if item.annual_segment_label == segment.label
        ]
        segment_summaries.append(
            {
                "annual_segment_label": segment.label,
                "annual_cell_count": len(segment_cells),
                "directional_record_count": sum(
                    item.directional_record_count for item in segment_cells
                ),
                "evaluable_record_count": sum(
                    item.evaluable_record_count for item in segment_cells
                ),
                "zero_support_record_count": sum(
                    item.zero_support_record_count for item in segment_cells
                ),
                "total_support": sum(item.total_support for item in segment_cells),
            }
        )

    evidence: dict[str, object] = {
        "evidence_version": ANNUAL_CATALOGUE_AGGREGATE_EVIDENCE_VERSION,
        "evidence_protocol": ANNUAL_CATALOGUE_AGGREGATE_EVIDENCE_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": SOURCE_MINER_DECISION,
        "miner_merge_sha": SOURCE_MINER_MERGE_SHA,
        "miner_source_blob_sha": SOURCE_MINER_BLOB_SHA,
        "code_commit": code_commit,
        "annual_segment_count": len(collection_segments()),
        "annual_cell_count": len(cells),
        "directional_record_count": sum(
            item.directional_record_count for item in ordered
        ),
        "evaluable_record_count": sum(
            item.evaluable_record_count for item in ordered
        ),
        "zero_support_record_count": sum(
            item.zero_support_record_count for item in ordered
        ),
        "total_support": sum(item.total_support for item in ordered),
        "segment_summaries": segment_summaries,
        "cells": cells,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": (
            HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED
        ),
        "historical_result_production_authorized": (
            HISTORICAL_RESULT_PRODUCTION_AUTHORIZED
        ),
        "cross_year_result_production_authorized": (
            CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED
        ),
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }
    evidence["evidence_fingerprint"] = _sha256_bytes(_canonical_json(evidence))
    validate_aggregate_evidence(evidence, expected_summaries=ordered)
    return evidence


def _summary_from_mapping(raw: Mapping[str, object]) -> ValidatedAnnualCellSummary:
    return ValidatedAnnualCellSummary(
        annual_segment_label=str(raw.get("annual_segment_label")),
        symbol=str(raw.get("symbol")),
        timeframe=str(raw.get("timeframe")),
        horizon_minutes=int(raw.get("horizon_minutes")),
        code_commit=str(raw.get("code_commit")),
        evidence_fingerprint=str(raw.get("evidence_fingerprint")),
        catalogue_payload_sha256=str(raw.get("catalogue_payload_sha256")),
        processed_manifest_sha256=str(raw.get("processed_manifest_sha256")),
        feature_manifest_sha256=str(raw.get("feature_manifest_sha256")),
        outcome_manifest_sha256=str(raw.get("outcome_manifest_sha256")),
        feature_evidence_fingerprint=str(raw.get("feature_evidence_fingerprint")),
        outcome_evidence_fingerprint=str(raw.get("outcome_evidence_fingerprint")),
        directional_record_count=int(raw.get("directional_record_count")),
        evaluable_record_count=int(raw.get("evaluable_record_count")),
        zero_support_record_count=int(raw.get("zero_support_record_count")),
        total_support=int(raw.get("total_support")),
    )


def validate_aggregate_evidence(
    value: Mapping[str, object],
    *,
    expected_summaries: Sequence[ValidatedAnnualCellSummary] | None = None,
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="DEC-472 aggregate evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-472 aggregate evidence fingerprint mismatch")

    expected = {
        "evidence_version": ANNUAL_CATALOGUE_AGGREGATE_EVIDENCE_VERSION,
        "evidence_protocol": ANNUAL_CATALOGUE_AGGREGATE_EVIDENCE_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "protocol_fingerprint": protocol_fingerprint(),
        "miner_decision": SOURCE_MINER_DECISION,
        "miner_merge_sha": SOURCE_MINER_MERGE_SHA,
        "miner_source_blob_sha": SOURCE_MINER_BLOB_SHA,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-472 aggregate evidence {field} mismatch")
    code_commit = _validate_commit(value.get("code_commit"))

    cells = value.get("cells")
    if not isinstance(cells, list) or len(cells) != EXPECTED_ANNUAL_CELL_COUNT:
        raise ValueError(
            f"DEC-472 aggregate requires exactly {EXPECTED_ANNUAL_CELL_COUNT} annual cells"
        )
    summaries: list[ValidatedAnnualCellSummary] = []
    for raw in cells:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-472 aggregate cell summary malformed")
        summaries.append(_summary_from_mapping(raw))
    identities = [
        (
            item.annual_segment_label,
            item.symbol,
            item.timeframe,
            item.horizon_minutes,
        )
        for item in summaries
    ]
    if identities != list(EXPECTED_ANNUAL_CELL_IDENTITIES):
        raise ValueError("DEC-472 aggregate annual cell ordering/universe mismatch")
    if any(item.code_commit != code_commit for item in summaries):
        raise ValueError("DEC-472 aggregate cell code commit mismatch")

    expected_totals = {
        "annual_segment_count": len(collection_segments()),
        "annual_cell_count": EXPECTED_ANNUAL_CELL_COUNT,
        "directional_record_count": EXPECTED_TOTAL_DIRECTIONAL_RECORDS,
        "evaluable_record_count": sum(item.evaluable_record_count for item in summaries),
        "zero_support_record_count": sum(
            item.zero_support_record_count for item in summaries
        ),
        "total_support": sum(item.total_support for item in summaries),
    }
    for field, expected_value in expected_totals.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-472 aggregate {field} mismatch")

    segment_summaries = value.get("segment_summaries")
    if not isinstance(segment_summaries, list) or len(segment_summaries) != len(
        collection_segments()
    ):
        raise ValueError("DEC-472 aggregate segment summary inventory mismatch")
    for raw, segment in zip(segment_summaries, collection_segments()):
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-472 aggregate segment summary malformed")
        members = [
            item for item in summaries if item.annual_segment_label == segment.label
        ]
        expected_segment = {
            "annual_segment_label": segment.label,
            "annual_cell_count": len(SYMBOLS) * len(TIMEFRAMES) * len(HORIZONS_MINUTES),
            "directional_record_count": sum(
                item.directional_record_count for item in members
            ),
            "evaluable_record_count": sum(
                item.evaluable_record_count for item in members
            ),
            "zero_support_record_count": sum(
                item.zero_support_record_count for item in members
            ),
            "total_support": sum(item.total_support for item in members),
        }
        if dict(raw) != expected_segment:
            raise ValueError("DEC-472 aggregate segment summary mismatch")

    if expected_summaries is not None:
        expected_payloads = [_summary_payload(item) for item in expected_summaries]
        if cells != expected_payloads:
            raise ValueError("DEC-472 aggregate validated-cell binding mismatch")

    for field in (
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
        "cross_year_result_production_authorized",
        "strategy_v1_synthesis_authorized",
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
            raise ValueError(f"DEC-472 aggregate evidence {field} must remain false")
    return value


def evidence_contract_payload() -> dict[str, object]:
    return {
        "decision": ANNUAL_CATALOGUE_EVIDENCE_DECISION,
        "experiment_id": EXPERIMENT_ID,
        "source_miner_decision": SOURCE_MINER_DECISION,
        "source_miner_merge_sha": SOURCE_MINER_MERGE_SHA,
        "source_miner_blob_sha": SOURCE_MINER_BLOB_SHA,
        "cell_evidence_protocol": ANNUAL_CATALOGUE_CELL_EVIDENCE_PROTOCOL,
        "aggregate_evidence_protocol": ANNUAL_CATALOGUE_AGGREGATE_EVIDENCE_PROTOCOL,
        "expected_annual_segment_count": len(collection_segments()),
        "expected_annual_cell_count": EXPECTED_ANNUAL_CELL_COUNT,
        "directional_records_per_annual_cell": DIRECTIONAL_RECORDS_PER_ANNUAL_CELL,
        "expected_total_directional_records": EXPECTED_TOTAL_DIRECTIONAL_RECORDS,
        "cell_payload_requires_full_record_semantic_validation": True,
        "aggregate_requires_exact_12_by_18_matrix": True,
        "aggregate_full_replay_must_bind_validated_cell_summaries": True,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
        "historical_result_production_authorized": HISTORICAL_RESULT_PRODUCTION_AUTHORIZED,
        "cross_year_result_production_authorized": CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED,
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_FULL_HISTORY_LOADER",
    }


if ANNUAL_CATALOGUE_MINER_DECISION != SOURCE_MINER_DECISION:
    raise ValueError("DEC-472 source miner decision drift")
if EXPECTED_ANNUAL_CELL_COUNT != 216:
    raise ValueError("DEC-472 annual cell matrix drift")
if DIRECTIONAL_RECORDS_PER_ANNUAL_CELL != 4970:
    raise ValueError("DEC-472 annual directional record count drift")
if EXPECTED_TOTAL_DIRECTIONAL_RECORDS != 1073520:
    raise ValueError("DEC-472 total directional record count drift")


__all__ = [
    "ANNUAL_CATALOGUE_AGGREGATE_EVIDENCE_PROTOCOL",
    "ANNUAL_CATALOGUE_CELL_EVIDENCE_PROTOCOL",
    "ANNUAL_CATALOGUE_EVIDENCE_DECISION",
    "DIRECTIONAL_RECORDS_PER_ANNUAL_CELL",
    "EXPECTED_ANNUAL_CELL_COUNT",
    "EXPECTED_ANNUAL_CELL_IDENTITIES",
    "EXPECTED_TOTAL_DIRECTIONAL_RECORDS",
    "ValidatedAnnualCellSummary",
    "cell_catalogue_payload",
    "compile_aggregate_evidence",
    "compile_cell_evidence",
    "evidence_contract_payload",
    "serialize_cell_catalogue",
    "validate_aggregate_evidence",
    "validate_cell_evidence",
    "validated_cell_summary",
]
