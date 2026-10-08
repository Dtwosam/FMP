from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_dispatch_immutability_audit import (
    PINNED_SOURCES as DEC611_PINNED_SOURCES,
    validate_2023_dispatch_main_immutability_audit,
)
from .annual_pattern_catalogue_2023_dispatch_preflight import (
    _validate_annual_inventory,
)

DECISION = "DEC-612"
VERSION = "fmp-annual-catalogue-2023-main-lock-readiness-v1"
DEC611_HEAD_SHA = "329e467a924ec00956505355f6cc1da7a589207c"
DEC611_RUN_ID = 37778086874
DEC611_ARTIFACT_ID = 11550716769
DEC611_ARTIFACT_DIGEST = (
    "sha256:3a9412e93cabd68eb5f19e73bf2769fa610c081ea10ce5fa370fa2ba59bf1e93"
)
DEC611_FINGERPRINT = (
    "f1842fd06bdba200be7ab521ed2735a9429df4836408a18297888d9c3d6416a5"
)
DEC611_CANONICAL_SHA256 = (
    "5de4c3b87b64795c14f84211c838c9d9e1400c4c32b06d46946cb10a00e3a026"
)
DEC611_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2023_dispatch_immutability_audit.py"
)
DEC611_SOURCE_BLOB_SHA = "39b3898240b887a4f1418a9980fbe3b7b2c6f2d3"

LOCK_OBSERVATIONS = (
    "branch_protected_reported",
    "protection_details_visible",
    "effective_branch_rules_visible",
    "rulesets_visible",
    "lock_branch_enabled",
    "enforce_admins_enabled",
    "fork_sync_disabled",
    "force_pushes_disabled",
    "deletions_disabled",
    "no_reported_bypass_actors",
    "lock_configuration_candidate",
)
DENIED = (
    "main_exclusive_lock_proven",
    "dispatch_atomic_to_vetted_sha",
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


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _commit(value: object) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError("DEC-612 expected head must be 40 hex characters")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("DEC-612 expected head must be hexadecimal") from exc
    if value != value.lower():
        raise ValueError("DEC-612 expected head must be lowercase")
    return value


def _blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data
    ).hexdigest()


def _enabled(protection: Mapping[str, object] | None, field: str) -> bool:
    if protection is None:
        return False
    section = protection.get(field)
    return (
        isinstance(section, Mapping)
        and section.get("enabled") is True
    )


def _disabled(protection: Mapping[str, object] | None, field: str) -> bool:
    if protection is None:
        return False
    section = protection.get(field)
    return (
        isinstance(section, Mapping)
        and section.get("enabled") is False
    )


def _no_bypass(rulesets: object) -> bool:
    # A missing, malformed, or inaccessible ruleset snapshot is never a pass.
    if not isinstance(rulesets, list):
        return False
    for row in rulesets:
        if not isinstance(row, Mapping):
            return False
        if row.get("enforcement") not in {"active", "disabled", "evaluate"}:
            return False
        actors = row.get("bypass_actors")
        if not isinstance(actors, list):
            return False
        if actors:
            return False
    return True


def _observations(
    *,
    main_branch: Mapping[str, object],
    branch_protection: Mapping[str, object] | None,
    effective_branch_rules: object,
    inherited_rulesets: object,
) -> dict[str, bool]:
    protected = main_branch.get("protected") is True
    details = isinstance(branch_protection, Mapping)
    effective = isinstance(effective_branch_rules, list) and all(
        isinstance(x, Mapping) and isinstance(x.get("type"), str)
        for x in effective_branch_rules
    )
    rulesets = isinstance(inherited_rulesets, list)
    value = {
        "branch_protected_reported": protected,
        "protection_details_visible": details,
        "effective_branch_rules_visible": effective,
        "rulesets_visible": rulesets,
        "lock_branch_enabled": _enabled(branch_protection, "lock_branch"),
        "enforce_admins_enabled": _enabled(branch_protection, "enforce_admins"),
        "fork_sync_disabled": _disabled(branch_protection, "allow_fork_syncing"),
        "force_pushes_disabled": _disabled(branch_protection, "allow_force_pushes"),
        "deletions_disabled": _disabled(branch_protection, "allow_deletions"),
        "no_reported_bypass_actors": _no_bypass(inherited_rulesets),
    }
    value["lock_configuration_candidate"] = all(value.values())
    return value


