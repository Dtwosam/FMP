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


ANNUAL_CATALOGUE_2022_RUN384_EVIDENCE_REVIEW_DECISION = "DEC-601"
ANNUAL_CATALOGUE_2022_RUN384_EVIDENCE_REVIEW_VERSION = (
    "fmp-annual-catalogue-2022-run384-evidence-review-v1"
)

SEGMENT_EVIDENCE_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_segment_evidence.py"
)
EXPECTED_SEGMENT_EVIDENCE_SOURCE_BLOB_SHA = (
    "1b14279864f01a1284c5be31552eee9bb3a2220c"
)
DISPATCH_ACTION_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2022_dispatch_action_preflight.py"
)
EXPECTED_DISPATCH_ACTION_PREFLIGHT_SOURCE_BLOB_SHA = (
    "34a805b3ab9038e847097f51a3fcc1d5c1806a53"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)
INSTALLED_GATE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2022_runtime_authorization.py"
)
EXPECTED_INSTALLED_GATE_BLOB_SHA = (
    "ecb21dc7106e7bd43447f4135c3a696251a75e05"
)
INSTALLED_RUNTIME_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_INSTALLED_RUNTIME_BLOB_SHA = (
    "f2734c7ea32355b1024d1097812578b23fc4409d"
)

SOURCE_PREFLIGHT_WORKFLOW_RUN_ID = 37657193417
SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA = (
    "246a452bc146da3463d81aed2395294b3a53f58c"
)
SOURCE_PREFLIGHT_ARTIFACT_ID = 11500265123
SOURCE_PREFLIGHT_ARTIFACT_DIGEST = (
    "sha256:05b22b33b49c10e5650a3fe7862846ee8ca7f7be8d042f39952161254043135a"
)
SOURCE_PREFLIGHT_FINGERPRINT_SHA256 = (
    "c046f502b6e231cb506e5b8c6430e259983ac2eb93d1d632840185aae40897bf"
)

ANNUAL_SEGMENT_LABEL = "2022"
EXPECTED_RUN_NUMBER = 384
EXPECTED_RUN_ATTEMPT = 1
EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37531960014
EXPECTED_JOB_COUNT = 20
EXPECTED_ARTIFACT_COUNT = 20


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
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
        raise ValueError(f"DEC-601 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-601 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-601 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-601 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-601 {field} must be a positive integer")
    return value


