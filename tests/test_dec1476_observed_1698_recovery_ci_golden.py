"""DEC-1476: observed unprotected 1698 recovery CI dual-checkout golden.

Source-only review of eight Phase3 lines and three historical job-log lines.
No annual dispatch, data/artifact download or authenticated provider claim.
"""
from __future__ import annotations

import unittest

import test_dec1454_runner_merge_checkout_trace_parser_offline as checkout
import test_dec1450_dual_suite_merge_checkout_offline as dual
import test_dec1462_phase3_raw_log_index_upload_offline as phase3
import test_dec1466_phase3_checkout_acceptance_chronology_offline as temporal
import test_dec1422_offline_exact_head_ci_evidence_review as workflows

PR = 1698
HEAD = "fa1cabab52e547b5f0a6f4cf39749df818529b59"
BASE = "4d4fbbae069254fdc4da549daaa799ba3ec09f6d"
MERGE = "0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9"
TREE = "21b9e451c6e255c0dfb73910995670b11f240bf3"
HIST_RUN = 39030113645
PHASE_RUN = 39030113556
HIST_JOB = 117388707144
PHASE_JOB = 117388706485
ARTIFACT_ID = 12100346157
OBSERVED_HIST_LOG_LINES = ["2026-10-17T11:49:01.4210120Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9:refs/remotes/pull/1698/merge","2026-10-17T11:49:02.6088732Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/1698/merge","2026-10-17T11:49:02.7746804Z HEAD is now at 0cf9a4b Merge fa1cabab52e547b5f0a6f4cf39749df818529b59 into 4d4fbbae069254fdc4da549daaa799ba3ec09f6d"]
OBSERVED_PHASE_LOG_LINES = ["2026-10-17T11:48:59.9084684Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9:refs/remotes/pull/1698/merge","2026-10-17T11:49:00.8034135Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/1698/merge","2026-10-17T11:49:01.0287628Z HEAD is now at 0cf9a4b Merge fa1cabab52e547b5f0a6f4cf39749df818529b59 into 4d4fbbae069254fdc4da549daaa799ba3ec09f6d","2026-10-17T11:49:17.3011567Z {\"code_commit\":\"0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9\",\"fixture_id\":\"phase3-merged-main-acceptance-v1\",\"protocol\":\"fmp-phase3-acceptance-fixture-v1\",\"scenario_count\":5,\"scenarios\":[{\"bytes_equal\":true,\"name\":\"ambiguity\",\"primary_manifest_sha256\":\"7afb5c370c8519337fae63ac1fb43f04358d7c514e778a4f0e498267e96a921f\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"7afb5c370c8519337fae63ac1fb43f04358d7c514e778a4f0e498267e96a921f\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"daily-halt-reset\",\"primary_manifest_sha256\":\"f1af5ad7bd2cf90a1c30125172624256f47d1cea2d0694c5e0eddcb725174e84\",\"rejection_count\":1,\"repeat_manifest_sha256\":\"f1af5ad7bd2cf90a1c30125172624256f47d1cea2d0694c5e0eddcb725174e84\",\"trade_count\":5},{\"bytes_equal\":true,\"name\":\"long-cost\",\"primary_manifest_sha256\":\"4ac62056ea1025f656eb1de38d3f4456df0b2c5b550e2af35127732f8d46cdd4\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"4ac62056ea1025f656eb1de38d3f4456df0b2c5b550e2af35127732f8d46cdd4\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"short-target\",\"primary_manifest_sha256\":\"1babd08b6854e480951745107ec7c38eff59cd0f89e3bbafe4ff2288114a60a7\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"1babd08b6854e480951745107ec7c38eff59cd0f89e3bbafe4ff2288114a60a7\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"simultaneous-risk\",\"primary_manifest_sha256\":\"a0aa7b79cce4f2fc2be28c1fbbaa2710bb10e8a5ff2b2006d0b05db4fd6a4a95\",\"rejection_count\":1,\"repeat_manifest_sha256\":\"a0aa7b79cce4f2fc2be28c1fbbaa2710bb10e8a5ff2b2006d0b05db4fd6a4a95\",\"trade_count\":2}]}","2026-10-17T11:49:17.3674415Z   name: phase3-backtester-acceptance-0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9","2026-10-17T11:49:18.7721136Z Artifact phase3-backtester-acceptance-0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9.zip successfully finalized. Artifact ID 12100346157","2026-10-17T11:49:18.7723473Z Artifact phase3-backtester-acceptance-0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9 has been successfully uploaded! Final size is 23491 bytes. Artifact ID is 12100346157","2026-10-17T11:49:18.7726359Z Artifact download URL: https://github.com/Dtwosam/FMP/actions/runs/39030113556/artifacts/12100346157"]


