from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2018_runtime_authorization_install_preflight import (
    ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION,
    ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION,
    validate_2018_runtime_authorization_install_preflight,
    validate_2018_runtime_authorization_install_preflight_sources,
)
from .annual_pattern_catalogue_2018_runtime_authorization_plan import (
    DORMANT_2018_GATE_TEMPLATE_PATH,
    DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
    EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA,
    EXPECTED_DORMANT_2018_GATE_TEMPLATE_BLOB_SHA,
    EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
    TARGET_2018_GATE_SOURCE_PATH,
    TARGET_RUNTIME_SOURCE_PATH,
)


ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION = "DEC-549"
ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION = (
    "fmp-annual-catalogue-2018-runtime-authorization-install-action-v1"
)

INSTALL_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2018_runtime_authorization_install_preflight.py"
)
EXPECTED_INSTALL_PREFLIGHT_SOURCE_BLOB_SHA = (
    "49e4549672a27bb8d985b0746d8914122072906d"
)

SOURCE_PREFLIGHT_WORKFLOW_RUN_ID = 37231591329
SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA = (
    "4f21ed0efa53beccc722a7180661e11603e6f14a"
)
SOURCE_PREFLIGHT_ARTIFACT_ID = 11314511176
SOURCE_PREFLIGHT_ARTIFACT_DIGEST = (
    "sha256:993afb2809aa675ee2df789a402cc736a5f4992f906394a2f9161ba66675887c"
)

