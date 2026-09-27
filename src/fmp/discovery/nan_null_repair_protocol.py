from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .historical_failed_result_decision import (
    EXP061_FAILED_RESULT_DECISION,
    EXP061_FAILED_RESULT_VERSION,
)
from .pattern_protocol import (
    EXPERIMENT_ID as EXP061_EXPERIMENT_ID,
    PATTERN_DISCOVERY_DECISION as EXP061_PROTOCOL_DECISION,
    PROTOCOL_VERSION as EXP061_PROTOCOL_VERSION,
    protocol_fingerprint as exp061_protocol_fingerprint,
    protocol_payload as exp061_protocol_payload,
)


EXP062_EXPERIMENT_ID = "EXP-20260927-062"
EXP062_REPAIR_PROTOCOL_DECISION = "DEC-292"
EXP062_REPAIR_PROTOCOL_VERSION = "fmp-exp062-nan-null-adapter-repair-protocol-v1"

DEC291_FAILED_RESULT_BLOB_SHA = "deb4a1d314b7e106deee71b6f82f79d0cddd8a9b"
EXP061_PROTOCOL_BLOB_SHA = "63b3f0121d6a50eb9e8e62ab666d70eb91791621"
EXP061_ADAPTER_BLOB_SHA = "978a33554fad7e9d78b002778c4896be0af3333a"

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

ADAPTER_NAN_TO_NULL_REPAIR_AUTHORIZED = True
PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED = False
POSITIVE_NEGATIVE_INFINITY_NORMALIZATION_AUTHORIZED = False

HISTORICAL_RESULT_EXECUTION_AUTHORIZED = False
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


def validate_exp062_predecessor_identity() -> None:
    if EXP061_FAILED_RESULT_DECISION != "DEC-291":
        raise ValueError("EXP-062 failed predecessor decision drift")
    if EXP061_FAILED_RESULT_VERSION != (
        "fmp-exp061-failed-historical-result-review-v1"
    ):
        raise ValueError("EXP-062 failed predecessor version drift")
    if EXP061_EXPERIMENT_ID != "EXP-20260927-061":
        raise ValueError("EXP-062 semantic predecessor experiment drift")
    if EXP061_PROTOCOL_DECISION != "DEC-270":
        raise ValueError("EXP-062 semantic predecessor decision drift")
    if EXP061_PROTOCOL_VERSION != "fmp-exp061-pattern-discovery-protocol-v1":
        raise ValueError("EXP-062 semantic predecessor version drift")
    fingerprint = exp061_protocol_fingerprint()
    if len(fingerprint) != 64:
        raise ValueError("EXP-062 predecessor protocol fingerprint invalid")


def exp062_repair_protocol_payload() -> dict[str, object]:
    validate_exp062_predecessor_identity()
    predecessor = deepcopy(exp061_protocol_payload())
    predecessor_authorization = predecessor.get("authorization")
    if not isinstance(predecessor_authorization, dict):
        raise ValueError("EXP-062 predecessor authorization payload missing")
    for field in tuple(predecessor_authorization):
        predecessor_authorization[field] = False

    return {
        "experiment_id": EXP062_EXPERIMENT_ID,
        "decision": EXP062_REPAIR_PROTOCOL_DECISION,
        "protocol_version": EXP062_REPAIR_PROTOCOL_VERSION,
        "semantic_predecessor_experiment_id": EXP061_EXPERIMENT_ID,
        "semantic_predecessor_protocol_decision": EXP061_PROTOCOL_DECISION,
        "semantic_predecessor_protocol_version": EXP061_PROTOCOL_VERSION,
        "semantic_predecessor_protocol_fingerprint": exp061_protocol_fingerprint(),
        "failed_predecessor_result_decision": EXP061_FAILED_RESULT_DECISION,
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "untouched_oos": UNTOUCHED_OOS,
        "retained_semantics": {
            "chronology": deepcopy(predecessor["windows"]),
            "chronology_boundary_rule": predecessor["chronology_boundary_rule"],
            "market_state": deepcopy(predecessor["market_state"]),
            "search": deepcopy(predecessor["search"]),
            "discovery_gate": deepcopy(predecessor["discovery_gate"]),
            "ranking": deepcopy(predecessor["ranking"]),
            "deduplication": deepcopy(predecessor["deduplication"]),
            "confirmation": deepcopy(predecessor["confirmation"]),
            "validation": deepcopy(predecessor["validation"]),
            "costs": {
                "discovery_slippage_pips": predecessor["discovery_gate"]["slippage_pips"],
                "stress_slippage_pips": predecessor["discovery_gate"]["stress_slippage_pips"],
            },
        },
        "implementation_repair": {
            "authorized": ADAPTER_NAN_TO_NULL_REPAIR_AUTHORIZED,
            "protocol_semantics_change_authorized": PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED,
            "source_adapter_blob_sha": EXP061_ADAPTER_BLOB_SHA,
            "exact_boundary": "continuous_feature_values_before_FeatureObservation",
            "exact_rule": "float_nan_to_none",
            "positive_negative_infinity_normalization_authorized": (
                POSITIVE_NEGATIVE_INFINITY_NORMALIZATION_AUTHORIZED
            ),
            "observed_failure_features": ["realized_vol_1h", "realized_vol_8h"],
            "all_other_continuous_values_unchanged": True,
            "session_flags_unchanged": True,
            "feature_definitions_unchanged": True,
            "outcome_definitions_unchanged": True,
            "pattern_fingerprint_semantics_retained_from_exp061": True,
        },
        "authorization": {
            "adapter_nan_to_null_repair_authorized": True,
            "protocol_semantics_change_authorized": False,
            "historical_result_execution_authorized": False,
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
        },
    }


def exp062_repair_protocol_fingerprint() -> str:
    return hashlib.sha256(_canonical_json(exp062_repair_protocol_payload())).hexdigest()


__all__ = [
    "ADAPTER_NAN_TO_NULL_REPAIR_AUTHORIZED",
    "EXP062_EXPERIMENT_ID",
    "EXP062_REPAIR_PROTOCOL_DECISION",
    "EXP062_REPAIR_PROTOCOL_VERSION",
    "HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED",
    "exp062_repair_protocol_fingerprint",
    "exp062_repair_protocol_payload",
    "validate_exp062_predecessor_identity",
]
