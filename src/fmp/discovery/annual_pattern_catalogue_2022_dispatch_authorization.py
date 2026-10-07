from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2022_dispatch_preflight import (
    ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_DECISION,
    ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_VERSION,
    validate_2022_dispatch_preflight,
)


ANNUAL_CATALOGUE_2022_DISPATCH_AUTHORIZATION_DECISION = "DEC-598"
ANNUAL_CATALOGUE_2022_DISPATCH_AUTHORIZATION_VERSION = (
    "fmp-annual-catalogue-2022-dispatch-authorization-v1"
)

DISPATCH_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2022_dispatch_preflight.py"
)
EXPECTED_DISPATCH_PREFLIGHT_SOURCE_BLOB_SHA = (
    "6680b571765622653bf53a006a1cb7126cf7ea80"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)
INSTALLED_GATE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2022_runtime_authorization.py"
)
EXPECTED_INSTALLED_GATE_BLOB_SHA = (
    "ecb21dc7106e7bd43447f4135c3a696251a75e05"
)
INSTALLED_RUNTIME_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_INSTALLED_RUNTIME_BLOB_SHA = (
    "f2734c7ea32355b1024d1097812578b23fc4409d"
)

SOURCE_PREFLIGHT_WORKFLOW_RUN_ID = 37643850671
SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA = (
    "1fafdacab1df0bc2df24b6fa8cd822b031e5cda8"
)
SOURCE_PREFLIGHT_ARTIFACT_ID = 11492114816
SOURCE_PREFLIGHT_ARTIFACT_DIGEST = (
    "sha256:440254694717b13d2fe346a0aae4b247beb02dd9cb18feab7ad6a947968d13d2"
)
SOURCE_PREFLIGHT_FINGERPRINT_SHA256 = (
    "090b8c7e9a1e835387bb7e1579d6db902d359e537c67caa1357a1d96ff938c92"
)
SOURCE_PREFLIGHT_CANONICAL_SHA256 = (
    "015a894dca744889a6fdb56b64190e48c43a13e62c149363e248778660c53481"
)


ANNUAL_SEGMENT_LABEL = "2022"
PRIOR_SEGMENT_LABEL = "2021"
PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37531960014
EXPECTED_RUN_NUMBER = 384
EXPECTED_RUN_ATTEMPT = 1

ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED = True
HISTORICAL_ARTIFACT_READ_AUTHORIZED = True
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = True
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = True
AUTHORIZATION_CONTRACT_VALIDATED = True

