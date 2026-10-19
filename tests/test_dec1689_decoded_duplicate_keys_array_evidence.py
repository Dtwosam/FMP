"""DEC-1689: duplicate decoded JSON member keys nested inside evidence arrays.

Offline synthetic ingress tests only; never authorize protected actions.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class ArrayEvidenceDecodedDuplicateMemberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_duplicate_decoded_key_fails(self, category, path, alias):
        self.assertIn(category, source.REQUIRED)
        key = "synthetic_shadow"
        self.assertEqual(json.loads(alias), key)
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        cursor = copied[category]
        for part in path:
            cursor = cursor[part]
        self.assertIs(type(cursor), dict)
        self.assertNotIn(key, cursor)
        cursor[key] = "first"
        encoded = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        original = json.dumps(key) + ":" + json.dumps("first")
        self.assertEqual(encoded.count(original), 1)
        injected = original + "," + alias + ":" + json.dumps("second")
        duplicate = encoded.replace(original, injected, 1)
        # Generic JSON silently loses one member; the reviewed parser must not.
        self.assertEqual(json.loads(duplicate)[category] is not None, True)
        with self.assertRaises(ValueError):
            json.loads(duplicate, object_pairs_hook=source._no_duplicate_keys)
        parsed = source.review_bundle_json_text(duplicate)
        out = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(duplicate), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(rc, 2)
        self.assertEqual(parsed["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("synthetic_shadow", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for result in (parsed, emitted):
            self.assertFalse(result["source_consistency"])
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_duplicate_member_runs_literal(self):
        self._assert_duplicate_decoded_key_fails(
            "runs", (0,), "\"synthetic_shadow\"")

    def test_duplicate_member_runs_unicode_head(self):
        self._assert_duplicate_decoded_key_fails(
            "runs", (0,), "\"\\u0073ynthetic_shadow\"")

    def test_duplicate_member_runs_unicode_separator(self):
        self._assert_duplicate_decoded_key_fails(
            "runs", (0,), "\"synthetic\\u005fshadow\"")

    def test_duplicate_member_runs_unicode_end(self):
        self._assert_duplicate_decoded_key_fails(
            "runs", (0,), "\"synthetic_shado\\u0077\"")

    def test_duplicate_member_runs_uppercase_unicode(self):
        self._assert_duplicate_decoded_key_fails(
            "runs", (0,), "\"synthetic\\u005Fshadow\"")

    def test_duplicate_member_comparison_files_literal(self):
        self._assert_duplicate_decoded_key_fails(
            "compare", ("files", 0), "\"synthetic_shadow\"")

    def test_duplicate_member_comparison_files_unicode_head(self):
        self._assert_duplicate_decoded_key_fails(
            "compare", ("files", 0), "\"\\u0073ynthetic_shadow\"")

    def test_duplicate_member_comparison_files_unicode_separator(self):
        self._assert_duplicate_decoded_key_fails(
            "compare", ("files", 0), "\"synthetic\\u005fshadow\"")

    def test_duplicate_member_comparison_files_unicode_end(self):
        self._assert_duplicate_decoded_key_fails(
            "compare", ("files", 0), "\"synthetic_shado\\u0077\"")

    def test_duplicate_member_comparison_files_uppercase_unicode(self):
        self._assert_duplicate_decoded_key_fails(
            "compare", ("files", 0), "\"synthetic\\u005Fshadow\"")

    def test_duplicate_member_jobs_by_run_literal(self):
        self._assert_duplicate_decoded_key_fails(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"synthetic_shadow\"")

    def test_duplicate_member_jobs_by_run_unicode_head(self):
        self._assert_duplicate_decoded_key_fails(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"\\u0073ynthetic_shadow\"")

    def test_duplicate_member_jobs_by_run_unicode_separator(self):
        self._assert_duplicate_decoded_key_fails(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"synthetic\\u005fshadow\"")

    def test_duplicate_member_jobs_by_run_unicode_end(self):
        self._assert_duplicate_decoded_key_fails(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"synthetic_shado\\u0077\"")

    def test_duplicate_member_jobs_by_run_uppercase_unicode(self):
        self._assert_duplicate_decoded_key_fails(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"synthetic\\u005Fshadow\"")

    def test_duplicate_member_phase3_scenarios_literal(self):
        self._assert_duplicate_decoded_key_fails(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"synthetic_shadow\"")

    def test_duplicate_member_phase3_scenarios_unicode_head(self):
        self._assert_duplicate_decoded_key_fails(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"\\u0073ynthetic_shadow\"")

    def test_duplicate_member_phase3_scenarios_unicode_separator(self):
        self._assert_duplicate_decoded_key_fails(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"synthetic\\u005fshadow\"")

    def test_duplicate_member_phase3_scenarios_unicode_end(self):
        self._assert_duplicate_decoded_key_fails(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"synthetic_shado\\u0077\"")

    def test_duplicate_member_phase3_scenarios_uppercase_unicode(self):
        self._assert_duplicate_decoded_key_fails(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"synthetic\\u005Fshadow\"")

    def test_duplicate_member_full_tree_entries_literal(self):
        self._assert_duplicate_decoded_key_fails(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"synthetic_shadow\"")

    def test_duplicate_member_full_tree_entries_unicode_head(self):
        self._assert_duplicate_decoded_key_fails(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"\\u0073ynthetic_shadow\"")

    def test_duplicate_member_full_tree_entries_unicode_separator(self):
        self._assert_duplicate_decoded_key_fails(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"synthetic\\u005fshadow\"")

    def test_duplicate_member_full_tree_entries_unicode_end(self):
        self._assert_duplicate_decoded_key_fails(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"synthetic_shado\\u0077\"")

    def test_duplicate_member_full_tree_entries_uppercase_unicode(self):
        self._assert_duplicate_decoded_key_fails(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"synthetic\\u005Fshadow\"")

    def test_duplicate_member_merge_parents_literal(self):
        self._assert_duplicate_decoded_key_fails(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"synthetic_shadow\"")

    def test_duplicate_member_merge_parents_unicode_head(self):
        self._assert_duplicate_decoded_key_fails(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"\\u0073ynthetic_shadow\"")

    def test_duplicate_member_merge_parents_unicode_separator(self):
        self._assert_duplicate_decoded_key_fails(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"synthetic\\u005fshadow\"")

    def test_duplicate_member_merge_parents_unicode_end(self):
        self._assert_duplicate_decoded_key_fails(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"synthetic_shado\\u0077\"")

    def test_duplicate_member_merge_parents_uppercase_unicode(self):
        self._assert_duplicate_decoded_key_fails(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"synthetic\\u005Fshadow\"")

    def test_duplicate_member_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
