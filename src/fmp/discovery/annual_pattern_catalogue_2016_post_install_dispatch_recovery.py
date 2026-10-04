from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2015_runtime_evidence_binding import (
    validate_2015_runtime_evidence_binding,
)
from .annual_pattern_catalogue_2016_post_install_runtime_repair import (
    INSTALL_COMMIT_SHA,
    validate_2016_post_install_runtime_repair,
)
from .annual_pattern_catalogue_2016_runtime_authorization_install_receipt import (
    validate_2016_runtime_authorization_install_receipt,
)


ANNUAL_CATALOGUE_2016_POST_INSTALL_DISPATCH_RECOVERY_DECISION = "DEC-532"
ANNUAL_CATALOGUE_2016_POST_INSTALL_DISPATCH_RECOVERY_VERSION = (
    "fmp-annual-catalogue-2016-post-install-dispatch-recovery-v1"
)

REPAIR_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2016_post_install_runtime_repair.py"
)
EXPECTED_REPAIR_SOURCE_BLOB_SHA = "fce9214787b487f9dacf083adec39a4507958d92"
INSTALL_RECEIPT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2016_runtime_authorization_install_receipt.py"
)
EXPECTED_INSTALL_RECEIPT_SOURCE_BLOB_SHA = (
    "3a5614af2393378ed664c4802806147d79ccd8c7"
)
RUNTIME_BINDING_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_runtime_evidence_binding.py"
)
EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA = (
    "400e9715a6e3b2dab413ce2ecff0fbce8c46f6b0"
)
ACTIVE_GATE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2016_runtime_authorization.py"
)
EXPECTED_ACTIVE_GATE_BLOB_SHA = "5b034fba697c3de0c0f8b6140d6f84771f1ae54b"
RUNTIME_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_RUNTIME_BLOB_SHA = "b564f5a26fdef146fc6080962e7c4762b0b5949a"
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"

FAILED_FIRST_RUN_ID = 37126711695
FAILED_FIRST_RUN_HEAD_SHA = "fd85a886d07234ad584dcca08692b37e6af54b2e"
FAILED_RUN376_ID = 37191637168
FAILED_RUN376_HEAD_SHA = "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3"
SUCCESSFUL_2015_RUN_ID = 37198002653
SUCCESSFUL_2015_RUN_HEAD_SHA = "a89db974be9a94481e7ed0990476bc661012f1e4"


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-532 {field} must be a 40-character commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-532 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-532 {field} must be a positive integer")
    return value


