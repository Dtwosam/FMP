"""DEC-1480: check the upload-action byte-transfer receipt, source-only.

Read-only, caller-supplied job logs. Does not download the actual artifact
or attest bytes, GitHub log provider, protected annual execution or OS isolation.
"""
from __future__ import annotations

from datetime import datetime
import re
import unittest

import test_dec1462_phase3_raw_log_index_upload_offline as phase3
import test_dec1476_recovered_1698_dual_ci_golden as observed

PREFIX = r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) "
TRANSFER = re.compile(PREFIX + r"Uploaded bytes ([1-9][0-9]*)$")
NAME = phase3.NAME
FINAL = phase3.FINAL


def review_phase3_uploaded_bytes(raw_log, run_id, merge_sha):
    """Audit transfer bytes, final upload size and stage order from the same log."""
    index, receipt, issues = phase3.parse_phase3_log_evidence(
        raw_log, run_id, merge_sha)
    issues = list(issues)
    if index is None or receipt is None or type(raw_log) is not str:
        return tuple(sorted(set(
            issues + ["PHASE3_UPLOAD_BYTE_PROVENANCE_UNREVIEWED"])))
    lines = raw_log.splitlines()
    recognized = [(i, m) for i, line in enumerate(lines)
                  if (m := TRANSFER.fullmatch(line)) is not None]
    candidates = [
        (i, line) for i, line in enumerate(lines)
        if re.match(PREFIX, line) is not None and
           line.split("Z ", 1)[1].startswith("Uploaded bytes ")
    ]
    if len(recognized) != 1:
        issues.append("PHASE3_UPLOADED_BYTES_RECORD_COUNT_UNREVIEWED")
    if len(candidates) != 1 or len(recognized) != len(candidates):
        issues.append("PHASE3_UPLOADED_BYTES_RECORD_UNREVIEWED")
    if len(recognized) != 1:
        return tuple(sorted(set(issues)))
    upload_i, match = recognized[0]
    if int(match.group(2)) != receipt.get("size_bytes"):
        issues.append("PHASE3_UPLOADED_VS_FINAL_SIZE_MISMATCH")
    named = [(i, m) for i, line in enumerate(lines)
             if (m := NAME.fullmatch(line)) is not None]
    finished = [(i, m) for i, line in enumerate(lines)
                if (m := FINAL.fullmatch(line)) is not None]
    if len(named) != 1 or len(finished) != 1:
        issues.append("PHASE3_UPLOAD_BYTES_STAGE_UNREVIEWED")
        return tuple(sorted(set(issues)))
    named_i, named_match = named[0]
    final_i, final_match = finished[0]
    if not named_i < upload_i < final_i:
        issues.append("PHASE3_UPLOAD_BYTES_STAGE_ORDER_UNREVIEWED")
    try:
        time_texts = [named_match.group(1), match.group(1),
                      final_match.group(1)]
        stamps = [
            datetime.fromisoformat(t.replace("Z", "+00:00"))
            for t in time_texts
        ]
    except (ValueError, OverflowError, TypeError):
        issues.append("PHASE3_UPLOAD_BYTES_TIMESTAMP_UNREVIEWED")
    else:
        if not stamps[0] < stamps[1] < stamps[2]:
            issues.append("PHASE3_UPLOAD_BYTES_TIMESTAMP_ORDER_UNREVIEWED")
    return tuple(sorted(set(issues)))


class ObservedUnprotectedPhase3TransferCountIsNotArtifactAttestation(unittest.TestCase):
    def setUp(self):
        self.log = list(observed.PHASE3_LINES)
        self.receipt = (
            "2026-10-17T11:49:18.3192715Z Uploaded bytes 23491")
        self.log.insert(5, self.receipt)

    def verdict(self):
        return review_phase3_uploaded_bytes(
            "\n".join(self.log), observed.PHASE3_RUN, observed.MERGE)

    def test_real_1698_uploaded_bytes_equal_final_size(self):
        self.assertEqual(self.verdict(), ())

    def test_missing_transfer_count_rejected(self):
        self.log.pop(5)
        self.assertIn("PHASE3_UPLOADED_BYTES_RECORD_COUNT_UNREVIEWED",
                      self.verdict())

    def test_duplicate_transfer_count_rejected(self):
        self.log.insert(6, self.receipt)
        self.assertIn("PHASE3_UPLOADED_BYTES_RECORD_COUNT_UNREVIEWED",
                      self.verdict())

    def test_transfer_count_differs_from_final_upload_size_rejected(self):
        self.log[5] = self.log[5].replace("23491", "23490")
        self.assertIn("PHASE3_UPLOADED_VS_FINAL_SIZE_MISMATCH",
                      self.verdict())

    def test_malformed_transfer_count_rejected(self):
        self.log[5] = self.log[5].replace("23491", "NaN")
        self.assertIn("PHASE3_UPLOADED_BYTES_RECORD_UNREVIEWED",
                      self.verdict())

    def test_boolean_or_zero_transfer_count_rejected(self):
        self.log[5] = self.log[5].replace("23491", "0")
        self.assertIn("PHASE3_UPLOADED_BYTES_RECORD_COUNT_UNREVIEWED",
                      self.verdict())

    def test_transfer_record_after_finalization_rejected(self):
        self.log[5], self.log[6] = self.log[6], self.log[5]
        self.assertIn("PHASE3_UPLOAD_BYTES_STAGE_ORDER_UNREVIEWED",
                      self.verdict())

    def test_transfer_timestamp_earlier_than_artifact_name_rejected(self):
        self.log[5] = self.log[5].replace(
            "11:49:18.3192715Z", "11:49:17.3192715Z")
        self.assertIn("PHASE3_UPLOAD_BYTES_TIMESTAMP_ORDER_UNREVIEWED",
                      self.verdict())

    def test_invalid_calendar_transfer_timestamp_rejected(self):
        self.log[5] = self.log[5].replace("2026-10-17", "2026-99-17")
        self.assertIn("PHASE3_UPLOAD_BYTES_TIMESTAMP_UNREVIEWED",
                      self.verdict())

    def test_wrong_artifact_run_still_rejected_by_original_parser(self):
        self.log[-1] = self.log[-1].replace(
            "/runs/39030113556/artifacts/", "/runs/39030113645/artifacts/")
        self.assertIn("PHASE3_RAW_UPLOAD_ID_RUN_MISMATCH", self.verdict())

    def test_wrong_source_merge_still_rejected(self):
        self.log[3] = self.log[3].replace(observed.MERGE, observed.HEAD)
        self.assertIn("PHASE3_RAW_INDEX_IDENTITY_UNREVIEWED", self.verdict())

    def test_valid_transfer_receipt_never_proves_original_or_dispatch(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
