from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .proof_result_decision import (
    EXP061_GATE_PROOF_HEAD_SHA,
    EXP061_GATE_PROOF_RUN_ID,
    EXP061_REVIEWED_GATE_PROOF_DECISION,
)
from .run_contract import (
    DISCOVERY_RESULT_AUTHORIZED as RUN_CONTRACT_DISCOVERY_RESULT_AUTHORIZED,
    EXPECTED_CELLS,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED as RUN_CONTRACT_EXECUTION_AUTHORIZED,
    REPLACEMENT_RUN_AUTHORIZED as RUN_CONTRACT_REPLACEMENT_AUTHORIZED,
    RERUN_AUTHORIZED as RUN_CONTRACT_RERUN_AUTHORIZED,
    RETRY_AUTHORIZED as RUN_CONTRACT_RETRY_AUTHORIZED,
    WORKFLOW_BRANCH,
    WORKFLOW_EVENT,
    WORKFLOW_NAME,
    WORKFLOW_PATH,
    WORKFLOW_RUN_ATTEMPT,
)
from .workflow_install import (
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED as INSTALL_HISTORICAL_DISPATCH_AUTHORIZED,
    PROOF_DISPATCH_AUTHORIZED as INSTALL_PROOF_DISPATCH_AUTHORIZED,
)
from .workflow_source import (
    CANDIDATE_COMPILATION_AUTHORIZED as SOURCE_CANDIDATE_COMPILATION_AUTHORIZED,
    DEMO_ORDER_AUTHORIZED as SOURCE_DEMO_ORDER_AUTHORIZED,
    DISCOVERY_RESULT_AUTHORIZED as SOURCE_DISCOVERY_RESULT_AUTHORIZED,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED as SOURCE_EXECUTION_AUTHORIZED,
    LIVE_ORDER_AUTHORIZED as SOURCE_LIVE_ORDER_AUTHORIZED,
    PHASE8B_AUTHORIZED as SOURCE_PHASE8B_AUTHORIZED,
    PROMOTION_AUTHORIZED as SOURCE_PROMOTION_AUTHORIZED,
    REAL_MONEY_AUTHORIZED as SOURCE_REAL_MONEY_AUTHORIZED,
    RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED as SOURCE_RESERVED_ACCESS_AUTHORIZED,
    TRADING_AUTHORIZED as SOURCE_TRADING_AUTHORIZED,
    WORKFLOW_DISPATCH_AUTHORIZED as SOURCE_WORKFLOW_DISPATCH_AUTHORIZED,
)


EXP061_HISTORICAL_RUN_AUTHORIZATION_DECISION = "DEC-281"
EXP061_HISTORICAL_RUN_AUTHORIZATION_VERSION = (
    "fmp-exp061-historical-run-authorization-v1"
)

DEC280_MERGED_COMMIT = "da40f1cf3b45b111bb87099353ec79d5f2b95918"
DEC280_REVIEWED_PROOF_SOURCE_BLOB_SHA = "fbed3788ab0c1c1e00dccfe0f84a293ff04f6ccd"

PATTERN_PROTOCOL_BLOB_SHA = "63b3f0121d6a50eb9e8e62ab666d70eb91791621"
PATTERN_MINER_BLOB_SHA = "495a67699eb5014e52129f0238a2737049fe38e6"
MARKET_LEARNING_ADAPTER_BLOB_SHA = "978a33554fad7e9d78b002778c4896be0af3333a"
RANGE_LIMITED_LOADER_BLOB_SHA = "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
RUN_CONTRACT_BLOB_SHA = "260eb6930673427266463517546969635188b143"
WORKFLOW_SOURCE_BLOB_SHA = "68566fc86ff3470cc8b6ebef606becaff9f3450b"
WORKFLOW_INSTALL_BLOB_SHA = "e959a782fdbb6bf5b578e60e44f5e015b50086a6"
PROOF_CONTRACT_BLOB_SHA = "4c0a6f58e5611cfeb14eed15f62893e8956f09a7"
ACTIVE_WORKFLOW_BLOB_SHA = "d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9"
EXP061_CLI_BLOB_SHA = "bd40f17566f4c03e623215fe9e615b00b2fc9039"
RUNTIME_REQUIREMENTS_BLOB_SHA = "1ff32214dee10d877a067e750cd69ffad96d5fe5"

EXPECTED_PROOF_RUN = {
    "id": EXP061_GATE_PROOF_RUN_ID,
    "name": WORKFLOW_NAME,
    "path": WORKFLOW_PATH,
    "event": WORKFLOW_EVENT,
    "head_branch": WORKFLOW_BRANCH,
    "head_sha": EXP061_GATE_PROOF_HEAD_SHA,
    "run_attempt": WORKFLOW_RUN_ATTEMPT,
    "status": "completed",
    "conclusion": "failure",
}

HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED = True
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
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


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def validate_historical_run_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    if EXP061_REVIEWED_GATE_PROOF_DECISION != "DEC-280":
        raise ValueError("EXP-061 reviewed-proof decision drift")

    for field, value in (
        ("run-contract execution", RUN_CONTRACT_EXECUTION_AUTHORIZED),
        ("run-contract result", RUN_CONTRACT_DISCOVERY_RESULT_AUTHORIZED),
        ("run-contract rerun", RUN_CONTRACT_RERUN_AUTHORIZED),
        ("run-contract retry", RUN_CONTRACT_RETRY_AUTHORIZED),
        ("run-contract replacement", RUN_CONTRACT_REPLACEMENT_AUTHORIZED),
        ("workflow-source dispatch", SOURCE_WORKFLOW_DISPATCH_AUTHORIZED),
        ("workflow-source execution", SOURCE_EXECUTION_AUTHORIZED),
        ("workflow-source result", SOURCE_DISCOVERY_RESULT_AUTHORIZED),
        ("workflow-install proof dispatch", INSTALL_PROOF_DISPATCH_AUTHORIZED),
        (
            "workflow-install historical dispatch",
            INSTALL_HISTORICAL_DISPATCH_AUTHORIZED,
        ),
        ("reserved robustness access", SOURCE_RESERVED_ACCESS_AUTHORIZED),
        ("candidate compilation", SOURCE_CANDIDATE_COMPILATION_AUTHORIZED),
        ("promotion", SOURCE_PROMOTION_AUTHORIZED),
        ("phase8b", SOURCE_PHASE8B_AUTHORIZED),
        ("demo orders", SOURCE_DEMO_ORDER_AUTHORIZED),
        ("live orders", SOURCE_LIVE_ORDER_AUTHORIZED),
        ("real money", SOURCE_REAL_MONEY_AUTHORIZED),
        ("trading", SOURCE_TRADING_AUTHORIZED),
    ):
        if value is not False:
            raise ValueError(f"EXP-061 {field} must remain false before DEC-281")

    expected = {
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
        "workflow_source": (
            root / "src/fmp/discovery/workflow_source.py",
            WORKFLOW_SOURCE_BLOB_SHA,
        ),
        "workflow_install": (
            root / "src/fmp/discovery/workflow_install.py",
            WORKFLOW_INSTALL_BLOB_SHA,
        ),
        "proof_contract": (
            root / "src/fmp/discovery/proof_contract.py",
            PROOF_CONTRACT_BLOB_SHA,
        ),
        "reviewed_proof": (
            root / "src/fmp/discovery/proof_result_decision.py",
            DEC280_REVIEWED_PROOF_SOURCE_BLOB_SHA,
        ),
        "active_workflow": (
            root / ".github/workflows/phase8a-exp061-discovery.yml",
            ACTIVE_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root / "scripts/phase8a_exp061.py",
            EXP061_CLI_BLOB_SHA,
        ),
        "runtime_requirements": (
            root / "requirements/exp061-discovery-run.txt",
            RUNTIME_REQUIREMENTS_BLOB_SHA,
        ),
    }

    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing EXP-061 historical-run dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-061 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        "decision": EXP061_HISTORICAL_RUN_AUTHORIZATION_DECISION,
        "authorization_version": EXP061_HISTORICAL_RUN_AUTHORIZATION_VERSION,
        "dec280_merged_commit": DEC280_MERGED_COMMIT,
        "reviewed_proof_blob_sha": actual["reviewed_proof"],
        "active_workflow_blob_sha": actual["active_workflow"],
        "cli_blob_sha": actual["cli"],
        "runtime_requirements_blob_sha": actual["runtime_requirements"],
        "run_contract_blob_sha": actual["run_contract"],
        "workflow_source_blob_sha": actual["workflow_source"],
        "workflow_install_blob_sha": actual["workflow_install"],
        "pattern_protocol_blob_sha": actual["pattern_protocol"],
        "pattern_miner_blob_sha": actual["pattern_miner"],
        "market_learning_adapter_blob_sha": actual["market_learning_adapter"],
        "range_limited_loader_blob_sha": actual["range_limited_loader"],
        "proof_contract_blob_sha": actual["proof_contract"],
        "expected_cell_count": len(EXPECTED_CELLS),
        "historical_data_start": "2015-01-01T00:00:00Z",
        "historical_data_end_exclusive": "2023-01-01T00:00:00Z",
        "reserved_robustness_start": "2023-01-01T00:00:00Z",
        "reserved_robustness_end_exclusive": "2026-08-21T00:00:00Z",
        "proof_run_excluded_from_historical_result_slot": True,
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
    }


