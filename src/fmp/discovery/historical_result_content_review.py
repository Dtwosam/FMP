from __future__ import annotations

from typing import Mapping, Sequence

from .market_learning_adapter import validate_cell_evidence
from .run_contract import (
    EXPECTED_CELL_COUNT,
    compile_aggregate_evidence,
    validate_aggregate_evidence,
)
from .historical_result_review_contract import (
    EXP061_HISTORICAL_TERMINAL_REVIEW_DECISION,
    EXP061_HISTORICAL_TERMINAL_REVIEW_VERSION,
)


EXP061_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION = "DEC-291"
EXP061_HISTORICAL_RESULT_CONTENT_REVIEW_VERSION = (
    "fmp-exp061-historical-result-content-review-v1"
)

CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
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


def _validate_terminal_review(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> Mapping[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    expected = {
        "decision": EXP061_HISTORICAL_TERMINAL_REVIEW_DECISION,
        "version": EXP061_HISTORICAL_TERMINAL_REVIEW_VERSION,
        "stage": "EXP061_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED",
        "historical_run_head_sha": expected_head_sha,
        "historical_run_number": 2,
        "historical_run_attempt": 1,
        "historical_result_slot_consumed": True,
        "historical_result_success_complete": True,
        "materialized_job_count": 20,
        "artifact_count": 20,
        "github_unexpanded_matrix_placeholder_present": False,
        "aggregate_result_content_review_required": True,
        "partial_evidence_may_be_preserved": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
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
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(
                f"DEC-291 terminal review {field} mismatch"
            )
    run_id = value.get("historical_run_id")
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        raise ValueError("DEC-291 historical run id is invalid")
    return value


def review_successful_historical_result_content(
    *,
    terminal_review: Mapping[str, object],
    cell_evidence: Sequence[Mapping[str, object]],
    aggregate_evidence: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    terminal = _validate_terminal_review(
        terminal_review,
        expected_head_sha=expected_head_sha,
    )

    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError(
            f"DEC-291 requires exactly {EXPECTED_CELL_COUNT} cell evidence objects"
        )

    validated_cells = [
        dict(validate_cell_evidence(item))
        for item in cell_evidence
    ]
    for item in validated_cells:
        if item.get("code_commit") != expected_head_sha:
            raise ValueError("DEC-291 cell evidence code commit mismatch")

    validated_aggregate = dict(
        validate_aggregate_evidence(aggregate_evidence)
    )
    if validated_aggregate.get("code_commit") != expected_head_sha:
        raise ValueError("DEC-291 aggregate code commit mismatch")

    recompiled = compile_aggregate_evidence(
        validated_cells,
        code_commit=expected_head_sha,
    )
    if validated_aggregate != recompiled:
        raise ValueError(
            "DEC-291 aggregate does not match deterministic cell recompilation"
        )

    shortlist_count = int(validated_aggregate["discovery_shortlist_count"])
    frozen_count = int(validated_aggregate["confirmation_frozen_count"])
    accepted_count = int(validated_aggregate["validation_accepted_count"])

    cells = validated_aggregate.get("cells")
    if not isinstance(cells, list) or len(cells) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-291 aggregate cell summaries are incomplete")

    accepted_by_cell: list[dict[str, object]] = []
    accepted_fingerprints: list[str] = []
    for raw in cells:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-291 aggregate cell summary is malformed")
        accepted = raw.get("validation_accepted_fingerprints")
        if not isinstance(accepted, list):
            raise ValueError(
                "DEC-291 validation accepted fingerprint inventory is malformed"
            )
        if accepted:
            summary = {
                "symbol": raw.get("symbol"),
                "timeframe": raw.get("timeframe"),
                "horizon_minutes": raw.get("horizon_minutes"),
                "validated_pattern_fingerprints": list(accepted),
            }
            accepted_by_cell.append(summary)
            accepted_fingerprints.extend(str(item) for item in accepted)

    if accepted_count != len(accepted_fingerprints):
        raise ValueError("DEC-291 accepted pattern count mismatch")
    if len(accepted_fingerprints) != len(set(accepted_fingerprints)):
        raise ValueError(
            "DEC-291 validated pattern fingerprints must be globally unique"
        )

    stage = (
        "EXP061_HISTORICAL_RESULT_REVIEWED_VALIDATED_PATTERN_HYPOTHESES_PRESENT"
        if accepted_count
        else "EXP061_HISTORICAL_RESULT_REVIEWED_NO_VALIDATED_PATTERNS"
    )

    return {
        "decision": EXP061_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION,
        "version": EXP061_HISTORICAL_RESULT_CONTENT_REVIEW_VERSION,
        "stage": stage,
        "historical_run_id": terminal["historical_run_id"],
        "historical_run_head_sha": expected_head_sha,
        "historical_run_number": 2,
        "historical_run_attempt": 1,
        "historical_result_slot_consumed": True,
        "verified_cell_evidence_count": len(validated_cells),
        "aggregate_evidence_verified": True,
        "aggregate_evidence_fingerprint": validated_aggregate[
            "evidence_fingerprint"
        ],
        "discovery_shortlist_count": shortlist_count,
        "confirmation_frozen_count": frozen_count,
        "validation_accepted_count": accepted_count,
        "validated_pattern_hypotheses_present": accepted_count > 0,
        "validated_pattern_fingerprints": sorted(accepted_fingerprints),
        "validated_patterns_by_cell": accepted_by_cell,
        "output_meaning": "PATTERN_HYPOTHESIS_NOT_EXECUTABLE_STRATEGY",
        "untouched_oos": False,
        "reserved_robustness_opened": False,
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
    "EXP061_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION",
    "EXP061_HISTORICAL_RESULT_CONTENT_REVIEW_VERSION",
    "review_successful_historical_result_content",
]
