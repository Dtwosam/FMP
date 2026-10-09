from __future__ import annotations

"""DEC-627: real-process audit CLI no-checkout-write regression."""

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
            baseline = sorted(
                p.relative_to(checkout).as_posix()
                for p in checkout.rglob("*") if p.is_file()
            )
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
                        sorted(p.relative_to(checkout).as_posix()
                               for p in checkout.rglob("*") if p.is_file()),
                        baseline,
                        f"{name} wrote files inside checkout",
                    )
                    self.assertEqual(list(checkout.rglob("*.pyc")), [])


if __name__ == "__main__":
    unittest.main()
