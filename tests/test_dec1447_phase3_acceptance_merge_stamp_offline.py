"""DEC-1447: synthetic Phase 3 acceptance evidence merge-SHA label audit.

No downloading artifacts, networking, protected original/annual workflow,
repo security mutation, merge, brokerage or trading.
"""
from __future__ import annotations
import re
import unittest

HEX = re.compile(r"[0-9a-f]{40}\Z")
SCENARIOS = (
    "ambiguity", "daily-halt-reset", "long-cost", "short-target",
    "simultaneous-risk",
)


def review_phase3_merge_evidence(run, merge_sha, index, upload):
    """Inspect independently read runner-log fields; never confer approval."""
    if any(type(x) is not dict for x in (run, index, upload)):
        return ("PHASE3_EVIDENCE_INPUT_UNREVIEWED",)
    issues = []
    head_sha = run.get("head_sha")
    if any(type(s) is not str or HEX.fullmatch(s) is None
           for s in (head_sha, merge_sha)):
        return ("PHASE3_COMMIT_SHA_UNREVIEWED",)
    if head_sha == merge_sha:
        issues.append("PHASE3_MERGE_HEAD_IDENTITY_UNREVIEWED")
    if (run.get("name") != "phase3-acceptance" or
            run.get("event") != "pull_request" or
            run.get("status") != "completed" or
            run.get("conclusion") != "success"):
        issues.append("PHASE3_RUN_NOT_REVIEWED_SUCCESS")
    if type(run.get("id")) is not int or run["id"] <= 0:
        issues.append("PHASE3_RUN_ID_UNREVIEWED")
    if type(run.get("run_attempt")) is not int or run["run_attempt"] != 1:
        issues.append("PHASE3_ATTEMPT_UNREVIEWED")
    if index.get("code_commit") != merge_sha:
        issues.append("PHASE3_INDEX_COMMIT_NOT_TESTED_MERGE")
    if index.get("protocol") != "fmp-phase3-acceptance-fixture-v1":
        issues.append("PHASE3_INDEX_PROTOCOL_UNREVIEWED")
    if index.get("fixture_id") != "phase3-merged-main-acceptance-v1":
        issues.append("PHASE3_INDEX_FIXTURE_UNREVIEWED")
    if type(index.get("scenario_count")) is not int or (
            index["scenario_count"] != len(SCENARIOS)):
        issues.append("PHASE3_INDEX_SCENARIO_COUNT_UNREVIEWED")
    scenarios = index.get("scenarios")
    if type(scenarios) is not list or not all(
            type(s) is dict for s in scenarios):
        issues.append("PHASE3_SCENARIOS_UNREVIEWED")
    else:
        names = [s.get("name") for s in scenarios]
        if tuple(names) != SCENARIOS:
            issues.append("PHASE3_SCENARIO_NAMES_UNREVIEWED")
        if any(s.get("bytes_equal") is not True for s in scenarios):
            issues.append("PHASE3_SCENARIO_DETERMINISM_UNREVIEWED")
    expected_artifact_name = "phase3-backtester-acceptance-" + merge_sha
    if upload.get("name") != expected_artifact_name:
        issues.append("PHASE3_UPLOAD_MERGE_SHA_NAME_MISMATCH")
    if type(upload.get("id")) is not int or upload["id"] <= 0:
        issues.append("PHASE3_UPLOAD_ID_UNREVIEWED")
    if upload.get("run_id") != run.get("id"):
        issues.append("PHASE3_UPLOAD_RUN_ASSOCIATION_MISMATCH")
    if upload.get("finalized") is not True:
        issues.append("PHASE3_UPLOAD_NOT_FINALIZED")
    return tuple(sorted(set(issues)))


