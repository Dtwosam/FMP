"""DEC-1714: valid astral Unicode *object keys* reach source-only review.

Confirms JSON decoding retains paired surrogate equivalence in member names.
"""
import copy
import io
import json
import unittest
from unittest import mock

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class ValidSupplementaryUnicodeKeyPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_valid_astral_member_key_parity(self, category, path, scalar):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(scalar, ("1F600", "1D11E", "1F9EA", "10000"))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        target = copied[category]
        for part in path:
            target = target[part]
        self.assertIs(type(target), dict)
        key = chr(int(scalar, 16))
        self.assertNotIn(key, target)
        target[key] = "synthetic_value"
        raw = json.dumps(copied, ensure_ascii=True,
                         sort_keys=True, separators=(",", ":"))
        self.assertTrue(raw.isascii())
        decoded = json.loads(raw)
        node = decoded[category]
        for part in path:
            node = node[part]
        self.assertIn(key, node)
        self.assertEqual(decoded, copied)
        direct = source.review_bundle_envelope(copied)
        with mock.patch.object(
            source.composite, "review_stacked_draft_evidence",
            wraps=source.composite.review_stacked_draft_evidence,
        ) as nested:
            parsed = source.review_bundle_json_text(raw)
            out = io.StringIO()
            rc = cli.run_stdin_review(io.StringIO(raw), out)
            self.assertEqual(nested.call_count, 2)
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(parsed, direct)
        self.assertNotIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                         parsed["diagnostics"])
        self.assertNotIn("BUNDLE_JSON_UNICODE_UNREVIEWED",
                         parsed["diagnostics"])
        self.assertEqual(rc, 0 if direct["source_consistency"] else 2)
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["source_consistency"],
                         direct["source_consistency"])
        self.assertEqual(emitted["diagnostics"], list(direct["diagnostics"]))
        self.assertNotIn("synthetic_value", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for verdict in (direct, parsed, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_valid_astral_key_runs_grinning_face(self):
        self._assert_valid_astral_member_key_parity(
            "runs", (0,), "1F600")

    def test_valid_astral_key_runs_musical_symbol(self):
        self._assert_valid_astral_member_key_parity(
            "runs", (0,), "1D11E")

    def test_valid_astral_key_runs_test_tube(self):
        self._assert_valid_astral_member_key_parity(
            "runs", (0,), "1F9EA")

    def test_valid_astral_key_runs_plane_one_start(self):
        self._assert_valid_astral_member_key_parity(
            "runs", (0,), "10000")

    def test_valid_astral_key_compare_files_grinning_face(self):
        self._assert_valid_astral_member_key_parity(
            "compare", ("files", 0), "1F600")

    def test_valid_astral_key_compare_files_musical_symbol(self):
        self._assert_valid_astral_member_key_parity(
            "compare", ("files", 0), "1D11E")

    def test_valid_astral_key_compare_files_test_tube(self):
        self._assert_valid_astral_member_key_parity(
            "compare", ("files", 0), "1F9EA")

    def test_valid_astral_key_compare_files_plane_one_start(self):
        self._assert_valid_astral_member_key_parity(
            "compare", ("files", 0), "10000")

    def test_valid_astral_key_jobs_grinning_face(self):
        self._assert_valid_astral_member_key_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "1F600")

    def test_valid_astral_key_jobs_musical_symbol(self):
        self._assert_valid_astral_member_key_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "1D11E")

    def test_valid_astral_key_jobs_test_tube(self):
        self._assert_valid_astral_member_key_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "1F9EA")

    def test_valid_astral_key_jobs_plane_one_start(self):
        self._assert_valid_astral_member_key_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "10000")

    def test_valid_astral_key_phase3_scenarios_grinning_face(self):
        self._assert_valid_astral_member_key_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "1F600")

    def test_valid_astral_key_phase3_scenarios_musical_symbol(self):
        self._assert_valid_astral_member_key_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "1D11E")

    def test_valid_astral_key_phase3_scenarios_test_tube(self):
        self._assert_valid_astral_member_key_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "1F9EA")

    def test_valid_astral_key_phase3_scenarios_plane_one_start(self):
        self._assert_valid_astral_member_key_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "10000")

    def test_valid_astral_key_full_tree_entries_grinning_face(self):
        self._assert_valid_astral_member_key_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "1F600")

    def test_valid_astral_key_full_tree_entries_musical_symbol(self):
        self._assert_valid_astral_member_key_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "1D11E")

    def test_valid_astral_key_full_tree_entries_test_tube(self):
        self._assert_valid_astral_member_key_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "1F9EA")

    def test_valid_astral_key_full_tree_entries_plane_one_start(self):
        self._assert_valid_astral_member_key_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "10000")

    def test_valid_astral_key_merge_parents_grinning_face(self):
        self._assert_valid_astral_member_key_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "1F600")

    def test_valid_astral_key_merge_parents_musical_symbol(self):
        self._assert_valid_astral_member_key_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "1D11E")

    def test_valid_astral_key_merge_parents_test_tube(self):
        self._assert_valid_astral_member_key_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "1F9EA")

    def test_valid_astral_key_merge_parents_plane_one_start(self):
        self._assert_valid_astral_member_key_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "10000")

    def test_valid_astral_key_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
