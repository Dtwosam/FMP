from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2018_execution_authorization import (
    ANNUAL_CATALOGUE_2018_EXECUTION_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_2018_EXECUTION_AUTHORIZATION_VERSION,
    validate_2018_execution_authorization,
)


ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_PLAN_DECISION = "DEC-547"
ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_PLAN_VERSION = (
    "fmp-annual-catalogue-2018-runtime-authorization-plan-v1"
)

EXECUTION_AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2018_execution_authorization.py"
)
EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA = (
    "c50f1480ae6b39764f75974182830f149fc820fc"
)
EXECUTION_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2018_execution_preflight.py"
)
EXPECTED_EXECUTION_PREFLIGHT_SOURCE_BLOB_SHA = (
    "ed71113733ae0034d81914d4c0ab37efb5c4ce6e"
)
CURRENT_RUNTIME_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
)
EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA = (
    "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

DORMANT_2018_GATE_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "annual_pattern_catalogue_2018_runtime_authorization.py.disabled"
)
EXPECTED_DORMANT_2018_GATE_TEMPLATE_BLOB_SHA = (
    "cd50f50156cf74c34cd97d69d24291dc373b390f"
)
DORMANT_RUNTIME_TARGET_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "annual_pattern_catalogue_runtime_with_2018_authorization.py.disabled"
)
EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA = (
    "410180c34a9e3500bbbb42310a5253b993ac7785"
)

TARGET_2018_GATE_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2018_runtime_authorization.py"
)
TARGET_RUNTIME_SOURCE_PATH = CURRENT_RUNTIME_SOURCE_PATH

EXPECTED_RUN_NUMBER = 380
EXPECTED_RUN_ATTEMPT = 1
EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37227536041

SOURCE_AUTHORIZATION_WORKFLOW_RUN_ID = 37229862532
SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA = (
    "8440244e1c77ecaf5773427d6d4efcd1a7d4dc16"
)
SOURCE_AUTHORIZATION_ARTIFACT_ID = 11313482812
SOURCE_AUTHORIZATION_ARTIFACT_DIGEST = (
    "sha256:79e9bd2485160dd59fbb88a2d50f32a52b6cfd573f80555a8716fde4ea18c71e"
)
SOURCE_AUTHORIZATION_FINGERPRINT_SHA256 = (
    "34fe76b3bd30d054853b43f660f996757e8bdb30793c03ad6937cc3078b427a0"
)

RUNTIME_AUTHORIZATION_INSTALLED = False
RUNTIME_GATE_ACTIVE = False
REPOSITORY_MUTATION_AUTHORIZED = False
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


