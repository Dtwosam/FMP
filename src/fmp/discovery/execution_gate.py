from __future__ import annotations

import hashlib
from pathlib import Path

from .pattern_protocol import (
    DISCOVERY_EXECUTION_AUTHORIZED as PROTOCOL_DISCOVERY_EXECUTION_AUTHORIZED,
    DISCOVERY_RESULT_AUTHORIZED as PROTOCOL_DISCOVERY_RESULT_AUTHORIZED,
    RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED as PROTOCOL_RESERVED_ACCESS_AUTHORIZED,
    SOURCE_ACCESS_AUTHORIZED as PROTOCOL_SOURCE_ACCESS_AUTHORIZED,
)
from .pattern_miner import (
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED as MINER_EXECUTION_AUTHORIZED,
    HISTORICAL_SOURCE_ACCESS_AUTHORIZED as MINER_SOURCE_ACCESS_AUTHORIZED,
    RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED as MINER_RESERVED_ACCESS_AUTHORIZED,
)
from .range_limited_loader import (
    DISCOVERY_RESULT_AUTHORIZED as LOADER_RESULT_AUTHORIZED,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED as LOADER_EXECUTION_AUTHORIZED,
    RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED as LOADER_RESERVED_ACCESS_AUTHORIZED,
)
from .run_contract import (
    DISCOVERY_RESULT_AUTHORIZED as CONTRACT_RESULT_AUTHORIZED,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED as CONTRACT_EXECUTION_AUTHORIZED,
    REPLACEMENT_RUN_AUTHORIZED as CONTRACT_REPLACEMENT_AUTHORIZED,
    RERUN_AUTHORIZED as CONTRACT_RERUN_AUTHORIZED,
    RETRY_AUTHORIZED as CONTRACT_RETRY_AUTHORIZED,
    WORKFLOW_DISPATCH_AUTHORIZED as CONTRACT_DISPATCH_AUTHORIZED,
    WORKFLOW_PATH,
)


EXP061_WORKFLOW_SOURCE_DECISION = "DEC-275"
EXP061_WORKFLOW_SOURCE_VERSION = "fmp-exp061-workflow-source-v1"
AUTHORIZED_PYTHON_VERSION = "3.12.14"

PROTOCOL_SOURCE_BLOB_SHA = "63b3f0121d6a50eb9e8e62ab666d70eb91791621"
MINER_SOURCE_BLOB_SHA = "495a67699eb5014e52129f0238a2737049fe38e6"
ADAPTER_SOURCE_BLOB_SHA = "978a33554fad7e9d78b002778c4896be0af3333a"
LOADER_SOURCE_BLOB_SHA = "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
RUN_CONTRACT_SOURCE_BLOB_SHA = "260eb6930673427266463517546969635188b143"
WORKFLOW_BLOB_SHA = "b3906c46b4d1b7d47564006172ee4f1a77b93a39"
CLI_BLOB_SHA = "56fd0db28e67cfd76f4c68f4e5efe02d584595e7"
RUNTIME_REQUIREMENTS_BLOB_SHA = "d25ab16056b9f5df283147d67b8f401f60ae7520"

PYPROJECT_BLOB_SHA = "de850a1ba397fc69ba634ecf178d732b5012c378"
PHASE2_ARTIFACTS_BLOB_SHA = "595152127749969a1eb0fd158636d5c289fc2531"
FEATURE_SCHEMA_BLOB_SHA = "afbddc84676faadb8660b4da03c6abeb10cd2a13"
MARKET_CONTRACTS_BLOB_SHA = "4c5a75232e66715c0829e545d8659f59fb8b7724"
MARKET_FEATURE_EVIDENCE_BLOB_SHA = "e78cb7c81e09c2c773a2603a546636d39a36cdab"
MARKET_OUTCOME_EVIDENCE_BLOB_SHA = "b6bda6a89a56d6f4ba5dadd2f489775e612ab066"
MARKET_OUTCOMES_BLOB_SHA = "c83fefd4252b2fe426af97686f86e43021760c77"

EXP061_WORKFLOW_SOURCE_FROZEN = True
WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_SOURCE_OPEN_AUTHORIZED = False
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


