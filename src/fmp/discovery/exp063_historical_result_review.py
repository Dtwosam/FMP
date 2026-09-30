from __future__ import annotations

import hashlib
import json
from typing import Mapping, Sequence


EXP063_HISTORICAL_RESULT_REVIEW_DECISION = "DEC-450"
EXP063_HISTORICAL_RESULT_REVIEW_VERSION = (
    "fmp-exp063-historical-result-review-v1"
)

RUN_ID = 36773288493
RUN_NAME = "phase8a-exp063-persistence"
RUN_PATH = ".github/workflows/phase8a-exp063-persistence.yml"
RUN_EVENT = "workflow_dispatch"
RUN_BRANCH = "main"
RUN_HEAD_SHA = "6b106e4514f6ca3f06c677aab66fb04eb37ad881"
RUN_NUMBER = 1
RUN_ATTEMPT = 1
RUN_STATUS = "completed"
RUN_CONCLUSION = "success"

EXPECTED_JOB_COUNT = 20
EXPECTED_ARTIFACT_COUNT = 20
EXPECTED_CELL_COUNT = 18

AGGREGATE_ARTIFACT_ID = 11127203563
AGGREGATE_ARTIFACT_NAME = (
    "phase8a-exp063-aggregate-"
    "6b106e4514f6ca3f06c677aab66fb04eb37ad881"
)
AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:4d730f2dfdb6e6ef7201eb2d9ce48678f29882df8075a396254f5051425611d3"
)
AGGREGATE_RAW_JSON_SHA256 = (
    "c012740e856b351320cb95c06583d8db2c3120cce8d14e26e091594a505f24ad"
)
AGGREGATE_EVIDENCE_FINGERPRINT = (
    "d0562d29da38c8ee4c0d3b28c35b3de7c9c42a5157910eef319a91b67ca4be42"
)
PROTOCOL_FINGERPRINT = (
    "fce16ec83e695a05ebbeffaa99a5705039852182d4150956d62dc056e37ef8c5"
)

TOTAL_ENUMERATED_PATTERNS = 37350
TOTAL_DIRECTIONAL_HYPOTHESES = 74700
TOTAL_QUALIFYING_DIRECTIONAL_HYPOTHESES = 0
TOTAL_DEDUPLICATED_DIRECTIONAL_HYPOTHESES = 0
PERSISTENCE_SHORTLIST_COUNT = 0
PERSISTENCE_FROZEN_COUNT = 0

EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"
OUTPUT_KIND = "RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED"

UNTouched_OOS = False
RESERVED_ROBUSTNESS_OPENED = False
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

STAGE = "EXP063_HISTORICAL_RESULT_REVIEWED_AND_FROZEN_NO_PERSISTENCE_HYPOTHESES"
CLASSIFICATION = "NO_DIRECTIONAL_HYPOTHESIS_PASSED_FROZEN_PERSISTENCE_GATE"


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


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
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


