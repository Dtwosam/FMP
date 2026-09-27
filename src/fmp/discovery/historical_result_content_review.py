from __future__ import annotations

from typing import Mapping, Sequence

from .market_learning_adapter import validate_cell_evidence
from .run_contract import (
    EXPECTED_CELL_COUNT,
    EXPECTED_CELLS,
    compile_aggregate_evidence,
    validate_aggregate_evidence,
)


EXP061_HISTORICAL_CONTENT_REVIEW_DECISION = "DEC-291"
EXP061_HISTORICAL_CONTENT_REVIEW_VERSION = (
    "fmp-exp061-historical-content-review-v1"
)

RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _cell_identity(value: Mapping[str, object]) -> tuple[str, str, int]:
    raw = value.get("cell")
    if not isinstance(raw, Mapping):
        raise ValueError("DEC-291 cell evidence is missing cell identity")
    identity = (
        raw.get("symbol"),
        raw.get("timeframe"),
        raw.get("horizon_minutes"),
    )
    if identity not in EXPECTED_CELLS:
        raise ValueError(f"DEC-291 unexpected cell identity: {identity!r}")
    return str(identity[0]), str(identity[1]), int(identity[2])


def review_historical_result_content(
    cell_evidence: Sequence[Mapping[str, object]],
    aggregate_evidence: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError(
            f"DEC-291 requires exactly {EXPECTED_CELL_COUNT} cell evidence objects"
        )

    validated_cells: list[Mapping[str, object]] = []
    seen: set[tuple[str, str, int]] = set()
    for raw in cell_evidence:
        validated = validate_cell_evidence(raw)
        if validated.get("code_commit") != expected_head_sha:
            raise ValueError("DEC-291 cell code commit mismatch")
        identity = _cell_identity(validated)
        if identity in seen:
            raise ValueError(f"DEC-291 duplicate cell evidence: {identity!r}")
        seen.add(identity)
        validated_cells.append(validated)

    if seen != set(EXPECTED_CELLS):
        raise ValueError("DEC-291 cell inventory is incomplete or unexpected")

    validated_aggregate = validate_aggregate_evidence(aggregate_evidence)
    if validated_aggregate.get("code_commit") != expected_head_sha:
        raise ValueError("DEC-291 aggregate code commit mismatch")

    recomputed = compile_aggregate_evidence(
        validated_cells,
        code_commit=expected_head_sha,
    )
    if dict(validated_aggregate) != recomputed:
        raise ValueError(
            "DEC-291 aggregate evidence differs from independent recomputation"
        )

    discovery_count = int(validated_aggregate["discovery_shortlist_count"])
    frozen_count = int(validated_aggregate["confirmation_frozen_count"])
    accepted_count = int(validated_aggregate["validation_accepted_count"])

    if not (0 <= accepted_count <= frozen_count <= discovery_count):
        raise ValueError("DEC-291 aggregate pattern counts are inconsistent")

    return {
        "decision": EXP061_HISTORICAL_CONTENT_REVIEW_DECISION,
        "version": EXP061_HISTORICAL_CONTENT_REVIEW_VERSION,
        "code_commit": expected_head_sha,
        "verified_cell_count": EXPECTED_CELL_COUNT,
        "aggregate_recomputed_exactly": True,
        "discovery_shortlist_count": discovery_count,
        "confirmation_frozen_count": frozen_count,
        "validation_accepted_count": accepted_count,
        "content_classification": (
            "HISTORICAL_CONTENT_VALID_WITH_VALIDATED_PATTERNS"
            if accepted_count > 0
            else "HISTORICAL_CONTENT_VALID_NO_VALIDATED_PATTERNS"
        ),
        "historical_result_content_validated": True,
        "historical_result_accepted": False,
        "pattern_hypotheses_accepted": False,
        "reviewed_result_decision_required": True,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "reserved_robustness_opened": False,
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


__all__ = [
    "EXP061_HISTORICAL_CONTENT_REVIEW_DECISION",
    "EXP061_HISTORICAL_CONTENT_REVIEW_VERSION",
    "review_historical_result_content",
]
