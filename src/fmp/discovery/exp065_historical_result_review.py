from __future__ import annotations

from typing import Mapping, Sequence

from .exp065_historical_result_review_contract import (
    RUN_ATTEMPT,
    RUN_HEAD_SHA,
    RUN_ID,
    RUN_NUMBER,
    review_success_evidence as review_dec467_success_evidence,
    validate_success_run_shape as validate_dec467_success_run_shape,
)


EXP065_HISTORICAL_RESULT_REVIEW_DECISION = "DEC-468"
EXP065_HISTORICAL_RESULT_REVIEW_VERSION = "fmp-exp065-historical-result-review-v1"

RUN_NAME = "phase8a-exp065-pairwise-interaction"
RUN_PATH = ".github/workflows/phase8a-exp065-pairwise-interaction.yml"
RUN_EVENT = "workflow_dispatch"
RUN_BRANCH = "main"
RUN_STATUS = "completed"
RUN_CONCLUSION = "success"

EXPECTED_JOB_COUNT = 20
EXPECTED_ARTIFACT_COUNT = 20
EXPECTED_CELL_COUNT = 18

AGGREGATE_ARTIFACT_ID = 11202316160
AGGREGATE_ARTIFACT_NAME = (
    "phase8a-exp065-aggregate-"
    "5faa733572576aa5a1c56176ac27c415eaaf6416"
)
AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:55e3a725127a1195a23159a6f8f8e187d90443f6e4df1be213a143c8e8868214"
)
AGGREGATE_RAW_JSON_SHA256 = (
    "080d9e36c572d570f7890b51d543cb00821ba25f76164a6c6d289d9b6ccb8a62"
)
AGGREGATE_EVIDENCE_FINGERPRINT = (
    "be0822560c0c4ec5a7dfc90e85c65d963621e04a4bd238ea078a4ac4d7a99682"
)
PROTOCOL_FINGERPRINT = (
    "437e86d53094a52445b02956498b6b1bafcc91575efad1661dddf8aefaf0c4f0"
)
FEATURE_EVIDENCE_FINGERPRINT = (
    "1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815"
)
OUTCOME_EVIDENCE_FINGERPRINT = (
    "b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117"
)

TOTAL_HYPOTHESES = 13680
TOTAL_EVALUABLE_HYPOTHESES = 13680
TOTAL_QUALIFYING_HYPOTHESES = 0
TOTAL_DEDUPLICATED_HYPOTHESES = 0
PAIRWISE_INTERACTION_SHORTLIST_COUNT = 0
PAIRWISE_INTERACTION_FROZEN_COUNT = 0

EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"
OUTPUT_KIND = "RETROSPECTIVE_PAIRWISE_INTERACTION_HYPOTHESIS_NOT_VALIDATED"
RESULT_STATE = "ZERO_PAIRWISE_INTERACTION_QUALIFIERS"

STAGE = (
    "EXP065_HISTORICAL_RESULT_REVIEWED_AND_FROZEN_"
    "NO_PAIRWISE_INTERACTION_HYPOTHESES"
)
CLASSIFICATION = "NO_PAIRWISE_INTERACTION_HYPOTHESIS_PASSED_FROZEN_GATE"
GOVERNING_RESEARCH_METHOD = "DISCOVERY_FIRST_MARKET_PATTERN_RESEARCH"
NEGATIVE_RESULT_SCOPE = "EXACT_FROZEN_EXP065_PAIRWISE_INTERACTION_PROTOCOL_ONLY"
DISCOVERY_FIRST_METHOD_REJECTED = False
NEXT_GATE = "EXPLICIT_POST_EXP065_DISCOVERY_FIRST_RESEARCH_DIRECTION_DECISION"

RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False

