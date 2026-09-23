from __future__ import annotations

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
)
from .model_successor_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    EXP045_REPLACEMENT_RUN_AUTHORIZED,
    EXP045_RERUN_AUTHORIZED,
    MIN_DIRECTIONAL_CANDIDATE_COUNT,
    POST_RESULT_DIAGNOSTIC_DECISION,
    SOURCE_EVIDENCE_FINGERPRINT,
    SOURCE_EXPERIMENT_ID,
    SOURCE_MODEL_RUN_ID,
    SOURCE_RESULT_DECISION,
)
from .model_successor_protocol import (
    LOGISTIC_NONCONVERGENCE_POLICY,
    successor_protocol_fingerprint,
)


STABILITY_SUCCESSOR_EXPERIMENT_ID = "EXP-20260923-046"
STABILITY_PROTOCOL_VERSION = "fmp-exp046-stability-protocol-v1"
STABILITY_PROTOCOL_DECISION = "DEC-104"

PREDECESSOR_PROTOCOL_FINGERPRINT = (
    "35526f123190c93948b4791920e7b350f"
    "7fbe0d8ec751b8c0f9d41e69b91944e"
)
PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT = (
    "3e0ebac02dbba690b4c03dd10c3fdd30"
    "c5eb0d6356b881e38f9a3527f0135c55"
)
POST_RESULT_DIAGNOSTIC_BLOB_SHA = (
    "f1ccda0d393b851cd7c1db1399da57a920a0a7c1"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

TEMPORAL_STABILITY_WINDOWS = (
    MappingProxyType(
        {
            "name": "selection_2021_h1",
            "start": "2021-01-01",
            "end_exclusive": "2021-07-01",
        }
    ),
    MappingProxyType(
        {
            "name": "selection_2021_h2",
            "start": "2021-07-01",
            "end_exclusive": "2022-01-01",
        }
    ),
    MappingProxyType(
        {
            "name": "selection_2022_h1",
            "start": "2022-01-01",
            "end_exclusive": "2022-07-01",
        }
    ),
    MappingProxyType(
        {
            "name": "selection_2022_h2",
            "start": "2022-07-01",
            "end_exclusive": "2023-01-01",
        }
    ),
)

MIN_STABILITY_WINDOW_CANDIDATE_SHARE = 0.10
ALL_STABILITY_WINDOWS_MUST_PASS = True
OVERALL_SELECTION_GATE_STILL_REQUIRED = True

STABILITY_WINDOW_REQUIREMENTS = (
    "directional_candidate_share>=0.10",
    "total_net_pips>0",
    "mean_net_pips>0",
    "gross_positive_pips>absolute_gross_negative_pips",
)

CONFIDENCE_THRESHOLD_CHANGE_AUTHORIZED = False
MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED = False
MODEL_FAMILY_CHANGE_AUTHORIZED = False
MODEL_CONFIG_CHANGE_AUTHORIZED = False
TARGET_CHANGE_AUTHORIZED = False
FEATURE_CHANGE_AUTHORIZED = False
DATA_SPLIT_CHANGE_AUTHORIZED = False
LOGISTIC_RESCUE_AUTHORIZED = False

MODEL_PROTOCOL_RESULT_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
HISTORICAL_RESULT_EXECUTION_AUTHORIZED = False
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


def _split_payload(split: object) -> dict[str, object]:
    return {
        "name": str(getattr(split, "name")),
        "start": getattr(split, "start").isoformat(),
        "end_exclusive": (
            getattr(split, "end_exclusive").isoformat()
        ),
    }


def validate_predecessor_identity() -> None:
    actual = successor_protocol_fingerprint()
    if actual != PREDECESSOR_PROTOCOL_FINGERPRINT:
        raise ValueError(
            "EXP-046 predecessor protocol fingerprint drift"
        )
    if SOURCE_EXPERIMENT_ID != "EXP-20260923-045":
        raise ValueError(
            "EXP-046 predecessor experiment identity drift"
        )
    if SOURCE_RESULT_DECISION != "DEC-102":
        raise ValueError(
            "EXP-046 predecessor result decision drift"
        )
    if POST_RESULT_DIAGNOSTIC_DECISION != "DEC-103":
        raise ValueError(
            "EXP-046 diagnostic decision drift"
        )
    if SOURCE_EVIDENCE_FINGERPRINT != (
        PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
    ):
        raise ValueError(
            "EXP-046 predecessor evidence fingerprint drift"
        )
    if SOURCE_MODEL_RUN_ID != 35911916239:
        raise ValueError(
            "EXP-046 predecessor model run id drift"
        )
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "EXP-046 requires zero accepted predecessor candidates"
        )
    if EXP045_RERUN_AUTHORIZED is not False:
        raise ValueError(
            "EXP-046 requires EXP-045 rerun to remain closed"
        )
    if EXP045_REPLACEMENT_RUN_AUTHORIZED is not False:
        raise ValueError(
            "EXP-046 requires EXP-045 replacement to remain closed"
        )
    if MIN_DIRECTIONAL_CANDIDATE_COUNT != (
        MIN_DIRECTIONAL_CANDIDATES
    ):
        raise ValueError(
            "EXP-046 minimum directional candidate count drift"
        )


