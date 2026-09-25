from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Iterable

from .model_successor_fit_temporal_residual_lower_tail_utility_result_decision import (
    FAILURE_CLASSIFICATION as DEC218_FAILURE_CLASSIFICATION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_DECISION,
    REVIEWED_MODEL_RUN_ID,
)


FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION = (
    "DEC-219"
)

DEC218_MERGED_COMMIT = "2f2171f0166f22c19482a905d6906d1cfd672275"
DEC218_RESULT_DECISION_BLOB_SHA = (
    "75fc25ae97c03730ab75a3036059f761d8234630"
)
EXP056_TRAINING_CORE_BLOB_SHA = (
    "c472ed48e7b79d22056d43deb0fe09166ccf34c9"
)
EXP055_PREDECESSOR_TRAINING_CORE_BLOB_SHA = (
    "c9517b7516940c78621448088c3933aa1c57e281"
)
EXP054_BASE_TRAINING_CORE_BLOB_SHA = (
    "4f3f189c104d41352433397421f021896c03a5e9"
)

IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION = (
    "EXP056_IMPLEMENTATION_FAILED_BEFORE_EVIDENCE_DUE_INTERMEDIATE_"
    "PREDECESSOR_EXPORT_DRIFT"
)

OBSERVED_RUNTIME_MISSING_EXPORTS = (
    "FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL",
    "MIN_STABILITY_WINDOW_CANDIDATE_SHARE",
)

EXPECTED_STATIC_MISSING_PREDECESSOR_EXPORTS = (
    "FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE",
    "FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL",
    "FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL",
    "FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL",
    "MIN_STABILITY_WINDOW_CANDIDATE_SHARE",
    "ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE",
    "ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE",
)

IMPLEMENTATION_REPAIR_RULE = (
    "for a future successor implementation only, replace each of the seven "
    "invalid EXP-056 accesses to inherited EXP-054 constants from "
    "_predecessor.<name> with _base.<name>; retain legitimate EXP-055 "
    "breadth-specific accesses on _predecessor and do not change protocol "
    "semantics, model family, data, chronology, ranking, budgets, financial "
    "gates, temporal-stability gates, validation, or holdout rules"
)

EXP056_RERUN_AUTHORIZED = False
EXP056_REPLACEMENT_RUN_AUTHORIZED = False
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
                        "DEC-219 source audit forbids wildcard imports"
                    )
                names.add(alias.asname or alias.name)
    return names


def _direct_attribute_names(source: str, root_name: str) -> set[str]:
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == root_name
        ):
            names.add(node.attr)
    return names


