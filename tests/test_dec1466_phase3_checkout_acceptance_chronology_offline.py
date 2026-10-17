"""DEC-1466: Phase3 acceptance index must follow tested Git checkout.

Pure offline caller-supplied GitHub Actions log text. Never downloads
artifacts or accesses protected originals, dispatch, brokers or security.
"""
from __future__ import annotations

from datetime import datetime
import json
import unittest

import test_dec1454_runner_merge_checkout_trace_parser_offline as checkout
import test_dec1462_phase3_raw_log_index_upload_offline as acceptance


def review_phase3_checkout_then_acceptance(raw_log, number, head, base,
                                           run_id, merge_sha):
    """Chain both independently reviewed stage parsers and temporal ordering."""
    fetched, checkout_issues = checkout.parse_runner_checkout(
        raw_log, number, head, base)
    index, receipt, acceptance_issues = acceptance.parse_phase3_log_evidence(
        raw_log, run_id, merge_sha)
    issues = list(checkout_issues) + list(acceptance_issues)
    if fetched is None or index is None or receipt is None:
        return tuple(sorted(set(issues + [
            "PHASE3_CHECKOUT_ACCEPTANCE_SOURCE_UNREVIEWED"])))
    if fetched["checkout_fetch_sha"] != merge_sha:
        issues.append("PHASE3_CHECKOUT_ACCEPTANCE_MERGE_MISMATCH")
    lines = raw_log.splitlines()
    checkout_found = [
        (i, m.group(1))
        for i, line in enumerate(lines)
        if (m := checkout.HEAD.fullmatch(line)) is not None
    ]
    index_found = [
        (i, m.group(1))
        for i, line in enumerate(lines)
        if (m := acceptance.INDEX.fullmatch(line)) is not None
    ]
    if len(checkout_found) != 1 or len(index_found) != 1:
        issues.append("PHASE3_CHECKOUT_ACCEPTANCE_STAGE_UNREVIEWED")
    else:
        checkout_i, _ = checkout_found[0]
        index_i, _ = index_found[0]
        if checkout_i >= index_i:
            issues.append("PHASE3_ACCEPTANCE_GENERATED_BEFORE_CHECKOUT")
        try:
            checkout_at = datetime.fromisoformat(
                lines[checkout_i].split(" ", 1)[0].replace("Z", "+00:00"))
            index_at = datetime.fromisoformat(
                lines[index_i].split(" ", 1)[0].replace("Z", "+00:00"))
        except (ValueError, OverflowError, TypeError):
            issues.append("PHASE3_CHECKOUT_ACCEPTANCE_TIMESTAMP_UNREVIEWED")
        else:
            if not checkout_at < index_at:
                issues.append("PHASE3_ACCEPTANCE_TIMESTAMP_BEFORE_CHECKOUT")
    return tuple(sorted(set(issues)))


