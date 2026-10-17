"""DEC-1476: immutable-looking source fixtures from successful PR #1698 CI.

Observed unprotected GitHub Actions log excerpts, checked via offline readers.
No artifact download, protected original, annual dispatch or trading.
"""
from __future__ import annotations
import unittest

import test_dec1454_runner_merge_checkout_trace_parser_offline as checkout
import test_dec1450_dual_suite_merge_checkout_offline as dual
import test_dec1462_phase3_raw_log_index_upload_offline as acceptance
import test_dec1466_phase3_checkout_acceptance_chronology_offline as chronology
import test_dec1422_offline_exact_head_ci_evidence_review as workflow

PR = 1698
BASE = "4d4fbbae069254fdc4da549daaa799ba3ec09f6d"
HEAD = "fa1cabab52e547b5f0a6f4cf39749df818529b59"
MERGE = "0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9"
SOURCE_TREE = "21b9e451c6e255c0dfb73910995670b11f240bf3"
HISTORICAL_RUN = 39030113645
HISTORICAL_JOB = 117388707144
PHASE3_RUN = 39030113556
PHASE3_JOB = 117388706485
ARTIFACT_ID = 12100346157
HISTORICAL_CHECKOUT = ["2026-10-17T11:49:01.4210120Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9:refs/remotes/pull/1698/merge","2026-10-17T11:49:02.6088732Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/1698/merge","2026-10-17T11:49:02.7746804Z HEAD is now at 0cf9a4b Merge fa1cabab52e547b5f0a6f4cf39749df818529b59 into 4d4fbbae069254fdc4da549daaa799ba3ec09f6d"]
PHASE3_LOG = ["2026-10-17T11:48:59.9084684Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9:refs/remotes/pull/1698/merge","2026-10-17T11:49:00.8034135Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/1698/merge","2026-10-17T11:49:01.0287628Z HEAD is now at 0cf9a4b Merge fa1cabab52e547b5f0a6f4cf39749df818529b59 into 4d4fbbae069254fdc4da549daaa799ba3ec09f6d","2026-10-17T11:49:17.3011567Z {\"code_commit\":\"0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9\",\"fixture_id\":\"phase3-merged-main-acceptance-v1\",\"protocol\":\"fmp-phase3-acceptance-fixture-v1\",\"scenario_count\":5,\"scenarios\":[{\"bytes_equal\":true,\"name\":\"ambiguity\",\"primary_manifest_sha256\":\"7afb5c370c8519337fae63ac1fb43f04358d7c514e778a4f0e498267e96a921f\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"7afb5c370c8519337fae63ac1fb43f04358d7c514e778a4f0e498267e96a921f\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"daily-halt-reset\",\"primary_manifest_sha256\":\"f1af5ad7bd2cf90a1c30125172624256f47d1cea2d0694c5e0eddcb725174e84\",\"rejection_count\":1,\"repeat_manifest_sha256\":\"f1af5ad7bd2cf90a1c30125172624256f47d1cea2d0694c5e0eddcb725174e84\",\"trade_count\":5},{\"bytes_equal\":true,\"name\":\"long-cost\",\"primary_manifest_sha256\":\"4ac62056ea1025f656eb1de38d3f4456df0b2c5b550e2af35127732f8d46cdd4\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"4ac62056ea1025f656eb1de38d3f4456df0b2c5b550e2af35127732f8d46cdd4\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"short-target\",\"primary_manifest_sha256\":\"1babd08b6854e480951745107ec7c38eff59cd0f89e3bbafe4ff2288114a60a7\",\"rejection_count\":0,\"repeat_manifest_sha256\":\"1babd08b6854e480951745107ec7c38eff59cd0f89e3bbafe4ff2288114a60a7\",\"trade_count\":1},{\"bytes_equal\":true,\"name\":\"simultaneous-risk\",\"primary_manifest_sha256\":\"a0aa7b79cce4f2fc2be28c1fbbaa2710bb10e8a5ff2b2006d0b05db4fd6a4a95\",\"rejection_count\":1,\"repeat_manifest_sha256\":\"a0aa7b79cce4f2fc2be28c1fbbaa2710bb10e8a5ff2b2006d0b05db4fd6a4a95\",\"trade_count\":2}]}","2026-10-17T11:49:17.3674415Z   name: phase3-backtester-acceptance-0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9","2026-10-17T11:49:18.7721136Z Artifact phase3-backtester-acceptance-0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9.zip successfully finalized. Artifact ID 12100346157","2026-10-17T11:49:18.7723473Z Artifact phase3-backtester-acceptance-0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9 has been successfully uploaded! Final size is 23491 bytes. Artifact ID is 12100346157","2026-10-17T11:49:18.7726359Z Artifact download URL: https://github.com/Dtwosam/FMP/actions/runs/39030113556/artifacts/12100346157"]


