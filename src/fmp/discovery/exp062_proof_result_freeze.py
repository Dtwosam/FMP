from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .exp062_proof_contract import (
    EXP062_GATE_PROOF_CONTRACT_DECISION,
    EXP062_GATE_PROOF_CONTRACT_VERSION,
)
from .exp062_proof_executor import (
    EXP062_PROOF_EXECUTOR_DECISION,
    EXP062_PROOF_EXECUTOR_VERSION,
)
from .exp062_proof_result_review import (
    EXP062_PROOF_RESULT_REVIEW_DECISION,
    EXP062_PROOF_RESULT_REVIEW_VERSION,
)


EXP062_REVIEWED_GATE_PROOF_FREEZE_DECISION = "DEC-305"
EXP062_REVIEWED_GATE_PROOF_FREEZE_VERSION = (
    "fmp-exp062-reviewed-gate-proof-freeze-v1"
)

_FALSE_AUTHORITY_FIELDS = (
    "historical_result_slot_consumed",
    "historical_result_slot_open_authorized",
    "historical_discovery_execution_occurred",
    "proof_dispatch_authorized",
    "historical_result_dispatch_authorized",
    "historical_discovery_execution_authorized",
    "discovery_result_authorized",
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
)


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


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_positive_int(value: object, *, field: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        raise ValueError(f"{field} must be a positive integer")
    return value


def _validate_nonnegative_int(value: object, *, field: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
    ):
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _validate_sha256_digest(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"{field} must use sha256:<hex>")
    raw = value.removeprefix("sha256:")
    if len(raw) != 64:
        raise ValueError(f"{field} must contain 64 hex characters")
    try:
        int(raw, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_reviewed_result(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> None:
    exact = {
        "decision": EXP062_PROOF_RESULT_REVIEW_DECISION,
        "version": EXP062_PROOF_RESULT_REVIEW_VERSION,
        "stage": "EXP062_GATE_PROOF_RESULT_REVIEWED_FAIL_CLOSED",
        "proof_contract_decision": EXP062_GATE_PROOF_CONTRACT_DECISION,
        "proof_contract_version": EXP062_GATE_PROOF_CONTRACT_VERSION,
        "proof_executor_decision": EXP062_PROOF_EXECUTOR_DECISION,
        "proof_executor_version": EXP062_PROOF_EXECUTOR_VERSION,
        "proof_head_sha": expected_head_sha,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "failure",
        "cell_result_artifact_count": 0,
        "aggregate_result_artifact_count": 0,
        "proof_dispatch_submitted": True,
        "next_gate": (
            "IMMUTABLE_PROOF_RESULT_FREEZE_BEFORE_HISTORICAL_SLOT"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-305 reviewed result {field} mismatch")

    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-305 reviewed result {field} must remain false"
            )

    _validate_positive_int(
        value.get("proof_run_id"),
        field="DEC-305 proof_run_id",
    )
    _validate_positive_int(
        value.get("preflight_artifact_id"),
        field="DEC-305 preflight_artifact_id",
    )
    _validate_sha256_digest(
        value.get("preflight_artifact_digest"),
        field="DEC-305 preflight_artifact_digest",
    )

    materialized = _validate_positive_int(
        value.get("materialized_job_count"),
        field="DEC-305 materialized_job_count",
    )
    downstream = _validate_nonnegative_int(
        value.get("materialized_downstream_job_count"),
        field="DEC-305 materialized_downstream_job_count",
    )
    if downstream >= materialized:
        raise ValueError(
            "DEC-305 downstream job count must exclude preflight"
        )

    names = value.get("materialized_downstream_job_names")
    if not isinstance(names, list):
        raise ValueError(
            "DEC-305 materialized downstream job names must be a list"
        )
    if len(names) != downstream:
        raise ValueError(
            "DEC-305 materialized downstream job count mismatch"
        )
    if any(
        not isinstance(name, str) or not name.strip()
        for name in names
    ):
        raise ValueError(
            "DEC-305 materialized downstream job name is invalid"
        )
    if len(set(names)) != len(names):
        raise ValueError(
            "DEC-305 materialized downstream job names must be unique"
        )

    placeholder = value.get(
        "github_unexpanded_matrix_placeholder_present"
    )
    if not isinstance(placeholder, bool):
        raise ValueError(
            "DEC-305 matrix-placeholder flag must be boolean"
        )


def freeze_reviewed_gate_proof_result(
    reviewed_result: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    _validate_reviewed_result(
        reviewed_result,
        expected_head_sha=expected_head_sha,
    )

    frozen: dict[str, object] = {
        "decision": EXP062_REVIEWED_GATE_PROOF_FREEZE_DECISION,
        "version": EXP062_REVIEWED_GATE_PROOF_FREEZE_VERSION,
        "stage": "EXP062_GATE_PROOF_REVIEWED_FAIL_CLOSED_AND_FROZEN",
        "source_review_decision": reviewed_result["decision"],
        "source_review_version": reviewed_result["version"],
        "proof_contract_decision": reviewed_result[
            "proof_contract_decision"
        ],
        "proof_contract_version": reviewed_result[
            "proof_contract_version"
        ],
        "proof_executor_decision": reviewed_result[
            "proof_executor_decision"
        ],
        "proof_executor_version": reviewed_result[
            "proof_executor_version"
        ],
        "proof_outcome": "EXPECTED_FAIL_CLOSED_EXECUTION_GATE",
        "proof_run_id": reviewed_result["proof_run_id"],
        "proof_head_sha": expected_head_sha,
        "proof_run_number": reviewed_result["proof_run_number"],
        "proof_run_attempt": reviewed_result["proof_run_attempt"],
        "proof_run_conclusion": reviewed_result[
            "proof_run_conclusion"
        ],
        "preflight_artifact_id": reviewed_result[
            "preflight_artifact_id"
        ],
        "preflight_artifact_digest": reviewed_result[
            "preflight_artifact_digest"
        ],
        "materialized_job_count": reviewed_result[
            "materialized_job_count"
        ],
        "materialized_downstream_job_count": reviewed_result[
            "materialized_downstream_job_count"
        ],
        "materialized_downstream_job_names": list(
            reviewed_result["materialized_downstream_job_names"]
        ),
        "github_unexpanded_matrix_placeholder_present": (
            reviewed_result[
                "github_unexpanded_matrix_placeholder_present"
            ]
        ),
        "fail_closed_semantics_verified": True,
        "historical_result_slot_consumed": False,
        "historical_result_slot_open_authorized": False,
        "historical_discovery_execution_occurred": False,
        "cell_result_artifact_count": 0,
        "aggregate_result_artifact_count": 0,
        "proof_rerun_authorized": False,
        "proof_retry_authorized": False,
        "proof_replacement_authorized": False,
        "historical_result_dispatch_authorized": False,
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
        "next_gate": (
            "SOURCE_ONLY_HISTORICAL_RUN_AUTHORIZATION_CONTRACT"
        ),
    }
    frozen["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "EXP062_REVIEWED_GATE_PROOF_FREEZE_DECISION",
    "EXP062_REVIEWED_GATE_PROOF_FREEZE_VERSION",
    "freeze_reviewed_gate_proof_result",
]
