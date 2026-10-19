"""DEC-1711: decoded duplicate JSON object keys cannot reach nested review.

The strict pairs hook sees Unicode-decoded aliases, unlike normal json.loads.
"""
import copy
import io
import json
import unittest
from unittest import mock

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class DecodedDuplicateMemberPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_duplicate_member_skips_nested(self, category, path, alias_kind):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(alias_kind, (
            "literal", "escaped_first_letter", "escaped_underscore",
            "escaped_final_letter"))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        node = copied[category]
        for part in path:
            node = node[part]
        self.assertIs(type(node), dict)
        key = "zz_dec1711_duplicate"
        self.assertNotIn(key, node)
        node[key] = "first"
        inner = key
        if alias_kind == "escaped_first_letter":
            inner = chr(92) + "u007a" + inner[1:]
        elif alias_kind == "escaped_underscore":
            inner = inner.replace("_", chr(92) + "u005f", 1)
        elif alias_kind == "escaped_final_letter":
            inner = inner[:-1] + chr(92) + "u0065"
        alias = '"' + inner + '"'
        self.assertEqual(json.loads(alias), key)
        encoded = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        original = json.dumps(key) + ":" + json.dumps("first")
        self.assertEqual(encoded.count(original), 1)
        injected = original + "," + alias + ":" + json.dumps("second")
        duplicate = encoded.replace(original, injected, 1)
        # Standard json.loads is permissive; the strict decoder is not.
        self.assertIsNotNone(json.loads(duplicate))
        with self.assertRaises(ValueError):
            json.loads(duplicate, object_pairs_hook=source._no_duplicate_keys)
        with mock.patch.object(
            source.composite, "review_stacked_draft_evidence",
            side_effect=AssertionError("DUPLICATE_REACHED_NESTED_REVIEW"),
        ) as nested:
            parsed = source.review_bundle_json_text(duplicate)
            out = io.StringIO()
            status = cli.run_stdin_review(io.StringIO(duplicate), out)
            nested.assert_not_called()
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(status, 2)
        self.assertEqual(parsed["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("zz_dec1711_duplicate", out.getvalue())
        self.assertNotIn("DUPLICATE_REACHED_NESTED_REVIEW", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for result in (parsed, emitted):
            self.assertFalse(result["source_consistency"])
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_duplicate_preflight_runs_literal(self):
        self._assert_duplicate_member_skips_nested(
            "runs", (0,), "literal")

    def test_duplicate_preflight_runs_escaped_first_letter(self):
        self._assert_duplicate_member_skips_nested(
            "runs", (0,), "escaped_first_letter")

    def test_duplicate_preflight_runs_escaped_underscore(self):
        self._assert_duplicate_member_skips_nested(
            "runs", (0,), "escaped_underscore")

    def test_duplicate_preflight_runs_escaped_final_letter(self):
        self._assert_duplicate_member_skips_nested(
            "runs", (0,), "escaped_final_letter")

    def test_duplicate_preflight_compare_files_literal(self):
        self._assert_duplicate_member_skips_nested(
            "compare", ("files", 0), "literal")

    def test_duplicate_preflight_compare_files_escaped_first_letter(self):
        self._assert_duplicate_member_skips_nested(
            "compare", ("files", 0), "escaped_first_letter")

    def test_duplicate_preflight_compare_files_escaped_underscore(self):
        self._assert_duplicate_member_skips_nested(
            "compare", ("files", 0), "escaped_underscore")

    def test_duplicate_preflight_compare_files_escaped_final_letter(self):
        self._assert_duplicate_member_skips_nested(
            "compare", ("files", 0), "escaped_final_letter")

    def test_duplicate_preflight_jobs_literal(self):
        self._assert_duplicate_member_skips_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "literal")

    def test_duplicate_preflight_jobs_escaped_first_letter(self):
        self._assert_duplicate_member_skips_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "escaped_first_letter")

    def test_duplicate_preflight_jobs_escaped_underscore(self):
        self._assert_duplicate_member_skips_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "escaped_underscore")

    def test_duplicate_preflight_jobs_escaped_final_letter(self):
        self._assert_duplicate_member_skips_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "escaped_final_letter")

    def test_duplicate_preflight_phase3_scenarios_literal(self):
        self._assert_duplicate_member_skips_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "literal")

    def test_duplicate_preflight_phase3_scenarios_escaped_first_letter(self):
        self._assert_duplicate_member_skips_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "escaped_first_letter")

    def test_duplicate_preflight_phase3_scenarios_escaped_underscore(self):
        self._assert_duplicate_member_skips_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "escaped_underscore")

    def test_duplicate_preflight_phase3_scenarios_escaped_final_letter(self):
        self._assert_duplicate_member_skips_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "escaped_final_letter")

    def test_duplicate_preflight_full_tree_entries_literal(self):
        self._assert_duplicate_member_skips_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "literal")

    def test_duplicate_preflight_full_tree_entries_escaped_first_letter(self):
        self._assert_duplicate_member_skips_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "escaped_first_letter")

    def test_duplicate_preflight_full_tree_entries_escaped_underscore(self):
        self._assert_duplicate_member_skips_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "escaped_underscore")

    def test_duplicate_preflight_full_tree_entries_escaped_final_letter(self):
        self._assert_duplicate_member_skips_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "escaped_final_letter")

    def test_duplicate_preflight_merge_parents_literal(self):
        self._assert_duplicate_member_skips_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "literal")

    def test_duplicate_preflight_merge_parents_escaped_first_letter(self):
        self._assert_duplicate_member_skips_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "escaped_first_letter")

    def test_duplicate_preflight_merge_parents_escaped_underscore(self):
        self._assert_duplicate_member_skips_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "escaped_underscore")

    def test_duplicate_preflight_merge_parents_escaped_final_letter(self):
        self._assert_duplicate_member_skips_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "escaped_final_letter")

    def test_duplicate_preflight_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
