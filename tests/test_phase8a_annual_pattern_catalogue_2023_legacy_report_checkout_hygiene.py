from __future__ import annotations

"""DEC-631: real-process guard regression for 10 legacy source-only 2023 CLIs."""

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
SHA = "a" * 40
CASES = {
    "admin_lock_handoff": ("DEC-613", "prepare", ("dec612-readiness-json", "main-branch-json", "annual-workflow-runs-json"), ("expected-head-sha",)),
    "dispatch_action_preflight": ("DEC-610", "plan", ("authorization-json", "main-branch-json", "annual-workflow-runs-json"), ("expected-head-sha",)),
    "dispatch_authorization": ("DEC-609", "authorize", ("preflight-json",), ("authorization-head-sha",)),
    "dispatch_immutability_audit": ("DEC-611", "audit", ("dec610-preflight-json", "main-branch-json", "annual-workflow-runs-json"), ("expected-head-sha",)),
    "dispatch_preflight": ("DEC-608", "plan", ("install-receipt-json", "main-branch-json", "annual-workflow-runs-json"), ("expected-head-sha",)),
    "execution_preflight": ("DEC-602", "plan", ("runtime-binding-json", "main-branch-json", "annual-workflow-runs-json"), ("expected-head-sha",)),
    "runtime_authorization_install_action": ("DEC-606", "compile", ("preflight-json", "main-branch-json"), ("expected-head-sha",)),
    "runtime_authorization_install_preflight": ("DEC-605", "plan", ("authorization-json", "plan-json", "main-branch-json"), ("expected-head-sha",)),
    "runtime_authorization_install_receipt": ("DEC-607", "review", ("action-json", "changed-files"), ("install-commit-sha", "installed-gate-blob-sha", "installed-runtime-blob-sha")),
    "runtime_authorization_plan": ("DEC-604", "plan", ("authorization-json",), ()),
}


def _checksum_files(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*")) if p.is_file()
    }


def _copy_checkout(root: Path) -> tuple[Path, Path]:
    checkout = root / "checkout"
    shutil.copytree(
        ROOT / "src" / "fmp",
        checkout / "src" / "fmp",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    scripts = checkout / "scripts"
    scripts.mkdir()
    for suffix in CASES:
        filename = f"{PREFIX}{suffix}.py"
        shutil.copy2(ROOT / "scripts" / filename, scripts / filename)
    workflow = checkout / ".github" / "workflows" / "phase8a-annual-pattern-catalogue.yml"
    workflow.parent.mkdir(parents=True)
    shutil.copy2(ROOT / ".github" / "workflows" / workflow.name, workflow)
    return checkout, scripts


def _flags(suffix: str, missing: Path) -> list[str]:
    _, _, json_flags, sha_flags = CASES[suffix]
    args = []
    for flag in json_flags:
        args += ["--" + flag, str(missing)]
    for flag in sha_flags:
        args += ["--" + flag, SHA]
    return args


def _env(checkout: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(checkout / "src")
    env.pop("PYTHONDONTWRITEBYTECODE", None)
    env.pop("PYTHONPYCACHEPREFIX", None)
    return env


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-631 requires unchanged installed annual workflow source",
)
class LegacyCliReadOnlyOutputHygieneTests(unittest.TestCase):
    def test_all_ten_guard_before_input_and_disable_bytecode_before_import(self):
        self.assertEqual(len(CASES), 10)
        for suffix, (decision, command, _, _) in CASES.items():
            filename = f"{PREFIX}{suffix}.py"
            code = (ROOT / "scripts" / filename).read_text(encoding="utf-8")
            with self.subTest(decision=decision):
                self.assertIn(f'add_parser("{command}")', code)
                self.assertIn("source_checkout = Path(__file__).resolve().parents[1]", code)
                self.assertIn("target = args.out.resolve()", code)
                self.assertIn("if target.is_relative_to(source_checkout):", code)
                self.assertIn(f"{decision} refuses audit output inside checkout", code)
                guard_index = code.index("if target.is_relative_to(source_checkout):")
                # Helpers may assign "value" before the guarded handler.
                # Compare against the first builder invocation *after* the guard.
                self.assertLess(
                    guard_index,
                    code.index("    value = ", guard_index),
                )
                self.assertIn("sys.dont_write_bytecode = True", code)
                self.assertLess(
                    code.index("sys.dont_write_bytecode = True"),
                    code.index("from fmp.discovery."),
                )
                self.assertNotIn("args.out.write_text(", code)
                self.assertIn("return 0", code)

    def test_help_commands_leave_copied_checkout_byte_identical(self):
        with tempfile.TemporaryDirectory(prefix="dec631-help-") as tmp:
            checkout, scripts = _copy_checkout(Path(tmp))
            env = _env(checkout)
            baseline = _checksum_files(checkout)
            for suffix, (_, command, _, _) in CASES.items():
                with self.subTest(script=suffix):
                    result = subprocess.run(
                        [sys.executable, str(scripts / f"{PREFIX}{suffix}.py"), command, "--help"],
                        cwd=checkout, env=env, capture_output=True,
                        text=True, timeout=40, check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("--out", result.stdout)
                    self.assertEqual(_checksum_files(checkout), baseline)
                    self.assertEqual(list(checkout.rglob("*.pyc")), [])

    def test_all_seventy_output_denials_are_before_input_read_and_leave_checkout_pristine(self):
        with tempfile.TemporaryDirectory(prefix="dec631-no-source-writes-") as tmp:
            root = Path(tmp)
            checkout, scripts = _copy_checkout(root)
            reports = checkout / "reports"
            reports.mkdir()
            sentinel = reports / "existing.json"
            sentinel.write_text("PRESERVE ORIGINAL SOURCE\n", encoding="utf-8")
            outside = root / "outside-cwd"
            outside.mkdir()
            alias = root / "alias-to-checkout"
            alias.symlink_to(checkout, target_is_directory=True)
            missing = root / "intentionally-missing-input.json"
            self.assertFalse(missing.exists())
            before = _checksum_files(checkout)
            env = _env(checkout)
            for suffix, (decision, command, _, _) in CASES.items():
                script = scripts / f"{PREFIX}{suffix}.py"
                outputs = (
                    ("root_relative", "reports/denied.json", checkout),
                    ("scripts_relative", "../reports/denied.json", scripts),
                    ("scripts_parent", "../../checkout/reports/denied.json", scripts),
                    ("outside_absolute", str(reports / "denied.json"), outside),
                    ("outside_symlink", str(alias / "reports" / "denied.json"), outside),
                    ("outside_existing", str(sentinel), outside),
                    ("outside_script", str(script), outside),
                )
                for mode, out, workdir in outputs:
                    with self.subTest(decision=decision, case=mode):
                        result = subprocess.run(
                            [sys.executable, str(script), command,
                             *_flags(suffix, missing), "--out", out],
                            cwd=workdir, env=env, capture_output=True,
                            text=True, timeout=40, check=False,
                        )
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(
                            f"{decision} refuses audit output inside checkout",
                            result.stderr,
                        )
                        self.assertEqual(sentinel.read_text(), "PRESERVE ORIGINAL SOURCE\n")
                        self.assertEqual(_checksum_files(checkout), before)
                        self.assertEqual(list(checkout.rglob("*.pyc")), [])
            self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
