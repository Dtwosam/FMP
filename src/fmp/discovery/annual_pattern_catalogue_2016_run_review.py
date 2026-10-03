from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2016_dispatch_action_preflight import (
    ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_DECISION,
    ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_VERSION,
    validate_2016_dispatch_action_preflight,
)
from .annual_pattern_catalogue_segment_evidence import (
    EXPECTED_CELLS_PER_SEGMENT,
    EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT,
    validate_annual_segment_freeze,
)
from .pattern_protocol import HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


ANNUAL_CATALOGUE_2016_RUN_REVIEW_DECISION = "DEC-512"
ANNUAL_CATALOGUE_2016_RUN_REVIEW_VERSION = (
    "fmp-annual-catalogue-2016-run-review-v1"
)

DISPATCH_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2016_dispatch_action_preflight.py"
)
EXPECTED_DISPATCH_PREFLIGHT_SOURCE_BLOB_SHA = (
    "301214231775b83df99d1ff9f878f916ec76a07e"
)
SEGMENT_FREEZE_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_segment_evidence.py"
)
EXPECTED_SEGMENT_FREEZE_SOURCE_BLOB_SHA = (
    "1b14279864f01a1284c5be31552eee9bb3a2220c"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "f7e65ee95f472918e390bceedd7cf2f38bbf7e92"
)

ANNUAL_SEGMENT_LABEL = "2016"
EXPECTED_RUN_NUMBER = 3
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
        raise ValueError(f"DEC-512 {field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-512 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-512 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-512 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-512 {field} must be a positive integer")
    return value


