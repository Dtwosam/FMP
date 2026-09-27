from __future__ import annotations

from fmp.discovery.nan_null_repair_protocol import (
    ADAPTER_NAN_TO_NULL_REPAIR_AUTHORIZED,
    EXP062_EXPERIMENT_ID,
    EXP062_REPAIR_PROTOCOL_DECISION,
    EXP062_REPAIR_PROTOCOL_VERSION,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED,
    exp062_repair_protocol_fingerprint,
    exp062_repair_protocol_payload,
    validate_exp062_predecessor_identity,
)
from fmp.discovery.pattern_protocol import (
    protocol_fingerprint as exp061_protocol_fingerprint,
    protocol_payload as exp061_protocol_payload,
)


def test_exp062_predecessor_identity_is_exact() -> None:
    validate_exp062_predecessor_identity()


def test_exp062_has_new_identity_but_retains_exp061_semantics() -> None:
    value = exp062_repair_protocol_payload()
    predecessor = exp061_protocol_payload()

    assert value["experiment_id"] == EXP062_EXPERIMENT_ID
    assert value["decision"] == EXP062_REPAIR_PROTOCOL_DECISION
    assert value["protocol_version"] == EXP062_REPAIR_PROTOCOL_VERSION
    assert value["semantic_predecessor_experiment_id"] == predecessor["experiment_id"]
    assert (
        value["semantic_predecessor_protocol_fingerprint"]
        == exp061_protocol_fingerprint()
    )

    retained = value["retained_semantics"]
    assert retained["chronology"] == predecessor["windows"]
    assert retained["chronology_boundary_rule"] == predecessor["chronology_boundary_rule"]
    assert retained["market_state"] == predecessor["market_state"]
    assert retained["search"] == predecessor["search"]
    assert retained["discovery_gate"] == predecessor["discovery_gate"]
    assert retained["ranking"] == predecessor["ranking"]
    assert retained["deduplication"] == predecessor["deduplication"]
    assert retained["confirmation"] == predecessor["confirmation"]
    assert retained["validation"] == predecessor["validation"]


def test_exp062_authorizes_only_nan_to_null_adapter_repair() -> None:
    value = exp062_repair_protocol_payload()
    repair = value["implementation_repair"]

    assert ADAPTER_NAN_TO_NULL_REPAIR_AUTHORIZED is True
    assert PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED is False
    assert repair["authorized"] is True
    assert repair["protocol_semantics_change_authorized"] is False
    assert repair["exact_boundary"] == (
        "continuous_feature_values_before_FeatureObservation"
    )
    assert repair["exact_rule"] == "float_nan_to_none"
    assert repair["positive_negative_infinity_normalization_authorized"] is False
    assert repair["observed_failure_features"] == [
        "realized_vol_1h",
        "realized_vol_8h",
    ]
    assert repair["all_other_continuous_values_unchanged"] is True
    assert repair["session_flags_unchanged"] is True
    assert repair["feature_definitions_unchanged"] is True
    assert repair["outcome_definitions_unchanged"] is True
    assert repair["pattern_fingerprint_semantics_retained_from_exp061"] is True


def test_exp062_execution_and_downstream_paths_remain_locked() -> None:
    value = exp062_repair_protocol_payload()
    auth = value["authorization"]

    assert HISTORICAL_RESULT_EXECUTION_AUTHORIZED is False
    assert auth["adapter_nan_to_null_repair_authorized"] is True
    for field in (
        "protocol_semantics_change_authorized",
        "historical_result_execution_authorized",
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
        assert auth[field] is False, field


def test_exp062_protocol_fingerprint_is_stable_shape() -> None:
    fingerprint = exp062_repair_protocol_fingerprint()
    assert isinstance(fingerprint, str)
    assert len(fingerprint) == 64
    int(fingerprint, 16)
