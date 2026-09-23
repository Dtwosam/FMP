from __future__ import annotations

from typing import Mapping

from .model_protocol import (
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_DECISION,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    MODEL_PROTOCOL_VERSION,
    PROMOTION_AUTHORIZED,
    REAL_MONEY_AUTHORIZED,
)


MODEL_RUN_GATE_DECISION = "DEC-089"
EXPECTED_PROTOCOL_SOURCE_COMMIT = "a9305ba9c42b7224e5d4b3f7d26f268447cdf469"
EXPECTED_PROTOCOL_FINGERPRINT = "1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605"
EXPECTED_FEATURE_RUN_ID = 35867307338
EXPECTED_FEATURE_EVIDENCE_FINGERPRINT = "1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815"
EXPECTED_OUTCOME_RUN_ID = 35876715434
EXPECTED_OUTCOME_EVIDENCE_ARTIFACT_ID = 10758027876
EXPECTED_READINESS_ARTIFACT_ID = 10757578276


def build_model_run_source_gate(
    *,
    execution_status: Mapping[str, object],
    protocol_fingerprint_value: str,
    feature_run_id: int,
    feature_evidence_fingerprint: str,
    outcome_run_id: int,
    outcome_evidence_artifact_id: int,
    readiness_artifact_id: int,
) -> dict[str, object]:
    if execution_status.get("stage") != "MODEL_PROTOCOL_SOURCE_OPEN":
        raise ValueError("EXP-044 model-run gate requires MODEL_PROTOCOL_SOURCE_OPEN")
    if execution_status.get("readiness_verified") is not True:
        raise ValueError("EXP-044 model-run gate requires verified DEC-074 readiness")
    if execution_status.get("model_protocol_source_open_authorized") is not True:
        raise ValueError("EXP-044 model-run gate requires protocol-source authorization")
    if execution_status.get("feature_run_id") != feature_run_id:
        raise ValueError("EXP-044 model-run gate feature run mismatch")
    if execution_status.get("outcome_run_id") != outcome_run_id:
        raise ValueError("EXP-044 model-run gate outcome run mismatch")

    for field in (
        "model_protocol_result_authorized",
        "model_fit_authorized",
        "promotion_authorized",
        "shadow_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
    ):
        if execution_status.get(field) is not False:
            raise ValueError(f"EXP-044 model-run gate requires {field}=false")

    if MODEL_PROTOCOL_DECISION != "DEC-088":
        raise ValueError("EXP-044 model protocol decision identity drift")
    if MODEL_PROTOCOL_VERSION != "fmp-exp044-model-protocol-v1":
        raise ValueError("EXP-044 model protocol version identity drift")
    if protocol_fingerprint_value != EXPECTED_PROTOCOL_FINGERPRINT:
        raise ValueError("EXP-044 DEC-088 protocol fingerprint mismatch")
    if feature_run_id != EXPECTED_FEATURE_RUN_ID:
        raise ValueError("EXP-044 authoritative feature run mismatch")
    if feature_evidence_fingerprint != EXPECTED_FEATURE_EVIDENCE_FINGERPRINT:
        raise ValueError("EXP-044 authoritative feature evidence mismatch")
    if outcome_run_id != EXPECTED_OUTCOME_RUN_ID:
        raise ValueError("EXP-044 authoritative outcome run mismatch")
    if outcome_evidence_artifact_id != EXPECTED_OUTCOME_EVIDENCE_ARTIFACT_ID:
        raise ValueError("EXP-044 authoritative outcome evidence artifact mismatch")
    if readiness_artifact_id != EXPECTED_READINESS_ARTIFACT_ID:
        raise ValueError("EXP-044 authoritative readiness artifact mismatch")

    if MODEL_PROTOCOL_RESULT_AUTHORIZED is not False:
        raise ValueError("DEC-088 result authorization must remain false")
    if MODEL_FIT_AUTHORIZED is not False:
        raise ValueError("DEC-088 fit authorization must remain false")
    if PROMOTION_AUTHORIZED is not False:
        raise ValueError("DEC-088 promotion authorization must remain false")
    if REAL_MONEY_AUTHORIZED is not False:
        raise ValueError("DEC-088 real-money authorization must remain false")

    return {
        "stage": "MODEL_PROTOCOL_FROZEN",
        "next_action": "Implement a separate guarded EXP-044 model-run source/workflow under a later decision. Do not fit a model yet.",
        "model_protocol_frozen": True,
        "model_run_source_open_authorized": True,
        "model_protocol_decision": MODEL_PROTOCOL_DECISION,
        "model_protocol_version": MODEL_PROTOCOL_VERSION,
        "model_protocol_source_commit": EXPECTED_PROTOCOL_SOURCE_COMMIT,
        "model_protocol_fingerprint": EXPECTED_PROTOCOL_FINGERPRINT,
        "feature_run_id": EXPECTED_FEATURE_RUN_ID,
        "feature_evidence_fingerprint": EXPECTED_FEATURE_EVIDENCE_FINGERPRINT,
        "outcome_run_id": EXPECTED_OUTCOME_RUN_ID,
        "outcome_evidence_artifact_id": EXPECTED_OUTCOME_EVIDENCE_ARTIFACT_ID,
        "readiness_artifact_id": EXPECTED_READINESS_ARTIFACT_ID,
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


__all__ = [
    "EXPECTED_FEATURE_EVIDENCE_FINGERPRINT",
    "EXPECTED_FEATURE_RUN_ID",
    "EXPECTED_OUTCOME_EVIDENCE_ARTIFACT_ID",
    "EXPECTED_OUTCOME_RUN_ID",
    "EXPECTED_PROTOCOL_FINGERPRINT",
    "EXPECTED_PROTOCOL_SOURCE_COMMIT",
    "EXPECTED_READINESS_ARTIFACT_ID",
    "MODEL_RUN_GATE_DECISION",
    "build_model_run_source_gate",
]
