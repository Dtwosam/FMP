from __future__ import annotations

"""DEC-618: exact-source disarmed YAML amendment PREVIEW, not an installed workflow."""

import difflib
import hashlib
import json
import re
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import (
    ANNUAL_WORKFLOW_BLOB,
    ANNUAL_WORKFLOW_PATH,
    MAIN_REF_GUARD,
    REQUIRED_JOBS,
    _git_blob,
    verify_original_workflow_order,
)

DECISION = "DEC-618"
VERSION = "fmp-2023-run385-disarmed-tag-amendment-preview-v1"
NOT_APPROVED_REF = "refs/tags/fmp/phase8a/2023/run385/dec618-not-authorized"
HARD_STOP_MESSAGE = "DEC-618 DISARMED PREVIEW: tag workflow execution is not authorized"
DISARMED_GUARD = (
    f'test "$GITHUB_REF" = "{NOT_APPROVED_REF}"'
    f'\n          echo "{HARD_STOP_MESSAGE}" >&2'
    '\n          exit 1'
)
LOCKED_FALSE = (
    "candidate_workflow_installed",
    "runtime_amendment_installed",
    "workflow_tag_execution_compatible",
    "immutable_tag_proven",
    "main_exclusive_lock_proven",
    "tag_creation_authorized",
    "tag_protection_mutation_authorized",
    "annual_workflow_dispatch_authorized",
    "dispatch_action_executed",
    "run_385_current_state_independently_verified",
    "retry_authorized",
    "rerun_authorized",
    "replacement_run_authorized",
    "run_386_or_later_authorized",
    "future_year_research_authorized",
    "cross_year_research_authorized",
    "strategy_synthesis_authorized",
    "promotion_authorized",
    "phase8b_authorized",
    "broker_mutation_authorized",
    "demo_order_authorized",
    "live_order_authorized",
    "real_money_authorized",
    "trading_authorized",
)


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _source(root: Path) -> str:
    blob = (root / ANNUAL_WORKFLOW_PATH).read_bytes()
    if _git_blob(blob) != ANNUAL_WORKFLOW_BLOB:
        raise ValueError("DEC-618 original annual workflow source blob drift")
    text = blob.decode("utf-8")
    if verify_original_workflow_order(text) != list(REQUIRED_JOBS):
        raise ValueError("DEC-618 original three guard jobs drift")
    if text.count(MAIN_REF_GUARD) != 3:
        raise ValueError("DEC-618 expected exactly three original main-ref guards")
    return text


def _preview(source: str) -> tuple[str, str]:
    # Refuse any changed original workflow job/guard topology, including test fixtures.
    if verify_original_workflow_order(source) != list(REQUIRED_JOBS):
        raise ValueError("DEC-618 original guard job ordering changed")
    # Never touch disk at the original workflow path: return only a diff.
    preview = source.replace(MAIN_REF_GUARD, DISARMED_GUARD)
    if preview.count(HARD_STOP_MESSAGE) != 3 or preview.count(MAIN_REF_GUARD) != 0:
        raise ValueError("DEC-618 disarmed replacement count mismatch")
    if preview.count(NOT_APPROVED_REF) != 3:
        raise ValueError("DEC-618 unexpected preview ref inventory")
    reconstructed = preview.replace(DISARMED_GUARD, MAIN_REF_GUARD)
    if reconstructed != source:
        raise ValueError("DEC-618 unexpected changes outside original ref guards")
    diff = "".join(difflib.unified_diff(
        source.splitlines(keepends=True),
        preview.splitlines(keepends=True),
        fromfile="a/" + ANNUAL_WORKFLOW_PATH,
        tofile="b/" + ANNUAL_WORKFLOW_PATH + " (DISARMED PREVIEW ONLY)",
    ))
    if diff.count("+" + "          exit 1") != 3:
        raise ValueError("DEC-618 missing three explicit hard stops")
    return preview, diff


def build_2023_disarmed_tag_amendment_preview(*, repository_root: Path) -> dict[str, object]:
    source = _source(Path(repository_root))
    preview, diff = _preview(source)
    report: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        "stage": "NON_EXECUTABLE_DISARMED_SOURCE_PREVIEW_ONLY",
        "repository_full_name": "Dtwosam/FMP",
        "original_workflow_path": ANNUAL_WORKFLOW_PATH,
        "original_workflow_git_blob_sha": ANNUAL_WORKFLOW_BLOB,
        "preview_tag_ref_is_deliberately_unapproved": NOT_APPROVED_REF,
        "hard_stop_message": HARD_STOP_MESSAGE,
        "main_ref_guards_replaced_in_preview": 3,
        "hard_stops_added_in_preview": 3,
        "reviewed_jobs": list(REQUIRED_JOBS),
        "preview_sha256": hashlib.sha256(preview.encode("utf-8")).hexdigest(),
        "preview_unified_diff": diff,
        "original_source_reconstructs_byte_identical": True,
        "preview_hard_stops_are_unconditional": True,
        "no_actual_runtime_sha_ref_binding_provided": True,
        "live_annual_workflow_unchanged": True,
        "live_runtime_unchanged": True,
        "separate_workflow_runtime_amendment_required": True,
        "independent_admin_immutable_ref_witness_required": True,
        "separate_run385_action_decision_required": True,
        "expected_annual_run_number": 385,
        "expected_annual_run_attempt": 1,
        "previous_annual_freeze_run_id": 37663157285,
        "read_only": True,
        "dispatch_blocked": True,
        **{name: False for name in LOCKED_FALSE},
        "next_gate": "SEPARATE_APPROVAL_OF_WORKFLOW_AND_RUNTIME_DESIGN_WITH_ADMIN_WITNESS",
    }
    report["preview_fingerprint_sha256"] = _digest(report)
    validate_2023_disarmed_tag_amendment_preview(report)
    return report


