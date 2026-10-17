"""DEC-1458: offline raw CI log receipt tied to exact GitHub job and run.

Only independently supplied in-memory source-shaped records; no GitHub
network, real annual execution, protected data, security changes or trading.
A self-declared checksum is NOT a signed provider attestation.
"""
from __future__ import annotations

import hashlib
import re
import unittest

EXPECTED = {"phase3-acceptance": "acceptance", "tests": "unit-tests"}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def review_ci_job_log_receipts(runs, jobs_by_run, raw_logs, receipts):
    """Return diagnostics for exact job-id, run-id and raw-text digest linkage."""
    if not all(type(x) is t for x,t in (
            (runs,list), (jobs_by_run,dict), (raw_logs,dict), (receipts,dict))):
        return ("CI_LOG_RECEIPT_INPUT_UNREVIEWED",)
    if len(runs) != 2 or not all(type(r) is dict for r in runs):
        return ("CI_LOG_RECEIPT_RUN_INVENTORY_UNREVIEWED",)
    issues, used = [], []
    for workflow, job_name in EXPECTED.items():
        matches = [r for r in runs if r.get("name") == workflow]
        if len(matches) != 1:
            issues.append(workflow + "_RUN_UNREVIEWED")
            continue
        run = matches[0]
        run_id = run.get("id")
        if type(run_id) is not int or run_id <= 0:
            issues.append(workflow + "_RUN_ID_UNREVIEWED")
            continue
        used.append(run_id)
        jobs = jobs_by_run.get(run_id)
        if (type(jobs) is not list or len(jobs) != 1 or
                type(jobs[0]) is not dict):
            issues.append(workflow + "_JOB_UNREVIEWED")
            continue
        job = jobs[0]
        job_id = job.get("id")
        if (type(job_id) is not int or job_id <= 0 or
                job.get("run_id") != run_id or job.get("name") != job_name):
            issues.append(workflow + "_JOB_IDENTITY_UNREVIEWED")
        record = receipts.get(run_id)
        if type(record) is not dict:
            issues.append(workflow + "_LOG_RECEIPT_UNREVIEWED")
            continue
        if type(record.get("run_id")) is not int or record["run_id"] != run_id:
            issues.append(workflow + "_RECEIPT_RUN_MISMATCH")
        if type(record.get("job_id")) is not int or record["job_id"] != job_id:
            issues.append(workflow + "_RECEIPT_JOB_MISMATCH")
        text = raw_logs.get(run_id)
        if type(text) is not str:
            issues.append(workflow + "_RAW_LOG_UNREVIEWED")
            continue
        try:
            data = text.encode("utf-8", errors="strict")
        except UnicodeEncodeError:
            issues.append(workflow + "_RAW_LOG_ENCODING_UNREVIEWED")
            continue
        if not data:
            issues.append(workflow + "_RAW_LOG_EMPTY")
        if type(record.get("byte_count")) is not int or (
                record["byte_count"] != len(data)):
            issues.append(workflow + "_RECEIPT_LENGTH_MISMATCH")
        supplied = record.get("text_sha256")
        if type(supplied) is not str or SHA256.fullmatch(supplied) is None:
            issues.append(workflow + "_RECEIPT_DIGEST_UNREVIEWED")
        elif supplied != hashlib.sha256(data).hexdigest():
            issues.append(workflow + "_RECEIPT_DIGEST_MISMATCH")
    if len(used) != 2 or len(set(used)) != 2:
        issues.append("CI_LOG_RECEIPT_RUN_IDS_UNREVIEWED")
    if set(jobs_by_run) != set(used) or set(raw_logs) != set(used) or (
            set(receipts) != set(used)):
        issues.append("CI_LOG_RECEIPT_INVENTORY_UNREVIEWED")
    valid_job_ids = [
        jobs_by_run[run_id][0].get("id")
        for run_id in used
        if type(jobs_by_run.get(run_id)) is list and
           len(jobs_by_run[run_id]) == 1 and
           type(jobs_by_run[run_id][0]) is dict
    ]
    if len(valid_job_ids) != 2 or not all(
            type(id_) is int and id_ > 0 for id_ in valid_job_ids) or (
            len(set(valid_job_ids)) != 2):
        issues.append("CI_LOG_RECEIPT_JOB_IDS_UNREVIEWED")
    return tuple(sorted(set(issues)))


