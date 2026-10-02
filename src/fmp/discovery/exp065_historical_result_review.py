from __future__ import annotations

DECISION = "DEC-468"
RUN_ID = 36905224184
RUN_HEAD_SHA = "5faa733572576aa5a1c56176ac27c415eaaf6416"
RUN_NUMBER = 1
RUN_ATTEMPT = 1
RUN_CONCLUSION = "success"
JOB_COUNT = 20
ARTIFACT_COUNT = 20

AGGREGATE_ARTIFACT_ID = 11202316160
AGGREGATE_ARTIFACT_DIGEST = "sha256:55e3a725127a1195a23159a6f8f8e187d90443f6e4df1be213a143c8e8868214"
AGGREGATE_RAW_JSON_SHA256 = "080d9e36c572d570f7890b51d543cb00821ba25f76164a6c6d289d9b6ccb8a62"
AGGREGATE_EVIDENCE_FINGERPRINT = "be0822560c0c4ec5a7dfc90e85c65d963621e04a4bd238ea078a4ac4d7a99682"
PROTOCOL_FINGERPRINT = "437e86d53094a52445b02956498b6b1bafcc91575efad1661dddf8aefaf0c4f0"
FEATURE_EVIDENCE_FINGERPRINT = "1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815"
OUTCOME_EVIDENCE_FINGERPRINT = "b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117"

TOTAL_NOMINAL_HYPOTHESES = 13680
TOTAL_EVALUABLE_HYPOTHESES = 13680
TOTAL_QUALIFYING_HYPOTHESES = 0
TOTAL_DEDUPLICATED_HYPOTHESES = 0
SHORTLIST_COUNT = 0
FROZEN_COUNT = 0
RESULT_STATE = "ZERO_PAIRWISE_INTERACTION_QUALIFIERS"
EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"
UNTOUCHED_OOS = False
RESERVED_ROBUSTNESS_OPENED = False

CELL_EVIDENCE_FINGERPRINTS = (
"b63610c51888623718f223410d71ee25a5294ebac27663e1c483c337818e7422",
"0a0ae5ccd53cfae7d546480bcb92fdeeb743fceae6c3684c9462cb918e6ce263",
"e72bb79a67b20ebfe611ac7bb92d375dfe4ab411859a1158bc36da3d91403407",
"dc181a773fca0eaaaa31f61f7dffbd5ea85b7333041cc11c57b742aebe915afe",
"1f4d5b330bc50fa7e466e33c478800fde532d3c5ee2c5d605a848a33396c6cb0",
"bdbf516c5853ba4e408f52ccc89dd241f003e655776a4cabfca9fe7a76e473cf",
"c6b22ad04794ed4d7ff7a92c8941f6cc604c8d232c337c4a7b132896b57f81f6",
"3715e51357fa276eec150de617e3acf79155ce336968407debb2b22e293a68cf",
"a61b9ecabad91dbfaa7012803345e73d8fc514040bf039460fcc483bfe31d670",
"19b001c1d021bcdb8bc12654d82f2119e7fa9e7615b1552d6bcb15597159e55b",
"961c7a43f35ddbe31c6c8386aac04373e92814268893a6c2cdb3d9e180078a51",
"4750ad12a9890af705e7cc89653d77dbe6add74a4aa9645e42c2fea6b2fbbfdf",
"8f33023987f8b917106e04cde4fcdac08459192156483aa830c9fb410ff56466",
"6e420df47c49fe2d3ba5aa60e225ddbae725c692281eca34428736e499c0fd38",
"4a26e5cca2c5a9751f39d0050b3a502892cf816e87822cd70996128a787987a1",
"56aae91070bfcdf607239e49cc496344ee4cc79fb5e505da9e34ff2b3be6299b",
"37fcd6664febe14c3c19c567922e97aaaaf51785974036b37f10e18cd095ee2f",
"c672bef3d4a08854689bf52f3dfd29132338f97b23697a90f918d051064deca5",
)

def historical_result_review() -> dict[str, object]:
    return {
        "decision": DECISION,
        "run_id": RUN_ID,
        "run_head_sha": RUN_HEAD_SHA,
        "run_number": RUN_NUMBER,
        "run_attempt": RUN_ATTEMPT,
        "run_conclusion": RUN_CONCLUSION,
        "job_count": JOB_COUNT,
        "artifact_count": ARTIFACT_COUNT,
        "aggregate_artifact_id": AGGREGATE_ARTIFACT_ID,
        "aggregate_artifact_digest": AGGREGATE_ARTIFACT_DIGEST,
        "aggregate_raw_json_sha256": AGGREGATE_RAW_JSON_SHA256,
        "aggregate_evidence_fingerprint": AGGREGATE_EVIDENCE_FINGERPRINT,
        "protocol_fingerprint": PROTOCOL_FINGERPRINT,
        "feature_evidence_fingerprint": FEATURE_EVIDENCE_FINGERPRINT,
        "outcome_evidence_fingerprint": OUTCOME_EVIDENCE_FINGERPRINT,
        "cell_evidence_fingerprints": CELL_EVIDENCE_FINGERPRINTS,
        "total_nominal_hypotheses": TOTAL_NOMINAL_HYPOTHESES,
        "total_evaluable_hypotheses": TOTAL_EVALUABLE_HYPOTHESES,
        "total_qualifying_hypotheses": TOTAL_QUALIFYING_HYPOTHESES,
        "total_deduplicated_hypotheses": TOTAL_DEDUPLICATED_HYPOTHESES,
        "shortlist_count": SHORTLIST_COUNT,
        "frozen_count": FROZEN_COUNT,
        "result_state": RESULT_STATE,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": UNTOUCHED_OOS,
        "reserved_robustness_opened": RESERVED_ROBUSTNESS_OPENED,
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
        "next_gate": "EXPLICIT_POST_EXP065_DISCOVERY_FIRST_RESEARCH_DIRECTION_DECISION",
    }
