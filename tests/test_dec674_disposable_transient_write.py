from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec674_disposable_transient_write.py"
spec = importlib.util.spec_from_file_location("dec674", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RevertedWriteProofTests(unittest.TestCase):
    def test_equal_digest_without_event_log_is_blocked(self):
        r = module.assess(b"same", b"same", None, False)
        self.assertEqual(r["status"], "BLOCKED")
        self.assertTrue(r["observed_checks"]["digest_equal"])
        self.assertFalse(r["can_authorize_dispatch"])

    def test_two_writes_reverted_are_still_blocked(self):
        r = module.assess(b"same", b"same", 2, True)
        self.assertTrue(r["observed_checks"]["digest_equal"])
        self.assertEqual(r["status"], "BLOCKED")
        self.assertFalse(r["observed_checks"]["no_observed_writes"])

    def test_one_reverted_write_blocks(self):
        self.assertEqual(module.assess(b"abc", b"abc", 1, True)["status"], "BLOCKED")

    def test_real_disposable_reverted_bytes_are_equal_but_blocked(self):
        r = module.run_demo(True)
        self.assertEqual(r["status"], "BLOCKED", r)
        self.assertTrue(r["observed_checks"]["final_bytes_equal"])
        self.assertTrue(r["observed_checks"]["digest_equal"])
        self.assertFalse(r["can_authorize_dispatch"])

    def test_real_disposable_control_is_unverified(self):
        r = module.run_demo(False)
        self.assertEqual(r["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED", r)
        self.assertFalse(r["independent_os_proof_verified"])

    def test_changed_final_bytes_blocks(self):
        self.assertEqual(module.assess(b"a", b"b", 0, True)["status"], "BLOCKED")

    def test_unknown_event_log_blocks(self):
        for events in (True, False, -1, "0", 0.0, None, [], {}):
            with self.subTest(events=repr(events)):
                self.assertEqual(module.assess(b"a", b"a", events, True)["status"], "BLOCKED")

    def test_untrusted_observer_blocks(self):
        self.assertEqual(module.assess(b"a", b"a", 0, False)["status"], "BLOCKED")

    def test_synthetic_no_write_is_still_not_authorization(self):
        r = module.assess(b"abc", b"abc", 0, True)
        self.assertEqual(r["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED")
        self.assertFalse(r["independent_os_proof_verified"])
        self.assertFalse(r["can_authorize_dispatch"])

    def test_default_cli_is_blocked(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT)], capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)["status"], "BLOCKED")

    def test_cli_negative_control_is_nonzero(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT), "--execute-reverted-write-negative"],
                           capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        self.assertTrue(json.loads(p.stdout)["observed_checks"]["digest_equal"])

    def test_cli_rejects_arbitrary_checkout(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT), "--checkout", "/protected"],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)


if __name__ == "__main__":
    unittest.main()