def analyze_exp056_dependency_export_drift(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    lower_path = (
        root
        / "src/fmp/market_learning/"
        "model_successor_fit_temporal_residual_lower_tail_utility_training.py"
    )
    predecessor_path = (
        root
        / "src/fmp/market_learning/"
        "model_successor_fit_temporal_residual_breadth_utility_training.py"
    )
    base_path = (
        root
        / "src/fmp/market_learning/"
        "model_successor_fit_temporal_residual_bound_utility_training.py"
    )
    decision_path = (
        root
        / "src/fmp/market_learning/"
        "model_successor_fit_temporal_residual_lower_tail_utility_result_decision.py"
    )

    expected_blobs = {
        decision_path: DEC218_RESULT_DECISION_BLOB_SHA,
        lower_path: EXP056_TRAINING_CORE_BLOB_SHA,
        predecessor_path: EXP055_PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        base_path: EXP054_BASE_TRAINING_CORE_BLOB_SHA,
    }
    for path, expected in expected_blobs.items():
        if not path.is_file():
            raise ValueError(f"DEC-219 missing frozen source: {path}")
        actual = _git_blob_sha(path)
        if actual != expected:
            raise ValueError(
                f"DEC-219 frozen source blob mismatch: {actual} != {expected}"
            )

    lower_source = lower_path.read_text(encoding="utf-8")
    predecessor_source = predecessor_path.read_text(encoding="utf-8")
    base_source = base_path.read_text(encoding="utf-8")

    predecessor_accesses = _direct_attribute_names(
        lower_source,
        "_predecessor",
    )
    base_accesses = _direct_attribute_names(lower_source, "_base")
    predecessor_exports = _top_level_names(predecessor_source)
    base_exports = _top_level_names(base_source)

    missing_predecessor = tuple(
        sorted(predecessor_accesses - predecessor_exports)
    )
    missing_base = tuple(sorted(base_accesses - base_exports))
    expected_missing = tuple(
        sorted(EXPECTED_STATIC_MISSING_PREDECESSOR_EXPORTS)
    )
    if missing_predecessor != expected_missing:
        raise ValueError(
            "DEC-219 static missing-predecessor export inventory drift"
        )
    if missing_base:
        raise ValueError(
            "DEC-219 EXP-054 base dereference inventory is incomplete"
        )

    not_available_on_base = tuple(
        name
        for name in missing_predecessor
        if name not in base_exports
    )
    if not_available_on_base:
        raise ValueError(
            "DEC-219 missing predecessor exports are not all available on base"
        )

    observed = set(OBSERVED_RUNTIME_MISSING_EXPORTS)
    if not observed.issubset(set(missing_predecessor)):
        raise ValueError(
            "DEC-219 observed runtime failures are not explained by audit"
        )

    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_DECISION != (
        "DEC-218"
    ):
        raise ValueError("DEC-219 predecessor result decision drift")
    if REVIEWED_MODEL_RUN_ID != 36175841645:
        raise ValueError("DEC-219 predecessor failed-run identity drift")
    if DEC218_FAILURE_CLASSIFICATION != (
        "IMPLEMENTATION_DEPENDENCY_EXPORT_DRIFT_PREVENTED_ALL_EXP056_CELL_RESULTS"
    ):
        raise ValueError("DEC-219 predecessor failure classification drift")

    return {
        "diagnostic_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION
        ),
        "diagnostic_classification": IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION,
        "dec218_merged_commit": DEC218_MERGED_COMMIT,
        "reviewed_failed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "predecessor_result_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RESULT_DECISION
        ),
        "predecessor_failure_classification": DEC218_FAILURE_CLASSIFICATION,
        "exp056_training_core_blob_sha": EXP056_TRAINING_CORE_BLOB_SHA,
        "exp055_predecessor_training_core_blob_sha": (
            EXP055_PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "exp054_base_training_core_blob_sha": (
            EXP054_BASE_TRAINING_CORE_BLOB_SHA
        ),
        "direct_predecessor_dereference_count": len(predecessor_accesses),
        "direct_base_dereference_count": len(base_accesses),
        "static_missing_predecessor_exports": list(missing_predecessor),
        "static_missing_predecessor_export_count": len(missing_predecessor),
        "observed_runtime_missing_exports": list(
            OBSERVED_RUNTIME_MISSING_EXPORTS
        ),
        "latent_missing_export_count": (
            len(missing_predecessor) - len(observed)
        ),
        "all_missing_exports_available_on_base": True,
        "implementation_repair_rule": IMPLEMENTATION_REPAIR_RULE,
        "protocol_semantics_change_authorized": False,
        "exp056_rerun_authorized": EXP056_RERUN_AUTHORIZED,
        "exp056_replacement_run_authorized": (
            EXP056_REPLACEMENT_RUN_AUTHORIZED
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
    "DEC218_MERGED_COMMIT",
    "DEC218_RESULT_DECISION_BLOB_SHA",
    "EXP054_BASE_TRAINING_CORE_BLOB_SHA",
    "EXP055_PREDECESSOR_TRAINING_CORE_BLOB_SHA",
    "EXP056_REPLACEMENT_RUN_AUTHORIZED",
    "EXP056_RERUN_AUTHORIZED",
    "EXP056_TRAINING_CORE_BLOB_SHA",
    "EXPECTED_STATIC_MISSING_PREDECESSOR_EXPORTS",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION",
    "IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION",
    "IMPLEMENTATION_REPAIR_RULE",
    "OBSERVED_RUNTIME_MISSING_EXPORTS",
    "SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "SUCCESSOR_MODEL_FIT_AUTHORIZED",
    "SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED",
    "analyze_exp056_dependency_export_drift",
]
