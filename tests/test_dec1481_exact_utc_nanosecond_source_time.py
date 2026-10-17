"""DEC-1481: exact nanosecond UTC stage timestamps, no float precision loss.

Purely offline source-evidence helper, never an OS or one-shot protected
annual-execution authorization witness.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re
import unittest

REVIEWED_UTC = re.compile(
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?Z\Z")
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
BILLION = 1_000_000_000


def reviewed_utc_nanoseconds(value):
    """Return integer epoch nanoseconds for exact reviewed UTC Z strings."""
    if type(value) is not str:
        return None
    match = REVIEWED_UTC.fullmatch(value)
    if match is None:
        return None
    stamp, fraction = match.groups()
    try:
        second = datetime.fromisoformat(stamp + "+00:00")
    except (ValueError, OverflowError):
        return None
    offset = second - EPOCH
    whole_seconds = offset.days * 86400 + offset.seconds
    return whole_seconds * BILLION + int((fraction or "").ljust(9, "0") or "0")


class ExactUtcSubmicrosecondOrderingSourceChecks(unittest.TestCase):
    def test_unix_epoch_is_zero_nanoseconds(self):
        self.assertEqual(reviewed_utc_nanoseconds("1970-01-01T00:00:00Z"), 0)

    def test_one_second_is_exact_billion_nanoseconds(self):
        self.assertEqual(reviewed_utc_nanoseconds("1970-01-01T00:00:01Z"),
                         BILLION)

    def test_single_nanosecond_is_preserved(self):
        self.assertEqual(
            reviewed_utc_nanoseconds("1970-01-01T00:00:00.000000001Z"), 1)

    def test_seven_fraction_digits_remain_distinguishable(self):
        a = reviewed_utc_nanoseconds("2026-10-17T10:00:00.0000001Z")
        b = reviewed_utc_nanoseconds("2026-10-17T10:00:00.0000002Z")
        self.assertEqual(b - a, 100)

    def test_nine_fraction_digits_remain_distinguishable(self):
        a = reviewed_utc_nanoseconds("2026-10-17T10:00:00.123456789Z")
        b = reviewed_utc_nanoseconds("2026-10-17T10:00:00.123456790Z")
        self.assertEqual(b - a, 1)

    def test_microseconds_are_not_rounded_from_seven_digits(self):
        a = reviewed_utc_nanoseconds("2026-10-17T10:00:00.9999999Z")
        b = reviewed_utc_nanoseconds("2026-10-17T10:00:01.0000000Z")
        self.assertEqual(b - a, 100)

    def test_reviewed_actions_seven_digit_precision_is_supported(self):
        self.assertIs(type(reviewed_utc_nanoseconds(
            "2026-10-17T11:49:18.7726359Z")), int)

    def test_timezone_offset_instead_of_z_is_rejected(self):
        self.assertIsNone(reviewed_utc_nanoseconds(
            "2026-10-17T11:49:18.7726359+00:00"))

    def test_missing_timezone_is_rejected(self):
        self.assertIsNone(reviewed_utc_nanoseconds(
            "2026-10-17T11:49:18.7726359"))

    def test_more_than_nine_fraction_digits_is_rejected(self):
        self.assertIsNone(reviewed_utc_nanoseconds(
            "2026-10-17T11:49:18.7726359123Z"))

    def test_invalid_calendar_day_is_rejected(self):
        self.assertIsNone(reviewed_utc_nanoseconds(
            "2026-02-30T10:00:00Z"))

    def test_valid_leap_day_is_supported(self):
        self.assertIs(type(reviewed_utc_nanoseconds(
            "2024-02-29T10:00:00Z")), int)

    def test_invalid_second_is_rejected(self):
        self.assertIsNone(reviewed_utc_nanoseconds(
            "2026-10-17T10:00:60Z"))

    def test_nontext_timestamps_are_rejected(self):
        self.assertIsNone(reviewed_utc_nanoseconds(None))
        self.assertIsNone(reviewed_utc_nanoseconds(True))

    def test_stale_suffix_cannot_be_silently_accepted(self):
        self.assertIsNone(reviewed_utc_nanoseconds(
            "2026-10-17T10:00:00.1Z unexplained"))

    def test_precision_does_not_authorize_protected_annual_run(self):
        self.assertIsNotNone(reviewed_utc_nanoseconds(
            "2026-10-17T10:00:00.0000001Z"))
        self.assertNotEqual(
            reviewed_utc_nanoseconds("2026-10-17T10:00:00.0000001Z"),
            "ANNUAL_DISPATCH_AUTHORIZED")
