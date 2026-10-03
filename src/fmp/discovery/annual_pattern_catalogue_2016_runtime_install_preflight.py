from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2016_execution_authorization import (
    ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_VERSION,
    validate_2016_execution_authorization,
)


ANNUAL_CATALOGUE_2016_RUNTIME_INSTALL_PREFLIGHT_DECISION = "DEC-505"
ANNUAL_CATALOGUE_2016_RUNTIME_INSTALL_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2016-runtime-install-preflight-v1"
)

AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2016_execution_authorization.py"
)
EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA = (
    "19d95a11e3ae1684d28ab17020f78bea39003bc8"
)
RUNTIME_SOURCE_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_RUNTIME_SOURCE_BLOB_SHA = (
    "ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "f7e65ee95f472918e390bceedd7cf2f38bbf7e92"
)


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_2016_runtime_install_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "authorization_source_blob_sha": (
            root / AUTHORIZATION_SOURCE_PATH,
            EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA,
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
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-505 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-505 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_DECISION != "DEC-504":
        raise ValueError("DEC-505 source authorization decision drift")
    if (
        ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZATION_VERSION
        != "fmp-annual-catalogue-2016-execution-authorization-v1"
    ):
        raise ValueError("DEC-505 source authorization version drift")

    runtime_text = (root / RUNTIME_SOURCE_PATH).read_text(encoding="utf-8")
    if "annual_pattern_catalogue_2016_execution_authorization" in runtime_text:
        raise ValueError("DEC-505 runtime already imports 2016 authorization")
    if "require_2016_execution_authorized" in runtime_text:
        raise ValueError("DEC-505 runtime already contains 2016 execution gate")

    return actual


def build_2016_runtime_install_preflight(
    authorization: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2016_runtime_install_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2016_execution_authorization(authorization)

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-505 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-505 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-505 main head mismatch")

    if authorization.get("runtime_authorization_installed") is not False:
        raise ValueError("DEC-505 source authorization is already installed")
    if authorization.get("runtime_gate_active") is not False:
        raise ValueError("DEC-505 source runtime gate is already active")

    plan = {
        "path": RUNTIME_SOURCE_PATH,
        "operation": "update",
        "expected_blob_sha": EXPECTED_RUNTIME_SOURCE_BLOB_SHA,
        "required_import_module": (
            "annual_pattern_catalogue_2016_execution_authorization"
        ),
        "required_gate_function": "require_2016_execution_authorized",
        "authorized_segment": "2016",
        "authorized_run_number": 3,
        "authorized_run_attempt": 1,
    }

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2016_RUNTIME_INSTALL_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2016_RUNTIME_INSTALL_PREFLIGHT_VERSION,
        **source,
        "source_authorization_decision": "DEC-504",
        "source_authorization_fingerprint": authorization.get(
            "authorization_fingerprint_sha256"
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2016_RUNTIME_INSTALL_"
            "PREFLIGHT_MUTATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2016",
        "prior_segment_label": "2015",
        "previous_annual_freeze_run_id": authorization.get(
            "previous_annual_freeze_run_id"
        ),
        "expected_run_number": 3,
        "expected_run_attempt": 1,
        "source_authorization_dispatch_authorized": True,
        "source_authorization_execution_authorized": True,
        "runtime_install_preflight_validated": True,
        "planned_mutation_count": 1,
        "planned_mutations": [plan],
        "repository_mutation_authorized": False,
        "runtime_authorization_install_authorized": False,
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
        "preflight_read_only": True,
        "next_gate": (
            "CONCRETE_2016_RUNTIME_AUTHORIZATION_INSTALL_MUTATION_"
            "AFTER_PREFLIGHT"
        ),
    }
    validate_2016_runtime_install_preflight(value)
    return value


def validate_2016_runtime_install_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    if value.get("decision") != "DEC-505":
        raise ValueError("DEC-505 decision mismatch")
    if value.get("source_authorization_decision") != "DEC-504":
        raise ValueError("DEC-505 source authorization decision mismatch")
    if value.get("annual_segment_label") != "2016":
        raise ValueError("DEC-505 annual segment mismatch")
    if value.get("prior_segment_label") != "2015":
        raise ValueError("DEC-505 predecessor mismatch")
    if value.get("expected_run_number") != 3:
        raise ValueError("DEC-505 run number mismatch")
    if value.get("expected_run_attempt") != 1:
        raise ValueError("DEC-505 run attempt mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")

    if value.get("runtime_install_preflight_validated") is not True:
        raise ValueError("DEC-505 install preflight must be validated")
    if value.get("planned_mutation_count") != 1:
        raise ValueError("DEC-505 planned mutation count mismatch")
    mutations = value.get("planned_mutations")
    if not isinstance(mutations, list) or len(mutations) != 1:
        raise ValueError("DEC-505 planned mutation inventory mismatch")
    mutation = mutations[0]
    if not isinstance(mutation, Mapping):
        raise ValueError("DEC-505 planned mutation malformed")
    exact_mutation = {
        "path": RUNTIME_SOURCE_PATH,
        "operation": "update",
        "expected_blob_sha": EXPECTED_RUNTIME_SOURCE_BLOB_SHA,
        "required_import_module": (
            "annual_pattern_catalogue_2016_execution_authorization"
        ),
        "required_gate_function": "require_2016_execution_authorized",
        "authorized_segment": "2016",
        "authorized_run_number": 3,
        "authorized_run_attempt": 1,
    }
    for field, expected in exact_mutation.items():
        if mutation.get(field) != expected:
            raise ValueError(f"DEC-505 planned mutation {field} mismatch")

    for field in (
        "source_authorization_dispatch_authorized",
        "source_authorization_execution_authorized",
    ):
        if value.get(field) is not True:
            raise ValueError(f"DEC-505 {field} must be true")

    for field in (
        "repository_mutation_authorized",
        "runtime_authorization_install_authorized",
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
            raise ValueError(f"DEC-505 {field} must remain false")

    if value.get("preflight_read_only") is not True:
        raise ValueError("DEC-505 preflight must remain read-only")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_RUNTIME_INSTALL_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2016_RUNTIME_INSTALL_PREFLIGHT_VERSION",
    "build_2016_runtime_install_preflight",
    "validate_2016_runtime_install_preflight",
    "validate_2016_runtime_install_preflight_sources",
]