def validate_2022_run384_evidence_review_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "segment_evidence_source_blob_sha": (
            root / SEGMENT_EVIDENCE_SOURCE_PATH,
            EXPECTED_SEGMENT_EVIDENCE_SOURCE_BLOB_SHA,
        ),
        "dispatch_action_preflight_source_blob_sha": (
            root / DISPATCH_ACTION_PREFLIGHT_SOURCE_PATH,
            EXPECTED_DISPATCH_ACTION_PREFLIGHT_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
        "installed_gate_blob_sha": (
            root / INSTALLED_GATE_PATH,
            EXPECTED_INSTALLED_GATE_BLOB_SHA,
        ),
        "installed_runtime_blob_sha": (
            root / INSTALLED_RUNTIME_PATH,
            EXPECTED_INSTALLED_RUNTIME_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-601 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-601 {field} mismatch")
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


def _validate_dispatch_receipt(
    receipt: Mapping[str, object],
    *,
    expected_head_sha: str,
    expected_run_id: int,
) -> dict[str, object]:
    exact = {
        "decision": "DEC-600",
        "stage": "ANNUAL_CATALOGUE_2022_RUN_384_DISPATCH_SUBMITTED",
        "source_preflight_decision": "DEC-599",
        "source_preflight_workflow_run_id": SOURCE_PREFLIGHT_WORKFLOW_RUN_ID,
        "source_preflight_workflow_head_sha": SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA,
        "source_preflight_artifact_id": SOURCE_PREFLIGHT_ARTIFACT_ID,
        "source_preflight_artifact_digest": SOURCE_PREFLIGHT_ARTIFACT_DIGEST,
        "source_preflight_fingerprint_sha256": (
            SOURCE_PREFLIGHT_FINGERPRINT_SHA256
        ),
        "dispatch_head_sha": expected_head_sha,
        "annual_segment_label": ANNUAL_SEGMENT_LABEL,
        "previous_annual_freeze_run_id": EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "run_id": expected_run_id,
        "run_number": EXPECTED_RUN_NUMBER,
        "run_attempt": EXPECTED_RUN_ATTEMPT,
        "run_head_sha": expected_head_sha,
        "dispatch_submitted": True,
        "result_claimed": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_385_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "protected_history_access_authorized": False,
        "cross_year_comparison_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": "REVIEW_2022_RUN_384_BEFORE_CROSS_YEAR_COMPARISON",
    }
    for field, expected in exact.items():
        if receipt.get(field) != expected:
            raise ValueError(f"DEC-601 dispatch receipt {field} mismatch")
    return {
        "source_dispatch_receipt_decision": "DEC-600",
        "previous_annual_freeze_run_id": EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "dispatch_receipt_bound": True,
    }


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
            raise ValueError(f"DEC-601 run {field} mismatch")
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
        raise ValueError("DEC-601 job inventory count mismatch")
    expected_names = {
        f"annual-preflight-{ANNUAL_SEGMENT_LABEL}",
        f"annual-freeze-{ANNUAL_SEGMENT_LABEL}",
        *_expected_cell_job_names(),
    }
    seen: dict[str, Mapping[str, object]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-601 job row malformed")
        name = raw.get("name")
        if not isinstance(name, str) or name not in expected_names:
            raise ValueError("DEC-601 unexpected job name")
        if name in seen:
            raise ValueError("DEC-601 duplicate job name")
        if raw.get("status") != "completed" or raw.get("conclusion") != "success":
            raise ValueError(f"DEC-601 job not successful: {name}")
        _positive_int(raw.get("id"), field=f"job id {name}")
        seen[name] = raw
    if set(seen) != expected_names:
        raise ValueError("DEC-601 job inventory mismatch")
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
        raise ValueError("DEC-601 artifact name mismatch")
    if raw.get("expired") is not False:
        raise ValueError(f"DEC-601 artifact expired: {expected_name}")
    digest = raw.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ValueError(f"DEC-601 artifact digest malformed: {expected_name}")
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
        raise ValueError("DEC-601 artifact inventory count mismatch")
    by_name: dict[str, Mapping[str, object]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-601 artifact row malformed")
        name = raw.get("name")
        if not isinstance(name, str) or name in by_name:
            raise ValueError("DEC-601 artifact name inventory malformed")
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
        raise ValueError("DEC-601 artifact inventory mismatch")

    return {
        "preflight_artifact": _artifact_row(
            by_name[preflight_name],
            expected_name=preflight_name,
        ),
        "freeze_artifact": _artifact_row(
            by_name[freeze_name],
            expected_name=freeze_name,
        ),
        "cell_artifacts": {
            name: _artifact_row(by_name[name], expected_name=name)
            for name in sorted(cell_names)
        },
    }


def review_2022_run384_evidence(
    *,
    repository_root: Path,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    freeze_evidence: Mapping[str, object],
    freeze_artifact_zip_sha256: str,
    dispatch_receipt: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2022_run384_evidence_review_sources(
        repository_root=Path(repository_root),
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    run_identity = _validate_run(run, expected_head_sha=expected_head_sha)
    receipt = _validate_dispatch_receipt(
        dispatch_receipt,
        expected_head_sha=expected_head_sha,
        expected_run_id=int(run_identity["run_id"]),
    )
    jobs = _validate_jobs(jobs_payload)
    artifacts = _validate_artifacts(
        artifacts_payload,
        expected_head_sha=expected_head_sha,
    )

    freeze_zip_sha256 = _validate_sha256(
        freeze_artifact_zip_sha256,
        field="freeze artifact ZIP SHA-256",
    )
    freeze_artifact = artifacts["freeze_artifact"]
    assert isinstance(freeze_artifact, Mapping)
    if freeze_artifact.get("digest") != f"sha256:{freeze_zip_sha256}":
        raise ValueError("DEC-601 freeze artifact ZIP digest mismatch")

    validate_annual_segment_freeze(freeze_evidence)
    if freeze_evidence.get("annual_segment_label") != ANNUAL_SEGMENT_LABEL:
        raise ValueError("DEC-601 freeze annual segment mismatch")
    if freeze_evidence.get("code_commit") != expected_head_sha:
        raise ValueError("DEC-601 freeze code commit mismatch")
    if freeze_evidence.get("annual_cell_count") != EXPECTED_CELLS_PER_SEGMENT:
        raise ValueError("DEC-601 freeze annual cell count mismatch")
    if (
        freeze_evidence.get("directional_record_count")
        != EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT
    ):
        raise ValueError("DEC-601 freeze directional record count mismatch")

    review: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2022_RUN384_EVIDENCE_REVIEW_DECISION,
        "version": ANNUAL_CATALOGUE_2022_RUN384_EVIDENCE_REVIEW_VERSION,
        **source,
        **run_identity,
        **receipt,
        **jobs,
        **artifacts,
        "stage": "ANNUAL_CATALOGUE_2022_RUN384_CONCRETE_RUNTIME_EVIDENCE_BOUND",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": ANNUAL_SEGMENT_LABEL,
        "freeze_artifact_zip_sha256": freeze_zip_sha256,
        "freeze_evidence_canonical_sha256": _sha256_bytes(
            _canonical_json(dict(freeze_evidence))
        ),
        "freeze_evidence_fingerprint": freeze_evidence.get(
            "evidence_fingerprint"
        ),
        "annual_cell_count": freeze_evidence.get("annual_cell_count"),
        "directional_record_count": freeze_evidence.get(
            "directional_record_count"
        ),
        "evaluable_record_count": freeze_evidence.get("evaluable_record_count"),
        "zero_support_record_count": freeze_evidence.get(
            "zero_support_record_count"
        ),
        "total_support": freeze_evidence.get("total_support"),
        "runtime_review_validated": True,
        "runtime_evidence_bound": True,
        "final_required_annual_segment_bound": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_385_or_later_authorized": False,
        "protected_history_access_authorized": False,
        "cross_year_comparison_authorized": False,
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
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_CROSS_YEAR_COMPARISON_PREFLIGHT",
    }
    review["binding_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(review)
    )
    validate_2022_run384_evidence_review(review)
    return review


def validate_2022_run384_evidence_review(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("binding_fingerprint_sha256"),
        field="binding fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("binding_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-601 binding fingerprint mismatch")

    exact = {
        "decision": "DEC-601",
        "version": "fmp-annual-catalogue-2022-run384-evidence-review-v1",
        "stage": "ANNUAL_CATALOGUE_2022_RUN384_CONCRETE_RUNTIME_EVIDENCE_BOUND",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2022",
        "run_number": 383,
        "run_attempt": 1,
        "run_status": "completed",
        "run_conclusion": "success",
        "source_dispatch_receipt_decision": "DEC-600",
        "dispatch_receipt_bound": True,
        "previous_annual_freeze_run_id": EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "annual_cell_count": 18,
        "directional_record_count": 89460,
        "runtime_review_validated": True,
        "runtime_evidence_bound": True,
        "final_required_annual_segment_bound": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_385_or_later_authorized": False,
        "protected_history_access_authorized": False,
        "cross_year_comparison_authorized": False,
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
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_CROSS_YEAR_COMPARISON_PREFLIGHT",
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-601 {field} mismatch")

    _positive_int(value.get("run_id"), field="run id")
    _validate_commit(value.get("run_head_sha"), field="run head")
    for field in (
        "freeze_artifact_zip_sha256",
        "freeze_evidence_canonical_sha256",
        "freeze_evidence_fingerprint",
    ):
        _validate_sha256(value.get(field), field=field)

    cell_job_ids = value.get("cell_job_ids")
    if not isinstance(cell_job_ids, Mapping) or len(cell_job_ids) != 18:
        raise ValueError("DEC-601 cell job inventory mismatch")
    cell_artifacts = value.get("cell_artifacts")
    if not isinstance(cell_artifacts, Mapping) or len(cell_artifacts) != 18:
        raise ValueError("DEC-601 cell artifact inventory mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2022_RUN384_EVIDENCE_REVIEW_DECISION",
    "ANNUAL_CATALOGUE_2022_RUN384_EVIDENCE_REVIEW_VERSION",
    "review_2022_run384_evidence",
    "validate_2022_run384_evidence_review",
    "validate_2022_run384_evidence_review_sources",
]