RUNTIME_AUTHORIZATION_INSTALLED = True
RUNTIME_GATE_ACTIVE = True
DISPATCH_COMMAND_PRESENT = False
DISPATCH_ACTION_EXECUTED = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RUN_385_OR_LATER_AUTHORIZED = False
NEXT_SEGMENT_EXECUTION_AUTHORIZED = False
PROTECTED_HISTORY_ACCESS_AUTHORIZED = False
CROSS_YEAR_COMPARISON_AUTHORIZED = False
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
        raise ValueError(f"DEC-598 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-598 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-598 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-598 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2022_dispatch_authorization_sources(
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
    for field, (source_path, expected_sha) in expected.items():
        if not source_path.is_file():
            raise ValueError(f"DEC-598 source file missing: {source_path}")
        sha = _git_blob_sha(source_path)
        if sha != expected_sha:
            raise ValueError(f"DEC-598 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_DECISION != "DEC-597":
        raise ValueError("DEC-598 dispatch preflight decision drift")
    if (
        ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_VERSION
        != "fmp-annual-catalogue-2022-dispatch-preflight-v1"
    ):
        raise ValueError("DEC-598 dispatch preflight version drift")
    return actual


def build_2022_dispatch_authorization(
    preflight: Mapping[str, object],
    *,
    repository_root: Path,
    authorization_head_sha: str,
) -> dict[str, object]:
    source = validate_2022_dispatch_authorization_sources(
        repository_root=Path(repository_root),
    )
    validate_2022_dispatch_preflight(preflight)

    if preflight.get("decision") != "DEC-597":
        raise ValueError("DEC-598 source preflight decision mismatch")
    if preflight.get("expected_head_sha") != SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA:
        raise ValueError("DEC-598 source preflight head mismatch")
    if preflight.get("preflight_fingerprint_sha256") != (
        SOURCE_PREFLIGHT_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-598 source preflight fingerprint mismatch")
    if preflight.get("annual_segment_label") != ANNUAL_SEGMENT_LABEL:
        raise ValueError("DEC-598 annual segment mismatch")
    if (
        preflight.get("previous_annual_freeze_run_id")
        != PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-598 predecessor run id mismatch")
    if preflight.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-598 expected run number mismatch")
    if preflight.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-598 expected run attempt mismatch")
    if preflight.get("runtime_authorization_installed") is not True:
        raise ValueError("DEC-598 runtime authorization is not installed")
    if preflight.get("runtime_gate_active") is not True:
        raise ValueError("DEC-598 runtime gate is not active")
    if preflight.get("preflight_read_only") is not True:
        raise ValueError("DEC-598 source preflight must be read-only")
    if preflight.get("dispatch_command_present") is not False:
        raise ValueError("DEC-598 source preflight contains a dispatch command")

    for field in (
        "annual_workflow_dispatch_authorized",
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
        "rerun_authorized",
        "retry_authorized",
        "replacement_run_authorized",
        "run_385_or_later_authorized",
        "next_segment_execution_authorized",
        "protected_history_access_authorized",
        "cross_year_comparison_authorized",
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
        if preflight.get(field) is not False:
            raise ValueError(f"DEC-598 source preflight {field} must be false")

    landing_head = _validate_commit(
        authorization_head_sha,
        field="authorization_head_sha",
    )
    source_preflight_fingerprint = _sha256_hex(
        preflight.get("preflight_fingerprint_sha256"),
        field="source preflight fingerprint",
    )
    source_preflight_canonical = _sha256_bytes(_canonical_json(dict(preflight)))
    if source_preflight_canonical != SOURCE_PREFLIGHT_CANONICAL_SHA256:
        raise ValueError("DEC-598 source preflight canonical SHA-256 mismatch")

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2022_DISPATCH_AUTHORIZATION_DECISION,
        "version": ANNUAL_CATALOGUE_2022_DISPATCH_AUTHORIZATION_VERSION,
        **source,
        "source_preflight_decision": "DEC-597",
        "source_preflight_version": (
            "fmp-annual-catalogue-2022-dispatch-preflight-v1"
        ),
        "source_preflight_workflow_run_id": SOURCE_PREFLIGHT_WORKFLOW_RUN_ID,
        "source_preflight_workflow_head_sha": SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA,
        "source_preflight_artifact_id": SOURCE_PREFLIGHT_ARTIFACT_ID,
        "source_preflight_artifact_digest": SOURCE_PREFLIGHT_ARTIFACT_DIGEST,
        "source_preflight_fingerprint_sha256": source_preflight_fingerprint,
        "source_preflight_canonical_sha256": source_preflight_canonical,
        "authorization_head_sha": landing_head,
        "stage": "ANNUAL_CATALOGUE_2022_DISPATCH_AUTHORIZED_NOT_DISPATCHED",
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_scope": "2022_run_383_attempt_1_only",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": ANNUAL_SEGMENT_LABEL,
        "prior_segment_label": PRIOR_SEGMENT_LABEL,
        "previous_annual_freeze_run_id": PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "runtime_authorization_installed": RUNTIME_AUTHORIZATION_INSTALLED,
        "runtime_gate_active": RUNTIME_GATE_ACTIVE,
        "authorization_contract_validated": AUTHORIZATION_CONTRACT_VALIDATED,
        "annual_workflow_dispatch_authorized": (
            ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED
        ),
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": (
            HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED
        ),
        "historical_result_production_authorized": (
            HISTORICAL_RESULT_PRODUCTION_AUTHORIZED
        ),
        "dispatch_command_present": DISPATCH_COMMAND_PRESENT,
        "dispatch_action_executed": DISPATCH_ACTION_EXECUTED,
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "run_385_or_later_authorized": RUN_385_OR_LATER_AUTHORIZED,
        "next_segment_execution_authorized": NEXT_SEGMENT_EXECUTION_AUTHORIZED,
        "protected_history_access_authorized": PROTECTED_HISTORY_ACCESS_AUTHORIZED,
        "cross_year_comparison_authorized": CROSS_YEAR_COMPARISON_AUTHORIZED,
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
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2022_DISPATCH_ACTION_PREFLIGHT"
        ),
    }
    value["authorization_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2022_dispatch_authorization(value)
    return value


def validate_2022_dispatch_authorization(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("authorization_fingerprint_sha256"),
        field="authorization fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("authorization_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-598 authorization fingerprint mismatch")

    exact = {
        "decision": "DEC-598",
        "version": "fmp-annual-catalogue-2022-dispatch-authorization-v1",
        "dispatch_preflight_source_blob_sha": (
            EXPECTED_DISPATCH_PREFLIGHT_SOURCE_BLOB_SHA
        ),
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "installed_gate_blob_sha": EXPECTED_INSTALLED_GATE_BLOB_SHA,
        "installed_runtime_blob_sha": EXPECTED_INSTALLED_RUNTIME_BLOB_SHA,
        "source_preflight_decision": "DEC-597",
        "source_preflight_version": (
            "fmp-annual-catalogue-2022-dispatch-preflight-v1"
        ),
        "source_preflight_workflow_run_id": SOURCE_PREFLIGHT_WORKFLOW_RUN_ID,
        "source_preflight_workflow_head_sha": SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA,
        "source_preflight_artifact_id": SOURCE_PREFLIGHT_ARTIFACT_ID,
        "source_preflight_artifact_digest": SOURCE_PREFLIGHT_ARTIFACT_DIGEST,
        "source_preflight_fingerprint_sha256": (
            SOURCE_PREFLIGHT_FINGERPRINT_SHA256
        ),
        "stage": "ANNUAL_CATALOGUE_2022_DISPATCH_AUTHORIZED_NOT_DISPATCHED",
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_scope": "2022_run_383_attempt_1_only",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2022",
        "prior_segment_label": "2021",
        "previous_annual_freeze_run_id": 37531960014,
        "expected_run_number": 384,
        "expected_run_attempt": 1,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "authorization_contract_validated": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_385_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "protected_history_access_authorized": False,
        "cross_year_comparison_authorized": False,
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
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2022_DISPATCH_ACTION_PREFLIGHT"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-598 {field} mismatch")

    _validate_commit(
        value.get("authorization_head_sha"),
        field="authorization_head_sha",
    )
    if _sha256_hex(
        value.get("source_preflight_canonical_sha256"),
        field="source preflight canonical sha",
    ) != SOURCE_PREFLIGHT_CANONICAL_SHA256:
        raise ValueError("DEC-598 source preflight canonical sha mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2022_DISPATCH_AUTHORIZATION_DECISION",
    "ANNUAL_CATALOGUE_2022_DISPATCH_AUTHORIZATION_VERSION",
    "EXPECTED_RUN_ATTEMPT",
    "EXPECTED_RUN_NUMBER",
    "build_2022_dispatch_authorization",
    "validate_2022_dispatch_authorization",
    "validate_2022_dispatch_authorization_sources",
]
