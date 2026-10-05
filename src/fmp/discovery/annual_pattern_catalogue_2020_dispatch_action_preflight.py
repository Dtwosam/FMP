from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2020_dispatch_authorization import (
    ANNUAL_CATALOGUE_2020_DISPATCH_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_2020_DISPATCH_AUTHORIZATION_VERSION,
    validate_2020_dispatch_authorization,
)


ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_DECISION = "DEC-575"
ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2020-dispatch-action-preflight-v1"
)

AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2020_dispatch_authorization.py"
)
EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA = (
    "e6962667406a92982d60ed66b3a1cc48cf2c0bdc"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)
INSTALLED_GATE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2020_runtime_authorization.py"
)
EXPECTED_INSTALLED_GATE_BLOB_SHA = (
    "695a50b418da752e1bd37d6302f209033ab611f5"
)
INSTALLED_RUNTIME_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_INSTALLED_RUNTIME_BLOB_SHA = (
    "4e124365430672fa63825b272001937c60151644"
)

SOURCE_AUTHORIZATION_WORKFLOW_RUN_ID = 37378217595
SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA = (
    "4dae528384904779a9a8d110c347fb92d23ac75f"
)
SOURCE_AUTHORIZATION_ARTIFACT_ID = 11372815746
SOURCE_AUTHORIZATION_ARTIFACT_DIGEST = (
    "sha256:52e9424d5448bb6c2ec51edabc832350c34dbe6f53dcb5a9cae883b987c4d53d"
)
SOURCE_AUTHORIZATION_FINGERPRINT_SHA256 = (
    "bf1960379603190bf990d808b102c67d156d8ba194e023ef90859c8a8da3d79e"
)

FAILED_RUN_1_ID = 37126711695
FAILED_RUN_1_HEAD_SHA = "fd85a886d07234ad584dcca08692b37e6af54b2e"
FAILED_RUN_376_ID = 37191637168
FAILED_RUN_376_HEAD_SHA = "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3"
SUCCESSFUL_2015_RUN_ID = 37198002653
SUCCESSFUL_2015_RUN_HEAD_SHA = "a89db974be9a94481e7ed0990476bc661012f1e4"
SUCCESSFUL_2016_RUN_ID = 37206992367
SUCCESSFUL_2016_RUN_HEAD_SHA = "2524fde355349581c9440a172d0384c3cbce31ed"
SUCCESSFUL_2017_RUN_ID = 37227536041
SUCCESSFUL_2017_RUN_HEAD_SHA = "7b4c1ef8573e280c067443b72f1534d9091d5b7f"
SUCCESSFUL_2018_RUN_ID = 37237817538
SUCCESSFUL_2018_RUN_HEAD_SHA = "30971a996f514670a6f836d8e45cf80137197a4f"
SUCCESSFUL_2019_RUN_ID = 37310525635
SUCCESSFUL_2019_RUN_HEAD_SHA = "8bcee3a7a834743f08bd9ad73109bfc09609a2fe"

ANNUAL_SEGMENT_LABEL = "2020"
PRIOR_SEGMENT_LABEL = "2019"
PREVIOUS_ANNUAL_FREEZE_RUN_ID = SUCCESSFUL_2019_RUN_ID
EXPECTED_RUN_NUMBER = 382
EXPECTED_RUN_ATTEMPT = 1


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


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_hex(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"DEC-575 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-575 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-575 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-575 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-575 {field} must be a positive integer")
    return value


