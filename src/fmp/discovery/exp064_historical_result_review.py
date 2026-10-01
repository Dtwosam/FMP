from __future__ import annotations

import hashlib
import json
from typing import Mapping, Sequence


EXP064_HISTORICAL_RESULT_REVIEW_DECISION = "DEC-458"
EXP064_HISTORICAL_RESULT_REVIEW_VERSION = (
    "fmp-exp064-historical-result-review-v1"
)

RUN_ID = 36853290904
RUN_NAME = "phase8a-exp064-continuous-stability"
RUN_PATH = ".github/workflows/phase8a-exp064-continuous-stability.yml"
RUN_EVENT = "workflow_dispatch"
RUN_BRANCH = "main"
RUN_HEAD_SHA = "b13f89f4d6bef8b1ab4a2fa12c6b01d0e5067506"
RUN_NUMBER = 1
RUN_ATTEMPT = 1
RUN_STATUS = "completed"
RUN_CONCLUSION = "success"

EXPECTED_JOB_COUNT = 20
EXPECTED_ARTIFACT_COUNT = 20
EXPECTED_CELL_COUNT = 18

AGGREGATE_ARTIFACT_ID = 11158816828
AGGREGATE_ARTIFACT_NAME = (
    "phase8a-exp064-aggregate-"
    "b13f89f4d6bef8b1ab4a2fa12c6b01d0e5067506"
)
AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:a404c053a5dd6989cf0efb2adba2cb276fec9a66a448a8617e7dac7da50c577f"
)
AGGREGATE_RAW_JSON_SHA256 = (
    "b971340204ec2a6136559dc467f84f1e6b69f1c58fe3c5cca01e437ba6c80284"
)
AGGREGATE_EVIDENCE_FINGERPRINT = (
    "832e8c814ac578b614764d37cba15e64569e2f841dfa6f72f2c9cd9a8fdbcbb1"
)
PROTOCOL_FINGERPRINT = (
    "0fe6f992f0d6c27b1d7998561005f37b07f89c8715edd874ee8eb8f8d79ca7e0"
)
FEATURE_EVIDENCE_FINGERPRINT = (
    "1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815"
)
OUTCOME_EVIDENCE_FINGERPRINT = (
    "b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117"
)

TOTAL_HYPOTHESES = 1440
TOTAL_EVALUABLE_HYPOTHESES = 1440
TOTAL_QUALIFYING_HYPOTHESES = 0
TOTAL_DEDUPLICATED_HYPOTHESES = 0
CONTINUOUS_STABILITY_SHORTLIST_COUNT = 0
CONTINUOUS_STABILITY_FROZEN_COUNT = 0

EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"
OUTPUT_KIND = "RETROSPECTIVE_CONTINUOUS_STABILITY_HYPOTHESIS_NOT_VALIDATED"

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

STAGE = (
    "EXP064_HISTORICAL_RESULT_REVIEWED_AND_FROZEN_"
    "NO_CONTINUOUS_STABILITY_HYPOTHESES"
)
CLASSIFICATION = "NO_CONTINUOUS_STABILITY_HYPOTHESIS_PASSED_FROZEN_GATE"

SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
TIMEFRAMES = ("5m", "15m", "1h")
HORIZONS_MINUTES = (60, 240)
EXPECTED_CELLS = tuple(
    (symbol, timeframe, horizon)
    for symbol in SYMBOLS
    for timeframe in TIMEFRAMES
    for horizon in HORIZONS_MINUTES
)

EXPECTED_JOB_NAMES = {
    "exp064-preflight",
    "exp064-aggregate",
    *{
        f"exp064-cell-{symbol}-{timeframe}-{horizon}m"
        for symbol, timeframe, horizon in EXPECTED_CELLS
    },
}

EXPECTED_ARTIFACT_NAMES = {
    f"phase8a-exp064-preflight-{RUN_HEAD_SHA}",
    f"phase8a-exp064-aggregate-{RUN_HEAD_SHA}",
    *{
        f"phase8a-exp064-cell-{symbol}-{timeframe}-{horizon}m-{RUN_HEAD_SHA}"
        for symbol, timeframe, horizon in EXPECTED_CELLS
    },
}


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