class JobLinkedRawLogReceiptsAreNotExecutionConsent(unittest.TestCase):
    def setUp(self):
        self.runs = [
            {"id": 5001, "name": "tests"},
            {"id": 5002, "name": "phase3-acceptance"},
        ]
        self.jobs = {
            5001: [{"id": 6001, "run_id": 5001, "name": "unit-tests"}],
            5002: [{"id": 6002, "run_id": 5002, "name": "acceptance"}],
        }
        self.logs = {
            5001: "2026-10-17T10:01:00.000Z tests checkout fetched SHA\n",
            5002: "2026-10-17T10:01:02.000Z phase3 checkout fetched SHA\n",
        }
        self.receipts = {
            run_id: {
                "run_id": run_id,
                "job_id": self.jobs[run_id][0]["id"],
                "byte_count": len(text.encode("utf-8")),
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
            for run_id, text in self.logs.items()
        }

    def verdict(self):
        return review_ci_job_log_receipts(
            self.runs, self.jobs, self.logs, self.receipts)

    def test_two_correct_job_log_receipts_match(self):
        self.assertEqual(self.verdict(), ())

    def test_swapped_job_receipt_identifiers_are_rejected(self):
        self.receipts[5001]["job_id"] = 6002
        self.assertIn("tests_RECEIPT_JOB_MISMATCH", self.verdict())

    def test_stale_raw_log_text_is_rejected(self):
        self.logs[5002] += "extra log line\n"
        self.assertIn("phase3-acceptance_RECEIPT_DIGEST_MISMATCH",
                      self.verdict())

    def test_changed_log_length_is_rejected(self):
        self.receipts[5001]["byte_count"] += 1
        self.assertIn("tests_RECEIPT_LENGTH_MISMATCH", self.verdict())

    def test_removed_log_receipt_is_rejected(self):
        self.receipts.pop(5001)
        self.assertIn("tests_LOG_RECEIPT_UNREVIEWED", self.verdict())

    def test_unlisted_third_log_is_rejected(self):
        self.logs[9000] = "unreviewed"
        self.assertIn("CI_LOG_RECEIPT_INVENTORY_UNREVIEWED", self.verdict())

    def test_wrong_job_name_is_rejected(self):
        self.jobs[5001][0]["name"] = "unreviewed"
        self.assertIn("tests_JOB_IDENTITY_UNREVIEWED", self.verdict())

    def test_duplicate_job_identifiers_are_rejected(self):
        self.jobs[5002][0]["id"] = 6001
        self.assertIn("CI_LOG_RECEIPT_JOB_IDS_UNREVIEWED", self.verdict())

    def test_wrong_job_run_id_is_rejected(self):
        self.jobs[5001][0]["run_id"] = 5002
        self.assertIn("tests_JOB_IDENTITY_UNREVIEWED", self.verdict())

    def test_empty_raw_log_is_rejected(self):
        self.logs[5002] = ""
        self.assertIn("phase3-acceptance_RAW_LOG_EMPTY", self.verdict())

    def test_missing_raw_log_is_rejected(self):
        self.logs.pop(5002)
        self.assertIn("phase3-acceptance_RAW_LOG_UNREVIEWED", self.verdict())

    def test_boolean_job_identifier_cannot_pass(self):
        self.receipts[5001]["job_id"] = True
        self.assertIn("tests_RECEIPT_JOB_MISMATCH", self.verdict())

    def test_bad_digest_shape_is_rejected(self):
        self.receipts[5002]["text_sha256"] = "bad"
        self.assertIn("phase3-acceptance_RECEIPT_DIGEST_UNREVIEWED",
                      self.verdict())

    def test_illformed_utf8_source_is_rejected(self):
        self.logs[5001] = "\ud800"
        self.assertIn("tests_RAW_LOG_ENCODING_UNREVIEWED", self.verdict())

    def test_malformed_snapshot_is_rejected(self):
        self.assertEqual(review_ci_job_log_receipts([], None, {}, {}),
                         ("CI_LOG_RECEIPT_INPUT_UNREVIEWED",))

    def test_raw_log_checksum_does_not_authenticate_provider(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("GITHUB_LOG_PROVIDER_AUTHENTICATED", self.verdict())

    def test_matching_log_receipt_never_authorizes_run385(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
