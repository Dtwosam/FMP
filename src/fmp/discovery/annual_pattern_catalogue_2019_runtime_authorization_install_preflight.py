from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2019_execution_authorization import (
    ANNUAL_CATALOGUE_2019_EXECUTION_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_2019_EXECUTION_AUTHORIZATION_VERSION,
    validate_2019_execution_authorization,
)
from .annual_pattern_catalogue_2019_runtime_authorization_plan import (
    ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_PLAN_DECISION,
    ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_PLAN_VERSION,
    DORMANT_2019_GATE_TEMPLATE_PATH,
    DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
    EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA,
    EXPECTED_DORMANT_2019_GATE_TEMPLATE_BLOB_SHA,
    EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
    TARGET_2019_GATE_SOURCE_PATH,
    TARGET_RUNTIME_SOURCE_PATH,
    validate_2019_runtime_authorization_plan,
    validate_2019_runtime_authorization_plan_sources,
)


ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION = "DEC-559"
ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2019-runtime-authorization-install-preflight-v1"
)

EXECUTION_AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2019_execution_authorization.py"
)
EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA = (
    "084fa62c7fd4855fc561038d991e1215df2ff73b"
)
RUNTIME_AUTHORIZATION_PLAN_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2019_runtime_authorization_plan.py"
)
EXPECTED_RUNTIME_AUTHORIZATION_PLAN_SOURCE_BLOB_SHA = (
    "41e7adba8b5061028d8adc7ef93d1fc02424039e"
)

SOURCE_PLAN_WORKFLOW_RUN_ID = 37294642532
SOURCE_PLAN_WORKFLOW_HEAD_SHA = "2e8d66e515b9f87023f78ae06c644bf804440501"
SOURCE_PLAN_ARTIFACT_ID = 11337484835
SOURCE_PLAN_ARTIFACT_DIGEST = (
    "sha256:7ee0dbfd168a8a63664419cce85e41a65fde46f9e492dbee65868386d74975a8"
)

EXPECTED_RUN_NUMBER = 381
EXPECTED_RUN_ATTEMPT = 1
EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37237817538

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
        raise ValueError(f"DEC-559 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-559 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-559 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-559 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-559 {field} must be a positive integer")
    return value


