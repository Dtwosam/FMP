from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_dispatch_action_preflight import (
    validate_2023_dispatch_action_preflight,
)
from .annual_pattern_catalogue_2023_dispatch_preflight import (
    _validate_annual_inventory,
)

DECISION = "DEC-611"
VERSION = "fmp-annual-catalogue-2023-dispatch-main-immutability-audit-v1"
DEC610_HEAD_SHA = "58d17adbaf2238b6b774cb69f0434259984d1cb7"
DEC610_WORKFLOW_RUN_ID = 37773291427
DEC610_ARTIFACT_ID = 11547739610
DEC610_ARTIFACT_DIGEST = (
    "sha256:e093274fc52e8e5abdb1bd08455f0fcdb2374bab15f3d507abfea59b91a60143"
)
DEC610_FINGERPRINT = (
    "07f391338fe3d20c5e823f72a14cecdf454aec87a6e7638bdd8774f3c9b4b063"
)
DEC610_CANONICAL_SHA256 = (
    "176cadda04eac41454d401bbabeeadc91e701307bbdd94054890ae89bf65689e"
)

PINNED_SOURCES = {
    "dec610_action_preflight_blob_sha": (
        "src/fmp/discovery/annual_pattern_catalogue_2023_dispatch_action_preflight.py",
        "60923763b844b8a1348cbfcf2612b739b8c7c28a",
    ),
    "dec609_authorization_blob_sha": (
        "src/fmp/discovery/annual_pattern_catalogue_2023_dispatch_authorization.py",
        "b7f55dd68d5054c472b4e070521c411c02a4da3c",
    ),
    "installed_2023_gate_blob_sha": (
        "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py",
        "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
    ),
    "installed_runtime_blob_sha": (
        "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
    ),
    "active_catalogue_workflow_blob_sha": (
        ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
    ),
}
DENIED_FIELDS = (
    "annual_workflow_dispatch_authorized",
    "dispatch_action_executed",
    "protected_history_access_authorized",
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
)


def _canonical(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _fingerprint(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data
    ).hexdigest()


def _check_commit(value: object, *, name: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-611 invalid {name}")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-611 invalid {name}") from exc
    if value.lower() != value:
        raise ValueError(f"DEC-611 invalid {name}")
    return value


def audit_2023_dispatch_main_immutability(
    preflight: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    validate_2023_dispatch_action_preflight(preflight)
    if preflight.get("expected_head_sha") != DEC610_HEAD_SHA:
        raise ValueError("DEC-611 DEC-610 head mismatch")
    if preflight.get("preflight_fingerprint_sha256") != DEC610_FINGERPRINT:
        raise ValueError("DEC-611 DEC-610 fingerprint mismatch")
    if _fingerprint(dict(preflight)) != DEC610_CANONICAL_SHA256:
        raise ValueError("DEC-611 DEC-610 canonical SHA-256 mismatch")
    if preflight.get("expected_run_number") != 385 or type(
        preflight.get("expected_run_number")
    ) is not int:
        raise ValueError("DEC-611 expected annual run mismatch")
    if preflight.get("expected_run_attempt") != 1 or type(
        preflight.get("expected_run_attempt")
    ) is not int:
        raise ValueError("DEC-611 expected annual attempt mismatch")
    if preflight.get("dispatch_action_executed") is not False:
        raise ValueError("DEC-611 dispatch slot already executed")

    sources: dict[str, str] = {}
    for key, (relative, expected) in PINNED_SOURCES.items():
        path = Path(repository_root) / relative
        if not path.is_file():
            raise ValueError(f"DEC-611 missing source {relative}")
        actual = _git_blob_sha(path)
        if actual != expected:
            raise ValueError(f"DEC-611 pinned source drift: {relative}")
        sources[key] = actual
    head = _check_commit(expected_head_sha, name="expected_head_sha")
    if main_branch.get("name") != "main":
        raise ValueError("DEC-611 requires main")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping) or commit.get("sha") != head:
        raise ValueError("DEC-611 current main head mismatch")
    protected = main_branch.get("protected")
    if type(protected) is not bool:
        raise ValueError("DEC-611 main protected flag missing")
    inventory = _validate_annual_inventory(annual_workflow_runs)
    if inventory["successful_2022_run_id"] != 37663157285:
        raise ValueError("DEC-611 predecessor mismatch")

    # GitHub workflow_dispatch binds branch/tag names, not immutable commits.
    # Even "protected": true alone cannot prove that main is exclusively locked:
    # authorized bypasses and concurrent updates may still exist.
    reason = (
        "UNPROTECTED_MUTABLE_MAIN_REF"
        if not protected
        else "EXCLUSIVE_MAIN_LOCK_NOT_PROVEN"
    )
    value: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        **sources,
        **inventory,
        "stage": "ANNUAL_CATALOGUE_2023_DISPATCH_IMMUTABILITY_BLOCKED",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": head,
        "dec610_head_sha": DEC610_HEAD_SHA,
        "dec610_workflow_run_id": DEC610_WORKFLOW_RUN_ID,
        "dec610_artifact_id": DEC610_ARTIFACT_ID,
        "dec610_artifact_digest": DEC610_ARTIFACT_DIGEST,
        "dec610_preflight_fingerprint_sha256": DEC610_FINGERPRINT,
        "dec610_preflight_canonical_sha256": DEC610_CANONICAL_SHA256,
        "annual_segment_label": "2023",
        "previous_annual_freeze_run_id": 37663157285,
        "expected_run_number": 385,
        "expected_run_attempt": 1,
        "annual_workflow_ref": "main",
        "main_branch_protected_reported": protected,
        "main_exclusive_lock_proven": False,
        "dispatch_atomic_to_vetted_sha": False,
        "dispatch_blocked": True,
        "block_reason": reason,
        "audit_read_only": True,
        "dispatch_command_present": False,
        "source_dec610_authorized_annual_dispatch": True,
        "source_dec610_protected_catalogue_segment": True,
        **{key: False for key in DENIED_FIELDS},
        "next_gate": "EXCLUSIVE_MAIN_LOCK_OR_REAUTHORIZED_IMMUTABLE_REF_DESIGN",
    }
    value["audit_fingerprint_sha256"] = _fingerprint(value)
    validate_2023_dispatch_main_immutability_audit(value)
    return value


