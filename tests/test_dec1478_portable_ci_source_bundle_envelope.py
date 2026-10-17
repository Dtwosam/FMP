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
import re
import unittest

import test_dec1440_stacked_source_evidence_offline as composite

ENVELOPE_SCHEMA = "fmp-offline-source-bundle-v1"
MAX_TEXT_CHARS = 2_000_000
MAX_BLOB_BYTES = 1_000_000
MAX_TOTAL_BLOB_BYTES = 4_000_000
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
    for key in REQUIRED - frozenset(("schema",)):
        value = envelope[key]
        if key in ID_MAPS:
            decoded = {}
            for k, item in value.items():
                if (type(k) is not str or
                        re.fullmatch(r"[1-9][0-9]*", k) is None):
                    return fail_closed("BUNDLE_RUN_KEY_UNREVIEWED")
                number = int(k)
                if number in decoded:
                    return fail_closed("BUNDLE_RUN_KEY_DUPLICATED")
                decoded[number] = item
            converted[key] = decoded
        elif key in BYTES_MAPS:
            decoded = {}
            for path, payload in value.items():
                if type(path) is not str or not path:
                    return fail_closed("BUNDLE_SOURCE_PATH_UNREVIEWED")
                if type(payload) is not str:
                    return fail_closed("BUNDLE_SOURCE_B64_UNREVIEWED")
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
            OverflowError, UnicodeError) as _:
        return fail_closed("BUNDLE_NESTED_EVIDENCE_UNREVIEWED")
    if (type(verdict) is not dict or
            verdict.get("independent_original_os_proof") is not False or
            verdict.get("exclusive_server_dispatch_gate_proven") is not False or
            verdict.get("can_authorize_annual_run") is not False or
            type(verdict.get("source_consistency")) is not bool or
            type(verdict.get("diagnostics")) is not tuple):
        return fail_closed("BUNDLE_RESULT_SHAPE_UNREVIEWED")
    return verdict


def review_bundle_json_text(text):
    """No external I/O: caller provides raw UTF-8-decoded JSON text."""
    if type(text) is not str or len(text) > MAX_TEXT_CHARS:
        return fail_closed("BUNDLE_JSON_TEXT_UNREVIEWED")
    try:
        doc = json.loads(text, object_pairs_hook=_no_duplicate_keys,
                         parse_constant=_no_nonfinite)
    except (ValueError, TypeError, UnicodeError):
        return fail_closed("BUNDLE_JSON_GRAMMAR_UNREVIEWED")
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
