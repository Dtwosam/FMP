from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Mapping

from .historical_plan_result_decision import (
    EXP061_REVIEWED_HISTORICAL_PLAN_DECISION,
    EXP061_REVIEWED_HISTORICAL_PLAN_VERSION,
)
from .historical_run_authorization import (
    HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED,
)
from .proof_result_decision import (
    EXP061_GATE_PROOF_HEAD_SHA,
    EXP061_GATE_PROOF_RUN_ID,
)
from .workflow_source import (
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED as LEGACY_EXECUTION_AUTHORIZED,
)


EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION = "DEC-285"
EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION = (
    "fmp-exp061-historical-execution-authorization-v1"
)

DEC284_REVIEWED_PLAN_SOURCE_BLOB_SHA = (
    "14d9c559eaa33e5cb217baaf3ed2597091735b18"
)
ACTIVE_WORKFLOW_BLOB_SHA = "d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9"
PATTERN_PROTOCOL_BLOB_SHA = "63b3f0121d6a50eb9e8e62ab666d70eb91791621"
PATTERN_MINER_BLOB_SHA = "495a67699eb5014e52129f0238a2737049fe38e6"
MARKET_LEARNING_ADAPTER_BLOB_SHA = "978a33554fad7e9d78b002778c4896be0af3333a"
RANGE_LIMITED_LOADER_BLOB_SHA = "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
RUN_CONTRACT_BLOB_SHA = "260eb6930673427266463517546969635188b143"
WORKFLOW_SOURCE_BLOB_SHA = "68566fc86ff3470cc8b6ebef606becaff9f3450b"
RUNTIME_REQUIREMENTS_BLOB_SHA = "1ff32214dee10d877a067e750cd69ffad96d5fe5"

EXPECTED_WORKFLOW_NAME = "phase8a-exp061-discovery"
EXPECTED_WORKFLOW_EVENT = "workflow_dispatch"
EXPECTED_WORKFLOW_REF = "refs/heads/main"
EXPECTED_REPOSITORY = "Dtwosam/FMP"
EXPECTED_WORKFLOW_RUN_NUMBER = 2
EXPECTED_WORKFLOW_RUN_ATTEMPT = 1

HISTORICAL_EXECUTION_SOURCE_AUTHORIZED = True
HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED = True
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = True
DISCOVERY_RESULT_AUTHORIZED = True
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


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _require_env(
    environment: Mapping[str, str],
    field: str,
    expected: str,
) -> None:
    actual = environment.get(field)
    if actual != expected:
        raise PermissionError(
            f"DEC-285 requires {field}={expected!r}; got {actual!r}"
        )


def validate_historical_execution_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "reviewed_plan": (
            root / "src/fmp/discovery/historical_plan_result_decision.py",
            DEC284_REVIEWED_PLAN_SOURCE_BLOB_SHA,
        ),
        "active_workflow": (
            root / ".github/workflows/phase8a-exp061-discovery.yml",
            ACTIVE_WORKFLOW_BLOB_SHA,
        ),
        "pattern_protocol": (
            root / "src/fmp/discovery/pattern_protocol.py",
            PATTERN_PROTOCOL_BLOB_SHA,
        ),
        "pattern_miner": (
            root / "src/fmp/discovery/pattern_miner.py",
            PATTERN_MINER_BLOB_SHA,
        ),
        "market_learning_adapter": (
            root / "src/fmp/discovery/market_learning_adapter.py",
            MARKET_LEARNING_ADAPTER_BLOB_SHA,
        ),
        "range_limited_loader": (
            root / "src/fmp/discovery/range_limited_loader.py",
            RANGE_LIMITED_LOADER_BLOB_SHA,
        ),
        "run_contract": (
            root / "src/fmp/discovery/run_contract.py",
            RUN_CONTRACT_BLOB_SHA,
        ),
        "legacy_workflow_source": (
            root / "src/fmp/discovery/workflow_source.py",
            WORKFLOW_SOURCE_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp061-discovery-run.txt",
            RUNTIME_REQUIREMENTS_BLOB_SHA,
        ),
    }

    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-285 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-285 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    if EXP061_REVIEWED_HISTORICAL_PLAN_DECISION != "DEC-284":
        raise ValueError("DEC-285 reviewed-plan predecessor decision drift")
    if EXP061_REVIEWED_HISTORICAL_PLAN_VERSION != (
        "fmp-exp061-reviewed-historical-plan-proof-v1"
    ):
        raise ValueError("DEC-285 reviewed-plan predecessor version drift")
    if LEGACY_EXECUTION_AUTHORIZED is not False:
        raise ValueError(
            "DEC-285 requires the frozen DEC-275 execution flag to stay false"
        )

    return {
        "decision": EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION,
        "version": EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION,
        "reviewed_plan_decision": EXP061_REVIEWED_HISTORICAL_PLAN_DECISION,
        "reviewed_plan_version": EXP061_REVIEWED_HISTORICAL_PLAN_VERSION,
        "reviewed_plan_source_blob_sha": actual["reviewed_plan"],
        "active_workflow_blob_sha": actual["active_workflow"],
        "pattern_protocol_blob_sha": actual["pattern_protocol"],
        "pattern_miner_blob_sha": actual["pattern_miner"],
        "market_learning_adapter_blob_sha": actual[
            "market_learning_adapter"
        ],
        "range_limited_loader_blob_sha": actual["range_limited_loader"],
        "run_contract_blob_sha": actual["run_contract"],
        "legacy_workflow_source_blob_sha": actual["legacy_workflow_source"],
        "runtime_requirements_blob_sha": actual["runtime_requirements"],
        "legacy_workflow_source_execution_authorized": False,
        "historical_execution_source_authorized": (
            HISTORICAL_EXECUTION_SOURCE_AUTHORIZED
        ),
        "historical_result_slot_source_authorized": (
            HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED
        ),
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "expected_workflow_name": EXPECTED_WORKFLOW_NAME,
        "expected_workflow_event": EXPECTED_WORKFLOW_EVENT,
        "expected_workflow_ref": EXPECTED_WORKFLOW_REF,
        "expected_repository": EXPECTED_REPOSITORY,
        "expected_workflow_run_number": EXPECTED_WORKFLOW_RUN_NUMBER,
        "expected_workflow_run_attempt": EXPECTED_WORKFLOW_RUN_ATTEMPT,
        "historical_data_start": "2015-01-01T00:00:00Z",
        "historical_data_end_exclusive": "2023-01-01T00:00:00Z",
        "reserved_robustness_start": "2023-01-01T00:00:00Z",
        "reserved_robustness_end_exclusive": "2026-08-21T00:00:00Z",
    }


