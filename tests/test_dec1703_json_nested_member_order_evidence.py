"""DEC-1703: JSON nested member-order permutations preserve review results.

All evidence is synthetic; JSON object member order has no semantic authority.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class ArrayContainedEvidenceMemberOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_nested_member_order_parity(self, category, path, ordering):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(ordering, (
            "original", "reversed", "sorted", "reverse_sorted",
            "rotate_left", "rotate_right"))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        node = copied[category]
        for part in path:
            node = node[part]
        self.assertIs(type(node), dict)
        node["zz_dec1703_alpha"] = 1
        node["zz_dec1703_beta"] = 2
        items = list(node.items())
        self.assertGreaterEqual(len(items), 3)
        if ordering == "reversed":
            items = list(reversed(items))
        elif ordering == "sorted":
            items = sorted(items)
        elif ordering == "reverse_sorted":
            items = sorted(items, reverse=True)
        elif ordering == "rotate_left":
            items = items[1:] + items[:1]
        elif ordering == "rotate_right":
            items = items[-1:] + items[:-1]
        node.clear()
        node.update(items)
        self.assertEqual(list(node.items()), items)
        raw = json.dumps(copied, sort_keys=False, separators=(",", ":"))
        self.assertEqual(json.loads(raw), copied)
        direct = source.review_bundle_envelope(copied)
        parsed = source.review_bundle_json_text(raw)
        self.assertEqual(parsed, direct)
        self.assertNotIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                         parsed["diagnostics"])
        self.assertNotIn("BUNDLE_JSON_UNICODE_UNREVIEWED",
                         parsed["diagnostics"])
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(raw), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertEqual(status, 0 if direct["source_consistency"] else 2)
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"], list(direct["diagnostics"]))
        self.assertEqual(emitted["source_consistency"],
                         direct["source_consistency"])
        self.assertNotIn("zz_dec1703_alpha", out.getvalue())
        self.assertNotIn("zz_dec1703_beta", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for verdict in (direct, parsed, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_member_order_runs_original(self):
        self._assert_nested_member_order_parity(
            "runs", (0,), "original")

    def test_member_order_runs_reversed(self):
        self._assert_nested_member_order_parity(
            "runs", (0,), "reversed")

    def test_member_order_runs_sorted(self):
        self._assert_nested_member_order_parity(
            "runs", (0,), "sorted")

    def test_member_order_runs_reverse_sorted(self):
        self._assert_nested_member_order_parity(
            "runs", (0,), "reverse_sorted")

    def test_member_order_runs_rotate_left(self):
        self._assert_nested_member_order_parity(
            "runs", (0,), "rotate_left")

    def test_member_order_runs_rotate_right(self):
        self._assert_nested_member_order_parity(
            "runs", (0,), "rotate_right")

    def test_member_order_compare_files_original(self):
        self._assert_nested_member_order_parity(
            "compare", ("files", 0), "original")

    def test_member_order_compare_files_reversed(self):
        self._assert_nested_member_order_parity(
            "compare", ("files", 0), "reversed")

    def test_member_order_compare_files_sorted(self):
        self._assert_nested_member_order_parity(
            "compare", ("files", 0), "sorted")

    def test_member_order_compare_files_reverse_sorted(self):
        self._assert_nested_member_order_parity(
            "compare", ("files", 0), "reverse_sorted")

    def test_member_order_compare_files_rotate_left(self):
        self._assert_nested_member_order_parity(
            "compare", ("files", 0), "rotate_left")

    def test_member_order_compare_files_rotate_right(self):
        self._assert_nested_member_order_parity(
            "compare", ("files", 0), "rotate_right")

    def test_member_order_jobs_original(self):
        self._assert_nested_member_order_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "original")

    def test_member_order_jobs_reversed(self):
        self._assert_nested_member_order_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "reversed")

    def test_member_order_jobs_sorted(self):
        self._assert_nested_member_order_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "sorted")

    def test_member_order_jobs_reverse_sorted(self):
        self._assert_nested_member_order_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "reverse_sorted")

    def test_member_order_jobs_rotate_left(self):
        self._assert_nested_member_order_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "rotate_left")

    def test_member_order_jobs_rotate_right(self):
        self._assert_nested_member_order_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "rotate_right")

    def test_member_order_phase3_scenarios_original(self):
        self._assert_nested_member_order_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "original")

    def test_member_order_phase3_scenarios_reversed(self):
        self._assert_nested_member_order_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "reversed")

    def test_member_order_phase3_scenarios_sorted(self):
        self._assert_nested_member_order_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "sorted")

    def test_member_order_phase3_scenarios_reverse_sorted(self):
        self._assert_nested_member_order_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "reverse_sorted")

    def test_member_order_phase3_scenarios_rotate_left(self):
        self._assert_nested_member_order_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "rotate_left")

    def test_member_order_phase3_scenarios_rotate_right(self):
        self._assert_nested_member_order_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "rotate_right")

    def test_member_order_full_tree_entries_original(self):
        self._assert_nested_member_order_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "original")

    def test_member_order_full_tree_entries_reversed(self):
        self._assert_nested_member_order_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "reversed")

    def test_member_order_full_tree_entries_sorted(self):
        self._assert_nested_member_order_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "sorted")

    def test_member_order_full_tree_entries_reverse_sorted(self):
        self._assert_nested_member_order_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "reverse_sorted")

    def test_member_order_full_tree_entries_rotate_left(self):
        self._assert_nested_member_order_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "rotate_left")

    def test_member_order_full_tree_entries_rotate_right(self):
        self._assert_nested_member_order_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "rotate_right")

    def test_member_order_merge_parents_original(self):
        self._assert_nested_member_order_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "original")

    def test_member_order_merge_parents_reversed(self):
        self._assert_nested_member_order_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "reversed")

    def test_member_order_merge_parents_sorted(self):
        self._assert_nested_member_order_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "sorted")

    def test_member_order_merge_parents_reverse_sorted(self):
        self._assert_nested_member_order_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "reverse_sorted")

    def test_member_order_merge_parents_rotate_left(self):
        self._assert_nested_member_order_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "rotate_left")

    def test_member_order_merge_parents_rotate_right(self):
        self._assert_nested_member_order_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "rotate_right")

    def test_member_order_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