def validate_exp061_workflow_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    predecessor_locks = (
        ("protocol source access", PROTOCOL_SOURCE_ACCESS_AUTHORIZED),
        ("protocol discovery execution", PROTOCOL_DISCOVERY_EXECUTION_AUTHORIZED),
        ("protocol discovery result", PROTOCOL_DISCOVERY_RESULT_AUTHORIZED),
        ("protocol reserved access", PROTOCOL_RESERVED_ACCESS_AUTHORIZED),
        ("miner source access", MINER_SOURCE_ACCESS_AUTHORIZED),
        ("miner discovery execution", MINER_EXECUTION_AUTHORIZED),
        ("miner reserved access", MINER_RESERVED_ACCESS_AUTHORIZED),
        ("loader discovery execution", LOADER_EXECUTION_AUTHORIZED),
        ("loader discovery result", LOADER_RESULT_AUTHORIZED),
        ("loader reserved access", LOADER_RESERVED_ACCESS_AUTHORIZED),
        ("run-contract dispatch", CONTRACT_DISPATCH_AUTHORIZED),
        ("run-contract execution", CONTRACT_EXECUTION_AUTHORIZED),
        ("run-contract result", CONTRACT_RESULT_AUTHORIZED),
        ("run-contract rerun", CONTRACT_RERUN_AUTHORIZED),
        ("run-contract retry", CONTRACT_RETRY_AUTHORIZED),
        ("run-contract replacement", CONTRACT_REPLACEMENT_AUTHORIZED),
    )
    for label, value in predecessor_locks:
        if value is not False:
            raise ValueError(f"EXP-061 predecessor {label} authorization drift")

    if WORKFLOW_PATH != ".github/workflows/phase8a-exp061-discovery.yml":
        raise ValueError("EXP-061 workflow path contract drift")

    expected = {
        "pattern_protocol": (
            root / "src/fmp/discovery/pattern_protocol.py",
            PROTOCOL_SOURCE_BLOB_SHA,
        ),
        "pattern_miner": (
            root / "src/fmp/discovery/pattern_miner.py",
            MINER_SOURCE_BLOB_SHA,
        ),
        "market_learning_adapter": (
            root / "src/fmp/discovery/market_learning_adapter.py",
            ADAPTER_SOURCE_BLOB_SHA,
        ),
        "range_limited_loader": (
            root / "src/fmp/discovery/range_limited_loader.py",
            LOADER_SOURCE_BLOB_SHA,
        ),
        "run_contract": (
            root / "src/fmp/discovery/run_contract.py",
            RUN_CONTRACT_SOURCE_BLOB_SHA,
        ),
        "workflow": (
            root / WORKFLOW_PATH,
            WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root / "scripts/phase8a_exp061_discovery.py",
            CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp061-discovery-run.txt",
            RUNTIME_REQUIREMENTS_BLOB_SHA,
        ),
        "pyproject": (
            root / "pyproject.toml",
            PYPROJECT_BLOB_SHA,
        ),
        "phase2_artifacts": (
            root / "src/fmp/data/phase2/artifacts.py",
            PHASE2_ARTIFACTS_BLOB_SHA,
        ),
        "feature_schema": (
            root / "src/fmp/features/schema.py",
            FEATURE_SCHEMA_BLOB_SHA,
        ),
        "market_contracts": (
            root / "src/fmp/market_learning/contracts.py",
            MARKET_CONTRACTS_BLOB_SHA,
        ),
        "market_feature_evidence": (
            root / "src/fmp/market_learning/evidence.py",
            MARKET_FEATURE_EVIDENCE_BLOB_SHA,
        ),
        "market_outcome_evidence": (
            root / "src/fmp/market_learning/outcome_evidence.py",
            MARKET_OUTCOME_EVIDENCE_BLOB_SHA,
        ),
        "market_outcomes": (
            root / "src/fmp/market_learning/outcomes.py",
            MARKET_OUTCOMES_BLOB_SHA,
        ),
    }

    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing EXP-061 workflow dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-061 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        "decision": EXP061_WORKFLOW_SOURCE_DECISION,
        "workflow_source_version": EXP061_WORKFLOW_SOURCE_VERSION,
        "authorized_python_version": AUTHORIZED_PYTHON_VERSION,
        "source_blobs": actual,
        "workflow_source_frozen": EXP061_WORKFLOW_SOURCE_FROZEN,
        "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_source_open_authorized": HISTORICAL_SOURCE_OPEN_AUTHORIZED,
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
    }


def build_exp061_workflow_source_gate(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_exp061_workflow_sources(repository_root=repository_root)
    return {
        **source,
        "stage": "EXP061_WORKFLOW_SOURCE_FROZEN_EXECUTION_LOCKED",
        "next_action": (
            "A later decision must add terminal review, prove zero prior manual-main "
            "EXP-061 runs, add a first-run guard, and separately authorize at most "
            "one historical discovery attempt. DEC-275 itself cannot dispatch."
        ),
    }


def require_exp061_historical_execution(
    *,
    repository_root: Path,
    code_commit: str,
) -> dict[str, object]:
    source = validate_exp061_workflow_sources(repository_root=repository_root)
    commit = _validate_commit(code_commit, field="EXP-061 code commit")

    required_true = (
        WORKFLOW_DISPATCH_AUTHORIZED,
        HISTORICAL_SOURCE_OPEN_AUTHORIZED,
        HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
        DISCOVERY_RESULT_AUTHORIZED,
    )
    if not all(required_true):
        raise PermissionError(
            "DEC-275 EXP-061 historical discovery execution authorization is locked"
        )

    return {
        **source,
        "code_commit": commit,
        "stage": "EXP061_HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    }


__all__ = [
    "ADAPTER_SOURCE_BLOB_SHA",
    "AUTHORIZED_PYTHON_VERSION",
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_COMPILATION_AUTHORIZED",
    "CLI_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "DISCOVERY_RESULT_AUTHORIZED",
    "EXP061_WORKFLOW_SOURCE_DECISION",
    "EXP061_WORKFLOW_SOURCE_FROZEN",
    "EXP061_WORKFLOW_SOURCE_VERSION",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "HISTORICAL_SOURCE_OPEN_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "LOADER_SOURCE_BLOB_SHA",
    "MINER_SOURCE_BLOB_SHA",
    "PHASE8B_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "PROTOCOL_SOURCE_BLOB_SHA",
    "REAL_MONEY_AUTHORIZED",
    "REPLACEMENT_RUN_AUTHORIZED",
    "RERUN_AUTHORIZED",
    "RETRY_AUTHORIZED",
    "RUN_CONTRACT_SOURCE_BLOB_SHA",
    "RUNTIME_REQUIREMENTS_BLOB_SHA",
    "TRADING_AUTHORIZED",
    "WORKFLOW_BLOB_SHA",
    "WORKFLOW_DISPATCH_AUTHORIZED",
    "build_exp061_workflow_source_gate",
    "require_exp061_historical_execution",
    "validate_exp061_workflow_sources",
]
