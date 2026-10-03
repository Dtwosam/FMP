from __future__ import annotations

import hashlib
from pathlib import Path

from .annual_pattern_catalogue_2017_execution_authorization import (
    ANNUAL_CATALOGUE_2017_EXECUTION_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_2017_EXECUTION_AUTHORIZATION_VERSION,
)


ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_PLAN_DECISION = "DEC-525"
ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_PLAN_VERSION = (
    "fmp-annual-catalogue-2017-runtime-authorization-plan-v1"
)

EXECUTION_AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2017_execution_authorization.py"
)
EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA = (
    "e7c1b20516cff69e6ab177d255b64c95616f9533"
)
EXECUTION_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2017_execution_preflight.py"
)
EXPECTED_EXECUTION_PREFLIGHT_SOURCE_BLOB_SHA = (
    "e800a24b6ab50fdd11ff3c907fe0cc5d647beff9"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

BASE_RUNTIME_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "annual_pattern_catalogue_runtime_with_2016_authorization.py.disabled"
)
EXPECTED_BASE_RUNTIME_SOURCE_BLOB_SHA = (
    "995bb46ddd95563f904243c78ae4fc3cf3308968"
)

DORMANT_2017_GATE_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "annual_pattern_catalogue_2017_runtime_authorization.py.disabled"
)
EXPECTED_DORMANT_2017_GATE_TEMPLATE_BLOB_SHA = (
    "9016baaee0d3fd8915590a399eb8d242a954dfee"
)
DORMANT_RUNTIME_TARGET_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "annual_pattern_catalogue_runtime_with_2017_authorization.py.disabled"
)
EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA = (
    "2ac50ccbdfb40d2971c06711e98e464badd9f1fc"
)

TARGET_2017_GATE_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2017_runtime_authorization.py"
)
TARGET_RUNTIME_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
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


def validate_2017_runtime_authorization_plan_sources(
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
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
        "base_runtime_source_blob_sha": (
            root / BASE_RUNTIME_TEMPLATE_PATH,
            EXPECTED_BASE_RUNTIME_SOURCE_BLOB_SHA,
        ),
        "dormant_2017_gate_template_blob_sha": (
            root / DORMANT_2017_GATE_TEMPLATE_PATH,
            EXPECTED_DORMANT_2017_GATE_TEMPLATE_BLOB_SHA,
        ),
        "dormant_runtime_target_template_blob_sha": (
            root / DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-525 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-525 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2017_EXECUTION_AUTHORIZATION_DECISION != "DEC-524":
        raise ValueError("DEC-525 execution authorization decision drift")
    if (
        ANNUAL_CATALOGUE_2017_EXECUTION_AUTHORIZATION_VERSION
        != "fmp-annual-catalogue-2017-execution-authorization-v1"
    ):
        raise ValueError("DEC-525 execution authorization version drift")

    gate_template = (root / DORMANT_2017_GATE_TEMPLATE_PATH).read_text(
        encoding="utf-8"
    )
    if 'AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2017"' not in gate_template:
        raise ValueError("DEC-525 dormant gate segment drift")
    if "EXPECTED_RUN_NUMBER = 378" not in gate_template:
        raise ValueError("DEC-525 dormant gate run-number drift")
    if "EXPECTED_RUN_ATTEMPT = 1" not in gate_template:
        raise ValueError("DEC-525 dormant gate run-attempt drift")
    if "previous_annual_freeze_run_id" not in gate_template:
        raise ValueError("DEC-525 dormant gate predecessor binding missing")
    if "TRADING_AUTHORIZED = False" not in gate_template:
        raise ValueError("DEC-525 dormant gate trading lock drift")

    runtime_target = (
        root / DORMANT_RUNTIME_TARGET_TEMPLATE_PATH
    ).read_text(encoding="utf-8")
    for required in (
        "require_2017_execution_authorized",
        'segment == "2017" and effective_run_number == 378',
        'segment == "2016" and effective_run_number == 377',
        "if effective_run_number == 376:",
        "DEC-525 2017 execution requires previous annual freeze run id",
    ):
        if required not in runtime_target:
            raise ValueError(f"DEC-525 runtime target missing: {required}")

    return actual


def build_2017_runtime_authorization_plan(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_2017_runtime_authorization_plan_sources(
        repository_root=Path(repository_root),
    )
    return {
        "decision": ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_PLAN_DECISION,
        "version": ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_PLAN_VERSION,
        **source,
        "stage": "ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_DORMANT_PLAN_READY",
        "source_authorization_decision": "DEC-524",
        "source_preflight_decision": "DEC-523",
        "annual_segment_label": "2017",
        "expected_run_number": 378,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_required": True,
        "expected_current_runtime_source_blob_sha": (
            EXPECTED_BASE_RUNTIME_SOURCE_BLOB_SHA
        ),
        "target_gate_source_path": TARGET_2017_GATE_SOURCE_PATH,
        "target_runtime_source_path": TARGET_RUNTIME_SOURCE_PATH,
        "target_gate_source_blob_sha": (
            EXPECTED_DORMANT_2017_GATE_TEMPLATE_BLOB_SHA
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
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_RUNTIME_"
            "AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC524"
        ),
    }


__all__ = [
    "ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_PLAN_DECISION",
    "ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_PLAN_VERSION",
    "build_2017_runtime_authorization_plan",
    "validate_2017_runtime_authorization_plan_sources",
]
