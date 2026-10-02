from __future__ import annotations

import hashlib
import json
from typing import Mapping, Sequence

from .annual_pattern_catalogue_evidence import (
    ANNUAL_CATALOGUE_CELL_EVIDENCE_PROTOCOL,
    ANNUAL_CATALOGUE_EVIDENCE_DECISION,
    DIRECTIONAL_RECORDS_PER_ANNUAL_CELL,
    ValidatedAnnualCellSummary,
)
from .annual_pattern_catalogue_method import collection_segments
from .annual_pattern_catalogue_protocol import (
    EVIDENCE_LABEL,
    EXPERIMENT_ID,
    protocol_fingerprint,
)
from .pattern_protocol import HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


ANNUAL_SEGMENT_FREEZE_DECISION = "DEC-477"
ANNUAL_SEGMENT_FREEZE_VERSION = 1
ANNUAL_SEGMENT_FREEZE_PROTOCOL = "fmp-annual-pattern-catalogue-segment-freeze-v1"
SOURCE_WORKFLOW_PLAN_DECISION = "DEC-476"
SOURCE_WORKFLOW_PLAN_MERGE_SHA = "23ca37a74296a8ad0ac5e4cd1775c3b76714f698"
SOURCE_CELL_EVIDENCE_DECISION = ANNUAL_CATALOGUE_EVIDENCE_DECISION

EXPECTED_CELLS_PER_SEGMENT = len(SYMBOLS) * len(TIMEFRAMES) * len(HORIZONS_MINUTES)
EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT = (
    EXPECTED_CELLS_PER_SEGMENT * DIRECTIONAL_RECORDS_PER_ANNUAL_CELL
)

HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
NEXT_SEGMENT_EXECUTION_AUTHORIZED = False
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
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
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
    return value.lower()


def _segment_labels() -> tuple[str, ...]:
    return tuple(segment.label for segment in collection_segments())