class ActualRecoveryRunnerLogsAreSourceEvidenceNotAnnualPermission(unittest.TestCase):
    def setUp(self):
        self.logs = {
            HIST_RUN: list(OBSERVED_HIST_LOG_LINES),
            PHASE_RUN: list(OBSERVED_PHASE_LOG_LINES),
        }
        self.pr = {"number": PR, "head_sha": HEAD, "base_sha": BASE}
        self.runs = [{
            "name": name, "id": run_id,
            "workflow_id": workflows.WORKFLOWS[name][0],
            "path": workflows.WORKFLOWS[name][1],
            "head_sha": HEAD, "run_attempt": 1, "event": "pull_request",
            "status": "completed", "conclusion": "success",
        } for name, run_id in (("tests", HIST_RUN),
                               ("phase3-acceptance", PHASE_RUN))]
        self.merge_ref = {"ref": "refs/pull/1698/merge",
                          "object": {"type": "commit", "sha": MERGE}}
        self.merge_commit = {
            "sha": MERGE, "tree": {"sha": TREE},
            "parents": [{"sha": BASE}, {"sha": HEAD}],
        }
        self.head_commit = {"sha": HEAD, "tree": {"sha": TREE}}

    def extracted(self):
        records, issues = {}, []
        for run_id, lines in self.logs.items():
            result, errors = checkout.parse_runner_checkout(
                "\n".join(lines), PR, HEAD, BASE)
            issues.extend(errors)
            if result is not None:
                records[run_id] = {"run_id": run_id, **result}
        return records, tuple(sorted(set(issues)))

    def dual_verdict(self):
        records, problems = self.extracted()
        if problems:
            return problems
        return dual.review_dual_suite_merge_checkouts(
            self.pr, self.runs, records, self.merge_ref,
            self.merge_commit, self.head_commit)

    def phase_verdict(self):
        return temporal.review_phase3_checkout_then_acceptance(
            "\n".join(self.logs[PHASE_RUN]), PR, HEAD, BASE, PHASE_RUN, MERGE)

    def acceptance_verdict(self):
        return phase3.parse_phase3_log_evidence(
            "\n".join(self.logs[PHASE_RUN]), PHASE_RUN, MERGE)

    def test_reviewed_both_ci_runners_fetched_one_full_merge_sha(self):
        evidence, issues = self.extracted()
        self.assertEqual(issues, ())
        self.assertEqual(evidence[HIST_RUN]["checkout_fetch_sha"], MERGE)
        self.assertEqual(evidence[PHASE_RUN]["checkout_fetch_sha"], MERGE)
        self.assertEqual(self.dual_verdict(), ())

    def test_reviewed_merge_tree_is_identical_to_head_source_tree(self):
        self.assertNotEqual(MERGE, HEAD)
        self.assertEqual(self.head_commit["tree"]["sha"],
                         self.merge_commit["tree"]["sha"])
        self.assertEqual(self.merge_commit["parents"][1]["sha"], HEAD)
        self.assertEqual(self.dual_verdict(), ())

    def test_reviewed_phase3_acceptance_follows_checkout(self):
        self.assertEqual(self.phase_verdict(), ())

    def test_reviewed_phase3_log_index_and_artifact_receipt(self):
        idx, uploaded, reasons = self.acceptance_verdict()
        self.assertEqual(reasons, ())
        self.assertEqual(idx["code_commit"], MERGE)
        self.assertEqual(uploaded["id"], ARTIFACT_ID)
        self.assertEqual(uploaded["run_id"], PHASE_RUN)
        self.assertEqual(uploaded["size_bytes"], 23491)

    def test_reviewed_phase3_manifest_hash_from_recovery_run(self):
        idx, _, reasons = self.acceptance_verdict()
        self.assertEqual(reasons, ())
        self.assertEqual(idx["scenarios"][0]["primary_manifest_sha256"],
                         "7afb5c370c8519337fae63ac1fb43f04358d7c514e778a4f0e498267e96a921f")
        self.assertEqual(idx["scenarios"][0]["repeat_manifest_sha256"],
                         idx["scenarios"][0]["primary_manifest_sha256"])

    def test_phase3_draft_head_as_fetched_sha_fails(self):
        self.logs[PHASE_RUN][0] = self.logs[PHASE_RUN][0].replace(MERGE, HEAD)
        self.assertIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH", self.dual_verdict())

    def test_historical_mismatched_checkout_prefix_fails(self):
        self.logs[HIST_RUN][2] = self.logs[HIST_RUN][2].replace("0cf9a4b", "fa1caba")
        self.assertIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH", self.dual_verdict())

    def test_missing_historical_checkout_fetch_fails(self):
        self.logs[HIST_RUN].pop(0)
        self.assertIn("RUNNER_LOG_STAGE_CARDINALITY_UNREVIEWED",
                      self.dual_verdict())

    def test_wrong_phase3_index_commit_fails(self):
        self.logs[PHASE_RUN][3] = self.logs[PHASE_RUN][3].replace(
            '"code_commit":"' + MERGE, '"code_commit":"' + HEAD)
        self.assertIn("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED",
                      self.phase_verdict())

    def test_wrong_phase3_artifact_id_fails(self):
        self.logs[PHASE_RUN][5] = self.logs[PHASE_RUN][5].replace(
            str(ARTIFACT_ID), "9999")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH",
                      self.phase_verdict())

    def test_wrong_phase3_run_url_fails(self):
        self.logs[PHASE_RUN][7] = self.logs[PHASE_RUN][7].replace(
            str(PHASE_RUN), "9999")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH",
                      self.phase_verdict())

    def test_phase3_index_before_checkout_timestamp_fails(self):
        self.logs[PHASE_RUN][3] = self.logs[PHASE_RUN][3].replace(
            "2026-10-17T11:49:17.3011567Z",
            "2026-10-17T11:48:58.3011567Z")
        self.assertIn("PHASE3_ACCEPTANCE_TIMESTAMP_BEFORE_CHECKOUT",
                      self.phase_verdict())

    def test_phase3_workflow_identity_drift_fails(self):
        self.runs[1]["workflow_id"] = 1
        self.assertIn("phase3-acceptance_WORKFLOW_IDENTITY_UNREVIEWED",
                      self.dual_verdict())

    def test_broken_merge_parent_pair_fails(self):
        self.merge_commit["parents"][0]["sha"] = "f"*40
        self.assertIn("tests_MERGE_COMMIT_PARENT_PAIR_UNREVIEWED",
                      self.dual_verdict())

    def test_broken_source_tree_equivalence_fails(self):
        self.merge_commit["tree"]["sha"] = "f"*40
        self.assertIn("tests_MERGE_AND_HEAD_FILE_TREE_MISMATCH",
                      self.dual_verdict())

    def test_real_ci_trace_source_consistency_cannot_authorize_annual_run(self):
        self.assertEqual(self.dual_verdict(), ())
        self.assertEqual(self.phase_verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.dual_verdict())