def validate_2016_post_install_dispatch_recovery_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "repair_source_blob_sha": (
            root / REPAIR_SOURCE_PATH,
            EXPECTED_REPAIR_SOURCE_BLOB_SHA,
        ),
        "install_receipt_source_blob_sha": (
            root / INSTALL_RECEIPT_SOURCE_PATH,
            EXPECTED_INSTALL_RECEIPT_SOURCE_BLOB_SHA,
        ),
        "runtime_binding_source_blob_sha": (
            root / RUNTIME_BINDING_SOURCE_PATH,
            EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA,
        ),
        "active_gate_blob_sha": (
            root / ACTIVE_GATE_PATH,
            EXPECTED_ACTIVE_GATE_BLOB_SHA,
        ),
        "runtime_blob_sha": (
            root / RUNTIME_PATH,
            EXPECTED_RUNTIME_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-532 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-532 {field} mismatch")
        actual[field] = sha
    return actual


def _validate_annual_inventory(
    value: Mapping[str, object],
    *,
    runtime_binding: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list) or len(runs) != 3:
        raise ValueError("DEC-532 requires exactly three prior annual workflow runs")
    by_number: dict[int, Mapping[str, object]] = {}
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-532 annual workflow row malformed")
        number = raw.get("run_number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise ValueError("DEC-532 annual run number malformed")
        if number in by_number:
            raise ValueError("DEC-532 duplicate annual run number")
        by_number[number] = raw
    if set(by_number) != {1, 376, 377}:
        raise ValueError("DEC-532 annual workflow run inventory mismatch")

    exact = {
        1: {
            "id": FAILED_FIRST_RUN_ID,
            "run_attempt": 1,
            "head_sha": FAILED_FIRST_RUN_HEAD_SHA,
            "conclusion": "failure",
        },
        376: {
            "id": FAILED_RUN376_ID,
            "run_attempt": 1,
            "head_sha": FAILED_RUN376_HEAD_SHA,
            "conclusion": "failure",
        },
        377: {
            "id": SUCCESSFUL_2015_RUN_ID,
            "run_attempt": 1,
            "head_sha": SUCCESSFUL_2015_RUN_HEAD_SHA,
            "conclusion": "success",
        },
    }
    for number, fields in exact.items():
        row = by_number[number]
        shared = {
            "run_number": number,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "status": "completed",
        }
        for field, expected in {**shared, **fields}.items():
            if row.get(field) != expected:
                raise ValueError(
                    f"DEC-532 annual run {number} {field} mismatch"
                )

    if runtime_binding.get("run_id") != SUCCESSFUL_2015_RUN_ID:
        raise ValueError("DEC-532 runtime binding run id mismatch")
    if runtime_binding.get("run_number") != 377:
        raise ValueError("DEC-532 runtime binding run number mismatch")
    if runtime_binding.get("run_head_sha") != SUCCESSFUL_2015_RUN_HEAD_SHA:
        raise ValueError("DEC-532 runtime binding head mismatch")
    return {
        "annual_workflow_run_count": 3,
        "successful_2015_run_id": SUCCESSFUL_2015_RUN_ID,
        "successful_2015_run_number": 377,
        "successful_2015_run_head_sha": SUCCESSFUL_2015_RUN_HEAD_SHA,
    }


def build_2016_post_install_dispatch_recovery(
    *,
    repository_root: Path,
    repair_receipt: Mapping[str, object],
    install_receipt: Mapping[str, object],
    runtime_binding: Mapping[str, object],
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2016_post_install_dispatch_recovery_sources(
        repository_root=Path(repository_root)
    )
    validate_2016_post_install_runtime_repair(repair_receipt)
    validate_2016_runtime_authorization_install_receipt(install_receipt)
    validate_2015_runtime_evidence_binding(runtime_binding)

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-532 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping) or commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-532 main head mismatch")
    if repair_receipt.get("repair_head_sha") != expected_head_sha:
        raise ValueError("DEC-532 repair/main head mismatch")
    if install_receipt.get("install_commit_sha") != INSTALL_COMMIT_SHA:
        raise ValueError("DEC-532 historical install commit mismatch")
    if install_receipt.get("expected_run_number") != 378:
        raise ValueError("DEC-532 install receipt run number mismatch")
    if install_receipt.get("expected_run_attempt") != 1:
        raise ValueError("DEC-532 install receipt run attempt mismatch")
    if install_receipt.get("runtime_authorization_installed") is not True:
        raise ValueError("DEC-532 runtime authorization is not installed")
    if install_receipt.get("runtime_gate_active") is not True:
        raise ValueError("DEC-532 runtime gate is not active")

    inventory = _validate_annual_inventory(
        annual_workflow_runs,
        runtime_binding=runtime_binding,
    )
    previous_run_id = _positive_int(
        runtime_binding.get("run_id"),
        field="previous annual freeze run id",
    )
    if install_receipt.get("previous_annual_freeze_run_id") != previous_run_id:
        raise ValueError("DEC-532 install receipt predecessor mismatch")

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2016_POST_INSTALL_DISPATCH_RECOVERY_DECISION,
        "version": ANNUAL_CATALOGUE_2016_POST_INSTALL_DISPATCH_RECOVERY_VERSION,
        **source,
        **inventory,
        "source_repair_decision": "DEC-531",
        "source_install_receipt_decision": "DEC-508",
        "stage": "ANNUAL_CATALOGUE_2016_POST_INSTALL_DISPATCH_RECOVERY_READY",
        "repository_full_name": "Dtwosam/FMP",
        "install_commit_sha": INSTALL_COMMIT_SHA,
        "repair_head_sha": expected_head_sha,
        "annual_segment_label": "2016",
        "previous_annual_freeze_run_id": previous_run_id,
        "expected_run_number": 378,
        "expected_run_attempt": 1,
        "dispatch_ref": "main",
        "dispatch_input_annual_segment_label": "2016",
        "dispatch_input_previous_annual_freeze_run_id": str(previous_run_id),
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "runtime_import_cycle_repaired": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_379_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": "EXACT_2016_RUN378_DISPATCH_ON_REPAIRED_MAIN",
    }
    value["recovery_fingerprint_sha256"] = _sha256(value)
    validate_2016_post_install_dispatch_recovery(value)
    return value


def validate_2016_post_install_dispatch_recovery(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = value.get("recovery_fingerprint_sha256")
    unsigned = dict(value)
    unsigned.pop("recovery_fingerprint_sha256", None)
    if fingerprint != _sha256(unsigned):
        raise ValueError("DEC-532 recovery fingerprint mismatch")
    exact = {
        "decision": "DEC-532",
        "source_repair_decision": "DEC-531",
        "source_install_receipt_decision": "DEC-508",
        "install_commit_sha": INSTALL_COMMIT_SHA,
        "annual_segment_label": "2016",
        "annual_workflow_run_count": 3,
        "successful_2015_run_id": SUCCESSFUL_2015_RUN_ID,
        "successful_2015_run_number": 377,
        "expected_run_number": 378,
        "expected_run_attempt": 1,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "runtime_import_cycle_repaired": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_379_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-532 {field} mismatch")
    repair_head = _validate_commit(
        value.get("repair_head_sha"),
        field="repair_head_sha",
    )
    if value.get("dispatch_ref") != "main":
        raise ValueError("DEC-532 dispatch ref mismatch")
    if value.get("dispatch_input_annual_segment_label") != "2016":
        raise ValueError("DEC-532 dispatch segment input mismatch")
    previous_run_id = _positive_int(
        value.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    if value.get("dispatch_input_previous_annual_freeze_run_id") != str(
        previous_run_id
    ):
        raise ValueError("DEC-532 predecessor dispatch input mismatch")
    if not repair_head:
        raise ValueError("DEC-532 repair head missing")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_POST_INSTALL_DISPATCH_RECOVERY_DECISION",
    "ANNUAL_CATALOGUE_2016_POST_INSTALL_DISPATCH_RECOVERY_VERSION",
    "build_2016_post_install_dispatch_recovery",
    "validate_2016_post_install_dispatch_recovery",
    "validate_2016_post_install_dispatch_recovery_sources",
]
