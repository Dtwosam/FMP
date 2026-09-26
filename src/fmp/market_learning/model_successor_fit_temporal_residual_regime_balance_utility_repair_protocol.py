from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .model_successor_fit_temporal_residual_regime_balance_utility_failure_diagnostics import (
    EXPECTED_INVALID_BREADTH_ACCESS_NAMES,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION,
    IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION,
    IMPLEMENTATION_REPAIR_RULE,
    SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    SUCCESSOR_MODEL_FIT_AUTHORIZED,
    SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED,
)
from .model_successor_fit_temporal_residual_regime_balance_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_PENALTY_MULTIPLIER,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_REGIME_COUNT,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_SOURCE_BOUND_COUNT_PER_ROW,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_VERSION,
    fit_temporal_residual_regime_balance_utility_protocol_fingerprint,
    fit_temporal_residual_regime_balance_utility_protocol_payload,
)


FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_EXPERIMENT_ID = (
    "EXP-20260926-060"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_VERSION = (
    "fmp-exp060-fit-temporal-residual-regime-balance-utility-"
    "implementation-repair-protocol-v1"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_DECISION = (
    "DEC-253"
)

DEC252_MERGED_COMMIT = "fffe7311bfb0c14bf6936657b81ffe8a38c66414"
DEC252_DIAGNOSTIC_BLOB_SHA = (
    "d73008c7faf236f915685110d6cf59988d6fc27f"
)
DEC251_RESULT_DECISION_BLOB_SHA = (
    "c8ca7143e687494b81205556af7e317ec69937fd"
)
EXP059_PROTOCOL_BLOB_SHA = "cd4e790098a5c8d99ea2aa5264465b5d4b6b6acc"
EXP059_TRAINING_CORE_BLOB_SHA = (
    "4f99c1d0cb18551b67cc89357ad4a3940c190cd2"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED = True
PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED = False

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


def validate_fit_temporal_residual_regime_balance_utility_repair_predecessor_identity(
) -> None:
    if (
        FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION
        != "DEC-252"
    ):
        raise ValueError("EXP-060 predecessor diagnostic decision drift")
    if IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION != (
        "EXP059_IMPLEMENTATION_FAILED_BEFORE_EVIDENCE_DUE_PREDECESSOR_DEPTH_DRIFT"
    ):
        raise ValueError("EXP-060 predecessor diagnostic classification drift")
    if SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED is not True:
        raise ValueError("EXP-060 successor protocol source is not open")
    if SUCCESSOR_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError("EXP-060 predecessor successor fit must be closed")
    if SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED is not False:
        raise ValueError(
            "EXP-060 predecessor successor execution must be closed"
        )
    if tuple(sorted(EXPECTED_INVALID_BREADTH_ACCESS_NAMES)) != (
        "FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW",
        "FIT_TEMPORAL_RESIDUAL_BREADTH_RULE",
        "RESIDUAL_BREADTH_ELIGIBILITY_RULE",
        "RESIDUAL_BREADTH_POSITIVITY_RULE",
    ):
        raise ValueError("EXP-060 repair breadth-name inventory drift")

    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID != (
        "EXP-20260926-059"
    ):
        raise ValueError("EXP-060 semantic predecessor experiment drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_DECISION != (
        "DEC-242"
    ):
        raise ValueError("EXP-060 semantic predecessor decision drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_VERSION != (
        "fmp-exp059-fit-temporal-residual-regime-balance-utility-protocol-v1"
    ):
        raise ValueError("EXP-060 semantic predecessor version drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_REGIME_COUNT != 3:
        raise ValueError("EXP-060 regime-count drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_SOURCE_BOUND_COUNT_PER_ROW != 12:
        raise ValueError("EXP-060 source-bound inventory drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_PENALTY_MULTIPLIER != 1.0:
        raise ValueError("EXP-060 balance penalty drift")

    predecessor = fit_temporal_residual_regime_balance_utility_protocol_payload()
    if predecessor["experiment_id"] != (
        FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID
    ):
        raise ValueError("EXP-060 predecessor payload experiment drift")
    selection = predecessor.get("selection")
    if not isinstance(selection, dict):
        raise ValueError("EXP-060 predecessor selection payload missing")
    if selection.get("candidate_budget_anchors") != [250, 500, 1000]:
        raise ValueError("EXP-060 predecessor budget identity drift")
    if selection.get("ranking_order") != [
        "fit_temporal_residual_regime_balance_utility_desc",
        "fit_temporal_residual_regime_floor_utility_desc",
        "fit_temporal_residual_lower_tail_mean_desc",
        "fit_temporal_residual_breadth_desc",
        "robust_fit_temporal_residual_bound_utility_desc",
        "robust_fit_temporal_feature_support_desc",
        "robust_fit_temporal_support_desc",
        "robust_pooled_calibrated_utility_desc",
        "robust_raw_utility_desc",
        "row_identity_asc",
    ]:
        raise ValueError("EXP-060 predecessor ranking identity drift")
    stability = selection.get("temporal_stability")
    if not isinstance(stability, dict):
        raise ValueError("EXP-060 predecessor stability payload missing")
    if len(stability.get("windows", [])) != 4:
        raise ValueError("EXP-060 predecessor stability-window count drift")
    if (
        stability.get("minimum_directional_candidate_share_per_window")
        != 0.10
    ):
        raise ValueError("EXP-060 predecessor stability-share drift")


def fit_temporal_residual_regime_balance_utility_repair_protocol_payload(
) -> dict[str, object]:
    validate_fit_temporal_residual_regime_balance_utility_repair_predecessor_identity()
    predecessor = fit_temporal_residual_regime_balance_utility_protocol_payload()

    chronology = deepcopy(predecessor["chronology"])
    model_family = deepcopy(predecessor["model_family"])
    temporal_jackknife = deepcopy(predecessor["temporal_jackknife"])
    utility_consensus = deepcopy(predecessor["utility_consensus"])
    pooled_calibration = deepcopy(
        predecessor["out_of_fit_utility_calibration"]
    )
    utility_support = deepcopy(
        predecessor["fit_temporal_support_calibration"]
    )
    feature_support = deepcopy(
        predecessor["fit_temporal_feature_support"]
    )
    residual_bound = deepcopy(predecessor["fit_temporal_residual_bound"])
    residual_breadth = deepcopy(predecessor["fit_temporal_residual_breadth"])
    residual_lower_tail = deepcopy(
        predecessor["fit_temporal_residual_lower_tail"]
    )
    residual_regime_floor = deepcopy(
        predecessor["fit_temporal_residual_regime_floor"]
    )
    residual_regime_balance = deepcopy(
        predecessor["fit_temporal_residual_regime_balance"]
    )
    selection = deepcopy(predecessor["selection"])
    validation = deepcopy(predecessor["validation"])
    holdout = deepcopy(predecessor["retrospective_holdout"])

    utility_consensus["fit_temporal_residual_regime_balance_added"] = False
    utility_consensus["fit_temporal_residual_regime_balance_retained"] = True

    residual_regime_balance["authorized_protocol_change"] = False
    residual_regime_balance["retained_from_exp059"] = True

    authorization = deepcopy(predecessor["authorization"])
    for field in tuple(authorization):
        authorization[field] = False
    authorization.update(
        {
            "implementation_dependency_repair_authorized": (
                IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED
            ),
            "protocol_semantics_change_authorized": (
                PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED
            ),
        }
    )

    return {
        "protocol_version": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_VERSION
        ),
        "protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_DECISION
        ),
        "experiment_id": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_EXPERIMENT_ID
        ),
        "semantic_predecessor_experiment_id": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID
        ),
        "semantic_predecessor_protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_DECISION
        ),
        "semantic_predecessor_protocol_fingerprint": (
            fit_temporal_residual_regime_balance_utility_protocol_fingerprint()
        ),
        "failed_predecessor_result_decision": "DEC-251",
        "failure_diagnostic_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION
        ),
        "failure_diagnostic_classification": (
            IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION
        ),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "untouched_oos": UNTOUCHED_OOS,
        "chronology": chronology,
        "model_family": model_family,
        "temporal_jackknife": temporal_jackknife,
        "utility_consensus": utility_consensus,
        "out_of_fit_utility_calibration": pooled_calibration,
        "fit_temporal_support_calibration": utility_support,
        "fit_temporal_feature_support": feature_support,
        "fit_temporal_residual_bound": residual_bound,
        "fit_temporal_residual_breadth": residual_breadth,
        "fit_temporal_residual_lower_tail": residual_lower_tail,
        "fit_temporal_residual_regime_floor": residual_regime_floor,
        "fit_temporal_residual_regime_balance": residual_regime_balance,
        "selection": selection,
        "validation": validation,
        "retrospective_holdout": holdout,
        "implementation_repair": {
            "authorized": IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED,
            "protocol_semantics_change_authorized": (
                PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED
            ),
            "source_training_core_blob_sha": EXP059_TRAINING_CORE_BLOB_SHA,
            "from_module_role": "exp057_lower_tail_repair_predecessor",
            "to_module_role": "exp055_breadth_predecessor",
            "from_attribute_root": "_predecessor._predecessor",
            "to_attribute_root": (
                "_predecessor._predecessor._predecessor"
            ),
            "exact_attribute_names": list(
                sorted(EXPECTED_INVALID_BREADTH_ACCESS_NAMES)
            ),
            "exact_attribute_count": 4,
            "repair_rule": IMPLEMENTATION_REPAIR_RULE,
        },
        "authorization": authorization,
    }


def fit_temporal_residual_regime_balance_utility_repair_protocol_fingerprint(
) -> str:
    return hashlib.sha256(
        _canonical_json(
            fit_temporal_residual_regime_balance_utility_repair_protocol_payload()
        )
    ).hexdigest()


__all__ = [
    "DEC251_RESULT_DECISION_BLOB_SHA",
    "DEC252_DIAGNOSTIC_BLOB_SHA",
    "DEC252_MERGED_COMMIT",
    "EXP059_PROTOCOL_BLOB_SHA",
    "EXP059_TRAINING_CORE_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_EXPERIMENT_ID",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_DECISION",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_PROTOCOL_VERSION",
    "HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "fit_temporal_residual_regime_balance_utility_repair_protocol_fingerprint",
    "fit_temporal_residual_regime_balance_utility_repair_protocol_payload",
    "validate_fit_temporal_residual_regime_balance_utility_repair_predecessor_identity",
]
