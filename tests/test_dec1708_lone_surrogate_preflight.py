"""DEC-1708: lone decoded UTF-16 surrogate escapes are pre-review failures.

The raw JSON text is ASCII; unpaired surrogates appear only after decoding.
"""
import copy
import io
import json
import unittest
from unittest import mock

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class UnpairedSurrogatePreflightNeverCallsNestedReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_lone_surrogate_is_rejected_before_nested(self, category,
                                                        path, target_kind,
                                                        hex_code):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(target_kind, ("key", "value"))
        self.assertIn(hex_code, ("D800", "DBFF", "DC00", "DFFF"))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        node = copied[category]
        for segment in path:
            node = node[segment]
        self.assertIs(type(node), dict)
        lone = chr(int(hex_code, 16))
        if target_kind == "key":
            node[lone] = "DEC1708_SECRET_MARKER"
        else:
            node["zz_dec1708_lone"] = lone
        raw = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        self.assertTrue(raw.isascii())
        decoded = json.loads(raw)
        parsed_node = decoded[category]
        for segment in path:
            parsed_node = parsed_node[segment]
        self.assertIs(type(parsed_node), dict)
        if target_kind == "key":
            self.assertIn(lone, parsed_node)
        else:
            self.assertEqual(parsed_node["zz_dec1708_lone"], lone)
        with mock.patch.object(
            source.composite, "review_stacked_draft_evidence",
            side_effect=AssertionError("NESTED_REVIEW_FORBIDDEN"),
        ) as nested:
            result = source.review_bundle_json_text(raw)
            out = io.StringIO()
            rc = cli.run_stdin_review(io.StringIO(raw), out)
            nested.assert_not_called()
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(rc, 2)
        self.assertEqual(result["diagnostics"],
                         ("BUNDLE_JSON_UNICODE_UNREVIEWED",))
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_UNICODE_UNREVIEWED"])
        self.assertNotIn("DEC1708_SECRET_MARKER", out.getvalue())
        self.assertNotIn("zz_dec1708_lone", out.getvalue())
        self.assertNotIn("NESTED_REVIEW_FORBIDDEN", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for verdict in (result, emitted):
            self.assertFalse(verdict["source_consistency"])
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_surrogate_preflight_runs_key_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "runs", (0,), "key", "D800")

    def test_surrogate_preflight_runs_key_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "runs", (0,), "key", "DBFF")

    def test_surrogate_preflight_runs_key_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "runs", (0,), "key", "DC00")

    def test_surrogate_preflight_runs_key_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "runs", (0,), "key", "DFFF")

    def test_surrogate_preflight_runs_value_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "runs", (0,), "value", "D800")

    def test_surrogate_preflight_runs_value_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "runs", (0,), "value", "DBFF")

    def test_surrogate_preflight_runs_value_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "runs", (0,), "value", "DC00")

    def test_surrogate_preflight_runs_value_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "runs", (0,), "value", "DFFF")

    def test_surrogate_preflight_compare_files_key_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "compare", ("files", 0), "key", "D800")

    def test_surrogate_preflight_compare_files_key_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "compare", ("files", 0), "key", "DBFF")

    def test_surrogate_preflight_compare_files_key_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "compare", ("files", 0), "key", "DC00")

    def test_surrogate_preflight_compare_files_key_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "compare", ("files", 0), "key", "DFFF")

    def test_surrogate_preflight_compare_files_value_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "compare", ("files", 0), "value", "D800")

    def test_surrogate_preflight_compare_files_value_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "compare", ("files", 0), "value", "DBFF")

    def test_surrogate_preflight_compare_files_value_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "compare", ("files", 0), "value", "DC00")

    def test_surrogate_preflight_compare_files_value_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "compare", ("files", 0), "value", "DFFF")

    def test_surrogate_preflight_jobs_key_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "key", "D800")

    def test_surrogate_preflight_jobs_key_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "key", "DBFF")

    def test_surrogate_preflight_jobs_key_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "key", "DC00")

    def test_surrogate_preflight_jobs_key_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "key", "DFFF")

    def test_surrogate_preflight_jobs_value_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "value", "D800")

    def test_surrogate_preflight_jobs_value_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "value", "DBFF")

    def test_surrogate_preflight_jobs_value_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "value", "DC00")

    def test_surrogate_preflight_jobs_value_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "value", "DFFF")

    def test_surrogate_preflight_phase3_scenarios_key_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "key", "D800")

    def test_surrogate_preflight_phase3_scenarios_key_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "key", "DBFF")

    def test_surrogate_preflight_phase3_scenarios_key_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "key", "DC00")

    def test_surrogate_preflight_phase3_scenarios_key_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "key", "DFFF")

    def test_surrogate_preflight_phase3_scenarios_value_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "value", "D800")

    def test_surrogate_preflight_phase3_scenarios_value_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "value", "DBFF")

    def test_surrogate_preflight_phase3_scenarios_value_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "value", "DC00")

    def test_surrogate_preflight_phase3_scenarios_value_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "value", "DFFF")

    def test_surrogate_preflight_full_tree_entries_key_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "key", "D800")

    def test_surrogate_preflight_full_tree_entries_key_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "key", "DBFF")

    def test_surrogate_preflight_full_tree_entries_key_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "key", "DC00")

    def test_surrogate_preflight_full_tree_entries_key_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "key", "DFFF")

    def test_surrogate_preflight_full_tree_entries_value_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "value", "D800")

    def test_surrogate_preflight_full_tree_entries_value_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "value", "DBFF")

    def test_surrogate_preflight_full_tree_entries_value_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "value", "DC00")

    def test_surrogate_preflight_full_tree_entries_value_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "value", "DFFF")

    def test_surrogate_preflight_merge_parents_key_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "key", "D800")

    def test_surrogate_preflight_merge_parents_key_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "key", "DBFF")

    def test_surrogate_preflight_merge_parents_key_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "key", "DC00")

    def test_surrogate_preflight_merge_parents_key_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "key", "DFFF")

    def test_surrogate_preflight_merge_parents_value_high_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "value", "D800")

    def test_surrogate_preflight_merge_parents_value_high_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "value", "DBFF")

    def test_surrogate_preflight_merge_parents_value_low_min(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "value", "DC00")

    def test_surrogate_preflight_merge_parents_value_low_max(self):
        self._assert_lone_surrogate_is_rejected_before_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "value", "DFFF")

    def test_surrogate_preflight_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
