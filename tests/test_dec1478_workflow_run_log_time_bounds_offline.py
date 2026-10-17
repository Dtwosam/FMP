"""DEC-1478: workflow-run window bounds on caller-supplied CI log timestamps.

Pure offline run/log consistency, not a signed GitHub provenance assertion,
job-level clock attestation, protected annual dispatch, or original data access.
"""
from __future__ import annotations

from datetime import datetime
import re
import unittest

import test_dec1422_offline_exact_head_ci_evidence_review as policy
import test_dec1476_recovered_1698_dual_ci_golden as observed

RUN_TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")
LOG_TIME = re.compile(
    r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) ")


def _parse_utc(timestamp):
    if type(timestamp) is not str:
        return None
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except (ValueError, OverflowError, TypeError):
        return None


def review_two_ci_runner_log_windows(runs, logs_by_run):
    """Require independently supplied first-attempt run lifecycle bounds."""
    if (type(runs) is not list or type(logs_by_run) is not dict or
            len(runs) != 2 or not all(type(r) is dict for r in runs)):
        return ("CI_RUN_WINDOW_INPUT_UNREVIEWED",)
    reasons, ids, head_shas = [], [], []
    for name in policy.REQUIRED:
        matched = [r for r in runs if r.get("name") == name]
        if len(matched) != 1:
            reasons.append(name + "_RUN_WINDOW_INVENTORY_UNREVIEWED")
            continue
        r = matched[0]
        run_id = r.get("id")
        if type(run_id) is not int or run_id <= 0:
            reasons.append(name + "_RUN_WINDOW_ID_UNREVIEWED")
            continue
        ids.append(run_id)
        if r.get("event") != "pull_request":
            reasons.append(name + "_RUN_WINDOW_EVENT_UNREVIEWED")
        head_sha = r.get("head_sha")
        if (type(head_sha) is not str or
                re.fullmatch(r"[0-9a-f]{40}", head_sha) is None):
            reasons.append(name + "_RUN_WINDOW_HEAD_SHA_UNREVIEWED")
        else:
            head_shas.append(head_sha)
        expected_id, expected_path = policy.WORKFLOWS[name]
        if (type(r.get("workflow_id")) is not int or
                r.get("workflow_id") != expected_id or
                r.get("path") != expected_path or
                r.get("status") != "completed" or
                r.get("conclusion") != "success" or
                type(r.get("run_attempt")) is not int or
                r["run_attempt"] != 1):
            reasons.append(name + "_RUN_WINDOW_IDENTITY_UNREVIEWED")
        stamps = [r.get(k) for k in (
            "created_at", "run_started_at", "updated_at")]
        if any(type(v) is not str or RUN_TIME.fullmatch(v) is None
               for v in stamps):
            reasons.append(name + "_RUN_WINDOW_TIMESTAMP_UNREVIEWED")
            continue
        times = [_parse_utc(v) for v in stamps]
        if any(v is None for v in times):
            reasons.append(name + "_RUN_WINDOW_TIMESTAMP_UNREVIEWED")
            continue
        created, started, updated = times
        if not created <= started <= updated:
            reasons.append(name + "_RUN_WINDOW_ORDER_UNREVIEWED")
        raw = logs_by_run.get(run_id)
        if type(raw) is not str or not raw:
            reasons.append(name + "_RUN_WINDOW_LOG_UNREVIEWED")
            continue
        seen = 0
        for line in raw.splitlines():
            if not re.match(r"^\d{4}-\d{2}-\d{2}T", line):
                continue
            match = LOG_TIME.match(line)
            if match is None:
                reasons.append(name + "_RUN_WINDOW_LOG_TIMESTAMP_UNREVIEWED")
                continue
            at = _parse_utc(match.group(1))
            if at is None:
                reasons.append(name + "_RUN_WINDOW_LOG_TIMESTAMP_UNREVIEWED")
                continue
            seen += 1
            # A created-but-not-yet-started workflow cannot have produced
            # the checked-out source log line.
            if not started <= at <= updated:
                reasons.append(name + "_RUN_WINDOW_LOG_OUTSIDE_RUN")
        if not seen:
            reasons.append(name + "_RUN_WINDOW_LOG_TIMESTAMPS_MISSING")
    if len(ids) != 2 or len(set(ids)) != 2:
        reasons.append("CI_RUN_WINDOW_REQUIRED_IDS_UNREVIEWED")
    if len(head_shas) != 2 or len(set(head_shas)) != 1:
        reasons.append("CI_RUN_WINDOW_HEAD_SHA_AFFINITY_UNREVIEWED")
    if set(logs_by_run) != set(ids):
        reasons.append("CI_RUN_WINDOW_LOG_INVENTORY_UNREVIEWED")
    return tuple(sorted(set(reasons)))


