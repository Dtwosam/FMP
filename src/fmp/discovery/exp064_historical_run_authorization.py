from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .exp064_runtime_source import (
    ACTIVE_WORKFLOW_PATH,
    HISTORICAL_EXECUTION_AUTHORIZED as DEC455_EXECUTION_AUTHORIZED,
    WORKFLOW_BRANCH,
    WORKFLOW_DISPATCH_AUTHORIZED as DEC455_DISPATCH_AUTHORIZED,
    WORKFLOW_EVENT,
    WORKFLOW_NAME,
)


EXP064_HISTORICAL_RUN_AUTHORIZATION_DECISION = "DEC-456"
EXP064_HISTORICAL_RUN_AUTHORIZATION_VERSION = (
    "fmp-exp064-historical-run-authorization-v1"
)

DEC455_MERGE_SHA = "c388def44d251c96832572f07de43d9dc6a909ee"
DEC455_RUNTIME_SOURCE_BLOB_SHA = (
    "07e5ccebb6416c04621aa54e170cd4eb1e0a2a04"
)
DEC455_ACTIVE_WORKFLOW_BLOB_SHA = (
    "caca62672ad9796764c18be6b8da9785b98c9733"
)
DEC455_CLI_BLOB_SHA = "a44aed6d890e25a781b7b92d7efb3dabe06f9047"
DEC454_EVIDENCE_CONTRACT_BLOB_SHA = (
    "9aee3f9e273e20329c9de5a7079ed924ffee0a9a"
)
DEC453_MINER_BLOB_SHA = "b0d799ec1afaf43b0441290c97a9f39c37ecd2fd"
DEC452_PROTOCOL_BLOB_SHA = "c108ea047c7bfb3e588bfbac33993180066c28ad"

EXPECTED_WORKFLOW_PATH = ACTIVE_WORKFLOW_PATH
EXPECTED_WORKFLOW_EVENT = WORKFLOW_EVENT
EXPECTED_WORKFLOW_BRANCH = WORKFLOW_BRANCH
EXPECTED_FIRST_RUN_NUMBER = 1
EXPECTED_RUN_ATTEMPT = 1

HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED = True
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
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


def validate_historical_run_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)

    if DEC455_DISPATCH_AUTHORIZED is not False:
        raise ValueError("DEC-456 requires DEC-455 dispatch to remain false")
    if DEC455_EXECUTION_AUTHORIZED is not False:
        raise ValueError("DEC-456 requires DEC-455 execution to remain false")

    expected = {
        "dec455_runtime_source": (
            root / "src/fmp/discovery/exp064_runtime_source.py",
            DEC455_RUNTIME_SOURCE_BLOB_SHA,
        ),
        "active_workflow": (
            root / ACTIVE_WORKFLOW_PATH,
            DEC455_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
        "cli": (
            root / "scripts/phase8a_exp064.py",
            DEC455_CLI_BLOB_SHA,
        ),
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
    }

    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-456 dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-456 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    return {
        "decision": EXP064_HISTORICAL_RUN_AUTHORIZATION_DECISION,
        "authorization_version": EXP064_HISTORICAL_RUN_AUTHORIZATION_VERSION,
        "dec455_merge_sha": DEC455_MERGE_SHA,
        "runtime_source_blob_sha": actual["dec455_runtime_source"],
        "active_workflow_blob_sha": actual["active_workflow"],
        "cli_blob_sha": actual["cli"],
        "evidence_contract_blob_sha": actual["dec454_evidence_contract"],
        "continuous_stability_miner_blob_sha": actual["dec453_continuous_stability_miner"],
        "continuous_stability_protocol_blob_sha": actual[
            "dec452_continuous_stability_protocol"
        ],
        "workflow_name": WORKFLOW_NAME,
        "workflow_path": EXPECTED_WORKFLOW_PATH,
        "workflow_event": EXPECTED_WORKFLOW_EVENT,
        "workflow_branch": EXPECTED_WORKFLOW_BRANCH,
        "expected_first_run_number": EXPECTED_FIRST_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "historical_data_start": "2015-01-01T00:00:00Z",
        "historical_data_end_exclusive": "2023-01-01T00:00:00Z",
        "reserved_robustness_start": "2023-01-01T00:00:00Z",
        "reserved_robustness_end_exclusive": "2026-08-21T00:00:00Z",
        "historical_result_slot_source_authorized": (
            HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED
        ),
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_execution_authorized": (
            HISTORICAL_EXECUTION_AUTHORIZED
        ),
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
    }


