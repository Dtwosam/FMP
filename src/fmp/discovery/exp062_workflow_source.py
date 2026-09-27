from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from . import workflow_source as _pre_source
from .exp062_run_contract import (
    EXPECTED_CELLS,
    EXP062_EXPERIMENT_ID,
    expected_aggregate_artifact_name,
    expected_cell_artifact_name,
    expected_job_names,
    expected_preflight_artifact_name,
    run_contract_payload,
)


EXP062_DORMANT_WORKFLOW_SOURCE_DECISION = "DEC-299"
EXP062_DORMANT_WORKFLOW_SOURCE_VERSION = (
    "fmp-exp062-dormant-workflow-source-v1"
)

DORMANT_WORKFLOW_TEMPLATE_PATH = (
    "docs/superpowers/templates/phase8a-exp062-discovery.yml.disabled"
)
RESERVED_ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-exp062-discovery.yml"

DEC298_RUN_CONTRACT_BLOB_SHA = "d304c8fafcff64f967f6777b1c494819f69d4a03"
DEC293_REPAIRED_ADAPTER_BLOB_SHA = "491ba8c92cb6e6e4c715bfb1ecb934b6949e1596"
EXP061_SOURCE_CONTRACT_BLOB_SHA = "68566fc86ff3470cc8b6ebef606becaff9f3450b"
EXP061_MINER_BLOB_SHA = "495a67699eb5014e52129f0238a2737049fe38e6"
EXP061_LOADER_BLOB_SHA = "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
RUNTIME_REQUIREMENTS_BLOB_SHA = "1ff32214dee10d877a067e750cd69ffad96d5fe5"

WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED = False
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


