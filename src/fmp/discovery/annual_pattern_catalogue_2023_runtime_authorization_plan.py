from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_execution_authorization import (
    ANNUAL_CATALOGUE_2023_EXECUTION_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_2023_EXECUTION_AUTHORIZATION_VERSION,
    validate_2023_execution_authorization,
)


ANNUAL_CATALOGUE_2023_RUNTIME_AUTHORIZATION_PLAN_DECISION = "DEC-604"
ANNUAL_CATALOGUE_2023_RUNTIME_AUTHORIZATION_PLAN_VERSION = (
    "fmp-annual-catalogue-2023-runtime-authorization-plan-v1"
)

EXECUTION_AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2023_execution_authorization.py"
)
EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA = (
    "2c4292abadbffb9dd87edaab67d9e32783facae7"
)
EXECUTION_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2023_execution_preflight.py"
)
EXPECTED_EXECUTION_PREFLIGHT_SOURCE_BLOB_SHA = (
    "d7e0823bc0d7513b6d7ee27a02fb5b519bc4818b"
)
CURRENT_RUNTIME_SOURCE_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA = (
    "f2734c7ea32355b1024d1097812578b23fc4409d"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

DORMANT_2023_GATE_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "annual_pattern_catalogue_2023_runtime_authorization.py.disabled"
)
EXPECTED_DORMANT_2023_GATE_TEMPLATE_BLOB_SHA = (
    "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191"
)
DORMANT_RUNTIME_TARGET_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "annual_pattern_catalogue_runtime_with_2023_authorization.py.disabled"
)
EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA = (
    "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3"
)

TARGET_2023_GATE_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py"
)
TARGET_RUNTIME_SOURCE_PATH = CURRENT_RUNTIME_SOURCE_PATH

EXPECTED_RUN_NUMBER = 385
EXPECTED_RUN_ATTEMPT = 1
EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37663157285

SOURCE_AUTHORIZATION_WORKFLOW_RUN_ID = 37685394468
SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA = (
    "a4235aa2bc8501da8a7273d80a133e712cd04721"
)
SOURCE_AUTHORIZATION_ARTIFACT_ID = 11511180606
SOURCE_AUTHORIZATION_ARTIFACT_DIGEST = (
    "sha256:ee25e982971a0c3ce65f4a6b25a2229e35e7a2f3285b30f2bfcdff87734c311a"
)
SOURCE_AUTHORIZATION_FINGERPRINT_SHA256 = (
    "dc1f6dc96e4bdbf527ffba49be9df175310389737bd7c70ca945bd260baf3946"
)
SOURCE_AUTHORIZATION_CANONICAL_SHA256 = (
    "aa9b4e8c4bceee20f5d03d8579e1b0407bc21b6597528707f003f5f0bc5aef7d"
)

