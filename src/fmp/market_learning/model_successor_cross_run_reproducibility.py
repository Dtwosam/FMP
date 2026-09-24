from __future__ import annotations


CROSS_RUN_REPRODUCIBILITY_DECISION = "DEC-112"

EXP045_RESULT_DECISION = "DEC-102"
EXP045_RUN_ID = 35911916239
EXP045_HEAD_SHA = (
    "6d42a5053c5f2f696071715640dab24973a40517"
)
EXP045_EVIDENCE_FINGERPRINT = (
    "3e0ebac02dbba690b4c03dd10c3fdd30"
    "c5eb0d6356b881e38f9a3527f0135c55"
)

EXP046_RESULT_DECISION = "DEC-111"
EXP046_RUN_ID = 35978474425
EXP046_HEAD_SHA = (
    "dabafcc290d2b383531532d873c7d6c697198d5a"
)
EXP046_EVIDENCE_FINGERPRINT = (
    "499c91e4508f07bf8a637657969175fb"
    "ba8e93d07236b94ded06ae884b386214"
)

SHARED_RUNTIME_REQUIREMENTS_BLOB_SHA = (
    "d25ab16056b9f5df283147d67b8f401f60ae7520"
)
SHARED_SUCCESSOR_TRAINING_BLOB_SHA = (
    "3f0bc1bfa9640d08175e72cdf131bb97c94d562c"
)

COMPARED_CELL_COUNT = 18

HGB_MODEL_FINGERPRINT_MATCH_COUNT = 18
HGB_PROBABILITY_DIGEST_MATCH_COUNT = 4
HGB_CANDIDATE_IDENTITY_MATCH_COUNT = 54
HGB_CANDIDATE_VARIANT_COUNT = 54

LOGISTIC_BOTH_FITTED_CELL_COUNT = 10
LOGISTIC_MODEL_FINGERPRINT_MATCH_COUNT = 4
LOGISTIC_PROBABILITY_DIGEST_MATCH_COUNT = 4
LOGISTIC_CANDIDATE_IDENTITY_MATCH_COUNT = 29
LOGISTIC_CANDIDATE_VARIANT_COUNT = 30
LOGISTIC_FAMILY_AVAILABILITY_CHANGED_CELL_COUNT = 5

LOGISTIC_RECOVERED_CELL_IDENTITIES = (
    ("EURUSD", "15m", 240),
    ("EURUSD", "5m", 60),
    ("EURUSD", "5m", 240),
)
LOGISTIC_NEW_NONCONVERGENCE_CELL_IDENTITIES = (
    ("GBPUSD", "5m", 240),
    ("USDJPY", "15m", 240),
)
LOGISTIC_COMMON_NONCONVERGENCE_CELL_IDENTITIES = (
    ("GBPUSD", "5m", 60),
    ("USDJPY", "5m", 60),
    ("USDJPY", "5m", 240),
)

CROSS_RUN_AGGREGATE_GATE_OUTCOME_CHANGE_COUNT = 1
CROSS_RUN_AGGREGATE_GATE_OUTCOME_CHANGE = {
    "symbol": "EURUSD",
    "timeframe": "5m",
    "horizon_minutes": 60,
    "model_family": "logistic_regression",
    "confidence_threshold": 0.6,
    "exp045_status": "FAMILY_UNAVAILABLE",
    "exp046_status": "AGGREGATE_GATE_PASS_STABILITY_REJECT",
}

CROSS_RUN_JOINTLY_FITTED_CANDIDATE_SET_CHANGE_COUNT = 1
CROSS_RUN_JOINTLY_FITTED_CANDIDATE_SET_CHANGE = {
    "symbol": "USDJPY",
    "timeframe": "15m",
    "horizon_minutes": 60,
    "model_family": "logistic_regression",
    "confidence_threshold": 0.5,
    "exp045_directional_candidate_count": 5579,
    "exp046_directional_candidate_count": 5578,
    "aggregate_gate_outcome_unchanged": True,
}

EXP046_STABLE_SELECTION_PASS_VARIANT_COUNT = 0
EXP046_ACCEPTED_MODEL_CANDIDATE_COUNT = 0

LOGISTIC_FAMILY_REUSE_FOR_RESULT_EXECUTION_AUTHORIZED = False
LOGISTIC_NUMERICAL_REMEDY_RESULT_EXECUTION_AUTHORIZED = False
RELAX_STABILITY_SCREEN_AUTHORIZED = False
EXP046_RERUN_AUTHORIZED = False
EXP046_REPLACEMENT_RUN_AUTHORIZED = False

SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = True
SUCCESSOR_RESULT_EXECUTION_AUTHORIZED = False
SUCCESSOR_MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def build_cross_run_reproducibility_gate() -> dict[str, object]:
    if HGB_MODEL_FINGERPRINT_MATCH_COUNT != COMPARED_CELL_COUNT:
        raise ValueError(
            "DEC-112 HGB model fingerprint reproducibility drift"
        )
    if (
        HGB_CANDIDATE_IDENTITY_MATCH_COUNT
        != HGB_CANDIDATE_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-112 HGB candidate reproducibility drift"
        )
    if (
        LOGISTIC_FAMILY_AVAILABILITY_CHANGED_CELL_COUNT
        != len(LOGISTIC_RECOVERED_CELL_IDENTITIES)
        + len(LOGISTIC_NEW_NONCONVERGENCE_CELL_IDENTITIES)
    ):
        raise ValueError(
            "DEC-112 logistic family-availability accounting drift"
        )
    if (
        LOGISTIC_CANDIDATE_IDENTITY_MATCH_COUNT
        + CROSS_RUN_JOINTLY_FITTED_CANDIDATE_SET_CHANGE_COUNT
        != LOGISTIC_CANDIDATE_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-112 logistic candidate accounting drift"
        )
    if EXP046_STABLE_SELECTION_PASS_VARIANT_COUNT != 0:
        raise ValueError(
            "DEC-112 EXP-046 stability-pass count drift"
        )
    if EXP046_ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "DEC-112 accepted-candidate count drift"
        )

    return {
        "cross_run_reproducibility_decision": (
            CROSS_RUN_REPRODUCIBILITY_DECISION
        ),
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "source_results": {
            "exp045": {
                "result_decision": EXP045_RESULT_DECISION,
                "run_id": EXP045_RUN_ID,
                "head_sha": EXP045_HEAD_SHA,
                "evidence_fingerprint": (
                    EXP045_EVIDENCE_FINGERPRINT
                ),
            },
            "exp046": {
                "result_decision": EXP046_RESULT_DECISION,
                "run_id": EXP046_RUN_ID,
                "head_sha": EXP046_HEAD_SHA,
                "evidence_fingerprint": (
                    EXP046_EVIDENCE_FINGERPRINT
                ),
            },
        },
        "shared_source_identity": {
            "runtime_requirements_blob_sha": (
                SHARED_RUNTIME_REQUIREMENTS_BLOB_SHA
            ),
            "successor_training_blob_sha": (
                SHARED_SUCCESSOR_TRAINING_BLOB_SHA
            ),
            "compared_cell_count": COMPARED_CELL_COUNT,
        },
        "hgb": {
            "classification": (
                "MATERIAL_DECISION_REPRODUCIBILITY_ESTABLISHED"
            ),
            "model_fingerprint_match_count": (
                HGB_MODEL_FINGERPRINT_MATCH_COUNT
            ),
            "probability_digest_match_count": (
                HGB_PROBABILITY_DIGEST_MATCH_COUNT
            ),
            "candidate_identity_match_count": (
                HGB_CANDIDATE_IDENTITY_MATCH_COUNT
            ),
            "candidate_variant_count": (
                HGB_CANDIDATE_VARIANT_COUNT
            ),
        },
        "logistic_regression": {
            "classification": (
                "FAMILY_AVAILABILITY_REPRODUCIBILITY_FAILED"
            ),
            "both_fitted_cell_count": (
                LOGISTIC_BOTH_FITTED_CELL_COUNT
            ),
            "model_fingerprint_match_count": (
                LOGISTIC_MODEL_FINGERPRINT_MATCH_COUNT
            ),
            "probability_digest_match_count": (
                LOGISTIC_PROBABILITY_DIGEST_MATCH_COUNT
            ),
            "candidate_identity_match_count": (
                LOGISTIC_CANDIDATE_IDENTITY_MATCH_COUNT
            ),
            "candidate_variant_count": (
                LOGISTIC_CANDIDATE_VARIANT_COUNT
            ),
            "family_availability_changed_cell_count": (
                LOGISTIC_FAMILY_AVAILABILITY_CHANGED_CELL_COUNT
            ),
            "recovered_cell_identities": [
                list(value)
                for value in LOGISTIC_RECOVERED_CELL_IDENTITIES
            ],
            "new_nonconvergence_cell_identities": [
                list(value)
                for value in (
                    LOGISTIC_NEW_NONCONVERGENCE_CELL_IDENTITIES
                )
            ],
            "common_nonconvergence_cell_identities": [
                list(value)
                for value in (
                    LOGISTIC_COMMON_NONCONVERGENCE_CELL_IDENTITIES
                )
            ],
        },
        "cross_run_effects": {
            "aggregate_gate_outcome_change_count": (
                CROSS_RUN_AGGREGATE_GATE_OUTCOME_CHANGE_COUNT
            ),
            "aggregate_gate_outcome_change": dict(
                CROSS_RUN_AGGREGATE_GATE_OUTCOME_CHANGE
            ),
            "jointly_fitted_candidate_set_change_count": (
                CROSS_RUN_JOINTLY_FITTED_CANDIDATE_SET_CHANGE_COUNT
            ),
            "jointly_fitted_candidate_set_change": dict(
                CROSS_RUN_JOINTLY_FITTED_CANDIDATE_SET_CHANGE
            ),
            "exp046_stable_selection_pass_variant_count": (
                EXP046_STABLE_SELECTION_PASS_VARIANT_COUNT
            ),
            "exp046_accepted_model_candidate_count": (
                EXP046_ACCEPTED_MODEL_CANDIDATE_COUNT
            ),
        },
        "guardrails": {
            "logistic_family_reuse_for_result_execution_authorized": (
                LOGISTIC_FAMILY_REUSE_FOR_RESULT_EXECUTION_AUTHORIZED
            ),
            "logistic_numerical_remedy_result_execution_authorized": (
                LOGISTIC_NUMERICAL_REMEDY_RESULT_EXECUTION_AUTHORIZED
            ),
            "relax_stability_screen_authorized": (
                RELAX_STABILITY_SCREEN_AUTHORIZED
            ),
            "exp046_rerun_authorized": (
                EXP046_RERUN_AUTHORIZED
            ),
            "exp046_replacement_run_authorized": (
                EXP046_REPLACEMENT_RUN_AUTHORIZED
            ),
        },
        "successor_protocol_source_open_authorized": (
            SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED
        ),
        "successor_result_execution_authorized": (
            SUCCESSOR_RESULT_EXECUTION_AUTHORIZED
        ),
        "successor_model_fit_authorized": (
            SUCCESSOR_MODEL_FIT_AUTHORIZED
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
    }


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "CROSS_RUN_AGGREGATE_GATE_OUTCOME_CHANGE",
    "CROSS_RUN_AGGREGATE_GATE_OUTCOME_CHANGE_COUNT",
    "CROSS_RUN_JOINTLY_FITTED_CANDIDATE_SET_CHANGE",
    "CROSS_RUN_JOINTLY_FITTED_CANDIDATE_SET_CHANGE_COUNT",
    "CROSS_RUN_REPRODUCIBILITY_DECISION",
    "DEMO_ORDER_AUTHORIZED",
    "EXP045_EVIDENCE_FINGERPRINT",
    "EXP045_HEAD_SHA",
    "EXP045_RESULT_DECISION",
    "EXP045_RUN_ID",
    "EXP046_ACCEPTED_MODEL_CANDIDATE_COUNT",
    "EXP046_EVIDENCE_FINGERPRINT",
    "EXP046_HEAD_SHA",
    "EXP046_REPLACEMENT_RUN_AUTHORIZED",
    "EXP046_RESULT_DECISION",
    "EXP046_RERUN_AUTHORIZED",
    "EXP046_RUN_ID",
    "EXP046_STABLE_SELECTION_PASS_VARIANT_COUNT",
    "HGB_CANDIDATE_IDENTITY_MATCH_COUNT",
    "HGB_CANDIDATE_VARIANT_COUNT",
    "HGB_MODEL_FINGERPRINT_MATCH_COUNT",
    "HGB_PROBABILITY_DIGEST_MATCH_COUNT",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_BOTH_FITTED_CELL_COUNT",
    "LOGISTIC_CANDIDATE_IDENTITY_MATCH_COUNT",
    "LOGISTIC_CANDIDATE_VARIANT_COUNT",
    "LOGISTIC_FAMILY_AVAILABILITY_CHANGED_CELL_COUNT",
    "LOGISTIC_FAMILY_REUSE_FOR_RESULT_EXECUTION_AUTHORIZED",
    "LOGISTIC_MODEL_FINGERPRINT_MATCH_COUNT",
    "LOGISTIC_NEW_NONCONVERGENCE_CELL_IDENTITIES",
    "LOGISTIC_NUMERICAL_REMEDY_RESULT_EXECUTION_AUTHORIZED",
    "LOGISTIC_PROBABILITY_DIGEST_MATCH_COUNT",
    "LOGISTIC_RECOVERED_CELL_IDENTITIES",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "RELAX_STABILITY_SCREEN_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "SHARED_RUNTIME_REQUIREMENTS_BLOB_SHA",
    "SHARED_SUCCESSOR_TRAINING_BLOB_SHA",
    "SUCCESSOR_MODEL_FIT_AUTHORIZED",
    "SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED",
    "SUCCESSOR_RESULT_EXECUTION_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "build_cross_run_reproducibility_gate",
]