class RecoveredTwoSuiteCheckoutAndArtifactGolden(unittest.TestCase):
    def setUp(self):
        self.logs = {
            HISTORICAL_RUN: list(HISTORICAL_CHECKOUT),
            PHASE3_RUN: list(PHASE3_LOG),
        }
        self.pr = {"number": PR, "head_sha": HEAD, "base_sha": BASE}
        self.runs = [
            {"id": run_id, "name": name,
             "workflow_id": workflow.WORKFLOWS[name][0],
             "path": workflow.WORKFLOWS[name][1],
             "head_sha": HEAD, "run_attempt": 1, "event": "pull_request",
             "status": "completed", "conclusion": "success"}
            for name, run_id in (("tests", HISTORICAL_RUN),
                                 ("phase3-acceptance", PHASE3_RUN))
        ]
        self.merge_ref = {
            "ref": "refs/pull/1698/merge",
            "object": {"type": "commit", "sha": MERGE},
        }
        self.merge_commit = {
            "sha": MERGE, "parents": [{"sha": BASE}, {"sha": HEAD}],
            "tree": {"sha": SOURCE_TREE},
        }
        self.head_commit = {"sha": HEAD, "tree": {"sha": SOURCE_TREE}}

    def parsed_checkouts(self):
        records, issues = {}, []
        for run_id, lines in self.logs.items():
            extracted, errors = checkout.parse_runner_checkout(
                "\n".join(lines), PR, HEAD, BASE)
            issues.extend(errors)
            if extracted is not None:
                records[run_id] = {"run_id": run_id, **extracted}
        return records, tuple(sorted(set(issues)))

    def dual_verdict(self):
        records, issues = self.parsed_checkouts()
        if issues:
            return issues
        return dual.review_dual_suite_merge_checkouts(
            self.pr, self.runs, records, self.merge_ref,
            self.merge_commit, self.head_commit)

    def phase3_verdict(self):
        return chronology.review_phase3_checkout_then_acceptance(
            "\n".join(self.logs[PHASE3_RUN]), PR, HEAD, BASE,
            PHASE3_RUN, MERGE)

    def test_both_real_runners_fetched_identical_merge_sha(self):
        checkouts, issues = self.parsed_checkouts()
        self.assertEqual(issues, ())
        self.assertEqual(checkouts[HISTORICAL_RUN]["checkout_fetch_sha"], MERGE)
        self.assertEqual(checkouts[PHASE3_RUN]["checkout_fetch_sha"], MERGE)

    def test_actual_two_ci_workflows_match_exact_source_tree(self):
        self.assertEqual(self.dual_verdict(), ())
        self.assertEqual(self.merge_commit["tree"]["sha"],
                         self.head_commit["tree"]["sha"])
        self.assertNotEqual(MERGE, HEAD)

    def test_actual_phase3_index_follows_checked_out_head(self):
        self.assertEqual(self.phase3_verdict(), ())

    def test_actual_phase3_index_has_five_matching_scenarios(self):
        index, receipt, issues = acceptance.parse_phase3_log_evidence(
            "\n".join(self.logs[PHASE3_RUN]), PHASE3_RUN, MERGE)
        self.assertEqual(issues, ())
        self.assertEqual(index["scenario_count"], 5)
        self.assertEqual(tuple(s["name"] for s in index["scenarios"]),
                         acceptance.SCENARIOS)
        for scenario in index["scenarios"]:
            self.assertIs(scenario["bytes_equal"], True)
            self.assertEqual(scenario["primary_manifest_sha256"],
                             scenario["repeat_manifest_sha256"])
        self.assertEqual(receipt["id"], ARTIFACT_ID)

    def test_phase3_artifact_is_stamped_with_merge_not_branch_head(self):
        index, receipt, issues = acceptance.parse_phase3_log_evidence(
            "\n".join(self.logs[PHASE3_RUN]), PHASE3_RUN, MERGE)
        self.assertEqual(issues, ())
        self.assertEqual(index["code_commit"], MERGE)
        self.assertNotEqual(index["code_commit"], HEAD)
        self.assertEqual(receipt["name"],
                         "phase3-backtester-acceptance-" + MERGE)
        self.assertEqual(receipt["run_id"], PHASE3_RUN)
        self.assertEqual(receipt["size_bytes"], 23491)

    def test_historical_short_head_must_match_immutable_fetched_sha(self):
        self.logs[HISTORICAL_RUN][2] = self.logs[HISTORICAL_RUN][2].replace(
            "0cf9a4b", "fa1caba")
        self.assertIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH",
                      self.dual_verdict())

    def test_phase3_fetched_sha_divergence_must_be_rejected(self):
        self.logs[PHASE3_RUN][0] = self.logs[PHASE3_RUN][0].replace(
            MERGE, HEAD)
        self.assertIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH",
                      self.dual_verdict())

    def test_different_merge_git_tree_must_be_rejected(self):
        self.merge_commit["tree"]["sha"] = "d"*40
        self.assertIn("tests_MERGE_AND_HEAD_FILE_TREE_MISMATCH",
                      self.dual_verdict())

    def test_wrong_merge_commit_parent_must_be_rejected(self):
        self.merge_commit["parents"][0]["sha"] = "e"*40
        self.assertIn("tests_MERGE_COMMIT_PARENT_PAIR_UNREVIEWED",
                      self.dual_verdict())

    def test_wrong_historical_workflow_id_must_be_rejected(self):
        self.runs[0]["workflow_id"] = 1
        self.assertIn("tests_WORKFLOW_IDENTITY_UNREVIEWED",
                      self.dual_verdict())

    def test_missing_historical_checkout_trace_must_be_rejected(self):
        self.logs[HISTORICAL_RUN].pop()
        self.assertIn("RUNNER_LOG_STAGE_CARDINALITY_UNREVIEWED",
                      self.dual_verdict())

    def test_phase3_index_wrong_checkout_sha_must_be_rejected(self):
        self.logs[PHASE3_RUN][3] = self.logs[PHASE3_RUN][3].replace(
            '"code_commit":"' + MERGE,
            '"code_commit":"' + HEAD)
        self.assertIn("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED",
                      self.phase3_verdict())

    def test_wrong_finalized_artifact_id_must_be_rejected(self):
        self.logs[PHASE3_RUN][5] = self.logs[PHASE3_RUN][5].replace(
            str(ARTIFACT_ID), "999999")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH",
                      self.phase3_verdict())

    def test_wrong_artifact_run_url_must_be_rejected(self):
        self.logs[PHASE3_RUN][7] = self.logs[PHASE3_RUN][7].replace(
            str(PHASE3_RUN), "100")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH",
                      self.phase3_verdict())

    def test_index_timestamp_before_checkout_must_be_rejected(self):
        self.logs[PHASE3_RUN][3] = self.logs[PHASE3_RUN][3].replace(
            "2026-10-17T11:49:17.3011567Z",
            "2026-10-17T11:48:58.3011567Z")
        self.assertIn("PHASE3_ACCEPTANCE_TIMESTAMP_BEFORE_CHECKOUT",
                      self.phase3_verdict())

    def test_source_goldens_never_confer_annual_execution_permission(self):
        self.assertEqual(self.dual_verdict(), ())
        self.assertEqual(self.phase3_verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED",
                         self.dual_verdict())