class RealRecoveredCiWorkflowWindowsAreNotProtectedRunPermission(unittest.TestCase):
    def setUp(self):
        self.runs = [
            {
                "name": "tests", "id": observed.HISTORICAL_RUN,
                "workflow_id": policy.WORKFLOWS["tests"][0],
                "path": policy.WORKFLOWS["tests"][1],
                "status": "completed", "conclusion": "success",
                "run_attempt": 1, "event": "pull_request",
                "head_sha": observed.HEAD,
                "created_at": "2026-10-17T11:48:44Z",
                "run_started_at": "2026-10-17T11:48:44Z",
                "updated_at": "2026-10-17T12:02:06Z",
            },
            {
                "name": "phase3-acceptance", "id": observed.PHASE3_RUN,
                "workflow_id": policy.WORKFLOWS["phase3-acceptance"][0],
                "path": policy.WORKFLOWS["phase3-acceptance"][1],
                "status": "completed", "conclusion": "success",
                "run_attempt": 1, "event": "pull_request",
                "head_sha": observed.HEAD,
                "created_at": "2026-10-17T11:48:44Z",
                "run_started_at": "2026-10-17T11:48:44Z",
                "updated_at": "2026-10-17T11:49:22Z",
            },
        ]
        self.logs = {
            observed.HISTORICAL_RUN: "\n".join(observed.HISTORICAL_LINES),
            observed.PHASE3_RUN: "\n".join(observed.PHASE3_LINES),
        }

    def verdict(self):
        return review_two_ci_runner_log_windows(self.runs, self.logs)

    def test_real_1698_both_ci_logs_within_actual_run_lifecycle(self):
        self.assertEqual(self.verdict(), ())

    def test_historical_log_predates_run_created_at(self):
        self.runs[0]["created_at"] = "2026-10-17T11:49:50Z"
        self.runs[0]["run_started_at"] = "2026-10-17T11:49:50Z"
        self.assertIn("tests_RUN_WINDOW_LOG_OUTSIDE_RUN", self.verdict())

    def test_phase3_timestamp_after_updated_at_rejected(self):
        self.runs[1]["updated_at"] = "2026-10-17T11:49:00Z"
        self.assertIn("phase3-acceptance_RUN_WINDOW_LOG_OUTSIDE_RUN",
                      self.verdict())

    def test_phase3_run_updated_before_started_rejected(self):
        self.runs[1]["updated_at"] = "2026-10-17T11:48:00Z"
        self.assertIn("phase3-acceptance_RUN_WINDOW_ORDER_UNREVIEWED",
                      self.verdict())

    def test_nonexistent_calendar_run_month_rejected(self):
        self.runs[0]["created_at"] = "2026-99-17T11:48:44Z"
        self.assertIn("tests_RUN_WINDOW_TIMESTAMP_UNREVIEWED",
                      self.verdict())

    def test_bad_timestamped_line_rejected_not_ignored(self):
        self.logs[observed.PHASE3_RUN] += (
            "\n2026-99-17T11:49:00.123Z malformed CI runner timestamp")
        self.assertIn("phase3-acceptance_RUN_WINDOW_LOG_TIMESTAMP_UNREVIEWED",
                      self.verdict())

    def test_timestamped_record_from_other_day_fails(self):
        self.logs[observed.HISTORICAL_RUN] += (
            "\n2026-10-16T11:49:00.123Z stale CI trace")
        self.assertIn("tests_RUN_WINDOW_LOG_OUTSIDE_RUN", self.verdict())

    def test_extra_unreviewed_third_run_log_rejected(self):
        self.logs[12345] = self.logs[observed.PHASE3_RUN]
        self.assertIn("CI_RUN_WINDOW_LOG_INVENTORY_UNREVIEWED", self.verdict())

    def test_duplicate_run_id_cannot_prove_two_run_windows(self):
        self.runs[1]["id"] = self.runs[0]["id"]
        self.assertIn("CI_RUN_WINDOW_REQUIRED_IDS_UNREVIEWED",
                      self.verdict())

    def test_bool_run_id_is_not_exact_identity(self):
        self.runs[1]["id"] = True
        self.assertIn("phase3-acceptance_RUN_WINDOW_ID_UNREVIEWED",
                      self.verdict())

    def test_second_attempt_requires_separate_review(self):
        self.runs[1]["run_attempt"] = 2
        self.assertIn("phase3-acceptance_RUN_WINDOW_IDENTITY_UNREVIEWED",
                      self.verdict())

    def test_false_success_run_cannot_claim_time_window(self):
        self.runs[0]["conclusion"] = "failure"
        self.assertIn("tests_RUN_WINDOW_IDENTITY_UNREVIEWED", self.verdict())

    def test_empty_historical_log_does_not_supply_timestamps(self):
        self.logs[observed.HISTORICAL_RUN] = ""
        self.assertIn("tests_RUN_WINDOW_LOG_UNREVIEWED", self.verdict())

    def test_read_only_model_never_grants_protected_run385(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())

    def test_checkout_log_before_run_started_but_after_created_rejected(self):
        self.runs[0]["run_started_at"] = "2026-10-17T11:49:30Z"
        self.assertIn("tests_RUN_WINDOW_LOG_OUTSIDE_RUN", self.verdict())

    def test_phase3_index_log_before_run_started_but_after_created_rejected(self):
        self.runs[1]["run_started_at"] = "2026-10-17T11:49:20Z"
        self.assertIn("phase3-acceptance_RUN_WINDOW_LOG_OUTSIDE_RUN",
                      self.verdict())

    def test_wrong_event_cannot_claim_pr_runner_window(self):
        self.runs[0]["event"] = "workflow_dispatch"
        self.assertIn("tests_RUN_WINDOW_EVENT_UNREVIEWED", self.verdict())

    def test_two_different_run_head_shas_cannot_share_pr_source_review(self):
        self.runs[1]["head_sha"] = "f"*40
        self.assertIn("CI_RUN_WINDOW_HEAD_SHA_AFFINITY_UNREVIEWED",
                      self.verdict())

    def test_nonhex_workflow_head_sha_fails_closed(self):
        self.runs[0]["head_sha"] = "not-a-commit"
        self.assertIn("tests_RUN_WINDOW_HEAD_SHA_UNREVIEWED", self.verdict())
        self.assertIn("CI_RUN_WINDOW_HEAD_SHA_AFFINITY_UNREVIEWED",
                      self.verdict())

    def test_missing_phase3_head_sha_fails_closed(self):
        self.runs[1].pop("head_sha")
        self.assertIn("phase3-acceptance_RUN_WINDOW_HEAD_SHA_UNREVIEWED",
                      self.verdict())

    def test_valid_two_run_head_affinity_never_confers_annual_permission(self):
        self.assertEqual(self.runs[0]["head_sha"], self.runs[1]["head_sha"])
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
