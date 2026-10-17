"""DEC-1486: verify observed checkout-action submodule cleanup command shapes.

Read-only exact source log excerpts from unprotected #1698 historical and Phase3
CI jobs. No network or signed provider/OS protected annual attestations.
"""
from __future__ import annotations

from datetime import datetime
import re
import unittest

import test_dec1454_runner_merge_checkout_trace_parser_offline as checkout
import test_dec1476_recovered_1698_dual_ci_golden as observed

PREFIX = r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) "
CMD = re.compile(PREFIX + r"\[command\]/usr/bin/git submodule (.*)$")
ALLOWED_SOURCE_COMMANDS = ["foreach --recursive sh -c \"git config --local --name-only --get-regexp 'core\\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :\"","foreach --recursive sh -c \"git config --local --name-only --get-regexp 'http\\.https\\:\\/\\/github\\.com\\/\\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :\"","foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url"]
OBSERVED_HISTORICAL_SUBMODULE_LINES = ["2026-10-17T11:49:01.3424152Z [command]/usr/bin/git submodule foreach --recursive sh -c \"git config --local --name-only --get-regexp 'core\\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :\"","2026-10-17T11:49:01.3765491Z [command]/usr/bin/git submodule foreach --recursive sh -c \"git config --local --name-only --get-regexp 'http\\.https\\:\\/\\/github\\.com\\/\\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :\"","2026-10-17T11:49:01.3984048Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url","2026-10-17T12:02:03.5820931Z [command]/usr/bin/git submodule foreach --recursive sh -c \"git config --local --name-only --get-regexp 'core\\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :\"","2026-10-17T12:02:03.6116846Z [command]/usr/bin/git submodule foreach --recursive sh -c \"git config --local --name-only --get-regexp 'http\\.https\\:\\/\\/github\\.com\\/\\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :\"","2026-10-17T12:02:03.6365055Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url"]
OBSERVED_PHASE3_SUBMODULE_LINES = ["2026-10-17T11:48:59.7878275Z [command]/usr/bin/git submodule foreach --recursive sh -c \"git config --local --name-only --get-regexp 'core\\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :\"","2026-10-17T11:48:59.8368333Z [command]/usr/bin/git submodule foreach --recursive sh -c \"git config --local --name-only --get-regexp 'http\\.https\\:\\/\\/github\\.com\\/\\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :\"","2026-10-17T11:48:59.8636290Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url","2026-10-17T11:49:19.0521493Z [command]/usr/bin/git submodule foreach --recursive sh -c \"git config --local --name-only --get-regexp 'core\\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :\"","2026-10-17T11:49:19.0867115Z [command]/usr/bin/git submodule foreach --recursive sh -c \"git config --local --name-only --get-regexp 'http\\.https\\:\\/\\/github\\.com\\/\\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :\"","2026-10-17T11:49:19.1703453Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url"]


def review_submodule_cleanup_source(raw_log, pr_number, head, base):
    """Review *this* observed actions/checkout submodule command sequence."""
    checkout_record, checkout_issues = checkout.parse_runner_checkout(
        raw_log, pr_number, head, base)
    issues = list(checkout_issues)
    if checkout_record is None or type(raw_log) is not str:
        return tuple(sorted(set(issues + [
            "SUBMODULE_CLEANUP_CHECKOUT_UNREVIEWED"])))
    lines = raw_log.splitlines()
    found = [(i, m) for i, line in enumerate(lines)
             if (m := CMD.fullmatch(line)) is not None]
    candidates = [
        i for i, line in enumerate(lines)
        if "[command]/usr/bin/git submodule " in line
    ]
    if len(found) != 6 or len(candidates) != 6:
        issues.append("SUBMODULE_CLEANUP_COMMAND_INVENTORY_UNREVIEWED")
        return tuple(sorted(set(issues)))
    expected = tuple(ALLOWED_SOURCE_COMMANDS) * 2
    if tuple(m.group(2) for _, m in found) != expected:
        issues.append("SUBMODULE_CLEANUP_SOURCE_SHAPE_DRIFT")
    fetch = [(i, m) for i, line in enumerate(lines)
             if (m := checkout.FETCH.fullmatch(line)) is not None]
    headmsg = [(i, m) for i, line in enumerate(lines)
               if (m := checkout.HEAD.fullmatch(line)) is not None]
    if len(fetch) != 1 or len(headmsg) != 1:
        issues.append("SUBMODULE_CLEANUP_SOURCE_STAGES_UNREVIEWED")
        return tuple(sorted(set(issues)))
    fetch_i, fetch_m = fetch[0]
    head_i, head_m = headmsg[0]
    order = [i for i, _ in found[:3]] + [fetch_i, head_i] + [
        i for i, _ in found[3:]]
    if order != sorted(order) or len(set(order)) != 8:
        issues.append("SUBMODULE_CLEANUP_STAGE_ORDER_UNREVIEWED")
    try:
        timestamps = [
            datetime.fromisoformat(t.replace("Z", "+00:00"))
            for t in [m.group(1) for _, m in found[:3]] +
                     [fetch_m.group(1), head_m.group(1)] +
                     [m.group(1) for _, m in found[3:]]
        ]
    except (ValueError, TypeError, OverflowError):
        issues.append("SUBMODULE_CLEANUP_TIMESTAMP_UNREVIEWED")
    else:
        if not all(a < b for a, b in zip(timestamps, timestamps[1:])):
            issues.append("SUBMODULE_CLEANUP_TIMESTAMP_ORDER_UNREVIEWED")
    return tuple(sorted(set(issues)))