def _sha256_hex(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"DEC-547 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-547 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2018_runtime_authorization_plan_sources(
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
        "dormant_2018_gate_template_blob_sha": (
            root / DORMANT_2018_GATE_TEMPLATE_PATH,
            EXPECTED_DORMANT_2018_GATE_TEMPLATE_BLOB_SHA,
        ),
        "dormant_runtime_target_template_blob_sha": (
            root / DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (source_path, expected_sha) in expected.items():
        if not source_path.is_file():
            raise ValueError(f"DEC-547 source file missing: {source_path}")
        sha = _git_blob_sha(source_path)
        if sha != expected_sha:
            raise ValueError(f"DEC-547 {field} mismatch")
        actual[field] = sha

    target_gate = root / TARGET_2018_GATE_SOURCE_PATH
    if target_gate.exists():
        raise ValueError("DEC-547 requires 2018 runtime gate target to remain absent")

    current_runtime = (root / CURRENT_RUNTIME_SOURCE_PATH).read_text(
        encoding="utf-8"
    )
    if "annual_pattern_catalogue_2018_runtime_authorization" in current_runtime:
        raise ValueError("DEC-547 current runtime is already wired to 2018")
    if 'segment == "2018"' in current_runtime:
        raise ValueError("DEC-547 current runtime already routes 2018")

    gate_template = (root / DORMANT_2018_GATE_TEMPLATE_PATH).read_text(
        encoding="utf-8"
    )
    required_gate = (
        'AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2018"',
        "EXPECTED_RUN_NUMBER = 380",
        "EXPECTED_RUN_ATTEMPT = 1",
        "EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37227536041",
        "require_2018_execution_authorized",
        "RUN_381_OR_LATER_AUTHORIZED = False",
        "TRADING_AUTHORIZED = False",
    )
    for needle in required_gate:
        if needle not in gate_template:
            raise ValueError(f"DEC-547 dormant gate drift: {needle}")

    runtime_target = (
        root / DORMANT_RUNTIME_TARGET_TEMPLATE_PATH
    ).read_text(encoding="utf-8")
    required_runtime = (
        "require_2018_execution_authorized",
        'segment == "2018" and effective_run_number == 380',
        "DEC-547 2018 execution requires previous annual freeze run id",
        'segment == "2017" and effective_run_number == 379',
        "require_2017_execution_authorized",
        'segment == "2016" and effective_run_number == 378',
        "require_2016_execution_authorized",
        "if effective_run_number == 377:",
        "if effective_run_number == 376:",
    )
    for needle in required_runtime:
        if needle not in runtime_target:
            raise ValueError(f"DEC-547 runtime target drift: {needle}")
    return actual


def build_2018_runtime_authorization_plan(
    authorization: Mapping[str, object],
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_2018_runtime_authorization_plan_sources(
        repository_root=Path(repository_root),
    )
    validate_2018_execution_authorization(authorization)

    if authorization.get("decision") != "DEC-546":
        raise ValueError("DEC-547 source authorization decision mismatch")
    if authorization.get("authorization_fingerprint_sha256") != (
        SOURCE_AUTHORIZATION_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-547 source authorization fingerprint mismatch")
    if authorization.get("annual_segment_label") != "2018":
        raise ValueError("DEC-547 annual segment mismatch")
    if authorization.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-547 expected run number mismatch")
    if authorization.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-547 expected run attempt mismatch")
    if (
        authorization.get("previous_annual_freeze_run_id")
        != EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-547 predecessor run id mismatch")
    if authorization.get("runtime_authorization_installed") is not False:
        raise ValueError("DEC-547 source authorization already installed")
    if authorization.get("runtime_gate_active") is not False:
        raise ValueError("DEC-547 source authorization gate already active")
    if authorization.get("dispatch_action_executed") is not False:
        raise ValueError("DEC-547 source authorization already dispatched")
    if authorization.get("trading_authorized") is not False:
        raise ValueError("DEC-547 source authorization trading authority drift")

    authorization_fingerprint = _sha256_hex(
        authorization.get("authorization_fingerprint_sha256"),
        field="source authorization fingerprint",
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_PLAN_DECISION,
        "version": ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_PLAN_VERSION,
        **source,
        "stage": "ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_DORMANT_PLAN_READY",
        "source_authorization_decision": "DEC-546",
        "source_authorization_version": (
            "fmp-annual-catalogue-2018-execution-authorization-v1"
        ),
        "source_authorization_workflow_run_id": SOURCE_AUTHORIZATION_WORKFLOW_RUN_ID,
        "source_authorization_workflow_head_sha": SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA,
        "source_authorization_artifact_id": SOURCE_AUTHORIZATION_ARTIFACT_ID,
        "source_authorization_artifact_digest": SOURCE_AUTHORIZATION_ARTIFACT_DIGEST,
        "source_authorization_fingerprint_sha256": authorization_fingerprint,
        "source_preflight_workflow_run_id": authorization.get(
            "source_preflight_workflow_run_id"
        ),
        "source_preflight_artifact_id": authorization.get(
            "source_preflight_artifact_id"
        ),
        "annual_segment_label": "2018",
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "previous_annual_freeze_run_required": True,
        "expected_previous_annual_freeze_run_id": (
            EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
        ),
        "target_gate_source_path": TARGET_2018_GATE_SOURCE_PATH,
        "target_runtime_source_path": TARGET_RUNTIME_SOURCE_PATH,
        "target_gate_source_blob_sha": (
            EXPECTED_DORMANT_2018_GATE_TEMPLATE_BLOB_SHA
        ),
        "target_runtime_source_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "runtime_authorization_installed": RUNTIME_AUTHORIZATION_INSTALLED,
        "runtime_gate_active": RUNTIME_GATE_ACTIVE,
        "repository_mutation_authorized": REPOSITORY_MUTATION_AUTHORIZED,
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
        "plan_source_only": True,
        "next_gate": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_RUNTIME_"
            "AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC546"
        ),
    }
    validate_2018_runtime_authorization_plan(value)
    return value


def validate_2018_runtime_authorization_plan(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    exact = {
        "decision": "DEC-547",
        "version": "fmp-annual-catalogue-2018-runtime-authorization-plan-v1",
        "execution_authorization_source_blob_sha": (
            EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA
        ),
        "execution_preflight_source_blob_sha": (
            EXPECTED_EXECUTION_PREFLIGHT_SOURCE_BLOB_SHA
        ),
        "current_runtime_source_blob_sha": EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "dormant_2018_gate_template_blob_sha": (
            EXPECTED_DORMANT_2018_GATE_TEMPLATE_BLOB_SHA
        ),
        "dormant_runtime_target_template_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "stage": "ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_DORMANT_PLAN_READY",
        "source_authorization_decision": "DEC-546",
        "source_authorization_version": (
            "fmp-annual-catalogue-2018-execution-authorization-v1"
        ),
        "source_authorization_workflow_run_id": SOURCE_AUTHORIZATION_WORKFLOW_RUN_ID,
        "source_authorization_workflow_head_sha": SOURCE_AUTHORIZATION_WORKFLOW_HEAD_SHA,
        "source_authorization_artifact_id": SOURCE_AUTHORIZATION_ARTIFACT_ID,
        "source_authorization_artifact_digest": SOURCE_AUTHORIZATION_ARTIFACT_DIGEST,
        "source_authorization_fingerprint_sha256": (
            SOURCE_AUTHORIZATION_FINGERPRINT_SHA256
        ),
        "annual_segment_label": "2018",
        "expected_run_number": 380,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_required": True,
        "expected_previous_annual_freeze_run_id": 37227536041,
        "target_gate_source_path": TARGET_2018_GATE_SOURCE_PATH,
        "target_runtime_source_path": TARGET_RUNTIME_SOURCE_PATH,
        "target_gate_source_blob_sha": EXPECTED_DORMANT_2018_GATE_TEMPLATE_BLOB_SHA,
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
        "plan_source_only": True,
        "next_gate": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_RUNTIME_"
            "AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC546"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-547 {field} mismatch")

    _sha256_hex(
        value.get("source_authorization_fingerprint_sha256"),
        field="source authorization fingerprint",
    )
    if value.get("source_preflight_workflow_run_id") != 37229319220:
        raise ValueError("DEC-547 source preflight workflow run mismatch")
    if value.get("source_preflight_artifact_id") != 11313083318:
        raise ValueError("DEC-547 source preflight artifact mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_PLAN_DECISION",
    "ANNUAL_CATALOGUE_2018_RUNTIME_AUTHORIZATION_PLAN_VERSION",
    "build_2018_runtime_authorization_plan",
    "validate_2018_runtime_authorization_plan",
    "validate_2018_runtime_authorization_plan_sources",
]