def build_2023_main_lock_readiness(
    *,
    dec611_audit: Mapping[str, object],
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    branch_protection: Mapping[str, object] | None,
    effective_branch_rules: object,
    inherited_rulesets: object,
    expected_head_sha: str,
) -> dict[str, object]:
    validate_2023_dispatch_main_immutability_audit(dec611_audit)
    if dec611_audit.get("expected_head_sha") != DEC611_HEAD_SHA:
        raise ValueError("DEC-612 DEC-611 source head mismatch")
    if dec611_audit.get("audit_fingerprint_sha256") != DEC611_FINGERPRINT:
        raise ValueError("DEC-612 DEC-611 fingerprint mismatch")
    if _digest(dict(dec611_audit)) != DEC611_CANONICAL_SHA256:
        raise ValueError("DEC-612 DEC-611 canonical SHA-256 mismatch")
    if dec611_audit.get("dispatch_blocked") is not True:
        raise ValueError("DEC-612 DEC-611 must be blocked")
    if dec611_audit.get("dispatch_action_executed") is not False:
        raise ValueError("DEC-612 source dispatch already executed")

    source_paths = {
        "dec611_immutability_audit_blob_sha": (
            DEC611_SOURCE_PATH, DEC611_SOURCE_BLOB_SHA
        ),
        **DEC611_PINNED_SOURCES,
    }
    source_hashes: dict[str, str] = {}
    for key, (relative, sha) in source_paths.items():
        path = Path(repository_root) / relative
        if not path.is_file() or _blob_sha(path) != sha:
            raise ValueError(f"DEC-612 source drift: {relative}")
        source_hashes[key] = sha

    head = _commit(expected_head_sha)
    if main_branch.get("name") != "main":
        raise ValueError("DEC-612 must inspect main")
    main_commit = main_branch.get("commit")
    if not isinstance(main_commit, Mapping) or main_commit.get("sha") != head:
        raise ValueError("DEC-612 current main SHA mismatch")
    if type(main_branch.get("protected")) is not bool:
        raise ValueError("DEC-612 branch protection flag missing")
    inventory = _validate_annual_inventory(annual_workflow_runs)
    if inventory["successful_2022_run_id"] != 37663157285:
        raise ValueError("DEC-612 predecessor mismatch")

    flags = _observations(
        main_branch=main_branch,
        branch_protection=branch_protection,
        effective_branch_rules=effective_branch_rules,
        inherited_rulesets=inherited_rulesets,
    )
    if not flags["branch_protected_reported"]:
        blocker = "MAIN_UNPROTECTED"
    elif not flags["lock_configuration_candidate"]:
        blocker = "INSUFFICIENT_LOCK_CONFIGURATION_OR_VISIBILITY"
    else:
        blocker = "LOCK_SNAPSHOT_REQUIRES_EXCLUSIVE_WINDOW_REVIEW"

    result: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        **source_hashes,
        **inventory,
        **flags,
        "stage": "ANNUAL_CATALOGUE_2023_MAIN_LOCK_READINESS_RECORDED",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": head,
        "source_dec611_head_sha": DEC611_HEAD_SHA,
        "source_dec611_workflow_run_id": DEC611_RUN_ID,
        "source_dec611_artifact_id": DEC611_ARTIFACT_ID,
        "source_dec611_artifact_digest": DEC611_ARTIFACT_DIGEST,
        "source_dec611_fingerprint_sha256": DEC611_FINGERPRINT,
        "source_dec611_canonical_sha256": DEC611_CANONICAL_SHA256,
        "annual_segment_label": "2023",
        "previous_annual_freeze_run_id": 37663157285,
        "expected_run_number": 385,
        "expected_run_attempt": 1,
        "workflow_ref": "main",
        "block_reason": blocker,
        "read_only": True,
        "dispatch_blocked": True,
        "dispatch_command_present": False,
        **{key: False for key in DENIED},
        "next_gate": "HUMAN_REVIEW_EXCLUSIVE_MAIN_LOCK_AND_SEPARATE_RUN385_AUTHORIZATION",
    }
    result["readiness_fingerprint_sha256"] = _digest(result)
    validate_2023_main_lock_readiness(result)
    return result


