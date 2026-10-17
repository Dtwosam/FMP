"""DEC-1479: raw CI job logs must show their distinct reviewed work roles.

Offline source-shape checks only; untrusted text is not provider attestation
or protected annual dispatch approval.
"""
from __future__ import annotations
import re
import unittest

TS = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z "
UNITS = re.compile(TS + r"##\[group\]Run python -m unittest discover -s tests -p '[^']+' -v$")
RAN = re.compile(TS + r"Ran ([0-9]+) tests in [0-9]+(?:\.[0-9]+)?s$")
OK = re.compile(TS + r"OK(?: \(skipped=[0-9]+\))?$")
GEN = re.compile(TS + r"##\[group\]Run rm -rf \.phase3-acceptance$")
INDEX = re.compile(TS + r'\{"code_commit":"[0-9a-f]{40}".*\}$')
UPLOAD = re.compile(TS + r"##\[group\]Run actions/upload-artifact@v[0-9]+$")
FINAL = re.compile(TS + r"Artifact phase3-backtester-acceptance-[0-9a-f]{40}"
                   r"\.zip successfully finalized\. Artifact ID [1-9][0-9]*$")
REQUIRED = ("tests", "phase3-acceptance")


def review_ci_workflow_log_roles(runs, raw_logs):
    if (type(runs) is not list or type(raw_logs) is not dict
            or not all(type(r) is dict for r in runs)):
        return ("CI_LOG_ROLE_INPUT_UNREVIEWED",)
    issues, ids = [], []
    if len(runs) != 2:
        issues.append("CI_LOG_ROLE_RUN_INVENTORY_UNREVIEWED")
    for name in REQUIRED:
        matches = [r for r in runs if r.get("name") == name]
        if len(matches) != 1:
            issues.append(name + "_RUN_CARDINALITY_UNREVIEWED")
            continue
        run_id = matches[0].get("id")
        if type(run_id) is not int or run_id <= 0:
            issues.append(name + "_RUN_ID_UNREVIEWED")
            continue
        ids.append(run_id)
        raw = raw_logs.get(run_id)
        if type(raw) is not str or not raw:
            issues.append(name + "_RAW_LOG_UNREVIEWED")
            continue
        lines = raw.splitlines()
        if name == "tests":
            starts = [i for i,l in enumerate(lines) if UNITS.fullmatch(l)]
            totals = [(i,int(m.group(1))) for i,l in enumerate(lines)
                      if (m := RAN.fullmatch(l)) is not None
                      and int(m.group(1)) >= 5000]
            ok = [i for i,l in enumerate(lines) if OK.fullmatch(l)]
            if (not starts or len(totals) != 1 or not ok
                    or not min(starts) < totals[0][0] < max(ok)):
                issues.append("tests_FULL_SUITE_COMPLETION_UNREVIEWED")
            if any("Z FAILED (" in l for l in lines):
                issues.append("tests_FAILURE_SUMMARY_PRESENT")
            if any(FINAL.fullmatch(l) for l in lines):
                issues.append("tests_PHASE3_ARTIFACT_IN_HISTORICAL_LOG")
        else:
            seq = [
                [i for i,l in enumerate(lines) if rx.fullmatch(l)]
                for rx in (GEN, INDEX, UPLOAD, FINAL)
            ]
            if (any(len(group) != 1 for group in seq)
                    or not all(seq[i][0] < seq[i+1][0]
                               for i in range(3))):
                issues.append("phase3-acceptance_UPLOAD_SEQUENCE_UNREVIEWED")
            if any(RAN.fullmatch(l) for l in lines):
                issues.append("phase3-acceptance_HISTORICAL_SUMMARY_IN_PHASE3")
    if len(ids) != 2 or len(set(ids)) != 2:
        issues.append("CI_LOG_ROLE_RUN_IDS_UNREVIEWED")
    if set(raw_logs) != set(ids):
        issues.append("CI_LOG_ROLE_LOG_INVENTORY_UNREVIEWED")
    return tuple(sorted(set(issues)))


