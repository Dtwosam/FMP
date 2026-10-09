from __future__ import annotations

"""DEC-644: NEGATIVE witness of residual dirfd inode-reparent boundary.

All filesystem objects in this test are disposable under TemporaryDirectory.
This is not a real checkout mutation or a security acceptance test.
"""

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fmp.discovery import annual_pattern_catalogue_2023_dirfd_publication_preview as anchored
from fmp.discovery.annual_pattern_catalogue_2023_external_report_create import (
    write_once_external_report,
)


class KnownOutputDirectoryReparentLimit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.external = self.root / "external"
        self.external.mkdir()
        self.checkout = self.root / "synthetic-checkout"
        self.checkout.mkdir()
        (self.checkout / "locked.txt").write_text("inventory\n")
        self.target = self.external / "proof.json"

    def test_known_limit_directory_moved_inside_synthetic_checkout_after_open(self):
        """Current anchored writer follows the moved inode into the checkout.

        This intentionally verifies a residual vulnerability, not a guarantee
        that real checkout output is denied. Do not use as merge approval.
        """
        real_open = os.open
        moved = self.checkout / "relocated-external"
        triggered = []
        def reparent(path, flags, *args, **kwargs):
            if str(path).startswith(".fmp-audit-") and not triggered:
                triggered.append(True)
                self.external.rename(moved)
            return real_open(path, flags, *args, **kwargs)
        original_flags = anchored._safe_flags()
        with (
            mock.patch.object(anchored, "_safe_flags", return_value=original_flags),
            mock.patch.object(anchored.os, "open", side_effect=reparent),
        ):
            write_once_external_report(self.target, "proof\n", "conflict")
        self.assertEqual(triggered, [True])
        # NEGATIVE WITNESS: the new report is inside the synthetic checkout.
        self.assertEqual((moved / "proof.json").read_text(), "proof\n")
        self.assertFalse(self.target.exists())
        self.assertEqual(
            (self.checkout / "locked.txt").read_text(), "inventory\n"
        )
        self.assertEqual(
            sorted(p.name for p in self.checkout.iterdir()),
            ["locked.txt", "relocated-external"],
        )


if __name__ == "__main__":
    unittest.main()
