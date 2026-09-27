from __future__ import annotations

from collections import Counter
from typing import Mapping

from .historical_result_review_contract import (
    EXP061_HISTORICAL_TERMINAL_REVIEW_DECISION,
    EXP061_HISTORICAL_TERMINAL_REVIEW_VERSION,
    classify_historical_terminal_result,
)


EXP061_FAILED_RESULT_DECISION = "DEC-292"
EXP061_FAILED_RESULT_VERSION = "fmp-exp061-reviewed-failed-historical-result-v1"

EXECUTOR_RUN_ID = 36335739823
EXECUTOR_HEAD_SHA = "a7b3bc2d0b196da2631b64c19331efb3af12c98e"
EXECUTOR_ARTIFACT_ID = 10936194549
EXECUTOR_ARTIFACT_NAME = (
    "exp061-dec289-historical-dispatch-evidence-"
    "a7b3bc2d0b196da2631b64c19331efb3af12c98e"
)
EXECUTOR_ARTIFACT_DIGEST = (
    "sha256:e7ffe1f08ce358eca210ef41397165196cb64bee31696a180c7fd02af8c68f1c"
)
EXECUTOR_ZIP_SHA256 = (
    "e7ffe1f08ce358eca210ef41397165196cb64bee31696a180c7fd02af8c68f1c"
)
EXECUTOR_FILE_SHA256 = {
    "executor.json": "1e35f83f7b7e584c3ff13b4c6ba46d2c358bae323b06e564f069f03d4aba313c",
    "historical-run.json": (
        "3fe6a0cd0563e514d868bce9ab6076844049046f86ab87f2a8928a39e697d641"
    ),
    "historical-runs.json": (
        "e0515a6175e343e778e2a5da307889d89f808dc3978a4789716604ba001dec6f"
    ),
}
EXECUTOR_JSON_HAS_LEADING_DISPATCH_URL = True

HISTORICAL_RUN_ID = 36335879839
HISTORICAL_HEAD_SHA = EXECUTOR_HEAD_SHA
HISTORICAL_RUN_NUMBER = 2
HISTORICAL_RUN_ATTEMPT = 1
HISTORICAL_RUN_CONCLUSION = "failure"

PREFLIGHT_ARTIFACT_ID = 10937316246
PREFLIGHT_ARTIFACT_NAME = (
    "phase8a-exp061-preflight-"
    "a7b3bc2d0b196da2631b64c19331efb3af12c98e"
)
PREFLIGHT_ARTIFACT_DIGEST = (
    "sha256:e9a898df51317250944ad0a111d01d96d2081d708ea80872ed11b5cee48d356f"
)
PREFLIGHT_ZIP_SHA256 = (
    "e9a898df51317250944ad0a111d01d96d2081d708ea80872ed11b5cee48d356f"
)
PREFLIGHT_JSON_SHA256 = (
    "d8a85a2482f1bf72128a8f019b73c59fccad612ad02722821cca1a09c7bc582d"
)

EXPECTED_JOBS: dict[str, tuple[int, str]] = {
    "exp061-preflight": (108666516885, "success"),
    "exp061-cell-EURUSD-5m-60m": (108666605488, "failure"),
    "exp061-cell-EURUSD-5m-240m": (108666605382, "failure"),
    "exp061-cell-EURUSD-15m-60m": (108666605427, "failure"),
    "exp061-cell-EURUSD-15m-240m": (108666605479, "failure"),
    "exp061-cell-EURUSD-1h-60m": (108666605444, "failure"),
    "exp061-cell-EURUSD-1h-240m": (108666605440, "failure"),
    "exp061-cell-GBPUSD-5m-60m": (108666605475, "failure"),
    "exp061-cell-GBPUSD-5m-240m": (108666605476, "failure"),
    "exp061-cell-GBPUSD-15m-60m": (108666605520, "failure"),
    "exp061-cell-GBPUSD-15m-240m": (108666605527, "failure"),
    "exp061-cell-GBPUSD-1h-60m": (108666605567, "failure"),
    "exp061-cell-GBPUSD-1h-240m": (108666605486, "failure"),
    "exp061-cell-USDJPY-5m-60m": (108666605501, "failure"),
    "exp061-cell-USDJPY-5m-240m": (108666606397, "failure"),
    "exp061-cell-USDJPY-15m-60m": (108666606336, "failure"),
    "exp061-cell-USDJPY-15m-240m": (108666606402, "failure"),
    "exp061-cell-USDJPY-1h-60m": (108666606420, "failure"),
    "exp061-cell-USDJPY-1h-240m": (108666606450, "failure"),
    "exp061-aggregate": (108667168765, "skipped"),
}

