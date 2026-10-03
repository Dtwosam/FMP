from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2015_replacement_run_review import (
    ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_REVIEW_DECISION,
    ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_REVIEW_VERSION,
    validate_2015_replacement_run_review,
)


ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_DECISION = "DEC-501"
ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_VERSION = (
    "fmp-annual-catalogue-2015-replacement-run-freeze-v1"
)

RUN_REVIEW_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_replacement_run_review.py"
)
EXPECTED_RUN_REVIEW_SOURCE_BLOB_SHA = (
    "954718b9780004907c385ebb0496469d8433b844"
)


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_2015_replacement_run_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = root / RUN_REVIEW_SOURCE_PATH
    if not path.is_file():
        raise ValueError(f"DEC-501 source file missing: {path}")
    sha = _git_blob_sha(path)
    if sha != EXPECTED_RUN_REVIEW_SOURCE_BLOB_SHA:
        raise ValueError("DEC-501 run review source blob mismatch")
    if ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_REVIEW_DECISION != "DEC-500":
        raise ValueError("DEC-501 source review decision drift")
    if (
        ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_REVIEW_VERSION
        != "fmp-annual-catalogue-2015-replacement-run-review-v1"
    ):
        raise ValueError("DEC-501 source review version drift")
    return {"run_review_source_blob_sha": sha}


def freeze_2015_replacement_run_review(
    review: Mapping[str, object],
    *,
    repository_root: Path,
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2015_replacement_run_freeze_sources(
        repository_root=Path(repository_root),
    )
    validate_2015_replacement_run_review(review)
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if review.get("run_head_sha") != expected_head_sha:
        raise ValueError("DEC-501 review head mismatch")

    freeze: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_DECISION,
        "version": ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_VERSION,
        **source,
        "source_review_decision": "DEC-500",
        "source_review_version": (
            "fmp-annual-catalogue-2015-replacement-run-review-v1"
        ),
        "stage": "ANNUAL_CATALOGUE_2015_REPLACEMENT_RUNTIME_EVIDENCE_FROZEN",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2015",
        "run_id": review.get("run_id"),
        "run_number": review.get("run_number"),
        "run_attempt": review.get("run_attempt"),
        "run_status": review.get("run_status"),
        "run_conclusion": review.get("run_conclusion"),
        "preflight_job_id": review.get("preflight_job_id"),
        "freeze_job_id": review.get("freeze_job_id"),
        "cell_job_ids": review.get("cell_job_ids"),
        "preflight_artifact": review.get("preflight_artifact"),
        "freeze_artifact": review.get("freeze_artifact"),
        "cell_artifacts": review.get("cell_artifacts"),
        "freeze_artifact_zip_sha256": review.get(
            "freeze_artifact_zip_sha256"
        ),
        "freeze_evidence_canonical_sha256": review.get(
            "freeze_evidence_canonical_sha256"
        ),
        "freeze_evidence_fingerprint": review.get(
            "freeze_evidence_fingerprint"
        ),
        "annual_cell_count": review.get("annual_cell_count"),
        "directional_record_count": review.get(
            "directional_record_count"
        ),
        "evaluable_record_count": review.get("evaluable_record_count"),
        "zero_support_record_count": review.get(
            "zero_support_record_count"
        ),
        "total_support": review.get("total_support"),
        "review_fingerprint_sha256": review.get(
            "review_fingerprint_sha256"
        ),
        "replacement_authorization_consumed": True,
        "runtime_review_validated": True,
        "runtime_evidence_frozen": True,
        "next_segment_execution_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": (
            "CONCRETE_2015_ANNUAL_PATTERN_CATALOGUE_RUNTIME_EVIDENCE_BINDING"
        ),
    }
    freeze["freeze_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(freeze)
    )
    validate_2015_replacement_run_freeze(freeze)
    return freeze


def validate_2015_replacement_run_freeze(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = value.get("freeze_fingerprint_sha256")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("DEC-501 freeze fingerprint malformed")
    try:
        int(fingerprint, 16)
    except ValueError as exc:
        raise ValueError("DEC-501 freeze fingerprint must be hexadecimal") from exc
    unsigned = dict(value)
    unsigned.pop("freeze_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-501 freeze fingerprint mismatch")
    if value.get("decision") != "DEC-501":
        raise ValueError("DEC-501 decision mismatch")
    if value.get("source_review_decision") != "DEC-500":
        raise ValueError("DEC-501 source review decision mismatch")
    if value.get("annual_segment_label") != "2015":
        raise ValueError("DEC-501 annual segment mismatch")
    if value.get("run_number") != 376:
        raise ValueError("DEC-501 run number mismatch")
    if value.get("run_attempt") != 1:
        raise ValueError("DEC-501 run attempt mismatch")
    if value.get("run_conclusion") != "success":
        raise ValueError("DEC-501 run conclusion mismatch")
    if value.get("annual_cell_count") != 18:
        raise ValueError("DEC-501 annual cell count mismatch")
    if value.get("directional_record_count") != 89460:
        raise ValueError("DEC-501 directional record count mismatch")
    if value.get("replacement_authorization_consumed") is not True:
        raise ValueError("DEC-501 replacement authorization must be consumed")
    if value.get("runtime_review_validated") is not True:
        raise ValueError("DEC-501 runtime review must be validated")
    if value.get("runtime_evidence_frozen") is not True:
        raise ValueError("DEC-501 runtime evidence must be frozen")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    for field in (
        "next_segment_execution_authorized",
        "cross_year_result_production_authorized",
        "strategy_v1_synthesis_authorized",
        "promotion_authorized",
        "phase8b_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"DEC-501 {field} must remain false")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_DECISION",
    "ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_VERSION",
    "freeze_2015_replacement_run_review",
    "validate_2015_replacement_run_freeze",
    "validate_2015_replacement_run_freeze_sources",
]
