"""DEC-1709: paired supplementary Unicode escapes reach nested review.

Valid JSON astral code points must not be mistaken for lone surrogates.
"""
import copy
import io
import json
import unittest
from unittest import mock

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class ValidAstralUnicodeReachesNestedReviewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_astral_unicode_passes_preflight(self, category, path,
                                               hex_code):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(hex_code, ("1F600", "1D11E", "1F9EA", "10000"))
        clean = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        node = copied[category]
        for segment in path:
            node = node[segment]
        self.assertIs(type(node), dict)
        char = chr(int(hex_code, 16))
        self.assertEqual(len(char), 1)
        node["zz_dec1709_valid_astral"] = char
        raw = json.dumps(copied, ensure_ascii=True,
                         separators=(",", ":"), sort_keys=True)
        self.assertTrue(raw.isascii())
        self.assertEqual(json.loads(raw), copied)
        direct = source.review_bundle_envelope(copied)
        with mock.patch.object(
            source.composite, "review_stacked_draft_evidence",
            wraps=source.composite.review_stacked_draft_evidence,
        ) as nested:
            parsed = source.review_bundle_json_text(raw)
            out = io.StringIO()
            status = cli.run_stdin_review(io.StringIO(raw), out)
            self.assertEqual(nested.call_count, 2)
        emitted = json.loads(out.getvalue())
        self.assertEqual(clean, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(direct, parsed)
        self.assertNotIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                         parsed["diagnostics"])
        self.assertNotIn("BUNDLE_JSON_UNICODE_UNREVIEWED",
                         parsed["diagnostics"])
        self.assertEqual(status, 0 if direct["source_consistency"] else 2)
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["source_consistency"],
                         direct["source_consistency"])
        self.assertEqual(emitted["diagnostics"], list(direct["diagnostics"]))
        self.assertNotIn("zz_dec1709_valid_astral", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for result in (direct, parsed, emitted):
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_valid_astral_runs_grinning_face(self):
        self._assert_astral_unicode_passes_preflight(
            "runs", (0,), "1F600")

    def test_valid_astral_runs_musical_symbol(self):
        self._assert_astral_unicode_passes_preflight(
            "runs", (0,), "1D11E")

    def test_valid_astral_runs_test_tube(self):
        self._assert_astral_unicode_passes_preflight(
            "runs", (0,), "1F9EA")

    def test_valid_astral_runs_plane_one_start(self):
        self._assert_astral_unicode_passes_preflight(
            "runs", (0,), "10000")

    def test_valid_astral_compare_files_grinning_face(self):
        self._assert_astral_unicode_passes_preflight(
            "compare", ("files", 0), "1F600")

    def test_valid_astral_compare_files_musical_symbol(self):
        self._assert_astral_unicode_passes_preflight(
            "compare", ("files", 0), "1D11E")

    def test_valid_astral_compare_files_test_tube(self):
        self._assert_astral_unicode_passes_preflight(
            "compare", ("files", 0), "1F9EA")

    def test_valid_astral_compare_files_plane_one_start(self):
        self._assert_astral_unicode_passes_preflight(
            "compare", ("files", 0), "10000")

    def test_valid_astral_jobs_grinning_face(self):
        self._assert_astral_unicode_passes_preflight(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "1F600")

    def test_valid_astral_jobs_musical_symbol(self):
        self._assert_astral_unicode_passes_preflight(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "1D11E")

    def test_valid_astral_jobs_test_tube(self):
        self._assert_astral_unicode_passes_preflight(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "1F9EA")

    def test_valid_astral_jobs_plane_one_start(self):
        self._assert_astral_unicode_passes_preflight(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "10000")

    def test_valid_astral_phase3_scenarios_grinning_face(self):
        self._assert_astral_unicode_passes_preflight(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "1F600")

    def test_valid_astral_phase3_scenarios_musical_symbol(self):
        self._assert_astral_unicode_passes_preflight(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "1D11E")

    def test_valid_astral_phase3_scenarios_test_tube(self):
        self._assert_astral_unicode_passes_preflight(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "1F9EA")

    def test_valid_astral_phase3_scenarios_plane_one_start(self):
        self._assert_astral_unicode_passes_preflight(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "10000")

    def test_valid_astral_full_tree_entries_grinning_face(self):
        self._assert_astral_unicode_passes_preflight(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "1F600")

    def test_valid_astral_full_tree_entries_musical_symbol(self):
        self._assert_astral_unicode_passes_preflight(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "1D11E")

    def test_valid_astral_full_tree_entries_test_tube(self):
        self._assert_astral_unicode_passes_preflight(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "1F9EA")

    def test_valid_astral_full_tree_entries_plane_one_start(self):
        self._assert_astral_unicode_passes_preflight(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "10000")

    def test_valid_astral_merge_parents_grinning_face(self):
        self._assert_astral_unicode_passes_preflight(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "1F600")

    def test_valid_astral_merge_parents_musical_symbol(self):
        self._assert_astral_unicode_passes_preflight(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "1D11E")

    def test_valid_astral_merge_parents_test_tube(self):
        self._assert_astral_unicode_passes_preflight(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "1F9EA")

    def test_valid_astral_merge_parents_plane_one_start(self):
        self._assert_astral_unicode_passes_preflight(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "10000")

    def test_valid_astral_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