EXPECTED_RUN_NUMBER = 380
EXPECTED_RUN_ATTEMPT = 1
EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37227536041

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
        raise ValueError(f"DEC-549 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-549 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-549 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-549 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2018_runtime_authorization_install_action_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    preflight_path = root / INSTALL_PREFLIGHT_SOURCE_PATH
    if not preflight_path.is_file():
        raise ValueError(f"DEC-549 source file missing: {preflight_path}")
    preflight_sha = _git_blob_sha(preflight_path)
    if preflight_sha != EXPECTED_INSTALL_PREFLIGHT_SOURCE_BLOB_SHA:
        raise ValueError("DEC-549 install preflight source blob mismatch")

    validate_2018_runtime_authorization_install_preflight_sources(
        repository_root=root,
    )

    if (
        ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION
        != "DEC-548"
    ):
        raise ValueError("DEC-549 install preflight decision drift")
    if (
        ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION
        != "fmp-annual-catalogue-2018-runtime-authorization-install-preflight-v1"
    ):
        raise ValueError("DEC-549 install preflight version drift")

    return {"install_preflight_source_blob_sha": preflight_sha}


def compile_2018_runtime_authorization_install_action(
    preflight: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2018_runtime_authorization_install_action_sources(
        repository_root=Path(repository_root),
    )
    validate_2018_runtime_authorization_install_preflight(preflight)

    if preflight.get("expected_head_sha") != SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA:
        raise ValueError("DEC-549 source preflight head mismatch")
    if preflight.get("source_plan_workflow_run_id") != 37231060551:
        raise ValueError("DEC-549 source plan workflow run mismatch")
    if preflight.get("source_plan_artifact_id") != 11314500352:
        raise ValueError("DEC-549 source plan artifact mismatch")
    if preflight.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-549 source preflight run number mismatch")
    if preflight.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-549 source preflight run attempt mismatch")
    if (
        preflight.get("previous_annual_freeze_run_id")
        != EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-549 source preflight predecessor mismatch")
    if preflight.get("preflight_read_only") is not True:
        raise ValueError("DEC-549 source preflight must remain read-only")
    if preflight.get("repository_mutation_authorized") is not False:
        raise ValueError("DEC-549 source preflight mutation authority drift")

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-549 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-549 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-549 current main head mismatch")

    preflight_fingerprint = _sha256_hex(
        preflight.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )

    actions: list[dict[str, object]] = [
        {
            "order": 1,
            "operation": "create",
            "target_path": TARGET_2018_GATE_SOURCE_PATH,
            "expected_target_absent": True,
            "content_source_path": DORMANT_2018_GATE_TEMPLATE_PATH,
            "content_source_blob_sha": (
                EXPECTED_DORMANT_2018_GATE_TEMPLATE_BLOB_SHA
            ),
            "expected_result_blob_sha": (
                EXPECTED_DORMANT_2018_GATE_TEMPLATE_BLOB_SHA
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
        "decision": ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION,
        "version": ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION,
        **source,
        "source_preflight_decision": "DEC-548",
        "source_preflight_workflow_run_id": SOURCE_PREFLIGHT_WORKFLOW_RUN_ID,
        "source_preflight_workflow_head_sha": SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA,
        "source_preflight_artifact_id": SOURCE_PREFLIGHT_ARTIFACT_ID,
        "source_preflight_artifact_digest": SOURCE_PREFLIGHT_ARTIFACT_DIGEST,
        "source_preflight_fingerprint_sha256": preflight_fingerprint,
        "stage": "ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_ACTION_READY",
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "activation_condition": (
            "validated_concrete_dec548_preflight_and_unchanged_runtime_on_exact_main"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "source_preflight_expected_head_sha": SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA,
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2018",
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "previous_annual_freeze_run_id": EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID,
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
            "APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2018_"
            "RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC549"
        ),
    }
    value["install_action_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2018_runtime_authorization_install_action(value)
    return value


def validate_2018_runtime_authorization_install_action(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("install_action_fingerprint_sha256"),
        field="install action fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("install_action_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-549 install action fingerprint mismatch")

    exact = {
        "decision": "DEC-549",
        "version": "fmp-annual-catalogue-2018-runtime-authorization-install-action-v1",
        "install_preflight_source_blob_sha": EXPECTED_INSTALL_PREFLIGHT_SOURCE_BLOB_SHA,
        "source_preflight_decision": "DEC-548",
        "source_preflight_workflow_run_id": SOURCE_PREFLIGHT_WORKFLOW_RUN_ID,
        "source_preflight_workflow_head_sha": SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA,
        "source_preflight_artifact_id": SOURCE_PREFLIGHT_ARTIFACT_ID,
        "source_preflight_artifact_digest": SOURCE_PREFLIGHT_ARTIFACT_DIGEST,
        "stage": "ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_ACTION_READY",
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "activation_condition": (
            "validated_concrete_dec548_preflight_and_unchanged_runtime_on_exact_main"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "source_preflight_expected_head_sha": SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA,
        "annual_segment_label": "2018",
        "expected_run_number": 380,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37227536041,
        "action_count": 2,
        "repository_mutation_authorized": True,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "annual_workflow_dispatch_authorized": False,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
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
            "APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2018_"
            "RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC549"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-549 {field} mismatch")

    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    _sha256_hex(
        value.get("source_preflight_fingerprint_sha256"),
        field="source preflight fingerprint",
    )

    actions = value.get("actions")
    if not isinstance(actions, list) or len(actions) != 2:
        raise ValueError("DEC-549 actions inventory mismatch")
    create, update = actions
    if not isinstance(create, Mapping) or not isinstance(update, Mapping):
        raise ValueError("DEC-549 action row malformed")

    create_exact = {
        "order": 1,
        "operation": "create",
        "target_path": TARGET_2018_GATE_SOURCE_PATH,
        "expected_target_absent": True,
        "content_source_path": DORMANT_2018_GATE_TEMPLATE_PATH,
        "content_source_blob_sha": EXPECTED_DORMANT_2018_GATE_TEMPLATE_BLOB_SHA,
        "expected_result_blob_sha": EXPECTED_DORMANT_2018_GATE_TEMPLATE_BLOB_SHA,
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
        raise ValueError("DEC-549 create action mismatch")
    if dict(update) != update_exact:
        raise ValueError("DEC-549 update action mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION",
    "ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION",
    "compile_2018_runtime_authorization_install_action",
    "validate_2018_runtime_authorization_install_action",
    "validate_2018_runtime_authorization_install_action_sources",
]
