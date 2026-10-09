from __future__ import annotations

"""DEC-630: merged assess-only CLI source checkout and inode-write regression."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "phase8a_annual_pattern_catalogue_2023_"
DECISIONS = {
    "review_manifest_identity_separation": "DEC-625",
    "precheckout_job_if_preview": "DEC-626",
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
        name = f"{PREFIX}{suffix}.py"
        shutil.copy2(ROOT / "scripts" / name, scripts / name)
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
    "DEC-630 depends on frozen installed annual workflow source",
)
class MergedAuditOutputBoundaryTests(unittest.TestCase):
    def test_both_cli_guards_pin_source_and_disable_import_bytecode(self):
        self.assertEqual(len(DECISIONS), 2)
        for suffix, decision in DECISIONS.items():
            source = (ROOT / "scripts" / f"{PREFIX}{suffix}.py").read_text()
            with self.subTest(decision=decision):
                self.assertIn("source_checkout = Path(__file__).resolve().parents[1]", source)
                self.assertIn("target = args.out.resolve()", source)
                self.assertIn("if target.is_relative_to(source_checkout):", source)
                self.assertNotIn("if target.is_relative_to(checkout):", source)
                self.assertLess(
                    source.index("if target.is_relative_to(source_checkout):"),
                    source.index("    report = build_"),
                )
                self.assertIn("sys.dont_write_bytecode = True", source)
                self.assertLess(
                    source.index("sys.dont_write_bytecode = True"),
                    source.index("from fmp.discovery."),
                )
                self.assertIn("    if target.exists():", source)
                self.assertIn("    target.write_text(", source)
                self.assertNotIn("args.out.write_text(", source)

    def test_real_subprocess_denies_fourteen_checkout_output_attempts(self):
        with tempfile.TemporaryDirectory(prefix="dec630-negative-") as tmp:
            root = Path(tmp)
            checkout, scripts = _checkout(root)
            reports = checkout / "reports"
            reports.mkdir()
            sentinel = reports / "existing.json"
            sentinel.write_text("DO NOT OVERWRITE\n", encoding="utf-8")
            alias = root / "alias-to-checkout"
            alias.symlink_to(checkout, target_is_directory=True)
            outside = root / "other-cwd"
            outside.mkdir()
            env = _env(checkout)
            baseline = _inventory(checkout)

            for suffix, decision in DECISIONS.items():
                script = scripts / f"{PREFIX}{suffix}.py"
                attempts = (
                    ("root_relative", "reports/blocked.json", checkout),
                    ("scripts_relative", "../reports/blocked.json", scripts),
                    ("scripts_parent", "../../checkout/reports/blocked.json", scripts),
                    ("outside_absolute", str(reports / "blocked.json"), outside),
                    ("outside_symlink", str(alias / "reports/blocked.json"), outside),
                    ("outside_existing", str(sentinel), outside),
                    ("script_file", str(script), outside),
                )
                for mode, target, cwd in attempts:
                    with self.subTest(decision=decision, mode=mode):
                        result = subprocess.run(
                            [sys.executable, str(script), "assess", "--out", target],
                            cwd=cwd, env=env, capture_output=True, text=True,
                            timeout=40, check=False,
                        )
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(decision, result.stderr)
                        self.assertIn("checkout", result.stderr.lower())
                        self.assertEqual(_inventory(checkout), baseline)
                        self.assertEqual(sentinel.read_text(), "DO NOT OVERWRITE\n")
                        self.assertEqual(list(checkout.rglob("*.pyc")), [])

    def test_real_external_positive_rerun_and_conflict_are_nonwriting(self):
        with tempfile.TemporaryDirectory(prefix="dec630-positive-") as tmp:
            root = Path(tmp)
            checkout, scripts = _checkout(root)
            env = _env(checkout)
            for suffix, decision in DECISIONS.items():
                with self.subTest(decision=decision):
                    command = [sys.executable, str(scripts / f"{PREFIX}{suffix}.py"), "assess"]
                    output = root / f"{suffix}.json"
                    before = _inventory(checkout)
                    first = subprocess.run(
                        [*command, "--out", str(output)], cwd=checkout, env=env,
                        capture_output=True, text=True, timeout=40, check=False,
                    )
                    self.assertEqual(first.returncode, 0, first.stderr)
                    report = json.loads(output.read_text(encoding="utf-8"))
                    self.assertEqual(report["decision"], decision)
                    self.assertIs(report["dispatch_blocked"], True)
                    self.assertIs(report["trading_authorized"], False)
                    self.assertEqual(_inventory(checkout), before)

                    linked = checkout / f"hardlinked-{suffix}.json"
                    os.link(output, linked)
                    pinned_ns = 1_600_000_000_000_000_000
                    os.utime(output, ns=(pinned_ns, pinned_ns))
                    unchanged_mtime = output.stat().st_mtime_ns
                    with_link = _inventory(checkout)
                    repeat = subprocess.run(
                        [*command, "--out", str(output)], cwd=checkout, env=env,
                        capture_output=True, text=True, timeout=40, check=False,
                    )
                    self.assertEqual(repeat.returncode, 0, repeat.stderr)
                    self.assertEqual(output.stat().st_mtime_ns, unchanged_mtime)
                    self.assertEqual(linked.stat().st_mtime_ns, unchanged_mtime)
                    self.assertEqual(_inventory(checkout), with_link)

                    conflicting = root / f"conflict-{suffix}.json"
                    conflicting.write_text("PRESERVE EXTERNAL SENTINEL\n", encoding="utf-8")
                    denial = subprocess.run(
                        [*command, "--out", str(conflicting)], cwd=checkout, env=env,
                        capture_output=True, text=True, timeout=40, check=False,
                    )
                    self.assertNotEqual(denial.returncode, 0)
                    self.assertIn(decision, denial.stderr)
                    self.assertIn("conflicting", denial.stderr)
                    self.assertEqual(
                        conflicting.read_text(), "PRESERVE EXTERNAL SENTINEL\n"
                    )
                    self.assertEqual(_inventory(checkout), with_link)
                    self.assertEqual(list(checkout.rglob("*.pyc")), [])


if __name__ == "__main__":
    unittest.main()
