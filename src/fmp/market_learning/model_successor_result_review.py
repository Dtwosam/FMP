from __future__ import annotations

from typing import Mapping

from .model_successor_artifacts import (
    validate_successor_model_result_evidence,
)


SUCCESSOR_MODEL_RESULT_REVIEW_DECISION = "DEC-100"
SUCCESSOR_MODEL_WORKFLOW_NAME = "phase8a-exp045-model-training"
SUCCESSOR_MODEL_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp045-model-training.yml"
)

EXPECTED_DATASETS = (
    ("EURUSD", "5m"),
    ("EURUSD", "15m"),
    ("EURUSD", "1h"),
    ("GBPUSD", "5m"),
    ("GBPUSD", "15m"),
    ("GBPUSD", "1h"),
    ("USDJPY", "5m"),
    ("USDJPY", "15m"),
    ("USDJPY", "1h"),
)

TERMINAL_NON_SUCCESS_CONCLUSIONS = {
    "failure",
    "cancelled",
    "timed_out",
}

PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False
REPLACEMENT_MODEL_RUN_AUTHORIZED = False


def _validate_head_sha(value: object) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(
            "EXP-045 terminal review head SHA must be a 40-character commit"
        )
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(
            "EXP-045 terminal review head SHA must be hexadecimal"
        ) from exc
    return value.lower()


def _index_jobs(
    jobs_payload: Mapping[str, object],
) -> tuple[
    Mapping[str, object],
    list[Mapping[str, object]],
    Mapping[str, object],
]:
    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError(
            "EXP-045 terminal review jobs payload is malformed"
        )
    if len(jobs) != 11:
        raise ValueError(
            "EXP-045 terminal review requires exactly 11 workflow jobs"
        )

    preflight: list[Mapping[str, object]] = []
    matrix: list[Mapping[str, object]] = []
    aggregate: list[Mapping[str, object]] = []
    seen_ids: set[int] = set()

    for raw in jobs:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-045 terminal review job row is malformed"
            )
        job_id = raw.get("id")
        if (
            not isinstance(job_id, int)
            or isinstance(job_id, bool)
            or job_id in seen_ids
        ):
            raise ValueError(
                "EXP-045 terminal review job id is malformed or duplicated"
            )
        seen_ids.add(job_id)

        if raw.get("status") != "completed":
            raise ValueError(
                "EXP-045 terminal review requires completed jobs"
            )
        name = raw.get("name")
        if not isinstance(name, str):
            raise ValueError(
                "EXP-045 terminal review job name is malformed"
            )

        if name == "authorization-preflight":
            preflight.append(raw)
        elif name == "aggregate-model-evidence":
            aggregate.append(raw)
        elif name.startswith("model-cells ("):
            matrix.append(raw)
        else:
            raise ValueError(
                f"unexpected EXP-045 terminal review job name: {name!r}"
            )

    if len(preflight) != 1:
        raise ValueError(
            "EXP-045 terminal review requires one authorization-preflight job"
        )
    if len(matrix) != 9:
        raise ValueError(
            "EXP-045 terminal review requires nine matrix jobs"
        )
    if len(aggregate) != 1:
        raise ValueError(
            "EXP-045 terminal review requires one aggregate job"
        )

    return preflight[0], matrix, aggregate[0]


def _expected_artifact_names(head_sha: str) -> tuple[set[str], str]:
    cells = {
        f"exp045-model-cell-results-{symbol}-{timeframe}-{head_sha}"
        for symbol, timeframe in EXPECTED_DATASETS
    }
    aggregate = (
        f"exp045-model-result-evidence-{head_sha}-"
        "from-feature-35867307338-outcome-35876715434"
    )
    return cells, aggregate


def _validate_artifacts(
    artifacts_payload: Mapping[str, object],
    *,
    head_sha: str,
) -> tuple[set[str], bool]:
    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError(
            "EXP-045 terminal review artifact listing is malformed"
        )

    expected_cells, expected_aggregate = _expected_artifact_names(
        head_sha
    )
    seen: set[str] = set()

    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-045 terminal review artifact row is malformed"
            )
        name = raw.get("name")
        if not isinstance(name, str) or name in seen:
            raise ValueError(
                "EXP-045 terminal review artifact name is malformed or duplicated"
            )
        if raw.get("expired") is not False:
            raise ValueError(
                "EXP-045 terminal review requires non-expired artifacts"
            )
        if name not in expected_cells and name != expected_aggregate:
            raise ValueError(
                f"unexpected EXP-045 terminal review artifact: {name!r}"
            )
        seen.add(name)

    total_count = artifacts_payload.get("total_count")
    if total_count is not None and total_count != len(artifacts):
        raise ValueError(
            "EXP-045 terminal review artifact count mismatch"
        )

    return seen & expected_cells, expected_aggregate in seen


