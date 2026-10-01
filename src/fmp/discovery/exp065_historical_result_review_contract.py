from __future__ import annotations

from typing import Mapping, Sequence

from .exp065_evidence_contract import (
    EXPECTED_CELLS,
    EXPECTED_CELL_COUNT,
    validate_aggregate_evidence as validate_dec463_aggregate_evidence,
    validate_cell_evidence as validate_dec463_cell_evidence,
)
from .exp065_pairwise_interaction_protocol import (
    HYPOTHESES_PER_CELL_HORIZON,
    MAX_FROZEN_GLOBAL,
    MAX_SHORTLIST_GLOBAL,
    OUTPUT_KIND,
)


EXP065_HISTORICAL_RESULT_REVIEW_CONTRACT_DECISION = "DEC-467"
EXP065_HISTORICAL_RESULT_REVIEW_CONTRACT_VERSION = (
    "fmp-exp065-historical-result-review-contract-v1"
)

DEC466_MERGE_SHA = "5faa733572576aa5a1c56176ac27c415eaaf6416"
DEC466_EXECUTION_AUTHORIZATION_BLOB_SHA = (
    "ccc99179a51145534e1b48b8520b2f743580c217"
)
DEC466_DISPATCH_OPERATOR_BLOB_SHA = (
    "6a386c556e121d959ec1ea8bbb56dbb49b42dde2"
)
DEC463_EVIDENCE_CONTRACT_BLOB_SHA = (
    "ca68622ddfc9866f00569d558b2ab927be23686d"
)

RUN_ID = 36905224184
RUN_NAME = "phase8a-exp065-pairwise-interaction"
RUN_PATH = ".github/workflows/phase8a-exp065-pairwise-interaction.yml"
RUN_EVENT = "workflow_dispatch"
RUN_BRANCH = "main"
RUN_HEAD_SHA = DEC466_MERGE_SHA
RUN_NUMBER = 1
RUN_ATTEMPT = 1

EXPECTED_JOB_COUNT = 20
EXPECTED_ARTIFACT_COUNT = 20
EXPECTED_CELL_COUNT = 18
TOTAL_NOMINAL_HYPOTHESES = EXPECTED_CELL_COUNT * HYPOTHESES_PER_CELL_HORIZON

EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"

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

EXPECTED_JOB_NAMES = {
    "exp065-preflight",
    "exp065-aggregate",
    *{
        f"exp065-cell-{symbol}-{timeframe}-{horizon}m"
        for symbol, timeframe, horizon in EXPECTED_CELLS
    },
}

