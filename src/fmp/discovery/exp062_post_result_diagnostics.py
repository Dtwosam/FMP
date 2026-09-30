from __future__ import annotations

from collections import Counter


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-442"
SOURCE_FREEZE_DECISION = "DEC-441"
SOURCE_FREEZE_MERGE_SHA = "d5e8ad7cd98ec1511742d1b266e6779852155c96"
SOURCE_FREEZE_BLOB_SHA = "ae0353fce77e9ff03536f2323820804dbda7241c"
SOURCE_EXPERIMENT_ID = "EXP-20260927-062"
SOURCE_HISTORICAL_RUN_ID = 36714210992
SOURCE_HISTORICAL_HEAD_SHA = "013395092804de6b0ef51537081ab8443b8b91be"
SOURCE_AGGREGATE_EVIDENCE_FINGERPRINT = (
    "b8019226fb7fce14c6711834fe16cdbb52795d9ca8996b1ed98ede7ecfba9506"
)

CONFIRMATION_MIN_SUPPORT = 75
VALIDATION_MIN_TOTAL_SUPPORT = 200
VALIDATION_MIN_YEAR_SUPPORT = 40
VALIDATION_MIN_POSITIVE_YEARS = 3
VALIDATION_YEAR_COUNT = 4

CELL_SOURCES = (
    {
        "symbol": "EURUSD",
        "timeframe": "15m",
        "horizon_minutes": 240,
        "artifact_id": 11095339152,
        "artifact_digest": (
            "sha256:31e7df76d2bf14dae56d2aa48173485"
            "a59b12ca18cd2ccf1be9e08d38d534ba1"
        ),
        "cell_json_sha256": (
            "e3b9765e5b12f1864a3859d8dfa940e"
            "2ed6878c1c1173e6b99902da73c4015da"
        ),
        "cell_evidence_fingerprint": (
            "ddc8da1e2857f857c20ce808ab2d2955"
            "79b579a7800d06207d685f0faf0c52c9"
        ),
        "frozen_pattern_count": 3,
    },
    {
        "symbol": "EURUSD",
        "timeframe": "1h",
        "horizon_minutes": 240,
        "artifact_id": 11095214565,
        "artifact_digest": (
            "sha256:d9c9196a425504c03bbc9bf5ae3e1417"
            "a30bde01c79e783c8e6f9bdbab45c82d"
        ),
        "cell_json_sha256": (
            "a23624079bd93e01ae96371f25c6bd49"
            "2953eb61b917c2057610bd1ba6d2b11d"
        ),
        "cell_evidence_fingerprint": (
            "2307ce27219f1d5ca7bf4ef6c9b39969"
            "933994d377422dfe8ef371596adfef5d"
        ),
        "frozen_pattern_count": 2,
    },
    {
        "symbol": "EURUSD",
        "timeframe": "5m",
        "horizon_minutes": 240,
        "artifact_id": 11095614187,
        "artifact_digest": (
            "sha256:e84a24be6068b655cdc81e5263b3f062"
            "6710fa0339ac9f03ccd63fcd20b441b8"
        ),
        "cell_json_sha256": (
            "f922713ecd8e7064e549b64c84eea75f"
            "a8e8e01897a7a1f89c7e26c5c088df34"
        ),
        "cell_evidence_fingerprint": (
            "abac9345e2bb951e9278b9cf83ac1366"
            "164fb7a640f6babd8c6ce97c7c953d84"
        ),
        "frozen_pattern_count": 2,
    },
    {
        "symbol": "GBPUSD",
        "timeframe": "15m",
        "horizon_minutes": 240,
        "artifact_id": 11096870214,
        "artifact_digest": (
            "sha256:d147c958944440fb9d1db831be25668e"
            "eb0e22c57c413ac99fc96613b7bfcc8d"
        ),
        "cell_json_sha256": (
            "1eea23107aab83da5b9342983f6f19d8"
            "190127947f5f4cdd2c625680d096faf1"
        ),
        "cell_evidence_fingerprint": (
            "8afc977ebf2f90de491e5129f7b254bb"
            "04d0c83fa26246f4b21e26bddd1dec23"
        ),
        "frozen_pattern_count": 2,
    },
    {
        "symbol": "GBPUSD",
        "timeframe": "1h",
        "horizon_minutes": 240,
        "artifact_id": 11095901780,
        "artifact_digest": (
            "sha256:18a138ec503d49027f64aeab77ded3e7"
            "c8e2d9dabc97d78cde7eb24c98de8ccb"
        ),
        "cell_json_sha256": (
            "842bff74e09e2fdca4854a71c9ec8469"
            "8b5a1fdd0de587ce3c81dcd738518636"
        ),
        "cell_evidence_fingerprint": (
            "bb2bc5933698a4bb132f337c21d388f8"
            "05f7c892a413fe0437473b32e51a58d2"
        ),
        "frozen_pattern_count": 1,
    },
    {
        "symbol": "GBPUSD",
        "timeframe": "5m",
        "horizon_minutes": 240,
        "artifact_id": 11096166535,
        "artifact_digest": (
            "sha256:6986fb74a907a016d7e7a4a0f499d0c"
            "4c24dc544f7bcd56ea4e203f951b7f723"
        ),
        "cell_json_sha256": (
            "cbb6c5fd5b5f8849ce570b19416b3ae4"
            "3b69e20b1a9ab85fa6628b41121585e0"
        ),
        "cell_evidence_fingerprint": (
            "f935cfbc4065f996a32abd3f7d2613b7"
            "96965d4fb43123ba629e174082fe543f"
        ),
        "frozen_pattern_count": 1,
    },
)

