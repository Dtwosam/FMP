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
VERDICT_FIELDS = frozenset((
    "source_consistency", "diagnostics", "independent_original_os_proof",
    "exclusive_server_dispatch_gate_proven", "can_authorize_annual_run",
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


def _reviewed_source_path(path):
    """Require unambiguous repository-relative POSIX source labels."""
    if type(path) is not str or not path or path.startswith("/") or "\\" in path:
        return False
    if ":" in path or not unicodedata.is_normalized("NFC", path):
        return False
    for segment in path.split("/"):
        if (segment in ("", ".", "..") or segment.endswith((" ", ".")) or
                re.fullmatch(r"(?i:(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9]))"
                             r"(?:\..*)?", segment) is not None):
            return False
    return not any(ord(char) < 32 or ord(char) == 127 or
                   0xD800 <= ord(char) <= 0xDFFF or
                   0x202A <= ord(char) <= 0x202E or
                   0x2066 <= ord(char) <= 0x2069 for char in path)


def review_bundle_envelope(envelope):
    """Decode an offline-only JSON-compatible envelope, fail closed on bad input."""
    if type(envelope) is not dict:
        return fail_closed("BUNDLE_SHAPE_UNREVIEWED")
    if set(envelope) != REQUIRED:
        return fail_closed("BUNDLE_KEY_INVENTORY_UNREVIEWED")
    if envelope["schema"] != ENVELOPE_SCHEMA:
        return fail_closed("BUNDLE_SCHEMA_UNREVIEWED")
    if type(envelope["runs"]) is not list or any(
            type(envelope[key]) is not dict for key in DICT_KEYS):
        return fail_closed("BUNDLE_CATEGORY_TYPE_UNREVIEWED")

    converted = {}
    total_bytes = 0
    # Stable ordering makes the same malformed bundle produce the same
    # diagnostics regardless of PYTHONHASHSEED or JSON field insertion order.
    for key in sorted(REQUIRED - frozenset(("schema",))):
        value = envelope[key]
        if key in ID_MAPS:
            decoded = {}
            if any(type(k) is not str for k in value):
                return fail_closed("BUNDLE_RUN_KEY_UNREVIEWED")
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
            if any(type(path) is not str for path in value):
                return fail_closed("BUNDLE_SOURCE_PATH_UNREVIEWED")
            for path in sorted(value):
                payload = value[path]
                if not _reviewed_source_path(path):
                    return fail_closed("BUNDLE_SOURCE_PATH_UNREVIEWED")
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

    try:
        verdict = composite.review_stacked_draft_evidence(**converted)
    except (TypeError, ValueError, KeyError, IndexError, AttributeError,
            OverflowError, UnicodeError, RecursionError) as _:
        return fail_closed("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")
    if (type(verdict) is not dict or
            set(verdict) != VERDICT_FIELDS or
            verdict.get("independent_original_os_proof") is not False or
            verdict.get("exclusive_server_dispatch_gate_proven") is not False or
            verdict.get("can_authorize_annual_run") is not False or
            type(verdict.get("source_consistency")) is not bool or
            type(verdict.get("diagnostics")) is not tuple or
            len(verdict["diagnostics"]) > 256 or
            any(type(code) is not str or re.fullmatch(
                    r"[A-Za-z][A-Za-z0-9_-]{0,127}", code) is None
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
    """Do not admit syntactically valid JSON numbers decoded as infinity."""
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
        expected = ("A_ERROR", "Z_ERROR")
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
        valid["diagnostics"] = ("SYNTHETIC_REVIEW_WARNING",)
        with patch.object(composite, "review_stacked_draft_evidence",
                          return_value=valid):
            result = self.verdict()
        self.assertFalse(result["source_consistency"])
        self.assertEqual(result["diagnostics"], ("SYNTHETIC_REVIEW_WARNING",))
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
        for path in ("tests /module.py", "tests/module .py", "tests/readme "):
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

