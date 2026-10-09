from __future__ import annotations

"""DEC-627: real-process audit CLI no-checkout-write regression."""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "phase8a_annual_pattern_catalogue_2023_"
ASSESS_ONLY_AUDITS = (
    "main_lock_readiness",
    "immutable_tag_feasibility",
    "tag_ruleset_static_review",
    "tag_ref_guard_rehearsal",
    "disarmed_tag_amendment_preview",
    "ref_race_interleaving_model",
    "lock_witness_coverage",
    "ambiguous_dispatch_hold_model",
    "runtime_tag_sha_binding_preview",
    "preaccess_identity_gate_topology_audit",
    "three_layer_admission_model",
)


def _checksum_inventory(checkout: Path) -> dict[str, str]:
    # Compare file names AND bytes: new files or in-place source edits must fail.
    return {
        p.relative_to(checkout).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(checkout.rglob("*")) if p.is_file()
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-627 tests require the installed annual workflow source",
)
class ReadonlyAuditCliBytecodeHygieneTests(unittest.TestCase):
    def test_every_legacy_assess_cli_blocks_bytecode_before_package_imports(self):
        self.assertEqual(len(ASSESS_ONLY_AUDITS), len(set(ASSESS_ONLY_AUDITS)))
        self.assertEqual(len(ASSESS_ONLY_AUDITS), 11)
        for suffix in ASSESS_ONLY_AUDITS:
            path = ROOT / "scripts" / f"{PREFIX}{suffix}.py"
            with self.subTest(script=path.name):
                source = path.read_text(encoding="utf-8")
                setting = "sys.dont_write_bytecode = True"
                package = "from fmp.discovery."
                self.assertEqual(source.count(setting), 1)
                self.assertIn("import sys", source)
                self.assertIn(package, source)
                self.assertLess(source.index(setting), source.index(package))
                self.assertIn('add_parser("assess")', source)

    def test_actual_help_subprocesses_cannot_write_to_clean_checkout(self):
        # A source grep alone misses Python's import-time __pycache__ side effect.
        with tempfile.TemporaryDirectory(prefix="dec627-audit-bytecode-") as temp:
            root = Path(temp)
            checkout = root / "checkout"
            shutil.copytree(
                ROOT / "src" / "fmp",
                checkout / "src" / "fmp",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            script_dir = checkout / "scripts"
            script_dir.mkdir(parents=True)
            for suffix in ASSESS_ONLY_AUDITS:
                name = f"{PREFIX}{suffix}.py"
                shutil.copy2(ROOT / "scripts" / name, script_dir / name)
            env = os.environ.copy()
            env["PYTHONPATH"] = str(checkout / "src")
            # Explicitly remove all upstream suppression mechanisms to exercise
            # the CLI's own pre-import bytecode-write gate.
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            env.pop("PYTHONPYCACHEPREFIX", None)
            baseline = _checksum_inventory(checkout)
            for suffix in ASSESS_ONLY_AUDITS:
                name = f"{PREFIX}{suffix}.py"
                with self.subTest(script=name):
                    result = subprocess.run(
                        [sys.executable, str(script_dir / name), "--help"],
                        cwd=checkout,
                        env=env,
                        text=True,
                        capture_output=True,
                        timeout=40,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("assess", result.stdout)
                    self.assertEqual(
                        _checksum_inventory(checkout),
                        baseline,
                        f"{name} wrote files inside checkout",
                    )
                    self.assertEqual(list(checkout.rglob("*.pyc")), [])


    def test_real_offline_assess_reports_preserve_checkout_and_deny_dispatch(self):
        """Execute four real source-pinned assess subcommands, not only --help."""
        import json

        cases = {
            "disarmed_tag_amendment_preview": "DEC-618",
            "runtime_tag_sha_binding_preview": "DEC-622",
            "preaccess_identity_gate_topology_audit": "DEC-623",
            "three_layer_admission_model": "DEC-624",
        }
        with tempfile.TemporaryDirectory(prefix="dec627-assess-no-writes-") as tmp:
            temp_root = Path(tmp)
            checkout = temp_root / "checkout"
            shutil.copytree(
                ROOT / "src" / "fmp",
                checkout / "src" / "fmp",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            scripts = checkout / "scripts"
            scripts.mkdir(parents=True)
            workflow = checkout / ".github" / "workflows" / "phase8a-annual-pattern-catalogue.yml"
            workflow.parent.mkdir(parents=True)
            shutil.copy2(ROOT / ".github" / "workflows" / workflow.name, workflow)
            for suffix in cases:
                name = f"{PREFIX}{suffix}.py"
                shutil.copy2(ROOT / "scripts" / name, scripts / name)
            files_before = _checksum_inventory(checkout)
            env = os.environ.copy()
            env["PYTHONPATH"] = str(checkout / "src")
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            env.pop("PYTHONPYCACHEPREFIX", None)
            for suffix, expected_decision in cases.items():
                with self.subTest(command=suffix):
                    name = f"{PREFIX}{suffix}.py"
                    out = temp_root / f"{suffix}.json"
                    completed = subprocess.run(
                        [sys.executable, str(scripts / name), "assess", "--out", str(out)],
                        cwd=checkout,
                        env=env,
                        text=True,
                        capture_output=True,
                        timeout=40,
                        check=False,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    report = json.loads(out.read_text(encoding="utf-8"))
                    self.assertEqual(report["decision"], expected_decision)
                    self.assertIs(report["dispatch_blocked"], True)
                    self.assertIs(report["trading_authorized"], False)
                    self.assertEqual(
                        _checksum_inventory(checkout),
                        files_before,
                        f"{name} changed its checkout during assess",
                    )
                    self.assertEqual(list(checkout.rglob("*.pyc")), [])



if __name__ == "__main__":
    unittest.main()