def validate_2020_dispatch_action_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "authorization_source_blob_sha": (
            root / AUTHORIZATION_SOURCE_PATH,
            EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
        "installed_gate_blob_sha": (
            root / INSTALLED_GATE_PATH,
            EXPECTED_INSTALLED_GATE_BLOB_SHA,
        ),
        "installed_runtime_blob_sha": (
            root / INSTALLED_RUNTIME_PATH,
            EXPECTED_INSTALLED_RUNTIME_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-575 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-575 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2020_DISPATCH_AUTHORIZATION_DECISION != "DEC-574":
        raise ValueError("DEC-575 authorization decision drift")
    if (
        ANNUAL_CATALOGUE_2020_DISPATCH_AUTHORIZATION_VERSION
        != "fmp-annual-catalogue-2020-dispatch-authorization-v1"
    ):
        raise ValueError("DEC-575 authorization version drift")
    return actual


def _validate_run_inventory(payload: Mapping[str, object]) -> dict[str, object]:
    rows = payload.get("workflow_runs")
    if not isinstance(rows, list):
        raise ValueError("DEC-575 annual workflow_runs must be a list")
    if len(rows) != 7:
        raise ValueError("DEC-575 requires exactly seven prior annual workflow runs")

    by_number: dict[int, Mapping[str, object]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-575 annual run row malformed")
        number = raw.get("run_number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise ValueError("DEC-575 annual run number malformed")
        if number in by_number:
            raise ValueError("DEC-575 duplicate annual run number")
        by_number[number] = raw

    if set(by_number) != {1, 376, 377, 378, 379, 380, 381}:
        raise ValueError("DEC-575 annual run inventory mismatch")

    exact = {
        1: (FAILED_RUN_1_ID, FAILED_RUN_1_HEAD_SHA, "failure"),
        376: (FAILED_RUN_376_ID, FAILED_RUN_376_HEAD_SHA, "failure"),
        377: (SUCCESSFUL_2015_RUN_ID, SUCCESSFUL_2015_RUN_HEAD_SHA, "success"),
        378: (SUCCESSFUL_2016_RUN_ID, SUCCESSFUL_2016_RUN_HEAD_SHA, "success"),
        379: (SUCCESSFUL_2017_RUN_ID, SUCCESSFUL_2017_RUN_HEAD_SHA, "success"),
        380: (SUCCESSFUL_2018_RUN_ID, SUCCESSFUL_2018_RUN_HEAD_SHA, "success"),
        381: (SUCCESSFUL_2019_RUN_ID, SUCCESSFUL_2019_RUN_HEAD_SHA, "success"),
    }
    for number, (run_id, head_sha, conclusion) in exact.items():
        row = by_number[number]
        required = {
            "id": run_id,
            "name": "phase8a-annual-pattern-catalogue",
            "path": ACTIVE_WORKFLOW_PATH,
            "run_number": number,
            "run_attempt": 1,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": head_sha,
            "status": "completed",
            "conclusion": conclusion,
        }
        for field, expected in required.items():
            if row.get(field) != expected:
                raise ValueError(
                    f"DEC-575 annual run {number} {field} mismatch"
                )

    return {
        "annual_workflow_run_count": 7,
        "failed_run_1_id": FAILED_RUN_1_ID,
        "failed_run_376_id": FAILED_RUN_376_ID,
        "successful_2015_run_id": SUCCESSFUL_2015_RUN_ID,
        "successful_2015_run_head_sha": SUCCESSFUL_2015_RUN_HEAD_SHA,
        "successful_2016_run_id": SUCCESSFUL_2016_RUN_ID,
        "successful_2016_run_head_sha": SUCCESSFUL_2016_RUN_HEAD_SHA,
        "successful_2017_run_id": SUCCESSFUL_2017_RUN_ID,
        "successful_2017_run_head_sha": SUCCESSFUL_2017_RUN_HEAD_SHA,
        "successful_2018_run_id": SUCCESSFUL_2018_RUN_ID,
        "successful_2018_run_head_sha": SUCCESSFUL_2018_RUN_HEAD_SHA,
        "successful_2019_run_id": SUCCESSFUL_2019_RUN_ID,
        "successful_2019_run_head_sha": SUCCESSFUL_2019_RUN_HEAD_SHA,
    }


def build_2020_dispatch_action_preflight(
    authorization: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2020_dispatch_action_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2020_dispatch_authorization(authorization)

    if authorization.get("decision") != "DEC-574":
        raise ValueError("DEC-575 source authorization decision mismatch")
    if (
        authorization.get("authorization_head_sha")
        != SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA
    ):
        raise ValueError("DEC-575 source authorization head mismatch")
    if (
        authorization.get("authorization_fingerprint_sha256")
        != SOURCE_AUTHORIZATION_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-575 source authorization fingerprint mismatch")

    if authorization.get("annual_segment_label") != ANNUAL_SEGMENT_LABEL:
        raise ValueError("DEC-575 annual segment mismatch")
    if authorization.get("prior_segment_label") != PRIOR_SEGMENT_LABEL:
        raise ValueError("DEC-575 predecessor segment mismatch")
    if (
        authorization.get("previous_annual_freeze_run_id")
        != PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-575 predecessor run id mismatch")
    if authorization.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-575 expected run number mismatch")
    if authorization.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-575 expected run attempt mismatch")

    for field in (
        "runtime_authorization_installed",
        "runtime_gate_active",
        "authorization_contract_validated",
        "annual_workflow_dispatch_authorized",
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
        "source_only_authorization",
    ):
        if authorization.get(field) is not True:
            raise ValueError(f"DEC-575 authorization {field} must be true")

    for field in (
        "dispatch_command_present",
        "dispatch_action_executed",
        "rerun_authorized",
        "retry_authorized",
        "replacement_run_authorized",
        "run_383_or_later_authorized",
        "next_segment_execution_authorized",
        "cross_year_result_production_authorized",
        "strategy_v1_synthesis_authorized",
        "promotion_authorized",
        "phase8b_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if authorization.get(field) is not False:
            raise ValueError(f"DEC-575 authorization {field} must remain false")

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-575 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-575 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-575 main head mismatch")

    inventory = _validate_run_inventory(annual_workflow_runs)
    previous_run_id = _positive_int(
        authorization.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    if previous_run_id != inventory["successful_2019_run_id"]:
        raise ValueError("DEC-575 predecessor run identity mismatch")

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_VERSION,
        **source,
        **inventory,
        "source_authorization_decision": "DEC-574",
        "source_authorization_version": (
            "fmp-annual-catalogue-2020-dispatch-authorization-v1"
        ),
        "source_authorization_workflow_run_id": (
            SOURCE_AUTHORIZATION_WORKFLOW_RUN_ID
        ),
        "source_authorization_workflow_head_sha": (
            SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA
        ),
        "source_authorization_artifact_id": SOURCE_AUTHORIZATION_ARTIFACT_ID,
        "source_authorization_artifact_digest": (
            SOURCE_AUTHORIZATION_ARTIFACT_DIGEST
        ),
        "source_authorization_fingerprint_sha256": _sha256_hex(
            authorization.get("authorization_fingerprint_sha256"),
            field="source authorization fingerprint",
        ),
        "source_authorization_canonical_sha256": _sha256_bytes(
            _canonical_json(dict(authorization))
        ),
        "stage": "ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "authorization_head_sha": SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA,
        "active_workflow_path": ACTIVE_WORKFLOW_PATH,
        "annual_segment_label": ANNUAL_SEGMENT_LABEL,
        "prior_segment_label": PRIOR_SEGMENT_LABEL,
        "previous_annual_freeze_run_id": previous_run_id,
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "dispatch_ref": "main",
        "dispatch_input_annual_segment_label": ANNUAL_SEGMENT_LABEL,
        "dispatch_input_previous_annual_freeze_run_id": str(previous_run_id),
        "dispatch_parameters_frozen": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "preflight_read_only": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_383_or_later_authorized": False,
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
        "next_gate": (
            "EXACT_2020_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN"
        ),
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2020_dispatch_action_preflight(value)
    return value


def validate_2020_dispatch_action_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-575 preflight fingerprint mismatch")

    exact = {
        "decision": "DEC-575",
        "version": "fmp-annual-catalogue-2020-dispatch-action-preflight-v1",
        "authorization_source_blob_sha": EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "installed_gate_blob_sha": EXPECTED_INSTALLED_GATE_BLOB_SHA,
        "installed_runtime_blob_sha": EXPECTED_INSTALLED_RUNTIME_BLOB_SHA,
        "source_authorization_decision": "DEC-574",
        "source_authorization_version": (
            "fmp-annual-catalogue-2020-dispatch-authorization-v1"
        ),
        "source_authorization_workflow_run_id": (
            SOURCE_AUTHORIZATION_WORKFLOW_RUN_ID
        ),
        "source_authorization_workflow_head_sha": (
            SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA
        ),
        "source_authorization_artifact_id": SOURCE_AUTHORIZATION_ARTIFACT_ID,
        "source_authorization_artifact_digest": (
            SOURCE_AUTHORIZATION_ARTIFACT_DIGEST
        ),
        "source_authorization_fingerprint_sha256": (
            SOURCE_AUTHORIZATION_FINGERPRINT_SHA256
        ),
        "stage": "ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "authorization_head_sha": SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA,
        "active_workflow_path": ACTIVE_WORKFLOW_PATH,
        "annual_segment_label": "2020",
        "prior_segment_label": "2019",
        "annual_workflow_run_count": 7,
        "failed_run_1_id": FAILED_RUN_1_ID,
        "failed_run_376_id": FAILED_RUN_376_ID,
        "successful_2015_run_id": SUCCESSFUL_2015_RUN_ID,
        "successful_2015_run_head_sha": SUCCESSFUL_2015_RUN_HEAD_SHA,
        "successful_2016_run_id": SUCCESSFUL_2016_RUN_ID,
        "successful_2016_run_head_sha": SUCCESSFUL_2016_RUN_HEAD_SHA,
        "successful_2017_run_id": SUCCESSFUL_2017_RUN_ID,
        "successful_2017_run_head_sha": SUCCESSFUL_2017_RUN_HEAD_SHA,
        "successful_2018_run_id": SUCCESSFUL_2018_RUN_ID,
        "successful_2018_run_head_sha": SUCCESSFUL_2018_RUN_HEAD_SHA,
        "successful_2019_run_id": SUCCESSFUL_2019_RUN_ID,
        "successful_2019_run_head_sha": SUCCESSFUL_2019_RUN_HEAD_SHA,
        "previous_annual_freeze_run_id": SUCCESSFUL_2019_RUN_ID,
        "expected_run_number": 382,
        "expected_run_attempt": 1,
        "dispatch_ref": "main",
        "dispatch_input_annual_segment_label": "2020",
        "dispatch_input_previous_annual_freeze_run_id": str(
            SUCCESSFUL_2019_RUN_ID
        ),
        "dispatch_parameters_frozen": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "preflight_read_only": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_383_or_later_authorized": False,
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
        "next_gate": (
            "EXACT_2020_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-575 {field} mismatch")

    _validate_commit(
        value.get("expected_head_sha"),
        field="expected_head_sha",
    )
    _sha256_hex(
        value.get("source_authorization_canonical_sha256"),
        field="source authorization canonical sha",
    )
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_VERSION",
    "build_2020_dispatch_action_preflight",
    "validate_2020_dispatch_action_preflight",
    "validate_2020_dispatch_action_preflight_sources",
]
