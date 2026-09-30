from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .exp062_historical_result_content_review import (
    EXP062_AGGREGATE_ARTIFACT_DIGEST,
    EXP062_AGGREGATE_ARTIFACT_ID,
    EXP062_AGGREGATE_EVIDENCE_FINGERPRINT,
    EXP062_AGGREGATE_JSON_SHA256,
    EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION,
    EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_VERSION,
    EXP062_HISTORICAL_RUN_HEAD_SHA,
    EXP062_HISTORICAL_RUN_ID,
)
from .exp062_run_contract import (
    EXP062_EXPERIMENT_ID,
    expected_aggregate_artifact_name,
)


EXP062_HISTORICAL_RESULT_REVIEW_FREEZE_DECISION = "DEC-441"
EXP062_HISTORICAL_RESULT_REVIEW_FREEZE_VERSION = (
    "fmp-exp062-historical-result-review-freeze-v1"
)

DEC440_REVIEW_SOURCE_BLOB_SHA = "17facb0f77f6419de5f8a74f80019bb7289fe984"

_FALSE_AUTHORITY_FIELDS = (
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


def _sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character SHA-256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _sha256_digest(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"{field} must use sha256:<hex>")
    _sha256(value.removeprefix("sha256:"), field=field)
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _nonnegative_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def _validate_reviewed_result(
    value: Mapping[str, object],
) -> None:
    _require_exact(
        value,
        {
            "decision": EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_DECISION,
            "version": EXP062_HISTORICAL_RESULT_CONTENT_REVIEW_VERSION,
            "stage": (
                "EXP062_HISTORICAL_RESULT_CONTENT_REVIEWED_"
                "NO_VALIDATION_ACCEPTED"
            ),
            "experiment_id": EXP062_EXPERIMENT_ID,
            "terminal_review_decision": "DEC-334",
            "terminal_review_version": (
                "fmp-exp062-historical-terminal-review-contract-v1"
            ),
            "historical_run_id": EXP062_HISTORICAL_RUN_ID,
            "historical_run_head_sha": EXP062_HISTORICAL_RUN_HEAD_SHA,
            "historical_run_number": 2,
            "historical_run_attempt": 1,
            "historical_run_conclusion": "success",
            "historical_result_slot_consumed": True,
            "aggregate_artifact_id": EXP062_AGGREGATE_ARTIFACT_ID,
            "aggregate_artifact_name": expected_aggregate_artifact_name(
                code_commit=EXP062_HISTORICAL_RUN_HEAD_SHA,
            ),
            "aggregate_artifact_digest": EXP062_AGGREGATE_ARTIFACT_DIGEST,
            "aggregate_json_sha256": EXP062_AGGREGATE_JSON_SHA256,
            "aggregate_evidence_fingerprint": (
                EXP062_AGGREGATE_EVIDENCE_FINGERPRINT
            ),
            "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
            "untouched_oos": False,
            "verified_cell_count": 18,
            "discovery_shortlist_count": 67,
            "confirmation_frozen_count": 11,
            "validation_accepted_count": 0,
            "aggregate_result_content_review_required": False,
            "historical_result_review_complete": True,
            "validation_accepted_candidates_present": False,
            "next_gate": "IMMUTABLE_HISTORICAL_RESULT_REVIEW_FREEZE",
        },
        prefix="DEC-441 reviewed result",
    )

    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-441 reviewed result {field} must remain false"
            )

    _positive_int(
        value.get("historical_run_id"),
        field="DEC-441 historical_run_id",
    )
    _positive_int(
        value.get("aggregate_artifact_id"),
        field="DEC-441 aggregate_artifact_id",
    )
    _sha256_digest(
        value.get("aggregate_artifact_digest"),
        field="DEC-441 aggregate_artifact_digest",
    )
    _sha256(
        value.get("aggregate_json_sha256"),
        field="DEC-441 aggregate_json_sha256",
    )
    _sha256(
        value.get("aggregate_evidence_fingerprint"),
        field="DEC-441 aggregate_evidence_fingerprint",
    )
    _positive_int(
        value.get("verified_cell_count"),
        field="DEC-441 verified_cell_count",
    )
    _nonnegative_int(
        value.get("discovery_shortlist_count"),
        field="DEC-441 discovery_shortlist_count",
    )
    _nonnegative_int(
        value.get("confirmation_frozen_count"),
        field="DEC-441 confirmation_frozen_count",
    )
    _nonnegative_int(
        value.get("validation_accepted_count"),
        field="DEC-441 validation_accepted_count",
    )


def freeze_exp062_historical_result_review(
    reviewed_result: Mapping[str, object],
) -> dict[str, object]:
    _validate_reviewed_result(reviewed_result)

    frozen: dict[str, object] = {
        "decision": EXP062_HISTORICAL_RESULT_REVIEW_FREEZE_DECISION,
        "version": EXP062_HISTORICAL_RESULT_REVIEW_FREEZE_VERSION,
        "stage": (
            "EXP062_HISTORICAL_RESULT_REVIEWED_AND_FROZEN_"
            "NO_VALIDATION_ACCEPTED"
        ),
        "source_review_decision": reviewed_result["decision"],
        "source_review_version": reviewed_result["version"],
        "source_review_blob_sha": DEC440_REVIEW_SOURCE_BLOB_SHA,
        "experiment_id": reviewed_result["experiment_id"],
        "terminal_review_decision": reviewed_result[
            "terminal_review_decision"
        ],
        "terminal_review_version": reviewed_result[
            "terminal_review_version"
        ],
        "historical_run_id": reviewed_result["historical_run_id"],
        "historical_run_head_sha": reviewed_result[
            "historical_run_head_sha"
        ],
        "historical_run_number": reviewed_result[
            "historical_run_number"
        ],
        "historical_run_attempt": reviewed_result[
            "historical_run_attempt"
        ],
        "historical_run_conclusion": reviewed_result[
            "historical_run_conclusion"
        ],
        "historical_result_slot_consumed": True,
        "aggregate_artifact_id": reviewed_result[
            "aggregate_artifact_id"
        ],
        "aggregate_artifact_name": reviewed_result[
            "aggregate_artifact_name"
        ],
        "aggregate_artifact_digest": reviewed_result[
            "aggregate_artifact_digest"
        ],
        "aggregate_json_sha256": reviewed_result[
            "aggregate_json_sha256"
        ],
        "aggregate_evidence_fingerprint": reviewed_result[
            "aggregate_evidence_fingerprint"
        ],
        "evidence_label": reviewed_result["evidence_label"],
        "untouched_oos": False,
        "verified_cell_count": reviewed_result["verified_cell_count"],
        "discovery_shortlist_count": reviewed_result[
            "discovery_shortlist_count"
        ],
        "confirmation_frozen_count": reviewed_result[
            "confirmation_frozen_count"
        ],
        "validation_accepted_count": reviewed_result[
            "validation_accepted_count"
        ],
        "historical_result_review_complete": True,
        "validation_accepted_candidates_present": False,
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
        "next_gate": "EXPLICIT_POST_EXP062_RESEARCH_DIRECTION_DECISION",
    }
    frozen["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "DEC440_REVIEW_SOURCE_BLOB_SHA",
    "EXP062_HISTORICAL_RESULT_REVIEW_FREEZE_DECISION",
    "EXP062_HISTORICAL_RESULT_REVIEW_FREEZE_VERSION",
    "freeze_exp062_historical_result_review",
]
