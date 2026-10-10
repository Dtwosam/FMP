from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec675_synthetic_atomic_admission.py"
spec = importlib.util.spec_from_file_location("dec675", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SyntheticAtomicAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.db = Path(self.directory.name) / "synthetic-only.sqlite3"
        module._initialize(self.db)

    def claim(self, **overrides):
        values = dict(sha=module.EXPECTED_SHA, actor=module.EXPECTED_ACTOR,
                      payload=module.EXPECTED_PAYLOAD, claim_id="first")
        values.update(overrides)
        return module._claim(self.db, **values)

    def test_first_claim_only_synthetic_not_real_authorization(self):
        r = self.claim()
        self.assertEqual(r["status"], "SYNTHETIC_RESERVATION_UNVERIFIED")
        self.assertFalse(r["can_authorize_dispatch"])
        self.assertFalse(r["server_enforcement_verified"])
        self.assertFalse(r["annual_run_385_consumed"])

    def test_replay_never_reopens_claimed_slot(self):
        self.claim()
        self.assertEqual(self.claim(claim_id="second")["status"], "BLOCKED")
        self.assertEqual(module._inspect(self.db), ("RESERVED", "first"))

    def test_incorrect_source_does_not_consume_slot(self):
        self.assertEqual(self.claim(sha="b" * 40)["status"], "BLOCKED")
        self.assertEqual(module._inspect(self.db), ("UNCLAIMED", None))

    def test_unapproved_actor_does_not_consume_slot(self):
        self.assertEqual(self.claim(actor="competing_actor")["status"], "BLOCKED")
        self.assertEqual(module._inspect(self.db), ("UNCLAIMED", None))

    def test_different_payload_does_not_consume_slot(self):
        self.assertEqual(self.claim(payload="different-event")["status"], "BLOCKED")
        self.assertEqual(module._inspect(self.db), ("UNCLAIMED", None))

    def test_invalid_claims_are_blocked(self):
        for field in ("sha", "actor", "payload", "claim_id"):
            for value in (None, "", 123, "X" * 129):
                with self.subTest(field=field, value=value):
                    self.assertEqual(self.claim(**{field: value})["status"], "BLOCKED")
        self.assertEqual(module._inspect(self.db), ("UNCLAIMED", None))

    def test_duplicate_initialization_never_resets_slot(self):
        self.claim()
        with self.assertRaises(FileExistsError):
            module._initialize(self.db)
        self.assertEqual(module._inspect(self.db), ("RESERVED", "first"))

    def test_database_absent_does_not_create_fresh_slot(self):
        absent = self.db.with_name("absent.sqlite3")
        r = module._claim(absent, sha=module.EXPECTED_SHA,
                          actor=module.EXPECTED_ACTOR,
                          payload=module.EXPECTED_PAYLOAD, claim_id="test")
        self.assertEqual(r["status"], "BLOCKED")
        self.assertFalse(absent.exists())

    def test_threaded_race_grants_exactly_one_fake_slot(self):
        with ThreadPoolExecutor(max_workers=12) as executor:
            tasks = [executor.submit(self.claim, claim_id=f"writer-{i}") for i in range(12)]
            results = [t.result(timeout=10) for t in tasks]
        self.assertEqual(sum(r["status"] == "SYNTHETIC_RESERVATION_UNVERIFIED"
                             for r in results), 1)
        self.assertEqual(sum(r["status"] == "BLOCKED" for r in results), 11)
        self.assertEqual(module._inspect(self.db)[0], "RESERVED")

    def test_process_race_grants_one_fake_slot(self):
        # Distinct interpreters/SQLite connections, not only thread contention.
        code = ("import importlib.util,sys,json;"
                "sp=importlib.util.spec_from_file_location('m',sys.argv[1]);"
                "m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);"
                "r=m._claim(__import__('pathlib').Path(sys.argv[2]),"
                "sha=m.EXPECTED_SHA,actor=m.EXPECTED_ACTOR,"
                "payload=m.EXPECTED_PAYLOAD,claim_id=sys.argv[3]);"
                "print(json.dumps(r))")
        processes = [subprocess.Popen([sys.executable, '-B', '-c', code,
                                       str(SCRIPT), str(self.db), f'pid-{i}'],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      text=True) for i in range(6)]
        results = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, stderr)
            results.append(json.loads(stdout))
        self.assertEqual(sum(r['status'] == 'SYNTHETIC_RESERVATION_UNVERIFIED'
                             for r in results), 1)
        self.assertEqual(module._inspect(self.db)[0], 'RESERVED')

    def test_local_database_writer_can_forge_reopening_but_never_authorize(self):
        # Counterexample: SQLite is NOT a trusted GitHub-control-plane gate.
        self.claim()
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE reservations SET state='UNCLAIMED', claim_id=NULL WHERE slot=?",
                         (module.SLOT,))
        replay = self.claim(claim_id='forged-replay')
        self.assertEqual(replay['status'], 'SYNTHETIC_RESERVATION_UNVERIFIED')
        self.assertFalse(replay['can_authorize_dispatch'])
        self.assertFalse(replay['server_enforcement_verified'])

    def test_simulated_crash_post_reservation_replay_fails(self):
        self.claim()
        # A new independent connection represents a restart. No reset API.
        self.assertEqual(self.claim(claim_id="after-restart")["status"], "BLOCKED")
        self.assertEqual(module._inspect(self.db), ("RESERVED", "first"))

    def test_inert_cli_nonzero_and_nonauthorizing(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT)], capture_output=True,
                           text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["can_authorize_dispatch"])

    def test_optin_local_demo_nonzero_and_nonauthorizing(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT), "--execute-disposable-demo"],
                           capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 3, p.stderr)
        result = json.loads(p.stdout)
        self.assertEqual(result["synthetic_winners"], 1)
        self.assertEqual(result["synthetic_attempts"], 24)
        self.assertFalse(result["annual_run_385_consumed"])

    def test_ref_workflow_db_options_are_rejected(self):
        for option in ("--repo", "--workflow", "--db", "--ref", "--dispatch"):
            with self.subTest(option=option):
                p = subprocess.run([sys.executable, "-B", str(SCRIPT), option, "value"],
                                   capture_output=True, text=True, timeout=4)
                self.assertNotEqual(p.returncode, 0)

    def test_bad_worker_counts_block(self):
        for count in (0, 1, 33, "24", True):
            with self.subTest(count=count):
                self.assertEqual(module.run_demo(workers=count)["status"], "BLOCKED")

    def test_nonlinux_blocks_without_attempt(self):
        with patch.object(module.sys, "platform", "win32"):
            self.assertEqual(module.run_demo()["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