CANDIDATES = (
    ("EURUSD", "15m", 240, "6207c7c6c60cf5bcf4bda365865a8744fc525ceb92cb4e109598c39a79300eb9", 196, 3.340816326530456, 2640, 199, 0, -3.024393939393941),
    ("EURUSD", "15m", 240, "e7bcaa1eafdc61968e7d4cec724a6aa3db56059966003071566c910cda3faff0", 362, 2.8994475138122273, 2106, 54, 1, -1.7145299145299642),
    ("EURUSD", "15m", 240, "b0fbaeb88f6327bd359a8edca85f5850f458107f70c4127f444512518fb9a4c2", 1472, 0.5785326086956198, 4961, 1050, 2, -0.22481354565614933),
    ("EURUSD", "1h", 240, "a6985abd8ddb8f05ebe29b8c5fe41b008a75e1e3f2b6814db6351e14ce9f6c8a", 370, 0.9397297297297569, 1177, 228, 2, -0.7514868309260823),
    ("EURUSD", "1h", 240, "79027d4adcd34a7a9834160e8470119b80a27a0ca65e4a630e14db2664db21ea", 363, 0.12617079889809085, 1237, 263, 2, -0.16119644300730013),
    ("EURUSD", "5m", 240, "7eed8f75d0c13b9623fe1095af892252e406cf064776a3fb5d26c1908eb28f50", 558, 3.6983870967740824, 7682, 591, 0, -2.8876204113512136),
    ("EURUSD", "5m", 240, "2577804363ad5ad85753135a001bf0e16b8f8e8aeafb376585ae557ea7e75082", 4393, 0.4998634190757892, 14838, 3114, 2, -0.24581479983826723),
    ("GBPUSD", "15m", 240, "fbed69c88e341c89431a4bb7b392d5619f274ab126f9593a8cd52c6be2ccab0a", 1436, 0.8191504178272646, 4427, 869, 1, -0.6015134402530152),
    ("GBPUSD", "15m", 240, "4ecc4381a47cabce40df3b11aa189b25be2ed6b70708a1e3b880354ca5225a31", 521, 4.530134357005766, 2796, 115, 1, -6.9608726752503385),
    ("GBPUSD", "1h", 240, "59dd3690711b4d746287f553bf276e2892fd15a8a653146b72f6b75dc527c351", 124, 5.457258064516046, 716, 29, 1, -6.294553072625681),
    ("GBPUSD", "5m", 240, "2e92ea4e066daf0696141d62d4785adab4ce22325563fcdfcd4be5a94178e246", 1562, 5.051856594110125, 8324, 358, 1, -7.144521864488217),
)

RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
THRESHOLD_RELAXATION_AUTHORIZED = False
PATTERN_REDEFINITION_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = False
SUCCESSOR_RESULT_EXECUTION_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _failure_reasons(row: tuple[object, ...]) -> tuple[str, ...]:
    (
        _symbol,
        _timeframe,
        _horizon,
        _fingerprint,
        confirmation_support,
        confirmation_mean,
        validation_total_support,
        validation_min_year_support,
        validation_positive_year_count,
        validation_aggregate_mean,
    ) = row
    reasons: list[str] = []
    if validation_total_support < VALIDATION_MIN_TOTAL_SUPPORT:
        reasons.append("VALIDATION_TOTAL_SUPPORT_LT_200")
    if validation_min_year_support < VALIDATION_MIN_YEAR_SUPPORT:
        reasons.append("VALIDATION_YEAR_SUPPORT_LT_40")
    if validation_positive_year_count < VALIDATION_MIN_POSITIVE_YEARS:
        reasons.append("VALIDATION_POSITIVE_YEARS_LT_3")
    if validation_aggregate_mean <= 0:
        reasons.append("VALIDATION_AGGREGATE_MEAN_NOT_POSITIVE")
    if confirmation_support < CONFIRMATION_MIN_SUPPORT or confirmation_mean <= 0:
        reasons.append("CONFIRMATION_GATE_DRIFT")
    return tuple(reasons)