def classify_historical_run_inventory(
    workflow_runs_payload: Mapping[str, object],
) -> dict[str, object]:
    raw = workflow_runs_payload.get("workflow_runs")
    if not isinstance(raw, list):
        raise ValueError("EXP-061 workflow-run payload must contain workflow_runs")

    relevant: list[Mapping[str, object]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("EXP-061 workflow-run row is malformed")
        if (
            item.get("name") == WORKFLOW_NAME
            and item.get("path") == WORKFLOW_PATH
            and item.get("event") == WORKFLOW_EVENT
            and item.get("head_branch") == WORKFLOW_BRANCH
        ):
            relevant.append(item)

    proof_rows = [
        item for item in relevant if item.get("id") == EXP061_GATE_PROOF_RUN_ID
    ]
    if len(proof_rows) != 1:
        raise ValueError("EXP-061 requires exactly the frozen DEC-280 proof run")
    _require_exact(
        proof_rows[0],
        EXPECTED_PROOF_RUN,
        prefix="EXP-061 frozen proof run",
    )

    historical_rows = [
        item for item in relevant if item.get("id") != EXP061_GATE_PROOF_RUN_ID
    ]
    if len(historical_rows) > 1:
        raise ValueError("EXP-061 historical-result slot has multiple attempts")

    if not historical_rows:
        return {
            "decision": EXP061_HISTORICAL_RUN_AUTHORIZATION_DECISION,
            "stage": "EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE",
            "proof_run_id": EXP061_GATE_PROOF_RUN_ID,
            "proof_head_sha": EXP061_GATE_PROOF_HEAD_SHA,
            "proof_run_count": 1,
            "historical_result_attempt_count": 0,
            "historical_result_run_id": None,
            "historical_result_head_sha": None,
            "historical_result_run_status": None,
            "historical_result_run_conclusion": None,
            "historical_result_slot_consumed": False,
            "historical_result_slot_source_authorized": (
                HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED
            ),
            "historical_result_dispatch_authorized": False,
            "historical_discovery_execution_authorized": False,
            "discovery_result_authorized": False,
            "rerun_authorized": False,
            "retry_authorized": False,
            "replacement_run_authorized": False,
        }

    run = historical_rows[0]
    run_id = run.get("id")
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        raise ValueError("EXP-061 historical-result run id is invalid")
    if run.get("run_attempt") != WORKFLOW_RUN_ATTEMPT:
        raise ValueError("EXP-061 historical-result run attempt must remain 1")
    head_sha = _validate_commit(
        run.get("head_sha"),
        field="EXP-061 historical-result head",
    )
    status = run.get("status")
    if not isinstance(status, str) or not status:
        raise ValueError("EXP-061 historical-result run status is malformed")
    conclusion = run.get("conclusion")
    if status == "completed" and not isinstance(conclusion, str):
        raise ValueError(
            "completed EXP-061 historical-result run requires a conclusion"
        )
    if status != "completed" and conclusion is not None:
        raise ValueError(
            "non-terminal EXP-061 historical-result run cannot have a conclusion"
        )

    return {
        "decision": EXP061_HISTORICAL_RUN_AUTHORIZATION_DECISION,
        "stage": "EXP061_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED",
        "proof_run_id": EXP061_GATE_PROOF_RUN_ID,
        "proof_head_sha": EXP061_GATE_PROOF_HEAD_SHA,
        "proof_run_count": 1,
        "historical_result_attempt_count": 1,
        "historical_result_run_id": run_id,
        "historical_result_head_sha": head_sha,
        "historical_result_run_status": status,
        "historical_result_run_conclusion": conclusion,
        "historical_result_slot_consumed": True,
        "historical_result_slot_source_authorized": (
            HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED
        ),
        "historical_result_dispatch_authorized": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
    }


def build_historical_run_authorization_contract(
    *,
    repository_root: Path,
    workflow_runs_payload: Mapping[str, object],
) -> dict[str, object]:
    source = validate_historical_run_authorization_sources(
        repository_root=repository_root,
    )
    inventory = classify_historical_run_inventory(workflow_runs_payload)
    if inventory["stage"] != "EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE":
        raise ValueError(
            "EXP-061 historical-result source authorization requires an unused slot"
        )

    return {
        **source,
        **inventory,
        "stage": "EXP061_HISTORICAL_RESULT_SOURCE_AUTHORIZED_DISPATCH_LOCKED",
        "terminal_outcome_consumes_slot": True,
        "proof_retry_or_replacement_authorized": False,
        "next_action": (
            "A later decision may add a read-only exact-main operator for the "
            "single historical-result slot. DEC-281 itself provides no dispatch "
            "or execution path."
        ),
    }


__all__ = [
    "DEC280_MERGED_COMMIT",
    "EXP061_HISTORICAL_RUN_AUTHORIZATION_DECISION",
    "EXP061_HISTORICAL_RUN_AUTHORIZATION_VERSION",
    "EXPECTED_PROOF_RUN",
    "HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED",
    "build_historical_run_authorization_contract",
    "classify_historical_run_inventory",
    "validate_historical_run_authorization_sources",
]
