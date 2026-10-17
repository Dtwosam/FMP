"""DEC-1440: compose independently supplied offline draft/CI evidence shapes.

Absolutely no network, workflow dispatch, protected-original read/write,
GitHub settings change or trading. Consistency is NOT source authentication.
"""
from __future__ import annotations

import unittest
import hashlib
import json
import test_dec1426_exact_ci_job_critical_steps_offline as jobs_review
import test_dec1436_pr_compare_file_count_offline as file_review
import test_dec1435_git_tree_regular_blob_review as modes_review
import test_dec1439_changed_git_blob_source_bytes_offline as bytes_review
import test_dec1430_reviewed_ci_workflow_blob_source_identity as ci_source
import test_dec1441_git_tree_sha_chain_source_review as tree_chain
import test_dec1445_pr_merge_checkout_tree_identity_offline as merge_review
import test_dec1450_dual_suite_merge_checkout_offline as dual_runner
import test_dec1447_phase3_acceptance_merge_stamp_offline as phase3_stamps
import test_dec1454_runner_merge_checkout_trace_parser_offline as log_parse
import test_dec1458_ci_job_raw_log_receipt_offline as log_receipt
import test_dec1462_phase3_raw_log_index_upload_offline as phase3_raw


def review_stacked_draft_evidence(pr, runs, jobs_by_run, compare, commit,
                                  tree, nodes, changed_bytes, ci_workflow_bytes,
                                  full_tree_snapshots, merge_checkout_snapshot,
                                  checkout_by_run, phase3_evidence_snapshot,
                                  raw_ci_runner_logs, raw_ci_log_receipts):
    """Return diagnostic shape only; never authorization or authenticated proof."""
    # Run metadata head_sha is an association to the PR branch head, not
    # evidence that checkout HEAD equaled that SHA. Review the actual merge.
    if type(merge_checkout_snapshot) is not dict:
        merge_check = ("MERGE_CHECKOUT_SNAPSHOT_UNREVIEWED",)
    elif type(runs) is not list or not all(type(r) is dict for r in runs):
        merge_check = ("MERGE_HISTORICAL_RUN_UNREVIEWED",)
    else:
        historical = [r for r in runs if r.get("name") == "tests"]
        if len(historical) != 1:
            merge_check = ("MERGE_HISTORICAL_RUN_UNREVIEWED",)
        else:
            e = merge_checkout_snapshot
            merge_check = merge_review.review_pr_merge_checkout(
                pr, historical[0], e.get("merge_ref"),
                e.get("merge_commit"), e.get("head_commit"),
                e.get("checkout_ref"), e.get("checkout_sha_prefix"),
                e.get("checkout_fetch_sha"))
    if type(merge_checkout_snapshot) is dict:
        e = merge_checkout_snapshot
        dual_check = dual_runner.review_dual_suite_merge_checkouts(
            pr, runs, checkout_by_run, e.get("merge_ref"),
            e.get("merge_commit"), e.get("head_commit"))
    else:
        dual_check = ("DUAL_CHECKOUT_INPUT_UNREVIEWED",)
    if (type(phase3_evidence_snapshot) is not dict or
            type(merge_checkout_snapshot) is not dict or
            type(runs) is not list or
            not all(type(run) is dict for run in runs)):
        phase3_check = ("PHASE3_ACCEPTANCE_SNAPSHOT_UNREVIEWED",)
    else:
        phase3_runs = [r for r in runs if r.get("name") == "phase3-acceptance"]
        if len(phase3_runs) != 1:
            phase3_check = ("PHASE3_ACCEPTANCE_RUN_UNREVIEWED",)
        else:
            e = phase3_evidence_snapshot
            merge = merge_checkout_snapshot.get("merge_commit")
            merge_sha = merge.get("sha") if type(merge) is dict else None
            phase3_check = phase3_stamps.review_phase3_merge_evidence(
                phase3_runs[0], merge_sha, e.get("index"), e.get("upload"))
    # Raw run logs are separate per-workflow evidence, not metadata derived
    # from the run's association to a mutable PR merge ref.
    raw_issues = []
    if (type(raw_ci_runner_logs) is not dict or type(checkout_by_run) is not dict
            or type(runs) is not list or type(pr) is not dict or
            not all(type(r) is dict for r in runs)):
        raw_issues.append("RAW_CI_RUNNER_LOG_INPUT_UNREVIEWED")
    else:
        expected_run_ids = [
            r.get("id") for r in runs
            if r.get("name") in ("phase3-acceptance", "tests")
            and type(r.get("id")) is int and r["id"] > 0
        ]
        if (len(expected_run_ids) != 2 or
                len(set(expected_run_ids)) != 2 or
                set(raw_ci_runner_logs) != set(expected_run_ids)):
            raw_issues.append("RAW_CI_RUNNER_LOG_INVENTORY_UNREVIEWED")
        for run_id in expected_run_ids:
            parsed, parse_issues = log_parse.parse_runner_checkout(
                raw_ci_runner_logs.get(run_id),
                pr.get("number"), pr.get("head_sha"), pr.get("base_sha"))
            raw_issues.extend(parse_issues)
            supplied = checkout_by_run.get(run_id)
            if type(supplied) is not dict or parsed is None:
                raw_issues.append("RAW_CI_RUNNER_LOG_RECORD_UNREVIEWED")
            elif any(parsed.get(key) != supplied.get(key)
                     for key in ("checkout_ref", "checkout_fetch_sha",
                                 "checkout_sha_prefix")):
                raw_issues.append("RAW_CI_RUNNER_LOG_METADATA_MISMATCH")
    # Decode Phase3's actual JSON index, finalization/upload and run URL
    # from the supplied job log, instead of trusting pre-extracted dicts.
    phase3_log_issues = []
    if (type(raw_ci_runner_logs) is not dict or type(runs) is not list or
            type(phase3_evidence_snapshot) is not dict or
            type(merge_checkout_snapshot) is not dict):
        phase3_log_issues.append("PHASE3_RAW_INDEX_RECEIPT_INPUT_UNREVIEWED")
    else:
        matching = [r for r in runs if type(r) is dict and
                    r.get("name") == "phase3-acceptance"]
        merge = merge_checkout_snapshot.get("merge_commit")
        merge_sha = merge.get("sha") if type(merge) is dict else None
        if len(matching) != 1 or type(matching[0].get("id")) is not int:
            phase3_log_issues.append("PHASE3_RAW_INDEX_RUN_UNREVIEWED")
        else:
            phase3_id = matching[0]["id"]
            idx, receipt, parsed_issues = phase3_raw.parse_phase3_log_evidence(
                raw_ci_runner_logs.get(phase3_id), phase3_id, merge_sha)
            phase3_log_issues.extend(parsed_issues)
            if idx is None or receipt is None:
                phase3_log_issues.append("PHASE3_RAW_INDEX_RECEIPT_UNREVIEWED")
            else:
                if idx != phase3_evidence_snapshot.get("index"):
                    phase3_log_issues.append(
                        "PHASE3_RAW_INDEX_VS_SUPPLIED_EVIDENCE_MISMATCH")
                supplied = phase3_evidence_snapshot.get("upload")
                if type(supplied) is not dict or any(
                        receipt.get(k) != supplied.get(k)
                        for k in ("name", "id", "run_id", "finalized")):
                    phase3_log_issues.append(
                        "PHASE3_RAW_UPLOAD_VS_SUPPLIED_EVIDENCE_MISMATCH")
    checks = (
        tuple(sorted(set(phase3_log_issues))),
        tuple(sorted(set(raw_issues))),
        log_receipt.review_ci_job_log_receipts(
            runs, jobs_by_run, raw_ci_runner_logs, raw_ci_log_receipts),
        merge_check,
        phase3_check,
        dual_check,
        jobs_review.review_exact_pr_ci_jobs(pr, runs, jobs_by_run),
        file_review.review_draft_file_inventory_counts(pr, compare, commit),
        modes_review.review_source_tree_mode(pr, compare, commit, tree, nodes),
        bytes_review.review_changed_blob_byte_identity(
            compare, nodes, changed_bytes),
        ci_source.review_ci_workflow_blobs(ci_workflow_bytes),
        tree_chain.review_exact_changed_tree_chain(
            commit, compare, full_tree_snapshots, changed_bytes),
    )
    diagnostics = tuple(sorted({reason for check in checks for reason in check}))
    return {
        "source_consistency": not diagnostics,
        "diagnostics": diagnostics,
        "independent_original_os_proof": False,
        "exclusive_server_dispatch_gate_proven": False,
        "can_authorize_annual_run": False,
    }