def stability_protocol_payload() -> dict[str, object]:
    validate_predecessor_identity()

    return {
        "experiment_id": STABILITY_SUCCESSOR_EXPERIMENT_ID,
        "protocol_version": STABILITY_PROTOCOL_VERSION,
        "protocol_decision": STABILITY_PROTOCOL_DECISION,
        "predecessor": {
            "experiment_id": SOURCE_EXPERIMENT_ID,
            "result_decision": SOURCE_RESULT_DECISION,
            "diagnostic_decision": POST_RESULT_DIAGNOSTIC_DECISION,
            "model_run_id": SOURCE_MODEL_RUN_ID,
            "result_evidence_fingerprint": (
                PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
            ),
            "protocol_fingerprint": (
                PREDECESSOR_PROTOCOL_FINGERPRINT
            ),
            "diagnostic_blob_sha": (
                POST_RESULT_DIAGNOSTIC_BLOB_SHA
            ),
            "accepted_model_candidate_count": 0,
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
            "feature_change_authorized": FEATURE_CHANGE_AUTHORIZED,
        },
        "target": {
            "column": TARGET_COLUMN,
            "slippage_pips": TARGET_SLIPPAGE_PIPS,
            "classes": list(TARGET_CLASSES),
            "target_change_authorized": TARGET_CHANGE_AUTHORIZED,
        },
        "chronology": {
            "splits": [
                _split_payload(split)
                for split in PROTOCOL_SPLITS
            ],
            "fit_split": _split_payload(FIT_SPLIT),
            "selection_split": _split_payload(SELECTION_SPLIT),
            "validation_split": _split_payload(VALIDATION_SPLIT),
            "retrospective_holdout_split": _split_payload(
                RETROSPECTIVE_HOLDOUT_SPLIT
            ),
            "data_split_change_authorized": (
                DATA_SPLIT_CHANGE_AUTHORIZED
            ),
            "no_refit_after_fit": True,
            "untouched_oos": False,
        },
        "model_families": {
            "families": list(MODEL_FAMILIES),
            "scikit_learn_version": SCIKIT_LEARN_VERSION,
            "logistic_regression": dict(
                LOGISTIC_REGRESSION_CONFIG
            ),
            "hist_gradient_boosting": dict(
                HIST_GRADIENT_BOOSTING_CONFIG
            ),
            "family_change_authorized": (
                MODEL_FAMILY_CHANGE_AUTHORIZED
            ),
            "config_change_authorized": (
                MODEL_CONFIG_CHANGE_AUTHORIZED
            ),
            "logistic_nonconvergence_policy": dict(
                LOGISTIC_NONCONVERGENCE_POLICY
            ),
            "logistic_rescue_authorized": (
                LOGISTIC_RESCUE_AUTHORIZED
            ),
        },
        "selection": {
            "confidence_thresholds": list(
                CONFIDENCE_THRESHOLDS
            ),
            "confidence_threshold_change_authorized": (
                CONFIDENCE_THRESHOLD_CHANGE_AUTHORIZED
            ),
            "minimum_directional_candidates": (
                MIN_DIRECTIONAL_CANDIDATES
            ),
            "minimum_directional_candidate_count_change_authorized": (
                MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED
            ),
            "gate_scenarios": list(
                SELECTION_GATE_SCENARIOS
            ),
            "aggregate_gate_requirements": list(
                GATE_REQUIREMENTS
            ),
            "aggregate_gate_must_pass": (
                OVERALL_SELECTION_GATE_STILL_REQUIRED
            ),
            "temporal_stability": {
                "windows": [
                    dict(window)
                    for window in TEMPORAL_STABILITY_WINDOWS
                ],
                "minimum_directional_candidate_share_per_window": (
                    MIN_STABILITY_WINDOW_CANDIDATE_SHARE
                ),
                "requirements_per_window": list(
                    STABILITY_WINDOW_REQUIREMENTS
                ),
                "all_windows_must_pass": (
                    ALL_STABILITY_WINDOWS_MUST_PASS
                ),
            },
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
            "gate_scenarios": list(
                HOLDOUT_GATE_SCENARIOS
            ),
            "diagnostic_scenarios": list(
                DIAGNOSTIC_SCENARIOS
            ),
            "evidence_is_retrospective": True,
        },
        "authorization": {
            "model_protocol_result_authorized": (
                MODEL_PROTOCOL_RESULT_AUTHORIZED
            ),
            "model_fit_authorized": MODEL_FIT_AUTHORIZED,
            "historical_result_execution_authorized": (
                HISTORICAL_RESULT_EXECUTION_AUTHORIZED
            ),
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


def stability_protocol_fingerprint() -> str:
    return hashlib.sha256(
        _canonical_json(stability_protocol_payload())
    ).hexdigest()


__all__ = [
    "ALL_STABILITY_WINDOWS_MUST_PASS",
    "BROKER_MUTATION_AUTHORIZED",
    "CONFIDENCE_THRESHOLD_CHANGE_AUTHORIZED",
    "DATA_SPLIT_CHANGE_AUTHORIZED",
    "DEMO_ORDER_AUTHORIZED",
    "FEATURE_CHANGE_AUTHORIZED",
    "HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_RESCUE_AUTHORIZED",
    "MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED",
    "MIN_STABILITY_WINDOW_CANDIDATE_SHARE",
    "MODEL_CONFIG_CHANGE_AUTHORIZED",
    "MODEL_FAMILY_CHANGE_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "POST_RESULT_DIAGNOSTIC_BLOB_SHA",
    "PREDECESSOR_PROTOCOL_FINGERPRINT",
    "PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT",
    "PRIOR_RESULT_INFORMED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "STABILITY_PROTOCOL_DECISION",
    "STABILITY_PROTOCOL_VERSION",
    "STABILITY_SUCCESSOR_EXPERIMENT_ID",
    "STABILITY_WINDOW_REQUIREMENTS",
    "TARGET_CHANGE_AUTHORIZED",
    "TEMPORAL_STABILITY_WINDOWS",
    "TRADING_AUTHORIZED",
    "UNTOUCHED_OOS",
    "stability_protocol_fingerprint",
    "stability_protocol_payload",
    "validate_predecessor_identity",
]
