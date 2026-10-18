"""DEC-1478: portable, strictly decoded offline CI/source evidence envelope.

No network, GitHub APIs, workflow dispatch, protected original/annual
artifact reads, merge, security settings change, or live trading.

A valid envelope is *caller-supplied* evidence consistency, NOT remotely
authenticated logs or protected annual execution authorization.
"""
from __future__ import annotations

import base64
import binascii
import copy
import json
import math
import re
import unittest
import unicodedata

import test_dec1440_stacked_source_evidence_offline as composite

ENVELOPE_SCHEMA = "fmp-offline-source-bundle-v1"
MAX_TEXT_CHARS = 2_000_000
MAX_TEXT_UTF8_BYTES = 2_000_000
MAX_BLOB_BYTES = 1_000_000
MAX_TOTAL_BLOB_BYTES = 4_000_000
MAX_JSON_NESTING = 512
MAX_JSON_INTEGER_DIGITS = 64
MAX_JSON_OBJECT_MEMBERS = 16384
MAX_JSON_TOTAL_OBJECT_MEMBERS = 32768
MAX_JSON_ARRAY_ITEMS = 16384
MAX_JSON_TOTAL_ARRAY_ITEMS = 65536
MAX_JSON_FLOAT_LITERAL_CHARS = 128
MAX_SOURCE_PATH_CHARS = 4096
MAX_SOURCE_PATH_UTF8_BYTES = 4096
MAX_SOURCE_SEGMENT_UTF8_BYTES = 255
SOURCE_PATH_CONFUSABLE_SEPARATORS = frozenset((
    "\u2044", "\u2215", "\u29f8", "\uff0f",
    "\u2216", "\u29f5", "\uff3c",
))
MAX_SOURCE_ENTRIES_PER_MAP = 8192
MAX_RUNS_PER_ENVELOPE = 4096
MAX_RUN_MAP_ENTRIES = 8192
MAX_RAW_LOG_CHARS_PER_RUN = 2_000_000
MAX_TOTAL_RAW_LOG_CHARS = 4_000_000
MAX_RAW_LOG_UTF8_BYTES_PER_RUN = 2_000_000
MAX_TOTAL_RAW_LOG_UTF8_BYTES = 4_000_000
MAX_INMEMORY_NODES = 200_000
MAX_INMEMORY_DEPTH = 512
MAX_INMEMORY_SCALAR_UNITS = 4_000_000
MAX_INMEMORY_TOTAL_SCALAR_UNITS = 16_000_000
MAX_INMEMORY_SCALAR_UTF8_BYTES = 4_000_000
MAX_INMEMORY_TOTAL_UTF8_BYTES = 16_000_000
MAX_INMEMORY_INTEGER_MAGNITUDE = 10**MAX_JSON_INTEGER_DIGITS-1
VERDICT_FIELDS = frozenset((
    "source_consistency", "diagnostics", "independent_original_os_proof",
    "exclusive_server_dispatch_gate_proven", "can_authorize_annual_run",
))
# Frozen allowlist of diagnostic literals emitted by the reviewed DEC-1440
# composite and its 13 direct source-only reviewer dependencies.
# Never trust an arbitrary caller-controlled or mocked diagnostic identifier.
REVIEWED_NESTED_DIAGNOSTICS = frozenset((
    "BLOB_CHANGED_FILES_UNREVIEWED",
    "BLOB_DELETION_UNREVIEWED",
    "BLOB_LEAF_TYPE_UNREVIEWED",
    "BLOB_PATH_UNREVIEWED",
    "BLOB_REVIEW_INPUT_UNREVIEWED",
    "BLOB_SHA_UNREVIEWED",
    "BLOB_SOURCE_BYTES_SHA_MISMATCH",
    "BLOB_SOURCE_BYTES_UNREVIEWED",
    "BLOB_SOURCE_INVENTORY_UNREVIEWED",
    "CI_JOB_SNAPSHOT_UNREVIEWED",
    "CI_LOG_RECEIPT_INPUT_UNREVIEWED",
    "CI_LOG_RECEIPT_INVENTORY_UNREVIEWED",
    "CI_LOG_RECEIPT_JOB_IDS_UNREVIEWED",
    "CI_LOG_RECEIPT_RUN_IDS_UNREVIEWED",
    "CI_LOG_RECEIPT_RUN_INVENTORY_UNREVIEWED",
    "CI_SOURCE_INVENTORY_UNREVIEWED",
    "COMMIT_TREE_ROOT_UNREVIEWED",
    "COMPARE_FILE_LINE_COUNTS_UNREVIEWED",
    "COMPARE_FILE_LIST_UNREVIEWED",
    "COMPARE_FILE_TOTAL_LINES_MISMATCH",
    "COMPARE_NOT_STRICT_ONE_COMMIT_CHILD",
    "DELETED_OR_UNREVIEWED_SOURCE_FILE",
    "DIFF_COUNT_INPUT_UNREVIEWED",
    "DUAL_CHECKOUT_INPUT_UNREVIEWED",
    "DUAL_CHECKOUT_RUNNER_LOG_INVENTORY_UNREVIEWED",
    "DUAL_CHECKOUT_RUN_ID_UNIQUENESS_UNREVIEWED",
    "DUAL_CHECKOUT_TESTED_MERGE_SHA_DIFFERENT",
    "DUAL_CHECKOUT_WORKFLOW_INVENTORY_UNREVIEWED",
    "GITHUB_MERGE_REF_SHA_MISMATCH",
    "GITHUB_MERGE_REF_UNREVIEWED",
    "GIT_TREE_DIRECTORY_MODE_DRIFT",
    "GIT_TREE_LEAF_MODE_DRIFT",
    "GIT_TREE_NODES_UNREVIEWED",
    "GIT_TREE_PATH_MISSING",
    "GIT_TREE_SNAPSHOT_UNREVIEWED",
    "HEAD_AND_MERGE_COMMIT_UNEXPECTEDLY_EQUAL",
    "HEAD_COMMIT_SHA_MISMATCH",
    "MERGE_AND_HEAD_FILE_TREE_MISMATCH",
    "MERGE_CHECKOUT_INPUT_UNREVIEWED",
    "MERGE_CHECKOUT_SNAPSHOT_UNREVIEWED",
    "MERGE_COMMIT_PARENT_PAIR_UNREVIEWED",
    "MERGE_COMMIT_SHA_UNREVIEWED",
    "MERGE_HISTORICAL_RUN_UNREVIEWED",
    "PHASE3_ACCEPTANCE_GENERATED_BEFORE_CHECKOUT",
    "PHASE3_ACCEPTANCE_RUN_UNREVIEWED",
    "PHASE3_ACCEPTANCE_SNAPSHOT_UNREVIEWED",
    "PHASE3_ACCEPTANCE_TIMESTAMP_BEFORE_CHECKOUT",
    "PHASE3_ATTEMPT_UNREVIEWED",
    "PHASE3_CHECKOUT_ACCEPTANCE_MERGE_MISMATCH",
    "PHASE3_CHECKOUT_ACCEPTANCE_SOURCE_UNREVIEWED",
    "PHASE3_CHECKOUT_ACCEPTANCE_STAGE_UNREVIEWED",
    "PHASE3_CHECKOUT_ACCEPTANCE_TIMESTAMP_UNREVIEWED",
    "PHASE3_CHECKOUT_INDEX_ORDER_INPUT_UNREVIEWED",
    "PHASE3_CHECKOUT_INDEX_ORDER_RUN_ID_UNREVIEWED",
    "PHASE3_CHECKOUT_INDEX_ORDER_RUN_UNREVIEWED",
    "PHASE3_COMMIT_SHA_UNREVIEWED",
    "PHASE3_EVIDENCE_INPUT_UNREVIEWED",
    "PHASE3_INDEX_COMMIT_NOT_TESTED_MERGE",
    "PHASE3_INDEX_FIXTURE_UNREVIEWED",
    "PHASE3_INDEX_PROTOCOL_UNREVIEWED",
    "PHASE3_INDEX_SCENARIO_COUNT_UNREVIEWED",
    "PHASE3_MERGE_HEAD_IDENTITY_UNREVIEWED",
    "PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED",
    "PHASE3_RAW_INDEX_JSON_UNREVIEWED",
    "PHASE3_RAW_INDEX_RECEIPT_INPUT_UNREVIEWED",
    "PHASE3_RAW_INDEX_RECEIPT_UNREVIEWED",
    "PHASE3_RAW_INDEX_RUN_UNREVIEWED",
    "PHASE3_RAW_INDEX_SCHEMA_DRIFT",
    "PHASE3_RAW_INDEX_SHAPE_UNREVIEWED",
    "PHASE3_RAW_INDEX_VS_SUPPLIED_EVIDENCE_MISMATCH",
    "PHASE3_RAW_LOG_CONFLICTING_STAGE_UNREVIEWED",
    "PHASE3_RAW_LOG_INPUT_UNREVIEWED",
    "PHASE3_RAW_LOG_STAGE_CARDINALITY_UNREVIEWED",
    "PHASE3_RAW_LOG_STAGE_ORDER_UNREVIEWED",
    "PHASE3_RAW_LOG_TIMESTAMP_ORDER_UNREVIEWED",
    "PHASE3_RAW_LOG_TIMESTAMP_UNREVIEWED",
    "PHASE3_RAW_SCENARIO_DETERMINISM_UNREVIEWED",
    "PHASE3_RAW_SCENARIO_INVENTORY_UNREVIEWED",
    "PHASE3_RAW_SCENARIO_NAMES_UNREVIEWED",
    "PHASE3_RAW_SCENARIO_SCHEMA_DRIFT",
    "PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH",
    "PHASE3_RAW_UPLOAD_MERGE_NAME_MISMATCH",
    "PHASE3_RAW_UPLOAD_VS_SUPPLIED_EVIDENCE_MISMATCH",
    "PHASE3_RUN_ID_UNREVIEWED",
    "PHASE3_RUN_NOT_REVIEWED_SUCCESS",
    "PHASE3_SCENARIOS_UNREVIEWED",
    "PHASE3_SCENARIO_DETERMINISM_UNREVIEWED",
    "PHASE3_SCENARIO_NAMES_UNREVIEWED",
    "PHASE3_UPLOAD_ID_UNREVIEWED",
    "PHASE3_UPLOAD_MERGE_SHA_NAME_MISMATCH",
    "PHASE3_UPLOAD_NOT_FINALIZED",
    "PHASE3_UPLOAD_RUN_ASSOCIATION_MISMATCH",
    "PRODUCTION_OR_WORKFLOW_PATH_UNREVIEWED",
    "PR_ADDITIONS_UNREVIEWED",
    "PR_CHANGED_FILE_COUNT_UNREVIEWED",
    "PR_COMPARE_ADDITIONS_MISMATCH",
    "PR_COMPARE_DELETIONS_MISMATCH",
    "PR_COMPARE_FILE_COUNT_MISMATCH",
    "PR_HEAD_BASE_SHA_UNREVIEWED",
    "PR_NUMBER_UNREVIEWED",
    "RAW_CI_RUNNER_LOG_INPUT_UNREVIEWED",
    "RAW_CI_RUNNER_LOG_INVENTORY_UNREVIEWED",
    "RAW_CI_RUNNER_LOG_METADATA_MISMATCH",
    "RAW_CI_RUNNER_LOG_RECORD_UNREVIEWED",
    "RENAMED_FROM_PRODUCTION_PATH_UNREVIEWED",
    "RUNNER_CHECKOUT_REF_UNREVIEWED",
    "RUNNER_CHECKOUT_SHA_PREFIX_MISMATCH",
    "RUNNER_FETCH_FULL_SHA_MISMATCH",
    "RUNNER_FETCH_FULL_SHA_UNREVIEWED",
    "RUNNER_LOG_CHECKOUT_SHA_MISMATCH",
    "RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
    "RUNNER_LOG_INPUT_UNREVIEWED",
    "RUNNER_LOG_ORDER_UNREVIEWED",
    "RUNNER_LOG_PARENT_SHA_MISMATCH",
    "RUNNER_LOG_PR_REF_MISMATCH",
    "RUNNER_LOG_STAGE_CARDINALITY_UNREVIEWED",
    "RUNNER_LOG_TIMESTAMP_ORDER_UNREVIEWED",
    "RUNNER_LOG_TIMESTAMP_UNREVIEWED",
    "RUN_HEAD_ASSOCIATION_UNREVIEWED",
    "RUN_NOT_COMPLETED_SUCCESS",
    "TREE_CHAIN_CHANGED_BYTES_UNREVIEWED",
    "TREE_CHAIN_CHANGED_FILES_UNREVIEWED",
    "TREE_CHAIN_CHANGED_PATH_UNREVIEWED",
    "TREE_CHAIN_CHANGE_STATUS_UNREVIEWED",
    "TREE_CHAIN_DUPLICATE_CHANGED_PATH",
    "TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED",
    "TREE_CHAIN_ENTRY_SHA_UNREVIEWED",
    "TREE_CHAIN_INPUT_UNREVIEWED",
    "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH",
    "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB",
    "TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH",
    "TREE_CHAIN_PARENT_NOT_REGULAR_TREE",
    "TREE_CHAIN_ROOT_SHA_UNREVIEWED",
    "TREE_CHAIN_SOURCE_BYTE_INVENTORY_UNREVIEWED",
    "TREE_CHAIN_TREE_ENTRIES_UNREVIEWED",
    "TREE_CHAIN_TREE_OBJECT_UNREVIEWED",
    "TREE_CHAIN_TREE_SNAPSHOT_INVENTORY_UNREVIEWED",
))
REQUIRED = frozenset((
    "schema", "pr", "runs", "jobs_by_run", "compare", "commit", "tree",
    "nodes", "changed_bytes_b64", "ci_workflow_bytes_b64",
    "full_tree_snapshots", "merge_checkout_snapshot", "checkout_by_run",
    "phase3_evidence_snapshot", "raw_ci_runner_logs", "raw_ci_log_receipts",
))
ID_MAPS = frozenset((
    "jobs_by_run", "checkout_by_run", "raw_ci_runner_logs",
    "raw_ci_log_receipts",
))
BYTES_MAPS = frozenset(("changed_bytes_b64", "ci_workflow_bytes_b64"))
DICT_KEYS = REQUIRED - frozenset(("schema", "runs"))


def fail_closed(*codes):
    return {
        "source_consistency": False,
        "diagnostics": tuple(sorted(set(codes))),
        "independent_original_os_proof": False,
        "exclusive_server_dispatch_gate_proven": False,
        "can_authorize_annual_run": False,
    }


def _no_duplicate_keys(pairs):
    # JSON decoder already supplied pairs; refuse oversized objects before
    # constructing their dictionary or invoking nested review.
    if len(pairs) > MAX_JSON_OBJECT_MEMBERS:
        raise ValueError("unreviewed JSON object member count")
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def _bounded_json_pairs_hook():
    """Create one per-document budget shared by every decoded JSON object."""
    total_members = 0

    def accept(pairs):
        nonlocal total_members
        total_members += len(pairs)
        if total_members > MAX_JSON_TOTAL_OBJECT_MEMBERS:
            raise ValueError("unreviewed aggregate JSON member count")
        return _no_duplicate_keys(pairs)

    return accept


def _no_nonfinite(value):
    raise ValueError("nonstandard JSON constant: " + value)


def _json_nesting_within_limit(text):
    """Count only JSON containers outside quoted strings.

    Enforce a bound independent of process-global sys.setrecursionlimit.
    The decoder still validates full syntax and balanced delimiters.
    """
    depth = 0
    in_string = False
    escaped = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            if depth > MAX_JSON_NESTING:
                return False
        elif char in "]}":
            depth -= 1
            if depth < 0:
                return False
    return True


def _portable_source_path_identity(path):
    """Conservatively compare labels across Unicode compatibility forms."""
    return unicodedata.normalize("NFKC", path).casefold()


def _reviewed_source_path(path):
    """Require unambiguous repository-relative POSIX source labels."""
    if (type(path) is not str or not path or
            len(path) > MAX_SOURCE_PATH_CHARS or
            path.startswith("/") or "\\" in path):
        return False
    if ":" in path or not unicodedata.is_normalized("NFC", path):
        return False
    if any(char in SOURCE_PATH_CONFUSABLE_SEPARATORS for char in path):
        return False
    try:
        compatible = unicodedata.normalize("NFKC", path)
        if (len(path.encode("utf-8")) > MAX_SOURCE_PATH_UTF8_BYTES or
                len(compatible.encode("utf-8")) > MAX_SOURCE_PATH_UTF8_BYTES or
                "\\" in compatible or ":" in compatible or
                compatible.startswith("/") or
                compatible.count("/") != path.count("/")):
            return False
        for segment, alias in zip(path.split("/"), compatible.split("/")):
            if (len(segment.encode("utf-8")) >
                    MAX_SOURCE_SEGMENT_UTF8_BYTES or
                    len(alias.encode("utf-8")) >
                    MAX_SOURCE_SEGMENT_UTF8_BYTES or
                    segment in ("", ".", "..") or
                    alias in ("", ".", "..") or
                    segment.endswith((" ", ".")) or
                    alias.endswith((" ", ".")) or
                    re.fullmatch(r"(?i:(CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|COM[1-9¹²³]|LPT[1-9¹²³]))"
                                 r"(?:\..*)?",
                                 unicodedata.normalize("NFKC", segment))
                    is not None):
                return False
    except UnicodeError:
        return False
    # Reject invisible layout/format characters and the full Unicode
    # control inventory, including C1 controls not covered by ASCII checks.
    return not any(
        unicodedata.category(char) in ("Cc", "Cf", "Cs", "Zl", "Zp") or
        (unicodedata.category(char) == "Zs" and char != " ") or
        ord(char) == 0x034F or  # combining grapheme joiner
        0x180B <= ord(char) <= 0x180D or  # Mongolian variation selectors
        0xFE00 <= ord(char) <= 0xFE0F or  # BMP variation selectors
        0xE0100 <= ord(char) <= 0xE01EF or  # supplementary selectors
        0xFDD0 <= ord(char) <= 0xFDEF or  # Unicode noncharacters
        (ord(char) & 0xFFFE) == 0xFFFE  # last two code points of each plane
        for char in path)


def _within_inmemory_structure_budget(root):
    """Iteratively refuse cyclic, excessively deep, or huge input graphs."""
    active = set()
    stack = [(root, 0, False)]
    nodes = 0
    total_scalar_units = 0
    total_utf8_units = 0
    while stack:
        item, depth, leaving = stack.pop()
        if leaving:
            active.remove(id(item))
            continue
        nodes += 1
        if nodes > MAX_INMEMORY_NODES or depth > MAX_INMEMORY_DEPTH:
            return False
        if type(item) not in (dict, list, tuple, str, bytes, int,
                             float, bool, type(None)):
            # Reject unknown Python objects and subclasses before a
            # composite reviewer could invoke their special methods.
            return False
        if (type(item) is int and
                not (-MAX_INMEMORY_INTEGER_MAGNITUDE <= item <=
                     MAX_INMEMORY_INTEGER_MAGNITUDE)):
            # Magnitude comparison enforces the exact decimal digit bound
            # without formatting arbitrarily large integers.
            return False
        if type(item) is float and not math.isfinite(item):
            return False
        if type(item) in (str, bytes):
            units = len(item)
            total_scalar_units += units
            if (units > MAX_INMEMORY_SCALAR_UNITS or
                    total_scalar_units > MAX_INMEMORY_TOTAL_SCALAR_UNITS):
                return False
            try:
                byte_units = (len(item.encode("utf-8")) if type(item) is str
                              else len(item))
            except UnicodeError:
                return False
            total_utf8_units += byte_units
            if (byte_units > MAX_INMEMORY_SCALAR_UTF8_BYTES or
                    total_utf8_units > MAX_INMEMORY_TOTAL_UTF8_BYTES):
                return False
            if type(item) is str and any(
                    0xD800 <= ord(char) <= 0xDFFF for char in item):
                return False
        if type(item) in (dict, list, tuple):
            if id(item) in active:
                return False
            children = len(item) * (2 if type(item) is dict else 1)
            if children > MAX_INMEMORY_NODES:
                return False
            active.add(id(item))
            stack.append((item, depth, True))
            if type(item) is dict:
                for key, value in item.items():
                    stack.append((key, depth+1, False))
                    stack.append((value, depth+1, False))
            else:
                for value in item:
                    stack.append((value, depth+1, False))
    return True


def review_bundle_envelope(envelope):
    """Decode an offline-only JSON-compatible envelope, fail closed on bad input."""
    if type(envelope) is not dict:
        return fail_closed("BUNDLE_SHAPE_UNREVIEWED")
    if any(type(key) is not str for key in envelope):
        # Inventory comparison must not invoke custom key hashing/equality.
        return fail_closed("BUNDLE_KEY_INVENTORY_UNREVIEWED")
    if set(envelope) != REQUIRED:
        return fail_closed("BUNDLE_KEY_INVENTORY_UNREVIEWED")
    if (type(envelope["schema"]) is not str or
            envelope["schema"] != ENVELOPE_SCHEMA):
        return fail_closed("BUNDLE_SCHEMA_UNREVIEWED")
    if type(envelope["runs"]) is not list or any(
            type(envelope[key]) is not dict for key in DICT_KEYS):
        return fail_closed("BUNDLE_CATEGORY_TYPE_UNREVIEWED")
    if len(envelope["runs"]) > MAX_RUNS_PER_ENVELOPE:
        return fail_closed("BUNDLE_RUN_COLLECTION_OVERSIZE")
    if not _within_inmemory_structure_budget(envelope):
        return fail_closed("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED")

    converted = {}
    total_bytes = 0
    # Stable ordering makes the same malformed bundle produce the same
    # diagnostics regardless of PYTHONHASHSEED or JSON field insertion order.
    for key in sorted(REQUIRED - frozenset(("schema",))):
        value = envelope[key]
        if key in ID_MAPS:
            decoded = {}
            if len(value) > MAX_RUN_MAP_ENTRIES:
                return fail_closed("BUNDLE_RUN_MAP_OVERSIZE")
            if any(type(k) is not str for k in value):
                return fail_closed("BUNDLE_RUN_KEY_UNREVIEWED")
            if key == "raw_ci_runner_logs":
                if any(type(log) is not str for log in value.values()):
                    return fail_closed("BUNDLE_RAW_LOG_TEXT_UNREVIEWED")
                if any(len(log) > MAX_RAW_LOG_CHARS_PER_RUN
                       for log in value.values()):
                    return fail_closed("BUNDLE_RAW_LOG_TEXT_OVERSIZE")
                if sum(len(log) for log in value.values()) > MAX_TOTAL_RAW_LOG_CHARS:
                    return fail_closed("BUNDLE_TOTAL_RAW_LOG_OVERSIZE")
                byte_counts = []
                for log in value.values():
                    try:
                        byte_count = len(log.encode("utf-8"))
                    except UnicodeError:
                        return fail_closed("BUNDLE_RAW_LOG_TEXT_UNREVIEWED")
                    if byte_count > MAX_RAW_LOG_UTF8_BYTES_PER_RUN:
                        return fail_closed("BUNDLE_RAW_LOG_UTF8_OVERSIZE")
                    byte_counts.append(byte_count)
                if sum(byte_counts) > MAX_TOTAL_RAW_LOG_UTF8_BYTES:
                    return fail_closed("BUNDLE_TOTAL_RAW_LOG_UTF8_OVERSIZE")
                if any("\x00" in log for log in value.values()):
                    return fail_closed("BUNDLE_RAW_LOG_TEXT_UNREVIEWED")
            for k in sorted(value):
                item = value[k]
                if (type(k) is not str or
                        len(k) > 19 or
                        re.fullmatch(r"[1-9][0-9]*", k) is None):
                    return fail_closed("BUNDLE_RUN_KEY_UNREVIEWED")
                # GitHub run identifiers must fit a signed 64-bit integer.
                # Length and range checks occur before any unbounded int().
                number = int(k)
                if number > 9223372036854775807:
                    return fail_closed("BUNDLE_RUN_KEY_UNREVIEWED")
                if number in decoded:
                    return fail_closed("BUNDLE_RUN_KEY_DUPLICATED")
                decoded[number] = item
            converted[key] = decoded
        elif key in BYTES_MAPS:
            decoded = {}
            if len(value) > MAX_SOURCE_ENTRIES_PER_MAP:
                return fail_closed("BUNDLE_SOURCE_MAP_OVERSIZE")
            if any(type(path) is not str for path in value):
                return fail_closed("BUNDLE_SOURCE_PATH_UNREVIEWED")
            seen_folded = set()
            for path in sorted(value):
                payload = value[path]
                if not _reviewed_source_path(path):
                    return fail_closed("BUNDLE_SOURCE_PATH_UNREVIEWED")
                folded = _portable_source_path_identity(path)
                if folded in seen_folded:
                    return fail_closed("BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED")
                seen_folded.add(folded)
                if type(payload) is not str:
                    return fail_closed("BUNDLE_SOURCE_B64_UNREVIEWED")
                # Check the encoded length *before* allocating decoded bytes.
                # 4*ceil(n/3) is the largest canonical Base64 text for n bytes.
                if len(payload) > 4 * ((MAX_BLOB_BYTES + 2) // 3):
                    return fail_closed("BUNDLE_SOURCE_BLOB_OVERSIZE")
                try:
                    raw = base64.b64decode(payload, validate=True)
                except (binascii.Error, ValueError):
                    return fail_closed("BUNDLE_SOURCE_B64_UNREVIEWED")
                if base64.b64encode(raw).decode("ascii") != payload:
                    return fail_closed("BUNDLE_SOURCE_B64_NONCANONICAL")
                if len(raw) > MAX_BLOB_BYTES:
                    return fail_closed("BUNDLE_SOURCE_BLOB_OVERSIZE")
                total_bytes += len(raw)
                if total_bytes > MAX_TOTAL_BLOB_BYTES:
                    return fail_closed("BUNDLE_TOTAL_SOURCE_OVERSIZE")
                decoded[path] = raw
            converted[key.replace("_b64", "")] = decoded
        else:
            converted[key] = value

    # Changed source and installed CI workflow source inventories have
    # different roles; the same casefolded path cannot claim both roles.
    changed_folded = {_portable_source_path_identity(path) for path in converted["changed_bytes"]}
    ci_folded = {_portable_source_path_identity(path) for path in converted["ci_workflow_bytes"]}
    if changed_folded & ci_folded:
        return fail_closed("BUNDLE_SOURCE_CROSSMAP_COLLISION_UNREVIEWED")

    try:
        # Caller-supplied source evidence must remain untouched even if a
        # downstream checker unexpectedly mutates the decoded graph.
        isolated = copy.deepcopy(converted)
        verdict = composite.review_stacked_draft_evidence(**isolated)
    except (TypeError, ValueError, KeyError, IndexError, AttributeError,
            OverflowError, UnicodeError, RecursionError, RuntimeError,
            AssertionError, OSError) as _:
        return fail_closed("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")
    if (type(verdict) is not dict or
            any(type(key) is not str for key in verdict) or
            set(verdict) != VERDICT_FIELDS or
            verdict.get("independent_original_os_proof") is not False or
            verdict.get("exclusive_server_dispatch_gate_proven") is not False or
            verdict.get("can_authorize_annual_run") is not False or
            type(verdict.get("source_consistency")) is not bool or
            type(verdict.get("diagnostics")) is not tuple or
            len(verdict["diagnostics"]) > 256 or
            any(type(code) is not str or
                code not in REVIEWED_NESTED_DIAGNOSTICS
                for code in verdict["diagnostics"]) or
            # Caller-supplied or mocked reviewers must not return a
            # contradictory success flag or nondeterministic diagnostics.
            (type(verdict["diagnostics"]) is tuple and
             (verdict["source_consistency"] != (not verdict["diagnostics"]) or
              verdict["diagnostics"] != tuple(sorted(set(verdict["diagnostics"])))))):
        # Do not echo arbitrary caller-provided bytes through diagnostics.
        return fail_closed("BUNDLE_RESULT_SHAPE_UNREVIEWED")
    return verdict


def _has_unpaired_json_surrogate(doc):
    """Reject lone UTF-16 surrogate code points in parsed JSON strings.

    JSON decoding can leave such code points in keys or values. Walking
    iteratively avoids relying on the interpreter's recursion limit.
    """
    pending = [doc]
    while pending:
        item = pending.pop()
        if type(item) is str:
            if any(0xD800 <= ord(char) <= 0xDFFF for char in item):
                return True
        elif type(item) is dict:
            pending.extend(item.keys())
            pending.extend(item.values())
        elif type(item) is list:
            pending.extend(item)
    return False


def _bounded_json_integer(value):
    """Reject oversized JSON numeric literals before bigint construction."""
    digits = value[1:] if value.startswith("-") else value
    if len(digits) > MAX_JSON_INTEGER_DIGITS:
        raise ValueError("JSON integer over reviewed digit bound")
    return int(value)


def _finite_json_float(value):
    """Bound floating-point token text and reject decoded infinity."""
    if len(value) > MAX_JSON_FLOAT_LITERAL_CHARS:
        raise ValueError("unreviewed JSON float token length")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite JSON number")
    return number


def _json_lexical_array_budgets(text):
    """Check array sizes before JSON decoding, skipping quoted content."""
    stack = []
    in_string = False
    escaped = False
    total = 0
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            if stack and stack[-1][0] == "[":
                stack[-1][2] = True
            in_string = True
        elif char in "[{":
            if stack and stack[-1][0] == "[":
                stack[-1][2] = True
            stack.append([char, 0, False])
        elif char == ",":
            if stack and stack[-1][0] == "[":
                stack[-1][1] += 1
                if stack[-1][1] >= MAX_JSON_ARRAY_ITEMS:
                    return False
        elif char in "]}":
            if not stack or (stack[-1][0] == "[") != (char == "]"):
                return False
            opening, commas, has_content = stack.pop()
            if opening == "[":
                members = commas + (1 if has_content else 0)
                total += members
                if (members > MAX_JSON_ARRAY_ITEMS or
                        total > MAX_JSON_TOTAL_ARRAY_ITEMS):
                    return False
        elif not char.isspace():
            if stack and stack[-1][0] == "[" and char != ":":
                stack[-1][2] = True
    return not stack


def _json_lexical_object_budgets(text):
    """Reject too many object members before JSON decoder allocation."""
    stack = []
    in_string = False
    escaped = False
    total = 0
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            if stack and stack[-1][0] == "{":
                stack[-1][2] = True
            in_string = True
        elif char in "[{":
            stack.append([char, 0, False])
        elif char == ",":
            if stack and stack[-1][0] == "{":
                stack[-1][1] += 1
                if stack[-1][1] >= MAX_JSON_OBJECT_MEMBERS:
                    return False
        elif char in "]}":
            if not stack or (stack[-1][0] == "{") != (char == "}"):
                return False
            opening, commas, has_content = stack.pop()
            if opening == "{":
                count = commas + (1 if has_content else 0)
                total += count
                if (count > MAX_JSON_OBJECT_MEMBERS or
                        total > MAX_JSON_TOTAL_OBJECT_MEMBERS):
                    return False
    return not stack


def _within_json_array_budgets(root):
    """Inspect built-in parsed JSON containers without recursion."""
    total_items = 0
    stack = [root]
    while stack:
        item = stack.pop()
        if type(item) is list:
            n = len(item)
            total_items += n
            if (n > MAX_JSON_ARRAY_ITEMS or
                    total_items > MAX_JSON_TOTAL_ARRAY_ITEMS):
                return False
            stack.extend(item)
        elif type(item) is dict:
            stack.extend(item.values())
    return True


def review_bundle_json_text(text):
    """No external I/O: caller provides raw UTF-8-decoded JSON text."""
    if type(text) is not str or len(text) > MAX_TEXT_CHARS:
        return fail_closed("BUNDLE_JSON_TEXT_UNREVIEWED")
    try:
        if len(text.encode("utf-8")) > MAX_TEXT_UTF8_BYTES:
            return fail_closed("BUNDLE_JSON_TEXT_UNREVIEWED")
    except UnicodeError:
        return fail_closed("BUNDLE_JSON_UNICODE_UNREVIEWED")
    if (not _json_nesting_within_limit(text) or
            not _json_lexical_array_budgets(text) or
            not _json_lexical_object_budgets(text)):
        return fail_closed("BUNDLE_JSON_GRAMMAR_UNREVIEWED")
    try:
        doc = json.loads(text, object_pairs_hook=_bounded_json_pairs_hook(),
                         parse_constant=_no_nonfinite,
                         parse_int=_bounded_json_integer,
                         parse_float=_finite_json_float)
    except (ValueError, TypeError, UnicodeError, RecursionError,
            OverflowError):
        return fail_closed("BUNDLE_JSON_GRAMMAR_UNREVIEWED")
    if not _within_json_array_budgets(doc):
        return fail_closed("BUNDLE_JSON_GRAMMAR_UNREVIEWED")
    if _has_unpaired_json_surrogate(doc):
        return fail_closed("BUNDLE_JSON_UNICODE_UNREVIEWED")
    return review_bundle_envelope(doc)


class PortableSourceBundleNeverGrantsAnnualRunAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        composite.CombinedSourceChecksRemainNonAuthorizing.setUpClass()

    def setUp(self):
        fixture = composite.CombinedSourceChecksRemainNonAuthorizing(
            "test_consistent_synthetic_bundle_passes_only_source_consistency")
        fixture.setUp()
        self.envelope = {
            "schema": ENVELOPE_SCHEMA,
            "pr": fixture.pr,
            "runs": fixture.runs,
            "jobs_by_run": {str(k): v for k, v in fixture.jobs.items()},
            "compare": fixture.compare,
            "commit": fixture.commit,
            "tree": fixture.tree,
            "nodes": fixture.nodes,
            "changed_bytes_b64": {
                k: base64.b64encode(v).decode("ascii")
                for k, v in fixture.changed.items()},
            "ci_workflow_bytes_b64": {
                k: base64.b64encode(v).decode("ascii")
                for k, v in fixture.ci_bytes.items()},
            "full_tree_snapshots": fixture.full_trees,
            "merge_checkout_snapshot": fixture.merge_checkout,
            "checkout_by_run": {str(k): v for k, v in fixture.runner_checks.items()},
            "phase3_evidence_snapshot": fixture.phase3_evidence,
            "raw_ci_runner_logs": {
                str(k): v for k, v in fixture.raw_ci_runner_logs.items()},
            "raw_ci_log_receipts": {
                str(k): v for k, v in fixture.raw_log_receipts.items()},
        }

    def verdict(self):
        return review_bundle_envelope(self.envelope)

    def assert_fails(self, code=None):
        result = self.verdict()
        self.assertFalse(result["source_consistency"])
        self.assertTrue(result["diagnostics"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])
        if code:
            self.assertIn(code, result["diagnostics"])

    def test_valid_portable_synthetic_bundle_returns_consistency_only(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_valid_json_roundtrip_returns_consistency_only(self):
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_missing_required_category_fails(self):
        self.envelope.pop("ci_workflow_bytes_b64")
        self.assert_fails("BUNDLE_KEY_INVENTORY_UNREVIEWED")

    def test_extra_unreviewed_category_fails(self):
        self.envelope["approval"] = True
        self.assert_fails("BUNDLE_KEY_INVENTORY_UNREVIEWED")

    def test_unreviewed_schema_version_fails(self):
        self.envelope["schema"] = "unknown"
        self.assert_fails("BUNDLE_SCHEMA_UNREVIEWED")

    def test_wrong_top_level_category_type_fails(self):
        self.envelope["runs"] = {}
        self.assert_fails("BUNDLE_CATEGORY_TYPE_UNREVIEWED")

    def test_invalid_run_key_leading_zero_fails(self):
        value = self.envelope["jobs_by_run"].pop("8000")
        self.envelope["jobs_by_run"]["08000"] = value
        self.assert_fails("BUNDLE_RUN_KEY_UNREVIEWED")

    def test_zero_run_key_fails(self):
        self.envelope["checkout_by_run"]["0"] = {}
        self.assert_fails("BUNDLE_RUN_KEY_UNREVIEWED")

    def test_run_id_not_matching_original_ci_log_fails(self):
        self.envelope["raw_ci_runner_logs"]["1234"] = (
            self.envelope["raw_ci_runner_logs"].pop("8000"))
        self.assert_fails()

    def test_invalid_base64_source_fails(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = "%%%"
        self.assert_fails("BUNDLE_SOURCE_B64_UNREVIEWED")

    def test_base64_with_whitespace_fails(self):
        value = self.envelope["changed_bytes_b64"]["tests/sample.py"]
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = value + "\n"
        self.assert_fails("BUNDLE_SOURCE_B64_UNREVIEWED")

    def test_b64_payload_replaced_with_different_valid_bytes_fails(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = (
            base64.b64encode(b"tamper\n").decode("ascii"))
        self.assert_fails()

    def test_modified_reviewed_ci_workflow_source_bytes_fail(self):
        key = ".github/workflows/tests.yml"
        self.envelope["ci_workflow_bytes_b64"][key] = (
            base64.b64encode(b"unreviewed").decode("ascii"))
        self.assert_fails()

    def test_wrong_raw_runner_log_text_fails(self):
        self.envelope["raw_ci_runner_logs"]["8000"] += "\nnew"
        self.assert_fails()

    def test_unhashable_nested_run_id_fails_closed(self):
        self.envelope["runs"][0]["id"] = [8000]
        self.assert_fails()

    def test_boolean_nested_run_id_fails_closed(self):
        self.envelope["runs"][0]["id"] = True
        self.assert_fails()

    def test_invalid_json_document_fails_closed(self):
        result = review_bundle_json_text('{"schema":')
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                      result["diagnostics"])

    def test_duplicate_json_key_fails_closed(self):
        result = review_bundle_json_text('{"schema":1,"schema":2}')
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                      result["diagnostics"])

    def test_json_nan_constant_fails_closed(self):
        result = review_bundle_json_text('{"schema":NaN}')
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                      result["diagnostics"])

    def test_oversized_json_text_fails_before_parser(self):
        result = review_bundle_json_text(" " * (MAX_TEXT_CHARS + 1))
        self.assertIn("BUNDLE_JSON_TEXT_UNREVIEWED",
                      result["diagnostics"])

    def test_oversized_single_source_blob_fails(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = (
            base64.b64encode(b"x"*(MAX_BLOB_BYTES+1)).decode("ascii"))
        self.assert_fails("BUNDLE_SOURCE_BLOB_OVERSIZE")

    def test_null_json_envelope_fails_closed(self):
        result = review_bundle_json_text("null")
        self.assertIn("BUNDLE_SHAPE_UNREVIEWED", result["diagnostics"])

    def test_no_bundle_can_supply_authorization_flags(self):
        self.envelope["can_authorize_annual_run"] = True
        self.assert_fails("BUNDLE_KEY_INVENTORY_UNREVIEWED")

    def test_long_decimal_run_key_rejected_before_int_conversion(self):
        k = self.envelope["jobs_by_run"].pop("8000")
        self.envelope["jobs_by_run"]["8"*6000] = k
        self.assert_fails("BUNDLE_RUN_KEY_UNREVIEWED")

    def test_overflow_signed_64_bit_run_key_is_rejected(self):
        k = self.envelope["jobs_by_run"].pop("8000")
        self.envelope["jobs_by_run"]["9223372036854775808"] = k
        self.assert_fails("BUNDLE_RUN_KEY_UNREVIEWED")

    def test_signed_64_bit_max_run_key_is_structurally_decodable(self):
        value = self.envelope["jobs_by_run"].pop("8000")
        self.envelope["jobs_by_run"]["9223372036854775807"] = value
        result = self.verdict()
        self.assertFalse(result["source_consistency"])
        self.assertNotIn("BUNDLE_RUN_KEY_UNREVIEWED", result["diagnostics"])

    def test_excessive_base64_text_rejected_before_decode(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = (
            "A" * (4*((MAX_BLOB_BYTES+2)//3)+4))
        self.assert_fails("BUNDLE_SOURCE_BLOB_OVERSIZE")

    def test_corrupted_base64_near_limit_does_not_pass(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = (
            "A" * (4*((MAX_BLOB_BYTES+2)//3)-1) + "%")
        self.assert_fails("BUNDLE_SOURCE_B64_UNREVIEWED")

    def test_resource_limits_never_imply_annual_permission(self):
        k = self.envelope["checkout_by_run"].pop("8000")
        self.envelope["checkout_by_run"]["9"*6000] = k
        result = self.verdict()
        self.assertFalse(result["can_authorize_annual_run"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertIn("BUNDLE_RUN_KEY_UNREVIEWED", result["diagnostics"])

    def test_excessively_nested_json_is_diagnostic_not_recursionerror(self):
        raw = "["*1600 + "null" + "]"*1600
        result = review_bundle_json_text(raw)
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                      result["diagnostics"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_malformed_composite_diagnostic_cannot_echo_input(self):
        from unittest.mock import patch
        untrusted = {"source_consistency": False,
                     "diagnostics": ("secret\nprotected-material",),
                     "independent_original_os_proof": False,
                     "exclusive_server_dispatch_gate_proven": False,
                     "can_authorize_annual_run": False}
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=untrusted):
            result = self.verdict()
        self.assertIn("BUNDLE_RESULT_SHAPE_UNREVIEWED",
                      result["diagnostics"])
        self.assertNotIn("secret", repr(result))

    def test_excessively_long_diagnostic_replaced_by_safe_error(self):
        from unittest.mock import patch
        bad = {"source_consistency": False, "diagnostics": ("A"*200,),
               "independent_original_os_proof": False,
               "exclusive_server_dispatch_gate_proven": False,
               "can_authorize_annual_run": False}
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RESULT_SHAPE_UNREVIEWED",))

    def test_excessive_diagnostic_count_rejected(self):
        from unittest.mock import patch
        bad = {"source_consistency": False,
               "diagnostics": tuple("E"+str(i) for i in range(300)),
               "independent_original_os_proof": False,
               "exclusive_server_dispatch_gate_proven": False,
               "can_authorize_annual_run": False}
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertIn("BUNDLE_RESULT_SHAPE_UNREVIEWED",
                      result["diagnostics"])

    def test_bogus_positive_annual_authorization_result_is_rejected(self):
        from unittest.mock import patch
        bad = {"source_consistency": True, "diagnostics": (),
               "independent_original_os_proof": False,
               "exclusive_server_dispatch_gate_proven": False,
               "can_authorize_annual_run": True}
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertFalse(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])
        self.assertIn("BUNDLE_RESULT_SHAPE_UNREVIEWED",
                      result["diagnostics"])

    def test_valid_reordered_bundle_categories_has_same_clean_verdict(self):
        original = self.verdict()
        self.envelope = dict(reversed(list(self.envelope.items())))
        self.assertEqual(self.verdict(), original)

    def test_two_faults_have_identical_result_after_category_reorder(self):
        self.envelope["changed_bytes_b64"]["docs/sample.md"] = "bad%"
        self.envelope["jobs_by_run"]["0"] = {}
        original = self.verdict()
        self.envelope = dict(reversed(list(self.envelope.items())))
        self.assertEqual(self.verdict(), original)
        self.assertFalse(original["source_consistency"])

    def test_invalid_run_keys_report_same_error_after_map_reorder(self):
        self.envelope["jobs_by_run"]["0"] = {}
        self.envelope["jobs_by_run"]["08000"] = {}
        original = self.verdict()
        self.envelope["jobs_by_run"] = dict(
            reversed(list(self.envelope["jobs_by_run"].items())))
        self.assertEqual(self.verdict(), original)
        self.assertIn("BUNDLE_RUN_KEY_UNREVIEWED",
                      original["diagnostics"])

    def test_invalid_source_paths_do_not_trigger_mixed_type_sort_exception(self):
        self.envelope["changed_bytes_b64"][4] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_invalid_run_key_types_do_not_trigger_sort_exception(self):
        self.envelope["raw_ci_log_receipts"][4] = {}
        self.assert_fails("BUNDLE_RUN_KEY_UNREVIEWED")

    def test_sorted_validation_does_not_make_annual_gate_true(self):
        self.envelope = dict(reversed(list(self.envelope.items())))
        self.envelope["ci_workflow_bytes_b64"]["invalid"] = "%%%!"
        result = self.verdict()
        self.assertFalse(result["can_authorize_annual_run"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertTrue(result["diagnostics"])

    def test_depth_limit_rejects_one_too_many_array_levels(self):
        raw = "[" * (MAX_JSON_NESTING + 1) + "null" + "]" * (MAX_JSON_NESTING + 1)
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"], ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_depth_limit_rejects_one_too_many_object_levels(self):
        raw = '{"a":' * (MAX_JSON_NESTING + 1) + "null" + "}" * (MAX_JSON_NESTING + 1)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_depth_limit_counts_mixed_array_and_object_levels(self):
        raw = ('[{"a":' * (MAX_JSON_NESTING // 2 + 1) + 'null' +
               '}]' * (MAX_JSON_NESTING // 2 + 1))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_boundary_array_depth_reaches_shape_check(self):
        raw = "[" * MAX_JSON_NESTING + "null" + "]" * MAX_JSON_NESTING
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_boundary_object_depth_reaches_inventory_check(self):
        raw = '{"a":' * MAX_JSON_NESTING + 'null' + "}" * MAX_JSON_NESTING
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_brackets_inside_string_do_not_count_as_container_depth(self):
        raw = json.dumps("[" * 800 + "]" * 800 + "{" * 800 + "}" * 800)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_escaped_quotes_do_not_release_string_brackets(self):
        raw = json.dumps('quoted "[' * 600 + ']" tail')
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_escaped_backslashes_do_not_change_bracket_depth(self):
        raw = json.dumps(("\\\\[" * 600) + ("]\\\\" * 600))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_stray_closing_container_remains_grammar_error(self):
        self.assertEqual(review_bundle_json_text("]")["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_nesting_guard_keeps_clean_envelope_non_authorizing(self):
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_success_with_nonempty_diagnostics_is_invalid(self):
        from unittest.mock import patch
        bad = {"source_consistency": True, "diagnostics": ("ISSUE",),
               "independent_original_os_proof": False,
               "exclusive_server_dispatch_gate_proven": False,
               "can_authorize_annual_run": False}
        with patch.object(composite, "review_stacked_draft_evidence", return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_failure_with_empty_diagnostics_is_invalid(self):
        from unittest.mock import patch
        bad = {"source_consistency": False, "diagnostics": (),
               "independent_original_os_proof": False,
               "exclusive_server_dispatch_gate_proven": False,
               "can_authorize_annual_run": False}
        with patch.object(composite, "review_stacked_draft_evidence", return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_unsorted_diagnostics_are_invalid(self):
        from unittest.mock import patch
        bad = {"source_consistency": False, "diagnostics": ("Z_ERROR", "A_ERROR"),
               "independent_original_os_proof": False,
               "exclusive_server_dispatch_gate_proven": False,
               "can_authorize_annual_run": False}
        with patch.object(composite, "review_stacked_draft_evidence", return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_duplicate_diagnostics_are_invalid(self):
        from unittest.mock import patch
        bad = {"source_consistency": False, "diagnostics": ("ISSUE", "ISSUE"),
               "independent_original_os_proof": False,
               "exclusive_server_dispatch_gate_proven": False,
               "can_authorize_annual_run": False}
        with patch.object(composite, "review_stacked_draft_evidence", return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_sorted_unique_negative_diagnostics_are_retained(self):
        from unittest.mock import patch
        expected = ("MERGE_HISTORICAL_RUN_UNREVIEWED",
                    "TREE_CHAIN_ROOT_SHA_UNREVIEWED")
        bad = {"source_consistency": False, "diagnostics": expected,
               "independent_original_os_proof": False,
               "exclusive_server_dispatch_gate_proven": False,
               "can_authorize_annual_run": False}
        with patch.object(composite, "review_stacked_draft_evidence", return_value=bad):
            result = self.verdict()
        self.assertFalse(result["source_consistency"])
        self.assertEqual(result["diagnostics"], expected)
        self.assertFalse(result["can_authorize_annual_run"])

    def test_clean_positive_diagnostics_still_empty(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_composite_recursion_error_fails_closed_in_memory(self):
        from unittest.mock import patch
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=RecursionError("synthetic")):
            self.assert_fails("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")

    def test_composite_recursion_error_fails_closed_from_json(self):
        from unittest.mock import patch
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=RecursionError("synthetic")):
            result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(result["diagnostics"], ("BUNDLE_NESTED_EVIDENCE_UNREVIEWED",))
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_object_one_below_depth_limit_is_valid_json_but_wrong_inventory(self):
        depth = MAX_JSON_NESTING - 1
        raw = '{"nested":' * depth + "null" + "}" * depth
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_object_one_above_depth_limit_is_grammar_rejection(self):
        depth = MAX_JSON_NESTING + 1
        raw = '{"nested":' * depth + "null" + "}" * depth
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_empty_object_is_inventory_failure_not_shape_failure(self):
        self.assertEqual(review_bundle_json_text("{}")["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_scalar_json_is_shape_failure_not_inventory_failure(self):
        for raw in ("42", '""', "true", "null"):
            with self.subTest(raw=raw):
                self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                                 ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_exact_mixed_boundary_top_level_object_is_inventory_failure(self):
        raw = '{"nested":' + "[" * (MAX_JSON_NESTING-1) + "null" + "]" * (MAX_JSON_NESTING-1) + "}"
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_one_above_mixed_boundary_is_grammar_failure(self):
        raw = '{"nested":' + "[" * MAX_JSON_NESTING + "null" + "]" * MAX_JSON_NESTING + "}"
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_mismatched_nested_delimiters_still_fail_grammar(self):
        self.assertEqual(review_bundle_json_text('{"a":[1}}')["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_duplicate_nested_object_keys_still_fail_grammar(self):
        self.assertEqual(review_bundle_json_text('{"a":{"b":1,"b":2}}')["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_utf8_escaped_nested_key_brackets_are_not_containers(self):
        raw = json.dumps({"[[]" * 100: None})
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_boundary_inventory_diagnostic_cannot_grant_annual_permission(self):
        raw = '{"a":' * MAX_JSON_NESTING + 'null' + "}" * MAX_JSON_NESTING
        result = review_bundle_json_text(raw)
        self.assertFalse(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_valid_result_inventory_matches_canonical_fail_closed_shape(self):
        self.assertEqual(set(fail_closed("SYNTHETIC")), VERDICT_FIELDS)
        result = self.verdict()
        self.assertEqual(set(result), VERDICT_FIELDS)
        self.assertFalse(result["can_authorize_annual_run"])

    def test_extra_secret_result_key_rejected_without_echo(self):
        from unittest.mock import patch
        valid = self.verdict()
        bad = dict(valid, leaked_source_text="protected-source-sentinel")
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RESULT_SHAPE_UNREVIEWED",))
        self.assertNotIn("protected-source-sentinel", repr(result))

    def test_extra_nested_raw_log_payload_rejected(self):
        from unittest.mock import patch
        bad = dict(self.verdict(), raw_runner_logs={"secret": "material"})
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_extra_false_authority_like_field_still_rejected(self):
        from unittest.mock import patch
        bad = dict(self.verdict(), protected_execution_ready=False)
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_missing_each_required_result_field_rejected(self):
        from unittest.mock import patch
        valid = self.verdict()
        for missing in sorted(VERDICT_FIELDS):
            with self.subTest(missing=missing):
                bad = {k: v for k, v in valid.items() if k != missing}
                with patch.object(composite, "review_stacked_draft_evidence",
                                  return_value=bad):
                    self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_unrecognized_nonstring_result_key_fails_closed(self):
        from unittest.mock import patch
        bad = dict(self.verdict())
        bad[3] = "secret-result"
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_result_dict_subclass_is_not_accepted(self):
        from unittest.mock import patch
        class DictSubclass(dict):
            pass
        bad = DictSubclass(self.verdict())
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_exact_valid_negative_verdict_preserves_codes(self):
        from unittest.mock import patch
        valid = dict(self.verdict())
        valid["source_consistency"] = False
        valid["diagnostics"] = ("MERGE_HISTORICAL_RUN_UNREVIEWED",)
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=valid):
            result = self.verdict()
        self.assertFalse(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ("MERGE_HISTORICAL_RUN_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_stdin_json_verdict_never_serializes_extra_source_field(self):
        from unittest.mock import patch
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as stdin_review
        valid = dict(self.verdict())
        valid["provider_secret"] = "untrusted-protected-evidence"
        output = io.StringIO()
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=valid):
            code = stdin_review.run_stdin_review(
                io.StringIO(json.dumps(self.envelope)), output)
        verdict = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(len(verdict), 5)
        self.assertIn("BUNDLE_RESULT_SHAPE_UNREVIEWED", verdict["diagnostics"])
        self.assertNotIn("untrusted-protected-evidence", output.getvalue())
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_escaped_lone_high_surrogate_value_fails_closed(self):
        raw = '{"key":"\\ud800"}'
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_UNICODE_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_escaped_lone_low_surrogate_value_fails_closed(self):
        raw = '{"key":"\\udfff"}'
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_UNICODE_UNREVIEWED",))

    def test_escaped_lone_surrogate_object_key_fails_closed(self):
        raw = '{"\\ud800": "anything"}'
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_UNICODE_UNREVIEWED",))

    def test_nested_unpaired_surrogate_fails_before_evidence_review(self):
        nested = dict(self.envelope)
        nested["pr"] = dict(nested["pr"])
        nested["pr"]["synthetic_bad"] = "\ud800"
        result = review_bundle_json_text(json.dumps(nested))
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_UNICODE_UNREVIEWED",))
        self.assertFalse(result["source_consistency"])

    def test_valid_escaped_surrogate_pair_is_not_unpaired(self):
        result = review_bundle_json_text('"\\ud83d\\ude00"')
        self.assertEqual(result["diagnostics"], ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_valid_emoji_scalar_is_not_unpaired(self):
        result = review_bundle_json_text(json.dumps("🚀"))
        self.assertEqual(result["diagnostics"], ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_valid_multilingual_scalar_is_not_unpaired(self):
        result = review_bundle_json_text(json.dumps("日本語 العربية"))
        self.assertEqual(result["diagnostics"], ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_valid_escaped_bmp_character_is_not_unpaired(self):
        result = review_bundle_json_text('"\\u20ac"')
        self.assertEqual(result["diagnostics"], ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_stdin_unpaired_surrogate_diagnostic_does_not_echo_source(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as stdin_review
        raw = '{"private":"\\ud800","marker":"protected-log"}'
        out = io.StringIO()
        rc = stdin_review.run_stdin_review(io.StringIO(raw), out)
        self.assertEqual(rc, 2)
        self.assertEqual(json.loads(out.getvalue())["diagnostics"],
                         ["BUNDLE_JSON_UNICODE_UNREVIEWED"])
        self.assertNotIn("protected-log", out.getvalue())

    def test_json_surrogate_guard_preserves_valid_offline_consistency_only(self):
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_overflow_positive_json_exponent_is_grammar_failure(self):
        result = review_bundle_json_text("1e400")
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_overflow_negative_json_exponent_is_grammar_failure(self):
        result = review_bundle_json_text("-1e400")
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_nested_overflow_exponent_is_grammar_failure(self):
        result = review_bundle_json_text('{"pr":{"size":1e999999}}')
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_overflow_large_decimal_mantissa_rejected(self):
        result = review_bundle_json_text("1.0e+9999")
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_underflow_exponent_is_finite_but_invalid_envelope_shape(self):
        result = review_bundle_json_text("1e-9999")
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_ordinary_finite_json_decimal_is_shape_not_grammar_failure(self):
        result = review_bundle_json_text("1.25e+2")
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_exact_integer_digit_limit_is_decodable(self):
        result = review_bundle_json_text("9" * MAX_JSON_INTEGER_DIGITS)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_one_above_integer_digit_limit_fails_before_int(self):
        result = review_bundle_json_text("9" * (MAX_JSON_INTEGER_DIGITS + 1))
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_negative_integer_over_digit_limit_is_rejected(self):
        result = review_bundle_json_text("-" + "9" * (MAX_JSON_INTEGER_DIGITS + 1))
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_nested_unbounded_integer_rejected(self):
        raw = '{"unused":' + "9" * 6000 + "}"
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_stdin_nonfinite_exponent_cannot_echo_evidence(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as stdin_review
        raw = '{"synthetic_secret":"canary-not-for-output","x":1e500}'
        out = io.StringIO()
        rc = stdin_review.run_stdin_review(io.StringIO(raw), out)
        self.assertEqual(rc, 2)
        verdict = json.loads(out.getvalue())
        self.assertEqual(verdict["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("canary-not-for-output", out.getvalue())
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_bounded_number_parser_preserves_clean_synthetic_bundle(self):
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_source_absolute_unix_path_rejected(self):
        self.envelope["changed_bytes_b64"]["/tests/synthetic.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_source_parent_segment_rejected(self):
        self.envelope["changed_bytes_b64"]["tests/../synthetic.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_source_dot_segment_rejected(self):
        self.envelope["changed_bytes_b64"]["./tests/synthetic.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_source_duplicate_separator_rejected(self):
        self.envelope["changed_bytes_b64"]["tests//synthetic.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_source_backslash_separator_rejected(self):
        self.envelope["changed_bytes_b64"]["tests\\synthetic.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_source_embedded_null_rejected(self):
        self.envelope["changed_bytes_b64"]["tests/\x00synthetic.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_source_newline_label_rejected(self):
        self.envelope["changed_bytes_b64"]["tests/\nsynthetic.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_source_windows_drive_absolute_label_rejected(self):
        self.envelope["changed_bytes_b64"]["C:/tests/synthetic.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_source_trailing_separator_rejected(self):
        self.envelope["changed_bytes_b64"]["tests/synthetic.py/"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_valid_hidden_workflow_and_dotfiles_not_rejected(self):
        self.assertTrue(_reviewed_source_path(".github/workflows/tests.yml"))
        self.assertTrue(_reviewed_source_path("docs/.keep"))
        self.assertTrue(_reviewed_source_path("tests/synthetic.py"))

    def test_stdin_unsafe_source_label_is_not_echoed(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as stdin_review
        self.envelope["changed_bytes_b64"]["../protected-evidence-canary"] = "YQ=="
        output = io.StringIO()
        code = stdin_review.run_stdin_review(
            io.StringIO(json.dumps(self.envelope)), output)
        result = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", result["diagnostics"])
        self.assertNotIn("protected-evidence-canary", output.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_safe_source_labels_preserve_consistency_only(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_non_nfc_combining_unicode_path_is_rejected(self):
        path = "tests/cafe\u0301.py"
        self.assertFalse(_reviewed_source_path(path))
        self.envelope["changed_bytes_b64"][path] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_nfc_unicode_path_is_valid_portable_label(self):
        self.assertTrue(_reviewed_source_path("tests/café.py"))
        self.assertTrue(_reviewed_source_path("tests/日本語.py"))

    def test_embedded_drive_colon_path_is_rejected(self):
        for path in ("tests/C:temp.py", "C:relative.txt", "x/y:z.md"):
            with self.subTest(path=path):
                self.assertFalse(_reviewed_source_path(path))

    def test_windows_device_name_is_rejected(self):
        for path in ("CON", "tests/con.txt", "src/NUL", "COM1.py", "aux.md"):
            with self.subTest(path=path):
                self.assertFalse(_reviewed_source_path(path))

    def test_windows_device_name_embedded_normal_word_allowed(self):
        for path in ("tests/console.py", "tests/auxiliary.md", "src/com10.py"):
            with self.subTest(path=path):
                self.assertTrue(_reviewed_source_path(path))

    def test_windows_reserved_extension_path_rejected_before_base64(self):
        self.envelope["ci_workflow_bytes_b64"]["docs/PRN.md"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_trailing_space_in_segment_is_rejected(self):
        for path in ("tests /module.py", "tests/readme ", "docs/folder /readme.md"):
            with self.subTest(path=path):
                self.assertFalse(_reviewed_source_path(path))

    def test_trailing_dot_in_segment_is_rejected(self):
        for path in ("tests./file.py", "docs/README.", "src/a./module.py"):
            with self.subTest(path=path):
                self.assertFalse(_reviewed_source_path(path))

    def test_bidi_override_source_label_is_rejected(self):
        self.envelope["changed_bytes_b64"]["tests/\u202efile.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_bidi_isolate_source_label_is_rejected(self):
        self.envelope["changed_bytes_b64"]["src/\u2066trick.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_stdin_rejected_path_does_not_echo_untrusted_label(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as stdin_review
        self.envelope["changed_bytes_b64"]["src/CON.private-sentinel"] = "YQ=="
        output = io.StringIO()
        code = stdin_review.run_stdin_review(
            io.StringIO(json.dumps(self.envelope)), output)
        result = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", result["diagnostics"])
        self.assertNotIn("private-sentinel", output.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_previous_valid_source_paths_remain_reviewable(self):
        self.assertTrue(_reviewed_source_path(".github/workflows/tests.yml"))
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_exact_source_path_limit_is_lexically_permitted(self):
        # 17 components of 240 bytes + 16 separators = 4096 bytes.
        path = "/".join(["a" * 240] * 17)
        self.assertEqual(len(path), MAX_SOURCE_PATH_CHARS)
        self.assertEqual(len(path.encode("utf-8")), MAX_SOURCE_PATH_UTF8_BYTES)
        self.assertTrue(_reviewed_source_path(path))

    def test_one_above_source_path_limit_is_lexically_rejected(self):
        path = "/".join(["a" * 240] * 16 + ["a" * 241])
        self.assertEqual(len(path), MAX_SOURCE_PATH_CHARS+1)
        self.assertTrue(all(len(p.encode("utf-8")) <=
                            MAX_SOURCE_SEGMENT_UTF8_BYTES
                            for p in path.split("/")))
        self.assertFalse(_reviewed_source_path(path))

    def test_overlong_changed_source_path_fails_without_decoding(self):
        path = "src/" + "x" * (MAX_SOURCE_PATH_CHARS+1)
        self.envelope["changed_bytes_b64"][path] = "!"
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_overlong_ci_workflow_source_path_fails(self):
        path = ".github/workflows/" + "y" * MAX_SOURCE_PATH_CHARS
        self.envelope["ci_workflow_bytes_b64"][path] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_source_map_over_entry_count_fails_closed(self):
        self.envelope["changed_bytes_b64"] = {
            "tests/synthetic_%05d.py" % n: "YQ=="
            for n in range(MAX_SOURCE_ENTRIES_PER_MAP+1)}
        self.assert_fails("BUNDLE_SOURCE_MAP_OVERSIZE")

    def test_ci_workflow_map_over_entry_count_fails_closed(self):
        self.envelope["ci_workflow_bytes_b64"] = {
            "workflows/synthetic_%05d.yml" % n: "YQ=="
            for n in range(MAX_SOURCE_ENTRIES_PER_MAP+1)}
        self.assert_fails("BUNDLE_SOURCE_MAP_OVERSIZE")

    def test_exact_source_map_entry_count_not_rejected_by_count_guard(self):
        self.envelope["changed_bytes_b64"] = {
            "tests/synthetic_%05d.py" % n: "YQ=="
            for n in range(MAX_SOURCE_ENTRIES_PER_MAP)}
        result = self.verdict()
        self.assertNotIn("BUNDLE_SOURCE_MAP_OVERSIZE", result["diagnostics"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_map_entry_cap_precedes_binary_decoding(self):
        self.envelope["changed_bytes_b64"] = {
            "tests/synthetic_%05d.py" % n: "not base64!"
            for n in range(MAX_SOURCE_ENTRIES_PER_MAP+1)}
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ("BUNDLE_SOURCE_MAP_OVERSIZE",))

    def test_stdin_overlong_source_label_not_echoed(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as stdin_review
        path = "src/" + "private-source-sentinel" + "x" * MAX_SOURCE_PATH_CHARS
        self.envelope["changed_bytes_b64"][path] = "YQ=="
        out = io.StringIO()
        status = stdin_review.run_stdin_review(
            io.StringIO(json.dumps(self.envelope)), out)
        self.assertEqual(status, 2)
        result = json.loads(out.getvalue())
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", result["diagnostics"])
        self.assertNotIn("private-source-sentinel", out.getvalue())

    def test_inmemory_source_map_count_guard_needs_no_json_text(self):
        data = dict(self.envelope)
        data["changed_bytes_b64"] = {"src/a%05d" % i: "" for i in range(MAX_SOURCE_ENTRIES_PER_MAP+1)}
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"], ("BUNDLE_SOURCE_MAP_OVERSIZE",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_source_map_ordinary_fixture_still_consistent_only(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_direct_schema_string_subclass_is_rejected(self):
        class NonPlainSchema(str):
            pass
        self.envelope["schema"] = NonPlainSchema(ENVELOPE_SCHEMA)
        self.assert_fails("BUNDLE_SCHEMA_UNREVIEWED")

    def test_exact_plain_schema_still_passes_source_consistency_only(self):
        self.assertIs(type(self.envelope["schema"]), str)
        self.assertTrue(self.verdict()["source_consistency"])
        self.assertFalse(self.verdict()["can_authorize_annual_run"])

    def test_over_count_top_level_runs_rejected_directly(self):
        self.envelope["runs"] = [{}] * (MAX_RUNS_PER_ENVELOPE+1)
        self.assert_fails("BUNDLE_RUN_COLLECTION_OVERSIZE")

    def test_exact_run_collection_limit_is_not_count_rejection(self):
        self.envelope["runs"] = [{}] * MAX_RUNS_PER_ENVELOPE
        result = self.verdict()
        self.assertNotIn("BUNDLE_RUN_COLLECTION_OVERSIZE", result["diagnostics"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_jobs_run_map_over_count_rejected(self):
        self.envelope["jobs_by_run"] = {
            str(i+1): [] for i in range(MAX_RUN_MAP_ENTRIES+1)}
        self.assert_fails("BUNDLE_RUN_MAP_OVERSIZE")

    def test_checkout_run_map_over_count_rejected(self):
        self.envelope["checkout_by_run"] = {
            str(i+1): {} for i in range(MAX_RUN_MAP_ENTRIES+1)}
        self.assert_fails("BUNDLE_RUN_MAP_OVERSIZE")

    def test_raw_ci_runner_logs_over_count_rejected(self):
        self.envelope["raw_ci_runner_logs"] = {
            str(i+1): "synthetic" for i in range(MAX_RUN_MAP_ENTRIES+1)}
        self.assert_fails("BUNDLE_RUN_MAP_OVERSIZE")

    def test_raw_ci_receipts_over_count_rejected(self):
        self.envelope["raw_ci_log_receipts"] = {
            str(i+1): {} for i in range(MAX_RUN_MAP_ENTRIES+1)}
        self.assert_fails("BUNDLE_RUN_MAP_OVERSIZE")

    def test_map_over_count_precedes_malformed_run_keys(self):
        self.envelope["jobs_by_run"] = {
            "invalid_%05d" % i: [] for i in range(MAX_RUN_MAP_ENTRIES+1)}
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ("BUNDLE_RUN_MAP_OVERSIZE",))

    def test_stdin_oversized_runs_preserves_safe_diagnostics(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as stdin_review
        self.envelope["runs"] = ["synthetic-sentinel"] * (MAX_RUNS_PER_ENVELOPE+1)
        out = io.StringIO()
        status = stdin_review.run_stdin_review(
            io.StringIO(json.dumps(self.envelope)), out)
        result = json.loads(out.getvalue())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_RUN_COLLECTION_OVERSIZE", result["diagnostics"])
        self.assertNotIn("synthetic-sentinel", out.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_overlong_raw_runner_log_is_rejected_in_memory(self):
        self.envelope["raw_ci_runner_logs"]["9001"] = (
            "x" * (MAX_RAW_LOG_CHARS_PER_RUN+1))
        self.assert_fails("BUNDLE_RAW_LOG_TEXT_OVERSIZE")

    def test_raw_runner_logs_over_total_budget_rejected(self):
        self.envelope["raw_ci_runner_logs"] = {
            "8001": "a" * 1_500_000,
            "8002": "b" * 1_500_000,
            "8003": "c" * 1_500_001,
        }
        self.assert_fails("BUNDLE_TOTAL_RAW_LOG_OVERSIZE")

    def test_raw_log_nontext_type_is_rejected(self):
        self.envelope["raw_ci_runner_logs"]["9001"] = b"synthetic-raw-log"
        self.assert_fails("BUNDLE_RAW_LOG_TEXT_UNREVIEWED")

    def test_raw_log_none_value_is_rejected(self):
        self.envelope["raw_ci_runner_logs"]["9001"] = None
        self.assert_fails("BUNDLE_RAW_LOG_TEXT_UNREVIEWED")

    def test_raw_log_string_subclass_is_rejected_by_structure_guard(self):
        class NonPlainLog(str):
            pass
        self.envelope["raw_ci_runner_logs"]["9001"] = NonPlainLog("synthetic")
        self.assert_fails("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED")

    def test_raw_log_limit_precedes_malformed_run_id(self):
        self.envelope["raw_ci_runner_logs"]["not-a-run-id"] = (
            "s" * (MAX_RAW_LOG_CHARS_PER_RUN+1))
        result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RAW_LOG_TEXT_OVERSIZE",))

    def test_overlong_raw_log_diagnostic_does_not_echo_source(self):
        self.envelope["raw_ci_runner_logs"]["9001"] = (
            "sensitive-log-canary" + "x" * MAX_RAW_LOG_CHARS_PER_RUN)
        result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RAW_LOG_TEXT_OVERSIZE",))
        self.assertNotIn("sensitive-log-canary", repr(result))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_valid_synthetic_logs_remain_source_consistency_only(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_nested_runtime_error_is_sanitized(self):
        from unittest.mock import patch
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=RuntimeError("private-runner-log-sentinel")):
            result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_NESTED_EVIDENCE_UNREVIEWED",))
        self.assertNotIn("private-runner-log-sentinel", repr(result))

    def test_nested_assertion_failure_is_sanitized(self):
        from unittest.mock import patch
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=AssertionError("secret-assertion")):
            self.assert_fails("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")

    def test_nested_file_permission_error_is_sanitized(self):
        from unittest.mock import patch
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=PermissionError("never-open-original")):
            result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_NESTED_EVIDENCE_UNREVIEWED",))
        self.assertNotIn("never-open-original", repr(result))

    def test_nested_generic_io_failure_is_sanitized(self):
        from unittest.mock import patch
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=OSError("sensitive-path")):
            self.assert_fails("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")

    def test_nested_lookup_index_error_stays_fail_closed(self):
        from unittest.mock import patch
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=IndexError("untrusted-index")):
            self.assert_fails("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")

    def test_nested_value_error_stays_fail_closed(self):
        from unittest.mock import patch
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=ValueError("untrusted-value")):
            self.assert_fails("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")

    def test_nested_runtime_error_via_stdin_is_one_safe_verdict(self):
        from unittest.mock import patch
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as stdin_review
        output = io.StringIO()
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=RuntimeError("sensitive-log-sentinel")):
            code = stdin_review.run_stdin_review(
                io.StringIO(json.dumps(self.envelope)), output)
        result = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(result["diagnostics"],
                         ["BUNDLE_NESTED_EVIDENCE_UNREVIEWED"])
        self.assertEqual(len(output.getvalue().splitlines()), 1)
        self.assertNotIn("sensitive-log-sentinel", output.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_nested_assertion_failure_via_stdin_is_non_authorizing(self):
        from unittest.mock import patch
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as stdin_review
        output = io.StringIO()
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=AssertionError("hidden-assertion")):
            code = stdin_review.run_stdin_review(
                io.StringIO(json.dumps(self.envelope)), output)
        result = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertNotIn("hidden-assertion", output.getvalue())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_nested_crash_policy_preserves_clean_consistency_only(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_internal_space_before_extension_is_not_trailing(self):
        self.assertTrue(_reviewed_source_path("tests/module .py"))

    def test_multiple_internal_spaces_before_extension_are_allowed(self):
        self.assertTrue(_reviewed_source_path("docs/project  notes.md"))

    def test_plain_internal_spaces_remain_allowed(self):
        self.assertTrue(_reviewed_source_path("docs/meeting notes.txt"))

    def test_component_only_space_is_rejected(self):
        self.assertFalse(_reviewed_source_path("docs/ /notes.txt"))

    def test_multiple_trailing_spaces_in_component_rejected(self):
        self.assertFalse(_reviewed_source_path("docs/draft  /notes.txt"))

    def test_trailing_space_in_final_component_rejected(self):
        self.assertFalse(_reviewed_source_path("docs/report.md "))

    def test_spaces_inside_dotfile_name_still_allowed(self):
        self.assertTrue(_reviewed_source_path("docs/.project notes"))

    def test_trailing_dot_still_rejected_after_boundary_correction(self):
        self.assertFalse(_reviewed_source_path("docs/reports./notes.md"))

    def test_whitespace_boundary_correction_preserves_source_only_verdict(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_changed_source_names_differing_only_by_case_are_rejected(self):
        self.envelope["changed_bytes_b64"].update({
            "tests/CASEFOLD_SYNTHETIC.py": "YQ==",
            "tests/casefold_synthetic.py": "YQ==",
        })
        self.assert_fails("BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED")

    def test_workflow_source_names_differing_only_by_case_are_rejected(self):
        self.envelope["ci_workflow_bytes_b64"].update({
            "ci/Synthetic.yml": "YQ==",
            "ci/synthetic.yml": "YQ==",
        })
        self.assert_fails("BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED")

    def test_unicode_sharp_s_casefold_alias_is_rejected(self):
        self.envelope["changed_bytes_b64"].update({
            "tests/Straße.py": "YQ==",
            "tests/Strasse.py": "YQ==",
        })
        self.assert_fails("BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED")

    def test_unicode_uppercase_accent_casefold_alias_is_rejected(self):
        self.envelope["changed_bytes_b64"].update({
            "tests/Café.py": "YQ==",
            "tests/café.py": "YQ==",
        })
        self.assert_fails("BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED")

    def test_similar_names_with_different_extensions_do_not_collide(self):
        self.assertNotEqual("src/synthetic.py".casefold(),
                            "src/synthetic.pyi".casefold())
        self.assertTrue(_reviewed_source_path("src/synthetic.py"))
        self.assertTrue(_reviewed_source_path("src/synthetic.pyi"))

    def test_filenames_in_distinct_directories_do_not_collide(self):
        a = "docs/report.md"
        b = "tests/report.md"
        self.assertNotEqual(a.casefold(), b.casefold())
        self.assertTrue(_reviewed_source_path(a))
        self.assertTrue(_reviewed_source_path(b))

    def test_casefold_collision_output_does_not_echo_untrusted_path(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as stdin_review
        self.envelope["changed_bytes_b64"].update({
            "src/SECRET-CANARY-A.py": "YQ==",
            "src/secret-canary-a.py": "YQ==",
        })
        out = io.StringIO()
        status = stdin_review.run_stdin_review(
            io.StringIO(json.dumps(self.envelope)), out)
        result = json.loads(out.getvalue())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED",
                      result["diagnostics"])
        self.assertNotIn("SECRET-CANARY-A", out.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_casefold_cannot_mask_absolute_or_parent_path_rejection(self):
        self.envelope["changed_bytes_b64"]["../SYNTHETIC.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_unmodified_synthetic_bundle_stays_source_consistent_only(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_direct_inmemory_self_referential_dict_rejected(self):
        data = dict(self.envelope)
        pr = dict(data["pr"])
        pr["synthetic_cycle"] = pr
        data["pr"] = pr
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_direct_inmemory_self_referential_list_rejected(self):
        data = dict(self.envelope)
        cycle = []
        cycle.append(cycle)
        pr = dict(data["pr"])
        pr["synthetic_cycle"] = cycle
        data["pr"] = pr
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))

    def test_direct_inmemory_tuple_list_cycle_rejected(self):
        cycle = []
        cycle.append((cycle,))
        self.assertFalse(_within_inmemory_structure_budget(cycle))

    def test_direct_inmemory_deep_nested_list_rejected(self):
        nested = []
        for _ in range(MAX_INMEMORY_DEPTH+2):
            nested = [nested]
        data = dict(self.envelope)
        pr = dict(data["pr"])
        pr["synthetic_deep"] = nested
        data["pr"] = pr
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))

    def test_direct_inmemory_overlarge_list_rejected_before_walk(self):
        data = dict(self.envelope)
        pr = dict(data["pr"])
        pr["synthetic_large"] = [None] * (MAX_INMEMORY_NODES+1)
        data["pr"] = pr
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_shared_acyclic_dict_is_not_a_cycle(self):
        shared = {"fixture": "synthetic"}
        self.assertTrue(_within_inmemory_structure_budget(
            {"first": shared, "second": shared}))

    def test_large_scalar_string_is_not_exploded_into_nodes(self):
        self.assertTrue(_within_inmemory_structure_budget(
            {"synthetic": "x" * (MAX_INMEMORY_NODES+1)}))

    def test_structure_budget_allows_moderately_nested_acyclic_lists(self):
        nested = []
        for _ in range(100):
            nested = [nested]
        self.assertTrue(_within_inmemory_structure_budget(nested))

    def test_json_over_depth_still_fails_before_composite_review(self):
        raw = "[" * (MAX_JSON_NESTING+1) + "null" + "]" * (MAX_JSON_NESTING+1)
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_structure_budget_preserves_clean_source_only_fixture(self):
        self.assertTrue(_within_inmemory_structure_budget(self.envelope))
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_inmemory_one_over_scalar_string_length_is_rejected(self):
        self.assertFalse(_within_inmemory_structure_budget(
            "x" * (MAX_INMEMORY_SCALAR_UNITS+1)))

    def test_inmemory_exact_scalar_string_length_is_permitted(self):
        self.assertTrue(_within_inmemory_structure_budget(
            "x" * MAX_INMEMORY_SCALAR_UNITS))

    def test_inmemory_one_over_scalar_bytes_length_is_rejected(self):
        self.assertFalse(_within_inmemory_structure_budget(
            b"x" * (MAX_INMEMORY_SCALAR_UNITS+1)))

    def test_inmemory_exact_scalar_bytes_length_is_permitted(self):
        self.assertTrue(_within_inmemory_structure_budget(
            b"x" * MAX_INMEMORY_SCALAR_UNITS))

    def test_inmemory_scalar_budget_applies_to_dict_keys(self):
        self.assertFalse(_within_inmemory_structure_budget({
            "private" * (MAX_INMEMORY_SCALAR_UNITS//7+1): None}))

    def test_inmemory_scalar_budget_applies_to_nested_tuple_strings(self):
        self.assertFalse(_within_inmemory_structure_budget((
            ["x" * (MAX_INMEMORY_SCALAR_UNITS+1)],)))

    def test_inmemory_total_scalar_budget_applies_to_many_valid_values(self):
        values = ["a" * 3_000_000 for _ in range(6)]
        self.assertFalse(_within_inmemory_structure_budget(values))

    def test_inmemory_total_scalar_exact_boundary_is_permitted(self):
        values = ["a" * 4_000_000 for _ in range(4)]
        self.assertTrue(_within_inmemory_structure_budget(values))

    def test_inmemory_oversized_scalar_in_direct_envelope_fails_closed(self):
        data = dict(self.envelope)
        pr = dict(data["pr"])
        pr["private_synthetic"] = "canary" + "x" * MAX_INMEMORY_SCALAR_UNITS
        data["pr"] = pr
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))
        self.assertNotIn("canary", repr(result))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_inmemory_scalar_budget_preserves_clean_evidence_fixture(self):
        self.assertTrue(_within_inmemory_structure_budget(self.envelope))
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_inmemory_large_positive_integer_fails_before_stringify(self):
        self.assertFalse(_within_inmemory_structure_budget(10**10000))

    def test_inmemory_large_negative_integer_fails(self):
        self.assertFalse(_within_inmemory_structure_budget(-(10**10000)))

    def test_inmemory_exact_max_64_digit_integer_is_permitted(self):
        self.assertTrue(_within_inmemory_structure_budget(10**64-1))

    def test_inmemory_first_65_digit_integer_is_rejected(self):
        self.assertFalse(_within_inmemory_structure_budget(10**64))

    def test_inmemory_nonfinite_positive_float_is_rejected(self):
        self.assertFalse(_within_inmemory_structure_budget(float("inf")))

    def test_inmemory_nonfinite_negative_float_is_rejected(self):
        self.assertFalse(_within_inmemory_structure_budget(float("-inf")))

    def test_inmemory_nonfinite_nan_is_rejected(self):
        self.assertFalse(_within_inmemory_structure_budget(float("nan")))

    def test_inmemory_finite_float_remains_allowed(self):
        self.assertTrue(_within_inmemory_structure_budget(
            {"synthetic_float": 2.5e300}))

    def test_inmemory_overlong_integer_inside_envelope_fails_closed(self):
        data = dict(self.envelope)
        pr = dict(data["pr"])
        pr["synthetic_bigint"] = 10**10000
        data["pr"] = pr
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_inmemory_nan_in_envelope_fails_closed(self):
        data = dict(self.envelope)
        pr = dict(data["pr"])
        pr["synthetic_nan"] = float("nan")
        data["pr"] = pr
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))

    def test_inmemory_numeric_guard_preserves_clean_synthetic_source_only(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_inmemory_custom_object_not_accepted_as_scalar(self):
        class Untrusted:
            pass
        self.assertFalse(_within_inmemory_structure_budget({"x": Untrusted()}))

    def test_inmemory_custom_object_rejected_without_repr(self):
        class Dangerous:
            def __repr__(self):
                raise AssertionError("must not render unknown object")
        self.assertFalse(_within_inmemory_structure_budget({"private": Dangerous()}))

    def test_inmemory_str_subclass_is_rejected(self):
        class UntrustedStr(str):
            pass
        self.assertFalse(_within_inmemory_structure_budget(UntrustedStr("data")))

    def test_inmemory_dict_subclass_is_rejected(self):
        class UntrustedDict(dict):
            pass
        self.assertFalse(_within_inmemory_structure_budget(UntrustedDict()))

    def test_inmemory_list_subclass_is_rejected(self):
        class UntrustedList(list):
            pass
        self.assertFalse(_within_inmemory_structure_budget(UntrustedList()))

    def test_inmemory_bytes_subclass_is_rejected(self):
        class UntrustedBytes(bytes):
            pass
        self.assertFalse(_within_inmemory_structure_budget(UntrustedBytes(b"abc")))

    def test_inmemory_set_and_frozenset_are_not_reviewed(self):
        self.assertFalse(_within_inmemory_structure_budget({"synthetic": set()}))
        self.assertFalse(_within_inmemory_structure_budget({"synthetic": frozenset()}))

    def test_inmemory_decimal_and_complex_numbers_are_not_reviewed(self):
        from decimal import Decimal
        self.assertFalse(_within_inmemory_structure_budget(Decimal("1.25")))
        self.assertFalse(_within_inmemory_structure_budget(2+3j))

    def test_inmemory_plain_supported_scalars_are_accepted(self):
        values = [None, False, True, 42, -42, 1.25, "synthetic", b"bytes"]
        self.assertTrue(_within_inmemory_structure_budget(values))

    def test_inmemory_unknown_object_in_envelope_is_sanitized(self):
        class Untrusted:
            def __repr__(self):
                raise AssertionError("hidden source")
        data = dict(self.envelope)
        pr = dict(data["pr"])
        pr["unknown_synthetic"] = Untrusted()
        data["pr"] = pr
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_inmemory_known_types_preserve_clean_consistency_only(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_direct_unpaired_high_surrogate_string_is_rejected(self):
        self.assertFalse(_within_inmemory_structure_budget("\ud800"))

    def test_direct_unpaired_low_surrogate_string_is_rejected(self):
        self.assertFalse(_within_inmemory_structure_budget("\udfff"))

    def test_direct_unpaired_surrogate_dict_key_is_rejected(self):
        self.assertFalse(_within_inmemory_structure_budget({
            "private_\ud800": "synthetic"}))

    def test_direct_unpaired_surrogate_nested_tuple_is_rejected(self):
        self.assertFalse(_within_inmemory_structure_budget(
            {"pr": (["synthetic", "\udc00"],)}))

    def test_direct_unpaired_surrogate_in_envelope_fails_closed(self):
        data = dict(self.envelope)
        pr = dict(data["pr"])
        pr["private_synthetic"] = "secret-canary-\ud800"
        data["pr"] = pr
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))
        self.assertNotIn("secret-canary", repr(result))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_direct_valid_emoji_and_multilingual_text_are_allowed(self):
        self.assertTrue(_within_inmemory_structure_budget(
            {"unicode": ["🚀", "日本語", "العربية", "café"]}))

    def test_direct_valid_private_use_unicode_is_allowed(self):
        self.assertTrue(_within_inmemory_structure_budget("\ue000"))

    def test_json_surrogate_rejection_retains_safe_specific_code(self):
        raw = '{"synthetic":"\\ud800"}'
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_UNICODE_UNREVIEWED",))

    def test_plain_utf8_synthetic_evidence_still_consistency_only(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_raw_log_plain_bytes_still_reaches_category_type_guard(self):
        self.envelope["raw_ci_runner_logs"]["9001"] = b"synthetic"
        self.assert_fails("BUNDLE_RAW_LOG_TEXT_UNREVIEWED")

    def test_raw_log_plain_none_still_reaches_category_type_guard(self):
        self.envelope["raw_ci_runner_logs"]["9001"] = None
        self.assert_fails("BUNDLE_RAW_LOG_TEXT_UNREVIEWED")

    def test_raw_log_subclass_diagnostic_precedes_category_guard(self):
        class SubclassLog(str):
            pass
        self.envelope["raw_ci_runner_logs"]["9001"] = SubclassLog("private-canary")
        result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))
        self.assertNotIn("private-canary", repr(result))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_custom_payload_inside_job_map_fails_preflight(self):
        class Untrusted:
            pass
        self.envelope["jobs_by_run"]["9001"] = Untrusted()
        self.assert_fails("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED")

    def test_run_id_key_subclass_fails_preflight_before_id_parse(self):
        class IdSubclass(str):
            pass
        self.envelope["checkout_by_run"][IdSubclass("9001")] = {}
        self.assert_fails("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED")

    def test_plain_invalid_run_id_still_reaches_id_guard(self):
        self.envelope["checkout_by_run"]["not-an-id"] = {}
        self.assert_fails("BUNDLE_RUN_KEY_UNREVIEWED")

    def test_direct_subclass_rejection_never_invokes_nested_reviewer(self):
        from unittest.mock import patch
        class SubclassLog(str):
            pass
        self.envelope["raw_ci_runner_logs"]["9001"] = SubclassLog("synthetic")
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=AssertionError("must not run")) as nested:
            result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))
        nested.assert_not_called()

    def test_stdin_only_json_has_plain_strings_not_subclasses(self):
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_valid_source_consistency_retains_all_negative_authority(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_reviewed_nested_diagnostics_set_is_exact_known_literatures(self):
        self.assertIn("MERGE_HISTORICAL_RUN_UNREVIEWED",
                      REVIEWED_NESTED_DIAGNOSTICS)
        self.assertNotIn("SYNTHETIC_REVIEW_WARNING",
                         REVIEWED_NESTED_DIAGNOSTICS)
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED",
                         REVIEWED_NESTED_DIAGNOSTICS)

    def test_unknown_well_formed_nested_diagnostic_rejected(self):
        from unittest.mock import patch
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=("SYNTHETIC_PRIVATE_CANARY",))
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RESULT_SHAPE_UNREVIEWED",))
        self.assertNotIn("SYNTHETIC_PRIVATE_CANARY", repr(result))

    def test_annual_authorization_diagnostic_label_is_rejected(self):
        from unittest.mock import patch
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=("ANNUAL_DISPATCH_AUTHORIZED",))
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_trusted_nested_source_only_failure_code_is_preserved(self):
        from unittest.mock import patch
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=("MERGE_HISTORICAL_RUN_UNREVIEWED",))
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("MERGE_HISTORICAL_RUN_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_reviewer_known_multi_code_sorted_tuple_is_preserved(self):
        from unittest.mock import patch
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=("MERGE_HISTORICAL_RUN_UNREVIEWED",
                                "TREE_CHAIN_ROOT_SHA_UNREVIEWED"))
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertEqual(result["diagnostics"], bad["diagnostics"])

    def test_known_plus_unknown_code_causes_whole_result_refusal(self):
        from unittest.mock import patch
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=("MERGE_HISTORICAL_RUN_UNREVIEWED",
                                "SECRET_CANARY_SOURCE"))
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RESULT_SHAPE_UNREVIEWED",))
        self.assertNotIn("SECRET_CANARY_SOURCE", repr(result))

    def test_stdin_looks_like_diagnostic_secret_cannot_be_echoed(self):
        from unittest.mock import patch
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as stdin_review
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=("PRIVATE_SOURCE_CANARY_2026",))
        output = io.StringIO()
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            rc = stdin_review.run_stdin_review(
                io.StringIO(json.dumps(self.envelope)), output)
        result = json.loads(output.getvalue())
        self.assertEqual(rc, 2)
        self.assertEqual(result["diagnostics"],
                         ["BUNDLE_RESULT_SHAPE_UNREVIEWED"])
        self.assertNotIn("PRIVATE_SOURCE_CANARY_2026", output.getvalue())

    def test_plain_source_bundle_without_diagnostics_stays_consistent(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_zero_width_space_source_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/synthe\u200btic.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_zero_width_joiner_source_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/zero\u200dwidth.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_soft_hyphen_source_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/soft\u00adhyphen.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_bom_source_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/\ufeffmodule.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_c1_control_source_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/control\u0085.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_line_separator_source_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/x\u2028y.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_paragraph_separator_source_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/x\u2029y.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_word_joiner_source_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/a\u2060b.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_private_use_printable_path_allowed_by_character_class(self):
        self.assertTrue(_reviewed_source_path("src/\ue000.py"))

    def test_unicode_canonical_multilingual_source_path_allowed(self):
        for path in ("src/café.py", "src/日本語.py", "src/العربية.py"):
            with self.subTest(path=path):
                self.assertTrue(_reviewed_source_path(path))

    def test_invisible_path_stdin_output_never_echoes_supplied_label(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"]["src/private\u200bcanary.py"] = "YQ=="
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), output)
        self.assertEqual(status, 2)
        record = json.loads(output.getvalue())
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", record["diagnostics"])
        self.assertNotIn("private", output.getvalue())
        self.assertFalse(record["can_authorize_annual_run"])

    def test_canonical_source_fixture_preserves_consistency_only(self):
        verdict = self.verdict()
        self.assertTrue(verdict["source_consistency"])
        self.assertEqual(verdict["diagnostics"], ())
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_crossmap_identical_workflow_source_path_fails_closed(self):
        path = next(iter(self.envelope["ci_workflow_bytes_b64"]))
        self.envelope["changed_bytes_b64"][path] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_CROSSMAP_COLLISION_UNREVIEWED")

    def test_crossmap_ascii_casefold_workflow_path_fails_closed(self):
        path = next(iter(self.envelope["ci_workflow_bytes_b64"]))
        self.envelope["changed_bytes_b64"][path.swapcase()] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_CROSSMAP_COLLISION_UNREVIEWED")

    def test_crossmap_unicode_casefold_sharp_s_fails_closed(self):
        self.envelope["changed_bytes_b64"]["src/Straße.py"] = "YQ=="
        self.envelope["ci_workflow_bytes_b64"]["src/Strasse.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_CROSSMAP_COLLISION_UNREVIEWED")

    def test_crossmap_unicode_accent_casefold_fails_closed(self):
        self.envelope["changed_bytes_b64"]["src/Café.py"] = "YQ=="
        self.envelope["ci_workflow_bytes_b64"]["src/café.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_CROSSMAP_COLLISION_UNREVIEWED")

    def test_crossmap_same_basename_different_directory_not_collision(self):
        first = "docs/synthetic.txt"
        second = "tests/synthetic.txt"
        self.assertNotEqual(first.casefold(), second.casefold())
        self.assertTrue(_reviewed_source_path(first))
        self.assertTrue(_reviewed_source_path(second))

    def test_crossmap_valid_distinct_paths_preserve_source_consistency(self):
        changed = {k.casefold() for k in self.envelope["changed_bytes_b64"]}
        workflows = {k.casefold() for k in self.envelope["ci_workflow_bytes_b64"]}
        self.assertFalse(changed & workflows)
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_crossmap_invalid_base64_is_rejected_before_collision(self):
        path = next(iter(self.envelope["ci_workflow_bytes_b64"]))
        self.envelope["changed_bytes_b64"][path] = "not valid base64!"
        self.assert_fails("BUNDLE_SOURCE_B64_UNREVIEWED")

    def test_crossmap_collision_never_uses_supplied_log_text(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"]["src/PRIVATE-CANARY.py"] = "YQ=="
        self.envelope["ci_workflow_bytes_b64"]["src/private-canary.py"] = "YQ=="
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), output)
        result = json.loads(output.getvalue())
        self.assertEqual(status, 2)
        self.assertEqual(result["diagnostics"],
                         ["BUNDLE_SOURCE_CROSSMAP_COLLISION_UNREVIEWED"])
        self.assertNotIn("PRIVATE-CANARY", output.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_crossmap_collision_cannot_grant_independent_authority(self):
        path = next(iter(self.envelope["ci_workflow_bytes_b64"]))
        self.envelope["changed_bytes_b64"][path] = "YQ=="
        result = self.verdict()
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_combining_grapheme_joiner_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/ab\u034fcd.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_mongolian_free_variation_selector_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/a\u180bb.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_bmp_emoji_variation_selector_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/a\ufe0fb.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_bmp_text_variation_selector_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/a\ufe0eb.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_supplementary_variation_selector_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/a\U000e0100b.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_supplementary_last_variation_selector_path_refused(self):
        self.envelope["changed_bytes_b64"]["src/a\U000e01efb.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_regular_composed_diacritic_remains_valid(self):
        self.assertTrue(_reviewed_source_path("src/café.py"))

    def test_multilingual_unicode_without_selector_remains_valid(self):
        self.assertTrue(_reviewed_source_path("src/日本語.py"))

    def test_stdin_supplementary_selector_is_safe_failure(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"]["src/PRIVATE\U000e0100CANARY.py"] = "YQ=="
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), output)
        record = json.loads(output.getvalue())
        self.assertEqual(status, 2)
        self.assertEqual(record["diagnostics"], ["BUNDLE_SOURCE_PATH_UNREVIEWED"])
        self.assertNotIn("PRIVATE", output.getvalue())
        self.assertFalse(record["can_authorize_annual_run"])

    def test_valid_synthetic_evidence_stays_source_only(self):
        verdict = self.verdict()
        self.assertEqual(verdict["diagnostics"], ())
        self.assertTrue(verdict["source_consistency"])
        self.assertFalse(verdict["independent_original_os_proof"])
        self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_top_level_plain_non_string_key_fails_inventory(self):
        data = dict(self.envelope)
        data[101] = "synthetic"
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_top_level_plain_none_key_fails_inventory(self):
        data = dict(self.envelope)
        data[None] = "synthetic"
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_top_level_string_subclass_key_fails_inventory(self):
        class NonPlainKey(str):
            pass
        data = dict(self.envelope)
        data[NonPlainKey("unrecognized_synthetic")] = "synthetic"
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_top_level_custom_key_is_not_rehashed_by_inventory(self):
        class DangerousKey:
            def __init__(self):
                self.calls = 0
            def __hash__(self):
                self.calls += 1
                return 918237
            def __eq__(self, other):
                raise AssertionError("key equality must not run")
        key = DangerousKey()
        data = dict(self.envelope)
        data[key] = "synthetic"
        key.calls = 0
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))
        self.assertEqual(key.calls, 0)
        self.assertFalse(result["can_authorize_annual_run"])

    def test_top_level_custom_key_diagnostic_never_renders_key(self):
        class SecretKey:
            def __hash__(self):
                return 191827
            def __repr__(self):
                raise AssertionError("sensitive identifier must not print")
        data = dict(self.envelope)
        data[SecretKey()] = "protected-private-canary"
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))
        self.assertNotIn("protected-private-canary", repr(result))

    def test_top_level_missing_string_key_retains_inventory_code(self):
        data = dict(self.envelope)
        del data["schema"]
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_top_level_unknown_plain_string_retains_inventory_code(self):
        data = dict(self.envelope)
        data["not_reviewed"] = None
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_top_level_dict_subclass_still_fails_shape_first(self):
        class UntrustedDict(dict):
            pass
        result = review_bundle_envelope(UntrustedDict(self.envelope))
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_top_level_plain_keys_keep_clean_source_only_verdict(self):
        self.assertTrue(all(type(key) is str for key in self.envelope))
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_sorted_reviewed_diagnostic_names_are_retained(self):
        from unittest.mock import patch
        codes = ("MERGE_HISTORICAL_RUN_UNREVIEWED",
                 "TREE_CHAIN_ROOT_SHA_UNREVIEWED")
        self.assertTrue(all(code in REVIEWED_NESTED_DIAGNOSTICS for code in codes))
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=codes)
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assertEqual(self.verdict()["diagnostics"], codes)

    def test_reverse_order_reviewed_diagnostics_are_rejected(self):
        from unittest.mock import patch
        codes = ("TREE_CHAIN_ROOT_SHA_UNREVIEWED",
                 "MERGE_HISTORICAL_RUN_UNREVIEWED")
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=codes)
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_repeated_reviewed_diagnostic_is_rejected(self):
        from unittest.mock import patch
        codes = ("MERGE_HISTORICAL_RUN_UNREVIEWED",) * 2
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=codes)
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_unreviewed_ascii_diagnostics_remain_rejected(self):
        from unittest.mock import patch
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=("A_ERROR", "Z_ERROR"))
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_mixed_known_unknown_codes_deny_full_result(self):
        from unittest.mock import patch
        codes = ("MERGE_HISTORICAL_RUN_UNREVIEWED", "Z_ERROR")
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=codes)
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RESULT_SHAPE_UNREVIEWED",))
        self.assertNotIn("Z_ERROR", repr(result))

    def test_real_diagnostic_code_does_not_grant_annual_authority(self):
        from unittest.mock import patch
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=("TREE_CHAIN_ROOT_SHA_UNREVIEWED",))
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertFalse(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_single_real_code_remains_source_diagnostic_only(self):
        from unittest.mock import patch
        code = "MERGE_HISTORICAL_RUN_UNREVIEWED"
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=(code,))
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertEqual(result["diagnostics"], (code,))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_clean_source_fixture_remains_nonauthorizing_after_correction(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_exact_255_byte_ascii_filename_is_lexically_reviewable(self):
        path = "docs/" + "x"*255
        self.assertEqual(len(path.split("/")[-1].encode("utf-8")), 255)
        self.assertTrue(_reviewed_source_path(path))

    def test_one_over_255_byte_ascii_filename_rejected(self):
        path = "docs/" + "x"*256
        self.assertFalse(_reviewed_source_path(path))

    def test_exact_utf8_multibyte_component_boundary_reviewable(self):
        path = "docs/" + "é"*127 + "a"
        self.assertEqual(len(path.split("/")[-1].encode("utf-8")), 255)
        self.assertTrue(_reviewed_source_path(path))

    def test_multibyte_component_over_utf8_byte_cap_rejected(self):
        path = "docs/" + "é"*128
        self.assertEqual(len(path.split("/")[-1].encode("utf-8")), 256)
        self.assertFalse(_reviewed_source_path(path))

    def test_total_utf8_path_over_cap_rejected_even_with_short_segments(self):
        segments = ["é"*100 for _ in range(23)]
        path = "/".join(segments)
        self.assertGreater(len(path.encode("utf-8")), MAX_SOURCE_PATH_UTF8_BYTES)
        self.assertLess(len(path), MAX_SOURCE_PATH_CHARS)
        self.assertFalse(_reviewed_source_path(path))

    def test_direct_source_over_utf8_segment_cap_fails_closed(self):
        self.envelope["changed_bytes_b64"]["docs/" + "é"*128] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_ci_workflow_source_over_utf8_segment_cap_fails_closed(self):
        self.envelope["ci_workflow_bytes_b64"]["ci/" + "x"*256] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_unpaired_unicode_path_refused_without_encoding_exception(self):
        self.assertFalse(_reviewed_source_path("docs/\ud800.txt"))

    def test_stdin_oversized_component_never_echoes_source_label(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"]["docs/" + "SENTINEL" + "x"*256] = "YQ=="
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), output)
        result = json.loads(output.getvalue())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", result["diagnostics"])
        self.assertNotIn("SENTINEL", output.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_utf8_byte_caps_preserve_clean_synthetic_source_only(self):
        verdict = self.verdict()
        self.assertTrue(verdict["source_consistency"])
        self.assertEqual(verdict["diagnostics"], ())
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_raw_ci_log_embedded_nul_is_rejected_directly(self):
        self.envelope["raw_ci_runner_logs"]["9101"] = "before\x00after"
        self.assert_fails("BUNDLE_RAW_LOG_TEXT_UNREVIEWED")

    def test_raw_ci_log_leading_nul_is_rejected(self):
        self.envelope["raw_ci_runner_logs"]["9101"] = "\x00marker"
        self.assert_fails("BUNDLE_RAW_LOG_TEXT_UNREVIEWED")

    def test_raw_ci_log_trailing_nul_is_rejected(self):
        self.envelope["raw_ci_runner_logs"]["9101"] = "marker\x00"
        self.assert_fails("BUNDLE_RAW_LOG_TEXT_UNREVIEWED")

    def test_raw_ci_log_nul_rejected_before_invalid_run_id(self):
        self.envelope["raw_ci_runner_logs"]["non-decimal"] = "safe\x00hidden"
        result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RAW_LOG_TEXT_UNREVIEWED",))

    def test_raw_ci_log_nul_json_escape_fails_closed(self):
        raw = json.dumps(self.envelope)
        parsed = json.loads(raw)
        parsed["raw_ci_runner_logs"]["9101"] = "\u0000"
        verdict = review_bundle_json_text(json.dumps(parsed))
        self.assertEqual(verdict["diagnostics"],
                         ("BUNDLE_RAW_LOG_TEXT_UNREVIEWED",))
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_raw_ci_log_newline_and_tab_are_not_forbidden_by_nul_guard(self):
        self.assertNotIn("\x00", "synthetic\n\tCI log")
        self.assertTrue(_within_inmemory_structure_budget(
            {"raw_ci_runner_logs": {"9101": "synthetic\n\tCI log"}}))

    def test_raw_ci_log_nul_stdin_output_never_echoes_private_bytes(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["raw_ci_runner_logs"]["9101"] = "private-canary\x00secret"
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), out)
        record = json.loads(out.getvalue())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_RAW_LOG_TEXT_UNREVIEWED", record["diagnostics"])
        self.assertNotIn("private-canary", out.getvalue())
        self.assertFalse(record["can_authorize_annual_run"])

    def test_raw_ci_log_nul_cannot_approve_annual_execution(self):
        self.envelope["raw_ci_runner_logs"]["9101"] = "\x00"
        result = self.verdict()
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_regular_raw_ci_log_fixture_remains_source_only_consistent(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_float_exact_literal_cap_is_syntactically_accepted(self):
        raw = "1." + "0" * (MAX_JSON_FLOAT_LITERAL_CHARS-2)
        self.assertEqual(len(raw), MAX_JSON_FLOAT_LITERAL_CHARS)
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"], ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_float_over_literal_cap_is_grammar_refusal(self):
        raw = "1." + "0" * (MAX_JSON_FLOAT_LITERAL_CHARS-1)
        self.assertEqual(len(raw), MAX_JSON_FLOAT_LITERAL_CHARS+1)
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_negative_float_over_literal_cap_refused(self):
        raw = "-1." + "0" * (MAX_JSON_FLOAT_LITERAL_CHARS-2)
        self.assertGreater(len(raw), MAX_JSON_FLOAT_LITERAL_CHARS)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_long_exponent_text_refused_before_float_conversion(self):
        raw = "1e-" + "0" * MAX_JSON_FLOAT_LITERAL_CHARS
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_exact_exponent_text_limit_is_decodable(self):
        raw = "1e-" + "0" * (MAX_JSON_FLOAT_LITERAL_CHARS-3)
        self.assertEqual(len(raw), MAX_JSON_FLOAT_LITERAL_CHARS)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_nested_oversized_float_literal_fails_grammar(self):
        raw = '{"synthetic":' + "1." + "0" * 140 + "}"
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_normal_scientific_decimal_still_decodable(self):
        result = review_bundle_json_text("1.25e+2")
        self.assertEqual(result["diagnostics"], ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_nonfinite_short_exponent_still_fails_grammar(self):
        result = review_bundle_json_text("1e400")
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_oversized_float_stdout_does_not_echo_token(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        raw = '{"private_sentinel":' + "1." + "9"*200 + "}"
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), output)
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(output.getvalue())["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("9999999999", output.getvalue())

    def test_json_float_parser_budget_preserves_clean_evidence_consistency(self):
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_windows_com_superscript_one_is_reserved(self):
        self.assertFalse(_reviewed_source_path("src/COM¹.txt"))

    def test_windows_com_superscript_two_is_reserved(self):
        self.assertFalse(_reviewed_source_path("src/com².md"))

    def test_windows_com_superscript_three_is_reserved(self):
        self.assertFalse(_reviewed_source_path("docs/CoM³"))

    def test_windows_lpt_superscript_one_is_reserved(self):
        self.assertFalse(_reviewed_source_path("src/LPT¹.txt"))

    def test_windows_lpt_superscript_two_and_three_are_reserved(self):
        self.assertFalse(_reviewed_source_path("src/lpt².txt"))
        self.assertFalse(_reviewed_source_path("src/LPT³"))

    def test_windows_conin_conout_dollar_devices_are_reserved(self):
        self.assertFalse(_reviewed_source_path("src/CONIN$.txt"))
        self.assertFalse(_reviewed_source_path("src/conout$.log"))

    def test_windows_similar_unreserved_names_remain_allowed(self):
        for path in ("src/COM10.txt", "src/LPT10.txt",
                     "src/CONINPUT.log", "src/CONOUTFILE.txt"):
            with self.subTest(path=path):
                self.assertTrue(_reviewed_source_path(path))

    def test_superscript_reserved_source_map_fails_closed(self):
        self.envelope["changed_bytes_b64"]["src/COM².txt"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_reserved_workflow_name_fails_closed(self):
        self.envelope["ci_workflow_bytes_b64"]["ci/CONOUT$.yml"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_reserved_superscript_stdin_verdict_never_echoes_name(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"]["src/COM¹-PRIVATE.txt"] = "YQ=="
        self.envelope["changed_bytes_b64"]["src/COM¹.txt"] = "YQ=="
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), output)
        record = json.loads(output.getvalue())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", record["diagnostics"])
        self.assertNotIn("COM¹", output.getvalue())
        self.assertFalse(record["can_authorize_annual_run"])

    def test_clean_non_reserved_synthetic_source_remains_consistent_only(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_noncharacter_fdd0_source_path_rejected(self):
        self.assertFalse(_reviewed_source_path("src/\ufdd0.py"))

    def test_noncharacter_fdef_source_path_rejected(self):
        self.assertFalse(_reviewed_source_path("src/\ufdef.py"))

    def test_noncharacter_fffe_source_path_rejected(self):
        self.assertFalse(_reviewed_source_path("src/\ufffe.py"))

    def test_noncharacter_ffff_source_path_rejected(self):
        self.assertFalse(_reviewed_source_path("src/\uffff.py"))

    def test_supplementary_plane_noncharacter_rejected(self):
        self.assertFalse(_reviewed_source_path("src/\U0001fffe.py"))

    def test_highest_unicode_noncharacter_rejected(self):
        self.assertFalse(_reviewed_source_path("src/\U0010ffff.py"))

    def test_noncharacter_in_changed_source_map_fails_closed(self):
        self.envelope["changed_bytes_b64"]["src/\ufdd0canary.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_noncharacter_in_workflow_source_map_fails_closed(self):
        self.envelope["ci_workflow_bytes_b64"]["ci/\ufffe.yml"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_noncharacter_stdin_source_name_never_echoed(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"]["src/private\U0010ffffcanary.py"] = "YQ=="
        out = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), out)
        verdict = json.loads(out.getvalue())
        self.assertEqual(rc, 2)
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", verdict["diagnostics"])
        self.assertNotIn("private", out.getvalue())
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_noncharacter_guard_preserves_plain_unicode_source_only(self):
        self.assertTrue(_reviewed_source_path("docs/café.py"))
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_fraction_slash_source_path_refused(self):
        self.assertFalse(_reviewed_source_path("src\u2044file.py"))

    def test_division_slash_source_path_refused(self):
        self.assertFalse(_reviewed_source_path("src\u2215file.py"))

    def test_big_solidus_source_path_refused(self):
        self.assertFalse(_reviewed_source_path("src\u29f8file.py"))

    def test_fullwidth_solidus_source_path_refused(self):
        self.assertFalse(_reviewed_source_path("src\uff0ffile.py"))

    def test_set_minus_source_path_refused(self):
        self.assertFalse(_reviewed_source_path("src\u2216file.py"))

    def test_reverse_solidus_operator_source_path_refused(self):
        self.assertFalse(_reviewed_source_path("src\u29f5file.py"))

    def test_fullwidth_reverse_solidus_source_path_refused(self):
        self.assertFalse(_reviewed_source_path("src\uff3cfile.py"))

    def test_confusable_separator_changed_source_map_fails_closed(self):
        self.envelope["changed_bytes_b64"]["src\u2215secret.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_confusable_separator_workflow_source_map_fails_closed(self):
        self.envelope["ci_workflow_bytes_b64"]["ci\uff0fsecret.yml"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_confusable_separator_stdin_verdict_is_non_disclosing(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"]["src\u2044PRIVATE-CANARY.py"] = "YQ=="
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), out)
        result = json.loads(out.getvalue())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", result["diagnostics"])
        self.assertNotIn("PRIVATE-CANARY", out.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_real_posix_separator_and_clean_source_only_fixture_preserved(self):
        self.assertTrue(_reviewed_source_path("docs/sample.md"))
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_no_break_space_in_source_label_is_rejected(self):
        self.assertFalse(_reviewed_source_path("docs/non\u00a0break.md"))

    def test_narrow_no_break_space_source_label_is_rejected(self):
        self.assertFalse(_reviewed_source_path("docs/narrow\u202fspace.md"))

    def test_thin_space_source_label_is_rejected(self):
        self.assertFalse(_reviewed_source_path("docs/thin\u2009space.md"))

    def test_en_space_source_label_is_rejected(self):
        self.assertFalse(_reviewed_source_path("docs/en\u2002space.md"))

    def test_ideographic_space_source_label_is_rejected(self):
        self.assertFalse(_reviewed_source_path("docs/ideographic\u3000space.md"))

    def test_ascii_internal_space_remains_accepted(self):
        self.assertTrue(_reviewed_source_path("docs/project notes.md"))

    def test_ascii_trailing_space_remains_rejected(self):
        self.assertFalse(_reviewed_source_path("docs/report.md "))

    def test_nonascii_space_in_changed_source_map_fails_closed(self):
        self.envelope["changed_bytes_b64"]["docs/a\u00a0b.md"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_nonascii_space_in_ci_workflow_map_fails_closed(self):
        self.envelope["ci_workflow_bytes_b64"]["ci/a\u2009b.yml"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_nonascii_space_stdin_does_not_echo_private_name(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"]["docs/private\u202fCANARY.md"] = "YQ=="
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), output)
        result = json.loads(output.getvalue())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", result["diagnostics"])
        self.assertNotIn("CANARY", output.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_plain_space_guard_preserves_clean_source_consistency(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_long_path_exact_boundary_all_components_portable(self):
        path = "/".join(["x"*240] * 17)
        self.assertEqual(len(path), 4096)
        self.assertEqual(max(len(x.encode("utf-8")) for x in path.split("/")), 240)
        self.assertTrue(_reviewed_source_path(path))

    def test_long_path_one_extra_ascii_character_rejected_by_total(self):
        path = "/".join(["x"*240] * 16 + ["x"*241])
        self.assertEqual(len(path), 4097)
        self.assertFalse(_reviewed_source_path(path))

    def test_one_256_byte_component_rejected_even_under_total_cap(self):
        path = "src/" + "x"*256
        self.assertLess(len(path), MAX_SOURCE_PATH_CHARS)
        self.assertFalse(_reviewed_source_path(path))

    def test_multibyte_path_uses_utf8_length_not_code_point_count(self):
        path = "/".join(["é"*120] * 17)
        self.assertEqual(max(len(p.encode("utf-8")) for p in path.split("/")), 240)
        self.assertTrue(_reviewed_source_path(path))
        over = path + "/" + "é"*120
        self.assertLess(len(over), MAX_SOURCE_PATH_CHARS)
        self.assertGreater(len(over.encode("utf-8")), MAX_SOURCE_PATH_UTF8_BYTES)
        self.assertFalse(_reviewed_source_path(over))

    def test_ascii_compound_path_4095_bytes_is_valid(self):
        path = "/".join(["x"*255]*16)
        self.assertEqual(len(path.encode("utf-8")), 4095)
        self.assertTrue(_reviewed_source_path(path))

    def test_total_path_limit_does_not_override_255_byte_component(self):
        path = "/".join(["x"*255]*15 + ["x"*256])
        self.assertFalse(_reviewed_source_path(path))

    def test_overlong_component_fails_closed_before_composite_review(self):
        from unittest.mock import patch
        self.envelope["changed_bytes_b64"]["src/" + "x"*256] = "YQ=="
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=AssertionError("must not run")) as nested:
            self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")
        nested.assert_not_called()

    def test_overlimit_total_path_fails_closed_without_echoing_path(self):
        from unittest.mock import patch
        path = "/".join(["SECRET"*40] * 16 + ["SECRET"*40+"x"])
        self.envelope["changed_bytes_b64"][path] = "YQ=="
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=AssertionError("must not run")):
            result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SOURCE_PATH_UNREVIEWED",))
        self.assertNotIn("SECRET", repr(result))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_path_boundary_corrected_fixture_remains_source_only(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_hook_exact_object_member_limit_is_accepted(self):
        pairs = [(str(i), i) for i in range(MAX_JSON_OBJECT_MEMBERS)]
        self.assertEqual(len(_no_duplicate_keys(pairs)), MAX_JSON_OBJECT_MEMBERS)

    def test_json_hook_one_over_member_limit_is_rejected(self):
        pairs = [(str(i), i) for i in range(MAX_JSON_OBJECT_MEMBERS+1)]
        with self.assertRaises(ValueError):
            _no_duplicate_keys(pairs)

    def test_json_hook_duplicate_keys_still_rejected_below_cap(self):
        with self.assertRaises(ValueError):
            _no_duplicate_keys([("synthetic", 1), ("synthetic", 2)])

    def test_json_hook_small_object_preserves_pair_values(self):
        self.assertEqual(_no_duplicate_keys([("x", 1), ("y", 2)]),
                         {"x": 1, "y": 2})

    def test_json_nested_object_over_member_limit_fails_grammar(self):
        data = {"synthetic": {str(i): 0
                              for i in range(MAX_JSON_OBJECT_MEMBERS+1)}}
        raw = json.dumps(data, separators=(",", ":"))
        self.assertLess(len(raw), MAX_TEXT_CHARS)
        verdict = review_bundle_json_text(raw)
        self.assertEqual(verdict["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_json_nested_exact_member_limit_reaches_envelope_shape(self):
        data = {"synthetic": {str(i): 0
                              for i in range(MAX_JSON_OBJECT_MEMBERS)}}
        verdict = review_bundle_json_text(json.dumps(data))
        self.assertEqual(verdict["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_json_top_level_many_unique_keys_fail_grammar_before_shape(self):
        raw = json.dumps({str(i): None
                          for i in range(MAX_JSON_OBJECT_MEMBERS+1)})
        verdict = review_bundle_json_text(raw)
        self.assertEqual(verdict["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_object_cap_rejects_untrusted_values_without_echo(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        data = {"private_canary": {str(i): "secret"
                 for i in range(MAX_JSON_OBJECT_MEMBERS+1)}}
        out = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(json.dumps(data)), out)
        self.assertEqual(rc, 2)
        result = json.loads(out.getvalue())
        self.assertEqual(result["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("private_canary", out.getvalue())

    def test_valid_nested_json_source_fixture_still_non_authorizing(self):
        verdict = review_bundle_json_text(json.dumps(self.envelope))
        self.assertTrue(verdict["source_consistency"])
        self.assertEqual(verdict["diagnostics"], ())
        self.assertFalse(verdict["independent_original_os_proof"])
        self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_compatibility_fullwidth_ascii_source_alias_rejected(self):
        self.envelope["changed_bytes_b64"].update({
            "src/ＡＢＣ.py": "YQ==", "src/abc.py": "YQ=="})
        self.assert_fails("BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED")

    def test_compatibility_circled_digit_source_alias_rejected(self):
        self.envelope["changed_bytes_b64"].update({
            "src/stage①.py": "YQ==", "src/stage1.py": "YQ=="})
        self.assert_fails("BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED")

    def test_compatibility_roman_numeral_source_alias_rejected(self):
        self.envelope["changed_bytes_b64"].update({
            "src/Ⅰ.py": "YQ==", "src/i.py": "YQ=="})
        self.assert_fails("BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED")

    def test_compatibility_workflow_map_alias_rejected(self):
        self.envelope["ci_workflow_bytes_b64"].update({
            "ci/ＦＯＯ.yml": "YQ==", "ci/foo.yml": "YQ=="})
        self.assert_fails("BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED")

    def test_compatibility_crossmap_alias_rejected(self):
        self.envelope["changed_bytes_b64"]["ci/ＡＢＣ.yml"] = "YQ=="
        self.envelope["ci_workflow_bytes_b64"]["ci/abc.yml"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_CROSSMAP_COLLISION_UNREVIEWED")

    def test_compatibility_identity_retains_literal_valid_path(self):
        self.assertTrue(_reviewed_source_path("src/①.py"))
        self.assertEqual(_portable_source_path_identity("src/①.py"),
                         _portable_source_path_identity("src/1.py"))

    def test_compatibility_identity_does_not_alias_distinct_dirs(self):
        self.assertNotEqual(
            _portable_source_path_identity("src/①.py"),
            _portable_source_path_identity("docs/1.py"))

    def test_compatibility_source_stdin_diagnostic_has_no_path_echo(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"].update({
            "src/ＰＲＩＶＡＴＥ.py": "YQ==",
            "src/private.py": "YQ=="})
        output = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), output)
        record = json.loads(output.getvalue())
        self.assertEqual(rc, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED"])
        self.assertNotIn("private.py", output.getvalue())
        self.assertFalse(record["can_authorize_annual_run"])

    def test_compatibility_alias_guard_preserves_clean_source_only(self):
        verdict = self.verdict()
        self.assertTrue(verdict["source_consistency"])
        self.assertEqual(verdict["diagnostics"], ())
        self.assertFalse(verdict["independent_original_os_proof"])
        self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_fullwidth_con_is_reserved_source_device(self):
        self.assertFalse(_reviewed_source_path("src/ＣＯＮ.txt"))

    def test_fullwidth_prn_and_aux_are_reserved(self):
        self.assertFalse(_reviewed_source_path("src/ＰＲＮ.log"))
        self.assertFalse(_reviewed_source_path("src/ＡＵＸ.md"))

    def test_fullwidth_com_digit_is_reserved(self):
        self.assertFalse(_reviewed_source_path("src/ＣＯＭ１.txt"))

    def test_compatibility_circled_digit_device_is_reserved(self):
        self.assertFalse(_reviewed_source_path("src/COM①.txt"))

    def test_fullwidth_lpt_digit_is_reserved(self):
        self.assertFalse(_reviewed_source_path("src/ＬＰＴ９.log"))

    def test_fullwidth_console_aliases_are_reserved(self):
        self.assertFalse(_reviewed_source_path("src/ＣＯＮＩＮ＄.log"))
        self.assertFalse(_reviewed_source_path("src/ＣＯＮＯＵＴ＄.log"))

    def test_compatibility_similar_ordinary_names_still_allowed(self):
        self.assertTrue(_reviewed_source_path("src/ＣＯＮＳＯＬＥ.py"))
        self.assertTrue(_reviewed_source_path("src/ＣＯＭ１０.txt"))

    def test_compatibility_reserved_changed_source_fails_closed(self):
        self.envelope["changed_bytes_b64"]["src/ＣＯＮ.txt"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_compatibility_reserved_workflow_source_fails_closed(self):
        self.envelope["ci_workflow_bytes_b64"]["ci/ＣＯＭ１.yml"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_compatibility_reserved_stdin_never_echoes_source(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"]["src/ＣＯＮ.private-canary"] = "YQ=="
        output = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), output)
        result = json.loads(output.getvalue())
        self.assertEqual(rc, 2)
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", result["diagnostics"])
        self.assertNotIn("private-canary", output.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_compatibility_device_guard_preserves_source_consistency_only(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_compatibility_exact_252_byte_segment_is_valid(self):
        path = "src/" + "Ⅷ"*63
        self.assertEqual(len(unicodedata.normalize("NFKC", path).split("/")[-1]
                             .encode("utf-8")), 252)
        self.assertTrue(_reviewed_source_path(path))

    def test_compatibility_256_byte_segment_is_rejected(self):
        path = "src/" + "Ⅷ"*64
        self.assertLess(len(path.split("/")[-1].encode("utf-8")), 255)
        self.assertFalse(_reviewed_source_path(path))

    def test_compatibility_total_path_over_utf8_budget_is_rejected(self):
        path = "/".join(["Ⅷ"*50] * 23)
        self.assertLess(len(path.encode("utf-8")), MAX_SOURCE_PATH_UTF8_BYTES)
        self.assertGreater(len(unicodedata.normalize("NFKC", path).encode("utf-8")),
                           MAX_SOURCE_PATH_UTF8_BYTES)
        self.assertFalse(_reviewed_source_path(path))

    def test_fullwidth_period_trailing_segment_is_rejected(self):
        self.assertFalse(_reviewed_source_path("docs/report．"))

    def test_fullwidth_period_inside_component_remains_valid(self):
        self.assertTrue(_reviewed_source_path("docs/report．txt"))

    def test_compatibility_introduced_reverse_solidus_is_rejected(self):
        self.assertEqual(unicodedata.normalize("NFKC", "\ufe68"), "\\")
        self.assertFalse(_reviewed_source_path("src/a\ufe68b.py"))

    def test_compatibility_introduced_colon_is_rejected(self):
        self.assertEqual(unicodedata.normalize("NFKC", "\ufe13"), ":")
        self.assertFalse(_reviewed_source_path("src/a\ufe13b.py"))

    def test_compatibility_byte_overflow_changed_source_map_fails_closed(self):
        self.envelope["changed_bytes_b64"]["src/" + "Ⅷ"*64] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_compatibility_trailing_period_workflow_map_fails_closed(self):
        self.envelope["ci_workflow_bytes_b64"]["ci/hidden．"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_compatibility_overflow_stdin_does_not_echo_name(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"]["src/private-"+"Ⅷ"*64] = "YQ=="
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), out)
        result = json.loads(out.getvalue())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", result["diagnostics"])
        self.assertNotIn("private-", out.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_compatibility_budget_preserves_clean_source_only_fixture(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_fourbyte_unicode_log_exceeds_per_run_byte_cap(self):
        self.envelope["raw_ci_runner_logs"]["9101"] = "😀"*500001
        self.assert_fails("BUNDLE_RAW_LOG_UTF8_OVERSIZE")

    def test_fourbyte_unicode_log_exact_per_run_byte_limit(self):
        log = "😀"*500000
        self.assertEqual(len(log.encode("utf-8")), MAX_RAW_LOG_UTF8_BYTES_PER_RUN)
        self.envelope["raw_ci_runner_logs"]["9101"] = log
        verdict = self.verdict()
        self.assertNotIn("BUNDLE_RAW_LOG_UTF8_OVERSIZE", verdict["diagnostics"])
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_twobyte_unicode_log_exceeds_per_run_byte_cap(self):
        self.envelope["raw_ci_runner_logs"]["9101"] = "é"*1000001
        self.assert_fails("BUNDLE_RAW_LOG_UTF8_OVERSIZE")

    def test_multiple_multibyte_logs_exceed_total_byte_cap(self):
        self.envelope["raw_ci_runner_logs"] = {
            "9101": "😀"*350000, "9102": "😀"*350000, "9103": "😀"*350000}
        self.assert_fails("BUNDLE_TOTAL_RAW_LOG_UTF8_OVERSIZE")

    def test_exact_aggregate_four_megabyte_logs_not_byte_rejected(self):
        self.envelope["raw_ci_runner_logs"] = {
            "9101": "😀"*500000, "9102": "😀"*500000}
        result = self.verdict()
        self.assertNotIn("BUNDLE_TOTAL_RAW_LOG_UTF8_OVERSIZE",
                         result["diagnostics"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_byte_cap_precedes_invalid_runner_id_parse(self):
        self.envelope["raw_ci_runner_logs"]["not-an-id"] = "😀"*500001
        result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RAW_LOG_UTF8_OVERSIZE",))

    def test_stdin_global_utf8_json_cap_precedes_raw_log_byte_guard(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["raw_ci_runner_logs"]["9101"] = "PRIVATE-CANARY" + "😀"*500001
        output = io.StringIO()
        raw = json.dumps(self.envelope, ensure_ascii=False)
        self.assertGreater(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        rc = cli.run_stdin_review(io.StringIO(raw), output)
        verdict = json.loads(output.getvalue())
        self.assertEqual(rc, 2)
        self.assertEqual(verdict["diagnostics"],
                         ["BUNDLE_JSON_TEXT_UNREVIEWED"])
        self.assertNotIn("PRIVATE-CANARY", output.getvalue())
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_plain_ascii_ci_log_within_byte_cap(self):
        text = "ASCII synthetic CI receipt"
        self.assertEqual(len(text), len(text.encode("utf-8")))
        self.assertLess(len(text.encode("utf-8")), MAX_RAW_LOG_UTF8_BYTES_PER_RUN)

    def test_valid_ci_log_fixture_remains_source_consistent_only(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_fullwidth_single_dot_component_is_rejected(self):
        self.assertFalse(_reviewed_source_path("src/．/file.py"))

    def test_fullwidth_double_dot_component_is_rejected(self):
        self.assertFalse(_reviewed_source_path("src/．．/file.py"))

    def test_mixed_fullwidth_ascii_dot_component_is_rejected(self):
        self.assertFalse(_reviewed_source_path("src/．./file.py"))
        self.assertFalse(_reviewed_source_path("src/.．/file.py"))

    def test_compatibility_dot_traversal_changed_map_rejected(self):
        self.envelope["changed_bytes_b64"]["src/．．/hidden.py"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_compatibility_dot_traversal_workflow_map_rejected(self):
        self.envelope["ci_workflow_bytes_b64"]["ci/．/hidden.yml"] = "YQ=="
        self.assert_fails("BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_compatibility_dot_traversal_stdin_does_not_echo_input(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["changed_bytes_b64"]["src/．．/private-canary.py"] = "YQ=="
        out = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(json.dumps(self.envelope)), out)
        result = json.loads(out.getvalue())
        self.assertEqual(rc, 2)
        self.assertIn("BUNDLE_SOURCE_PATH_UNREVIEWED", result["diagnostics"])
        self.assertNotIn("private-canary", out.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_fullwidth_leading_dotfile_is_not_a_dot_segment(self):
        self.assertTrue(_reviewed_source_path("src/．gitignore"))

    def test_fullwidth_double_leading_dot_filename_is_not_parent(self):
        self.assertTrue(_reviewed_source_path("src/．．gitignore"))

    def test_compatibility_dot_segment_guard_preserves_source_only_fixture(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_text_exact_two_million_ascii_bytes_keeps_parser_contract(self):
        raw = "x" * MAX_TEXT_UTF8_BYTES
        self.assertEqual(len(raw), MAX_TEXT_CHARS)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_text_one_over_ascii_byte_limit_refused(self):
        raw = "x" * (MAX_TEXT_UTF8_BYTES+1)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))

    def test_json_text_exact_multibyte_utf8_byte_limit(self):
        raw = '"'+ "é" * (MAX_TEXT_UTF8_BYTES//2 - 2) + '"'
        self.assertLess(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_text_multibyte_excess_refused_before_parse(self):
        raw = '"'+ "é" * (MAX_TEXT_UTF8_BYTES//2) + '"'
        self.assertLess(len(raw), MAX_TEXT_CHARS)
        self.assertGreater(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))

    def test_json_text_emoji_byte_excess_refused(self):
        raw = '"'+ "🚀" * (MAX_TEXT_UTF8_BYTES//4) + '"'
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))

    def test_json_text_actual_unpaired_surrogate_refused_without_traceback(self):
        raw = '{"private":"\ud800"}'
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_UNICODE_UNREVIEWED",))

    def test_json_text_escaped_surrogate_retains_unicode_specific_refusal(self):
        raw = r'{"private":"\ud800"}'
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_UNICODE_UNREVIEWED",))

    def test_json_text_utf8_size_refusal_stdin_does_not_echo_source(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        raw = '{"secret":"'+ "é" * (MAX_TEXT_UTF8_BYTES//2) + '"}'
        out = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(raw), out)
        result = json.loads(out.getvalue())
        self.assertEqual(rc, 2)
        self.assertEqual(result["diagnostics"], ["BUNDLE_JSON_TEXT_UNREVIEWED"])
        self.assertNotIn("secret", out.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_text_utf8_cap_preserves_synthetic_source_only(self):
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_direct_utf8_exact_four_megabyte_scalar_accepted(self):
        value = "é" * 2000000
        self.assertEqual(len(value.encode("utf-8")), MAX_INMEMORY_SCALAR_UTF8_BYTES)
        self.assertTrue(_within_inmemory_structure_budget(value))

    def test_direct_utf8_one_over_scalar_byte_limit_refused(self):
        value = "é" * 2000000 + "a"
        self.assertFalse(_within_inmemory_structure_budget(value))

    def test_direct_utf8_emoji_scalar_excess_refused(self):
        self.assertFalse(_within_inmemory_structure_budget("🚀"*1000001))

    def test_direct_utf8_bytes_scalar_at_exact_limit_accepted(self):
        value = b"x" * MAX_INMEMORY_SCALAR_UTF8_BYTES
        self.assertTrue(_within_inmemory_structure_budget(value))

    def test_direct_utf8_aggregate_byte_cap_refuses_unicode(self):
        value = "é"*2000000
        self.assertFalse(_within_inmemory_structure_budget([value]*5))

    def test_direct_utf8_aggregate_byte_cap_exact_boundary_accepted(self):
        value = "é"*2000000
        self.assertTrue(_within_inmemory_structure_budget([value]*4))

    def test_direct_utf8_unicode_dict_key_budget_enforced(self):
        value = "é"*2000001
        self.assertFalse(_within_inmemory_structure_budget({value: None}))

    def test_direct_utf8_byte_cap_in_envelope_is_sanitized(self):
        data = dict(self.envelope)
        pr = dict(data["pr"])
        pr["synthetic_private"] = "canary" + "🚀"*1000001
        data["pr"] = pr
        result = review_bundle_envelope(data)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",))
        self.assertNotIn("canary", repr(result))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_direct_utf8_scalar_budget_clean_consistency_only(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_nested_result_integer_key_is_safely_refused(self):
        from unittest.mock import patch
        bad = dict(self.verdict())
        bad[99] = "private-canary"
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_nested_result_none_key_is_safely_refused(self):
        from unittest.mock import patch
        bad = dict(self.verdict())
        bad[None] = "private-canary"
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_nested_result_string_subclass_key_is_safely_refused(self):
        from unittest.mock import patch
        class NonPlainKey(str):
            pass
        bad = dict(self.verdict())
        bad[NonPlainKey("private-canary")] = True
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_nested_result_custom_key_is_not_rehashed_during_review(self):
        from unittest.mock import patch
        class Untrusted:
            def __init__(self):
                self.hash_calls = 0
            def __hash__(self):
                self.hash_calls += 1
                return 19024
            def __eq__(self, other):
                raise AssertionError("untrusted equality")
        key = Untrusted()
        bad = dict(self.verdict())
        bad[key] = "private-canary"
        key.hash_calls = 0
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertEqual(key.hash_calls, 0)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RESULT_SHAPE_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_nested_result_custom_key_never_rendered_into_diagnostics(self):
        from unittest.mock import patch
        class Untrusted:
            def __hash__(self):
                return 17290
            def __repr__(self):
                raise AssertionError("must not render key")
        bad = dict(self.verdict())
        bad[Untrusted()] = "secret-result"
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertNotIn("secret-result", repr(result))
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RESULT_SHAPE_UNREVIEWED",))

    def test_nested_result_plain_unexpected_key_still_refused(self):
        from unittest.mock import patch
        bad = dict(self.verdict(), unauthorized_synthetic=True)
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_nested_result_dict_subclass_still_refused_first(self):
        from unittest.mock import patch
        class CustomDict(dict):
            pass
        bad = CustomDict(self.verdict())
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            self.assert_fails("BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_nested_result_correct_plain_keys_can_preserve_known_failure(self):
        from unittest.mock import patch
        bad = dict(self.verdict(), source_consistency=False,
                   diagnostics=("MERGE_HISTORICAL_RUN_UNREVIEWED",))
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=bad):
            result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("MERGE_HISTORICAL_RUN_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_nested_result_key_type_guard_preserves_clean_source_only(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_direct_large_multibyte_log_retains_per_log_byte_refusal(self):
        self.envelope["raw_ci_runner_logs"]["9101"] = "🚀"*500001
        verdict = self.verdict()
        self.assertEqual(verdict["diagnostics"],
                         ("BUNDLE_RAW_LOG_UTF8_OVERSIZE",))
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_direct_raw_log_utf8_total_budget_is_still_independent(self):
        self.envelope["raw_ci_runner_logs"] = {
            "9101": "é"*800000, "9102": "é"*800000, "9103": "é"*800000}
        verdict = self.verdict()
        self.assertEqual(verdict["diagnostics"],
                         ("BUNDLE_TOTAL_RAW_LOG_UTF8_OVERSIZE",))

    def test_stdin_emits_global_byte_limit_when_log_exceeds_text_budget(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["raw_ci_runner_logs"]["9101"] = "é"*1000001
        out = io.StringIO()
        status = cli.run_stdin_review(
            io.StringIO(json.dumps(self.envelope, ensure_ascii=False)), out)
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(out.getvalue())["diagnostics"],
                         ["BUNDLE_JSON_TEXT_UNREVIEWED"])

    def test_global_input_byte_guard_applies_even_without_large_log(self):
        raw = json.dumps(self.envelope) + " " * MAX_TEXT_UTF8_BYTES
        verdict = review_bundle_json_text(raw)
        self.assertEqual(verdict["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))

    def test_small_multibyte_ci_log_not_rejected_by_global_budget(self):
        self.envelope["raw_ci_runner_logs"]["9101"] = "é"*100
        raw = json.dumps(self.envelope, ensure_ascii=False)
        self.assertLess(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        result = review_bundle_json_text(raw)
        self.assertNotIn("BUNDLE_JSON_TEXT_UNREVIEWED", result["diagnostics"])
        self.assertNotIn("BUNDLE_RAW_LOG_UTF8_OVERSIZE", result["diagnostics"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_stdin_global_limit_precedence_never_echoes_private_log(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["raw_ci_runner_logs"]["9101"] = (
            "private-log-canary" + "🚀"*500001)
        out = io.StringIO()
        rc = cli.run_stdin_review(
            io.StringIO(json.dumps(self.envelope, ensure_ascii=False)), out)
        result = json.loads(out.getvalue())
        self.assertEqual(rc, 2)
        self.assertEqual(result["diagnostics"], ["BUNDLE_JSON_TEXT_UNREVIEWED"])
        self.assertNotIn("private-log-canary", out.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_direct_oversized_raw_log_never_grants_exclusive_server_gate(self):
        self.envelope["raw_ci_runner_logs"]["9101"] = "🚀"*500001
        verdict = self.verdict()
        self.assertFalse(verdict["independent_original_os_proof"])
        self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_utf8_precedence_correction_keeps_clean_source_consistency(self):
        verdict = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(verdict["diagnostics"], ())
        self.assertTrue(verdict["source_consistency"])
        self.assertFalse(verdict["independent_original_os_proof"])
        self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_json_total_member_hook_accepts_exact_global_budget(self):
        hook = _bounded_json_pairs_hook()
        for _ in range(MAX_JSON_TOTAL_OBJECT_MEMBERS):
            self.assertEqual(hook([("k", 1)]), {"k": 1})

    def test_json_total_member_hook_rejects_one_over_global_budget(self):
        hook = _bounded_json_pairs_hook()
        for _ in range(MAX_JSON_TOTAL_OBJECT_MEMBERS):
            hook([("k", 1)])
        with self.assertRaises(ValueError):
            hook([("k", 1)])

    def test_json_total_member_hook_preserves_per_object_limit(self):
        hook = _bounded_json_pairs_hook()
        with self.assertRaises(ValueError):
            hook([(str(i), 1) for i in range(MAX_JSON_OBJECT_MEMBERS+1)])

    def test_json_total_member_hook_rejects_duplicate_before_budget_exhaustion(self):
        hook = _bounded_json_pairs_hook()
        with self.assertRaises(ValueError):
            hook([("k", 1), ("k", 2)])

    def test_json_many_small_objects_exceed_aggregate_members(self):
        # Hold every array below its own item limit: 16,384 groups of two
        # single-member objects, with one extra member in the first group.
        groups = ['[{"a":1},{"a":1},{"a":1}]'] + [
            '[{"a":1},{"a":1}]' for _ in range(MAX_JSON_ARRAY_ITEMS-1)]
        raw = "[" + ",".join(groups) + "]"
        self.assertLess(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertFalse(_json_lexical_object_budgets(raw))
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_exact_aggregate_object_members_reaches_shape(self):
        # A flat array of 32,768 objects trips the separate 16,384-item
        # array ceiling. Group pairs to isolate the object-member boundary.
        raw = "[" + ",".join('[{"a":1},{"a":1}]' for _ in range(
            MAX_JSON_ARRAY_ITEMS)) + "]"
        self.assertEqual(MAX_JSON_TOTAL_OBJECT_MEMBERS,
                         2 * MAX_JSON_ARRAY_ITEMS)
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"], ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_global_member_exact_boundary_does_not_raise_lexical_array(self):
        raw = "[" + ",".join('[{"a":1},{"a":1}]' for _ in range(
            MAX_JSON_ARRAY_ITEMS)) + "]"
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_global_member_one_over_is_not_an_array_failure(self):
        raw = ("[" + '[{"a":1},{"a":1},{"a":1}],' +
               ",".join('[{"a":1},{"a":1}]' for _ in range(
                   MAX_JSON_ARRAY_ITEMS-1)) + "]")
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertFalse(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_flat_array_over_cap_is_not_object_member_failure(self):
        raw = "[" + ",".join('{"a":1}' for _ in range(
            MAX_JSON_ARRAY_ITEMS+1)) + "]"
        self.assertFalse(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_empty_objects_do_not_exhaust_member_budget(self):
        raw = "[" + ",".join("[{},{}]" for _ in range(
            MAX_JSON_ARRAY_ITEMS)) + "]"
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_global_member_limit_fresh_for_separate_documents(self):
        raw = "[" + ",".join('[{"a":1},{"a":1}]' for _ in range(
            MAX_JSON_ARRAY_ITEMS)) + "]"
        for _ in range(2):
            self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                             ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_object_member_and_array_counts_do_not_grant_annual_authority(self):
        raw = "[" + ",".join('[{"a":1},{"a":1}]' for _ in range(
            MAX_JSON_ARRAY_ITEMS)) + "]"
        result = review_bundle_json_text(raw)
        self.assertFalse(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_array_budget_with_few_object_members_still_precedes_shape(self):
        raw = "[" + ",".join("[]" for _ in range(
            MAX_JSON_ARRAY_ITEMS+1)) + "]"
        self.assertFalse(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_mixed_small_object_groups_keep_shape_diagnostic(self):
        raw = json.dumps([[{"synthetic": 1}, {"synthetic": 2}],
                          [{"synthetic": 3}]], separators=(",", ":"))
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_total_member_counter_resets_for_each_document(self):
        raw = '["' + 'synthetic' + '"]'
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_total_members_stdin_never_echoes_evidence(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        # Root object's own member is the one-over case; arrays stay in
        # budget so this exercises the aggregate object-member refusal.
        raw = ('{"private_canary":[' +
               ",".join('[{"x":1},{"x":1}]' for _ in range(
                   MAX_JSON_ARRAY_ITEMS)) + ']}')
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertFalse(_json_lexical_object_budgets(raw))
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        record = json.loads(out.getvalue())
        self.assertEqual(status, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("private_canary", out.getvalue())
        self.assertFalse(record["can_authorize_annual_run"])

    def test_json_total_member_budget_keeps_clean_source_only_fixture(self):
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_array_at_exact_per_list_cap_reaches_shape(self):
        raw = "[" + ",".join("0" for _ in range(MAX_JSON_ARRAY_ITEMS)) + "]"
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_array_one_over_per_list_cap_rejected(self):
        raw = "[" + ",".join("0" for _ in range(MAX_JSON_ARRAY_ITEMS+1)) + "]"
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_many_small_arrays_exceed_global_item_cap(self):
        raw = "[" + ",".join("[0,0,0,0]" for _ in range(16384)) + "]"
        self.assertLess(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_global_array_cap_exact_boundary_allows_preflight(self):
        root = [[0, 0, 0] for _ in range(16384)]
        self.assertEqual(sum(len(v) for v in root) + len(root), 65536)
        self.assertTrue(_within_json_array_budgets(root))

    def test_json_global_array_cap_one_over_refused_by_preflight(self):
        root = [[0, 0, 0] for _ in range(16384)]
        root[0].append(0)
        self.assertFalse(_within_json_array_budgets(root))

    def test_json_nested_oversized_array_fails_grammar_before_shape(self):
        raw = '{"untrusted":[' + ",".join("null" for _ in range(
            MAX_JSON_ARRAY_ITEMS+1)) + "]}"
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_array_budget_has_fresh_state_per_document(self):
        raw = "[0,1,2]"
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_array_guard_stdout_never_echoes_raw_content(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        raw = '{"private_canary":[' + ",".join("0" for _ in range(
            MAX_JSON_ARRAY_ITEMS+1)) + ']}'
        output = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(raw), output)
        record = json.loads(output.getvalue())
        self.assertEqual(rc, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("private_canary", output.getvalue())
        self.assertFalse(record["can_authorize_annual_run"])

    def test_json_array_budget_preserves_clean_synthetic_bundle(self):
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_lexical_array_max_items_stays_in_bounds(self):
        raw = "[" + ",".join("0" for _ in range(MAX_JSON_ARRAY_ITEMS)) + "]"
        self.assertTrue(_json_lexical_array_budgets(raw))

    def test_lexical_array_one_over_max_items_fails(self):
        raw = "[" + ",".join("0" for _ in range(MAX_JSON_ARRAY_ITEMS+1)) + "]"
        self.assertFalse(_json_lexical_array_budgets(raw))

    def test_lexical_array_many_nested_containers_exceed_global_items(self):
        raw = "[" + ",".join("[1,2,3,4]" for _ in range(16384)) + "]"
        self.assertFalse(_json_lexical_array_budgets(raw))

    def test_lexical_array_global_exact_limit_stays_in_bounds(self):
        raw = "[" + ",".join("[1,2,3]" for _ in range(16384)) + "]"
        self.assertTrue(_json_lexical_array_budgets(raw))

    def test_lexical_scanner_ignores_commas_brackets_in_quoted_strings(self):
        raw = json.dumps(["x," * 20000 + "[]{}"])
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_lexical_scanner_ignores_escaped_quotes_inside_string(self):
        raw = '["text \\"escaped,] quote", 1]'
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_lexical_empty_arrays_not_counted_as_one_item(self):
        raw = "[" + ",".join("[]" for _ in range(MAX_JSON_ARRAY_ITEMS)) + "]"
        self.assertTrue(_json_lexical_array_budgets(raw))

    def test_lexical_oversized_array_refused_before_json_decoder(self):
        from unittest.mock import patch
        raw = "[" + ",".join("0" for _ in range(MAX_JSON_ARRAY_ITEMS+1)) + "]"
        with patch.object(json, "loads",
                          side_effect=AssertionError("decoder must not run")) as decoder:
            result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        decoder.assert_not_called()

    def test_lexical_scanner_rejects_mismatched_containers(self):
        self.assertFalse(_json_lexical_array_budgets("[1,2}"))
        self.assertFalse(_json_lexical_array_budgets('{"x":[1,2}'))

    def test_lexical_array_budget_keeps_valid_non_authorizing_fixture(self):
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_lexical_object_exact_individual_member_cap_allowed(self):
        raw = "{" + ",".join('"k%d":0' % i for i in range(
            MAX_JSON_OBJECT_MEMBERS)) + "}"
        self.assertTrue(_json_lexical_object_budgets(raw))

    def test_lexical_object_one_over_member_cap_rejected(self):
        raw = "{" + ",".join('"k%d":0' % i for i in range(
            MAX_JSON_OBJECT_MEMBERS+1)) + "}"
        self.assertFalse(_json_lexical_object_budgets(raw))

    def test_lexical_object_exact_aggregate_member_cap_allowed(self):
        raw = "[" + ",".join('{"a":0}' for _ in range(
            MAX_JSON_TOTAL_OBJECT_MEMBERS)) + "]"
        self.assertTrue(_json_lexical_object_budgets(raw))

    def test_lexical_many_small_objects_over_aggregate_cap_rejected(self):
        groups = [
            "[" + ",".join('{"a":0}' for _ in range(11000)) + "]"
            for _ in range(3)]
        raw = "[" + ",".join(groups) + "]"
        self.assertLess(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertFalse(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_lexical_scanner_ignores_braces_commas_in_string_values(self):
        raw = '{"message":"' + ",{}[]"*10000 + '"}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_lexical_scanner_ignores_escaped_quote_and_comma(self):
        raw = '{"name":"embedded \\"quoted,\\": data"}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_lexical_empty_objects_have_zero_members(self):
        raw = "[" + ",".join("{}" for _ in range(MAX_JSON_ARRAY_ITEMS)) + "]"
        self.assertTrue(_json_lexical_object_budgets(raw))

    def test_lexical_large_object_never_invokes_json_decoder(self):
        from unittest.mock import patch
        raw = "{" + ",".join('"k%d":0' % i for i in range(
            MAX_JSON_OBJECT_MEMBERS+1)) + "}"
        with patch.object(json, "loads",
                          side_effect=AssertionError("decoder forbidden")) as p:
            result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        p.assert_not_called()

    def test_lexical_object_budget_does_not_echo_private_fields(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        raw = '{"private_canary":0,' + ",".join(
            '"k%d":0' % i for i in range(MAX_JSON_OBJECT_MEMBERS)) + "}"
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), output)
        self.assertEqual(status, 2)
        record = json.loads(output.getvalue())
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("private_canary", output.getvalue())

    def test_lexical_object_budget_preserves_clean_source_consistency(self):
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_nested_mutation_of_pr_does_not_change_original_evidence(self):
        from unittest.mock import patch
        original = copy.deepcopy(self.envelope)
        def mutate(**values):
            values["pr"]["private_canary"] = "synthetic"
            raise RuntimeError("synthetic nested failure")
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=mutate):
            self.assert_fails("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")
        self.assertEqual(self.envelope, original)

    def test_nested_mutation_of_runs_does_not_change_original_evidence(self):
        from unittest.mock import patch
        original = copy.deepcopy(self.envelope)
        def mutate(**values):
            values["runs"].append({"private_canary": "synthetic"})
            raise RuntimeError("synthetic nested failure")
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=mutate):
            self.assert_fails("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")
        self.assertEqual(self.envelope, original)

    def test_nested_mutation_of_job_map_does_not_change_original_evidence(self):
        from unittest.mock import patch
        original = copy.deepcopy(self.envelope)
        def mutate(**values):
            values["jobs_by_run"][99999] = ["synthetic"]
            raise RuntimeError("synthetic nested failure")
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=mutate):
            self.assert_fails("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")
        self.assertEqual(self.envelope, original)

    def test_nested_mutation_of_full_trees_does_not_modify_source(self):
        from unittest.mock import patch
        original = copy.deepcopy(self.envelope)
        def mutate(**values):
            values["full_tree_snapshots"].clear()
            raise RuntimeError("synthetic nested failure")
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=mutate):
            self.assert_fails("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")
        self.assertEqual(self.envelope, original)

    def test_nested_mutation_of_source_byte_map_does_not_modify_source(self):
        from unittest.mock import patch
        original = copy.deepcopy(self.envelope)
        def mutate(**values):
            values["changed_bytes"]["docs/synthetic-private"] = b"secret"
            raise RuntimeError("synthetic nested failure")
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=mutate):
            self.assert_fails("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")
        self.assertEqual(self.envelope, original)

    def test_nested_mutation_followed_by_clean_review_still_consistent(self):
        from unittest.mock import patch
        def mutate(**values):
            values["pr"]["private_canary"] = True
            raise RuntimeError("synthetic")
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=mutate):
            self.assert_fails("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_nested_copy_failure_is_sanitized_without_composite_invocation(self):
        from unittest.mock import patch
        with patch.object(copy, "deepcopy",
                          side_effect=RuntimeError("private-source-canary")):
            with patch.object(composite, "review_stacked_draft_evidence") as downstream:
                result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_NESTED_EVIDENCE_UNREVIEWED",))
        self.assertNotIn("private-source-canary", repr(result))
        downstream.assert_not_called()

    def test_mutated_nested_result_cannot_grant_protected_authority(self):
        from unittest.mock import patch
        original_pr = copy.deepcopy(self.envelope["pr"])
        def mutate(**values):
            values["pr"]["can_authorize_annual_run"] = True
            return {"source_consistency": True, "diagnostics": (),
                    "independent_original_os_proof": True,
                    "exclusive_server_dispatch_gate_proven": True,
                    "can_authorize_annual_run": True}
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=mutate):
            result = self.verdict()
        self.assertFalse(result["can_authorize_annual_run"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertEqual(self.envelope["pr"], original_pr)

    def test_nested_source_isolation_preserves_clean_consistency_only(self):
        original = copy.deepcopy(self.envelope)
        result = self.verdict()
        self.assertEqual(self.envelope, original)
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_raw_ci_byte_error_precedence_ignores_map_order(self):
        too_big = "🚀" * 500001
        other = "🚀" * 400000
        pairs = [("9101", other), ("9102", other),
                 ("9103", other), ("9104", too_big)]
        for ordering in (pairs, list(reversed(pairs))):
            with self.subTest(ordering=[p[0] for p in ordering]):
                self.envelope["raw_ci_runner_logs"] = dict(ordering)
                self.assert_fails("BUNDLE_RAW_LOG_UTF8_OVERSIZE")

    def test_raw_ci_multiple_valid_per_log_but_aggregate_over(self):
        self.envelope["raw_ci_runner_logs"] = {
            "9101": "🚀"*400000, "9102": "🚀"*400000,
            "9103": "🚀"*400000}
        self.assert_fails("BUNDLE_TOTAL_RAW_LOG_UTF8_OVERSIZE")

    def test_raw_ci_aggregate_utf8_diagnostic_stable_under_reverse(self):
        pairs = [("9101", "🚀"*400000), ("9102", "🚀"*400000),
                 ("9103", "🚀"*400000)]
        for ordering in (pairs, list(reversed(pairs))):
            self.envelope["raw_ci_runner_logs"] = dict(ordering)
            result = self.verdict()
            self.assertEqual(result["diagnostics"],
                             ("BUNDLE_TOTAL_RAW_LOG_UTF8_OVERSIZE",))

    def test_raw_ci_individual_utf8_error_precedes_invalid_run_id(self):
        self.envelope["raw_ci_runner_logs"] = {
            "not-run-id": "🚀"*500001}
        self.assert_fails("BUNDLE_RAW_LOG_UTF8_OVERSIZE")

    def test_raw_ci_byte_guard_zero_length_strings_are_not_oversize(self):
        self.envelope["raw_ci_runner_logs"] = {"9101": ""}
        result = self.verdict()
        self.assertNotIn("BUNDLE_RAW_LOG_UTF8_OVERSIZE", result["diagnostics"])
        self.assertNotIn("BUNDLE_TOTAL_RAW_LOG_UTF8_OVERSIZE", result["diagnostics"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_raw_ci_utf8_error_never_echoes_private_log_bytes(self):
        self.envelope["raw_ci_runner_logs"] = {
            "9101": "private-canary" + "🚀"*500001}
        result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RAW_LOG_UTF8_OVERSIZE",))
        self.assertNotIn("private-canary", repr(result))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_raw_ci_utf8_error_keeps_both_authorization_gates_false(self):
        self.envelope["raw_ci_runner_logs"] = {
            "9101": "🚀"*500001}
        result = self.verdict()
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_raw_ci_only_one_utf8_per_run_error_code_in_output(self):
        self.envelope["raw_ci_runner_logs"] = {
            "9101": "🚀"*500001, "9102": "🚀"*500001}
        result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_RAW_LOG_UTF8_OVERSIZE",))

    def test_order_invariant_raw_log_guard_preserves_clean_fixture(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_lexical_scanners_ignore_large_comma_text(self):
        raw = "[" + json.dumps("value,"*10000) + "]"
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_lexical_scanners_ignore_bracket_like_object_keys(self):
        raw = json.dumps({"[[],{},:]"*3000: "synthetic"})
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_json_lexical_scanners_handle_escaped_quote_backslash(self):
        raw = json.dumps({"synthetic": 'quoted "\\"][,{}]\\" content'})
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_json_lexical_scanners_accept_many_empty_containers(self):
        raw = json.dumps({"synthetic": [{"a": [], "b": {}} for _ in range(500)]},
                         separators=(",", ":"))
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_json_lexical_scanners_reject_crossed_container_closures(self):
        for raw in ('{"a":[1,2}', '[{"a":1]', '{[}]'):
            with self.subTest(raw=raw):
                self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                                 ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_decoded_duplicate_keys_hidden_by_escape_fail_closed(self):
        raw = '{"a":1,"\\u0061":2}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_lexical_scanners_ignore_escaped_punctuation_text(self):
        raw = json.dumps({"message": '\\[\\,\\} "secret" ' * 500})
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_json_lexical_scanners_accept_nested_small_arrays_objects(self):
        raw = json.dumps({"synthetic": [[{"k": i} for i in range(10)]
                                         for _ in range(10)]})
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_json_lexical_scanners_reject_malformed_closing_tokens(self):
        for raw in ('[1,2]]', '{"a":1}}', '{"x":[0,1}}'):
            with self.subTest(raw=raw):
                self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                                 ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_lexical_scanners_keep_order_independent_source_consistency(self):
        for sort_keys in (False, True):
            with self.subTest(sort_keys=sort_keys):
                raw = json.dumps(self.envelope, sort_keys=sort_keys)
                result = review_bundle_json_text(raw)
                self.assertEqual(result["diagnostics"], ())
                self.assertTrue(result["source_consistency"])
                self.assertFalse(result["independent_original_os_proof"])
                self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
                self.assertFalse(result["can_authorize_annual_run"])

    def test_json_serialized_ascii_escape_corpus_matches_decoder(self):
        samples = ('[,]{}:"\\', 'backslash \\ quote "', '\t\n\r', '',
                   'comma,comma,comma', '[[[{{{}}}]]]')
        for sample in samples:
            with self.subTest(sample=repr(sample)):
                raw = json.dumps([sample])
                self.assertTrue(_json_lexical_array_budgets(raw))
                self.assertTrue(_json_lexical_object_budgets(raw))
                self.assertEqual(json.loads(raw), [sample])
                self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                                 ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_unicode_serializations_share_lexical_verdict(self):
        value = ["é", "🚀", "\u2028", "quotation \" and backslash \\"]
        for ensure_ascii in (True, False):
            with self.subTest(ensure_ascii=ensure_ascii):
                raw = json.dumps(value, ensure_ascii=ensure_ascii)
                self.assertTrue(_json_lexical_array_budgets(raw))
                self.assertTrue(_json_lexical_object_budgets(raw))
                self.assertEqual(json.loads(raw), value)
                self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                                 ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_separator_and_indent_modes_keep_structural_counts(self):
        value = [{"a": "[,:}]", "b": ['"\\', "two,three"]},
                 {"c": {"d": "escaped: \\n and \\t"}}]
        for opts in ({"separators": (",", ":")}, {"indent": 2},
                     {"sort_keys": True}, {"ensure_ascii": False}):
            with self.subTest(options=opts):
                raw = json.dumps(value, **opts)
                self.assertTrue(_json_lexical_array_budgets(raw))
                self.assertTrue(_json_lexical_object_budgets(raw))
                self.assertEqual(json.loads(raw), value)
                self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                                 ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_scanners_ignore_even_and_odd_escaped_backslashes(self):
        for count in range(9):
            with self.subTest(count=count):
                sample = "\\" * count + '"[,]{}'
                raw = json.dumps({"sample": sample})
                self.assertTrue(_json_lexical_array_budgets(raw))
                self.assertTrue(_json_lexical_object_budgets(raw))
                self.assertEqual(json.loads(raw)["sample"], sample)
                self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                                 ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_json_punctuation_dense_nested_strings_stay_in_budget(self):
        value = [["[]{}:,\"\\"] * 3 for _ in range(1000)]
        raw = json.dumps(value, separators=(",", ":"))
        self.assertLess(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_scanners_do_not_accept_nonstandard_decoder_constants(self):
        for raw in ('{"payload":NaN}', '{"payload":Infinity}',
                    '{"payload":-Infinity}'):
            with self.subTest(raw=raw):
                self.assertTrue(_json_lexical_array_budgets(raw))
                self.assertTrue(_json_lexical_object_budgets(raw))
                self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                                 ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_trailing_escaped_quote_or_backslash_fails_closed(self):
        for raw in ('{"payload":"unclosed', '{"payload":"unclosed\\',
                    '{"payload":"closing\\"}'):
            with self.subTest(raw=raw):
                result = review_bundle_json_text(raw)
                self.assertEqual(result["diagnostics"],
                                 ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
                self.assertFalse(result["can_authorize_annual_run"])

    def test_json_serialized_source_fixture_only_proves_consistency(self):
        for opts in ({"sort_keys": True}, {"separators": (",", ":")},
                     {"indent": 2}):
            with self.subTest(options=opts):
                raw = json.dumps(self.envelope, **opts)
                self.assertTrue(_json_lexical_array_budgets(raw))
                self.assertTrue(_json_lexical_object_budgets(raw))
                result = review_bundle_json_text(raw)
                self.assertEqual(result["diagnostics"], ())
                self.assertTrue(result["source_consistency"])
                self.assertFalse(result["independent_original_os_proof"])
                self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
                self.assertFalse(result["can_authorize_annual_run"])

    def test_json_decoded_ascii_escape_alias_is_duplicate_key(self):
        raw = r'{"\u0061":1,"a":2}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_decoded_slash_escape_alias_is_duplicate_key(self):
        raw = r'{"\/":1,"/":2}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_decoded_backslash_escape_alias_is_duplicate_key(self):
        raw = r'{"\\":1,"\u005c":2}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_decoded_surrogate_pair_alias_is_duplicate_key(self):
        raw = r'{"😀":1,"\ud83d\ude00":2}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_decoded_accent_escape_alias_is_duplicate_key(self):
        raw = r'{"é":1,"\u00e9":2}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_nested_alias_duplicate_fails_before_inventory(self):
        raw = r'{"synthetic":{"k":1,"\u006b":2}}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_case_distinct_keys_are_not_false_duplicates(self):
        raw = r'{"A":1,"a":2}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_json_equal_keys_in_distinct_objects_are_not_duplicates(self):
        raw = r'[{"a":1},{"a":2}]'
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_cli_decoded_private_duplicate_key_is_not_echoed(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        raw = r'{"private-canary":1,"\u0070rivate-canary":2}'
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        self.assertEqual(status, 2)
        record = json.loads(out.getvalue())
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("private-canary", out.getvalue())
        self.assertFalse(record["independent_original_os_proof"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_json_global_object_overlimit_skips_decoder_allocation(self):
        from unittest.mock import patch
        raw = ("[" + '[{"a":1},{"a":1},{"a":1}],' +
               ",".join('[{"a":1},{"a":1}]' for _ in range(
                   MAX_JSON_ARRAY_ITEMS-1)) + "]")
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertFalse(_json_lexical_object_budgets(raw))
        with patch.object(json, "loads",
                          side_effect=AssertionError("decoder must not run")) as decode:
            result = review_bundle_json_text(raw)
        decode.assert_not_called()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_global_array_overlimit_skips_decoder_allocation(self):
        from unittest.mock import patch
        raw = "[" + ",".join("[0,0,0,0]" for _ in range(
            MAX_JSON_ARRAY_ITEMS)) + "]"
        self.assertFalse(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        with patch.object(json, "loads",
                          side_effect=AssertionError("decoder must not run")) as decode:
            result = review_bundle_json_text(raw)
        decode.assert_not_called()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_exact_global_object_budget_invokes_decoder_once(self):
        from unittest.mock import patch
        raw = "[" + ",".join('[{"a":1},{"a":1}]' for _ in range(
            MAX_JSON_ARRAY_ITEMS)) + "]"
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        with patch.object(json, "loads", wraps=json.loads) as decode:
            result = review_bundle_json_text(raw)
        decode.assert_called_once()
        self.assertEqual(result["diagnostics"], ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_exact_global_array_budget_invokes_decoder_once(self):
        from unittest.mock import patch
        raw = "[" + ",".join("[0,0,0]" for _ in range(
            MAX_JSON_ARRAY_ITEMS)) + "]"
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        with patch.object(json, "loads", wraps=json.loads) as decode:
            result = review_bundle_json_text(raw)
        decode.assert_called_once()
        self.assertEqual(result["diagnostics"], ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_unbalanced_container_fails_without_decoder(self):
        from unittest.mock import patch
        raw = '{"a":[1,2}'
        self.assertFalse(_json_lexical_array_budgets(raw))
        with patch.object(json, "loads",
                          side_effect=AssertionError("decoder must not run")) as decode:
            result = review_bundle_json_text(raw)
        decode.assert_not_called()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_utf8_overlimit_skips_decoder_even_below_char_cap(self):
        from unittest.mock import patch
        raw = json.dumps(["🚀"*500000], ensure_ascii=False)
        self.assertLess(len(raw), MAX_TEXT_CHARS)
        self.assertGreater(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        with patch.object(json, "loads",
                          side_effect=AssertionError("decoder must not run")) as decode:
            result = review_bundle_json_text(raw)
        decode.assert_not_called()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))

    def test_json_char_overlimit_skips_decoder(self):
        from unittest.mock import patch
        raw = " " * (MAX_TEXT_CHARS + 1)
        with patch.object(json, "loads",
                          side_effect=AssertionError("decoder must not run")) as decode:
            result = review_bundle_json_text(raw)
        decode.assert_not_called()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))

    def test_json_lexically_bounded_invalid_separator_defers_to_decoder(self):
        from unittest.mock import patch
        raw = '{"synthetic":[1,]}'
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        with patch.object(json, "loads", wraps=json.loads) as decode:
            result = review_bundle_json_text(raw)
        decode.assert_called_once()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_fault_precedence_char_cap_before_invalid_container(self):
        raw = " " * (MAX_TEXT_CHARS + 1) + '{"unclosed":['
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_fault_precedence_utf8_cap_before_duplicate_key(self):
        raw = '{"x":"'+ "🚀"*500001 + '","x":2}'
        self.assertLess(len(raw), MAX_TEXT_CHARS)
        self.assertGreater(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_fault_precedence_depth_guard_before_duplicate_key(self):
        raw = "["*(MAX_JSON_NESTING+1) + '{"a":1,"a":2}' + "]"*(MAX_JSON_NESTING+1)
        self.assertLess(len(raw), MAX_TEXT_CHARS)
        self.assertFalse(_json_nesting_within_limit(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_fault_precedence_aggregate_array_before_key_inventory(self):
        raw = '{"bad":[' + ",".join("[0,0,0,0]" for _ in range(
            MAX_JSON_ARRAY_ITEMS)) + "]}"
        self.assertFalse(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_fault_precedence_object_members_before_duplicate_hook(self):
        raw = "{" + ",".join('"k%d":0'%i for i in range(
            MAX_JSON_OBJECT_MEMBERS)) + ',"k0":1}'
        self.assertFalse(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_fault_precedence_duplicate_key_before_surrogate_walk(self):
        raw = r'{"a":"\ud800","a":2}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_fault_precedence_unicode_walk_before_envelope_inventory(self):
        raw = r'{"unreviewed":"\ud800"}'
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_UNICODE_UNREVIEWED",))

    def test_json_fault_precedence_missing_envelope_keys_after_valid_parse(self):
        raw = '{"unexpected":"synthetic"}'
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_json_multifault_rejection_never_invokes_nested_source_review(self):
        from unittest.mock import patch
        raw = r'{"bad":{"a":1,"\u0061":2}}'
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=AssertionError("nested review forbidden")) as nested:
            result = review_bundle_json_text(raw)
        nested.assert_not_called()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_unicode_accent_escape_inflation_hits_document_cap(self):
        value = ["é" * 400000]
        escaped = json.dumps(value, ensure_ascii=True)
        literal = json.dumps(value, ensure_ascii=False)
        self.assertGreater(len(escaped.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        self.assertLess(len(literal.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        self.assertEqual(json.loads(escaped), json.loads(literal))
        self.assertEqual(review_bundle_json_text(escaped)["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))
        self.assertEqual(review_bundle_json_text(literal)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_unicode_emoji_escape_inflation_hits_document_cap(self):
        value = ["🚀" * 170000]
        escaped = json.dumps(value, ensure_ascii=True)
        literal = json.dumps(value, ensure_ascii=False)
        self.assertGreater(len(escaped), MAX_TEXT_CHARS)
        self.assertLess(len(literal.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        self.assertEqual(review_bundle_json_text(escaped)["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))
        self.assertEqual(review_bundle_json_text(literal)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_literal_unicode_exact_utf8_document_ceiling(self):
        raw = json.dumps(["é"*999998], ensure_ascii=False)
        self.assertEqual(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        self.assertLess(len(raw), MAX_TEXT_CHARS)
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"], ("BUNDLE_SHAPE_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_literal_unicode_one_utf8_scalar_above_ceiling(self):
        raw = json.dumps(["é"*999999], ensure_ascii=False)
        self.assertEqual(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES+2)
        self.assertLess(len(raw), MAX_TEXT_CHARS)
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))

    def test_json_control_escape_expansion_is_counted_before_decode(self):
        raw = json.dumps(["\x00" * 333334])
        self.assertGreater(len(raw), MAX_TEXT_CHARS)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))

    def test_json_small_control_escape_payload_remains_grammar_valid(self):
        raw = json.dumps(["\x00" * 1000])
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_escaped_lone_surrogate_uses_unicode_diagnostic(self):
        raw = r'["\ud800"]'
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_UNICODE_UNREVIEWED",))

    def test_json_unescaped_lone_surrogate_fails_utf8_preflight(self):
        raw = json.dumps(["\ud800"], ensure_ascii=False)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_UNICODE_UNREVIEWED",))

    def test_json_stdin_escaped_unicode_oversize_never_echoes_canary(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        canary = "private-unicode-overlimit-canary"
        raw = json.dumps([canary + "é"*400000], ensure_ascii=True)
        self.assertGreater(len(raw), MAX_TEXT_CHARS)
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), output)
        self.assertEqual(status, 2)
        record = json.loads(output.getvalue())
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_JSON_TEXT_UNREVIEWED"])
        self.assertNotIn(canary, output.getvalue())
        self.assertFalse(record["independent_original_os_proof"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(record["can_authorize_annual_run"])

    def assert_lexically_bounded_invalid_json_uses_decoder(self, raw):
        from unittest.mock import patch
        self.assertLess(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        self.assertTrue(_json_nesting_within_limit(raw))
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        with patch.object(json, "loads", wraps=json.loads) as decoder, \
             patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=AssertionError("nested review forbidden")) as nested:
            verdict = review_bundle_json_text(raw)
        decoder.assert_called_once()
        nested.assert_not_called()
        self.assertEqual(verdict["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertFalse(verdict["independent_original_os_proof"])
        self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_json_grammar_missing_object_colon_rejected_after_lexing(self):
        self.assert_lexically_bounded_invalid_json_uses_decoder('{"a" 1}')

    def test_json_grammar_missing_object_comma_rejected_after_lexing(self):
        self.assert_lexically_bounded_invalid_json_uses_decoder(
            '{"a":1 "b":2}')

    def test_json_grammar_trailing_object_comma_rejected_after_lexing(self):
        self.assert_lexically_bounded_invalid_json_uses_decoder('{"a":1,}')

    def test_json_grammar_trailing_array_comma_rejected_after_lexing(self):
        self.assert_lexically_bounded_invalid_json_uses_decoder('[1,]')

    def test_json_grammar_single_quote_key_rejected_after_lexing(self):
        self.assert_lexically_bounded_invalid_json_uses_decoder("{'a':1}")

    def test_json_grammar_javascript_comment_rejected_after_lexing(self):
        self.assert_lexically_bounded_invalid_json_uses_decoder(
            '{"a":1/* synthetic comment */}')

    def test_json_grammar_invalid_number_tokens_rejected_after_lexing(self):
        for raw in ('{"a":01}', '{"a":+1}', '{"a":.5}'):
            with self.subTest(raw=raw):
                self.assert_lexically_bounded_invalid_json_uses_decoder(raw)

    def test_json_grammar_missing_nested_array_separator_rejected_after_lexing(self):
        self.assert_lexically_bounded_invalid_json_uses_decoder(
            '{"a":[1 2]}')

    def test_json_exact_text_cap_with_trailing_space_reaches_shape(self):
        raw = "null" + " "*(MAX_TEXT_CHARS-4)
        self.assertEqual(len(raw), MAX_TEXT_CHARS)
        self.assertEqual(len(raw.encode("utf-8")), MAX_TEXT_UTF8_BYTES)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_one_trailing_space_over_text_cap_refused(self):
        raw = "null" + " "*(MAX_TEXT_CHARS-3)
        self.assertEqual(len(raw), MAX_TEXT_CHARS+1)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))

    def test_json_semantic_same_pretty_layout_can_cross_character_cap(self):
        value = ["a"*(MAX_TEXT_CHARS-6)]
        compact = json.dumps(value, separators=(",", ":"))
        pretty = json.dumps(value, indent=2)
        self.assertLessEqual(len(compact), MAX_TEXT_CHARS)
        self.assertGreater(len(pretty), MAX_TEXT_CHARS)
        self.assertEqual(json.loads(compact), json.loads(pretty))
        self.assertEqual(review_bundle_json_text(compact)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))
        self.assertEqual(review_bundle_json_text(pretty)["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))

    def test_json_valid_ascii_whitespace_around_document_is_allowed(self):
        raw = " \t\r\n" + json.dumps(["synthetic"]) + "\r\n\t "
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_SHAPE_UNREVIEWED",))

    def test_json_vertical_tab_not_accepted_as_json_whitespace(self):
        raw = "\vnull"
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_nbsp_not_accepted_as_json_whitespace(self):
        raw = "\u00a0null"
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_leading_bom_is_not_a_valid_prefix(self):
        raw = "\ufeffnull"
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_nul_outside_quoted_value_is_grammar_error(self):
        raw = "null\x00"
        self.assertTrue(_json_lexical_array_budgets(raw))
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_json_ascii_whitespace_clean_bundle_stays_source_only(self):
        raw = " \n\t" + json.dumps(self.envelope, sort_keys=True) + "\r\n "
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def _json_document_with_duplicate_map_member(self, category, escape_alias=False):
        raw = json.dumps(self.envelope, separators=(",", ":"))
        existing = json.dumps(self.envelope[category], separators=(",", ":"))
        key = next(iter(self.envelope[category]))
        encoded_key = (('"\\u%04x%s"' % (ord(key[0]), key[1:]))
                       if escape_alias else json.dumps(key))
        duplicate = (existing[:-1] + "," + encoded_key + ":" +
                     json.dumps(self.envelope[category][key],
                                separators=(",", ":")) + "}")
        needle = json.dumps(category) + ":" + existing
        self.assertEqual(raw.count(needle), 1)
        return raw.replace(needle, json.dumps(category) + ":" + duplicate, 1)

    def test_valid_envelope_duplicate_schema_same_value_rejected(self):
        raw = json.dumps(self.envelope, separators=(",", ":"))
        raw = raw[:-1] + ',"schema":' + json.dumps(ENVELOPE_SCHEMA) + "}"
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_valid_envelope_duplicate_schema_escaped_key_rejected(self):
        raw = json.dumps(self.envelope, separators=(",", ":"))
        raw = raw[:-1] + ',"\\u0073chema":' + json.dumps(ENVELOPE_SCHEMA) + "}"
        self.assertTrue(_json_lexical_object_budgets(raw))
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_valid_envelope_duplicate_runs_cannot_replace_provenance(self):
        raw = json.dumps(self.envelope, separators=(",", ":"))
        raw = raw[:-1] + ',"runs":[]}'
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_valid_envelope_duplicate_pr_inner_key_rejected(self):
        raw = self._json_document_with_duplicate_map_member("pr")
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_valid_envelope_duplicate_pr_escaped_inner_key_rejected(self):
        raw = self._json_document_with_duplicate_map_member(
            "pr", escape_alias=True)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_valid_envelope_duplicate_source_path_rejected(self):
        raw = self._json_document_with_duplicate_map_member("changed_bytes_b64")
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_valid_envelope_duplicate_source_path_escaped_key_rejected(self):
        raw = self._json_document_with_duplicate_map_member(
            "changed_bytes_b64", escape_alias=True)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_valid_envelope_duplicate_raw_ci_run_key_rejected(self):
        raw = self._json_document_with_duplicate_map_member(
            "raw_ci_runner_logs")
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))

    def test_valid_envelope_cross_map_same_run_key_is_not_duplicate(self):
        raw = json.dumps(self.envelope, separators=(",", ":"), sort_keys=True)
        result = review_bundle_json_text(raw)
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def _assert_inmemory_and_json_bundle_parity(self, mutated, diagnostic):
        direct = review_bundle_envelope(mutated)
        serialized = json.dumps(mutated, ensure_ascii=True)
        parsed = review_bundle_json_text(serialized)
        self.assertEqual(direct, parsed)
        self.assertEqual(direct["diagnostics"], diagnostic)
        self.assertEqual(direct["source_consistency"], not diagnostic)
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def test_inmemory_json_parity_rejects_unreviewed_schema(self):
        altered = copy.deepcopy(self.envelope)
        altered["schema"] = "synthetic-unreviewed-schema"
        self._assert_inmemory_and_json_bundle_parity(
            altered, ("BUNDLE_SCHEMA_UNREVIEWED",))

    def test_inmemory_json_parity_rejects_missing_required_category(self):
        altered = copy.deepcopy(self.envelope)
        del altered["nodes"]
        self._assert_inmemory_and_json_bundle_parity(
            altered, ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_inmemory_json_parity_rejects_extra_authorization_field(self):
        altered = copy.deepcopy(self.envelope)
        altered["can_authorize_annual_run"] = True
        self._assert_inmemory_and_json_bundle_parity(
            altered, ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_inmemory_json_parity_rejects_nonlist_runs(self):
        altered = copy.deepcopy(self.envelope)
        altered["runs"] = {}
        self._assert_inmemory_and_json_bundle_parity(
            altered, ("BUNDLE_CATEGORY_TYPE_UNREVIEWED",))

    def test_inmemory_json_parity_rejects_nonmap_logs(self):
        altered = copy.deepcopy(self.envelope)
        altered["raw_ci_runner_logs"] = []
        self._assert_inmemory_and_json_bundle_parity(
            altered, ("BUNDLE_CATEGORY_TYPE_UNREVIEWED",))

    def test_inmemory_json_parity_rejects_invalid_run_map_key(self):
        altered = copy.deepcopy(self.envelope)
        key, value = altered["jobs_by_run"].popitem()
        altered["jobs_by_run"]["0"] = value
        self._assert_inmemory_and_json_bundle_parity(
            altered, ("BUNDLE_RUN_KEY_UNREVIEWED",))

    def test_inmemory_json_parity_rejects_invalid_base64_leaf(self):
        altered = copy.deepcopy(self.envelope)
        key = next(iter(altered["changed_bytes_b64"]))
        altered["changed_bytes_b64"][key] = "synthetic%%%%"
        self._assert_inmemory_and_json_bundle_parity(
            altered, ("BUNDLE_SOURCE_B64_UNREVIEWED",))

    def test_inmemory_json_parity_rejects_absolute_source_path(self):
        altered = copy.deepcopy(self.envelope)
        key, value = altered["changed_bytes_b64"].popitem()
        altered["changed_bytes_b64"]["/private/synthetic.py"] = value
        self._assert_inmemory_and_json_bundle_parity(
            altered, ("BUNDLE_SOURCE_PATH_UNREVIEWED",))

    def test_inmemory_json_parity_preserves_clean_source_only(self):
        altered = copy.deepcopy(self.envelope)
        altered = dict(reversed(list(altered.items())))
        self._assert_inmemory_and_json_bundle_parity(altered, ())

    def _refingerprint_portable_synthetic_ci_log(self, run_id):
        import hashlib
        raw = self.envelope["raw_ci_runner_logs"][run_id].encode("utf-8")
        receipt = self.envelope["raw_ci_log_receipts"][run_id]
        receipt["byte_count"] = len(raw)
        receipt["text_sha256"] = hashlib.sha256(raw).hexdigest()

    def _assert_refingerprinted_portable_log_rejected(self, expected=None):
        direct = self.verdict()
        parsed = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(direct, parsed)
        self.assertFalse(direct["source_consistency"])
        self.assertTrue(direct["diagnostics"])
        if expected is not None:
            self.assertIn(expected, direct["diagnostics"])
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def test_portable_refingerprint_wrong_historical_checkout_still_rejected(self):
        text = self.envelope["raw_ci_runner_logs"]["8001"]
        self.envelope["raw_ci_runner_logs"]["8001"] = (
            text.replace("f"*40, "e"*40)
                .replace("fffffff Merge ", "eeeeeee Merge "))
        self._refingerprint_portable_synthetic_ci_log("8001")
        self._assert_refingerprinted_portable_log_rejected(
            "RAW_CI_RUNNER_LOG_METADATA_MISMATCH")

    def test_portable_refingerprint_wrong_phase3_pr_ref_still_rejected(self):
        text = self.envelope["raw_ci_runner_logs"]["8000"]
        self.envelope["raw_ci_runner_logs"]["8000"] = text.replace(
            "/1649/merge", "/9999/merge")
        self._refingerprint_portable_synthetic_ci_log("8000")
        self._assert_refingerprinted_portable_log_rejected(
            "RUNNER_LOG_PR_REF_MISMATCH")

    def test_portable_refingerprint_changed_phase3_index_still_rejected(self):
        text = self.envelope["raw_ci_runner_logs"]["8000"]
        self.assertIn('"trade_count":1', text)
        self.envelope["raw_ci_runner_logs"]["8000"] = text.replace(
            '"trade_count":1', '"trade_count":99', 1)
        self._refingerprint_portable_synthetic_ci_log("8000")
        self._assert_refingerprinted_portable_log_rejected(
            "PHASE3_RAW_INDEX_VS_SUPPLIED_EVIDENCE_MISMATCH")

    def test_portable_refingerprint_changed_upload_id_still_rejected(self):
        text = self.envelope["raw_ci_runner_logs"]["8000"]
        self.envelope["raw_ci_runner_logs"]["8000"] = text.replace(
            "7777", "8888")
        self._refingerprint_portable_synthetic_ci_log("8000")
        self._assert_refingerprinted_portable_log_rejected(
            "PHASE3_RAW_UPLOAD_VS_SUPPLIED_EVIDENCE_MISMATCH")

    def test_portable_refingerprint_receipt_cannot_change_job_identity(self):
        self._refingerprint_portable_synthetic_ci_log("8001")
        self.envelope["raw_ci_log_receipts"]["8001"]["job_id"] = (
            self.envelope["raw_ci_log_receipts"]["8000"]["job_id"])
        # The portable result allowlist intentionally declines this nested
        # receipt diagnostic and emits a generic, nonauthorizing refusal.
        self._assert_refingerprinted_portable_log_rejected(
            "BUNDLE_RESULT_SHAPE_UNREVIEWED")

    def test_portable_refingerprint_private_raw_log_never_echoes(self):
        text = self.envelope["raw_ci_runner_logs"]["8001"]
        self.envelope["raw_ci_runner_logs"]["8001"] = (
            text + "\nprivate-synthetic-canary")
        self._refingerprint_portable_synthetic_ci_log("8001")
        result = self.verdict()
        # An additional non-stage log line is not a checkout or artifact
        # identity mutation. Source consistency is not provider authentication.
        self.assertTrue(result["source_consistency"], result["diagnostics"])
        self.assertEqual(result["diagnostics"], ())
        self.assertNotIn("private-synthetic-canary", repr(result))
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_portable_refingerprint_swapped_runner_logs_fail_closed(self):
        logs = self.envelope["raw_ci_runner_logs"]
        logs["8000"], logs["8001"] = logs["8001"], logs["8000"]
        for key in ("8000", "8001"):
            self._refingerprint_portable_synthetic_ci_log(key)
        self._assert_refingerprinted_portable_log_rejected()

    def test_portable_refingerprint_stdin_result_never_echoes_canary(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.envelope["raw_ci_runner_logs"]["8001"] += (
            "\nprivate-stdin-canary")
        self._refingerprint_portable_synthetic_ci_log("8001")
        out = io.StringIO()
        status = cli.run_stdin_review(
            io.StringIO(json.dumps(self.envelope)), out)
        record = json.loads(out.getvalue())
        # A generic log line does not alter mandatory evidence stages.
        # CLI exit zero here is only a source-consistency signal.
        self.assertEqual(status, 0)
        self.assertTrue(record["source_consistency"])
        self.assertEqual(record["diagnostics"], [])
        self.assertNotIn("private-stdin-canary", out.getvalue())
        self.assertFalse(record["independent_original_os_proof"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_portable_unchanged_receipt_refresh_only_proves_source_consistency(self):
        for run_id in ("8000", "8001"):
            before = dict(self.envelope["raw_ci_log_receipts"][run_id])
            self._refingerprint_portable_synthetic_ci_log(run_id)
            self.assertEqual(self.envelope["raw_ci_log_receipts"][run_id],
                             before)
        result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def _assert_portable_order_invariance_with_json(self, expect_clean=False):
        original = self.verdict()
        baseline_json = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(original, baseline_json)
        for key in ("raw_ci_runner_logs", "raw_ci_log_receipts",
                    "jobs_by_run", "checkout_by_run", "changed_bytes_b64",
                    "ci_workflow_bytes_b64"):
            value = self.envelope[key]
            self.envelope[key] = dict(reversed(list(value.items())))
        self.envelope = dict(reversed(list(self.envelope.items())))
        reordered = self.verdict()
        decoded = review_bundle_json_text(
            json.dumps(self.envelope, sort_keys=True))
        self.assertEqual(original, reordered)
        self.assertEqual(reordered, decoded)
        self.assertEqual(original["source_consistency"], expect_clean)
        self.assertFalse(decoded["independent_original_os_proof"])
        self.assertFalse(decoded["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(decoded["can_authorize_annual_run"])

    def test_portable_map_order_clean_evidence_stays_source_only(self):
        self._assert_portable_order_invariance_with_json(expect_clean=True)

    def test_portable_map_order_refingerprinted_wrong_merge_is_stable(self):
        raw = self.envelope["raw_ci_runner_logs"]["8001"]
        self.envelope["raw_ci_runner_logs"]["8001"] = (
            raw.replace("f"*40, "e"*40)
               .replace("fffffff Merge ", "eeeeeee Merge "))
        self._refingerprint_portable_synthetic_ci_log("8001")
        self._assert_portable_order_invariance_with_json()

    def test_portable_map_order_refingerprinted_phase3_upload_is_stable(self):
        raw = self.envelope["raw_ci_runner_logs"]["8000"]
        self.envelope["raw_ci_runner_logs"]["8000"] = raw.replace(
            "7777", "8888")
        self._refingerprint_portable_synthetic_ci_log("8000")
        self._assert_portable_order_invariance_with_json()

    def test_portable_map_order_changed_pr_file_count_is_stable(self):
        self.envelope["pr"]["changed_files"] = 3
        self._assert_portable_order_invariance_with_json()

    def test_portable_map_order_invalid_run_key_precedence_is_stable(self):
        self.envelope["jobs_by_run"]["0"] = {}
        self._assert_portable_order_invariance_with_json()

    def test_portable_map_order_changed_receipt_job_binding_is_stable(self):
        self.envelope["raw_ci_log_receipts"]["8001"]["job_id"] = (
            self.envelope["raw_ci_log_receipts"]["8000"]["job_id"])
        self._assert_portable_order_invariance_with_json()

    def test_portable_map_order_invalid_source_base64_is_stable(self):
        key = next(iter(self.envelope["changed_bytes_b64"]))
        self.envelope["changed_bytes_b64"][key] = "not-base64%"
        self._assert_portable_order_invariance_with_json()

    def test_portable_map_order_extra_annual_authority_stays_rejected(self):
        self.envelope["can_authorize_annual_run"] = True
        self._assert_portable_order_invariance_with_json()

    def _assert_untrusted_nested_authority_claim_not_promoted(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        raw = json.dumps(self.envelope, sort_keys=True)
        direct = self.verdict()
        parsed = review_bundle_json_text(raw)
        self.assertEqual(direct, parsed)
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), output)
        record = json.loads(output.getvalue())
        self.assertEqual(status, 0 if parsed["source_consistency"] else 2)
        self.assertEqual(set(record), VERDICT_FIELDS)
        self.assertEqual(record["diagnostics"], list(parsed["diagnostics"]))
        self.assertEqual(record["source_consistency"],
                         parsed["source_consistency"])
        self.assertNotIn("private-authority-canary", output.getvalue())
        self.assertFalse(parsed["independent_original_os_proof"])
        self.assertFalse(parsed["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(parsed["can_authorize_annual_run"])
        self.assertFalse(record["independent_original_os_proof"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_untrusted_authority_top_level_claim_not_promoted(self):
        self.envelope["can_authorize_annual_run"] = True
        self._assert_untrusted_nested_authority_claim_not_promoted()

    def test_untrusted_authority_pr_metadata_claim_not_promoted(self):
        self.envelope["pr"]["can_authorize_annual_run"] = True
        self._assert_untrusted_nested_authority_claim_not_promoted()

    def test_untrusted_authority_run_metadata_claim_not_promoted(self):
        self.envelope["runs"][0]["can_authorize_annual_run"] = True
        self._assert_untrusted_nested_authority_claim_not_promoted()

    def test_untrusted_authority_ci_job_claim_not_promoted(self):
        self.envelope["jobs_by_run"]["8000"][0]["can_authorize_annual_run"] = True
        self._assert_untrusted_nested_authority_claim_not_promoted()

    def test_untrusted_authority_compare_claim_not_promoted(self):
        self.envelope["compare"]["can_authorize_annual_run"] = True
        self._assert_untrusted_nested_authority_claim_not_promoted()

    def test_untrusted_authority_commit_claim_not_promoted(self):
        self.envelope["commit"]["can_authorize_annual_run"] = True
        self._assert_untrusted_nested_authority_claim_not_promoted()

    def test_untrusted_authority_git_tree_claim_not_promoted(self):
        self.envelope["tree"]["can_authorize_annual_run"] = True
        self._assert_untrusted_nested_authority_claim_not_promoted()

    def test_untrusted_authority_merge_checkout_claim_not_promoted(self):
        self.envelope["merge_checkout_snapshot"]["can_authorize_annual_run"] = True
        self._assert_untrusted_nested_authority_claim_not_promoted()

    def test_untrusted_authority_phase3_index_claim_not_promoted(self):
        self.envelope["phase3_evidence_snapshot"]["index"][
            "can_authorize_annual_run"] = True
        self._assert_untrusted_nested_authority_claim_not_promoted()

    def test_untrusted_authority_log_receipt_claim_not_promoted(self):
        self.envelope["raw_ci_log_receipts"]["8001"][
            "can_authorize_annual_run"] = True
        self._assert_untrusted_nested_authority_claim_not_promoted()

    def test_untrusted_authority_private_claim_cannot_echo_from_stdin(self):
        self.envelope["pr"]["can_authorize_annual_run"] = True
        self.envelope["pr"]["private_note"] = "private-authority-canary"
        self._assert_untrusted_nested_authority_claim_not_promoted()

    def test_untrusted_authority_clean_source_only_control(self):
        self._assert_untrusted_nested_authority_claim_not_promoted()
        self.assertEqual(self.verdict()["diagnostics"], ())
        self.assertTrue(self.verdict()["source_consistency"])

    def test_portable_refingerprinted_checkout_mutation_with_benign_line_fails(self):
        text = self.envelope["raw_ci_runner_logs"]["8001"]
        self.assertIn("/1649/merge", text)
        self.envelope["raw_ci_runner_logs"]["8001"] = (
            text.replace("/1649/merge", "/9999/merge") +
            "\nprivate-stage-checkout-canary")
        self._refingerprint_portable_synthetic_ci_log("8001")
        result = self.verdict()
        self.assertFalse(result["source_consistency"])
        self.assertIn("RUNNER_LOG_PR_REF_MISMATCH", result["diagnostics"])
        self.assertNotIn("private-stage-checkout-canary", repr(result))
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_portable_stdin_rehashed_stage_mutation_not_echoed(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        text = self.envelope["raw_ci_runner_logs"]["8000"]
        self.assertIn("/1649/merge", text)
        self.envelope["raw_ci_runner_logs"]["8000"] = (
            text.replace("/1649/merge", "/9999/merge") +
            "\nprivate-stage-stdin-canary")
        self._refingerprint_portable_synthetic_ci_log("8000")
        out = io.StringIO()
        status = cli.run_stdin_review(
            io.StringIO(json.dumps(self.envelope)), out)
        record = json.loads(out.getvalue())
        self.assertEqual(status, 2)
        self.assertIn("RUNNER_LOG_PR_REF_MISMATCH", record["diagnostics"])
        self.assertNotIn("private-stage-stdin-canary", out.getvalue())
        self.assertFalse(record["independent_original_os_proof"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(record["can_authorize_annual_run"])

    def _tamper_portable_receipt_job_binding(self):
        self.envelope["raw_ci_log_receipts"]["8001"]["job_id"] = (
            self.envelope["raw_ci_log_receipts"]["8000"]["job_id"])

    def test_receipt_nested_rejection_is_not_a_portable_diagnostic_allowlist_entry(self):
        fixture = composite.CombinedSourceChecksRemainNonAuthorizing(
            "test_consistent_synthetic_bundle_passes_only_source_consistency")
        fixture.setUp()
        fixture.raw_log_receipts[8001]["job_id"] = fixture.jobs[8000][0]["id"]
        self.assertIn("tests_RECEIPT_JOB_MISMATCH",
                      fixture.verdict()["diagnostics"])
        self.assertNotIn("tests_RECEIPT_JOB_MISMATCH",
                         REVIEWED_NESTED_DIAGNOSTICS)
        self._tamper_portable_receipt_job_binding()
        self.assertEqual(self.verdict()["diagnostics"],
                         ("BUNDLE_RESULT_SHAPE_UNREVIEWED",))

    def test_receipt_unallowlisted_nested_label_fails_closed_in_json(self):
        self._tamper_portable_receipt_job_binding()
        record = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(record["diagnostics"],
                         ("BUNDLE_RESULT_SHAPE_UNREVIEWED",))
        self.assertFalse(record["source_consistency"])
        self.assertFalse(record["independent_original_os_proof"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_receipt_unallowlisted_nested_label_fails_closed_via_stdin(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self._tamper_portable_receipt_job_binding()
        out = io.StringIO()
        status = cli.run_stdin_review(
            io.StringIO(json.dumps(self.envelope)), out)
        record = json.loads(out.getvalue())
        self.assertEqual(status, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_RESULT_SHAPE_UNREVIEWED"])
        self.assertNotIn("tests_RECEIPT_JOB_MISMATCH", out.getvalue())
        self.assertEqual(set(record), VERDICT_FIELDS)
        self.assertFalse(record["can_authorize_annual_run"])

    def test_receipt_unallowlisted_diagnostic_stable_with_reordered_maps(self):
        self._tamper_portable_receipt_job_binding()
        prior = self.verdict()
        self.envelope["raw_ci_log_receipts"] = dict(
            reversed(list(self.envelope["raw_ci_log_receipts"].items())))
        self.envelope = dict(reversed(list(self.envelope.items())))
        self.assertEqual(prior, self.verdict())
        self.assertEqual(prior, review_bundle_json_text(
            json.dumps(self.envelope, sort_keys=True)))
        self.assertEqual(prior["diagnostics"],
                         ("BUNDLE_RESULT_SHAPE_UNREVIEWED",))

    def test_reviewed_compare_failure_diagnostic_is_not_overly_suppressed(self):
        self.envelope["pr"]["changed_files"] = 3
        direct = self.verdict()
        parsed = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(direct, parsed)
        self.assertIn("PR_COMPARE_FILE_COUNT_MISMATCH", direct["diagnostics"])
        self.assertFalse(direct["source_consistency"])
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def test_receipt_allowlist_clean_source_only_control(self):
        original = self.verdict()
        parsed = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(original, parsed)
        self.assertEqual(original["diagnostics"], ())
        self.assertTrue(original["source_consistency"])
        self.assertFalse(original["independent_original_os_proof"])
        self.assertFalse(original["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(original["can_authorize_annual_run"])

    def _assert_invalid_run_map_key_all_entrypoints(self, map_name, bad_key):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        record = self.envelope[map_name]
        original = record.pop("8000")
        record[bad_key] = original
        direct = self.verdict()
        raw = json.dumps(self.envelope, ensure_ascii=True)
        parsed = review_bundle_json_text(raw)
        out = io.StringIO()
        exit_code = cli.run_stdin_review(io.StringIO(raw), out)
        cli_result = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(exit_code, 2)
        self.assertEqual(direct["diagnostics"],
                         ("BUNDLE_RUN_KEY_UNREVIEWED",))
        self.assertEqual(cli_result["diagnostics"],
                         ["BUNDLE_RUN_KEY_UNREVIEWED"])
        self.assertEqual(set(cli_result), VERDICT_FIELDS)
        self.assertFalse(cli_result["source_consistency"])
        self.assertFalse(cli_result["independent_original_os_proof"])
        self.assertFalse(cli_result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(cli_result["can_authorize_annual_run"])

    def test_run_map_key_plus_prefix_rejected_in_jobs(self):
        self._assert_invalid_run_map_key_all_entrypoints(
            "jobs_by_run", "+8000")

    def test_run_map_key_negative_prefix_rejected_in_checkout(self):
        self._assert_invalid_run_map_key_all_entrypoints(
            "checkout_by_run", "-8000")

    def test_run_map_key_leading_zero_rejected_in_raw_logs(self):
        self._assert_invalid_run_map_key_all_entrypoints(
            "raw_ci_runner_logs", "08000")

    def test_run_map_key_trailing_space_rejected_in_raw_receipts(self):
        self._assert_invalid_run_map_key_all_entrypoints(
            "raw_ci_log_receipts", "8000 ")

    def test_run_map_key_scientific_notation_rejected(self):
        self._assert_invalid_run_map_key_all_entrypoints(
            "jobs_by_run", "8e3")

    def test_run_map_key_unicode_decimal_digits_rejected(self):
        self._assert_invalid_run_map_key_all_entrypoints(
            "checkout_by_run", "\u0668\u0660\u0660\u0660")

    def test_run_map_key_signed_int64_overflow_rejected(self):
        self._assert_invalid_run_map_key_all_entrypoints(
            "raw_ci_runner_logs", "9223372036854775808")

    def test_run_map_key_overlong_decimal_rejected_without_conversion(self):
        self._assert_invalid_run_map_key_all_entrypoints(
            "raw_ci_log_receipts", "8"*2000)

    def test_run_map_key_private_canary_not_echoed(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        key = "private-runkey-canary"
        self.envelope["raw_ci_log_receipts"][key] = (
            self.envelope["raw_ci_log_receipts"].pop("8001"))
        output = io.StringIO()
        status = cli.run_stdin_review(
            io.StringIO(json.dumps(self.envelope)), output)
        self.assertEqual(status, 2)
        self.assertNotIn(key, output.getvalue())
        result = json.loads(output.getvalue())
        self.assertEqual(result["diagnostics"],
                         ["BUNDLE_RUN_KEY_UNREVIEWED"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_run_map_key_canonical_fixture_keeps_source_only(self):
        direct = self.verdict()
        json_verdict = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(direct, json_verdict)
        self.assertEqual(direct["diagnostics"], ())
        self.assertTrue(direct["source_consistency"])
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def _assert_run_inventory_mismatch_all_portable_entrypoints(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        direct = self.verdict()
        raw = json.dumps(self.envelope, separators=(",", ":"))
        parsed = review_bundle_json_text(raw)
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), output)
        cli_result = json.loads(output.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 2)
        self.assertFalse(direct["source_consistency"])
        self.assertTrue(direct["diagnostics"])
        self.assertEqual(cli_result["diagnostics"],
                         list(direct["diagnostics"]))
        self.assertEqual(set(cli_result), VERDICT_FIELDS)
        self.assertFalse(cli_result["source_consistency"])
        self.assertFalse(cli_result["independent_original_os_proof"])
        self.assertFalse(cli_result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(cli_result["can_authorize_annual_run"])

    def test_missing_historical_jobs_map_refuses_source_inventory(self):
        self.envelope["jobs_by_run"].pop("8001")
        self._assert_run_inventory_mismatch_all_portable_entrypoints()

    def test_missing_phase3_checkout_map_refuses_source_inventory(self):
        self.envelope["checkout_by_run"].pop("8000")
        self._assert_run_inventory_mismatch_all_portable_entrypoints()

    def test_missing_historical_raw_log_map_refuses_source_inventory(self):
        self.envelope["raw_ci_runner_logs"].pop("8001")
        self._assert_run_inventory_mismatch_all_portable_entrypoints()

    def test_missing_phase3_raw_receipt_map_refuses_source_inventory(self):
        self.envelope["raw_ci_log_receipts"].pop("8000")
        self._assert_run_inventory_mismatch_all_portable_entrypoints()

    def test_extra_positive_job_map_run_key_does_not_expand_run_list(self):
        self.envelope["jobs_by_run"]["9000"] = []
        self._assert_run_inventory_mismatch_all_portable_entrypoints()

    def test_extra_positive_checkout_map_run_key_does_not_expand_run_list(self):
        self.envelope["checkout_by_run"]["9000"] = {}
        self._assert_run_inventory_mismatch_all_portable_entrypoints()

    def test_extra_positive_raw_log_run_key_does_not_expand_run_list(self):
        self.envelope["raw_ci_runner_logs"]["9000"] = "synthetic log"
        self._assert_run_inventory_mismatch_all_portable_entrypoints()

    def test_extra_positive_receipt_map_run_key_does_not_expand_run_list(self):
        self.envelope["raw_ci_log_receipts"]["9000"] = {}
        self._assert_run_inventory_mismatch_all_portable_entrypoints()

    def test_changed_phase3_run_identity_not_fixed_by_existing_maps(self):
        target = next(r for r in self.envelope["runs"]
                      if r["name"] == "phase3-acceptance")
        target["id"] = 9000
        self._assert_run_inventory_mismatch_all_portable_entrypoints()

    def test_colliding_two_run_ids_does_not_relabel_run_provenance(self):
        historical = next(r for r in self.envelope["runs"]
                          if r["name"] == "tests")
        historical["id"] = 8000
        self._assert_run_inventory_mismatch_all_portable_entrypoints()

    def test_clean_two_run_inventory_retains_source_consistency_only(self):
        expected = {"8000", "8001"}
        for key in ("jobs_by_run", "checkout_by_run",
                    "raw_ci_runner_logs", "raw_ci_log_receipts"):
            self.assertEqual(set(self.envelope[key]), expected)
        self.assertEqual({r["id"] for r in self.envelope["runs"]},
                         {8000, 8001})
        direct = self.verdict()
        parsed = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(direct, parsed)
        self.assertEqual(direct["diagnostics"], ())
        self.assertTrue(direct["source_consistency"])
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def _assert_rehashed_nonstage_log_line_is_not_annual_admission(
            self, added_text, change_checkout=False):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        raw = self.envelope["raw_ci_runner_logs"]["8001"]
        if change_checkout:
            self.assertIn("/1649/merge", raw)
            raw = raw.replace("/1649/merge", "/9999/merge")
        self.envelope["raw_ci_runner_logs"]["8001"] = (
            raw + "\nprivate-untrusted-note: " + added_text)
        self._refingerprint_portable_synthetic_ci_log("8001")
        direct = self.verdict()
        json_text = json.dumps(self.envelope, ensure_ascii=True)
        parsed = review_bundle_json_text(json_text)
        out = io.StringIO()
        exit_code = cli.run_stdin_review(io.StringIO(json_text), out)
        record = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(record["diagnostics"], list(direct["diagnostics"]))
        self.assertEqual(record["source_consistency"],
                         direct["source_consistency"])
        self.assertEqual(exit_code,
                         2 if change_checkout else 0)
        self.assertEqual(direct["source_consistency"],
                         not change_checkout)
        self.assertNotIn("private-untrusted-note", out.getvalue())
        self.assertNotIn(added_text, out.getvalue())
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])
        self.assertFalse(record["independent_original_os_proof"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_rehashed_nonstage_log_fake_annual_permission_is_not_proof(self):
        self._assert_rehashed_nonstage_log_line_is_not_annual_admission(
            "can_authorize_annual_run=true")

    def test_rehashed_nonstage_log_fake_original_os_proof_is_not_proof(self):
        self._assert_rehashed_nonstage_log_line_is_not_annual_admission(
            "independent_original_os_proof=true")

    def test_rehashed_nonstage_log_fake_server_gate_is_not_proof(self):
        self._assert_rehashed_nonstage_log_line_is_not_annual_admission(
            "exclusive_server_dispatch_gate_proven=true")

    def test_rehashed_nonstage_log_fake_annual_approval_is_not_proof(self):
        self._assert_rehashed_nonstage_log_line_is_not_annual_admission(
            "protected 2023 annual run385 attempt1 permission granted")

    def test_rehashed_nonstage_log_fake_approval_cannot_mask_wrong_pr_ref(self):
        self._assert_rehashed_nonstage_log_line_is_not_annual_admission(
            "can_authorize_annual_run=true", change_checkout=True)

    def test_rehashed_nonstage_log_fake_os_proof_cannot_mask_wrong_pr_ref(self):
        self._assert_rehashed_nonstage_log_line_is_not_annual_admission(
            "independent_original_os_proof=true", change_checkout=True)

    def test_rehashed_nonstage_log_fake_gate_cannot_mask_wrong_pr_ref(self):
        self._assert_rehashed_nonstage_log_line_is_not_annual_admission(
            "exclusive_server_dispatch_gate_proven=true",
            change_checkout=True)

    def test_rehashed_nonstage_log_fake_approval_cannot_mask_wrong_pr_ref(self):
        self._assert_rehashed_nonstage_log_line_is_not_annual_admission(
            "protected 2023 annual run385 attempt1 permission granted",
            change_checkout=True)

    def _assert_malformed_numeric_run_identity_all_entrypoints(self, run_id):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        target = next(r for r in self.envelope["runs"]
                      if r["name"] == "phase3-acceptance")
        target["id"] = run_id
        raw = json.dumps(self.envelope, allow_nan=False)
        direct = self.verdict()
        json_result = review_bundle_json_text(raw)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct, json_result)
        self.assertFalse(direct["source_consistency"])
        self.assertTrue(direct["diagnostics"])
        self.assertEqual(status, 2)
        self.assertEqual(emitted["diagnostics"],
                         list(json_result["diagnostics"]))
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertFalse(emitted["source_consistency"])
        self.assertFalse(emitted["independent_original_os_proof"])
        self.assertFalse(emitted["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(emitted["can_authorize_annual_run"])

    def test_phase3_nested_run_id_boolean_not_integer_identity(self):
        self._assert_malformed_numeric_run_identity_all_entrypoints(True)

    def test_phase3_nested_run_id_string_not_integer_identity(self):
        self._assert_malformed_numeric_run_identity_all_entrypoints("8000")

    def test_phase3_nested_run_id_float_not_integer_identity(self):
        self._assert_malformed_numeric_run_identity_all_entrypoints(8000.0)

    def test_phase3_nested_run_id_null_not_integer_identity(self):
        self._assert_malformed_numeric_run_identity_all_entrypoints(None)

    def test_phase3_nested_run_id_list_not_integer_identity(self):
        self._assert_malformed_numeric_run_identity_all_entrypoints([8000])

    def test_phase3_nested_run_id_object_not_integer_identity(self):
        self._assert_malformed_numeric_run_identity_all_entrypoints(
            {"synthetic": 8000})

    def test_phase3_nested_run_id_zero_not_positive_identity(self):
        self._assert_malformed_numeric_run_identity_all_entrypoints(0)

    def test_phase3_nested_run_id_negative_not_positive_identity(self):
        self._assert_malformed_numeric_run_identity_all_entrypoints(-8000)

    def test_phase3_nested_run_id_over_signed64_cannot_rebind_maps(self):
        self._assert_malformed_numeric_run_identity_all_entrypoints(
            9223372036854775808)

    def test_phase3_nested_run_id_clean_two_runner_control(self):
        values = {r["id"] for r in self.envelope["runs"]}
        self.assertEqual(values, {8000, 8001})
        direct = self.verdict()
        parsed = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(direct, parsed)
        self.assertEqual(direct["diagnostics"], ())
        self.assertTrue(direct["source_consistency"])
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def _assert_returning_nested_reviewer_cannot_mutate_original(self, tamper):
        from unittest.mock import patch
        original = copy.deepcopy(self.envelope)
        invoked = []
        def synthetic_nested_result(**values):
            tamper(values)
            invoked.append(True)
            return {
                "source_consistency": True, "diagnostics": (),
                "independent_original_os_proof": False,
                "exclusive_server_dispatch_gate_proven": False,
                "can_authorize_annual_run": False,
            }
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=synthetic_nested_result):
            result = self.verdict()
        self.assertEqual(invoked, [True])
        self.assertEqual(self.envelope, original)
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])
        after = self.verdict()
        self.assertEqual(after["diagnostics"], ())
        self.assertTrue(after["source_consistency"])
        self.assertFalse(after["independent_original_os_proof"])
        self.assertFalse(after["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(after["can_authorize_annual_run"])

    def test_returning_nested_review_mutation_of_pr_is_isolated(self):
        self._assert_returning_nested_reviewer_cannot_mutate_original(
            lambda v: v["pr"].update({"private": "unreviewed"}))

    def test_returning_nested_review_mutation_of_run_list_is_isolated(self):
        self._assert_returning_nested_reviewer_cannot_mutate_original(
            lambda v: v["runs"].clear())

    def test_returning_nested_review_mutation_of_jobs_is_isolated(self):
        self._assert_returning_nested_reviewer_cannot_mutate_original(
            lambda v: v["jobs_by_run"].clear())

    def test_returning_nested_review_mutation_of_ci_source_map_is_isolated(self):
        self._assert_returning_nested_reviewer_cannot_mutate_original(
            lambda v: v["ci_workflow_bytes"].clear())

    def test_returning_nested_review_mutation_of_git_tree_is_isolated(self):
        self._assert_returning_nested_reviewer_cannot_mutate_original(
            lambda v: v["full_tree_snapshots"].clear())

    def test_returning_nested_review_mutation_of_runner_evidence_is_isolated(self):
        self._assert_returning_nested_reviewer_cannot_mutate_original(
            lambda v: v["checkout_by_run"].clear())

    def test_returning_nested_review_mutation_of_acceptance_is_isolated(self):
        self._assert_returning_nested_reviewer_cannot_mutate_original(
            lambda v: v["phase3_evidence_snapshot"].clear())

    def test_returning_nested_review_mutation_of_raw_logs_is_isolated(self):
        self._assert_returning_nested_reviewer_cannot_mutate_original(
            lambda v: v["raw_ci_runner_logs"].clear())

    def test_returning_nested_review_mutation_of_log_receipts_is_isolated(self):
        self._assert_returning_nested_reviewer_cannot_mutate_original(
            lambda v: v["raw_ci_log_receipts"].clear())

    def _assert_base64_alias_refusal_all_entrypoints(self, category, encoded,
                                                       canonical, diagnostic):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.assertEqual(base64.b64decode(encoded, validate=True),
                         base64.b64decode(canonical, validate=True))
        self.assertNotEqual(encoded, canonical)
        key = next(iter(self.envelope[category]))
        self.envelope[category][key] = encoded
        direct = self.verdict()
        raw = json.dumps(self.envelope)
        json_result = review_bundle_json_text(raw)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        record = json.loads(out.getvalue())
        self.assertEqual(direct, json_result)
        self.assertEqual(direct["diagnostics"], (diagnostic,))
        self.assertEqual(record["diagnostics"], [diagnostic])
        self.assertEqual(status, 2)
        self.assertEqual(set(record), VERDICT_FIELDS)
        self.assertFalse(record["source_consistency"])
        self.assertFalse(record["independent_original_os_proof"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_base64_pad_bit_alias_z_h_changed_source_refused(self):
        self._assert_base64_alias_refusal_all_entrypoints(
            "changed_bytes_b64", "Zh==", "Zg==",
            "BUNDLE_SOURCE_B64_NONCANONICAL")

    def test_base64_pad_bit_alias_z_v_changed_source_refused(self):
        self._assert_base64_alias_refusal_all_entrypoints(
            "changed_bytes_b64", "Zv==", "Zg==",
            "BUNDLE_SOURCE_B64_NONCANONICAL")

    def test_base64_pad_bit_alias_null_byte_changed_source_refused(self):
        self._assert_base64_alias_refusal_all_entrypoints(
            "changed_bytes_b64", "AB==", "AA==",
            "BUNDLE_SOURCE_B64_NONCANONICAL")

    def test_base64_pad_bit_alias_two_byte_changed_source_refused(self):
        self._assert_base64_alias_refusal_all_entrypoints(
            "changed_bytes_b64", "Zm9=", "Zm8=",
            "BUNDLE_SOURCE_B64_NONCANONICAL")

    def test_base64_pad_bit_alias_two_byte_workflow_refused(self):
        self._assert_base64_alias_refusal_all_entrypoints(
            "ci_workflow_bytes_b64", "Zm/=", "Zm8=",
            "BUNDLE_SOURCE_B64_NONCANONICAL")

    def test_base64_pad_bit_alias_one_byte_workflow_refused(self):
        self._assert_base64_alias_refusal_all_entrypoints(
            "ci_workflow_bytes_b64", "Zh==", "Zg==",
            "BUNDLE_SOURCE_B64_NONCANONICAL")

    def test_base64_pad_bit_alias_nul_workflow_refused(self):
        self._assert_base64_alias_refusal_all_entrypoints(
            "ci_workflow_bytes_b64", "AB==", "AA==",
            "BUNDLE_SOURCE_B64_NONCANONICAL")

    def test_base64_missing_padding_refused_before_nested_evidence(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = "Zg="
        result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SOURCE_B64_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_base64_excess_padding_refused_before_nested_evidence(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = "Zg==="
        result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SOURCE_B64_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_base64_canonical_replacement_decodes_but_cannot_spoof_source(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = "Zg=="
        raw = json.dumps(self.envelope)
        direct = self.verdict()
        parsed = review_bundle_json_text(raw)
        self.assertEqual(direct, parsed)
        self.assertFalse(direct["source_consistency"])
        self.assertTrue(direct["diagnostics"])
        self.assertNotIn("BUNDLE_SOURCE_B64_UNREVIEWED",
                         direct["diagnostics"])
        self.assertNotIn("BUNDLE_SOURCE_B64_NONCANONICAL",
                         direct["diagnostics"])
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def _assert_base64_decoder_skipped_for_preflight(self, category,
                                                      new_map, code):
        from unittest.mock import patch
        self.envelope[category] = new_map
        # Map preflights are ordered. Isolate the target map so decoding
        # valid entries in an earlier map cannot trip this sentinel.
        other = ("ci_workflow_bytes_b64" if category == "changed_bytes_b64"
                 else "changed_bytes_b64")
        self.envelope[other] = {}
        with patch.object(base64, "b64decode",
                          side_effect=AssertionError("decoder was invoked")) as decoder:
            result = self.verdict()
        decoder.assert_not_called()
        self.assertEqual(result["diagnostics"], (code,))
        self.assertFalse(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_oversized_changed_base64_text_never_invokes_decoder(self):
        limit = 4*((MAX_BLOB_BYTES+2)//3)
        self._assert_base64_decoder_skipped_for_preflight(
            "changed_bytes_b64",
            {"tests/sample.py": "A"*(limit+4)},
            "BUNDLE_SOURCE_BLOB_OVERSIZE")

    def test_oversized_workflow_base64_text_never_invokes_decoder(self):
        limit = 4*((MAX_BLOB_BYTES+2)//3)
        self._assert_base64_decoder_skipped_for_preflight(
            "ci_workflow_bytes_b64",
            {".github/workflows/tests.yml": "A"*(limit+4)},
            "BUNDLE_SOURCE_BLOB_OVERSIZE")

    def test_overlarge_changed_source_inventory_never_decodes_any_blob(self):
        values = {f"tests/sample-{i}.py": "AA=="
                  for i in range(MAX_SOURCE_ENTRIES_PER_MAP+1)}
        self._assert_base64_decoder_skipped_for_preflight(
            "changed_bytes_b64", values,
            "BUNDLE_SOURCE_MAP_OVERSIZE")

    def test_overlarge_workflow_source_inventory_never_decodes_any_blob(self):
        values = {f".github/workflows/synthetic-{i}.yml": "AA=="
                  for i in range(MAX_SOURCE_ENTRIES_PER_MAP+1)}
        self._assert_base64_decoder_skipped_for_preflight(
            "ci_workflow_bytes_b64", values,
            "BUNDLE_SOURCE_MAP_OVERSIZE")

    def test_invalid_absolute_changed_source_path_skips_base64_decode(self):
        self._assert_base64_decoder_skipped_for_preflight(
            "changed_bytes_b64",
            {"/private/not-a-source.py": "AA=="},
            "BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_invalid_parent_workflow_source_path_skips_base64_decode(self):
        self._assert_base64_decoder_skipped_for_preflight(
            "ci_workflow_bytes_b64",
            {".github/workflows/../unsafe.yml": "AA=="},
            "BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_exact_encoded_length_still_decodes_then_checks_raw_bytes(self):
        from unittest.mock import patch
        limit = 4*((MAX_BLOB_BYTES+2)//3)
        # Isolate the target blob: the normal fixture has a valid docs
        # entry that the decoder necessarily visits first.
        self.envelope["changed_bytes_b64"] = {
            "tests/sample.py": "A"*limit}
        self.envelope["ci_workflow_bytes_b64"] = {}
        with patch.object(base64, "b64decode",
                          wraps=base64.b64decode) as decoder:
            result = self.verdict()
        decoder.assert_called_once()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SOURCE_BLOB_OVERSIZE",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_predecode_guards_preserve_canonical_small_clean_bundle(self):
        from unittest.mock import patch
        expected_count = (len(self.envelope["changed_bytes_b64"]) +
                          len(self.envelope["ci_workflow_bytes_b64"]))
        with patch.object(base64, "b64decode",
                          wraps=base64.b64decode) as decoder:
            result = self.verdict()
        self.assertEqual(decoder.call_count, expected_count)
        self.assertTrue(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def _synthetic_bulk_source_encoding(self, size=800001):
        return base64.b64encode(b"x"*size).decode("ascii")

    def _assert_source_aggregate_refusal_before_nested_review(self):
        from unittest.mock import patch
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=AssertionError("source review must not run")) as review:
            result = self.verdict()
        review.assert_not_called()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_TOTAL_SOURCE_OVERSIZE",))
        self.assertFalse(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_direct_memory_changed_source_aggregate_over_ceiling(self):
        encoded = self._synthetic_bulk_source_encoding()
        self.envelope["changed_bytes_b64"] = {
            f"tests/bulk-{i}.py": encoded for i in range(5)}
        self.envelope["ci_workflow_bytes_b64"] = {}
        self._assert_source_aggregate_refusal_before_nested_review()

    def test_direct_memory_cross_category_source_aggregate_over_ceiling(self):
        encoded = self._synthetic_bulk_source_encoding()
        self.envelope["changed_bytes_b64"] = {
            f"tests/bulk-{i}.py": encoded for i in range(3)}
        self.envelope["ci_workflow_bytes_b64"] = {
            f".github/workflows/bulk-{i}.yml": encoded for i in range(2)}
        self._assert_source_aggregate_refusal_before_nested_review()

    def test_direct_memory_cross_category_order_does_not_change_budget(self):
        encoded = self._synthetic_bulk_source_encoding()
        changed = [(f"tests/bulk-{i}.py", encoded) for i in range(3)]
        workflows = [(f".github/workflows/bulk-{i}.yml", encoded)
                     for i in range(2)]
        self.envelope["changed_bytes_b64"] = dict(reversed(changed))
        self.envelope["ci_workflow_bytes_b64"] = dict(reversed(workflows))
        self._assert_source_aggregate_refusal_before_nested_review()

    def test_direct_memory_exact_four_million_bytes_reaches_nested_review(self):
        from unittest.mock import patch
        encoded = self._synthetic_bulk_source_encoding(1_000_000)
        self.envelope["changed_bytes_b64"] = {
            f"tests/exact-{i}.py": encoded for i in range(4)}
        self.envelope["ci_workflow_bytes_b64"] = {}
        allowed_source_only = {
            "source_consistency": True, "diagnostics": (),
            "independent_original_os_proof": False,
            "exclusive_server_dispatch_gate_proven": False,
            "can_authorize_annual_run": False,
        }
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=allowed_source_only) as review:
            result = self.verdict()
        review.assert_called_once()
        self.assertEqual(result, allowed_source_only)
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_per_source_raw_byte_limit_precedes_aggregate_budget(self):
        encoded = self._synthetic_bulk_source_encoding(1_000_001)
        self.envelope["changed_bytes_b64"] = {
            "tests/over-single.py": encoded}
        self.envelope["ci_workflow_bytes_b64"] = {}
        result = self.verdict()
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SOURCE_BLOB_OVERSIZE",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_json_document_budget_precedes_large_aggregate_source_budget(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        encoded = self._synthetic_bulk_source_encoding()
        self.envelope["changed_bytes_b64"] = {
            f"tests/bulk-{i}.py": encoded for i in range(5)}
        self.envelope["ci_workflow_bytes_b64"] = {}
        self.assertEqual(self.verdict()["diagnostics"],
                         ("BUNDLE_TOTAL_SOURCE_OVERSIZE",))
        raw = json.dumps(self.envelope)
        self.assertGreater(len(raw), MAX_TEXT_CHARS)
        self.assertEqual(review_bundle_json_text(raw)["diagnostics"],
                         ("BUNDLE_JSON_TEXT_UNREVIEWED",))
        out = io.StringIO()
        exit_code = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_TEXT_UNREVIEWED"])
        self.assertFalse(emitted["independent_original_os_proof"])
        self.assertFalse(emitted["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(emitted["can_authorize_annual_run"])

    def _assert_pairwise_fault_review_parity(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        text = json.dumps(self.envelope, ensure_ascii=True)
        direct = self.verdict()
        parsed = review_bundle_json_text(text)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(text), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 2)
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertFalse(direct["source_consistency"])
        self.assertTrue(direct["diagnostics"])
        self.assertEqual(emitted["diagnostics"], list(direct["diagnostics"]))
        self.assertNotIn("private-pairwise-canary", out.getvalue())
        for verdict in (direct, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_pairwise_pr_diff_and_rehashed_checkout_mismatch_are_refused(self):
        self.envelope["pr"]["changed_files"] = 3
        log = self.envelope["raw_ci_runner_logs"]["8001"]
        self.envelope["raw_ci_runner_logs"]["8001"] = log.replace(
            "/1649/merge", "/9999/merge")
        self._refingerprint_portable_synthetic_ci_log("8001")
        self._assert_pairwise_fault_review_parity()

    def test_pairwise_source_bytes_and_rehashed_artifact_id_are_refused(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = (
            base64.b64encode(b"private-pairwise-canary").decode("ascii"))
        log = self.envelope["raw_ci_runner_logs"]["8000"]
        self.envelope["raw_ci_runner_logs"]["8000"] = log.replace(
            "7777", "8888")
        self._refingerprint_portable_synthetic_ci_log("8000")
        self._assert_pairwise_fault_review_parity()

    def test_pairwise_tree_and_acceptance_index_mismatch_are_refused(self):
        self.envelope["tree"]["sha"] = "e"*40
        self.envelope["phase3_evidence_snapshot"]["index"][
            "scenario_count"] = 9
        self._assert_pairwise_fault_review_parity()

    def test_pairwise_duplicate_run_identity_and_ci_job_failure_are_refused(self):
        historical = next(r for r in self.envelope["runs"]
                          if r["name"] == "tests")
        historical["id"] = 8000
        self.envelope["jobs_by_run"]["8001"][0]["conclusion"] = "failure"
        self._assert_pairwise_fault_review_parity()

    def test_pairwise_extra_annual_field_and_changed_source_fail_inventory(self):
        self.envelope["can_authorize_annual_run"] = True
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = (
            base64.b64encode(b"private-pairwise-canary").decode("ascii"))
        self._assert_pairwise_fault_review_parity()
        self.assertEqual(self.verdict()["diagnostics"],
                         ("BUNDLE_KEY_INVENTORY_UNREVIEWED",))

    def test_pairwise_invalid_run_map_key_and_bad_base64_fail_preflight(self):
        self.envelope["jobs_by_run"]["08000"] = (
            self.envelope["jobs_by_run"].pop("8000"))
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = (
            "private-pairwise-canary%")
        self._assert_pairwise_fault_review_parity()

    def test_pairwise_absolute_source_path_and_failed_ci_run_are_refused(self):
        self.envelope["changed_bytes_b64"][
            "/private-pairwise-canary.py"] = (
            self.envelope["changed_bytes_b64"].pop("tests/sample.py"))
        self.envelope["runs"][0]["conclusion"] = "failure"
        self._assert_pairwise_fault_review_parity()

    def test_pairwise_extra_raw_log_run_and_wrong_pr_ref_are_refused(self):
        self.envelope["raw_ci_runner_logs"]["9000"] = (
            "private-pairwise-canary")
        log = self.envelope["raw_ci_runner_logs"]["8000"]
        self.envelope["raw_ci_runner_logs"]["8000"] = log.replace(
            "/1649/merge", "/9999/merge")
        self._refingerprint_portable_synthetic_ci_log("8000")
        self._assert_pairwise_fault_review_parity()

    def test_pairwise_job_map_type_and_wrong_upload_name_are_refused(self):
        self.envelope["jobs_by_run"]["8001"] = "private-pairwise-canary"
        self.envelope["phase3_evidence_snapshot"]["upload"]["name"] = (
            "private-pairwise-canary")
        self._assert_pairwise_fault_review_parity()

    def test_pairwise_pr_number_and_raw_log_checkout_identity_are_refused(self):
        self.envelope["pr"]["number"] = 9999
        log = self.envelope["raw_ci_runner_logs"]["8001"]
        self.envelope["raw_ci_runner_logs"]["8001"] = log.replace(
            "/1649/merge", "/9999/merge")
        self._refingerprint_portable_synthetic_ci_log("8001")
        self._assert_pairwise_fault_review_parity()

    def _assert_offline_review_no_external_action(self, runner,
                                                  expect_consistent):
        import builtins
        import os
        import pathlib
        import socket
        import subprocess
        import urllib.request
        from contextlib import ExitStack
        from unittest.mock import patch
        forbidden = []
        def refuse(*args, **kwargs):
            forbidden.append("unexpected external action")
            raise AssertionError("offline source reviewer external action")
        boundaries = (
            (builtins, "open"),
            (pathlib.Path, "open"),
            (socket, "socket"),
            (socket, "create_connection"),
            (subprocess, "run"),
            (subprocess, "Popen"),
            (subprocess, "check_output"),
            (os, "system"),
            (os, "popen"),
            (urllib.request, "urlopen"),
        )
        with ExitStack() as stack:
            for module, name in boundaries:
                stack.enter_context(
                    patch.object(module, name, side_effect=refuse))
            result = runner()
        self.assertEqual(forbidden, [])
        self.assertEqual(result["source_consistency"], expect_consistent)
        self.assertEqual(type(result["diagnostics"]), tuple)
        self.assertEqual(bool(result["diagnostics"]), not expect_consistent)
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_offline_clean_direct_memory_avoids_external_action_apis(self):
        self._assert_offline_review_no_external_action(self.verdict, True)

    def test_offline_clean_json_text_avoids_external_action_apis(self):
        raw = json.dumps(self.envelope)
        self._assert_offline_review_no_external_action(
            lambda: review_bundle_json_text(raw), True)

    def test_offline_bad_source_identity_avoids_external_action_apis(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = (
            base64.b64encode(b"synthetic-unreviewed").decode("ascii"))
        self._assert_offline_review_no_external_action(self.verdict, False)

    def test_offline_bad_ci_source_identity_avoids_external_action_apis(self):
        self.envelope["ci_workflow_bytes_b64"][
            ".github/workflows/tests.yml"] = (
            base64.b64encode(b"synthetic-unreviewed").decode("ascii"))
        self._assert_offline_review_no_external_action(self.verdict, False)

    def test_offline_json_duplicate_key_avoids_external_action_apis(self):
        self._assert_offline_review_no_external_action(
            lambda: review_bundle_json_text(
                '{"schema":1,"schema":2}'), False)

    def test_offline_invalid_source_path_avoids_external_action_apis(self):
        self.envelope["changed_bytes_b64"][
            "/private/synthetic-evidence.py"] = (
            self.envelope["changed_bytes_b64"].pop("tests/sample.py"))
        self._assert_offline_review_no_external_action(
            lambda: review_bundle_json_text(json.dumps(self.envelope)),
            False)

    def test_offline_private_url_string_never_triggers_network_apis(self):
        self.envelope["pr"]["untrusted_origin"] = (
            "https://private.invalid/annual-run385")
        # An ignored untrusted note does not change reviewed source stages.
        # Passing source consistency is still not provider authentication.
        self._assert_offline_review_no_external_action(self.verdict, True)

    def test_offline_stdin_review_avoids_external_action_apis(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        raw = json.dumps(self.envelope)
        def review_via_stdin():
            out = io.StringIO()
            status = cli.run_stdin_review(io.StringIO(raw), out)
            self.assertEqual(status, 0)
            doc = json.loads(out.getvalue())
            doc["diagnostics"] = tuple(doc["diagnostics"])
            return doc
        self._assert_offline_review_no_external_action(review_via_stdin,
                                                       True)

    def _assert_portable_preflight_does_not_call_nested_review(self, code):
        from unittest.mock import patch
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=AssertionError("must-not-review")) as nested:
            verdict = self.verdict()
        nested.assert_not_called()
        self.assertEqual(verdict["diagnostics"], (code,))
        self.assertFalse(verdict["source_consistency"])
        self.assertFalse(verdict["independent_original_os_proof"])
        self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_preflight_root_extra_field_skips_nested_review(self):
        self.envelope["can_authorize_annual_run"] = True
        self._assert_portable_preflight_does_not_call_nested_review(
            "BUNDLE_KEY_INVENTORY_UNREVIEWED")

    def test_preflight_wrong_schema_skips_nested_review(self):
        self.envelope["schema"] = "unreviewed-schema"
        self._assert_portable_preflight_does_not_call_nested_review(
            "BUNDLE_SCHEMA_UNREVIEWED")

    def test_preflight_wrong_runs_type_skips_nested_review(self):
        self.envelope["runs"] = {}
        self._assert_portable_preflight_does_not_call_nested_review(
            "BUNDLE_CATEGORY_TYPE_UNREVIEWED")

    def test_preflight_invalid_run_map_key_skips_nested_review(self):
        self.envelope["jobs_by_run"]["08000"] = (
            self.envelope["jobs_by_run"].pop("8000"))
        self._assert_portable_preflight_does_not_call_nested_review(
            "BUNDLE_RUN_KEY_UNREVIEWED")

    def test_preflight_malformed_source_base64_skips_nested_review(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = "not-base64%"
        self._assert_portable_preflight_does_not_call_nested_review(
            "BUNDLE_SOURCE_B64_UNREVIEWED")

    def test_preflight_absolute_source_path_skips_nested_review(self):
        self.envelope["changed_bytes_b64"][
            "/private/synthetic.py"] = (
            self.envelope["changed_bytes_b64"].pop("tests/sample.py"))
        self._assert_portable_preflight_does_not_call_nested_review(
            "BUNDLE_SOURCE_PATH_UNREVIEWED")

    def test_preflight_nul_in_raw_ci_log_skips_nested_review(self):
        self.envelope["raw_ci_runner_logs"]["8001"] += "\x00"
        self._assert_portable_preflight_does_not_call_nested_review(
            "BUNDLE_RAW_LOG_TEXT_UNREVIEWED")

    def test_preflight_source_case_alias_skips_nested_review(self):
        self.envelope["changed_bytes_b64"]["TESTS/SAMPLE.PY"] = (
            self.envelope["changed_bytes_b64"]["tests/sample.py"])
        self._assert_portable_preflight_does_not_call_nested_review(
            "BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED")

    def test_preflight_source_workflow_map_overlap_skips_nested_review(self):
        key = ".github/workflows/tests.yml"
        self.envelope["changed_bytes_b64"][key] = (
            self.envelope["ci_workflow_bytes_b64"][key])
        self._assert_portable_preflight_does_not_call_nested_review(
            "BUNDLE_SOURCE_CROSSMAP_COLLISION_UNREVIEWED")

    def test_valid_preflight_invokes_nested_review_once_without_authority(self):
        from unittest.mock import patch
        clean = {
            "source_consistency": True, "diagnostics": (),
            "independent_original_os_proof": False,
            "exclusive_server_dispatch_gate_proven": False,
            "can_authorize_annual_run": False,
        }
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=clean) as nested:
            result = self.verdict()
        nested.assert_called_once()
        self.assertEqual(result, clean)
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def _assert_repeated_review_does_not_retain_failed_input(self, mutate):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        original = copy.deepcopy(self.envelope)
        def review_all():
            raw = json.dumps(self.envelope, ensure_ascii=True)
            direct = self.verdict()
            parsed = review_bundle_json_text(raw)
            output = io.StringIO()
            status = cli.run_stdin_review(io.StringIO(raw), output)
            record = json.loads(output.getvalue())
            self.assertEqual(direct, parsed)
            self.assertEqual(set(record), VERDICT_FIELDS)
            self.assertEqual(record["diagnostics"],
                             list(direct["diagnostics"]))
            self.assertEqual(record["source_consistency"],
                             direct["source_consistency"])
            self.assertNotIn("private-replay-canary", output.getvalue())
            self.assertFalse(record["independent_original_os_proof"])
            self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(record["can_authorize_annual_run"])
            return status, direct
        before_status, before = review_all()
        self.assertEqual(before_status, 0)
        self.assertTrue(before["source_consistency"])
        self.assertEqual(before["diagnostics"], ())
        mutate()
        bad_status, bad = review_all()
        self.assertEqual(bad_status, 2)
        self.assertFalse(bad["source_consistency"])
        self.assertTrue(bad["diagnostics"])
        self.envelope = original
        after_status, after = review_all()
        self.assertEqual(after_status, 0)
        self.assertEqual(after, before)
        self.assertFalse(after["independent_original_os_proof"])
        self.assertFalse(after["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(after["can_authorize_annual_run"])

    def test_repeat_recovery_after_extra_annual_root_field(self):
        self._assert_repeated_review_does_not_retain_failed_input(
            lambda: self.envelope.update({
                "can_authorize_annual_run": True}))

    def test_repeat_recovery_after_unknown_schema(self):
        self._assert_repeated_review_does_not_retain_failed_input(
            lambda: self.envelope.update({
                "schema": "private-replay-canary"}))

    def test_repeat_recovery_after_invalid_run_map_key(self):
        def corrupt():
            self.envelope["jobs_by_run"]["08000"] = (
                self.envelope["jobs_by_run"].pop("8000"))
        self._assert_repeated_review_does_not_retain_failed_input(corrupt)

    def test_repeat_recovery_after_malformed_base64(self):
        def corrupt():
            self.envelope["changed_bytes_b64"]["tests/sample.py"] = (
                "private-replay-canary%")
        self._assert_repeated_review_does_not_retain_failed_input(corrupt)

    def test_repeat_recovery_after_valid_but_wrong_source_bytes(self):
        def corrupt():
            self.envelope["changed_bytes_b64"]["tests/sample.py"] = (
                base64.b64encode(b"private-replay-canary").decode("ascii"))
        self._assert_repeated_review_does_not_retain_failed_input(corrupt)

    def test_repeat_recovery_after_rehashed_wrong_checkout_ref(self):
        def corrupt():
            log = self.envelope["raw_ci_runner_logs"]["8001"]
            self.envelope["raw_ci_runner_logs"]["8001"] = (
                log.replace("/1649/merge", "/9999/merge"))
            self._refingerprint_portable_synthetic_ci_log("8001")
        self._assert_repeated_review_does_not_retain_failed_input(corrupt)

    def test_repeat_recovery_after_unreviewed_raw_log_receipt_job(self):
        def corrupt():
            self.envelope["raw_ci_log_receipts"]["8001"]["job_id"] = (
                self.envelope["raw_ci_log_receipts"]["8000"]["job_id"])
        self._assert_repeated_review_does_not_retain_failed_input(corrupt)

    def test_repeat_recovery_after_absolute_source_path(self):
        def corrupt():
            self.envelope["changed_bytes_b64"][
                "/private-replay-canary.py"] = (
                self.envelope["changed_bytes_b64"].pop("tests/sample.py"))
        self._assert_repeated_review_does_not_retain_failed_input(corrupt)

    def test_repeat_recovery_after_phase3_artifact_drift(self):
        def corrupt():
            self.envelope["phase3_evidence_snapshot"]["upload"][
                "name"] = "private-replay-canary"
        self._assert_repeated_review_does_not_retain_failed_input(corrupt)

    def test_repeat_recovery_after_duplicate_runner_run_id(self):
        def corrupt():
            historical = next(r for r in self.envelope["runs"]
                              if r["name"] == "tests")
            historical["id"] = 8000
        self._assert_repeated_review_does_not_retain_failed_input(corrupt)

    def test_workflow_preflight_allows_decoded_earlier_source_map(self):
        from unittest.mock import patch
        limit = 4*((MAX_BLOB_BYTES+2)//3)
        expected = len(self.envelope["changed_bytes_b64"])
        self.envelope["ci_workflow_bytes_b64"] = {
            ".github/workflows/tests.yml": "A"*(limit+4)}
        with patch.object(base64, "b64decode",
                          wraps=base64.b64decode) as decoder:
            result = self.verdict()
        self.assertEqual(decoder.call_count, expected)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SOURCE_BLOB_OVERSIZE",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_workflow_bad_path_allows_prior_changed_source_decoding(self):
        from unittest.mock import patch
        expected = len(self.envelope["changed_bytes_b64"])
        self.envelope["ci_workflow_bytes_b64"] = {
            ".github/workflows/../invalid.yml": "AA=="}
        with patch.object(base64, "b64decode",
                          wraps=base64.b64decode) as decoder:
            result = self.verdict()
        self.assertEqual(decoder.call_count, expected)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SOURCE_PATH_UNREVIEWED",))
        self.assertFalse(result["can_authorize_annual_run"])

    def test_workflow_overlarge_inventory_allows_earlier_source_decoding(self):
        from unittest.mock import patch
        expected = len(self.envelope["changed_bytes_b64"])
        self.envelope["ci_workflow_bytes_b64"] = {
            f".github/workflows/synthetic-{i}.yml": "AA=="
            for i in range(MAX_SOURCE_ENTRIES_PER_MAP+1)}
        with patch.object(base64, "b64decode",
                          wraps=base64.b64decode) as decoder:
            result = self.verdict()
        self.assertEqual(decoder.call_count, expected)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_SOURCE_MAP_OVERSIZE",))
        self.assertFalse(result["can_authorize_annual_run"])

    def _assert_unicode_log_receipt_parity(self, source_consistency):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        direct = self.verdict()
        raw = json.dumps(self.envelope, ensure_ascii=False)
        json_result = review_bundle_json_text(raw)
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), output)
        record = json.loads(output.getvalue())
        self.assertEqual(direct, json_result)
        self.assertEqual(record["diagnostics"],
                         list(direct["diagnostics"]))
        self.assertEqual(record["source_consistency"],
                         direct["source_consistency"])
        self.assertEqual(direct["source_consistency"], source_consistency)
        self.assertEqual(status, 0 if source_consistency else 2)
        self.assertNotIn("private-unicode-ci-canary", output.getvalue())
        self.assertEqual(set(record), VERDICT_FIELDS)
        for result in (direct, record):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def _append_unicode_nonstage_historical_ci_note(self, suffix):
        key = "8001"
        self.envelope["raw_ci_runner_logs"][key] += (
            "\nprivate-unicode-ci-canary " + suffix)
        self._refingerprint_portable_synthetic_ci_log(key)

    def test_utf8_emoji_ci_log_receipt_counts_bytes_not_chars(self):
        self._append_unicode_nonstage_historical_ci_note("🚀")
        raw = self.envelope["raw_ci_runner_logs"]["8001"]
        self.assertGreater(len(raw.encode("utf-8")), len(raw))
        self.assertEqual(self.envelope["raw_ci_log_receipts"]["8001"][
            "byte_count"], len(raw.encode("utf-8")))
        self._assert_unicode_log_receipt_parity(True)

    def test_utf8_accent_ci_log_note_rehashed_is_source_only(self):
        self._append_unicode_nonstage_historical_ci_note("é")
        self._assert_unicode_log_receipt_parity(True)

    def test_utf8_supplementary_ci_log_note_rehashed_is_source_only(self):
        self._append_unicode_nonstage_historical_ci_note("\U00010400")
        self._assert_unicode_log_receipt_parity(True)

    def test_utf8_combining_ci_log_note_rehashed_is_source_only(self):
        self._append_unicode_nonstage_historical_ci_note("e\u0301")
        self._assert_unicode_log_receipt_parity(True)

    def test_utf8_log_wrong_character_count_receipt_fails_closed(self):
        self._append_unicode_nonstage_historical_ci_note("🚀")
        raw = self.envelope["raw_ci_runner_logs"]["8001"]
        receipt = self.envelope["raw_ci_log_receipts"]["8001"]
        receipt["byte_count"] = len(raw)
        self.assertNotEqual(receipt["byte_count"], len(raw.encode("utf-8")))
        self._assert_unicode_log_receipt_parity(False)

    def test_utf8_log_stale_digest_after_unicode_edit_fails_closed(self):
        original_sha = self.envelope["raw_ci_log_receipts"]["8001"][
            "text_sha256"]
        self._append_unicode_nonstage_historical_ci_note("🚀")
        self.envelope["raw_ci_log_receipts"]["8001"][
            "text_sha256"] = original_sha
        self._assert_unicode_log_receipt_parity(False)

    def test_utf8_log_wrong_receipt_job_id_still_fails_closed(self):
        self._append_unicode_nonstage_historical_ci_note("é")
        self.envelope["raw_ci_log_receipts"]["8001"]["job_id"] = (
            self.envelope["raw_ci_log_receipts"]["8000"]["job_id"])
        self._assert_unicode_log_receipt_parity(False)

    def test_utf8_log_rehashed_wrong_checkout_identity_still_fails(self):
        self._append_unicode_nonstage_historical_ci_note("🚀")
        text = self.envelope["raw_ci_runner_logs"]["8001"]
        self.envelope["raw_ci_runner_logs"]["8001"] = text.replace(
            "/1649/merge", "/9999/merge")
        self._refingerprint_portable_synthetic_ci_log("8001")
        self._assert_unicode_log_receipt_parity(False)

    def test_utf8_log_nonstage_annual_claim_does_not_confer_permission(self):
        self._append_unicode_nonstage_historical_ci_note(
            "🚀 can_authorize_annual_run=true")
        self._assert_unicode_log_receipt_parity(True)

    def test_utf8_log_clean_baseline_is_source_consistency_only(self):
        self._assert_unicode_log_receipt_parity(True)

    def _append_phase3_unicode_nonstage_note(self, note):
        self.envelope["raw_ci_runner_logs"]["8000"] += (
            "\nprivate-phase3-unicode-note " + note)
        self._refingerprint_portable_synthetic_ci_log("8000")

    def _assert_phase3_unicode_receipt_parity(self, expect_source_consistency):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        raw = json.dumps(self.envelope, ensure_ascii=False)
        direct = self.verdict()
        parsed = review_bundle_json_text(raw)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        record = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(record["diagnostics"], list(parsed["diagnostics"]))
        self.assertEqual(record["source_consistency"],
                         parsed["source_consistency"])
        self.assertEqual(parsed["source_consistency"],
                         expect_source_consistency)
        self.assertEqual(status, 0 if expect_source_consistency else 2)
        self.assertNotIn("private-phase3-unicode-note", out.getvalue())
        self.assertEqual(set(record), VERDICT_FIELDS)
        for result in (direct, record):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_phase3_unicode_rehashed_nonstage_log_remains_source_only(self):
        self._append_phase3_unicode_nonstage_note("🚀")
        self._assert_phase3_unicode_receipt_parity(True)

    def test_phase3_unicode_rehashed_accented_log_remains_source_only(self):
        self._append_phase3_unicode_nonstage_note("café")
        self._assert_phase3_unicode_receipt_parity(True)

    def test_phase3_unicode_rehashed_approval_claim_not_authorizing(self):
        self._append_phase3_unicode_nonstage_note(
            "🚀 protected-annual-run385-approved")
        self._assert_phase3_unicode_receipt_parity(True)

    def test_phase3_unicode_receipt_uses_utf8_bytes_not_characters(self):
        self._append_phase3_unicode_nonstage_note("🚀")
        raw = self.envelope["raw_ci_runner_logs"]["8000"]
        receipt = self.envelope["raw_ci_log_receipts"]["8000"]
        self.assertGreater(len(raw.encode("utf-8")), len(raw))
        self.assertEqual(receipt["byte_count"], len(raw.encode("utf-8")))
        self._assert_phase3_unicode_receipt_parity(True)

    def test_phase3_unicode_wrong_char_count_refused_after_rehash(self):
        self._append_phase3_unicode_nonstage_note("🚀")
        raw = self.envelope["raw_ci_runner_logs"]["8000"]
        self.envelope["raw_ci_log_receipts"]["8000"][
            "byte_count"] = len(raw)
        self._assert_phase3_unicode_receipt_parity(False)

    def test_phase3_unicode_stale_receipt_digest_refused(self):
        previous = self.envelope["raw_ci_log_receipts"]["8000"][
            "text_sha256"]
        self._append_phase3_unicode_nonstage_note("🚀")
        self.envelope["raw_ci_log_receipts"]["8000"][
            "text_sha256"] = previous
        self._assert_phase3_unicode_receipt_parity(False)

    def test_phase3_unicode_rehashed_wrong_checkout_ref_refused(self):
        self._append_phase3_unicode_nonstage_note("🚀")
        old = self.envelope["raw_ci_runner_logs"]["8000"]
        self.assertIn("/1649/merge", old)
        self.envelope["raw_ci_runner_logs"]["8000"] = old.replace(
            "/1649/merge", "/9999/merge")
        self._refingerprint_portable_synthetic_ci_log("8000")
        self._assert_phase3_unicode_receipt_parity(False)

    def test_phase3_unicode_rehashed_wrong_artifact_id_refused(self):
        self._append_phase3_unicode_nonstage_note("🚀")
        old = self.envelope["raw_ci_runner_logs"]["8000"]
        self.assertIn("7777", old)
        self.envelope["raw_ci_runner_logs"]["8000"] = old.replace(
            "7777", "8888")
        self._refingerprint_portable_synthetic_ci_log("8000")
        self._assert_phase3_unicode_receipt_parity(False)

    def test_phase3_unicode_wrong_receipt_job_binding_refused(self):
        self._append_phase3_unicode_nonstage_note("🚀")
        self.envelope["raw_ci_log_receipts"]["8000"]["job_id"] = (
            self.envelope["raw_ci_log_receipts"]["8001"]["job_id"])
        self._assert_phase3_unicode_receipt_parity(False)

    def test_phase3_clean_baseline_remains_non_authorizing(self):
        self._assert_phase3_unicode_receipt_parity(True)

    def _assert_nfkc_path_alias_is_preflight_refused(self, first, second,
                                                    cross_map=False):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        from unittest.mock import patch
        self.assertNotEqual(first, second)
        self.assertTrue(_reviewed_source_path(first))
        self.assertTrue(_reviewed_source_path(second))
        self.assertEqual(_portable_source_path_identity(first),
                         _portable_source_path_identity(second))
        payload = base64.b64encode(b"synthetic").decode("ascii")
        self.envelope["changed_bytes_b64"] = {first: payload}
        if cross_map:
            self.envelope["ci_workflow_bytes_b64"] = {second: payload}
            diagnostic = "BUNDLE_SOURCE_CROSSMAP_COLLISION_UNREVIEWED"
        else:
            self.envelope["changed_bytes_b64"][second] = payload
            self.envelope["ci_workflow_bytes_b64"] = {}
            diagnostic = "BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED"
        raw = json.dumps(self.envelope, ensure_ascii=False)
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=AssertionError("must not source review")) as nested:
            direct = self.verdict()
            parsed = review_bundle_json_text(raw)
        nested.assert_not_called()
        self.assertEqual(direct, parsed)
        self.assertEqual(direct["diagnostics"], (diagnostic,))
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(status, 2)
        self.assertEqual(emitted["diagnostics"], [diagnostic])
        self.assertNotIn(first, out.getvalue())
        self.assertNotIn(second, out.getvalue())
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertFalse(emitted["independent_original_os_proof"])
        self.assertFalse(emitted["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(emitted["can_authorize_annual_run"])

    def test_nfkc_ligature_ffi_source_alias_is_rejected(self):
        self._assert_nfkc_path_alias_is_preflight_refused(
            "tests/oﬃce.py", "tests/office.py")

    def test_nfkc_circled_letter_source_alias_is_rejected(self):
        self._assert_nfkc_path_alias_is_preflight_refused(
            "tests/ⓐ.py", "tests/a.py")

    def test_nfkc_superscript_digit_source_alias_is_rejected(self):
        self._assert_nfkc_path_alias_is_preflight_refused(
            "tests/⁵.py", "tests/5.py")

    def test_nfkc_double_struck_letter_source_alias_is_rejected(self):
        self._assert_nfkc_path_alias_is_preflight_refused(
            "tests/ℝ.py", "tests/R.py")

    def test_nfkc_roman_numeral_source_alias_is_rejected(self):
        self._assert_nfkc_path_alias_is_preflight_refused(
            "tests/Ⅳ.py", "tests/IV.py")

    def test_nfkc_modifier_letter_source_alias_is_rejected(self):
        self._assert_nfkc_path_alias_is_preflight_refused(
            "tests/ᵃ.py", "tests/a.py")

    def test_nfkc_fullwidth_letter_source_alias_is_rejected(self):
        self._assert_nfkc_path_alias_is_preflight_refused(
            "tests/Ｋ.py", "tests/K.py")

    def test_nfkc_fi_ligature_crossmap_alias_is_rejected(self):
        self._assert_nfkc_path_alias_is_preflight_refused(
            "tests/ﬁle.py", "tests/file.py", cross_map=True)

    def test_nfkc_circled_letter_crossmap_alias_is_rejected(self):
        self._assert_nfkc_path_alias_is_preflight_refused(
            "tests/ⓐ.py", "tests/a.py", cross_map=True)

    def test_nfkc_distinct_directories_are_not_false_collision(self):
        payload = base64.b64encode(b"synthetic").decode("ascii")
        self.envelope["changed_bytes_b64"] = {
            "tests/oﬃce.py": payload,
            "docs/office.py": payload}
        self.envelope["ci_workflow_bytes_b64"] = {}
        result = self.verdict()
        self.assertNotIn("BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED",
                         result["diagnostics"])
        self.assertNotIn("BUNDLE_SOURCE_CROSSMAP_COLLISION_UNREVIEWED",
                         result["diagnostics"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_nfkc_clean_synthetic_bundle_stays_source_only(self):
        original = self.verdict()
        parsed = review_bundle_json_text(json.dumps(
            self.envelope, ensure_ascii=False))
        self.assertEqual(original, parsed)
        self.assertEqual(original["diagnostics"], ())
        self.assertTrue(original["source_consistency"])
        self.assertFalse(original["independent_original_os_proof"])
        self.assertFalse(original["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(original["can_authorize_annual_run"])

    def _assert_canonical_binary_source_mutation_rejected(self, changed):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.assertEqual(type(changed), bytes)
        canonical = base64.b64encode(changed).decode("ascii")
        self.assertEqual(base64.b64encode(
            base64.b64decode(canonical, validate=True)).decode("ascii"),
            canonical)
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = canonical
        direct = self.verdict()
        raw = json.dumps(self.envelope, ensure_ascii=True)
        parsed = review_bundle_json_text(raw)
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), output)
        emitted = json.loads(output.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 2)
        self.assertFalse(direct["source_consistency"])
        self.assertTrue(direct["diagnostics"])
        self.assertNotIn("BUNDLE_SOURCE_B64_UNREVIEWED",
                         direct["diagnostics"])
        self.assertNotIn("BUNDLE_SOURCE_B64_NONCANONICAL",
                         direct["diagnostics"])
        self.assertEqual(emitted["diagnostics"],
                         list(direct["diagnostics"]))
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        if canonical:
            self.assertNotIn(canonical, output.getvalue())
        self.assertNotIn("changed_bytes_b64", output.getvalue())
        for verdict in (direct, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_canonical_raw_source_null_byte_fails_source_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(b"\x00")

    def test_canonical_raw_source_invalid_utf8_fails_source_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(b"\xff\xfe")

    def test_canonical_raw_source_utf8_bom_fails_source_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"\xef\xbb\xbf# Source-only\n")

    def test_canonical_raw_source_crlf_fails_source_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"# Source-only\r\n")

    def test_canonical_raw_source_appended_nul_fails_source_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"# Source-only\n\x00")

    def test_canonical_raw_source_trailing_space_fails_source_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"# Source-only \n")

    def test_canonical_raw_source_nonascii_utf8_fails_source_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            "🚀".encode("utf-8"))

    def test_canonical_raw_source_empty_bytes_fails_source_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(b"")

    def test_canonical_raw_source_same_length_edit_fails_source_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"fail\n")

    def test_canonical_source_original_bytes_still_source_only(self):
        # Match the committed synthetic baseline, not a presumed comment.
        expected = b"pass\n"
        self.assertEqual(
            base64.b64decode(self.envelope["changed_bytes_b64"][
                "tests/sample.py"], validate=True), expected)
        direct = self.verdict()
        parsed = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(direct, parsed)
        self.assertTrue(direct["source_consistency"])
        self.assertEqual(direct["diagnostics"], ())
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def _assert_canonical_ci_workflow_mutation_refused(self, bytes_payload):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.assertEqual(type(bytes_payload), bytes)
        encoded = base64.b64encode(bytes_payload).decode("ascii")
        self.assertEqual(
            base64.b64encode(base64.b64decode(
                encoded, validate=True)).decode("ascii"), encoded)
        self.envelope["ci_workflow_bytes_b64"][
            ".github/workflows/tests.yml"] = encoded
        direct = self.verdict()
        raw = json.dumps(self.envelope, ensure_ascii=True)
        parsed = review_bundle_json_text(raw)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 2)
        self.assertFalse(direct["source_consistency"])
        self.assertTrue(direct["diagnostics"])
        self.assertNotIn("BUNDLE_SOURCE_B64_UNREVIEWED",
                         direct["diagnostics"])
        self.assertNotIn("BUNDLE_SOURCE_B64_NONCANONICAL",
                         direct["diagnostics"])
        self.assertEqual(emitted["diagnostics"],
                         list(direct["diagnostics"]))
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertNotIn("ci_workflow_bytes_b64", out.getvalue())
        if len(encoded) > 8:
            self.assertNotIn(encoded, out.getvalue())
        for verdict in (direct, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_canonical_workflow_empty_bytes_fail_source_identity(self):
        self._assert_canonical_ci_workflow_mutation_refused(b"")

    def test_canonical_workflow_nul_bytes_fail_source_identity(self):
        self._assert_canonical_ci_workflow_mutation_refused(b"\x00")

    def test_canonical_workflow_invalid_utf8_fail_source_identity(self):
        self._assert_canonical_ci_workflow_mutation_refused(b"\xff\xfe")

    def test_canonical_workflow_utf8_bom_fail_source_identity(self):
        self._assert_canonical_ci_workflow_mutation_refused(
            b"\xef\xbb\xbfname: synthetic\n")

    def test_canonical_workflow_newline_swap_fail_source_identity(self):
        self._assert_canonical_ci_workflow_mutation_refused(
            b"name: synthetic\r\n")

    def test_canonical_workflow_forged_dispatch_fail_source_identity(self):
        self._assert_canonical_ci_workflow_mutation_refused(
            b"name: run385\non: workflow_dispatch\n")

    def test_canonical_workflow_unicode_bytes_fail_source_identity(self):
        self._assert_canonical_ci_workflow_mutation_refused(
            "name: 🚀\n".encode("utf-8"))

    def test_canonical_workflow_appended_nul_fail_source_identity(self):
        self._assert_canonical_ci_workflow_mutation_refused(
            b"name: synthetic\n\x00")

    def test_canonical_workflow_original_fixture_source_consistency_only(self):
        original = self.verdict()
        parsed = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(original, parsed)
        self.assertEqual(original["diagnostics"], ())
        self.assertTrue(original["source_consistency"])
        self.assertFalse(original["independent_original_os_proof"])
        self.assertFalse(original["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(original["can_authorize_annual_run"])

    def _json_escaped_canonical_b64_document(self, map_name, path, mode):
        value = self.envelope[map_name][path]
        self.assertTrue(value)
        raw = json.dumps(self.envelope, sort_keys=True, separators=(",", ":"))
        needle = json.dumps(path) + ":" + json.dumps(value)
        self.assertEqual(raw.count(needle), 1)
        def escape(ch):
            return "\\u%04x" % ord(ch)
        if mode == "all":
            variant = "".join(escape(ch) for ch in value)
        elif mode == "head":
            variant = escape(value[0]) + value[1:]
        elif mode == "tail":
            variant = value[:-1] + escape(value[-1])
        else:
            raise AssertionError("unknown synthetic JSON spelling")
        changed = raw.replace(
            needle, json.dumps(path) + ':"' + variant + '"', 1)
        self.assertNotEqual(changed, raw)
        self.assertEqual(json.loads(changed), self.envelope)
        return changed

    def _assert_escaped_b64_json_parity(self, map_name, path, mode,
                                        expect_clean):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        escaped = self._json_escaped_canonical_b64_document(
            map_name, path, mode)
        original = self.verdict()
        plain_json = review_bundle_json_text(json.dumps(self.envelope))
        escaped_json = review_bundle_json_text(escaped)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(escaped), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(original, plain_json)
        self.assertEqual(original, escaped_json)
        self.assertEqual(emitted["diagnostics"],
                         list(original["diagnostics"]))
        self.assertEqual(emitted["source_consistency"],
                         original["source_consistency"])
        self.assertEqual(status, 0 if expect_clean else 2)
        self.assertEqual(original["source_consistency"], expect_clean)
        self.assertFalse(original["independent_original_os_proof"])
        self.assertFalse(original["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(original["can_authorize_annual_run"])
        self.assertFalse(emitted["independent_original_os_proof"])
        self.assertFalse(emitted["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(emitted["can_authorize_annual_run"])

    def test_json_escaped_all_changed_base64_chars_preserves_clean_evidence(self):
        self._assert_escaped_b64_json_parity(
            "changed_bytes_b64", "tests/sample.py", "all", True)

    def test_json_escaped_head_changed_base64_preserves_clean_evidence(self):
        self._assert_escaped_b64_json_parity(
            "changed_bytes_b64", "tests/sample.py", "head", True)

    def test_json_escaped_tail_changed_base64_preserves_clean_evidence(self):
        self._assert_escaped_b64_json_parity(
            "changed_bytes_b64", "tests/sample.py", "tail", True)

    def test_json_escaped_all_workflow_base64_preserves_clean_evidence(self):
        self._assert_escaped_b64_json_parity(
            "ci_workflow_bytes_b64", ".github/workflows/tests.yml",
            "all", True)

    def test_json_escaped_head_workflow_base64_preserves_clean_evidence(self):
        self._assert_escaped_b64_json_parity(
            "ci_workflow_bytes_b64", ".github/workflows/tests.yml",
            "head", True)

    def test_json_escaped_tail_workflow_base64_preserves_clean_evidence(self):
        self._assert_escaped_b64_json_parity(
            "ci_workflow_bytes_b64", ".github/workflows/tests.yml",
            "tail", True)

    def test_json_escaped_altered_changed_source_still_fails_identity(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = (
            base64.b64encode(b"synthetic-forged-source").decode("ascii"))
        self._assert_escaped_b64_json_parity(
            "changed_bytes_b64", "tests/sample.py", "all", False)

    def test_json_escaped_altered_workflow_source_still_fails_identity(self):
        self.envelope["ci_workflow_bytes_b64"][
            ".github/workflows/tests.yml"] = (
            base64.b64encode(b"synthetic-forged-workflow").decode("ascii"))
        self._assert_escaped_b64_json_parity(
            "ci_workflow_bytes_b64", ".github/workflows/tests.yml",
            "all", False)

    def test_json_escaped_malformed_base64_still_fails_closed(self):
        self.envelope["changed_bytes_b64"]["tests/sample.py"] = "invalid%"
        self._assert_escaped_b64_json_parity(
            "changed_bytes_b64", "tests/sample.py", "all", False)
        self.assertEqual(self.verdict()["diagnostics"],
                         ("BUNDLE_SOURCE_B64_UNREVIEWED",))

    def _assert_escaped_invalid_base64_character_refused(self, category,
                                                          path, code_point):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.assertLessEqual(code_point, 0xFFFF)
        value = self.envelope[category][path]
        replacement = value[0] + chr(code_point) + value[1:]
        raw = json.dumps(self.envelope, sort_keys=True, separators=(",", ":"))
        needle = json.dumps(path) + ":" + json.dumps(value)
        self.assertEqual(raw.count(needle), 1)
        escaped = (value[0] + "\\u%04x" % code_point + value[1:])
        raw = raw.replace(needle, json.dumps(path) + ':"' +
                          escaped + '"', 1)
        self.assertEqual(json.loads(raw)[category][path], replacement)
        self.envelope[category][path] = replacement
        direct = self.verdict()
        parsed = review_bundle_json_text(raw)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 2)
        self.assertEqual(direct["diagnostics"],
                         ("BUNDLE_SOURCE_B64_UNREVIEWED",))
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_SOURCE_B64_UNREVIEWED"])
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertFalse(emitted["source_consistency"])
        self.assertNotIn("changed_bytes_b64", out.getvalue())
        self.assertNotIn("ci_workflow_bytes_b64", out.getvalue())
        self.assertFalse(emitted["independent_original_os_proof"])
        self.assertFalse(emitted["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(emitted["can_authorize_annual_run"])

    def test_escaped_lf_inside_changed_base64_is_rejected(self):
        self._assert_escaped_invalid_base64_character_refused(
            "changed_bytes_b64", "tests/sample.py", 0x000A)

    def test_escaped_cr_inside_changed_base64_is_rejected(self):
        self._assert_escaped_invalid_base64_character_refused(
            "changed_bytes_b64", "tests/sample.py", 0x000D)

    def test_escaped_tab_inside_changed_base64_is_rejected(self):
        self._assert_escaped_invalid_base64_character_refused(
            "changed_bytes_b64", "tests/sample.py", 0x0009)

    def test_escaped_nul_inside_changed_base64_is_rejected(self):
        self._assert_escaped_invalid_base64_character_refused(
            "changed_bytes_b64", "tests/sample.py", 0x0000)

    def test_escaped_nbsp_inside_changed_base64_is_rejected(self):
        self._assert_escaped_invalid_base64_character_refused(
            "changed_bytes_b64", "tests/sample.py", 0x00A0)

    def test_escaped_zero_width_space_inside_changed_base64_is_rejected(self):
        self._assert_escaped_invalid_base64_character_refused(
            "changed_bytes_b64", "tests/sample.py", 0x200B)

    def test_escaped_fullwidth_a_inside_changed_base64_is_rejected(self):
        self._assert_escaped_invalid_base64_character_refused(
            "changed_bytes_b64", "tests/sample.py", 0xFF21)

    def test_escaped_bidi_override_inside_changed_base64_is_rejected(self):
        self._assert_escaped_invalid_base64_character_refused(
            "changed_bytes_b64", "tests/sample.py", 0x202E)

    def test_escaped_zero_width_joiner_inside_workflow_base64_is_rejected(self):
        self._assert_escaped_invalid_base64_character_refused(
            "ci_workflow_bytes_b64", ".github/workflows/tests.yml", 0x200D)

    def test_escaped_unicode_accent_inside_workflow_base64_is_rejected(self):
        self._assert_escaped_invalid_base64_character_refused(
            "ci_workflow_bytes_b64", ".github/workflows/tests.yml", 0x00E9)

    def test_escaped_base64_character_guard_preserves_clean_source_only(self):
        direct = self.verdict()
        json_result = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(direct, json_result)
        self.assertEqual(direct["diagnostics"], ())
        self.assertTrue(direct["source_consistency"])
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def test_original_changed_source_fixture_has_expected_sha_bytes(self):
        import hashlib
        payload = base64.b64decode(self.envelope["changed_bytes_b64"][
            "tests/sample.py"], validate=True)
        self.assertEqual(payload, b"pass\n")
        self.assertEqual(len(payload), 5)
        self.assertEqual(hashlib.sha256(payload).hexdigest(),
                         hashlib.sha256(b"pass\n").hexdigest())
        self.assertEqual(self.verdict()["diagnostics"], ())
        self.assertFalse(self.verdict()["can_authorize_annual_run"])

    def test_real_fixture_crlf_edit_fails_reviewed_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"pass\r\n")

    def test_real_fixture_trailing_space_edit_fails_reviewed_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"pass \n")

    def test_real_fixture_bom_edit_fails_reviewed_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"\xef\xbb\xbfpass\n")

    def test_real_fixture_append_nul_edit_fails_reviewed_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"pass\n\x00")

    def test_real_fixture_same_length_uppercase_fails_reviewed_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"PASS\n")

    def test_real_fixture_same_length_keyword_edit_fails_reviewed_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"fail\n")

    def test_real_fixture_without_final_newline_fails_reviewed_identity(self):
        self._assert_canonical_binary_source_mutation_rejected(
            b"pass")

    def _assert_json_escaped_key_spelling_keeps_source_only(self, category,
                                                            key, offset):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.assertLess(offset, len(key))
        self.assertLess(ord(key[offset]), 128)
        encoded = json.dumps(self.envelope, sort_keys=True,
                             separators=(",", ":"))
        inner = json.dumps(self.envelope[category][key], sort_keys=True,
                           separators=(",", ":"))
        literal = json.dumps(key) + ":" + inner
        self.assertEqual(encoded.count(literal), 1)
        alias = ('"' + key[:offset] + '\\u%04x' % ord(key[offset]) +
                 key[offset+1:] + '"')
        self.assertNotEqual(alias, json.dumps(key))
        rewritten = encoded.replace(literal, alias + ":" + inner, 1)
        self.assertEqual(json.loads(rewritten), self.envelope)
        original = self.verdict()
        parsed = review_bundle_json_text(rewritten)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(rewritten), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(original, parsed)
        self.assertEqual(status, 0)
        self.assertEqual(original["diagnostics"], ())
        self.assertTrue(original["source_consistency"])
        self.assertEqual(emitted["diagnostics"], [])
        self.assertTrue(emitted["source_consistency"])
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        for result in (original, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_json_escaped_changed_source_first_path_letter_is_equivalent(self):
        self._assert_json_escaped_key_spelling_keeps_source_only(
            "changed_bytes_b64", "tests/sample.py", 0)

    def test_json_escaped_changed_source_path_separator_is_equivalent(self):
        self._assert_json_escaped_key_spelling_keeps_source_only(
            "changed_bytes_b64", "tests/sample.py", 5)

    def test_json_escaped_ci_workflow_first_path_dot_is_equivalent(self):
        self._assert_json_escaped_key_spelling_keeps_source_only(
            "ci_workflow_bytes_b64", ".github/workflows/tests.yml", 0)

    def test_json_escaped_ci_workflow_path_separator_is_equivalent(self):
        self._assert_json_escaped_key_spelling_keeps_source_only(
            "ci_workflow_bytes_b64", ".github/workflows/tests.yml", 7)

    def test_json_escaped_jobs_run_map_key_is_equivalent(self):
        self._assert_json_escaped_key_spelling_keeps_source_only(
            "jobs_by_run", "8000", 0)

    def test_json_escaped_checkout_run_map_key_is_equivalent(self):
        self._assert_json_escaped_key_spelling_keeps_source_only(
            "checkout_by_run", "8000", 1)

    def test_json_escaped_raw_log_run_map_key_is_equivalent(self):
        self._assert_json_escaped_key_spelling_keeps_source_only(
            "raw_ci_runner_logs", "8001", 2)

    def test_json_escaped_receipt_run_map_key_is_equivalent(self):
        self._assert_json_escaped_key_spelling_keeps_source_only(
            "raw_ci_log_receipts", "8001", 3)

    def test_json_escaped_schema_root_key_is_equivalent(self):
        raw = json.dumps(self.envelope, sort_keys=True,
                         separators=(",", ":"))
        before = '"schema":'
        self.assertEqual(raw.count(before), 1)
        rewritten = raw.replace(before, '"\\u0073chema":', 1)
        self.assertEqual(json.loads(rewritten), self.envelope)
        self.assertEqual(review_bundle_json_text(rewritten), self.verdict())
        self.assertTrue(self.verdict()["source_consistency"])
        self.assertFalse(self.verdict()["can_authorize_annual_run"])

    def test_json_escaped_schema_value_is_equivalent(self):
        raw = json.dumps(self.envelope, sort_keys=True,
                         separators=(",", ":"))
        before = '"schema":' + json.dumps(ENVELOPE_SCHEMA)
        self.assertEqual(raw.count(before), 1)
        encoded_schema = '"\\u%04x%s"' % (
            ord(ENVELOPE_SCHEMA[0]), ENVELOPE_SCHEMA[1:])
        rewritten = raw.replace(before, '"schema":' + encoded_schema, 1)
        self.assertEqual(json.loads(rewritten), self.envelope)
        self.assertEqual(review_bundle_json_text(rewritten), self.verdict())
        self.assertFalse(self.verdict()["independent_original_os_proof"])
        self.assertFalse(self.verdict()["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(self.verdict()["can_authorize_annual_run"])

    def _assert_canonical_doc_source_bytes_still_need_tree_identity(self, payload):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.assertEqual(type(payload), bytes)
        original = b"# Source-only\n"
        self.assertNotEqual(payload, original)
        encoded = base64.b64encode(payload).decode("ascii")
        self.assertEqual(base64.b64encode(
            base64.b64decode(encoded, validate=True)).decode("ascii"),
            encoded)
        self.envelope["changed_bytes_b64"]["docs/sample.md"] = encoded
        direct = self.verdict()
        json_string = json.dumps(self.envelope)
        parsed = review_bundle_json_text(json_string)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(json_string), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(status, 2)
        self.assertEqual(direct, parsed)
        self.assertFalse(direct["source_consistency"])
        self.assertTrue(direct["diagnostics"])
        self.assertNotIn("BUNDLE_SOURCE_B64_UNREVIEWED",
                         direct["diagnostics"])
        self.assertNotIn("BUNDLE_SOURCE_B64_NONCANONICAL",
                         direct["diagnostics"])
        self.assertEqual(emitted["diagnostics"],
                         list(direct["diagnostics"]))
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertNotIn("changed_bytes_b64", out.getvalue())
        for v in (direct, emitted):
            self.assertFalse(v["independent_original_os_proof"])
            self.assertFalse(v["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(v["can_authorize_annual_run"])

    def test_actual_markdown_fixture_bytes_are_source_only(self):
        actual = base64.b64decode(
            self.envelope["changed_bytes_b64"]["docs/sample.md"],
            validate=True)
        self.assertEqual(actual, b"# Source-only\n")
        self.assertEqual(self.verdict()["diagnostics"], ())
        self.assertTrue(self.verdict()["source_consistency"])
        self.assertFalse(self.verdict()["can_authorize_annual_run"])

    def test_canonical_markdown_same_length_case_edit_fails_identity(self):
        self._assert_canonical_doc_source_bytes_still_need_tree_identity(
            b"# source-only\n")

    def test_canonical_markdown_crlf_edit_fails_identity(self):
        self._assert_canonical_doc_source_bytes_still_need_tree_identity(
            b"# Source-only\r\n")

    def test_canonical_markdown_bom_edit_fails_identity(self):
        self._assert_canonical_doc_source_bytes_still_need_tree_identity(
            b"\xef\xbb\xbf# Source-only\n")

    def test_canonical_markdown_trailing_space_edit_fails_identity(self):
        self._assert_canonical_doc_source_bytes_still_need_tree_identity(
            b"# Source-only \n")

    def test_canonical_markdown_nul_suffix_fails_identity(self):
        self._assert_canonical_doc_source_bytes_still_need_tree_identity(
            b"# Source-only\n\x00")

    def test_canonical_markdown_empty_bytes_fail_identity(self):
        self._assert_canonical_doc_source_bytes_still_need_tree_identity(
            b"")

    def test_canonical_markdown_wrong_heading_text_fails_identity(self):
        self._assert_canonical_doc_source_bytes_still_need_tree_identity(
            b"# Annual-approved\n")

    def test_canonical_markdown_no_final_newline_fails_identity(self):
        self._assert_canonical_doc_source_bytes_still_need_tree_identity(
            b"# Source-only")

    def test_canonical_markdown_unicode_heading_fails_identity(self):
        self._assert_canonical_doc_source_bytes_still_need_tree_identity(
            "# Sôurce-only\n".encode("utf-8"))

    def _assert_swapped_canonical_source_evidence_is_not_tree_proof(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        for encoded in self.envelope["changed_bytes_b64"].values():
            raw = base64.b64decode(encoded, validate=True)
            self.assertEqual(base64.b64encode(raw).decode("ascii"), encoded)
        direct = self.verdict()
        raw = json.dumps(self.envelope, sort_keys=True)
        parsed = review_bundle_json_text(raw)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 2)
        self.assertFalse(direct["source_consistency"])
        self.assertTrue(direct["diagnostics"])
        self.assertNotIn("BUNDLE_SOURCE_B64_UNREVIEWED",
                         direct["diagnostics"])
        self.assertNotIn("BUNDLE_SOURCE_B64_NONCANONICAL",
                         direct["diagnostics"])
        self.assertEqual(emitted["diagnostics"],
                         list(direct["diagnostics"]))
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        for result in (direct, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def _swap_two_changed_source_payloads(self):
        pairs = self.envelope["changed_bytes_b64"]
        self.assertEqual(base64.b64decode(pairs["tests/sample.py"]),
                         b"pass\n")
        self.assertEqual(base64.b64decode(pairs["docs/sample.md"]),
                         b"# Source-only\n")
        pairs["tests/sample.py"], pairs["docs/sample.md"] = (
            pairs["docs/sample.md"], pairs["tests/sample.py"])

    def test_changed_sources_swapped_bytes_fail_tree_identity(self):
        self._swap_two_changed_source_payloads()
        self._assert_swapped_canonical_source_evidence_is_not_tree_proof()

    def test_changed_sources_swapped_bytes_with_reversed_map_fail(self):
        self._swap_two_changed_source_payloads()
        self.envelope["changed_bytes_b64"] = dict(
            reversed(list(self.envelope["changed_bytes_b64"].items())))
        self._assert_swapped_canonical_source_evidence_is_not_tree_proof()

    def test_changed_sources_swapped_and_rehashed_nodes_fail_tree_identity(self):
        self._swap_two_changed_source_payloads()
        for path, encoded in self.envelope["changed_bytes_b64"].items():
            self.envelope["nodes"][path]["sha"] = (
                composite.ci_source.git_blob_id(
                    base64.b64decode(encoded, validate=True)))
        self._assert_swapped_canonical_source_evidence_is_not_tree_proof()

    def test_changed_sources_swapped_and_changed_compare_counts_fail(self):
        self._swap_two_changed_source_payloads()
        self.envelope["compare"]["files"][0]["changes"] = 5
        self._assert_swapped_canonical_source_evidence_is_not_tree_proof()

    def test_changed_sources_swapped_with_false_annual_claim_fail(self):
        self._swap_two_changed_source_payloads()
        self.envelope["pr"]["can_authorize_annual_run"] = True
        self._assert_swapped_canonical_source_evidence_is_not_tree_proof()

    def test_changed_sources_copy_docs_bytes_into_python_path_fail(self):
        pairs = self.envelope["changed_bytes_b64"]
        pairs["tests/sample.py"] = pairs["docs/sample.md"]
        self._assert_swapped_canonical_source_evidence_is_not_tree_proof()

    def test_changed_sources_copy_python_bytes_into_docs_path_fail(self):
        pairs = self.envelope["changed_bytes_b64"]
        pairs["docs/sample.md"] = pairs["tests/sample.py"]
        self._assert_swapped_canonical_source_evidence_is_not_tree_proof()

    def test_changed_sources_swap_rehashed_node_and_fake_tree_sha_fail(self):
        self._swap_two_changed_source_payloads()
        for path, encoded in self.envelope["changed_bytes_b64"].items():
            self.envelope["nodes"][path]["sha"] = (
                composite.ci_source.git_blob_id(
                    base64.b64decode(encoded, validate=True)))
        self.envelope["tree"]["sha"] = "a"*40
        self._assert_swapped_canonical_source_evidence_is_not_tree_proof()

    def test_changed_sources_unswapped_fixture_remains_source_only(self):
        raw = json.dumps(self.envelope)
        direct = self.verdict()
        self.assertEqual(direct, review_bundle_json_text(raw))
        self.assertTrue(direct["source_consistency"])
        self.assertEqual(direct["diagnostics"], ())
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def _assert_changed_tree_node_mode_refused(self, code):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        direct = self.verdict()
        raw = json.dumps(self.envelope)
        parsed = review_bundle_json_text(raw)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 2)
        self.assertFalse(direct["source_consistency"])
        self.assertIn(code, direct["diagnostics"])
        self.assertEqual(emitted["diagnostics"],
                         list(direct["diagnostics"]))
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertNotIn("changed_bytes_b64", out.getvalue())
        for result in (direct, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_portable_test_leaf_executable_mode_cannot_override_source(self):
        self.envelope["nodes"]["tests/sample.py"]["mode"] = "100755"
        self._assert_changed_tree_node_mode_refused(
            "GIT_TREE_LEAF_MODE_DRIFT")

    def test_portable_docs_leaf_executable_mode_cannot_override_source(self):
        self.envelope["nodes"]["docs/sample.md"]["mode"] = "100755"
        self._assert_changed_tree_node_mode_refused(
            "GIT_TREE_LEAF_MODE_DRIFT")

    def test_portable_test_leaf_symlink_mode_cannot_override_source(self):
        self.envelope["nodes"]["tests/sample.py"]["mode"] = "120000"
        self._assert_changed_tree_node_mode_refused(
            "GIT_TREE_LEAF_MODE_DRIFT")

    def test_portable_docs_leaf_symlink_mode_cannot_override_source(self):
        self.envelope["nodes"]["docs/sample.md"]["mode"] = "120000"
        self._assert_changed_tree_node_mode_refused(
            "GIT_TREE_LEAF_MODE_DRIFT")

    def test_portable_test_leaf_gitlink_mode_cannot_override_source(self):
        self.envelope["nodes"]["tests/sample.py"] = {
            "mode": "160000", "type": "commit", "sha": "a"*40}
        self._assert_changed_tree_node_mode_refused(
            "GIT_TREE_LEAF_MODE_DRIFT")

    def test_portable_docs_leaf_tree_type_cannot_override_source(self):
        self.envelope["nodes"]["docs/sample.md"]["type"] = "tree"
        self._assert_changed_tree_node_mode_refused(
            "GIT_TREE_LEAF_MODE_DRIFT")

    def test_portable_docs_parent_symlink_cannot_override_source(self):
        self.envelope["nodes"]["docs"] = {
            "mode": "120000", "type": "blob"}
        self._assert_changed_tree_node_mode_refused(
            "GIT_TREE_DIRECTORY_MODE_DRIFT")

    def test_portable_tests_parent_regular_file_cannot_override_source(self):
        self.envelope["nodes"]["tests"] = {
            "mode": "100644", "type": "blob"}
        self._assert_changed_tree_node_mode_refused(
            "GIT_TREE_DIRECTORY_MODE_DRIFT")

    def test_portable_missing_docs_leaf_cannot_override_source(self):
        self.envelope["nodes"].pop("docs/sample.md")
        self._assert_changed_tree_node_mode_refused(
            "GIT_TREE_PATH_MISSING")

    def test_portable_tree_nodes_clean_source_is_not_annual_authority(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def _portable_snapshot_leaf(self, directory):
        root_sha = self.envelope["commit"]["tree"]["sha"]
        trees = self.envelope["full_tree_snapshots"]
        root = trees[root_sha]
        entries = [entry for entry in root["tree"]
                   if entry["path"] == directory]
        self.assertEqual(len(entries), 1)
        child = trees[entries[0]["sha"]]
        self.assertEqual(len(child["tree"]), 1)
        return child["tree"][0]

    def _assert_full_tree_snapshot_mutation_refused(self, code):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        for path, data in (("tests/sample.py", b"pass\n"),
                           ("docs/sample.md", b"# Source-only\n")):
            self.assertEqual(self.envelope["changed_bytes_b64"][path],
                             base64.b64encode(data).decode("ascii"))
            self.assertEqual(self.envelope["nodes"][path]["mode"], "100644")
            self.assertEqual(self.envelope["nodes"][path]["type"], "blob")
        direct = self.verdict()
        raw = json.dumps(self.envelope, sort_keys=True)
        parsed = review_bundle_json_text(raw)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 2)
        self.assertFalse(direct["source_consistency"])
        self.assertIn(code, direct["diagnostics"])
        self.assertEqual(emitted["diagnostics"],
                         list(direct["diagnostics"]))
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for result in (direct, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_portable_snapshot_tests_executable_leaf_refused(self):
        self._portable_snapshot_leaf("tests")["mode"] = "100755"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_snapshot_docs_executable_leaf_refused(self):
        self._portable_snapshot_leaf("docs")["mode"] = "100755"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_snapshot_tests_symlink_leaf_refused(self):
        self._portable_snapshot_leaf("tests")["mode"] = "120000"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_snapshot_docs_symlink_leaf_refused(self):
        self._portable_snapshot_leaf("docs")["mode"] = "120000"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_snapshot_docs_gitlink_leaf_refused(self):
        leaf = self._portable_snapshot_leaf("docs")
        leaf["mode"] = "160000"
        leaf["type"] = "commit"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_snapshot_tests_tree_typed_leaf_refused(self):
        self._portable_snapshot_leaf("tests")["type"] = "tree"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_snapshot_tests_blob_parent_refused(self):
        root = self.envelope["full_tree_snapshots"][
            self.envelope["commit"]["tree"]["sha"]]
        parent = next(e for e in root["tree"] if e["path"] == "tests")
        parent["mode"], parent["type"] = "100644", "blob"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_PARENT_NOT_REGULAR_TREE")

    def test_portable_snapshot_docs_symlink_parent_refused(self):
        root = self.envelope["full_tree_snapshots"][
            self.envelope["commit"]["tree"]["sha"]]
        parent = next(e for e in root["tree"] if e["path"] == "docs")
        parent["mode"], parent["type"] = "120000", "blob"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_PARENT_NOT_REGULAR_TREE")

    def test_portable_snapshot_docs_sha_points_at_python_blob_refused(self):
        leaf = self._portable_snapshot_leaf("docs")
        leaf["sha"] = self.envelope["nodes"]["tests/sample.py"]["sha"]
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH")

    def test_portable_snapshot_rehashed_executable_chain_still_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        old_root_sha = self.envelope["commit"]["tree"]["sha"]
        root = trees[old_root_sha]
        tests_parent = next(e for e in root["tree"] if e["path"] == "tests")
        old_child_sha = tests_parent["sha"]
        child = trees.pop(old_child_sha)
        self.assertEqual(child["tree"][0]["path"], "sample.py")
        child["tree"][0]["mode"] = "100755"
        new_child_sha = composite.tree_chain.reviewed_git_tree_sha(
            child["tree"])
        self.assertNotEqual(new_child_sha, old_child_sha)
        child["sha"] = new_child_sha
        trees[new_child_sha] = child
        tests_parent["sha"] = new_child_sha
        new_root_sha = composite.tree_chain.reviewed_git_tree_sha(
            root["tree"])
        self.assertNotEqual(new_root_sha, old_root_sha)
        root["sha"] = new_root_sha
        trees.pop(old_root_sha)
        trees[new_root_sha] = root
        self.envelope["commit"]["tree"]["sha"] = new_root_sha
        self.envelope["tree"]["sha"] = new_root_sha
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_snapshot_clean_tree_remains_source_only(self):
        direct = self.verdict()
        parsed = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(direct, parsed)
        self.assertEqual(direct["diagnostics"], ())
        self.assertTrue(direct["source_consistency"])
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def _portable_snapshot_parent_child(self, directory):
        trees = self.envelope["full_tree_snapshots"]
        root_sha = self.envelope["commit"]["tree"]["sha"]
        root = trees[root_sha]
        parents = [entry for entry in root["tree"]
                   if entry["path"] == directory]
        self.assertEqual(len(parents), 1)
        child_sha = parents[0]["sha"]
        self.assertIn(child_sha, trees)
        return trees, root_sha, child_sha

    def test_portable_full_snapshot_missing_root_object_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        root_sha = self.envelope["commit"]["tree"]["sha"]
        trees.pop(root_sha)
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_full_snapshot_missing_tests_subtree_refused(self):
        trees, _, child_sha = self._portable_snapshot_parent_child("tests")
        trees.pop(child_sha)
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_full_snapshot_missing_docs_subtree_refused(self):
        trees, _, child_sha = self._portable_snapshot_parent_child("docs")
        trees.pop(child_sha)
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_full_snapshot_truncated_tests_subtree_refused(self):
        trees, _, child_sha = self._portable_snapshot_parent_child("tests")
        trees[child_sha]["truncated"] = True
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_full_snapshot_truncated_docs_subtree_refused(self):
        trees, _, child_sha = self._portable_snapshot_parent_child("docs")
        trees[child_sha]["truncated"] = True
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_full_snapshot_duplicate_docs_leaf_refused(self):
        trees, _, child_sha = self._portable_snapshot_parent_child("docs")
        entries = trees[child_sha]["tree"]
        entries.append(dict(entries[0]))
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED")

    def test_portable_full_snapshot_duplicate_tests_parent_refused(self):
        trees, root_sha, _ = self._portable_snapshot_parent_child("tests")
        entries = trees[root_sha]["tree"]
        parent = next(e for e in entries if e["path"] == "tests")
        entries.append(dict(parent))
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED")

    def test_portable_full_snapshot_missing_docs_leaf_refused(self):
        trees, _, child_sha = self._portable_snapshot_parent_child("docs")
        trees[child_sha]["tree"].clear()
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED")

    def test_portable_full_snapshot_renamed_tests_leaf_refused(self):
        self._portable_snapshot_leaf("tests")["path"] = "different.py"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED")

    def test_portable_full_snapshot_orphaned_extra_object_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        self.assertNotIn("f"*40, trees)
        trees["f"*40] = {
            "sha": "f"*40, "truncated": False, "tree": []}
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_SNAPSHOT_INVENTORY_UNREVIEWED")

    def test_portable_full_snapshot_wrong_root_self_sha_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        root_sha = self.envelope["commit"]["tree"]["sha"]
        trees[root_sha]["sha"] = "f"*40
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_full_snapshot_wrong_docs_self_sha_refused(self):
        trees, _, child_sha = self._portable_snapshot_parent_child("docs")
        trees[child_sha]["sha"] = "f"*40
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_wire_root_entries_reordered_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        root_sha = self.envelope["commit"]["tree"]["sha"]
        trees[root_sha]["tree"].reverse()
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH")

    def test_portable_wire_docs_leaf_uppercase_sha_refused(self):
        self._portable_snapshot_leaf("docs")["sha"] = "A"*40
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_SHA_UNREVIEWED")

    def test_portable_wire_tests_leaf_short_sha_refused(self):
        self._portable_snapshot_leaf("tests")["sha"] = "a"*39
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_SHA_UNREVIEWED")

    def test_portable_wire_root_parent_nonhex_sha_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        root = trees[self.envelope["commit"]["tree"]["sha"]]
        next(e for e in root["tree"] if e["path"] == "tests")["sha"] = "z"*40
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_SHA_UNREVIEWED")

    def test_portable_wire_docs_leaf_slash_path_refused(self):
        self._portable_snapshot_leaf("docs")["path"] = "nested/sample.md"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH")

    def test_portable_wire_docs_leaf_nul_path_refused(self):
        self._portable_snapshot_leaf("docs")["path"] = "sample.md\x00forged"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH")

    def test_portable_wire_root_parent_noncanonical_tree_mode_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        root = trees[self.envelope["commit"]["tree"]["sha"]]
        next(e for e in root["tree"] if e["path"] == "docs")["mode"] = "40000"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH")

    def test_portable_wire_tests_leaf_list_mode_refused(self):
        self._portable_snapshot_leaf("tests")["mode"] = ["100644"]
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH")

    def test_portable_wire_docs_leaf_missing_sha_refused(self):
        self._portable_snapshot_leaf("docs").pop("sha")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_SHA_UNREVIEWED")

    def test_portable_wire_docs_child_tree_object_not_array_refused(self):
        trees, _, child_sha = self._portable_snapshot_parent_child("docs")
        trees[child_sha]["tree"] = {}
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_ENTRIES_UNREVIEWED")

    def test_portable_wire_tests_child_null_entry_refused(self):
        trees, _, child_sha = self._portable_snapshot_parent_child("tests")
        trees[child_sha]["tree"] = [None]
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_ENTRIES_UNREVIEWED")

    def test_portable_wire_root_tree_entries_string_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        trees[self.envelope["commit"]["tree"]["sha"]]["tree"] = "not-a-tree"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_ENTRIES_UNREVIEWED")

    def test_portable_wire_docs_leaf_numeric_sha_refused(self):
        self._portable_snapshot_leaf("docs")["sha"] = 12345
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_SHA_UNREVIEWED")

    def _rehash_portable_snapshot_root(self):
        trees = self.envelope["full_tree_snapshots"]
        old_root_sha = self.envelope["commit"]["tree"]["sha"]
        root = trees.pop(old_root_sha)
        new_root_sha = composite.tree_chain.reviewed_git_tree_sha(
            root["tree"])
        self.assertIsNotNone(new_root_sha)
        self.assertNotEqual(new_root_sha, old_root_sha)
        root["sha"] = new_root_sha
        trees[new_root_sha] = root
        self.envelope["commit"]["tree"]["sha"] = new_root_sha
        self.envelope["tree"]["sha"] = new_root_sha

    def _rehash_portable_snapshot_child_and_root(self, directory):
        trees, root_sha, child_sha = self._portable_snapshot_parent_child(
            directory)
        child = trees.pop(child_sha)
        new_child_sha = composite.tree_chain.reviewed_git_tree_sha(
            child["tree"])
        self.assertIsNotNone(new_child_sha)
        self.assertNotEqual(new_child_sha, child_sha)
        child["sha"] = new_child_sha
        trees[new_child_sha] = child
        root = trees[root_sha]
        parent = next(e for e in root["tree"] if e["path"] == directory)
        parent["sha"] = new_child_sha
        self._rehash_portable_snapshot_root()

    def test_portable_rehashed_tests_leaf_uses_docs_blob_sha_refused(self):
        self._portable_snapshot_leaf("tests")["sha"] = (
            self.envelope["nodes"]["docs/sample.md"]["sha"])
        self._rehash_portable_snapshot_child_and_root("tests")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH")

    def test_portable_rehashed_docs_leaf_uses_tests_blob_sha_refused(self):
        self._portable_snapshot_leaf("docs")["sha"] = (
            self.envelope["nodes"]["tests/sample.py"]["sha"])
        self._rehash_portable_snapshot_child_and_root("docs")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH")

    def test_portable_rehashed_tests_leaf_forged_blob_sha_refused(self):
        self._portable_snapshot_leaf("tests")["sha"] = "a"*40
        self._rehash_portable_snapshot_child_and_root("tests")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH")

    def test_portable_rehashed_docs_leaf_forged_blob_sha_refused(self):
        self._portable_snapshot_leaf("docs")["sha"] = "b"*40
        self._rehash_portable_snapshot_child_and_root("docs")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH")

    def test_portable_rehashed_docs_executable_leaf_refused(self):
        self._portable_snapshot_leaf("docs")["mode"] = "100755"
        self._rehash_portable_snapshot_child_and_root("docs")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_rehashed_tests_symlink_leaf_refused(self):
        self._portable_snapshot_leaf("tests")["mode"] = "120000"
        self._rehash_portable_snapshot_child_and_root("tests")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_rehashed_docs_gitlink_leaf_refused(self):
        leaf = self._portable_snapshot_leaf("docs")
        leaf["mode"], leaf["type"], leaf["sha"] = (
            "160000", "commit", "a"*40)
        self._rehash_portable_snapshot_child_and_root("docs")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_rehashed_tests_case_renamed_leaf_refused(self):
        self._portable_snapshot_leaf("tests")["path"] = "Sample.py"
        self._rehash_portable_snapshot_child_and_root("tests")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED")

    def test_portable_rehashed_docs_unicode_renamed_leaf_refused(self):
        self._portable_snapshot_leaf("docs")["path"] = "sample\u2024md"
        self._rehash_portable_snapshot_child_and_root("docs")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED")

    def test_portable_rehashed_docs_symlink_parent_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        root = trees[self.envelope["commit"]["tree"]["sha"]]
        parent = next(e for e in root["tree"] if e["path"] == "docs")
        parent["mode"], parent["type"] = "120000", "blob"
        self._rehash_portable_snapshot_root()
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_PARENT_NOT_REGULAR_TREE")

    def test_portable_rehashed_root_swapped_child_pointers_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        root = trees[self.envelope["commit"]["tree"]["sha"]]
        parents = {e["path"]: e for e in root["tree"]}
        parents["tests"]["sha"], parents["docs"]["sha"] = (
            parents["docs"]["sha"], parents["tests"]["sha"])
        self._rehash_portable_snapshot_root()
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED")

    def test_portable_rehashed_root_case_renamed_docs_parent_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        root = trees[self.envelope["commit"]["tree"]["sha"]]
        next(e for e in root["tree"] if e["path"] == "docs")[
            "path"] = "Docs"
        self._rehash_portable_snapshot_root()
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED")

    def test_portable_unmodified_rehashed_chain_control_source_only(self):
        direct = self.verdict()
        self.assertTrue(direct["source_consistency"])
        self.assertEqual(direct["diagnostics"], ())
        self.assertEqual(direct, review_bundle_json_text(
            json.dumps(self.envelope, sort_keys=True)))
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def _json_full_tree_member_spelling(self, key, duplicate=False,
                                        root_category=False):
        raw = json.dumps(self.envelope, sort_keys=True,
                         separators=(",", ":"))
        if root_category:
            self.assertEqual(key, "full_tree_snapshots")
            prefix, suffix = "", raw
        else:
            marker = '"full_tree_snapshots":{'
            self.assertEqual(raw.count(marker), 1)
            before, after = raw.split(marker, 1)
            prefix, suffix = before + marker, after
        needle = json.dumps(key) + ":"
        self.assertIn(needle, suffix)
        escaped = ('"' + '\\u%04x' % ord(key[0]) + key[1:] + '"')
        self.assertNotEqual(escaped, json.dumps(key))
        replacement = ((needle + "null," + escaped + ":")
                       if duplicate else escaped + ":")
        rewritten = prefix + suffix.replace(needle, replacement, 1)
        self.assertNotEqual(rewritten, raw)
        # A naive JSON decoder silently retains the second decoded key.
        # Strict ingress must reject that ambiguity before source review.
        self.assertEqual(json.loads(rewritten), self.envelope)
        return rewritten

    def _assert_json_tree_member_equivalence(self, key, root_category=False):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        encoded = self._json_full_tree_member_spelling(
            key, root_category=root_category)
        direct = self.verdict()
        parsed = review_bundle_json_text(encoded)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(encoded), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct["diagnostics"], ())
        self.assertTrue(direct["source_consistency"])
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 0)
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"], [])
        self.assertTrue(emitted["source_consistency"])
        for result in (direct, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def _assert_json_tree_duplicate_decoded_key_refused(
            self, key, root_category=False):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        encoded = self._json_full_tree_member_spelling(
            key, duplicate=True, root_category=root_category)
        direct = self.verdict()
        self.assertTrue(direct["source_consistency"])
        self.assertEqual(direct["diagnostics"], ())
        parsed = review_bundle_json_text(encoded)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(encoded), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(status, 2)
        self.assertEqual(parsed["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertFalse(parsed["source_consistency"])
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         list(parsed["diagnostics"]))
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for result in (parsed, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_portable_tree_json_escaped_root_category_equivalent(self):
        self._assert_json_tree_member_equivalence(
            "full_tree_snapshots", root_category=True)

    def test_portable_tree_json_escaped_root_snapshot_hash_key_equivalent(self):
        self._assert_json_tree_member_equivalence(
            self.envelope["commit"]["tree"]["sha"])

    def test_portable_tree_json_escaped_nested_path_key_equivalent(self):
        self._assert_json_tree_member_equivalence("path")

    def test_portable_tree_json_escaped_nested_mode_key_equivalent(self):
        self._assert_json_tree_member_equivalence("mode")

    def test_portable_tree_json_escaped_nested_type_key_equivalent(self):
        self._assert_json_tree_member_equivalence("type")

    def test_portable_tree_json_escaped_nested_sha_key_equivalent(self):
        self._assert_json_tree_member_equivalence("sha")

    def test_portable_tree_json_escaped_nested_tree_key_equivalent(self):
        self._assert_json_tree_member_equivalence("tree")

    def test_portable_tree_json_escaped_nested_truncated_key_equivalent(self):
        self._assert_json_tree_member_equivalence("truncated")

    def test_portable_tree_json_duplicate_root_category_refused(self):
        self._assert_json_tree_duplicate_decoded_key_refused(
            "full_tree_snapshots", root_category=True)

    def test_portable_tree_json_duplicate_root_snapshot_hash_key_refused(self):
        self._assert_json_tree_duplicate_decoded_key_refused(
            self.envelope["commit"]["tree"]["sha"])

    def test_portable_tree_json_duplicate_nested_path_key_refused(self):
        self._assert_json_tree_duplicate_decoded_key_refused("path")

    def test_portable_tree_json_duplicate_nested_mode_key_refused(self):
        self._assert_json_tree_duplicate_decoded_key_refused("mode")

    def test_portable_tree_json_duplicate_nested_type_key_refused(self):
        self._assert_json_tree_duplicate_decoded_key_refused("type")

    def test_portable_tree_json_duplicate_nested_sha_key_refused(self):
        self._assert_json_tree_duplicate_decoded_key_refused("sha")

    def test_portable_tree_json_duplicate_nested_tree_key_refused(self):
        self._assert_json_tree_duplicate_decoded_key_refused("tree")

    def test_portable_tree_json_duplicate_nested_truncated_key_refused(self):
        self._assert_json_tree_duplicate_decoded_key_refused("truncated")

    def _json_full_tree_entry_value_escape(self, field, value, offset):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.assertLess(offset, len(value))
        self.assertLess(ord(value[offset]), 128)
        raw = json.dumps(self.envelope, sort_keys=True,
                         separators=(",", ":"))
        marker = '"full_tree_snapshots":{'
        self.assertEqual(raw.count(marker), 1)
        before, after = raw.split(marker, 1)
        needle = json.dumps(field) + ":" + json.dumps(value)
        self.assertIn(needle, after)
        escaped_value = (
            '"' + value[:offset] + '\\u%04x' % ord(value[offset]) +
            value[offset+1:] + '"')
        self.assertNotEqual(escaped_value, json.dumps(value))
        encoded = before + marker + after.replace(
            needle, json.dumps(field) + ":" + escaped_value, 1)
        self.assertNotEqual(encoded, raw)
        self.assertEqual(json.loads(encoded), self.envelope)
        direct = self.verdict()
        parsed = review_bundle_json_text(encoded)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(encoded), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(direct, parsed)
        self.assertEqual(direct["diagnostics"], ())
        self.assertTrue(direct["source_consistency"])
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"], [])
        self.assertTrue(emitted["source_consistency"])
        for result in (direct, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def _json_full_tree_unicode_path_rejected(self, directory, mutated,
                                              parent=False):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        if parent:
            root = self.envelope["full_tree_snapshots"][
                self.envelope["commit"]["tree"]["sha"]]
            item = next(entry for entry in root["tree"]
                        if entry["path"] == directory)
        else:
            item = self._portable_snapshot_leaf(directory)
        self.assertNotEqual(mutated, item["path"])
        item["path"] = mutated
        raw = json.dumps(self.envelope, sort_keys=True)
        self.assertIn("\\u", raw)
        direct = self.verdict()
        parsed = review_bundle_json_text(raw)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 2)
        self.assertIn("TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED",
                      direct["diagnostics"])
        self.assertFalse(direct["source_consistency"])
        self.assertEqual(emitted["diagnostics"],
                         list(direct["diagnostics"]))
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertNotIn(mutated, out.getvalue())
        for result in (direct, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_portable_tree_json_escaped_docs_parent_path_value_equivalent(self):
        self._json_full_tree_entry_value_escape("path", "docs", 0)

    def test_portable_tree_json_escaped_tests_parent_path_value_equivalent(self):
        self._json_full_tree_entry_value_escape("path", "tests", 1)

    def test_portable_tree_json_escaped_docs_leaf_path_value_equivalent(self):
        self._json_full_tree_entry_value_escape("path", "sample.md", 6)

    def test_portable_tree_json_escaped_tests_leaf_path_value_equivalent(self):
        self._json_full_tree_entry_value_escape("path", "sample.py", 7)

    def test_portable_tree_json_escaped_parent_mode_value_equivalent(self):
        self._json_full_tree_entry_value_escape("mode", "040000", 0)

    def test_portable_tree_json_escaped_leaf_mode_value_equivalent(self):
        self._json_full_tree_entry_value_escape("mode", "100644", 3)

    def test_portable_tree_json_escaped_leaf_type_value_equivalent(self):
        self._json_full_tree_entry_value_escape("type", "blob", 0)

    def test_portable_tree_json_escaped_leaf_sha_value_equivalent(self):
        self._json_full_tree_entry_value_escape(
            "sha", self.envelope["nodes"]["docs/sample.md"]["sha"], 2)

    def test_portable_tree_json_docs_one_dot_confusable_refused(self):
        self._json_full_tree_unicode_path_rejected(
            "docs", "sample\u2024md")

    def test_portable_tree_json_docs_division_slash_confusable_refused(self):
        self._json_full_tree_unicode_path_rejected(
            "docs", "sample\u2215md")

    def test_portable_tree_json_docs_zero_width_space_refused(self):
        self._json_full_tree_unicode_path_rejected(
            "docs", "s\u200bample.md")

    def test_portable_tree_json_docs_word_joiner_refused(self):
        self._json_full_tree_unicode_path_rejected(
            "docs", "s\u2060ample.md")

    def test_portable_tree_json_docs_cyrillic_e_refused(self):
        self._json_full_tree_unicode_path_rejected(
            "docs", "sampl\u0435.md")

    def test_portable_tree_json_tests_fullwidth_s_refused(self):
        self._json_full_tree_unicode_path_rejected(
            "tests", "\uff53ample.py")

    def test_portable_tree_json_root_tests_zero_width_joiner_refused(self):
        self._json_full_tree_unicode_path_rejected(
            "tests", "te\u200dsts", parent=True)

    def test_portable_tree_json_root_docs_zero_width_space_refused(self):
        self._json_full_tree_unicode_path_rejected(
            "docs", "d\u200bocs", parent=True)

    def test_portable_tree_json_entry_clean_control_nonauthorizing(self):
        direct = self.verdict()
        parsed = review_bundle_json_text(json.dumps(self.envelope))
        self.assertEqual(direct, parsed)
        self.assertTrue(direct["source_consistency"])
        self.assertEqual(direct["diagnostics"], ())
        self.assertFalse(direct["independent_original_os_proof"])
        self.assertFalse(direct["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(direct["can_authorize_annual_run"])

    def _assert_portable_tree_object_order_consistency_only(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        direct = self.verdict()
        encoded = json.dumps(self.envelope)
        parsed = review_bundle_json_text(encoded)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(encoded), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 0)
        self.assertTrue(direct["source_consistency"])
        self.assertEqual(direct["diagnostics"], ())
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"], [])
        self.assertTrue(emitted["source_consistency"])
        for result in (direct, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def _reversed_portable_tree_fields(self, directory=None):
        trees = self.envelope["full_tree_snapshots"]
        if directory is None:
            sha = self.envelope["commit"]["tree"]["sha"]
        else:
            _, _, sha = self._portable_snapshot_parent_child(directory)
        trees[sha] = dict(reversed(list(trees[sha].items())))

    def _reversed_portable_tree_entry_fields(self, directory, leaf=False):
        trees = self.envelope["full_tree_snapshots"]
        root = trees[self.envelope["commit"]["tree"]["sha"]]
        if leaf:
            _, _, sha = self._portable_snapshot_parent_child(directory)
            entries = trees[sha]["tree"]
            index = 0
        else:
            entries = root["tree"]
            index = next(i for i, e in enumerate(entries)
                         if e["path"] == directory)
        entries[index] = dict(reversed(list(entries[index].items())))

    def test_portable_tree_map_order_reverse_snapshot_inventory_clean(self):
        trees = self.envelope["full_tree_snapshots"]
        self.envelope["full_tree_snapshots"] = dict(
            reversed(list(trees.items())))
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_reverse_root_object_fields_clean(self):
        self._reversed_portable_tree_fields()
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_reverse_tests_object_fields_clean(self):
        self._reversed_portable_tree_fields("tests")
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_reverse_docs_object_fields_clean(self):
        self._reversed_portable_tree_fields("docs")
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_reverse_tests_parent_fields_clean(self):
        self._reversed_portable_tree_entry_fields("tests")
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_reverse_docs_parent_fields_clean(self):
        self._reversed_portable_tree_entry_fields("docs")
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_reverse_tests_leaf_fields_clean(self):
        self._reversed_portable_tree_entry_fields("tests", leaf=True)
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_reverse_docs_leaf_fields_clean(self):
        self._reversed_portable_tree_entry_fields("docs", leaf=True)
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_reverse_flat_node_inventory_clean(self):
        self.envelope["nodes"] = dict(
            reversed(list(self.envelope["nodes"].items())))
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_reverse_flat_node_fields_clean(self):
        self.envelope["nodes"] = {
            k: dict(reversed(list(v.items())))
            for k, v in self.envelope["nodes"].items()}
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_reverse_changed_bytes_map_clean(self):
        pairs = self.envelope["changed_bytes_b64"]
        self.envelope["changed_bytes_b64"] = dict(
            reversed(list(pairs.items())))
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_all_nested_objects_reversed_clean(self):
        trees = self.envelope["full_tree_snapshots"]
        self.envelope["full_tree_snapshots"] = {
            sha: dict(reversed([
                (k, ([dict(reversed(list(entry.items())))
                      for entry in v] if k == "tree" else v))
                for k, v in snapshot.items()]))
            for sha, snapshot in reversed(list(trees.items()))}
        self.envelope["nodes"] = dict(reversed([
            (k, dict(reversed(list(v.items()))))
            for k, v in self.envelope["nodes"].items()]))
        pairs = self.envelope["changed_bytes_b64"]
        self.envelope["changed_bytes_b64"] = dict(
            reversed(list(pairs.items())))
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_map_order_root_entry_array_reversed_refused(self):
        root = self.envelope["full_tree_snapshots"][
            self.envelope["commit"]["tree"]["sha"]]
        self.assertEqual([e["path"] for e in root["tree"]],
                         ["docs", "tests"])
        root["tree"].reverse()
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH")

    def test_portable_tree_map_order_original_clean_source_only(self):
        self._assert_portable_tree_object_order_consistency_only()

    def test_portable_tree_root_snapshot_key_uppercase_not_same_sha(self):
        trees = self.envelope["full_tree_snapshots"]
        old = self.envelope["commit"]["tree"]["sha"]
        self.assertNotEqual(old.upper(), old)
        trees[old.upper()] = trees.pop(old)
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_tree_root_snapshot_key_fullwidth_not_same_sha(self):
        trees = self.envelope["full_tree_snapshots"]
        old = self.envelope["commit"]["tree"]["sha"]
        trees["\uff14" + old[1:]] = trees.pop(old)
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_tree_root_snapshot_key_zero_width_not_same_sha(self):
        trees = self.envelope["full_tree_snapshots"]
        old = self.envelope["commit"]["tree"]["sha"]
        trees[old[:8] + "\u200b" + old[8:]] = trees.pop(old)
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_tree_tests_snapshot_key_uppercase_not_same_sha(self):
        trees, _, old = self._portable_snapshot_parent_child("tests")
        self.assertNotEqual(old.upper(), old)
        trees[old.upper()] = trees.pop(old)
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_tree_docs_snapshot_key_trailing_space_not_same_sha(self):
        trees, _, old = self._portable_snapshot_parent_child("docs")
        trees[old + " "] = trees.pop(old)
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_tree_root_snapshot_self_sha_uppercase_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        root = trees[self.envelope["commit"]["tree"]["sha"]]
        root["sha"] = root["sha"].upper()
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_tree_tests_snapshot_self_sha_newline_refused(self):
        trees, _, old = self._portable_snapshot_parent_child("tests")
        trees[old]["sha"] += "\n"
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_tree_docs_snapshot_self_sha_unicode_refused(self):
        trees, _, old = self._portable_snapshot_parent_child("docs")
        trees[old]["sha"] = "\uff46" + old[1:]
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_tree_commit_root_sha_uppercase_refused(self):
        tree = self.envelope["commit"]["tree"]
        tree["sha"] = tree["sha"].upper()
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ROOT_SHA_UNREVIEWED")

    def test_portable_tree_commit_root_sha_hex_prefix_refused(self):
        self.envelope["commit"]["tree"]["sha"] = (
            "0x" + self.envelope["commit"]["tree"]["sha"])
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ROOT_SHA_UNREVIEWED")

    def test_portable_tree_tests_parent_pointer_uppercase_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        root = trees[self.envelope["commit"]["tree"]["sha"]]
        parent = next(e for e in root["tree"] if e["path"] == "tests")
        parent["sha"] = parent["sha"].upper()
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_SHA_UNREVIEWED")

    def test_portable_tree_docs_parent_pointer_nonhex_refused(self):
        trees = self.envelope["full_tree_snapshots"]
        root = trees[self.envelope["commit"]["tree"]["sha"]]
        next(e for e in root["tree"] if e["path"] == "docs")["sha"] = "g"*40
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_SHA_UNREVIEWED")

    def test_portable_tree_leaf_sha_fullwidth_digit_refused(self):
        self._portable_snapshot_leaf("docs")["sha"] = "\uff11"*40
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_ENTRY_SHA_UNREVIEWED")

    def test_portable_tree_sha_lexical_clean_source_only(self):
        self._assert_portable_tree_object_order_consistency_only()

    def _set_portable_full_snapshot_truncated(self, directory, value):
        trees = self.envelope["full_tree_snapshots"]
        if directory is None:
            sha = self.envelope["commit"]["tree"]["sha"]
        else:
            _, _, sha = self._portable_snapshot_parent_child(directory)
        trees[sha]["truncated"] = value
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_git_tree_root_truncated_integer_zero_refused(self):
        self._set_portable_full_snapshot_truncated(None, 0)

    def test_portable_git_tree_root_truncated_null_refused(self):
        self._set_portable_full_snapshot_truncated(None, None)

    def test_portable_git_tree_root_truncated_string_false_refused(self):
        self._set_portable_full_snapshot_truncated(None, "false")

    def test_portable_git_tree_root_truncated_empty_string_refused(self):
        self._set_portable_full_snapshot_truncated(None, "")

    def test_portable_git_tree_root_truncated_empty_list_refused(self):
        self._set_portable_full_snapshot_truncated(None, [])

    def test_portable_git_tree_root_truncated_empty_object_refused(self):
        self._set_portable_full_snapshot_truncated(None, {})

    def test_portable_git_tree_root_truncated_float_zero_refused(self):
        self._set_portable_full_snapshot_truncated(None, 0.0)

    def test_portable_git_tree_child_truncated_tests_integer_zero_refused(self):
        self._set_portable_full_snapshot_truncated("tests", 0)

    def test_portable_git_tree_child_truncated_docs_null_refused(self):
        self._set_portable_full_snapshot_truncated("docs", None)

    def test_portable_git_tree_child_truncated_tests_string_false_refused(self):
        self._set_portable_full_snapshot_truncated("tests", "false")

    def test_portable_git_tree_child_truncated_docs_empty_list_refused(self):
        self._set_portable_full_snapshot_truncated("docs", [])

    def test_portable_git_tree_child_truncated_tests_float_zero_refused(self):
        self._set_portable_full_snapshot_truncated("tests", 0.0)

    def test_portable_git_tree_root_truncated_field_missing_refused(self):
        root = self.envelope["full_tree_snapshots"][
            self.envelope["commit"]["tree"]["sha"]]
        root.pop("truncated")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_git_tree_docs_truncated_field_missing_refused(self):
        trees, _, sha = self._portable_snapshot_parent_child("docs")
        trees[sha].pop("truncated")
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def test_portable_git_tree_flat_root_integer_zero_refused(self):
        self.envelope["tree"]["truncated"] = 0
        self._assert_changed_tree_node_mode_refused(
            "COMMIT_TREE_ROOT_UNREVIEWED")

    def test_portable_git_tree_flat_root_string_false_refused(self):
        self.envelope["tree"]["truncated"] = "false"
        self._assert_changed_tree_node_mode_refused(
            "COMMIT_TREE_ROOT_UNREVIEWED")

    def test_portable_git_tree_truncated_clean_boolean_control(self):
        self.assertIs(self.envelope["tree"]["truncated"], False)
        for snapshot in self.envelope["full_tree_snapshots"].values():
            self.assertIs(snapshot["truncated"], False)
        self._assert_portable_tree_object_order_consistency_only()

    def _set_portable_tree_object_shape(self, directory, value):
        trees = self.envelope["full_tree_snapshots"]
        if directory is None:
            sha = self.envelope["commit"]["tree"]["sha"]
        else:
            _, _, sha = self._portable_snapshot_parent_child(directory)
        trees[sha] = value
        self._assert_full_tree_snapshot_mutation_refused(
            "TREE_CHAIN_TREE_OBJECT_UNREVIEWED")

    def _assert_portable_tree_category_type_refused(self):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        direct = self.verdict()
        raw = json.dumps(self.envelope)
        parsed = review_bundle_json_text(raw)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 2)
        self.assertEqual(direct["diagnostics"],
                         ("BUNDLE_CATEGORY_TYPE_UNREVIEWED",))
        self.assertFalse(direct["source_consistency"])
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         list(direct["diagnostics"]))
        self.assertNotIn("tests/sample.py", out.getvalue())
        for result in (direct, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_portable_tree_object_root_null_refused(self):
        self._set_portable_tree_object_shape(None, None)

    def test_portable_tree_object_root_boolean_false_refused(self):
        self._set_portable_tree_object_shape(None, False)

    def test_portable_tree_object_root_integer_zero_refused(self):
        self._set_portable_tree_object_shape(None, 0)

    def test_portable_tree_object_root_empty_string_refused(self):
        self._set_portable_tree_object_shape(None, "")

    def test_portable_tree_object_root_empty_list_refused(self):
        self._set_portable_tree_object_shape(None, [])

    def test_portable_tree_object_root_empty_dict_refused(self):
        self._set_portable_tree_object_shape(None, {})

    def test_portable_tree_object_root_float_zero_refused(self):
        self._set_portable_tree_object_shape(None, 0.0)

    def test_portable_tree_object_child_tests_null_refused(self):
        self._set_portable_tree_object_shape("tests", None)

    def test_portable_tree_object_child_docs_boolean_false_refused(self):
        self._set_portable_tree_object_shape("docs", False)

    def test_portable_tree_object_child_tests_integer_zero_refused(self):
        self._set_portable_tree_object_shape("tests", 0)

    def test_portable_tree_object_child_docs_empty_string_refused(self):
        self._set_portable_tree_object_shape("docs", "")

    def test_portable_tree_object_child_tests_empty_list_refused(self):
        self._set_portable_tree_object_shape("tests", [])

    def test_portable_tree_object_child_docs_empty_dict_refused(self):
        self._set_portable_tree_object_shape("docs", {})

    def test_portable_tree_object_child_tests_float_zero_refused(self):
        self._set_portable_tree_object_shape("tests", 0.0)

    def test_portable_tree_object_category_null_refused(self):
        self.envelope["full_tree_snapshots"] = None
        self._assert_portable_tree_category_type_refused()

    def test_portable_tree_object_category_array_refused(self):
        self.envelope["full_tree_snapshots"] = []
        self._assert_portable_tree_category_type_refused()

    def test_portable_tree_object_clean_dict_control(self):
        self.assertIs(type(self.envelope["full_tree_snapshots"]), dict)
        for snapshot in self.envelope["full_tree_snapshots"].values():
            self.assertIs(type(snapshot), dict)
        self._assert_portable_tree_object_order_consistency_only()

    def _assert_portable_multiple_tree_faults(self, *expected_codes):
        import io
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        self.assertGreaterEqual(len(set(expected_codes)), 2)
        direct = self.verdict()
        payload = json.dumps(self.envelope, sort_keys=True)
        parsed = review_bundle_json_text(payload)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(payload), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 2)
        self.assertFalse(direct["source_consistency"])
        self.assertEqual(direct["diagnostics"],
                         tuple(sorted(set(direct["diagnostics"]))))
        for code in expected_codes:
            self.assertIn(code, direct["diagnostics"])
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         list(direct["diagnostics"]))
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for result in (direct, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_portable_multi_tree_test_mode_and_docs_wrong_blob_sha(self):
        self._portable_snapshot_leaf("tests")["mode"] = "100755"
        self._portable_snapshot_leaf("docs")["sha"] = "a"*40
        self._assert_portable_multiple_tree_faults(
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB",
            "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH")

    def test_portable_multi_tree_docs_parent_and_test_wrong_blob_sha(self):
        root = self.envelope["full_tree_snapshots"][
            self.envelope["commit"]["tree"]["sha"]]
        next(e for e in root["tree"] if e["path"] == "docs")[
            "mode"] = "120000"
        self._portable_snapshot_leaf("tests")["sha"] = "a"*40
        self._assert_portable_multiple_tree_faults(
            "TREE_CHAIN_PARENT_NOT_REGULAR_TREE",
            "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH")

    def test_portable_multi_tree_docs_parent_and_test_executable(self):
        root = self.envelope["full_tree_snapshots"][
            self.envelope["commit"]["tree"]["sha"]]
        next(e for e in root["tree"] if e["path"] == "docs")[
            "mode"] = "120000"
        self._portable_snapshot_leaf("tests")["mode"] = "100755"
        self._assert_portable_multiple_tree_faults(
            "TREE_CHAIN_PARENT_NOT_REGULAR_TREE",
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_multi_tree_docs_nonhex_and_test_symlink(self):
        self._portable_snapshot_leaf("docs")["sha"] = "g"*40
        self._portable_snapshot_leaf("tests")["mode"] = "120000"
        self._assert_portable_multiple_tree_faults(
            "TREE_CHAIN_ENTRY_SHA_UNREVIEWED",
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_multi_tree_tests_parent_nonhex_and_docs_symlink(self):
        root = self.envelope["full_tree_snapshots"][
            self.envelope["commit"]["tree"]["sha"]]
        next(e for e in root["tree"] if e["path"] == "tests")[
            "sha"] = "g"*40
        self._portable_snapshot_leaf("docs")["mode"] = "120000"
        self._assert_portable_multiple_tree_faults(
            "TREE_CHAIN_ENTRY_SHA_UNREVIEWED",
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_multi_tree_extra_orphan_and_docs_executable(self):
        self.envelope["full_tree_snapshots"]["f"*40] = {
            "sha": "f"*40, "truncated": False, "tree": []}
        self._portable_snapshot_leaf("docs")["mode"] = "100755"
        self._assert_portable_multiple_tree_faults(
            "TREE_CHAIN_TREE_SNAPSHOT_INVENTORY_UNREVIEWED",
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_multi_tree_tests_leaf_renamed_docs_blob_replaced(self):
        self._portable_snapshot_leaf("tests")["path"] = "changed.py"
        self._portable_snapshot_leaf("docs")["sha"] = "a"*40
        self._assert_portable_multiple_tree_faults(
            "TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED",
            "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH")

    def test_portable_multi_tree_tests_wrong_sha_docs_wrong_mode(self):
        self._portable_snapshot_leaf("tests")["sha"] = "a"*40
        self._portable_snapshot_leaf("docs")["mode"] = "160000"
        self._assert_portable_multiple_tree_faults(
            "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH",
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_multi_tree_reversed_snapshot_map_keeps_fail_closed(self):
        self._portable_snapshot_leaf("docs")["sha"] = "a"*40
        self._portable_snapshot_leaf("tests")["mode"] = "100755"
        trees = self.envelope["full_tree_snapshots"]
        self.envelope["full_tree_snapshots"] = dict(
            reversed(list(trees.items())))
        self._assert_portable_multiple_tree_faults(
            "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH",
            "TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")

    def test_portable_multi_tree_wrong_nodes_and_wrong_full_tree(self):
        self.envelope["nodes"]["docs/sample.md"]["mode"] = "100755"
        self._portable_snapshot_leaf("tests")["sha"] = "a"*40
        self._assert_portable_multiple_tree_faults(
            "GIT_TREE_LEAF_MODE_DRIFT",
            "TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH")

    def test_portable_multi_tree_clean_control_source_only(self):
        self._assert_portable_tree_object_order_consistency_only()

    def _assert_nested_tree_graph_mutation_isolated(self, mutate):
        import io
        from unittest.mock import patch
        import test_dec1479_offline_ci_bundle_stdin_command as cli
        before = copy.deepcopy(self.envelope)
        calls = []

        def synthetic_nested_review(**evidence):
            self.assertIsNot(evidence["full_tree_snapshots"],
                             self.envelope["full_tree_snapshots"])
            self.assertIsNot(evidence["nodes"], self.envelope["nodes"])
            mutate(evidence)
            calls.append(True)
            return {
                "source_consistency": True,
                "diagnostics": (),
                "independent_original_os_proof": False,
                "exclusive_server_dispatch_gate_proven": False,
                "can_authorize_annual_run": False,
            }

        raw = json.dumps(self.envelope, sort_keys=True)
        with patch.object(composite, "review_stacked_draft_evidence",
                          side_effect=synthetic_nested_review):
            direct = self.verdict()
            parsed = review_bundle_json_text(raw)
            out = io.StringIO()
            status = cli.run_stdin_review(io.StringIO(raw), out)
        self.assertEqual(len(calls), 3)
        self.assertEqual(self.envelope, before)
        self.assertEqual(direct, parsed)
        self.assertEqual(status, 0)
        self.assertTrue(direct["source_consistency"])
        self.assertEqual(direct["diagnostics"], ())
        emitted = json.loads(out.getvalue())
        self.assertEqual(set(emitted), VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"], [])
        self.assertTrue(emitted["source_consistency"])
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for result in (direct, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])
        # Run the real nested checker after the malicious mock was removed.
        self.assertEqual(self.verdict()["diagnostics"], ())

    def test_portable_nested_tree_mutate_snapshot_map_clear_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["full_tree_snapshots"].clear())

    def test_portable_nested_tree_mutate_root_entries_clear_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["full_tree_snapshots"][
                e["commit"]["tree"]["sha"]]["tree"].clear())

    def test_portable_nested_tree_mutate_root_self_sha_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["full_tree_snapshots"][
                e["commit"]["tree"]["sha"]].__setitem__("sha", "a"*40))

    def test_portable_nested_tree_mutate_root_truncated_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["full_tree_snapshots"][
                e["commit"]["tree"]["sha"]].__setitem__("truncated", True))

    def test_portable_nested_tree_mutate_root_duplicate_entry_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["full_tree_snapshots"][
                e["commit"]["tree"]["sha"]]["tree"].append(
                    dict(e["full_tree_snapshots"][
                        e["commit"]["tree"]["sha"]]["tree"][0])))

    def test_portable_nested_tree_mutate_flat_node_inventory_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["nodes"].clear())

    def test_portable_nested_tree_mutate_flat_docs_mode_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["nodes"]["docs/sample.md"].__setitem__(
                "mode", "120000"))

    def test_portable_nested_tree_mutate_changed_raw_bytes_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["changed_bytes"].__setitem__(
                "tests/sample.py", b"evil\n"))

    def test_portable_nested_tree_mutate_ci_source_map_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["ci_workflow_bytes"].clear())

    def test_portable_nested_tree_mutate_commit_root_pointer_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["commit"]["tree"].__setitem__("sha", "a"*40))

    def test_portable_nested_tree_mutate_compare_files_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["compare"]["files"].clear())

    def test_portable_nested_tree_mutate_raw_ci_logs_isolated(self):
        self._assert_nested_tree_graph_mutation_isolated(
            lambda e: e["raw_ci_runner_logs"].clear())

    def test_portable_nested_tree_real_reviewer_still_non_authorizing(self):
        self._assert_portable_tree_object_order_consistency_only()

