"""DEC-1477: bind CI checkout log timestamps to completed workflow-run bounds.

This is source consistency over caller-supplied metadata, not an authenticated
GitHub provider/job attestation or protected annual-run authorization.
"""
from __future__ import annotations
from test_dec1481_exact_utc_nanosecond_source_time import reviewed_utc_nanoseconds
import re
import unittest

UTC_TIME = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\Z")
PREFIX = re.compile(
    r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z) ")
REQUIRED = frozenset(("tests", "phase3-acceptance"))


def _utc(value):
    return reviewed_utc_nanoseconds(value)


def review_both_run_log_windows(run_snapshots, logs_by_run_id):
    """Require two complete-success run envelopes bracketing raw log lines."""
    if (type(run_snapshots) is not list or type(logs_by_run_id) is not dict
            or not all(type(run) is dict for run in run_snapshots)):
        return ("CI_RUN_WINDOW_INPUT_UNREVIEWED",)
    issues, ids = [], []
    names = [run.get("name") for run in run_snapshots]
    if (len(names) != 2 or not all(type(n) is str for n in names)
            or any(names.count(required) != 1 for required in REQUIRED)):
        issues.append("CI_RUN_WINDOW_INVENTORY_UNREVIEWED")
    for name in sorted(REQUIRED):
        found = [r for r in run_snapshots if r.get("name") == name]
        if len(found) != 1:
            issues.append(name + "_RUN_CARDINALITY_UNREVIEWED")
            continue
        run = found[0]
        run_id = run.get("id")
        if type(run_id) is not int or run_id <= 0:
            issues.append(name + "_RUN_ID_UNREVIEWED")
            continue
        ids.append(run_id)
        if (run.get("status") != "completed" or
                run.get("conclusion") != "success"):
            issues.append(name + "_RUN_NOT_COMPLETED_SUCCESS")
        created = _utc(run.get("created_at"))
        started = _utc(run.get("run_started_at"))
        updated = _utc(run.get("updated_at"))
        if any(t is None for t in (created, started, updated)):
            issues.append(name + "_RUN_WINDOW_TIMESTAMP_UNREVIEWED")
        elif not created <= started <= updated:
            issues.append(name + "_RUN_WINDOW_TIME_ORDER_UNREVIEWED")
        text = logs_by_run_id.get(run_id)
        if type(text) is not str or not text:
            issues.append(name + "_RAW_LOG_UNREVIEWED")
            continue
        for line in text.splitlines():
            match = PREFIX.match(line)
            if match is None:
                issues.append(name + "_LOG_LINE_TIMESTAMP_UNREVIEWED")
                continue
            stamp = _utc(match.group(1))
            if stamp is None:
                issues.append(name + "_LOG_TIMESTAMP_CALENDAR_UNREVIEWED")
            elif started is not None and updated is not None and (
                    stamp < started or stamp > updated):
                issues.append(name + "_LOG_OUTSIDE_RUN_WINDOW")
    if len(ids) != 2 or len(set(ids)) != 2:
        issues.append("CI_RUN_WINDOW_IDS_NOT_UNIQUE")
    if set(logs_by_run_id) != set(ids):
        issues.append("CI_RUN_WINDOW_LOG_INVENTORY_UNREVIEWED")
    return tuple(sorted(set(issues)))