def historical_execution_authorization_payload(
    *,
    code_commit: str,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit, field="code_commit")
    return {
        "decision": EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION,
        "version": EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION,
        "code_commit": code_commit,
        "reviewed_plan_decision": EXP061_REVIEWED_HISTORICAL_PLAN_DECISION,
        "reviewed_plan_version": EXP061_REVIEWED_HISTORICAL_PLAN_VERSION,
        "historical_execution_source_authorized": True,
        "historical_result_slot_source_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "expected_workflow_run_number": EXPECTED_WORKFLOW_RUN_NUMBER,
        "expected_workflow_run_attempt": EXPECTED_WORKFLOW_RUN_ATTEMPT,
        "proof_run_id": EXP061_GATE_PROOF_RUN_ID,
        "proof_head_sha": EXP061_GATE_PROOF_HEAD_SHA,
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
    }


def require_historical_execution_authorized(
    *,
    code_commit: str,
    environment: Mapping[str, str] | None = None,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit, field="code_commit")
    env = os.environ if environment is None else environment

    _require_env(env, "GITHUB_ACTIONS", "true")
    _require_env(env, "GITHUB_REPOSITORY", EXPECTED_REPOSITORY)
    _require_env(env, "GITHUB_WORKFLOW", EXPECTED_WORKFLOW_NAME)
    _require_env(env, "GITHUB_EVENT_NAME", EXPECTED_WORKFLOW_EVENT)
    _require_env(env, "GITHUB_REF", EXPECTED_WORKFLOW_REF)
    _require_env(env, "GITHUB_RUN_NUMBER", str(EXPECTED_WORKFLOW_RUN_NUMBER))
    _require_env(env, "GITHUB_RUN_ATTEMPT", str(EXPECTED_WORKFLOW_RUN_ATTEMPT))
    _require_env(env, "GITHUB_SHA", code_commit)

    run_id_raw = env.get("GITHUB_RUN_ID")
    try:
        run_id = int(run_id_raw or "")
    except ValueError as exc:
        raise PermissionError("DEC-285 requires a positive GITHUB_RUN_ID") from exc
    if run_id <= 0 or run_id == EXP061_GATE_PROOF_RUN_ID:
        raise PermissionError(
            "DEC-285 requires the distinct positive historical-result run id"
        )
    if code_commit == EXP061_GATE_PROOF_HEAD_SHA:
        raise PermissionError(
            "DEC-285 historical execution cannot reuse the gate-proof head"
        )

    return {
        **historical_execution_authorization_payload(
            code_commit=code_commit,
        ),
        "stage": "EXP061_HISTORICAL_EXECUTION_RUNTIME_AUTHORIZED",
        "runtime_workflow_run_id": run_id,
        "runtime_workflow_run_number": EXPECTED_WORKFLOW_RUN_NUMBER,
        "runtime_workflow_run_attempt": EXPECTED_WORKFLOW_RUN_ATTEMPT,
        "runtime_identity_verified": True,
    }


__all__ = [
    "DISCOVERY_RESULT_AUTHORIZED",
    "EXPECTED_WORKFLOW_RUN_ATTEMPT",
    "EXPECTED_WORKFLOW_RUN_NUMBER",
    "EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION",
    "EXP061_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "HISTORICAL_EXECUTION_SOURCE_AUTHORIZED",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "historical_execution_authorization_payload",
    "require_historical_execution_authorized",
    "validate_historical_execution_authorization_sources",
]
