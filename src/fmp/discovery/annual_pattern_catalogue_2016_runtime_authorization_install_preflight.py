from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2016_execution_authorization import (
    ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_VERSION,
    validate_2016_execution_authorization,
)
from .annual_pattern_catalogue_2016_runtime_authorization_plan import (
    ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_PLAN_DECISION,
    ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_PLAN_VERSION,
    DORMANT_2016_GATE_TEMPLATE_PATH,
    DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
    EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA,
    EXPECTED_DORMANT_2016_GATE_TEMPLATE_BLOB_SHA,
    EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
    TARGET_2016_GATE_SOURCE_PATH,
    TARGET_RUNTIME_SOURCE_PATH,
    validate_2016_runtime_authorization_plan_sources,
)


ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION = "DEC-506"
ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2016-runtime-authorization-install-preflight-v1"
)

EXECUTION_AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2016_execution_authorization.py"
)
EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA = (
    "f3d93ba4701a5d9d80005664445104d1105ff25f"
)
RUNTIME_AUTHORIZATION_PLAN_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2016_runtime_authorization_plan.py"
)
EXPECTED_RUNTIME_AUTHORIZATION_PLAN_SOURCE_BLOB_SHA = (
    "f2e84069ed6b761fa5001ca6dd722cee05e63224"
)

REPOSITORY_MUTATION_AUTHORIZED = False
RUNTIME_AUTHORIZATION_INSTALLED = False
RUNTIME_GATE_ACTIVE = False
ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
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
        raise ValueError(f"DEC-506 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-506 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-506 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-506 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-506 {field} must be a positive integer")
    return value


