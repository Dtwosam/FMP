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
    try:
        while True:
            remaining = envelope.MAX_TEXT_CHARS - size + 1
            requested = min(MAX_STDIN_READ_CHARS, remaining)
            part = input_stream.read(requested)
            if type(part) is not str or len(part) > requested:
                return None, "BUNDLE_STDIN_READ_UNREVIEWED"
            size += len(part)
            if size > envelope.MAX_TEXT_CHARS:
                return None, "BUNDLE_JSON_TEXT_UNREVIEWED"
            if not part:
                return "".join(chunks), None
            chunks.append(part)
    except (OSError, UnicodeError, ValueError, TypeError, RuntimeError,
            RecursionError):
        return None, "BUNDLE_STDIN_READ_UNREVIEWED"


def run_stdin_review(input_stream, output_stream):
    """Read complete capped stdin text and emit one fail-closed verdict."""
    raw, read_error = _read_complete_bounded_stdin(input_stream)
    if read_error is not None:
        verdict = envelope.fail_closed(read_error)
    else:
        verdict = envelope.review_bundle_json_text(raw)
    # Never echo supplied evidence. Only machine-readable verdict fields.
    output_stream.write(json.dumps(verdict, sort_keys=True,
                                   ensure_ascii=True,
                                   separators=(",", ":")) + "\n")
    # Zero is merely *offline source consistency*, never execution consent.
    return 0 if verdict["source_consistency"] is True else 2


def main():
    # No positional filenames, network URLs, auth tokens or workflow actions.
    if len(sys.argv) != 1:
        verdict = envelope.fail_closed("BUNDLE_STDIN_ONLY_INVOCATION_REQUIRED")
        sys.stdout.write(json.dumps(verdict, sort_keys=True) + "\n")
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


if __name__ == "__main__":
    raise SystemExit(main())