ERROR_VOL_1H = "EXP-061 continuous feature realized_vol_1h must be finite or null"
ERROR_VOL_8H = "EXP-061 continuous feature realized_vol_8h must be finite or null"

EXPECTED_CELL_ERRORS: dict[str, str] = {
    "exp061-cell-EURUSD-5m-60m": ERROR_VOL_8H,
    "exp061-cell-EURUSD-5m-240m": ERROR_VOL_8H,
    "exp061-cell-EURUSD-15m-60m": ERROR_VOL_1H,
    "exp061-cell-EURUSD-15m-240m": ERROR_VOL_1H,
    "exp061-cell-EURUSD-1h-60m": ERROR_VOL_8H,
    "exp061-cell-EURUSD-1h-240m": ERROR_VOL_8H,
    "exp061-cell-GBPUSD-5m-60m": ERROR_VOL_1H,
    "exp061-cell-GBPUSD-5m-240m": ERROR_VOL_1H,
    "exp061-cell-GBPUSD-15m-60m": ERROR_VOL_1H,
    "exp061-cell-GBPUSD-15m-240m": ERROR_VOL_1H,
    "exp061-cell-GBPUSD-1h-60m": ERROR_VOL_8H,
    "exp061-cell-GBPUSD-1h-240m": ERROR_VOL_8H,
    "exp061-cell-USDJPY-5m-60m": ERROR_VOL_1H,
    "exp061-cell-USDJPY-5m-240m": ERROR_VOL_1H,
    "exp061-cell-USDJPY-15m-60m": ERROR_VOL_8H,
    "exp061-cell-USDJPY-15m-240m": ERROR_VOL_8H,
    "exp061-cell-USDJPY-1h-60m": ERROR_VOL_8H,
    "exp061-cell-USDJPY-1h-240m": ERROR_VOL_8H,
}

