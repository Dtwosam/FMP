from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from types import MappingProxyType

from .model_protocol import (
    CONFIDENCE_THRESHOLDS,
    DIAGNOSTIC_SCENARIOS,
    FIT_SPLIT,
    GATE_REQUIREMENTS,
    HIST_GRADIENT_BOOSTING_CONFIG,
    HOLDOUT_GATE_SCENARIOS,
    LOGISTIC_REGRESSION_CONFIG,
    MIN_DIRECTIONAL_CANDIDATES,
    MODEL_CELLS,
    MODEL_FAMILIES,
    MODEL_HORIZONS_MINUTES,
    MODEL_INPUT_COLUMNS,
    MODEL_PROTOCOL_DECISION,
    MODEL_PROTOCOL_VERSION,
    MODEL_SYMBOLS,
    MODEL_TIMEFRAMES,
    PROTOCOL_SPLITS,
    RETROSPECTIVE_HOLDOUT_SPLIT,
    SCIKIT_LEARN_VERSION,
    SELECTION_GATE_SCENARIOS,
    SELECTION_SPLIT,
    SELECTION_TIE_BREAK,
    TARGET_CLASSES,
    TARGET_COLUMN,
    TARGET_SLIPPAGE_PIPS,
    VALIDATION_GATE_SCENARIOS,
    VALIDATION_SPLIT,
    protocol_fingerprint,
)


SUCCESSOR_EXPERIMENT_ID = "EXP-20260923-045"
SUCCESSOR_PROTOCOL_VERSION = "fmp-exp045-model-protocol-v1"
SUCCESSOR_PROTOCOL_DECISION = "DEC-095"

