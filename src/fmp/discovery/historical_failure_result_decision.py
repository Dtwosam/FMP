from __future__ import annotations

from typing import Mapping

from .historical_result_review_contract import (
    EXP061_HISTORICAL_TERMINAL_REVIEW_DECISION,
    classify_historical_terminal_result,
)


EXP061_HISTORICAL_FAILURE_FREEZE_DECISION = "DEC-292"
EXP061_HISTORICAL_FAILURE_FREEZE_VERSION = (
    "fmp-exp061-historical-failure-freeze-v1"
)

EXP061_HISTORICAL_RUN_ID = 36335879839
EXP061_HISTORICAL_RUN_HEAD_SHA = "a7b3bc2d0b196da2631b64c19331efb3af12c98e"
EXP061_HISTORICAL_RUN_NUMBER = 2
EXP061_HISTORICAL_RUN_ATTEMPT = 1

EXP061_EXECUTOR_RUN_ID = 36335739823
EXP061_EXECUTOR_ARTIFACT_ID = 10936194549
EXP061_EXECUTOR_ARTIFACT_NAME = (
    "exp061-dec289-historical-dispatch-evidence-"
    "a7b3bc2d0b196da2631b64c19331efb3af12c98e"
)
EXP061_EXECUTOR_ARTIFACT_DIGEST = (
    "sha256:e7ffe1f08ce358eca210ef41397165196cb64bee31696a180c7fd02af8c68f1c"
)
EXP061_EXECUTOR_JSON_SHA256 = (
    "1e35f83f7b7e584c3ff13b4c6ba46d2c358bae323b06e564f069f03d4aba313c"
)
EXP061_EXECUTOR_HISTORICAL_RUN_JSON_SHA256 = (
    "3fe6a0cd0563e514d868bce9ab6076844049046f86ab87f2a8928a39e697d641"
)
EXP061_EXECUTOR_HISTORICAL_RUNS_JSON_SHA256 = (
    "e0515a6175e343e778e2a5da307889d89f808dc3978a4789716604ba001dec6f"
)

EXP061_PREFLIGHT_ARTIFACT_ID = 10937316246
EXP061_PREFLIGHT_ARTIFACT_NAME = (
    "phase8a-exp061-preflight-"
    "a7b3bc2d0b196da2631b64c19331efb3af12c98e"
)
EXP061_PREFLIGHT_ARTIFACT_DIGEST = (
    "sha256:e9a898df51317250944ad0a111d01d96d2081d708ea80872ed11b5cee48d356f"
)
EXP061_PREFLIGHT_JSON_SHA256 = (
    "d8a85a2482f1bf72128a8f019b73c59fccad612ad02722821cca1a09c7bc582d"
)

FAILURE_CLASS = "NONFINITE_FEATURE_WARMUP_NOT_NORMALIZED"
FAILURE_LAYER = "market_learning_adapter.adapt_feature_frame"
REPRESENTATIVE_FAILURE_SIGNATURES = (
    "EXP-061 continuous feature realized_vol_1h must be finite or null",
    "EXP-061 continuous feature realized_vol_8h must be finite or null",
)

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


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def _validate_single_artifact(
    payload: Mapping[str, object],
    *,
    artifact_id: int,
    name: str,
    digest: str,
    label: str,
) -> None:
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError(f"{label} requires exactly one artifact")
    item = artifacts[0]
    if not isinstance(item, Mapping):
        raise ValueError(f"{label} artifact row is malformed")
    _require_exact(
        item,
        {
            "id": artifact_id,
            "name": name,
            "digest": digest,
            "expired": False,
        },
        prefix=label,
    )


