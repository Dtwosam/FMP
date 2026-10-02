from fmp.discovery.exp065_historical_result_review import historical_result_review

def test_dec468_freezes_result() -> None:
    review = historical_result_review()
    assert review["decision"] == "DEC-468"
    assert review["run_id"] == 36905224184
    assert review["total_nominal_hypotheses"] == 13680
    assert review["total_evaluable_hypotheses"] == 13680
    assert review["total_qualifying_hypotheses"] == 0
    assert review["result_state"] == "ZERO_PAIRWISE_INTERACTION_QUALIFIERS"
    assert review["untouched_oos"] is False