def _rows(
    payload: Mapping[str, object],
    *,
    field: str,
    decision_label: str,
) -> list[Mapping[str, object]]:
    raw = payload.get(field)
    if not isinstance(raw, list):
        raise ValueError(f"{decision_label} payload must contain {field}")
    out: list[Mapping[str, object]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError(f"{decision_label} {field} row malformed")
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
        prefix="DEC-458 run",
    )

    jobs = _rows(
        jobs_payload,
        field="jobs",
        decision_label="DEC-458 jobs",
    )
    if len(jobs) != EXPECTED_JOB_COUNT:
        raise ValueError("DEC-458 requires exactly 20 jobs")
    names = [item.get("name") for item in jobs]
    if len(names) != len(set(names)):
        raise ValueError("DEC-458 job names duplicated")
    if set(names) != EXPECTED_JOB_NAMES:
        raise ValueError("DEC-458 job inventory mismatch")
    for item in jobs:
        if item.get("status") != "completed" or item.get("conclusion") != "success":
            raise ValueError("DEC-458 requires every job to complete successfully")

    artifacts = _rows(
        artifacts_payload,
        field="artifacts",
        decision_label="DEC-458 artifacts",
    )
    if len(artifacts) != EXPECTED_ARTIFACT_COUNT:
        raise ValueError("DEC-458 requires exactly 20 artifacts")
    artifact_names = [item.get("name") for item in artifacts]
    if len(artifact_names) != len(set(artifact_names)):
        raise ValueError("DEC-458 artifact names duplicated")
    if set(artifact_names) != EXPECTED_ARTIFACT_NAMES:
        raise ValueError("DEC-458 artifact inventory mismatch")
    for item in artifacts:
        if item.get("expired") is not False:
            raise ValueError("DEC-458 requires every artifact to be non-expired")

    aggregate = [
        item for item in artifacts if item.get("id") == AGGREGATE_ARTIFACT_ID
    ]
    if len(aggregate) != 1:
        raise ValueError("DEC-458 aggregate artifact identity mismatch")
    _require_exact(
        aggregate[0],
        {
            "name": AGGREGATE_ARTIFACT_NAME,
            "digest": AGGREGATE_ARTIFACT_DIGEST,
            "expired": False,
        },
        prefix="DEC-458 aggregate artifact",
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
        field="DEC-458 aggregate evidence fingerprint",
    )
    unsigned = dict(aggregate)
    unsigned.pop("evidence_fingerprint", None)
    computed = hashlib.sha256(_canonical_json(unsigned)).hexdigest()
    if stored_fingerprint != computed:
        raise ValueError("DEC-458 aggregate evidence fingerprint mismatch")
    if stored_fingerprint != AGGREGATE_EVIDENCE_FINGERPRINT:
        raise ValueError("DEC-458 aggregate evidence fingerprint identity drift")

    _require_exact(
        aggregate,
        {
            "experiment_id": "EXP-20261001-064",
            "code_commit": RUN_HEAD_SHA,
            "protocol_fingerprint": PROTOCOL_FINGERPRINT,
            "feature_evidence_fingerprint": FEATURE_EVIDENCE_FINGERPRINT,
            "outcome_evidence_fingerprint": OUTCOME_EVIDENCE_FINGERPRINT,
            "evidence_label": EVIDENCE_LABEL,
            "untouched_oos": False,
            "expected_cell_count": EXPECTED_CELL_COUNT,
            "verified_cell_count": EXPECTED_CELL_COUNT,
            "continuous_stability_shortlist_count": (
                CONTINUOUS_STABILITY_SHORTLIST_COUNT
            ),
            "continuous_stability_frozen_count": (
                CONTINUOUS_STABILITY_FROZEN_COUNT
            ),
            "output_kind": OUTPUT_KIND,
            "reserved_robustness_opened": False,
            "source_access_authorized": False,
            "historical_execution_authorized": False,
            "historical_result_authorized": False,
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
        prefix="DEC-458 aggregate",
    )

    cells = aggregate.get("cells")
    if not isinstance(cells, list) or len(cells) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-458 aggregate cell inventory mismatch")

    seen: set[tuple[object, object, object]] = set()
    cell_fingerprints: set[str] = set()
    total_hypotheses = 0
    total_evaluable = 0
    total_qualifying = 0
    total_deduplicated = 0

    for item in cells:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-458 aggregate cell row malformed")
        identity = (
            item.get("symbol"),
            item.get("timeframe"),
            item.get("horizon_minutes"),
        )
        if identity not in EXPECTED_CELLS:
            raise ValueError("DEC-458 aggregate cell identity mismatch")
        if identity in seen:
            raise ValueError("DEC-458 aggregate cell identity duplicated")
        seen.add(identity)

        cell_fp = _validate_sha256(
            item.get("cell_evidence_fingerprint"),
            field="DEC-458 cell evidence fingerprint",
        )
        if cell_fp in cell_fingerprints:
            raise ValueError("DEC-458 cell evidence fingerprint duplicated")
        cell_fingerprints.add(cell_fp)

        if item.get("hypothesis_count") != 80:
            raise ValueError("DEC-458 cell hypothesis count mismatch")
        if item.get("evaluable_hypothesis_count") != 80:
            raise ValueError("DEC-458 cell evaluable hypothesis count mismatch")
        if item.get("qualifying_hypothesis_count") != 0:
            raise ValueError("DEC-458 cell qualifying count must be zero")
        if item.get("deduplicated_hypothesis_count") != 0:
            raise ValueError("DEC-458 cell deduplicated count must be zero")
        if item.get("continuous_stability_shortlist_count") != 0:
            raise ValueError("DEC-458 cell shortlist count must be zero")
        if item.get("continuous_stability_frozen_count") != 0:
            raise ValueError("DEC-458 cell frozen count must be zero")
        if item.get("continuous_stability_shortlist_fingerprints") != []:
            raise ValueError("DEC-458 cell shortlist fingerprints must be empty")
        if item.get("continuous_stability_frozen_fingerprints") != []:
            raise ValueError("DEC-458 cell frozen fingerprints must be empty")
        if item.get("output_kind") != OUTPUT_KIND:
            raise ValueError("DEC-458 cell output kind mismatch")

        total_hypotheses += 80
        total_evaluable += 80

    if seen != set(EXPECTED_CELLS):
        raise ValueError("DEC-458 aggregate cell universe incomplete")
    if total_hypotheses != TOTAL_HYPOTHESES:
        raise ValueError("DEC-458 total hypothesis count mismatch")
    if total_evaluable != TOTAL_EVALUABLE_HYPOTHESES:
        raise ValueError("DEC-458 total evaluable hypothesis count mismatch")
    if total_qualifying != TOTAL_QUALIFYING_HYPOTHESES:
        raise ValueError("DEC-458 total qualifying hypothesis count mismatch")
    if total_deduplicated != TOTAL_DEDUPLICATED_HYPOTHESES:
        raise ValueError("DEC-458 total deduplicated hypothesis count mismatch")

    return {
        "aggregate_verified": True,
        "aggregate_evidence_fingerprint": stored_fingerprint,
        "verified_cell_count": len(seen),
        "total_hypotheses": total_hypotheses,
        "total_evaluable_hypotheses": total_evaluable,
        "total_qualifying_hypotheses": total_qualifying,
        "total_deduplicated_hypotheses": total_deduplicated,
        "continuous_stability_shortlist_count": 0,
        "continuous_stability_frozen_count": 0,
    }


def review_cell_evidence(
    cell_evidence: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-458 requires exactly 18 cell evidence objects")

    seen: set[tuple[object, object, object]] = set()
    total_hypotheses = 0
    total_evaluable = 0
    total_qualifying = 0
    total_deduplicated = 0

    for value in cell_evidence:
        cell = value.get("cell")
        section = value.get("continuous_stability")
        if not isinstance(cell, Mapping) or not isinstance(section, Mapping):
            raise ValueError("DEC-458 cell evidence malformed")

        identity = (
            cell.get("symbol"),
            cell.get("timeframe"),
            cell.get("horizon_minutes"),
        )
        if identity not in EXPECTED_CELLS:
            raise ValueError("DEC-458 cell evidence identity mismatch")
        if identity in seen:
            raise ValueError("DEC-458 cell evidence identity duplicated")
        seen.add(identity)

        unsigned = dict(value)
        fingerprint = _validate_sha256(
            unsigned.pop("evidence_fingerprint", None),
            field="DEC-458 cell evidence fingerprint",
        )
        if hashlib.sha256(_canonical_json(unsigned)).hexdigest() != fingerprint:
            raise ValueError("DEC-458 cell evidence fingerprint mismatch")

        _require_exact(
            value,
            {
                "experiment_id": "EXP-20261001-064",
                "code_commit": RUN_HEAD_SHA,
                "protocol_fingerprint": PROTOCOL_FINGERPRINT,
                "feature_evidence_fingerprint": FEATURE_EVIDENCE_FINGERPRINT,
                "outcome_evidence_fingerprint": OUTCOME_EVIDENCE_FINGERPRINT,
                "evidence_label": EVIDENCE_LABEL,
                "untouched_oos": False,
                "reserved_robustness_opened": False,
                "source_access_authorized": False,
                "historical_execution_authorized": False,
                "historical_result_authorized": False,
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
            prefix="DEC-458 cell",
        )
        _require_exact(
            section,
            {
                "hypothesis_count": 80,
                "evaluable_hypothesis_count": 80,
                "qualifying_hypothesis_count": 0,
                "deduplicated_hypothesis_count": 0,
                "shortlist": [],
                "frozen_hypothesis_fingerprints": [],
                "output_kind": OUTPUT_KIND,
            },
            prefix="DEC-458 continuous stability",
        )

        total_hypotheses += 80
        total_evaluable += 80

    if seen != set(EXPECTED_CELLS):
        raise ValueError("DEC-458 cell evidence universe incomplete")
    if total_hypotheses != TOTAL_HYPOTHESES:
        raise ValueError("DEC-458 total hypothesis count mismatch")
    if total_evaluable != TOTAL_EVALUABLE_HYPOTHESES:
        raise ValueError("DEC-458 total evaluable hypothesis count mismatch")
    if total_qualifying != TOTAL_QUALIFYING_HYPOTHESES:
        raise ValueError("DEC-458 total qualifying hypothesis count mismatch")
    if total_deduplicated != TOTAL_DEDUPLICATED_HYPOTHESES:
        raise ValueError("DEC-458 total deduplicated hypothesis count mismatch")

    return {
        "cell_evidence_verified": True,
        "verified_cell_count": len(seen),
        "total_hypotheses": total_hypotheses,
        "total_evaluable_hypotheses": total_evaluable,
        "total_qualifying_hypotheses": total_qualifying,
        "total_deduplicated_hypotheses": total_deduplicated,
    }


def historical_result_review_payload() -> dict[str, object]:
    return {
        "decision": EXP064_HISTORICAL_RESULT_REVIEW_DECISION,
        "version": EXP064_HISTORICAL_RESULT_REVIEW_VERSION,
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
        "feature_evidence_fingerprint": FEATURE_EVIDENCE_FINGERPRINT,
        "outcome_evidence_fingerprint": OUTCOME_EVIDENCE_FINGERPRINT,
        "verified_cell_count": EXPECTED_CELL_COUNT,
        "total_hypotheses": TOTAL_HYPOTHESES,
        "total_evaluable_hypotheses": TOTAL_EVALUABLE_HYPOTHESES,
        "total_qualifying_hypotheses": TOTAL_QUALIFYING_HYPOTHESES,
        "total_deduplicated_hypotheses": TOTAL_DEDUPLICATED_HYPOTHESES,
        "continuous_stability_shortlist_count": (
            CONTINUOUS_STABILITY_SHORTLIST_COUNT
        ),
        "continuous_stability_frozen_count": (
            CONTINUOUS_STABILITY_FROZEN_COUNT
        ),
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
        "next_gate": "EXPLICIT_POST_EXP064_RESEARCH_DIRECTION_DECISION",
    }


__all__ = [
    "AGGREGATE_ARTIFACT_DIGEST",
    "AGGREGATE_ARTIFACT_ID",
    "AGGREGATE_ARTIFACT_NAME",
    "AGGREGATE_EVIDENCE_FINGERPRINT",
    "AGGREGATE_RAW_JSON_SHA256",
    "CLASSIFICATION",
    "CONTINUOUS_STABILITY_FROZEN_COUNT",
    "CONTINUOUS_STABILITY_SHORTLIST_COUNT",
    "EXP064_HISTORICAL_RESULT_REVIEW_DECISION",
    "EXP064_HISTORICAL_RESULT_REVIEW_VERSION",
    "RUN_HEAD_SHA",
    "RUN_ID",
    "STAGE",
    "TOTAL_EVALUABLE_HYPOTHESES",
    "TOTAL_HYPOTHESES",
    "TOTAL_QUALIFYING_HYPOTHESES",
    "historical_result_review_payload",
    "review_cell_evidence",
    "validate_aggregate_evidence",
    "validate_terminal_run",
]