def _expected_identities(
    annual_segment_label: str,
) -> tuple[tuple[str, str, str, int], ...]:
    if annual_segment_label not in _segment_labels():
        raise ValueError("DEC-477 annual segment label drift")
    return tuple(
        (annual_segment_label, symbol, timeframe, horizon)
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
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


def _canonicalize_summaries(
    summaries: Sequence[ValidatedAnnualCellSummary],
    *,
    annual_segment_label: str,
    code_commit: str,
) -> tuple[ValidatedAnnualCellSummary, ...]:
    expected = _expected_identities(annual_segment_label)
    if len(summaries) != EXPECTED_CELLS_PER_SEGMENT:
        raise ValueError(
            f"DEC-477 annual freeze requires exactly {EXPECTED_CELLS_PER_SEGMENT} cells"
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
            raise ValueError(f"DEC-477 duplicate annual cell: {identity!r}")
        if summary.code_commit != code_commit:
            raise ValueError("DEC-477 annual freeze cell code commit mismatch")
        seen[identity] = summary
    if set(seen) != set(expected):
        raise ValueError("DEC-477 annual freeze cell universe mismatch")
    return tuple(seen[identity] for identity in expected)


def compile_annual_segment_freeze(
    summaries: Sequence[ValidatedAnnualCellSummary],
    *,
    annual_segment_label: str,
    code_commit: str,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    ordered = _canonicalize_summaries(
        summaries,
        annual_segment_label=annual_segment_label,
        code_commit=code_commit,
    )
    cells = [_summary_payload(item) for item in ordered]
    evidence: dict[str, object] = {
        "evidence_version": ANNUAL_SEGMENT_FREEZE_VERSION,
        "evidence_protocol": ANNUAL_SEGMENT_FREEZE_PROTOCOL,
        "decision": ANNUAL_SEGMENT_FREEZE_DECISION,
        "experiment_id": EXPERIMENT_ID,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "source_workflow_plan_decision": SOURCE_WORKFLOW_PLAN_DECISION,
        "source_workflow_plan_merge_sha": SOURCE_WORKFLOW_PLAN_MERGE_SHA,
        "source_cell_evidence_decision": SOURCE_CELL_EVIDENCE_DECISION,
        "source_cell_evidence_protocol": ANNUAL_CATALOGUE_CELL_EVIDENCE_PROTOCOL,
        "protocol_fingerprint": protocol_fingerprint(),
        "annual_segment_label": annual_segment_label,
        "code_commit": code_commit,
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
        "cells": cells,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
        "historical_result_production_authorized": HISTORICAL_RESULT_PRODUCTION_AUTHORIZED,
        "next_segment_execution_authorized": NEXT_SEGMENT_EXECUTION_AUTHORIZED,
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
    }
    evidence["evidence_fingerprint"] = _sha256_bytes(_canonical_json(evidence))
    validate_annual_segment_freeze(evidence, expected_summaries=ordered)
    return evidence


def validate_annual_segment_freeze(
    value: Mapping[str, object],
    *,
    expected_summaries: Sequence[ValidatedAnnualCellSummary] | None = None,
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="DEC-477 evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-477 evidence fingerprint mismatch")

    if value.get("evidence_version") != ANNUAL_SEGMENT_FREEZE_VERSION:
        raise ValueError("DEC-477 evidence version mismatch")
    if value.get("evidence_protocol") != ANNUAL_SEGMENT_FREEZE_PROTOCOL:
        raise ValueError("DEC-477 evidence protocol mismatch")
    if value.get("decision") != ANNUAL_SEGMENT_FREEZE_DECISION:
        raise ValueError("DEC-477 decision mismatch")
    if value.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("DEC-477 experiment identity mismatch")
    if value.get("evidence_label") != EVIDENCE_LABEL:
        raise ValueError("DEC-477 evidence label mismatch")
    if value.get("untouched_oos") is not False:
        raise ValueError("DEC-477 cannot claim untouched OOS")
    if value.get("source_workflow_plan_decision") != SOURCE_WORKFLOW_PLAN_DECISION:
        raise ValueError("DEC-477 source workflow plan mismatch")
    if value.get("source_workflow_plan_merge_sha") != SOURCE_WORKFLOW_PLAN_MERGE_SHA:
        raise ValueError("DEC-477 source workflow plan merge mismatch")
    if value.get("source_cell_evidence_decision") != SOURCE_CELL_EVIDENCE_DECISION:
        raise ValueError("DEC-477 source cell evidence decision mismatch")
    if value.get("source_cell_evidence_protocol") != ANNUAL_CATALOGUE_CELL_EVIDENCE_PROTOCOL:
        raise ValueError("DEC-477 source cell evidence protocol mismatch")
    if value.get("protocol_fingerprint") != protocol_fingerprint():
        raise ValueError("DEC-477 catalogue protocol fingerprint mismatch")

    annual_segment_label = value.get("annual_segment_label")
    if not isinstance(annual_segment_label, str):
        raise ValueError("DEC-477 annual segment label malformed")
    code_commit = _validate_commit(value.get("code_commit"))
    expected = _expected_identities(annual_segment_label)

    raw_cells = value.get("cells")
    if not isinstance(raw_cells, list) or len(raw_cells) != EXPECTED_CELLS_PER_SEGMENT:
        raise ValueError("DEC-477 annual freeze cell inventory mismatch")
    summaries: list[ValidatedAnnualCellSummary] = []
    for raw in raw_cells:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-477 annual freeze cell summary malformed")
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
    if identities != list(expected):
        raise ValueError("DEC-477 annual freeze cell ordering/universe mismatch")
    if any(item.code_commit != code_commit for item in summaries):
        raise ValueError("DEC-477 annual freeze cell code commit mismatch")

    expected_totals = {
        "annual_cell_count": EXPECTED_CELLS_PER_SEGMENT,
        "directional_record_count": EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT,
        "evaluable_record_count": sum(item.evaluable_record_count for item in summaries),
        "zero_support_record_count": sum(
            item.zero_support_record_count for item in summaries
        ),
        "total_support": sum(item.total_support for item in summaries),
    }
    for field, expected_value in expected_totals.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-477 {field} mismatch")

    if expected_summaries is not None:
        ordered = _canonicalize_summaries(
            expected_summaries,
            annual_segment_label=annual_segment_label,
            code_commit=code_commit,
        )
        if raw_cells != [_summary_payload(item) for item in ordered]:
            raise ValueError("DEC-477 validated-cell binding mismatch")

    for field in (
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
        "next_segment_execution_authorized",
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
            raise ValueError(f"DEC-477 evidence {field} must remain false")
    return value


def segment_freeze_contract_payload() -> dict[str, object]:
    return {
        "decision": ANNUAL_SEGMENT_FREEZE_DECISION,
        "version": ANNUAL_SEGMENT_FREEZE_VERSION,
        "protocol": ANNUAL_SEGMENT_FREEZE_PROTOCOL,
        "source_workflow_plan_decision": SOURCE_WORKFLOW_PLAN_DECISION,
        "source_workflow_plan_merge_sha": SOURCE_WORKFLOW_PLAN_MERGE_SHA,
        "source_cell_evidence_decision": SOURCE_CELL_EVIDENCE_DECISION,
        "annual_segment_count": len(collection_segments()),
        "cells_per_segment": EXPECTED_CELLS_PER_SEGMENT,
        "directional_records_per_segment": EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT,
        "requires_validated_dec472_cell_summaries": True,
        "annual_freeze_required_before_next_segment": True,
        "annual_freeze_required_before_cross_year_comparison": True,
        "next_segment_execution_authorized": NEXT_SEGMENT_EXECUTION_AUTHORIZED,
        "cross_year_result_production_authorized": CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED,
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_SOURCE",
    }


if EXPECTED_CELLS_PER_SEGMENT != 18:
    raise ValueError("DEC-477 per-segment cell count drift")
if EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT != 89460:
    raise ValueError("DEC-477 per-segment directional record count drift")


__all__ = [
    "ANNUAL_SEGMENT_FREEZE_DECISION",
    "ANNUAL_SEGMENT_FREEZE_PROTOCOL",
    "ANNUAL_SEGMENT_FREEZE_VERSION",
    "EXPECTED_CELLS_PER_SEGMENT",
    "EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT",
    "compile_annual_segment_freeze",
    "segment_freeze_contract_payload",
    "validate_annual_segment_freeze",
]
