from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Iterable

from .model_successor_fit_temporal_residual_regime_balance_utility_result_decision import (
    FAILURE_CLASSIFICATION as DEC251_FAILURE_CLASSIFICATION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_DECISION,
    REVIEWED_MODEL_RUN_ID,
)


FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION = (
    "DEC-252"
)

DEC251_MERGED_COMMIT = "639fa26f841d0d3bb4c8577372a8539a0c0fd38f"
DEC251_RESULT_DECISION_BLOB_SHA = (
    "c8ca7143e687494b81205556af7e317ec69937fd"
)
EXP059_TRAINING_CORE_BLOB_SHA = (
    "4f99c1d0cb18551b67cc89357ad4a3940c190cd2"
)
EXP058_REGIME_FLOOR_TRAINING_CORE_BLOB_SHA = (
    "77f2010574b3d8ecc958930d5bfadf7ddb4f2231"
)
EXP057_LOWER_TAIL_REPAIR_TRAINING_CORE_BLOB_SHA = (
    "ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd"
)
EXP055_BREADTH_TRAINING_CORE_BLOB_SHA = (
    "c9517b7516940c78621448088c3933aa1c57e281"
)

IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION = (
    "EXP059_IMPLEMENTATION_FAILED_BEFORE_EVIDENCE_DUE_PREDECESSOR_DEPTH_DRIFT"
)

OBSERVED_RUNTIME_MISSING_EXPORT = "FIT_TEMPORAL_RESIDUAL_BREADTH_RULE"

EXPECTED_INVALID_BREADTH_ACCESS_NAMES = (
    "FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW",
    "FIT_TEMPORAL_RESIDUAL_BREADTH_RULE",
    "RESIDUAL_BREADTH_ELIGIBILITY_RULE",
    "RESIDUAL_BREADTH_POSITIVITY_RULE",
)

EXPECTED_INVALID_CHAIN_DEPTH = 2
EXPECTED_REPAIRED_CHAIN_DEPTH = 3

IMPLEMENTATION_REPAIR_RULE = (
    "for a future successor implementation only, replace the four EXP-059 "
    "breadth metadata accesses _predecessor._predecessor.<name> with "
    "_predecessor._predecessor._predecessor.<name>; retain every other "
    "regime-balance protocol, model, data, chronology, ranking, cutoff, "
    "financial-gate, temporal-stability, validation, and holdout rule unchanged"
)

EXP059_RERUN_AUTHORIZED = False
EXP059_REPLACEMENT_RUN_AUTHORIZED = False
SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = True
SUCCESSOR_MODEL_FIT_AUTHORIZED = False
SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def _bound_name(alias: ast.alias) -> str:
    if alias.asname:
        return alias.asname
    return alias.name.split(".", 1)[0]


def _assignment_names(target: ast.expr) -> Iterable[str]:
    if isinstance(target, ast.Name):
        yield target.id
    elif isinstance(target, (ast.Tuple, ast.List)):
        for item in target.elts:
            yield from _assignment_names(item)


