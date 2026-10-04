from __future__ import annotations

import hashlib
import json
from typing import Mapping


ANNUAL_CATALOGUE_2015_RUN376_FAILURE_RECEIPT_DECISION = "DEC-526"
ANNUAL_CATALOGUE_2015_RUN376_FAILURE_RECEIPT_VERSION = (
    "fmp-annual-catalogue-2015-run376-failure-receipt-v1"
)

FAILED_RUN_ID = 37191637168
FAILED_RUN_NUMBER = 376
FAILED_RUN_ATTEMPT = 1
FAILED_RUN_HEAD_SHA = "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3"
FAILED_PREFLIGHT_JOB_ID = 111404873333


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _fingerprint(value: Mapping[str, object]) -> str:
    return hashlib.sha256(_canonical_json(dict(value))).hexdigest()


def build_2015_run376_failure_receipt(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
) -> dict[str, object]:
    exact = {
        "id": FAILED_RUN_ID,
        "name": "phase8a-annual-pattern-catalogue",
        "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": FAILED_RUN_HEAD_SHA,
        "run_number": FAILED_RUN_NUMBER,
        "run_attempt": FAILED_RUN_ATTEMPT,
        "status": "completed",
        "conclusion": "failure",
    }
    for field, expected in exact.items():
        if run.get(field) != expected:
            raise ValueError(f"DEC-526 failed run {field} mismatch")

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError("DEC-526 jobs payload malformed")
    preflight = [
        row
        for row in jobs
        if isinstance(row, Mapping)
        and row.get("name") == "annual-preflight-2015"
    ]
    if len(preflight) != 1:
        raise ValueError("DEC-526 preflight job inventory mismatch")
    job = preflight[0]
    if job.get("id") != FAILED_PREFLIGHT_JOB_ID:
        raise ValueError("DEC-526 preflight job id mismatch")
    if job.get("status") != "completed" or job.get("conclusion") != "failure":
        raise ValueError("DEC-526 preflight job must be completed failure")

    non_preflight = [
        row
        for row in jobs
        if isinstance(row, Mapping)
        and row.get("name") != "annual-preflight-2015"
    ]
    if not non_preflight:
        raise ValueError("DEC-526 skipped downstream jobs missing")
    if any(
        row.get("status") != "completed" or row.get("conclusion") != "skipped"
        for row in non_preflight
    ):
        raise ValueError("DEC-526 downstream annual jobs must be skipped")

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2015_RUN376_FAILURE_RECEIPT_DECISION,
        "version": ANNUAL_CATALOGUE_2015_RUN376_FAILURE_RECEIPT_VERSION,
        "stage": "ANNUAL_CATALOGUE_2015_RUN376_PREFLIGHT_FAILED",
        "run_id": FAILED_RUN_ID,
        "run_number": FAILED_RUN_NUMBER,
        "run_attempt": FAILED_RUN_ATTEMPT,
        "run_head_sha": FAILED_RUN_HEAD_SHA,
        "run_status": "completed",
        "run_conclusion": "failure",
        "preflight_job_id": FAILED_PREFLIGHT_JOB_ID,
        "preflight_conclusion": "failure",
        "downstream_jobs_skipped": True,
        "result_produced": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_377_authorized": False,
        "run_378_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": "FRESH_2015_RUN377_EXECUTION_AUTHORIZATION",
    }
    value["receipt_fingerprint_sha256"] = _fingerprint(value)
    validate_2015_run376_failure_receipt(value)
    return value


def validate_2015_run376_failure_receipt(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = value.get("receipt_fingerprint_sha256")
    unsigned = dict(value)
    unsigned.pop("receipt_fingerprint_sha256", None)
    if fingerprint != _fingerprint(unsigned):
        raise ValueError("DEC-526 receipt fingerprint mismatch")
    exact = {
        "decision": "DEC-526",
        "stage": "ANNUAL_CATALOGUE_2015_RUN376_PREFLIGHT_FAILED",
        "run_id": FAILED_RUN_ID,
        "run_number": 376,
        "run_attempt": 1,
        "run_head_sha": FAILED_RUN_HEAD_SHA,
        "run_conclusion": "failure",
        "preflight_conclusion": "failure",
        "downstream_jobs_skipped": True,
        "result_produced": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_377_authorized": False,
        "run_378_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-526 {field} mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2015_RUN376_FAILURE_RECEIPT_DECISION",
    "ANNUAL_CATALOGUE_2015_RUN376_FAILURE_RECEIPT_VERSION",
    "FAILED_RUN_HEAD_SHA",
    "FAILED_RUN_ID",
    "build_2015_run376_failure_receipt",
    "validate_2015_run376_failure_receipt",
]
