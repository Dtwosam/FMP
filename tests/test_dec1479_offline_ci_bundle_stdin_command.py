"""DEC-1479: explicitly supplied stdin-only offline CI source review command.

Usage: python tests/test_dec1479_offline_ci_bundle_stdin_command.py < bundle.json

Exit 0 means caller-supplied records passed shape/source consistency checks,
NOT that a protected annual workflow is authorized. No GitHub client, browser,
protected original/archive, annual dispatch, merge, or broker interaction.
"""
from __future__ import annotations

import io
import json
import sys
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as envelope


MAX_STDIN_READ_CHARS = 65536


def _read_complete_bounded_stdin(input_stream):
    """Read to EOF, including streams that return fewer chars than requested.

    Do not treat a valid JSON prefix as the complete document when a later
    read could contain more material. Refuse non-text chunks and read errors.
    """
    chunks = []
    size = 0
    utf8_bytes = 0
    try:
        while True:
            remaining = min(envelope.MAX_TEXT_CHARS - size + 1,
                            envelope.MAX_TEXT_UTF8_BYTES - utf8_bytes + 1)
            requested = min(MAX_STDIN_READ_CHARS, remaining)
            part = input_stream.read(requested)
            if type(part) is not str or len(part) > requested:
                return None, "BUNDLE_STDIN_READ_UNREVIEWED"
            size += len(part)
            if size > envelope.MAX_TEXT_CHARS:
                return None, "BUNDLE_JSON_TEXT_UNREVIEWED"
            try:
                utf8_bytes += len(part.encode("utf-8"))
            except UnicodeError:
                return None, "BUNDLE_JSON_UNICODE_UNREVIEWED"
            if utf8_bytes > envelope.MAX_TEXT_UTF8_BYTES:
                return None, "BUNDLE_JSON_TEXT_UNREVIEWED"
            if not part:
                return "".join(chunks), None
            chunks.append(part)
    except (OSError, UnicodeError, ValueError, TypeError, RuntimeError,
            RecursionError, AssertionError, AttributeError, OverflowError,
            IndexError, EOFError):
        return None, "BUNDLE_STDIN_READ_UNREVIEWED"


APPROVED_OUTPUT_DIAGNOSTICS = frozenset((
    "BUNDLE_CATEGORY_TYPE_UNREVIEWED",
    "BUNDLE_JSON_GRAMMAR_UNREVIEWED",
    "BUNDLE_JSON_TEXT_UNREVIEWED",
    "BUNDLE_JSON_UNICODE_UNREVIEWED",
    "BUNDLE_KEY_INVENTORY_UNREVIEWED",
    "BUNDLE_NESTED_EVIDENCE_UNREVIEWED",
    "BUNDLE_OFFLINE_RESULT_SHAPE_UNREVIEWED",
    "BUNDLE_OFFLINE_REVIEW_UNREVIEWED",
    "BUNDLE_RAW_LOG_TEXT_OVERSIZE",
    "BUNDLE_RAW_LOG_TEXT_UNREVIEWED",
    "BUNDLE_RAW_LOG_UTF8_OVERSIZE",
    "BUNDLE_RESULT_SHAPE_UNREVIEWED",
    "BUNDLE_RUN_COLLECTION_OVERSIZE",
    "BUNDLE_RUN_KEY_DUPLICATED",
    "BUNDLE_RUN_KEY_UNREVIEWED",
    "BUNDLE_RUN_MAP_OVERSIZE",
    "BUNDLE_SCHEMA_UNREVIEWED",
    "BUNDLE_SHAPE_UNREVIEWED",
    "BUNDLE_SOURCE_B64_NONCANONICAL",
    "BUNDLE_SOURCE_B64_UNREVIEWED",
    "BUNDLE_SOURCE_BLOB_OVERSIZE",
    "BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED",
    "BUNDLE_SOURCE_CROSSMAP_COLLISION_UNREVIEWED",
    "BUNDLE_SOURCE_MAP_OVERSIZE",
    "BUNDLE_SOURCE_PATH_UNREVIEWED",
    "BUNDLE_STDIN_ONLY_INVOCATION_REQUIRED",
    "BUNDLE_STDIN_READ_UNREVIEWED",
    "BUNDLE_STRUCTURE_BUDGET_UNREVIEWED",
    "BUNDLE_TOTAL_RAW_LOG_OVERSIZE",
    "BUNDLE_TOTAL_RAW_LOG_UTF8_OVERSIZE",
    "BUNDLE_TOTAL_SOURCE_OVERSIZE",
)) | envelope.REVIEWED_NESTED_DIAGNOSTICS


def _reviewed_output_verdict_shape(verdict):
    """Refuse mocked/untrusted verdict data before any JSON serialization."""
    if type(verdict) is not dict or any(type(key) is not str for key in verdict):
        return False
    if set(verdict) != envelope.VERDICT_FIELDS:
        return False
    if (type(verdict["source_consistency"]) is not bool or
            verdict["independent_original_os_proof"] is not False or
            verdict["exclusive_server_dispatch_gate_proven"] is not False or
            verdict["can_authorize_annual_run"] is not False):
        return False
    codes = verdict["diagnostics"]
    if (type(codes) is not tuple or len(codes) > 256 or
            any(type(code) is not str or
                code not in APPROVED_OUTPUT_DIAGNOSTICS for code in codes)):
        return False
    return (verdict["source_consistency"] is (not codes) and
            codes == tuple(sorted(set(codes))))


def _emit_safe_verdict(verdict, output_stream):
    """Never claim a complete machine-readable result on failed delivery."""
    try:
        encoded = (json.dumps(verdict, sort_keys=True, ensure_ascii=True,
                              separators=(",", ":")) + "\n")
        written = output_stream.write(encoded)
        if type(written) is not int or written != len(encoded):
            return False
        flush = getattr(output_stream, "flush", None)
        if flush is not None:
            if not callable(flush):
                return False
            if flush() is not None:
                # Python text stream flush has no return value. Do not
                # infer successful delivery from an unexpected result.
                return False
    except (OSError, UnicodeError, ValueError, TypeError, RuntimeError,
            RecursionError, AssertionError, AttributeError, OverflowError,
            IndexError, EOFError):
        return False
    return True


def run_stdin_review(input_stream, output_stream):
    """Read complete capped stdin text and emit one fail-closed verdict."""
    raw, read_error = _read_complete_bounded_stdin(input_stream)
    if read_error is not None:
        verdict = envelope.fail_closed(read_error)
    else:
        try:
            verdict = envelope.review_bundle_json_text(raw)
        except (OSError, UnicodeError, ValueError, TypeError, RuntimeError,
                RecursionError, AssertionError, AttributeError, OverflowError,
                IndexError, EOFError):
            # Never emit a traceback, exception message or source bytes.
            verdict = envelope.fail_closed("BUNDLE_OFFLINE_REVIEW_UNREVIEWED")
    # A mocked/corrupted reviewer must not smuggle arbitrary fields,
    # diagnostics or execution authorization through the final CLI output.
    if not _reviewed_output_verdict_shape(verdict):
        verdict = envelope.fail_closed("BUNDLE_OFFLINE_RESULT_SHAPE_UNREVIEWED")
    # Never echo supplied evidence. An incomplete verdict cannot
    # produce a success exit code.
    if not _emit_safe_verdict(verdict, output_stream):
        return 2
    # Zero is merely *offline source consistency*, never execution consent.
    return 0 if verdict["source_consistency"] is True else 2


