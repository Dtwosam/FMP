from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2022_execution_authorization import (
    ANNUAL_CATALOGUE_2022_EXECUTION_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_2022_EXECUTION_AUTHORIZATION_VERSION,
    validate_2022_execution_authorization,
)
from .annual_pattern_catalogue_2022_runtime_authorization_plan import (
    ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_PLAN_DECISION,
    ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_PLAN_VERSION,
    DORMANT_2022_GATE_TEMPLATE_PATH,
    DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
    EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA,
    EXPECTED_DORMANT_2022_GATE_TEMPLATE_BLOB_SHA,
    EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
    TARGET_2022_GATE_SOURCE_PATH,
    TARGET_RUNTIME_SOURCE_PATH,
    validate_2022_runtime_authorization_plan,
    validate_2022_runtime_authorization_plan_sources,
)


ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION = "DEC-594"
ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2022-runtime-authorization-install-preflight-v1"
)

EXECUTION_AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2022_execution_authorization.py"
)
EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA = (
    "e68e9f1ee41ca89f0ae3d7758d59b4ce8c5823bb"
)
RUNTIME_AUTHORIZATION_PLAN_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2022_runtime_authorization_plan.py"
)
EXPECTED_RUNTIME_AUTHORIZATION_PLAN_SOURCE_BLOB_SHA = (
    "d7710ab16dde2eea6b0d93dc6387c6cc489b30d7"
)

SOURCE_PLAN_WORKFLOW_RUN_ID = 37611869958
SOURCE_PLAN_WORKFLOW_HEAD_SHA = "9d53e2f11746ccff7e525a1df1d10427fdfdd2be"
SOURCE_PLAN_ARTIFACT_ID = 11477773270
SOURCE_PLAN_ARTIFACT_DIGEST = (
    "sha256:ff974250ff9a09069e77f8c61e96649c9318e83dfcccab74e8dfd3dd07fed420"
)
SOURCE_PLAN_CANONICAL_SHA256 = (
    "2ed8681de71e27f9767f75a9e47861044c81c3886639195e412495613acd09fd"
)


EXPECTED_RUN_NUMBER = 384
EXPECTED_RUN_ATTEMPT = 1
EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37531960014

REPOSITORY_MUTATION_AUTHORIZED = False
RUNTIME_AUTHORIZATION_INSTALLED = False
RUNTIME_GATE_ACTIVE = False
ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
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
        raise ValueError(f"DEC-594 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-594 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-594 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-594 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-594 {field} must be a positive integer")
    return value


