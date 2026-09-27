from __future__ import annotations

import hashlib
import json
from typing import Mapping, Sequence

from . import run_contract as _predecessor
from .nan_null_repair_adapter import (
    _reconstruct_predecessor_evidence,
    validate_cell_evidence,
)
from .nan_null_repair_protocol import (
    EXP062_EXPERIMENT_ID,
    EXP062_REPAIR_PROTOCOL_DECISION,
    EXP062_REPAIR_PROTOCOL_VERSION,
    exp062_repair_protocol_fingerprint,
)
from .pattern_protocol import (
    EXPERIMENT_ID as EXP061_EXPERIMENT_ID,
    protocol_fingerprint as exp061_protocol_fingerprint,
)


EXP062_RUN_CONTRACT_DECISION = "DEC-294"
EXP062_RUN_CONTRACT_VERSION = "fmp-exp062-run-contract-v1"
EXP062_AGGREGATE_EVIDENCE_VERSION = 1
EXP062_AGGREGATE_EVIDENCE_PROTOCOL = "fmp-exp062-aggregate-evidence-v1"

WORKFLOW_NAME = "phase8a-exp062-discovery"
WORKFLOW_PATH = ".github/workflows/phase8a-exp062-discovery.yml"
WORKFLOW_EVENT = "workflow_dispatch"
WORKFLOW_BRANCH = "main"
WORKFLOW_RUN_ATTEMPT = 1

PREFLIGHT_JOB_NAME = "exp062-preflight"
AGGREGATE_JOB_NAME = "exp062-aggregate"

DEC292_PROTOCOL_BLOB_SHA = "1d26da24134c825e2f405224316e1dd3136a38fb"
DEC293_ADAPTER_BLOB_SHA = "53f85d99bad42decb673e9fa2ff0f771150e17db"
EXP061_MINER_BLOB_SHA = "495a67699eb5014e52129f0238a2737049fe38e6"
EXP061_LOADER_BLOB_SHA = "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
EXP061_RUN_CONTRACT_BLOB_SHA = "260eb6930673427266463517546969635188b143"

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

EXPECTED_CELLS = tuple(_predecessor.EXPECTED_CELLS)
EXPECTED_CELL_COUNT = _predecessor.EXPECTED_CELL_COUNT
EXPECTED_JOB_COUNT = _predecessor.EXPECTED_JOB_COUNT
EXPECTED_ARTIFACT_COUNT = _predecessor.EXPECTED_ARTIFACT_COUNT


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
    return _predecessor._validate_sha256(value, field=field)


def _validate_commit(value: object, *, field: str = "code_commit") -> str:
    return _predecessor._validate_commit(value, field=field)