class ObservedRecoveredCIWorkflowRunWindows(unittest.TestCase):
    def setUp(self):
        self.runs = [
            {"name": "tests", "id": 39030113645,
             "created_at": "2026-10-17T11:48:44Z",
             "run_started_at": "2026-10-17T11:48:44Z",
             "updated_at": "2026-10-17T12:02:06Z",
             "status": "completed", "conclusion": "success"},
            {"name": "phase3-acceptance", "id": 39030113556,
             "created_at": "2026-10-17T11:48:44Z",
             "run_started_at": "2026-10-17T11:48:44Z",
             "updated_at": "2026-10-17T11:49:22Z",
             "status": "completed", "conclusion": "success"},
        ]
        self.logs = {
            39030113645: "\n".join([
                "2026-10-17T11:49:01.4210120Z [command]/usr/bin/git fetch checkout source",
                "2026-10-17T11:49:02.7746804Z HEAD is now at 0cf9a4b",
                "2026-10-17T12:02:01.5069070Z OK (skipped=702)",
            ]),
            39030113556: "\n".join([
                "2026-10-17T11:48:59.9084684Z [command]/usr/bin/git fetch checkout source",
                "2026-10-17T11:49:01.0287628Z HEAD is now at 0cf9a4b",
                "2026-10-17T11:49:18.7726359Z Artifact download URL: reviewed",
            ]),
        }

    def verdict(self):
        return review_both_run_log_windows(self.runs, self.logs)

    def test_observed_1698_run_metadata_brackets_log_lines(self):
        self.assertEqual(self.verdict(), ())

    def test_historical_log_prior_to_run_start_is_rejected(self):
        self.logs[39030113645] = (
            "2026-10-17T11:40:01.4210120Z earlier than run started")
        self.assertIn("tests_LOG_OUTSIDE_RUN_WINDOW", self.verdict())

    def test_phase3_log_after_run_update_is_rejected(self):
        self.logs[39030113556] += (
            "\n2026-10-17T11:55:00.000Z later than completed run")
        self.assertIn("phase3-acceptance_LOG_OUTSIDE_RUN_WINDOW",
                      self.verdict())

    def test_stale_updated_at_before_run_start_is_rejected(self):
        self.runs[0]["updated_at"] = "2026-10-17T11:00:00Z"
        self.assertIn("tests_RUN_WINDOW_TIME_ORDER_UNREVIEWED",
                      self.verdict())

    def test_created_at_after_started_at_is_rejected(self):
        self.runs[0]["created_at"] = "2026-10-17T11:49:00Z"
        self.assertIn("tests_RUN_WINDOW_TIME_ORDER_UNREVIEWED",
                      self.verdict())

    def test_noncalendar_run_start_is_rejected(self):
        self.runs[1]["run_started_at"] = "2026-99-17T11:48:44Z"
        self.assertIn("phase3-acceptance_RUN_WINDOW_TIMESTAMP_UNREVIEWED",
                      self.verdict())

    def test_offset_without_reviewed_utc_z_shape_is_rejected(self):
        self.runs[0]["created_at"] = "2026-10-17T12:48:44+01:00"
        self.assertIn("tests_RUN_WINDOW_TIMESTAMP_UNREVIEWED",
                      self.verdict())

    def test_wrong_calendar_date_in_raw_line_is_rejected(self):
        self.logs[39030113556] = (
            "2026-10-99T11:49:00.000Z invalid calendar")
        self.assertIn("phase3-acceptance_LOG_TIMESTAMP_CALENDAR_UNREVIEWED",
                      self.verdict())

    def test_bare_log_line_is_not_proven_run_timing(self):
        self.logs[39030113645] += "\nunknown unprefixed line"
        self.assertIn("tests_LOG_LINE_TIMESTAMP_UNREVIEWED", self.verdict())

    def test_failed_historical_run_does_not_pass(self):
        self.runs[0]["conclusion"] = "failure"
        self.assertIn("tests_RUN_NOT_COMPLETED_SUCCESS", self.verdict())

    def test_in_progress_phase3_run_does_not_pass(self):
        self.runs[1]["status"] = "in_progress"
        self.assertIn("phase3-acceptance_RUN_NOT_COMPLETED_SUCCESS",
                      self.verdict())

    def test_missing_phase3_raw_log_is_rejected(self):
        self.logs.pop(39030113556)
        self.assertIn("phase3-acceptance_RAW_LOG_UNREVIEWED", self.verdict())

    def test_extra_unreviewed_run_log_is_rejected(self):
        self.logs[123] = "2026-10-17T11:49:00Z unreviewed"
        self.assertIn("CI_RUN_WINDOW_LOG_INVENTORY_UNREVIEWED",
                      self.verdict())

    def test_bool_run_id_is_rejected(self):
        self.runs[0]["id"] = True
        self.assertIn("tests_RUN_ID_UNREVIEWED", self.verdict())

    def test_unhashable_run_id_fails_closed(self):
        self.runs[1]["id"] = {"run": 39030113556}
        self.assertIn("phase3-acceptance_RUN_ID_UNREVIEWED",
                      self.verdict())

    def test_duplicate_run_id_is_rejected(self):
        self.runs[1]["id"] = 39030113645
        self.assertIn("CI_RUN_WINDOW_IDS_NOT_UNIQUE", self.verdict())

    def test_missing_named_workflow_is_rejected(self):
        self.runs[0]["name"] = "other-workflow"
        self.assertIn("CI_RUN_WINDOW_INVENTORY_UNREVIEWED", self.verdict())

    def test_bad_snapshot_shape_is_rejected(self):
        self.assertEqual(review_both_run_log_windows(None, {}),
                         ("CI_RUN_WINDOW_INPUT_UNREVIEWED",))

    def test_run_time_envelope_is_not_an_authenticated_job_witness(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("GITHUB_JOB_OS_ATTESTED", self.verdict())

    def test_run_window_consistency_never_authorizes_annual_run(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())

    def test_log_line_within_submicrosecond_run_window_passes(self):
        self.runs[0].update({
            "created_at": "2026-10-17T11:49:00Z",
            "run_started_at": "2026-10-17T11:49:01.0000001Z",
            "updated_at": "2026-10-17T11:49:01.0000003Z",
        })
        self.logs[39030113645] = "2026-10-17T11:49:01.0000002Z reviewed"
        self.assertEqual(self.verdict(), ())

    def test_log_line_exceeding_run_end_by_hundred_ns_fails(self):
        self.runs[0].update({
            "created_at": "2026-10-17T11:49:00Z",
            "run_started_at": "2026-10-17T11:49:01.0000001Z",
            "updated_at": "2026-10-17T11:49:01.0000003Z",
        })
        self.logs[39030113645] = "2026-10-17T11:49:01.0000004Z unreviewed"
        self.assertIn("tests_LOG_OUTSIDE_RUN_WINDOW", self.verdict())
