from __future__ import annotations

from typing import Mapping

from .model_successor_fit_temporal_residual_regime_balance_utility_repair_artifacts import (
    compile_fit_temporal_residual_regime_balance_utility_repair_model_result_evidence,
)


FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RESULT_REVIEW_DECISION = "DEC-257"
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_NAME = (
    "phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_PATH = (
    ".github/workflows/"
    "phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml"
)

DEC256_MERGED_COMMIT = "cef9f6d201bf2b025f08c924a11c84e9684b9ba0"
DEC256_WORKFLOW_BLOB_SHA = "20af1bf2f9057274a8c50d5b48becbf5f683ef86"
DEC256_CLI_BLOB_SHA = "90c6bc9e893c813d394e3a9c4adc5a155e938af0"
DEC256_EXECUTION_GATE_BLOB_SHA = (
    "82f51bf85ccb1793b3a980b2884f3e122a03c8db"
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
            "EXP-060 terminal review head SHA must be a 40-character commit"
        )
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(
            "EXP-060 terminal review head SHA must be hexadecimal"
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
        raise ValueError("EXP-060 terminal review jobs payload is malformed")
    if len(jobs) != 11:
        raise ValueError(
            "EXP-060 terminal review requires exactly 11 workflow jobs"
        )

    preflight: list[Mapping[str, object]] = []
    matrix: list[Mapping[str, object]] = []
    aggregate: list[Mapping[str, object]] = []
    seen_ids: set[int] = set()
    for raw in jobs:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-060 terminal review job row is malformed")
        job_id = raw.get("id")
        if (
            not isinstance(job_id, int)
            or isinstance(job_id, bool)
            or job_id in seen_ids
        ):
            raise ValueError(
                "EXP-060 terminal review job id is malformed or duplicated"
            )
        seen_ids.add(job_id)
        if raw.get("status") != "completed":
            raise ValueError("EXP-060 terminal review requires completed jobs")
        name = raw.get("name")
        if not isinstance(name, str):
            raise ValueError("EXP-060 terminal review job name is malformed")
        if name == "authorization-preflight":
            preflight.append(raw)
        elif name == "aggregate-model-evidence":
            aggregate.append(raw)
        elif name.startswith("model-cells ("):
            matrix.append(raw)
        else:
            raise ValueError(
                f"unexpected EXP-060 terminal review job name: {name!r}"
            )

    if len(preflight) != 1:
        raise ValueError(
            "EXP-060 terminal review requires one authorization-preflight job"
        )
    if len(matrix) != 9:
        raise ValueError(
            "EXP-060 terminal review requires nine matrix jobs"
        )
    if len(aggregate) != 1:
        raise ValueError(
            "EXP-060 terminal review requires one aggregate job"
        )
    return preflight[0], matrix, aggregate[0]


def _expected_artifact_names(head_sha: str) -> tuple[set[str], str]:
    cells = {
        (
            "exp060-fit-temporal-residual-regime-balance-utility-model-cell-results-"
            f"{symbol}-{timeframe}-{head_sha}"
        )
        for symbol, timeframe in EXPECTED_DATASETS
    }
    aggregate = (
        "exp060-fit-temporal-residual-regime-balance-utility-model-result-evidence-"
        f"{head_sha}-from-feature-35867307338-outcome-35876715434"
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
            "EXP-060 terminal review artifact listing is malformed"
        )
    expected_cells, expected_aggregate = _expected_artifact_names(head_sha)
    seen: set[str] = set()
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-060 terminal review artifact row is malformed")
        name = raw.get("name")
        if not isinstance(name, str) or name in seen:
            raise ValueError(
                "EXP-060 terminal review artifact name is malformed or duplicated"
            )
        if raw.get("expired") is not False:
            raise ValueError(
                "EXP-060 terminal review requires non-expired artifacts"
            )
        if name not in expected_cells and name != expected_aggregate:
            raise ValueError(
                f"unexpected EXP-060 terminal review artifact: {name!r}"
            )
        seen.add(name)
    total_count = artifacts_payload.get("total_count")
    if total_count is not None and total_count != len(artifacts):
        raise ValueError("EXP-060 terminal review artifact count mismatch")
    return seen & expected_cells, expected_aggregate in seen


def _revalidate_aggregate_evidence(
    evidence: Mapping[str, object],
    *,
    head_sha: str,
) -> dict[str, object]:
    cells = evidence.get("cells")
    if not isinstance(cells, list):
        raise ValueError(
            "successful EXP-060 run requires aggregate evidence cells"
        )
    recompiled = (
        compile_fit_temporal_residual_regime_balance_utility_repair_model_result_evidence(
            cells,
            code_commit=head_sha,
        )
    )
    if dict(evidence) != recompiled:
        raise ValueError(
            "EXP-060 aggregate evidence does not match deterministic recompilation"
        )
    return {
        "fit_temporal_residual_regime_balance_utility_repair_model_result_evidence_verified": True,
        "verified_cell_count": int(recompiled["cell_count"]),
        "verified_regressor_count": int(recompiled["verified_regressor_count"]),
        "verified_pooled_calibration_reference_count": int(
            recompiled["verified_pooled_calibration_reference_count"]
        ),
        "verified_fit_temporal_support_reference_count": int(
            recompiled["verified_fit_temporal_support_reference_count"]
        ),
        "verified_fit_temporal_feature_support_reference_count": int(
            recompiled["verified_fit_temporal_feature_support_reference_count"]
        ),
        "verified_fit_temporal_residual_reference_count": int(
            recompiled["verified_fit_temporal_residual_reference_count"]
        ),
        "verified_fit_temporal_residual_breadth_bound_count_per_row": int(
            recompiled[
                "verified_fit_temporal_residual_breadth_bound_count_per_row"
            ]
        ),
        "verified_fit_temporal_residual_lower_tail_bound_count_per_row": int(
            recompiled[
                "verified_fit_temporal_residual_lower_tail_bound_count_per_row"
            ]
        ),
        "verified_fit_temporal_residual_lower_tail_count": int(
            recompiled["verified_fit_temporal_residual_lower_tail_count"]
        ),
        "verified_fit_temporal_residual_regime_count": int(
            recompiled["verified_fit_temporal_residual_regime_count"]
        ),
        "verified_fit_temporal_residual_windows_per_regime": int(
            recompiled["verified_fit_temporal_residual_windows_per_regime"]
        ),
        "verified_fit_temporal_residual_regime_floor_bound_count_per_row": int(
            recompiled[
                "verified_fit_temporal_residual_regime_floor_bound_count_per_row"
            ]
        ),
        "verified_fit_temporal_residual_regime_balance_regime_count": int(
            recompiled[
                "verified_fit_temporal_residual_regime_balance_regime_count"
            ]
        ),
        "verified_fit_temporal_residual_regime_balance_source_bound_count_per_row": int(
            recompiled[
                "verified_fit_temporal_residual_regime_balance_source_bound_count_per_row"
            ]
        ),
        "verified_fit_temporal_residual_regime_balance_penalty_multiplier": float(
            recompiled[
                "verified_fit_temporal_residual_regime_balance_penalty_multiplier"
            ]
        ),
        "evidence_fingerprint": str(recompiled["evidence_fingerprint"]),
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def validate_fit_temporal_residual_regime_balance_utility_repair_model_terminal_review(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    aggregate_evidence: Mapping[str, object] | None = None,
) -> dict[str, object]:
    run_id = run.get("id")
    if not isinstance(run_id, int) or isinstance(run_id, bool):
        raise ValueError("EXP-060 terminal review run id is malformed")
    if run.get("name") != FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_NAME:
        raise ValueError("EXP-060 terminal review workflow name mismatch")
    if run.get("path") != FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_PATH:
        raise ValueError("EXP-060 terminal review workflow path mismatch")
    if run.get("event") != "workflow_dispatch":
        raise ValueError("EXP-060 terminal review event mismatch")
    if run.get("head_branch") != "main":
        raise ValueError("EXP-060 terminal review branch mismatch")
    if run.get("run_attempt") != 1:
        raise ValueError("EXP-060 terminal review forbids rerun attempts")
    if run.get("status") != "completed":
        raise ValueError("EXP-060 terminal review run is not completed")

    head_sha = _validate_head_sha(run.get("head_sha"))
    conclusion = run.get("conclusion")
    if conclusion not in {"success", *TERMINAL_NON_SUCCESS_CONCLUSIONS}:
        raise ValueError(
            f"unexpected EXP-060 terminal run conclusion: {conclusion!r}"
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
        "fit_temporal_residual_regime_balance_utility_repair_model_terminal_reviewed": True,
        "fit_temporal_residual_regime_balance_utility_repair_model_result_review_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RESULT_REVIEW_DECISION
        ),
        "dec245_merged_commit": DEC256_MERGED_COMMIT,
        "dec245_workflow_blob_sha": DEC256_WORKFLOW_BLOB_SHA,
        "dec245_cli_blob_sha": DEC256_CLI_BLOB_SHA,
        "dec245_execution_gate_blob_sha": DEC256_EXECUTION_GATE_BLOB_SHA,
        "reviewed_model_run_id": run_id,
        "reviewed_model_head_sha": head_sha,
        "reviewed_model_run_attempt": 1,
        "reviewed_model_run_conclusion": conclusion,
        "persisted_cell_artifact_count": len(persisted_cells),
        "aggregate_artifact_present": aggregate_present,
        "prior_result_informed": True,
        "untouched_oos": False,
        "replacement_model_run_authorized": REPLACEMENT_MODEL_RUN_AUTHORIZED,
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
                "successful EXP-060 run requires successful preflight"
            )
        if any(value != "success" for value in matrix_conclusions):
            raise ValueError(
                "successful EXP-060 run requires all matrix jobs to succeed"
            )
        if aggregate_conclusion != "success":
            raise ValueError(
                "successful EXP-060 run requires aggregate job success"
            )
        if len(persisted_cells) != 9 or not aggregate_present:
            raise ValueError(
                "successful EXP-060 run requires all ten expected artifacts"
            )
        if aggregate_evidence is None:
            raise ValueError(
                "successful EXP-060 run requires aggregate evidence"
            )
        summary = _revalidate_aggregate_evidence(
            aggregate_evidence,
            head_sha=head_sha,
        )
        return {
            **review,
            **summary,
            "stage": (
                "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_"
                "RESULT_REVIEW_REQUIRED"
            ),
            "replacement_model_run_authorized": False,
            "promotion_authorized": False,
            "shadow_authorized": False,
            "trading_authorized": False,
        }

    if aggregate_evidence is not None:
        raise ValueError(
            "non-success EXP-060 run cannot claim aggregate result evidence"
        )
    if aggregate_present:
        raise ValueError(
            "non-success EXP-060 run cannot claim aggregate artifact"
        )
    if aggregate_conclusion not in {"skipped", "failure", "cancelled"}:
        raise ValueError(
            "non-success EXP-060 aggregate job conclusion mismatch"
        )
    return {
        **review,
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_"
            "RUN_FAILURE_REVIEW_REQUIRED"
        ),
        "authorization_preflight_conclusion": preflight_conclusion,
        "successful_matrix_job_count": sum(
            value == "success" for value in matrix_conclusions
        ),
        "failed_matrix_job_count": sum(
            value == "failure" for value in matrix_conclusions
        ),
        "cancelled_matrix_job_count": sum(
            value == "cancelled" for value in matrix_conclusions
        ),
        "skipped_matrix_job_count": sum(
            value == "skipped" for value in matrix_conclusions
        ),
    }


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "DEC256_CLI_BLOB_SHA",
    "DEC256_EXECUTION_GATE_BLOB_SHA",
    "DEC256_MERGED_COMMIT",
    "DEC256_WORKFLOW_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "EXPECTED_DATASETS",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RESULT_REVIEW_DECISION",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_NAME",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_WORKFLOW_PATH",
    "LIVE_ORDER_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REPLACEMENT_MODEL_RUN_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TERMINAL_NON_SUCCESS_CONCLUSIONS",
    "TRADING_AUTHORIZED",
    "validate_fit_temporal_residual_regime_balance_utility_repair_model_terminal_review",
]
