from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_segment_evidence import (
    EXPECTED_CELLS_PER_SEGMENT,
    EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT,
    validate_annual_segment_freeze,
)
from .pattern_protocol import HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_REVIEW_DECISION = "DEC-500"
ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_REVIEW_VERSION = (
    "fmp-annual-catalogue-2015-replacement-run-review-v1"
)

DISPATCH_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2015_replacement_dispatch_action_preflight.py"
)
EXPECTED_DISPATCH_PREFLIGHT_SOURCE_BLOB_SHA = (
    "6701d3607d1576a81848810ec699ffd5b7a858a1"
)
SEGMENT_FREEZE_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_segment_evidence.py"
)
EXPECTED_SEGMENT_FREEZE_SOURCE_BLOB_SHA = (
    "1b14279864f01a1284c5be31552eee9bb3a2220c"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_REPAIRED_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

ANNUAL_SEGMENT_LABEL = "2015"
EXPECTED_RUN_NUMBER = 376
EXPECTED_RUN_ATTEMPT = 1
EXPECTED_JOB_COUNT = 20
EXPECTED_ARTIFACT_COUNT = 20


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


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def validate_2015_replacement_run_review_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dispatch_preflight_source_blob_sha": (
            root / DISPATCH_PREFLIGHT_SOURCE_PATH,
            EXPECTED_DISPATCH_PREFLIGHT_SOURCE_BLOB_SHA,
        ),
        "segment_freeze_source_blob_sha": (
            root / SEGMENT_FREEZE_SOURCE_PATH,
            EXPECTED_SEGMENT_FREEZE_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_REPAIRED_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-500 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-500 {field} mismatch")
        actual[field] = sha
    return actual


def _expected_cell_job_names() -> tuple[str, ...]:
    return tuple(
        f"annual-cell-{ANNUAL_SEGMENT_LABEL}-{symbol}-{timeframe}-{horizon}m"
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
    )


def _expected_cell_artifact_names(head_sha: str) -> tuple[str, ...]:
    return tuple(
        (
            f"phase8a-annual-catalogue-cell-{ANNUAL_SEGMENT_LABEL}-"
            f"{symbol}-{timeframe}-{horizon}m-{head_sha}"
        )
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
    )


def _validate_run(
    run: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> dict[str, object]:
    exact = {
        "name": "phase8a-annual-pattern-catalogue",
        "path": ACTIVE_WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": expected_head_sha,
        "run_number": EXPECTED_RUN_NUMBER,
        "run_attempt": EXPECTED_RUN_ATTEMPT,
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in exact.items():
        if run.get(field) != expected:
            raise ValueError(f"DEC-500 run {field} mismatch")
    return {
        "run_id": _positive_int(run.get("id"), field="run id"),
        "run_number": EXPECTED_RUN_NUMBER,
        "run_attempt": EXPECTED_RUN_ATTEMPT,
        "run_status": "completed",
        "run_conclusion": "success",
        "run_head_sha": expected_head_sha,
    }


def _validate_jobs(jobs_payload: Mapping[str, object]) -> dict[str, object]:
    rows = jobs_payload.get("jobs")
    if not isinstance(rows, list) or len(rows) != EXPECTED_JOB_COUNT:
        raise ValueError("DEC-500 job inventory count mismatch")
    expected_names = {
        f"annual-preflight-{ANNUAL_SEGMENT_LABEL}",
        f"annual-freeze-{ANNUAL_SEGMENT_LABEL}",
        *_expected_cell_job_names(),
    }
    seen: dict[str, Mapping[str, object]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-500 job row malformed")
        name = raw.get("name")
        if not isinstance(name, str) or name not in expected_names:
            raise ValueError("DEC-500 unexpected job name")
        if name in seen:
            raise ValueError("DEC-500 duplicate job name")
        if raw.get("status") != "completed" or raw.get("conclusion") != "success":
            raise ValueError(f"DEC-500 job not successful: {name}")
        _positive_int(raw.get("id"), field=f"job id {name}")
        seen[name] = raw
    if set(seen) != expected_names:
        raise ValueError("DEC-500 job inventory mismatch")
    return {
        "preflight_job_id": int(
            seen[f"annual-preflight-{ANNUAL_SEGMENT_LABEL}"]["id"]
        ),
        "freeze_job_id": int(
            seen[f"annual-freeze-{ANNUAL_SEGMENT_LABEL}"]["id"]
        ),
        "cell_job_ids": {
            name: int(seen[name]["id"])
            for name in sorted(_expected_cell_job_names())
        },
    }


def _artifact_row(
    raw: Mapping[str, object],
    *,
    expected_name: str,
) -> dict[str, object]:
    if raw.get("name") != expected_name:
        raise ValueError("DEC-500 artifact name mismatch")
    if raw.get("expired") is not False:
        raise ValueError(f"DEC-500 artifact expired: {expected_name}")
    digest = raw.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ValueError(f"DEC-500 artifact digest malformed: {expected_name}")
    digest_sha256 = _validate_sha256(
        digest.removeprefix("sha256:"),
        field=f"artifact digest {expected_name}",
    )
    return {
        "id": _positive_int(raw.get("id"), field=f"artifact id {expected_name}"),
        "name": expected_name,
        "digest": f"sha256:{digest_sha256}",
        "size_in_bytes": _positive_int(
            raw.get("size_in_bytes"),
            field=f"artifact size {expected_name}",
        ),
    }


def _validate_artifacts(
    artifacts_payload: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> dict[str, object]:
    rows = artifacts_payload.get("artifacts")
    if not isinstance(rows, list) or len(rows) != EXPECTED_ARTIFACT_COUNT:
        raise ValueError("DEC-500 artifact inventory count mismatch")
    by_name: dict[str, Mapping[str, object]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-500 artifact row malformed")
        name = raw.get("name")
        if not isinstance(name, str) or name in by_name:
            raise ValueError("DEC-500 artifact name inventory malformed")
        by_name[name] = raw

    preflight_name = (
        f"phase8a-annual-catalogue-preflight-{ANNUAL_SEGMENT_LABEL}-"
        f"{expected_head_sha}"
    )
    freeze_name = (
        f"phase8a-annual-catalogue-freeze-{ANNUAL_SEGMENT_LABEL}-"
        f"{expected_head_sha}"
    )
    cell_names = _expected_cell_artifact_names(expected_head_sha)
    expected_names = {preflight_name, freeze_name, *cell_names}
    if set(by_name) != expected_names:
        raise ValueError("DEC-500 artifact inventory mismatch")

    preflight = _artifact_row(by_name[preflight_name], expected_name=preflight_name)
    freeze = _artifact_row(by_name[freeze_name], expected_name=freeze_name)
    cells = {
        name: _artifact_row(by_name[name], expected_name=name)
        for name in sorted(cell_names)
    }
    return {
        "preflight_artifact": preflight,
        "freeze_artifact": freeze,
        "cell_artifacts": cells,
    }


def review_2015_replacement_run(
    *,
    repository_root: Path,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    freeze_evidence: Mapping[str, object],
    freeze_artifact_zip_sha256: str,
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2015_replacement_run_review_sources(
        repository_root=Path(repository_root),
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    run_identity = _validate_run(run, expected_head_sha=expected_head_sha)
    jobs = _validate_jobs(jobs_payload)
    artifacts = _validate_artifacts(
        artifacts_payload,
        expected_head_sha=expected_head_sha,
    )
    freeze_zip_sha256 = _validate_sha256(
        freeze_artifact_zip_sha256,
        field="freeze_artifact_zip_sha256",
    )
    freeze_artifact = artifacts["freeze_artifact"]
    assert isinstance(freeze_artifact, Mapping)
    if freeze_artifact.get("digest") != f"sha256:{freeze_zip_sha256}":
        raise ValueError("DEC-500 freeze artifact ZIP digest mismatch")

    validate_annual_segment_freeze(freeze_evidence)
    if freeze_evidence.get("annual_segment_label") != ANNUAL_SEGMENT_LABEL:
        raise ValueError("DEC-500 freeze annual segment mismatch")
    if freeze_evidence.get("code_commit") != expected_head_sha:
        raise ValueError("DEC-500 freeze code commit mismatch")
    if freeze_evidence.get("annual_cell_count") != EXPECTED_CELLS_PER_SEGMENT:
        raise ValueError("DEC-500 freeze annual cell count mismatch")
    if (
        freeze_evidence.get("directional_record_count")
        != EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT
    ):
        raise ValueError("DEC-500 freeze directional record count mismatch")

    freeze_bytes = _canonical_json(dict(freeze_evidence))
    review: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_REVIEW_DECISION,
        "version": ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_REVIEW_VERSION,
        **source,
        **run_identity,
        **jobs,
        **artifacts,
        "annual_segment_label": ANNUAL_SEGMENT_LABEL,
        "freeze_artifact_zip_sha256": freeze_zip_sha256,
        "freeze_evidence_canonical_sha256": _sha256_bytes(freeze_bytes),
        "freeze_evidence_fingerprint": freeze_evidence.get(
            "evidence_fingerprint"
        ),
        "annual_cell_count": freeze_evidence.get("annual_cell_count"),
        "directional_record_count": freeze_evidence.get(
            "directional_record_count"
        ),
        "evaluable_record_count": freeze_evidence.get(
            "evaluable_record_count"
        ),
        "zero_support_record_count": freeze_evidence.get(
            "zero_support_record_count"
        ),
        "total_support": freeze_evidence.get("total_support"),
        "replacement_authorization_consumed": True,
        "review_validated": True,
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
        "next_gate": "DETERMINISTIC_2015_REPLACEMENT_RUNTIME_EVIDENCE_FREEZE",
    }
    review["review_fingerprint_sha256"] = _sha256_bytes(_canonical_json(review))
    validate_2015_replacement_run_review(review)
    return review


def validate_2015_replacement_run_review(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("review_fingerprint_sha256"),
        field="DEC-500 review fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("review_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-500 review fingerprint mismatch")
    if value.get("decision") != "DEC-500":
        raise ValueError("DEC-500 decision mismatch")
    if value.get("run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-500 run number mismatch")
    if value.get("run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-500 run attempt mismatch")
    if value.get("run_conclusion") != "success":
        raise ValueError("DEC-500 run conclusion mismatch")
    if value.get("annual_segment_label") != ANNUAL_SEGMENT_LABEL:
        raise ValueError("DEC-500 annual segment mismatch")
    if value.get("annual_cell_count") != EXPECTED_CELLS_PER_SEGMENT:
        raise ValueError("DEC-500 annual cell count mismatch")
    if (
        value.get("directional_record_count")
        != EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT
    ):
        raise ValueError("DEC-500 directional record count mismatch")
    if value.get("replacement_authorization_consumed") is not True:
        raise ValueError("DEC-500 replacement authorization must be consumed")
    if value.get("review_validated") is not True:
        raise ValueError("DEC-500 review must be validated")
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
            raise ValueError(f"DEC-500 {field} must remain false")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_REVIEW_DECISION",
    "ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_REVIEW_VERSION",
    "review_2015_replacement_run",
    "validate_2015_replacement_run_review",
    "validate_2015_replacement_run_review_sources",
]
