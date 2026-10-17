"""DEC-1454: parse the actual three-stage GitHub PR merge runner checkout.

Caller-supplied text only, no network, protected annual data, GitHub settings,
workflow dispatch, merging, or trading.
"""
from __future__ import annotations
import re
import unittest
from datetime import datetime

PREFIX = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z "
FETCH = re.compile(PREFIX + r"\[command\]/usr/bin/git .*?\bfetch\b .*?"
                   r" origin \+([0-9a-f]{40}):refs/remotes/pull/([1-9]\d*)/merge$")
CHECKOUT = re.compile(PREFIX +
                      r"\[command\]/usr/bin/git checkout --progress --force "
                      r"refs/remotes/pull/([1-9]\d*)/merge$")
HEAD = re.compile(PREFIX + r"HEAD is now at ([0-9a-f]{7,40}) "
                  r"Merge ([0-9a-f]{40}) into ([0-9a-f]{40})$")
SHA = re.compile(r"[0-9a-f]{40}\Z")


def parse_runner_checkout(raw_log, pr_number, head_sha, base_sha):
    if (type(raw_log) is not str or type(pr_number) is not int or
            pr_number <= 0 or any(
                type(x) is not str or SHA.fullmatch(x) is None
                for x in (head_sha, base_sha))):
        return None, ("RUNNER_LOG_INPUT_UNREVIEWED",)
    candidates = {}
    for label, regex in (("fetch", FETCH), ("checkout", CHECKOUT), ("head", HEAD)):
        candidates[label] = [
            (i, match.groups())
            for i, line in enumerate(raw_log.splitlines())
            if (match := regex.fullmatch(line)) is not None
        ]
    if any(len(v) != 1 for v in candidates.values()):
        return None, ("RUNNER_LOG_STAGE_CARDINALITY_UNREVIEWED",)
    i, (full_sha, fetch_pr) = candidates["fetch"][0]
    j, (checkout_pr,) = candidates["checkout"][0]
    k, (short_sha, msg_head, msg_base) = candidates["head"][0]
    issues = []
    if not i < j < k:
        issues.append("RUNNER_LOG_ORDER_UNREVIEWED")
    # A line-order-only check can accept transplanted stages from logs
    # with impossible or reversed timestamps.
    all_lines = raw_log.splitlines()
    try:
        stamps = [
            datetime.fromisoformat(all_lines[index].split(" ", 1)[0].replace(
                "Z", "+00:00"))
            for index in (i, j, k)
        ]
    except (ValueError, OverflowError, TypeError):
        issues.append("RUNNER_LOG_TIMESTAMP_UNREVIEWED")
    else:
        if not stamps[0] < stamps[1] < stamps[2]:
            issues.append("RUNNER_LOG_TIMESTAMP_ORDER_UNREVIEWED")
    if fetch_pr != str(pr_number) or checkout_pr != str(pr_number):
        issues.append("RUNNER_LOG_PR_REF_MISMATCH")
    if not full_sha.startswith(short_sha):
        issues.append("RUNNER_LOG_CHECKOUT_SHA_MISMATCH")
    if msg_head != head_sha or msg_base != base_sha:
        issues.append("RUNNER_LOG_PARENT_SHA_MISMATCH")
    if issues:
        return None, tuple(sorted(set(issues)))
    return {
        "checkout_fetch_sha": full_sha,
        "checkout_ref": "refs/remotes/pull/" + str(pr_number) + "/merge",
        "checkout_sha_prefix": short_sha,
    }, ()


