from __future__ import annotations

from typing import Mapping, Sequence

from .exp062_adapter_proof_review import (
    EXP062_ADAPTER_PROOF_REVIEW_DECISION,
    classify_exp062_adapter_proof_terminal,
)
from .exp062_adapter_proof_content_review import (
    EXP062_ADAPTER_PROOF_CONTENT_REVIEW_DECISION,
    review_exp062_adapter_proof_content,
)


EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION = "DEC-297"
EXP062_ADAPTER_PROOF_RESULT_FREEZE_VERSION = (
    "fmp-exp062-adapter-proof-result-freeze-v1"
)

PROOF_RUN_ID = 36348366166
PROOF_HEAD_SHA = "5e235938dc7e8eb467f59ca85ae4b6e1d5179475"
PROOF_RUN_NUMBER = 1
PROOF_RUN_ATTEMPT = 1

CELL_ARTIFACT_BINDINGS = (
    (
        "EURUSD",
        "5m",
        10941671328,
        "exp062-dec294-adapter-probe-EURUSD-5m-" + PROOF_HEAD_SHA,
        "sha256:1044e35a44834c3ae93498d44e8824d462ae2627a7978d459ddf06ad711f46c9",
        "17f972dab7435ef4790c98b97bc8e1e2c220454da0bf1112d7a091c7438640dc",
    ),
    (
        "EURUSD",
        "15m",
        10941094396,
        "exp062-dec294-adapter-probe-EURUSD-15m-" + PROOF_HEAD_SHA,
        "sha256:28ede5e6cb5cf8a9a9caf6ba3ea2cedd7bb5371abe5393105ed37f6a933459ce",
        "ea83442a7f9ab0710006d522247dbe0065990e8bbd59fc98fae8a695e68c9472",
    ),
    (
        "EURUSD",
        "1h",
        10941517270,
        "exp062-dec294-adapter-probe-EURUSD-1h-" + PROOF_HEAD_SHA,
        "sha256:f53706c196f1646e3f8c4d89df893db7ba24d55e62ebed5e8ef12b99ce54a5d3",
        "eba299f5995df7c068803197a8798789d3686fe53d7a99e83e4e4163714a3dfd",
    ),
    (
        "GBPUSD",
        "5m",
        10940808485,
        "exp062-dec294-adapter-probe-GBPUSD-5m-" + PROOF_HEAD_SHA,
        "sha256:85c328e46bee232ead82a4b56d65462bab65d9aa3c922143a2f9f8ea08008983",
        "875bdadbc582d2fd20dbad50873f6310c1f41ff55f0b02c7622be3fa5ebe76ba",
    ),
    (
        "GBPUSD",
        "15m",
        10941502297,
        "exp062-dec294-adapter-probe-GBPUSD-15m-" + PROOF_HEAD_SHA,
        "sha256:998767ceab7f6b61998ef115c4ac58a2616294251c52a9098ea3be279c026cbd",
        "ec8a62eff6363498a025766ba99f6c6b37385bf00fd38e09e162b9ef449f0f01",
    ),
    (
        "GBPUSD",
        "1h",
        10941517129,
        "exp062-dec294-adapter-probe-GBPUSD-1h-" + PROOF_HEAD_SHA,
        "sha256:b11fda55aba34b7343f825fbc8ffcff76ba5cc4842b67ca194763f4df6f00aca",
        "159cf2f9b2b09bace8e20b26f1a6204d92e7f67de36e98dcabb6f17a88c2dd18",
    ),
    (
        "USDJPY",
        "5m",
        10940628528,
        "exp062-dec294-adapter-probe-USDJPY-5m-" + PROOF_HEAD_SHA,
        "sha256:87040beea532b66f75e1cc387f68c2a0acd7e53ab1879714fba7abd42fd8fcfa",
        "cfcab5225f384aaef89f330910fc238c2528a5f8d7c561c09a011920c823891f",
    ),
    (
        "USDJPY",
        "15m",
        10941695816,
        "exp062-dec294-adapter-probe-USDJPY-15m-" + PROOF_HEAD_SHA,
        "sha256:f27155332639932241527f902bbf11bcf1adc71f00eb55be68e74ee915fe9f32",
        "0d53fa4ef0ffbbb4e2c10cc4b73b32646382174877c686a8ce80c93010f64ec0",
    ),
    (
        "USDJPY",
        "1h",
        10940793448,
        "exp062-dec294-adapter-probe-USDJPY-1h-" + PROOF_HEAD_SHA,
        "sha256:d4649d05f44d4ac5d512aeaf50b8b762b92e18025a4c71dc6cfc959cfea58ab9",
        "a3f387c5352f01c978cacdbcd4290aba919db9aef27acb8999ee6bfe205a68a2",
    ),
)