def _job_rows(jobs_payload: Mapping[str, object]) -> list[Mapping[str, object]]:
    raw = jobs_payload.get("jobs")
    if not isinstance(raw, list):
        raise ValueError("DEC-450 jobs payload must contain jobs")
    out: list[Mapping[str, object]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-450 job row malformed")
        out.append(item)
    return out


def _artifact_rows(
    artifacts_payload: Mapping[str, object],
) -> list[Mapping[str, object]]:
    raw = artifacts_payload.get("artifacts")
    if not isinstance(raw, list):
        raise ValueError("DEC-450 artifacts payload must contain artifacts")
    out: list[Mapping[str, object]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-450 artifact row malformed")
        out.append(item)
    return out


def validate_terminal_run(
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
) -> dict[str, object]:
    _require_exact(
        run,
        {
            "id": RUN_ID,
            "name": RUN_NAME,
            "path": RUN_PATH,
            "event": RUN_EVENT,
            "head_branch": RUN_BRANCH,
            "head_sha": RUN_HEAD_SHA,
            "run_number": RUN_NUMBER,
            "run_attempt": RUN_ATTEMPT,
            "status": RUN_STATUS,
            "conclusion": RUN_CONCLUSION,
        },
        prefix="DEC-450 run",
    )

    jobs = _job_rows(jobs_payload)
    if len(jobs) != EXPECTED_JOB_COUNT:
        raise ValueError("DEC-450 requires exactly 20 jobs")
    names = [item.get("name") for item in jobs]
    if len(names) != len(set(names)):
        raise ValueError("DEC-450 job names duplicated")
    for item in jobs:
        if item.get("status") != "completed" or item.get("conclusion") != "success":
            raise ValueError("DEC-450 requires every job to complete successfully")

    artifacts = _artifact_rows(artifacts_payload)
    if len(artifacts) != EXPECTED_ARTIFACT_COUNT:
        raise ValueError("DEC-450 requires exactly 20 artifacts")
    artifact_names = [item.get("name") for item in artifacts]
    if len(artifact_names) != len(set(artifact_names)):
        raise ValueError("DEC-450 artifact names duplicated")
    for item in artifacts:
        if item.get("expired") is not False:
            raise ValueError("DEC-450 requires every artifact to be non-expired")

    aggregate = [
        item for item in artifacts if item.get("id") == AGGREGATE_ARTIFACT_ID
    ]
    if len(aggregate) != 1:
        raise ValueError("DEC-450 aggregate artifact identity mismatch")
    _require_exact(
        aggregate[0],
        {
            "name": AGGREGATE_ARTIFACT_NAME,
            "digest": AGGREGATE_ARTIFACT_DIGEST,
            "expired": False,
        },
        prefix="DEC-450 aggregate artifact",
    )

    return {
        "run_verified": True,
        "job_count": len(jobs),
        "artifact_count": len(artifacts),
        "aggregate_artifact_id": AGGREGATE_ARTIFACT_ID,
        "aggregate_artifact_name": AGGREGATE_ARTIFACT_NAME,
        "aggregate_artifact_digest": AGGREGATE_ARTIFACT_DIGEST,
    }


def validate_aggregate_evidence(
    aggregate: Mapping[str, object],
) -> dict[str, object]:
    stored_fingerprint = _validate_sha256(
        aggregate.get("evidence_fingerprint"),
        field="DEC-450 aggregate evidence fingerprint",
    )
    unsigned = dict(aggregate)
    unsigned.pop("evidence_fingerprint", None)
    computed = hashlib.sha256(_canonical_json(unsigned)).hexdigest()
    if stored_fingerprint != computed:
        raise ValueError("DEC-450 aggregate evidence fingerprint mismatch")
    if stored_fingerprint != AGGREGATE_EVIDENCE_FINGERPRINT:
        raise ValueError("DEC-450 aggregate evidence fingerprint identity drift")

    _require_exact(
        aggregate,
        {
            "experiment_id": "EXP-20260930-063",
            "code_commit": RUN_HEAD_SHA,
            "protocol_fingerprint": PROTOCOL_FINGERPRINT,
            "evidence_label": EVIDENCE_LABEL,
            "untouched_oos": False,
            "expected_cell_count": EXPECTED_CELL_COUNT,
            "verified_cell_count": EXPECTED_CELL_COUNT,
            "persistence_shortlist_count": PERSISTENCE_SHORTLIST_COUNT,
            "persistence_frozen_count": PERSISTENCE_FROZEN_COUNT,
            "output_kind": OUTPUT_KIND,
            "reserved_robustness_opened": False,
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
        prefix="DEC-450 aggregate",
    )

    cells = aggregate.get("cells")
    if not isinstance(cells, list) or len(cells) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-450 aggregate cell inventory mismatch")
    identities: set[tuple[object, object, object]] = set()
    for item in cells:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-450 aggregate cell row malformed")
        identity = (
            item.get("symbol"),
            item.get("timeframe"),
            item.get("horizon_minutes"),
        )
        if identity in identities:
            raise ValueError("DEC-450 aggregate cell identity duplicated")
        identities.add(identity)
        if item.get("persistence_shortlist_count") != 0:
            raise ValueError("DEC-450 cell shortlist count must be zero")
        if item.get("persistence_frozen_count") != 0:
            raise ValueError("DEC-450 cell frozen count must be zero")
        if item.get("persistence_shortlist_fingerprints") != []:
            raise ValueError("DEC-450 cell shortlist fingerprints must be empty")
        if item.get("persistence_frozen_fingerprints") != []:
            raise ValueError("DEC-450 cell frozen fingerprints must be empty")
        if item.get("output_kind") != OUTPUT_KIND:
            raise ValueError("DEC-450 cell output kind mismatch")

    return {
        "aggregate_verified": True,
        "aggregate_evidence_fingerprint": stored_fingerprint,
        "verified_cell_count": len(cells),
        "persistence_shortlist_count": 0,
        "persistence_frozen_count": 0,
    }


def review_cell_evidence(
    cell_evidence: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-450 requires exactly 18 cell evidence objects")

    total_enumerated = 0
    total_directional = 0
    total_qualifying = 0
    total_deduplicated = 0
    seen: set[tuple[object, object, object]] = set()

    for value in cell_evidence:
        cell = value.get("cell")
        persistence = value.get("persistence")
        if not isinstance(cell, Mapping) or not isinstance(persistence, Mapping):
            raise ValueError("DEC-450 cell evidence malformed")
        identity = (
            cell.get("symbol"),
            cell.get("timeframe"),
            cell.get("horizon_minutes"),
        )
        if identity in seen:
            raise ValueError("DEC-450 cell evidence identity duplicated")
        seen.add(identity)

        unsigned = dict(value)
        fingerprint = _validate_sha256(
            unsigned.pop("evidence_fingerprint", None),
            field="DEC-450 cell evidence fingerprint",
        )
        if hashlib.sha256(_canonical_json(unsigned)).hexdigest() != fingerprint:
            raise ValueError("DEC-450 cell evidence fingerprint mismatch")

        total_enumerated += int(persistence.get("enumerated_pattern_count", -1))
        total_directional += int(
            persistence.get("directional_hypothesis_count", -1)
        )
        total_qualifying += int(
            persistence.get("qualifying_directional_hypothesis_count", -1)
        )
        total_deduplicated += int(
            persistence.get("deduplicated_directional_hypothesis_count", -1)
        )
        if persistence.get("shortlist") != []:
            raise ValueError("DEC-450 cell shortlist must be empty")
        if persistence.get("frozen_pattern_fingerprints") != []:
            raise ValueError("DEC-450 cell frozen inventory must be empty")

    if total_enumerated != TOTAL_ENUMERATED_PATTERNS:
        raise ValueError("DEC-450 total enumerated pattern count mismatch")
    if total_directional != TOTAL_DIRECTIONAL_HYPOTHESES:
        raise ValueError("DEC-450 total directional hypothesis count mismatch")
    if total_qualifying != TOTAL_QUALIFYING_DIRECTIONAL_HYPOTHESES:
        raise ValueError("DEC-450 qualifying hypothesis count mismatch")
    if total_deduplicated != TOTAL_DEDUPLICATED_DIRECTIONAL_HYPOTHESES:
        raise ValueError("DEC-450 deduplicated hypothesis count mismatch")

    return {
        "cell_evidence_verified": True,
        "verified_cell_count": len(seen),
        "total_enumerated_patterns": total_enumerated,
        "total_directional_hypotheses": total_directional,
        "total_qualifying_directional_hypotheses": total_qualifying,
        "total_deduplicated_directional_hypotheses": total_deduplicated,
    }


def historical_result_review_payload() -> dict[str, object]:
    return {
        "decision": EXP063_HISTORICAL_RESULT_REVIEW_DECISION,
        "version": EXP063_HISTORICAL_RESULT_REVIEW_VERSION,
        "stage": STAGE,
        "classification": CLASSIFICATION,
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
        "verified_cell_count": EXPECTED_CELL_COUNT,
        "total_enumerated_patterns": TOTAL_ENUMERATED_PATTERNS,
        "total_directional_hypotheses": TOTAL_DIRECTIONAL_HYPOTHESES,
        "total_qualifying_directional_hypotheses": (
            TOTAL_QUALIFYING_DIRECTIONAL_HYPOTHESES
        ),
        "total_deduplicated_directional_hypotheses": (
            TOTAL_DEDUPLICATED_DIRECTIONAL_HYPOTHESES
        ),
        "persistence_shortlist_count": PERSISTENCE_SHORTLIST_COUNT,
        "persistence_frozen_count": PERSISTENCE_FROZEN_COUNT,
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
        "next_gate": "EXPLICIT_POST_EXP063_RESEARCH_DIRECTION_DECISION",
    }


__all__ = [
    "AGGREGATE_ARTIFACT_DIGEST",
    "AGGREGATE_ARTIFACT_ID",
    "AGGREGATE_ARTIFACT_NAME",
    "AGGREGATE_EVIDENCE_FINGERPRINT",
    "AGGREGATE_RAW_JSON_SHA256",
    "CLASSIFICATION",
    "EXP063_HISTORICAL_RESULT_REVIEW_DECISION",
    "EXP063_HISTORICAL_RESULT_REVIEW_VERSION",
    "PERSISTENCE_FROZEN_COUNT",
    "PERSISTENCE_SHORTLIST_COUNT",
    "RUN_HEAD_SHA",
    "RUN_ID",
    "STAGE",
    "TOTAL_DIRECTIONAL_HYPOTHESES",
    "TOTAL_QUALIFYING_DIRECTIONAL_HYPOTHESES",
    "historical_result_review_payload",
    "review_cell_evidence",
    "validate_aggregate_evidence",
    "validate_terminal_run",
]
