from __future__ import annotations

import hashlib
import json
from types import MappingProxyType

from .model_protocol import (
    DIAGNOSTIC_SCENARIOS,
    FIT_SPLIT,
    GATE_REQUIREMENTS,
    HIST_GRADIENT_BOOSTING_CONFIG,
    HOLDOUT_GATE_SCENARIOS,
    MIN_DIRECTIONAL_CANDIDATES,
    MODEL_CELLS,
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
from .model_successor_density_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    POST_RESULT_DIAGNOSTIC_DECISION,
    SOURCE_EVIDENCE_FINGERPRINT,
    SOURCE_MODEL_RUN_ID,
)
from .model_successor_density_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
)
from .model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    STABILITY_WINDOW_REQUIREMENTS,
    TEMPORAL_STABILITY_WINDOWS,
)


REGIME_CONSENSUS_EXPERIMENT_ID = "EXP-20260924-048"
REGIME_CONSENSUS_PROTOCOL_VERSION = (
    "fmp-exp048-regime-consensus-protocol-v1"
)
REGIME_CONSENSUS_PROTOCOL_DECISION = "DEC-123"

DEC121_RESULT_DECISION = "DEC-121"
DEC122_MERGED_COMMIT = (
    "c893bd8b69743b28c8488854b3b026e69e62362e"
)
DEC122_DIAGNOSTIC_BLOB_SHA = (
    "ceb18c634af55051d2bbd5c749a7bc5862eba470"
)
PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT = (
    "f047310749a2742d75d2e448243080d3"
    "68b6a5cdf66bc119ec33e59cc192352f"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

AUTHORIZED_MODEL_FAMILIES = ("hist_gradient_boosting",)
EXCLUDED_MODEL_FAMILIES = ("logistic_regression",)

FIT_REGIME_WINDOWS = (
    MappingProxyType(
        {
            "name": "fit_2015_2016",
            "start": "2015-01-01",
            "end_exclusive": "2017-01-01",
        }
    ),
    MappingProxyType(
        {
            "name": "fit_2017_2018",
            "start": "2017-01-01",
            "end_exclusive": "2019-01-01",
        }
    ),
    MappingProxyType(
        {
            "name": "fit_2019_2020",
            "start": "2019-01-01",
            "end_exclusive": "2021-01-01",
        }
    ),
)
REQUIRED_REGIME_MODEL_COUNT = 3
ALL_REGIME_MODELS_REQUIRED = True
REGIME_FALLBACK_AUTHORIZED = False

CONSENSUS_DIRECTION_RULE = (
    "a row is eligible only when all three regime models have the same "
    "unique top class and that class is LONG or SHORT"
)
CONSENSUS_CONFIDENCE_RULE = (
    "for an eligible row, consensus confidence is the minimum across "
    "the three regime models of the probability assigned to the agreed "
    "directional class"
)
CONSENSUS_DISAGREEMENT_POLICY = "NO_TRADE"

SELECTION_CUTOFF_RULE = (
    "for each candidate budget, sort consensus-eligible selection rows "
    "by consensus confidence descending and row identity ascending; "
    "use the consensus confidence of the budget-th ranked row as the "
    "frozen cutoff"
)
CUTOFF_TIE_POLICY = (
    "all consensus-eligible rows whose consensus confidence is greater "
    "than or equal to the frozen cutoff are candidates; ties may exceed "
    "the nominal budget"
)
FORWARD_APPLICATION_RULE = (
    "apply the exact selection-derived consensus-confidence cutoff "
    "unchanged to validation and retrospective holdout using the same "
    "three frozen regime models; do not recompute a quantile or budget"
)

REGIME_CONSENSUS_SELECTION_TIE_BREAK = (
    *SELECTION_TIE_BREAK,
    "candidate_budget_anchor_ascending",
)

FEATURE_CHANGE_AUTHORIZED = False
TARGET_CHANGE_AUTHORIZED = False
OUTER_CHRONOLOGY_CHANGE_AUTHORIZED = False
HGB_MODEL_CONFIG_CHANGE_AUTHORIZED = False
DENSITY_ANCHOR_CHANGE_AUTHORIZED = False
MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED = False
STABILITY_SCREEN_CHANGE_AUTHORIZED = False
LOGISTIC_REINTRODUCTION_AUTHORIZED = False
FULL_FIT_SINGLE_MODEL_AUTHORIZED = False

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


def validate_regime_consensus_predecessor_identity() -> None:
    if POST_RESULT_DIAGNOSTIC_DECISION != "DEC-122":
        raise ValueError(
            "EXP-048 predecessor diagnostic decision drift"
        )
    if SOURCE_MODEL_RUN_ID != 35993400007:
        raise ValueError(
            "EXP-048 predecessor model run id drift"
        )
    if SOURCE_EVIDENCE_FINGERPRINT != (
        PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
    ):
        raise ValueError(
            "EXP-048 predecessor evidence fingerprint drift"
        )
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "EXP-048 requires zero accepted predecessor candidates"
        )

    if FIT_SPLIT.start.isoformat() != "2015-01-01":
        raise ValueError(
            "EXP-048 outer fit split start drift"
        )
    if FIT_SPLIT.end_exclusive.isoformat() != "2021-01-01":
        raise ValueError(
            "EXP-048 outer fit split end drift"
        )

    windows = [dict(window) for window in FIT_REGIME_WINDOWS]
    if len(windows) != REQUIRED_REGIME_MODEL_COUNT:
        raise ValueError(
            "EXP-048 fit-regime window count drift"
        )
    if windows[0]["start"] != FIT_SPLIT.start.isoformat():
        raise ValueError(
            "EXP-048 first fit-regime start drift"
        )
    if (
        windows[-1]["end_exclusive"]
        != FIT_SPLIT.end_exclusive.isoformat()
    ):
        raise ValueError(
            "EXP-048 final fit-regime end drift"
        )
    for previous, current in zip(
        windows,
        windows[1:],
        strict=True,
    ):
        if previous["end_exclusive"] != current["start"]:
            raise ValueError(
                "EXP-048 fit-regime windows must be contiguous"
            )

    if tuple(CANDIDATE_BUDGET_ANCHORS) != (250, 500, 1000):
        raise ValueError(
            "EXP-048 density-anchor identity drift"
        )
    if MIN_DIRECTIONAL_CANDIDATES != 250:
        raise ValueError(
            "EXP-048 minimum directional candidate count drift"
        )
    if MIN_STABILITY_WINDOW_CANDIDATE_SHARE != 0.10:
        raise ValueError(
            "EXP-048 temporal stability share drift"
        )