def validate_successor_model_terminal_review(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    aggregate_evidence: Mapping[str, object] | None = None,
) -> dict[str, object]:
    run_id = run.get("id")
    if not isinstance(run_id, int) or isinstance(run_id, bool):
        raise ValueError(
            "EXP-045 terminal review run id is malformed"
        )
    if run.get("name") != SUCCESSOR_MODEL_WORKFLOW_NAME:
        raise ValueError(
            "EXP-045 terminal review workflow name mismatch"
        )
    if run.get("path") != SUCCESSOR_MODEL_WORKFLOW_PATH:
        raise ValueError(
            "EXP-045 terminal review workflow path mismatch"
        )
    if run.get("event") != "workflow_dispatch":
        raise ValueError(
            "EXP-045 terminal review event mismatch"
        )
    if run.get("head_branch") != "main":
        raise ValueError(
            "EXP-045 terminal review branch mismatch"
        )
    if run.get("run_attempt") != 1:
        raise ValueError(
            "EXP-045 terminal review forbids rerun attempts"
        )
    if run.get("status") != "completed":
        raise ValueError(
            "EXP-045 terminal review run is not completed"
        )

    head_sha = _validate_head_sha(run.get("head_sha"))
    conclusion = run.get("conclusion")
    if conclusion not in {
        "success",
        *TERMINAL_NON_SUCCESS_CONCLUSIONS,
    }:
        raise ValueError(
            f"unexpected EXP-045 terminal run conclusion: {conclusion!r}"
        )

    preflight, matrix, aggregate = _index_jobs(jobs_payload)
    persisted_cells, aggregate_present = _validate_artifacts(
        artifacts_payload,
        head_sha=head_sha,
    )

    preflight_conclusion = preflight.get("conclusion")
    matrix_conclusions = [job.get("conclusion") for job in matrix]
    aggregate_conclusion = aggregate.get("conclusion")

    review: dict[str, object] = {
        "successor_model_terminal_reviewed": True,
        "successor_model_result_review_decision": (
            SUCCESSOR_MODEL_RESULT_REVIEW_DECISION
        ),
        "reviewed_model_run_id": run_id,
        "reviewed_model_head_sha": head_sha,
        "reviewed_model_run_attempt": 1,
        "reviewed_model_run_conclusion": conclusion,
        "persisted_cell_artifact_count": len(persisted_cells),
        "aggregate_artifact_present": aggregate_present,
        "prior_result_informed": True,
        "untouched_oos": False,
        "replacement_model_run_authorized": (
            REPLACEMENT_MODEL_RUN_AUTHORIZED
        ),
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "shadow_authorized": SHADOW_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }

    if conclusion == "success":
        if preflight_conclusion != "success":
            raise ValueError(
                "successful EXP-045 run requires successful preflight"
            )
        if any(value != "success" for value in matrix_conclusions):
            raise ValueError(
                "successful EXP-045 run requires all matrix jobs to succeed"
            )
        if aggregate_conclusion != "success":
            raise ValueError(
                "successful EXP-045 run requires aggregate job success"
            )
        if len(persisted_cells) != 9 or not aggregate_present:
            raise ValueError(
                "successful EXP-045 run requires all ten expected artifacts"
            )
        if aggregate_evidence is None:
            raise ValueError(
                "successful EXP-045 run requires aggregate evidence"
            )

        summary = validate_successor_model_result_evidence(
            aggregate_evidence,
            expected_code_commit=head_sha,
        )
        return {
            **review,
            **summary,
            "stage": "SUCCESSOR_MODEL_RESULT_REVIEW_REQUIRED",
            "replacement_model_run_authorized": False,
            "promotion_authorized": False,
            "shadow_authorized": False,
            "trading_authorized": False,
        }

    if aggregate_evidence is not None:
        raise ValueError(
            "non-success EXP-045 run cannot claim aggregate result evidence"
        )
    if aggregate_present:
        raise ValueError(
            "non-success EXP-045 run cannot claim aggregate artifact"
        )
    if aggregate_conclusion not in {
        "skipped",
        "failure",
        "cancelled",
    }:
        raise ValueError(
            "non-success EXP-045 aggregate job conclusion mismatch"
        )

    return {
        **review,
        "stage": "SUCCESSOR_MODEL_RUN_FAILURE_REVIEW_REQUIRED",
        "authorization_preflight_conclusion": preflight_conclusion,
        "successful_matrix_job_count": sum(
            value == "success"
            for value in matrix_conclusions
        ),
        "failed_matrix_job_count": sum(
            value == "failure"
            for value in matrix_conclusions
        ),
        "cancelled_matrix_job_count": sum(
            value == "cancelled"
            for value in matrix_conclusions
        ),
        "skipped_matrix_job_count": sum(
            value == "skipped"
            for value in matrix_conclusions
        ),
    }


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "DEMO_ORDER_AUTHORIZED",
    "EXPECTED_DATASETS",
    "LIVE_ORDER_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REPLACEMENT_MODEL_RUN_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "SUCCESSOR_MODEL_RESULT_REVIEW_DECISION",
    "SUCCESSOR_MODEL_WORKFLOW_NAME",
    "SUCCESSOR_MODEL_WORKFLOW_PATH",
    "TERMINAL_NON_SUCCESS_CONCLUSIONS",
    "TRADING_AUTHORIZED",
    "validate_successor_model_terminal_review",
]
