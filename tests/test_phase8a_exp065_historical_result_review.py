from fmp.discovery.exp065_historical_result_review import (
    CELL_EVIDENCE_FINGERPRINTS,
    historical_result_review,
)


def test_dec468_freezes_exact_success_result() -> None:
    review = historical_result_review()
    assert review["decision"] == "DEC-468"
    assert review["run_id"] == 36905224184
    assert review["run_head_sha"] == "5faa733572576aa5a1c56176ac27c415eaaf6416"
    assert review["run_number"] == 1
    assert review["run_attempt"] == 1
    assert review["run_conclusion"] == "success"
    assert review["job_count"] == 20
    assert review["artifact_count"] == 20
    assert review["aggregate_artifact_id"] == 11202316160
    assert review["aggregate_artifact_digest"] == "sha256:55e3a725127a1195a23159a6f8f8e187d90443f6e4df1be213a143c8e8868214"
    assert review["aggregate_raw_json_sha256"] == "080d9e36c572d570f7890b51d543cb00821ba25f76164a6c6d289d9b6ccb8a62"
    assert review["aggregate_evidence_fingerprint"] == "be0822560c0c4ec5a7dfc90e85c65d963621e04a4bd238ea078a4ac4d7a99682"
    assert review["total_nominal_hypotheses"] == 13680
    assert review["total_evaluable_hypotheses"] == 13680
    assert review["total_qualifying_hypotheses"] == 0
    assert review["total_deduplicated_hypotheses"] == 0
    assert review["shortlist_count"] == 0
    assert review["frozen_count"] == 0
    assert review["result_state"] == "ZERO_PAIRWISE_INTERACTION_QUALIFIERS"
    assert review["evidence_label"] == "RETROSPECTIVE_ALREADY_SEEN"
    assert review["untouched_oos"] is False
    assert review["reserved_robustness_opened"] is False
    assert len(CELL_EVIDENCE_FINGERPRINTS) == 18
    assert len(set(CELL_EVIDENCE_FINGERPRINTS)) == 18


def test_dec468_keeps_every_downstream_authority_closed() -> None:
    review = historical_result_review()
    for field in (
        "rerun_authorized",
        "retry_authorized",
        "replacement_run_authorized",
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
        assert review[field] is False