AGGREGATE_ARTIFACT_ID = 10941770676
AGGREGATE_ARTIFACT_NAME = "exp062-dec294-adapter-proof-" + PROOF_HEAD_SHA
AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:ce22fba00e711ba91f29c797dba19814aea9b9c907df66e8bfd75aefdcc08e5b"
)
AGGREGATE_JSON_SHA256 = (
    "8f11806a4d2ffc4fb00a62360b35fc132efbb7f4e1ab44ea03a2244003dec056"
)

TOTAL_FEATURE_ROW_COUNT = 3576519
TOTAL_OUTCOME_ROW_COUNT = 7152783
TOTAL_RAW_NONFINITE_VALUE_COUNT = 6763
RAW_NONFINITE_BY_FEATURE = {
    "realized_vol_1h": 2683,
    "realized_vol_8h": 4070,
    "realized_vol_24h": 10,
}

HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
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


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def _validate_hash(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _expected_artifacts() -> dict[int, tuple[str, str, str]]:
    out: dict[int, tuple[str, str, str]] = {}
    for _, _, artifact_id, name, digest, raw_sha in CELL_ARTIFACT_BINDINGS:
        out[artifact_id] = (name, digest, raw_sha)
    out[AGGREGATE_ARTIFACT_ID] = (
        AGGREGATE_ARTIFACT_NAME,
        AGGREGATE_ARTIFACT_DIGEST,
        AGGREGATE_JSON_SHA256,
    )
    return out


def freeze_exp062_adapter_proof_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    cell_probes: Sequence[Mapping[str, object]],
    aggregate_proof: Mapping[str, object],
    artifact_zip_sha256_by_id: Mapping[int, str],
    artifact_json_sha256_by_id: Mapping[int, str],
) -> dict[str, object]:
    _require_exact(
        run,
        {
            "id": PROOF_RUN_ID,
            "name": "phase8a-exp062-adapter-proof",
            "path": ".github/workflows/phase8a-exp062-adapter-proof.yml",
            "event": "push",
            "head_branch": "main",
            "head_sha": PROOF_HEAD_SHA,
            "run_number": PROOF_RUN_NUMBER,
            "run_attempt": PROOF_RUN_ATTEMPT,
            "status": "completed",
            "conclusion": "success",
        },
        prefix="DEC-297 proof run",
    )

    terminal = classify_exp062_adapter_proof_terminal(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        expected_head_sha=PROOF_HEAD_SHA,
    )
    _require_exact(
        terminal,
        {
            "decision": EXP062_ADAPTER_PROOF_REVIEW_DECISION,
            "stage": "EXP062_ADAPTER_PROOF_SUCCESS_COMPLETE_REVIEW_REQUIRED",
            "proof_run_id": PROOF_RUN_ID,
            "proof_run_head_sha": PROOF_HEAD_SHA,
            "proof_run_conclusion": "success",
            "proof_run_attempt": 1,
            "proof_success_complete": True,
            "materialized_job_count": 10,
            "artifact_count": 10,
            "aggregate_content_review_required": True,
            "historical_discovery_execution_authorized": False,
            "discovery_result_authorized": False,
            "candidate_compilation_authorized": False,
            "trading_authorized": False,
        },
        prefix="DEC-297 terminal review",
    )

    expected_artifacts = _expected_artifacts()
    raw_artifacts = artifacts_payload.get("artifacts")
    if not isinstance(raw_artifacts, list) or len(raw_artifacts) != 10:
        raise ValueError("DEC-297 requires exactly ten artifacts")
    seen: set[int] = set()
    for item in raw_artifacts:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-297 artifact row is malformed")
        artifact_id = item.get("id")
        if not isinstance(artifact_id, int) or isinstance(artifact_id, bool):
            raise ValueError("DEC-297 artifact id is invalid")
        if artifact_id not in expected_artifacts:
            raise ValueError("DEC-297 unexpected artifact id")
        if artifact_id in seen:
            raise ValueError("DEC-297 duplicate artifact id")
        seen.add(artifact_id)
        expected_name, expected_digest, expected_raw_sha = expected_artifacts[
            artifact_id
        ]
        _require_exact(
            item,
            {
                "name": expected_name,
                "digest": expected_digest,
                "expired": False,
            },
            prefix=f"DEC-297 artifact {artifact_id}",
        )
        zip_sha = _validate_hash(
            artifact_zip_sha256_by_id.get(artifact_id),
            field=f"DEC-297 artifact {artifact_id} ZIP sha256",
        )
        if zip_sha != expected_digest.removeprefix("sha256:"):
            raise ValueError(f"DEC-297 artifact {artifact_id} ZIP sha256 mismatch")
        raw_sha = _validate_hash(
            artifact_json_sha256_by_id.get(artifact_id),
            field=f"DEC-297 artifact {artifact_id} JSON sha256",
        )
        if raw_sha != expected_raw_sha:
            raise ValueError(f"DEC-297 artifact {artifact_id} JSON sha256 mismatch")
    if seen != set(expected_artifacts):
        raise ValueError("DEC-297 artifact inventory mismatch")

    content = review_exp062_adapter_proof_content(
        terminal_review=terminal,
        cell_probes=cell_probes,
        aggregate_proof=aggregate_proof,
        expected_head_sha=PROOF_HEAD_SHA,
    )
    _require_exact(
        content,
        {
            "decision": EXP062_ADAPTER_PROOF_CONTENT_REVIEW_DECISION,
            "stage": "EXP062_ADAPTER_REPAIR_REAL_DATA_PROOF_VERIFIED",
            "proof_run_id": PROOF_RUN_ID,
            "proof_run_head_sha": PROOF_HEAD_SHA,
            "verified_cell_probe_count": 9,
            "aggregate_proof_verified": True,
            "all_nine_real_data_adapter_probes_successful": True,
            "total_feature_row_count": TOTAL_FEATURE_ROW_COUNT,
            "total_outcome_row_count": TOTAL_OUTCOME_ROW_COUNT,
            "total_raw_nonfinite_value_count": TOTAL_RAW_NONFINITE_VALUE_COUNT,
            "historical_discovery_execution_authorized": False,
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
        prefix="DEC-297 content review",
    )
    observed = content.get("raw_nonfinite_by_feature")
    if not isinstance(observed, Mapping):
        raise ValueError("DEC-297 non-finite summary is malformed")
    nonzero = {
        str(name): int(count)
        for name, count in observed.items()
        if int(count) != 0
    }
    if nonzero != RAW_NONFINITE_BY_FEATURE:
        raise ValueError("DEC-297 non-finite feature totals mismatch")

    return {
        "decision": EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION,
        "version": EXP062_ADAPTER_PROOF_RESULT_FREEZE_VERSION,
        "stage": "EXP062_ADAPTER_REPAIR_PROOF_FROZEN_AND_VERIFIED",
        "proof_run_id": PROOF_RUN_ID,
        "proof_run_head_sha": PROOF_HEAD_SHA,
        "proof_run_number": PROOF_RUN_NUMBER,
        "proof_run_attempt": PROOF_RUN_ATTEMPT,
        "proof_run_conclusion": "success",
        "proof_job_count": 10,
        "proof_artifact_count": 10,
        "verified_cell_probe_count": 9,
        "aggregate_artifact_id": AGGREGATE_ARTIFACT_ID,
        "aggregate_artifact_digest": AGGREGATE_ARTIFACT_DIGEST,
        "aggregate_json_sha256": AGGREGATE_JSON_SHA256,
        "total_feature_row_count": TOTAL_FEATURE_ROW_COUNT,
        "total_outcome_row_count": TOTAL_OUTCOME_ROW_COUNT,
        "total_raw_nonfinite_value_count": TOTAL_RAW_NONFINITE_VALUE_COUNT,
        "raw_nonfinite_by_feature": dict(RAW_NONFINITE_BY_FEATURE),
        "repair_verified_on_real_accepted_data": True,
        "repair_meaning": "NONFINITE_MISSING_VALUES_NORMALIZED_WITHOUT_MINING",
        "historical_discovery_execution_authorized": False,
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
    }


__all__ = [
    "AGGREGATE_ARTIFACT_DIGEST",
    "AGGREGATE_ARTIFACT_ID",
    "AGGREGATE_JSON_SHA256",
    "CELL_ARTIFACT_BINDINGS",
    "EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION",
    "EXP062_ADAPTER_PROOF_RESULT_FREEZE_VERSION",
    "PROOF_HEAD_SHA",
    "PROOF_RUN_ID",
    "RAW_NONFINITE_BY_FEATURE",
    "TOTAL_FEATURE_ROW_COUNT",
    "TOTAL_OUTCOME_ROW_COUNT",
    "TOTAL_RAW_NONFINITE_VALUE_COUNT",
    "freeze_exp062_adapter_proof_result",
]