class ImmutableGitFetchCheckoutHeadLogTrace(unittest.TestCase):
    def setUp(self):
        self.sha = "5857e06c3cff50243d2ad87c31c55e86a636ea50"
        self.head = "7eb566a3448f9fc01ed6a1433714304c19e4568c"
        self.base = "624b002f0de79174b2b9aecb3343f64d5f3e658f"
        self.lines = [
            "2026-10-16T23:10:54.6953610Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +" + self.sha + ":refs/remotes/pull/1664/merge",
            "2026-10-16T23:10:55.7325917Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/1664/merge",
            "2026-10-16T23:10:55.9519792Z HEAD is now at 5857e06 Merge " + self.head + " into " + self.base,
        ]

    def verdict(self):
        return parse_runner_checkout("\n".join(self.lines), 1664,
                                     self.head, self.base)

    def test_observed_checkout_log_extracts_full_sha(self):
        record, issues = self.verdict()
        self.assertEqual(issues, ())
        self.assertEqual(record["checkout_fetch_sha"], self.sha)

    def test_fetch_different_pr_ref_is_rejected(self):
        self.lines[0] = self.lines[0].replace("/1664/merge", "/1665/merge")
        self.assertIn("RUNNER_LOG_PR_REF_MISMATCH", self.verdict()[1])

    def test_checkout_different_pr_ref_is_rejected(self):
        self.lines[1] = self.lines[1].replace("/1664/merge", "/1665/merge")
        self.assertIn("RUNNER_LOG_PR_REF_MISMATCH", self.verdict()[1])

    def test_abbreviated_head_sha_mismatch_is_rejected(self):
        self.lines[2] = self.lines[2].replace("5857e06", "7eb566a")
        self.assertIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH", self.verdict()[1])

    def test_merge_head_parent_mismatch_is_rejected(self):
        self.lines[2] = self.lines[2].replace(self.head, self.base)
        self.assertIn("RUNNER_LOG_PARENT_SHA_MISMATCH", self.verdict()[1])

    def test_merge_base_parent_mismatch_is_rejected(self):
        self.lines[2] = self.lines[2].replace(self.base, self.head)
        self.assertIn("RUNNER_LOG_PARENT_SHA_MISMATCH", self.verdict()[1])

    def test_swapping_fetch_and_checkout_order_is_rejected(self):
        self.lines[0], self.lines[1] = self.lines[1], self.lines[0]
        self.assertIn("RUNNER_LOG_ORDER_UNREVIEWED", self.verdict()[1])

    def test_swapping_checkout_and_head_order_is_rejected(self):
        self.lines[1], self.lines[2] = self.lines[2], self.lines[1]
        self.assertIn("RUNNER_LOG_ORDER_UNREVIEWED", self.verdict()[1])

    def test_duplicate_fetch_stage_is_rejected(self):
        self.lines.append(self.lines[0])
        self.assertIn("RUNNER_LOG_STAGE_CARDINALITY_UNREVIEWED",
                      self.verdict()[1])

    def test_duplicate_checkout_stage_is_rejected(self):
        self.lines.append(self.lines[1])
        self.assertIn("RUNNER_LOG_STAGE_CARDINALITY_UNREVIEWED",
                      self.verdict()[1])

    def test_missing_checkout_stage_is_rejected(self):
        self.lines.pop(1)
        self.assertIn("RUNNER_LOG_STAGE_CARDINALITY_UNREVIEWED",
                      self.verdict()[1])

    def test_malformed_full_fetch_sha_is_rejected(self):
        self.lines[0] = self.lines[0].replace(self.sha, "z"*40)
        self.assertIn("RUNNER_LOG_STAGE_CARDINALITY_UNREVIEWED",
                      self.verdict()[1])

    def test_unrelated_log_line_is_ignored(self):
        self.lines.insert(1, "2026-10-16T23:10:55.1000000Z unrelated output")
        self.assertEqual(self.verdict()[1], ())

    def test_nontext_log_is_not_evidence(self):
        self.assertEqual(
            parse_runner_checkout(None, 1664, self.head, self.base),
            (None, ("RUNNER_LOG_INPUT_UNREVIEWED",)))

    def test_boolean_pr_number_is_not_evidence(self):
        self.assertEqual(
            parse_runner_checkout("\n".join(self.lines),
                                  True, self.head, self.base),
            (None, ("RUNNER_LOG_INPUT_UNREVIEWED",)))

    def test_extracted_sha_never_approves_protected_annual_run(self):
        self.assertEqual(self.verdict()[1], ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict()[1])

    def test_monotone_utc_stage_timestamps_are_accepted(self):
        self.assertEqual(self.verdict()[1], ())

    def test_checkout_earlier_timestamp_than_fetch_is_rejected(self):
        self.lines[1] = self.lines[1].replace(
            "2026-10-16T23:10:55.7325917Z",
            "2026-10-16T23:10:53.7325917Z")
        self.assertIn("RUNNER_LOG_TIMESTAMP_ORDER_UNREVIEWED",
                      self.verdict()[1])

    def test_head_earlier_timestamp_than_checkout_is_rejected(self):
        self.lines[2] = self.lines[2].replace(
            "2026-10-16T23:10:55.9519792Z",
            "2026-10-16T23:10:54.9519792Z")
        self.assertIn("RUNNER_LOG_TIMESTAMP_ORDER_UNREVIEWED",
                      self.verdict()[1])

    def test_equal_checkout_and_head_timestamps_are_not_distinct(self):
        self.lines[2] = self.lines[2].replace(
            "2026-10-16T23:10:55.9519792Z",
            "2026-10-16T23:10:55.7325917Z")
        self.assertIn("RUNNER_LOG_TIMESTAMP_ORDER_UNREVIEWED",
                      self.verdict()[1])

    def test_invalid_calendar_month_does_not_count_as_log_time(self):
        self.lines[0] = self.lines[0].replace("2026-10-16", "2026-99-16")
        self.assertIn("RUNNER_LOG_TIMESTAMP_UNREVIEWED",
                      self.verdict()[1])

    def test_invalid_calendar_day_does_not_count_as_log_time(self):
        self.lines[1] = self.lines[1].replace("2026-10-16", "2026-10-99")
        self.assertIn("RUNNER_LOG_TIMESTAMP_UNREVIEWED",
                      self.verdict()[1])

    def test_increasing_log_times_remain_non_authorizing(self):
        self.assertEqual(self.verdict()[1], ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict()[1])
