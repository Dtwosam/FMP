"""DEC-1454: parse the actual three-stage GitHub PR merge runner checkout.

Caller-supplied text only, no network, protected annual data, GitHub settings,
workflow dispatch, merging, or trading.
"""
from __future__ import annotations
import re
import unittest
from test_dec1481_exact_utc_nanosecond_source_time import reviewed_utc_nanoseconds

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
    # Do not accept a log containing the expected three-stage trace AND
    # an additional checkout-changing Git action not recognized above.
    # Restrict to actual actions/checkout runner command records: shell
    # scripts echoed inside logs are not independent git execution evidence.
    extra_mutations = []
    for line in raw_log.splitlines():
        if re.match(PREFIX, line) is None:
            continue
        if "[command]/usr/bin/git " in line:
            command = line.split("[command]/usr/bin/git ", 1)[1]
            mutating = re.search(
                # Detect command words, not substrings of paths such as
                # refs/remotes/pull/N/merge or branch "cherry-pick".
                r"(?:^|\s)(fetch|checkout|switch|reset|restore|clean|apply|"
                r"am|cherry-pick|merge|rebase|pull|read-tree|worktree|"
                r"update-index)(?=\s|$)",
                command)
            if mutating and not (
                    FETCH.fullmatch(line) or CHECKOUT.fullmatch(line)):
                extra_mutations.append(line)
        elif "HEAD is now at " in line and HEAD.fullmatch(line) is None:
            extra_mutations.append(line)
    if extra_mutations:
        return None, ("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",)
    i, (full_sha, fetch_pr) = candidates["fetch"][0]
    j, (checkout_pr,) = candidates["checkout"][0]
    k, (short_sha, msg_head, msg_base) = candidates["head"][0]
    issues = []
    if not i < j < k:
        issues.append("RUNNER_LOG_ORDER_UNREVIEWED")
    # A line-order-only check can accept transplanted stages from logs
    # with impossible or reversed timestamps.
    all_lines = raw_log.splitlines()
    stamps = [
        reviewed_utc_nanoseconds(all_lines[index].split(" ", 1)[0])
        for index in (i, j, k)
    ]
    if any(stamp is None for stamp in stamps):
        issues.append("RUNNER_LOG_TIMESTAMP_UNREVIEWED")
    elif not stamps[0] < stamps[1] < stamps[2]:
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

    def test_unreviewed_second_checkout_after_valid_head_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git checkout "
            "--force refs/heads/other")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_unreviewed_second_fetch_after_valid_head_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git fetch "
            "origin refs/heads/other")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_reset_hard_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git reset "
            "--hard 0000000")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_git_switch_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git switch "
            "unreviewed")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_extra_differently_formatted_head_message_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:58.1000000Z HEAD is now at 0000000 unreviewed")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_read_only_git_status_action_does_not_look_like_checkout(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git status --short")
        self.assertEqual(self.verdict()[1], ())

    def test_read_only_git_show_action_does_not_look_like_checkout(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git show --format=oneline")
        self.assertEqual(self.verdict()[1], ())

    def test_ignored_console_echo_without_runner_command_marker(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z shell example: git checkout other")
        self.assertEqual(self.verdict()[1], ())

    def test_extra_reset_even_before_checkout_is_rejected(self):
        self.lines.insert(1,
            "2026-10-16T23:10:55.1000000Z [command]/usr/bin/git reset --hard")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_extra_checkout_evidence_does_not_authorize_run385(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git checkout other")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict()[1])

    def test_git_restore_worktree_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git restore --worktree .")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_git_clean_untracked_worktree_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git clean -fd")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_git_apply_patch_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git apply a.patch")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_git_am_patch_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git am a.mbox")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_git_merge_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git merge other")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_git_rebase_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git rebase other")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_git_pull_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git pull origin main")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_git_cherry_pick_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git cherry-pick abc1234")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_git_read_tree_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git read-tree HEAD")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_git_worktree_add_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git worktree add /tmp/w HEAD")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_git_update_index_after_checkout_is_rejected(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git update-index --refresh")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])

    def test_read_only_log_option_with_merge_word_is_allowed(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git log -1 --format=Merge")
        self.assertEqual(self.verdict()[1], ())

    def test_read_only_show_with_refs_pull_merge_path_is_allowed(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git show refs/pull/1664/merge")
        self.assertEqual(self.verdict()[1], ())

    def test_added_source_mutator_does_not_authorize_annual(self):
        self.lines.append(
            "2026-10-16T23:10:57.1000000Z [command]/usr/bin/git rebase main")
        self.assertIn("RUNNER_LOG_EXTRA_GIT_MUTATION_UNREVIEWED",
                      self.verdict()[1])
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict()[1])

    def test_fetch_checkout_head_times_one_hundred_ns_apart_pass(self):
        for i, fraction in enumerate(("0000001", "0000002", "0000003")):
            self.lines[i] = re.sub(
                r"^\S+", "2026-10-16T23:10:55." + fraction + "Z",
                self.lines[i])
        self.assertEqual(self.verdict()[1], ())

    def test_head_one_hundred_ns_before_checkout_is_rejected(self):
        for i, fraction in enumerate(("0000001", "0000003", "0000002")):
            self.lines[i] = re.sub(
                r"^\S+", "2026-10-16T23:10:55." + fraction + "Z",
                self.lines[i])
        self.assertIn("RUNNER_LOG_TIMESTAMP_ORDER_UNREVIEWED",
                      self.verdict()[1])
