from __future__ import annotations

"""DEC-629: source checkout output boundary is independent of caller cwd."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_lock_witness_coverage import (
    VERSION as WITNESS_VERSION, INTERVALS, REQUIRED_CLAIMS,
)
from fmp.discovery.annual_pattern_catalogue_2023_ambiguous_dispatch_hold_model import (
    VERSION as SIMULATION_VERSION,
)

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "phase8a_annual_pattern_catalogue_2023_"
DECISIONS = {
    "disarmed_tag_amendment_preview": "DEC-618",
    "ref_race_interleaving_model": "DEC-619",
    "lock_witness_coverage": "DEC-620",
    "ambiguous_dispatch_hold_model": "DEC-621",
    "runtime_tag_sha_binding_preview": "DEC-622",
    "preaccess_identity_gate_topology_audit": "DEC-623",
    "three_layer_admission_model": "DEC-624",
}


def _inventory(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*")) if p.is_file()
    }


def _checkout(root: Path) -> tuple[Path, Path]:
    checkout = root / "checkout"
    shutil.copytree(
        ROOT / "src" / "fmp", checkout / "src" / "fmp",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    scripts = checkout / "scripts"
    scripts.mkdir()
    for suffix in DECISIONS:
        script = f"{PREFIX}{suffix}.py"
        shutil.copy2(ROOT / "scripts" / script, scripts / script)
    workflow = checkout / ".github" / "workflows" / "phase8a-annual-pattern-catalogue.yml"
    workflow.parent.mkdir(parents=True)
    shutil.copy2(ROOT / ".github" / "workflows" / workflow.name, workflow)
    return checkout, scripts


def _env(checkout: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(checkout / "src")
    env.pop("PYTHONDONTWRITEBYTECODE", None)
    env.pop("PYTHONPYCACHEPREFIX", None)
    return env


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-629 tests require installed annual workflow source",
)
class AuditSourceCheckoutBoundaryTests(unittest.TestCase):
    def test_guards_are_anchored_to_real_source_and_precede_work(self):
        self.assertEqual(len(DECISIONS), 7)
        for suffix, decision in DECISIONS.items():
            script = ROOT / "scripts" / f"{PREFIX}{suffix}.py"
            code = script.read_text(encoding="utf-8")
            with self.subTest(decision=decision):
                self.assertEqual(code.count("source_checkout = Path(__file__).resolve().parents[1]"), 1)
                self.assertEqual(code.count("if target.is_relative_to(source_checkout):"), 1)
                self.assertIn(decision, code)
                self.assertIn("sys.dont_write_bytecode = True", code)
                self.assertNotIn("args.out.write_text(", code)
                self.assertLess(
                    code.index("if target.is_relative_to(source_checkout):"),
                    code.index("    target.write_text("),
                )

    def test_all_seven_denials_from_checkout_script_and_outside_cwds(self):
        with tempfile.TemporaryDirectory(prefix="dec629-checkout-") as tmp:
            root = Path(tmp)
            checkout, scripts = _checkout(root)
            reports = checkout / "reports"
            reports.mkdir()
            sentinel = reports / "existing.txt"
            sentinel.write_text("DO NOT MODIFY\n", encoding="utf-8")
            outside = root / "outside"
            outside.mkdir()
            alias = root / "source-alias"
            alias.symlink_to(checkout, target_is_directory=True)
            missing = root / "missing-input.json"
            baseline = _inventory(checkout)
            env = _env(checkout)

            for suffix, decision in DECISIONS.items():
                script = scripts / f"{PREFIX}{suffix}.py"
                flags = (
                    ["--witness-json", str(missing)]
                    if suffix == "lock_witness_coverage"
                    else ["--simulation-json", str(missing)]
                    if suffix == "ambiguous_dispatch_hold_model"
                    else []
                )
                attempts = (
                    ("root_relative", "reports/blocked.json", checkout),
                    ("scripts_relative", "../reports/blocked.json", scripts),
                    ("scripts_parent", "../../checkout/reports/blocked.json", scripts),
                    ("outside_absolute", str(reports / "blocked.json"), outside),
                    ("outside_symlink", str(alias / "reports" / "blocked.json"), outside),
                    ("outside_existing", str(sentinel), outside),
                    ("script_file", str(script), outside),
                )
                for mode, target, cwd in attempts:
                    with self.subTest(decision=decision, mode=mode):
                        command = [
                            sys.executable, str(script), "assess",
                            *flags, "--out", target,
                        ]
                        result = subprocess.run(
                            command, cwd=cwd, env=env, text=True,
                            capture_output=True, timeout=40, check=False,
                        )
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(decision, result.stderr)
                        self.assertIn("checkout", result.stderr.lower())
                        self.assertEqual(_inventory(checkout), baseline)
                        self.assertEqual(sentinel.read_text(), "DO NOT MODIFY\n")
                        self.assertEqual(list(checkout.rglob("*.pyc")), [])
            self.assertFalse(missing.exists())

    def test_all_seven_external_reports_are_inode_idempotent(self):
        """No second write, even when an external report shares a checkout inode."""
        with tempfile.TemporaryDirectory(prefix="dec629-idempotent-") as tmp:
            root = Path(tmp)
            checkout, scripts = _checkout(root)
            env = _env(checkout)
            witness = {
                "schema": WITNESS_VERSION,
                "ref": "refs/heads/main",
                "reviewed_commit_sha": "a" * 40,
                "intervals": [
                    {
                        "interval": label,
                        "resolved_ref_sha": "a" * 40,
                        **{field: True for field in REQUIRED_CLAIMS},
                    }
                    for label in INTERVALS
                ],
            }
            simulation = {
                "schema": SIMULATION_VERSION,
                "reviewed_code_sha": "a" * 40,
                "dispatch_call_made": False,
                "client_observed_outcome": "not_called",
                "observed_runs": [],
            }
            witness_file = root / "untrusted-witness.json"
            simulation_file = root / "untrusted-simulation.json"
            witness_file.write_text(json.dumps(witness), encoding="utf-8")
            simulation_file.write_text(json.dumps(simulation), encoding="utf-8")

            for suffix, decision in DECISIONS.items():
                with self.subTest(decision=decision):
                    flags = (
                        ["--witness-json", str(witness_file)]
                        if suffix == "lock_witness_coverage"
                        else ["--simulation-json", str(simulation_file)]
                        if suffix == "ambiguous_dispatch_hold_model"
                        else []
                    )
                    report_path = root / f"{suffix}.json"
                    command = [
                        sys.executable, str(scripts / f"{PREFIX}{suffix}.py"),
                        "assess", *flags, "--out", str(report_path),
                    ]
                    before = _inventory(checkout)
                    first = subprocess.run(
                        command, cwd=checkout, env=env, text=True,
                        capture_output=True, timeout=40, check=False,
                    )
                    self.assertEqual(first.returncode, 0, first.stderr)
                    report = json.loads(report_path.read_text(encoding="utf-8"))
                    self.assertEqual(report["decision"], decision)
                    self.assertIs(report["dispatch_blocked"], True)
                    self.assertIs(report["trading_authorized"], False)
                    self.assertEqual(_inventory(checkout), before)

                    # A hardlink reveals metadata writes invisible to SHA-256
                    # even when the external and checkout bytes remain identical.
                    linked = checkout / f"linked-{suffix}.json"
                    os.link(report_path, linked)
                    pinned = 1_600_000_000_000_000_000
                    os.utime(report_path, ns=(pinned, pinned))
                    mtime_before = report_path.stat().st_mtime_ns
                    linked_inventory = _inventory(checkout)
                    second = subprocess.run(
                        command, cwd=checkout, env=env, text=True,
                        capture_output=True, timeout=40, check=False,
                    )
                    self.assertEqual(second.returncode, 0, second.stderr)
                    self.assertEqual(report_path.stat().st_mtime_ns, mtime_before)
                    self.assertEqual(linked.stat().st_mtime_ns, mtime_before)
                    self.assertEqual(_inventory(checkout), linked_inventory)
                    self.assertEqual(list(checkout.rglob("*.pyc")), [])


if __name__ == "__main__":
    unittest.main()