def expected_cell_job_name(
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> str:
    cell = (symbol, timeframe, horizon_minutes)
    if cell not in EXPECTED_CELLS:
        raise ValueError("unsupported EXP-062 run-contract cell")
    return f"exp062-cell-{symbol}-{timeframe}-{horizon_minutes}m"


def expected_cell_artifact_name(
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    *,
    code_commit: str,
) -> str:
    _validate_commit(code_commit)
    return (
        f"phase8a-exp062-cell-{symbol}-{timeframe}-"
        f"{horizon_minutes}m-{code_commit}"
    )


def expected_preflight_artifact_name(*, code_commit: str) -> str:
    _validate_commit(code_commit)
    return f"phase8a-exp062-preflight-{code_commit}"


def expected_aggregate_artifact_name(*, code_commit: str) -> str:
    _validate_commit(code_commit)
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
    _validate_commit(code_commit)
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
        raise ValueError("EXP-062 run-contract job inventory drift")
    if (
        len(artifacts) != EXPECTED_ARTIFACT_COUNT
        or len(set(artifacts)) != EXPECTED_ARTIFACT_COUNT
    ):
        raise ValueError("EXP-062 run-contract artifact inventory drift")

    return {
        "decision": EXP062_RUN_CONTRACT_DECISION,
        "contract_version": EXP062_RUN_CONTRACT_VERSION,
        "experiment_id": EXP062_EXPERIMENT_ID,
        "repair_protocol_decision": EXP062_REPAIR_PROTOCOL_DECISION,
        "repair_protocol_version": EXP062_REPAIR_PROTOCOL_VERSION,
        "repair_protocol_fingerprint": exp062_repair_protocol_fingerprint(),
        "semantic_predecessor_experiment_id": EXP061_EXPERIMENT_ID,
        "semantic_predecessor_protocol_fingerprint": exp061_protocol_fingerprint(),
        "semantic_predecessor_run_contract_version": (
            _predecessor.EXP061_RUN_CONTRACT_VERSION
        ),
        "code_commit": code_commit,
        "workflow": {
            "name": WORKFLOW_NAME,
            "path": WORKFLOW_PATH,
            "event": WORKFLOW_EVENT,
            "branch": WORKFLOW_BRANCH,
            "run_attempt": WORKFLOW_RUN_ATTEMPT,
        },
        "source_blobs": {
            "dec292_repair_protocol": DEC292_PROTOCOL_BLOB_SHA,
            "dec293_repaired_adapter": DEC293_ADAPTER_BLOB_SHA,
            "exp061_miner": EXP061_MINER_BLOB_SHA,
            "exp061_range_limited_loader": EXP061_LOADER_BLOB_SHA,
            "exp061_run_contract": EXP061_RUN_CONTRACT_BLOB_SHA,
        },
        "cells": [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "horizon_minutes": horizon,
                "job_name": expected_cell_job_name(symbol, timeframe, horizon),
                "artifact_name": expected_cell_artifact_name(
                    symbol,
                    timeframe,
                    horizon,
                    code_commit=code_commit,
                ),
            }
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ],
        "expected_job_names": list(jobs),
        "expected_artifact_names": list(artifacts),
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
            "aggregate_success_evidence_required": False,
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


def _exp062_cell_identity(
    value: Mapping[str, object],
) -> tuple[str, str, int]:
    raw = value.get("cell")
    if not isinstance(raw, Mapping):
        raise ValueError("EXP-062 aggregate cell evidence is missing cell identity")
    identity = (
        raw.get("symbol"),
        raw.get("timeframe"),
        raw.get("horizon_minutes"),
    )
    if identity not in EXPECTED_CELLS:
        raise ValueError(
            f"unexpected EXP-062 aggregate cell identity: {identity!r}"
        )
    return str(identity[0]), str(identity[1]), int(identity[2])


def compile_aggregate_evidence(
    cell_evidence: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    if len(cell_evidence) != EXPECTED_CELL_COUNT:
        raise ValueError(
            f"EXP-062 aggregate requires exactly {EXPECTED_CELL_COUNT} "
            "cell evidence objects"
        )

    validated: list[Mapping[str, object]] = []
    exp062_fingerprints: dict[tuple[str, str, int], str] = {}
    predecessor_cells: list[dict[str, object]] = []
    seen: set[tuple[str, str, int]] = set()
    for raw in cell_evidence:
        item = validate_cell_evidence(raw)
        if item.get("code_commit") != code_commit:
            raise ValueError("EXP-062 aggregate cell code commit mismatch")
        identity = _exp062_cell_identity(item)
        if identity in seen:
            raise ValueError(
                f"duplicate EXP-062 aggregate cell evidence: {identity!r}"
            )
        seen.add(identity)
        validated.append(item)
        exp062_fingerprints[identity] = _validate_sha256(
            item.get("evidence_fingerprint"),
            field="EXP-062 cell evidence fingerprint",
        )
        predecessor_cells.append(_reconstruct_predecessor_evidence(item))

    if tuple(sorted(seen)) != tuple(sorted(EXPECTED_CELLS)):
        raise ValueError(
            "EXP-062 aggregate cell inventory is incomplete or unexpected"
        )

    predecessor = _predecessor.compile_aggregate_evidence(
        predecessor_cells,
        code_commit=code_commit,
    )
    predecessor_fingerprint = str(predecessor["evidence_fingerprint"])

    value = dict(predecessor)
    value.pop("evidence_fingerprint", None)
    value["evidence_version"] = EXP062_AGGREGATE_EVIDENCE_VERSION
    value["evidence_protocol"] = EXP062_AGGREGATE_EVIDENCE_PROTOCOL
    value["experiment_id"] = EXP062_EXPERIMENT_ID
    value["run_contract_version"] = EXP062_RUN_CONTRACT_VERSION
    value["protocol_fingerprint"] = exp062_repair_protocol_fingerprint()
    value["repair_protocol_decision"] = EXP062_REPAIR_PROTOCOL_DECISION
    value["repair_protocol_version"] = EXP062_REPAIR_PROTOCOL_VERSION
    value["semantic_predecessor_experiment_id"] = EXP061_EXPERIMENT_ID
    value["semantic_predecessor_protocol_fingerprint"] = (
        exp061_protocol_fingerprint()
    )
    value["semantic_predecessor_aggregate_evidence_fingerprint"] = (
        predecessor_fingerprint
    )
    value["nan_to_null_adapter_repair_applied"] = True
    value["exp062_cell_evidence_fingerprints"] = [
        {
            "symbol": symbol,
            "timeframe": timeframe,
            "horizon_minutes": horizon,
            "evidence_fingerprint": exp062_fingerprints[
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
    predecessor.pop("repair_protocol_decision", None)
    predecessor.pop("repair_protocol_version", None)
    predecessor.pop("semantic_predecessor_experiment_id", None)
    predecessor.pop("semantic_predecessor_protocol_fingerprint", None)
    stored_fingerprint = predecessor.pop(
        "semantic_predecessor_aggregate_evidence_fingerprint",
        None,
    )
    predecessor.pop("nan_to_null_adapter_repair_applied", None)
    predecessor.pop("exp062_cell_evidence_fingerprints", None)
    predecessor["evidence_version"] = (
        _predecessor.EXP061_AGGREGATE_EVIDENCE_VERSION
    )
    predecessor["evidence_protocol"] = (
        _predecessor.EXP061_AGGREGATE_EVIDENCE_PROTOCOL
    )
    predecessor["experiment_id"] = EXP061_EXPERIMENT_ID
    predecessor["run_contract_version"] = (
        _predecessor.EXP061_RUN_CONTRACT_VERSION
    )
    predecessor["protocol_fingerprint"] = exp061_protocol_fingerprint()
    predecessor["evidence_fingerprint"] = _predecessor._sha256_bytes(
        _predecessor._canonical_json(predecessor)
    )
    if predecessor["evidence_fingerprint"] != stored_fingerprint:
        raise ValueError(
            "EXP-062 semantic predecessor aggregate fingerprint mismatch"
        )
    return predecessor


def validate_aggregate_evidence(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="EXP-062 aggregate evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("EXP-062 aggregate evidence fingerprint mismatch")

    if value.get("evidence_version") != EXP062_AGGREGATE_EVIDENCE_VERSION:
        raise ValueError("EXP-062 aggregate evidence version mismatch")
    if value.get("evidence_protocol") != EXP062_AGGREGATE_EVIDENCE_PROTOCOL:
        raise ValueError("EXP-062 aggregate evidence protocol mismatch")
    if value.get("experiment_id") != EXP062_EXPERIMENT_ID:
        raise ValueError("EXP-062 aggregate experiment identity mismatch")
    if value.get("run_contract_version") != EXP062_RUN_CONTRACT_VERSION:
        raise ValueError("EXP-062 aggregate run-contract identity mismatch")
    if value.get("protocol_fingerprint") != exp062_repair_protocol_fingerprint():
        raise ValueError("EXP-062 aggregate repair protocol mismatch")
    if value.get("repair_protocol_decision") != EXP062_REPAIR_PROTOCOL_DECISION:
        raise ValueError("EXP-062 aggregate repair decision mismatch")
    if value.get("repair_protocol_version") != EXP062_REPAIR_PROTOCOL_VERSION:
        raise ValueError("EXP-062 aggregate repair version mismatch")
    if value.get("semantic_predecessor_experiment_id") != EXP061_EXPERIMENT_ID:
        raise ValueError(
            "EXP-062 aggregate semantic predecessor experiment mismatch"
        )
    if value.get("semantic_predecessor_protocol_fingerprint") != (
        exp061_protocol_fingerprint()
    ):
        raise ValueError(
            "EXP-062 aggregate semantic predecessor protocol mismatch"
        )
    if value.get("nan_to_null_adapter_repair_applied") is not True:
        raise ValueError("EXP-062 aggregate repair marker missing")

    raw_fingerprints = value.get("exp062_cell_evidence_fingerprints")
    if (
        not isinstance(raw_fingerprints, list)
        or len(raw_fingerprints) != EXPECTED_CELL_COUNT
    ):
        raise ValueError(
            "EXP-062 aggregate cell evidence fingerprint inventory is incomplete"
        )
    identities: list[tuple[str, str, int]] = []
    fingerprints: list[str] = []
    for raw in raw_fingerprints:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-062 aggregate cell evidence fingerprint row is malformed"
            )
        identity = (
            raw.get("symbol"),
            raw.get("timeframe"),
            raw.get("horizon_minutes"),
        )
        if identity not in EXPECTED_CELLS:
            raise ValueError(
                "EXP-062 aggregate cell evidence fingerprint identity mismatch"
            )
        identities.append(
            (str(identity[0]), str(identity[1]), int(identity[2]))
        )
        fingerprints.append(
            _validate_sha256(
                raw.get("evidence_fingerprint"),
                field="EXP-062 cell evidence fingerprint",
            )
        )
    if tuple(identities) != tuple(sorted(EXPECTED_CELLS)):
        raise ValueError(
            "EXP-062 aggregate cell evidence fingerprints are not exact and sorted"
        )
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError(
            "EXP-062 aggregate cell evidence fingerprints contain duplicates"
        )

    predecessor = _reconstruct_predecessor_aggregate(value)
    _predecessor.validate_aggregate_evidence(predecessor)

    for field in (
        "reserved_robustness_opened",
        "candidate_compilation_authorized",
        "promotion_authorized",
        "phase8b_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"EXP-062 aggregate {field} must remain false")
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
    "EXP062_RUN_CONTRACT_DECISION",
    "EXP062_RUN_CONTRACT_VERSION",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "PREFLIGHT_JOB_NAME",
    "RERUN_AUTHORIZED",
    "REPLACEMENT_RUN_AUTHORIZED",
    "RETRY_AUTHORIZED",
    "WORKFLOW_DISPATCH_AUTHORIZED",
    "WORKFLOW_NAME",
    "WORKFLOW_PATH",
    "WORKFLOW_RUN_ATTEMPT",
    "compile_aggregate_evidence",
    "expected_artifact_names",
    "expected_cell_artifact_name",
    "expected_cell_job_name",
    "expected_job_names",
    "run_contract_payload",
    "validate_aggregate_evidence",
]
