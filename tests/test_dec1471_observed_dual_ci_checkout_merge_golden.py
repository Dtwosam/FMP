"""DEC-1471: actual unprotected dual-CI fetched-merge source golden fixture.

Only static source records from GitHub Actions run logs, not artifact bytes,
protected originals, annual dispatch, broker operations, or live GitHub calls.
"""
from __future__ import annotations

import unittest

import test_dec1454_runner_merge_checkout_trace_parser_offline as parse
import test_dec1450_dual_suite_merge_checkout_offline as review
import test_dec1422_offline_exact_head_ci_evidence_review as workflows

PR_NUMBER = 1674
HEAD = "3033bec6416e1aeeb0fb7c41f6376d785b0ab425"
BASE = "5c05f06874efed6c561103d89f443fff6be7d0a4"
MERGE = "7630c183c7aca3e72a01b405b342c73db228c845"
COMMON_TREE = "a122a136d6f5eb110349fd2fb02abf44ce12a37f"
HISTORICAL_RUN_ID = 39026055632
PHASE3_RUN_ID = 39026055591
HISTORICAL_JOB_ID = 117377149221
PHASE3_JOB_ID = 117377148833
OBSERVED_HISTORICAL_CHECKOUT_LINES = ["2026-10-17T10:44:42.9549313Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +7630c183c7aca3e72a01b405b342c73db228c845:refs/remotes/pull/1674/merge","2026-10-17T10:44:44.3027940Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/1674/merge","2026-10-17T10:44:44.4755423Z HEAD is now at 7630c18 Merge 3033bec6416e1aeeb0fb7c41f6376d785b0ab425 into 5c05f06874efed6c561103d89f443fff6be7d0a4"]
OBSERVED_PHASE3_CHECKOUT_LINES = ["2026-10-17T10:44:42.4802303Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +7630c183c7aca3e72a01b405b342c73db228c845:refs/remotes/pull/1674/merge","2026-10-17T10:44:43.6358903Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/1674/merge","2026-10-17T10:44:43.8544428Z HEAD is now at 7630c18 Merge 3033bec6416e1aeeb0fb7c41f6376d785b0ab425 into 5c05f06874efed6c561103d89f443fff6be7d0a4"]


class ActualDualWorkflowRunnerCheckoutsShareOneSourceTree(unittest.TestCase):
    def setUp(self):
        self.pr = {"number": PR_NUMBER, "head_sha": HEAD,
                   "base_sha": BASE}
        self.runs = [
            {
                "id": number, "name": name, "workflow_id": workflows.WORKFLOWS[name][0],
                "path": workflows.WORKFLOWS[name][1],
                "head_sha": HEAD, "run_attempt": 1, "event": "pull_request",
                "status": "completed", "conclusion": "success",
            }
            for name, number in (("tests", HISTORICAL_RUN_ID),
                                 ("phase3-acceptance", PHASE3_RUN_ID))
        ]
        self.merge_ref = {
            "ref": "refs/pull/1674/merge",
            "object": {"type": "commit", "sha": MERGE},
        }
        self.merge_commit = {
            "sha": MERGE, "parents": [{"sha": BASE}, {"sha": HEAD}],
            "tree": {"sha": COMMON_TREE},
        }
        self.head_commit = {"sha": HEAD, "tree": {"sha": COMMON_TREE}}
        self.logs = {
            HISTORICAL_RUN_ID: list(OBSERVED_HISTORICAL_CHECKOUT_LINES),
            PHASE3_RUN_ID: list(OBSERVED_PHASE3_CHECKOUT_LINES),
        }

    def extract(self):
        records, reasons = {}, []
        for run_id, lines in self.logs.items():
            evidence, diagnostics = parse.parse_runner_checkout(
                "\n".join(lines), PR_NUMBER, HEAD, BASE)
            reasons.extend(diagnostics)
            if evidence is not None:
                records[run_id] = {"run_id": run_id, **evidence}
        return records, tuple(sorted(set(reasons)))

    def verdict(self):
        checkouts, issues = self.extract()
        if issues:
            return issues
        return review.review_dual_suite_merge_checkouts(
            self.pr, self.runs, checkouts, self.merge_ref,
            self.merge_commit, self.head_commit)

    def test_actual_both_ci_runners_fetched_identical_full_sha(self):
        records, issues = self.extract()
        self.assertEqual(issues, ())
        self.assertEqual(records[HISTORICAL_RUN_ID]["checkout_fetch_sha"], MERGE)
        self.assertEqual(records[PHASE3_RUN_ID]["checkout_fetch_sha"], MERGE)
        self.assertEqual(self.verdict(), ())

    def test_actual_merge_and_head_commit_trees_are_identical(self):
        self.assertEqual(self.merge_commit["tree"]["sha"], COMMON_TREE)
        self.assertEqual(self.head_commit["tree"]["sha"], COMMON_TREE)
        self.assertNotEqual(MERGE, HEAD)
        self.assertEqual(self.verdict(), ())

    def test_changed_historical_log_short_checkout_sha_fails(self):
        self.logs[HISTORICAL_RUN_ID][2] = self.logs[HISTORICAL_RUN_ID][2].replace(
            "7630c18", "3033bec")
        self.assertIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH", self.verdict())

    def test_changed_phase3_fetched_commit_sha_fails(self):
        self.logs[PHASE3_RUN_ID][0] = self.logs[PHASE3_RUN_ID][0].replace(
            MERGE, HEAD)
        self.assertIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH", self.verdict())

    def test_different_source_tree_for_merge_fails(self):
        self.merge_commit["tree"]["sha"] = "f"*40
        self.assertIn("tests_MERGE_AND_HEAD_FILE_TREE_MISMATCH",
                      self.verdict())

    def test_wrong_second_merge_parent_fails(self):
        self.merge_commit["parents"][1]["sha"] = BASE
        self.assertIn("tests_MERGE_COMMIT_PARENT_PAIR_UNREVIEWED",
                      self.verdict())

    def test_wrong_phase3_workflow_identity_fails(self):
        self.runs[1]["workflow_id"] = 1
        self.assertIn("phase3-acceptance_WORKFLOW_IDENTITY_UNREVIEWED",
                      self.verdict())

    def test_stale_phase3_workflow_attempt_fails(self):
        self.runs[1]["run_attempt"] = 2
        self.assertIn("phase3-acceptance_WORKFLOW_IDENTITY_UNREVIEWED",
                      self.verdict())

    def test_missing_historical_checkout_trace_fails(self):
        self.logs[HISTORICAL_RUN_ID] = []
        self.assertIn("RUNNER_LOG_STAGE_CARDINALITY_UNREVIEWED",
                      self.verdict())

    def test_real_ci_merge_tree_identity_cannot_authorize_annual(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
