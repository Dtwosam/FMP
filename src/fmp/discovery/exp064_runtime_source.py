from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from . import workflow_source as _exp061_source
from . import exp062_workflow_source as _exp062_source
from .exp064_evidence_contract import EXPECTED_CELLS
from .exp064_continuous_stability_protocol import protocol_fingerprint
from .exp064_research_direction import SUCCESSOR_EXPERIMENT_ID


EXP064_LOCKED_RUNTIME_DECISION = "DEC-455"
EXP064_LOCKED_RUNTIME_VERSION = "fmp-exp064-locked-runtime-wiring-v1"

WORKFLOW_NAME = "phase8a-exp064-continuous-stability"
WORKFLOW_EVENT = "workflow_dispatch"
WORKFLOW_BRANCH = "main"
WORKFLOW_RUN_ATTEMPT = 1

DORMANT_WORKFLOW_TEMPLATE_PATH = (
    "docs/superpowers/templates/phase8a-exp064-continuous-stability.yml.disabled"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-exp064-continuous-stability.yml"
CLI_PATH = "scripts/phase8a_exp064.py"
RUNTIME_REQUIREMENTS_PATH = "requirements/exp061-discovery-run.txt"

PREFLIGHT_JOB_NAME = "exp064-preflight"
AGGREGATE_JOB_NAME = "exp064-aggregate"

DEC454_EVIDENCE_CONTRACT_BLOB_SHA = (
    "9aee3f9e273e20329c9de5a7079ed924ffee0a9a"
)
DEC453_MINER_BLOB_SHA = "b0d799ec1afaf43b0441290c97a9f39c37ecd2fd"
DEC452_PROTOCOL_BLOB_SHA = "c108ea047c7bfb3e588bfbac33993180066c28ad"
EXP062_REPAIRED_ADAPTER_BLOB_SHA = (
    "491ba8c92cb6e6e4c715bfb1ecb934b6949e1596"
)
EXP062_SOURCE_CONTRACT_BLOB_SHA = (
    "e20ded13de24f99e8ea6cfdc6cb0d1309d984f24"
)
EXP061_LOADER_BLOB_SHA = "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
RUNTIME_REQUIREMENTS_BLOB_SHA = (
    "1ff32214dee10d877a067e750cd69ffad96d5fe5"
)

EXPECTED_TEMPLATE_BLOB_SHA = "caca62672ad9796764c18be6b8da9785b98c9733"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = "caca62672ad9796764c18be6b8da9785b98c9733"
EXPECTED_CLI_BLOB_SHA = "a44aed6d890e25a781b7b92d7efb3dabe06f9047"

WORKFLOW_SOURCE_AUTHORIZED = True
WORKFLOW_INSTALLED = True
WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_AUTHORIZED = False
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

EXPECTED_CELL_COUNT = len(EXPECTED_CELLS)
EXPECTED_JOB_COUNT = EXPECTED_CELL_COUNT + 2
EXPECTED_ARTIFACT_COUNT = EXPECTED_CELL_COUNT + 2

FEATURE_RUN = _exp061_source.FEATURE_RUN
OUTCOME_RUN = _exp061_source.OUTCOME_RUN
FEATURE_EVIDENCE_ARTIFACT = _exp061_source.FEATURE_EVIDENCE_ARTIFACT
OUTCOME_EVIDENCE_ARTIFACT = _exp061_source.OUTCOME_EVIDENCE_ARTIFACT


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


def expected_cell_job_name(
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> str:
    identity = (symbol, timeframe, horizon_minutes)
    if identity not in EXPECTED_CELLS:
        raise ValueError("unsupported DEC-455 EXP-064 cell")
    return f"exp064-cell-{symbol}-{timeframe}-{horizon_minutes}m"


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
        f"phase8a-exp064-cell-{symbol}-{timeframe}-"
        f"{horizon_minutes}m-{code_commit}"
    )


def expected_preflight_artifact_name(*, code_commit: str) -> str:
    code_commit = _validate_commit(code_commit)
    return f"phase8a-exp064-preflight-{code_commit}"


def expected_aggregate_artifact_name(*, code_commit: str) -> str:
    code_commit = _validate_commit(code_commit)
    return f"phase8a-exp064-aggregate-{code_commit}"


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


def source_artifacts_for_cell(
    symbol: str,
    timeframe: str,
) -> Mapping[str, object]:
    return _exp062_source.source_artifacts_for_cell(symbol, timeframe)


def validate_source_snapshots(
    *,
    feature_run: Mapping[str, object],
    feature_artifacts: Mapping[str, object],
    outcome_run: Mapping[str, object],
    outcome_artifacts: Mapping[str, object],
) -> dict[str, object]:
    predecessor = _exp062_source.validate_source_snapshots(
        feature_run=feature_run,
        feature_artifacts=feature_artifacts,
        outcome_run=outcome_run,
        outcome_artifacts=outcome_artifacts,
    )
    if predecessor.get("source_ready") is not True:
        raise ValueError("DEC-455 predecessor source snapshot is not ready")
    report: dict[str, object] = {
        "decision": EXP064_LOCKED_RUNTIME_DECISION,
        "runtime_version": EXP064_LOCKED_RUNTIME_VERSION,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
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
        "workflow_dispatch_authorized": False,
        "historical_execution_authorized": False,
        "historical_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "phase8b_authorized": False,
        "trading_authorized": False,
    }
    report["source_fingerprint"] = _sha256_bytes(_canonical_json(report))
    return report


def validate_runtime_dependencies(*, repository_root: Path) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec454_evidence_contract": (
            root / "src/fmp/discovery/exp064_evidence_contract.py",
            DEC454_EVIDENCE_CONTRACT_BLOB_SHA,
        ),
        "dec453_continuous_stability_miner": (
            root / "src/fmp/discovery/exp064_continuous_stability_miner.py",
            DEC453_MINER_BLOB_SHA,
        ),
        "dec452_continuous_stability_protocol": (
            root / "src/fmp/discovery/exp064_continuous_stability_protocol.py",
            DEC452_PROTOCOL_BLOB_SHA,
        ),
        "exp062_repaired_adapter": (
            root / "src/fmp/discovery/exp062_nonfinite_feature_adapter.py",
            EXP062_REPAIRED_ADAPTER_BLOB_SHA,
        ),
        "exp062_source_contract": (
            root / "src/fmp/discovery/exp062_workflow_source.py",
            EXP062_SOURCE_CONTRACT_BLOB_SHA,
        ),
        "exp061_loader": (
            root / "src/fmp/discovery/range_limited_loader.py",
            EXP061_LOADER_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / RUNTIME_REQUIREMENTS_PATH,
            RUNTIME_REQUIREMENTS_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-455 source dependency: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(
                f"DEC-455 {label} Git blob mismatch: {sha} != {expected_sha}"
            )
        actual[label] = sha
    return {
        "decision": EXP064_LOCKED_RUNTIME_DECISION,
        "runtime_version": EXP064_LOCKED_RUNTIME_VERSION,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "source_blobs": actual,
    }


def validate_workflow_text(text: str) -> None:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("DEC-455 workflow must be non-empty")
    required = (
        "name: phase8a-exp064-continuous-stability",
        "workflow_dispatch:",
        "name: exp064-preflight",
        "name: exp064-aggregate",
        "python scripts/phase8a_exp064.py preflight",
        "python scripts/phase8a_exp064.py require-execution",
        "python scripts/phase8a_exp064.py cell",
        "python scripts/phase8a_exp064.py aggregate",
        "requirements/exp061-discovery-run.txt",
    )
    for needle in required:
        if needle not in text:
            raise ValueError(f"DEC-455 workflow missing frozen source: {needle}")
    expected_cell_name = (
        "name: exp064-cell-${{ matrix.dataset.symbol }}-"
        "${{ matrix.dataset.timeframe }}-"
        "${{ matrix.dataset.horizon }}m"
    )
    if expected_cell_name not in text:
        raise ValueError("DEC-455 explicit cell job-name expression missing")
    if text.count("          - symbol:") != EXPECTED_CELL_COUNT:
        raise ValueError("DEC-455 workflow matrix must contain exactly 18 cells")
    if text.count("            horizon: 60") != 9:
        raise ValueError("DEC-455 workflow must contain nine 60m cells")
    if text.count("            horizon: 240") != 9:
        raise ValueError("DEC-455 workflow must contain nine 240m cells")
    predecessor_cell_clis = (
        "phase8a_exp061.py cell",
        "phase8a_exp062.py cell",
        "phase8a_exp063.py cell",
    )
    if any(needle in text for needle in predecessor_cell_clis):
        raise ValueError("DEC-455 workflow cannot invoke predecessor cell CLI")
    predecessor_aggregate_clis = (
        "phase8a_exp061.py aggregate",
        "phase8a_exp062.py aggregate",
        "phase8a_exp063.py aggregate",
    )
    if any(needle in text for needle in predecessor_aggregate_clis):
        raise ValueError("DEC-455 workflow cannot invoke predecessor aggregate CLI")


def validate_installed_runtime_paths(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    dormant = root / DORMANT_WORKFLOW_TEMPLATE_PATH
    active = root / ACTIVE_WORKFLOW_PATH
    cli = root / CLI_PATH
    for path in (dormant, active, cli):
        if not path.is_file():
            raise ValueError(f"DEC-455 installed source missing: {path}")

    dormant_bytes = dormant.read_bytes()
    active_bytes = active.read_bytes()
    if dormant_bytes != active_bytes:
        raise ValueError("DEC-455 active workflow differs from frozen template")
    text = dormant_bytes.decode("utf-8")
    validate_workflow_text(text)

    dormant_sha = _git_blob_sha(dormant)
    active_sha = _git_blob_sha(active)
    cli_sha = _git_blob_sha(cli)
    if EXPECTED_TEMPLATE_BLOB_SHA and dormant_sha != EXPECTED_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-455 dormant template Git blob mismatch")
    if EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA and active_sha != EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA:
        raise ValueError("DEC-455 active workflow Git blob mismatch")
    if EXPECTED_CLI_BLOB_SHA and cli_sha != EXPECTED_CLI_BLOB_SHA:
        raise ValueError("DEC-455 CLI Git blob mismatch")

    return {
        "decision": EXP064_LOCKED_RUNTIME_DECISION,
        "runtime_version": EXP064_LOCKED_RUNTIME_VERSION,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "dormant_template_blob_sha": dormant_sha,
        "active_workflow_blob_sha": active_sha,
        "cli_blob_sha": cli_sha,
        "workflow_installed": True,
        "workflow_dispatch_authorized": False,
        "historical_execution_authorized": False,
        "historical_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "phase8b_authorized": False,
        "trading_authorized": False,
    }


def require_historical_execution_authorized(*, code_commit: str) -> None:
    _validate_commit(code_commit)
    if not HISTORICAL_EXECUTION_AUTHORIZED:
        raise PermissionError(
            "DEC-455 historical EXP-064 execution remains locked"
        )


def run_contract_payload(*, code_commit: str) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    jobs = expected_job_names()
    artifacts = expected_artifact_names(code_commit=code_commit)
    if len(jobs) != EXPECTED_JOB_COUNT or len(set(jobs)) != EXPECTED_JOB_COUNT:
        raise ValueError("DEC-455 job inventory drift")
    if (
        len(artifacts) != EXPECTED_ARTIFACT_COUNT
        or len(set(artifacts)) != EXPECTED_ARTIFACT_COUNT
    ):
        raise ValueError("DEC-455 artifact inventory drift")

    return {
        "decision": EXP064_LOCKED_RUNTIME_DECISION,
        "runtime_version": EXP064_LOCKED_RUNTIME_VERSION,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "code_commit": code_commit,
        "workflow": {
            "name": WORKFLOW_NAME,
            "path": ACTIVE_WORKFLOW_PATH,
            "event": WORKFLOW_EVENT,
            "branch": WORKFLOW_BRANCH,
            "run_attempt": WORKFLOW_RUN_ATTEMPT,
        },
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
        },
        "authorizations": {
            "workflow_source_authorized": WORKFLOW_SOURCE_AUTHORIZED,
            "workflow_installed": WORKFLOW_INSTALLED,
            "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
            "historical_execution_authorized": HISTORICAL_EXECUTION_AUTHORIZED,
            "historical_result_authorized": HISTORICAL_RESULT_AUTHORIZED,
            "rerun_authorized": RERUN_AUTHORIZED,
            "retry_authorized": RETRY_AUTHORIZED,
            "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
            "reserved_robustness_access_authorized": (
                RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
            ),
            "candidate_compilation_authorized": (
                CANDIDATE_COMPILATION_AUTHORIZED
            ),
            "promotion_authorized": PROMOTION_AUTHORIZED,
            "phase8b_authorized": PHASE8B_AUTHORIZED,
            "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
            "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
            "live_order_authorized": LIVE_ORDER_AUTHORIZED,
            "real_money_authorized": REAL_MONEY_AUTHORIZED,
            "trading_authorized": TRADING_AUTHORIZED,
        },
    }


def runtime_source_payload(*, code_commit: str) -> dict[str, object]:
    code_commit = _validate_commit(code_commit)
    return {
        "decision": EXP064_LOCKED_RUNTIME_DECISION,
        "runtime_version": EXP064_LOCKED_RUNTIME_VERSION,
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "code_commit": code_commit,
        "dormant_template_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
        "active_workflow_path": ACTIVE_WORKFLOW_PATH,
        "cli_path": CLI_PATH,
        "runtime_requirements_path": RUNTIME_REQUIREMENTS_PATH,
        "feature_source_run": dict(FEATURE_RUN),
        "outcome_source_run": dict(OUTCOME_RUN),
        "feature_evidence_artifact": dict(FEATURE_EVIDENCE_ARTIFACT),
        "outcome_evidence_artifact": dict(OUTCOME_EVIDENCE_ARTIFACT),
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
        "run_contract": run_contract_payload(code_commit=code_commit),
        "authorizations": {
            "workflow_source_authorized": True,
            "workflow_installed": True,
            "workflow_dispatch_authorized": False,
            "historical_execution_authorized": False,
            "historical_result_authorized": False,
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


__all__ = [
    "ACTIVE_WORKFLOW_PATH",
    "AGGREGATE_JOB_NAME",
    "CLI_PATH",
    "DORMANT_WORKFLOW_TEMPLATE_PATH",
    "EXPECTED_ARTIFACT_COUNT",
    "EXPECTED_CELL_COUNT",
    "EXPECTED_CELLS",
    "EXPECTED_JOB_COUNT",
    "EXP064_LOCKED_RUNTIME_DECISION",
    "EXP064_LOCKED_RUNTIME_VERSION",
    "FEATURE_EVIDENCE_ARTIFACT",
    "FEATURE_RUN",
    "HISTORICAL_EXECUTION_AUTHORIZED",
    "OUTCOME_EVIDENCE_ARTIFACT",
    "OUTCOME_RUN",
    "PREFLIGHT_JOB_NAME",
    "RUNTIME_REQUIREMENTS_PATH",
    "WORKFLOW_DISPATCH_AUTHORIZED",
    "expected_aggregate_artifact_name",
    "expected_artifact_names",
    "expected_cell_artifact_name",
    "expected_cell_job_name",
    "expected_job_names",
    "expected_preflight_artifact_name",
    "require_historical_execution_authorized",
    "run_contract_payload",
    "runtime_source_payload",
    "source_artifacts_for_cell",
    "validate_installed_runtime_paths",
    "validate_runtime_dependencies",
    "validate_source_snapshots",
    "validate_workflow_text",
]
