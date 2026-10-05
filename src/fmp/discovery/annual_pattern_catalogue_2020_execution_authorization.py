from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2020_execution_preflight import (
    ANNUAL_CATALOGUE_2020_EXECUTION_PREFLIGHT_DECISION,
    ANNUAL_CATALOGUE_2020_EXECUTION_PREFLIGHT_VERSION,
    validate_2020_execution_preflight,
)


ANNUAL_CATALOGUE_2020_EXECUTION_AUTHORIZATION_DECISION = "DEC-568"
ANNUAL_CATALOGUE_2020_EXECUTION_AUTHORIZATION_VERSION = (
    "fmp-annual-catalogue-2020-execution-authorization-v1"
)

EXECUTION_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2020_execution_preflight.py"
)
EXPECTED_EXECUTION_PREFLIGHT_SOURCE_BLOB_SHA = (
    "e045b3e82d2f16e870c77b5b107d8d46fcf96f85"
)
RUNTIME_SOURCE_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_RUNTIME_SOURCE_BLOB_SHA = (
    "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

SOURCE_PREFLIGHT_WORKFLOW_RUN_ID = 37313687059
SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA = (
    "35115a69cae452d0afd922549fe41b4b8e404fd7"
)
SOURCE_PREFLIGHT_ARTIFACT_ID = 11346985812
SOURCE_PREFLIGHT_ARTIFACT_DIGEST = (
    "sha256:182be0b68d721e3267a84bab37c5a3bcb5c25b84b546ba9565c20b6c2ee1f1b0"
)
SOURCE_PREFLIGHT_FINGERPRINT_SHA256 = (
    "bfccf190a7abad8464bafbf96a039305a8034f754fdc7cd05f5825c65398204f"
)

ANNUAL_SEGMENT_LABEL = "2020"
PRIOR_SEGMENT_LABEL = "2019"
PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37310525635
EXPECTED_RUN_NUMBER = 382
EXPECTED_RUN_ATTEMPT = 1

ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED = True
HISTORICAL_ARTIFACT_READ_AUTHORIZED = True
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = True
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = True
AUTHORIZATION_CONTRACT_VALIDATED = True

RUNTIME_AUTHORIZATION_INSTALLED = False
RUNTIME_GATE_ACTIVE = False
DISPATCH_COMMAND_PRESENT = False
DISPATCH_ACTION_EXECUTED = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RUN_383_OR_LATER_AUTHORIZED = False
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
        raise ValueError(f"DEC-568 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-568 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-568 {field} must be a positive integer")
    return value


def validate_2020_execution_authorization_sources(
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
    for field, (source_path, expected_sha) in expected.items():
        if not source_path.is_file():
            raise ValueError(f"DEC-568 source file missing: {source_path}")
        sha = _git_blob_sha(source_path)
        if sha != expected_sha:
            raise ValueError(f"DEC-568 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2020_EXECUTION_PREFLIGHT_DECISION != "DEC-567":
        raise ValueError("DEC-568 preflight decision drift")
    if (
        ANNUAL_CATALOGUE_2020_EXECUTION_PREFLIGHT_VERSION
        != "fmp-annual-catalogue-2020-execution-preflight-v1"
    ):
        raise ValueError("DEC-568 preflight version drift")

    runtime_text = (root / RUNTIME_SOURCE_PATH).read_text(encoding="utf-8")
    if 'segment == "2020"' in runtime_text:
        raise ValueError("DEC-568 runtime already routes 2020")
    if "require_2020_execution_authorized" in runtime_text:
        raise ValueError("DEC-568 2020 runtime gate already active")
    return actual


def build_2020_execution_authorization(
    preflight: Mapping[str, object],
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_2020_execution_authorization_sources(
        repository_root=Path(repository_root),
    )
    validate_2020_execution_preflight(preflight)

    if preflight.get("decision") != "DEC-567":
        raise ValueError("DEC-568 source preflight decision mismatch")
    if preflight.get("expected_head_sha") != SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA:
        raise ValueError("DEC-568 source preflight head mismatch")
    if (
        preflight.get("preflight_fingerprint_sha256")
        != SOURCE_PREFLIGHT_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-568 source preflight fingerprint mismatch")
    if preflight.get("annual_segment_label") != ANNUAL_SEGMENT_LABEL:
        raise ValueError("DEC-568 annual segment mismatch")
    if preflight.get("prior_segment_label") != PRIOR_SEGMENT_LABEL:
        raise ValueError("DEC-568 predecessor segment mismatch")
    if (
        preflight.get("previous_annual_freeze_run_id")
        != PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-568 predecessor run id mismatch")
    if preflight.get("expected_next_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-568 expected run number mismatch")
    if preflight.get("expected_next_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-568 expected run attempt mismatch")
    if preflight.get("preflight_read_only") is not True:
        raise ValueError("DEC-568 source preflight must be read-only")

    for field in (
        "annual_workflow_dispatch_authorized",
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
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
        if preflight.get(field) is not False:
            raise ValueError(f"DEC-568 source preflight {field} must be false")

    source_preflight_fingerprint = _sha256_hex(
        preflight.get("preflight_fingerprint_sha256"),
        field="source preflight fingerprint",
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2020_EXECUTION_AUTHORIZATION_DECISION,
        "version": ANNUAL_CATALOGUE_2020_EXECUTION_AUTHORIZATION_VERSION,
        **source,
        "source_preflight_decision": "DEC-567",
        "source_preflight_version": (
            "fmp-annual-catalogue-2020-execution-preflight-v1"
        ),
        "source_preflight_workflow_run_id": SOURCE_PREFLIGHT_WORKFLOW_RUN_ID,
        "source_preflight_workflow_head_sha": SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA,
        "source_preflight_artifact_id": SOURCE_PREFLIGHT_ARTIFACT_ID,
        "source_preflight_artifact_digest": SOURCE_PREFLIGHT_ARTIFACT_DIGEST,
        "source_preflight_fingerprint_sha256": source_preflight_fingerprint,
        "source_preflight_canonical_sha256": _sha256_bytes(
            _canonical_json(dict(preflight))
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2020_EXECUTION_AUTHORIZED_"
            "RUNTIME_NOT_INSTALLED"
        ),
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_scope": "2020_run_382_attempt_1_only",
        "annual_segment_label": ANNUAL_SEGMENT_LABEL,
        "prior_segment_label": PRIOR_SEGMENT_LABEL,
        "previous_annual_freeze_run_id": PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "previous_runtime_binding_fingerprint_sha256": preflight.get(
            "source_runtime_binding_fingerprint_sha256"
        ),
        "previous_annual_freeze_evidence_fingerprint_sha256": preflight.get(
            "source_freeze_evidence_fingerprint_sha256"
        ),
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "annual_workflow_dispatch_authorized": ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": (
            HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED
        ),
        "historical_result_production_authorized": (
            HISTORICAL_RESULT_PRODUCTION_AUTHORIZED
        ),
        "authorization_contract_validated": AUTHORIZATION_CONTRACT_VALIDATED,
        "runtime_authorization_installed": RUNTIME_AUTHORIZATION_INSTALLED,
        "runtime_gate_active": RUNTIME_GATE_ACTIVE,
        "dispatch_command_present": DISPATCH_COMMAND_PRESENT,
        "dispatch_action_executed": DISPATCH_ACTION_EXECUTED,
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "run_383_or_later_authorized": RUN_383_OR_LATER_AUTHORIZED,
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
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_RUNTIME_AUTHORIZATION_PLAN"
        ),
    }
    value["authorization_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2020_execution_authorization(value)
    return value


def validate_2020_execution_authorization(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("authorization_fingerprint_sha256"),
        field="authorization fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("authorization_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-568 authorization fingerprint mismatch")

    exact = {
        "decision": "DEC-568",
        "version": "fmp-annual-catalogue-2020-execution-authorization-v1",
        "execution_preflight_source_blob_sha": (
            EXPECTED_EXECUTION_PREFLIGHT_SOURCE_BLOB_SHA
        ),
        "runtime_source_blob_sha": EXPECTED_RUNTIME_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "source_preflight_decision": "DEC-567",
        "source_preflight_version": (
            "fmp-annual-catalogue-2020-execution-preflight-v1"
        ),
        "source_preflight_workflow_run_id": SOURCE_PREFLIGHT_WORKFLOW_RUN_ID,
        "source_preflight_workflow_head_sha": SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA,
        "source_preflight_artifact_id": SOURCE_PREFLIGHT_ARTIFACT_ID,
        "source_preflight_artifact_digest": SOURCE_PREFLIGHT_ARTIFACT_DIGEST,
        "source_preflight_fingerprint_sha256": (
            SOURCE_PREFLIGHT_FINGERPRINT_SHA256
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2020_EXECUTION_AUTHORIZED_"
            "RUNTIME_NOT_INSTALLED"
        ),
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_scope": "2020_run_382_attempt_1_only",
        "annual_segment_label": "2020",
        "prior_segment_label": "2019",
        "previous_annual_freeze_run_id": PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "expected_run_number": 382,
        "expected_run_attempt": 1,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "authorization_contract_validated": True,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
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
        "source_only_authorization": True,
        "next_gate": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_RUNTIME_AUTHORIZATION_PLAN"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-568 {field} mismatch")

    for field in (
        "source_preflight_fingerprint_sha256",
        "source_preflight_canonical_sha256",
        "previous_runtime_binding_fingerprint_sha256",
        "previous_annual_freeze_evidence_fingerprint_sha256",
    ):
        _sha256_hex(value.get(field), field=field)

    _positive_int(
        value.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2020_EXECUTION_AUTHORIZATION_DECISION",
    "ANNUAL_CATALOGUE_2020_EXECUTION_AUTHORIZATION_VERSION",
    "EXPECTED_RUN_ATTEMPT",
    "EXPECTED_RUN_NUMBER",
    "build_2020_execution_authorization",
    "validate_2020_execution_authorization",
    "validate_2020_execution_authorization_sources",
]
