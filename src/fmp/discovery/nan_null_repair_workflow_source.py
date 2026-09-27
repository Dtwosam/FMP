from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from . import workflow_source as _predecessor_source
from .nan_null_repair_run_contract import (
    EXPECTED_CELLS,
    run_contract_payload,
)


EXP062_DORMANT_WORKFLOW_SOURCE_DECISION = "DEC-295"
EXP062_DORMANT_WORKFLOW_SOURCE_VERSION = (
    "fmp-exp062-dormant-workflow-source-v1"
)

DORMANT_WORKFLOW_TEMPLATE_PATH = (
    "docs/superpowers/templates/phase8a-exp062-discovery.yml.disabled"
)
RESERVED_ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-exp062-discovery.yml"

DEC294_RUN_CONTRACT_BLOB_SHA = "0d1532e6a747e2dd9f0e70cd395e97433e6320ce"
DEC293_REPAIRED_ADAPTER_BLOB_SHA = (
    "53f85d99bad42decb673e9fa2ff0f771150e17db"
)
EXP061_SOURCE_VALIDATOR_BLOB_SHA = (
    "68566fc86ff3470cc8b6ebef606becaff9f3450b"
)
EXP061_LOADER_BLOB_SHA = "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
EXP061_MINER_BLOB_SHA = "495a67699eb5014e52129f0238a2737049fe38e6"
RUNTIME_REQUIREMENTS_BLOB_SHA = "1ff32214dee10d877a067e750cd69ffad96d5fe5"

WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED = False
WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def validate_workflow_source_dependencies(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec294_run_contract": (
            root / "src/fmp/discovery/nan_null_repair_run_contract.py",
            DEC294_RUN_CONTRACT_BLOB_SHA,
        ),
        "dec293_repaired_adapter": (
            root / "src/fmp/discovery/nan_null_repair_adapter.py",
            DEC293_REPAIRED_ADAPTER_BLOB_SHA,
        ),
        "exp061_source_validator": (
            root / "src/fmp/discovery/workflow_source.py",
            EXP061_SOURCE_VALIDATOR_BLOB_SHA,
        ),
        "exp061_loader": (
            root / "src/fmp/discovery/range_limited_loader.py",
            EXP061_LOADER_BLOB_SHA,
        ),
        "exp061_miner": (
            root / "src/fmp/discovery/pattern_miner.py",
            EXP061_MINER_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp061-discovery-run.txt",
            RUNTIME_REQUIREMENTS_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing EXP-062 workflow dependency: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(
                f"EXP-062 {label} Git blob mismatch: {sha} != {expected_sha}"
            )
        actual[label] = sha
    return {
        "decision": EXP062_DORMANT_WORKFLOW_SOURCE_DECISION,
        "source_version": EXP062_DORMANT_WORKFLOW_SOURCE_VERSION,
        "source_blobs": actual,
        "workflow_template_install_authorized": False,
        "workflow_dispatch_authorized": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
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


def source_artifacts_for_cell(
    symbol: str,
    timeframe: str,
) -> Mapping[str, object]:
    return _predecessor_source.source_artifacts_for_cell(
        symbol,
        timeframe,
    )


def validate_source_snapshots(
    *,
    feature_run: Mapping[str, object],
    feature_artifacts: Mapping[str, object],
    outcome_run: Mapping[str, object],
    outcome_artifacts: Mapping[str, object],
) -> dict[str, object]:
    predecessor = _predecessor_source.validate_source_snapshots(
        feature_run=feature_run,
        feature_artifacts=feature_artifacts,
        outcome_run=outcome_run,
        outcome_artifacts=outcome_artifacts,
    )
    if predecessor.get("source_ready") is not True:
        raise ValueError("EXP-062 predecessor source snapshots are not ready")
    if predecessor.get("verified_pair_timeframe_source_count") != 9:
        raise ValueError("EXP-062 source pair/timeframe count drift")

    return {
        "decision": EXP062_DORMANT_WORKFLOW_SOURCE_DECISION,
        "source_version": EXP062_DORMANT_WORKFLOW_SOURCE_VERSION,
        "semantic_source_predecessor_decision": (
            _predecessor_source.EXP061_DORMANT_WORKFLOW_SOURCE_DECISION
        ),
        "feature_run_id": predecessor["feature_run_id"],
        "feature_head_sha": predecessor["feature_head_sha"],
        "outcome_run_id": predecessor["outcome_run_id"],
        "outcome_head_sha": predecessor["outcome_head_sha"],
        "feature_evidence_artifact_id": predecessor[
            "feature_evidence_artifact_id"
        ],
        "outcome_evidence_artifact_id": predecessor[
            "outcome_evidence_artifact_id"
        ],
        "verified_pair_timeframe_source_count": 9,
        "source_ready": True,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
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


def workflow_source_payload(*, code_commit: str) -> dict[str, object]:
    contract = run_contract_payload(code_commit=code_commit)
    cells: list[dict[str, object]] = []
    for symbol, timeframe, horizon in EXPECTED_CELLS:
        source = source_artifacts_for_cell(symbol, timeframe)
        cells.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "horizon_minutes": horizon,
                "feature_artifact_id": source["feature_id"],
                "feature_artifact_digest": source["feature_digest"],
                "outcome_artifact_id": source["outcome_id"],
                "outcome_artifact_digest": source["outcome_digest"],
            }
        )

    return {
        "decision": EXP062_DORMANT_WORKFLOW_SOURCE_DECISION,
        "source_version": EXP062_DORMANT_WORKFLOW_SOURCE_VERSION,
        "code_commit": code_commit,
        "dormant_workflow_template_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
        "reserved_active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "run_contract": contract,
        "accepted_feature_run_id": _predecessor_source.FEATURE_RUN["id"],
        "accepted_outcome_run_id": _predecessor_source.OUTCOME_RUN["id"],
        "feature_evidence_artifact_id": (
            _predecessor_source.FEATURE_EVIDENCE_ARTIFACT["id"]
        ),
        "outcome_evidence_artifact_id": (
            _predecessor_source.OUTCOME_EVIDENCE_ARTIFACT["id"]
        ),
        "cells": cells,
        "workflow_template_install_authorized": False,
        "workflow_dispatch_authorized": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
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


def require_historical_execution_authorized(*, code_commit: str) -> None:
    run_contract_payload(code_commit=code_commit)
    raise PermissionError(
        "EXP-062 historical discovery execution is not authorized by DEC-295"
    )


__all__ = [
    "DORMANT_WORKFLOW_TEMPLATE_PATH",
    "EXP062_DORMANT_WORKFLOW_SOURCE_DECISION",
    "EXP062_DORMANT_WORKFLOW_SOURCE_VERSION",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "RESERVED_ACTIVE_WORKFLOW_PATH",
    "WORKFLOW_DISPATCH_AUTHORIZED",
    "WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED",
    "require_historical_execution_authorized",
    "source_artifacts_for_cell",
    "validate_source_snapshots",
    "validate_workflow_source_dependencies",
    "workflow_source_payload",
]
