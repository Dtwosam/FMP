from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Mapping

from .exp063_historical_run_authorization import (
    HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED as DEC448_SLOT_SOURCE_AUTHORIZED,
)
from .exp063_runtime_source import (
    HISTORICAL_EXECUTION_AUTHORIZED as DEC447_EXECUTION_AUTHORIZED,
)


EXP063_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION = "DEC-449"
EXP063_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION = (
    "fmp-exp063-historical-execution-authorization-v1"
)

DEC448_MERGE_SHA = "ee38ea4224345e2ed0a2c4a4baa9913b0589c8a0"
DEC448_RUN_AUTHORIZATION_BLOB_SHA = (
    "f6070b1ecc8951338767b24dac1f0ff9ec7a24ae"
)
ACTIVE_WORKFLOW_BLOB_SHA = "1038beb4b704ddead4e5841a6f799858732189e6"
EVIDENCE_CONTRACT_BLOB_SHA = "e8614beb156d24584b82611db47afb8c00ece71c"
PERSISTENCE_MINER_BLOB_SHA = "40c49a372b35dbc113dbfb71374b1ae5fc7acc45"
PERSISTENCE_PROTOCOL_BLOB_SHA = "2c781dd2811b66d2d88f008007bf5c8bcf99f14f"
REPAIRED_ADAPTER_BLOB_SHA = "491ba8c92cb6e6e4c715bfb1ecb934b6949e1596"
RANGE_LIMITED_LOADER_BLOB_SHA = "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
RUNTIME_REQUIREMENTS_BLOB_SHA = "1ff32214dee10d877a067e750cd69ffad96d5fe5"
ACTIVATED_CLI_BLOB_SHA = ""

EXPECTED_REPOSITORY = "Dtwosam/FMP"
EXPECTED_WORKFLOW_NAME = "phase8a-exp063-persistence"
EXPECTED_WORKFLOW_EVENT = "workflow_dispatch"
EXPECTED_WORKFLOW_REF = "refs/heads/main"
EXPECTED_WORKFLOW_RUN_NUMBER = 1
EXPECTED_WORKFLOW_RUN_ATTEMPT = 1

HISTORICAL_EXECUTION_SOURCE_AUTHORIZED = True
HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED = True
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = True
HISTORICAL_EXECUTION_AUTHORIZED = True
HISTORICAL_RESULT_AUTHORIZED = True
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
            f"DEC-449 requires {field}={expected!r}; got {actual!r}"
        )


def validate_historical_execution_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    if DEC448_SLOT_SOURCE_AUTHORIZED is not True:
        raise ValueError("DEC-449 requires the DEC-448 one-shot slot")
    if DEC447_EXECUTION_AUTHORIZED is not False:
        raise ValueError(
            "DEC-449 requires the frozen DEC-447 execution flag to stay false"
        )

    expected = {
        "dec448_run_authorization": (
            root / "src/fmp/discovery/exp063_historical_run_authorization.py",
            DEC448_RUN_AUTHORIZATION_BLOB_SHA,
        ),
        "active_workflow": (
            root / ".github/workflows/phase8a-exp063-persistence.yml",
            ACTIVE_WORKFLOW_BLOB_SHA,
        ),
        "evidence_contract": (
            root / "src/fmp/discovery/exp063_evidence_contract.py",
            EVIDENCE_CONTRACT_BLOB_SHA,
        ),
        "persistence_miner": (
            root / "src/fmp/discovery/exp063_persistence_miner.py",
            PERSISTENCE_MINER_BLOB_SHA,
        ),
        "persistence_protocol": (
            root / "src/fmp/discovery/exp063_persistence_protocol.py",
            PERSISTENCE_PROTOCOL_BLOB_SHA,
        ),
        "repaired_adapter": (
            root / "src/fmp/discovery/exp062_nonfinite_feature_adapter.py",
            REPAIRED_ADAPTER_BLOB_SHA,
        ),
        "range_limited_loader": (
            root / "src/fmp/discovery/range_limited_loader.py",
            RANGE_LIMITED_LOADER_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp061-discovery-run.txt",
            RUNTIME_REQUIREMENTS_BLOB_SHA,
        ),
    }
    if ACTIVATED_CLI_BLOB_SHA:
        expected["activated_cli"] = (
            root / "scripts/phase8a_exp063.py",
            ACTIVATED_CLI_BLOB_SHA,
        )

    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-449 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-449 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        "decision": EXP063_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION,
        "version": EXP063_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION,
        "dec448_merge_sha": DEC448_MERGE_SHA,
        "dec448_run_authorization_blob_sha": actual[
            "dec448_run_authorization"
        ],
        "active_workflow_blob_sha": actual["active_workflow"],
        "evidence_contract_blob_sha": actual["evidence_contract"],
        "persistence_miner_blob_sha": actual["persistence_miner"],
        "persistence_protocol_blob_sha": actual["persistence_protocol"],
        "repaired_adapter_blob_sha": actual["repaired_adapter"],
        "range_limited_loader_blob_sha": actual["range_limited_loader"],
        "runtime_requirements_blob_sha": actual["runtime_requirements"],
        "activated_cli_blob_sha": actual.get("activated_cli"),
        "historical_execution_source_authorized": True,
        "historical_result_slot_source_authorized": True,
        "historical_result_dispatch_authorized": True,
        "historical_execution_authorized": True,
        "historical_result_authorized": True,
        "expected_repository": EXPECTED_REPOSITORY,
        "expected_workflow_name": EXPECTED_WORKFLOW_NAME,
        "expected_workflow_event": EXPECTED_WORKFLOW_EVENT,
        "expected_workflow_ref": EXPECTED_WORKFLOW_REF,
        "expected_workflow_run_number": EXPECTED_WORKFLOW_RUN_NUMBER,
        "expected_workflow_run_attempt": EXPECTED_WORKFLOW_RUN_ATTEMPT,
        "historical_data_start": "2015-01-01T00:00:00Z",
        "historical_data_end_exclusive": "2023-01-01T00:00:00Z",
        "reserved_robustness_start": "2023-01-01T00:00:00Z",
        "reserved_robustness_end_exclusive": "2026-08-21T00:00:00Z",
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