def validate_2019_runtime_authorization_install_preflight_sources(
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
    for field, (source_path, expected_sha) in expected.items():
        if not source_path.is_file():
            raise ValueError(f"DEC-559 source file missing: {source_path}")
        sha = _git_blob_sha(source_path)
        if sha != expected_sha:
            raise ValueError(f"DEC-559 {field} mismatch")
        actual[field] = sha

    validate_2019_runtime_authorization_plan_sources(repository_root=root)

    if ANNUAL_CATALOGUE_2019_EXECUTION_AUTHORIZATION_DECISION != "DEC-557":
        raise ValueError("DEC-559 execution authorization decision drift")
    if (
        ANNUAL_CATALOGUE_2019_EXECUTION_AUTHORIZATION_VERSION
        != "fmp-annual-catalogue-2019-execution-authorization-v1"
    ):
        raise ValueError("DEC-559 execution authorization version drift")
    if ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_PLAN_DECISION != "DEC-558":
        raise ValueError("DEC-559 runtime plan decision drift")
    if (
        ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_PLAN_VERSION
        != "fmp-annual-catalogue-2019-runtime-authorization-plan-v1"
    ):
        raise ValueError("DEC-559 runtime plan version drift")
    return actual


def build_2019_runtime_authorization_install_preflight(
    authorization: Mapping[str, object],
    plan: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2019_runtime_authorization_install_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2019_execution_authorization(authorization)
    validate_2019_runtime_authorization_plan(plan)

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-559 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-559 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-559 main head mismatch")

    if authorization.get("annual_segment_label") != "2019":
        raise ValueError("DEC-559 authorization segment mismatch")
    if authorization.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-559 authorization run number mismatch")
    if authorization.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-559 authorization run attempt mismatch")
    if (
        authorization.get("previous_annual_freeze_run_id")
        != EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-559 authorization predecessor mismatch")

    if plan.get("decision") != "DEC-558":
        raise ValueError("DEC-559 source plan decision mismatch")
    if plan.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-559 plan run number mismatch")
    if plan.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-559 plan run attempt mismatch")
    if (
        plan.get("expected_previous_annual_freeze_run_id")
        != EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-559 plan predecessor mismatch")
    if plan.get("source_authorization_fingerprint_sha256") != authorization.get(
        "authorization_fingerprint_sha256"
    ):
        raise ValueError("DEC-559 plan/authorization fingerprint mismatch")
    if plan.get("source_authorization_workflow_run_id") != 37241812968:
        raise ValueError("DEC-559 plan DEC-557 workflow run mismatch")
    if plan.get("source_authorization_artifact_id") != 11317224241:
        raise ValueError("DEC-559 plan DEC-557 artifact mismatch")
    if plan.get("plan_source_only") is not True:
        raise ValueError("DEC-559 source plan must remain source-only")

    for field in (
        "runtime_authorization_installed",
        "runtime_gate_active",
        "repository_mutation_authorized",
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
        if plan.get(field) is not False:
            raise ValueError(f"DEC-559 source plan {field} must remain false")

    authorization_fingerprint = _sha256_hex(
        authorization.get("authorization_fingerprint_sha256"),
        field="authorization fingerprint",
    )
    plan_canonical_sha = _sha256_bytes(_canonical_json(dict(plan)))

    value: dict[str, object] = {
        "decision": (
            ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION
        ),
        "version": (
            ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION
        ),
        **source,
        "source_authorization_decision": "DEC-557",
        "source_authorization_fingerprint_sha256": authorization_fingerprint,
        "source_plan_decision": "DEC-558",
        "source_plan_workflow_run_id": SOURCE_PLAN_WORKFLOW_RUN_ID,
        "source_plan_workflow_head_sha": SOURCE_PLAN_WORKFLOW_HEAD_SHA,
        "source_plan_artifact_id": SOURCE_PLAN_ARTIFACT_ID,
        "source_plan_artifact_digest": SOURCE_PLAN_ARTIFACT_DIGEST,
        "source_plan_canonical_sha256": plan_canonical_sha,
        "stage": "ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2019",
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "previous_annual_freeze_run_id": EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "expected_current_runtime_source_blob_sha": (
            EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA
        ),
        "dormant_gate_template_path": DORMANT_2019_GATE_TEMPLATE_PATH,
        "dormant_gate_template_blob_sha": (
            EXPECTED_DORMANT_2019_GATE_TEMPLATE_BLOB_SHA
        ),
        "dormant_runtime_target_template_path": DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
        "dormant_runtime_target_template_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "target_gate_source_path": TARGET_2019_GATE_SOURCE_PATH,
        "target_gate_source_blob_sha": EXPECTED_DORMANT_2019_GATE_TEMPLATE_BLOB_SHA,
        "target_runtime_source_path": TARGET_RUNTIME_SOURCE_PATH,
        "target_runtime_source_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "activation_mutation_file_count": 2,
        "authorization_contract_validated": True,
        "runtime_plan_validated": True,
        "runtime_install_preflight_ready": True,
        "preflight_read_only": True,
        "repository_mutation_authorized": REPOSITORY_MUTATION_AUTHORIZED,
        "runtime_authorization_installed": RUNTIME_AUTHORIZATION_INSTALLED,
        "runtime_gate_active": RUNTIME_GATE_ACTIVE,
        "annual_workflow_dispatch_authorized": ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
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
            "EXACT_ANNUAL_PATTERN_CATALOGUE_2019_RUNTIME_"
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC559"
        ),
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2019_runtime_authorization_install_preflight(value)
    return value


def validate_2019_runtime_authorization_install_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-559 preflight fingerprint mismatch")

    exact = {
        "decision": "DEC-559",
        "version": "fmp-annual-catalogue-2019-runtime-authorization-install-preflight-v1",
        "execution_authorization_source_blob_sha": (
            EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA
        ),
        "runtime_authorization_plan_source_blob_sha": (
            EXPECTED_RUNTIME_AUTHORIZATION_PLAN_SOURCE_BLOB_SHA
        ),
        "source_authorization_decision": "DEC-557",
        "source_plan_decision": "DEC-558",
        "source_plan_workflow_run_id": SOURCE_PLAN_WORKFLOW_RUN_ID,
        "source_plan_workflow_head_sha": SOURCE_PLAN_WORKFLOW_HEAD_SHA,
        "source_plan_artifact_id": SOURCE_PLAN_ARTIFACT_ID,
        "source_plan_artifact_digest": SOURCE_PLAN_ARTIFACT_DIGEST,
        "stage": "ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2019",
        "expected_run_number": 381,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37237817538,
        "expected_current_runtime_source_blob_sha": (
            EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA
        ),
        "dormant_gate_template_path": DORMANT_2019_GATE_TEMPLATE_PATH,
        "dormant_gate_template_blob_sha": (
            EXPECTED_DORMANT_2019_GATE_TEMPLATE_BLOB_SHA
        ),
        "dormant_runtime_target_template_path": DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
        "dormant_runtime_target_template_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "target_gate_source_path": TARGET_2019_GATE_SOURCE_PATH,
        "target_gate_source_blob_sha": EXPECTED_DORMANT_2019_GATE_TEMPLATE_BLOB_SHA,
        "target_runtime_source_path": TARGET_RUNTIME_SOURCE_PATH,
        "target_runtime_source_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "activation_mutation_file_count": 2,
        "authorization_contract_validated": True,
        "runtime_plan_validated": True,
        "runtime_install_preflight_ready": True,
        "preflight_read_only": True,
        "repository_mutation_authorized": False,
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
            "EXACT_ANNUAL_PATTERN_CATALOGUE_2019_RUNTIME_"
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC559"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-559 {field} mismatch")

    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    _positive_int(
        value.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    for field in (
        "source_authorization_fingerprint_sha256",
        "source_plan_canonical_sha256",
    ):
        _sha256_hex(value.get(field), field=field)
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION",
    "build_2019_runtime_authorization_install_preflight",
    "validate_2019_runtime_authorization_install_preflight",
    "validate_2019_runtime_authorization_install_preflight_sources",
]