class CombinedSourceChecksRemainNonAuthorizing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_ci_bytes = ci_source.checked_in_ci_sources()

    def setUp(self):
        fixture = jobs_review.ActualRequiredStepEvidenceIsNotProtectedExecutionConsent(
            "test_exact_successful_job_and_step_evidence_is_consistent")
        fixture.setUp()
        self.pr = dict(fixture.pr)
        self.pr.update({"changed_files": 2, "additions": 10, "deletions": 0})
        self.runs = fixture.runs
        self.jobs = fixture.jobs_by_run
        base, head = self.pr["base_sha"], self.pr["head_sha"]
        self.compare = {
            "repository_full_name": "Dtwosam/FMP",
            "base": base, "head": head, "status": "ahead",
            "ahead_by": 1, "behind_by": 0, "total_commits": 1,
            "base_commit": {"sha": base},
            "merge_base_commit": {"sha": base},
            "too_large": None,
            "files": [
                {"filename": "tests/sample.py", "status": "added",
                 "previous_filename": None, "additions": 6,
                 "deletions": 0, "changes": 6},
                {"filename": "docs/sample.md", "status": "added",
                 "previous_filename": None, "additions": 4,
                 "deletions": 0, "changes": 4},
            ],
        }
        tree_sha = "c" * 40
        self.commit = {"sha": head, "parents": [{"sha": base}],
                       "tree": {"sha": tree_sha}}
        self.tree = {"sha": tree_sha, "truncated": False}
        self.changed = {
            "tests/sample.py": b"pass\n",
            "docs/sample.md": b"# Source-only\n",
        }
        self.nodes = {
            "tests": {"mode": "040000", "type": "tree"},
            "docs": {"mode": "040000", "type": "tree"},
        }
        self.nodes.update({
            path: {"mode": "100644", "type": "blob",
                   "sha": ci_source.git_blob_id(payload)}
            for path, payload in self.changed.items()
        })
        self.full_trees = {
            tree_sha: {
                "sha": tree_sha, "truncated": False,
                "tree": [
                    {"path": "tests", "mode": "040000", "type": "tree", "sha": "d"*40},
                    {"path": "docs", "mode": "040000", "type": "tree", "sha": "e"*40},
                ],
            },
            "d"*40: {
                "sha": "d"*40, "truncated": False,
                "tree": [{"path": "sample.py", "mode": "100644",
                          "type": "blob",
                          "sha": ci_source.git_blob_id(self.changed["tests/sample.py"])}],
            },
            "e"*40: {
                "sha": "e"*40, "truncated": False,
                "tree": [{"path": "sample.md", "mode": "100644",
                          "type": "blob",
                          "sha": ci_source.git_blob_id(self.changed["docs/sample.md"])}],
            },
        }
        tests_object = self.full_trees.pop("d"*40)
        self.git_tests_tree = tree_chain.reviewed_git_tree_sha(
            tests_object["tree"])
        tests_object["sha"] = self.git_tests_tree
        self.full_trees[self.git_tests_tree] = tests_object
        docs_object = self.full_trees.pop("e"*40)
        self.git_docs_tree = tree_chain.reviewed_git_tree_sha(
            docs_object["tree"])
        docs_object["sha"] = self.git_docs_tree
        self.full_trees[self.git_docs_tree] = docs_object
        root_object = self.full_trees.pop(tree_sha)
        for entry in root_object["tree"]:
            entry["sha"] = (self.git_tests_tree if entry["path"] == "tests"
                            else self.git_docs_tree)
        root_object["tree"].sort(
            key=lambda e: e["path"].encode("utf-8") +
            (b"/" if e["mode"] == "040000" else b""))
        self.git_root_tree = tree_chain.reviewed_git_tree_sha(
            root_object["tree"])
        root_object["sha"] = self.git_root_tree
        self.full_trees[self.git_root_tree] = root_object
        self.commit["tree"]["sha"] = self.git_root_tree
        self.tree["sha"] = self.git_root_tree
        self.merge_checkout = {
            "merge_ref": {
                "ref": "refs/pull/1649/merge",
                "object": {"type": "commit", "sha": "f"*40},
            },
            "merge_commit": {
                "sha": "f"*40, "tree": {"sha": self.git_root_tree},
                "parents": [{"sha": self.pr["base_sha"]},
                            {"sha": self.pr["head_sha"]}],
            },
            "head_commit": {
                "sha": self.pr["head_sha"],
                "tree": {"sha": self.git_root_tree},
            },
            "checkout_ref": "refs/remotes/pull/1649/merge",
            "checkout_sha_prefix": "fffffff",
            "checkout_fetch_sha": "f"*40,
        }
        self.runner_checks = {
            r["id"]: {
                "run_id": r["id"],
                "checkout_ref": self.merge_checkout["checkout_ref"],
                "checkout_sha_prefix": self.merge_checkout["checkout_sha_prefix"],
                "checkout_fetch_sha": self.merge_checkout["checkout_fetch_sha"],
            }
            for r in self.runs
        }
        self.phase3_evidence = {
            "index": {
                "protocol": "fmp-phase3-acceptance-fixture-v1",
                "fixture_id": "phase3-merged-main-acceptance-v1",
                "code_commit": self.merge_checkout["merge_commit"]["sha"],
                "scenario_count": 5,
                "scenarios": [
                    {"name": scenario, "bytes_equal": True,
                     "primary_manifest_sha256": "a"*64,
                     "repeat_manifest_sha256": "a"*64,
                     "trade_count": 1, "rejection_count": 0}
                    for scenario in phase3_stamps.SCENARIOS
                ],
            },
            "upload": {
                "name": "phase3-backtester-acceptance-" +
                        self.merge_checkout["merge_commit"]["sha"],
                "id": 7777, "run_id": 8000, "finalized": True,
            },
        }
        raw_ref = "refs/remotes/pull/" + str(self.pr["number"]) + "/merge"
        raw_merge = self.merge_checkout["merge_commit"]["sha"]
        raw_head = self.pr["head_sha"]
        raw_base = self.pr["base_sha"]
        self.raw_ci_runner_logs = {
            run["id"]: "\n".join([
                "2026-10-17T10:00:00.1000000Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags origin +" + raw_merge + ":" + raw_ref,
                "2026-10-17T10:00:01.1000000Z [command]/usr/bin/git checkout --progress --force " + raw_ref,
                "2026-10-17T10:00:02.1000000Z HEAD is now at " + raw_merge[:7] + " Merge " + raw_head + " into " + raw_base,
            ])
            for run in self.runs
        }
        phase3_merge = self.merge_checkout["merge_commit"]["sha"]
        phase3_name = "phase3-backtester-acceptance-" + phase3_merge
        phase3_id = 8000
        artifact_id = 7777
        self.raw_ci_runner_logs[phase3_id] += "\n" + "\n".join([
            "2026-10-17T10:00:03.1000000Z " + json.dumps(
                self.phase3_evidence["index"], separators=(",", ":")),
            "2026-10-17T10:00:04.1000000Z   name: " + phase3_name,
            "2026-10-17T10:00:05.1000000Z Artifact " + phase3_name +
                ".zip successfully finalized. Artifact ID " + str(artifact_id),
            "2026-10-17T10:00:06.1000000Z Artifact " + phase3_name +
                " has been successfully uploaded! Final size is 100 bytes. "
                "Artifact ID is " + str(artifact_id),
            "2026-10-17T10:00:07.1000000Z Artifact download URL: "
                "https://github.com/Dtwosam/FMP/actions/runs/8000/artifacts/" +
                str(artifact_id),
        ])
        self.raw_log_receipts = {
            run_id: {
                "run_id": run_id,
                "job_id": self.jobs[run_id][0]["id"],
                "byte_count": len(text.encode("utf-8")),
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
            for run_id, text in self.raw_ci_runner_logs.items()
        }
        self.ci_bytes = dict(self.original_ci_bytes)

    def verdict(self):
        return review_stacked_draft_evidence(
            self.pr, self.runs, self.jobs, self.compare, self.commit,
            self.tree, self.nodes, self.changed, self.ci_bytes,
            self.full_trees, self.merge_checkout,
            self.runner_checks, self.phase3_evidence,
            self.raw_ci_runner_logs, self.raw_log_receipts)

    def test_consistent_synthetic_bundle_passes_only_source_consistency(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"], result["diagnostics"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_missing_historical_job_fails_the_composite(self):
        self.jobs.pop(8001)
        self.assertFalse(self.verdict()["source_consistency"])

    def test_failed_phase3_step_fails_the_composite(self):
        self.jobs[8000][0]["steps"][1]["conclusion"] = "failure"
        self.assertFalse(self.verdict()["source_consistency"])

    def test_wrong_pr_link_fails_the_composite(self):
        self.runs[1]["pull_requests"][0]["number"] = 10
        self.assertFalse(self.verdict()["source_consistency"])

    def test_two_commit_lineage_fails_the_composite(self):
        self.compare["ahead_by"] = 2
        self.assertFalse(self.verdict()["source_consistency"])

    def test_hidden_change_count_fails_the_composite(self):
        self.pr["changed_files"] = 3
        self.assertFalse(self.verdict()["source_consistency"])

    def test_production_file_path_fails_the_composite(self):
        self.compare["files"][0]["filename"] = "src/fmp/runtime.py"
        self.assertFalse(self.verdict()["source_consistency"])

    def test_symlink_leaf_fails_the_composite(self):
        self.nodes["tests/sample.py"]["mode"] = "120000"
        self.assertFalse(self.verdict()["source_consistency"])

    def test_wrong_git_object_bytes_fail_the_composite(self):
        self.changed["docs/sample.md"] += b"tampered"
        self.assertFalse(self.verdict()["source_consistency"])

    def test_missing_changed_source_bytes_fail_the_composite(self):
        self.changed.pop("tests/sample.py")
        self.assertFalse(self.verdict()["source_consistency"])

    def test_mismatched_commit_tree_sha_fails_the_composite(self):
        self.tree["sha"] = "d" * 40
        self.assertFalse(self.verdict()["source_consistency"])

    def test_modified_historical_ci_workflow_fails_the_composite(self):
        key = ".github/workflows/tests.yml"
        self.ci_bytes[key] += b"\n"
        self.assertFalse(self.verdict()["source_consistency"])

    def test_missing_ci_workflow_source_fails_the_composite(self):
        self.ci_bytes.pop(".github/workflows/tests.yml")
        self.assertFalse(self.verdict()["source_consistency"])

    def test_multiple_failures_accumulate_diagnostics(self):
        self.pr["changed_files"] = 3
        self.nodes["tests/sample.py"]["mode"] = "120000"
        result = self.verdict()
        self.assertFalse(result["source_consistency"])
        self.assertIn("PR_COMPARE_FILE_COUNT_MISMATCH",
                      result["diagnostics"])
        self.assertIn("BLOB_LEAF_TYPE_UNREVIEWED",
                      result["diagnostics"])

    def test_external_os_original_integrity_is_never_inferred(self):
        result = self.verdict()
        self.assertFalse(result["independent_original_os_proof"])

    def test_exclusive_2023_dispatch_admission_is_never_inferred(self):
        result = self.verdict()
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])

    def test_no_combination_of_offline_snapshots_can_grant_run385(self):
        result = self.verdict()
        self.assertFalse(result["can_authorize_annual_run"])
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", result["diagnostics"])

    def test_mismatched_parent_git_tree_sha_rejected(self):
        self.full_trees[self.git_root_tree]["tree"][0]["sha"] = "f"*40
        self.assertIn("TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_missing_subtree_snapshot_rejected(self):
        self.full_trees.pop(self.git_tests_tree)
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_duplicate_root_tree_entry_rejected(self):
        root = self.full_trees[self.git_root_tree]["tree"]
        root.append(dict(root[0]))
        self.assertIn("TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_truncated_child_tree_rejected(self):
        self.full_trees[self.git_docs_tree]["truncated"] = True
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_leaf_tree_sha_not_matched_to_source_rejected(self):
        self.full_trees[self.git_docs_tree]["tree"][0]["sha"] = "f"*40
        self.assertIn("TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_extra_unlinked_tree_snapshot_rejected(self):
        self.full_trees["f"*40] = {
            "sha": "f"*40, "truncated": False, "tree": []}
        self.assertIn("TREE_CHAIN_TREE_SNAPSHOT_INVENTORY_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_flat_regular_leaf_cannot_override_symlinked_chain(self):
        self.full_trees[self.git_tests_tree]["tree"][0]["mode"] = "120000"
        self.assertEqual(self.nodes["tests/sample.py"]["mode"], "100644")
        self.assertIn("TREE_CHAIN_LEAF_NOT_REGULAR_BLOB",
                      self.verdict()["diagnostics"])

    def test_fully_consistent_composite_remains_non_authorizing(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_full_tree_fixtures_rehash_to_their_sha_identifiers(self):
        for sha, obj in self.full_trees.items():
            self.assertEqual(tree_chain.reviewed_git_tree_sha(obj["tree"]), sha)
        self.assertEqual(self.verdict()["diagnostics"], ())

    def test_new_sibling_entry_without_new_sha_fails_composite(self):
        self.full_trees[self.git_docs_tree]["tree"].append({
            "path": "zzz.md", "mode": "100644", "type": "blob",
            "sha": "f"*40})
        self.assertIn("TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_reordered_root_entries_without_rehash_fail_composite(self):
        self.full_trees[self.git_root_tree]["tree"].reverse()
        self.assertIn("TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_merge_checkout_tree_consistency_is_separately_required(self):
        self.assertEqual(self.verdict()["diagnostics"], ())
        self.assertNotEqual(self.merge_checkout["merge_commit"]["sha"],
                            self.pr["head_sha"])

    def test_missing_merge_checkout_snapshot_blocks_composite(self):
        self.merge_checkout = None
        self.assertIn("MERGE_CHECKOUT_SNAPSHOT_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_different_pr_merge_ref_blocks_composite(self):
        self.merge_checkout["merge_ref"]["ref"] = "refs/pull/99/merge"
        self.assertIn("GITHUB_MERGE_REF_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_merge_source_tree_different_from_head_blocks_composite(self):
        self.merge_checkout["merge_commit"]["tree"]["sha"] = "e"*40
        self.assertIn("MERGE_AND_HEAD_FILE_TREE_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_merge_wrong_second_parent_blocks_composite(self):
        self.merge_checkout["merge_commit"]["parents"][1]["sha"] = "d"*40
        self.assertIn("MERGE_COMMIT_PARENT_PAIR_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_runner_claimed_draft_head_checkout_is_not_merge_proof(self):
        self.merge_checkout["checkout_ref"] = "refs/heads/draft"
        self.assertIn("RUNNER_CHECKOUT_REF_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_incorrect_checkout_sha_prefix_blocks_composite(self):
        self.merge_checkout["checkout_sha_prefix"] = "eeeeeee"
        self.assertIn("RUNNER_CHECKOUT_SHA_PREFIX_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_green_composite_is_merge_tree_review_not_annual_consent(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])

    def test_missing_full_runner_fetch_sha_blocks_composite(self):
        self.merge_checkout.pop("checkout_fetch_sha")
        self.assertIn("RUNNER_FETCH_FULL_SHA_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_stale_runner_full_fetch_sha_blocks_composite(self):
        self.merge_checkout["checkout_fetch_sha"] = "d"*40
        self.assertIn("RUNNER_FETCH_FULL_SHA_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_computed_tree_keys_are_not_old_placeholder_identifiers(self):
        self.assertNotEqual(self.git_tests_tree, "d"*40)
        self.assertNotEqual(self.git_docs_tree, "e"*40)
        self.assertNotEqual(self.git_root_tree, "c"*40)
        self.assertEqual(self.verdict()["diagnostics"], ())

    def test_missing_computed_docs_tree_fails_with_diagnostic(self):
        self.full_trees.pop(self.git_docs_tree)
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_missing_computed_root_tree_fails_with_diagnostic(self):
        self.full_trees.pop(self.git_root_tree)
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_both_runner_checkouts_are_now_mandatory(self):
        self.assertEqual(self.verdict()["diagnostics"], ())
        self.assertEqual(set(self.runner_checks), {8000, 8001})

    def test_missing_phase3_runner_checkout_fails_complete_review(self):
        self.runner_checks.pop(8000)
        self.assertIn("phase3-acceptance_RUNNER_LOG_SNAPSHOT_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_different_phase3_full_merge_sha_fails_complete_review(self):
        self.runner_checks[8000]["checkout_fetch_sha"] = "e"*40
        self.assertIn("DUAL_CHECKOUT_TESTED_MERGE_SHA_DIFFERENT",
                      self.verdict()["diagnostics"])

    def test_historical_runner_checkout_must_be_run_id_bound(self):
        self.runner_checks[8001]["run_id"] = 8000
        self.assertIn("tests_RUNNER_LOG_RUN_ASSOCIATION_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_phase3_wrong_pr_checkout_ref_fails_complete_review(self):
        self.runner_checks[8000]["checkout_ref"] = "refs/remotes/pull/999/merge"
        self.assertIn("phase3-acceptance_RUNNER_CHECKOUT_REF_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_duplicate_unreviewed_log_snapshot_fails_complete_review(self):
        self.runner_checks[8888] = dict(self.runner_checks[8000])
        self.assertIn("DUAL_CHECKOUT_RUNNER_LOG_INVENTORY_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_mismatch_in_workflow_id_fails_dual_checkout_review(self):
        self.runs[0]["workflow_id"] = 1
        self.assertIn("phase3-acceptance_WORKFLOW_IDENTITY_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_complete_two_runner_source_consistency_still_non_authorizing(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"], result["diagnostics"])
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_phase3_acceptance_merge_stamp_is_required(self):
        self.assertEqual(self.verdict()["diagnostics"], ())
        self.assertEqual(self.phase3_evidence["index"]["code_commit"],
                         self.merge_checkout["merge_commit"]["sha"])

    def test_missing_phase3_acceptance_snapshot_blocks_composite(self):
        self.phase3_evidence = None
        self.assertIn("PHASE3_ACCEPTANCE_SNAPSHOT_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_acceptance_index_head_sha_instead_of_merge_sha_blocks(self):
        self.phase3_evidence["index"]["code_commit"] = self.pr["head_sha"]
        self.assertIn("PHASE3_INDEX_COMMIT_NOT_TESTED_MERGE",
                      self.verdict()["diagnostics"])

    def test_artifact_named_for_head_not_merge_sha_blocks(self):
        self.phase3_evidence["upload"]["name"] = (
            "phase3-backtester-acceptance-" + self.pr["head_sha"])
        self.assertIn("PHASE3_UPLOAD_MERGE_SHA_NAME_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_wrong_acceptance_artifact_run_id_blocks(self):
        self.phase3_evidence["upload"]["run_id"] = 8001
        self.assertIn("PHASE3_UPLOAD_RUN_ASSOCIATION_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_unfinalized_acceptance_artifact_blocks(self):
        self.phase3_evidence["upload"]["finalized"] = False
        self.assertIn("PHASE3_UPLOAD_NOT_FINALIZED",
                      self.verdict()["diagnostics"])

    def test_missing_acceptance_scenario_blocks(self):
        self.phase3_evidence["index"]["scenarios"].pop()
        self.assertIn("PHASE3_SCENARIO_NAMES_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_dual_checkout_and_acceptance_stamps_never_authorize_run385(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"], result["diagnostics"])
        self.assertFalse(result["can_authorize_annual_run"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])

    def test_complete_raw_both_runner_logs_are_required(self):
        self.assertEqual(self.verdict()["diagnostics"], ())
        self.assertEqual(set(self.raw_ci_runner_logs), {8000, 8001})

    def test_missing_phase3_raw_log_fails_composite(self):
        self.raw_ci_runner_logs.pop(8000)
        self.assertIn("RAW_CI_RUNNER_LOG_INVENTORY_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_missing_historical_raw_log_fails_composite(self):
        self.raw_ci_runner_logs.pop(8001)
        self.assertIn("RAW_CI_RUNNER_LOG_INVENTORY_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_historical_raw_log_different_merge_sha_fails(self):
        log = self.raw_ci_runner_logs[8001]
        # A coherent but wrong *other* merge checkout is valid parse syntax,
        # then fails the independent exact-SHA metadata comparison.
        self.raw_ci_runner_logs[8001] = (
            log.replace("f"*40, "e"*40)
               .replace("fffffff Merge ", "eeeeeee Merge "))
        self.assertIn("RAW_CI_RUNNER_LOG_METADATA_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_phase3_checkout_ref_tampered_in_raw_log_fails(self):
        self.raw_ci_runner_logs[8000] = self.raw_ci_runner_logs[8000].replace(
            "/1649/merge", "/999/merge")
        self.assertIn("RUNNER_LOG_PR_REF_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_raw_phase3_checkout_order_must_be_verified(self):
        log_lines = self.raw_ci_runner_logs[8000].splitlines()
        log_lines[0], log_lines[1] = log_lines[1], log_lines[0]
        self.raw_ci_runner_logs[8000] = "\n".join(log_lines)
        self.assertIn("RUNNER_LOG_ORDER_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_valid_raw_log_cannot_override_wrong_supplied_fetch_sha(self):
        self.runner_checks[8001]["checkout_fetch_sha"] = "e"*40
        self.assertIn("RAW_CI_RUNNER_LOG_METADATA_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_green_raw_log_consistency_does_not_prove_os_or_admission(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["independent_original_os_proof"])

    def test_incoherent_log_sha_abbreviation_fails_at_parser_stage(self):
        log = self.raw_ci_runner_logs[8001]
        self.raw_ci_runner_logs[8001] = log.replace("f"*40, "e"*40)
        diagnostics = self.verdict()["diagnostics"]
        self.assertIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH", diagnostics)
        self.assertIn("RAW_CI_RUNNER_LOG_RECORD_UNREVIEWED", diagnostics)

    def test_coherent_other_merge_log_is_rejected_by_cross_run_proof(self):
        log = self.raw_ci_runner_logs[8000]
        self.raw_ci_runner_logs[8000] = (
            log.replace("f"*40, "e"*40)
               .replace("fffffff Merge ", "eeeeeee Merge "))
        diagnostics = self.verdict()["diagnostics"]
        self.assertIn("RAW_CI_RUNNER_LOG_METADATA_MISMATCH", diagnostics)
        self.assertNotIn("RUNNER_LOG_CHECKOUT_SHA_MISMATCH", diagnostics)

    def test_raw_job_log_receipts_are_composite_prerequisite(self):
        self.assertEqual(self.verdict()["diagnostics"], ())
        self.assertEqual(set(self.raw_log_receipts), {8000, 8001})

    def test_swapped_historical_log_job_id_blocks_composite(self):
        self.raw_log_receipts[8001]["job_id"] = self.jobs[8000][0]["id"]
        self.assertIn("tests_RECEIPT_JOB_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_phase3_log_text_mutation_blocks_digest_check(self):
        self.raw_ci_runner_logs[8000] += "\nInjected unreviewed log line"
        self.assertIn("phase3-acceptance_RECEIPT_DIGEST_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_missing_run_log_receipt_blocks_composite(self):
        self.raw_log_receipts.pop(8000)
        self.assertIn("phase3-acceptance_LOG_RECEIPT_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_extra_unreviewed_log_receipt_blocks_composite(self):
        self.raw_log_receipts[8888] = dict(self.raw_log_receipts[8000])
        self.assertIn("CI_LOG_RECEIPT_INVENTORY_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_log_receipt_job_id_boolean_blocks_composite(self):
        self.raw_log_receipts[8001]["job_id"] = True
        self.assertIn("tests_RECEIPT_JOB_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_log_receipt_digest_mismatch_does_not_confer_dispatch(self):
        self.raw_log_receipts[8001]["text_sha256"] = "a"*64
        result = self.verdict()
        self.assertIn("tests_RECEIPT_DIGEST_MISMATCH",
                      result["diagnostics"])
        self.assertFalse(result["can_authorize_annual_run"])

    def test_consistent_receipts_cannot_prove_provider_authentication(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])

    def test_phase3_index_and_upload_receipt_came_from_raw_log(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertTrue(result["source_consistency"])

    def test_phase3_claimed_index_not_equal_to_log_json_fails(self):
        self.phase3_evidence["index"]["scenarios"][0]["trade_count"] = 99
        self.assertIn("PHASE3_RAW_INDEX_VS_SUPPLIED_EVIDENCE_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_phase3_claimed_artifact_id_not_equal_to_log_fails(self):
        self.phase3_evidence["upload"]["id"] = 9999
        self.assertIn("PHASE3_RAW_UPLOAD_VS_SUPPLIED_EVIDENCE_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_phase3_raw_index_wrong_merge_sha_fails(self):
        self.raw_ci_runner_logs[8000] = self.raw_ci_runner_logs[8000].replace(
            '"code_commit":"f', '"code_commit":"e')
        self.assertIn("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_phase3_raw_index_missing_fails_composite(self):
        lines = self.raw_ci_runner_logs[8000].splitlines()
        self.raw_ci_runner_logs[8000] = "\n".join(
            line for line in lines if '"code_commit":' not in line)
        self.assertIn("PHASE3_RAW_LOG_STAGE_CARDINALITY_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_phase3_raw_artifact_wrong_finalized_id_fails(self):
        self.raw_ci_runner_logs[8000] = self.raw_ci_runner_logs[8000].replace(
            ".zip successfully finalized. Artifact ID 7777",
            ".zip successfully finalized. Artifact ID 9999")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_phase3_raw_unreviewed_download_url_run_fails(self):
        self.raw_ci_runner_logs[8000] = self.raw_ci_runner_logs[8000].replace(
            "/runs/8000/artifacts/", "/runs/9999/artifacts/")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_phase3_raw_log_stale_text_digest_also_fails(self):
        self.raw_ci_runner_logs[8000] += "\nunknown log modification"
        self.assertIn("phase3-acceptance_RECEIPT_DIGEST_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_phase3_synthetic_log_evidence_cannot_authorize_annual(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["can_authorize_annual_run"])