def validate_2023_main_lock_readiness(value: Mapping[str, object]) -> Mapping[str, object]:
    fingerprint = value.get("readiness_fingerprint_sha256")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("DEC-612 readiness fingerprint missing")
    unsigned = dict(value)
    unsigned.pop("readiness_fingerprint_sha256", None)
    if _digest(unsigned) != fingerprint:
        raise ValueError("DEC-612 readiness fingerprint mismatch")
    exact: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        "dec611_immutability_audit_blob_sha": DEC611_SOURCE_BLOB_SHA,
        **{key: sha for key, (_, sha) in DEC611_PINNED_SOURCES.items()},
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
        "stage": "ANNUAL_CATALOGUE_2023_MAIN_LOCK_READINESS_RECORDED",
        "repository_full_name": "Dtwosam/FMP",
        "source_dec611_head_sha": DEC611_HEAD_SHA,
        "source_dec611_workflow_run_id": DEC611_RUN_ID,
        "source_dec611_artifact_id": DEC611_ARTIFACT_ID,
        "source_dec611_artifact_digest": DEC611_ARTIFACT_DIGEST,
        "source_dec611_fingerprint_sha256": DEC611_FINGERPRINT,
        "source_dec611_canonical_sha256": DEC611_CANONICAL_SHA256,
        "annual_segment_label": "2023",
        "previous_annual_freeze_run_id": 37663157285,
        "expected_run_number": 385,
        "expected_run_attempt": 1,
        "workflow_ref": "main",
        "read_only": True,
        "dispatch_blocked": True,
        "dispatch_command_present": False,
        **{key: False for key in DENIED},
        "next_gate": "HUMAN_REVIEW_EXCLUSIVE_MAIN_LOCK_AND_SEPARATE_RUN385_AUTHORIZATION",
    }
    allowed = set(exact) | set(LOCK_OBSERVATIONS) | {
        "expected_head_sha", "block_reason", "readiness_fingerprint_sha256",
    }
    if set(value) != allowed:
        raise ValueError("DEC-612 unauthorized fields")
    for key, expected in exact.items():
        actual = value.get(key)
        valid = (
            actual is expected if type(expected) is bool
            else (type(actual) is int and actual == expected)
            if type(expected) is int else actual == expected
        )
        if not valid:
            raise ValueError(f"DEC-612 {key} mismatch")
    for key in LOCK_OBSERVATIONS:
        if type(value.get(key)) is not bool:
            raise ValueError(f"DEC-612 {key} must be boolean")
    observations = [value[key] for key in LOCK_OBSERVATIONS if key != "lock_configuration_candidate"]
    if value["lock_configuration_candidate"] is not all(observations):
        raise ValueError("DEC-612 lock candidate inconsistent")
    expected_reason = (
        "MAIN_UNPROTECTED"
        if not value["branch_protected_reported"]
        else "LOCK_SNAPSHOT_REQUIRES_EXCLUSIVE_WINDOW_REVIEW"
        if value["lock_configuration_candidate"]
        else "INSUFFICIENT_LOCK_CONFIGURATION_OR_VISIBILITY"
    )
    if value.get("block_reason") != expected_reason:
        raise ValueError("DEC-612 block reason inconsistent")
    _commit(value.get("expected_head_sha"))
    return value


__all__ = [
    "DECISION",
    "VERSION",
    "DEC611_HEAD_SHA",
    "build_2023_main_lock_readiness",
    "validate_2023_main_lock_readiness",
]
