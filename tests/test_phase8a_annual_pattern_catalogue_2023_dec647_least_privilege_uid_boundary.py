from __future__ import annotations

"""DEC-647 inert, disposable-only UID boundary counterexamples.

No real source tree is used as a checkout fixture. Never use this module to
authorize an annual run, installation, merge, broker order, or live trading.
"""

import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


@unittest.skipUnless(
    os.name == "posix" and hasattr(os, "geteuid") and os.geteuid() == 0
    and shutil.which("setpriv") is not None,
    "Requires isolated root test environment and setpriv; never escalate in CI",
)
class DisposableLeastPrivilegeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.root.chmod(0o755)
        self.checkout = self.root / "synthetic-checkout"
        self.checkout.mkdir(mode=0o755)
        (self.checkout / "inventory.txt").write_text("locked\n")
        self.external = self.root / "synthetic-external"
        self.external.mkdir(mode=0o755)
        os.chown(self.external, 65534, 65534)
        self.external.chmod(0o700)
        self.payload = self.external / "relocatable"
        self.payload.mkdir(mode=0o700)
        os.chown(self.payload, 65534, 65534)

    def actor(self, program: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["setpriv", "--no-new-privs", "--bounding-set=-all",
             "--reuid=65534", "--regid=65534", "--clear-groups",
             sys.executable, "-B", "-c", program, *map(str, args)],
            capture_output=True, text=True, timeout=8,
        )

    def assert_locked_inventory(self):
        self.assertEqual((self.checkout / "inventory.txt").read_text(), "locked\n")

    def test_unprivileged_process_cannot_reparent_into_trusted_checkout(self):
        script = "import os,sys; os.rename(sys.argv[1],sys.argv[2])"
        proc = self.actor(script, self.payload, self.checkout / "relocatable")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("PermissionError", proc.stderr)
        self.assertTrue(self.payload.is_dir())
        self.assertFalse((self.checkout / "relocatable").exists())
        self.assert_locked_inventory()

    def test_same_unprivileged_process_succeeds_if_checkout_world_writable(self):
        self.checkout.chmod(0o777)
        script = "import os,sys; os.rename(sys.argv[1],sys.argv[2])"
        proc = self.actor(script, self.payload, self.checkout / "relocatable")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.checkout / "relocatable").is_dir())
        self.assert_locked_inventory()

    def test_unprivileged_actor_can_publish_to_allowed_external_location(self):
        script = "import sys; from pathlib import Path; Path(sys.argv[1]).write_text('audit\\n')"
        out = self.external / "report.txt"
        proc = self.actor(script, out)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(out.read_text(), "audit\n")
        self.assert_locked_inventory()

    def test_unprivileged_actor_cannot_chmod_trusted_checkout(self):
        script = "import os,sys; os.chmod(sys.argv[1], 0o777)"
        proc = self.actor(script, self.checkout)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("PermissionError", proc.stderr)
        self.assertEqual(stat.S_IMODE(self.checkout.stat().st_mode), 0o755)
        self.assert_locked_inventory()

    def test_unprivileged_actor_cannot_restore_root_owned_0555_checkout(self):
        self.checkout.chmod(0o555)
        try:
            script = "import os,sys; os.chmod(sys.argv[1], 0o777)"
            proc = self.actor(script, self.checkout)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("PermissionError", proc.stderr)
            self.assertEqual(stat.S_IMODE(self.checkout.stat().st_mode), 0o555)
        finally:
            self.checkout.chmod(0o755)
        self.assert_locked_inventory()

    def test_unprivileged_actor_has_no_new_privileges_and_no_effective_caps(self):
        program = "from pathlib import Path; print(Path('/proc/self/status').read_text())"
        proc = self.actor(program)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("NoNewPrivs:\t1", proc.stdout)
        self.assertIn("CapEff:\t0000000000000000", proc.stdout)
        self.assert_locked_inventory()


class WorkflowTrustBoundarySourceTests(unittest.TestCase):
    def test_frozen_annual_workflow_does_not_explicitly_drop_uid_privileges(self):
        root = Path(__file__).resolve().parents[1]
        src = (root / ".github/workflows/phase8a-annual-pattern-catalogue.yml").read_text()
        self.assertEqual(src.count("uses: actions/checkout@v6"), 3)
        self.assertIn("contents: read", src)
        for marker in ("setpriv ", "--no-new-privs", "capsh ", "runuser "):
            self.assertNotIn(marker, src)

    def test_negative_witness_has_no_authority_or_real_checkout_mutation(self):
        source = Path(__file__).read_text()
        src = source.split("    def test_negative_witness_has_no_authority_or_real_checkout_mutation(self):")[0]
        for marker in (
            "workflow_dispatch(", "gh workflow run", "place_order(",
            "requests.", "subprocess.Popen", "sudo ", "--reuid=0",
        ):
            self.assertNotIn(marker, src)
        self.assertIn("tempfile.TemporaryDirectory()", src)
        self.assertIn("--no-new-privs", src)
        self.assertIn("--bounding-set=-all", src)


if __name__ == "__main__":
    unittest.main()
