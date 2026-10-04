from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2016_execution_preflight import (
    ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_DECISION,
    ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_VERSION,
    validate_2016_execution_preflight,
)


ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_DECISION = "DEC-504"
ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_VERSION = (
    "fmp-annual-catalogue-2016-execution-authorization-v1"
)

EXECUTION_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2016_execution_preflight.py"
)
EXPECTED_EXECUTION_PREFLIGHT_SOURCE_BLOB_SHA = (
    "b6764addd7b471e65f05428f745fa93051bd8785"
)
RUNTIME_SOURCE_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_RUNTIME_SOURCE_BLOB_SHA = (
    "f1fa50e7c862354931d919fe7da241de863f6834"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)


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


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-504 {field} must be a positive integer")
    return value


def validate_2016_execution_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "execution_preflight_source_blob_sha": (
            root / EXECUTION_PREFLIGHT_SOURCE_PATH,
            EXPECTED_EXECUTION_PREFLIGHT_SOURCE_BLOB_SHA,
        ),
        "runtime_source_blob_sha": (
            root / RUNTIME_SOURCE_PATH,
            EXPECTED_RUNTIME_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-504 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-504 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_DECISION != "DEC-503":
        raise ValueError("DEC-504 preflight decision drift")
    if (
        ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_VERSION
        != "fmp-annual-catalogue-2016-execution-preflight-v1"
    ):
        raise ValueError("DEC-504 preflight version drift")

    return actual


def build_2016_execution_authorization(
    preflight: Mapping[str, object],
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_2016_execution_authorization_sources(
        repository_root=Path(repository_root),
    )
    validate_2016_execution_preflight(preflight)

    if preflight.get("annual_segment_label") != "2016":
        raise ValueError("DEC-504 annual segment mismatch")
    if preflight.get("prior_segment_label") != "2015":
        raise ValueError("DEC-504 predecessor segment mismatch")
    if preflight.get("expected_next_run_number") != 378:
        raise ValueError("DEC-504 expected run number mismatch")
    if preflight.get("expected_next_run_attempt") != 1:
        raise ValueError("DEC-504 expected run attempt mismatch")

    previous_freeze_run_id = _positive_int(
        preflight.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_DECISION,
        "version": ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_VERSION,
        **source,
        "source_preflight_decision": "DEC-503",
        "source_preflight_version": (
            "fmp-annual-catalogue-2016-execution-preflight-v1"
        ),
        "source_preflight_canonical_sha256": _sha256_bytes(
            _canonical_json(dict(preflight))
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZED_"
            "RUNTIME_NOT_INSTALLED"
        ),
        "authorization_basis": (
            "standing_operator_autonomous_build_authorization"
        ),
        "authorization_scope": "2016_run_378_attempt_1_only",
        "annual_segment_label": "2016",
        "prior_segment_label": "2015",
        "previous_annual_freeze_run_id": previous_freeze_run_id,
        "expected_run_number": 378,
        "expected_run_attempt": 1,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "authorization_contract_validated": True,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
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
            "INSTALL_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_AUTHORIZATION_"
            "AFTER_CONCRETE_PREFLIGHT"
        ),
    }
    value["authorization_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2016_execution_authorization(value)
    return value


def validate_2016_execution_authorization(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = value.get("authorization_fingerprint_sha256")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("DEC-504 authorization fingerprint malformed")
    try:
        int(fingerprint, 16)
    except ValueError as exc:
        raise ValueError(
            "DEC-504 authorization fingerprint must be hexadecimal"
        ) from exc

    unsigned = dict(value)
    unsigned.pop("authorization_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-504 authorization fingerprint mismatch")

    if value.get("decision") != "DEC-504":
        raise ValueError("DEC-504 decision mismatch")
    if value.get("source_preflight_decision") != "DEC-503":
        raise ValueError("DEC-504 source preflight decision mismatch")
    if value.get("annual_segment_label") != "2016":
        raise ValueError("DEC-504 annual segment mismatch")
    if value.get("prior_segment_label") != "2015":
        raise ValueError("DEC-504 predecessor mismatch")
    if value.get("expected_run_number") != 378:
        raise ValueError("DEC-504 run number mismatch")
    if value.get("expected_run_attempt") != 1:
        raise ValueError("DEC-504 run attempt mismatch")
    _positive_int(
        value.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )

    for field in (
        "annual_workflow_dispatch_authorized",
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
        "authorization_contract_validated",
    ):
        if value.get(field) is not True:
            raise ValueError(f"DEC-504 {field} must be true")

    for field in (
        "runtime_authorization_installed",
        "runtime_gate_active",
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
        if value.get(field) is not False:
            raise ValueError(f"DEC-504 {field} must remain false")

    if (
        value.get("next_gate")
        != (
            "INSTALL_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_AUTHORIZATION_"
            "AFTER_CONCRETE_PREFLIGHT"
        )
    ):
        raise ValueError("DEC-504 next gate mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_DECISION",
    "ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_VERSION",
    "build_2016_execution_authorization",
    "validate_2016_execution_authorization",
    "validate_2016_execution_authorization_sources",
]
