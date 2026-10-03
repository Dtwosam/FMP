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


ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_CONTRACT_DECISION = "DEC-502"
ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_CONTRACT_VERSION = (
    "fmp-annual-catalogue-2015-runtime-evidence-binding-contract-v1"
)

RUN_FREEZE_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_replacement_run_freeze.py"
)
EXPECTED_RUN_FREEZE_SOURCE_BLOB_SHA = (
    "8e2a6ab27b4941e3ee12b5463247999200d33e69"
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


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_2015_runtime_evidence_binding_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = root / RUN_FREEZE_SOURCE_PATH
    if not path.is_file():
        raise ValueError(f"DEC-502 source file missing: {path}")
    sha = _git_blob_sha(path)
    if sha != EXPECTED_RUN_FREEZE_SOURCE_BLOB_SHA:
        raise ValueError("DEC-502 run-freeze source blob mismatch")
    if ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_DECISION != "DEC-501":
        raise ValueError("DEC-502 source freeze decision drift")
    if (
        ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_FREEZE_VERSION
        != "fmp-annual-catalogue-2015-replacement-run-freeze-v1"
    ):
        raise ValueError("DEC-502 source freeze version drift")
    return {"run_freeze_source_blob_sha": sha}


def bind_2015_runtime_evidence(
    freeze: Mapping[str, object],
    *,
    repository_root: Path,
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2015_runtime_evidence_binding_contract_sources(
        repository_root=Path(repository_root),
    )
    validate_2015_replacement_run_freeze(freeze)
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if freeze.get("expected_head_sha") != expected_head_sha:
        raise ValueError("DEC-502 freeze head mismatch")

    _positive_int(freeze.get("run_id"), field="run_id")
    _positive_int(freeze.get("preflight_job_id"), field="preflight_job_id")
    _positive_int(freeze.get("freeze_job_id"), field="freeze_job_id")

    cell_job_ids = freeze.get("cell_job_ids")
    if not isinstance(cell_job_ids, Mapping) or len(cell_job_ids) != 18:
        raise ValueError("DEC-502 cell job inventory mismatch")
    for name, raw in cell_job_ids.items():
        if not isinstance(name, str):
            raise ValueError("DEC-502 cell job name malformed")
        _positive_int(raw, field=f"cell job id {name}")

    for field in ("preflight_artifact", "freeze_artifact"):
        artifact = freeze.get(field)
        if not isinstance(artifact, Mapping):
            raise ValueError(f"DEC-502 {field} malformed")
        _positive_int(artifact.get("id"), field=f"{field} id")
        digest = artifact.get("digest")
        if not isinstance(digest, str) or not digest.startswith("sha256:"):
            raise ValueError(f"DEC-502 {field} digest malformed")
        _validate_sha256(
            digest.removeprefix("sha256:"),
            field=f"{field} digest",
        )

    cell_artifacts = freeze.get("cell_artifacts")
    if not isinstance(cell_artifacts, Mapping) or len(cell_artifacts) != 18:
        raise ValueError("DEC-502 cell artifact inventory mismatch")
    for name, raw in cell_artifacts.items():
        if not isinstance(name, str) or not isinstance(raw, Mapping):
            raise ValueError("DEC-502 cell artifact row malformed")
        _positive_int(raw.get("id"), field=f"cell artifact id {name}")
        digest = raw.get("digest")
        if not isinstance(digest, str) or not digest.startswith("sha256:"):
            raise ValueError(f"DEC-502 cell artifact digest malformed: {name}")
        _validate_sha256(
            digest.removeprefix("sha256:"),
            field=f"cell artifact digest {name}",
        )

    for field in (
        "freeze_artifact_zip_sha256",
        "freeze_evidence_canonical_sha256",
        "freeze_evidence_fingerprint",
        "review_fingerprint_sha256",
        "freeze_fingerprint_sha256",
    ):
        _validate_sha256(freeze.get(field), field=field)

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_CONTRACT_DECISION,
        "version": ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_CONTRACT_VERSION,
        **source,
        "source_freeze_decision": "DEC-501",
        "source_freeze_version": (
            "fmp-annual-catalogue-2015-replacement-run-freeze-v1"
        ),
        "stage": "ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BOUND",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2015",
        "run_id": freeze.get("run_id"),
        "run_number": freeze.get("run_number"),
        "run_attempt": freeze.get("run_attempt"),
        "run_conclusion": freeze.get("run_conclusion"),
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
            "READ_ONLY_2016_ANNUAL_PATTERN_CATALOGUE_EXECUTION_PREFLIGHT"
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
    if value.get("run_conclusion") != "success":
        raise ValueError("DEC-502 run conclusion mismatch")
    if value.get("annual_cell_count") != 18:
        raise ValueError("DEC-502 annual cell count mismatch")
    if value.get("directional_record_count") != 89460:
        raise ValueError("DEC-502 directional record count mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    for field in (
        "replacement_authorization_consumed",
        "runtime_review_validated",
        "runtime_evidence_frozen",
        "runtime_evidence_bound",
    ):
        if value.get(field) is not True:
            raise ValueError(f"DEC-502 {field} must be true")
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
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_CONTRACT_DECISION",
    "ANNUAL_CATALOGUE_2015_RUNTIME_EVIDENCE_BINDING_CONTRACT_VERSION",
    "bind_2015_runtime_evidence",
    "validate_2015_runtime_evidence_binding",
    "validate_2015_runtime_evidence_binding_contract_sources",
]