PREDECESSOR_EXPERIMENT_ID = "EXP-20260923-044"
PREDECESSOR_FAILURE_REVIEW_DECISION = "DEC-094"
PREDECESSOR_FAILED_MODEL_RUN_ID = 35891605645
PREDECESSOR_FAILED_MODEL_HEAD_SHA = (
    "e97fa03d0e94fd505d0f926eb730e01a41947880"
)
BASE_PROTOCOL_FINGERPRINT = (
    "1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

FAMILY_FIT_ATTEMPTS = 1
LOGISTIC_NONCONVERGENCE_POLICY = MappingProxyType(
    {
        "warning_type": "sklearn.exceptions.ConvergenceWarning",
        "family_status": "FAILED_NON_CONVERGENCE",
        "failure_reason": "LBFGS_MAX_ITER_REACHED",
        "variant_status": "FAMILY_UNAVAILABLE",
        "selection_gate_passed": False,
        "retry_authorized": False,
        "solver_fallback_authorized": False,
        "max_iter_change_authorized": False,
        "preprocessing_change_authorized": False,
        "cell_may_continue_with_other_frozen_family": True,
    }
)
OTHER_FAMILY_FIT_FAILURE_POLICY = "FAIL_CELL"
ALL_FAMILIES_UNAVAILABLE_STATUS = "NO_MODEL_FAMILY_AVAILABLE"
NO_FINANCIAL_CHALLENGER_STATUS = "NO_MODEL_CHALLENGER"

PAIR_RESULT_UPLOAD_ALWAYS = True
PAIR_RESULT_INCLUDE_HIDDEN_FILES = True
PAIR_RESULT_MISSING_FILE_POLICY = "WARN_AND_PRESERVE_JOB_FAILURE"
AGGREGATE_RESULT_INCLUDE_HIDDEN_FILES = True
AGGREGATE_REQUIRES_ALL_CELLS = True

MODEL_PROTOCOL_RESULT_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
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


def validate_base_protocol_identity() -> None:
    if MODEL_PROTOCOL_DECISION != "DEC-088":
        raise ValueError("EXP-045 base model-protocol decision drift")
    if MODEL_PROTOCOL_VERSION != "fmp-exp044-model-protocol-v1":
        raise ValueError("EXP-045 base model-protocol version drift")
    actual = protocol_fingerprint()
    if actual != BASE_PROTOCOL_FINGERPRINT:
        raise ValueError(
            "EXP-045 base model-protocol fingerprint drift: "
            f"{actual} != {BASE_PROTOCOL_FINGERPRINT}"
        )


def successor_protocol_payload() -> dict[str, object]:
    validate_base_protocol_identity()
    return {
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_version": SUCCESSOR_PROTOCOL_VERSION,
        "protocol_decision": SUCCESSOR_PROTOCOL_DECISION,
        "predecessor": {
            "experiment_id": PREDECESSOR_EXPERIMENT_ID,
            "failure_review_decision": PREDECESSOR_FAILURE_REVIEW_DECISION,
            "failed_model_run_id": PREDECESSOR_FAILED_MODEL_RUN_ID,
            "failed_model_head_sha": PREDECESSOR_FAILED_MODEL_HEAD_SHA,
            "base_protocol_fingerprint": BASE_PROTOCOL_FINGERPRINT,
            "prior_result_informed": PRIOR_RESULT_INFORMED,
            "untouched_oos": UNTOUCHED_OOS,
        },
        "universe": {
            "symbols": list(MODEL_SYMBOLS),
            "timeframes": list(MODEL_TIMEFRAMES),
            "horizons_minutes": list(MODEL_HORIZONS_MINUTES),
            "cell_count": len(MODEL_CELLS),
        },
        "inputs": {
            "columns": list(MODEL_INPUT_COLUMNS),
            "column_count": len(MODEL_INPUT_COLUMNS),
        },
        "target": {
            "column": TARGET_COLUMN,
            "slippage_pips": TARGET_SLIPPAGE_PIPS,
            "classes": list(TARGET_CLASSES),
        },
        "chronology": {
            "splits": [asdict(split) for split in PROTOCOL_SPLITS],
            "fit_split": asdict(FIT_SPLIT),
            "selection_split": asdict(SELECTION_SPLIT),
            "validation_split": asdict(VALIDATION_SPLIT),
            "retrospective_holdout_split": asdict(
                RETROSPECTIVE_HOLDOUT_SPLIT
            ),
            "no_refit_after_fit": True,
            "untouched_oos": False,
        },
        "model_families": {
            "families": list(MODEL_FAMILIES),
            "scikit_learn_version": SCIKIT_LEARN_VERSION,
            "logistic_regression": dict(LOGISTIC_REGRESSION_CONFIG),
            "hist_gradient_boosting": dict(
                HIST_GRADIENT_BOOSTING_CONFIG
            ),
            "fit_attempts_per_family": FAMILY_FIT_ATTEMPTS,
        },
        "family_failure_policy": {
            "logistic_nonconvergence": dict(
                LOGISTIC_NONCONVERGENCE_POLICY
            ),
            "other_family_fit_failure": (
                OTHER_FAMILY_FIT_FAILURE_POLICY
            ),
            "all_families_unavailable_status": (
                ALL_FAMILIES_UNAVAILABLE_STATUS
            ),
            "no_financial_challenger_status": (
                NO_FINANCIAL_CHALLENGER_STATUS
            ),
            "failed_family_variant_slots_preserved": True,
            "selection_uses_only_fitted_families": True,
        },
        "selection": {
            "confidence_thresholds": list(
                CONFIDENCE_THRESHOLDS
            ),
            "minimum_directional_candidates": (
                MIN_DIRECTIONAL_CANDIDATES
            ),
            "gate_scenarios": list(
                SELECTION_GATE_SCENARIOS
            ),
            "gate_requirements": list(GATE_REQUIREMENTS),
            "tie_break": list(SELECTION_TIE_BREAK),
        },
        "validation": {
            "gate_scenarios": list(
                VALIDATION_GATE_SCENARIOS
            ),
            "diagnostic_scenarios": list(
                DIAGNOSTIC_SCENARIOS
            ),
        },
        "retrospective_holdout": {
            "gate_scenarios": list(HOLDOUT_GATE_SCENARIOS),
            "diagnostic_scenarios": list(
                DIAGNOSTIC_SCENARIOS
            ),
            "evidence_is_retrospective": True,
        },
        "evidence_persistence": {
            "pair_result_upload_always": (
                PAIR_RESULT_UPLOAD_ALWAYS
            ),
            "pair_result_include_hidden_files": (
                PAIR_RESULT_INCLUDE_HIDDEN_FILES
            ),
            "pair_result_missing_file_policy": (
                PAIR_RESULT_MISSING_FILE_POLICY
            ),
            "aggregate_include_hidden_files": (
                AGGREGATE_RESULT_INCLUDE_HIDDEN_FILES
            ),
            "aggregate_requires_all_cells": (
                AGGREGATE_REQUIRES_ALL_CELLS
            ),
        },
        "authorization": {
            "model_protocol_result_authorized": (
                MODEL_PROTOCOL_RESULT_AUTHORIZED
            ),
            "model_fit_authorized": MODEL_FIT_AUTHORIZED,
            "promotion_authorized": PROMOTION_AUTHORIZED,
            "shadow_authorized": SHADOW_AUTHORIZED,
            "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
            "broker_mutation_authorized": (
                BROKER_MUTATION_AUTHORIZED
            ),
            "live_order_authorized": LIVE_ORDER_AUTHORIZED,
            "real_money_authorized": REAL_MONEY_AUTHORIZED,
            "trading_authorized": TRADING_AUTHORIZED,
        },
    }


def successor_protocol_fingerprint() -> str:
    return hashlib.sha256(
        _canonical_json(successor_protocol_payload())
    ).hexdigest()


__all__ = [
    "AGGREGATE_REQUIRES_ALL_CELLS",
    "ALL_FAMILIES_UNAVAILABLE_STATUS",
    "BASE_PROTOCOL_FINGERPRINT",
    "BROKER_MUTATION_AUTHORIZED",
    "DEMO_ORDER_AUTHORIZED",
    "FAMILY_FIT_ATTEMPTS",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_NONCONVERGENCE_POLICY",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "NO_FINANCIAL_CHALLENGER_STATUS",
    "OTHER_FAMILY_FIT_FAILURE_POLICY",
    "PAIR_RESULT_INCLUDE_HIDDEN_FILES",
    "PAIR_RESULT_MISSING_FILE_POLICY",
    "PAIR_RESULT_UPLOAD_ALWAYS",
    "PREDECESSOR_EXPERIMENT_ID",
    "PREDECESSOR_FAILED_MODEL_HEAD_SHA",
    "PREDECESSOR_FAILED_MODEL_RUN_ID",
    "PREDECESSOR_FAILURE_REVIEW_DECISION",
    "PRIOR_RESULT_INFORMED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "SUCCESSOR_EXPERIMENT_ID",
    "SUCCESSOR_PROTOCOL_DECISION",
    "SUCCESSOR_PROTOCOL_VERSION",
    "TRADING_AUTHORIZED",
    "UNTOUCHED_OOS",
    "successor_protocol_fingerprint",
    "successor_protocol_payload",
    "validate_base_protocol_identity",
]