class ActualSuccessfulCIJobRolesAreDistinct(unittest.TestCase):
    def setUp(self):
        self.runs = [{"name":"tests","id":39030113645},
                     {"name":"phase3-acceptance","id":39030113556}]
        self.logs = {
            39030113645: "\n".join([
                "2026-10-17T11:49:15.1531187Z ##[group]Run python -m unittest discover -s tests -p 'test_a.py' -v",
                "2026-10-17T12:02:01.5068915Z Ran 6867 tests in 724.350s",
                "2026-10-17T12:02:01.5069070Z OK (skipped=702)",
            ]),
            39030113556: "\n".join([
                "2026-10-17T11:49:17.1861780Z ##[group]Run rm -rf .phase3-acceptance",
                '2026-10-17T11:49:17.3011567Z {"code_commit":"' +
                "0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9" + '"}',
                "2026-10-17T11:49:17.3673726Z ##[group]Run actions/upload-artifact@v6",
                "2026-10-17T11:49:18.7721136Z Artifact phase3-backtester-acceptance-" +
                "0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9" +
                ".zip successfully finalized. Artifact ID 12100346157",
            ]),
        }

    def verdict(self):
        return review_ci_workflow_log_roles(self.runs, self.logs)

    def test_observed_1698_critical_log_roles_match(self):
        self.assertEqual(self.verdict(), ())

    def test_only_smoke_tests_not_historical_suite(self):
        self.logs[39030113645] = self.logs[39030113645].replace(
            "6867 tests", "8 tests")
        self.assertIn("tests_FULL_SUITE_COMPLETION_UNREVIEWED", self.verdict())

    def test_unverified_historical_result_cannot_pass(self):
        self.logs[39030113645] = self.logs[39030113645].replace(
            "OK (skipped=702)", "not completed")
        self.assertIn("tests_FULL_SUITE_COMPLETION_UNREVIEWED", self.verdict())

    def test_history_log_failure_summary_cannot_pass(self):
        self.logs[39030113645] += "\n2026-10-17T12:02:02.000Z FAILED (errors=1)"
        self.assertIn("tests_FAILURE_SUMMARY_PRESENT", self.verdict())

    def test_historical_log_missing_discovery_fails(self):
        self.logs[39030113645] = "\n".join(
            self.logs[39030113645].splitlines()[1:])
        self.assertIn("tests_FULL_SUITE_COMPLETION_UNREVIEWED", self.verdict())

    def test_phase3_generation_stage_missing_fails(self):
        self.logs[39030113556] = "\n".join(
            self.logs[39030113556].splitlines()[1:])
        self.assertIn("phase3-acceptance_UPLOAD_SEQUENCE_UNREVIEWED",
                      self.verdict())

    def test_phase3_upload_action_missing_fails(self):
        lines = self.logs[39030113556].splitlines()
        lines.pop(2)
        self.logs[39030113556] = "\n".join(lines)
        self.assertIn("phase3-acceptance_UPLOAD_SEQUENCE_UNREVIEWED",
                      self.verdict())

    def test_phase3_finalization_before_upload_stage_fails(self):
        lines = self.logs[39030113556].splitlines()
        lines[2], lines[3] = lines[3], lines[2]
        self.logs[39030113556] = "\n".join(lines)
        self.assertIn("phase3-acceptance_UPLOAD_SEQUENCE_UNREVIEWED",
                      self.verdict())

    def test_historical_artifact_in_wrong_job_fails(self):
        self.logs[39030113645] += "\n" + self.logs[39030113556].splitlines()[-1]
        self.assertIn("tests_PHASE3_ARTIFACT_IN_HISTORICAL_LOG",
                      self.verdict())

    def test_phase3_log_historical_summary_fails(self):
        self.logs[39030113556] += "\n" + self.logs[39030113645].splitlines()[1]
        self.assertIn("phase3-acceptance_HISTORICAL_SUMMARY_IN_PHASE3",
                      self.verdict())

    def test_swapped_job_logs_fail_both_roles(self):
        self.logs[39030113645], self.logs[39030113556] = (
            self.logs[39030113556], self.logs[39030113645])
        self.assertIn("tests_FULL_SUITE_COMPLETION_UNREVIEWED",
                      self.verdict())
        self.assertIn("phase3-acceptance_UPLOAD_SEQUENCE_UNREVIEWED",
                      self.verdict())

    def test_wrong_run_id_shape_fails_closed(self):
        self.runs[0]["id"] = [39030113645]
        self.assertIn("tests_RUN_ID_UNREVIEWED", self.verdict())

    def test_missing_raw_log_fails(self):
        self.logs.pop(39030113556)
        self.assertIn("phase3-acceptance_RAW_LOG_UNREVIEWED", self.verdict())

    def test_role_consistency_does_not_authorize_2023_annual(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