def historical_execution_authorization_payload(
    *,
    code_commit: str,
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit, field="code_commit")
    return {
        "decision": EXP063_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION,
        "version": EXP063_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION,
        "code_commit": code_commit,
        "historical_execution_source_authorized": True,
        "historical_result_slot_source_authorized": True,
        "historical_result_dispatch_authorized": True,
        "historical_execution_authorized": True,
        "historical_result_authorized": True,
        "expected_workflow_run_number": EXPECTED_WORKFLOW_RUN_NUMBER,
        "expected_workflow_run_attempt": EXPECTED_WORKFLOW_RUN_ATTEMPT,
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
    repository_root: Path = Path("."),
) -> dict[str, object]:
    code_commit = _validate_commit(code_commit, field="code_commit")
    source = validate_historical_execution_authorization_sources(
        repository_root=repository_root,
    )
    env = os.environ if environment is None else environment

    _require_env(env, "GITHUB_ACTIONS", "true")
    _require_env(env, "GITHUB_REPOSITORY", EXPECTED_REPOSITORY)
    _require_env(env, "GITHUB_WORKFLOW", EXPECTED_WORKFLOW_NAME)
    _require_env(env, "GITHUB_EVENT_NAME", EXPECTED_WORKFLOW_EVENT)
    _require_env(env, "GITHUB_REF", EXPECTED_WORKFLOW_REF)
    _require_env(
        env,
        "GITHUB_RUN_NUMBER",
        str(EXPECTED_WORKFLOW_RUN_NUMBER),
    )
    _require_env(
        env,
        "GITHUB_RUN_ATTEMPT",
        str(EXPECTED_WORKFLOW_RUN_ATTEMPT),
    )
    _require_env(env, "GITHUB_SHA", code_commit)

    run_id_raw = env.get("GITHUB_RUN_ID")
    try:
        run_id = int(run_id_raw or "")
    except ValueError as exc:
        raise PermissionError(
            "DEC-449 requires a positive GITHUB_RUN_ID"
        ) from exc
    if run_id <= 0:
        raise PermissionError(
            "DEC-449 requires a positive GITHUB_RUN_ID"
        )

    return {
        **source,
        **historical_execution_authorization_payload(
            code_commit=code_commit,
        ),
        "stage": "EXP063_ONE_SHOT_HISTORICAL_EXECUTION_RUNTIME_AUTHORIZED",
        "runtime_workflow_run_id": run_id,
        "runtime_workflow_run_number": EXPECTED_WORKFLOW_RUN_NUMBER,
        "runtime_workflow_run_attempt": EXPECTED_WORKFLOW_RUN_ATTEMPT,
        "runtime_identity_verified": True,
    }


__all__ = [
    "EXPECTED_WORKFLOW_RUN_ATTEMPT",
    "EXPECTED_WORKFLOW_RUN_NUMBER",
    "EXP063_HISTORICAL_EXECUTION_AUTHORIZATION_DECISION",
    "EXP063_HISTORICAL_EXECUTION_AUTHORIZATION_VERSION",
    "HISTORICAL_EXECUTION_AUTHORIZED",
    "HISTORICAL_EXECUTION_SOURCE_AUTHORIZED",
    "HISTORICAL_RESULT_AUTHORIZED",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "historical_execution_authorization_payload",
    "require_historical_execution_authorized",
    "validate_historical_execution_authorization_sources",
]