def _top_level_names(source: str) -> set[str]:
    tree = ast.parse(source)
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                names.update(_assignment_names(target))
        elif isinstance(node, ast.AnnAssign):
            names.update(_assignment_names(node.target))
        elif isinstance(node, ast.Import):
            names.update(_bound_name(alias) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    raise ValueError(
                        "DEC-252 source audit forbids wildcard imports"
                    )
                names.add(alias.asname or alias.name)
    return names


def _attribute_chain(node: ast.Attribute) -> tuple[str, ...] | None:
    parts: list[str] = [node.attr]
    value: ast.expr = node.value
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if not isinstance(value, ast.Name):
        return None
    parts.append(value.id)
    return tuple(reversed(parts))


def _nested_predecessor_breadth_accesses(
    source: str,
) -> set[tuple[str, ...]]:
    tree = ast.parse(source)
    expected_names = set(EXPECTED_INVALID_BREADTH_ACCESS_NAMES)
    result: set[tuple[str, ...]] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        chain = _attribute_chain(node)
        if (
            chain is not None
            and len(chain) >= 3
            and chain[0] == "_predecessor"
            and chain[-1] in expected_names
        ):
            result.add(chain)
    return result


def analyze_exp059_predecessor_depth_drift(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    balance_path = (
        root
        / "src/fmp/market_learning/"
        "model_successor_fit_temporal_residual_regime_balance_utility_training.py"
    )
    floor_path = (
        root
        / "src/fmp/market_learning/"
        "model_successor_fit_temporal_residual_regime_floor_utility_training.py"
    )
    lower_tail_repair_path = (
        root
        / "src/fmp/market_learning/"
        "model_successor_fit_temporal_residual_lower_tail_utility_repair_training.py"
    )
    breadth_path = (
        root
        / "src/fmp/market_learning/"
        "model_successor_fit_temporal_residual_breadth_utility_training.py"
    )
    decision_path = (
        root
        / "src/fmp/market_learning/"
        "model_successor_fit_temporal_residual_regime_balance_utility_result_decision.py"
    )

    expected_blobs = {
        decision_path: DEC251_RESULT_DECISION_BLOB_SHA,
        balance_path: EXP059_TRAINING_CORE_BLOB_SHA,
        floor_path: EXP058_REGIME_FLOOR_TRAINING_CORE_BLOB_SHA,
        lower_tail_repair_path: EXP057_LOWER_TAIL_REPAIR_TRAINING_CORE_BLOB_SHA,
        breadth_path: EXP055_BREADTH_TRAINING_CORE_BLOB_SHA,
    }
    for path, expected in expected_blobs.items():
        if not path.is_file():
            raise ValueError(f"DEC-252 missing frozen source: {path}")
        actual = _git_blob_sha(path)
        if actual != expected:
            raise ValueError(
                f"DEC-252 frozen source blob mismatch: {actual} != {expected}"
            )

    balance_source = balance_path.read_text(encoding="utf-8")
    floor_source = floor_path.read_text(encoding="utf-8")
    lower_source = lower_tail_repair_path.read_text(encoding="utf-8")
    breadth_source = breadth_path.read_text(encoding="utf-8")

    expected_import_chain = (
        (
            balance_source,
            "from . import "
            "model_successor_fit_temporal_residual_regime_floor_utility_training "
            "as _predecessor",
        ),
        (
            floor_source,
            "from . import "
            "model_successor_fit_temporal_residual_lower_tail_utility_repair_training "
            "as _predecessor",
        ),
        (
            lower_source,
            "from . import "
            "model_successor_fit_temporal_residual_breadth_utility_training "
            "as _predecessor",
        ),
    )
    for source, marker in expected_import_chain:
        if marker not in source:
            raise ValueError("DEC-252 predecessor import-chain drift")

    accesses = _nested_predecessor_breadth_accesses(balance_source)
    expected_accesses = {
        ("_predecessor", "_predecessor", name)
        for name in EXPECTED_INVALID_BREADTH_ACCESS_NAMES
    }
    if accesses != expected_accesses:
        raise ValueError(
            "DEC-252 invalid breadth access inventory drift"
        )

    lower_exports = _top_level_names(lower_source)
    breadth_exports = _top_level_names(breadth_source)
    invalid_names = set(EXPECTED_INVALID_BREADTH_ACCESS_NAMES)

    unexpectedly_exported_by_lower = tuple(
        sorted(invalid_names & lower_exports)
    )
    if unexpectedly_exported_by_lower:
        raise ValueError(
            "DEC-252 lower-tail repair unexpectedly exports breadth metadata"
        )

    missing_on_breadth = tuple(
        sorted(invalid_names - breadth_exports)
    )
    if missing_on_breadth:
        raise ValueError(
            "DEC-252 breadth source does not export full repair inventory"
        )

    if OBSERVED_RUNTIME_MISSING_EXPORT not in invalid_names:
        raise ValueError(
            "DEC-252 runtime failure is not explained by static audit"
        )
    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_DECISION != (
        "DEC-251"
    ):
        raise ValueError("DEC-252 predecessor result decision drift")
    if REVIEWED_MODEL_RUN_ID != 36239443323:
        raise ValueError("DEC-252 predecessor failed-run identity drift")
    if DEC251_FAILURE_CLASSIFICATION != (
        "IMPLEMENTATION_DEPENDENCY_EXPORT_DEPTH_DRIFT_PREVENTED_ALL_EXP059_CELL_RESULTS"
    ):
        raise ValueError("DEC-252 predecessor failure classification drift")

    repaired_accesses = tuple(
        sorted(
            "_predecessor._predecessor._predecessor." + name
            for name in invalid_names
        )
    )

    return {
        "diagnostic_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION
        ),
        "diagnostic_classification": IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION,
        "dec251_merged_commit": DEC251_MERGED_COMMIT,
        "reviewed_failed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "predecessor_result_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_DECISION
        ),
        "predecessor_failure_classification": DEC251_FAILURE_CLASSIFICATION,
        "exp059_training_core_blob_sha": EXP059_TRAINING_CORE_BLOB_SHA,
        "exp058_regime_floor_training_core_blob_sha": (
            EXP058_REGIME_FLOOR_TRAINING_CORE_BLOB_SHA
        ),
        "exp057_lower_tail_repair_training_core_blob_sha": (
            EXP057_LOWER_TAIL_REPAIR_TRAINING_CORE_BLOB_SHA
        ),
        "exp055_breadth_training_core_blob_sha": (
            EXP055_BREADTH_TRAINING_CORE_BLOB_SHA
        ),
        "invalid_breadth_access_count": len(accesses),
        "invalid_breadth_access_names": list(
            sorted(EXPECTED_INVALID_BREADTH_ACCESS_NAMES)
        ),
        "invalid_chain_depth": EXPECTED_INVALID_CHAIN_DEPTH,
        "repaired_chain_depth": EXPECTED_REPAIRED_CHAIN_DEPTH,
        "observed_runtime_missing_export": OBSERVED_RUNTIME_MISSING_EXPORT,
        "repaired_breadth_accesses": list(repaired_accesses),
        "implementation_repair_rule": IMPLEMENTATION_REPAIR_RULE,
        "protocol_semantics_change_authorized": False,
        "exp059_rerun_authorized": EXP059_RERUN_AUTHORIZED,
        "exp059_replacement_run_authorized": (
            EXP059_REPLACEMENT_RUN_AUTHORIZED
        ),
        "successor_protocol_source_open_authorized": (
            SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED
        ),
        "successor_model_fit_authorized": SUCCESSOR_MODEL_FIT_AUTHORIZED,
        "successor_historical_result_execution_authorized": (
            SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED
        ),
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "shadow_authorized": SHADOW_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


__all__ = [
    "DEC251_MERGED_COMMIT",
    "DEC251_RESULT_DECISION_BLOB_SHA",
    "EXPECTED_INVALID_BREADTH_ACCESS_NAMES",
    "EXP055_BREADTH_TRAINING_CORE_BLOB_SHA",
    "EXP057_LOWER_TAIL_REPAIR_TRAINING_CORE_BLOB_SHA",
    "EXP058_REGIME_FLOOR_TRAINING_CORE_BLOB_SHA",
    "EXP059_REPLACEMENT_RUN_AUTHORIZED",
    "EXP059_RERUN_AUTHORIZED",
    "EXP059_TRAINING_CORE_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION",
    "IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION",
    "IMPLEMENTATION_REPAIR_RULE",
    "OBSERVED_RUNTIME_MISSING_EXPORT",
    "SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "SUCCESSOR_MODEL_FIT_AUTHORIZED",
    "SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED",
    "analyze_exp059_predecessor_depth_drift",
]
