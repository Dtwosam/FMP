from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

from . import market_learning_adapter as _pre_cell
from . import run_contract as _pre_run
from .exp062_adapter_proof_result_decision import (
    EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION,
    EXP062_ADAPTER_PROOF_RESULT_FREEZE_VERSION,
)
from .exp062_nonfinite_feature_adapter import (
    EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION,
    EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION,
)
from .pattern_miner import InMemoryDiscoveryResult
from .pattern_protocol import (
    EXPERIMENT_ID as EXP061_EXPERIMENT_ID,
    protocol_fingerprint as exp061_protocol_fingerprint,
)


EXP062_RUN_EVIDENCE_DECISION = "DEC-298"
EXP062_RUN_CONTRACT_VERSION = "fmp-exp062-run-contract-v1"
EXP062_EXPERIMENT_ID = "EXP-20260927-062"

EXP062_CELL_EVIDENCE_VERSION = 1
EXP062_CELL_EVIDENCE_PROTOCOL = "fmp-exp062-cell-evidence-v1"
EXP062_AGGREGATE_EVIDENCE_VERSION = 1
EXP062_AGGREGATE_EVIDENCE_PROTOCOL = "fmp-exp062-aggregate-evidence-v1"

WORKFLOW_NAME = "phase8a-exp062-discovery"
WORKFLOW_PATH = ".github/workflows/phase8a-exp062-discovery.yml"
WORKFLOW_EVENT = "workflow_dispatch"
WORKFLOW_BRANCH = "main"
WORKFLOW_RUN_ATTEMPT = 1

PREFLIGHT_JOB_NAME = "exp062-preflight"
AGGREGATE_JOB_NAME = "exp062-aggregate"

DEC297_PROOF_FREEZE_BLOB_SHA = "18b7dde7eadf0f051a09fda04e648650bb270eb7"
DEC293_REPAIRED_ADAPTER_BLOB_SHA = "491ba8c92cb6e6e4c715bfb1ecb934b6949e1596"
EXP061_CELL_ADAPTER_BLOB_SHA = "978a33554fad7e9d78b002778c4896be0af3333a"
EXP061_MINER_BLOB_SHA = "495a67699eb5014e52129f0238a2737049fe38e6"
EXP061_LOADER_BLOB_SHA = "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
EXP061_RUN_CONTRACT_BLOB_SHA = "260eb6930673427266463517546969635188b143"
EXP061_PROTOCOL_BLOB_SHA = "63b3f0121d6a50eb9e8e62ab666d70eb91791621"

WORKFLOW_SOURCE_AUTHORIZED = False
WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
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

EXPECTED_CELLS = tuple(_pre_run.EXPECTED_CELLS)
EXPECTED_CELL_COUNT = _pre_run.EXPECTED_CELL_COUNT
EXPECTED_JOB_COUNT = _pre_run.EXPECTED_JOB_COUNT
EXPECTED_ARTIFACT_COUNT = _pre_run.EXPECTED_ARTIFACT_COUNT


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate_sha256(value: object, *, field: str) -> str:
    return _pre_run._validate_sha256(value, field=field)


def _validate_commit(value: object, *, field: str = "code_commit") -> str:
    return _pre_run._validate_commit(value, field=field)


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def exp062_protocol_fingerprint() -> str:
    return _sha256_bytes(
        _canonical_json(
            {
                "experiment_id": EXP062_EXPERIMENT_ID,
                "semantic_predecessor_experiment_id": EXP061_EXPERIMENT_ID,
                "semantic_predecessor_protocol_fingerprint": (
                    exp061_protocol_fingerprint()
                ),
                "repair_decision": (
                    EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION
                ),
                "repair_version": (
                    EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION
                ),
                "repair_proof_decision": (
                    EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION
                ),
                "repair_proof_version": (
                    EXP062_ADAPTER_PROOF_RESULT_FREEZE_VERSION
                ),
                "research_semantics_changed": False,
            }
        )
    )