EXPECTED_CELL_EVIDENCE_FINGERPRINTS = {
    ("EURUSD", "15m", 60): "e72bb79a67b20ebfe611ac7bb92d375dfe4ab411859a1158bc36da3d91403407",
    ("EURUSD", "15m", 240): "dc181a773fca0eaaaa31f61f7dffbd5ea85b7333041cc11c57b742aebe915afe",
    ("EURUSD", "1h", 60): "1f4d5b330bc50fa7e466e33c478800fde532d3c5ee2c5d605a848a33396c6cb0",
    ("EURUSD", "1h", 240): "bdbf516c5853ba4e408f52ccc89dd241f003e655776a4cabfca9fe7a76e473cf",
    ("EURUSD", "5m", 60): "b63610c51888623718f223410d71ee25a5294ebac27663e1c483c337818e7422",
    ("EURUSD", "5m", 240): "0a0ae5ccd53cfae7d546480bcb92fdeeb743fceae6c3684c9462cb918e6ce263",
    ("GBPUSD", "15m", 60): "a61b9ecabad91dbfaa7012803345e73d8fc514040bf039460fcc483bfe31d670",
    ("GBPUSD", "15m", 240): "19b001c1d021bcdb8bc12654d82f2119e7fa9e7615b1552d6bcb15597159e55b",
    ("GBPUSD", "1h", 60): "961c7a43f35ddbe31c6c8386aac04373e92814268893a6c2cdb3d9e180078a51",
    ("GBPUSD", "1h", 240): "4750ad12a9890af705e7cc89653d77dbe6add74a4aa9645e42c2fea6b2fbbfdf",
    ("GBPUSD", "5m", 60): "c6b22ad04794ed4d7ff7a92c8941f6cc604c8d232c337c4a7b132896b57f81f6",
    ("GBPUSD", "5m", 240): "3715e51357fa276eec150de617e3acf79155ce336968407debb2b22e293a68cf",
    ("USDJPY", "15m", 60): "4a26e5cca2c5a9751f39d0050b3a502892cf816e87822cd70996128a787987a1",
    ("USDJPY", "15m", 240): "56aae91070bfcdf607239e49cc496344ee4cc79fb5e505da9e34ff2b3be6299b",
    ("USDJPY", "1h", 60): "37fcd6664febe14c3c19c567922e97aaaaf51785974036b37f10e18cd095ee2f",
    ("USDJPY", "1h", 240): "c672bef3d4a08854689bf52f3dfd29132338f97b23697a90f918d051064deca5",
    ("USDJPY", "5m", 60): "8f33023987f8b917106e04cde4fcdac08459192156483aa830c9fb410ff56466",
    ("USDJPY", "5m", 240): "6e420df47c49fe2d3ba5aa60e225ddbae725c692281eca34428736e499c0fd38",
}


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def validate_terminal_run(
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
) -> dict[str, object]:
    reviewed = validate_dec467_success_run_shape(run, jobs_payload, artifacts_payload)
    _require_exact(
        reviewed,
        {
            "run_id": RUN_ID,
            "run_head_sha": RUN_HEAD_SHA,
            "run_number": RUN_NUMBER,
            "run_attempt": RUN_ATTEMPT,
            "run_status": RUN_STATUS,
            "run_conclusion": RUN_CONCLUSION,
            "job_count": EXPECTED_JOB_COUNT,
            "artifact_count": EXPECTED_ARTIFACT_COUNT,
            "aggregate_artifact_id": AGGREGATE_ARTIFACT_ID,
            "aggregate_artifact_name": AGGREGATE_ARTIFACT_NAME,
            "aggregate_artifact_digest": AGGREGATE_ARTIFACT_DIGEST,
            "success_shape_verified": True,
        },
        prefix="DEC-468 terminal review",
    )
    return {
        "run_verified": True,
        "job_count": EXPECTED_JOB_COUNT,
        "artifact_count": EXPECTED_ARTIFACT_COUNT,
        "aggregate_artifact_id": AGGREGATE_ARTIFACT_ID,
        "aggregate_artifact_name": AGGREGATE_ARTIFACT_NAME,
        "aggregate_artifact_digest": AGGREGATE_ARTIFACT_DIGEST,
    }