def validate_2022_runtime_authorization_install_preflight_sources(
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
            raise ValueError(f"DEC-594 source file missing: {source_path}")
        sha = _git_blob_sha(source_path)
        if sha != expected_sha:
            raise ValueError(f"DEC-594 {field} mismatch")
        actual[field] = sha

    validate_2022_runtime_authorization_plan_sources(repository_root=root)

    if ANNUAL_CATALOGUE_2022_EXECUTION_AUTHORIZATION_DECISION != "DEC-592":
        raise ValueError("DEC-594 execution authorization decision drift")
    if (
        ANNUAL_CATALOGUE_2022_EXECUTION_AUTHORIZATION_VERSION
        != "fmp-annual-catalogue-2022-execution-authorization-v1"
    ):
        raise ValueError("DEC-594 execution authorization version drift")
    if ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_PLAN_DECISION != "DEC-593":
        raise ValueError("DEC-594 runtime plan decision drift")
    if (
        ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_PLAN_VERSION
        != "fmp-annual-catalogue-2022-runtime-authorization-plan-v1"
    ):
        raise ValueError("DEC-594 runtime plan version drift")
    return actual


def build_2022_runtime_authorization_install_preflight(
    authorization: Mapping[str, object],
    plan: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2022_runtime_authorization_install_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2022_execution_authorization(authorization)
    validate_2022_runtime_authorization_plan(plan)

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-594 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-594 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-594 main head mismatch")

    if authorization.get("annual_segment_label") != "2022":
        raise ValueError("DEC-594 authorization segment mismatch")
    if authorization.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-594 authorization run number mismatch")
    if authorization.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-594 authorization run attempt mismatch")
    if (
        authorization.get("previous_annual_freeze_run_id")
        != EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-594 authorization predecessor mismatch")

    if plan.get("decision") != "DEC-593":
        raise ValueError("DEC-594 source plan decision mismatch")
    if plan.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-594 plan run number mismatch")
    if plan.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-594 plan run attempt mismatch")
    if (
        plan.get("expected_previous_annual_freeze_run_id")
        != EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-594 plan predecessor mismatch")
    if plan.get("source_authorization_fingerprint_sha256") != authorization.get(
        "authorization_fingerprint_sha256"
    ):
        raise ValueError("DEC-594 plan/authorization fingerprint mismatch")
    if plan.get("source_authorization_workflow_run_id") != 37608559036:
        raise ValueError("DEC-594 plan DEC-592 workflow run mismatch")
    if plan.get("source_authorization_artifact_id") != 11475911390:
        raise ValueError("DEC-594 plan DEC-592 artifact mismatch")
    if plan.get("plan_source_only") is not True:
        raise ValueError("DEC-594 source plan must remain source-only")

    for field in (
        "runtime_authorization_installed",
        "runtime_gate_active",
        "repository_mutation_authorized",
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
        if plan.get(field) is not False:
            raise ValueError(f"DEC-594 source plan {field} must remain false")

    authorization_fingerprint = _sha256_hex(
        authorization.get("authorization_fingerprint_sha256"),
        field="authorization fingerprint",
    )
    plan_canonical_sha = _sha256_bytes(_canonical_json(dict(plan)))
    if plan_canonical_sha != SOURCE_PLAN_CANONICAL_SHA256:
        raise ValueError("DEC-594 source plan canonical SHA-256 mismatch")

    value: dict[str, object] = {
        "decision": (
            ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION
        ),
        "version": (
            ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION
        ),
        **source,
        "source_authorization_decision": "DEC-592",
        "source_authorization_fingerprint_sha256": authorization_fingerprint,
        "source_plan_decision": "DEC-593",
        "source_plan_workflow_run_id": SOURCE_PLAN_WORKFLOW_RUN_ID,
        "source_plan_workflow_head_sha": SOURCE_PLAN_WORKFLOW_HEAD_SHA,
        "source_plan_artifact_id": SOURCE_PLAN_ARTIFACT_ID,
        "source_plan_artifact_digest": SOURCE_PLAN_ARTIFACT_DIGEST,
        "source_plan_canonical_sha256": plan_canonical_sha,
        "stage": "ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2022",
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "previous_annual_freeze_run_id": EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "expected_current_runtime_source_blob_sha": (
            EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA
        ),
        "dormant_gate_template_path": DORMANT_2022_GATE_TEMPLATE_PATH,
        "dormant_gate_template_blob_sha": (
            EXPECTED_DORMANT_2022_GATE_TEMPLATE_BLOB_SHA
        ),
        "dormant_runtime_target_template_path": DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
        "dormant_runtime_target_template_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "target_gate_source_path": TARGET_2022_GATE_SOURCE_PATH,
        "target_gate_source_blob_sha": EXPECTED_DORMANT_2022_GATE_TEMPLATE_BLOB_SHA,
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
        "next_gate": (
            "EXACT_ANNUAL_PATTERN_CATALOGUE_2022_RUNTIME_"
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC594"
        ),
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2022_runtime_authorization_install_preflight(value)
    return value


def validate_2022_runtime_authorization_install_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-594 preflight fingerprint mismatch")

    exact = {
        "decision": "DEC-594",
        "version": "fmp-annual-catalogue-2022-runtime-authorization-install-preflight-v1",
        "execution_authorization_source_blob_sha": (
            EXPECTED_EXECUTION_AUTHORIZATION_SOURCE_BLOB_SHA
        ),
        "runtime_authorization_plan_source_blob_sha": (
            EXPECTED_RUNTIME_AUTHORIZATION_PLAN_SOURCE_BLOB_SHA
        ),
        "source_authorization_decision": "DEC-592",
        "source_plan_decision": "DEC-593",
        "source_plan_workflow_run_id": SOURCE_PLAN_WORKFLOW_RUN_ID,
        "source_plan_workflow_head_sha": SOURCE_PLAN_WORKFLOW_HEAD_SHA,
        "source_plan_artifact_id": SOURCE_PLAN_ARTIFACT_ID,
        "source_plan_artifact_digest": SOURCE_PLAN_ARTIFACT_DIGEST,
        "source_plan_canonical_sha256": SOURCE_PLAN_CANONICAL_SHA256,
        "stage": "ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2022",
        "expected_run_number": 384,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37531960014,
        "expected_current_runtime_source_blob_sha": (
            EXPECTED_CURRENT_RUNTIME_SOURCE_BLOB_SHA
        ),
        "dormant_gate_template_path": DORMANT_2022_GATE_TEMPLATE_PATH,
        "dormant_gate_template_blob_sha": (
            EXPECTED_DORMANT_2022_GATE_TEMPLATE_BLOB_SHA
        ),
        "dormant_runtime_target_template_path": DORMANT_RUNTIME_TARGET_TEMPLATE_PATH,
        "dormant_runtime_target_template_blob_sha": (
            EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
        ),
        "target_gate_source_path": TARGET_2022_GATE_SOURCE_PATH,
        "target_gate_source_blob_sha": EXPECTED_DORMANT_2022_GATE_TEMPLATE_BLOB_SHA,
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
        "next_gate": (
            "EXACT_ANNUAL_PATTERN_CATALOGUE_2022_RUNTIME_"
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC594"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-594 {field} mismatch")

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
    "ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_VERSION",
    "build_2022_runtime_authorization_install_preflight",
    "validate_2022_runtime_authorization_install_preflight",
    "validate_2022_runtime_authorization_install_preflight_sources",
]
