"""DEC-1476: second observed real PR merge-source CI golden fixture.

Read-only inspected GitHub Actions job log lines and commit metadata from
unprotected PR #1698. No downloaded artifacts, protected historical originals,
annual dispatch, GitHub settings changes, or brokerage operations.
"""
from __future__ import annotations

import unittest

import test_dec1454_runner_merge_checkout_trace_parser_offline as checkout
import test_dec1450_dual_suite_merge_checkout_offline as dual
import test_dec1462_phase3_raw_log_index_upload_offline as index_parser
import test_dec1466_phase3_checkout_acceptance_chronology_offline as timeline
import test_dec1422_offline_exact_head_ci_evidence_review as workflows

PR = 1698
HEAD = "fa1cabab52e547b5f0a6f4cf39749df818529b59"
BASE = "4d4fbbae069254fdc4da549daaa799ba3ec09f6d"
MERGE = "0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9"
TREE = "21b9e451c6e255c0dfb73910995670b11f240bf3"
HISTORICAL_RUN = 39030113645
PHASE3_RUN = 39030113556
HISTORICAL_JOB = 117388707144
PHASE3_JOB = 117388706485
ARTIFACT_ID = 12100346157
HISTORICAL_LINES = ["2026-10-17T11:49:01.4210120Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9:refs/remotes/pull/1698/merge","2026-10-17T11:49:02.6088732Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/1698/merge","2026-10-17T11:49:02.7746804Z HEAD is now at 0cf9a4b Merge fa1cabab52e547b5f0a6f4cf39749df818529b59 into 4d4fbbae069254fdc4da549daaa799ba3ec09f6d"]
PHASE3_LINES = ["2026-10-17T11:48:59.9084684Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9:refs/remotes/pull/1698/merge","2026-10-17T11:49:00.8034135Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/1698/merge","2026-10-17T11:49:01.0287628Z HEAD is now at 0cf9a4b Merge fa1cabab52e547b5f0a6f4cf39749df818529b59 into 4d4fbbae069254fdc4da549daaa799ba3ec09f6d","2026-10-17T11:49:17.3011567Z {\"code_commit\":\"0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9\",\"fixture_id\":\"phase3-merged-main-acceptance-v1\",\"protocol\":\"fmp-phase3-acceptance-fixture-v1\",\"scenario_count\":5,\"scenarios\":[{\"bytes_equal\":true,\"name\":\"ambiguity\",\"primary_manifest_sha256\":\"7afb5c370c8519337fae63ac1fb43f04358d7c514e778a4f0e498267e96a921f\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"7afb5c370c8519337fae63ac1fb43f04358d7c514e778a4f0e498267e96a921f\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"daily-halt-reset\",\"primary_manifest_sha256\":\"f1af5ad7bd2cf90a1c30125172624256f47d1cea2d0694c5e0eddcb725174e84\",\"rejection_count\":1,\"repeat_manifest_sha256\":\"f1af5ad7bd2cf90a1c30125172624256f47d1cea2d0694c5e0eddcb725174e84\",\"trade_count\":5},{\"bytes_equal\":true,\"name\":\"long-cost\",\"primary_manifest_sha256\":\"4ac62056ea1025f656eb1de38d3f4456df0b2c5b550e2af35127732f8d46cdd4\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"4ac62056ea1025f656eb1de38d3f4456df0b2c5b550e2af35127732f8d46cdd4\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"short-target\",\"primary_manifest_sha256\":\"1babd08b6854e480951745107ec7c38eff59cd0f89e3bbafe4ff2288114a60a7\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"1babd08b6854e480951745107ec7c38eff59cd0f89e3bbafe4ff2288114a60a7\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"simultaneous-risk\",\"primary_manifest_sha256\":\"a0aa7b79cce4f2fc2be28c1fbbaa2710bb10e8a5ff2b2006d0b05db4fd6a4a95\",\"rejection_count\":1,\"repeat_manifest_sha256\":\"a0aa7b79cce4f2fc2be28c1fbbaa2710bb10e8a5ff2b2006d0b05db4fd6a4a95\",\"trade_count\":2}]}","2026-10-17T11:49:17.3674415Z   name: phase3-backtester-acceptance-0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9","2026-10-17T11:49:18.7721136Z Artifact phase3-backtester-acceptance-0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9.zip successfully finalized. Artifact ID 12100346157","2026-10-17T11:49:18.7723473Z Artifact phase3-backtester-acceptance-0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9 has been successfully uploaded! Final size is 23491 bytes. Artifact ID is 12100346157","2026-10-17T11:49:18.7726359Z Artifact download URL: https://github.com/Dtwosam/FMP/actions/runs/39030113556/artifacts/12100346157"]