class Phase3AcceptanceMustBeAfterItsOwnMergeCheckout(unittest.TestCase):
    def setUp(self):
        self.number, self.run_id, self.artifact_id = 1674, 39026055591, 12098433056
        self.head = "3033bec6416e1aeeb0fb7c41f6376d785b0ab425"
        self.base = "5c05f06874efed6c561103d89f443fff6be7d0a4"
        self.merge = "7630c183c7aca3e72a01b405b342c73db228c845"
        self.name = "phase3-backtester-acceptance-" + self.merge
        self.index = {
            "code_commit": self.merge,
            "fixture_id": "phase3-merged-main-acceptance-v1",
            "protocol": "fmp-phase3-acceptance-fixture-v1",
            "scenario_count": 5,
            "scenarios": [
                {"bytes_equal": True, "name": name,
                 "primary_manifest_sha256": "a"*64,
                 "repeat_manifest_sha256": "a"*64,
                 "trade_count": 1, "rejection_count": 0}
                for name in acceptance.SCENARIOS
            ],
        }
        self.lines = [
            "2026-10-17T10:44:42.4802303Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +" +
                self.merge + ":refs/remotes/pull/1674/merge",
            "2026-10-17T10:44:43.6358903Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/1674/merge",
            "2026-10-17T10:44:43.8544428Z HEAD is now at 7630c18 Merge " +
                self.head + " into " + self.base,
            "2026-10-17T10:44:58.9660091Z " +
                json.dumps(self.index, separators=(",", ":")),
            "2026-10-17T10:44:59.0284559Z   name: " + self.name,
            "2026-10-17T10:45:00.0166354Z Artifact " + self.name +
                ".zip successfully finalized. Artifact ID " +
                str(self.artifact_id),
            "2026-10-17T10:45:00.0169230Z Artifact " + self.name +
                " has been successfully uploaded! Final size is 23504 bytes. "
                "Artifact ID is " + str(self.artifact_id),
            "2026-10-17T10:45:00.0171215Z Artifact download URL: "
                "https://github.com/Dtwosam/FMP/actions/runs/" +
                str(self.run_id) + "/artifacts/" + str(self.artifact_id),
        ]

    def verdict(self):
        return review_phase3_checkout_then_acceptance(
            "\n".join(self.lines), self.number, self.head,
            self.base, self.run_id, self.merge)

    def test_observed_1674_source_stage_times_are_consistent(self):
        self.assertEqual(self.verdict(), ())

    def test_index_before_head_line_is_rejected(self):
        self.lines[2], self.lines[3] = self.lines[3], self.lines[2]
        self.assertIn("PHASE3_ACCEPTANCE_GENERATED_BEFORE_CHECKOUT",
                      self.verdict())

    def test_index_timestamp_before_head_timestamp_is_rejected(self):
        self.lines[3] = self.lines[3].replace(
            "2026-10-17T10:44:58.9660091Z",
            "2026-10-17T10:44:42.9660091Z")
        self.assertIn("PHASE3_ACCEPTANCE_TIMESTAMP_BEFORE_CHECKOUT",
                      self.verdict())

    def test_equal_head_and_index_times_are_rejected(self):
        self.lines[3] = self.lines[3].replace(
            "2026-10-17T10:44:58.9660091Z",
            "2026-10-17T10:44:43.8544428Z")
        self.assertIn("PHASE3_ACCEPTANCE_TIMESTAMP_BEFORE_CHECKOUT",
                      self.verdict())

    def test_index_uses_wrong_merge_sha_is_rejected(self):
        self.lines[3] = self.lines[3].replace(self.merge, "b"*40)
        self.assertIn("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED", self.verdict())

    def test_runner_fetch_another_merge_sha_is_rejected(self):
        self.lines[0] = self.lines[0].replace(self.merge, "b"*40)
        self.lines[2] = self.lines[2].replace("7630c18", "bbbbbbb")
        self.assertIn("PHASE3_CHECKOUT_ACCEPTANCE_MERGE_MISMATCH",
                      self.verdict())

    def test_missing_checkout_stage_is_rejected(self):
        self.lines.pop(1)
        self.assertIn("PHASE3_CHECKOUT_ACCEPTANCE_SOURCE_UNREVIEWED",
                      self.verdict())

    def test_missing_index_stage_is_rejected(self):
        self.lines.pop(3)
        self.assertIn("PHASE3_CHECKOUT_ACCEPTANCE_SOURCE_UNREVIEWED",
                      self.verdict())

    def test_wrong_artifact_run_url_is_rejected(self):
        self.lines[7] = self.lines[7].replace(str(self.run_id), "100")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH", self.verdict())

    def test_checkout_head_wrong_draft_parent_is_rejected(self):
        self.lines[2] = self.lines[2].replace(self.base, "d"*40)
        self.assertIn("RUNNER_LOG_PARENT_SHA_MISMATCH", self.verdict())

    def test_nontext_raw_log_fails_closed(self):
        self.assertIn("PHASE3_CHECKOUT_ACCEPTANCE_SOURCE_UNREVIEWED",
                      review_phase3_checkout_then_acceptance(
                          None, self.number, self.head, self.base,
                          self.run_id, self.merge))

    def test_temporal_evidence_never_grants_protected_2023_run(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