def validate_2016_run_review_sources(
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
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-512 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-512 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_DECISION != "DEC-511":
        raise ValueError("DEC-512 dispatch preflight decision drift")
    if (
        ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_VERSION
        != "fmp-annual-catalogue-2016-dispatch-action-preflight-v1"
    ):
        raise ValueError("DEC-512 dispatch preflight version drift")
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
            raise ValueError(f"DEC-512 run {field} mismatch")
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
        raise ValueError("DEC-512 job inventory count mismatch")
    expected_names = {
        f"annual-preflight-{ANNUAL_SEGMENT_LABEL}",
        f"annual-freeze-{ANNUAL_SEGMENT_LABEL}",
        *_expected_cell_job_names(),
    }
    seen: dict[str, Mapping[str, object]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-512 job row malformed")
        name = raw.get("name")
        if not isinstance(name, str) or name not in expected_names:
            raise ValueError("DEC-512 unexpected job name")
        if name in seen:
            raise ValueError("DEC-512 duplicate job name")
        if raw.get("status") != "completed" or raw.get("conclusion") != "success":
            raise ValueError(f"DEC-512 job not successful: {name}")
        _positive_int(raw.get("id"), field=f"job id {name}")
        seen[name] = raw
    if set(seen) != expected_names:
        raise ValueError("DEC-512 job inventory mismatch")
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
        raise ValueError("DEC-512 artifact name mismatch")
    if raw.get("expired") is not False:
        raise ValueError(f"DEC-512 artifact expired: {expected_name}")
    digest = raw.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ValueError(f"DEC-512 artifact digest malformed: {expected_name}")
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
        raise ValueError("DEC-512 artifact inventory count mismatch")
    by_name: dict[str, Mapping[str, object]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-512 artifact row malformed")
        name = raw.get("name")
        if not isinstance(name, str) or name in by_name:
            raise ValueError("DEC-512 artifact name inventory malformed")
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
        raise ValueError("DEC-512 artifact inventory mismatch")

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


def review_2016_run(
    dispatch_preflight: Mapping[str, object],
    *,
    repository_root: Path,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    freeze_evidence: Mapping[str, object],
    freeze_artifact_zip_sha256: str,
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2016_run_review_sources(
        repository_root=Path(repository_root),
    )
    validate_2016_dispatch_action_preflight(dispatch_preflight)

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if dispatch_preflight.get("expected_head_sha") != expected_head_sha:
        raise ValueError("DEC-512 dispatch preflight head mismatch")
    if dispatch_preflight.get("install_commit_sha") != expected_head_sha:
        raise ValueError("DEC-512 install commit/head mismatch")
    if dispatch_preflight.get("annual_segment_label") != ANNUAL_SEGMENT_LABEL:
        raise ValueError("DEC-512 dispatch preflight annual segment mismatch")
    if dispatch_preflight.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-512 dispatch preflight run number mismatch")
    if dispatch_preflight.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-512 dispatch preflight run attempt mismatch")
    if dispatch_preflight.get("dispatch_parameters_frozen") is not True:
        raise ValueError("DEC-512 dispatch parameters are not frozen")
    if dispatch_preflight.get("dispatch_command_present") is not False:
        raise ValueError("DEC-512 source preflight contains a dispatch command")
    if dispatch_preflight.get("dispatch_action_executed") is not False:
        raise ValueError("DEC-512 source preflight already records dispatch execution")

    previous_run_id = _positive_int(
        dispatch_preflight.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    if dispatch_preflight.get("successful_2015_run_id") != previous_run_id:
        raise ValueError("DEC-512 predecessor run identity mismatch")

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
        raise ValueError("DEC-512 freeze artifact ZIP digest mismatch")

    validate_annual_segment_freeze(freeze_evidence)
    if freeze_evidence.get("annual_segment_label") != ANNUAL_SEGMENT_LABEL:
        raise ValueError("DEC-512 freeze annual segment mismatch")
    if freeze_evidence.get("code_commit") != expected_head_sha:
        raise ValueError("DEC-512 freeze code commit mismatch")
    if freeze_evidence.get("annual_cell_count") != EXPECTED_CELLS_PER_SEGMENT:
        raise ValueError("DEC-512 freeze annual cell count mismatch")
    if (
        freeze_evidence.get("directional_record_count")
        != EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT
    ):
        raise ValueError("DEC-512 freeze directional record count mismatch")

    freeze_bytes = _canonical_json(dict(freeze_evidence))
    review: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2016_RUN_REVIEW_DECISION,
        "version": ANNUAL_CATALOGUE_2016_RUN_REVIEW_VERSION,
        **source,
        **run_identity,
        **jobs,
        **artifacts,
        "source_dispatch_preflight_decision": "DEC-511",
        "source_dispatch_preflight_version": (
            "fmp-annual-catalogue-2016-dispatch-action-preflight-v1"
        ),
        "source_dispatch_preflight_fingerprint_sha256": _validate_sha256(
            dispatch_preflight.get("preflight_fingerprint_sha256"),
            field="dispatch preflight fingerprint",
        ),
        "annual_segment_label": ANNUAL_SEGMENT_LABEL,
        "previous_annual_freeze_run_id": previous_run_id,
        "successful_2015_run_id": previous_run_id,
        "successful_2015_run_head_sha": _validate_commit(
            dispatch_preflight.get("successful_2015_run_head_sha"),
            field="successful 2015 run head",
        ),
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
        "dispatch_action_observed": True,
        "dispatch_action_preflight_consumed": True,
        "dispatch_authorization_consumed": True,
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
        "next_gate": "DETERMINISTIC_2016_RUNTIME_EVIDENCE_FREEZE",
    }
    review["review_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(review)
    )
    validate_2016_run_review(review)
    return review


def _validate_review_artifact(
    value: object,
    *,
    expected_name: str,
) -> tuple[int, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"DEC-512 review artifact malformed: {expected_name}")
    if value.get("name") != expected_name:
        raise ValueError(f"DEC-512 review artifact name mismatch: {expected_name}")
    artifact_id = _positive_int(
        value.get("id"),
        field=f"review artifact id {expected_name}",
    )
    size = _positive_int(
        value.get("size_in_bytes"),
        field=f"review artifact size {expected_name}",
    )
    del size
    digest = value.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ValueError(f"DEC-512 review artifact digest malformed: {expected_name}")
    digest_sha256 = _validate_sha256(
        digest.removeprefix("sha256:"),
        field=f"review artifact digest {expected_name}",
    )
    return artifact_id, digest_sha256


def validate_2016_run_review(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("review_fingerprint_sha256"),
        field="review fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("review_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-512 review fingerprint mismatch")

    exact = {
        "decision": "DEC-512",
        "version": "fmp-annual-catalogue-2016-run-review-v1",
        "dispatch_preflight_source_blob_sha": (
            EXPECTED_DISPATCH_PREFLIGHT_SOURCE_BLOB_SHA
        ),
        "segment_freeze_source_blob_sha": EXPECTED_SEGMENT_FREEZE_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "source_dispatch_preflight_decision": "DEC-511",
        "source_dispatch_preflight_version": (
            "fmp-annual-catalogue-2016-dispatch-action-preflight-v1"
        ),
        "run_number": EXPECTED_RUN_NUMBER,
        "run_attempt": EXPECTED_RUN_ATTEMPT,
        "run_status": "completed",
        "run_conclusion": "success",
        "annual_segment_label": ANNUAL_SEGMENT_LABEL,
        "annual_cell_count": EXPECTED_CELLS_PER_SEGMENT,
        "directional_record_count": EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT,
        "dispatch_action_observed": True,
        "dispatch_action_preflight_consumed": True,
        "dispatch_authorization_consumed": True,
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
        "next_gate": "DETERMINISTIC_2016_RUNTIME_EVIDENCE_FREEZE",
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-512 {field} mismatch")

    run_id = _positive_int(value.get("run_id"), field="run id")
    del run_id
    run_head = _validate_commit(value.get("run_head_sha"), field="run head")
    previous_run_id = _positive_int(
        value.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    if value.get("successful_2015_run_id") != previous_run_id:
        raise ValueError("DEC-512 predecessor run mismatch")
    _validate_commit(
        value.get("successful_2015_run_head_sha"),
        field="successful 2015 run head",
    )

    for field in (
        "source_dispatch_preflight_fingerprint_sha256",
        "freeze_artifact_zip_sha256",
        "freeze_evidence_canonical_sha256",
        "freeze_evidence_fingerprint",
    ):
        _validate_sha256(value.get(field), field=field)

    for field in (
        "evaluable_record_count",
        "zero_support_record_count",
        "total_support",
    ):
        item = value.get(field)
        if not isinstance(item, int) or isinstance(item, bool) or item < 0:
            raise ValueError(f"DEC-512 {field} must be a non-negative integer")

    preflight_job_id = _positive_int(
        value.get("preflight_job_id"),
        field="preflight job id",
    )
    freeze_job_id = _positive_int(
        value.get("freeze_job_id"),
        field="freeze job id",
    )
    cell_job_ids = value.get("cell_job_ids")
    if not isinstance(cell_job_ids, Mapping):
        raise ValueError("DEC-512 cell job ids malformed")
    expected_job_names = set(_expected_cell_job_names())
    if set(cell_job_ids) != expected_job_names:
        raise ValueError("DEC-512 cell job id inventory mismatch")
    job_ids = [preflight_job_id, freeze_job_id]
    for name in sorted(expected_job_names):
        job_ids.append(
            _positive_int(
                cell_job_ids.get(name),
                field=f"cell job id {name}",
            )
        )
    if len(set(job_ids)) != EXPECTED_JOB_COUNT:
        raise ValueError("DEC-512 job ids must be unique")

    preflight_name = (
        f"phase8a-annual-catalogue-preflight-{ANNUAL_SEGMENT_LABEL}-{run_head}"
    )
    freeze_name = (
        f"phase8a-annual-catalogue-freeze-{ANNUAL_SEGMENT_LABEL}-{run_head}"
    )
    artifact_ids: list[int] = []
    preflight_id, _ = _validate_review_artifact(
        value.get("preflight_artifact"),
        expected_name=preflight_name,
    )
    artifact_ids.append(preflight_id)
    freeze_id, freeze_digest = _validate_review_artifact(
        value.get("freeze_artifact"),
        expected_name=freeze_name,
    )
    artifact_ids.append(freeze_id)
    if freeze_digest != value.get("freeze_artifact_zip_sha256"):
        raise ValueError("DEC-512 freeze artifact ZIP digest mismatch")

    cell_artifacts = value.get("cell_artifacts")
    if not isinstance(cell_artifacts, Mapping):
        raise ValueError("DEC-512 cell artifact inventory malformed")
    expected_artifact_names = set(_expected_cell_artifact_names(run_head))
    if set(cell_artifacts) != expected_artifact_names:
        raise ValueError("DEC-512 cell artifact inventory mismatch")
    for name in sorted(expected_artifact_names):
        artifact_id, _ = _validate_review_artifact(
            cell_artifacts.get(name),
            expected_name=name,
        )
        artifact_ids.append(artifact_id)
    if len(artifact_ids) != EXPECTED_ARTIFACT_COUNT:
        raise ValueError("DEC-512 artifact count mismatch")
    if len(set(artifact_ids)) != EXPECTED_ARTIFACT_COUNT:
        raise ValueError("DEC-512 artifact ids must be unique")

    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_RUN_REVIEW_DECISION",
    "ANNUAL_CATALOGUE_2016_RUN_REVIEW_VERSION",
    "review_2016_run",
    "validate_2016_run_review",
    "validate_2016_run_review_sources",
]