def validate_2023_dispatch_main_immutability_audit(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    digest = value.get("audit_fingerprint_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("DEC-611 invalid audit fingerprint")
    unsigned = dict(value)
    unsigned.pop("audit_fingerprint_sha256", None)
    if _fingerprint(unsigned) != digest:
        raise ValueError("DEC-611 audit fingerprint mismatch")
    exact: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        **{key: sha for key, (_, sha) in PINNED_SOURCES.items()},
        "annual_workflow_run_count": 10,
        "failed_run_1_id": 37126711695,
        "failed_run_376_id": 37191637168,
        "successful_2015_run_id": 37198002653,
        "successful_2016_run_id": 37206992367,
        "successful_2017_run_id": 37227536041,
        "successful_2018_run_id": 37237817538,
        "successful_2019_run_id": 37310525635,
        "successful_2020_run_id": 37443770076,
        "successful_2021_run_id": 37531960014,
        "successful_2022_run_id": 37663157285,
        "stage": "ANNUAL_CATALOGUE_2023_DISPATCH_IMMUTABILITY_BLOCKED",
        "repository_full_name": "Dtwosam/FMP",
        "dec610_head_sha": DEC610_HEAD_SHA,
        "dec610_workflow_run_id": DEC610_WORKFLOW_RUN_ID,
        "dec610_artifact_id": DEC610_ARTIFACT_ID,
        "dec610_artifact_digest": DEC610_ARTIFACT_DIGEST,
        "dec610_preflight_fingerprint_sha256": DEC610_FINGERPRINT,
        "dec610_preflight_canonical_sha256": DEC610_CANONICAL_SHA256,
        "annual_segment_label": "2023",
        "previous_annual_freeze_run_id": 37663157285,
        "expected_run_number": 385,
        "expected_run_attempt": 1,
        "annual_workflow_ref": "main",
        "main_exclusive_lock_proven": False,
        "dispatch_atomic_to_vetted_sha": False,
        "dispatch_blocked": True,
        "audit_read_only": True,
        "dispatch_command_present": False,
        "source_dec610_authorized_annual_dispatch": True,
        "source_dec610_protected_catalogue_segment": True,
        **{key: False for key in DENIED_FIELDS},
        "next_gate": "EXCLUSIVE_MAIN_LOCK_OR_REAUTHORIZED_IMMUTABLE_REF_DESIGN",
    }
    allowed = set(exact) | {
        "expected_head_sha", "main_branch_protected_reported",
        "block_reason", "audit_fingerprint_sha256",
    }
    if set(value) != allowed:
        raise ValueError("DEC-611 unauthorized field set")
    for key, expected in exact.items():
        actual = value.get(key)
        if type(expected) is bool:
            valid = actual is expected
        elif type(expected) is int:
            valid = type(actual) is int and actual == expected
        else:
            valid = actual == expected
        if not valid:
            raise ValueError(f"DEC-611 {key} mismatch")
    _check_commit(value.get("expected_head_sha"), name="expected_head_sha")
    protected = value.get("main_branch_protected_reported")
    if type(protected) is not bool:
        raise ValueError("DEC-611 invalid branch protection type")
    expected_reason = (
        "EXCLUSIVE_MAIN_LOCK_NOT_PROVEN"
        if protected
        else "UNPROTECTED_MUTABLE_MAIN_REF"
    )
    if value.get("block_reason") != expected_reason:
        raise ValueError("DEC-611 block reason mismatch")
    return value
