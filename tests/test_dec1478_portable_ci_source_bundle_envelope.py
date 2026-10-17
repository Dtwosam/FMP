"""DEC-1478: portable, strictly decoded offline CI/source evidence envelope.

No network, GitHub APIs, workflow dispatch, protected original/annual
artifact reads, merge, security settings change, or live trading.

A valid envelope is *caller-supplied* evidence consistency, NOT remotely
authenticated logs or protected annual execution authorization.
"""
from __future__ import annotations

import base64
import binascii
import json
import math
import re
import unittest
import unicodedata

import test_dec1440_stacked_source_evidence_offline as composite

ENVELOPE_SCHEMA = "fmp-offline-source-bundle-v1"
MAX_TEXT_CHARS = 2_000_000
MAX_BLOB_BYTES = 1_000_000
MAX_TOTAL_BLOB_BYTES = 4_000_000
MAX_JSON_NESTING = 512
MAX_JSON_INTEGER_DIGITS = 64
MAX_JSON_OBJECT_MEMBERS = 16384
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
MAX_INMEMORY_NODES = 200_000
MAX_INMEMORY_DEPTH = 512
MAX_INMEMORY_SCALAR_UNITS = 4_000_000
MAX_INMEMORY_TOTAL_SCALAR_UNITS = 16_000_000
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
        verdict = composite.review_stacked_draft_evidence(**converted)
    except (TypeError, ValueError, KeyError, IndexError, AttributeError,
            OverflowError, UnicodeError, RecursionError, RuntimeError,
            AssertionError, OSError) as _:
        return fail_closed("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")
    if (type(verdict) is not dict or
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


def review_bundle_json_text(text):
    """No external I/O: caller provides raw UTF-8-decoded JSON text."""
    if type(text) is not str or len(text) > MAX_TEXT_CHARS:
        return fail_closed("BUNDLE_JSON_TEXT_UNREVIEWED")
    if not _json_nesting_within_limit(text):
        return fail_closed("BUNDLE_JSON_GRAMMAR_UNREVIEWED")
    try:
        doc = json.loads(text, object_pairs_hook=_no_duplicate_keys,
                         parse_constant=_no_nonfinite,
                         parse_int=_bounded_json_integer,
                         parse_float=_finite_json_float)
    except (ValueError, TypeError, UnicodeError, RecursionError,
            OverflowError):
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

