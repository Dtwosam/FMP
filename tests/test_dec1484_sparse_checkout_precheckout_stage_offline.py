"""DEC-1484: sparse-checkout disable is source-changing precheckout setup.

Audit caller-supplied actual GitHub Actions checkout trace. No protected
annual run, artifact downloads, network or authenticated runner OS claims.
"""
from __future__ import annotations

from datetime import datetime
import re
import unittest

import test_dec1454_runner_merge_checkout_trace_parser_offline as checkout
import test_dec1476_recovered_1698_dual_ci_golden as golden

SPARSE = re.compile(
    r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) "
    r"\[command\]/usr/bin/git sparse-checkout disable$")
MARKER = re.compile(r"\[command\]/usr/bin/git[ \t]+sparse-checkout(?:[ \t]+|$)")


def review_sparse_disable_before_checkout(raw_log, pr_number, head_sha, base_sha):
    """Require unique, strictly positioned sparse-disable checkout setup."""
    parsed, issues = checkout.parse_runner_checkout(
        raw_log, pr_number, head_sha, base_sha)
    issues = list(issues)
    if parsed is None or type(raw_log) is not str:
        return tuple(sorted(set(issues + ["SPARSE_SETUP_CHECKOUT_UNREVIEWED"])))
    lines = raw_log.splitlines()
    found = [(i, m) for i, line in enumerate(lines)
             if (m := SPARSE.fullmatch(line)) is not None]
    candidates = [(i, line) for i, line in enumerate(lines)
                  if MARKER.search(line) is not None]
    if len(found) != 1 or len(candidates) != 1:
        issues.append("SPARSE_SETUP_CARDINALITY_UNREVIEWED")
        return tuple(sorted(set(issues)))
    (sparse_i, sparse_match), = found
    if candidates[0][0] != sparse_i:
        issues.append("SPARSE_SETUP_COMMAND_UNREVIEWED")
    fetch = [(i, m) for i, line in enumerate(lines)
             if (m := checkout.FETCH.fullmatch(line)) is not None]
    checked = [(i, m) for i, line in enumerate(lines)
               if (m := checkout.CHECKOUT.fullmatch(line)) is not None]
    if len(fetch) != 1 or len(checked) != 1:
        issues.append("SPARSE_SETUP_SOURCE_SEQUENCE_UNREVIEWED")
        return tuple(sorted(set(issues)))
    fetch_i, fetch_match = fetch[0]
    checkout_i, checkout_match = checked[0]
    if not fetch_i < sparse_i < checkout_i:
        issues.append("SPARSE_SETUP_STAGE_ORDER_UNREVIEWED")
    try:
        stamps = [
            datetime.fromisoformat(x.group(1).replace("Z", "+00:00"))
            for x in (fetch_match, sparse_match, checkout_match)
        ]
    except (ValueError, OverflowError, TypeError):
        issues.append("SPARSE_SETUP_TIMESTAMP_UNREVIEWED")
    else:
        if not stamps[0] < stamps[1] < stamps[2]:
            issues.append("SPARSE_SETUP_TIMESTAMP_ORDER_UNREVIEWED")
    return tuple(sorted(set(issues)))


class ObservedCheckoutSparseSetupIsNotOriginalOsNoWriteProof(unittest.TestCase):
    def setUp(self):
        self.lines = [
            golden.PHASE3_LINES[0],
            "2026-10-17T11:49:00.7929061Z "
            "[command]/usr/bin/git sparse-checkout disable",
            golden.PHASE3_LINES[1],
            golden.PHASE3_LINES[2],
        ]

    def verdict(self):
        return review_sparse_disable_before_checkout(
            "\n".join(self.lines), golden.PR, golden.HEAD, golden.BASE)

    def test_1698_observed_phase3_sparse_setup_sequence_matches(self):
        self.assertEqual(self.verdict(), ())

    def test_historical_1698_observed_sparse_setup_sequence_matches(self):
        self.lines = [
            golden.HISTORICAL_LINES[0],
            "2026-10-17T11:49:02.6000539Z "
            "[command]/usr/bin/git sparse-checkout disable",
            golden.HISTORICAL_LINES[1],
            golden.HISTORICAL_LINES[2],
        ]
        self.assertEqual(self.verdict(), ())

    def test_no_sparse_setup_command_does_not_pass(self):
        self.lines.pop(1)
        self.assertIn("SPARSE_SETUP_CARDINALITY_UNREVIEWED", self.verdict())

    def test_duplicate_sparse_disable_does_not_pass(self):
        self.lines.insert(2, self.lines[1])
        self.assertIn("SPARSE_SETUP_CARDINALITY_UNREVIEWED", self.verdict())

    def test_sparse_set_instead_of_disable_does_not_pass(self):
        self.lines[1] = self.lines[1].replace(" disable", " set .")
        self.assertIn("SPARSE_SETUP_CARDINALITY_UNREVIEWED", self.verdict())

    def test_sparse_disable_after_checkout_is_rejected(self):
        self.lines[1], self.lines[2] = self.lines[2], self.lines[1]
        self.assertIn("SPARSE_SETUP_STAGE_ORDER_UNREVIEWED", self.verdict())

    def test_sparse_disable_before_fetch_is_rejected(self):
        self.lines[0], self.lines[1] = self.lines[1], self.lines[0]
        self.assertIn("SPARSE_SETUP_STAGE_ORDER_UNREVIEWED", self.verdict())

    def test_sparse_setup_timestamp_before_fetch_is_rejected(self):
        self.lines[1] = self.lines[1].replace(
            "11:49:00.7929061Z", "11:48:59.7929061Z")
        self.assertIn("SPARSE_SETUP_TIMESTAMP_ORDER_UNREVIEWED",
                      self.verdict())

    def test_sparse_setup_timestamp_after_checkout_is_rejected(self):
        self.lines[1] = self.lines[1].replace(
            "11:49:00.7929061Z", "11:49:01.7929061Z")
        self.assertIn("SPARSE_SETUP_TIMESTAMP_ORDER_UNREVIEWED",
                      self.verdict())

    def test_invalid_calendar_sparse_disable_fails_closed(self):
        self.lines[1] = self.lines[1].replace("2026-10-17", "2026-99-17")
        self.assertIn("SPARSE_SETUP_TIMESTAMP_UNREVIEWED", self.verdict())

    def test_unreviewed_second_sparse_set_command_fails(self):
        self.lines.insert(
            2, "2026-10-17T11:49:00.7950000Z "
               "[command]/usr/bin/git sparse-checkout set src")
        self.assertIn("SPARSE_SETUP_CARDINALITY_UNREVIEWED", self.verdict())

    def test_wrong_pr_merge_checkout_ref_still_rejected(self):
        self.lines[2] = self.lines[2].replace("/1698/merge", "/9999/merge")
        self.assertIn("RUNNER_LOG_PR_REF_MISMATCH", self.verdict())

    def test_syntactically_reviewed_setup_is_not_runtime_os_attestation(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("PROTECTED_ORIGINAL_OS_NO_WRITE_PROVEN", self.verdict())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
