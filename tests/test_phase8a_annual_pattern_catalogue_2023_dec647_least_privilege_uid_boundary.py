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
from unittest import mock


def _restricted_child_environment(home: Path) -> dict[str, str]:
    """Keep demonstration-only children free of inherited credentials."""
    return {"PATH": os.defpath, "HOME": str(home), "PYTHONDONTWRITEBYTECODE": "1"}


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
        setpriv_executable = shutil.which("setpriv")
        self.assertIsNotNone(setpriv_executable)
        return subprocess.run(
            [setpriv_executable, "--no-new-privs", "--bounding-set=-all",
             "--reuid=65534", "--regid=65534", "--clear-groups",
             sys.executable, "-B", "-c", program, *map(str, args)],
            capture_output=True, text=True, timeout=8,
            env=_restricted_child_environment(self.root),
            cwd=self.root, close_fds=True,
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

    def test_unprivileged_actor_does_not_inherit_synthetic_parent_secret(self):
        name = "FMP_DEC648_SYNTHETIC_SECRET_ONLY"
        with mock.patch.dict(os.environ, {name: "synthetic-secret-never-real"}):
            proc = self.actor(
                "import os; print(os.getenv('FMP_DEC648_SYNTHETIC_SECRET_ONLY', 'absent'))"
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "absent")
        self.assert_locked_inventory()

    def test_unprivileged_actor_has_no_new_privileges_and_no_effective_caps(self):
        program = "from pathlib import Path; print(Path('/proc/self/status').read_text())"
        proc = self.actor(program)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("NoNewPrivs:\t1", proc.stdout)
        self.assertIn("CapEff:\t0000000000000000", proc.stdout)
        self.assert_locked_inventory()


    def _synthetic_root_only_canary(self) -> Path:
        # Private test data only; never access the real checkout or credentials.
        canary = self.root / "synthetic-private-canary.txt"
        canary.write_text("synthetic-open-fd-canary\n")
        canary.chmod(0o600)
        return canary

    def test_restricted_child_starts_in_disposable_working_directory(self):
        proc = self.actor("import os; print(os.getcwd())")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), str(self.root.resolve()))
        self.assert_locked_inventory()

    def test_root_only_canary_cannot_be_read_by_restricted_path_open(self):
        canary = self._synthetic_root_only_canary()
        proc = self.actor(
            "import sys; from pathlib import Path; print(Path(sys.argv[1]).read_text())",
            canary,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("PermissionError", proc.stderr)
        self.assert_locked_inventory()

    def test_inheritable_parent_canary_fd_is_closed_in_restricted_child(self):
        canary = self._synthetic_root_only_canary()
        fd = os.open(canary, os.O_RDONLY)
        try:
            # Even an inheritable parent FD must not reach the default actor.
            os.set_inheritable(fd, True)
            code = (
                "import os,sys\n"
                "try:\n"
                " print(os.read(int(sys.argv[1]), 128).decode())\n"
                "except OSError:\n"
                " print('closed')\n"
            )
            proc = self.actor(code, fd)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), "closed")
        finally:
            os.close(fd)
        self.assert_locked_inventory()

    def test_explicit_pass_fds_can_expose_synthetic_canary_despite_uid_drop(self):
        # NEGATIVE witness: deliberately opt into passing *synthetic* data.
        # This is not the normal actor path and never uses a real credential.
        canary = self._synthetic_root_only_canary()
        fd = os.open(canary, os.O_RDONLY)
        try:
            os.set_inheritable(fd, True)
            setpriv_executable = shutil.which("setpriv")
            self.assertIsNotNone(setpriv_executable)
            proc = subprocess.run(
                [setpriv_executable, "--no-new-privs", "--bounding-set=-all",
                 "--reuid=65534", "--regid=65534", "--clear-groups",
                 sys.executable, "-B", "-c",
                 "import os,sys; print(os.geteuid()); "
                 "print(os.read(int(sys.argv[1]),128).decode().strip())", str(fd)],
                env=_restricted_child_environment(self.root),
                cwd=self.root, close_fds=True, pass_fds=(fd,),
                capture_output=True, text=True, timeout=8,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), "65534\nsynthetic-open-fd-canary")
        finally:
            os.close(fd)
        self.assert_locked_inventory()


class WorkflowTrustBoundarySourceTests(unittest.TestCase):
    def test_restricted_actor_explicitly_closes_fds_and_sets_fixture_cwd(self):
        source = Path(__file__).read_text()
        actor_source = source.split("    def actor(self, program:", 1)[1].split(
            "    def assert_locked_inventory(self):", 1,
        )[0]
        self.assertIn("env=_restricted_child_environment(self.root)", actor_source)
        self.assertIn("cwd=self.root", actor_source)
        self.assertIn("close_fds=True", actor_source)
        self.assertNotIn("pass_fds=", actor_source)

    def test_demo_child_environment_uses_explicit_allowlist(self):
        name = "FMP_DEC648_SYNTHETIC_SECRET_ONLY"
        with mock.patch.dict(os.environ, {name: "synthetic-secret-never-real"}):
            env = _restricted_child_environment(Path("/synthetic/no-real-home"))
        self.assertEqual(set(env), {"PATH", "HOME", "PYTHONDONTWRITEBYTECODE"})
        self.assertEqual(env["PATH"], os.defpath)
        self.assertEqual(env["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertNotIn(name, env)


    def test_frozen_annual_workflow_does_not_explicitly_drop_uid_privileges(self):
        root = Path(__file__).resolve().parents[1]
        # Historical tests may remove this file from the working tree while
        # leaving the tracked Git commit intact. Inspect committed evidence.
        result = subprocess.run(
            ["git", "show", "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=root, capture_output=True, text=True, check=True, timeout=10,
        )
        src = result.stdout
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