RUNTIME_AUTHORIZATION_INSTALLED = False
RUNTIME_GATE_ACTIVE = False
REPOSITORY_MUTATION_AUTHORIZED = False
ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RUN_386_OR_LATER_AUTHORIZED = False
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
    payload = Path(path).read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _sha256_hex(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"DEC-604 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-604 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2023_runtime_authorization_plan_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "execution_authorization_source_blob_sha": (
            root / EXECUTION_AUTHORIZATION_SOURCE_PATH,
            EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA,
        ),
        "execution_preflight_source_blob_sha": (
            root / EXECUTION_PREFLIGHT_SOURCE_PATH,
            EXPECTED_EXECUTION_PREFLIGHT_SOURCE_BLOB_SHA,
        ),
        "current_runtime_source_blob_sha": (
            root / CURRENT_RUNTIME_SOURCE_PATH,
            EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
        "dormant_2023_gate_template_blob_sha": (
            root / DORMANT_2023_GATE_TEMPLATE_PATH,
            EXPECTED_DORMANT_2023_GATE_TEMPLATE_BLOB_SHA,
        ),
        "dormant_runtime_target_template_blob_sha": (
            root / DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (source_path, expected_sha) in expected.items():
        if not source_path.is_file():
            raise ValueError(f"DEC-604 source file missing: {source_path}")
        sha = _git_blob_sha(source_path)
        if sha != expected_sha:
            raise ValueError(f"DEC-604 {field} mismatch")
        actual[field] = sha

    target_gate = root / TARGET_2023_GATE_SOURCE_PATH
    if target_gate.exists():
        raise ValueError("DEC-604 requires 2023 runtime gate target to remain absent")

    current_runtime = (root / CURRENT_RUNTIME_SOURCE_PATH).read_text(encoding="utf-8")
    if "annual_pattern_catalogue_2023_runtime_authorization" in current_runtime:
        raise ValueError("DEC-604 current runtime is already wired to 2023")
    if 'segment == "2023"' in current_runtime:
        raise ValueError("DEC-604 current runtime already routes 2023")

    gate_template = (root / DORMANT_2023_GATE_TEMPLATE_PATH).read_text(
        encoding="utf-8"
    )
    required_gate = (
        'AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2023"',
        "EXPECTED_RUN_NUMBER = 385",
        "EXPECTED_RUN_ATTEMPT = 1",
        "EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37663157285",
        "require_2023_execution_authorized",
        "RUN_386_OR_LATER_AUTHORIZED = False",
        "PROTECTED_HISTORY_ACCESS_AUTHORIZED = True",
        "CROSS_YEAR_COMPARISON_AUTHORIZED = False",
        "TRADING_AUTHORIZED = False",
    )
    for needle in required_gate:
        if needle not in gate_template:
            raise ValueError(f"DEC-604 dormant gate drift: {needle}")

    runtime_target = (root / DORMANT_RUNTIME_TARGET_TEMPLATE_PATH).read_text(
        encoding="utf-8"
    )
    required_runtime = (
        "require_2023_execution_authorized",
        'segment == "2023" and effective_run_number == 385',
        "DEC-604 2023 execution requires previous annual freeze run id",
        "require_2022_execution_authorized",
        'segment == "2022" and effective_run_number == 384',
        "require_2021_execution_authorized",
        'segment == "2021" and effective_run_number == 383',
        "require_2020_execution_authorized",
        'segment == "2020" and effective_run_number == 382',
        'segment == "2019" and effective_run_number == 381',
        'segment == "2018" and effective_run_number == 380',
        'segment == "2017" and effective_run_number == 379',
        'segment == "2016" and effective_run_number == 378',
        "if effective_run_number == 377:",
        "if effective_run_number == 376:",
    )
    for needle in required_runtime:
        if needle not in runtime_target:
            raise ValueError(f"DEC-604 runtime target drift: {needle}")
    return actual


def build_2023_runtime_authorization_plan(
    authorization: Mapping[str, object],
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_2023_runtime_authorization_plan_sources(
        repository_root=Path(repository_root),
    )
    validate_2023_execution_authorization(authorization)

    if authorization.get("decision") != "DEC-603":
        raise ValueError("DEC-604 source authorization decision mismatch")
    if (
        authorization.get("authorization_fingerprint_sha256")
        != SOURCE_AUTHORIZATION_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-604 source authorization fingerprint mismatch")
    if authorization.get("annual_segment_label") != "2023":
        raise ValueError("DEC-604 annual segment mismatch")
    if authorization.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-604 expected run number mismatch")
    if authorization.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-604 expected run attempt mismatch")
    if authorization.get("previous_annual_freeze_run_id") != (
        EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-604 predecessor run id mismatch")
    if authorization.get("runtime_authorization_installed") is not False:
        raise ValueError("DEC-604 source authorization already installed")
    if authorization.get("runtime_gate_active") is not False:
        raise ValueError("DEC-604 source authorization gate already active")
    if authorization.get("dispatch_action_executed") is not False:
        raise ValueError("DEC-604 source authorization already dispatched")
    for field in (
        "rerun_authorized",
        "retry_authorized",
        "replacement_run_authorized",
        "run_386_or_later_authorized",
        "next_segment_execution_authorized",
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
        if authorization.get(field) is not False:
            raise ValueError(f"DEC-604 source authorization {field} drift")

    if authorization.get("protected_history_access_authorized") is not True:
        raise ValueError("DEC-604 source authorization protected-history authority missing")
    if authorization.get("protected_catalogue_segment") is not True:
        raise ValueError("DEC-604 source authorization protected segment mismatch")
    if authorization.get("governing_method_decision") != "DEC-469":
        raise ValueError("DEC-604 source authorization method mismatch")
    if authorization.get("governing_protocol_decision") != "DEC-470":
        raise ValueError("DEC-604 source authorization protocol mismatch")

    authorization_fingerprint = _sha256_hex(
        authorization.get("authorization_fingerprint_sha256"),
        field="source authorization fingerprint",
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2023_RUNTIME_AUTHORIZATION_PLAN_DECISION,
        "version": ANNUAL_CATALOGUE_2023_RUNTIME_AUTHORIZATION_PLAN_VERSION,
        **source,
        "stage": "ANNUAL_CATALOGUE_2023_RUNTIME_AUTHORIZATION_DORMANT_PLAN_READY",
        "source_authorization_decision": "DEC-603",
        "source_authorization_version": (
            "fmp-annual-catalogue-2023-execution-authorization-v1"
        ),
        "source_authorization_workflow_run_id": SOURCE_AUTHORIZATION_WORKFLOW_RUN_ID,
        "source_authorization_workflow_head_sha": SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA,
        "source_authorization_artifact_id": SOURCE_AUTHORIZATION_ARTIFACT_ID,
        "source_authorization_artifact_digest": SOURCE_AUTHORIZATION_ARTIFACT_DIGEST,
        "source_authorization_fingerprint_sha256": authorization_fingerprint,
        "source_authorization_canonical_sha256": (
            SOURCE_AUTHORIZATION_CANONICAL_SHA256
        ),
        "source_preflight_workflow_run_id": authorization.get(
            "source_preflight_workflow_run_id"
        ),
        "source_preflight_artifact_id": authorization.get(
            "source_preflight_artifact_id"
        ),
        "source_authorization_protected_history_access_authorized": True,
        "protected_catalogue_segment": True,
        "governing_method_decision": "DEC-469",
        "governing_protocol_decision": "DEC-470",
        "protocol_full_collection_catalogue_use_authorized": True,
        "protocol_2023_2026_catalogue_use_authorized": True,
        "annual_segment_label": "2023",
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "previous_annual_freeze_run_required": True,
        "expected_previous_annual_freeze_run_id": (
            EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
        ),
        "target_gate_source_path": TARGET_2023_GATE_SOURCE_PATH,
        "target_runtime_source_path": TARGET_RUNTIME_SOURCE_PATH,
        "target_gate_source_blob_sha": EXPECTED_DORMANT_2023_GATE_TEMPLATE_BLOB_SHA,
        "target_runtime_source_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "runtime_authorization_installed": RUNTIME_AUTHORIZATION_INSTALLED,
        "runtime_gate_active": RUNTIME_GATE_ACTIVE,
        "repository_mutation_authorized": REPOSITORY_MUTATION_AUTHORIZED,
        "annual_workflow_dispatch_authorized": ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": (
            HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED
        ),
        "historical_result_production_authorized": (
            HISTORICAL_RESULT_PRODUCTION_AUTHORIZED
        ),
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "run_386_or_later_authorized": RUN_386_OR_LATER_AUTHORIZED,
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
        "plan_source_only": True,
        "next_gate": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2023_RUNTIME_"
            "AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC604"
        ),
    }
    validate_2023_runtime_authorization_plan(value)
    return value


def validate_2023_runtime_authorization_plan(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    exact = {
        "decision": "DEC-604",
        "version": "fmp-annual-catalogue-2023-runtime-authorization-plan-v1",
        "execution_authorization_source_blob_sha": (
            EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA
        ),
        "execution_preflight_source_blob_sha": (
            EXPECTED_EXECUTION_PREFLIGHT_SOURCE_BLOB_SHA
        ),
        "current_runtime_source_blob_sha": EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "dormant_2023_gate_template_blob_sha": (
            EXPECTED_DORMANT_2023_GATE_TEMPLATE_BLOB_SHA
        ),
        "dormant_runtime_target_template_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "stage": "ANNUAL_CATALOGUE_2023_RUNTIME_AUTHORIZATION_DORMANT_PLAN_READY",
        "source_authorization_decision": "DEC-603",
        "source_authorization_version": (
            "fmp-annual-catalogue-2023-execution-authorization-v1"
        ),
        "source_authorization_workflow_run_id": SOURCE_AUTHORIZATION_WORKFLOW_RUN_ID,
        "source_authorization_workflow_head_sha": SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA,
        "source_authorization_artifact_id": SOURCE_AUTHORIZATION_ARTIFACT_ID,
        "source_authorization_artifact_digest": SOURCE_AUTHORIZATION_ARTIFACT_DIGEST,
        "source_authorization_fingerprint_sha256": (
            SOURCE_AUTHORIZATION_FINGERPRINT_SHA256
        ),
        "source_authorization_canonical_sha256": (
            SOURCE_AUTHORIZATION_CANONICAL_SHA256
        ),
        "source_authorization_protected_history_access_authorized": True,
        "protected_catalogue_segment": True,
        "governing_method_decision": "DEC-469",
        "governing_protocol_decision": "DEC-470",
        "protocol_full_collection_catalogue_use_authorized": True,
        "protocol_2023_2026_catalogue_use_authorized": True,
        "annual_segment_label": "2023",
        "expected_run_number": 385,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_required": True,
        "expected_previous_annual_freeze_run_id": 37663157285,
        "target_gate_source_path": TARGET_2023_GATE_SOURCE_PATH,
        "target_runtime_source_path": TARGET_RUNTIME_SOURCE_PATH,
        "target_gate_source_blob_sha": EXPECTED_DORMANT_2023_GATE_TEMPLATE_BLOB_SHA,
        "target_runtime_source_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "repository_mutation_authorized": False,
        "annual_workflow_dispatch_authorized": False,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_386_or_later_authorized": False,
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
        "plan_source_only": True,
        "next_gate": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2023_RUNTIME_"
            "AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC604"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-604 {field} mismatch")

    for field in (
        "source_authorization_fingerprint_sha256",
        "source_authorization_canonical_sha256",
    ):
        _sha256_hex(value.get(field), field=field)
    if value.get("source_preflight_workflow_run_id") != 37678209687:
        raise ValueError("DEC-604 source preflight workflow run mismatch")
    if value.get("source_preflight_artifact_id") != 11507656390:
        raise ValueError("DEC-604 source preflight artifact mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2023_RUNTIME_AUTHORIZATION_PLAN_DECISION",
    "ANNUAL_CATALOGUE_2023_RUNTIME_AUTHORIZATION_PLAN_VERSION",
    "build_2023_runtime_authorization_plan",
    "validate_2023_runtime_authorization_plan",
    "validate_2023_runtime_authorization_plan_sources",
]
