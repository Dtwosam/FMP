"""DEC-1701: finite numeric literal length boundary inside evidence arrays.

No protected evidence I/O; only offline synthetic review and stdin parity.
"""
import copy
import io
import json
import math
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class NestedJsonFloatLiteralLengthBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_float_token_length(self, category, path, negative, over):
        self.assertIn(category, source.REQUIRED)
        self.assertIs(type(negative), bool)
        self.assertIs(type(over), bool)
        prefix = "-1." if negative else "1."
        allowed = source.MAX_JSON_FLOAT_LITERAL_CHARS
        token = prefix + ("0" * (allowed + int(over) - len(prefix)))
        self.assertEqual(len(token), allowed + int(over))
        value = json.loads(token)
        self.assertIs(type(value), float)
        self.assertTrue(math.isfinite(value))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        cursor = copied[category]
        for part in path:
            cursor = cursor[part]
        self.assertIs(type(cursor), dict)
        cursor["zz_dec1701_float"] = "DEC1701_MARKER"
        raw = json.dumps(copied, separators=(",", ":"), sort_keys=True)
        marker = '"zz_dec1701_float":"DEC1701_MARKER"'
        self.assertEqual(raw.count(marker), 1)
        changed = raw.replace(marker, '"zz_dec1701_float":' + token, 1)
        parsed = source.review_bundle_json_text(changed)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(changed), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        if over:
            self.assertEqual(status, 2)
            self.assertEqual(parsed["diagnostics"],
                             ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
            self.assertEqual(emitted["diagnostics"],
                             ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        else:
            cursor["zz_dec1701_float"] = value
            direct = source.review_bundle_envelope(copied)
            self.assertEqual(parsed, direct)
            self.assertNotIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                             parsed["diagnostics"])
            self.assertEqual(status, 0 if direct["source_consistency"] else 2)
            self.assertEqual(emitted["source_consistency"],
                             direct["source_consistency"])
            self.assertEqual(emitted["diagnostics"], list(direct["diagnostics"]))
        self.assertNotIn("DEC1701_MARKER", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for verdict in (parsed, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_float_length_runs_positive_at_limit(self):
        self._assert_float_token_length(
            "runs", (0,), False, False)

    def test_float_length_runs_positive_over_limit(self):
        self._assert_float_token_length(
            "runs", (0,), False, True)

    def test_float_length_runs_negative_at_limit(self):
        self._assert_float_token_length(
            "runs", (0,), True, False)

    def test_float_length_runs_negative_over_limit(self):
        self._assert_float_token_length(
            "runs", (0,), True, True)

    def test_float_length_compare_files_positive_at_limit(self):
        self._assert_float_token_length(
            "compare", ("files", 0), False, False)

    def test_float_length_compare_files_positive_over_limit(self):
        self._assert_float_token_length(
            "compare", ("files", 0), False, True)

    def test_float_length_compare_files_negative_at_limit(self):
        self._assert_float_token_length(
            "compare", ("files", 0), True, False)

    def test_float_length_compare_files_negative_over_limit(self):
        self._assert_float_token_length(
            "compare", ("files", 0), True, True)

    def test_float_length_jobs_positive_at_limit(self):
        self._assert_float_token_length(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), False, False)

    def test_float_length_jobs_positive_over_limit(self):
        self._assert_float_token_length(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), False, True)

    def test_float_length_jobs_negative_at_limit(self):
        self._assert_float_token_length(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), True, False)

    def test_float_length_jobs_negative_over_limit(self):
        self._assert_float_token_length(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), True, True)

    def test_float_length_phase3_scenarios_positive_at_limit(self):
        self._assert_float_token_length(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), False, False)

    def test_float_length_phase3_scenarios_positive_over_limit(self):
        self._assert_float_token_length(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), False, True)

    def test_float_length_phase3_scenarios_negative_at_limit(self):
        self._assert_float_token_length(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), True, False)

    def test_float_length_phase3_scenarios_negative_over_limit(self):
        self._assert_float_token_length(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), True, True)

    def test_float_length_full_tree_entries_positive_at_limit(self):
        self._assert_float_token_length(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), False, False)

    def test_float_length_full_tree_entries_positive_over_limit(self):
        self._assert_float_token_length(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), False, True)

    def test_float_length_full_tree_entries_negative_at_limit(self):
        self._assert_float_token_length(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), True, False)

    def test_float_length_full_tree_entries_negative_over_limit(self):
        self._assert_float_token_length(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), True, True)

    def test_float_length_merge_parents_positive_at_limit(self):
        self._assert_float_token_length(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), False, False)

    def test_float_length_merge_parents_positive_over_limit(self):
        self._assert_float_token_length(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), False, True)

    def test_float_length_merge_parents_negative_at_limit(self):
        self._assert_float_token_length(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), True, False)

    def test_float_length_merge_parents_negative_over_limit(self):
        self._assert_float_token_length(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), True, True)

    def test_float_length_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