ROOT_CAUSE = (
    "NONFINITE_ROLLING_FEATURE_WARMUP_VALUES_NOT_NORMALIZED_AT_ADAPTER_BOUNDARY"
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


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


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
    raw = artifacts[0]
    if not isinstance(raw, Mapping):
        raise ValueError(f"{label} artifact row is malformed")
    expected = {
        "id": artifact_id,
        "name": name,
        "digest": digest,
        "expired": False,
    }
    for field, expected_value in expected.items():
        if raw.get(field) != expected_value:
            raise ValueError(f"{label} artifact {field} mismatch")


def _validate_exact_jobs(jobs_payload: Mapping[str, object]) -> None:
    raw = jobs_payload.get("jobs")
    if not isinstance(raw, list) or len(raw) != len(EXPECTED_JOBS):
        raise ValueError("DEC-292 requires exact 20-job inventory")

    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-292 job row is malformed")
        name = item.get("name")
        if not isinstance(name, str) or name not in EXPECTED_JOBS:
            raise ValueError(f"DEC-292 unexpected job name: {name!r}")
        if name in seen:
            raise ValueError("DEC-292 duplicate job name")
        seen.add(name)
        expected_id, expected_conclusion = EXPECTED_JOBS[name]
        if item.get("id") != expected_id:
            raise ValueError(f"DEC-292 job id mismatch for {name}")
        if item.get("status") != "completed":
            raise ValueError(f"DEC-292 job status mismatch for {name}")
        if item.get("conclusion") != expected_conclusion:
            raise ValueError(f"DEC-292 job conclusion mismatch for {name}")

    if seen != set(EXPECTED_JOBS):
        raise ValueError("DEC-292 exact job inventory mismatch")


def freeze_failed_historical_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    historical_artifacts_payload: Mapping[str, object],
    executor_artifacts_payload: Mapping[str, object],
    cell_failure_messages: Mapping[str, str],
    executor_zip_sha256: str,
    executor_file_sha256: Mapping[str, str],
    preflight_zip_sha256: str,
    preflight_json_sha256: str,
) -> dict[str, object]:
    terminal = classify_historical_terminal_result(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=historical_artifacts_payload,
        expected_head_sha=HISTORICAL_HEAD_SHA,
    )
    expected_terminal = {
        "decision": EXP061_HISTORICAL_TERMINAL_REVIEW_DECISION,
        "version": EXP061_HISTORICAL_TERMINAL_REVIEW_VERSION,
        "stage": "EXP061_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED",
        "historical_run_id": HISTORICAL_RUN_ID,
        "historical_run_head_sha": HISTORICAL_HEAD_SHA,
        "historical_run_number": HISTORICAL_RUN_NUMBER,
        "historical_run_attempt": HISTORICAL_RUN_ATTEMPT,
        "historical_run_conclusion": HISTORICAL_RUN_CONCLUSION,
        "historical_result_slot_consumed": True,
        "historical_result_success_complete": False,
        "materialized_job_count": 20,
        "artifact_count": 1,
        "aggregate_result_content_review_required": False,
        "partial_evidence_may_be_preserved": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
    }
    for field, expected_value in expected_terminal.items():
        if terminal.get(field) != expected_value:
            raise ValueError(f"DEC-292 terminal review {field} mismatch")

    _validate_exact_jobs(jobs_payload)
    _validate_single_artifact(
        historical_artifacts_payload,
        artifact_id=PREFLIGHT_ARTIFACT_ID,
        name=PREFLIGHT_ARTIFACT_NAME,
        digest=PREFLIGHT_ARTIFACT_DIGEST,
        label="DEC-292 historical result",
    )
    _validate_single_artifact(
        executor_artifacts_payload,
        artifact_id=EXECUTOR_ARTIFACT_ID,
        name=EXECUTOR_ARTIFACT_NAME,
        digest=EXECUTOR_ARTIFACT_DIGEST,
        label="DEC-292 executor evidence",
    )

    if dict(cell_failure_messages) != EXPECTED_CELL_ERRORS:
        raise ValueError("DEC-292 cell failure messages mismatch")

    if _validate_sha256(
        executor_zip_sha256,
        field="executor ZIP sha256",
    ) != EXECUTOR_ZIP_SHA256:
        raise ValueError("DEC-292 executor ZIP sha256 mismatch")

    if dict(executor_file_sha256) != EXECUTOR_FILE_SHA256:
        raise ValueError("DEC-292 executor file hashes mismatch")

    if _validate_sha256(
        preflight_zip_sha256,
        field="preflight ZIP sha256",
    ) != PREFLIGHT_ZIP_SHA256:
        raise ValueError("DEC-292 preflight ZIP sha256 mismatch")

    if _validate_sha256(
        preflight_json_sha256,
        field="preflight JSON sha256",
    ) != PREFLIGHT_JSON_SHA256:
        raise ValueError("DEC-292 preflight JSON sha256 mismatch")

    error_counts = Counter(EXPECTED_CELL_ERRORS.values())
    return {
        "decision": EXP061_FAILED_RESULT_DECISION,
        "version": EXP061_FAILED_RESULT_VERSION,
        "stage": "EXP061_HISTORICAL_RESULT_FAILED_REVIEWED_AND_CLOSED",
        "experiment_id": "EXP-20260927-061",
        "executor_run_id": EXECUTOR_RUN_ID,
        "executor_head_sha": EXECUTOR_HEAD_SHA,
        "executor_artifact_id": EXECUTOR_ARTIFACT_ID,
        "executor_artifact_digest": EXECUTOR_ARTIFACT_DIGEST,
        "executor_zip_sha256": EXECUTOR_ZIP_SHA256,
        "executor_file_sha256": dict(EXECUTOR_FILE_SHA256),
        "executor_json_has_leading_dispatch_url": (
            EXECUTOR_JSON_HAS_LEADING_DISPATCH_URL
        ),
        "historical_run_id": HISTORICAL_RUN_ID,
        "historical_run_head_sha": HISTORICAL_HEAD_SHA,
        "historical_run_number": HISTORICAL_RUN_NUMBER,
        "historical_run_attempt": HISTORICAL_RUN_ATTEMPT,
        "historical_run_conclusion": HISTORICAL_RUN_CONCLUSION,
        "preflight_artifact_id": PREFLIGHT_ARTIFACT_ID,
        "preflight_artifact_digest": PREFLIGHT_ARTIFACT_DIGEST,
        "preflight_zip_sha256": PREFLIGHT_ZIP_SHA256,
        "preflight_json_sha256": PREFLIGHT_JSON_SHA256,
        "preflight_job_conclusion": "success",
        "failed_cell_job_count": 18,
        "aggregate_job_conclusion": "skipped",
        "cell_artifact_count": 0,
        "aggregate_artifact_count": 0,
        "root_cause": ROOT_CAUSE,
        "failure_message_counts": dict(error_counts),
        "realized_vol_1h_failure_count": error_counts[ERROR_VOL_1H],
        "realized_vol_8h_failure_count": error_counts[ERROR_VOL_8H],
        "historical_result_slot_consumed": True,
        "exp061_closed": True,
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
    "ERROR_VOL_1H",
    "ERROR_VOL_8H",
    "EXECUTOR_ARTIFACT_ID",
    "EXECUTOR_RUN_ID",
    "EXPECTED_CELL_ERRORS",
    "EXPECTED_JOBS",
    "EXP061_FAILED_RESULT_DECISION",
    "EXP061_FAILED_RESULT_VERSION",
    "HISTORICAL_RUN_ID",
    "PREFLIGHT_ARTIFACT_ID",
    "ROOT_CAUSE",
    "freeze_failed_historical_result",
]
