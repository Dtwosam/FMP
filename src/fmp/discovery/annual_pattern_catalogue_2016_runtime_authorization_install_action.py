from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2016_runtime_authorization_install_preflight import (
    ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION,
    ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION,
    validate_2016_runtime_authorization_install_preflight,
    validate_2016_runtime_authorization_install_preflight_sources,
)
from .annual_pattern_catalogue_2016_runtime_authorization_plan import (
    DORMANT_2016_GATE_TEMPLATE_PATH,
    DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
    EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA,
    EXPECTED_DORMANT_2016_GATE_TEMPLATE_BLOB_SHA,
    EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
    TARGET_2016_GATE_SOURCE_PATH,
    TARGET_RUNTIME_SOURCE_PATH,
)


ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION = "DEC-507"
ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION = (
    "fmp-annual-catalogue-2016-runtime-authorization-install-action-v1"
)

INSTALL_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2016_runtime_authorization_install_preflight.py"
)
EXPECTED_INSTALL_PREFLIGHT_SOURCE_BLOB_SHA = (
    "f39ff9cd4d9a53f5908036641be1031cee8e43c2"
)

REPOSITORY_MUTATION_AUTHORIZED = True
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
        raise ValueError(f"DEC-507 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-507 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-507 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-507 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2016_runtime_authorization_install_action_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    preflight_path = root / INSTALL_PREFLIGHT_SOURCE_PATH
    if not preflight_path.is_file():
        raise ValueError(f"DEC-507 source file missing: {preflight_path}")
    preflight_sha = _git_blob_sha(preflight_path)
    if preflight_sha != EXPECTED_INSTALL_PREFLIGHT_SOURCE_BLOB_SHA:
        raise ValueError("DEC-507 install preflight source blob mismatch")

    validate_2016_runtime_authorization_install_preflight_sources(
        repository_root=root,
    )

    if (
        ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION
        != "DEC-506"
    ):
        raise ValueError("DEC-507 install preflight decision drift")
    if (
        ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION
        != "fmp-annual-catalogue-2016-runtime-authorization-install-preflight-v1"
    ):
        raise ValueError("DEC-507 install preflight version drift")

    return {"install_preflight_source_blob_sha": preflight_sha}


def compile_2016_runtime_authorization_install_action(
    preflight: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2016_runtime_authorization_install_action_sources(
        repository_root=Path(repository_root),
    )
    validate_2016_runtime_authorization_install_preflight(preflight)

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if preflight.get("expected_head_sha") != expected_head_sha:
        raise ValueError("DEC-507 preflight/main head mismatch")
    if main_branch.get("name") != "main":
        raise ValueError("DEC-507 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-507 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-507 current main head mismatch")

    preflight_fingerprint = _sha256_hex(
        preflight.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )

    actions: list[dict[str, object]] = [
        {
            "order": 1,
            "operation": "create",
            "target_path": TARGET_2016_GATE_SOURCE_PATH,
            "expected_target_absent": True,
            "content_source_path": DORMANT_2016_GATE_TEMPLATE_PATH,
            "content_source_blob_sha": (
                EXPECTED_DORMANT_2016_GATE_TEMPLATE_BLOB_SHA
            ),
            "expected_result_blob_sha": (
                EXPECTED_DORMANT_2016_GATE_TEMPLATE_BLOB_SHA
            ),
        },
        {
            "order": 2,
            "operation": "update",
            "target_path": TARGET_RUNTIME_SOURCE_PATH,
            "expected_current_blob_sha": (
                EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA
            ),
            "content_source_path": DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
            "content_source_blob_sha": (
                EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
            ),
            "expected_result_blob_sha": (
                EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
            ),
        },
    ]

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION,
        "version": ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION,
        **source,
        "source_preflight_decision": "DEC-506",
        "source_preflight_fingerprint_sha256": preflight_fingerprint,
        "stage": "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION_READY",
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "activation_condition": "validated_concrete_dec506_preflight_on_exact_main",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2016",
        "expected_run_number": 377,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": preflight.get(
            "previous_annual_freeze_run_id"
        ),
        "action_count": 2,
        "actions": actions,
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
            "APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2016_"
            "RUNTIME_AUTHORIZATION_INSTALL_ACTION"
        ),
    }
    value["install_action_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2016_runtime_authorization_install_action(value)
    return value


def validate_2016_runtime_authorization_install_action(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("install_action_fingerprint_sha256"),
        field="install action fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("install_action_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-507 install action fingerprint mismatch")

    if value.get("decision") != "DEC-507":
        raise ValueError("DEC-507 decision mismatch")
    if value.get("source_preflight_decision") != "DEC-506":
        raise ValueError("DEC-507 source preflight mismatch")
    if value.get("annual_segment_label") != "2016":
        raise ValueError("DEC-507 annual segment mismatch")
    if value.get("expected_run_number") != 377:
        raise ValueError("DEC-507 expected run number mismatch")
    if value.get("expected_run_attempt") != 1:
        raise ValueError("DEC-507 expected run attempt mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    if not isinstance(value.get("previous_annual_freeze_run_id"), int):
        raise ValueError("DEC-507 previous annual freeze run id malformed")

    if value.get("action_count") != 2:
        raise ValueError("DEC-507 action count mismatch")
    actions = value.get("actions")
    if not isinstance(actions, list) or len(actions) != 2:
        raise ValueError("DEC-507 actions inventory mismatch")
    create, update = actions
    if not isinstance(create, Mapping) or not isinstance(update, Mapping):
        raise ValueError("DEC-507 action row malformed")

    create_exact = {
        "order": 1,
        "operation": "create",
        "target_path": TARGET_2016_GATE_SOURCE_PATH,
        "expected_target_absent": True,
        "content_source_path": DORMANT_2016_GATE_TEMPLATE_PATH,
        "content_source_blob_sha": EXPECTED_DORMANT_2016_GATE_TEMPLATE_BLOB_SHA,
        "expected_result_blob_sha": EXPECTED_DORMANT_2016_GATE_TEMPLATE_BLOB_SHA,
    }
    update_exact = {
        "order": 2,
        "operation": "update",
        "target_path": TARGET_RUNTIME_SOURCE_PATH,
        "expected_current_blob_sha": EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA,
        "content_source_path": DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
        "content_source_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "expected_result_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
    }
    if dict(create) != create_exact:
        raise ValueError("DEC-507 create action mismatch")
    if dict(update) != update_exact:
        raise ValueError("DEC-507 update action mismatch")

    if value.get("repository_mutation_authorized") is not True:
        raise ValueError("DEC-507 repository mutation must be authorized")
    for field in (
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
            raise ValueError(f"DEC-507 {field} must remain false")

    if (
        value.get("next_gate")
        != (
            "APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2016_"
            "RUNTIME_AUTHORIZATION_INSTALL_ACTION"
        )
    ):
        raise ValueError("DEC-507 next gate mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION",
    "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION",
    "compile_2016_runtime_authorization_install_action",
    "validate_2016_runtime_authorization_install_action",
    "validate_2016_runtime_authorization_install_action_sources",
]
