from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2015_replacement_run_freeze import (
    ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_DECISION,
    ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_VERSION,
    validate_2015_replacement_run_freeze,
)


ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_DECISION = "DEC-502"
ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_VERSION = (
    "fmp-annual-catalogue-2015-runtime-evidence-binding-v1"
)

RUN_FREEZE_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_replacement_run_freeze.py"
)
EXPECTED_RUN_FREEZE_SOURCE_BLOB_SHA = (
    "8e2a6ab27b4941e3ee12b5463247999200d33e69"
)
RUN_REVIEW_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_replacement_run_review.py"
)
EXPECTED_RUN_REVIEW_SOURCE_BLOB_SHA = (
    "883f82c85d2738c46284d3675278dc061f4ca07c"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "f7e65ee95f472918e390bceedd7cf2f38bbf7e92"
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


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-502 {field} must be a positive integer")
    return value


def _sha256_hex(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"DEC-502 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-502 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_artifact(value: object, *, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"DEC-502 {field} must be an artifact object")
    _positive_int(value.get("id"), field=f"{field} id")
    name = value.get("name")
    if not isinstance(name, str) or not name:
        raise ValueError(f"DEC-502 {field} name is malformed")
    digest = value.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ValueError(f"DEC-502 {field} digest is malformed")
    _sha256_hex(digest.removeprefix("sha256:"), field=f"{field} digest")
    _positive_int(value.get("size_in_bytes"), field=f"{field} size")
    return value


def validate_2015_runtime_evidence_binding_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "run_freeze_source_blob_sha": (
            root / RUN_FREEZE_SOURCE_PATH,
            EXPECTED_RUN_FREEZE_SOURCE_BLOB_SHA,
        ),
        "run_review_source_blob_sha": (
            root / RUN_REVIEW_SOURCE_PATH,
            EXPECTED_RUN_REVIEW_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-502 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-502 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_DECISION != "DEC-501":
        raise ValueError("DEC-502 source freeze decision drift")
    if (
        ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_VERSION
        != "fmp-annual-catalogue-2015-replacement-run-freeze-v1"
    ):
        raise ValueError("DEC-502 source freeze version drift")

    return actual


def bind_2015_runtime_evidence(
    freeze: Mapping[str, object],
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_2015_runtime_evidence_binding_sources(
        repository_root=Path(repository_root),
    )
    validate_2015_replacement_run_freeze(freeze)

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_DECISION,
        "version": ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_VERSION,
        **source,
        "source_freeze_decision": "DEC-501",
        "source_freeze_version": (
            "fmp-annual-catalogue-2015-replacement-run-freeze-v1"
        ),
        "stage": "ANNUAL_CATALOGUE_2015_CONCRETE_RUNTIME_EVIDENCE_BOUND",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2015",
        "run_id": freeze.get("run_id"),
        "run_number": freeze.get("run_number"),
        "run_attempt": freeze.get("run_attempt"),
        "run_status": freeze.get("run_status"),
        "run_conclusion": freeze.get("run_conclusion"),
        "run_head_sha": freeze.get("expected_head_sha"),
        "preflight_job_id": freeze.get("preflight_job_id"),
        "freeze_job_id": freeze.get("freeze_job_id"),
        "cell_job_ids": freeze.get("cell_job_ids"),
        "preflight_artifact": freeze.get("preflight_artifact"),
        "freeze_artifact": freeze.get("freeze_artifact"),
        "cell_artifacts": freeze.get("cell_artifacts"),
        "freeze_artifact_zip_sha256": freeze.get(
            "freeze_artifact_zip_sha256"
        ),
        "freeze_evidence_canonical_sha256": freeze.get(
            "freeze_evidence_canonical_sha256"
        ),
        "freeze_evidence_fingerprint": freeze.get(
            "freeze_evidence_fingerprint"
        ),
        "annual_cell_count": freeze.get("annual_cell_count"),
        "directional_record_count": freeze.get("directional_record_count"),
        "evaluable_record_count": freeze.get("evaluable_record_count"),
        "zero_support_record_count": freeze.get(
            "zero_support_record_count"
        ),
        "total_support": freeze.get("total_support"),
        "review_fingerprint_sha256": freeze.get(
            "review_fingerprint_sha256"
        ),
        "runtime_freeze_fingerprint_sha256": freeze.get(
            "freeze_fingerprint_sha256"
        ),
        "replacement_authorization_consumed": True,
        "runtime_review_validated": True,
        "runtime_evidence_frozen": True,
        "runtime_evidence_bound": True,
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
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_PREFLIGHT"
        ),
    }
    value["binding_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2015_runtime_evidence_binding(value)
    return value


def validate_2015_runtime_evidence_binding(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = value.get("binding_fingerprint_sha256")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("DEC-502 binding fingerprint malformed")
    try:
        int(fingerprint, 16)
    except ValueError as exc:
        raise ValueError("DEC-502 binding fingerprint must be hexadecimal") from exc

    unsigned = dict(value)
    unsigned.pop("binding_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-502 binding fingerprint mismatch")

    if value.get("decision") != "DEC-502":
        raise ValueError("DEC-502 decision mismatch")
    if value.get("source_freeze_decision") != "DEC-501":
        raise ValueError("DEC-502 source freeze decision mismatch")
    if value.get("annual_segment_label") != "2015":
        raise ValueError("DEC-502 annual segment mismatch")
    if value.get("run_number") != 2:
        raise ValueError("DEC-502 run number mismatch")
    if value.get("run_attempt") != 1:
        raise ValueError("DEC-502 run attempt mismatch")
    if value.get("run_status") != "completed":
        raise ValueError("DEC-502 run status mismatch")
    if value.get("run_conclusion") != "success":
        raise ValueError("DEC-502 run conclusion mismatch")
    if value.get("annual_cell_count") != 18:
        raise ValueError("DEC-502 annual cell count mismatch")
    if value.get("directional_record_count") != 89460:
        raise ValueError("DEC-502 directional record count mismatch")

    _positive_int(value.get("run_id"), field="run id")
    _positive_int(value.get("preflight_job_id"), field="preflight job id")
    _positive_int(value.get("freeze_job_id"), field="freeze job id")

    cell_job_ids = value.get("cell_job_ids")
    if not isinstance(cell_job_ids, Mapping) or len(cell_job_ids) != 18:
        raise ValueError("DEC-502 cell job inventory mismatch")
    seen_job_ids: set[int] = set()
    for name, raw_id in cell_job_ids.items():
        if not isinstance(name, str) or not name:
            raise ValueError("DEC-502 cell job name malformed")
        job_id = _positive_int(raw_id, field=f"cell job id {name}")
        if job_id in seen_job_ids:
            raise ValueError("DEC-502 duplicate cell job id")
        seen_job_ids.add(job_id)

    preflight_artifact = _validate_artifact(
        value.get("preflight_artifact"),
        field="preflight artifact",
    )
    freeze_artifact = _validate_artifact(
        value.get("freeze_artifact"),
        field="freeze artifact",
    )
    cell_artifacts = value.get("cell_artifacts")
    if not isinstance(cell_artifacts, Mapping) or len(cell_artifacts) != 18:
        raise ValueError("DEC-502 cell artifact inventory mismatch")
    seen_artifact_ids: set[int] = set()
    for name, artifact in cell_artifacts.items():
        if not isinstance(name, str) or not name:
            raise ValueError("DEC-502 cell artifact name malformed")
        row = _validate_artifact(artifact, field=f"cell artifact {name}")
        artifact_id = int(row["id"])
        if artifact_id in seen_artifact_ids:
            raise ValueError("DEC-502 duplicate cell artifact id")
        seen_artifact_ids.add(artifact_id)

    freeze_zip_sha256 = _sha256_hex(
        value.get("freeze_artifact_zip_sha256"),
        field="freeze artifact ZIP SHA-256",
    )
    if freeze_artifact.get("digest") != f"sha256:{freeze_zip_sha256}":
        raise ValueError("DEC-502 freeze artifact digest mismatch")

    for field in (
        "freeze_evidence_canonical_sha256",
        "freeze_evidence_fingerprint",
        "review_fingerprint_sha256",
        "runtime_freeze_fingerprint_sha256",
    ):
        _sha256_hex(value.get(field), field=field)

    if preflight_artifact.get("id") == freeze_artifact.get("id"):
        raise ValueError("DEC-502 preflight/freeze artifact ids must differ")

    if value.get("replacement_authorization_consumed") is not True:
        raise ValueError("DEC-502 replacement authorization must be consumed")
    if value.get("runtime_review_validated") is not True:
        raise ValueError("DEC-502 runtime review must be validated")
    if value.get("runtime_evidence_frozen") is not True:
        raise ValueError("DEC-502 runtime evidence must be frozen")
    if value.get("runtime_evidence_bound") is not True:
        raise ValueError("DEC-502 runtime evidence must be bound")

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
            raise ValueError(f"DEC-502 {field} must remain false")

    if (
        value.get("next_gate")
        != "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_PREFLIGHT"
    ):
        raise ValueError("DEC-502 next gate mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_DECISION",
    "ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_VERSION",
    "bind_2015_runtime_evidence",
    "validate_2015_runtime_evidence_binding",
    "validate_2015_runtime_evidence_binding_sources",
]
