from __future__ import annotations

import math
from pathlib import Path
from typing import Mapping, Sequence

from .historical_failure_result_decision import (
    EXP061_HISTORICAL_FAILURE_FREEZE_DECISION,
)
from .exp062_nonfinite_feature_adapter import (
    EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION,
    EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION,
    adapt_market_learning_cell,
)
from .pattern_protocol import CONTINUOUS_FEATURES, SYMBOLS, TIMEFRAMES
from .range_limited_loader import (
    EXP061_SELECTED_MONTH_COUNT,
    load_verified_exp061_cell_from_indexes,
)


EXP062_ADAPTER_PROBE_DECISION = "DEC-294"
EXP062_ADAPTER_PROBE_VERSION = "fmp-exp062-real-data-adapter-probe-v1"

EXPECTED_CELLS = tuple(
    (symbol, timeframe)
    for symbol in SYMBOLS
    for timeframe in TIMEFRAMES
)

HISTORICAL_SOURCE_PROBE_AUTHORIZED = True
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


def _raw_nonfinite_counts(frame: object) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name in CONTINUOUS_FEATURES:
        values = frame[name].to_list()
        count = 0
        for value in values:
            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and not math.isfinite(float(value))
            ):
                count += 1
        counts[name] = count
    return counts


def probe_exp062_adapter_cell(
    *,
    feature_root: Path,
    outcome_root: Path,
    feature_evidence_path: Path,
    outcome_evidence_path: Path,
    symbol: str,
    timeframe: str,
    code_commit: str,
) -> dict[str, object]:
    if len(code_commit) != 40:
        raise ValueError("DEC-294 code_commit must be a 40-character commit")
    try:
        int(code_commit, 16)
    except ValueError as exc:
        raise ValueError("DEC-294 code_commit must be hexadecimal") from exc

    loaded = load_verified_exp061_cell_from_indexes(
        feature_root=Path(feature_root),
        outcome_root=Path(outcome_root),
        feature_evidence_path=Path(feature_evidence_path),
        outcome_evidence_path=Path(outcome_evidence_path),
        symbol=symbol,
        timeframe=timeframe,
    )
    raw_nonfinite = _raw_nonfinite_counts(loaded.feature_frame)

    adapted = adapt_market_learning_cell(
        feature_frame=loaded.feature_frame,
        outcome_frame=loaded.outcome_frame,
        symbol=symbol,
        timeframe=timeframe,
    )

    if len(adapted.feature_observations) != loaded.feature_frame.height:
        raise ValueError("DEC-294 adapted feature row count mismatch")
    if len(adapted.outcome_observations) != loaded.outcome_frame.height:
        raise ValueError("DEC-294 adapted outcome row count mismatch")
    if len(loaded.selected_feature_artifacts) != EXP061_SELECTED_MONTH_COUNT:
        raise ValueError("DEC-294 feature partition count mismatch")
    if len(loaded.selected_outcome_artifacts) != EXP061_SELECTED_MONTH_COUNT:
        raise ValueError("DEC-294 outcome partition count mismatch")

    return {
        "decision": EXP062_ADAPTER_PROBE_DECISION,
        "version": EXP062_ADAPTER_PROBE_VERSION,
        "experiment_id": "EXP-20260927-062",
        "repair_decision": EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION,
        "repair_version": EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION,
        "predecessor_failure_decision": (
            EXP061_HISTORICAL_FAILURE_FREEZE_DECISION
        ),
        "code_commit": code_commit.lower(),
        "symbol": symbol,
        "timeframe": timeframe,
        "feature_row_count": loaded.feature_frame.height,
        "outcome_row_count": loaded.outcome_frame.height,
        "adapted_feature_observation_count": len(
            adapted.feature_observations
        ),
        "adapted_outcome_observation_count": len(
            adapted.outcome_observations
        ),
        "processed_manifest_sha256": loaded.processed_manifest_sha256,
        "feature_manifest_sha256": loaded.feature_manifest_sha256,
        "outcome_manifest_sha256": loaded.outcome_manifest_sha256,
        "feature_evidence_fingerprint": loaded.feature_evidence_fingerprint,
        "outcome_evidence_fingerprint": loaded.outcome_evidence_fingerprint,
        "selected_feature_partition_count": len(
            loaded.selected_feature_artifacts
        ),
        "selected_outcome_partition_count": len(
            loaded.selected_outcome_artifacts
        ),
        "raw_nonfinite_by_feature": raw_nonfinite,
        "raw_nonfinite_value_count": sum(raw_nonfinite.values()),
        "adapter_probe_success": True,
        "historical_source_probe_authorized": True,
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


def validate_exp062_adapter_probe_cell(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    if value.get("decision") != EXP062_ADAPTER_PROBE_DECISION:
        raise ValueError("DEC-294 cell probe decision mismatch")
    if value.get("version") != EXP062_ADAPTER_PROBE_VERSION:
        raise ValueError("DEC-294 cell probe version mismatch")
    if value.get("experiment_id") != "EXP-20260927-062":
        raise ValueError("DEC-294 experiment identity mismatch")
    cell = (value.get("symbol"), value.get("timeframe"))
    if cell not in EXPECTED_CELLS:
        raise ValueError("DEC-294 cell identity mismatch")
    if value.get("repair_decision") != "DEC-293":
        raise ValueError("DEC-294 repair decision mismatch")
    if value.get("predecessor_failure_decision") != "DEC-292":
        raise ValueError("DEC-294 predecessor failure decision mismatch")

    feature_rows = value.get("feature_row_count")
    outcome_rows = value.get("outcome_row_count")
    if not isinstance(feature_rows, int) or feature_rows <= 0:
        raise ValueError("DEC-294 feature row count must be positive")
    if not isinstance(outcome_rows, int) or outcome_rows <= 0:
        raise ValueError("DEC-294 outcome row count must be positive")
    if value.get("adapted_feature_observation_count") != feature_rows:
        raise ValueError("DEC-294 adapted feature count mismatch")
    if value.get("adapted_outcome_observation_count") != outcome_rows:
        raise ValueError("DEC-294 adapted outcome count mismatch")
    if value.get("selected_feature_partition_count") != 96:
        raise ValueError("DEC-294 feature partition count mismatch")
    if value.get("selected_outcome_partition_count") != 96:
        raise ValueError("DEC-294 outcome partition count mismatch")

    counts = value.get("raw_nonfinite_by_feature")
    if not isinstance(counts, Mapping) or set(counts) != set(CONTINUOUS_FEATURES):
        raise ValueError("DEC-294 raw nonfinite feature inventory mismatch")
    total = 0
    for name in CONTINUOUS_FEATURES:
        count = counts.get(name)
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError(
                f"DEC-294 raw nonfinite count malformed for {name}"
            )
        total += count
    if value.get("raw_nonfinite_value_count") != total:
        raise ValueError("DEC-294 raw nonfinite total mismatch")

    if value.get("adapter_probe_success") is not True:
        raise ValueError("DEC-294 cell probe must succeed")
    if value.get("historical_source_probe_authorized") is not True:
        raise ValueError("DEC-294 source probe authorization mismatch")
    for field in (
        "historical_discovery_execution_authorized",
        "discovery_result_authorized",
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
            raise ValueError(f"DEC-294 {field} must remain false")
    return value


def compile_exp062_adapter_probe(
    cells: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    if len(cells) != len(EXPECTED_CELLS):
        raise ValueError("DEC-294 aggregate requires exactly nine probes")

    validated = [
        dict(validate_exp062_adapter_probe_cell(item))
        for item in cells
    ]
    identities = {
        (str(item["symbol"]), str(item["timeframe"]))
        for item in validated
    }
    if identities != set(EXPECTED_CELLS):
        raise ValueError("DEC-294 aggregate cell inventory mismatch")
    if {str(item["code_commit"]) for item in validated} != {code_commit}:
        raise ValueError("DEC-294 aggregate code commit mismatch")

    normalized_total = sum(
        int(item["raw_nonfinite_value_count"])
        for item in validated
    )
    if normalized_total <= 0:
        raise ValueError(
            "DEC-294 real-data proof must encounter the repaired nonfinite case"
        )

    ordered = sorted(
        validated,
        key=lambda item: (
            str(item["symbol"]),
            str(item["timeframe"]),
        ),
    )
    return {
        "decision": EXP062_ADAPTER_PROBE_DECISION,
        "version": EXP062_ADAPTER_PROBE_VERSION,
        "experiment_id": "EXP-20260927-062",
        "code_commit": code_commit,
        "cell_count": len(ordered),
        "cells": ordered,
        "total_feature_row_count": sum(
            int(item["feature_row_count"]) for item in ordered
        ),
        "total_outcome_row_count": sum(
            int(item["outcome_row_count"]) for item in ordered
        ),
        "total_raw_nonfinite_value_count": normalized_total,
        "all_nine_real_data_adapter_probes_successful": True,
        "historical_source_probe_authorized": True,
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
    "EXPECTED_CELLS",
    "EXP062_ADAPTER_PROBE_DECISION",
    "EXP062_ADAPTER_PROBE_VERSION",
    "compile_exp062_adapter_probe",
    "probe_exp062_adapter_cell",
    "validate_exp062_adapter_probe_cell",
]