def validate_2016_runtime_authorization_install_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "execution_authorization_source_blob_sha": (
            root / EXECUTION_AUTHORIZATION_SOURCE_PATH,
            EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA,
        ),
        "runtime_authorization_plan_source_blob_sha": (
            root / RUNTIME_AUTHORIZATION_PLAN_SOURCE_PATH,
            EXPECTED_RUNTIME_AUTHORIZATION_PLAN_SOURCE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-506 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-506 {field} mismatch")
        actual[field] = sha

    validate_2016_runtime_authorization_plan_sources(
        repository_root=root,
    )

    if ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_DECISION != "DEC-504":
        raise ValueError("DEC-506 execution authorization decision drift")
    if (
        ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_VERSION
        != "fmp-annual-catalogue-2016-execution-authorization-v1"
    ):
        raise ValueError("DEC-506 execution authorization version drift")
    if ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_PLAN_DECISION != "DEC-505":
        raise ValueError("DEC-506 runtime plan decision drift")
    if (
        ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_PLAN_VERSION
        != "fmp-annual-catalogue-2016-runtime-authorization-plan-v1"
    ):
        raise ValueError("DEC-506 runtime plan version drift")

    return actual


def build_2016_runtime_authorization_install_preflight(
    authorization: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2016_runtime_authorization_install_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2016_execution_authorization(authorization)

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-506 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-506 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-506 main head mismatch")

    if authorization.get("annual_segment_label") != "2016":
        raise ValueError("DEC-506 authorization segment mismatch")
    if authorization.get("expected_run_number") != 377:
        raise ValueError("DEC-506 authorization run number mismatch")
    if authorization.get("expected_run_attempt") != 1:
        raise ValueError("DEC-506 authorization run attempt mismatch")
    if authorization.get("runtime_authorization_installed") is not False:
        raise ValueError("DEC-506 source authorization is already installed")
    if authorization.get("runtime_gate_active") is not False:
        raise ValueError("DEC-506 source authorization gate is already active")

    previous_freeze_run_id = _positive_int(
        authorization.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    authorization_fingerprint = _sha256_hex(
        authorization.get("authorization_fingerprint_sha256"),
        field="authorization fingerprint",
    )
    source_preflight_sha = _sha256_hex(
        authorization.get("source_preflight_canonical_sha256"),
        field="source preflight canonical SHA-256",
    )

    value: dict[str, object] = {
        "decision": (
            ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION
        ),
        "version": (
            ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION
        ),
        **source,
        "source_authorization_decision": "DEC-504",
        "source_authorization_fingerprint_sha256": authorization_fingerprint,
        "source_preflight_canonical_sha256": source_preflight_sha,
        "stage": (
            "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_"
            "INSTALL_PREFLIGHT_READY"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2016",
        "expected_run_number": 377,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": previous_freeze_run_id,
        "expected_current_runtime_source_blob_sha": (
            EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA
        ),
        "dormant_gate_template_path": DORMANT_2016_GATE_TEMPLATE_PATH,
        "dormant_gate_template_blob_sha": (
            EXPECTED_DORMANT_2016_GATE_TEMPLATE_BLOB_SHA
        ),
        "dormant_runtime_target_template_path": (
            DORMANT_RUNTIME_TARGET_TEMPLATE_PATH
        ),
        "dormant_runtime_target_template_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "target_gate_source_path": TARGET_2016_GATE_SOURCE_PATH,
        "target_gate_source_blob_sha": (
            EXPECTED_DORMANT_2016_GATE_TEMPLATE_BLOB_SHA
        ),
        "target_runtime_source_path": TARGET_RUNTIME_SOURCE_PATH,
        "target_runtime_source_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "activation_mutation_file_count": 2,
        "authorization_contract_validated": True,
        "runtime_install_preflight_ready": True,
        "preflight_read_only": True,
        "repository_mutation_authorized": REPOSITORY_MUTATION_AUTHORIZED,
        "runtime_authorization_installed": RUNTIME_AUTHORIZATION_INSTALLED,
        "runtime_gate_active": RUNTIME_GATE_ACTIVE,
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
        "next_gate": (
            "EXACT_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_"
            "AUTHORIZATION_INSTALL_MUTATION"
        ),
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2016_runtime_authorization_install_preflight(value)
    return value


def validate_2016_runtime_authorization_install_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-506 preflight fingerprint mismatch")

    if value.get("decision") != "DEC-506":
        raise ValueError("DEC-506 decision mismatch")
    if value.get("source_authorization_decision") != "DEC-504":
        raise ValueError("DEC-506 source authorization mismatch")
    if value.get("annual_segment_label") != "2016":
        raise ValueError("DEC-506 annual segment mismatch")
    if value.get("expected_run_number") != 377:
        raise ValueError("DEC-506 expected run number mismatch")
    if value.get("expected_run_attempt") != 1:
        raise ValueError("DEC-506 expected run attempt mismatch")
    _positive_int(
        value.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    _sha256_hex(
        value.get("source_authorization_fingerprint_sha256"),
        field="source authorization fingerprint",
    )
    _sha256_hex(
        value.get("source_preflight_canonical_sha256"),
        field="source preflight canonical SHA-256",
    )

    if value.get("activation_mutation_file_count") != 2:
        raise ValueError("DEC-506 activation mutation file count mismatch")
    if value.get("authorization_contract_validated") is not True:
        raise ValueError("DEC-506 authorization contract must be validated")
    if value.get("runtime_install_preflight_ready") is not True:
        raise ValueError("DEC-506 runtime install preflight must be ready")
    if value.get("preflight_read_only") is not True:
        raise ValueError("DEC-506 preflight must remain read-only")

    for field in (
        "repository_mutation_authorized",
        "runtime_authorization_installed",
        "runtime_gate_active",
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
        if value.get(field) is not False:
            raise ValueError(f"DEC-506 {field} must remain false")

    if (
        value.get("next_gate")
        != (
            "EXACT_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_"
            "AUTHORIZATION_INSTALL_MUTATION"
        )
    ):
        raise ValueError("DEC-506 next gate mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION",
    "build_2016_runtime_authorization_install_preflight",
    "validate_2016_runtime_authorization_install_preflight",
    "validate_2016_runtime_authorization_install_preflight_sources",
]