class Phase3EvidenceIsLabeledByTestedMergeNotBranchHead(unittest.TestCase):
    def setUp(self):
        self.merge = "5857e06c3cff50243d2ad87c31c55e86a636ea50"
        self.head = "7eb566a3448f9fc01ed6a1433714304c19e4568c"
        self.run = {
            "id": 38980012679, "name": "phase3-acceptance",
            "event": "pull_request", "status": "completed",
            "conclusion": "success", "run_attempt": 1,
            "head_sha": self.head,
        }
        self.index = {
            "protocol": "fmp-phase3-acceptance-fixture-v1",
            "fixture_id": "phase3-merged-main-acceptance-v1",
            "code_commit": self.merge, "scenario_count": 5,
            "scenarios": [{"name": name, "bytes_equal": True}
                          for name in SCENARIOS],
        }
        self.upload = {
            "name": "phase3-backtester-acceptance-" + self.merge,
            "id": 12080194915, "run_id": self.run["id"],
            "finalized": True,
        }

    def verdict(self):
        return review_phase3_merge_evidence(
            self.run, self.merge, self.index, self.upload)

    def test_observed_1664_merge_labeled_fixture_is_consistent(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotEqual(self.head, self.merge)

    def test_index_incorrectly_stamped_with_branch_head_fails(self):
        self.index["code_commit"] = self.head
        self.assertIn("PHASE3_INDEX_COMMIT_NOT_TESTED_MERGE",
                      self.verdict())

    def test_artifact_incorrectly_named_with_branch_head_fails(self):
        self.upload["name"] = "phase3-backtester-acceptance-" + self.head
        self.assertIn("PHASE3_UPLOAD_MERGE_SHA_NAME_MISMATCH",
                      self.verdict())

    def test_mismatched_uploaded_run_id_fails(self):
        self.upload["run_id"] = 123
        self.assertIn("PHASE3_UPLOAD_RUN_ASSOCIATION_MISMATCH",
                      self.verdict())

    def test_unfinalized_upload_fails(self):
        self.upload["finalized"] = False
        self.assertIn("PHASE3_UPLOAD_NOT_FINALIZED", self.verdict())

    def test_absent_artifact_identifier_fails(self):
        self.upload.pop("id")
        self.assertIn("PHASE3_UPLOAD_ID_UNREVIEWED", self.verdict())

    def test_bool_artifact_identifier_fails(self):
        self.upload["id"] = True
        self.assertIn("PHASE3_UPLOAD_ID_UNREVIEWED", self.verdict())

    def test_unreviewed_scenario_count_fails(self):
        self.index["scenario_count"] = 4
        self.assertIn("PHASE3_INDEX_SCENARIO_COUNT_UNREVIEWED",
                      self.verdict())

    def test_skipped_scenario_name_fails(self):
        self.index["scenarios"].pop()
        self.assertIn("PHASE3_SCENARIO_NAMES_UNREVIEWED", self.verdict())

    def test_nondeterministic_scenario_fails(self):
        self.index["scenarios"][0]["bytes_equal"] = False
        self.assertIn("PHASE3_SCENARIO_DETERMINISM_UNREVIEWED",
                      self.verdict())

    def test_wrong_protocol_fails(self):
        self.index["protocol"] = "unreviewed"
        self.assertIn("PHASE3_INDEX_PROTOCOL_UNREVIEWED", self.verdict())

    def test_wrong_fixture_label_fails(self):
        self.index["fixture_id"] = "unreviewed"
        self.assertIn("PHASE3_INDEX_FIXTURE_UNREVIEWED", self.verdict())

    def test_wrong_head_association_is_detectable(self):
        self.run["head_sha"] = self.merge
        self.assertIn("PHASE3_MERGE_HEAD_IDENTITY_UNREVIEWED",
                      self.verdict())

    def test_failed_run_cannot_pass_uploaded_evidence_review(self):
        self.run["conclusion"] = "failure"
        self.assertIn("PHASE3_RUN_NOT_REVIEWED_SUCCESS",
                      self.verdict())

    def test_rerun_attempt_requires_separate_review(self):
        self.run["run_attempt"] = 2
        self.assertIn("PHASE3_ATTEMPT_UNREVIEWED", self.verdict())

    def test_missing_fixture_input_fails_closed(self):
        self.assertEqual(
            review_phase3_merge_evidence(self.run, self.merge, [], self.upload),
            ("PHASE3_EVIDENCE_INPUT_UNREVIEWED",))

    def test_matching_merge_stamp_never_authorizes_annual_dispatch(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
