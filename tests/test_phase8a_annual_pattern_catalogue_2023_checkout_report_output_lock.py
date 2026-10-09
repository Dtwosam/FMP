from __future__ import annotations

"""DEC-628: actual CLI subprocess tests of checkout-local report-output denial."""

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
DECISIONS = {
    "main_lock_readiness": "DEC-612",
    "immutable_tag_feasibility": "DEC-615",
    "tag_ruleset_static_review": "DEC-616",
    "tag_ref_guard_rehearsal": "DEC-617",
}
SHA = "a" * 40


def _input_args(suffix: str, missing: Path) -> list[str]:
    if suffix == "main_lock_readiness":
        result = []
        for flag in (
            "dec611-audit-json", "main-branch-json", "annual-workflow-runs-json",
            "branch-protection-json", "effective-branch-rules-json", "inherited-rulesets-json",
        ):
            result += ["--" + flag, str(missing)]
        return result + ["--expected-head-sha", SHA]
    if suffix == "immutable_tag_feasibility":
        return [
            "--dec614-handoff-json", str(missing),
            "--main-branch-json", str(missing),
            "--annual-workflow-runs-json", str(missing),
            "--expected-head-sha", SHA,
        ]
    if suffix == "tag_ruleset_static_review":
        return [
            "--tag-ref", "refs/tags/fmp/phase8a/2023/run385/dec628-test-only",
            "--reviewed-commit-sha", SHA,
            "--git-ref-json", str(missing),
            "--rulesets-json", str(missing),
        ]
    if suffix == "tag_ref_guard_rehearsal":
        return [
            "--candidate-tag-ref", "refs/tags/fmp/phase8a/2023/run385/dec628-test-only",
            "--reviewed-commit-sha", SHA,
        ]
    raise ValueError("unexpected DEC-628 test CLI")


def _file_hashes(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-628 requires frozen installed annual workflow source",
)
class CheckoutReportOutputLockTests(unittest.TestCase):
    def test_four_guard_locations_precede_any_input_read(self):
        self.assertEqual(len(DECISIONS), 4)
        for suffix, decision in DECISIONS.items():
            source = (ROOT / "scripts" / f"{PREFIX}{suffix}.py").read_text()
            with self.subTest(decision=decision):
                guard = 'if target.is_relative_to(checkout):'
                self.assertEqual(source.count(guard), 1)
                self.assertIn(f'{decision} refuses audit output inside checkout', source)
                self.assertIn('target = args.out.resolve()', source)
                self.assertIn('checkout = Path(__file__).resolve().parents[1]', source)
                self.assertNotIn('checkout = Path.cwd().resolve()', source)
                self.assertIn('sys.dont_write_bytecode = True', source)
                self.assertLess(source.index(guard), source.index('    value = build_') if decision == "DEC-612"
                                else source.index('    result = build_') if decision in {"DEC-615", "DEC-617"}
                                else source.index('    report = inspect_'))
                self.assertIn('target.write_text(', source)
                self.assertNotIn('args.out.write_text(', source)

    def test_cli_rejects_relative_absolute_and_symlinked_checkout_outputs_first(self):
        with tempfile.TemporaryDirectory(prefix="dec628-outside-checkout-") as tmp:
            parent = Path(tmp)
            checkout = parent / "checkout"
            shutil.copytree(
                ROOT / "src" / "fmp",
                checkout / "src" / "fmp",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            scripts = checkout / "scripts"
            scripts.mkdir()
            for suffix in DECISIONS:
                filename = f"{PREFIX}{suffix}.py"
                shutil.copy2(ROOT / "scripts" / filename, scripts / filename)
            workflow = checkout / ".github" / "workflows" / "phase8a-annual-pattern-catalogue.yml"
            workflow.parent.mkdir(parents=True)
            shutil.copy2(ROOT / ".github" / "workflows" / workflow.name, workflow)

            reports = checkout / "reports"
            reports.mkdir()
            sentinel = reports / "existing.json"
            sentinel.write_text("DO NOT OVERWRITE\n")
            outside_link = parent / "alias-to-checkout"
            outside_link.symlink_to(checkout, target_is_directory=True)
            missing = parent / "nonexistent-input.json"
            self.assertFalse(missing.exists())
            baseline = _file_hashes(checkout)
            env = os.environ.copy()
            env["PYTHONPATH"] = str(checkout / "src")
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            env.pop("PYTHONPYCACHEPREFIX", None)
            for suffix, decision in DECISIONS.items():
                name = f"{PREFIX}{suffix}.py"
                attempts = (
                    ("relative", "reports/rejected.json", checkout),
                    ("absolute", str(reports / "rejected.json"), checkout),
                    ("parent_relative", "../checkout/reports/rejected.json", checkout),
                    ("symlink_alias", str(outside_link / "reports" / "rejected.json"), checkout),
                    ("existing_file", str(sentinel), checkout),
                    # The old Path.cwd() guard would accept these locations,
                    # even though the source is still under the same checkout.
                    ("subdir_to_parent", "../reports/rejected.json", scripts),
                    ("subdir_parent_sibling", "../../checkout/reports/rejected.json", scripts),
                    ("outside_cwd_absolute", str(reports / "rejected.json"), parent),
                    ("subdir_existing", str(sentinel), scripts),
                )
                for label, out, workdir in attempts:
                    with self.subTest(decision=decision, mode=label):
                        cmd = [
                            sys.executable, str(scripts / name), "assess",
                            *_input_args(suffix, missing), "--out", out,
                        ]
                        completed = subprocess.run(
                            cmd, cwd=workdir, env=env, text=True, capture_output=True,
                            timeout=40, check=False,
                        )
                        self.assertNotEqual(completed.returncode, 0)
                        self.assertIn(f"{decision} refuses audit output inside checkout", completed.stderr)
                        self.assertEqual(sentinel.read_text(), "DO NOT OVERWRITE\n")
                        self.assertEqual(_file_hashes(checkout), baseline)
                        self.assertEqual(list(checkout.rglob("*.pyc")), [])
            self.assertFalse(missing.exists())

    def test_resolved_external_output_is_not_rejected_as_checkout_local(self):
        with tempfile.TemporaryDirectory(prefix="dec628-outside-") as tmp:
            checkout = Path(tmp) / "checkout"
            checkout.mkdir()
            outside = Path(tmp) / "result.json"
            self.assertFalse(outside.resolve().is_relative_to(checkout.resolve()))
            self.assertTrue((checkout / "result.json").resolve().is_relative_to(checkout.resolve()))


if __name__ == "__main__":
    unittest.main()
