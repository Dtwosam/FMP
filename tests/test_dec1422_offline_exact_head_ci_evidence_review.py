"""DEC-1422: offline, synthetic exact-head CI evidence review.

No networking, GitHub Actions dispatch, annual execution, privileged data,
repository mutation, or trading path. Green source CI is not authorization.
"""
from __future__ import annotations

import re
import unittest

REQUIRED = ("phase3-acceptance", "tests")


def review_exact_head_ci(head_sha: object, runs: object) -> tuple[str, ...]:
    """Conservative review of caller-supplied GitHub REST-shaped snapshots."""
    if not isinstance(head_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", head_sha):
        return ("HEAD_SHA_UNREVIEWED",)
    if type(runs) is not list or not all(type(x) is dict for x in runs):
        return ("RUN_SNAPSHOT_UNREVIEWED",)
    reasons = []
    for name in REQUIRED:
        matched = [run for run in runs if run.get("name") == name]
        if len(matched) != 1:
            reasons.append(name + "_RUN_CARDINALITY_UNREVIEWED")
            continue
        run = matched[0]
        if run.get("head_sha") != head_sha:
            reasons.append(name + "_HEAD_SHA_MISMATCH")
        if run.get("event") != "pull_request":
            reasons.append(name + "_EVENT_UNREVIEWED")
        if run.get("status") != "completed":
            reasons.append(name + "_NOT_COMPLETED")
        if run.get("conclusion") != "success":
            reasons.append(name + "_NOT_SUCCESS")
        if type(run.get("id")) is not int or run["id"] <= 0:
            reasons.append(name + "_RUN_ID_UNREVIEWED")
    return tuple(sorted(set(reasons)))


class ExactHeadGreenIsNotAnnualAuthorization(unittest.TestCase):
    SHA = "a" * 40

    def setUp(self):
        self.runs = [
            {"name": n, "head_sha": self.SHA, "event": "pull_request",
             "status": "completed", "conclusion": "success", "id": 100 + i}
            for i, n in enumerate(REQUIRED)
        ]

    def test_two_exact_head_successful_runs_pass_source_evidence(self):
        self.assertEqual(review_exact_head_ci(self.SHA, self.runs), ())

    def test_unrelated_skipped_phase1_is_not_required(self):
        self.runs.append({"name": "phase1-network-smoke", "status": "completed",
                          "conclusion": "skipped", "id": 999})
        self.assertEqual(review_exact_head_ci(self.SHA, self.runs), ())

    def test_missing_phase3_is_not_full_green(self):
        self.runs.pop(0)
        self.assertIn("phase3-acceptance_RUN_CARDINALITY_UNREVIEWED",
                      review_exact_head_ci(self.SHA, self.runs))

    def test_missing_historical_is_not_full_green(self):
        self.runs.pop(1)
        self.assertIn("tests_RUN_CARDINALITY_UNREVIEWED",
                      review_exact_head_ci(self.SHA, self.runs))

    def test_duplicate_successful_workflow_runs_need_review(self):
        self.runs.append(dict(self.runs[1]))
        self.assertIn("tests_RUN_CARDINALITY_UNREVIEWED",
                      review_exact_head_ci(self.SHA, self.runs))

    def test_mismatched_historical_head_is_not_green(self):
        self.runs[1]["head_sha"] = "b" * 40
        self.assertIn("tests_HEAD_SHA_MISMATCH",
                      review_exact_head_ci(self.SHA, self.runs))

    def test_mismatched_phase3_head_is_not_green(self):
        self.runs[0]["head_sha"] = "b" * 40
        self.assertIn("phase3-acceptance_HEAD_SHA_MISMATCH",
                      review_exact_head_ci(self.SHA, self.runs))

    def test_non_pull_request_event_is_not_green(self):
        self.runs[1]["event"] = "workflow_dispatch"
        self.assertIn("tests_EVENT_UNREVIEWED",
                      review_exact_head_ci(self.SHA, self.runs))

    def test_pending_historical_workflow_is_not_green(self):
        self.runs[1]["status"] = "in_progress"
        self.runs[1]["conclusion"] = None
        self.assertIn("tests_NOT_COMPLETED", review_exact_head_ci(self.SHA, self.runs))
        self.assertIn("tests_NOT_SUCCESS", review_exact_head_ci(self.SHA, self.runs))

    def test_failed_historical_workflow_is_not_green(self):
        self.runs[1]["conclusion"] = "failure"
        self.assertIn("tests_NOT_SUCCESS", review_exact_head_ci(self.SHA, self.runs))

    def test_canceled_phase3_workflow_is_not_green(self):
        self.runs[0]["conclusion"] = "cancelled"
        self.assertIn("phase3-acceptance_NOT_SUCCESS",
                      review_exact_head_ci(self.SHA, self.runs))

    def test_skipped_required_workflow_is_not_green(self):
        self.runs[0]["conclusion"] = "skipped"
        self.assertIn("phase3-acceptance_NOT_SUCCESS",
                      review_exact_head_ci(self.SHA, self.runs))

    def test_unknown_run_id_is_not_green(self):
        self.runs[0]["id"] = False
        self.assertIn("phase3-acceptance_RUN_ID_UNREVIEWED",
                      review_exact_head_ci(self.SHA, self.runs))

    def test_missing_run_id_is_not_green(self):
        self.runs[1].pop("id")
        self.assertIn("tests_RUN_ID_UNREVIEWED",
                      review_exact_head_ci(self.SHA, self.runs))

    def test_invalid_commit_hex_is_not_green(self):
        self.assertEqual(review_exact_head_ci("unreviewed", self.runs),
                         ("HEAD_SHA_UNREVIEWED",))

    def test_untrusted_snapshot_container_is_not_green(self):
        self.assertEqual(review_exact_head_ci(self.SHA, {}),
                         ("RUN_SNAPSHOT_UNREVIEWED",))

    def test_non_mapping_run_item_is_not_green(self):
        self.assertEqual(review_exact_head_ci(self.SHA, ["not a run"]),
                         ("RUN_SNAPSHOT_UNREVIEWED",))

    def test_a_green_ci_verdict_has_no_protected_authorization_output(self):
        verdict = review_exact_head_ci(self.SHA, self.runs)
        self.assertEqual(verdict, ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", verdict)
        self.assertNotIn("ORIGINAL_OS_NO_WRITE_PROVEN", verdict)


if __name__ == "__main__":
    unittest.main()
