"""DEC-1477: two real unprotected PR CI golden samples cannot be mixed.

Source-only offline fixture and provenance diagnostics, not authenticated
runner OS proof, protected annual execution or trading.
"""
from __future__ import annotations
import unittest

import test_dec1470_observed_real_phase3_job_log_golden as first
import test_dec1471_observed_dual_ci_checkout_merge_golden as first_dual
import test_dec1476_observed_recovered_1698_dual_ci_golden as recovered
import test_dec1454_runner_merge_checkout_trace_parser_offline as checkout
import test_dec1462_phase3_raw_log_index_upload_offline as parser
import test_dec1466_phase3_checkout_acceptance_chronology_offline as chronology


class TwoDistinctActualPRAcceptanceFixturesCannotCrossContaminate(unittest.TestCase):
    def setUp(self):
        self.a = list(first.OBSERVED_RAW_LINES)
        self.b = list(recovered.PHASE3_LOG)

    def parse_a(self):
        return parser.parse_phase3_log_evidence(
            "\n".join(self.a), first.OBSERVED_RUN_ID, first.OBSERVED_MERGE)

    def parse_b(self):
        return parser.parse_phase3_log_evidence(
            "\n".join(self.b), recovered.PHASE3_RUN, recovered.MERGE)

    def test_both_independently_observed_samples_parse(self):
        self.assertEqual(self.parse_a()[2], ())
        self.assertEqual(self.parse_b()[2], ())

    def test_distinct_source_commits_and_tested_merge_ids(self):
        self.assertNotEqual(first.OBSERVED_HEAD, recovered.HEAD)
        self.assertNotEqual(first.OBSERVED_MERGE, recovered.MERGE)
        self.assertNotEqual(first_dual.COMMON_TREE, recovered.SOURCE_TREE)

    def test_two_real_samples_have_same_reviewed_five_scenario_schema(self):
        idx_a = self.parse_a()[0]
        idx_b = self.parse_b()[0]
        self.assertEqual(idx_a["protocol"], idx_b["protocol"])
        self.assertEqual(idx_a["fixture_id"], idx_b["fixture_id"])
        self.assertEqual(tuple(v["name"] for v in idx_a["scenarios"]),
                         tuple(v["name"] for v in idx_b["scenarios"]))
        self.assertNotEqual(idx_a["code_commit"], idx_b["code_commit"])

    def test_run_and_artifact_ids_are_not_interchangeable(self):
        a = self.parse_a()[1]
        b = self.parse_b()[1]
        self.assertNotEqual(a["run_id"], b["run_id"])
        self.assertNotEqual(a["id"], b["id"])
        self.assertNotEqual(a["name"], b["name"])

    def test_first_complete_phase3_log_cannot_replace_second(self):
        self.b = list(self.a)
        diagnostics = self.parse_b()[2]
        self.assertIn("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED", diagnostics)
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH", diagnostics)

    def test_second_complete_phase3_log_cannot_replace_first(self):
        self.a = list(self.b)
        diagnostics = self.parse_a()[2]
        self.assertIn("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED", diagnostics)
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH", diagnostics)

    def test_first_index_inserted_into_second_log_fails_merge_sha(self):
        self.b[3] = self.a[3]
        self.assertIn("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED",
                      self.parse_b()[2])

    def test_first_artifact_name_inserted_into_second_fails(self):
        self.b[4] = self.a[4]
        self.assertIn("PHASE3_RAW_UPLOAD_MERGE_NAME_MISMATCH",
                      self.parse_b()[2])

    def test_first_finalization_line_inserted_into_second_fails(self):
        self.b[5] = self.a[5]
        diagnostics = self.parse_b()[2]
        self.assertIn("PHASE3_RAW_UPLOAD_MERGE_NAME_MISMATCH", diagnostics)
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH", diagnostics)

    def test_first_successful_upload_line_inserted_into_second_fails(self):
        self.b[6] = self.a[6]
        diagnostics = self.parse_b()[2]
        self.assertIn("PHASE3_RAW_UPLOAD_MERGE_NAME_MISMATCH", diagnostics)
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH", diagnostics)

    def test_first_artifact_url_inserted_into_second_fails(self):
        self.b[7] = self.a[7]
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH",
                      self.parse_b()[2])

    def test_first_checkout_trace_cannot_be_used_under_second_pr(self):
        _, problems = checkout.parse_runner_checkout(
            "\n".join(self.a), recovered.PR, recovered.HEAD, recovered.BASE)
        self.assertIn("RUNNER_LOG_PR_REF_MISMATCH", problems)
        self.assertIn("RUNNER_LOG_PARENT_SHA_MISMATCH", problems)

    def test_mixed_phase3_index_and_checkout_do_not_pass_temporal_review(self):
        self.b[3] = self.a[3]
        issues = chronology.review_phase3_checkout_then_acceptance(
            "\n".join(self.b), recovered.PR, recovered.HEAD, recovered.BASE,
            recovered.PHASE3_RUN, recovered.MERGE)
        self.assertIn("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED", issues)

    def test_untampered_recovered_phase3_checkout_and_index_still_pass(self):
        self.assertEqual(
            chronology.review_phase3_checkout_then_acceptance(
                "\n".join(self.b), recovered.PR, recovered.HEAD,
                recovered.BASE, recovered.PHASE3_RUN, recovered.MERGE),
            ())

    def test_two_real_logs_still_cannot_authorize_protected_annual(self):
        self.assertEqual(self.parse_a()[2], ())
        self.assertEqual(self.parse_b()[2], ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED",
                         self.parse_a()[2] + self.parse_b()[2])
