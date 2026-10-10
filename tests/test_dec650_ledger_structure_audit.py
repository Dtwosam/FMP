from __future__ import annotations

"""Synthetic-only fixtures. They do NOT reproduce actual runner OS isolation."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec650_ledger_structure_audit.py"
spec = importlib.util.spec_from_file_location("dec650_ledger_structure_audit", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SHA40 = "a" * 40
SHA64 = "b" * 64


def fixtures():
    policy = {
        "schema": module.SCHEMA, "repository": "Dtwosam/FMP",
        "source_commit": SHA40, "source_tree": "c" * 40,
        "workflow_blob": "d" * 40, "workflow_ref": "refs/heads/main",
        "segment": "2023", "run_number": 385, "run_attempt": 1,
        "previous_freeze_run_id": 37663157285,
    }
    keys = ["preflight"] + sorted(k for k in module._required_job_keys() if k.startswith("cell:")) + ["freeze"]
    jobs = []
    for i, key in enumerate(keys, 1):
        parts = key.split(":")
        jobs.append({
            "kind": parts[0],
            "matrix": {"symbol": parts[1], "timeframe": parts[2], "horizon": int(parts[3])} if len(parts) == 4 else None,
            "job_id": 10000 + i, "runner_image": "synthetic-image",
            "kernel": "synthetic-kernel", "mount_namespace": "synthetic-ns",
            "mountinfo_sha256": SHA64, "source_mount_id": "synthetic-mount",
            "restricted_uid": 65534, "no_new_privs": True,
            "effective_capabilities": "0", "checkout_mount_readonly": True,
            "writable_checkout_aliases": [], "unapproved_inherited_fds": [],
            "standard_streams": {"0": "devnull", "1": "external-log", "2": "external-log"},
            "checkout_before_sha256": SHA64, "checkout_after_sha256": SHA64,
            "checks": {name: {"status": "PASS", "skipped": False, "privileged_test_executed": True, "evidence_sha256": SHA64} for name in module.REQUIRED_CHECKS},
        })
    return policy, {**policy, "jobs": jobs}


class LedgerStructureTests(unittest.TestCase):
    def test_complete_fabricated_evidence_can_never_authorize(self):
        policy, ledger = fixtures()
        result = module.assess(policy, ledger)
        self.assertEqual(result["status"], "STRUCTURALLY_COMPLETE_UNVERIFIED")
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])

    def test_exact_twenty_unique_jobs(self):
        _, ledger = fixtures()
        self.assertEqual(len(ledger["jobs"]), 20)
        self.assertEqual(len({module._job_key(j) for j in ledger["jobs"]}), 20)

    def test_missing_freeze_blocks(self):
        p, l = fixtures(); l["jobs"].pop()
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_duplicate_cell_cannot_replace_missing_cell(self):
        p, l = fixtures(); l["jobs"][3] = dict(l["jobs"][2])
        result = module.assess(p, l)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("duplicate job" in x for x in result["findings"]))

    def test_wrong_source_sha_blocks(self):
        p, l = fixtures(); l["source_commit"] = "e" * 40
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_changed_workflow_blob_blocks(self):
        p, l = fixtures(); l["workflow_blob"] = "f" * 40
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_wrong_attempt_blocks(self):
        p, l = fixtures(); l["run_attempt"] = 2
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_wrong_positive_run_number_blocks(self):
        p, l = fixtures(); p["run_number"] = 386; l["run_number"] = 386
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_wrong_positive_previous_freeze_run_blocks(self):
        p, l = fixtures(); p["previous_freeze_run_id"] = 999; l["previous_freeze_run_id"] = 999
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_boolean_instead_of_positive_run_identity_blocks(self):
        p, l = fixtures(); p["run_number"] = True; l["run_number"] = True
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_privileged_skip_blocks(self):
        p, l = fixtures(); l["jobs"][0]["checks"]["checkout_path_write_denied"]["skipped"] = True
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_failed_check_blocks(self):
        p, l = fixtures(); l["jobs"][0]["checks"]["checkout_path_write_denied"]["status"] = "FAIL"
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_missing_evidence_hash_blocks(self):
        p, l = fixtures(); l["jobs"][0]["checks"]["directory_reparent_denied"].pop("evidence_sha256")
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_root_actor_blocks(self):
        p, l = fixtures(); l["jobs"][0]["restricted_uid"] = 0
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_writable_alias_blocks(self):
        p, l = fixtures(); l["jobs"][1]["writable_checkout_aliases"] = ["synthetic-alias"]
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_unhashable_kind_returns_blocked_not_exception(self):
        p, l = fixtures(); l["jobs"][0]["kind"] = ["cell"]
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_cli_bad_digest_format_emits_structured_blocked(self):
        policy, ledger = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); a = base / "p.json"; b = base / "l.json"
            a.write_text(json.dumps(policy)); b.write_text(json.dumps(ledger))
            proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "--policy", str(a), "--policy-sha256", "bogus", "--ledger", str(b)], capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)["status"], "BLOCKED")

    def test_cli_oversized_json_fails_closed(self):
        policy, ledger = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); a = base / "p.json"; b = base / "l.json"
            a.write_bytes(b" " * (module.MAX_JSON_BYTES + 1))
            b.write_text(json.dumps(ledger))
            proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "--policy", str(a), "--policy-sha256", hashlib.sha256(a.read_bytes()).hexdigest(), "--ledger", str(b)], capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)["status"], "BLOCKED")

    def test_bad_fd_blocks(self):
        p, l = fixtures(); l["jobs"][0]["standard_streams"]["1"] = "checkout-file"
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_leaked_inherited_fd_blocks(self):
        p, l = fixtures(); l["jobs"][0]["unapproved_inherited_fds"] = [11]
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_inventory_mismatch_blocks(self):
        p, l = fixtures(); l["jobs"][0]["checkout_after_sha256"] = "f" * 64
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_no_new_privs_missing_blocks(self):
        p, l = fixtures(); l["jobs"][0]["no_new_privs"] = False
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_reused_job_id_blocks(self):
        p, l = fixtures(); l["jobs"][1]["job_id"] = l["jobs"][0]["job_id"]
        self.assertEqual(module.assess(p, l)["status"], "BLOCKED")

    def test_cli_success_only_means_unverified_structure(self):
        policy, ledger = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); a = base / "p.json"; b = base / "l.json"
            raw = json.dumps(policy).encode("utf-8"); a.write_bytes(raw); b.write_text(json.dumps(ledger))
            proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "--policy", str(a), "--policy-sha256", hashlib.sha256(raw).hexdigest(), "--ledger", str(b)], capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["status"], "STRUCTURALLY_COMPLETE_UNVERIFIED")

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(os, "O_NOFOLLOW"), "POSIX-only")
    def test_cli_fifo_input_does_not_hang(self):
        policy, ledger = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); fifo = base / "fifo.json"; b = base / "l.json"
            os.mkfifo(fifo); b.write_text(json.dumps(ledger))
            proc = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--policy", str(fifo),
                 "--policy-sha256", SHA64, "--ledger", str(b)],
                capture_output=True, text=True, timeout=4, check=False,
            )
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["status"], "BLOCKED")

    @unittest.skipUnless(hasattr(os, "symlink") and hasattr(os, "O_NOFOLLOW"), "POSIX-only")
    def test_cli_symlink_input_is_rejected(self):
        policy, ledger = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); target = base / "real.json"; alias = base / "alias.json"; b = base / "l.json"
            raw = json.dumps(policy).encode("utf-8")
            target.write_bytes(raw); alias.symlink_to(target); b.write_text(json.dumps(ledger))
            proc = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--policy", str(alias),
                 "--policy-sha256", hashlib.sha256(raw).hexdigest(), "--ledger", str(b)],
                capture_output=True, text=True, timeout=4, check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)["status"], "BLOCKED")

    def test_cli_directory_input_is_rejected(self):
        policy, ledger = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); b = base / "l.json"
            b.write_text(json.dumps(ledger))
            proc = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--policy", str(base),
                 "--policy-sha256", SHA64, "--ledger", str(b)],
                capture_output=True, text=True, timeout=4, check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)["status"], "BLOCKED")

    def test_cli_duplicate_policy_keys_fail_closed(self):
        policy, ledger = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); a = base / "p.json"; b = base / "l.json"
            raw = (json.dumps(policy)[:-1] + ', "run_number": 385}').encode("utf-8")
            a.write_bytes(raw); b.write_text(json.dumps(ledger))
            proc = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--policy", str(a),
                 "--policy-sha256", hashlib.sha256(raw).hexdigest(), "--ledger", str(b)],
                capture_output=True, text=True, timeout=4, check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)["status"], "BLOCKED")

    def test_cli_duplicate_nested_ledger_keys_fail_closed(self):
        policy, ledger = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); a = base / "p.json"; b = base / "l.json"
            raw = json.dumps(policy).encode("utf-8")
            a.write_bytes(raw)
            nested = json.dumps(ledger).replace('"job_id": 10001', '"job_id": 10001, "job_id": 10001', 1)
            b.write_text(nested)
            proc = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--policy", str(a),
                 "--policy-sha256", hashlib.sha256(raw).hexdigest(), "--ledger", str(b)],
                capture_output=True, text=True, timeout=4, check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)["status"], "BLOCKED")

    def test_cli_nan_ledger_value_fails_closed(self):
        policy, ledger = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); a = base / "p.json"; b = base / "l.json"
            raw = json.dumps(policy).encode("utf-8")
            a.write_bytes(raw)
            b.write_text(json.dumps(ledger).replace('"restricted_uid": 65534', '"restricted_uid": NaN', 1))
            proc = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--policy", str(a),
                 "--policy-sha256", hashlib.sha256(raw).hexdigest(), "--ledger", str(b)],
                capture_output=True, text=True, timeout=4, check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)["status"], "BLOCKED")

    def test_cli_deeply_nested_json_returns_blocked_not_traceback(self):
        policy, ledger = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); a = base / "p.json"; b = base / "l.json"
            raw = json.dumps(policy).encode("utf-8")
            a.write_bytes(raw)
            # Deep nesting is smaller than the byte limit but exceeds the
            # standard JSON decoder recursion limit on Python 3 runners.
            b.write_bytes(b"[" * 10000 + b"0" + b"]" * 10000)
            proc = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--policy", str(a),
                 "--policy-sha256", hashlib.sha256(raw).hexdigest(),
                 "--ledger", str(b)],
                capture_output=True, text=True, timeout=4, check=False,
            )
            self.assertEqual(proc.returncode, 2, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "BLOCKED")
            self.assertFalse(payload["can_authorize_dispatch"])
            self.assertFalse(payload["independent_os_proof_verified"])

    def test_cli_wrong_policy_digest_fails_closed(self):
        policy, ledger = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); a = base / "p.json"; b = base / "l.json"
            a.write_text(json.dumps(policy)); b.write_text(json.dumps(ledger))
            proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "--policy", str(a), "--policy-sha256", "e" * 64, "--ledger", str(b)], capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 2)
            self.assertFalse(json.loads(proc.stdout)["can_authorize_dispatch"])


if __name__ == "__main__":
    unittest.main()
