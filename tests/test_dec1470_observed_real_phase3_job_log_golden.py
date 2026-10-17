"""DEC-1470: reviewed real, unprotected #1674 Phase3 GitHub log golden fixture.

These are only eight already observed CI log lines, not downloaded artifacts,
protected original sources or operational execution authorization.
"""
from __future__ import annotations

import unittest

import test_dec1466_phase3_checkout_acceptance_chronology_offline as temporal
import test_dec1462_phase3_raw_log_index_upload_offline as phase3

OBSERVED_RUN_ID = 39026055591
OBSERVED_JOB_ID = 117377148833
OBSERVED_PR = 1674
OBSERVED_HEAD = "3033bec6416e1aeeb0fb7c41f6376d785b0ab425"
OBSERVED_BASE = "5c05f06874efed6c561103d89f443fff6be7d0a4"
OBSERVED_MERGE = "7630c183c7aca3e72a01b405b342c73db228c845"
OBSERVED_ARTIFACT_ID = 12098433056
OBSERVED_RAW_LINES = ["2026-10-17T10:44:42.4802303Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +7630c183c7aca3e72a01b405b342c73db228c845:refs/remotes/pull/1674/merge","2026-10-17T10:44:43.6358903Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/1674/merge","2026-10-17T10:44:43.8544428Z HEAD is now at 7630c18 Merge 3033bec6416e1aeeb0fb7c41f6376d785b0ab425 into 5c05f06874efed6c561103d89f443fff6be7d0a4","2026-10-17T10:44:58.9660091Z {\"code_commit\":\"7630c183c7aca3e72a01b405b342c73db228c845\",\"fixture_id\":\"phase3-merged-main-acceptance-v1\",\"protocol\":\"fmp-phase3-acceptance-fixture-v1\",\"scenario_count\":5,\"scenarios\":[{\"bytes_equal\":true,\"name\":\"ambiguity\",\"primary_manifest_sha256\":\"83dd1dbf3b8d4fb082d35aaa71c188f76e5dc80980f0741441664de9ea842cbe\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"83dd1dbf3b8d4fb082d35aaa71c188f76e5dc80980f0741441664de9ea842cbe\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"daily-halt-reset\",\"primary_manifest_sha256\":\"1f66dc88ebb6d99cc73be40a04c7473205089fb97b7d3b0817b730d19f09fc7a\",\"rejection_count\":1,\"repeat_manifest_sha256\":\"1f66dc88ebb6d99cc73be40a04c7473205089fb97b7d3b0817b730d19f09fc7a\",\"trade_count\":5},{\"bytes_equal\":true,\"name\":\"long-cost\",\"primary_manifest_sha256\":\"457200c8487eb7717bdfe9aafed6b64c27cdcbdd57fa377d660f39a2ff7b97ef\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"457200c8487eb7717bdfe9aafed6b64c27cdcbdd57fa377d660f39a2ff7b97ef\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"short-target\",\"primary_manifest_sha256\":\"5f2122b8306fbe2293e89207c0694d9f987ee101869b4c8b0ed778c63772d2a4\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"5f2122b8306fbe2293e89207c0694d9f987ee101869b4c8b0ed778c63772d2a4\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"simultaneous-risk\",\"primary_manifest_sha256\":\"73c1f4b09d053752b6202c6de46e429ca43c8c6027565e21e9b301b238e4aeef\",\"rejection_count\":1,\"repeat_manifest_sha256\":\"73c1f4b09d053752b6202c6de46e429ca43c8c6027565e21e9b301b238e4aeef\",\"trade_count\":2}]}","2026-10-17T10:44:59.0284559Z   name: phase3-backtester-acceptance-7630c183c7aca3e72a01b405b342c73db228c845","2026-10-17T10:45:00.0166354Z Artifact phase3-backtester-acceptance-7630c183c7aca3e72a01b405b342c73db228c845.zip successfully finalized. Artifact ID 12098433056","2026-10-17T10:45:00.0169230Z Artifact phase3-backtester-acceptance-7630c183c7aca3e72a01b405b342c73db228c845 has been successfully uploaded! Final size is 23504 bytes. Artifact ID is 12098433056","2026-10-17T10:45:00.0171215Z Artifact download URL: https://github.com/Dtwosam/FMP/actions/runs/39026055591/artifacts/12098433056"]


class ReviewedRealPhase3JobLogIsNotAnnualExecutionConsent(unittest.TestCase):
    def setUp(self):
        self.lines = list(OBSERVED_RAW_LINES)

    def log(self):
        return "\n".join(self.lines)

    def verdict(self):
        return temporal.review_phase3_checkout_then_acceptance(
            self.log(), OBSERVED_PR, OBSERVED_HEAD, OBSERVED_BASE,
            OBSERVED_RUN_ID, OBSERVED_MERGE)

    def test_real_1674_checkout_and_acceptance_log_stages_are_consistent(self):
        self.assertEqual(self.verdict(), ())

    def test_real_scenario_names_and_manifest_hashes_are_consistent(self):
        idx, receipt, issues = phase3.parse_phase3_log_evidence(
            self.log(), OBSERVED_RUN_ID, OBSERVED_MERGE)
        self.assertEqual(issues, ())
        self.assertEqual(tuple(s["name"] for s in idx["scenarios"]),
                         phase3.SCENARIOS)
        self.assertEqual(
            idx["scenarios"][0]["primary_manifest_sha256"],
            "83dd1dbf3b8d4fb082d35aaa71c188f76e5dc80980f0741441664de9ea842cbe")
        self.assertEqual(receipt["id"], OBSERVED_ARTIFACT_ID)
        self.assertEqual(receipt["run_id"], OBSERVED_RUN_ID)

    def test_real_phase3_log_uses_merge_not_pr_head_sha(self):
        idx, _, problems = phase3.parse_phase3_log_evidence(
            self.log(), OBSERVED_RUN_ID, OBSERVED_MERGE)
        self.assertEqual(problems, ())
        self.assertEqual(idx["code_commit"], OBSERVED_MERGE)
        self.assertNotEqual(idx["code_commit"], OBSERVED_HEAD)

    def test_mutated_observed_checkout_short_sha_fails(self):
        self.lines[2] = self.lines[2].replace("7630c18", "3033bec")
        self.assertIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH", self.verdict())

    def test_mutated_observed_index_code_sha_fails(self):
        self.lines[3] = self.lines[3].replace(
            '"code_commit":"' + OBSERVED_MERGE,
            '"code_commit":"' + OBSERVED_HEAD)
        self.assertIn("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED",
                      self.verdict())

    def test_mutated_real_upload_finalization_id_fails(self):
        self.lines[5] = self.lines[5].replace(
            str(OBSERVED_ARTIFACT_ID), "9999")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH", self.verdict())

    def test_mutated_real_index_before_checkout_time_fails(self):
        self.lines[3] = self.lines[3].replace(
            "2026-10-17T10:44:58.9660091Z",
            "2026-10-17T10:44:42.9660091Z")
        self.assertIn("PHASE3_ACCEPTANCE_TIMESTAMP_BEFORE_CHECKOUT",
                      self.verdict())

    def test_missing_real_artifact_url_fails_closed(self):
        self.lines.pop()
        self.assertIn("PHASE3_CHECKOUT_ACCEPTANCE_SOURCE_UNREVIEWED",
                      self.verdict())

    def test_observed_github_log_fixture_does_not_authenticate_runner(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("GITHUB_LOG_PROVIDER_AUTHENTICATED", self.verdict())

    def test_golden_phase3_ci_log_never_authorizes_run385(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