def build_exp062_post_result_diagnostic() -> dict[str, object]:
    if len(CANDIDATES) != 11:
        raise ValueError("DEC-442 frozen candidate count drift")
    if sum(int(row["frozen_pattern_count"]) for row in CELL_SOURCES) != 11:
        raise ValueError("DEC-442 frozen cell-source count drift")

    fingerprints = [str(row[3]) for row in CANDIDATES]
    if len(set(fingerprints)) != len(fingerprints):
        raise ValueError("DEC-442 duplicate candidate fingerprint")

    cell_counts = Counter((str(row[0]), str(row[1]), int(row[2])) for row in CANDIDATES)
    expected_cell_counts = Counter(
        {
            ("EURUSD", "15m", 240): 3,
            ("EURUSD", "1h", 240): 2,
            ("EURUSD", "5m", 240): 2,
            ("GBPUSD", "15m", 240): 2,
            ("GBPUSD", "1h", 240): 1,
            ("GBPUSD", "5m", 240): 1,
        }
    )
    if cell_counts != expected_cell_counts:
        raise ValueError("DEC-442 candidate cell distribution drift")

    reason_counts: Counter[str] = Counter()
    candidate_rows: list[dict[str, object]] = []
    for row in CANDIDATES:
        reasons = _failure_reasons(row)
        reason_counts.update(reasons)
        if "CONFIRMATION_GATE_DRIFT" in reasons:
            raise ValueError("DEC-442 confirmation survivor no longer passes confirmation")
        candidate_rows.append(
            {
                "symbol": row[0],
                "timeframe": row[1],
                "horizon_minutes": row[2],
                "pattern_fingerprint": row[3],
                "confirmation_support": row[4],
                "confirmation_mean_net_pips_0p5": row[5],
                "validation_total_support": row[6],
                "validation_min_year_support": row[7],
                "validation_positive_year_count": row[8],
                "validation_aggregate_mean_net_pips_0p5": row[9],
                "failure_reasons": list(reasons),
            }
        )

    expected_reason_counts = {
        "VALIDATION_AGGREGATE_MEAN_NOT_POSITIVE": 11,
        "VALIDATION_POSITIVE_YEARS_LT_3": 11,
        "VALIDATION_YEAR_SUPPORT_LT_40": 1,
    }
    if dict(sorted(reason_counts.items())) != dict(sorted(expected_reason_counts.items())):
        raise ValueError("DEC-442 validation failure accounting drift")

    return {
        "decision": POST_RESULT_DIAGNOSTIC_DECISION,
        "stage": "EXP062_POST_RESULT_DIAGNOSTIC_REVIEWED_NO_PERSISTENT_VALIDATION_EDGE",
        "diagnostic_classification": (
            "CONFIRMATION_EDGE_DID_NOT_PERSIST_THROUGH_2019_2022_VALIDATION"
        ),
        "source_freeze_decision": SOURCE_FREEZE_DECISION,
        "source_freeze_merge_sha": SOURCE_FREEZE_MERGE_SHA,
        "source_freeze_blob_sha": SOURCE_FREEZE_BLOB_SHA,
        "source_experiment_id": SOURCE_EXPERIMENT_ID,
        "source_historical_run_id": SOURCE_HISTORICAL_RUN_ID,
        "source_historical_head_sha": SOURCE_HISTORICAL_HEAD_SHA,
        "source_aggregate_evidence_fingerprint": (
            SOURCE_AGGREGATE_EVIDENCE_FINGERPRINT
        ),
        "validation_gate": {
            "minimum_total_support": VALIDATION_MIN_TOTAL_SUPPORT,
            "minimum_support_each_year": VALIDATION_MIN_YEAR_SUPPORT,
            "minimum_positive_years": VALIDATION_MIN_POSITIVE_YEARS,
            "year_count": VALIDATION_YEAR_COUNT,
            "require_positive_aggregate_mean_net_pips_at_0p5": True,
        },
        "cell_sources": [dict(row) for row in CELL_SOURCES],
        "candidate_count": 11,
        "candidate_cell_count": 6,
        "all_candidates_horizon_minutes": 240,
        "symbols_with_confirmation_survivors": ["EURUSD", "GBPUSD"],
        "usd_jpy_confirmation_survivor_count": 0,
        "horizon_60_confirmation_survivor_count": 0,
        "validation_accepted_count": 0,
        "validation_failure_reason_counts": dict(reason_counts),
        "candidate_diagnostics": candidate_rows,
        "interpretation": {
            "confirmation_gate_functioned": True,
            "broad_validation_sample_size_shortage": False,
            "validation_year_support_shortfall_candidate_count": 1,
            "all_candidates_failed_positive_year_persistence": True,
            "all_candidates_failed_positive_aggregate_validation_mean": True,
            "result_consistent_with_temporal_economic_non_persistence": True,
            "runtime_or_adapter_failure_detected": False,
        },
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "threshold_relaxation_authorized": THRESHOLD_RELAXATION_AUTHORIZED,
        "pattern_redefinition_authorized": PATTERN_REDEFINITION_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "successor_protocol_source_open_authorized": (
            SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED
        ),
        "successor_result_execution_authorized": (
            SUCCESSOR_RESULT_EXECUTION_AUTHORIZED
        ),
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": "EXPLICIT_POST_EXP062_RESEARCH_DIRECTION_DECISION_AFTER_DIAGNOSTIC",
    }


__all__ = [
    "POST_RESULT_DIAGNOSTIC_DECISION",
    "SOURCE_FREEZE_BLOB_SHA",
    "SOURCE_FREEZE_MERGE_SHA",
    "build_exp062_post_result_diagnostic",
]