def validate_exp062_run_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec297_verified_repair_proof": (
            root / "src/fmp/discovery/exp062_adapter_proof_result_decision.py",
            DEC297_PROOF_FREEZE_BLOB_SHA,
        ),
        "dec293_repaired_adapter": (
            root / "src/fmp/discovery/exp062_nonfinite_feature_adapter.py",
            DEC293_REPAIRED_ADAPTER_BLOB_SHA,
        ),
        "exp061_cell_adapter": (
            root / "src/fmp/discovery/market_learning_adapter.py",
            EXP061_CELL_ADAPTER_BLOB_SHA,
        ),
        "exp061_miner": (
            root / "src/fmp/discovery/pattern_miner.py",
            EXP061_MINER_BLOB_SHA,
        ),
        "exp061_range_limited_loader": (
            root / "src/fmp/discovery/range_limited_loader.py",
            EXP061_LOADER_BLOB_SHA,
        ),
        "exp061_run_contract": (
            root / "src/fmp/discovery/run_contract.py",
            EXP061_RUN_CONTRACT_BLOB_SHA,
        ),
        "exp061_protocol": (
            root / "src/fmp/discovery/pattern_protocol.py",
            EXP061_PROTOCOL_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-298 source dependency: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(
                f"DEC-298 {label} Git blob mismatch: {sha} != {expected_sha}"
            )
        actual[label] = sha

    return {
        "decision": EXP062_RUN_EVIDENCE_DECISION,
        "contract_version": EXP062_RUN_CONTRACT_VERSION,
        "experiment_id": EXP062_EXPERIMENT_ID,
        "protocol_fingerprint": exp062_protocol_fingerprint(),
        "source_blobs": actual,
        "workflow_source_authorized": False,
        "workflow_dispatch_authorized": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "trading_authorized": False,
    }


def expected_cell_job_name(
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> str:
    identity = (symbol, timeframe, horizon_minutes)
    if identity not in EXPECTED_CELLS:
        raise ValueError("unsupported DEC-298 cell")
    return f"exp062-cell-{symbol}-{timeframe}-{horizon_minutes}m"


def expected_cell_artifact_name(
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    *,
    code_commit: str,
) -> str:
    code_commit = _validate_commit(code_commit)
    expected_cell_job_name(symbol, timeframe, horizon_minutes)
    return (
        f"phase8a-exp062-cell-{symbol}-{timeframe}-"
        f"{horizon_minutes}m-{code_commit}"
    )


def expected_preflight_artifact_name(*, code_commit: str) -> str:
    code_commit = _validate_commit(code_commit)
    return f"phase8a-exp062-preflight-{code_commit}"


def expected_aggregate_artifact_name(*, code_commit: str) -> str:
    code_commit = _validate_commit(code_commit)
    return f"phase8a-exp062-aggregate-{code_commit}"


def expected_job_names() -> tuple[str, ...]:
    return (
        PREFLIGHT_JOB_NAME,
        *(
            expected_cell_job_name(symbol, timeframe, horizon)
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ),
        AGGREGATE_JOB_NAME,
    )


def expected_artifact_names(*, code_commit: str) -> tuple[str, ...]:
    code_commit = _validate_commit(code_commit)
    return (
        expected_preflight_artifact_name(code_commit=code_commit),
        *(
            expected_cell_artifact_name(
                symbol,
                timeframe,
                horizon,
                code_commit=code_commit,
            )
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ),
        expected_aggregate_artifact_name(code_commit=code_commit),
    )


def run_contract_payload(*, code_commit: str) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    jobs = expected_job_names()
    artifacts = expected_artifact_names(code_commit=code_commit)
    if len(jobs) != EXPECTED_JOB_COUNT or len(set(jobs)) != EXPECTED_JOB_COUNT:
        raise ValueError("DEC-298 job inventory drift")
    if (
        len(artifacts) != EXPECTED_ARTIFACT_COUNT
        or len(set(artifacts)) != EXPECTED_ARTIFACT_COUNT
    ):
        raise ValueError("DEC-298 artifact inventory drift")

    return {
        "decision": EXP062_RUN_EVIDENCE_DECISION,
        "contract_version": EXP062_RUN_CONTRACT_VERSION,
        "experiment_id": EXP062_EXPERIMENT_ID,
        "protocol_fingerprint": exp062_protocol_fingerprint(),
        "semantic_predecessor_experiment_id": EXP061_EXPERIMENT_ID,
        "semantic_predecessor_protocol_fingerprint": (
            exp061_protocol_fingerprint()
        ),
        "repair_decision": EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION,
        "repair_version": EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION,
        "repair_proof_decision": EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION,
        "repair_proof_version": EXP062_ADAPTER_PROOF_RESULT_FREEZE_VERSION,
        "code_commit": code_commit,
        "workflow": {
            "name": WORKFLOW_NAME,
            "path": WORKFLOW_PATH,
            "event": WORKFLOW_EVENT,
            "branch": WORKFLOW_BRANCH,
            "run_attempt": WORKFLOW_RUN_ATTEMPT,
        },
        "expected_job_names": list(jobs),
        "expected_artifact_names": list(artifacts),
        "cells": [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "horizon_minutes": horizon,
                "job_name": expected_cell_job_name(
                    symbol,
                    timeframe,
                    horizon,
                ),
                "artifact_name": expected_cell_artifact_name(
                    symbol,
                    timeframe,
                    horizon,
                    code_commit=code_commit,
                ),
            }
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ],
        "success_shape": {
            "job_count": EXPECTED_JOB_COUNT,
            "artifact_count": EXPECTED_ARTIFACT_COUNT,
            "all_jobs_success": True,
            "all_artifacts_non_expired": True,
            "aggregate_evidence_required": True,
            "result_review_required": True,
        },
        "non_success_shape": {
            "slot_consumed_if_later_authorized": True,
            "rerun_authorized": False,
            "retry_authorized": False,
            "replacement_run_authorized": False,
            "partial_expected_cell_evidence_may_be_preserved": True,
        },
        "authorizations": {
            "workflow_source_authorized": False,
            "workflow_dispatch_authorized": False,
            "historical_discovery_execution_authorized": False,
            "discovery_result_authorized": False,
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
        },
    }


def compile_cell_evidence(
    result: InMemoryDiscoveryResult,
    *,
    code_commit: str,
    processed_manifest_sha256: str,
    feature_manifest_sha256: str,
    outcome_manifest_sha256: str,
    feature_evidence_fingerprint: str,
    outcome_evidence_fingerprint: str,
) -> dict[str, object]:
    predecessor = _pre_cell.compile_cell_evidence(
        result,
        code_commit=code_commit,
        processed_manifest_sha256=processed_manifest_sha256,
        feature_manifest_sha256=feature_manifest_sha256,
        outcome_manifest_sha256=outcome_manifest_sha256,
        feature_evidence_fingerprint=feature_evidence_fingerprint,
        outcome_evidence_fingerprint=outcome_evidence_fingerprint,
    )
    predecessor_fingerprint = str(predecessor["evidence_fingerprint"])

    value = dict(predecessor)
    value.pop("evidence_fingerprint", None)
    value["evidence_version"] = EXP062_CELL_EVIDENCE_VERSION
    value["evidence_protocol"] = EXP062_CELL_EVIDENCE_PROTOCOL
    value["experiment_id"] = EXP062_EXPERIMENT_ID
    value["protocol_fingerprint"] = exp062_protocol_fingerprint()
    value["repair_decision"] = EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION
    value["repair_version"] = EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION
    value["repair_proof_decision"] = (
        EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION
    )
    value["repair_proof_version"] = (
        EXP062_ADAPTER_PROOF_RESULT_FREEZE_VERSION
    )
    value["semantic_predecessor_experiment_id"] = EXP061_EXPERIMENT_ID
    value["semantic_predecessor_protocol_fingerprint"] = (
        exp061_protocol_fingerprint()
    )
    value["semantic_predecessor_evidence_fingerprint"] = (
        predecessor_fingerprint
    )
    value["nonfinite_to_null_repair_applied"] = True
    value["evidence_fingerprint"] = _sha256_bytes(_canonical_json(value))
    return value


def _reconstruct_predecessor_cell(
    value: Mapping[str, object],
) -> dict[str, object]:
    predecessor = dict(value)
    predecessor.pop("evidence_fingerprint", None)
    stored_predecessor = predecessor.pop(
        "semantic_predecessor_evidence_fingerprint",
        None,
    )
    for field in (
        "repair_decision",
        "repair_version",
        "repair_proof_decision",
        "repair_proof_version",
        "semantic_predecessor_experiment_id",
        "semantic_predecessor_protocol_fingerprint",
        "nonfinite_to_null_repair_applied",
    ):
        predecessor.pop(field, None)
    predecessor["evidence_version"] = _pre_cell.EXP061_CELL_EVIDENCE_VERSION
    predecessor["evidence_protocol"] = _pre_cell.EXP061_CELL_EVIDENCE_PROTOCOL
    predecessor["experiment_id"] = EXP061_EXPERIMENT_ID
    predecessor["protocol_fingerprint"] = exp061_protocol_fingerprint()
    predecessor["evidence_fingerprint"] = _sha256_bytes(
        _canonical_json(predecessor)
    )
    if predecessor["evidence_fingerprint"] != stored_predecessor:
        raise ValueError(
            "DEC-298 semantic predecessor cell fingerprint mismatch"
        )
    _pre_cell.validate_cell_evidence(predecessor)
    return predecessor


def validate_cell_evidence(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="DEC-298 cell evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-298 cell evidence fingerprint mismatch")
    expected = {
        "evidence_version": EXP062_CELL_EVIDENCE_VERSION,
        "evidence_protocol": EXP062_CELL_EVIDENCE_PROTOCOL,
        "experiment_id": EXP062_EXPERIMENT_ID,
        "protocol_fingerprint": exp062_protocol_fingerprint(),
        "repair_decision": EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION,
        "repair_version": EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION,
        "repair_proof_decision": EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION,
        "repair_proof_version": EXP062_ADAPTER_PROOF_RESULT_FREEZE_VERSION,
        "semantic_predecessor_experiment_id": EXP061_EXPERIMENT_ID,
        "semantic_predecessor_protocol_fingerprint": (
            exp061_protocol_fingerprint()
        ),
        "nonfinite_to_null_repair_applied": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-298 cell evidence {field} mismatch")
    _validate_sha256(
        value.get("semantic_predecessor_evidence_fingerprint"),
        field="DEC-298 semantic predecessor cell fingerprint",
    )
    _reconstruct_predecessor_cell(value)
    return value


def _cell_identity(
    value: Mapping[str, object],
) -> tuple[str, str, int]:
    raw = value.get("cell")
    if not isinstance(raw, Mapping):
        raise ValueError("DEC-298 aggregate cell evidence missing identity")
    identity = (
        raw.get("symbol"),
        raw.get("timeframe"),
        raw.get("horizon_minutes"),
    )
    if identity not in EXPECTED_CELLS:
        raise ValueError(f"DEC-298 unexpected cell identity: {identity!r}")
    return str(identity[0]), str(identity[1]), int(identity[2])


def compile_aggregate_evidence(
    cell_evidence: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError(
            f"DEC-298 aggregate requires exactly {EXPECTED_CELL_COUNT} cells"
        )

    predecessors: list[dict[str, object]] = []
    outer_fingerprints: dict[tuple[str, str, int], str] = {}
    seen: set[tuple[str, str, int]] = set()
    for raw in cell_evidence:
        validated = validate_cell_evidence(raw)
        if validated.get("code_commit") != code_commit:
            raise ValueError("DEC-298 aggregate cell code commit mismatch")
        identity = _cell_identity(validated)
        if identity in seen:
            raise ValueError(f"DEC-298 duplicate cell: {identity!r}")
        seen.add(identity)
        outer_fingerprints[identity] = _validate_sha256(
            validated.get("evidence_fingerprint"),
            field="DEC-298 outer cell fingerprint",
        )
        predecessors.append(_reconstruct_predecessor_cell(validated))

    if set(seen) != set(EXPECTED_CELLS):
        raise ValueError("DEC-298 aggregate cell inventory mismatch")

    predecessor = _pre_run.compile_aggregate_evidence(
        predecessors,
        code_commit=code_commit,
    )
    predecessor_fingerprint = str(predecessor["evidence_fingerprint"])

    value = dict(predecessor)
    value.pop("evidence_fingerprint", None)
    value["evidence_version"] = EXP062_AGGREGATE_EVIDENCE_VERSION
    value["evidence_protocol"] = EXP062_AGGREGATE_EVIDENCE_PROTOCOL
    value["experiment_id"] = EXP062_EXPERIMENT_ID
    value["run_contract_version"] = EXP062_RUN_CONTRACT_VERSION
    value["protocol_fingerprint"] = exp062_protocol_fingerprint()
    value["repair_decision"] = EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION
    value["repair_version"] = EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION
    value["repair_proof_decision"] = EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION
    value["repair_proof_version"] = EXP062_ADAPTER_PROOF_RESULT_FREEZE_VERSION
    value["semantic_predecessor_experiment_id"] = EXP061_EXPERIMENT_ID
    value["semantic_predecessor_protocol_fingerprint"] = (
        exp061_protocol_fingerprint()
    )
    value["semantic_predecessor_aggregate_evidence_fingerprint"] = (
        predecessor_fingerprint
    )
    value["nonfinite_to_null_repair_applied"] = True
    value["exp062_cell_evidence_fingerprints"] = [
        {
            "symbol": symbol,
            "timeframe": timeframe,
            "horizon_minutes": horizon,
            "evidence_fingerprint": outer_fingerprints[
                (symbol, timeframe, horizon)
            ],
        }
        for symbol, timeframe, horizon in sorted(EXPECTED_CELLS)
    ]
    value["evidence_fingerprint"] = _sha256_bytes(_canonical_json(value))
    return value


def _reconstruct_predecessor_aggregate(
    value: Mapping[str, object],
) -> dict[str, object]:
    predecessor = dict(value)
    predecessor.pop("evidence_fingerprint", None)
    stored_predecessor = predecessor.pop(
        "semantic_predecessor_aggregate_evidence_fingerprint",
        None,
    )
    for field in (
        "repair_decision",
        "repair_version",
        "repair_proof_decision",
        "repair_proof_version",
        "semantic_predecessor_experiment_id",
        "semantic_predecessor_protocol_fingerprint",
        "nonfinite_to_null_repair_applied",
        "exp062_cell_evidence_fingerprints",
    ):
        predecessor.pop(field, None)
    predecessor["evidence_version"] = _pre_run.EXP061_AGGREGATE_EVIDENCE_VERSION
    predecessor["evidence_protocol"] = _pre_run.EXP061_AGGREGATE_EVIDENCE_PROTOCOL
    predecessor["experiment_id"] = EXP061_EXPERIMENT_ID
    predecessor["run_contract_version"] = _pre_run.EXP061_RUN_CONTRACT_VERSION
    predecessor["protocol_fingerprint"] = exp061_protocol_fingerprint()
    predecessor["evidence_fingerprint"] = _sha256_bytes(
        _canonical_json(predecessor)
    )
    if predecessor["evidence_fingerprint"] != stored_predecessor:
        raise ValueError(
            "DEC-298 semantic predecessor aggregate fingerprint mismatch"
        )
    _pre_run.validate_aggregate_evidence(predecessor)
    return predecessor


def validate_aggregate_evidence(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="DEC-298 aggregate evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-298 aggregate evidence fingerprint mismatch")
    expected = {
        "evidence_version": EXP062_AGGREGATE_EVIDENCE_VERSION,
        "evidence_protocol": EXP062_AGGREGATE_EVIDENCE_PROTOCOL,
        "experiment_id": EXP062_EXPERIMENT_ID,
        "run_contract_version": EXP062_RUN_CONTRACT_VERSION,
        "protocol_fingerprint": exp062_protocol_fingerprint(),
        "repair_decision": EXP062_NONFINITE_FEATURE_NORMALIZATION_DECISION,
        "repair_version": EXP062_NONFINITE_FEATURE_NORMALIZATION_VERSION,
        "repair_proof_decision": EXP062_ADAPTER_PROOF_RESULT_FREEZE_DECISION,
        "repair_proof_version": EXP062_ADAPTER_PROOF_RESULT_FREEZE_VERSION,
        "semantic_predecessor_experiment_id": EXP061_EXPERIMENT_ID,
        "semantic_predecessor_protocol_fingerprint": (
            exp061_protocol_fingerprint()
        ),
        "nonfinite_to_null_repair_applied": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"DEC-298 aggregate {field} mismatch")

    rows = value.get("exp062_cell_evidence_fingerprints")
    if not isinstance(rows, list) or len(rows) != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-298 outer cell fingerprint inventory mismatch")
    identities: list[tuple[str, str, int]] = []
    fingerprints: list[str] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("DEC-298 outer cell fingerprint row malformed")
        identity = (
            row.get("symbol"),
            row.get("timeframe"),
            row.get("horizon_minutes"),
        )
        if identity not in EXPECTED_CELLS:
            raise ValueError("DEC-298 outer cell fingerprint identity mismatch")
        identities.append((str(identity[0]), str(identity[1]), int(identity[2])))
        fingerprints.append(
            _validate_sha256(
                row.get("evidence_fingerprint"),
                field="DEC-298 outer cell fingerprint",
            )
        )
    if tuple(identities) != tuple(sorted(EXPECTED_CELLS)):
        raise ValueError("DEC-298 outer cell fingerprints are not exact/sorted")
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("DEC-298 outer cell fingerprints contain duplicates")

    _reconstruct_predecessor_aggregate(value)
    return value


__all__ = [
    "AGGREGATE_JOB_NAME",
    "DISCOVERY_RESULT_AUTHORIZED",
    "EXPECTED_ARTIFACT_COUNT",
    "EXPECTED_CELL_COUNT",
    "EXPECTED_CELLS",
    "EXPECTED_JOB_COUNT",
    "EXP062_AGGREGATE_EVIDENCE_PROTOCOL",
    "EXP062_AGGREGATE_EVIDENCE_VERSION",
    "EXP062_CELL_EVIDENCE_PROTOCOL",
    "EXP062_CELL_EVIDENCE_VERSION",
    "EXP062_EXPERIMENT_ID",
    "EXP062_RUN_CONTRACT_VERSION",
    "EXP062_RUN_EVIDENCE_DECISION",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "PREFLIGHT_JOB_NAME",
    "REPLACEMENT_RUN_AUTHORIZED",
    "RERUN_AUTHORIZED",
    "RETRY_AUTHORIZED",
    "WORKFLOW_DISPATCH_AUTHORIZED",
    "WORKFLOW_NAME",
    "WORKFLOW_PATH",
    "compile_aggregate_evidence",
    "compile_cell_evidence",
    "expected_artifact_names",
    "expected_cell_artifact_name",
    "expected_cell_job_name",
    "expected_job_names",
    "exp062_protocol_fingerprint",
    "run_contract_payload",
    "validate_aggregate_evidence",
    "validate_cell_evidence",
    "validate_exp062_run_contract_sources",
]
