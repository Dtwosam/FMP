"""DEC-1705: JSON-valid array cardinality changes reach nested review.

No remote artifacts, protected source changes, annual execution or trading.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class EvidenceArrayCardinalityReviewParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_array_cardinality_parity(self, category, path, mutation):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(mutation, (
            "empty", "single_empty_object", "two_empty_objects",
            "duplicate_first", "single_null"))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        array = copied[category]
        for segment in path:
            array = array[segment]
        self.assertIs(type(array), list)
        self.assertGreater(len(array), 0)
        original_first = copy.deepcopy(array[0])
        if mutation == "empty":
            array[:] = []
        elif mutation == "single_empty_object":
            array[:] = [{}]
        elif mutation == "two_empty_objects":
            array[:] = [{}, {}]
        elif mutation == "duplicate_first":
            array[:] = [copy.deepcopy(original_first),
                        copy.deepcopy(original_first)]
        elif mutation == "single_null":
            array[:] = [None]
        raw = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        self.assertEqual(json.loads(raw), copied)
        direct = source.review_bundle_envelope(copied)
        parsed = source.review_bundle_json_text(raw)
        self.assertEqual(parsed, direct)
        self.assertNotIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                         parsed["diagnostics"])
        self.assertNotIn("BUNDLE_JSON_UNICODE_UNREVIEWED",
                         parsed["diagnostics"])
        output = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(raw), output)
        emitted = json.loads(output.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(rc, 0 if direct["source_consistency"] else 2)
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["source_consistency"],
                         direct["source_consistency"])
        self.assertEqual(emitted["diagnostics"], list(direct["diagnostics"]))
        self.assertNotIn("tests/sample.py", output.getvalue())
        self.assertNotIn("docs/sample.md", output.getvalue())
        for verdict in (direct, parsed, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_array_cardinality_runs_empty(self):
        self._assert_array_cardinality_parity(
            "runs", (), "empty")

    def test_array_cardinality_runs_single_empty_object(self):
        self._assert_array_cardinality_parity(
            "runs", (), "single_empty_object")

    def test_array_cardinality_runs_two_empty_objects(self):
        self._assert_array_cardinality_parity(
            "runs", (), "two_empty_objects")

    def test_array_cardinality_runs_duplicate_first(self):
        self._assert_array_cardinality_parity(
            "runs", (), "duplicate_first")

    def test_array_cardinality_runs_single_null(self):
        self._assert_array_cardinality_parity(
            "runs", (), "single_null")

    def test_array_cardinality_jobs_empty(self):
        self._assert_array_cardinality_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "empty")

    def test_array_cardinality_jobs_single_empty_object(self):
        self._assert_array_cardinality_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "single_empty_object")

    def test_array_cardinality_jobs_two_empty_objects(self):
        self._assert_array_cardinality_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "two_empty_objects")

    def test_array_cardinality_jobs_duplicate_first(self):
        self._assert_array_cardinality_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "duplicate_first")

    def test_array_cardinality_jobs_single_null(self):
        self._assert_array_cardinality_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "single_null")

    def test_array_cardinality_compare_files_empty(self):
        self._assert_array_cardinality_parity(
            "compare", ("files",), "empty")

    def test_array_cardinality_compare_files_single_empty_object(self):
        self._assert_array_cardinality_parity(
            "compare", ("files",), "single_empty_object")

    def test_array_cardinality_compare_files_two_empty_objects(self):
        self._assert_array_cardinality_parity(
            "compare", ("files",), "two_empty_objects")

    def test_array_cardinality_compare_files_duplicate_first(self):
        self._assert_array_cardinality_parity(
            "compare", ("files",), "duplicate_first")

    def test_array_cardinality_compare_files_single_null(self):
        self._assert_array_cardinality_parity(
            "compare", ("files",), "single_null")

    def test_array_cardinality_phase3_scenarios_empty(self):
        self._assert_array_cardinality_parity(
            "phase3_evidence_snapshot", ("index", "scenarios"), "empty")

    def test_array_cardinality_phase3_scenarios_single_empty_object(self):
        self._assert_array_cardinality_parity(
            "phase3_evidence_snapshot", ("index", "scenarios"), "single_empty_object")

    def test_array_cardinality_phase3_scenarios_two_empty_objects(self):
        self._assert_array_cardinality_parity(
            "phase3_evidence_snapshot", ("index", "scenarios"), "two_empty_objects")

    def test_array_cardinality_phase3_scenarios_duplicate_first(self):
        self._assert_array_cardinality_parity(
            "phase3_evidence_snapshot", ("index", "scenarios"), "duplicate_first")

    def test_array_cardinality_phase3_scenarios_single_null(self):
        self._assert_array_cardinality_parity(
            "phase3_evidence_snapshot", ("index", "scenarios"), "single_null")

    def test_array_cardinality_full_tree_entries_empty(self):
        self._assert_array_cardinality_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "empty")

    def test_array_cardinality_full_tree_entries_single_empty_object(self):
        self._assert_array_cardinality_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "single_empty_object")

    def test_array_cardinality_full_tree_entries_two_empty_objects(self):
        self._assert_array_cardinality_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "two_empty_objects")

    def test_array_cardinality_full_tree_entries_duplicate_first(self):
        self._assert_array_cardinality_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "duplicate_first")

    def test_array_cardinality_full_tree_entries_single_null(self):
        self._assert_array_cardinality_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "single_null")

    def test_array_cardinality_merge_parents_empty(self):
        self._assert_array_cardinality_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "empty")

    def test_array_cardinality_merge_parents_single_empty_object(self):
        self._assert_array_cardinality_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "single_empty_object")

    def test_array_cardinality_merge_parents_two_empty_objects(self):
        self._assert_array_cardinality_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "two_empty_objects")

    def test_array_cardinality_merge_parents_duplicate_first(self):
        self._assert_array_cardinality_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "duplicate_first")

    def test_array_cardinality_merge_parents_single_null(self):
        self._assert_array_cardinality_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "single_null")

    def test_array_cardinality_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