def review_frozen_success_evidence(
    *,
    aggregate: Mapping[str, object],
    cell_evidence: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    reviewed = review_dec467_success_evidence(
        aggregate=aggregate,
        cell_evidence=cell_evidence,
    )
    _require_exact(
        reviewed,
        {
            "evidence_verified": True,
            "result_state": RESULT_STATE,
            "aggregate_evidence_fingerprint": AGGREGATE_EVIDENCE_FINGERPRINT,
            "protocol_fingerprint": PROTOCOL_FINGERPRINT,
            "feature_evidence_fingerprint": FEATURE_EVIDENCE_FINGERPRINT,
            "outcome_evidence_fingerprint": OUTCOME_EVIDENCE_FINGERPRINT,
            "verified_cell_count": EXPECTED_CELL_COUNT,
            "total_hypotheses": TOTAL_HYPOTHESES,
            "total_evaluable_hypotheses": TOTAL_EVALUABLE_HYPOTHESES,
            "total_qualifying_hypotheses": TOTAL_QUALIFYING_HYPOTHESES,
            "total_deduplicated_hypotheses": TOTAL_DEDUPLICATED_HYPOTHESES,
            "pairwise_interaction_shortlist_count": PAIRWISE_INTERACTION_SHORTLIST_COUNT,
            "pairwise_interaction_frozen_count": PAIRWISE_INTERACTION_FROZEN_COUNT,
            "evidence_label": EVIDENCE_LABEL,
            "untouched_oos": False,
            "reserved_robustness_opened": False,
        },
        prefix="DEC-468 frozen evidence",
    )

    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-468 requires exactly 18 cell evidence objects")
    seen: set[tuple[object, object, object]] = set()
    for value in cell_evidence:
        cell = value.get("cell")
        if not isinstance(cell, Mapping):
            raise ValueError("DEC-468 cell evidence missing cell identity")
        identity = (
            cell.get("symbol"),
            cell.get("timeframe"),
            cell.get("horizon_minutes"),
        )
        if identity in seen:
            raise ValueError("DEC-468 cell evidence identity duplicated")
        seen.add(identity)
        expected_fingerprint = EXPECTED_CELL_EVIDENCE_FINGERPRINTS.get(identity)
        if expected_fingerprint is None:
            raise ValueError("DEC-468 cell evidence identity mismatch")
        if value.get("evidence_fingerprint") != expected_fingerprint:
            raise ValueError("DEC-468 cell evidence fingerprint identity drift")

        section = value.get("pairwise_interaction")
        if not isinstance(section, Mapping):
            raise ValueError("DEC-468 pairwise-interaction section missing")
        _require_exact(
            section,
            {
                "hypothesis_count": 760,
                "evaluable_hypothesis_count": 760,
                "qualifying_hypothesis_count": 0,
                "deduplicated_hypothesis_count": 0,
                "shortlist": [],
                "frozen_hypothesis_fingerprints": [],
                "output_kind": OUTPUT_KIND,
            },
            prefix="DEC-468 cell result",
        )

    if seen != set(EXPECTED_CELL_EVIDENCE_FINGERPRINTS):
        raise ValueError("DEC-468 cell evidence universe incomplete")

    return {
        **reviewed,
        "classification": CLASSIFICATION,
        "negative_result_scope": NEGATIVE_RESULT_SCOPE,
        "discovery_first_method_rejected": DISCOVERY_FIRST_METHOD_REJECTED,
    }


def historical_result_review_payload() -> dict[str, object]:
    return {
        "decision": EXP065_HISTORICAL_RESULT_REVIEW_DECISION,
        "version": EXP065_HISTORICAL_RESULT_REVIEW_VERSION,
        "stage": STAGE,
        "classification": CLASSIFICATION,
        "result_state": RESULT_STATE,
        "governing_research_method": GOVERNING_RESEARCH_METHOD,
        "negative_result_scope": NEGATIVE_RESULT_SCOPE,
        "discovery_first_method_rejected": DISCOVERY_FIRST_METHOD_REJECTED,
        "run_id": RUN_ID,
        "run_head_sha": RUN_HEAD_SHA,
        "run_number": RUN_NUMBER,
        "run_attempt": RUN_ATTEMPT,
        "run_status": RUN_STATUS,
        "run_conclusion": RUN_CONCLUSION,
        "job_count": EXPECTED_JOB_COUNT,
        "artifact_count": EXPECTED_ARTIFACT_COUNT,
        "aggregate_artifact_id": AGGREGATE_ARTIFACT_ID,
        "aggregate_artifact_name": AGGREGATE_ARTIFACT_NAME,
        "aggregate_artifact_digest": AGGREGATE_ARTIFACT_DIGEST,
        "aggregate_raw_json_sha256": AGGREGATE_RAW_JSON_SHA256,
        "aggregate_evidence_fingerprint": AGGREGATE_EVIDENCE_FINGERPRINT,
        "protocol_fingerprint": PROTOCOL_FINGERPRINT,
        "feature_evidence_fingerprint": FEATURE_EVIDENCE_FINGERPRINT,
        "outcome_evidence_fingerprint": OUTCOME_EVIDENCE_FINGERPRINT,
        "verified_cell_count": EXPECTED_CELL_COUNT,
        "total_hypotheses": TOTAL_HYPOTHESES,
        "total_evaluable_hypotheses": TOTAL_EVALUABLE_HYPOTHESES,
        "total_qualifying_hypotheses": TOTAL_QUALIFYING_HYPOTHESES,
        "total_deduplicated_hypotheses": TOTAL_DEDUPLICATED_HYPOTHESES,
        "pairwise_interaction_shortlist_count": PAIRWISE_INTERACTION_SHORTLIST_COUNT,
        "pairwise_interaction_frozen_count": PAIRWISE_INTERACTION_FROZEN_COUNT,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "reserved_robustness_opened": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": NEXT_GATE,
    }


__all__ = [
    "AGGREGATE_ARTIFACT_DIGEST",
    "AGGREGATE_ARTIFACT_ID",
    "AGGREGATE_ARTIFACT_NAME",
    "AGGREGATE_EVIDENCE_FINGERPRINT",
    "AGGREGATE_RAW_JSON_SHA256",
    "CLASSIFICATION",
    "DISCOVERY_FIRST_METHOD_REJECTED",
    "EXP065_HISTORICAL_RESULT_REVIEW_DECISION",
    "EXP065_HISTORICAL_RESULT_REVIEW_VERSION",
    "EXPECTED_CELL_EVIDENCE_FINGERPRINTS",
    "GOVERNING_RESEARCH_METHOD",
    "NEGATIVE_RESULT_SCOPE",
    "NEXT_GATE",
    "PAIRWISE_INTERACTION_FROZEN_COUNT",
    "PAIRWISE_INTERACTION_SHORTLIST_COUNT",
    "RUN_HEAD_SHA",
    "RUN_ID",
    "STAGE",
    "TOTAL_EVALUABLE_HYPOTHESES",
    "TOTAL_HYPOTHESES",
    "TOTAL_QUALIFYING_HYPOTHESES",
    "historical_result_review_payload",
    "review_frozen_success_evidence",
    "validate_terminal_run",
]
