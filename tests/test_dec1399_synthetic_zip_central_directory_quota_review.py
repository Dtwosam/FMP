"""DEC-1399: bounded in-memory ZIP metadata quota review.

Never extract files. All inputs are synthesized with BytesIO, no GitHub
artifact or protected history is read, no annual runtime is imported.
A metadata-only diagnostic is NOT a decompression sandbox or OS attestation.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import subprocess
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def archive_bytes(members: list[tuple[str, bytes]], *, compress: int) -> bytes:
    target = BytesIO()
    with zipfile.ZipFile(target, "w", compression=compress) as archive:
        for name, content in members:
            archive.writestr(name, content)
    return target.getvalue()


def metadata_diagnostics(
    data: object,
    *,
    max_members: int = 3,
    max_member_bytes: int = 1024,
    max_total_bytes: int = 2048,
    max_ratio: int = 20,
) -> tuple[str, ...]:
    """Illustrative fail-closed archive metadata policy; never installed."""
    if type(data) is not bytes:
        return ("NON_BYTES_ARCHIVE",)
    limits = (max_members, max_member_bytes, max_total_bytes, max_ratio)
    if any(type(limit) is not int or limit <= 0 for limit in limits):
        return ("INVALID_REVIEW_LIMITS",)
    problems = []
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            members = archive.infolist()
            if len(members) > max_members:
                problems.append("EXCESS_MEMBER_COUNT")
            cumulative = 0
            for member in members:
                if member.file_size > max_member_bytes:
                    problems.append("EXCESS_MEMBER_SIZE")
                cumulative += member.file_size
                if member.file_size > 0 and member.compress_size == 0:
                    problems.append("NONEMPTY_ZERO_COMPRESSED_SIZE")
                if (member.compress_size > 0
                        and member.file_size > max_ratio * member.compress_size):
                    problems.append("EXCESS_COMPRESSION_RATIO")
            if cumulative > max_total_bytes:
                problems.append("EXCESS_TOTAL_DECLARED_SIZE")
    except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError):
        return ("MALFORMED_CENTRAL_DIRECTORY",)
    return tuple(sorted(set(problems)))


class InMemoryZipQuotasDoNotProveActualAnnualArchiveSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )

    def test_current_workflow_has_no_explicit_uncompressed_zip_quota_check(self):
        self.assertNotIn("zipinfo -l ", self.workflow)
        self.assertNotIn("--max-total-uncompressed", self.workflow)
        self.assertIn("unzip -q .prior-freeze/freeze.zip", self.workflow)

    def test_small_stored_synthetic_zip_has_no_size_diagnostics(self):
        data = archive_bytes([("safe/manifest.json", b"{}")],
                             compress=zipfile.ZIP_STORED)
        self.assertEqual(metadata_diagnostics(data), ())

    def test_excess_member_count_rejected_before_extraction(self):
        entries = [(str(i) + ".json", b"{}") for i in range(4)]
        data = archive_bytes(entries, compress=zipfile.ZIP_STORED)
        self.assertIn("EXCESS_MEMBER_COUNT", metadata_diagnostics(data))

    def test_oversized_single_entry_rejected_before_extraction(self):
        data = archive_bytes([("one.txt", b"x" * 1025)],
                             compress=zipfile.ZIP_STORED)
        self.assertIn("EXCESS_MEMBER_SIZE", metadata_diagnostics(data))

    def test_cumulative_size_rejected_when_each_member_under_cap(self):
        data = archive_bytes(
            [("a", b"A" * 800), ("b", b"B" * 800), ("c", b"C" * 800)],
            compress=zipfile.ZIP_STORED,
        )
        self.assertIn("EXCESS_TOTAL_DECLARED_SIZE",
                      metadata_diagnostics(data))
        self.assertNotIn("EXCESS_MEMBER_SIZE", metadata_diagnostics(data))

    def test_small_compressed_high_ratio_fixture_rejected(self):
        data = archive_bytes([("repeating.txt", b"X" * 4096)],
                             compress=zipfile.ZIP_DEFLATED)
        self.assertIn("EXCESS_COMPRESSION_RATIO", metadata_diagnostics(data))

    def test_noncompressed_small_fixture_does_not_trigger_ratio(self):
        data = archive_bytes([("a", b"first"), ("b", b"second")],
                             compress=zipfile.ZIP_STORED)
        self.assertNotIn("EXCESS_COMPRESSION_RATIO",
                         metadata_diagnostics(data))

    def test_corrupted_non_zip_input_is_fail_closed(self):
        self.assertEqual(metadata_diagnostics(b"not a zip"),
                         ("MALFORMED_CENTRAL_DIRECTORY",))

    def test_empty_bytes_archive_is_fail_closed(self):
        self.assertEqual(metadata_diagnostics(b""),
                         ("MALFORMED_CENTRAL_DIRECTORY",))

    def test_non_bytes_source_is_fail_closed(self):
        self.assertEqual(metadata_diagnostics("not bytes"),
                         ("NON_BYTES_ARCHIVE",))

    def test_invalid_configured_quota_value_is_fail_closed(self):
        data = archive_bytes([("safe.txt", b"ok")],
                             compress=zipfile.ZIP_STORED)
        for value in (0, -1, True, "2"):
            with self.subTest(value=value):
                self.assertEqual(metadata_diagnostics(data, max_ratio=value),
                                 ("INVALID_REVIEW_LIMITS",))