def _is_relevant_run(item: Mapping[str, object]) -> bool:
    return (
        item.get("name") == WORKFLOW_NAME
        and item.get("path") == EXPECTED_WORKFLOW_PATH
        and item.get("event") == EXPECTED_WORKFLOW_EVENT
        and item.get("head_branch") == EXPECTED_WORKFLOW_BRANCH
    )


def classify_historical_run_inventory(
    workflow_runs_payload: Mapping[str, object],
) -> dict[str, object]:
    raw = workflow_runs_payload.get("workflow_runs")
    if not isinstance(raw, list):
        raise ValueError(
            "DEC-456 workflow-run payload must contain workflow_runs"
        )

    relevant: list[Mapping[str, object]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-456 workflow-run row is malformed")
        if _is_relevant_run(item):
            relevant.append(item)

    if len(relevant) > 1:
        raise ValueError("DEC-456 one-shot slot has multiple attempts")

    if not relevant:
        return {
            "decision": EXP064_HISTORICAL_RUN_AUTHORIZATION_DECISION,
            "stage": "EXP064_HISTORICAL_RESULT_SLOT_AVAILABLE",
            "historical_result_attempt_count": 0,
            "historical_result_run_id": None,
            "historical_result_head_sha": None,
            "historical_result_run_number": None,
            "historical_result_run_attempt": None,
            "historical_result_run_status": None,
            "historical_result_run_conclusion": None,
            "historical_result_slot_consumed": False,
            "historical_result_slot_source_authorized": True,
            "historical_result_dispatch_authorized": False,
            "historical_execution_authorized": False,
            "historical_result_authorized": False,
            "rerun_authorized": False,
            "retry_authorized": False,
            "replacement_run_authorized": False,
        }

    run = relevant[0]
    run_id = run.get("id")
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        raise ValueError("DEC-456 historical run id is invalid")
    if run.get("run_number") != EXPECTED_FIRST_RUN_NUMBER:
        raise ValueError("DEC-456 historical run number must remain 1")
    if run.get("run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-456 historical run attempt must remain 1")

    head_sha = _validate_commit(
        run.get("head_sha"),
        field="DEC-456 historical run head",
    )
    status = run.get("status")
    if not isinstance(status, str) or not status:
        raise ValueError("DEC-456 historical run status is malformed")
    conclusion = run.get("conclusion")
    if status == "completed" and not isinstance(conclusion, str):
        raise ValueError(
            "completed DEC-456 historical run requires a conclusion"
        )
    if status != "completed" and conclusion is not None:
        raise ValueError(
            "non-terminal DEC-456 historical run cannot have a conclusion"
        )

    return {
        "decision": EXP064_HISTORICAL_RUN_AUTHORIZATION_DECISION,
        "stage": "EXP064_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED",
        "historical_result_attempt_count": 1,
        "historical_result_run_id": run_id,
        "historical_result_head_sha": head_sha,
        "historical_result_run_number": EXPECTED_FIRST_RUN_NUMBER,
        "historical_result_run_attempt": EXPECTED_RUN_ATTEMPT,
        "historical_result_run_status": status,
        "historical_result_run_conclusion": conclusion,
        "historical_result_slot_consumed": True,
        "historical_result_slot_source_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_execution_authorized": False,
        "historical_result_authorized": False,
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
    if inventory["stage"] != "EXP064_HISTORICAL_RESULT_SLOT_AVAILABLE":
        raise ValueError(
            "DEC-456 one-shot source authorization requires an unused slot"
        )

    return {
        **source,
        **inventory,
        "stage": "EXP064_ONE_SHOT_SLOT_SOURCE_AUTHORIZED_DISPATCH_LOCKED",
        "first_manual_main_run_consumes_slot": True,
        "terminal_outcome_consumes_slot": True,
        "queued_or_running_run_consumes_slot": True,
        "next_action": (
            "A separate later decision may activate runtime authorization and "
            "dispatch exactly one manual main run. DEC-456 itself provides no "
            "dispatch or execution path."
        ),
    }


__all__ = [
    "DEC455_MERGE_SHA",
    "EXP064_HISTORICAL_RUN_AUTHORIZATION_DECISION",
    "EXP064_HISTORICAL_RUN_AUTHORIZATION_VERSION",
    "HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED",
    "build_historical_run_authorization_contract",
    "classify_historical_run_inventory",
    "validate_historical_run_authorization_sources",
]