class ReviewedSubmoduleCleanupIsNotUnrestrictedGitPermission(unittest.TestCase):
    def setUp(self):
        self.lines = (
            list(OBSERVED_PHASE3_SUBMODULE_LINES[:3]) +
            list(observed.PHASE3_LINES[:3]) +
            list(OBSERVED_PHASE3_SUBMODULE_LINES[3:])
        )

    def verdict(self):
        return review_submodule_cleanup_source(
            "\n".join(self.lines), observed.PR,
            observed.HEAD, observed.BASE)

    def test_actual_phase3_submodule_cleanup_source_passes(self):
        self.assertEqual(self.verdict(), ())

    def test_actual_historical_submodule_cleanup_source_passes(self):
        self.lines = (
            list(OBSERVED_HISTORICAL_SUBMODULE_LINES[:3]) +
            list(observed.HISTORICAL_LINES[:3]) +
            list(OBSERVED_HISTORICAL_SUBMODULE_LINES[3:])
        )
        self.assertEqual(self.verdict(), ())

    def test_missing_precheckout_submodule_config_cleanup_fails(self):
        self.lines.pop(1)
        self.assertIn("SUBMODULE_CLEANUP_COMMAND_INVENTORY_UNREVIEWED",
                      self.verdict())

    def test_extra_submodule_update_after_checkout_fails(self):
        self.lines.append(
            "2026-10-17T11:49:20.0000000Z "
            "[command]/usr/bin/git submodule update --init")
        self.assertIn("SUBMODULE_CLEANUP_COMMAND_INVENTORY_UNREVIEWED",
                      self.verdict())

    def test_unreviewed_submodule_foreach_shell_action_fails(self):
        self.lines[1] = (
            "2026-10-17T11:48:59.8368333Z "
            "[command]/usr/bin/git submodule foreach --recursive git reset --hard")
        self.assertIn("SUBMODULE_CLEANUP_SOURCE_SHAPE_DRIFT", self.verdict())

    def test_precheckout_cleanup_moved_after_head_fails(self):
        item = self.lines.pop(0)
        self.lines.insert(6, item)
        self.assertIn("SUBMODULE_CLEANUP_STAGE_ORDER_UNREVIEWED",
                      self.verdict())

    def test_postcheckout_cleanup_moved_before_fetch_fails(self):
        item = self.lines.pop(-1)
        self.lines.insert(0, item)
        self.assertIn("SUBMODULE_CLEANUP_STAGE_ORDER_UNREVIEWED",
                      self.verdict())

    def test_invalid_submodule_cleanup_timestamp_fails(self):
        self.lines[0] = self.lines[0].replace("2026-10-17", "2026-99-17")
        self.assertIn("SUBMODULE_CLEANUP_TIMESTAMP_UNREVIEWED", self.verdict())

    def test_submodule_cleanup_timestamp_reverse_fails(self):
        self.lines[1] = self.lines[1].replace(
            "11:48:59.8368333Z", "11:48:58.8368333Z")
        self.assertIn("SUBMODULE_CLEANUP_TIMESTAMP_ORDER_UNREVIEWED",
                      self.verdict())

    def test_wrong_pr_merge_checkout_still_fails(self):
        self.lines[4] = self.lines[4].replace("/1698/merge", "/999/merge")
        self.assertIn("RUNNER_LOG_PR_REF_MISMATCH", self.verdict())

    def test_extra_read_only_git_show_is_not_submodule_cleanup(self):
        self.lines.append(
            "2026-10-17T11:49:20.0000000Z "
            "[command]/usr/bin/git show --no-patch")
        self.assertEqual(self.verdict(), ())

    def test_source_cleanup_model_is_not_real_protected_os_attestation(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("PROTECTED_ORIGINAL_OS_NO_WRITE_PROVEN",
                         self.verdict())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
