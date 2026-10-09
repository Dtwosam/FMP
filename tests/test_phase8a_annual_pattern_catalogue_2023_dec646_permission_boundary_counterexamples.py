from __future__ import annotations

"""DEC-646: disposable-only negative permission/mount boundary witnesses.

These tests never touch a real source checkout or invoke an annual workflow.
Passing demonstrates that the examined assumptions are insufficient as security
invariants, not that a vulnerability has been repaired.
"""

import errno
import os
import runpy
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest


class CheckoutIsolationCounterexamples(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.checkout = self.root / "synthetic-checkout"
        self.checkout.mkdir(mode=0o755)
        self.external = self.root / "synthetic-external"
        self.external.mkdir(mode=0o755)
        (self.checkout / "inventory.txt").write_text("unchanged\n")

    def assert_inventory_unchanged(self):
        self.assertEqual((self.checkout / "inventory.txt").read_text(), "unchanged\n")

    @unittest.skipUnless(os.name == "posix", "POSIX mode bits required")
    def test_owner_can_restore_checkout_write_after_chmod_0555(self):
        original = stat.S_IMODE(self.checkout.stat().st_mode)
        try:
            self.checkout.chmod(0o555)
            self.assertEqual(stat.S_IMODE(self.checkout.stat().st_mode), 0o555)
            # An untrusted same-UID actor can restore mode bits it owns.
            self.checkout.chmod(0o755)
            self.assertTrue(stat.S_IMODE(self.checkout.stat().st_mode) & stat.S_IWUSR)
            self.external.rename(self.checkout / "relocated")
            self.assertTrue((self.checkout / "relocated").is_dir())
        finally:
            self.checkout.chmod(original)
        self.assert_inventory_unchanged()

    def test_writable_checkout_allows_output_directory_reparent(self):
        self.external.rename(self.checkout / "relocated")
        self.assertTrue((self.checkout / "relocated").is_dir())
        self.assertFalse(self.external.exists())
        self.assert_inventory_unchanged()

    @unittest.skipUnless(os.name == "posix" and hasattr(os, "O_DIRECTORY"), "dirfd requires POSIX")
    def test_pinned_fd_follows_directory_reparent_into_checkout(self):
        fd = os.open(self.external, os.O_RDONLY | os.O_DIRECTORY)
        try:
            moved = self.checkout / "relocated"
            self.external.rename(moved)
            leaf = os.open("new-report.json", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600, dir_fd=fd)
            try:
                os.write(leaf, b'{"evidence":true}\n')
            finally:
                os.close(leaf)
            self.assertEqual((moved / "new-report.json").read_bytes(), b'{"evidence":true}\n')
            self.assertFalse(self.external.exists())
        finally:
            os.close(fd)
        self.assert_inventory_unchanged()

    def test_permission_snapshot_does_not_pin_future_mode(self):
        old = stat.S_IMODE(self.checkout.stat().st_mode)
        try:
            self.checkout.chmod(0o555)
            snapshot = stat.S_IMODE(self.checkout.stat().st_mode)
            self.assertFalse(snapshot & stat.S_IWUSR)
            self.checkout.chmod(0o700)
            self.assertNotEqual(snapshot, stat.S_IMODE(self.checkout.stat().st_mode))
        finally:
            self.checkout.chmod(old)
        self.assert_inventory_unchanged()

    @unittest.skipUnless(os.path.isdir("/dev/shm"), "Linux tmpfs fixture unavailable")
    def test_cross_device_reparent_requires_explicit_mount_boundary(self):
        if self.external.stat().st_dev == Path("/dev/shm").stat().st_dev:
            self.skipTest("fixture and /dev/shm share same device")
        try:
            dest_root = tempfile.TemporaryDirectory(dir="/dev/shm")
        except OSError:
            self.skipTest("cannot create disposable /dev/shm fixture")
        with dest_root:
            dest = Path(dest_root.name) / "relocated"
            with self.assertRaises(OSError) as exc:
                self.external.rename(dest)
            self.assertEqual(exc.exception.errno, errno.EXDEV)
            self.assertTrue(self.external.is_dir())
            self.assertFalse(dest.exists())
        self.assert_inventory_unchanged()

    def test_dec645_mount_observation_never_approves_same_uid_writes(self):
        root = Path(__file__).resolve().parents[1]
        probe = root / "scripts" / "dec645_mount_boundary_diagnostic.py"
        module = runpy.run_path(str(probe), run_name="dec646_consumer_test")
        sample = "1 0 1:1 / / rw - ext4 none rw\n"
        result = module["inspect_checkout_boundary"](
            self.checkout, self.external, sample,
        )
        self.assertIs(result["authorized"], False)
        self.assertEqual(result["classification"], "NOT_AN_AUTHORIZATION")

    def test_annual_workflow_has_no_explicit_checkout_mount_isolation(self):
        root = Path(__file__).resolve().parents[1]
        # Historical tests may remove the workflow from the mutable worktree.
        # Git's HEAD tree remains the exact immutable content under review.
        result = subprocess.run(
            ["git", "show", "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=root, capture_output=True, text=True, check=True, timeout=10,
        )
        yaml = result.stdout
        self.assertEqual(yaml.count("uses: actions/checkout@v6"), 3)
        self.assertEqual(yaml.count("runs-on: ubuntu-latest"), 3)
        self.assertIn("contents: read", yaml)
        self.assertIn("actions: read", yaml)
        # NEGATIVE WITNESS: token access is not read-only filesystem mounting.
        for marker in (
            "container:", "mount -o remount,ro", "mount --bind",
            "unshare --mount", "mount --make-private",
        ):
            self.assertNotIn(marker, yaml)

    def test_same_device_stat_is_observation_not_different_mount_proof(self):
        # Both paths are on the same created tree; the snapshot is not a lock.
        self.assertEqual(self.checkout.stat().st_dev, self.external.stat().st_dev)
        self.external.rename(self.checkout / "relocated")
        self.assert_inventory_unchanged()


if __name__ == "__main__":
    unittest.main()