def validate_2023_disarmed_tag_amendment_preview(value: Mapping[str, object]) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-618 invalid preview object")
    unsigned = dict(value)
    fp = unsigned.pop("preview_fingerprint_sha256", None)
    if not isinstance(fp, str) or re.fullmatch(r"[0-9a-f]{64}", fp) is None:
        raise ValueError("DEC-618 fingerprint absent")
    if _digest(unsigned) != fp:
        raise ValueError("DEC-618 fingerprint mismatch")
    required: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        "stage": "NON_EXECUTABLE_DISARMED_SOURCE_PREVIEW_ONLY",
        "repository_full_name": "Dtwosam/FMP",
        "original_workflow_path": ANNUAL_WORKFLOW_PATH,
        "original_workflow_git_blob_sha": ANNUAL_WORKFLOW_BLOB,
        "preview_tag_ref_is_deliberately_unapproved": NOT_APPROVED_REF,
        "hard_stop_message": HARD_STOP_MESSAGE,
        "main_ref_guards_replaced_in_preview": 3,
        "hard_stops_added_in_preview": 3,
        "reviewed_jobs": list(REQUIRED_JOBS),
        "original_source_reconstructs_byte_identical": True,
        "preview_hard_stops_are_unconditional": True,
        "no_actual_runtime_sha_ref_binding_provided": True,
        "live_annual_workflow_unchanged": True,
        "live_runtime_unchanged": True,
        "separate_workflow_runtime_amendment_required": True,
        "independent_admin_immutable_ref_witness_required": True,
        "separate_run385_action_decision_required": True,
        "expected_annual_run_number": 385,
        "expected_annual_run_attempt": 1,
        "previous_annual_freeze_run_id": 37663157285,
        "read_only": True,
        "dispatch_blocked": True,
        **{name: False for name in LOCKED_FALSE},
        "next_gate": "SEPARATE_APPROVAL_OF_WORKFLOW_AND_RUNTIME_DESIGN_WITH_ADMIN_WITNESS",
    }
    allowed = set(required) | {"preview_sha256", "preview_unified_diff", "preview_fingerprint_sha256"}
    if set(value) != allowed:
        raise ValueError("DEC-618 unauthorized report field set")
    for key, expected in required.items():
        actual = value.get(key)
        if type(expected) is bool:
            valid = actual is expected
        elif type(expected) is int:
            valid = type(actual) is int and actual == expected
        else:
            valid = actual == expected
        if not valid:
            raise ValueError("DEC-618 forbidden or changed field: " + key)
    preview_sha = value.get("preview_sha256")
    if not isinstance(preview_sha, str) or re.fullmatch(r"[0-9a-f]{64}", preview_sha) is None:
        raise ValueError("DEC-618 preview SHA invalid")
    diff = value.get("preview_unified_diff")
    if not isinstance(diff, str) or not diff.startswith("--- a/" + ANNUAL_WORKFLOW_PATH):
        raise ValueError("DEC-618 preview diff missing")
    if diff.count("+" + "          exit 1") != 3:
        raise ValueError("DEC-618 diff hard-stop count mismatch")
    if diff.count("+" + "          echo \"" + HARD_STOP_MESSAGE + "\"") != 3:
        raise ValueError("DEC-618 diff disarm message mismatch")
    if diff.count("-          " + MAIN_REF_GUARD) != 3:
        raise ValueError("DEC-618 diff source guards mismatch")
    # Independent validation is *not* a signature check. Rebuild the exact
    # disarmed diff from the separately pinned original source, then compare
    # all bytes and the preview SHA; a re-fingerprinted modified diff must fail.
    original = _source(Path(__file__).resolve().parents[3])
    expected_preview, expected_diff = _preview(original)
    if diff != expected_diff:
        raise ValueError("DEC-618 preview diff mismatch against pinned original source")
    if preview_sha != hashlib.sha256(expected_preview.encode("utf-8")).hexdigest():
        raise ValueError("DEC-618 preview SHA mismatch against pinned disarmed preview")