def _validate_commit(value: object) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError("code_commit must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("code_commit must be hexadecimal") from exc
    return value.lower()


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def validate_exp062_workflow_source_dependencies(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec298_run_contract": (
            root / "src/fmp/discovery/exp062_run_contract.py",
            DEC298_RUN_CONTRACT_BLOB_SHA,
        ),
        "dec293_repaired_adapter": (
            root / "src/fmp/discovery/exp062_nonfinite_feature_adapter.py",
            DEC293_REPAIRED_ADAPTER_BLOB_SHA,
        ),
        "exp061_source_contract": (
            root / "src/fmp/discovery/workflow_source.py",
            EXP061_SOURCE_CONTRACT_BLOB_SHA,
        ),
        "exp061_miner": (
            root / "src/fmp/discovery/pattern_miner.py",
            EXP061_MINER_BLOB_SHA,
        ),
        "exp061_loader": (
            root / "src/fmp/discovery/range_limited_loader.py",
            EXP061_LOADER_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp061-discovery-run.txt",
            RUNTIME_REQUIREMENTS_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-299 source dependency: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(
                f"DEC-299 {label} Git blob mismatch: {sha} != {expected_sha}"
            )
        actual[label] = sha

    return {
        "decision": EXP062_DORMANT_WORKFLOW_SOURCE_DECISION,
        "source_version": EXP062_DORMANT_WORKFLOW_SOURCE_VERSION,
        "experiment_id": EXP062_EXPERIMENT_ID,
        "source_blobs": actual,
        "template_install_authorized": False,
        "workflow_dispatch_authorized": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "trading_authorized": False,
    }


def validate_source_snapshots(
    *,
    feature_run: Mapping[str, object],
    feature_artifacts: Mapping[str, object],
    outcome_run: Mapping[str, object],
    outcome_artifacts: Mapping[str, object],
) -> dict[str, object]:
    predecessor = _pre_source.validate_source_snapshots(
        feature_run=feature_run,
        feature_artifacts=feature_artifacts,
        outcome_run=outcome_run,
        outcome_artifacts=outcome_artifacts,
    )
    if predecessor.get("source_ready") is not True:
        raise ValueError("DEC-299 predecessor source snapshot is not ready")

    report: dict[str, object] = {
        "decision": EXP062_DORMANT_WORKFLOW_SOURCE_DECISION,
        "source_version": EXP062_DORMANT_WORKFLOW_SOURCE_VERSION,
        "experiment_id": EXP062_EXPERIMENT_ID,
        "predecessor_source_decision": predecessor["decision"],
        "predecessor_source_version": predecessor["source_version"],
        "predecessor_source_fingerprint": predecessor["source_fingerprint"],
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
        "verified_pair_timeframe_source_count": predecessor[
            "verified_pair_timeframe_source_count"
        ],
        "source_ready": True,
        "nonfinite_to_null_repair_required": True,
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
    report["source_fingerprint"] = _sha256_bytes(_canonical_json(report))
    return report


def source_artifacts_for_cell(
    symbol: str,
    timeframe: str,
) -> Mapping[str, object]:
    return _pre_source.source_artifacts_for_cell(symbol, timeframe)


def require_historical_execution_authorized(*, code_commit: str) -> None:
    _validate_commit(code_commit)
    if not HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED:
        raise PermissionError(
            "DEC-299 historical EXP-062 discovery execution remains locked"
        )


def workflow_source_payload(*, code_commit: str) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    return {
        "decision": EXP062_DORMANT_WORKFLOW_SOURCE_DECISION,
        "source_version": EXP062_DORMANT_WORKFLOW_SOURCE_VERSION,
        "experiment_id": EXP062_EXPERIMENT_ID,
        "code_commit": code_commit,
        "dormant_template_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
        "reserved_active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "template_install_authorized": False,
        "workflow_dispatch_authorized": False,
        "historical_discovery_execution_authorized": False,
        "feature_source_run": dict(_pre_source.FEATURE_RUN),
        "outcome_source_run": dict(_pre_source.OUTCOME_RUN),
        "feature_evidence_artifact": dict(
            _pre_source.FEATURE_EVIDENCE_ARTIFACT
        ),
        "outcome_evidence_artifact": dict(
            _pre_source.OUTCOME_EVIDENCE_ARTIFACT
        ),
        "pair_timeframe_source_artifacts": [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                **dict(source_artifacts_for_cell(symbol, timeframe)),
            }
            for symbol, timeframe in sorted(
                {
                    (symbol, timeframe)
                    for symbol, timeframe, _ in EXPECTED_CELLS
                }
            )
        ],
        "expected_job_names": list(expected_job_names()),
        "expected_preflight_artifact": expected_preflight_artifact_name(
            code_commit=code_commit
        ),
        "expected_cell_artifacts": [
            expected_cell_artifact_name(
                symbol,
                timeframe,
                horizon,
                code_commit=code_commit,
            )
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ],
        "expected_aggregate_artifact": expected_aggregate_artifact_name(
            code_commit=code_commit
        ),
        "run_contract": run_contract_payload(code_commit=code_commit),
        "authorizations": {
            "template_install_authorized": False,
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


def validate_dormant_workflow_template(text: str) -> None:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("DEC-299 dormant workflow template must be non-empty")
    if "name: phase8a-exp062-discovery" not in text:
        raise ValueError("DEC-299 dormant workflow name mismatch")
    if "workflow_dispatch:" not in text:
        raise ValueError("DEC-299 dormant workflow trigger mismatch")
    if "matrix:" not in text:
        raise ValueError("DEC-299 dormant workflow must use the frozen matrix")
    expected_cell_name = (
        "name: exp062-cell-${{ matrix.dataset.symbol }}-"
        "${{ matrix.dataset.timeframe }}-"
        "${{ matrix.dataset.horizon }}m"
    )
    if expected_cell_name not in text:
        raise ValueError("DEC-299 explicit cell job-name expression missing")
    if "python scripts/phase8a_exp062.py require-execution" not in text:
        raise ValueError("DEC-299 dormant execution gate is missing")
    for job_name in ("exp062-preflight", "exp062-aggregate"):
        if f"name: {job_name}" not in text:
            raise ValueError(f"DEC-299 dormant workflow missing {job_name}")
    if "${{ matrix }}" in text:
        raise ValueError("DEC-299 dormant workflow may not use implicit matrix names")
    if "phase8a_exp061.py cell" in text:
        raise ValueError("DEC-299 dormant workflow cannot call EXP-061 cell CLI")
    if "phase8a_exp061.py aggregate" in text:
        raise ValueError(
            "DEC-299 dormant workflow cannot call EXP-061 aggregate CLI"
        )


def load_and_validate_dormant_workflow_template(path: Path) -> str:
    text = Path(path).read_text(encoding="utf-8")
    validate_dormant_workflow_template(text)
    return text


__all__ = [
    "DORMANT_WORKFLOW_TEMPLATE_PATH",
    "EXP062_DORMANT_WORKFLOW_SOURCE_DECISION",
    "EXP062_DORMANT_WORKFLOW_SOURCE_VERSION",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "RESERVED_ACTIVE_WORKFLOW_PATH",
    "WORKFLOW_DISPATCH_AUTHORIZED",
    "WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED",
    "load_and_validate_dormant_workflow_template",
    "require_historical_execution_authorized",
    "source_artifacts_for_cell",
    "validate_dormant_workflow_template",
    "validate_exp062_workflow_source_dependencies",
    "validate_source_snapshots",
    "workflow_source_payload",
]
