from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2016_dispatch_preflight import (
    ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_DECISION,
    ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_VERSION,
    validate_2016_dispatch_preflight,
)


ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZATION_DECISION = "DEC-510"
ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZATION_VERSION = (
    "fmp-annual-catalogue-2016-dispatch-authorization-v1"
)

DISPATCH_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2016_dispatch_preflight.py"
)
EXPECTED_DISPATCH_PREFLIGHT_SOURCE_BLOB_SHA = (
    "07802515d2cd8cdf8445dcc71be18c342596a83c"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED = True
HISTORICAL_ARTIFACT_READ_AUTHORIZED = True
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = True
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = True

NEXT_SEGMENT_EXECUTION_AUTHORIZED = False
CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED = False
STRATEGY_V1_SYNTHESIS_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
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
        raise ValueError(f"DEC-510 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-510 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-510 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-510 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-510 {field} must be a positive integer")
    return value


def validate_2016_dispatch_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dispatch_preflight_source_blob_sha": (
            root / DISPATCH_PREFLIGHT_SOURCE_PATH,
            EXPECTED_DISPATCH_PREFLIGHT_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-510 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-510 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_DECISION != "DEC-509":
        raise ValueError("DEC-510 dispatch preflight decision drift")
    if (
        ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_VERSION
        != "fmp-annual-catalogue-2016-dispatch-preflight-v1"
    ):
        raise ValueError("DEC-510 dispatch preflight version drift")
    return actual


def build_2016_dispatch_authorization(
    preflight: Mapping[str, object],
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_2016_dispatch_authorization_sources(
        repository_root=Path(repository_root),
    )
    validate_2016_dispatch_preflight(preflight)

    if preflight.get("annual_segment_label") != "2016":
        raise ValueError("DEC-510 annual segment mismatch")
    if preflight.get("prior_segment_label") != "2015":
        raise ValueError("DEC-510 predecessor segment mismatch")
    if preflight.get("expected_run_number") != 378:
        raise ValueError("DEC-510 expected run number mismatch")
    if preflight.get("expected_run_attempt") != 1:
        raise ValueError("DEC-510 expected run attempt mismatch")
    if preflight.get("runtime_authorization_installed") is not True:
        raise ValueError("DEC-510 runtime authorization is not installed")
    if preflight.get("runtime_gate_active") is not True:
        raise ValueError("DEC-510 runtime gate is not active")
    if preflight.get("preflight_read_only") is not True:
        raise ValueError("DEC-510 source preflight must be read-only")
    if preflight.get("annual_workflow_dispatch_authorized") is not False:
        raise ValueError("DEC-510 source preflight dispatch authority drift")
    if preflight.get("dispatch_command_present") is not False:
        raise ValueError("DEC-510 source preflight contains a dispatch command")

    expected_head_sha = _validate_commit(
        preflight.get("expected_head_sha"),
        field="expected_head_sha",
    )
    install_commit_sha = _validate_commit(
        preflight.get("install_commit_sha"),
        field="install_commit_sha",
    )
    if install_commit_sha != expected_head_sha:
        raise ValueError("DEC-510 install/main commit mismatch")

    previous_run_id = _positive_int(
        preflight.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZATION_DECISION,
        "version": ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZATION_VERSION,
        **source,
        "source_preflight_decision": "DEC-509",
        "source_preflight_version": (
            "fmp-annual-catalogue-2016-dispatch-preflight-v1"
        ),
        "source_preflight_fingerprint_sha256": _sha256_hex(
            preflight.get("preflight_fingerprint_sha256"),
            field="source preflight fingerprint",
        ),
        "stage": "ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZED_NOT_DISPATCHED",
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_scope": "2016_run_378_attempt_1_only",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "install_commit_sha": install_commit_sha,
        "annual_segment_label": "2016",
        "prior_segment_label": "2015",
        "previous_annual_freeze_run_id": previous_run_id,
        "successful_2015_run_id": _positive_int(
            preflight.get("successful_2015_run_id"),
            field="successful 2015 run id",
        ),
        "successful_2015_run_head_sha": _validate_commit(
            preflight.get("successful_2015_run_head_sha"),
            field="successful 2015 run head",
        ),
        "expected_run_number": 378,
        "expected_run_attempt": 1,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "authorization_contract_validated": True,
        "annual_workflow_dispatch_authorized": (
            ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED
        ),
        "historical_artifact_read_authorized": (
            HISTORICAL_ARTIFACT_READ_AUTHORIZED
        ),
        "historical_catalogue_execution_authorized": (
            HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED
        ),
        "historical_result_production_authorized": (
            HISTORICAL_RESULT_PRODUCTION_AUTHORIZED
        ),
        "dispatch_action_executed": False,
        "dispatch_command_present": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "fourth_or_later_run_authorized": False,
        "next_segment_execution_authorized": NEXT_SEGMENT_EXECUTION_AUTHORIZED,
        "cross_year_result_production_authorized": (
            CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED
        ),
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "source_only_authorization": True,
        "next_gate": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT"
        ),
    }
    value["authorization_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2016_dispatch_authorization(value)
    return value


def validate_2016_dispatch_authorization(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("authorization_fingerprint_sha256"),
        field="authorization fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("authorization_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-510 authorization fingerprint mismatch")

    exact = {
        "decision": "DEC-510",
        "version": "fmp-annual-catalogue-2016-dispatch-authorization-v1",
        "dispatch_preflight_source_blob_sha": (
            EXPECTED_DISPATCH_PREFLIGHT_SOURCE_BLOB_SHA
        ),
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "source_preflight_decision": "DEC-509",
        "source_preflight_version": (
            "fmp-annual-catalogue-2016-dispatch-preflight-v1"
        ),
        "stage": "ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZED_NOT_DISPATCHED",
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_scope": "2016_run_378_attempt_1_only",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2016",
        "prior_segment_label": "2015",
        "expected_run_number": 378,
        "expected_run_attempt": 1,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "authorization_contract_validated": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_action_executed": False,
        "dispatch_command_present": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "fourth_or_later_run_authorized": False,
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
        "source_only_authorization": True,
        "next_gate": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-510 {field} mismatch")

    expected_head = _validate_commit(
        value.get("expected_head_sha"),
        field="expected_head_sha",
    )
    install_commit = _validate_commit(
        value.get("install_commit_sha"),
        field="install_commit_sha",
    )
    if install_commit != expected_head:
        raise ValueError("DEC-510 install/main commit mismatch")
    _positive_int(
        value.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    _positive_int(
        value.get("successful_2015_run_id"),
        field="successful 2015 run id",
    )
    _validate_commit(
        value.get("successful_2015_run_head_sha"),
        field="successful 2015 run head",
    )
    _sha256_hex(
        value.get("source_preflight_fingerprint_sha256"),
        field="source preflight fingerprint",
    )
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZATION_DECISION",
    "ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZATION_VERSION",
    "build_2016_dispatch_authorization",
    "validate_2016_dispatch_authorization",
    "validate_2016_dispatch_authorization_sources",
]