def freeze_exp061_historical_failure(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    executor_run: Mapping[str, object],
    executor_artifacts_payload: Mapping[str, object],
    executor_zip_sha256: str,
    executor_json_sha256: str,
    historical_run_json_sha256: str,
    historical_runs_json_sha256: str,
    preflight_zip_sha256: str,
    preflight_json_sha256: str,
) -> dict[str, object]:
    _require_exact(
        run,
        {
            "id": EXP061_HISTORICAL_RUN_ID,
            "name": "phase8a-exp061-discovery",
            "path": ".github/workflows/phase8a-exp061-discovery.yml",
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": EXP061_HISTORICAL_RUN_HEAD_SHA,
            "run_number": EXP061_HISTORICAL_RUN_NUMBER,
            "run_attempt": EXP061_HISTORICAL_RUN_ATTEMPT,
            "status": "completed",
            "conclusion": "failure",
        },
        prefix="DEC-292 historical run",
    )

    terminal = classify_historical_terminal_result(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        expected_head_sha=EXP061_HISTORICAL_RUN_HEAD_SHA,
    )
    _require_exact(
        terminal,
        {
            "decision": EXP061_HISTORICAL_TERMINAL_REVIEW_DECISION,
            "stage": "EXP061_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED",
            "historical_run_id": EXP061_HISTORICAL_RUN_ID,
            "historical_run_number": 2,
            "historical_run_attempt": 1,
            "historical_run_conclusion": "failure",
            "historical_result_slot_consumed": True,
            "historical_result_success_complete": False,
            "materialized_job_count": 20,
            "artifact_count": 1,
            "github_unexpanded_matrix_placeholder_present": False,
            "aggregate_result_content_review_required": False,
            "rerun_authorized": False,
            "retry_authorized": False,
            "replacement_run_authorized": False,
            "candidate_compilation_authorized": False,
            "promotion_authorized": False,
            "phase8b_authorized": False,
            "trading_authorized": False,
        },
        prefix="DEC-292 terminal review",
    )
    if terminal.get("job_conclusion_counts") != {
        "success": 1,
        "failure": 18,
        "skipped": 1,
    }:
        raise ValueError("DEC-292 terminal job conclusion counts mismatch")

    _validate_single_artifact(
        artifacts_payload,
        artifact_id=EXP061_PREFLIGHT_ARTIFACT_ID,
        name=EXP061_PREFLIGHT_ARTIFACT_NAME,
        digest=EXP061_PREFLIGHT_ARTIFACT_DIGEST,
        label="DEC-292 preflight evidence",
    )

    _require_exact(
        executor_run,
        {
            "id": EXP061_EXECUTOR_RUN_ID,
            "name": "phase8a-exp061-historical-one-shot-execute",
            "path": ".github/workflows/phase8a-exp061-historical-one-shot-execute.yml",
            "event": "push",
            "head_branch": "main",
            "head_sha": EXP061_HISTORICAL_RUN_HEAD_SHA,
            "run_number": 1,
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "success",
        },
        prefix="DEC-292 executor run",
    )
    _validate_single_artifact(
        executor_artifacts_payload,
        artifact_id=EXP061_EXECUTOR_ARTIFACT_ID,
        name=EXP061_EXECUTOR_ARTIFACT_NAME,
        digest=EXP061_EXECUTOR_ARTIFACT_DIGEST,
        label="DEC-292 executor evidence",
    )

    exact_hashes = {
        "executor_zip_sha256": (
            executor_zip_sha256,
            EXP061_EXECUTOR_ARTIFACT_DIGEST.removeprefix("sha256:"),
        ),
        "executor_json_sha256": (
            executor_json_sha256,
            EXP061_EXECUTOR_JSON_SHA256,
        ),
        "historical_run_json_sha256": (
            historical_run_json_sha256,
            EXP061_EXECUTOR_HISTORICAL_RUN_JSON_SHA256,
        ),
        "historical_runs_json_sha256": (
            historical_runs_json_sha256,
            EXP061_EXECUTOR_HISTORICAL_RUNS_JSON_SHA256,
        ),
        "preflight_zip_sha256": (
            preflight_zip_sha256,
            EXP061_PREFLIGHT_ARTIFACT_DIGEST.removeprefix("sha256:"),
        ),
        "preflight_json_sha256": (
            preflight_json_sha256,
            EXP061_PREFLIGHT_JSON_SHA256,
        ),
    }
    for field, (actual, expected) in exact_hashes.items():
        if actual != expected:
            raise ValueError(f"DEC-292 {field} mismatch")

    return {
        "decision": EXP061_HISTORICAL_FAILURE_FREEZE_DECISION,
        "version": EXP061_HISTORICAL_FAILURE_FREEZE_VERSION,
        "stage": "EXP061_HISTORICAL_FAILURE_FROZEN_NO_RETRY",
        "historical_run_id": EXP061_HISTORICAL_RUN_ID,
        "historical_run_head_sha": EXP061_HISTORICAL_RUN_HEAD_SHA,
        "historical_run_number": 2,
        "historical_run_attempt": 1,
        "historical_run_conclusion": "failure",
        "historical_result_slot_consumed": True,
        "preflight_job_conclusion": "success",
        "failed_cell_job_count": 18,
        "aggregate_job_conclusion": "skipped",
        "cell_artifact_count": 0,
        "aggregate_artifact_count": 0,
        "preflight_artifact_id": EXP061_PREFLIGHT_ARTIFACT_ID,
        "preflight_artifact_digest": EXP061_PREFLIGHT_ARTIFACT_DIGEST,
        "executor_run_id": EXP061_EXECUTOR_RUN_ID,
        "executor_artifact_id": EXP061_EXECUTOR_ARTIFACT_ID,
        "executor_artifact_digest": EXP061_EXECUTOR_ARTIFACT_DIGEST,
        "failure_class": FAILURE_CLASS,
        "failure_layer": FAILURE_LAYER,
        "representative_failure_signatures": list(
            REPRESENTATIVE_FAILURE_SIGNATURES
        ),
        "failure_interpretation": (
            "IMPLEMENTATION_INPUT_NORMALIZATION_FAILURE_NOT_MARKET_RESULT"
        ),
        "exp061_reusable_as_result": False,
        "exp061_retry_authorized": False,
        "new_experiment_identity_required_for_repair": True,
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
    }


__all__ = [
    "EXP061_HISTORICAL_FAILURE_FREEZE_DECISION",
    "EXP061_HISTORICAL_FAILURE_FREEZE_VERSION",
    "EXP061_HISTORICAL_RUN_ID",
    "FAILURE_CLASS",
    "REPRESENTATIVE_FAILURE_SIGNATURES",
    "freeze_exp061_historical_failure",
]