EXPECTED_ARTIFACT_NAMES = {
    f"phase8a-exp065-preflight-{RUN_HEAD_SHA}",
    f"phase8a-exp065-aggregate-{RUN_HEAD_SHA}",
    *{
        f"phase8a-exp065-cell-{symbol}-{timeframe}-{horizon}m-{RUN_HEAD_SHA}"
        for symbol, timeframe, horizon in EXPECTED_CELLS
    },
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


def _rows(
    payload: Mapping[str, object],
    *,
    field: str,
) -> list[Mapping[str, object]]:
    raw = payload.get(field)
    if not isinstance(raw, list):
        raise ValueError(f"DEC-467 payload must contain {field}")
    result: list[Mapping[str, object]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError(f"DEC-467 {field} row malformed")
        result.append(item)
    return result


def _nonnegative_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _positive_int(value: object, *, field: str) -> int:
    result = _nonnegative_int(value, field=field)
    if result <= 0:
        raise ValueError(f"{field} must be positive")
    return result


def _validate_digest(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"{field} must be a sha256 artifact digest")
    raw = value.removeprefix("sha256:")
    if len(raw) != 64:
        raise ValueError(f"{field} must contain a 64-character sha256")
    try:
        int(raw, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def validate_terminal_run_identity(
    run: Mapping[str, object],
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
            "status": "completed",
        },
        prefix="DEC-467 run",
    )
    conclusion = run.get("conclusion")
    if not isinstance(conclusion, str) or not conclusion:
        raise ValueError("DEC-467 terminal run requires a conclusion")
    return {
        "run_identity_verified": True,
        "run_id": RUN_ID,
        "run_head_sha": RUN_HEAD_SHA,
        "run_number": RUN_NUMBER,
        "run_attempt": RUN_ATTEMPT,
        "run_status": "completed",
        "run_conclusion": conclusion,
    }


def validate_success_run_shape(
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
) -> dict[str, object]:
    identity = validate_terminal_run_identity(run)
    if identity["run_conclusion"] != "success":
        raise ValueError("DEC-467 success-shape review requires run success")

    jobs = _rows(jobs_payload, field="jobs")
    if len(jobs) != EXPECTED_JOB_COUNT:
        raise ValueError("DEC-467 successful run requires exactly 20 jobs")
    names = [item.get("name") for item in jobs]
    if len(names) != len(set(names)):
        raise ValueError("DEC-467 job names duplicated")
    if set(names) != EXPECTED_JOB_NAMES:
        raise ValueError("DEC-467 job inventory mismatch")
    for item in jobs:
        if item.get("status") != "completed" or item.get("conclusion") != "success":
            raise ValueError(
                "DEC-467 successful run requires every job to succeed"
            )

    artifacts = _rows(artifacts_payload, field="artifacts")
    if len(artifacts) != EXPECTED_ARTIFACT_COUNT:
        raise ValueError("DEC-467 successful run requires exactly 20 artifacts")
    artifact_names = [item.get("name") for item in artifacts]
    if len(artifact_names) != len(set(artifact_names)):
        raise ValueError("DEC-467 artifact names duplicated")
    if set(artifact_names) != EXPECTED_ARTIFACT_NAMES:
        raise ValueError("DEC-467 artifact inventory mismatch")

    aggregate: Mapping[str, object] | None = None
    for item in artifacts:
        _positive_int(item.get("id"), field="DEC-467 artifact id")
        _validate_digest(item.get("digest"), field="DEC-467 artifact digest")
        if item.get("expired") is not False:
            raise ValueError("DEC-467 requires every artifact non-expired")
        if item.get("name") == f"phase8a-exp065-aggregate-{RUN_HEAD_SHA}":
            aggregate = item

    if aggregate is None:
        raise ValueError("DEC-467 aggregate artifact missing")

    return {
        **identity,
        "job_count": len(jobs),
        "artifact_count": len(artifacts),
        "aggregate_artifact_id": aggregate.get("id"),
        "aggregate_artifact_name": aggregate.get("name"),
        "aggregate_artifact_digest": aggregate.get("digest"),
        "success_shape_verified": True,
    }


def _cell_identity(value: Mapping[str, object]) -> tuple[object, object, object]:
    cell = value.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError("DEC-467 cell evidence missing cell identity")
    return (
        cell.get("symbol"),
        cell.get("timeframe"),
        cell.get("horizon_minutes"),
    )


def review_success_evidence(
    *,
    aggregate: Mapping[str, object],
    cell_evidence: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validated_aggregate = validate_dec463_aggregate_evidence(aggregate)
    if validated_aggregate.get("code_commit") != RUN_HEAD_SHA:
        raise ValueError("DEC-467 aggregate code commit mismatch")
    if validated_aggregate.get("evidence_label") != EVIDENCE_LABEL:
        raise ValueError("DEC-467 aggregate evidence label mismatch")
    if validated_aggregate.get("untouched_oos") is not False:
        raise ValueError("DEC-467 aggregate cannot claim untouched OOS")
    if validated_aggregate.get("reserved_robustness_opened") is not False:
        raise ValueError("DEC-467 aggregate opened reserved robustness")
    if validated_aggregate.get("output_kind") != OUTPUT_KIND:
        raise ValueError("DEC-467 aggregate output kind mismatch")

    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-467 requires exactly 18 cell evidence objects")

    cells_by_identity: dict[
        tuple[object, object, object],
        Mapping[str, object],
    ] = {}
    total_evaluable = 0
    total_qualifying = 0
    total_deduplicated = 0
    total_shortlist = 0
    total_frozen = 0

    for raw in cell_evidence:
        value = validate_dec463_cell_evidence(raw)
        if value.get("code_commit") != RUN_HEAD_SHA:
            raise ValueError("DEC-467 cell code commit mismatch")
        identity = _cell_identity(value)
        if identity not in EXPECTED_CELLS:
            raise ValueError("DEC-467 cell identity mismatch")
        if identity in cells_by_identity:
            raise ValueError("DEC-467 cell identity duplicated")
        cells_by_identity[identity] = value

        section = value.get("pairwise_interaction")
        if not isinstance(section, Mapping):
            raise ValueError("DEC-467 pairwise-interaction section missing")
        if section.get("hypothesis_count") != HYPOTHESES_PER_CELL_HORIZON:
            raise ValueError("DEC-467 nominal hypothesis count mismatch")
        evaluable = _nonnegative_int(
            section.get("evaluable_hypothesis_count"),
            field="DEC-467 evaluable hypothesis count",
        )
        qualifying = _nonnegative_int(
            section.get("qualifying_hypothesis_count"),
            field="DEC-467 qualifying hypothesis count",
        )
        deduplicated = _nonnegative_int(
            section.get("deduplicated_hypothesis_count"),
            field="DEC-467 deduplicated hypothesis count",
        )
        shortlist = section.get("shortlist")
        frozen = section.get("frozen_hypothesis_fingerprints")
        if not isinstance(shortlist, list) or not isinstance(frozen, list):
            raise ValueError("DEC-467 shortlist/frozen inventory malformed")
        total_evaluable += evaluable
        total_qualifying += qualifying
        total_deduplicated += deduplicated
        total_shortlist += len(shortlist)
        total_frozen += len(frozen)

    if set(cells_by_identity) != set(EXPECTED_CELLS):
        raise ValueError("DEC-467 cell evidence universe incomplete")

    summaries = validated_aggregate.get("cells")
    if not isinstance(summaries, list) or len(summaries) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-467 aggregate cell inventory mismatch")
    seen_summary: set[tuple[object, object, object]] = set()
    for row in summaries:
        if not isinstance(row, Mapping):
            raise ValueError("DEC-467 aggregate cell summary malformed")
        identity = (
            row.get("symbol"),
            row.get("timeframe"),
            row.get("horizon_minutes"),
        )
        if identity in seen_summary:
            raise ValueError("DEC-467 aggregate cell summary duplicated")
        seen_summary.add(identity)
        cell = cells_by_identity.get(identity)
        if cell is None:
            raise ValueError("DEC-467 aggregate/cell identity mismatch")
        section = cell.get("pairwise_interaction")
        assert isinstance(section, Mapping)
        shortlist = section.get("shortlist")
        frozen = section.get("frozen_hypothesis_fingerprints")
        assert isinstance(shortlist, list)
        assert isinstance(frozen, list)

        expected_shortlist_fingerprints = [
            item.get("fingerprint")
            for item in shortlist
            if isinstance(item, Mapping)
        ]
        _require_exact(
            row,
            {
                "cell_evidence_fingerprint": cell.get("evidence_fingerprint"),
                "hypothesis_count": section.get("hypothesis_count"),
                "evaluable_hypothesis_count": section.get(
                    "evaluable_hypothesis_count"
                ),
                "qualifying_hypothesis_count": section.get(
                    "qualifying_hypothesis_count"
                ),
                "deduplicated_hypothesis_count": section.get(
                    "deduplicated_hypothesis_count"
                ),
                "pairwise_interaction_shortlist_count": len(shortlist),
                "pairwise_interaction_frozen_count": len(frozen),
                "pairwise_interaction_shortlist_fingerprints": (
                    expected_shortlist_fingerprints
                ),
                "pairwise_interaction_frozen_fingerprints": list(frozen),
                "output_kind": OUTPUT_KIND,
            },
            prefix="DEC-467 aggregate/cell",
        )

    if seen_summary != set(EXPECTED_CELLS):
        raise ValueError("DEC-467 aggregate cell universe incomplete")

    if total_shortlist > MAX_SHORTLIST_GLOBAL:
        raise ValueError("DEC-467 global shortlist cap exceeded")
    if total_frozen > MAX_FROZEN_GLOBAL:
        raise ValueError("DEC-467 global frozen cap exceeded")
    if validated_aggregate.get("pairwise_interaction_shortlist_count") != total_shortlist:
        raise ValueError("DEC-467 aggregate shortlist total mismatch")
    if validated_aggregate.get("pairwise_interaction_frozen_count") != total_frozen:
        raise ValueError("DEC-467 aggregate frozen total mismatch")

    if total_qualifying == 0:
        result_state = "ZERO_PAIRWISE_INTERACTION_QUALIFIERS"
    elif total_frozen == 0:
        result_state = "PAIRWISE_INTERACTION_QUALIFIERS_WITHOUT_FROZEN_CARRY_FORWARD"
    else:
        result_state = "PAIRWISE_INTERACTION_FROZEN_CARRY_FORWARD_PRESENT"

    return {
        "evidence_verified": True,
        "result_state": result_state,
        "aggregate_evidence_fingerprint": validated_aggregate.get(
            "evidence_fingerprint"
        ),
        "protocol_fingerprint": validated_aggregate.get("protocol_fingerprint"),
        "feature_evidence_fingerprint": validated_aggregate.get(
            "feature_evidence_fingerprint"
        ),
        "outcome_evidence_fingerprint": validated_aggregate.get(
            "outcome_evidence_fingerprint"
        ),
        "verified_cell_count": EXPECTED_CELL_COUNT,
        "total_hypotheses": TOTAL_NOMINAL_HYPOTHESES,
        "total_evaluable_hypotheses": total_evaluable,
        "total_qualifying_hypotheses": total_qualifying,
        "total_deduplicated_hypotheses": total_deduplicated,
        "pairwise_interaction_shortlist_count": total_shortlist,
        "pairwise_interaction_frozen_count": total_frozen,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "reserved_robustness_opened": False,
    }


def review_authority_boundary() -> dict[str, object]:
    return {
        "decision": EXP065_HISTORICAL_RESULT_REVIEW_CONTRACT_DECISION,
        "version": EXP065_HISTORICAL_RESULT_REVIEW_CONTRACT_VERSION,
        "stage": "EXP065_HISTORICAL_RESULT_REVIEW_CONTRACT_PREDECLARED",
        "run_id": RUN_ID,
        "run_head_sha": RUN_HEAD_SHA,
        "run_number": RUN_NUMBER,
        "run_attempt": RUN_ATTEMPT,
        "expected_job_count_on_success": EXPECTED_JOB_COUNT,
        "expected_artifact_count_on_success": EXPECTED_ARTIFACT_COUNT,
        "expected_cell_count": EXPECTED_CELL_COUNT,
        "total_nominal_hypotheses": TOTAL_NOMINAL_HYPOTHESES,
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
        "next_gate": "FREEZE_EXP065_HISTORICAL_RESULT_AFTER_TERMINAL_RUN",
    }


__all__ = [
    "DEC466_MERGE_SHA",
    "EXPECTED_ARTIFACT_COUNT",
    "EXPECTED_JOB_COUNT",
    "EXP065_HISTORICAL_RESULT_REVIEW_CONTRACT_DECISION",
    "EXP065_HISTORICAL_RESULT_REVIEW_CONTRACT_VERSION",
    "RUN_HEAD_SHA",
    "RUN_ID",
    "RUN_NUMBER",
    "RUN_ATTEMPT",
    "TOTAL_NOMINAL_HYPOTHESES",
    "review_authority_boundary",
    "review_success_evidence",
    "validate_success_run_shape",
    "validate_terminal_run_identity",
]
