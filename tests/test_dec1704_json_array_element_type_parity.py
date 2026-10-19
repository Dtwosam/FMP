"""DEC-1704: JSON-legal array element types defer to nested evidence review.

Replacing an evidence object with a JSON primitive is not a grammar error.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class EvidenceArrayElementJsonTypeParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_array_element_type_review_parity(self, category, path, token):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(token, ("null", "true", "false",
                              '"synthetic_non_object"', "[]", "0"))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        array = copied[category]
        for part in path:
            array = array[part]
        self.assertIs(type(array), list)
        self.assertGreater(len(array), 0)
        value = json.loads(token)
        self.assertNotEqual(type(value), dict)
        array[0] = value
        raw = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        self.assertEqual(json.loads(raw), copied)
        direct = source.review_bundle_envelope(copied)
        parsed = source.review_bundle_json_text(raw)
        self.assertEqual(direct, parsed)
        self.assertNotIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                         parsed["diagnostics"])
        self.assertNotIn("BUNDLE_JSON_UNICODE_UNREVIEWED",
                         parsed["diagnostics"])
        out = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(rc, 0 if direct["source_consistency"] else 2)
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"], list(direct["diagnostics"]))
        self.assertEqual(emitted["source_consistency"],
                         direct["source_consistency"])
        self.assertNotIn("synthetic_non_object", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for verdict in (direct, parsed, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_array_element_type_runs_null(self):
        self._assert_array_element_type_review_parity(
            "runs", (), "null")

    def test_array_element_type_runs_true(self):
        self._assert_array_element_type_review_parity(
            "runs", (), "true")

    def test_array_element_type_runs_false(self):
        self._assert_array_element_type_review_parity(
            "runs", (), "false")

    def test_array_element_type_runs_string(self):
        self._assert_array_element_type_review_parity(
            "runs", (), "\"synthetic_non_object\"")

    def test_array_element_type_runs_empty_array(self):
        self._assert_array_element_type_review_parity(
            "runs", (), "[]")

    def test_array_element_type_runs_integer_zero(self):
        self._assert_array_element_type_review_parity(
            "runs", (), "0")

    def test_array_element_type_jobs_null(self):
        self._assert_array_element_type_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "null")

    def test_array_element_type_jobs_true(self):
        self._assert_array_element_type_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "true")

    def test_array_element_type_jobs_false(self):
        self._assert_array_element_type_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "false")

    def test_array_element_type_jobs_string(self):
        self._assert_array_element_type_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "\"synthetic_non_object\"")

    def test_array_element_type_jobs_empty_array(self):
        self._assert_array_element_type_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "[]")

    def test_array_element_type_jobs_integer_zero(self):
        self._assert_array_element_type_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "0")

    def test_array_element_type_compare_files_null(self):
        self._assert_array_element_type_review_parity(
            "compare", ("files",), "null")

    def test_array_element_type_compare_files_true(self):
        self._assert_array_element_type_review_parity(
            "compare", ("files",), "true")

    def test_array_element_type_compare_files_false(self):
        self._assert_array_element_type_review_parity(
            "compare", ("files",), "false")

    def test_array_element_type_compare_files_string(self):
        self._assert_array_element_type_review_parity(
            "compare", ("files",), "\"synthetic_non_object\"")

    def test_array_element_type_compare_files_empty_array(self):
        self._assert_array_element_type_review_parity(
            "compare", ("files",), "[]")

    def test_array_element_type_compare_files_integer_zero(self):
        self._assert_array_element_type_review_parity(
            "compare", ("files",), "0")

    def test_array_element_type_phase3_scenarios_null(self):
        self._assert_array_element_type_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios"), "null")

    def test_array_element_type_phase3_scenarios_true(self):
        self._assert_array_element_type_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios"), "true")

    def test_array_element_type_phase3_scenarios_false(self):
        self._assert_array_element_type_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios"), "false")

    def test_array_element_type_phase3_scenarios_string(self):
        self._assert_array_element_type_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios"), "\"synthetic_non_object\"")

    def test_array_element_type_phase3_scenarios_empty_array(self):
        self._assert_array_element_type_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios"), "[]")

    def test_array_element_type_phase3_scenarios_integer_zero(self):
        self._assert_array_element_type_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios"), "0")

    def test_array_element_type_full_tree_entries_null(self):
        self._assert_array_element_type_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "null")

    def test_array_element_type_full_tree_entries_true(self):
        self._assert_array_element_type_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "true")

    def test_array_element_type_full_tree_entries_false(self):
        self._assert_array_element_type_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "false")

    def test_array_element_type_full_tree_entries_string(self):
        self._assert_array_element_type_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "\"synthetic_non_object\"")

    def test_array_element_type_full_tree_entries_empty_array(self):
        self._assert_array_element_type_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "[]")

    def test_array_element_type_full_tree_entries_integer_zero(self):
        self._assert_array_element_type_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "0")

    def test_array_element_type_merge_parents_null(self):
        self._assert_array_element_type_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "null")

    def test_array_element_type_merge_parents_true(self):
        self._assert_array_element_type_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "true")

    def test_array_element_type_merge_parents_false(self):
        self._assert_array_element_type_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "false")

    def test_array_element_type_merge_parents_string(self):
        self._assert_array_element_type_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "\"synthetic_non_object\"")

    def test_array_element_type_merge_parents_empty_array(self):
        self._assert_array_element_type_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "[]")

    def test_array_element_type_merge_parents_integer_zero(self):
        self._assert_array_element_type_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "0")

    def test_array_element_type_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