def regime_consensus_protocol_payload() -> dict[str, object]:
    validate_regime_consensus_predecessor_identity()

    return {
        "experiment_id": REGIME_CONSENSUS_EXPERIMENT_ID,
        "protocol_version": REGIME_CONSENSUS_PROTOCOL_VERSION,
        "protocol_decision": REGIME_CONSENSUS_PROTOCOL_DECISION,
        "predecessor": {
            "experiment_id": "EXP-20260924-047",
            "result_decision": DEC121_RESULT_DECISION,
            "diagnostic_decision": (
                POST_RESULT_DIAGNOSTIC_DECISION
            ),
            "diagnostic_merged_commit": (
                DEC122_MERGED_COMMIT
            ),
            "diagnostic_blob_sha": (
                DEC122_DIAGNOSTIC_BLOB_SHA
            ),
            "model_run_id": SOURCE_MODEL_RUN_ID,
            "result_evidence_fingerprint": (
                PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
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
            "outer_fit_split": _split_payload(FIT_SPLIT),
            "fit_regime_windows": [
                dict(window)
                for window in FIT_REGIME_WINDOWS
            ],
            "selection_split": _split_payload(SELECTION_SPLIT),
            "validation_split": _split_payload(VALIDATION_SPLIT),
            "retrospective_holdout_split": _split_payload(
                RETROSPECTIVE_HOLDOUT_SPLIT
            ),
            "outer_chronology_change_authorized": (
                OUTER_CHRONOLOGY_CHANGE_AUTHORIZED
            ),
            "no_refit_after_fit": True,
            "untouched_oos": False,
        },
        "model_families": {
            "authorized": list(AUTHORIZED_MODEL_FAMILIES),
            "excluded": list(EXCLUDED_MODEL_FAMILIES),
            "scikit_learn_version": SCIKIT_LEARN_VERSION,
            "hist_gradient_boosting": dict(
                HIST_GRADIENT_BOOSTING_CONFIG
            ),
            "hgb_model_config_change_authorized": (
                HGB_MODEL_CONFIG_CHANGE_AUTHORIZED
            ),
            "logistic_reintroduction_authorized": (
                LOGISTIC_REINTRODUCTION_AUTHORIZED
            ),
            "full_fit_single_model_authorized": (
                FULL_FIT_SINGLE_MODEL_AUTHORIZED
            ),
        },
        "regime_consensus": {
            "required_regime_model_count": (
                REQUIRED_REGIME_MODEL_COUNT
            ),
            "all_regime_models_required": (
                ALL_REGIME_MODELS_REQUIRED
            ),
            "regime_fallback_authorized": (
                REGIME_FALLBACK_AUTHORIZED
            ),
            "direction_rule": CONSENSUS_DIRECTION_RULE,
            "confidence_rule": CONSENSUS_CONFIDENCE_RULE,
            "disagreement_policy": (
                CONSENSUS_DISAGREEMENT_POLICY
            ),
        },
        "selection": {
            "candidate_budget_anchors": list(
                CANDIDATE_BUDGET_ANCHORS
            ),
            "density_anchor_change_authorized": (
                DENSITY_ANCHOR_CHANGE_AUTHORIZED
            ),
            "selection_cutoff_rule": (
                SELECTION_CUTOFF_RULE
            ),
            "cutoff_tie_policy": CUTOFF_TIE_POLICY,
            "forward_application_rule": (
                FORWARD_APPLICATION_RULE
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
                "all_windows_must_pass": True,
                "stability_screen_change_authorized": (
                    STABILITY_SCREEN_CHANGE_AUTHORIZED
                ),
            },
            "tie_break": list(
                REGIME_CONSENSUS_SELECTION_TIE_BREAK
            ),
        },
        "validation": {
            "consensus_models_source": "fit_regime_windows",
            "cutoff_source": "selection",
            "recompute_cutoff_on_validation": False,
            "gate_scenarios": list(
                VALIDATION_GATE_SCENARIOS
            ),
            "diagnostic_scenarios": list(
                DIAGNOSTIC_SCENARIOS
            ),
        },
        "retrospective_holdout": {
            "consensus_models_source": "fit_regime_windows",
            "cutoff_source": "selection",
            "recompute_cutoff_on_holdout": False,
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


def regime_consensus_protocol_fingerprint() -> str:
    return hashlib.sha256(
        _canonical_json(regime_consensus_protocol_payload())
    ).hexdigest()


__all__ = [
    "ALL_REGIME_MODELS_REQUIRED",
    "AUTHORIZED_MODEL_FAMILIES",
    "BROKER_MUTATION_AUTHORIZED",
    "CONSENSUS_CONFIDENCE_RULE",
    "CONSENSUS_DIRECTION_RULE",
    "CONSENSUS_DISAGREEMENT_POLICY",
    "CUTOFF_TIE_POLICY",
    "DEC121_RESULT_DECISION",
    "DEC122_DIAGNOSTIC_BLOB_SHA",
    "DEC122_MERGED_COMMIT",
    "DEMO_ORDER_AUTHORIZED",
    "DENSITY_ANCHOR_CHANGE_AUTHORIZED",
    "EXCLUDED_MODEL_FAMILIES",
    "FEATURE_CHANGE_AUTHORIZED",
    "FIT_REGIME_WINDOWS",
    "FORWARD_APPLICATION_RULE",
    "FULL_FIT_SINGLE_MODEL_AUTHORIZED",
    "HGB_MODEL_CONFIG_CHANGE_AUTHORIZED",
    "HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_REINTRODUCTION_AUTHORIZED",
    "MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "OUTER_CHRONOLOGY_CHANGE_AUTHORIZED",
    "PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT",
    "PRIOR_RESULT_INFORMED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REGIME_CONSENSUS_EXPERIMENT_ID",
    "REGIME_CONSENSUS_PROTOCOL_DECISION",
    "REGIME_CONSENSUS_PROTOCOL_VERSION",
    "REGIME_CONSENSUS_SELECTION_TIE_BREAK",
    "REGIME_FALLBACK_AUTHORIZED",
    "REQUIRED_REGIME_MODEL_COUNT",
    "SELECTION_CUTOFF_RULE",
    "SHADOW_AUTHORIZED",
    "STABILITY_SCREEN_CHANGE_AUTHORIZED",
    "TARGET_CHANGE_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "UNTOUCHED_OOS",
    "regime_consensus_protocol_fingerprint",
    "regime_consensus_protocol_payload",
    "validate_regime_consensus_predecessor_identity",
]
