"""DEC-1700: integer digit ingress boundary in array-contained evidence.

Tests only; source parity below limit and grammar refusal above limit.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class NestedJsonIntegerDigitBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_integer_digit_boundary(self, category, path, digits, negative):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(digits, (source.MAX_JSON_INTEGER_DIGITS,
                               source.MAX_JSON_INTEGER_DIGITS + 1))
        self.assertIs(type(negative), bool)
        token = ("-" if negative else "") + ("9" * digits)
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        cursor = copied[category]
        for segment in path:
            cursor = cursor[segment]
        self.assertIs(type(cursor), dict)
        cursor["zz_dec1700_integer"] = "DEC1700_MARKER"
        encoded = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        needle = '"zz_dec1700_integer":"DEC1700_MARKER"'
        self.assertEqual(encoded.count(needle), 1)
        raw = encoded.replace(needle, '"zz_dec1700_integer":' + token, 1)
        parsed = source.review_bundle_json_text(raw)
        output = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(raw), output)
        emitted = json.loads(output.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        if digits > source.MAX_JSON_INTEGER_DIGITS:
            self.assertEqual(rc, 2)
            self.assertEqual(parsed["diagnostics"],
                             ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
            self.assertEqual(emitted["diagnostics"],
                             ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        else:
            number = int(token)
            self.assertEqual(len(str(abs(number))), digits)
            cursor["zz_dec1700_integer"] = number
            direct = source.review_bundle_envelope(copied)
            self.assertEqual(parsed, direct)
            self.assertNotIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                             parsed["diagnostics"])
            self.assertEqual(rc, 0 if direct["source_consistency"] else 2)
            self.assertEqual(emitted["diagnostics"],
                             list(direct["diagnostics"]))
            self.assertEqual(emitted["source_consistency"],
                             direct["source_consistency"])
        self.assertNotIn("DEC1700_MARKER", output.getvalue())
        self.assertNotIn("tests/sample.py", output.getvalue())
        self.assertNotIn("docs/sample.md", output.getvalue())
        for verdict in (parsed, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_integer_boundary_runs_positive_at_limit(self):
        self._assert_integer_digit_boundary(
            "runs", (0,), 64, False)

    def test_integer_boundary_runs_positive_above_limit(self):
        self._assert_integer_digit_boundary(
            "runs", (0,), 65, False)

    def test_integer_boundary_runs_negative_at_limit(self):
        self._assert_integer_digit_boundary(
            "runs", (0,), 64, True)

    def test_integer_boundary_runs_negative_above_limit(self):
        self._assert_integer_digit_boundary(
            "runs", (0,), 65, True)

    def test_integer_boundary_compare_files_positive_at_limit(self):
        self._assert_integer_digit_boundary(
            "compare", ("files", 0), 64, False)

    def test_integer_boundary_compare_files_positive_above_limit(self):
        self._assert_integer_digit_boundary(
            "compare", ("files", 0), 65, False)

    def test_integer_boundary_compare_files_negative_at_limit(self):
        self._assert_integer_digit_boundary(
            "compare", ("files", 0), 64, True)

    def test_integer_boundary_compare_files_negative_above_limit(self):
        self._assert_integer_digit_boundary(
            "compare", ("files", 0), 65, True)

    def test_integer_boundary_jobs_positive_at_limit(self):
        self._assert_integer_digit_boundary(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), 64, False)

    def test_integer_boundary_jobs_positive_above_limit(self):
        self._assert_integer_digit_boundary(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), 65, False)

    def test_integer_boundary_jobs_negative_at_limit(self):
        self._assert_integer_digit_boundary(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), 64, True)

    def test_integer_boundary_jobs_negative_above_limit(self):
        self._assert_integer_digit_boundary(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), 65, True)

    def test_integer_boundary_phase3_scenarios_positive_at_limit(self):
        self._assert_integer_digit_boundary(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), 64, False)

    def test_integer_boundary_phase3_scenarios_positive_above_limit(self):
        self._assert_integer_digit_boundary(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), 65, False)

    def test_integer_boundary_phase3_scenarios_negative_at_limit(self):
        self._assert_integer_digit_boundary(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), 64, True)

    def test_integer_boundary_phase3_scenarios_negative_above_limit(self):
        self._assert_integer_digit_boundary(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), 65, True)

    def test_integer_boundary_full_tree_entries_positive_at_limit(self):
        self._assert_integer_digit_boundary(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), 64, False)

    def test_integer_boundary_full_tree_entries_positive_above_limit(self):
        self._assert_integer_digit_boundary(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), 65, False)

    def test_integer_boundary_full_tree_entries_negative_at_limit(self):
        self._assert_integer_digit_boundary(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), 64, True)

    def test_integer_boundary_full_tree_entries_negative_above_limit(self):
        self._assert_integer_digit_boundary(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), 65, True)

    def test_integer_boundary_merge_parents_positive_at_limit(self):
        self._assert_integer_digit_boundary(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), 64, False)

    def test_integer_boundary_merge_parents_positive_above_limit(self):
        self._assert_integer_digit_boundary(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), 65, False)

    def test_integer_boundary_merge_parents_negative_at_limit(self):
        self._assert_integer_digit_boundary(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), 64, True)

    def test_integer_boundary_merge_parents_negative_above_limit(self):
        self._assert_integer_digit_boundary(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), 65, True)

    def test_integer_boundary_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
