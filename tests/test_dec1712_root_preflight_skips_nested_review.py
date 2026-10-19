"""DEC-1712: invalid root evidence inventory is refused before nested review.

All evidence is synthetic. Tests cannot establish protected annual authority.
"""
import copy
import io
import json
import unittest
from unittest import mock

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class RootReviewPreflightBypassesNestedReviewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_root_preflight_fails_without_nested(self, category, path,
                                                    fault):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(fault, (
            "missing_schema", "forged_approval", "wrong_schema",
            "null_pr", "null_runs", "extra_root_member"))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        node = copied[category]
        for part in path:
            node = node[part]
        self.assertIs(type(node), dict)
        node["zz_dec1712_probe"] = True
        if fault == "missing_schema":
            copied.pop("schema")
            expected = "BUNDLE_KEY_INVENTORY_UNREVIEWED"
        elif fault == "forged_approval":
            copied["can_authorize_annual_run"] = True
            expected = "BUNDLE_KEY_INVENTORY_UNREVIEWED"
        elif fault == "extra_root_member":
            copied["zz_dec1712_root"] = True
            expected = "BUNDLE_KEY_INVENTORY_UNREVIEWED"
        elif fault == "wrong_schema":
            copied["schema"] = "unreviewed-v2"
            expected = "BUNDLE_SCHEMA_UNREVIEWED"
        elif fault == "null_pr":
            copied["pr"] = None
            expected = "BUNDLE_CATEGORY_TYPE_UNREVIEWED"
        else:
            copied["runs"] = None
            expected = "BUNDLE_CATEGORY_TYPE_UNREVIEWED"
        raw = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        self.assertEqual(json.loads(raw), copied)
        with mock.patch.object(
            source.composite, "review_stacked_draft_evidence",
            side_effect=AssertionError("EARLY_GATE_BYPASS"),
        ) as nested:
            direct = source.review_bundle_envelope(copied)
            parsed = source.review_bundle_json_text(raw)
            output = io.StringIO()
            rc = cli.run_stdin_review(io.StringIO(raw), output)
            nested.assert_not_called()
        emitted = json.loads(output.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(direct, parsed)
        self.assertEqual(direct["diagnostics"], (expected,))
        self.assertEqual(rc, 2)
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"], [expected])
        self.assertNotIn("zz_dec1712_probe", output.getvalue())
        self.assertNotIn("EARLY_GATE_BYPASS", output.getvalue())
        self.assertNotIn("tests/sample.py", output.getvalue())
        self.assertNotIn("docs/sample.md", output.getvalue())
        for result in (direct, parsed, emitted):
            self.assertFalse(result["source_consistency"])
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_root_preflight_runs_missing_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "runs", (0,), "missing_schema")

    def test_root_preflight_runs_forged_approval(self):
        self._assert_root_preflight_fails_without_nested(
            "runs", (0,), "forged_approval")

    def test_root_preflight_runs_wrong_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "runs", (0,), "wrong_schema")

    def test_root_preflight_runs_null_pr(self):
        self._assert_root_preflight_fails_without_nested(
            "runs", (0,), "null_pr")

    def test_root_preflight_runs_null_runs(self):
        self._assert_root_preflight_fails_without_nested(
            "runs", (0,), "null_runs")

    def test_root_preflight_runs_extra_root_member(self):
        self._assert_root_preflight_fails_without_nested(
            "runs", (0,), "extra_root_member")

    def test_root_preflight_compare_files_missing_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "compare", ("files", 0), "missing_schema")

    def test_root_preflight_compare_files_forged_approval(self):
        self._assert_root_preflight_fails_without_nested(
            "compare", ("files", 0), "forged_approval")

    def test_root_preflight_compare_files_wrong_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "compare", ("files", 0), "wrong_schema")

    def test_root_preflight_compare_files_null_pr(self):
        self._assert_root_preflight_fails_without_nested(
            "compare", ("files", 0), "null_pr")

    def test_root_preflight_compare_files_null_runs(self):
        self._assert_root_preflight_fails_without_nested(
            "compare", ("files", 0), "null_runs")

    def test_root_preflight_compare_files_extra_root_member(self):
        self._assert_root_preflight_fails_without_nested(
            "compare", ("files", 0), "extra_root_member")

    def test_root_preflight_jobs_missing_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "missing_schema")

    def test_root_preflight_jobs_forged_approval(self):
        self._assert_root_preflight_fails_without_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "forged_approval")

    def test_root_preflight_jobs_wrong_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "wrong_schema")

    def test_root_preflight_jobs_null_pr(self):
        self._assert_root_preflight_fails_without_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "null_pr")

    def test_root_preflight_jobs_null_runs(self):
        self._assert_root_preflight_fails_without_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "null_runs")

    def test_root_preflight_jobs_extra_root_member(self):
        self._assert_root_preflight_fails_without_nested(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "extra_root_member")

    def test_root_preflight_phase3_scenarios_missing_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "missing_schema")

    def test_root_preflight_phase3_scenarios_forged_approval(self):
        self._assert_root_preflight_fails_without_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "forged_approval")

    def test_root_preflight_phase3_scenarios_wrong_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "wrong_schema")

    def test_root_preflight_phase3_scenarios_null_pr(self):
        self._assert_root_preflight_fails_without_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "null_pr")

    def test_root_preflight_phase3_scenarios_null_runs(self):
        self._assert_root_preflight_fails_without_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "null_runs")

    def test_root_preflight_phase3_scenarios_extra_root_member(self):
        self._assert_root_preflight_fails_without_nested(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "extra_root_member")

    def test_root_preflight_tree_entries_missing_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "missing_schema")

    def test_root_preflight_tree_entries_forged_approval(self):
        self._assert_root_preflight_fails_without_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "forged_approval")

    def test_root_preflight_tree_entries_wrong_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "wrong_schema")

    def test_root_preflight_tree_entries_null_pr(self):
        self._assert_root_preflight_fails_without_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "null_pr")

    def test_root_preflight_tree_entries_null_runs(self):
        self._assert_root_preflight_fails_without_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "null_runs")

    def test_root_preflight_tree_entries_extra_root_member(self):
        self._assert_root_preflight_fails_without_nested(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "extra_root_member")

    def test_root_preflight_merge_parents_missing_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "missing_schema")

    def test_root_preflight_merge_parents_forged_approval(self):
        self._assert_root_preflight_fails_without_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "forged_approval")

    def test_root_preflight_merge_parents_wrong_schema(self):
        self._assert_root_preflight_fails_without_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "wrong_schema")

    def test_root_preflight_merge_parents_null_pr(self):
        self._assert_root_preflight_fails_without_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "null_pr")

    def test_root_preflight_merge_parents_null_runs(self):
        self._assert_root_preflight_fails_without_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "null_runs")

    def test_root_preflight_merge_parents_extra_root_member(self):
        self._assert_root_preflight_fails_without_nested(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "extra_root_member")

    def test_root_preflight_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