class RecoveredPairOfIndependentCiRunnersAreSourceEquivalent(unittest.TestCase):
    def setUp(self):
        self.pr = {"number": PR, "head_sha": HEAD, "base_sha": BASE}
        self.runs = [
            {
                "id": rid, "name": name, "workflow_id": workflows.WORKFLOWS[name][0],
                "path": workflows.WORKFLOWS[name][1], "head_sha": HEAD,
                "run_attempt": 1, "event": "pull_request", "status": "completed",
                "conclusion": "success",
            } for name, rid in (("tests", HISTORICAL_RUN),
                                ("phase3-acceptance", PHASE3_RUN))
        ]
        self.merge_ref = {"ref": "refs/pull/1698/merge",
                          "object": {"type": "commit", "sha": MERGE}}
        self.merge_commit = {
            "sha": MERGE, "tree": {"sha": TREE},
            "parents": [{"sha": BASE}, {"sha": HEAD}],
        }
        self.head_commit = {"sha": HEAD, "tree": {"sha": TREE}}
        self.historical_lines = list(HISTORICAL_LINES)
        self.phase3_lines = list(PHASE3_LINES)

    def checkouts(self):
        result = {}
        for run_id, lines in ((HISTORICAL_RUN, self.historical_lines),
                              (PHASE3_RUN, self.phase3_lines)):
            record, issues = checkout.parse_runner_checkout(
                "\n".join(lines), PR, HEAD, BASE)
            if issues:
                return {}, issues
            result[run_id] = {"run_id": run_id, **record}
        return result, ()

    def dual_verdict(self):
        records, problems = self.checkouts()
        if problems:
            return problems
        return dual.review_dual_suite_merge_checkouts(
            self.pr, self.runs, records, self.merge_ref,
            self.merge_commit, self.head_commit)

    def phase3_verdict(self):
        return index_parser.parse_phase3_log_evidence(
            "\n".join(self.phase3_lines), PHASE3_RUN, MERGE)

    def test_both_actual_1698_ci_runners_fetched_the_same_merge(self):
        records, issues = self.checkouts()
        self.assertEqual(issues, ())
        self.assertEqual(records[HISTORICAL_RUN]["checkout_fetch_sha"], MERGE)
        self.assertEqual(records[PHASE3_RUN]["checkout_fetch_sha"], MERGE)
        self.assertEqual(self.dual_verdict(), ())

    def test_actual_1698_git_source_trees_are_identical_not_commit_ids(self):
        self.assertEqual(self.head_commit["tree"]["sha"], TREE)
        self.assertEqual(self.merge_commit["tree"]["sha"], TREE)
        self.assertNotEqual(MERGE, HEAD)
        self.assertEqual(self.dual_verdict(), ())

    def test_phase3_logged_code_commit_and_artifact_are_merge_stamped(self):
        index, receipt, issues = self.phase3_verdict()
        self.assertEqual(issues, ())
        self.assertEqual(index["code_commit"], MERGE)
        self.assertNotEqual(index["code_commit"], HEAD)
        self.assertEqual(receipt["run_id"], PHASE3_RUN)
        self.assertEqual(receipt["id"], ARTIFACT_ID)
        self.assertEqual(receipt["size_bytes"], 23491)

    def test_real_1698_phase3_acceptance_follows_checkout_chronology(self):
        issues = timeline.review_phase3_checkout_then_acceptance(
            "\n".join(self.phase3_lines), PR, HEAD, BASE, PHASE3_RUN, MERGE)
        self.assertEqual(issues, ())

    def test_stale_historical_runner_short_sha_fails(self):
        self.historical_lines[2] = self.historical_lines[2].replace(
            "0cf9a4b", "fa1caba")
        self.assertIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH", self.dual_verdict())

    def test_different_phase3_full_fetched_sha_fails(self):
        self.phase3_lines[0] = self.phase3_lines[0].replace(MERGE, "a"*40)
        self.assertIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH", self.dual_verdict())

    def test_wrong_git_merge_parent_pair_fails(self):
        self.merge_commit["parents"][0]["sha"] = HEAD
        self.assertIn("tests_MERGE_COMMIT_PARENT_PAIR_UNREVIEWED",
                      self.dual_verdict())

    def test_changed_merge_tree_fails_even_when_green_ci_is_associated(self):
        self.merge_commit["tree"]["sha"] = "e"*40
        self.assertIn("tests_MERGE_AND_HEAD_FILE_TREE_MISMATCH",
                      self.dual_verdict())

    def test_wrong_phase3_run_attempt_fails(self):
        self.runs[1]["run_attempt"] = 2
        self.assertIn("phase3-acceptance_WORKFLOW_IDENTITY_UNREVIEWED",
                      self.dual_verdict())

    def test_phase3_artifact_url_wrong_run_fails_without_download(self):
        self.phase3_lines[-1] = self.phase3_lines[-1].replace(
            "/runs/39030113556/artifacts/", "/runs/39030113645/artifacts/")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH",
                      self.phase3_verdict()[2])

    def test_phase3_index_corrupted_manifest_hash_pair_fails(self):
        self.phase3_lines[3] = self.phase3_lines[3].replace(
            '"repeat_manifest_sha256":', '"repeat_manifest_sha256":"wrong",'
            '"repeat_manifest_sha256":', 1)
        self.assertIn("PHASE3_RAW_INDEX_JSON_UNREVIEWED",
                      self.phase3_verdict()[2])

    def test_both_actual_source_only_ci_log_fixtures_do_not_authorize_annual(self):
        self.assertEqual(self.dual_verdict(), ())
        self.assertEqual(self.phase3_verdict()[2], ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.dual_verdict())