def main():
    # No positional filenames, network URLs, auth tokens or workflow actions.
    if len(sys.argv) != 1:
        verdict = envelope.fail_closed("BUNDLE_STDIN_ONLY_INVOCATION_REQUIRED")
        _emit_safe_verdict(verdict, sys.stdout)
        return 2
    return run_stdin_review(sys.stdin, sys.stdout)


class _ShortReadTextStream:
    """Synthetic, nonblocking-style text stream with short positive reads."""
    def __init__(self, raw, chunk_size):
        self.raw = raw
        self.chunk_size = chunk_size
        self.offset = 0
        self.request_sizes = []

    def read(self, requested):
        self.request_sizes.append(requested)
        n = min(requested, self.chunk_size)
        part = self.raw[self.offset:self.offset+n]
        self.offset += len(part)
        return part


class ExplicitStdinReviewIsNotAnnualWorkflowAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        envelope.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        fixture = envelope.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        fixture.setUp()
        self.bundle = fixture.envelope
        self.stdout = io.StringIO()

    def run_raw(self, raw):
        status = run_stdin_review(io.StringIO(raw), self.stdout)
        record = json.loads(self.stdout.getvalue())
        return status, record

    def run_fixture(self):
        return self.run_raw(json.dumps(self.bundle))

    def test_consistent_bundle_reports_source_consistency_only(self):
        status, record = self.run_fixture()
        self.assertEqual(status, 0)
        self.assertTrue(record["source_consistency"])
        self.assertEqual(record["diagnostics"], [])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_output_contains_no_caller_original_evidence(self):
        status, record = self.run_fixture()
        self.assertEqual(status, 0)
        self.assertNotIn("changed_bytes_b64", self.stdout.getvalue())
        self.assertNotIn("phase3-backtester-acceptance-", self.stdout.getvalue())
        self.assertEqual(len(record), 5)

    def test_invalid_json_has_nonzero_exit_and_diagnostic(self):
        status, record = self.run_raw('{"schema":')
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED", record["diagnostics"])

    def test_null_stdin_object_never_passes(self):
        status, record = self.run_raw("null")
        self.assertEqual(status, 2)
        self.assertFalse(record["source_consistency"])

    def test_empty_stdin_never_passes(self):
        status, record = self.run_raw("")
        self.assertEqual(status, 2)
        self.assertFalse(record["can_authorize_annual_run"])

    def test_missing_evidence_category_has_nonzero_exit(self):
        self.bundle.pop("full_tree_snapshots")
        status, record = self.run_fixture()
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_KEY_INVENTORY_UNREVIEWED",
                      record["diagnostics"])

    def test_tampered_source_bytes_cannot_pass(self):
        import base64
        self.bundle["changed_bytes_b64"]["tests/sample.py"] = (
            base64.b64encode(b"other code\n").decode("ascii"))
        status, record = self.run_fixture()
        self.assertEqual(status, 2)
        self.assertFalse(record["source_consistency"])

    def test_job_log_text_changed_without_digest_cannot_pass(self):
        self.bundle["raw_ci_runner_logs"]["8000"] += "\nadded record"
        status, record = self.run_fixture()
        self.assertEqual(status, 2)
        self.assertFalse(record["source_consistency"])

    def test_excessive_stdin_is_rejected_without_processing(self):
        status, record = self.run_raw(" "*(envelope.MAX_TEXT_CHARS+1))
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_JSON_TEXT_UNREVIEWED",
                      record["diagnostics"])

    def test_source_consistency_never_enables_any_annual_gate(self):
        _, record = self.run_fixture()
        self.assertFalse(record["independent_original_os_proof"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_duplicate_json_keys_have_nonzero_exit(self):
        status, record = self.run_raw('{"schema":1,"schema":2}')
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                      record["diagnostics"])

    def test_malformed_run_map_key_is_rejected(self):
        item = self.bundle["jobs_by_run"].pop("8000")
        self.bundle["jobs_by_run"]["08000"] = item
        status, record = self.run_fixture()
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_RUN_KEY_UNREVIEWED", record["diagnostics"])


    def run_stream(self, stream):
        status = run_stdin_review(stream, self.stdout)
        return status, json.loads(self.stdout.getvalue())

    def test_short_reads_clean_bundle_consistency_only(self):
        raw = json.dumps(self.bundle)
        status, record = self.run_stream(_ShortReadTextStream(raw, 13))
        self.assertEqual(status, 0)
        self.assertEqual(record["diagnostics"], [])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_one_character_short_reads_preserve_clean_result(self):
        raw = json.dumps(self.bundle)
        status, record = self.run_stream(_ShortReadTextStream(raw, 1))
        self.assertEqual(status, 0)
        self.assertTrue(record["source_consistency"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])

    def test_short_read_valid_prefix_plus_invalid_trailer_is_rejected(self):
        raw = json.dumps(self.bundle)
        stream = _ShortReadTextStream(raw + "\nextra", len(raw))
        status, record = self.run_stream(stream)
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED", record["diagnostics"])

    def test_short_read_valid_prefix_plus_second_json_is_rejected(self):
        raw = json.dumps(self.bundle)
        stream = _ShortReadTextStream(raw + '{"annual":true}', len(raw))
        status, record = self.run_stream(stream)
        self.assertEqual(status, 2)
        self.assertFalse(record["source_consistency"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_short_read_truncated_json_is_rejected(self):
        raw = json.dumps(self.bundle)
        status, record = self.run_stream(_ShortReadTextStream(raw[:-1], 23))
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED", record["diagnostics"])

    def test_read_error_after_valid_prefix_does_not_accept_prefix(self):
        raw = json.dumps(self.bundle)

        class ErrorOnSecondRead:
            count = 0
            def read(self, requested):
                self.count += 1
                if self.count == 1:
                    return raw
                raise OSError("do-not-echo-secret")

        status, record = self.run_stream(ErrorOnSecondRead())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])
        self.assertNotIn("secret", self.stdout.getvalue())

    def test_unicode_error_after_valid_prefix_is_fail_closed(self):
        raw = json.dumps(self.bundle)

        class DecodeErrorOnSecondRead:
            count = 0
            def read(self, requested):
                self.count += 1
                if self.count == 1:
                    return raw
                raise UnicodeError("sensitive-data")

        status, record = self.run_stream(DecodeErrorOnSecondRead())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])
        self.assertNotIn("sensitive-data", self.stdout.getvalue())

    def test_bytes_input_chunk_cannot_be_treated_as_text(self):
        status, record = self.run_stream(io.BytesIO(json.dumps(self.bundle).encode()))
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])

    def test_none_chunk_is_rejected_without_exception(self):
        class NullRead:
            def read(self, requested):
                return None

        status, record = self.run_stream(NullRead())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])

    def test_read_chunk_length_is_bounded(self):
        stream = _ShortReadTextStream(json.dumps(self.bundle), 70000)
        status, record = self.run_stream(stream)
        self.assertEqual(status, 0)
        self.assertTrue(stream.request_sizes)
        self.assertLessEqual(max(stream.request_sizes), MAX_STDIN_READ_CHARS)
        self.assertFalse(record["can_authorize_annual_run"])

    def test_chunked_extra_text_is_rejected_without_echo(self):
        raw = json.dumps(self.bundle) + ' "protected-log-sentinel"'
        stream = _ShortReadTextStream(raw, 7)
        status, record = self.run_stream(stream)
        self.assertEqual(status, 2)
        self.assertFalse(record["source_consistency"])
        self.assertNotIn("protected-log-sentinel", self.stdout.getvalue())

    def test_chunk_boundaries_do_not_change_bad_diagnostic(self):
        raw = '{"schema":1,"schema":2}'
        diagnostic_sets = []
        for chunk_size in (1, 3, 8, 65536):
            output = io.StringIO()
            status = run_stdin_review(_ShortReadTextStream(raw, chunk_size), output)
            self.assertEqual(status, 2)
            diagnostic_sets.append(json.loads(output.getvalue())["diagnostics"])
        self.assertEqual(diagnostic_sets,
                         [["BUNDLE_JSON_GRAMMAR_UNREVIEWED"]] * 4)


    def test_nonconforming_stream_overreturn_rejected(self):
        raw = json.dumps(self.bundle) + " " * MAX_STDIN_READ_CHARS
        class Overreturn:
            def read(self, n):
                return raw
        status, record = self.run_stream(Overreturn())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_overreturn_after_valid_prefix_rejected(self):
        raw = json.dumps(self.bundle)
        class LateOverreturn:
            calls = 0
            def read(self, n):
                self.calls += 1
                return raw if self.calls == 1 else " " * (n + 1)
        status, record = self.run_stream(LateOverreturn())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])

    def test_exact_per_read_cap_accepts_complete_json(self):
        raw = json.dumps(self.bundle)
        stream = _ShortReadTextStream(raw + " " * (MAX_STDIN_READ_CHARS-len(raw)), MAX_STDIN_READ_CHARS)
        status, record = self.run_stream(stream)
        self.assertEqual(status, 0)
        self.assertLessEqual(max(stream.request_sizes), MAX_STDIN_READ_CHARS)
        self.assertFalse(record["can_authorize_annual_run"])

    def test_exact_total_cap_accepts_consistency_only(self):
        raw = json.dumps(self.bundle)
        status, record = self.run_stream(io.StringIO(raw + " " * (envelope.MAX_TEXT_CHARS-len(raw))))
        self.assertEqual(status, 0)
        self.assertTrue(record["source_consistency"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_one_above_total_cap_is_rejected(self):
        raw = json.dumps(self.bundle)
        status, record = self.run_stream(io.StringIO(raw + " " * (envelope.MAX_TEXT_CHARS+1-len(raw))))
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_JSON_TEXT_UNREVIEWED", record["diagnostics"])

    def test_only_one_verdict_written_after_many_short_reads(self):
        class Capture:
            def __init__(self):
                self.writes = []
            def write(self, value):
                self.writes.append(value)
                return len(value)
        target = Capture()
        rc = run_stdin_review(_ShortReadTextStream(json.dumps(self.bundle), 2), target)
        self.assertEqual(rc, 0)
        self.assertEqual(len(target.writes), 1)
        self.assertEqual(len(target.writes[0].splitlines()), 1)

    def test_late_value_error_has_safe_single_verdict(self):
        raw = json.dumps(self.bundle)
        class FailLate:
            calls = 0
            def read(self, n):
                self.calls += 1
                if self.calls == 1:
                    return raw
                raise ValueError("protected-sentinel")
        status, record = self.run_stream(FailLate())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])
        self.assertNotIn("protected-sentinel", self.stdout.getvalue())

    def test_str_subclass_chunk_fails_type_boundary(self):
        raw = json.dumps(self.bundle)
        class Substr(str):
            pass
        class Fake:
            def read(self, n):
                return Substr(raw)
        status, record = self.run_stream(Fake())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])


    def test_subclass_zero_length_chunk_refused_not_treated_as_eof(self):
        class TextSubclass(str):
            pass
        class SubclassEOF:
            def read(self, requested):
                return TextSubclass("")
        status, record = self.run_stream(SubclassEOF())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])

    def test_subclass_partial_prefix_cannot_bypass_strict_type(self):
        raw = json.dumps(self.bundle)
        class SubclassPrefix:
            def read(self, requested):
                return type("EvidenceText", (str,), {})(raw[:10])
        status, record = self.run_stream(SubclassPrefix())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_subclass_chunk_diagnostic_does_not_echo_sensitive_text(self):
        class Untrusted(str):
            pass
        class Malformed:
            def read(self, requested):
                return Untrusted("secret-token-sentinel")
        status, record = self.run_stream(Malformed())
        self.assertEqual(status, 2)
        self.assertEqual(record["diagnostics"], ["BUNDLE_STDIN_READ_UNREVIEWED"])
        self.assertNotIn("secret-token-sentinel", self.stdout.getvalue())

    def test_runtime_error_from_stream_fails_closed_without_echo(self):
        class BrokenStream:
            def read(self, requested):
                raise RuntimeError("private-evidence-sentinel")
        status, record = self.run_stream(BrokenStream())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])
        self.assertNotIn("private-evidence-sentinel", self.stdout.getvalue())

    def test_runtime_error_after_valid_prefix_fails_closed(self):
        raw = json.dumps(self.bundle)
        class BrokenAfterPrefix:
            calls = 0
            def read(self, requested):
                self.calls += 1
                if self.calls == 1:
                    return raw
                raise RuntimeError("late-stream-fault")
        status, record = self.run_stream(BrokenAfterPrefix())
        self.assertEqual(status, 2)
        self.assertFalse(record["source_consistency"])
        self.assertIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])

    def test_plain_string_short_reads_still_pass_after_type_enforcement(self):
        stream = _ShortReadTextStream(json.dumps(self.bundle), 9)
        status, record = self.run_stream(stream)
        self.assertEqual(status, 0)
        self.assertEqual(record["diagnostics"], [])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_plain_string_empty_eof_is_only_valid_end_marker(self):
        class EmptyStream:
            def read(self, requested):
                return ""
        status, record = self.run_stream(EmptyStream())
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED", record["diagnostics"])
        self.assertNotIn("BUNDLE_STDIN_READ_UNREVIEWED", record["diagnostics"])


    def _invoke_main_for_test(self, argv, raw):
        from unittest.mock import patch
        provided_stdin = io.StringIO(raw)
        out = io.StringIO()
        with patch.object(sys, "argv", argv), \
             patch.object(sys, "stdin", provided_stdin), \
             patch.object(sys, "stdout", out):
            rc = main()
        lines = out.getvalue().splitlines()
        self.assertEqual(len(lines), 1)
        return rc, json.loads(lines[0]), provided_stdin.tell(), out.getvalue()

    def test_main_accepts_only_stdin_synthetic_consistency(self):
        raw = json.dumps(self.bundle)
        status, result, chars_read, output = self._invoke_main_for_test(
            ["offline-review"], raw)
        self.assertEqual(status, 0)
        self.assertEqual(chars_read, len(raw))
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])
        self.assertEqual(len(result), 5)

    def test_main_rejects_filename_without_reading_stdin(self):
        raw = json.dumps(self.bundle)
        status, result, chars_read, _ = self._invoke_main_for_test(
            ["offline-review", "/tmp/private-evidence.json"], raw)
        self.assertEqual(status, 2)
        self.assertEqual(chars_read, 0)
        self.assertEqual(result["diagnostics"],
                         ["BUNDLE_STDIN_ONLY_INVOCATION_REQUIRED"])

    def test_main_rejects_url_argument_without_reading_stdin(self):
        raw = json.dumps(self.bundle)
        status, result, chars_read, output = self._invoke_main_for_test(
            ["offline-review", "https://example.invalid/bundle"], raw)
        self.assertEqual(status, 2)
        self.assertEqual(chars_read, 0)
        self.assertFalse(result["can_authorize_annual_run"])
        self.assertNotIn("example.invalid", output)

    def test_main_rejects_help_flag_without_reading_stdin(self):
        raw = json.dumps(self.bundle)
        status, result, chars_read, _ = self._invoke_main_for_test(
            ["offline-review", "--help"], raw)
        self.assertEqual(status, 2)
        self.assertEqual(chars_read, 0)
        self.assertIn("BUNDLE_STDIN_ONLY_INVOCATION_REQUIRED",
                      result["diagnostics"])

    def test_main_rejects_multiple_unreviewed_arguments(self):
        raw = json.dumps(self.bundle)
        status, result, chars_read, _ = self._invoke_main_for_test(
            ["offline-review", "--authorize", "2023", "run385"], raw)
        self.assertEqual(status, 2)
        self.assertEqual(chars_read, 0)
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])

    def test_main_rejects_missing_program_argument(self):
        raw = json.dumps(self.bundle)
        status, result, chars_read, _ = self._invoke_main_for_test([], raw)
        self.assertEqual(status, 2)
        self.assertEqual(chars_read, 0)
        self.assertEqual(result["diagnostics"],
                         ["BUNDLE_STDIN_ONLY_INVOCATION_REQUIRED"])

    def test_main_rejects_malformed_stdin_without_echo(self):
        raw = '{"schema":"secret-sentinel"'
        status, result, chars_read, output = self._invoke_main_for_test(
            ["offline-review"], raw)
        self.assertEqual(status, 2)
        self.assertEqual(chars_read, len(raw))
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED", result["diagnostics"])
        self.assertNotIn("secret-sentinel", output)

    def test_main_rejects_false_authorization_extra_input(self):
        data = dict(self.bundle)
        data["can_authorize_annual_run"] = True
        raw = json.dumps(data)
        status, result, chars_read, _ = self._invoke_main_for_test(
            ["offline-review"], raw)
        self.assertEqual(status, 2)
        self.assertEqual(chars_read, len(raw))
        self.assertIn("BUNDLE_KEY_INVENTORY_UNREVIEWED", result["diagnostics"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_main_rejects_positional_secret_without_echo(self):
        raw = json.dumps(self.bundle)
        status, result, chars_read, output = self._invoke_main_for_test(
            ["offline-review", "private-source-sentinel"], raw)
        self.assertEqual(status, 2)
        self.assertEqual(chars_read, 0)
        self.assertNotIn("private-source-sentinel", output)
        self.assertEqual(len(result), 5)


    def test_stdin_stdout_short_write_forces_nonzero_exit(self):
        class ShortOutput:
            def write(self, value):
                return len(value)-1
        status = run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), ShortOutput())
        self.assertEqual(status, 2)

    def test_stdin_stdout_zero_write_forces_nonzero_exit(self):
        class NoOutput:
            def write(self, value):
                return 0
        status = run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), NoOutput())
        self.assertEqual(status, 2)

    def test_stdin_stdout_overreported_count_forces_nonzero_exit(self):
        class OverreportingOutput:
            def write(self, value):
                return len(value)+1
        status = run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), OverreportingOutput())
        self.assertEqual(status, 2)

    def test_stdin_stdout_unknown_count_forces_nonzero_exit(self):
        class UnknownOutput:
            def write(self, value):
                return None
        status = run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), UnknownOutput())
        self.assertEqual(status, 2)

    def test_stdin_stdout_bool_count_not_treated_as_integer(self):
        class BooleanOutput:
            def write(self, value):
                return True
        status = run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), BooleanOutput())
        self.assertEqual(status, 2)

    def test_stdin_stdout_oserror_is_safe_nonzero_exit(self):
        class BrokenOutput:
            def write(self, value):
                raise OSError("protected-evidence-canary")
        status = run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), BrokenOutput())
        self.assertEqual(status, 2)

    def test_stdin_stdout_unicode_error_is_safe_nonzero_exit(self):
        class BrokenOutput:
            def write(self, value):
                raise UnicodeError("source-canary")
        status = run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), BrokenOutput())
        self.assertEqual(status, 2)

    def test_stdin_stdout_runtime_error_is_safe_nonzero_exit(self):
        class BrokenOutput:
            def write(self, value):
                raise RuntimeError("source-canary")
        status = run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), BrokenOutput())
        self.assertEqual(status, 2)

    def test_stdin_stdout_regular_full_write_has_one_safe_record(self):
        status, record = self.run_fixture()
        self.assertEqual(status, 0)
        self.assertTrue(record["source_consistency"])
        self.assertEqual(len(self.stdout.getvalue().splitlines()), 1)
        self.assertFalse(record["can_authorize_annual_run"])

    def test_invalid_bundle_regular_full_write_remains_nonzero(self):
        status, record = self.run_raw('{"invalid":"canary"}')
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_KEY_INVENTORY_UNREVIEWED",
                      record["diagnostics"])
        self.assertNotIn("canary", self.stdout.getvalue())
        self.assertFalse(record["can_authorize_annual_run"])


    def test_stdin_output_stream_flush_called_on_complete_write(self):
        class BufferedOutput:
            def __init__(self):
                self.flushes = 0
                self.text = ""
            def write(self, value):
                self.text += value
                return len(value)
            def flush(self):
                self.flushes += 1
        output = BufferedOutput()
        rc = run_stdin_review(io.StringIO(json.dumps(self.bundle)), output)
        self.assertEqual(rc, 0)
        self.assertEqual(output.flushes, 1)
        self.assertFalse(json.loads(output.text)["can_authorize_annual_run"])

    def test_stdin_output_oserror_during_flush_forces_failure(self):
        class FailingOutput:
            def write(self, value):
                return len(value)
            def flush(self):
                raise BrokenPipeError("private-log-canary")
        rc = run_stdin_review(io.StringIO(json.dumps(self.bundle)),
                              FailingOutput())
        self.assertEqual(rc, 2)

    def test_stdin_output_runtime_error_during_flush_forces_failure(self):
        class FailingOutput:
            def write(self, value):
                return len(value)
            def flush(self):
                raise RuntimeError("private-path-canary")
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), FailingOutput()), 2)

    def test_stdin_output_assertion_error_during_flush_forces_failure(self):
        class FailingOutput:
            def write(self, value):
                return len(value)
            def flush(self):
                raise AssertionError("synthetic-canary")
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), FailingOutput()), 2)

    def test_stdin_output_noncallable_flush_is_nonzero(self):
        class UnreviewedOutput:
            flush = True
            def write(self, value):
                return len(value)
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), UnreviewedOutput()), 2)

    def test_stdin_output_without_flush_method_preserves_full_write(self):
        class UnbufferedOutput:
            def __init__(self):
                self.text = ""
            def write(self, value):
                self.text += value
                return len(value)
        output = UnbufferedOutput()
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), output), 0)
        self.assertEqual(len(output.text.splitlines()), 1)

    def test_stdin_output_short_write_never_calls_flush(self):
        class PartialOutput:
            def __init__(self):
                self.flushes = 0
            def write(self, value):
                return len(value)-1
            def flush(self):
                self.flushes += 1
        output = PartialOutput()
        rc = run_stdin_review(io.StringIO(json.dumps(self.bundle)), output)
        self.assertEqual(rc, 2)
        self.assertEqual(output.flushes, 0)

    def test_stdin_invalid_json_full_write_flushed_but_still_failure(self):
        class BufferedOutput:
            def __init__(self):
                self.text = ""
                self.flushes = 0
            def write(self, value):
                self.text += value
                return len(value)
            def flush(self):
                self.flushes += 1
        output = BufferedOutput()
        rc = run_stdin_review(io.StringIO('{"private":"not a bundle"}'), output)
        self.assertEqual(rc, 2)
        self.assertEqual(output.flushes, 1)
        self.assertNotIn("not a bundle", output.text)
        self.assertFalse(json.loads(output.text)["can_authorize_annual_run"])

    def test_stdin_real_stringio_flush_keeps_source_only_verdict(self):
        out = io.StringIO()
        rc = run_stdin_review(io.StringIO(json.dumps(self.bundle)), out)
        self.assertEqual(rc, 0)
        record = json.loads(out.getvalue())
        self.assertTrue(record["source_consistency"])
        self.assertFalse(record["independent_original_os_proof"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(record["can_authorize_annual_run"])


    def test_stdin_utf8_reader_excess_rejected_before_bundle_review(self):
        raw = '"' + "é" * (envelope.MAX_TEXT_UTF8_BYTES//2) + '"'
        parsed, code = _read_complete_bounded_stdin(io.StringIO(raw))
        self.assertIsNone(parsed)
        self.assertEqual(code, "BUNDLE_JSON_TEXT_UNREVIEWED")

    def test_stdin_utf8_reader_exact_boundary_reads_complete_text(self):
        raw = '"' + "é" * (envelope.MAX_TEXT_UTF8_BYTES//2-1) + '"'
        self.assertEqual(len(raw.encode("utf-8")),
                         envelope.MAX_TEXT_UTF8_BYTES)
        parsed, code = _read_complete_bounded_stdin(io.StringIO(raw))
        self.assertIsNone(code)
        self.assertEqual(parsed, raw)

    def test_stdin_utf8_reader_emoji_excess_refused(self):
        raw = '"' + "🚀" * (envelope.MAX_TEXT_UTF8_BYTES//4) + '"'
        parsed, code = _read_complete_bounded_stdin(io.StringIO(raw))
        self.assertIsNone(parsed)
        self.assertEqual(code, "BUNDLE_JSON_TEXT_UNREVIEWED")

    def test_stdin_utf8_reader_lone_surrogate_fails_closed(self):
        raw = '{"private":"\ud800"}'
        parsed, code = _read_complete_bounded_stdin(io.StringIO(raw))
        self.assertIsNone(parsed)
        self.assertEqual(code, "BUNDLE_JSON_UNICODE_UNREVIEWED")

    def test_stdin_utf8_reader_short_chunks_counts_bytes(self):
        raw = '{"a":"' + "é"*100 + '"}'
        parsed, code = _read_complete_bounded_stdin(_ShortReadTextStream(raw, 1))
        self.assertIsNone(code)
        self.assertEqual(parsed, raw)

    def test_stdin_utf8_reader_no_early_success_on_multibyte_prefix(self):
        raw = '"' + "é" * (envelope.MAX_TEXT_UTF8_BYTES//2) + '"'
        parsed, code = _read_complete_bounded_stdin(_ShortReadTextStream(raw, 503))
        self.assertIsNone(parsed)
        self.assertEqual(code, "BUNDLE_JSON_TEXT_UNREVIEWED")

    def test_stdin_utf8_overrun_safe_verdict_never_echoes_input(self):
        raw = '{"private-canary":"' + "é"*(envelope.MAX_TEXT_UTF8_BYTES//2) + '"}'
        out = io.StringIO()
        rc = run_stdin_review(io.StringIO(raw), out)
        self.assertEqual(rc, 2)
        result = json.loads(out.getvalue())
        self.assertEqual(result["diagnostics"], ["BUNDLE_JSON_TEXT_UNREVIEWED"])
        self.assertNotIn("private-canary", out.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_stdin_read_complete_ascii_valid_fixture_still_source_only(self):
        raw, error = _read_complete_bounded_stdin(
            io.StringIO(json.dumps(self.bundle)))
        self.assertIsNone(error)
        self.assertTrue(json.loads(raw)["schema"].startswith("fmp-"))
        rc = run_stdin_review(io.StringIO(raw), self.stdout)
        self.assertEqual(rc, 0)
        self.assertFalse(json.loads(self.stdout.getvalue())["can_authorize_annual_run"])

    def test_stdin_utf8_scalar_budget_false_all_execution_authority(self):
        out = io.StringIO()
        rc = run_stdin_review(io.StringIO(json.dumps(self.bundle)), out)
        result = json.loads(out.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])


    def test_denied_argv_uses_single_checked_machine_readable_verdict(self):
        from unittest.mock import patch
        out = io.StringIO()
        with patch.object(sys, "argv", ["review", "--unsafe"]), \
             patch.object(sys, "stdout", out):
            rc = main()
        self.assertEqual(rc, 2)
        lines = out.getvalue().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(json.loads(lines[0])["diagnostics"],
                         ["BUNDLE_STDIN_ONLY_INVOCATION_REQUIRED"])

    def test_denied_argv_does_not_echo_supplied_path(self):
        from unittest.mock import patch
        out = io.StringIO()
        with patch.object(sys, "argv", ["review", "protected-canary.json"]), \
             patch.object(sys, "stdout", out):
            self.assertEqual(main(), 2)
        self.assertNotIn("protected-canary", out.getvalue())

    def test_denied_argv_never_reads_stdin(self):
        from unittest.mock import patch
        class Unreadable:
            def read(self, amount):
                raise AssertionError("denied args must not read evidence")
        out = io.StringIO()
        with patch.object(sys, "argv", ["review", "--url"]), \
             patch.object(sys, "stdin", Unreadable()), \
             patch.object(sys, "stdout", out):
            self.assertEqual(main(), 2)

    def test_denied_argv_short_write_remains_nonzero(self):
        from unittest.mock import patch
        class Partial:
            def write(self, value):
                return len(value)-1
        with patch.object(sys, "argv", ["review", "--unsafe"]), \
             patch.object(sys, "stdout", Partial()):
            self.assertEqual(main(), 2)

    def test_denied_argv_stdout_oserror_does_not_escape(self):
        from unittest.mock import patch
        class Broken:
            def write(self, value):
                raise BrokenPipeError("private-canary")
        with patch.object(sys, "argv", ["review", "--unsafe"]), \
             patch.object(sys, "stdout", Broken()):
            self.assertEqual(main(), 2)

    def test_denied_argv_flush_error_does_not_escape(self):
        from unittest.mock import patch
        class Broken:
            def write(self, value):
                return len(value)
            def flush(self):
                raise OSError("private-canary")
        with patch.object(sys, "argv", ["review", "--unsafe"]), \
             patch.object(sys, "stdout", Broken()):
            self.assertEqual(main(), 2)

    def test_denied_argv_flushed_once_before_exit(self):
        from unittest.mock import patch
        class Capture:
            def __init__(self):
                self.text = ""
                self.flushes = 0
            def write(self, value):
                self.text += value
                return len(value)
            def flush(self):
                self.flushes += 1
        out = Capture()
        with patch.object(sys, "argv", ["review", "ignored"]), \
             patch.object(sys, "stdout", out):
            self.assertEqual(main(), 2)
        self.assertEqual(out.flushes, 1)
        self.assertFalse(json.loads(out.text)["can_authorize_annual_run"])

    def test_denied_argv_noncallable_flush_remains_nonzero(self):
        from unittest.mock import patch
        class Invalid:
            flush = True
            def write(self, value):
                return len(value)
        with patch.object(sys, "argv", ["review", "ignored"]), \
             patch.object(sys, "stdout", Invalid()):
            self.assertEqual(main(), 2)

    def test_normal_main_stdin_synthetic_success_uses_shared_writer(self):
        from unittest.mock import patch
        out = io.StringIO()
        with patch.object(sys, "argv", ["review"]), \
             patch.object(sys, "stdin", io.StringIO(json.dumps(self.bundle))), \
             patch.object(sys, "stdout", out):
            self.assertEqual(main(), 0)
        result = json.loads(out.getvalue())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["can_authorize_annual_run"])


    def test_stdin_stream_assertion_failure_is_sanitized(self):
        class Fake:
            def read(self, count):
                raise AssertionError("PRIVATE-CANARY")
        raw, code = _read_complete_bounded_stdin(Fake())
        self.assertIsNone(raw)
        self.assertEqual(code, "BUNDLE_STDIN_READ_UNREVIEWED")

    def test_stdin_stream_missing_read_method_is_sanitized(self):
        raw, code = _read_complete_bounded_stdin(object())
        self.assertIsNone(raw)
        self.assertEqual(code, "BUNDLE_STDIN_READ_UNREVIEWED")

    def test_stdin_stream_overflow_error_is_sanitized(self):
        class Fake:
            def read(self, count):
                raise OverflowError("PRIVATE-CANARY")
        self.assertEqual(_read_complete_bounded_stdin(Fake())[1],
                         "BUNDLE_STDIN_READ_UNREVIEWED")

    def test_stdin_stream_index_error_is_sanitized(self):
        class Fake:
            def read(self, count):
                raise IndexError("PRIVATE-CANARY")
        self.assertEqual(_read_complete_bounded_stdin(Fake())[1],
                         "BUNDLE_STDIN_READ_UNREVIEWED")

    def test_stdin_stream_eof_error_is_sanitized(self):
        class Fake:
            def read(self, count):
                raise EOFError("PRIVATE-CANARY")
        self.assertEqual(_read_complete_bounded_stdin(Fake())[1],
                         "BUNDLE_STDIN_READ_UNREVIEWED")

    def test_stdin_stream_attribute_getter_exception_is_sanitized(self):
        class Fake:
            @property
            def read(self):
                raise AttributeError("PRIVATE-CANARY")
        self.assertEqual(_read_complete_bounded_stdin(Fake())[1],
                         "BUNDLE_STDIN_READ_UNREVIEWED")

    def test_stdin_stream_exception_never_echoed_in_verdict(self):
        class Fake:
            def read(self, count):
                raise AssertionError("PRIVATE-CANARY")
        out = io.StringIO()
        rc = run_stdin_review(Fake(), out)
        result = json.loads(out.getvalue())
        self.assertEqual(rc, 2)
        self.assertEqual(result["diagnostics"], ["BUNDLE_STDIN_READ_UNREVIEWED"])
        self.assertNotIn("PRIVATE-CANARY", out.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_stdin_read_error_still_emits_one_line_checked_json(self):
        class Fake:
            def read(self, count):
                raise EOFError("PRIVATE-CANARY")
        out = io.StringIO()
        rc = run_stdin_review(Fake(), out)
        self.assertEqual(rc, 2)
        self.assertEqual(len(out.getvalue().splitlines()), 1)
        self.assertFalse(json.loads(out.getvalue())["source_consistency"])

    def test_stdin_read_exception_guard_preserves_clean_source_only(self):
        out = io.StringIO()
        rc = run_stdin_review(io.StringIO(json.dumps(self.bundle)), out)
        self.assertEqual(rc, 0)
        result = json.loads(out.getvalue())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])


    def test_checked_writer_accepts_standard_none_flush_result(self):
        class Output:
            def __init__(self):
                self.flushes = 0
            def write(self, value):
                return len(value)
            def flush(self):
                self.flushes += 1
        output = Output()
        self.assertTrue(_emit_safe_verdict(envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED"),
                                          output))
        self.assertEqual(output.flushes, 1)

    def test_checked_writer_refuses_boolean_flush_return(self):
        class Output:
            def write(self, value):
                return len(value)
            def flush(self):
                return True
        self.assertFalse(_emit_safe_verdict(
            envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED"), Output()))

    def test_checked_writer_refuses_integer_flush_return(self):
        class Output:
            def write(self, value):
                return len(value)
            def flush(self):
                return 0
        self.assertFalse(_emit_safe_verdict(
            envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED"), Output()))

    def test_checked_writer_refuses_text_flush_return(self):
        class Output:
            def write(self, value):
                return len(value)
            def flush(self):
                return "flushed"
        self.assertFalse(_emit_safe_verdict(
            envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED"), Output()))

    def test_review_never_exits_zero_if_flush_reports_non_none(self):
        class Output:
            def write(self, value):
                return len(value)
            def flush(self):
                return False
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), Output()), 2)

    def test_denied_argv_with_invalid_flush_still_returns_two(self):
        from unittest.mock import patch
        class Output:
            def write(self, value):
                return len(value)
            def flush(self):
                return True
        with patch.object(sys, "argv", ["review", "--unsafe"]), \
             patch.object(sys, "stdout", Output()):
            self.assertEqual(main(), 2)

    def test_bad_flush_response_does_not_trigger_second_write(self):
        class Output:
            def __init__(self):
                self.writes = 0
            def write(self, value):
                self.writes += 1
                return len(value)
            def flush(self):
                return "unreviewed"
        output = Output()
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), output), 2)
        self.assertEqual(output.writes, 1)

    def test_real_stringio_flush_none_keeps_non_authorizing_verdict(self):
        out = io.StringIO()
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), out), 0)
        self.assertIsNone(out.flush())
        result = json.loads(out.getvalue())
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])


    def test_output_write_overflow_error_is_sanitized(self):
        class Output:
            def write(self, text):
                raise OverflowError("private-canary")
        out = Output()
        self.assertFalse(_emit_safe_verdict(
            envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED"), out))

    def test_output_write_index_error_is_sanitized(self):
        class Output:
            def write(self, text):
                raise IndexError("private-canary")
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), Output()), 2)

    def test_output_write_eof_error_is_sanitized(self):
        class Output:
            def write(self, text):
                raise EOFError("private-canary")
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), Output()), 2)

    def test_output_flush_overflow_error_is_sanitized(self):
        class Output:
            def write(self, text):
                return len(text)
            def flush(self):
                raise OverflowError("private-canary")
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), Output()), 2)

    def test_output_flush_index_error_is_sanitized(self):
        class Output:
            def write(self, text):
                return len(text)
            def flush(self):
                raise IndexError("private-canary")
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), Output()), 2)

    def test_output_flush_getter_eof_error_is_sanitized(self):
        class Output:
            def write(self, text):
                return len(text)
            @property
            def flush(self):
                raise EOFError("private-canary")
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), Output()), 2)

    def test_output_exception_denied_args_does_not_escape(self):
        from unittest.mock import patch
        class Output:
            def write(self, text):
                raise OverflowError("private-canary")
        with patch.object(sys, "argv", ["review", "--unsafe"]), \
             patch.object(sys, "stdout", Output()):
            self.assertEqual(main(), 2)

    def test_output_exception_never_retries_partial_write(self):
        class Output:
            def __init__(self):
                self.calls = 0
            def write(self, text):
                self.calls += 1
                raise IndexError("private-canary")
        output = Output()
        self.assertEqual(run_stdin_review(
            io.StringIO(json.dumps(self.bundle)), output), 2)
        self.assertEqual(output.calls, 1)

    def test_output_exception_guard_preserves_source_only_verdict(self):
        out = io.StringIO()
        rc = run_stdin_review(io.StringIO(json.dumps(self.bundle)), out)
        self.assertEqual(rc, 0)
        verdict = json.loads(out.getvalue())
        self.assertTrue(verdict["source_consistency"])
        self.assertFalse(verdict["independent_original_os_proof"])
        self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(verdict["can_authorize_annual_run"])


    def test_unexpected_review_runtime_error_yields_safe_verdict(self):
        from unittest.mock import patch
        with patch.object(envelope, "review_bundle_json_text",
                          side_effect=RuntimeError("private-canary")):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_OFFLINE_REVIEW_UNREVIEWED"])
        self.assertNotIn("private-canary", self.stdout.getvalue())

    def test_unexpected_review_assertion_error_is_sanitized(self):
        from unittest.mock import patch
        with patch.object(envelope, "review_bundle_json_text",
                          side_effect=AssertionError("private-canary")):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_OFFLINE_REVIEW_UNREVIEWED"])

    def test_unexpected_review_io_error_is_sanitized(self):
        from unittest.mock import patch
        with patch.object(envelope, "review_bundle_json_text",
                          side_effect=OSError("secret-source")):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_OFFLINE_REVIEW_UNREVIEWED"])

    def test_unexpected_review_unicode_error_is_sanitized(self):
        from unittest.mock import patch
        with patch.object(envelope, "review_bundle_json_text",
                          side_effect=UnicodeError("secret-source")):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_OFFLINE_REVIEW_UNREVIEWED"])

    def test_unexpected_review_overflow_error_is_sanitized(self):
        from unittest.mock import patch
        with patch.object(envelope, "review_bundle_json_text",
                          side_effect=OverflowError("private-canary")):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_OFFLINE_REVIEW_UNREVIEWED"])

    def test_unexpected_review_index_error_is_sanitized(self):
        from unittest.mock import patch
        with patch.object(envelope, "review_bundle_json_text",
                          side_effect=IndexError("private-canary")):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_OFFLINE_REVIEW_UNREVIEWED"])

    def test_unexpected_review_error_produces_one_checked_stdout_record(self):
        from unittest.mock import patch
        with patch.object(envelope, "review_bundle_json_text",
                          side_effect=RuntimeError("protected-original-canary")):
            out = io.StringIO()
            rc = run_stdin_review(io.StringIO(json.dumps(self.bundle)), out)
        self.assertEqual(rc, 2)
        self.assertEqual(len(out.getvalue().splitlines()), 1)
        self.assertFalse(json.loads(out.getvalue())["can_authorize_annual_run"])
        self.assertNotIn("protected-original-canary", out.getvalue())

    def test_unexpected_review_error_never_retries_evidence_review(self):
        from unittest.mock import patch
        with patch.object(envelope, "review_bundle_json_text",
                          side_effect=ValueError("private-canary")) as review:
            self.assertEqual(run_stdin_review(
                io.StringIO(json.dumps(self.bundle)), io.StringIO()), 2)
        review.assert_called_once()

    def test_unexpected_review_error_guard_keeps_positive_source_only(self):
        out = io.StringIO()
        rc = run_stdin_review(io.StringIO(json.dumps(self.bundle)), out)
        result = json.loads(out.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])


    def test_cli_rejects_true_annual_authorization_in_mocked_result(self):
        from unittest.mock import patch
        bad = envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED")
        bad["can_authorize_annual_run"] = True
        with patch.object(envelope, "review_bundle_json_text", return_value=bad):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertFalse(record["can_authorize_annual_run"])
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_OFFLINE_RESULT_SHAPE_UNREVIEWED"])

    def test_cli_rejects_mocked_independent_original_proof(self):
        from unittest.mock import patch
        bad = envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED")
        bad["independent_original_os_proof"] = True
        with patch.object(envelope, "review_bundle_json_text", return_value=bad):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertFalse(record["independent_original_os_proof"])

    def test_cli_rejects_mocked_exclusive_dispatch_gate(self):
        from unittest.mock import patch
        bad = envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED")
        bad["exclusive_server_dispatch_gate_proven"] = True
        with patch.object(envelope, "review_bundle_json_text", return_value=bad):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])

    def test_cli_rejects_mocked_extra_key_without_echoing_it(self):
        from unittest.mock import patch
        bad = envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED")
        bad["PRIVATE_RESULT_CANARY"] = "sensitive"
        with patch.object(envelope, "review_bundle_json_text", return_value=bad):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_OFFLINE_RESULT_SHAPE_UNREVIEWED"])
        self.assertNotIn("PRIVATE_RESULT_CANARY", self.stdout.getvalue())

    def test_cli_rejects_unknown_diagnostic_string_without_echo(self):
        from unittest.mock import patch
        bad = envelope.fail_closed("PRIVATE_DIAGNOSTIC_CANARY")
        with patch.object(envelope, "review_bundle_json_text", return_value=bad):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_OFFLINE_RESULT_SHAPE_UNREVIEWED"])
        self.assertNotIn("PRIVATE_DIAGNOSTIC_CANARY", self.stdout.getvalue())

    def test_cli_rejects_mocked_source_consistency_contradiction(self):
        from unittest.mock import patch
        bad = envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED")
        bad["source_consistency"] = True
        with patch.object(envelope, "review_bundle_json_text", return_value=bad):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertFalse(record["source_consistency"])

    def test_cli_rejects_mocked_missing_verdict_field(self):
        from unittest.mock import patch
        bad = envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED")
        del bad["independent_original_os_proof"]
        with patch.object(envelope, "review_bundle_json_text", return_value=bad):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertEqual(record["diagnostics"],
                         ["BUNDLE_OFFLINE_RESULT_SHAPE_UNREVIEWED"])

    def test_cli_rejects_mocked_custom_dict_key_before_rehash(self):
        from unittest.mock import patch
        class Untrusted:
            def __init__(self):
                self.hashes = 0
            def __hash__(self):
                self.hashes += 1
                return 28479
            def __eq__(self, other):
                raise AssertionError("no equality")
        bad = envelope.fail_closed("BUNDLE_SHAPE_UNREVIEWED")
        key = Untrusted()
        bad[key] = "private"
        key.hashes = 0
        with patch.object(envelope, "review_bundle_json_text", return_value=bad):
            rc, record = self.run_raw(json.dumps(self.bundle))
        self.assertEqual(rc, 2)
        self.assertEqual(key.hashes, 0)
        self.assertFalse(record["can_authorize_annual_run"])

    def test_cli_accepts_only_reviewed_known_negative_codes(self):
        valid = envelope.fail_closed("BUNDLE_JSON_TEXT_UNREVIEWED")
        self.assertTrue(_reviewed_output_verdict_shape(valid))
        self.assertFalse(_reviewed_output_verdict_shape(
            envelope.fail_closed("PRIVATE_CANARY")))

    def test_cli_final_verdict_guard_preserves_clean_synthetic_source(self):
        raw = json.dumps(self.bundle)
        rc, result = self.run_raw(raw)
        self.assertEqual(rc, 0)
        self.assertTrue(result["source_consistency"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])


    def test_cli_json_exact_total_object_members_is_not_array_overflow(self):
        raw = "[" + ",".join('[{"k":1},{"k":1}]' for _ in range(
            envelope.MAX_JSON_ARRAY_ITEMS)) + "]"
        rc, result = self.run_raw(raw)
        self.assertEqual(rc, 2)
        self.assertEqual(result["diagnostics"], ["BUNDLE_SHAPE_UNREVIEWED"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_cli_json_one_extra_object_member_reports_safe_grammar(self):
        raw = ("[" + '[{"k":1},{"k":1},{"k":1}],' +
               ",".join('[{"k":1},{"k":1}]' for _ in range(
                   envelope.MAX_JSON_ARRAY_ITEMS-1)) + "]")
        rc, result = self.run_raw(raw)
        self.assertEqual(rc, 2)
        self.assertEqual(result["diagnostics"], ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_cli_json_flat_array_over_limit_is_distinct_from_member_budget(self):
        raw = "[" + ",".join('{"k":1}' for _ in range(
            envelope.MAX_JSON_ARRAY_ITEMS+1)) + "]"
        rc, result = self.run_raw(raw)
        self.assertEqual(rc, 2)
        self.assertEqual(result["diagnostics"], ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertFalse(result["independent_original_os_proof"])

    def test_cli_json_quoted_punctuation_is_not_structural(self):
        canary = 'private-comma-canary:[,]{},:\\ "'
        rc, result = self.run_raw(json.dumps([canary]))
        self.assertEqual(rc, 2)
        self.assertEqual(result["diagnostics"], ["BUNDLE_SHAPE_UNREVIEWED"])
        self.assertNotIn(canary, self.stdout.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_cli_json_unicode_escape_forms_have_same_safe_shape(self):
        for ensure_ascii in (True, False):
            with self.subTest(ensure_ascii=ensure_ascii):
                self.stdout = io.StringIO()
                rc, result = self.run_raw(json.dumps(["🚀", "\u2028", '"\\'],
                                                    ensure_ascii=ensure_ascii))
                self.assertEqual(rc, 2)
                self.assertEqual(result["diagnostics"], ["BUNDLE_SHAPE_UNREVIEWED"])
                self.assertFalse(result["exclusive_server_dispatch_gate_proven"])

    def test_cli_json_unknown_object_field_does_not_echo_secret_key(self):
        rc, result = self.run_raw(json.dumps({"private-canary-secret": ["x"]}))
        self.assertEqual(rc, 2)
        self.assertEqual(result["diagnostics"],
                         ["BUNDLE_KEY_INVENTORY_UNREVIEWED"])
        self.assertNotIn("private-canary-secret", self.stdout.getvalue())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_cli_json_trailing_private_data_is_safe_grammar_failure(self):
        raw = json.dumps(["synthetic"]) + " private-trailing-canary"
        rc, result = self.run_raw(raw)
        self.assertEqual(rc, 2)
        self.assertEqual(result["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("private-trailing-canary", self.stdout.getvalue())
        self.assertFalse(result["source_consistency"])

    def test_cli_json_serialization_variants_remain_consistency_only(self):
        for opts in ({"sort_keys": True}, {"indent": 2},
                     {"separators": (",", ":")}):
            with self.subTest(options=opts):
                self.stdout = io.StringIO()
                rc, result = self.run_raw(json.dumps(self.bundle, **opts))
                self.assertEqual(rc, 0)
                self.assertTrue(result["source_consistency"])
                self.assertEqual(result["diagnostics"], [])
                self.assertFalse(result["independent_original_os_proof"])
                self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
                self.assertFalse(result["can_authorize_annual_run"])


if __name__ == "__main__":
    raise SystemExit(main())
