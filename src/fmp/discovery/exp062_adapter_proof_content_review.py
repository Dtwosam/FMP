from __future__ import annotations

from typing import Mapping, Sequence

from .exp062_adapter_probe import (
    EXPECTED_CELLS,
    compile_exp062_adapter_probe,
    validate_exp062_adapter_probe_cell,
)
from .exp062_adapter_proof_review import (
    EXP062_ADAPTER_PROOF_REVIEW_DECISION,
    EXP062_ADAPTER_PROOF_REVIEW_VERSION,
)


EXP062_ADAPTER_PROOF_CONTENT_REVIEW_DECISION = "DEC-296"
EXP062_ADAPTER_PROOF_CONTENT_REVIEW_VERSION = (
    "fmp-exp062-adapter-proof-content-review-v1"
)

HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
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
        "decision": EXP062_ADAPTER_PROOF_REVIEW_DECISION,
        "version": EXP062_ADAPTER_PROOF_REVIEW_VERSION,
        "stage": "EXP062_ADAPTER_PROOF_SUCCESS_COMPLETE_REVIEW_REQUIRED",
        "proof_run_head_sha": expected_head_sha,
        "proof_run_attempt": 1,
        "proof_success_complete": True,
        "materialized_job_count": 10,
        "artifact_count": 10,
        "expected_success_job_count": 10,
        "expected_success_artifact_count": 10,
        "aggregate_content_review_required": True,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
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
                f"DEC-296 terminal review {field} mismatch"
            )
    run_id = value.get("proof_run_id")
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        raise ValueError("DEC-296 proof run id is invalid")
    return value


def review_exp062_adapter_proof_content(
    *,
    terminal_review: Mapping[str, object],
    cell_probes: Sequence[Mapping[str, object]],
    aggregate_proof: Mapping[str, object],
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

    if len(cell_probes) != len(EXPECTED_CELLS):
        raise ValueError("DEC-296 requires exactly nine cell probes")

    validated = [
        dict(validate_exp062_adapter_probe_cell(item))
        for item in cell_probes
    ]
    identities = {
        (str(item["symbol"]), str(item["timeframe"]))
        for item in validated
    }
    if identities != set(EXPECTED_CELLS):
        raise ValueError("DEC-296 cell probe inventory mismatch")
    if {str(item["code_commit"]) for item in validated} != {
        expected_head_sha
    }:
        raise ValueError("DEC-296 cell probe commit mismatch")

    recompiled = compile_exp062_adapter_probe(
        validated,
        code_commit=expected_head_sha,
    )
    if dict(aggregate_proof) != recompiled:
        raise ValueError(
            "DEC-296 aggregate proof does not match deterministic recompilation"
        )

    total_nonfinite = int(recompiled["total_raw_nonfinite_value_count"])
    if total_nonfinite <= 0:
        raise ValueError(
            "DEC-296 proof must exercise at least one real non-finite value"
        )

    per_feature: dict[str, int] = {}
    cells_with_nonfinite = 0
    ordered_cells: list[dict[str, object]] = []
    for item in sorted(
        validated,
        key=lambda value: (
            str(value["symbol"]),
            str(value["timeframe"]),
        ),
    ):
        counts = item["raw_nonfinite_by_feature"]
        if not isinstance(counts, Mapping):
            raise ValueError("DEC-296 non-finite count map is malformed")
        cell_total = int(item["raw_nonfinite_value_count"])
        if cell_total > 0:
            cells_with_nonfinite += 1
        for name, raw_count in counts.items():
            count = int(raw_count)
            per_feature[str(name)] = per_feature.get(str(name), 0) + count
        ordered_cells.append(
            {
                "symbol": item["symbol"],
                "timeframe": item["timeframe"],
                "feature_row_count": item["feature_row_count"],
                "outcome_row_count": item["outcome_row_count"],
                "raw_nonfinite_value_count": cell_total,
            }
        )

    if sum(per_feature.values()) != total_nonfinite:
        raise ValueError("DEC-296 non-finite totals do not reconcile")

    return {
        "decision": EXP062_ADAPTER_PROOF_CONTENT_REVIEW_DECISION,
        "version": EXP062_ADAPTER_PROOF_CONTENT_REVIEW_VERSION,
        "stage": "EXP062_ADAPTER_REPAIR_REAL_DATA_PROOF_VERIFIED",
        "proof_run_id": terminal["proof_run_id"],
        "proof_run_head_sha": expected_head_sha,
        "verified_cell_probe_count": len(validated),
        "aggregate_proof_verified": True,
        "all_nine_real_data_adapter_probes_successful": True,
        "total_feature_row_count": recompiled["total_feature_row_count"],
        "total_outcome_row_count": recompiled["total_outcome_row_count"],
        "total_raw_nonfinite_value_count": total_nonfinite,
        "cells_with_raw_nonfinite_values": cells_with_nonfinite,
        "raw_nonfinite_by_feature": dict(sorted(per_feature.items())),
        "cells": ordered_cells,
        "repair_meaning": (
            "NONFINITE_MISSING_VALUES_NORMALIZED_WITHOUT_MINING"
        ),
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
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
    "EXP062_ADAPTER_PROOF_CONTENT_REVIEW_DECISION",
    "EXP062_ADAPTER_PROOF_CONTENT_REVIEW_VERSION",
    "review_exp062_adapter_proof_content",
]
